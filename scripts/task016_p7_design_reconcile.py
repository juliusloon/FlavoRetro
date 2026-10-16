"""A6 reconciles two immutable extraction outputs and freezes only qualified supports."""
import argparse,json
from pathlib import Path
from scripts.task016_p7_structure_harness import reconcile
from scripts.task016_p7_orchestrate import sha_file,role_manifest,save_json
from scripts.operate import write
from rdkit import Chem
from flavoretro.reviewed_resources import canonical_side
R=Path(__file__).resolve().parents[1];BASE=R/"outputs/task016-p7/v1"
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def main(family):
    o=BASE/("C/E01" if family=="C" else "SS")
    manifest=o/"design_source_input_manifest.json"
    a4=o/("design_extractor_A4.jsonl" if family=="C" else "design_extractor_A4_harness.jsonl")
    a5=o/"design_extractor_A5_harness.jsonl"
    xs={x["reaction_id"]:x for x in rows(a4)};ys={x["reaction_id"]:x for x in rows(a5)}
    result=[]
    for rid in sorted(set(xs)&set(ys)):
        z=reconcile(xs[rid],ys[rid])
        if family=="SS" and z.get("differences")==["donor_graph"]:
            pointer=ys[rid]["identity_chain"]["raw_database_pointers"]["donor"]
            raw_path=R/pointer["path"]
            if sha_file(raw_path)!=pointer["sha256"]:raise RuntimeError("donor raw SHA drift")
            source_donor=json.loads(raw_path.read_text())["PropertyTable"]["Properties"][0]
            mol_a=Chem.MolFromSmiles(xs[rid]["donor_smiles"]);mol_b=Chem.MolFromSmiles(ys[rid]["donor_smiles"])
            key_a=Chem.MolToInchiKey(mol_a);key_b=Chem.MolToInchiKey(mol_b)
            full_a=Chem.MolToInchi(mol_a);full_b=Chem.MolToInchi(mol_b)
            published=canonical_side([source_donor["SMILES"]])
            if (key_a!=key_b or key_a!=source_donor["InChIKey"] or full_a!=full_b
                    or published!=canonical_side([xs[rid]["donor_smiles"]])):
                raise RuntimeError("donor discrepancy not proven to be authoritative same stereochemical identity")
            original=z
            # Deliberate A6 resolution: preserve both independent rows, choose the
            # authoritative archived isomeric SMILES encoding for runtime references.
            z=dict(original,status="reconciled",structure_complete=True,reference_precursor_complete=True,
                   acceptor_smiles=canonical_side([xs[rid]["acceptor_smiles"]]),
                   product_smiles=canonical_side([xs[rid]["product_smiles"]]),donor_smiles=published,
                   reference_precursors=sorted([canonical_side([xs[rid]["acceptor_smiles"]]),published]),
                   site=xs[rid]["site"],sugar_identity=xs[rid]["sugar_identity"],anomer_stereo=xs[rid]["anomer_stereo"],
                   bond_atoms=xs[rid]["bond_atoms"],differences=[],
                   evidence_pointers=[xs[rid]["structure_evidence_pointer"],ys[rid]["structure_evidence_pointer"]],
                   donor_serialization_reconciliation=dict(original_differences=["donor_graph"],
                     decision="authoritative same Standard InChI with complete stereo layers; uracil keto/enol encoding difference resolved to archived PubChem isomeric SMILES",source_CID=source_donor["CID"],standard_InChI=full_a,InChIKey=key_a,raw_source_pointer=pointer,
                     extractor_A4_donor=xs[rid]["donor_smiles"],extractor_A5_donor=ys[rid]["donor_smiles"],selected_runtime_donor=published,
                     both_original_extractions_preserved=True,approval_type="agent_delegated"))
        z["instance_id"]=ys[rid]["instance_id"]
        z["pmcid"]=ys[rid]["pmcid"];z["reconciled"]=z["status"]=="reconciled"
        result.append(z)
    deferred=[]
    if family=="C":
        deferred=rows(o/"design_A5_deferred.jsonl")
    # Raw-only preregistered source universe cannot be silently reduced.
    raw=json.loads(manifest.read_text());raw_rows=raw["objects"] if family=="C" else raw["reaction_source_chains"]
    expected={x["reaction_id"] for x in raw_rows}
    if set(xs)|set(ys)|{x["reaction_id"] for x in deferred}!=expected:raise RuntimeError("extraction disposition universe mismatch")
    identities=rows(o/"source_identity_verification.jsonl")
    approved=[x for x in result if x["reconciled"]]
    source_ids={x["pmcid"] for x in approved}
    eligible_identities=[x for x in identities if x["pmcid"] in source_ids]
    identity_ok=(source_ids=={x["pmcid"] for x in eligible_identities} and all(x["source_identity_verified"] is True for x in eligible_identities))
    templates=json.loads((o/"formal_scope_candidates.json").read_text()) if family=="C" else rows(o/"scope_templates_proposed.jsonl")
    approved_instance_ids={x["instance_id"] for x in approved}
    scopes=[x["template_id"] for x in templates if set(x["support_instances"])<=approved_instance_ids]
    if not scopes:raise RuntimeError("no fully qualified selected scope")
    p=o/"dual_structure_reconciliation.jsonl";write("TASK-016-P7",str(p.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in result))
    q=dict(task="TASK-016-P7",epoch_id=family+"-E01",agent_role="A3/A5/A6 independent qualification",qualification_scope="selected scope bank only; excluded/deferred records remain explicitly unqualified",passed=identity_ok and all(x["reconciled"] for x in result),source_identity_verified=identity_ok,dual_structure_reconciled=all(x["reconciled"] for x in result),input_manifest_sha=sha_file(manifest),approved_scope_ids=scopes,approved_reaction_ids=sorted(approved_instance_ids),approved_sources=sorted(source_ids),source_identity=eligible_identities,source_universe=dict(processed=len(expected),passed=len(approved),deferred=len(deferred),disagreements=sum(not x["reconciled"] for x in result)),deferred=deferred,unresolved_reconciliations=[x for x in result if not x["reconciled"]],verified_input_files_sha256={str(v.relative_to(R)):sha_file(v) for v in [manifest,a4,a5,p,o/"source_identity_verification.jsonl"]},human_reviewed=False,independent_chemical_validation=False)
    path=o/"design_independent_qualification.json";save_json(path,q,immutable=True)
    save_json(o/"role_A6_design_qualification_manifest.json",role_manifest("A6 Reconciliation & Closure Auditor",family+"-E01",[manifest,a4,a5,o/"source_identity_verification.jsonl"],[p,path],dict(processed=len(expected),passed=len(approved),pending=len(deferred),rejected=0),errors=q["unresolved_reconciliations"],unprocessed=deferred))
    print(dict(family=family,passed=q["passed"],structures=len(approved),deferred=len(deferred),scopes=len(scopes),differences=[x["differences"] for x in result if x["differences"]]))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("family",choices=["C","SS"]);main(p.parse_args().family)
