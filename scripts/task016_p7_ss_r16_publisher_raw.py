"""SS-E02 R16: bounded, original Crossref-advertised publisher PDF raw custody only.

Two explicit public HTTPS URLs; no login, proxy, token, guessing, retries,
redirect-follow, or scientific PDF reads. Publication may require subscription.
"""
from __future__ import annotations
import fcntl,json,uuid,urllib.request,urllib.error,urllib.parse,hashlib
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
from scripts.task016_p7_ss_sources import require_acquisition_phase
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R15=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1"
O=B/"SS/E02/fresh/SS-E02-R16-verified-publisher-PDF-access-v1"
RAW=Path("data/raw/task016-p7/SS/E02/SS-E02-R16-verified-publisher-PDF-access-v1")
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
LOCK=B/"source_budget_acquisition.lock"
SELECT=["10.1021/acs.jafc.4c03824","10.1111/tpj.16898"]
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()] if (ROOT/p).exists() else []
def write_json(p,d):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS "+str(p))
 write(T,str(p),json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def append(p,d):write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n")
def basecounts(all_):
 return dict(HTTP=len(all_),bytes=sum(r["bytes"] for r in all_),
  article_versions=sum(r.get("kind",r.get("role")) in ("article_version","xml","original_pdf") for r in all_),
  attachments=sum(r.get("kind",r.get("role"))=="attachment" for r in all_))
def pre():
 if (ROOT/O).exists():raise RuntimeError("OUTPUT_EXISTS")
 verified=load(R15/"A3_two_route_bibliographic_preflight_v2.json")
 orig={x["DOI"]:x["metadata"] for x in rows(R15/"crossref_bibliography_projection.jsonl")}
 src={r["doi"]:r for r in verified["records"]}
 ps=[]
 for doi in SELECT:
  assert src[doi]["metadata_identity_verified"] and not src[doi]["original_full_scientific_article_present"]
  links=[link for link in orig[doi]["link"] if link.get("content-type") in ("application/pdf","unspecified") and link.get("URL","").startswith("https://")]
  assert links,("no verified publisher PDF link",doi)
  link=links[0]
  assert link["URL"].startswith("https://pubs.acs.org/doi/pdf/") or link["URL"].startswith("https://onlinelibrary.wiley.com/doi/pdf/")
  ps.append(dict(query_id="SS-R16-"+str(len(ps)+1),DOI=doi,PMID=src[doi]["pmid"],
     url=link["URL"],route="Crossref_actual_verified_publisher_PDF_URL",
     kind="article_version",max_bytes=10*1024**2,phase="fresh",
     family="SS",epoch_id="SS-E02",source_science_not_authorized_from_raw_custody=True,
     OA_status=src[doi]["access_status"]))
 assert len(ps)==2
 with (ROOT/LOCK).open("a+") as fd:
  fcntl.flock(fd.fileno(),fcntl.LOCK_EX)
  gate=require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
  all_=physical_attempts()
  for p in ps:p["prior_exact_url_attempts"]=sum(a.get("url")==p["url"] for a in all_)
  prior=dict(global_=basecounts(all_),SS=basecounts([a for a in all_ if "SS" in Path(a.get("path") or "").parts]))
  fcntl.flock(fd.fileno(),fcntl.LOCK_UN)
 verify_stage_chain(ROOT/G4,sha(G4));verify_stage_chain(ROOT/G5,sha(G5))
 inputs=[Path("scripts/task016_p7_ss_r16_publisher_raw.py"),G4,G5,
   R15/"A3_two_route_bibliographic_preflight_v2.json",
   R15/"crossref_bibliography_projection.jsonl",
   R15/"precontract.json"]
 write_json(O/"precontract.json",dict(task=T,epoch_id="SS-E02",batch="R16",
  at=now(),approval_type="agent_delegated",human_reviewed=False,
  source_count=2,requests=ps,registered_input_SHA={str(x):sha(x) for x in inputs},
  phase_gate=gate,budget_before=prior,
  goals="one attempt per exact Crossref-advertised publisher PDF under anonymous public access",
  no_login_cookie_payment_credential=False,no_login_or_access_bypass=True,
  redirect_auto_follow=False,automatic_retry=False,raw_only=True,not_scientific_content_read=True,
  source_identity_original_not_verified=True,scope_or_holdout_not_adjusted=True,
  G5_frozen_before_any_chemical_read=True,Article_cap=10*1024**2,
  no_MCTS=True,no_automatic_fresh=True))
 write_json(O/"query_plan.json",dict(task=T,at=now(),queries=ps,planned=2,precontract_SHA=sha(O/"precontract.json")))
 print(json.dumps(dict(registered=2,global_http=prior["global_"]["HTTP"],SS_http=prior["SS"]["HTTP"])),flush=True)
def acquire(q):
 pre=load(O/"precontract.json")
 if q not in load(O/"query_plan.json")["queries"]:raise RuntimeError("UNREGISTERED")
 for p,h in pre["registered_input_SHA"].items():
  if sha(Path(p))!=h:raise RuntimeError("INPUT_SHA_DRIFT "+p)
 url=q["url"]
 u=urllib.parse.urlsplit(url)
 if u.scheme!="https" or u.hostname not in ("pubs.acs.org","onlinelibrary.wiley.com") or u.username or u.password:raise RuntimeError("HOST_DENIED")
 with (ROOT/LOCK).open("a+") as lk:
  fcntl.flock(lk.fileno(),fcntl.LOCK_EX)
  try:
   require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
   all_=physical_attempts();prev=[a for a in all_ if a.get("url")==url]
   if len(prev)>=2 or any(a.get("status_code") in (401,403) for a in prev):
    return {"query_id":q["query_id"],"skipped_reason":"cap2_or_auth_failure","HTTP":0}
   before=basecounts(all_); ss=basecounts([a for a in all_ if "SS" in Path(a.get("path") or "").parts])
   if before["HTTP"]+1>8000 or before["bytes"]+q["max_bytes"]>8*1024**3 or before["article_versions"]+1>400:raise RuntimeError("GLOBAL_BUDGET")
   if ss["HTTP"]+1>2500 or ss["bytes"]+q["max_bytes"]>2*1024**3 or ss["article_versions"]+1>120:raise RuntimeError("SS_BUDGET")
   if len(rows(O/"http_ledger.jsonl"))>=2:raise RuntimeError("R16_HARD_BATCH_CAP")
   aid="SS-E02-R16-"+uuid.uuid4().hex;started=now()
   append(O/"physical_request_preregistration.jsonl",dict(attempt_id=aid,query_id=q["query_id"],
    url=url,source_id=q["DOI"],kind="article_version",batch="SS-R16",
    registered_at=started,byte_cap=q["max_bytes"],budget_before=before,SS_before=ss,
    URL_attempts_before=len(prev),plan_SHA=sha(O/"query_plan.json"),precontract_SHA=sha(O/"precontract.json")))
   data=b"";code=None;error=None;final=None;response=None;headers={}
   try:
    request=urllib.request.Request(url,headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 public scientific study","Accept-Encoding":"identity"})
    try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
    except urllib.error.HTTPError as err:response=err;error="HTTP_"+str(err.code)
    code=response.code;final=response.geturl()
    headers={k:v for k,v in response.headers.items() if k.lower() in ("content-type","content-length","location","date","etag")}
    data=response.read(q["max_bytes"]+1)
    if len(data)>q["max_bytes"]:data=data[:q["max_bytes"]];error="OBJECT_CAP"
    if final!=url or 300<=code<400:error="NO_REDIRECT_FOLLOW"
   except Exception as exc:error=type(exc).__name__+":"+str(exc)[:150]
   finally:
    if response is not None:response.close()
   path=RAW/(aid+".article_version");dest=ROOT/path;dest.parent.mkdir(parents=True,exist_ok=True)
   if dest.exists():raise RuntimeError("IMMUTABLE_RAW_ALREADY_EXISTS")
   dest.write_bytes(data);dest.chmod(0o444)
   event(T,"write_binary",path=str(path),before=None,after=sha(path),bytes=len(data))
   result=dict(attempt_id=aid,query_id=q["query_id"],source_id=q["DOI"],url=url,
     final_url=final,status_code=code,error=error,started_at=started,finished_at=now(),
     kind="article_version",role="article_version",phase="fresh",epoch_id="SS-E02",
     batch_id="SS-E02-R16-verified-publisher-PDF-access-v1",status="available" if code==200 and error is None else "failed",
     bytes=len(data),path=str(path),sha256=sha(path),headers=headers,
     public_pdf_magic=data.startswith(b"%PDF-"),source_original_contents_read=False,
     physical_redistribution_license="local-only pending exact source license",
     human_reviewed=False,current_epoch_fresh_eligible=False)
   append(O/"http_ledger.jsonl",result);event(T,"source_http",**result);return result
  finally:fcntl.flock(lk.fileno(),fcntl.LOCK_UN)
def run():
 for q in load(O/"query_plan.json")["queries"]:
  if any(x["query_id"]==q["query_id"] for x in rows(O/"query_execution.jsonl")):continue
  r=acquire(q)
  append(O/"query_execution.jsonl",dict(query_id=q["query_id"],DOI=q["DOI"],
      status=r.get("status"),HTTP=0 if r.get("HTTP")==0 else 1,
      HTTP_status=r.get("status_code"),raw_pointer={k:r.get(k) for k in ("path","sha256","bytes")},
      valid_PDF_magic=r.get("public_pdf_magic"),error=r.get("error") or r.get("skipped_reason"),
      no_body_or_chemical_read=True))
  print(json.dumps(dict(query=q["query_id"],status=r.get("status_code"),bytes=r.get("bytes"),pdf=r.get("public_pdf_magic"),error=r.get("error") or r.get("skipped_reason"))),flush=True)
def finish():
 e=rows(O/"query_execution.jsonl")
 if len(e)!=2:raise RuntimeError("R16_INCOMPLETE")
 write_json(O/"bounded_raw_access_dispositions.json",dict(task=T,epoch_id="SS-E02",at=now(),
    planned=2,completed=2,http_requests=len(rows(O/"http_ledger.jsonl")),
    successful_public_PDF=sum(r.get("status")=="available" and r.get("valid_PDF_magic") is True for r in e),
    raw_dispositions=e,scientific_originals_A3_verified=0,chemical_reactions_qualified=0,
    actual_fresh_holdout=0,assay_site_stereo_not_read=True,
    current_epoch_name_alias_graph_not_cleared=True,not_a_saturation_claim=True,
    no_credential_or_access_bypass=True,
    next_required="A3 original identity, permanent exposure pre-read, independent A4/A5 science + A6 only if valid lawful original"))
 print(json.dumps(dict(checked=2,http=len(rows(O/"http_ledger.jsonl")),valid_PDF=sum(r.get("valid_PDF_magic") is True for r in e))),flush=True)
if __name__=="__main__":
 import sys
 if len(sys.argv)!=2 or sys.argv[1] not in ("pre","run","finish"):raise SystemExit("pre|run|finish")
 {"pre":pre,"run":run,"finish":finish}[sys.argv[1]]()

