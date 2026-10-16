from pathlib import Path
import json,fcntl,hashlib
from scripts.operate import write
from scripts.task016_p7_orchestrate import now,sha_file,freeze_stage_manifest,verify_stage_chain,role_manifest
R=Path.cwd();B=R/"outputs/task016-p7/v1";T="TASK-016-P7";O=B/"governance/SS_E02_R4_G5_metadata_binding_v1";Q=B/"SS/E02/fresh/SS-E02-R4-bibliographic-resolution-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"; EXPECTED="a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f"
def put(p,obj):
 assert not p.exists(),str(p);write(T,str(p.relative_to(R)),json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
def rel(p):return str(p.relative_to(R))
assert sha_file(G4)==EXPECTED
verify_stage_chain(G4,EXPECTED)
role=Q/"role_A3_final_manifest.v2.json"
assert sha_file(role)=="b1cc27b0fc78607eefee88598cfcc515a9eb0ac8126219007bb84cc89fc96782"
ledger=[json.loads(l) for l in (Q/"http_ledger.jsonl").read_text().splitlines() if l];assert len(ledger)==16
raw=[R/x["path"] for x in ledger]
for row,p in zip(ledger,raw):
 assert p.is_file() and sha_file(p)==row["sha256"] and p.stat().st_size==row["bytes"]
put(O/"preregistration.json",{"task_id":T,"agent_role":"A0 G5 documentary binding","approval_type":"agent_delegated","created_at":now(),"reason":"Bind completed R4 metadata-only identity acquisition to unchanged SS G4 before any future original scientific extraction; do not treat it as full scientific round or source admission.","input_file_sha256":{rel(G4):EXPECTED,rel(role):sha_file(role)},"counts":{"HTTP_previously_executed":16,"records":72,"clusters":39,"bibliographic_pass":29,"bibliographic_pending":10,"fresh":0},"acceptance":["Existing G4 chain unchanged","All16 raw SHA and sizes match","Append one actual G5 registration preserving ledger prefix","Future name-exposure production requirement pinned; independent A8 remains pending"],"stop_conditions":["G4 or raw input drift","Any attempt to claim metadata as reaction evidence"],"HTTP_this_binding":0,"MCTS":0})
hyp=[B/"C/E02/pre_freeze_hypothesis_exposure/v1/permanent_exposure_manifest.json",B/"C/E02/post_scope_internal_hypotheses/v1/permanent_exposure_manifest.json",B/"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_exposure_manifest.json"]
files=[O/"preregistration.json",*Q.glob("*.json"),Q/"http_ledger.jsonl",Q/"authoritative_bibliographic_records.jsonl",Q/"query_execution.jsonl",*raw,*hyp]
folder=B/"SS/E02/stages/batches/SS-E02-R4-metadata"
assert not folder.exists()
stage=freeze_stage_manifest(folder,"G5_FRESH_HOLDOUT_ACQUIRE",files,G4,expected_previous_sha=EXPECTED,family="SS",epoch_id="SS-E02")
stagepath=folder/"G5_FRESH_HOLDOUT_ACQUIRE.json"
with (B/"source_budget_acquisition.lock").open("a+") as lock:
 fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
 e=B/"epoch_ledger.jsonl";before=e.read_bytes()
 ep={"task":T,"family":"SS","epoch_id":"SS-E02","stage":"G5_FRESH_HOLDOUT_ACQUIRE","status":"active","event_type":"metadata_acquisition_stage_registered","stage_manifest_path":rel(stagepath),"stage_manifest_sha256":sha_file(stagepath),"registered_at":now(),"original_manifest_created_at":stage["timestamp"],"registration_is_late":False,"stage_created_after_metadata_HTTP":True,"first_scientific_read_of_R4_candidates":None,"metadata_only":True,"full_scientific_round":False,"fresh_admitted":0,"approval_type":"agent_delegated","human_reviewed":False}
 write(T,rel(O/"epoch_ledger.before.jsonl"),before.decode())
 write(T,rel(e),before.decode()+json.dumps(ep,ensure_ascii=False,sort_keys=True)+"\n")
 assert e.read_bytes().startswith(before)
 req=B/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v2.json"
 old=B/"epochs/SS-E02/epoch_state.v4.json";state=json.loads(old.read_text())
 state.update(timestamp=now(),as_of=now(),previous_state_path=rel(old),previous_sha256=sha_file(old),status="G4_frozen_G5_R4_metadata_identity_29pass10pending_no_fresh",metadata_HTTP=22,metadata_bytes=227821,metadata_strict_clusters_R3=47,metadata_historically_exposed_clusters_R3=8,metadata_unknown_clusters_R3=39,R4_official_records=72,R4_bibliographic_pass=29,R4_bibliographic_pending=10,R4_unknown_project_exposure=39,new_HTTP_this_state_update=0,prior_new_HTTP_field_is_historical=True,future_G7_name_exposure_requirement={"path":rel(req),"sha256":sha_file(req)},named_exposure_A8_review="pending",named_exposure_actual_identity_comparisons=0)
 state["registered_stage_counts"]["G5"]=4;state["stage_sha256"][rel(stagepath)]=sha_file(stagepath)
 new=B/"epochs/SS-E02/epoch_state.v5.json";put(new,state)
 oldc=B/"epochs/C-E02/epoch_state.v7.json";cs=json.loads(oldc.read_text())
 cs.update(timestamp=now(),previous_state_path=rel(oldc),previous_sha256=sha_file(oldc),future_G7_name_exposure_requirement={"path":rel(req),"sha256":sha_file(req)},named_exposure_A8_review="pending",named_exposure_actual_identity_comparisons=0,scope_semantics_changed_by_name_gate=False)
 newc=B/"epochs/C-E02/epoch_state.v8.json";put(newc,cs)
put(O/"binding_validation.json",{"task_id":T,"created_at":now(),"G4_SHA":EXPECTED,"G5_SHA":sha_file(stagepath),"all_16_raw_sha_size_passed":True,"ledger_old_prefix_preserved":True,"registered_stage_added":1,"SS_registered_G5":4,"HTTP_this_binding":0,"source_qualified_added":0,"fresh_added":0,"science_ABE_cells":0,"metrics":None,"full_scientific_round":False,"C_scope_unchanged":True,"SS_scope_unchanged":True,"future_name_gate_A8":"pending"})
m=role_manifest("A0","SS-E02",[O/"preregistration.json",role,G4],[stagepath,O/"binding_validation.json",new,newc],{"processed":16,"passed":16,"rejected":0,"pending":0},pointers=[{"path":rel(stagepath),"sha256":sha_file(stagepath)}],errors=[],unprocessed=["39 source originals/reaction evidence and named identities","G6+/fresh panel","Independent name-gate A8"])
put(O/"role_A0_manifest.json",m)
print(json.dumps({"G5":rel(stagepath),"SHA":sha_file(stagepath),"SS_state":rel(new),"C_state":rel(newc),"new_HTTP":0,"fresh":0}))
