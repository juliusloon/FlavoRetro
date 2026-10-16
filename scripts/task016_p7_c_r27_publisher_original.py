"""C-E02 R27 exact publisher-advertised original PDF/HTML access for Gentiana
direct-C6 primary study. Never retried known 403 endpoints or followed redirects.
"""
import json,hashlib,uuid,fcntl,urllib.request,urllib.error,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R27-publisher-original-access-v1"
RAW=Path("data/raw/task016-p7/C/E02/C-E02-R27-publisher-original-access-v1")
G4=B/"C/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
A6=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1/A6/three_original_science_scope_dispositions.json"
LOCK=B/"source_budget_acquisition.lock"
URLS=[
("gentiana_publisher_pdf","https://febs.onlinelibrary.wiley.com/doi/pdfdirect/10.1016/j.febslet.2014.11.045","article_version"),
("gentiana_sciencedirect_original","https://www.sciencedirect.com/science/article/pii/S0014579314008618","article_version"),
]
def sha(p):return sha_file(ROOT/p)
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()] if (ROOT/p).exists() else []
def put(p,x):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_ALREADY_EXISTS")
 write(T,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def append(p,x):
 write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n")
def urlkey(url):
 p=urllib.parse.urlsplit(url)
 return ((p.hostname or "").casefold(),urllib.parse.unquote(p.path).rstrip("/"),tuple(sorted(urllib.parse.parse_qsl(p.query,keep_blank_values=True))))
def stats(a):
 return dict(HTTP=len(a),bytes=sum(x["bytes"] for x in a),article_versions=sum(x.get("kind",x.get("role")) in ("article_version","xml","original_pdf") for x in a))
def check_epoch():
 assert verify_stage_chain(ROOT/G4,sha(G4))["stage"]=="G4_SCOPE_FREEZE"
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 assert "10.1016/j.febslet.2014.11.045" in read(A6)["new_direct_C6_source_DOIs"]
 assert not (ROOT/B/"epochs/C-E02/incomplete_decision.json").exists()
def pre():
 if (ROOT/O).exists():raise RuntimeError("R27_EXISTS")
 check_epoch()
 with (ROOT/LOCK).open("a+") as f:
  fcntl.flock(f.fileno(),fcntl.LOCK_EX)
  old=physical_attempts()
  plans=[dict(query_id=f"C-R27-{i:02d}",source_id="DOI:10.1016/j.febslet.2014.11.045",
    source_title="Identification of the glucosyltransferase that mediates direct flavone C-glucosylation in Gentiana triflora",
    URL_discovery_type="actual official publisher direct article URL from public publisher index; not invented resource",
    route=k,url=url,kind=kind,limit_bytes=6*1024**2,
    old_exact_URL_attempts=sum(urlkey(x["url"])==urlkey(url) for x in old),
    phase="fresh",family="C",epoch_id="C-E02",scientific_exposure_already_known=True)
     for i,(k,url,kind) in enumerate(URLS,1)]
  initial=stats(old)
  fcntl.flock(f.fileno(),fcntl.LOCK_UN)
 inp=[G4,G5,A6,Path("scripts/task016_p7_c_r27_publisher_original.py")]
 put(O/"precontract.json",dict(task=T,family="C",epoch_id="C-E02",
  at=now(),approval_type="agent_delegated",human_reviewed=False,
  source_identity="DOI:10.1016/j.febslet.2014.11.045",already_exposed_public_web_source=True,
  citation_bridge_A6_sha=sha(A6),
  old_failed_publisher_URLs_not_retried=True,no_login_or_access_bypass=True,
  two_exact_real_advertised_publisher_links=True,
  budget_before=initial,batch_budget=dict(HTTP=2,bytes=12*1024**2,article_versions=2),
  raw_only=True,publication_original_scientific_body_not_read=True,
  no_redirect_follow=True,no_retry=True,no_fresh_admission=True,
  input_sha={str(p):sha(p) for p in inp}))
 put(O/"query_plan.json",dict(task=T,at=now(),queries=plans,planned=2,precontract_sha=sha(O/"precontract.json")))
 print(json.dumps(dict(registered=2,global_HTTP=initial["HTTP"],old_counts=[x["old_exact_URL_attempts"] for x in plans])),flush=True)
def req(q):
 if q not in read(O/"query_plan.json")["queries"]:raise RuntimeError("QUERY_NOT_IN_PLAN")
 for p,v in read(O/"precontract.json")["input_sha"].items():
  if sha(Path(p))!=v:raise RuntimeError("INPUT_DRIFT")
 uri=urllib.parse.urlsplit(q["url"])
 if uri.scheme!="https" or uri.hostname not in ("febs.onlinelibrary.wiley.com","www.sciencedirect.com"):raise RuntimeError("HOST_WRONG")
 with (ROOT/LOCK).open("a+") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX)
  try:
   check_epoch()
   old=physical_attempts();prior=[x for x in old if urlkey(x["url"])==urlkey(q["url"])]
   if len(prior)>=2 or any(x.get("status_code") in (401,403,429) for x in prior):
    return dict(skipped="PREVIOUS_ACCESS_DENIAL_OR_CAP2")
   cur=stats(old);fam=stats([x for x in old if "C" in Path(x.get("path") or "").parts])
   if cur["HTTP"]+1>8000 or cur["bytes"]+q["limit_bytes"]>8*1024**3 or cur["article_versions"]+1>400:raise RuntimeError("GLOBAL_BUDGET")
   if fam["HTTP"]+1>2500 or fam["bytes"]+q["limit_bytes"]>2*1024**3 or fam["article_versions"]+1>120:raise RuntimeError("C_BUDGET")
   if len(rows(O/"http_ledger.jsonl"))>=2:raise RuntimeError("BATCH_LIMIT")
   aid="C-E02-R27-"+uuid.uuid4().hex;start=now()
   append(O/"physical_request_preregistration.jsonl",dict(attempt_id=aid,query_id=q["query_id"],
    source_id=q["source_id"],url=q["url"],kind="article_version",registered_at=start,
    global_before=cur,C_before=fam,old_canonical_attempts=len(prior),
    precontract_SHA=sha(O/"precontract.json"),plan_SHA=sha(O/"query_plan.json"),
    no_auth_bypass=True,no_redirect_follow=True,byte_cap=q["limit_bytes"]))
   data=b"";code=None;error=None;final=None;response=None
   try:
    request=urllib.request.Request(q["url"],headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 public academic research","Accept-Encoding":"identity"})
    try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=30)
    except urllib.error.HTTPError as e:response=e;error="HTTP_"+str(e.code)
    code=response.code;final=response.geturl();data=response.read(q["limit_bytes"]+1)
    if len(data)>q["limit_bytes"]:data=data[:q["limit_bytes"]];error="SIZE_CAP"
    if final!=q["url"] or 300<=code<400:error="NO_FOLLOW"
   except Exception as e:error=type(e).__name__+":"+str(e)[:120]
   finally:
    if response is not None:response.close()
   raw=RAW/(aid+".article_version");p=ROOT/raw;p.parent.mkdir(parents=True,exist_ok=True)
   p.write_bytes(data);p.chmod(0o444);event(T,"write_binary",path=str(raw),before=None,after=sha(raw),bytes=len(data))
   pdf=data.startswith(b"%PDF-")
   html_present=b"<html" in data[:1000].lower() or b"<!doctype html" in data[:1000].lower()
   valid=bool(code==200 and not error and (pdf or html_present))
   r=dict(attempt_id=aid,query_id=q["query_id"],source_id=q["source_id"],url=q["url"],
    kind="article_version",role="article_version",phase="fresh",epoch_id="C-E02",
    batch_id="C-E02-R27-publisher-original-access-v1",started_at=start,finished_at=now(),
    status_code=code,final_url=final,status="available" if valid else "failed",error=error,
    bytes=len(data),path=str(raw),sha256=sha(raw),PDF_magic=pdf,HTML_magic=html_present,
    already_public_web_science_exposed=True,body_not_read=True,
    redistributable=False,license="pending_original_custody",automatic_redirect=False)
   append(O/"http_ledger.jsonl",r);event(T,"source_http",**r);return r
  finally:fcntl.flock(h.fileno(),fcntl.LOCK_UN)
def run():
 for q in read(O/"query_plan.json")["queries"]:
  if any(z["query_id"]==q["query_id"] for z in rows(O/"query_execution.jsonl")):continue
  r=req(q)
  append(O/"query_execution.jsonl",dict(query_id=q["query_id"],status=r.get("status"),
   HTTP_status=r.get("status_code"),bytes=r.get("bytes"),path=r.get("path"),sha256=r.get("sha256"),
   PDF=r.get("PDF_magic"),HTML=r.get("HTML_magic"),error=r.get("error",r.get("skipped")),no_chemical_read=True))
  print(json.dumps(dict(query=q["query_id"],http=r.get("status_code"),bytes=r.get("bytes"),PDF=r.get("PDF_magic"),error=r.get("error",r.get("skipped")))),flush=True)
def finish():
 rr=rows(O/"query_execution.jsonl");assert len(rr)==2
 put(O/"lawful_publisher_original_access_disposition.json",dict(task=T,at=now(),queries=rr,
  attempted=len(rows(O/"http_ledger.jsonl")),valid_pdf_count=sum(r.get("status")=="available" and r.get("PDF") for r in rr),
  valid_html_count=sum(r.get("status")=="available" and r.get("HTML") for r in rr),
  no_copyright_or_auth_bypass=True,old_failed_URLs_preserved=True,
  scientific_qualification_pending_primary_full_original=True,fresh=0))
 print(json.dumps(dict(HTTP=len(rows(O/"http_ledger.jsonl")),PDF_good=sum(bool(r.get("PDF") and r.get("status")=="available") for r in rr))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"finish":finish}[sys.argv[1]]()

