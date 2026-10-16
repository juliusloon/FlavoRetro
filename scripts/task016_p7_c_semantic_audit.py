"""Immutable post-freeze diagnostic; never alters scope or source extraction."""
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold
from scripts.operate import write
from flavoretro.glycoside_scope_c_v7 import apply_c_scope
from flavoretro.glycoside_library_v7 import apply_template
ROOT=Path.cwd(); BASE=ROOT/"outputs/task016-p7/v1/C/E01"; OUT=BASE/"postfreeze_diagnostics/C3H_semantic_audit"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(s):
 m=Chem.MolFromSmiles(s)
 return Chem.MolToSmiles(m,isomericSmiles=True) if m is not None else None
def save(n,o):
 p=OUT/n
 if p.exists():raise RuntimeError("diagnostic is immutable")
 write("TASK-016-P7",str(p.relative_to(ROOT)),json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
inputs=[BASE/"scope_manifest.json",BASE/"scope_bank.json",BASE/"boundary_plan.json",BASE/"formal_boundary_results.json",BASE/"fresh/alternate/A4_WASABI_product_graphs.jsonl",ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl",ROOT/"flavoretro/glycoside_scope_c_v7.py",ROOT/"flavoretro/glycoside_library_v7.py",ROOT/"scripts/task016_p7_c_scope.py"]
bank=json.loads((BASE/"scope_bank.json").read_text());t=next(t for t in bank if t["scope"]["center_class"]=="flavone_6_C_glucoside")
plan=json.loads((BASE/"boundary_plan.json").read_text());controls=[c for c in plan["controls"] if c["template_id"]==t["template_id"]]
source=[json.loads(x) for x in (BASE/"fresh/alternate/A4_WASABI_product_graphs.jsonl").read_text().splitlines()]
ledger=[json.loads(x) for x in (ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl").read_text().splitlines()]
query=Chem.MolFromSmarts(t["guard_spec"]["core_query"])
results=[]
for r in source:
 target=r["product_smiles"];a=r["acceptor_smiles"]
 duplicate=[dict(exposure_id=e["exposure_id"],target_graph=e["target_graph"],origins=e["origins"],development_exposed=e["development_exposed"],eligible_for_fresh_holdout=e["eligible_for_fresh_holdout"]) for e in ledger if e.get("target_graph") and canon(e["target_graph"])==canon(target)]
 c3oh=Chem.MolFromSmarts("O=c1c([OX2H])c(-c2ccccc2)oc2ccccc12")
 results.append(dict(reaction_id=r["reaction_id"],acceptor_smiles=a,product_smiles=target,source_donor_smiles=r["donor_smiles"],source_reference_precursors=r["reference_precursors"],source_evidence_eligible=r["evidence_eligible"],pyrone_C3_OH=Chem.MolFromSmiles(a).HasSubstructMatch(c3oh),mandatory_query_matches=Chem.MolFromSmiles(target).GetSubstructMatches(query),acceptor_Murcko_scaffold=Chem.MolToSmiles(MurckoScaffold.GetScaffoldForMol(Chem.MolFromSmiles(a))),child_production_outcomes=apply_c_scope(t,target),dispatcher_production_outcomes=apply_template(t,target),historical_exact_target_matches=duplicate,source_evidence=[r["structure_evidence_pointer"],r["additional_structure_evidence_pointer"]]))
replayed_controls=[dict(c,child_outcomes=apply_c_scope(t,c["target"]),dispatcher_outcomes=apply_template(t,c["target"])) for c in controls]
facts=dict(task="TASK-016-P7",epoch_id="C-E01",timestamp=datetime.now(timezone.utc).isoformat(),type="postfreeze_semantic_diagnostic_not_preregistered_control",input_files_sha256={str(p.relative_to(ROOT)):sha(p) for p in inputs},frozen_scope=t["scope"],frozen_guard_spec=t["guard_spec"],results=results,preregistered_controls_replay=replayed_controls,findings=dict(C3H_requirement_explicitly_preregistered=False,C3H_requirement_enforced=False,C3OH_candidate_was_preregistered_negative_control=False,preregistered_different_core_control="ring heteroatom O changed to S; not addition of pyrone C3-OH",preregistered_controls_violated=sum(bool(r["child_outcomes"] or r["dispatcher_outcomes"]) for r in replayed_controls),frozen_query_has_no_C3_hydrogen_or_degree_constraint=True,center_class_text="flavone_6_C_glucoside",allowed_generalization_text=t["scope"]["allowed_generalization"],scope_semantic_interpretation="center_class taxonomy versus source-derived mandatory structural-core decoration range requires independent adjudication; no unregistered C3H constraint may be silently added",same_epoch_scope_change=False,fresh_admission=False,source_donor_reaction_still_unverified=True),human_reviewed=False)
save("audit.json",facts)
save("role_A7_diagnostic_manifest.json",dict(task="TASK-016-P7",epoch_id="C-E01",agent_role="A7 Scope Builder diagnostic",approval_type="agent_delegated",input_files_sha256=facts["input_files_sha256"],output_files_sha256={str((OUT/"audit.json").relative_to(ROOT)):sha(OUT/"audit.json")},read_other_extractor_output=False,read_holdout=True,read_model_outcome=True,model_outcome_purpose="post-freeze guard diagnosis only; not source extraction or panel selection",counts=dict(source_graphs=4,registered_controls=6,registered_controls_violated=facts["findings"]["preregistered_controls_violated"],fresh_admitted=0),human_reviewed=False,errors=[],unprocessed=[],decision="pause fresh eligibility and all same-epoch scientific rule changes pending A6/A8 adjudication"))
print(json.dumps(dict(audit_path=str((OUT/"audit.json").relative_to(ROOT)),audit_sha256=sha(OUT/"audit.json"),role_sha256=sha(OUT/"role_A7_diagnostic_manifest.json"),sources=[dict(id=r["reaction_id"],child=len(r["child_production_outcomes"]),dispatcher=len(r["dispatcher_production_outcomes"]),historical=len(r["historical_exact_target_matches"]),C3OH=r["pyrone_C3_OH"]) for r in results],registered_control_violations=facts["findings"]["preregistered_controls_violated"])))
