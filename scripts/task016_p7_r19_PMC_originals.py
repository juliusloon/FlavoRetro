"""TASK-016-P7 R18 official PMC original article custody, 8 bounded registered PMCID URLs.

No source chemistry, abstract, supplementary interpretation in A2. No unregistered
redirect, no login, retry, or source claim. G4 required before physical request.
"""
from pathlib import Path
import hashlib,json,uuid,fcntl,urllib.request,urllib.error,urllib.parse
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
from scripts.task016_p7_ss_sources import require_acquisition_phase
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"governance/R19-three-PMC-targeted-original-access-v1"
RAW=Path("data/raw/task016-p7/R19-three-PMC-targeted-original-access-v1")
LOCK=B/"source_budget_acquisition.lock"
SOURCES=[
 ("SS","PMC12611259","2025 Tomato pollen tube growth requires flavonol glycosylation: SlUGT79B-B candidate; public web body already exposed"),
 ("SS","PMC11974848","2025 Solanaceae organ-specific flavonol glycosides: possible preprint same scientific study as PMC12611259; alias closure required"),
 ("C","PMC11577821","2024 UGT708S6 from Dendrobium catenatum catalyzes flavonoid C-glycosides"),
]
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def lines(p):return [json.loads(t) for t in (ROOT/p).read_text().splitlines() if t.strip()] if (ROOT/p).exists() else []
def put(p,v):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE "+str(p))
 write(T,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def append(p,v):write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n")
def can(url):
 u=urllib.parse.urlsplit(url)
 return ((u.hostname or "").casefold(),urllib.parse.unquote(u.path).rstrip("/"),tuple(sorted(urllib.parse.parse_qsl(u.query,keep_blank_values=True))))
def budget(all_):
 return dict(HTTP=len(all_),bytes=sum(int(r.get("bytes",0)) for r in all_),
   article_versions=sum(r.get("kind",r.get("role")) in ("article_version","xml","original_pdf") for r in all_),
   attachments=sum(r.get("kind",r.get("role"))=="attachment" for r in all_))
def gate(fam):
 g4=B/f"{fam}/E02/stages/G4_SCOPE_FREEZE.json"
 a=verify_stage_chain(ROOT/g4,sha(g4))
 if a["stage"]!="G4_SCOPE_FREEZE" or a["family"]!=fam or a["epoch_id"]!=fam+"-E02":raise RuntimeError("G4_WRONG")
 ledger=lines(B/"epoch_ledger.jsonl")
 if not any(r.get("epoch_id")==fam+"-E02" and r.get("stage")=="G4_SCOPE_FREEZE" and r.get("status") in (None,"active") and r.get("stage_manifest_path")==str(g4) and r.get("stage_manifest_sha256")==sha(g4) for r in ledger):raise RuntimeError("G4_NOT_REGISTERED")
 if any(r.get("epoch_id")==fam+"-E02" and (r.get("status") in ("closed","complete","development_epoch_incomplete","invalidated") or r.get("event_type") in ("epoch_incomplete_decision","epoch_closed","epoch_complete")) for r in ledger):raise RuntimeError("EPOCH_TERMINAL")
 if fam=="SS":require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
 return dict(G4_path=str(g4),G4_SHA=sha(g4),current_scope_SHA=sha(B/f"{fam}/E02/scope_manifest.json"))
def pre():
 if (ROOT/O).exists():raise RuntimeError("R19_PREEXISTING")
 with (ROOT/LOCK).open("a+") as fd:
  fcntl.flock(fd.fileno(),fcntl.LOCK_EX)
  ga={fam:gate(fam) for fam in ("C","SS")}
  all_=physical_attempts();prior=budget(all_)
  source=[]
  for index,(fam,pmcid,title) in enumerate(SOURCES,1):
   url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pmcid+"/fullTextXML"
   n=sum(can(r["url"])==can(url) for r in all_)
   source.append(dict(query_id=f"R19-{index:02d}",family=fam,epoch_id=fam+"-E02",
    source_id=pmcid,PMCID=pmcid,title_selection_hint=title,
    url=url,kind="article_version",route="EuropePMC_documented_exact_PMCID_fullTextXML",
    object_limit=6*1024**2,source_original_read_permission=False,
    prior_exact_canonical_attempt_count=n,scope_gate=ga[fam],
    direct_citation_from_prior_source_or_public_PMC_listing=True,
    current_chemical_status="unknown_not_qualified",source_original_availability="unknown"))
  fcntl.flock(fd.fileno(),fcntl.LOCK_UN)
 inputfiles=[Path("scripts/task016_p7_r19_PMC_originals.py"),
  B/"epoch_ledger.jsonl",
  B/"exposure_ledger.jsonl",
  B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl",
  B/"SS/E02/stages/G4_SCOPE_FREEZE.json",
  B/"C/E02/stages/G4_SCOPE_FREEZE.json",
  B/"SS/E02/scope_manifest.json",B/"C/E02/scope_manifest.json"]
 put(O/"precontract.json",dict(task=T,round_id="R19-three-PMC-targeted-original-access-v1",
  created_at=now(),approval_type="agent_delegated",human_reviewed=False,
  phase="fresh",read_scope="raw-original-bytes-custody-only",
  selected_count=len(source),source_universe=source,
  input_SHA={str(p):sha(p) for p in inputfiles},
  global_budget_before=prior,
  batch_ceiling=dict(HTTP=3,bytes=3*6*1024**2,article_versions=3,attachments=0),
  official_API_documentation="existing SS R11 official /{PMCID}/fullTextXML template",
  not_guessed_publisher_SI_paths=True,automatic_retry=False,
  redirect_follow=False,old_URL_global_count_used=True,
  before_science_read_exposure_protection="any original science reading requires separate G5 preregistration and permanent exposure, including web-exposed sources; otherwise not fresh",
  historical_exposed_sources_not_promoted=True,missing_originals_not_source_absence=True,
  no_A3_identity_from_HTTP200=True,no_A4_A5_body_read=True,web_search_scientific_text_already_exposed_PMC12611259_and_PMC11974848=True,
  no_MCTS=True,scope_unchanged=True))
 put(O/"query_plan.json",dict(task=T,registered_at=now(),queries=source,planned=len(source),
  precontract_SHA=sha(O/"precontract.json")))
 print(json.dumps(dict(registered=3,global_before=prior["HTTP"],old_url_attempts=[(r["PMCID"],r["prior_exact_canonical_attempt_count"]) for r in source])),flush=True)
def get(q):
 if q not in load(O/"query_plan.json")["queries"]:raise RuntimeError("UNREGISTERED_URL")
 prior=load(O/"precontract.json")
 for p,h in prior["input_SHA"].items():
  if p.endswith("/epoch_ledger.jsonl"):continue
  if sha(Path(p))!=h:raise RuntimeError("PREREG_INPUT_SHA_DRIFT "+p)
 u=urllib.parse.urlsplit(q["url"])
 if (u.scheme,u.hostname,u.path)!=("https","www.ebi.ac.uk","/europepmc/webservices/rest/"+q["PMCID"]+"/fullTextXML"):raise RuntimeError("SOURCE_URL_MISMATCH")
 with (ROOT/LOCK).open("a+") as fd:
  fcntl.flock(fd.fileno(),fcntl.LOCK_EX)
  try:
   gate(q["family"])
   all_=physical_attempts();prev=[x for x in all_ if can(x["url"])==can(q["url"])]
   if len(prev)>=2 or any(x.get("status_code") in (401,403) for x in prev):
    return dict(query_id=q["query_id"],status="blocked_prior_URL_cap_or_access_denial",HTTP=0)
   cur=budget(all_);fam=budget([r for r in all_ if q["family"] in Path(r.get("path") or "").parts])
   projected=dict(HTTP=cur["HTTP"]+1,bytes=cur["bytes"]+q["object_limit"],article_versions=cur["article_versions"]+1)
   if projected["HTTP"]>8000 or projected["bytes"]>8*1024**3 or projected["article_versions"]>400:raise RuntimeError("GLOBAL_LIMIT")
   if fam["HTTP"]+1>2500 or fam["bytes"]+q["object_limit"]>2*1024**3 or fam["article_versions"]+1>120:raise RuntimeError("FAMILY_LIMIT")
   if len(lines(O/"http_ledger.jsonl"))>=3:raise RuntimeError("R19_BATCH_LIMIT")
   aid="R19-"+uuid.uuid4().hex;start=now()
   append(O/"physical_request_preregistration.jsonl",dict(attempt_id=aid,source_id=q["PMCID"],
      family=q["family"],epoch_id=q["epoch_id"],query_id=q["query_id"],url=q["url"],
      kind="article_version",registered_at=start,byte_cap=q["object_limit"],
      global_budget_before=cur,family_budget_before=fam,previous_same_canonical_URL=len(prev),
      precontract_SHA=sha(O/"precontract.json"),query_plan_SHA=sha(O/"query_plan.json"),
      no_auto_redirect=True,no_auto_retry=True))
   response=None;data=b"";status=None;err=None;final=None;headers={}
   try:
    req=urllib.request.Request(q["url"],headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 official public primary science access","Accept-Encoding":"identity"})
    try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=28)
    except urllib.error.HTTPError as e:response=e;err="HTTP_"+str(e.code)
    status=response.code;final=response.geturl()
    headers={k.lower():v for k,v in response.headers.items() if k.lower() in ("content-type","content-length","location","date")}
    data=response.read(q["object_limit"]+1)
    if len(data)>q["object_limit"]:data=data[:q["object_limit"]];err="OBJECT_CAP"
    if final!=q["url"] or 300<=status<400:err="NO_REDIRECT_FOLLOW"
   except Exception as e:err=type(e).__name__+":"+str(e)[:160]
   finally:
    if response is not None:response.close()
   path=RAW/(aid+".article_version");p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():raise RuntimeError("IMMUTABLE_RAW_COLLISION")
   p.write_bytes(data);p.chmod(0o444)
   event(T,"write_binary",path=str(path),before=None,after=sha(path),bytes=len(data))
   valid=bool(status==200 and err is None and (b"<article" in data[:700] or b"<!DOCTYPE article" in data[:700]))
   record=dict(attempt_id=aid,query_id=q["query_id"],source_id=q["PMCID"],family=q["family"],
     epoch_id=q["epoch_id"],url=q["url"],final_url=final,status_code=status,
     kind="article_version",role="article_version",phase="fresh",
     batch_id="R19-three-PMC-targeted-original-access-v1",started_at=start,finished_at=now(),
     status="available" if valid else "failed",error=err,
     bytes=len(data),path=str(path),sha256=sha(path),headers=headers,xml_magic=valid,
     scientific_body_content_read=False,original_publication_identity_not_verified=True,
     chemical_extracted=False,license="record pending from original XML front",
     no_access_bypass=True,automatic_redirect=False,recovery=False,current_fresh_eligible=False)
   append(O/"http_ledger.jsonl",record);event(T,"source_http",**record);return record
  finally:fcntl.flock(fd.fileno(),fcntl.LOCK_UN)
def run():
 qs=load(O/"query_plan.json")["queries"]
 for q in qs:
  if any(x["query_id"]==q["query_id"] for x in lines(O/"query_execution.jsonl")):continue
  try:r=get(q)
  except Exception as e:r=dict(query_id=q["query_id"],status="gate_error",HTTP=0,error=type(e).__name__+":"+str(e)[:160])
  append(O/"query_execution.jsonl",dict(query_id=q["query_id"],family=q["family"],PMCID=q["PMCID"],
   status=r.get("status"),HTTP=0 if r.get("HTTP")==0 else 1,
   HTTP_status=r.get("status_code"),xml_magic=r.get("xml_magic"),
   bytes=r.get("bytes"),raw_pointer={k:r.get(k) for k in ("path","sha256","bytes")},
   error=r.get("error"),raw_only_no_chemical_read=True))
  print(json.dumps(dict(PMCID=q["PMCID"],family=q["family"],status=r.get("status_code"),
     xml=r.get("xml_magic"),bytes=r.get("bytes"),error=r.get("error"))),flush=True)
def finish():
 qs=load(O/"query_plan.json")["queries"];e=lines(O/"query_execution.jsonl")
 if len(qs)!=len(e):raise RuntimeError("INCOMPLETE")
 success=[r for r in e if r["status"]=="available" and r["xml_magic"] is True]
 put(O/"raw_custody_summary.json",dict(task=T,round="R18",at=now(),
  planned=3,terminal=len(e),physical_HTTP=len(lines(O/"http_ledger.jsonl")),
  usable_original_XML=len(success),by_family={f:len([x for x in success if x["family"]==f]) for f in ("C","SS")},
  successful_sources=[dict(family=r["family"],pmcid=r["PMCID"],raw_pointer=r["raw_pointer"]) for r in success],
  errors=[r for r in e if r not in success],no_body_science_read=True,none_automatically_fresh=True,
  next_gate="Independent A3 original front identity, prior-exposure/G5 then independent A4/A5 and A6",
  source_saturation_claim=False))
 print(json.dumps(dict(originals=len(success),C=sum(r["family"]=="C" for r in success),
    SS=sum(r["family"]=="SS" for r in success),physical=len(lines(O/"http_ledger.jsonl")))),flush=True)
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"finish":finish}[sys.argv[1]]()

