"""R31 v2: preserves v1; separately registered actual publisher-advertised S3 redirect route."""
import json,uuid,fcntl,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import now,sha,load,lines,put,append,can,budget,gate
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"SS/E02/fresh/SS-E02-R58-declared-primary-PDF-custody-v1"
RAW=Path("data/raw/task016-p7/SS/E02/SS-E02-R58-declared-primary-PDF-custody-v1")
LOCK=B/"source_budget_acquisition.lock"
BIB=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1/A3_two_route_bibliographic_preflight_v2.json"
DOIS=["10.1021/acs.jafc.5c06227","10.1021/acs.jafc.4c03824","10.1021/acs.jafc.4c00488"]
def get(q,plan):
 if q not in load(plan)["queries"]:raise RuntimeError("UNREGISTERED")
 if sha(BIB)!=load(O/"precontract.json")["bibliography_SHA"]:raise RuntimeError("BIB_DRIFT")
 u=urllib.parse.urlsplit(q["url"])
 allowed={"pubs.acs.org"}
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
   if len(lines(O/"http_ledger.jsonl"))>=2:raise RuntimeError("R58_BUDGET")
   aid="SS-E02-R58-"+uuid.uuid4().hex;start=now()
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
   r=dict(attempt_id=aid,query_id=q["query_id"],source_id=q["doi"],doi=q["doi"],family="SS",epoch_id="SS-E02",batch_id="SS-E02-R58",kind=q["kind"],role=q["kind"],url=q["url"],final_url=final,started_at=start,finished_at=now(),status_code=code,error=err,status="available" if code==200 and err is None else "failed",path=str(p),sha256=sha(p),bytes=len(data),headers=headers,no_scientific_read=True,evidence_eligible=False,license="pending_metadata_binding",redistribution="local_only")
   append(O/"http_ledger.jsonl",r);event(T,"source_http",**r)
   return r
  finally:fcntl.flock(fd.fileno(),fcntl.LOCK_UN)

def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 bib=load(BIB);hist=physical_attempts();qs=[]
 for d in ["10.1021/acs.jafc.5c06227","10.1021/acs.jafc.4c00488"]:
  r=next(x for x in bib["records"] if x["doi"]==d);raw=r["original_raw"]
  if sha(raw["path"])!=raw["sha256"]:raise RuntimeError("BIB_RAW_DRIFT")
  m=load(raw["path"])["message"]
  candidates=sorted({x["URL"] for x in m.get("link",[]) if x.get("content-type")=="application/pdf" and x.get("intended-application")=="unspecified"})
  if len(candidates)!=1:raise RuntimeError("NO_UNIQUE_DECLARED_PDF")
  u=candidates[0]
  if any(can(x["url"])==can(u) for x in hist):raise RuntimeError("PREVIOUS_URL_NOT_NEW")
  qs.append(dict(query_id="R58-declared-PDF-"+str(len(qs)+1),doi=d,url=u,kind="article_version",object_limit=64*1024**2,raw_declaration=raw))
 put(O/"precontract.json",dict(task=T,at=now(),agent_role="A2_raw_only",family="SS",epoch_id="SS-E02",approval_type="agent_delegated",human_reviewed=False,G4=gate("SS"),bibliography_path=str(BIB),bibliography_SHA=sha(BIB),script_SHA=sha(Path(__file__).resolve().relative_to(ROOT)),max_HTTP=2,max_file_bytes=64*1024**2,no_retry=True,no_redirect=True,no_scientific_read=True,reason="Exact new publisher-declared original PDF URLs for two already known sources; closed-access metadata retained and access control never bypassed.",earlier_denied_tea_and_apple_exact_URLs_not_reused=True,source_qualified=False,fresh_admitted=0,source_saturation=False))
 put(O/"query_plan.json",dict(task=T,at=now(),planned=len(qs),queries=qs,exact_Crossref_link_values_only=True))
 print(json.dumps(dict(registered=len(qs))))
def run():
 ex=[]
 for q in load(O/"query_plan.json")["queries"]:
  r=get(q,O/"query_plan.json")
  b=(ROOT/r["path"]).read_bytes() if r.get("path") else b""
  ex.append(dict(query_id=q["query_id"],doi=q["doi"],HTTP=r.get("HTTP",1),HTTP_status=r.get("status_code"),status=r["status"],raw_pointer={k:r.get(k) for k in ["path","sha256","bytes"]},PDF_signature=b[:5]==b"%PDF-",valid_original=r.get("status_code")==200 and b[:5]==b"%PDF-",scientific_content_read=False))
  write(T,str(O/"query_execution.jsonl"),"".join(json.dumps(x,sort_keys=True)+"\n" for x in ex))
 put(O/"raw_custody_summary.json",dict(task=T,at=now(),planned=2,terminal=len(ex),physical_HTTP=sum(x["HTTP"] for x in ex),HTTP_statuses=[x["HTTP_status"] for x in ex],valid_PDF=sum(x["valid_original"] for x in ex),scientific_content_read=False,fresh_admitted=0,source_saturation=False))
 print(json.dumps(dict(HTTP=sum(x["HTTP"] for x in ex),statuses=[x["HTTP_status"] for x in ex],valid_PDF=sum(x["valid_original"] for x in ex))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
