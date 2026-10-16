"""P7 C A4: source-graph transcription, separate from A5 final structures."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write
from flavoretro.glycoside_scope import c8_sites
from rdkit import Chem
from rdkit.Chem import Descriptors,rdMolDescriptors
TASK="TASK-016-P7";OUT=ROOT/"outputs/task016-p7/v1/C/E01"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):write(TASK,str((OUT/n).relative_to(ROOT)),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def save_rows(n,v):write(TASK,str((OUT/n).relative_to(ROOT)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in v))
# Independently transcribed aglycone connectivity from source drawings, not names.
SOURCE_ACCEPTOR_GRAPHS={
 "P3R-C05":"Oc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1",
 "P3R-C06":"Oc1ccc(-c2oc3cc(O)cc(O)c3c(=O)c2O)cc1O",
 "P3R-C03":"Oc1ccc(-c2cc(=O)c3c(O)cc(O)cc3o2)cc1",
 "P3R-C04":"Oc1ccc(-c2cc(=O)c3c(O)cc(O)cc3o2)cc1O",
 "P4R-C01":"Oc1ccc(C(=O)c2ccc(O)cc2O)c(O)c1",
 "P5R-C01":"O=C(O)c1cc(O)c(O)c(O)c1",
 "P5R-C02":"O=C(O)c1cc(O)c(OC)c(O)c1",
}
SITE_BY_ID={"P3R-C05":"C8","P3R-C06":"C8","P3R-C03":"C6","P3R-C04":"C6","P4R-C01":"C3","P4R-C04":"C3","P5R-C01":"C2","P5R-C02":"C2"}
FORMULA={"P3R-C05":"C21H20O11","P3R-C06":"C21H20O12","P3R-C03":"C21H20O10","P3R-C04":"C21H20O11","P4R-C01":"C19H20O10","P5R-C01":"C13H16O10","P5R-C02":"C14H18O10"}
# Chair/wedge beta-D-glucopyranose as displayed in source figure.
GLYCOSE_GRAPH="[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"
DONOR_POINTER="data/raw/task016-p7/C/3ef8ab143d3e8b2829eb0f4f6f34092cf4994722315db010f95ac98efe3f0707.attempt-1.structure_database"
def canonical(s):return Chem.MolToSmiles(Chem.MolFromSmiles(s),isomericSmiles=True)
def site_idx(m,site):
 if site in ("C8","C6"):
  c8=next(iter(c8_sites(m)))
  if site=="C8":return c8
  rings=m.GetRingInfo().AtomRings();ring=next(r for r in rings if c8 in r and all(m.GetAtomWithIdx(i).GetAtomicNum()==6 for i in r))
  c7=next(n.GetIdx() for n in m.GetAtomWithIdx(c8).GetNeighbors() if n.GetIdx() in ring and sum(n.GetIdx() in r for r in rings)==1)
  return next(n.GetIdx() for n in m.GetAtomWithIdx(c7).GetNeighbors() if n.GetIdx() in ring and n.GetIdx()!=c8)
 if site=="C2":
  anchor=next(a for a in m.GetAtoms() if a.GetIsAromatic() and any(n.GetAtomicNum()==6 and not n.GetIsAromatic() and any(b.GetBondType()==Chem.BondType.DOUBLE and b.GetOtherAtom(n).GetAtomicNum()==8 for b in n.GetBonds()) for n in a.GetNeighbors()))
  return next(n.GetIdx() for n in anchor.GetNeighbors() if n.GetIsAromatic() and n.GetTotalNumHs()==1)
 if site=="C3":
  return next(a.GetIdx() for a in m.GetAtoms() if a.GetIsAromatic() and a.GetTotalNumHs()==1 and len([n for n in a.GetNeighbors() if n.GetIsAromatic() and any(x.GetAtomicNum()==8 for x in n.GetNeighbors())])==2)
 raise ValueError("unknown source numbering")
def product(acceptor,site):
 a=Chem.MolFromSmiles(acceptor);g=Chem.MolFromSmiles(GLYCOSE_GRAPH);rw=Chem.RWMol(Chem.CombineMols(a,g));n=a.GetNumAtoms();rw.AddBond(site_idx(a,site),n,Chem.BondType.SINGLE);rw.GetAtomWithIdx(n).SetNumRadicalElectrons(0);rw.GetAtomWithIdx(n).SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW);p=rw.GetMol();Chem.SanitizeMol(p)
 if p.GetAtomWithIdx(n).GetChiralTag()==Chem.ChiralType.CHI_UNSPECIFIED:raise ValueError("source anomeric stereo not bound")
 return Chem.MolToSmiles(p,isomericSmiles=True)
def source_input():
 if (OUT/"design_source_input_manifest.json").exists():raise RuntimeError("already immutable")
 rr=[json.loads(s) for s in (OUT/"design_candidates.jsonl").read_text().splitlines()]
 bindings=[]
 for r in rr:
  evidence=r["source_evidence"]
  if r["pmcid"]=="PMC9700910":
   fig=next(x for x in evidence["P7_source_attachments"] if "Fig9_HTML" in x["url"]);locations=["main Fig9a/b" if r["reaction_id"]=="P3R-C05" else "main Fig9c/d","body//p[21-24] and p47"]
  else:fig=evidence["figure"];locations=[{"PMC6036675":"Fig1a numbered sites and Fig1b direct C6 source graphs","PMC11480083":"Fig2c source 1a -> blue C-glycoside 3a","PMC8841362":"Fig2A C3 maclurin, sugar stereo unresolved","PMC11053098":"Fig1A beta-D source sugar graph"}[r["pmcid"]]]
  xml=r["source_identity_input"]["xml"]
  bindings.append(dict(reaction_id=r["reaction_id"],pmcid=r["pmcid"],site=SITE_BY_ID[r["reaction_id"]],sugar_identity="D-glucose",anomer_stereo="beta-D-glucopyranose" if r["reaction_id"]!="P4R-C04" else "source_stereo_unresolved",evidence_locations=locations,figure_pointer=dict(path=fig["path"],sha256=fig["sha256"]),xml_pointer=dict(path=xml["path"],sha256=xml["sha256"]),bond_atoms=dict(acceptor_atom="source:"+SITE_BY_ID[r["reaction_id"]],donor_atom="source:Glc-C1",product_atoms=["source:"+SITE_BY_ID[r["reaction_id"]],"source:Glc-C1"])))
 save("design_source_input_manifest.json",dict(task=TASK,epoch_id="C-E01",created_at=datetime.now(timezone.utc).isoformat(),contains_final_graphs=False,objects=bindings,donor_structure_pointer=dict(path=DONOR_POINTER,sha256=sha(ROOT/DONOR_POINTER)),source_product_formula_basis="literal atom inventory independently counted from original source drawings",source_exact_mass_basis="theoretical formula consistency, measured LCMS retained separately where reported"))
 print(json.dumps(dict(source_input_manifest=str((OUT/"design_source_input_manifest.json").relative_to(ROOT)),sha256=sha(OUT/"design_source_input_manifest.json"))))
def extract():
 inp=json.loads((OUT/"design_source_input_manifest.json").read_text());inp_sha=sha(OUT/"design_source_input_manifest.json")
 inchi=json.loads((ROOT/DONOR_POINTER).read_text())["PropertyTable"]["Properties"][0]["InChI"]
 donor=Chem.MolToSmiles(Chem.MolFromInchi(inchi),isomericSmiles=True)
 out=[]
 for source in inp["objects"]:
  rid=source["reaction_id"]
  if rid not in SOURCE_ACCEPTOR_GRAPHS:continue
  a=canonical(SOURCE_ACCEPTOR_GRAPHS[rid]);p=product(a,source["site"]);formula=rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(p))
  if formula!=FORMULA[rid]:raise ValueError("source atom inventory formula mismatch "+rid)
  source_formula_mol=Chem.MolFromSmiles(p)
  out.append(dict(reaction_id=rid,acceptor_smiles=a,donor_smiles=donor,product_smiles=p,bond_atoms=source["bond_atoms"],site=source["site"],sugar_identity="D-glucose",anomer_stereo="beta-D-glucopyranose",direction="acceptor+donor->product",step_count=1,evidence_location=source["evidence_locations"],structure_origin="dual_independent_source_graph_transcription",structure_evidence_pointer=source["figure_pointer"],reference_precursors=[a,donor],agent_role="A4",input_manifest_sha=inp_sha,read_other_extractor_output=False,extraction_id="A4-C-E01-"+rid,source_product_formula=FORMULA[rid],source_product_exact_mass=Descriptors.ExactMolWt(source_formula_mol),source_exact_mass_basis="theoretical exact mass of independently source-transcribed atom inventory, not measured mass",source_measured_mass=dict(kaempferol_C8_M_minus_H=447.0957) if rid=="P3R-C05" else None,source_naming_check=True,extraction_method="original source graph transcription + explicit source-numbered linkage; beta-D chair/wedge graph; donor independent PubChem InChI",human_reviewed=False))
 for r in out:
  if r["reaction_id"]=="P4R-C01":r.update(chemical_evidence_conflict=True,chemical_evidence_status="unresolved_main_vs_SI_C_O_graph_conflict",evidence_eligible=False)
 save_rows("design_extractor_A4.jsonl",out)
 save_rows("design_A4_deferred.jsonl",[dict(reaction_id="P4R-C04",reason="source maclurin Fig2A supplies no sugar stereo; original primary SI403; do not infer beta from enzyme family",source_input_manifest_sha=inp_sha),dict(reaction_id="P4R-C01",reason="main Fig2c C graph contradicts SI Fig93/94 O graph; preserve pending chemical resolution",source_conflict_pointer=str((OUT/"source_internal_conflicts.json").relative_to(ROOT)))])
 save("role_A4_design_manifest.json",dict(task=TASK,epoch_id="C-E01",agent_role="A4",input_manifest_sha256=inp_sha,output_files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in ["design_extractor_A4.jsonl","design_A4_deferred.jsonl","source_internal_conflicts.json"]},counts=dict(processed=8,passed=6,rejected=0,pending=2),read_other_extractor_output=False,read_holdout=False,read_model_outcome=False,errors=[dict(kind="source_internal_conflict",reaction_id="P4R-C01",pointer=str((OUT/"source_internal_conflicts.json").relative_to(ROOT)))],unprocessed=[],evidence_pointers=[r["structure_evidence_pointer"] for r in out],human_reviewed=False))
 print(json.dumps(dict(independent_A4_graphs=len(out),qualification_passed=6,deferred=2,manifest_sha256=inp_sha)))
if __name__=="__main__":
 {"source_input":source_input,"extract":extract}[sys.argv[1]]()
