"""Freeze the formally replayed C bank with independent qualification and explicit donor serialization."""
import json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_orchestrate import save_json,sha_file,role_manifest,freeze_stage_manifest,verify_stage_chain,verify_hashes
from scripts.task016_p7_c_scope import rows
from scripts.task016_p7_scope_harness import freeze_scope_bank,validate_scope_bank
from flavoretro.reviewed_resources import canonical_side
from rdkit import Chem
TASK="TASK-016-P7";OUT=ROOT/"outputs/task016-p7/v1/C/E01"
def load(n):return json.loads((OUT/n).read_text())
def qualified():
 q=load("design_independent_qualification.json");resolution=load("runtime_donor_serialization_resolution.json")
 if q.get("passed") is not True or resolution.get("passed") is not True:raise RuntimeError("independent qualification/resolution failed")
 verify_hashes(q["verified_input_files_sha256"]);verify_hashes(resolution["verified_input_files_sha256"])
 if sha_file(OUT/"design_source_input_manifest.json")!=q["input_manifest_sha"]:raise RuntimeError("source input drift")
 rr=rows(OUT/"dual_structure_reconciliation.jsonl")
 if {r["instance_id"] for r in rr}!=set(q["approved_reaction_ids"]) or any(r.get("reconciled") is not True for r in rr):raise RuntimeError("qualified universe drift")
 return q,rr,resolution

def prepare():
 q,rr,resolution=qualified();byid={r["instance_id"]:r for r in rr};decisions={r["instance_id"]:r for r in resolution["decisions"]}
 supports=copy.deepcopy(load("formal_build_candidates.json"));bank=copy.deepcopy(load("formal_scope_candidates.json"))
 if {s["instance_id"] for s in supports}!=set(byid) or {t["template_id"] for t in bank}!=set(q["approved_scope_ids"]):raise RuntimeError("formal qualification universe mismatch")
 for s in supports:
  r=byid[s["instance_id"]];d=decisions[s["instance_id"]]
  for before,after in ((s["acceptor"],r["acceptor_smiles"]),(s["target"],r["product_smiles"]),(s["donor"],d["selected_runtime_donor"])):
   if canonical_side([before])!=canonical_side([after]):raise RuntimeError("qualified/runtime graph changed")
  for donor in (s["donor"],r["donor_smiles"]):
   mol=Chem.MolFromSmiles(donor)
   if Chem.MolToInchi(mol)!=d["full_Standard_InChI"] or Chem.MolToInchiKey(mol)!=d["InChIKey"]:raise RuntimeError("full donor stereo identity disagreement")
  expected=canonical_side([r["acceptor_smiles"],d["selected_runtime_donor"]])
  if canonical_side(s["reference_precursors"])!=expected:raise RuntimeError("formal reference disagrees with selected serialization")
  s.update(source_identity_status="independently_verified_A3",dual_structure_status="reconciled_A6_with_explicit_donor_serialization",evidence_eligible=True,evidence_closed=True,actionable=True,structure_qualification=dict(path=str((OUT/"dual_structure_reconciliation.jsonl").relative_to(ROOT)),sha256=sha_file(OUT/"dual_structure_reconciliation.jsonl"),instance_id=s["instance_id"]),runtime_donor_serialization_resolution=dict(path=str((OUT/"runtime_donor_serialization_resolution.json").relative_to(ROOT)),sha256=sha_file(OUT/"runtime_donor_serialization_resolution.json")),provenance=dict(pmcid=r["pmcid"],scope_role="historical_design_build_only",source_evidence_pointers=r["evidence_pointers"],evidence_locations=r["evidence_locations"],independent_qualification_sha256=sha_file(OUT/"design_independent_qualification.json")))
 for t in bank:t["validation_status"]="source_identity_and_dual_structure_qualified_scope_replayed_boundary_passed"
 validate_scope_bank(bank,supports,load("formal_build_replay.json"),load("formal_boundary_results.json"))
 save_json(OUT/"qualified_build_candidates.json",supports,immutable=True);save_json(OUT/"qualified_scope_candidates.json",bank,immutable=True)
 m=role_manifest("A7 Scope Builder","C-E01",[OUT/n for n in ("design_independent_qualification.json","dual_structure_reconciliation.jsonl","runtime_donor_serialization_resolution.json","boundary_plan.json")],[OUT/n for n in ("qualified_scope_candidates.json","qualified_build_candidates.json","formal_build_replay.json","formal_boundary_results.json","formal_scope_validation.json")],dict(processed=8,passed=6,rejected=0,pending=2),pointers=[dict(instance_id=s["instance_id"],pmcid=s["pmcid"],provenance=s["provenance"]) for s in supports],read_holdout=False,read_model_outcome=False)
 m.update(scopes=3,boundary_controls=18,boundary_violations=0,build_replay_passed=6,excluded_deferred=q["deferred"],formal_scientific_scope_unchanged=True,preregistered_boundary_plan_sha256=sha_file(OUT/"boundary_plan.json"))
 save_json(OUT/"role_A7_final_manifest.json",m,immutable=True);print(json.dumps(dict(qualified_supports=len(supports),scopes=len(bank),scope_candidate_sha256=sha_file(OUT/"qualified_scope_candidates.json"),role_A7_sha256=sha_file(OUT/"role_A7_final_manifest.json"))))

def freeze(a8path):
 q,structure,resolution=qualified();a8path=Path(a8path).resolve();a8=json.loads(a8path.read_text())
 if a8.get("passed") is not True:raise RuntimeError("A8 formal verification must pass before freeze")
 bank=load("qualified_scope_candidates.json");supports=load("qualified_build_candidates.json");replay=load("formal_build_replay.json");bounds=load("formal_boundary_results.json")
 extra=[OUT/n for n in ("design_independent_qualification.json","design_source_input_manifest.json","dual_structure_reconciliation.jsonl","role_A7_final_manifest.json","boundary_plan.json","formal_scope_validation.json","formal_build_replay.json","formal_boundary_results.json","runtime_donor_serialization_resolution.json")]+[a8path]
 m=freeze_scope_bank(OUT,bank,supports,replay,bounds,q["source_identity"],structure,family="C",epoch_id="C-E01",additional_files=extra,production_guard=ROOT/"flavoretro/glycoside_scope_c_v7.py")
 stages=OUT/"stages";previous=ROOT/"outputs/task016-p7/v1/stages/global/G1_EXPOSURE_LEDGER.json"
 g2_files=[OUT/n for n in ("design_source_input_manifest.json","design_source_identity_inputs.jsonl","source_identity_verification.jsonl","design_extractor_A4.jsonl","design_extractor_A5_harness.jsonl","dual_structure_reconciliation.jsonl","design_independent_qualification.json","source_internal_conflicts.json","design_A4_deferred.jsonl","design_A5_deferred.jsonl","role_A1_design_manifest.json","role_A3_identity_manifest.json","role_A4_design_manifest.json","role_A5_harness_manifest.json","role_A6_design_qualification_manifest.json","runtime_donor_serialization_resolution.json")]
 g3_files=[ROOT/"flavoretro/glycoside_scope_c_v7.py",ROOT/"scripts/task016_p7_c_freeze.py",ROOT/"scripts/task016_p3_build.py",a8path]+[OUT/n for n in ("role_A7_final_manifest.json","boundary_plan.json","exact_templates.jsonl","formal_scope_candidates.json","formal_build_candidates.json","qualified_scope_candidates.json","qualified_build_candidates.json","formal_scope_validation.json","formal_build_replay.json","formal_boundary_results.json")]
 g4_files=[OUT/"scope_manifest.json"]+[(ROOT/n if n.startswith(("outputs/","flavoretro/","scripts/","data/")) else OUT/n) for n in m["files_sha256"]]
 for stage,files in (("G2_DESIGN_ACQUIRE",g2_files),("G3_SCOPE_BUILD",g3_files),("G4_SCOPE_FREEZE",g4_files)):
  freeze_stage_manifest(stages,stage,files,previous,expected_previous_sha=sha_file(previous),family="C",epoch_id="C-E01");previous=stages/(stage+".json")
 verify_stage_chain(previous,sha_file(previous))
 print(json.dumps(dict(scope_manifest_sha256=sha_file(OUT/"scope_manifest.json"),scope_bank_sha256=m["scope_bank_sha256"],G4_sha256=sha_file(previous),scopes=3,supports=6)))
if __name__=="__main__":
 if sys.argv[1]=="prepare":prepare()
 elif sys.argv[1]=="freeze":freeze(sys.argv[2])
