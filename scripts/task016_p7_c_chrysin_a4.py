"""A4 independent original chrysin source graph transcription, donor from official raw identity."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from rdkit import Chem
from rdkit.Chem import Descriptors,rdMolDescriptors
from scripts.operate import write
from scripts.task016_p7_c_extract_a4 import product,canonical
from scripts.task016_p7_structure_harness import _validated
ROOT=Path.cwd();B=ROOT/"outputs/task016-p7/v1/C/E01";O=B/"fresh/alternate/A4_CHRYSIN"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):
 p=O/n
 if p.exists():raise RuntimeError("immutable extraction already exists")
 write("TASK-016-P7",str(p.relative_to(ROOT)),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
inp=B/"stages/batches/CHRYSIN_PUBLIC_SI/chrysin_reaction_graph_input_manifest.json";manifest=json.loads(inp.read_text());hs=sha(inp)
dp=ROOT/manifest["donor_identity_raw_pointer"]["path"]
assert sha(dp)==manifest["donor_identity_raw_pointer"]["sha256"]
d=json.loads(dp.read_text())["PropertyTable"]["Properties"][0];donor=canonical(d["SMILES"])
fig=ROOT/"data/raw/task016-p7/C/d47ce587bbd6371fc976a3a165d8ff0bed7c546441be070bb8b4197f4ad14d99.attempt-1.gif";si=ROOT/"data/raw/task016-p7/C/49056885bcaba1963c3a7ff01a249f287f9de32db4d786dd526c14653ec87b65.attempt-2.pdf"
rr=[]
for ident,raw,formula,observed,calc,location in [("CH6","O=c1cc(-c2ccccc2)oc2cc(O)cc(O)c12","C21H20O9",417.1166,417.1186,["main Fig2 R1=R2=H, complete depicted beta-D source product","SI TableS1; FigS4; FigS7 and S8 C1 product"]),("LU6","O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12","C21H20O11",449.1063,449.1063,["main Fig2 R1=R2=OH, complete depicted beta-D source product","SI TableS1; FigS12 and S13 luteolin source product"])]:
 a=canonical(raw);p=product(a,"C6");mol=Chem.MolFromSmiles(p);assert rdMolDescriptors.CalcMolFormula(mol)==formula
 r=dict(reaction_id="C-CHRYSIN-"+ident,acceptor_smiles=a,donor_smiles=donor,product_smiles=p,bond_atoms=dict(acceptor_atom="source:C6",donor_atom="source:Glc-C1",product_atoms=["source:C6","source:Glc-C1"]),site="C6",sugar_identity="D-glucopyranose",anomer_stereo="beta-D-glucopyranose",direction="acceptor+donor->product",step_count=1,evidence_location=location,structure_origin="dual_independent_source_graph_transcription",independent_extraction_completed=True,dual_independent_reconciliation_completed=False,structure_evidence_pointer=dict(path=str(fig.relative_to(ROOT)),sha256=sha(fig)),additional_structure_evidence_pointer=dict(path=str(si.relative_to(ROOT)),sha256=sha(si)),reference_precursors=[a,donor],agent_role="A4",input_manifest_sha=hs,read_other_extractor_output=False,read_model_outcome=False,extraction_id="A4-C-E01-C-CHRYSIN-"+ident,source_product_formula=formula,source_product_formula_basis="counted independently from original source Fig2 atom graph; not claimed as reported LCMS formula",source_product_exact_mass=observed-1.007276466812,source_exact_mass_basis="source measured TableS1 protonated [M+H]+ value minus proton mass; source observed/calculated values retained separately",source_measured_ion=dict(adduct="[M+H]+",observed_mz=observed,source_calculated_mz=calc),source_naming_check=True,source_doi=manifest["doi"],source_donor_identity_chain=dict(source_explicit_name="UDP-glucose",source_location="main Fig2 UDP-glucose metabolic donor and glucosyltransferase reaction; source public abstract explicitly enhanced UDP-glucose pool",CID=d["CID"],InChI=d["InChI"],InChIKey=d["InChIKey"],official_raw_pointer=dict(path=str(dp.relative_to(ROOT)),sha256=sha(dp)),complete_official_raw_SMILES_serialization=True),required_context=dict(mode="enzymatic",donor_name="UDP-glucose"),prediction_conditions_verified=False,evidence_eligible=False,human_reviewed=False)
 _validated(r);rr.append(r)
p=O/"extractor_A4.jsonl"
if p.exists():raise RuntimeError("immutable rows")
write("TASK-016-P7",str(p.relative_to(ROOT)),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rr))
save("role_A4_manifest.json",dict(task="TASK-016-P7",epoch_id="C-E01",agent_role="A4 Structure Extractor",timestamp=datetime.now(timezone.utc).isoformat(),input_manifest_sha={str(inp.relative_to(ROOT)):hs},output_files_sha256={str(p.relative_to(ROOT)):sha(p)},source_evidence_pointers=[dict(path=str(x.relative_to(ROOT)),sha256=sha(x)) for x in (fig,si,dp)],counts=dict(processed=2,source_graph_complete=2,schema_validated=2,independent_source_qualified=0,passed=0,rejected=0,pending=2),read_other_extractor_output=False,read_model_outcome=False,read_holdout=True,current_extraction_model_outcomes_unread=True,prior_distinct_role_WASABI_runtime_diagnostic_pointer="outputs/task016-p7/v1/C/E01/postfreeze_diagnostics/C3H_semantic_audit/role_label_correction.json",scope_built_or_modified=False,fresh_admission=False,errors=[],unprocessed=[],pending="A3 identity + A5 independent original source transcription + A6 reconciliation/closure; epoch semantics paused",human_reviewed=False))
print(json.dumps(dict(extraction_path=str(p.relative_to(ROOT)),extraction_SHA=sha(p),role_SHA=sha(O/"role_A4_manifest.json"),source_graphs=2,schema_validated=2,source_qualified=0)))
