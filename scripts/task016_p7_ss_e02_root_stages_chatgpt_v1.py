#!/usr/bin/env python3
"""SS-E02 source-qualified design G2 and bounded scope G3 stage bridge.
Never reads evaluation holdouts or model outcomes. Does not freeze G4.
"""
from __future__ import annotations
import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p7_orchestrate import (
 sha_file,freeze_stage_manifest,verify_stage_chain,ContractError,save_json)
from scripts.task016_p7_scope_harness import validate_scope_bank
from rdkit import Chem
TASK="TASK-016-P7"
BASE="outputs/task016-p7/v1/SS/"
DEST=BASE+"E02/"
A7=BASE+"E02_design/Petunia_scope_proposal_v1/"
A6=BASE+"E02_design/reference_discovery_r2/Petunia_A6_v1/"
A3=BASE+"E02_design/reference_discovery_r2/A3_publication_identity_v1/"
A8=BASE+"E02_design/Petunia_A8_chatgpt_bounded_v1/"
G1="outputs/task016-p7/v1/stages/global/G1_EXPOSURE_LEDGER.json"
OLD=BASE+"../epochs/SS-E01/incomplete_decision.json"
EXPOSE="outputs/task016-p7/v1/epochs/SS-E01/permanent_exposure_manifest.json"
RAW="data/raw/task016-p7/SS/reference_discovery_r2/originals/SS-REF-ORIG-R2-d94d8131c3734af38dee07d8ca0fba65.article_version"
def load(file): return json.loads((ROOT/file).read_text())
def sha(file): return sha_file(ROOT/file)
def utc(): return datetime.now(timezone.utc).isoformat()
def bind(*paths):return {f:sha(f) for f in paths}
def decide(condition,message):
 if not condition:raise ContractError(message)
def common():
 assert (ROOT/G1).is_file()
 verify_stage_chain(G1,sha(G1))
 old=load("outputs/task016-p7/v1/epochs/SS-E01/incomplete_decision.json")
 decide(old["status"]=="development_epoch_incomplete"
   and old["successor"]["epoch_id"]=="SS-E02","E01 successor mismatch")
 decide(sha(EXPOSE)==old["permanent_exposure_manifest"]["sha256"],"E01 exposure SHA drift")
 id_rows=load(A3+"six_original_publication_identity_checks.json")["records"]
 matches=[r for r in id_rows if r["source_id"]=="PMC5856881"]
 decide(len(matches)==1,"Petunia A3 source identity cardinality")
 idr=matches[0]
 decide(idr["publication_identity_passed"] is True
   and all(idr["checks"].values()) and idr["chemical_qualification"] is False,
   "Petunia A3 identity or source qualification confused")
 decide(idr["original_pointer"]["path"]==RAW
   and idr["original_pointer"]["sha256"]==sha(RAW),"Petunia raw original SHA drift")
 supports=load(A7+"build_supports.json")
 a6=load(A6+"A6_source_reconciliation_summary.json")
 decide(a6["source_qualified_design_supports"]==2
  and a6["distinct_complete_canonical_acceptors"]==2
  and a6["shared_source_closure_groups"]==1 and a6["fresh_admitted"]==0,
  "A6 support and closure qualification invalid")
 decide(len(supports)==2 and len({r["instance_id"] for r in supports})==2,
  "duplicate or incorrect support IDs")
 decide(all(r["source_id"]=="PMC5856881" and r["source_identity_verified"] is True
   and r["source_qualified_design_support"] is True
   and r["dual_full_graph_complete"] is True and r["fresh_eligible"] is False
   and r["human_reviewed"] is False for r in supports),"unqualified support used")
 decide(len({Chem.MolToSmiles(Chem.MolFromSmiles(r["acceptor"]),isomericSmiles=True)
   for r in supports})==2,"two different canonical acceptors required")
 a7=load(A7+"role_A7_final_manifest.json")
 a8=load(A8+"role_A8_bounded_review_manifest.json")
 decide(a7["all_input_output_sha_verified"] and a7["scope_frozen"] is False,
  "A7 SHA or stage claim inconsistent")
 decide(a8["status"]=="pass_bounded_engineering_review"
   and a8["total"]==12 and a8["passed"]==12
   and a8["fresh_holdout"]==0 and a8["scientific_ABE_cells"]==0,
   "A8 failed/not bounded")
 for file,digest in load(A8+"A8_pre_execution_manifest.json")["frozen_inputs"].items():
  decide(sha(file)==digest,"A8 bound input SHA drift: "+file)
 decide(not (ROOT/DEST/"scope_manifest.json").exists(),"SS-E02 scope already frozen")
 return idr,a6,supports,a7,a8
def g2():
 idr,a6,supports,a7,a8=common()
 p=DEST+"G2_design_source_validation.json"
 decide(not (ROOT/p).exists(),"immutable G2 output exists")
 save_json(p,dict(task=TASK,family="SS",epoch_id="SS-E02",
  role="A0 bounded root stage bridge",time=utc(),status="source_qualified_design_only",
  identity=dict(PMCID="PMC5856881",PMID="29214446",DOI="10.1007/s00425-017-2822-5",
   authoritative_A3_verified=True,raw_sha256=sha(RAW),
   original_publisher_field_missing_not_fabricated=True),
  A6=dict(design_supports=2,distinct_acceptors=2,source_closure_groups=1,
   complete_graph_pairs=a6["dual_complete_graph_matches"],fresh_admitted=0,
   other_5_sources_body_unread=True),
  exposure=dict(previous_epoch="SS-E01",previous_epoch_incomplete=True,
   previous_exposure_sha256=sha(EXPOSE),support_records_exposed_design_only=True),
  review=dict(A8_bounded_engineering=12,A8_passed=12,chemical_independent_review=False),
  G4_frozen=False,new_HOLDOUT_extracted=False,
  human_reviewed=False,source_saturation=False,scientific_ABE_cells=0,
  evidence_sha=bind(EXPOSE,RAW,A3+"role_A3_manifest.json",
   A3+"six_original_publication_identity_checks.json",
   A6+"role_A6_manifest.json",
   A6+"A6_source_reconciliation_summary.json",
   A6+"2_source_qualified_design_supports.jsonl",
   A7+"build_supports.json",A7+"role_A7_final_manifest.json",
   A8+"role_A8_bounded_review_manifest.json")))
 files=[p,"outputs/task016-p7/v1/epochs/SS-E01/incomplete_decision.json",
  EXPOSE,RAW,A3+"role_A3_manifest.json",
  A3+"six_original_publication_identity_checks.json",
  A6+"A6_source_reconciliation_summary.json",
  A6+"role_A6_manifest.json",
  A6+"2_source_qualified_design_supports.jsonl",
  A7+"build_supports.json",A7+"role_A7_final_manifest.json",
  A8+"role_A8_bounded_review_manifest.json",A8+"A8_pre_execution_manifest.json",
  "scripts/task016_p7_ss_e02_root_stages_chatgpt_v1.py"]
 stage=freeze_stage_manifest(DEST+"stages","G2_DESIGN_ACQUIRE",files,
  previous_manifest_path=G1,expected_previous_sha=sha(G1),
  family="SS",epoch_id="SS-E02")
 print(json.dumps(dict(stage=stage["stage"],status="registered",prev=G1,
  count=len(stage["files"]),G4_frozen=False),ensure_ascii=False))
def g3():
 idr,a6,supports,a7,a8=common()
 s2=DEST+"stages/G2_DESIGN_ACQUIRE.json"
 decide((ROOT/s2).is_file(),"G2 prerequisite missing")
 verify_stage_chain(s2,sha(s2))
 for f in (DEST+"G3_scope_preflight.json",DEST+"stages/G3_SCOPE_BUILD.json"):
  decide(not (ROOT/f).exists(),"immutable G3 output exists: "+f)
 bank=load(A7+"scope_bank.json")
 replay=load(A7+"build_replay.json")
 boundaries=load(A7+"boundary_results.json")
 outcome=validate_scope_bank(bank,supports,replay,boundaries)
 decide(outcome["passed"] and outcome["scopes"]==1,"P7 scope contract failed")
 decide(len({r["control_id"] for r in boundaries})==20
  and len(replay)==2 and all(r["mapped_passed"] for r in replay),
  "mapped replay or preregistered boundary mismatch")
 for key,value in a7["input_manifest_sha"].items():
  decide(sha(key)==value,"A7 frozen input drift: "+key)
 # Isolated A8 used the A7 runtime dispatcher; this does not falsely certify
 # independent chemical review or production registry integration.
 p=DEST+"G3_scope_preflight.json"
 save_json(p,dict(task=TASK,epoch_id="SS-E02",family="SS",
  role="A0 bounded root stage bridge",time=utc(),status="G3_source_bounded_scope_qualified",
  scope_contract=outcome,independent_engineering_checks=12,
  mapped_full_reference_replay=2,unregistered_v7_dispatcher_replay=0,
  distinct_acceptors=2,distinct_source_closure_groups=1,
  guard_is_proposal_only=True,G4_frozen=False,formal_runtime_connected=False,
  synthetic_OH_controls_are_not_sources=True,other5_scientific_sources_unread=True,
  no_new_fresh=True,scientific_ABE_cells=0,metrics=None,
  human_reviewed=False,independent_chemical_validation=False,
  evidence_sha=bind(A7+"scope_bank.json",A7+"build_replay.json",
   A7+"boundary_results.json",A7+"pre_execution_contract.v3.json",
   A8+"A8_pre_execution_manifest.json",A8+"role_A8_bounded_review_manifest.json",
   "scripts/task016_p7_ss_petunia_scope_guard_v1.py",
   "flavoretro/glycoside_library_v7.py")))
 files=[p,A7+"scope_bank.json",A7+"build_supports.json",
  A7+"build_replay.json",A7+"boundary_results.json",
  A7+"pre_execution_contract.v3.json",A7+"role_A7_final_manifest.json",
  A8+"role_A8_bounded_review_manifest.json",
  A8+"A8_pre_execution_manifest.json",
  "scripts/task016_p7_ss_petunia_scope_guard_v1.py",
  "scripts/task016_p7_ss_e02_root_stages_chatgpt_v1.py",
  "flavoretro/glycoside_library_v7.py"]
 stage=freeze_stage_manifest(DEST+"stages","G3_SCOPE_BUILD",files,
  previous_manifest_path=s2,expected_previous_sha=sha(s2),family="SS",epoch_id="SS-E02")
 print(json.dumps(dict(stage=stage["stage"],status="registered",
  count=len(stage["files"]),G4_frozen=False,scope=bank[0]["template_id"]),ensure_ascii=False))
if __name__=="__main__":
 {"g2":g2,"g3":g3}[sys.argv[1]]()
