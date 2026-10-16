"""R35: preserve full appended custody, restore exact originally frozen R12 inputs."""
import json,hashlib,fcntl
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import now,sha,load,lines,put
from scripts.task016_p7_c_e02_http import physical_attempts
from scripts.task016_p7_orchestrate import verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"governance/R35-frozen-input-exact-restoration-v1"
SUP=B/"governance/R33-prior-stage-exposure-supplement-v1/inventory_provenance.json"
R11=B/"SS/E02/fresh/SS-E02-R11-original-acquisition-v1"
OLDROLE=R11/"role_A2_raw_only_manifest.json"
R12G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
R12G6=R12G5.parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
def digest(b):return hashlib.sha256(b).hexdigest()
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 issues=load(SUP)["input_drift_issues"];assert len(issues)==2
 records=[]
 for i,x in enumerate(issues):
  p=Path(x["path"]);data=(ROOT/p).read_bytes()
  assert digest(data)==x["actual_SHA"]
  chunks=data.splitlines(keepends=True)
  matches=[n for n in range(1,len(chunks)) if digest(b"".join(chunks[:n]))==x["expected_SHA"]]
  assert len(matches)==1
  archive=O/("full_http_attempts_before_restore.jsonl" if p.name=="http_ledger.jsonl" else "full_raw_execution_before_restore.jsonl")
  assert not (ROOT/archive).exists()
  write(T,str(archive),data.decode("utf-8"));assert sha(archive)==x["actual_SHA"]
  records.append(dict(path=str(p),before_SHA=x["actual_SHA"],original_frozen_SHA=x["expected_SHA"],original_prefix_rows=matches[0],full_rows=len(chunks),full_archive_path=str(archive),full_archive_SHA=sha(archive),reason="Later raw-only SI completion appended one record to a live ledger that old G5 had already bound. Restore exact SHA-known original prefix after preserving full new ledger."))
 put(O/"precontract.json",dict(task=T,at=now(),approval_type="agent_delegated",human_reviewed=False,agent_role="A0",reason="Correct root's mutable-ledger append after old G5 freeze; raw objects and old frozen manifests remain byte-identical. Full appended records are sealed and separately referenced by R11 custody v2.",records=records,old_role_path=str(OLDROLE),old_role_SHA=sha(OLDROLE),protected_frozen_manifests_SHA={str(p):sha(p) for p in (R12G5,R12G6)},acceptance=["Both restored files exactly equal old stage SHA, never an inferred rewrite","Full before-restore bytes remain archived","All 11 R11 physical HTTP retained and independently deduplicated","R12 G5/G6 verifies again","R34 G5/G6 stays valid"],stop_conditions=["Any prefix missing or ambiguous","Archive SHA not identical","Physical source count or bytes change","Frozen manifest hash changes"],no_HTTP=True,no_science_read=True,no_MCTS=True))
 print(json.dumps(dict(exact_original_prefixes_verified=2,full_ledgers_archived=2)))
def restore():
 c=load(O/"precontract.json")
 with (ROOT/B/"source_budget_acquisition.lock").open("a+") as fd:
  fcntl.flock(fd.fileno(),fcntl.LOCK_EX)
  try:
   before=physical_attempts();before_keys={(r["url"],r["started_at"],r["path"],r["sha256"],r["bytes"]) for r in before}
   for x in c["records"]:
    p=Path(x["path"]);a=Path(x["full_archive_path"])
    assert sha(p)==x["before_SHA"] and sha(a)==x["full_archive_SHA"]
    pieces=(ROOT/a).read_bytes().splitlines(keepends=True)
    prefix=b"".join(pieces[:x["original_prefix_rows"]]);assert digest(prefix)==x["original_frozen_SHA"]
    write(T,str(p),prefix.decode("utf-8"));assert sha(p)==x["original_frozen_SHA"]
   for p,h in c["protected_frozen_manifests_SHA"].items():assert sha(Path(p))==h
   stages=[R12G5,R12G6,B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G5_FRESH_HOLDOUT_ACQUIRE.json",B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G6_IDENTITY_STRUCTURE_ADMIT.json"]
   for p in stages:verify_stage_chain(ROOT/p,sha(p))
   after=physical_attempts();after_keys={(r["url"],r["started_at"],r["path"],r["sha256"],r["bytes"]) for r in after}
   assert before_keys==after_keys
   original=load(OLDROLE)
   # Keep original role bytes as historical. New role binds final complete ledgers explicitly.
   role=dict(original)
   role.update(agent_role="A2",timestamp=now(),supersedes_role_path=str(OLDROLE),supersedes_role_SHA=sha(OLDROLE),supersession_reason="Seal final R11 complete custody in immutable archives; former mutable ledger paths restored to exact old G5 prefixes",restoration_contract_path=str(O/"precontract.json"),restoration_contract_SHA=sha(O/"precontract.json"),final_complete_custody_files={x["full_archive_path"]:x["full_archive_SHA"] for x in c["records"]},restored_frozen_input_files={x["path"]:x["original_frozen_SHA"] for x in c["records"]})
   for field in ("input_file_sha256","output_file_sha256","input_manifest_sha","output_file_sha"):
    if isinstance(role.get(field),dict):
     for x in c["records"]:
      if x["path"] in role[field]:role[field].pop(x["path"]);role[field][x["full_archive_path"]]=x["full_archive_SHA"]
   put(R11/"role_A2_raw_only_manifest.v2.json",role)
   put(O/"restoration_receipt.json",dict(task=T,agent_role="A0",at=now(),approval_type="agent_delegated",human_reviewed=False,restored_count=2,restored_original_SHA=True,full_before_bytes_preserved=True,all_source_physical_rows_unchanged=True,global_HTTP_before=len(before),global_HTTP_after=len(after),global_bytes_before=sum(r["bytes"] for r in before),global_bytes_after=sum(r["bytes"] for r in after),checked_stage_SHA={str(p):sha(p) for p in stages},frozen_manifest_mutation=False,original_role_SHA_preserved=sha(OLDROLE)==c["old_role_SHA"],new_R11_role_path=str(R11/"role_A2_raw_only_manifest.v2.json"),new_R11_role_SHA=sha(R11/"role_A2_raw_only_manifest.v2.json"),scientific_qualification_changed=False,fresh_admitted=0))
   event(T,"R35_exact_frozen_input_restoration",restored=2,archived_full_ledgers=2,physical_HTTP=len(after))
   print(json.dumps(dict(restored=2,checked_stage_chains=4,physical_HTTP=len(after),all_physical_rows_preserved=True)))
  finally:fcntl.flock(fd.fileno(),fcntl.LOCK_UN)
if __name__=="__main__":
 import sys
 {"pre":pre,"restore":restore}[sys.argv[1]]()
