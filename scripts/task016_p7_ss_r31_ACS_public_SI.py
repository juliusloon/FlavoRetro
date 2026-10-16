"""R31: bounded official Figshare publisher-SI custody, metadata projection only."""
import json,uuid,fcntl,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import now,sha,load,lines,put,append,can,budget,gate
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"SS/E02/fresh/SS-E02-R31-ACS-public-SI-custody-v1"
RAW=Path("data/raw/task016-p7/SS/E02/SS-E02-R31-ACS-public-SI-custody-v1")
LOCK=B/"source_budget_acquisition.lock"
BIB=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1/A3_two_route_bibliographic_preflight_v2.json"
DOIS=["10.1021/acs.jafc.5c06227","10.1021/acs.jafc.4c03824","10.1021/acs.jafc.4c00488"]
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 all_=physical_attempts();g=gate("SS")
 qs=[dict(query_id="R31-meta-"+str(i),doi=d,url="https://api.figshare.com/v2/articles?"+urllib.parse.urlencode({"resource_doi":d,"page_size":10}),kind="metadata",object_limit=2*1024**2) for i,d in enumerate(DOIS,1)]
 put(O/"precontract.json",dict(task=T,agent_role="A2_raw_only",approval_type="agent_delegated",at=now(),family="SS",epoch_id="SS-E02",G4=g,bibliography_path=str(BIB),bibliography_SHA=sha(BIB),script_SHA=sha(Path(__file__).resolve().relative_to(ROOT)),global_budget_before=budget(all_),max_HTTP=12,max_metadata_HTTP=6,max_attachments=6,max_file_bytes=64*1024**2,no_scientific_read=True,no_redirect=True,no_auto_retry=True,public_API_documentation=["https://docs.figshare.com/old_docs/api/articles/","https://docs.figshare.com/v2/"],external_documentation_web_tool_transport="unobservable_not_charged_as_precise_HTTP",reason="New primary ACS sources already bibliographically verified; public publisher-linked SI may contain source original evidence. No chemical qualification here.",metadata_projection_fields=["id","title","doi","resource_doi","resource_title","url","url_public_html","url_public_api","published_date","authors","license","files","download_url","name","size","is_link_only"],main_article_access_denial_not_bypassed=True,actual_Figshare_advertised_links_only=True))
 put(O/"metadata_query_plan.json",dict(task=T,at=now(),planned=len(qs),queries=qs,precontract_SHA=sha(O/"precontract.json")))
 print(json.dumps(dict(registered=len(qs),global_HTTP=len(all_))))
def get(q,plan):
 if q not in load(plan)["queries"]:raise RuntimeError("UNREGISTERED")
 if sha(BIB)!=load(O/"precontract.json")["bibliography_SHA"]:raise RuntimeError("BIB_DRIFT")
 u=urllib.parse.urlsplit(q["url"])
 allowed={"api.figshare.com"} if q["kind"]=="metadata" else {"ndownloader.figshare.com","acs.figshare.com","api.figshare.com"}
 if u.scheme!="https" or u.hostname not in allowed or u.username or u.password or u.fragment:raise RuntimeError("PUBLIC_URL_INVALID")
 with (ROOT/LOCK).open("a+") as fd:
  fcntl.flock(fd.fileno(),fcntl.LOCK_EX)
  try:
   gate("SS");all_=physical_attempts();previous=[r for r in all_ if can(r["url"])==can(q["url"])]
   if len(previous)>=2 or any(r.get("status_code") in (401,403,429) for r in previous):return dict(query_id=q["query_id"],HTTP=0,status="prior_cap_or_denial")
   cur=budget(all_);fam=budget([r for r in all_ if "SS" in Path(r.get("path") or "").parts])
   for x,lims in [(cur,dict(HTTP=8000,bytes=8*1024**3,article_versions=400,attachments=800)),(fam,dict(HTTP=2500,bytes=2*1024**3,article_versions=120,attachments=200))]:
    projected=dict(x);projected["HTTP"]+=1;projected["bytes"]+=q["object_limit"]+1
    if q["kind"]=="attachment":projected["attachments"]+=1
    if any(projected[k]>v for k,v in lims.items()):raise RuntimeError("GLOBAL_OR_SS_BUDGET")
   if len(lines(O/"http_ledger.jsonl"))>=12:raise RuntimeError("R31_BUDGET")
   aid="SS-E02-R31-"+uuid.uuid4().hex;start=now()
   append(O/"physical_request_preregistration.jsonl",dict(attempt_id=aid,at=start,query=q,plan_SHA=sha(plan),precontract_SHA=sha(O/"precontract.json"),global_before=cur,SS_before=fam,previous_URL_attempts=len(previous)))
   response=None;data=b"";code=None;err=None;final=q["url"];headers={}
   try:
    req=urllib.request.Request(q["url"],headers={"User-Agent":"FlavoRetro TASK016P7 public publisher SI research","Accept-Encoding":"identity"})
    try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=28)
    except urllib.error.HTTPError as e:response=e;err="HTTP_"+str(e.code)
    code=response.code;final=response.geturl()
    headers={k.lower():v for k,v in response.headers.items() if k.lower() in {"content-type","content-length","location","date"}}
    data=response.read(q["object_limit"]+1)
    if len(data)>q["object_limit"]:err="OBJECT_CAP"
    if final!=q["url"] or 300<=code<400:err="REDIRECT_DEFERRED"
   except Exception as e:err=type(e).__name__+":"+str(e)[:100]
   finally:
    if response is not None:response.close()
   p=RAW/(aid+"."+q["kind"]);(ROOT/p).parent.mkdir(parents=True,exist_ok=True)
   if (ROOT/p).exists():raise RuntimeError("RAW_COLLISION")
   (ROOT/p).write_bytes(data);(ROOT/p).chmod(0o444)
   event(T,"write_binary",path=str(p),before=None,after=sha(p),bytes=len(data))
   r=dict(attempt_id=aid,query_id=q["query_id"],source_id=q["doi"],doi=q["doi"],family="SS",epoch_id="SS-E02",batch_id="SS-E02-R31",kind=q["kind"],role=q["kind"],url=q["url"],final_url=final,started_at=start,finished_at=now(),status_code=code,error=err,status="available" if code==200 and err is None else "failed",path=str(p),sha256=sha(p),bytes=len(data),headers=headers,no_scientific_read=True,evidence_eligible=False,license="pending_metadata_binding",redistribution="local_only")
   append(O/"http_ledger.jsonl",r);event(T,"source_http",**r)
   return r
  finally:fcntl.flock(fd.fileno(),fcntl.LOCK_UN)
def run(planname):
 plan=O/planname
 for q in load(plan)["queries"]:
  if any(r["query_id"]==q["query_id"] for r in lines(O/"query_execution.jsonl")):continue
  r=get(q,plan);append(O/"query_execution.jsonl",dict(query_id=q["query_id"],doi=q["doi"],HTTP=r.get("HTTP",1),status=r["status"],HTTP_status=r.get("status_code"),raw_pointer={k:r.get(k) for k in ["path","sha256","bytes"]},error=r.get("error")))
  print(json.dumps({k:r.get(k) for k in ["query_id","doi","status_code","bytes","error"]}),flush=True)
def details():
 qs=[];out=[]
 for r in lines(O/"http_ledger.jsonl"):
  if not r["query_id"].startswith("R31-meta-") or r["status"]!="available":continue
  obj=json.loads((ROOT/r["path"]).read_bytes())
  if not isinstance(obj,list):raise RuntimeError("LIST_REQUIRED")
  if len(obj)>10:raise RuntimeError("PAGE_CAP")
  for a in obj:
   projection={k:a.get(k) for k in ["id","title","doi","resource_doi","resource_title","url","url_public_html","url_public_api","published_date"]}
   out.append(dict(requested_doi=r["doi"],metadata=projection,raw_SHA=r["sha256"]))
   if len([x for x in qs if x["doi"]==r["doi"]])>=1:continue
   if not isinstance(a.get("id"),int):continue
   # Returned list is only a discovery hint; exact resource DOI rechecked on detail.
   qs.append(dict(query_id="R31-detail-"+str(a["id"]),doi=r["doi"],url="https://api.figshare.com/v2/articles/"+str(a["id"]),kind="metadata",object_limit=2*1024**2,listing_raw_SHA=r["sha256"],article_id=a["id"]))
 put(O/"metadata_list_projection.json",dict(task=T,at=now(),records=out,chemical_content_read=False))
 put(O/"detail_query_plan.json",dict(task=T,at=now(),planned=len(qs),queries=qs,source_list_projection_SHA=sha(O/"metadata_list_projection.json")))
 print(json.dumps(dict(listed=len(out),details_planned=len(qs))))
def files():
 qs=[];out=[]
 for r in lines(O/"http_ledger.jsonl"):
  if not r["query_id"].startswith("R31-detail-") or r["status"]!="available":continue
  a=json.loads((ROOT/r["path"]).read_bytes())
  resource=str(a.get("resource_doi") or "").strip().lower().removeprefix("https://doi.org/")
  exact=resource==r["doi"];fs=a.get("files",[])
  out.append(dict(requested_doi=r["doi"],resource_doi=resource,exact_resource_DOI=exact,metadata={k:a.get(k) for k in ["id","title","doi","resource_doi","resource_title","url","url_public_html","published_date","authors","license","files"]},raw_SHA=r["sha256"]))
  if not exact:continue
  for f in fs[:2]:
   url=f.get("download_url");size=f.get("size");u=urllib.parse.urlsplit(url or "")
   if u.scheme!="https" or u.hostname not in {"ndownloader.figshare.com","acs.figshare.com","api.figshare.com"} or f.get("is_link_only") or not isinstance(size,int) or size<=0 or size>64*1024**2:continue
   qs.append(dict(query_id="R31-file-"+str(f["id"]),doi=r["doi"],url=url,kind="attachment",object_limit=64*1024**2,advertised_file=f,article_id=a["id"],detail_raw_SHA=r["sha256"]))
 put(O/"publisher_SI_metadata_projection.json",dict(task=T,at=now(),records=out,chemical_content_read=False,raw_custody_only=True))
 put(O/"file_query_plan.json",dict(task=T,at=now(),planned=len(qs),queries=qs,source_projection_SHA=sha(O/"publisher_SI_metadata_projection.json"),no_scientific_read=True))
 print(json.dumps(dict(detail_records=len(out),exact_DOI=sum(x["exact_resource_DOI"] for x in out),files_planned=len(qs))))
def finish():
 plans=[O/p for p in ["metadata_query_plan.json","detail_query_plan.json","file_query_plan.json"]]
 q=[x for p in plans for x in load(p)["queries"]];ex=lines(O/"query_execution.jsonl")
 if {x["query_id"] for x in q}!={x["query_id"] for x in ex} or len(q)!=len(ex):raise RuntimeError("QUERY_CONSERVATION")
 rr=lines(O/"http_ledger.jsonl");files=[r for r in rr if r["kind"]=="attachment"]
 put(O/"raw_custody_summary.json",dict(task=T,agent_role="A2_raw_only",at=now(),planned=len(q),terminal=len(ex),physical_HTTP=len(rr),bytes=sum(r["bytes"] for r in rr),attachment_available=sum(r["status"]=="available" for r in files),attachments=[{k:r[k] for k in ["doi","path","sha256","bytes","status","status_code"]} for r in files],source_science_read=False,source_A3_original_verified=False,chemical_qualification=False,fresh_admitted=0,saturation_claim=False,input_SHA={str(p):sha(p) for p in plans}))
 print(json.dumps(dict(physical_HTTP=len(rr),attachments_available=sum(r["status"]=="available" for r in files))))
if __name__=="__main__":
 import sys
 cmd=sys.argv[1]
 if cmd=="pre":pre()
 elif cmd=="details":details()
 elif cmd=="files":files()
 elif cmd=="finish":finish()
 elif cmd=="run":run(sys.argv[2])
