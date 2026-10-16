#!/usr/bin/env python3
"""SS-E02 scope design G4 conditional scientific-boundary freeze, no fresh/ABE/runtime.
Immutable separate epoch; A3/A6 provenance and A7/A8 replay are SHA-bound.
"""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p7_orchestrate import (
 ContractError,sha_file,verify_stage_chain,freeze_stage_manifest,save_json)
from scripts.task016_p7_scope_harness import validate_scope_bank,freeze_scope_bank
TASK="TASK-016-P7"
DEST="outputs/task016-p7/v1/SS/E02/"
A7="outputs/task016-p7/v1/SS/E02_design/Petunia_scope_proposal_v1/"
A8="outputs/task016-p7/v1/SS/E02_design/Petunia_A8_chatgpt_bounded_v1/"
A6="outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/Petunia_A6_v1/"
A3="outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/A3_publication_identity_v1/"
RAW="data/raw/task016-p7/SS/reference_discovery_r2/originals/SS-REF-ORIG-R2-d94d8131c3734af38dee07d8ca0fba65.article_version"
G3=DEST+"stages/G3_SCOPE_BUILD.json"
GUARD="scripts/task016_p7_ss_petunia_scope_guard_v1.py"
def load(f):return json.loads((ROOT/f).read_text())
def sha(f):return sha_file(ROOT/f)
def need(c,m):
 if not c:raise ContractError(m)
def stamp():return datetime.now(timezone.utc).isoformat()
def check():
 verify_stage_chain(G3,sha(G3))
 need(not (ROOT/DEST/"scope_manifest.json").exists(),"SS-E02 frozen already")
 need(not (ROOT/DEST/"stages/G4_SCOPE_FREEZE.json").exists(),"stage already frozen")
 need(not (ROOT/DEST/"stages/G5_FRESH_HOLDOUT_ACQUIRE.json").exists(),"fresh already began")
 a3=load(A3+"six_original_publication_identity_checks.json")
 petunia=[r for r in a3["records"] if r["source_id"]=="PMC5856881"]
 need(len(petunia)==1 and petunia[0]["publication_identity_passed"]
  and all(petunia[0]["checks"].values()),"independent A3 mismatch")
 source=petunia[0]
 need(source["original_pointer"]["sha256"]==sha(RAW),"original SHA drift")
 a6=load(A6+"A6_source_reconciliation_summary.json")
 role=load(A6+"role_A6_manifest.json")
 need(role["counts"]=={"processed":24,"passed":2,"rejected":12,"pending":10}
  and role["read_holdout"] is False and role["read_model_outcome"] is False,
  "A6 original role tally invalid")
 need(a6["dual_complete_graph_matches"]==9
  and a6["source_qualified_design_supports"]==2
  and a6["shared_source_closure_groups"]==1 and a6["fresh_admitted"]==0,
  "A6 source closure/dual evidence missing")
 support=load(A7+"build_supports.json")
 bank=load(A7+"scope_bank.json")
 replay=load(A7+"build_replay.json")
 boundaries=load(A7+"boundary_results.json")
 check=validate_scope_bank(bank,support,replay,boundaries)
 need(len(support)==2 and len(replay)==2 and len(boundaries)==20,
  "pre-reg counts mismatch")
 need(all(r["mapped_passed"] and r["passed"] for r in replay),"mapped replay not 100%")
 need(all(r["source_qualified_design_support"] is True
   and r["source_identity_verified"] is True
   and r["dual_full_graph_complete"] is True
   and r["fresh_eligible"] is False and r["source_id"]=="PMC5856881"
   for r in support),"unsupported build instance")
 a8=load(A8+"role_A8_bounded_review_manifest.json")
 need(a8["status"]=="pass_bounded_engineering_review"
  and a8["passed"]==a8["total"]==12
  and a8["formally_registered_runtime"] is False,"A8 preflight insufficient")
 # Explicit segregation: isolate guard acts through genuine AiZynthFinder
 # TreeMolecule mapping, but P7 E02 does NOT enter the official v7 registry.
 need(a8["source_closure_groups"]==1,"scope is incorrectly treated as two source groups")
 return source,a6,support,bank,replay,boundaries,check,a8
def freeze():
 source,a6,support,bank,replay,boundaries,pre,a8=check()
 source_identity=[dict(
  pmcid="PMC5856881",pmid="29214446",doi="10.1007/s00425-017-2822-5",
  title=source["MED_literals"]["title"],
  journal=source["MED_literals"]["journalInfo"]["journal"]["title"],
  year=2018,volume="247",pages="779-790",
  source_identity_verified=True,identity_from_A3=True,
  original_pointer=source["original_pointer"],verified_author_order=True,
  publisher_absent_in_source_not_guessed=True,
  chemical_claim_qualification_independent=False)]
 structure=[dict(instance_id=r["instance_id"],reconciled=True,
  A4_A5_A6_existing_evidence_role_sha256=sha(A6+"role_A6_manifest.json"),
  structure_origin=r["structure_origin"],source_id=r["source_id"],
  dual_complete_graph_confirmed_by_A6=True,
  fresh_eligible=False,source_qualified_design_support=True)
   for r in support]
 additional=[A3+"role_A3_manifest.json",
  A3+"six_original_publication_identity_checks.json",
  A6+"role_A6_manifest.json",
  A6+"A6_source_reconciliation_summary.json",
  A6+"2_source_qualified_design_supports.jsonl",
  A7+"role_A7_final_manifest.json",
  A7+"pre_execution_contract.v3.json",
  A7+"exact_templates.json",
  A8+"A8_pre_execution_manifest.json",
  A8+"role_A8_bounded_review_manifest.json",
  "outputs/task016-p7/v1/epochs/SS-E01/incomplete_decision.json",
  "outputs/task016-p7/v1/epochs/SS-E01/permanent_exposure_manifest.json",
  "scripts/task016_p7_ss_e02_root_stages_chatgpt_v1.py",
  "scripts/task016_p7_ss_e02_g4_freeze_chatgpt_v1.py"]
 # validate all additions before creating immutable files
 for f in additional+[GUARD]:
  need((ROOT/f).is_file(),"missing freeze dependency "+f)
 manifest=freeze_scope_bank(ROOT/DEST,bank,support,replay,boundaries,
  source_identity,structure,family="SS",epoch_id="SS-E02",
  additional_files=additional,production_guard=GUARD)
 decision=dict(task=TASK,family="SS",epoch_id="SS-E02",
  status="G4_scope_frozen_design_level_only",timestamp=stamp(),
  G4_scope_manifest_sha256=sha(DEST+"scope_manifest.json"),
  scope_sha256=sha(DEST+"scope_bank.json"),
  source_id="PMC5856881",source_closure_groups=1,
  distinct_canonical_acceptors=2,build_replay="2/2",
  mapped_replay="2/2",boundary_controls=20,boundary_violations=0,
  A8_engineering_reviews=12,A8_engineering_passed=12,
  separate_exact_templates=True,isolated_guard_tree_molecule_checked=True,
  formal_v7_registry_integrated=False,G9_completed=False,
  source_supported_aglycones=1,
  five_other_new_source_fulltext_chemistry_unread=True,
  already_observed_design_supports_not_eligible_for_fresh=True,
  fresh_targets=0,G5_started=False,G6_admitted=0,G7_panel=False,
  scientific_ABE_cells=0,metrics=None,source_saturation=False,
  read_holdout=False,read_model_outcome=False,
  human_reviewed=False,independent_chemical_validation=False,
  preflight_provenance="A3 publisher/front + A6 reconciled graph + separate A8 bounded engineering; no new human review",
  scope_contract=pre,
  stop_condition="Any future scope modification invalidates epoch and requires fresh entirely new panel")
 p=DEST+"role_A0_G4_freeze_decision.json"
 save_json(p,decision,immutable=True)
 files=[DEST+f for f in ("scope_bank.json","build_supports.json","build_replay.json",
  "boundary_results.json","source_identity.json","dual_structure_reconciliation.json",
  "scope_manifest.json","role_A0_G4_freeze_decision.json","G3_scope_preflight.json",
  "G2_design_source_validation.json")]
 files+=additional+[GUARD]
 stage=freeze_stage_manifest(DEST+"stages","G4_SCOPE_FREEZE",files,
  previous_manifest_path=G3,expected_previous_sha=sha(G3),
  family="SS",epoch_id="SS-E02")
 # scoped G4 snapshot, not a claim of running G5
 epoch=dict(task=TASK,family="SS",epoch_id="SS-E02",
  status="active_scope_frozen_before_any_fresh",stage="G4_SCOPE_FREEZE",
  scope_sha256=sha(DEST+"scope_bank.json"),
  scope_manifest_sha256=sha(DEST+"scope_manifest.json"),
  G4_stage_sha256=sha(DEST+"stages/G4_SCOPE_FREEZE.json"),
  scope_frozen_at=manifest["frozen_at"],fresh=0,
  historical_exposure_E01_immutable=True,human_reviewed=False,
  science_metrics=None,scientific_ABE_cells=0,
  G5_not_started=True,source_saturation=False,approval_type="agent_delegated")
 save_json("outputs/task016-p7/v1/epochs/SS-E02/epoch_state.v1.json",epoch,immutable=True)
 verify_stage_chain(DEST+"stages/G4_SCOPE_FREEZE.json",sha(DEST+"stages/G4_SCOPE_FREEZE.json"))
 print(json.dumps(dict(epoch_id="SS-E02",stage=stage["stage"],
  frozen=True,scope_sha256=epoch["scope_sha256"],source_groups=1,
  fresh=0,scientific_ABE=0,registry_connected=False),ensure_ascii=False))
if __name__=="__main__":
 {"check":lambda: print(json.dumps(dict(preflight=True,contract=check()[6]),
  ensure_ascii=False)),"freeze":freeze}[sys.argv[1]]()
