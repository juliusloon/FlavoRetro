"""R47: both frozen-family contracts and G5s before first Iris source science."""
import json
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts.task016_p7_orchestrate import role_manifest,freeze_stage_manifest,verify_stage_chain
from scripts import task016_p7_full_qualification_harness_v3 as fq
T="TASK-016-P7";B=Path("outputs/task016-p7/v1");SID="PMC13422134"
A3=B/"C/E02/fresh/C-E02-R46-Iris-advertised-assets-v1/A3_original_front_identity.json"
ASSETS=A3.parent/"asset_execution.jsonl"
POLICY=B/"governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json"
REQ=B/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json"
ROUTES=["EPMC_XML_attempt","PMC_public_open_data_index_attempt","PMC_public_HTML","Crossref_declared_publisher_HTML_attempt","PMC_advertised_SI_and_images_attempt"]
def base(f):return B/f"{f}/E02/fresh/{f}-E02-R47-Iris-prospective-qualification-v1"
def stage(f):return B/f"{f}/E02/stages/batches/{f}-E02-R47-Iris-prospective-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
def main():
 assert not any((ROOT/base(f)).exists() for f in ("C","SS"))
 identity=load(A3);assert all(identity["field_checks"].values())
 assets=lines(ASSETS);assert len(assets)==7
 raw=[dict(path=identity["original_raw"]["path"],sha256=identity["original_raw"]["sha256"])]
 si=next(x for x in assets if x["asset_role"]=="advertised_SI")
 assert not (ROOT/si["raw_pointer"]["path"]).read_bytes().startswith(b"%PDF")
 si_content=dict(raw_pointer=si["raw_pointer"],HTTP_status=si["HTTP_status"],actual_content="HTML title Checking your browser - reCAPTCHA",valid_original_SI=False,scientific_SI_read=False,challenge_not_solved=True,access_status="pending_access_restriction",not_counted_as_PDF=True)
 for row in assets:
  if row["asset_role"]=="advertised_original_figure":
   rp=row["raw_pointer"];assert row["status"]=="available" and sha(rp["path"])==rp["sha256"] and (ROOT/rp["path"]).read_bytes().startswith(b"\xff\xd8")
   raw.append(dict(path=rp["path"],sha256=rp["sha256"]))
 assert len(raw)==7
 prior=lines(B/"governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl")
 assert len(prior)==5204 and not any(set(identity["official_aliases"]).intersection(x["closure_tokens"]) for x in prior)
 contracts={}
 for family in ("C","SS"):
  r=base(family);g4=B/f"{family}/E02/stages/G4_SCOPE_FREEZE.json"
  source=dict(source_id=SID,official_aliases=identity["official_aliases"],raw_status="available",raw_files=raw,raw_available_content="public original HTML and six original figures; SI content access pending",prior_scientific_read=False,prior_scientific_read_basis="Known aliases absent 5204-row prior inventory; no complete source/graph/name historical clearance inferred.",full_alias_or_graph_historical_clearance=False,planned_original_routes=ROUTES,SI_access_disposition=si_content,intake_evidence=[fq.pointer(A3),fq.pointer(ASSETS),fq.pointer(B/"C/E02/fresh/C-E02-R44-Iris-original-custody-v1/query_execution.jsonl"),fq.pointer(B/"C/E02/fresh/C-E02-R45-Iris-public-body-access-v1/query_execution.jsonl")])
  put(r/"raw_source_universe.json",dict(task=T,scientific_content_read=False,final_structures_provided=False,source_candidates=[source],metadata_only_dispositions=[],source_count=1,source_shared_across_C_SS=True,source_independence_group_count_not_doubled=True,source_material_local_only_no_OA_grant_claim=True))
  put(r/"A3_source_results.json",dict(task=T,sources=[dict(source_id=SID,identity_status="verified",official_aliases=identity["official_aliases"],unresolved_conflicts=[],field_checks=identity["field_checks"],evidence=[fq.pointer(A3),fq.pointer(Path(identity["original_raw"]["path"])),fq.pointer(Path(identity["Crossref_raw"]["path"]))],SI_original_access_pending=True)]))
  role=role_manifest("A3",family+"-E02",[r/"raw_source_universe.json",A3,Path(identity["original_raw"]["path"]),Path(identity["Crossref_raw"]["path"])],[r/"A3_source_results.json"],dict(processed=1,passed=1,rejected=0,pending=0),pointers=[fq.pointer(A3)],read_holdout=False,read_model_outcome=False)
  put(r/"role_A3_manifest.json",role)
  ledger=B/"epoch_ledger.jsonl";data=(ROOT/ledger).read_bytes()
  epoch=B/"epochs"/(family+"-E02")/("epoch_state.v9.json" if family=="C" else "epoch_state.v6.json")
  spec=dict(family=family,epoch_id=family+"-E02",batch_id=family+"-E02-R47-Iris-prospective-qualification",G4=fq.pointer(g4),epoch_state=fq.pointer(epoch),epoch_ledger_prefix=dict(path=str(ledger),prefix_bytes=len(data),prefix_sha256=sha(ledger)),scope_manifest=fq.pointer(B/f"{family}/E02/scope_manifest.json"),scope_bank=fq.pointer(B/f"{family}/E02/scope_bank.json"),raw_source_universe=fq.pointer(r/"raw_source_universe.json"),A3_source_results=fq.pointer(r/"A3_source_results.json"),A3_role=fq.pointer(r/"role_A3_manifest.json"),prior_exposure_snapshot=fq.pointer(B/f"governance/prior_exposure_inventory_v4/prior_exposure_snapshot_{family}.json"),late_prior_design_files=[],future_G7_requirement=fq.pointer(REQ),policy=fq.pointer(POLICY),evaluation_events_directory=str(r/"evaluation_read_events"))
  cp=fq.freeze_full_qualification_contract(r/"full_qualification_contract.json",spec);validated=fq.validate_full_qualification_contract(cp)
  assert validated["source_candidates"]==1 and validated["admitted"]==0
  contracts[family]=cp
  put(r/"pre_G5_contract_validation.json",dict(task=T,at=now(),family=family,source_candidates=1,identity_pending=validated["source_identity_pending"],actual_G4_list_scope_bank_and_v3_implementation_validated=True,science_admitted=0,source_SI_access_pending=True))
 # Freeze both G5s before either family may open source science.
 for family in ("C","SS"):
  r=base(family);g4=B/f"{family}/E02/stages/G4_SCOPE_FREEZE.json";g5=stage(family)
  paths=[r/x for x in ("full_qualification_contract.json","raw_source_universe.json","A3_source_results.json","role_A3_manifest.json","pre_G5_contract_validation.json")]+[Path(x["path"]) for x in raw]
  freeze_stage_manifest(ROOT/g5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",paths,g4,expected_previous_sha=sha(g4),family=family,epoch_id=family+"-E02")
  verify_stage_chain(ROOT/g5,sha(g5))
  row=dict(task=T,epoch_id=family+"-E02",family=family,stage="G5_FRESH_HOLDOUT_ACQUIRE",status="active",event_type="R47_both_axes_preregistered_before_shared_original_science",at=now(),stage_manifest_path=str(g5),stage_manifest_sha256=sha(g5),qualification_contract=contracts[family],source_count=1,source_science_read=False,fresh_admitted=0,approval_type="agent_delegated",human_reviewed=False)
  ledger=B/"epoch_ledger.jsonl";write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,sort_keys=True)+"\n")
 shared=B/"governance/R47-Iris-cross-axis-source-read-binding-v1/both_G5_ready_before_first_read.json"
 put(shared,dict(task=T,at=now(),approval_type="agent_delegated",human_reviewed=False,source_id=SID,contracts=contracts,G5={f:fq.pointer(stage(f)) for f in ("C","SS")},shared_source_original_files=raw,SI_access_disposition=si_content,first_scientific_read_not_yet_started=all(not fq.evaluation_events(contracts[f]) for f in ("C","SS")),independent_source_group_count=1,new_source_eligibility=None,source_saturation=False))
 event(T,"R47_C_SS_both_G5_before_new_original_science",shared_binding_SHA=sha(shared),source_count=1,fresh_admitted=0)
 print(json.dumps(dict(G5={f:sha(stage(f)) for f in ("C","SS")},raw_scientific_files=7,SI_access_pending=True,scientific_reads=0)))
if __name__=="__main__":main()
