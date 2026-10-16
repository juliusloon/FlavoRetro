"""Add missing role fields and late SS epoch registry without rewriting fixed stages."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,fcntl
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,sha_file,verify_stage_chain,role_manifest
from scripts.task016_p7_c_e02_http import BASE,immutable_json
O=BASE/"governance/SS_E02_late_registry_and_role_adapters_v1"
S=ROOT/"scripts/task016_p7_ss_e02_governance_repair_v1.py"
E=BASE/"epoch_ledger.jsonl"
G4=BASE/"SS/E02/stages/G4_SCOPE_FREEZE.json"
SM=BASE/"SS/E02/scope_manifest.json"
ST=sorted((BASE/"SS/E02/stages").rglob("G*.json"))
A8=BASE/"SS/E02_design/Petunia_A8_chatgpt_bounded_v1"
A6=BASE/"SS/E02/fresh/SS-E02-R2-PMC11125054-A6_scope_disposition"
N=BASE/"SS/E02/fresh/SS-E02-R1R2-budget-normalization-v3"
def now():return datetime.now(timezone.utc).isoformat()
def load(p):return json.loads(p.read_text())
def rel(p):return str(p.relative_to(ROOT))
def inputs():
 return list(dict.fromkeys([E,G4,SM,S]+ST+[A8/"role_A8_bounded_review_manifest.json",A8/"A8_pre_execution_manifest.json",A8/"A8_root_handoff.zh.md",
 A6/"role_A6_manifest.json",A6/"A6_pre_execution_manifest.json",A6/"A6_source_scope_disposition.json",
 N/"role_A0_manifest.json",N/"preregistration.json",N/"normalization_validation.json",
 BASE/"epochs/SS-E02/epoch_state.v3.json",
 BASE/"SS/E02_design/reference_discovery_r2/Petunia_A6_v1/role_A6_manifest.json",
 BASE/"SS/E02_design/reference_discovery_r2/Petunia_A6_v1/2_source_qualified_design_supports.jsonl"]))
def pre():
 for p in ST:verify_stage_chain(p,sha_file(p))
 immutable_json(O/"preregistration.json",dict(task=TASK,epoch_id="SS-E02",agent_role="A0 governance repair custodian",
  registered_at=now(),input_file_sha={rel(p):sha_file(p) for p in inputs()},
  expected_stages=7,original_role_schema_defects_retained=True,
  no_scope_or_stage_overwrite=True,late_registration_not_historical_transition=True,
  no_HTTP=True,no_MCTS=True,approval_type="agent_delegated",human_reviewed=False))
 print("7 stage-chain inputs preregistered")
def run():
 reg=load(O/"preregistration.json")
 for p,h in reg["input_file_sha"].items():assert sha_file(ROOT/p)==h,p
 assert len(ST)==7
 for p in ST:verify_stage_chain(p,sha_file(p))
 originalA8=load(A8/"role_A8_bounded_review_manifest.json")
 for p,h in load(A8/"A8_pre_execution_manifest.json")["frozen_inputs"].items():assert sha_file(ROOT/p)==h
 cases=[
 ("A8",A8/"role_A8_bounded_review_manifest.json",A8/"A8_pre_execution_manifest.json",[A8/"A8_root_handoff.zh.md"],
  dict(processed=12,passed=12,rejected=0,pending=0),originalA8["unprocessed"]),
 ("A6",A6/"role_A6_manifest.json",A6/"A6_pre_execution_manifest.json",
 [A6/"A6_source_scope_disposition.json",A6/"permanent_exposure_ledger_addendum.jsonl"],
 load(A6/"role_A6_manifest.json")["counts"],["no full molecular graph reconstruction; source-assay rejected for frozen scope"]),
 ("A0",N/"role_A0_manifest.json",N/"preregistration.json",
 [N/"normalization_validation.json",N/"http_ledger.jsonl"],
 dict(processed=8,passed=8,rejected=0,pending=0),[])]
 ptrs=[rel(G4),rel(BASE/"SS/E02_design/reference_discovery_r2/Petunia_A6_v1/role_A6_manifest.json"),
       rel(BASE/"SS/E02_design/reference_discovery_r2/Petunia_A6_v1/2_source_qualified_design_supports.jsonl")]
 for role,old,prepath,outs,counts,pending in cases:
  adapter=role_manifest("A0 additive schema adapter for original "+role,"SS-E02",
   [old,prepath,G4,SM],outs+[old],counts,pointers=ptrs+[rel(prepath)],
   errors=["Original role lacked some TASK section4.1 canonical fields; preserved and explicitly mapped here."],
   unprocessed=pending)
  adapter.update(original_role=role,original_role_path=rel(old),original_role_SHA=sha_file(old),
   original_role_timestamp=load(old).get("timestamp",load(old).get("time")),
   late_schema_completion=True,not_backdated=True,original_scientific_judgments_unchanged=True,
   not_a_new_independent_scientific_review=True,original_A8_nonblind=role=="A8",
   original_source_read_disclosures=load(old).get("direct_source_chemistry_read_occurred_by_A4_A5",False),
   HTTP=0,MCTS=0)
  immutable_json(O/(role+"_role_schema_adapter.json"),adapter)
 with (BASE/"source_budget_acquisition.lock").open("a+") as lock:
  fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
  oldb=E.read_bytes();assert hashlib.sha256(oldb).hexdigest()==reg["input_file_sha"][rel(E)]
  prior=[json.loads(x) for x in oldb.splitlines() if x]
  assert not any(r.get("epoch_id")=="SS-E02" and r.get("family")=="SS" for r in prior)
  write(TASK,rel(O/"epoch_ledger.before.jsonl"),oldb.decode())
  add=[]
  for p in ST:
   m=load(p);st=m["stage"]
   add.append(dict(task=TASK,family="SS",epoch_id="SS-E02",
    event_type="verified_existing_stage_registration",stage=st,status="active",
    stage_manifest_path=rel(p),stage_manifest_sha256=sha_file(p),
    original_manifest_created_at=m["timestamp"],registered_at=now(),
    registration_is_late=True,backdated=False,not_an_original_transition_record=True,
    prior_registry_gap=True,scope_manifest_path=rel(SM),scope_manifest_sha256=sha_file(SM),
    scope_guard_not_G9_registry_integrated=True,fresh_admitted=0,
    approval_type="agent_delegated",human_reviewed=False))
  text=oldb.decode()+"".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in add)
  write(TASK,rel(E),text)
  assert E.read_bytes().startswith(oldb)
  from scripts.task016_p7_ss_sources import require_acquisition_phase
  gate=require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
  immutable_json(O/"registry_repair_validation.json",dict(task=TASK,epoch_id="SS-E02",timestamp=now(),
   old_rows=len(prior),added_rows=7,after_rows=len(prior)+7,old_prefix_preserved=True,
   original_registry_gap_not_retroactively_passed=True,
   earlier_8_requests_not_through_shared_epoch_registry_gate=True,
   actual_shared_fresh_gate_now_passed=True,gate_evidence=gate,HTTP=0,MCTS=0,
   old_epoch_ledger_SHA=hashlib.sha256(oldb).hexdigest(),after_epoch_ledger_SHA=sha_file(E),
   G4_scope_unchanged=True,scientific_ABE_cells=0,fresh_admitted=0,metrics=None))
  state=load(BASE/"epochs/SS-E02/epoch_state.v3.json")
  state.update(timestamp=now(),previous_state_path="outputs/task016-p7/v1/epochs/SS-E02/epoch_state.v3.json",
   previous_sha256=sha_file(BASE/"epochs/SS-E02/epoch_state.v3.json"),
   current_registration="verified existing 7 stages, registered late; no historical transition backfill",
   registered_stage_counts=dict(G2=1,G3=1,G4=1,G5=3,G6=1),
   registry_repair_pointer=dict(path=rel(O/"registry_repair_validation.json"),sha256=sha_file(O/"registry_repair_validation.json")))
  immutable_json(BASE/"epochs/SS-E02/epoch_state.v4.json",state)
  outs=[*O.glob("*_role_schema_adapter.json"),O/"registry_repair_validation.json",BASE/"epochs/SS-E02/epoch_state.v4.json"]
  final=role_manifest("A0 governance registry repair","SS-E02",[O/"preregistration.json",O/"epoch_ledger.before.jsonl"],outs,
   dict(processed=10,passed=10,rejected=0,pending=0),pointers=ptrs,
   errors=["Original registry missing SS-E02, 3 roles had schema gaps; late additive repair does not erase either defect."],
   unprocessed=["fresh panels and G7+","source/global name-identity closure","formal runtime G9"])
  immutable_json(O/"role_A0_repair_manifest.json",final)
 print(json.dumps(dict(registered_stages=7,role_adapters=3,gate_passed=True,new_HTTP=0,G4_sha=sha_file(G4))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
