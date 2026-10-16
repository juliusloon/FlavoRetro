#!/usr/bin/env python3
"""SS-E02 bounded A6 source-assay disposition: original source is out of frozen SS O2 scope.
Adjudication is source-local, cannot promote to fresh or claim independent chemistry.
"""
from __future__ import annotations
import sys,json,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import (
 sha_file,verify_stage_chain,freeze_stage_manifest,ContractError)
TASK="TASK-016-P7"
BASE="outputs/task016-p7/v1/SS/E02/"
F=BASE+"fresh/SS-E02-R2-PMC11125054-"
G5=BASE+"stages/batches/SS-E02-R2-PMC11125054/G5_FRESH_HOLDOUT_ACQUIRE.json"
G4=BASE+"stages/G4_SCOPE_FREEZE.json"
S=BASE+"scope_manifest.json"
A3=F+"A3/A3_publication_identity.json"
A4=F+"science-screen/A4_bounded_original_text_screen.json"
A5=F+"A5/A5_independent_source_assay_screen.json"
EX=F+"science-screen/permanent_postfreeze_source_exposure.json"
OUT=F+"A6_scope_disposition/"
SELF="scripts/task016_p7_ss_e02_pmc11125054_A6_disposition_v1.py"
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def now():return datetime.now(timezone.utc).isoformat()
def save(p,r):
 if (ROOT/p).exists():raise ContractError("immutable A6 file exists: "+p)
 write(TASK,p,json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def require(c,t):
 if not c:raise ContractError(t)
def prereg():
 verify_stage_chain(G5,sha(G5))
 for f in (G4,S,A3,A4,A5,EX):
  require((ROOT/f).is_file(),"source prerequisite missing: "+f)
 save(OUT+"A6_pre_execution_manifest.json",dict(
  task=TASK,epoch_id="SS-E02",role="A6 bounded source-specific evidence/admission adjudicator",
  preregistered_at=now(),code_sha256=sha(SELF),
  bound_inputs={p:sha(p) for p in (G5,G4,S,A3,A4,A5,EX)},
  acceptance_requirements=["source bibliographic A3 true","2 separate code paths locate explicit assay starting acceptors and products",
   "must already be flavonol 3-O beta Glcp/Galp for frozen parent-O2 SS","no exact prior exposure","complete covalent original product and UDP donor","source-qualified structure"],
  if_source_aglycones_are_starters="scope inapplicable to reported primary assay; no new G6 transfer group",
  missing_proof_is_not_automatic_chemical_falsity=True,
  no_full_graph_reconstruction_no_human_or_chemical_independent_claim=True,
  cannot_mutate_scope_or_G4=True,no_model_outcome_read=True))
 print("A6 preregistered from both original-reading paths and permanent exposure")
def run():
 verify_stage_chain(G5,sha(G5))
 reg=load(OUT+"A6_pre_execution_manifest.json")
 require(sha(SELF)==reg["code_sha256"],"A6 code drift")
 for p,digest in reg["bound_inputs"].items():
  require(sha(p)==digest,"A6 bound input drift: "+p)
 a3=load(A3);a4=load(A4);a5=load(A5);ex=load(EX)
 scope=load(S)
 require(scope["epoch_id"]=="SS-E02" and scope["scope_audit"]["passed"],"scope freeze missing")
 require(a3["publication_identity_verified"] is True,"A3 not source identified")
 require(a4["structure_complete"] is False and a4["G6_admitted"]==0,"A4 unexpectedly qualified")
 require(a5["status"]=="primary_assay_out_of_scope_SS_O2"
   and a5["passed"]==a5["total"]==5,"A5 out-of-scope inference not supported")
 require(ex["development_exposed"] is True
   and ex["first_scientific_body_read_started_at"],"first chemistry read not permanently bound")
 # Do not turn a single source first-glucosylation into sugar-sugar O2 transfer.
 outcome=dict(task=TASK,epoch_id="SS-E02",family="SS",source="PMC11125054",
  PMID="38794460",DOI="10.3390/plants13101390",
  at=now(),disposition="rejected_for_frozen_SS_E02_O2_assay",
  source_article_identity_verified=True,
  reported_primary_assay_reactants=["kaempferol","quercetin"],
  reported_donor="UDP-Glc",
  original_results_named=["kaempferol glucoside","quercetin glucoside"],
  frozen_SS_scope_parent="flavonol-3O-betaD-Glcp_or_Galp O2 transfer",
  scope_applicable_to_reported_assay=False,
  missing_pre_glycosylated_flavonol_acceptor_in_named_assay=True,
  not_a_global_negative_claim_about_all_other_chemistry=True,
  whole_article_postfreeze_exposed=True,
  no_graphic_structure_reconstruction=True,
  A4_A5_read_different_code_paths=True,
  not_independent_agents_or_human_chemical_validation=True,
  G6_new_structure_admitted=0,G6_new_runtime_complete_targets=0,
  G7_panel_formed=False,G10_ABE_cells=0,metrics=None,
  source_saturation=False,human_reviewed=False,
  evidence_SHA={p:sha(p) for p in (A3,A4,A5,EX,G5,S)})
 save(OUT+"A6_source_scope_disposition.json",outcome)
 # Retain an additive exposure ledger rather than modifying global frozen historical ledger.
 e=dict(task=TASK,epoch_id="SS-E02",exposure_type="post_G4_source_chemical_review",
  source_id=outcome["source"],DOI=outcome["DOI"],PMID=outcome["PMID"],
  closure_tokens=ex["closure_tokens"],development_exposed=True,
  eligible_for_fresh_holdout=False,current_epoch_source_disposition="scope_inapplicable",
  first_scientific_body_read_at=ex["first_scientific_body_read_started_at"],
  original_exposure_file_sha256=sha(EX),source_disposition_sha256=sha(OUT+"A6_source_scope_disposition.json"),
  cannot_recycle_in_later_epochs=True)
 path=OUT+"permanent_exposure_ledger_addendum.jsonl"
 if (ROOT/path).exists():raise ContractError("cannot append to existing frozen source exposure")
 write(TASK,path,json.dumps(e,sort_keys=True,ensure_ascii=False)+"\n")
 role=dict(task=TASK,epoch_id="SS-E02",agent_role="A6 bounded scope admission",
  time=now(),counts=dict(processed=1,passed=0,rejected=1,pending=0),
  original_source_qualified_bibliography=True,scientific_admission=0,
  source_inapplicable_to_frozen_scope=True,
  A4_A5_text_crosscheck_not_dual_molecular_graph_validation=True,
  read_holdout=False,read_model_outcome=False,
  direct_source_chemistry_read_occurred_by_A4_A5=True,
  source_exposed=True,metrics=None,scientific_ABE_cells=0,
  human_reviewed=False,
  output_SHA={p:sha(p) for p in (OUT+"A6_source_scope_disposition.json",path)},
  prereg_sha=sha(OUT+"A6_pre_execution_manifest.json"))
 save(OUT+"role_A6_manifest.json",role)
 # Scoped branch terminal: "G6 zero admitted", NOT a family-wide panel G6 pass.
 stagefolder=BASE+"stages/batches/SS-E02-R2-PMC11125054/"
 inputs=[A3,A4,A5,EX,OUT+"A6_pre_execution_manifest.json",
  OUT+"A6_source_scope_disposition.json",path,OUT+"role_A6_manifest.json",
  "scripts/task016_p7_ss_e02_pmc11125054_A3_identity_v1.py",
  "scripts/task016_p7_ss_e02_pmc11125054_science_screen_v1.py",
  "scripts/task016_p7_ss_e02_pmc11125054_A5_assay_v1.py",SELF]
 stage=freeze_stage_manifest(stagefolder,"G6_IDENTITY_STRUCTURE_ADMIT",inputs,
  previous_manifest_path=G5,expected_previous_sha=sha(G5),
  family="SS",epoch_id="SS-E02")
 verify_stage_chain(stagefolder+"G6_IDENTITY_STRUCTURE_ADMIT.json",
  sha(stagefolder+"G6_IDENTITY_STRUCTURE_ADMIT.json"))
 print(json.dumps(dict(stage=stage["stage"],G6_branch_terminal=True,
  admitted=0,rejected_source_assays=1,permanently_exposed=True,
  scope_unchanged_sha256=sha(S)),ensure_ascii=False))
if __name__=="__main__":
 {"pre":prereg,"run":run}[sys.argv[1]]()
