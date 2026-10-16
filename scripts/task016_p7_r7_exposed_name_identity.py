"""P7 R7 authoritative chemical NAME identity scout for 28 already-exposed hypotheses.

Not fresh holdout acquisition, not article/reaction evidence. Registrations and
HTTP are byte-preserved with SHA and the shared source budget lock.
"""
import fcntl, hashlib, json, re, sys, urllib.parse, urllib.request, urllib.error
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_c_e02_http import NoRedirect,physical_attempts,budget
TASK="TASK-016-P7"
B=Path("outputs/task016-p7/v1")
OUT=B/"governance/P7-R7-authoritative-exposed-name-resolution-v1"
RAW=Path("data/raw/task016-p7/governance/P7-R7-authoritative-exposed-name-resolution-v1")
SOURCES=[
 ("SS","pre_G4",B/"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_unverified_name_exposures.jsonl"),
 ("C","pre_G4",B/"C/E02/pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl"),
 ("C","post_G4",B/"C/E02/post_scope_internal_hypotheses/v1/permanent_name_hypothesis_exposure.jsonl")]
INP=[p for _,_,p in SOURCES]+[
 B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v2/A6_full_alias_union_dispositions.json",
 B/"report_snapshots/progress-v18.json"]
CAP=256*1024
LOCK=ROOT/B/"source_budget_acquisition.lock"
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
 h=hashlib.sha256()
 with (ROOT/p).open("rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()] if (ROOT/p).exists() else []
def save(p,obj):
 path=OUT/p
 if (ROOT/path).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS "+str(path))
 write(TASK,str(path),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
def append(p,obj):
 path=OUT/p
 content=(ROOT/path).read_text() if (ROOT/path).exists() else ""
 write(TASK,str(path),content+json.dumps(obj,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n")
def snapshot_guard(plan):
 for p,s in plan["inputs_SHA256"].items():
  if sha(Path(p))!=s:raise RuntimeError("FROZEN_NAME_EXPOSURE_DRIFT "+p)
 if plan["task"]!=TASK or plan["fresh_scientific_eligibility"] is not False:raise RuntimeError("BAD_PLAN")
def plan():
 if (ROOT/OUT).exists():raise RuntimeError("ALREADY_PLANNED")
 alln=defaultdict(list)
 for fam,epoch_phase,path in SOURCES:
  for row in rows(path):
   n=row.get("acceptor_name_literal") or row.get("literal_name")
   if not isinstance(n,str) or not n.strip():raise RuntimeError("BAD_EXPOSED_NAME")
   if row.get("future_fresh_eligible") is not False:raise RuntimeError("EXPOSURE_NOT_EXCLUDED")
   if row.get("source_scientific_qualified") is True:raise RuntimeError("UNEXPECTED_VERIFIED_NAME")
   alln[n.strip().casefold()].append({"family":fam,"phase":epoch_phase,"exposure_id":row["exposure_id"],
                                     "source_file":str(path)})
 assert sum(len(v) for v in alln.values())==28 and len(alln)==27
 queries=[]
 for i,(name,refs) in enumerate(sorted(alln.items()),1):
  url="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"+urllib.parse.quote(name,safe="")+"/property/CanonicalSMILES,IsomericSMILES,InChIKey/JSON"
  queries.append({"query_id":"R7-EXPOSED-NAME-%03d"%i,"name":name,"url":url,
      "route":"PubChem_PUGREST_exact_name_property","kind":"metadata",
      "object_limit":CAP,"max_attempts_per_URL":2,"recovery_redirect":False,
      "exposure_hypotheses":refs,"research_fresh_candidate":False})
 with LOCK.open("a+") as handle:
  fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
  global_current=physical_attempts()
  if len(global_current)+len(queries)>8000:raise RuntimeError("GLOBAL_HTTP_BUDGET_CAP")
  budget(global_current,"metadata",CAP)
  for q in queries:
   if sum(x["url"]==q["url"] for x in global_current)>=2:raise RuntimeError("URL_ALREADY_EXHAUSTED")
  before={"HTTP":len(global_current),"bytes":sum(x["bytes"] for x in global_current)}
  fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
 save("query_plan.json",{"task":TASK,"timestamp":now(),"approval_type":"agent_delegated",
   "inputs_SHA256":{str(p):sha(p) for p in INP},
   "queries":queries,"planned":27,"exposed_hypotheses":28,
   "source_domains":["SS","C"],"historically_exposed_only":True,
   "non_fresh_registration":True,"budget_before":before,
   "new_science_source_read":False,"fresh_scientific_eligibility":False,
   "source_identity_not_reaction_identity":True,
   "no_retries_no_automatic_redirects":True,"no_guess_on_ambiguous_CID":True})
 print(json.dumps({"status":"planned","unique_names":len(queries),"exposure_records":28,"budget_before":before}))
def acquire(q,plan_sha):
 with LOCK.open("a+") as handle:
  fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
  history=physical_attempts()
  budget(history,"metadata",CAP)
  count=sum(x["url"]==q["url"] for x in history)
  if count>=2:raise RuntimeError("URL_TWO_ATTEMPTS_EXCEEDED")
  id=q["query_id"];raw=RAW/(id+".attempt-"+str(count+1)+".metadata")
  if (ROOT/raw).exists():raise RuntimeError("IMMUTABLE_RAW_EXISTS")
  attempt={"query_id":id,"name":q["name"],"url":q["url"],"batch_id":"P7-R7-exposed-name-resolution-v1",
      "kind":"metadata","scope":"permanent_prior_exposure_alias_graph_only","registered_at":now(),
      "planned_query_SHA256":plan_sha,"body_max_bytes":CAP,
      "prior_URL_attempts":count,"no_redirects":True,"no_automatic_retries":True}
  append("request_preregistration.jsonl",attempt)
  opener=urllib.request.build_opener(NoRedirect)
  start=now();content=b"";status=None;err=None;headers={}
  try:
   req=urllib.request.Request(q["url"],headers={"User-Agent":"FlavoRetro-P7-source-governance/1.0","Accept":"application/json"})
   with opener.open(req,timeout=25) as resp:
    status=resp.status; headers={k:v for k,v in resp.headers.items() if k.lower() in ("content-type","content-length","date","location")}
    content=resp.read(CAP+1)
    if len(content)>CAP:raise RuntimeError("RAW_RESPONSE_CAP_EXCEEDED")
  except urllib.error.HTTPError as exc:
   status=exc.code;headers={k:v for k,v in exc.headers.items() if k.lower() in ("content-type","content-length","date","location")}
   content=exc.read(CAP+1)
   if len(content)>CAP:err="HTTP_ERROR_BODY_CAP";content=content[:CAP]
   else:err="HTTP "+str(status)
  except Exception as exc:
   err=type(exc).__name__+": "+str(exc)
  if (ROOT/raw).exists():raise RuntimeError("RAW_PATH_EXISTS_AFTER_HTTP")
  (ROOT/raw).parent.mkdir(parents=True,exist_ok=True)
  (ROOT/raw).write_bytes(content)
  file_sha=sha(raw)
  event(TASK,"raw_bytes",path=str(raw),sha256=file_sha,bytes=len(content),role="metadata",phase="exposed_name_resolution")
  ledger={"query_id":id,"batch_id":"P7-R7-exposed-name-resolution-v1",
    "name":q["name"],"url":q["url"],"kind":"metadata",
    "started_at":start,"finished_at":now(),"status_code":status,
    "bytes":len(content),"path":str(raw),"sha256":file_sha,
    "headers":headers,"error":err,"phase":"exposed_name_resolution",
    "scientific_chemical_original_read":False,"fresh_eligible":False,"evidence_eligible":False}
  append("http_ledger.jsonl",ledger)
  event(TASK,"source_http",**ledger)
  fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
 return ledger
def execute():
 plan_doc=load(OUT/"query_plan.json");snapshot_guard(plan_doc);plan_sha=sha(OUT/"query_plan.json")
 terminal={r["query_id"] for r in rows(OUT/"query_execution.jsonl")}
 for q in plan_doc["queries"]:
  if q["query_id"] in terminal:continue
  r=acquire(q,plan_sha)
  pointers=[];parser_error=None
  if r["status_code"]==200 and r["error"] is None:
   try:
    payload=load(Path(r["path"]))
    props=payload.get("PropertyTable",{}).get("Properties",[])
    if not isinstance(props,list):raise ValueError("NOT_COMPOUND_PROPERTY_LIST")
    for p in props:
     cid=p.get("CID")
     if not isinstance(cid,int):continue
     pointers.append({"CID":cid,"InChIKey":p.get("InChIKey"),
       "CanonicalSMILES":p.get("CanonicalSMILES"),
       "IsomericSMILES":p.get("SMILES") or p.get("IsomericSMILES"),
       "full_raw_SHA":r["sha256"]})
    if len({x["CID"] for x in pointers})!=len(pointers):raise ValueError("DUPLICATE_CID_IN_RESPONSE")
   except Exception as exc:parser_error=type(exc).__name__+": "+str(exc)
  disposition=("candidate_only_single_CID_pending_independent_identity" if len(pointers)==1 and parser_error is None else
      "multiple_CIDs_ambiguous_no_selection" if len(pointers)>1 else
      "parse_invalid_pending" if parser_error else "HTTP_unavailable_pending")
  terminal_row={"query_id":q["query_id"],"name":q["name"],"status_code":r["status_code"],
    "status":"terminal","error":r["error"],"parse_error":parser_error,
    "raw":{"path":r["path"],"sha256":r["sha256"],"bytes":r["bytes"]},
    "returned_unique_CIDs":len(pointers),"property_identity_candidates":pointers,
    "disposition":disposition,"scientific_structure_identity_certified":False,
    "fresh_eligible":False,"run_at":now()}
  append("query_execution.jsonl",terminal_row)
  print(json.dumps({"q":q["query_id"],"status":r["status_code"],"nCID":len(pointers),
    "disposition":disposition},ensure_ascii=False),flush=True)
def finish():
 plan_doc=load(OUT/"query_plan.json");snapshot_guard(plan_doc)
 q=plan_doc["queries"];exe=rows(OUT/"query_execution.jsonl");ledger=rows(OUT/"http_ledger.jsonl")
 if len(exe)!=len(q) or len(ledger)!=len(q) or len(q)!=27:raise RuntimeError("PLAN_EXECUTION_NOT_CONSERVED")
 if {x["query_id"] for x in exe}!={x["query_id"] for x in q} or len({x["query_id"] for x in exe})!=27:raise RuntimeError("QUERY_IDS_DIFF")
 if {x["query_id"] for x in ledger}!={x["query_id"] for x in q}:raise RuntimeError("HTTP_LEDGER_DIFF")
 total=0
 for r in ledger:
  path=Path(r["path"])
  if sha(path)!=r["sha256"] or (ROOT/path).stat().st_size!=r["bytes"]:raise RuntimeError("RAW_SHA_SIZE_DRIFT")
  total+=r["bytes"]
 with LOCK.open("a+") as h:
  fcntl.flock(h.fileno(),fcntl.LOCK_EX)
  current=physical_attempts()
  nowbudget={"HTTP":len(current),"bytes":sum(r["bytes"] for r in current)}
  fcntl.flock(h.fileno(),fcntl.LOCK_UN)
 if nowbudget["HTTP"]>8000 or nowbudget["bytes"]>8*1024**3:raise RuntimeError("HARD_BUDGET_EXCEEDED")
 n_single=sum(x["disposition"].startswith("candidate_only_single_CID") for x in exe)
 n_multi=sum(x["disposition"].startswith("multiple_CIDs") for x in exe)
 result={"task":TASK,"role":"A6_known_exposed_name_identity_scout",
  "timestamp":now(),"plan_SHA256":sha(OUT/"query_plan.json"),
  "counts":{"planned_unique_names":27,"permanent_exposure_hypothesis_records":28,
    "terminal":27,"physical_HTTP":len(ledger),"raw_bytes":total,"single_CID_candidate_only":n_single,
    "ambiguous_multiple_CIDs":n_multi,"HTTP_or_parse_pending":27-n_single-n_multi,
    "authoritatively_cross_verified_name_structures":0,
    "new_scientific_holdout":0,"new_MCTS":0},
  "current_global_physical_budget":nowbudget,
  "fully_frozen_known_exposure_names_only":True,
  "fresh_eligible":False,"human_reviewed":False,"independent_chemical_validation":False,
  "no_scientific_article_content_read":True,
  "no_name_resolved_to_fresh_or_scope_change":True,
  "input_SHA":plan_doc["inputs_SHA256"],
  "raw_ledger_SHA256":sha(OUT/"http_ledger.jsonl"),
  "query_execution_SHA256":sha(OUT/"query_execution.jsonl"),
  "unresolved":["official CID candidate is not independent structure/name confirmation",
   "28 preexisting exposures stay permanent even if the synonym/graph record is unresolved",
   "source/reaction transitive closure and G5 science extraction remain pending"]}
 save("disposition_summary.json",result)
 print(json.dumps({"status":"complete","counts":result["counts"],
   "global_after":nowbudget},ensure_ascii=False))
if __name__=="__main__":
 {"plan":plan,"execute":execute,"finish":finish}[sys.argv[1]]()
