"""Resolve runtime donor serialization against an independently archived official record."""
import json
from pathlib import Path
from rdkit import Chem
from flavoretro.reviewed_resources import canonical_side
from scripts.task016_p7_orchestrate import save_json,sha_file,role_manifest
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/C/E01"
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def main():
    raw=R/"data/raw/task016-p7/root/udp-glucose-attempt-1.json"
    props=json.loads(raw.read_text())["PropertyTable"]["Properties"]
    if len(props)!=1 or props[0]["CID"]!=8629:raise RuntimeError("ambiguous official donor record")
    source=props[0];published=canonical_side([source["SMILES"]])
    supports=json.loads((O/"formal_build_candidates.json").read_text())
    dual={x["instance_id"]:x for x in rows(O/"dual_structure_reconciliation.jsonl")}
    if {x["instance_id"] for x in supports}!=set(dual):raise RuntimeError("resolution universe mismatch")
    decisions=[]
    for s in supports:
        d=dual[s["instance_id"]];original=d["donor_smiles"]
        a=Chem.MolFromSmiles(original);b=Chem.MolFromSmiles(s["donor"])
        full_a=Chem.MolToInchi(a);full_b=Chem.MolToInchi(b)
        key_a=Chem.MolToInchiKey(a);key_b=Chem.MolToInchiKey(b)
        if not (full_a==full_b==source["InChI"] and key_a==key_b==source["InChIKey"] and canonical_side([s["donor"]])==published):
            raise RuntimeError("donor runtime choice not justified by full official identity")
        if canonical_side([s["acceptor"]])!=canonical_side([d["acceptor_smiles"]]) or canonical_side([s["target"]])!=canonical_side([d["product_smiles"]]):raise RuntimeError("non-donor graph drift")
        decisions.append(dict(instance_id=s["instance_id"],original_reconciled_donor=original,selected_runtime_donor=published,full_Standard_InChI=full_a,InChIKey=key_a,source_CID=8629,raw_source_pointer=dict(path=str(raw.relative_to(R)),sha256=sha_file(raw)),decision="Use the archived official PubChem isomeric SMILES (uracil keto form); both independently extracted InChI-derived enol graphs remain unchanged. Full Standard InChI including all stereo layers and InChIKey agree.",both_original_extractions_preserved=True,approval_type="agent_delegated",chemical_identity_changed=False))
    paths=[raw,O/"formal_build_candidates.json",O/"dual_structure_reconciliation.jsonl",O/"design_extractor_A4.jsonl",O/"design_extractor_A5_harness.jsonl",O/"design_independent_qualification.json"]
    out=O/"runtime_donor_serialization_resolution.json"
    save_json(out,dict(task="TASK-016-P7",agent_role="A6",family="C",epoch_id="C-E01",passed=True,source_identity_purpose="official donor serialization selection; not reaction evidence",decisions=decisions,verified_input_files_sha256={str(p.relative_to(R)):sha_file(p) for p in paths},approval_type="agent_delegated",human_reviewed=False,independent_chemical_validation=False,read_holdout=False,read_model_outcome=False),immutable=True)
    save_json(O/"role_A6_runtime_donor_resolution_manifest.json",role_manifest("A6","C-E01",paths,[out],dict(processed=len(supports),passed=len(supports),pending=0,rejected=0)))
    print(dict(passed=True,resolutions=len(decisions),output=str(out.relative_to(R)),sha256=sha_file(out)))
if __name__=="__main__":main()
