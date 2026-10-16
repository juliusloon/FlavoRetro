"""A5 independently decodes raw PubChem InChI; never reads A4 final graph rows."""
import json
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,save_json,role_manifest
from flavoretro.reviewed_resources import canonical_side
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/SS"
def graph_from_inchi(path,expected_cid):
    rows=json.loads(path.read_text())["PropertyTable"]["Properties"]
    if len(rows)!=1 or rows[0]["CID"]!=expected_cid:raise RuntimeError("ambiguous database CID identity")
    row=rows[0];mol=Chem.MolFromInchi(row["InChI"])
    if mol is None:raise RuntimeError("InChI graph parse failure")
    if rdMolDescriptors.CalcMolFormula(mol)!=row["MolecularFormula"]:raise RuntimeError("PubChem formula/graph mismatch")
    if Chem.MolToInchiKey(mol)!=row["InChIKey"]:raise RuntimeError("PubChem InChIKey mismatch")
    return canonical_side([Chem.MolToSmiles(mol,isomericSmiles=True)]),row

def main():
    input_path=O/"design_source_input_manifest.json";m=json.loads(input_path.read_text())
    by_cid={}
    for rel,h in m["raw_input_files_sha256"].items():
        p=R/rel
        if sha_file(p)!=h:raise RuntimeError("raw source input drift")
        if p.name.endswith("structure_database"):
            x=json.loads(p.read_text())
            for v in x.get("PropertyTable",{}).get("Properties",[]):
                if v["CID"] in by_cid:raise RuntimeError("duplicate raw CID needs explicit reconciliation")
                by_cid[v["CID"]]=p
    records=[]
    for spec in m["reaction_source_chains"]:
        graphs={};property_rows={};pointers={}
        for role,cid in spec["CID_by_role"].items():
            graph,raw=graph_from_inchi(by_cid[cid],cid);graphs[role]=graph;property_rows[role]=raw
            pointers[role]=dict(path=str(by_cid[cid].relative_to(R)),sha256=sha_file(by_cid[cid]),CID=cid,serialization="InChI",source_name=spec["source_names"][role])
        acceptor=Chem.MolFromSmiles(graphs["acceptor"]);product=Chem.MolFromSmiles(graphs["product"])
        if product.GetNumHeavyAtoms()-acceptor.GetNumHeavyAtoms()!=10:raise RuntimeError("Rha transfer atom conservation")
        if not product.HasSubstructMatch(acceptor,useChirality=True):raise RuntimeError("full acceptor conservation including stereo")
        records.append(dict(reaction_id=spec["reaction_id"],instance_id=spec["reaction_id"],acceptor_smiles=graphs["acceptor"],donor_smiles=graphs["donor"],product_smiles=graphs["product"],bond_atoms=spec["bond_atoms"],site=spec["site"],sugar_identity=spec["sugar_identity"],anomer_stereo=spec["anomer_stereo"],direction=spec["direction"],step_count=spec["step_count"],evidence_location=("PMC13084081 Fig2E/G, chemicals standards and SI Table6" if spec["pmcid"]=="PMC13084081" else "PMC9706480 Fig4/5; SI Supplemental FigS5 original product standards"),structure_origin="authoritative_structure_database_identity_chain",structure_evidence_pointer=pointers["product"],reference_precursors=[graphs["acceptor"],graphs["donor"]],agent_role="A5",input_manifest_sha=sha_file(input_path),read_other_extractor_output=False,extraction_id="A5-PubChem-InChI:"+spec["reaction_id"],identity_chain=dict(pmcid=spec["pmcid"],source_names=spec["source_names"],CID_by_role=spec["CID_by_role"],raw_database_pointers=pointers,original_source_input_manifest=dict(path=str(input_path.relative_to(R)),sha256=sha_file(input_path))),pmcid=spec["pmcid"],formula_checks={k:v["MolecularFormula"] for k,v in property_rows.items()},full_acceptor_conserved=True,human_reviewed=False))
    p=O/"design_extractor_A5_harness.jsonl";write("TASK-016-P7",str(p.relative_to(R)),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in records))
    save_json(O/"role_A5_harness_manifest.json",role_manifest("A5 Structure Extractor-2","SS-E01",[input_path]+list(by_cid.values()),[p],dict(processed=len(records),passed=len(records),rejected=0,pending=0),pointers=[r["structure_evidence_pointer"] for r in records]))
    print(dict(extracted=len(records),InChI_formula_key_checks=True,full_acceptor_conservation=True))
if __name__=="__main__":main()
