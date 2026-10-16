"""Adapt fixed SS physical-attempt schemas to shared budget ledger; never fetch."""
from pathlib import Path
from datetime import datetime,timezone
import json,fcntl
from scripts.operate import write,event
from scripts.task016_p7_ss_e02_metadata_r1_chatgpt_v1 import request_url
from scripts.task016_p7_orchestrate import ROOT,TASK,sha_file,ContractError
from scripts.task016_p7_c_e02_http import BASE,physical_attempts,immutable_json
O=BASE/"SS/E02/fresh/SS-E02-R1R2-budget-normalization-v2"
S="scripts/task016_p7_ss_e02_budget_normalization_v2.py"
BATCHES=["SS-E02-R1-metadata","SS-E02-R2-metadata","SS-E02-R2-PMC11125054-original"]
F=BASE/"SS/E02/fresh"
def now():return datetime.now(timezone.utc).isoformat()
def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x]
def inputs():return [F/b/n for b in BATCHES for n in ("physical_attempts.jsonl","raw_manifest.json","query_plan.json")]+[ROOT/"scripts/task016_p7_ss_e02_metadata_r1_chatgpt_v1.py",BASE/"SS/E02/fresh/SS-E02-R1R2-budget-normalization-v1/actual_failure.json"]
def pre():
 immutable_json(O/"preregistration.json",dict(task=TASK,agent_role="A0 physical budget format adapter",
  timestamp=now(),approval_type="agent_delegated",input_file_sha={str(p.relative_to(ROOT)):sha_file(p) for p in inputs()},
  code_sha256=sha_file(ROOT/S),physical_key=["url","started_at","path"],
  expected_source_rows=8,expected_bytes=251354,
  requirement="all physical bytes match immutable raw manifests and preregistered URL; duplicate events conserve bytes",
  error_policy="fail closed on missing status/type/time/url/byte/SHA, preserve original schemas",
  new_HTTP=0,new_MCTS=0,no_backdating=True,shared_budget_inclusion="add normalized http_ledger.jsonl; no source_http replay event"))
 print("normalization preregistered")
def run():
 reg=load(O/"preregistration.json")
 assert sha_file(ROOT/S)==reg["code_sha256"]
 for p,h in reg["input_file_sha"].items():assert sha_file(ROOT/p)==h,p
 records=[];checks=[]
 for b in BATCHES:
  d=F/b;manifest=load(d/"raw_manifest.json");plan=load(d/"query_plan.json")
  objects={x["path"]:x for x in manifest["objects"]}
  for r in rows(d/"physical_attempts.jsonl"):
   obj=objects[r["path"]]
   for k in ("path","bytes","sha256"):assert r[k]==obj[k],k
   p=ROOT/r["path"];assert p.stat().st_size==r["bytes"] and sha_file(p)==r["sha256"]
   q=r.get("query_id",r.get("attempt_id"))
   if "allowed_urls" in plan:assert r["url"]==plan["allowed_urls"][q]
   else:
    qs=[v for v in plan["queries"] if v["query_id"]==q]
    assert len(qs)==1
    assert r["url"]==request_url(qs[0])
   status=r.get("http_status",r.get("status"))
   assert isinstance(status,int) and isinstance(r["bytes"],int)
   records.append(dict(url=r["url"],started_at=r["started_at"],
    finished_at=r.get("ended_at"),path=r["path"],sha256=r["sha256"],bytes=r["bytes"],
    kind=obj["kind"],status_code=status,error=r.get("error"),
    task=TASK,family="SS",epoch_id="SS-E02",batch_id=b,phase="fresh",
    actual_late_normalized_at=now(),physical_request_reexecuted=False,
    finished_time_not_recorded_in_original=r.get("ended_at") is None,
    source_original_ledger_path=str((d/"physical_attempts.jsonl").relative_to(ROOT)),
    source_original_ledger_sha256=sha_file(d/"physical_attempts.jsonl"),
    original_fields_preserved_in_source_ledger=True))
   checks.append(dict(path=r["path"],raw_SHA_and_size=True,planned_URL_match=True))
 assert len(records)==reg["expected_source_rows"] and sum(x["bytes"] for x in records)==reg["expected_bytes"]
 with (BASE/"source_budget_acquisition.lock").open("a+") as lock:
  fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
  before=physical_attempts()
  index={(r["url"],r["started_at"],r["path"]):r for r in before}
  new=[]
  for r in records:
   key=(r["url"],r["started_at"],r["path"])
   if key in index:
    assert all(index[key][k]==r[k] for k in ("sha256","bytes"))
   else:new.append(r)
  out=O/"http_ledger.jsonl";assert not out.exists()
  write(TASK,str(out.relative_to(ROOT)),"".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in records))
  after=physical_attempts()
  assert len(after)==len(before)+len(new)
  assert sum(x["bytes"] for x in after)==sum(x["bytes"] for x in before)+sum(x["bytes"] for x in new)
  immutable_json(O/"normalization_validation.json",dict(task=TASK,timestamp=now(),
   before_HTTP=len(before),after_HTTP=len(after),newly_included_physical_HTTP=len(new),
   before_bytes=sum(r["bytes"] for r in before),after_bytes=sum(r["bytes"] for r in after),
   normalized_rows=len(records),raw_checks=checks,HTTP_actually_executed=0,MCTS=0,
   expected_conservation_passed=True,old_v13_collector_omitted_physical_attempts_schema=True,
   missing_finish_times_remain_null=True,original_ledgers_not_mutated=True,
   errors=[],scientific_eligibility_claim=False,human_reviewed=False))
  immutable_json(O/"role_A0_manifest.json",dict(task=TASK,timestamp=now(),agent_role="A0 physical source budget normalization",
   approval_type="agent_delegated",human_reviewed=False,input_manifest_sha=sha_file(O/"preregistration.json"),
   output_file_sha={str(p.relative_to(ROOT)):sha_file(p) for p in [out,O/"normalization_validation.json"]},
   counts=dict(processed=8,passed=8,rejected=0,pending=0),errors=[],unprocessed=[],
   read_holdout=False,read_model_outcome=False,no_scientific_content_read=True,HTTP=0,MCTS=0))
  event(TASK,"source_budget_normalization",rows=8,newly_included=len(new),not_source_http_event=True)
  print(json.dumps(dict(total_HTTP=len(after),total_bytes=sum(r["bytes"] for r in after),new_HTTP=0)))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
