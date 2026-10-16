"""Schema-bound A5 graph transcription using frozen raw-only design inputs."""
import json,re
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Descriptors,rdMolDescriptors
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,save_json,role_manifest
from scripts.task016_p7_c_extractor2 import C_RECORDS
from flavoretro.reviewed_resources import canonical_side
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/C/E01"
def formula_mass(formula):
    periodic=Chem.GetPeriodicTable()
    return sum(periodic.GetMostCommonIsotopeMass(symbol)*int(number or 1) for symbol,number in re.findall(r"([A-Z][a-z]?)([0-9]*)",formula))
def main():
    manifest=O/"design_source_input_manifest.json";m=json.loads(manifest.read_text())
    raw_donor=R/m["donor_structure_pointer"]["path"]
    donor_row=json.loads(raw_donor.read_text())["PropertyTable"]["Properties"][0]
    donor_mol=Chem.MolFromInchi(donor_row["InChI"])
    if donor_mol is None:raise RuntimeError("official donor InChI invalid")
    donor=canonical_side([Chem.MolToSmiles(donor_mol,isomericSmiles=True)])
    by_id={x["reaction_id"]:x for x in m["objects"]}
    out=[];deferred=[]
    for rid,pid,site,acc,target,formula in C_RECORDS:
        obj=by_id[rid]
        if rid in {"P4R-C04","P4R-C01"}:
            deferred.append(dict(reaction_id=rid,agent_role="A5",reason=("original source Figure2A lacks explicit glycosyl stereochemistry; original MiCGT2015 SI unavailable under legal access" if rid=="P4R-C04" else "main article Fig2c C product and original SI compound3a graph/NMR contain unresolved C/O conflict"),structure_complete=False,human_reviewed=False));continue
        if site!=obj["site"]:raise RuntimeError("source site disagreement")
        row=dict(reaction_id=rid,instance_id="p7-C-E01-build:"+rid,acceptor_smiles=canonical_side([acc]),donor_smiles=donor,product_smiles=canonical_side([target]),bond_atoms=obj["bond_atoms"],site=site,sugar_identity="D-glucose",anomer_stereo="beta-D-glucopyranose",direction="acceptor+donor->product",step_count=1,evidence_location=obj["evidence_locations"],structure_origin="dual_independent_source_graph_transcription",structure_evidence_pointer=obj["figure_pointer"],reference_precursors=[canonical_side([acc]),donor],agent_role="A5",input_manifest_sha=sha_file(manifest),read_other_extractor_output=False,extraction_id="A5-source-graph:"+rid,source_product_formula=formula,source_product_exact_mass=formula_mass(formula),source_product_exact_mass_origin="theoretical exact mass calculated independently from source drawing atom inventory; not a measured mass",source_naming_check=True,pmcid=pid,source_input_manifest=str(manifest.relative_to(R)),source_donor_pointer=m["donor_structure_pointer"],human_reviewed=False)
        if rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(row["product_smiles"]))!=formula:raise RuntimeError("source inventory formula mismatch")
        out.append(row)
    p=O/"design_extractor_A5_harness.jsonl";write("TASK-016-P7",str(p.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
    d=O/"design_A5_deferred.jsonl";write("TASK-016-P7",str(d.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in deferred))
    save_json(O/"role_A5_harness_manifest.json",role_manifest("A5 Structure Extractor-2","C-E01",[manifest,raw_donor],[p,d],dict(processed=len(out)+len(deferred),passed=len(out),pending=len(deferred),rejected=0),pointers=[x["structure_evidence_pointer"] for x in out]))
    print(dict(extracted=len(out),deferred=len(deferred)))
if __name__=="__main__":main()
