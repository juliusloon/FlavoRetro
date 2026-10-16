from pathlib import Path
import json,hashlib
from scripts.operate import write
from scripts.task016_p7_orchestrate import now,role_manifest,verify_stage_chain
R=Path.cwd();B=R/"outputs/task016-p7/v1";O=B/"governance/named_exposure_gate_v1";A=B/"governance/named_exposure_gate_A8_v4";T="TASK-016-P7"
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,obj):
 assert not p.exists(),str(p);write(T,str(p.relative_to(R)),json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
r=json.loads((A/"role_A8_manifest.json").read_text())
n=0
for key in ("input_manifest_sha","output_file_sha","input_file_sha256","output_file_sha256"):
 v=r.get(key)
 if isinstance(v,dict):
  for rel,d in v.items():
   assert sh(R/rel)==d,rel;n+=1
v=json.loads((A/"A8_independent_named_gate_validation.json").read_text())
assert v["counts"]["passed"]==20 and len(v["checks"])==20 and all(x["status"]=="passed" for x in v["checks"]) and v["passed"] is True and v["production_documentary_gate_ready"] is True
reqold=O/"future_G7_documentary_requirement.v2.json";req=json.loads(reqold.read_text())
codes=[R/f"scripts/task016_p7_named_exposure_gate_v{i}.py" for i in range(1,5)]
deps=json.loads((O/"strict_role_revision_v3_preregistration.json").read_text())["dependency_files_sha256"]
req.update(created_at=now(),supersedes_requirement_path=str(reqold.relative_to(R)),supersedes_requirement_sha256=sh(reqold),validator_path="scripts/task016_p7_named_exposure_gate_v4.py",validator_sha256=sh(codes[-1]),call="validate_final_panel",implementation_files_sha256={**deps,**{str(p.relative_to(R)):sh(p) for p in codes}},independent_A8_engineering_review={"path":str((A/"role_A8_manifest.json").relative_to(R)),"sha256":sh(A/"role_A8_manifest.json"),"tests":20,"passed":20,"failed":0,"bounded_engineering_only":True},actual_G7_writer_integrated=False,actual_official_identity_comparisons_completed=0,production_floor_cannot_be_disabled=True)
p=O/"future_G7_documentary_requirement.v4.json";put(p,req)
old=B/"epochs/SS-E02/epoch_state.v5.json";state=json.loads(old.read_text())
stages=list((B/"SS/E02/stages").rglob("*.json"))
stagebind={str(p.relative_to(R)):sh(p) for p in stages}
for p in stages:verify_stage_chain(p,sh(p))
counts={f"G{i}":sum(json.loads(p.read_text())["stage"].startswith(f"G{i}_") for p in stages) for i in range(2,7)}
state.update(timestamp=now(),as_of=now(),previous_state_path=str(old.relative_to(R)),previous_sha256=sh(old),status="G4_frozen_R8_G6_zero_admitted_R9_raw_access_in_progress",stage_sha256=stagebind,registered_stage_counts=counts,future_G7_name_exposure_requirement={"path":str(p.relative_to(R)),"sha256":sh(p)} if False else {"path":str((O/"future_G7_documentary_requirement.v4.json").relative_to(R)),"sha256":sh(O/"future_G7_documentary_requirement.v4.json")},named_exposure_A8_review="v4 bounded engineering 20pass0fail; no actual identity qualification",named_exposure_actual_identity_comparisons=0,R8_sources_processed=2,R8_source_admitted=0,R8_source_outside_scope=1,R8_source_reaction_deferred=1,prospective_full_qualification_policy={"path":"outputs/task016-p7/v1/governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json","sha256":sh(B/"governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json")})
new=B/"epochs/SS-E02/epoch_state.v6.json";put(new,state)
oldc=B/"epochs/C-E02/epoch_state.v8.json";cs=json.loads(oldc.read_text())
cs.update(timestamp=now(),previous_state_path=str(oldc.relative_to(R)),previous_sha256=sh(oldc),future_G7_name_exposure_requirement=state["future_G7_name_exposure_requirement"],named_exposure_A8_review=state["named_exposure_A8_review"],named_exposure_actual_identity_comparisons=0,prospective_full_qualification_policy=state["prospective_full_qualification_policy"])
newc=B/"epochs/C-E02/epoch_state.v9.json";put(newc,cs)
m=role_manifest("A0","P7-named-exposure-gate-v4",[A/"role_A8_manifest.json",O/"all_role_outputs_revision_v4_preregistration.json"],[O/"future_G7_documentary_requirement.v4.json",new,newc,*codes],{"processed":20,"passed":20,"rejected":0,"pending":0},pointers=[{"path":str((A/"A8_independent_named_gate_validation.json").relative_to(R)),"sha256":sh(A/"A8_independent_named_gate_validation.json")}],errors=["Original A8 v1 5 failures and v3 2 failures preserved; corrected additive v4"],unprocessed=["All actual official name identity comparisons","Final G7 panel and writer integration"])
m.update(approval_type="agent_delegated",human_reviewed=False,HTTP=0,MCTS=0,fresh_admitted=0)
put(O/"role_A0_manifest.v4.json",m)
print(json.dumps({"A8_SHA_items_pass":n,"SS_stage_counts":counts,"G7_requirement":str((O/"future_G7_documentary_requirement.v4.json").relative_to(R)),"SS_state":str(new.relative_to(R)),"C_state":str(newc.relative_to(R)),"fresh":0}))
