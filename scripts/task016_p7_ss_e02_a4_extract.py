"""SS-E02 independent A4 official-SMILES extraction from frozen raw inputs only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.operate import write
from scripts.task016_p7_structure_harness import FIELDS, _validated
TASK="TASK-016-P7"
BASE=Path("outputs/task016-p7/v1/SS/E02_design")
OUT=BASE/"A4_fixed_extraction_v1"
INPUT=BASE/"common_source_raw_only_input_v2.json"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,obj):
    if Path(p).exists(): raise RuntimeError("immutable output already exists: "+str(p))
    write(TASK,str(p),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def now(): return datetime.now(timezone.utc).isoformat()
def main():
    started=now(); manifest=json.loads(INPUT.read_text()); input_sha=sha(INPUT)
    assert input_sha=="6a560c61ada80ecfc0c74a8857fde5828bb515dda09ae799806f55dc93f469c5"
    for p,h in manifest["raw_input_files_sha256"].items(): assert sha(p)==h,p
    raw_names={x["source_name"]:x for x in manifest["source_named_official_database_raw_identity_candidates"]}
    qc=[]; molecules={}
    for name,x in raw_names.items():
        if x["properties"]["status_code"]!=200: continue
        prop=json.loads(Path(x["properties"]["path"]).read_text())["PropertyTable"]["Properties"][0]
        syn=json.loads(Path(x["synonyms"]["path"]).read_text())["InformationList"]["Information"][0]
        assert prop["CID"]==syn["CID"]
        original=prop.get("SMILES",prop.get("IsomericSMILES"))
        mol=Chem.MolFromSmiles(original); assert mol is not None
        canonical=Chem.MolToSmiles(mol,canonical=True,isomericSmiles=True)
        inchi=Chem.MolToInchi(mol); key=Chem.InchiToInchiKey(inchi)
        formula=rdMolDescriptors.CalcMolFormula(mol)
        checks={"formula":formula==prop["MolecularFormula"],"full_standard_InChI":inchi==prop["InChI"],"complete_stereo_InChIKey":key==prop["InChIKey"]}
        assert all(checks.values()),(name,checks)
        graph=dict(source_name=name,CID=prop["CID"],raw_properties={"path":x["properties"]["path"],"sha256":x["properties"]["sha256"]},raw_synonyms={"path":x["synonyms"]["path"],"sha256":x["synonyms"]["sha256"]},graph_construction="MolFromSmiles directly from original official JSON SMILES; InChI used only for independent verification",original_official_smiles=original,canonical_smiles=canonical,formula=formula,standard_inchi=inchi,full_stereo_key=key,checks=checks,source_name_in_synonyms=any(name.casefold()==s.casefold() for s in syn["Synonym"]),source_CAS_matches=[],source_CAS_conflicts=[],raw_IUPACName=prop["IUPACName"],evidence_eligible=False)
        cas={"quercetin 3-O-sophoroside":"18609-17-1","kaempferol 3-O-sophoroside":"19895-95-5","quercetin 3-O-neohesperidoside":"32453-36-4","kaempferol 3-O-neohesperidoside":"142451-65-8","UDP-glucose":"28053-08-9","UDP-beta-L-rhamnose":"1955-26-6","astragalin":"480-10-4","quercetin 3-O-glucoside":"482-35-9","apigenin 7-O-glucoside":"578-74-5"}.get(name)
        if cas:
            graph["source_CAS_matches" if cas in syn["Synonym"] else "source_CAS_conflicts"].append(cas)
        if name=="UDP-glucose": graph["normalization_pending"]="Source TableS6 disodium C15H22N2Na2O17P2 CAS28053-08-9 versus named official neutral acid C15H24N2O17P2 CAS133-89-1: retain both; no silent salt/formula equivalence."
        molecules[name]=graph;qc.append(graph)
    sources={x["source_id"]:x for x in manifest["sources"]}
    rows=[]
    for focus in manifest["focus_source_assay_universe"]:
        candidate=focus["design_candidate"]; source=focus["source_id"]
        if focus["acceptor_source_label"] in ("Q3Glu","quercetin3Glc"): acceptor="quercetin 3-O-glucoside"
        elif focus["acceptor_source_label"] in ("K3Glu","kaempferol3Glc","5/astragalin"): acceptor="astragalin"
        else: acceptor="apigenin 7-O-glucoside"
        donor={"D01":"UDP-glucose","D02":"UDP-beta-L-rhamnose","D03":"UDP-apiose"}[candidate]
        if candidate=="D01": product="quercetin 3-O-sophoroside" if acceptor.startswith("quercetin") else "kaempferol 3-O-sophoroside"
        elif candidate=="D02": product="quercetin 3-O-neohesperidoside" if acceptor.startswith("quercetin") else "kaempferol 3-O-neohesperidoside"
        else: product="apiin" if acceptor.startswith("apigenin") else None
        sugar={"D01":"D-glucopyranose","D02":"L-rhamnopyranose","D03":"D-apiofuranose"}[candidate]
        anomer={"D01":"beta-D","D02":"alpha-L","D03":"beta-D"}[candidate]
        precursor=[molecules[acceptor]["canonical_smiles"],molecules[donor]["canonical_smiles"]]
        row=dict(reaction_id=focus["reaction_id"],acceptor_smiles=precursor[0],donor_smiles=precursor[1],product_smiles=molecules[product]["canonical_smiles"] if product else None,bond_atoms=dict(acceptor_atom=focus["site_atom_convention"],donor_atom=focus["donor_atom_convention"],product_atoms=[focus["site_atom_convention"],focus["donor_atom_convention"]]),site="parent_Glcp_O2",sugar_identity=sugar,anomer_stereo=anomer,direction="acceptor+donor->product",step_count=1,evidence_location=dict(source_id=source,source_assay_locations=focus["evidence_pointers"],source_chemical_names=dict(acceptor=focus["acceptor_source_label"],donor=focus["donor_source_label"],product=focus["product_source_label"])),structure_origin="authoritative_structure_database_identity_chain",structure_evidence_pointer={"path":str(INPUT),"sha256":input_sha},reference_precursors=precursor,agent_role="A4",input_manifest_sha=input_sha,read_other_extractor_output=False,extraction_id="SS-E02-A4-official-SMILES-v1-"+focus["reaction_id"],identity_chain={k:molecules[n] for k,n in (("acceptor",acceptor),("donor",donor),("product",product)) if n},source_original_pointer=sources[source]["full_original_xml"],design_candidate=candidate,source_qualification_pending=True,evidence_eligible=False,human_reviewed=False,approval_type="agent_delegated",read_model_outcomes=False,read_future_holdout=False,full_reaction_universe_complete=False)
        blockers=[]
        if donor=="UDP-glucose": blockers.append("source disodium versus named neutral acid requires explicit identity/serialization resolution")
        if product=="kaempferol 3-O-neohesperidoside": blockers.append("source CAS142451-65-8 does not occur in named CID5318761 official synonym response")
        if source=="PMC4282749" and acceptor.startswith("quercetin"): blockers.append("Q Table1 positive activity and isolated f26 NMR do not establish direct assay product-standard identification; source Table1 footnote b only annotates Kae3Glc")
        if source=="PMC13140228": blockers.append("one-pot activated UDPApi generation context retained separately from the single transfer reaction; no whole-network one-step claim")
        if product is None:
            blockers.append("5a NMR/name/mass support but no original complete machine-readable/full graphical product graph; database named lookup404. Do not reconstruct a complex graph from name/NMR alone.")
            row.update(extraction_status="deferred_product_graph",structure_complete=False,reference_precursor_complete=False)
        else:
            _validated(row); row.update(extraction_status="complete_official_reference_graph_source_qualification_pending",structure_complete=True,reference_precursor_complete=True)
        row["qualification_blockers"]=blockers
        assert all(x in row for x in FIELDS)
        rows.append(row)
    dump(OUT/"A4_official_raw_SMILES_molecule_verification.json",dict(agent_role="A4",input_manifest_sha=input_sha,started_at=started,fixed_at=now(),read_other_extractor_output=False,read_model_outcomes=False,molecules=qc))
    dump(OUT/"A4_focus_extraction.json",rows)
    complete=[x for x in rows if x["product_smiles"]]
    distinct={(x["acceptor_smiles"],x["donor_smiles"],x["product_smiles"],x["site"]) for x in complete}
    outputs={str(p):sha(p) for p in sorted(OUT.glob("*.json"))}
    final=dict(task_id=TASK,epoch_id="SS-E02",family="SS",stage="A4 independent source-first design extraction fixed",agent_role="A4",started_at=started,fixed_at=now(),input_manifest_path=str(INPUT),input_manifest_sha=input_sha,input_files_sha256=manifest["raw_input_files_sha256"],output_files_sha256=outputs,script_path="scripts/task016_p7_ss_e02_a4_extract.py",script_sha256=sha("scripts/task016_p7_ss_e02_a4_extract.py"),read_other_extractor_output=False,read_model_outcomes=False,read_future_holdout=False,approval_type="agent_delegated",human_reviewed=False,evidence_eligible=False,focus_source_assay_count=len(rows),complete_reference_graph_contexts=len(complete),deferred_product_graph_contexts=len(rows)-len(complete),distinct_complete_reference_reaction_graphs=len(distinct),scientifically_qualified_reactions=0,full_reaction_universe_complete=False,scope_or_guard_built=False,model_runs=0,explanation="10 reference contexts reduce to five distinct canonical acceptor-donor-product-site graphs; no new scope qualification or novel reaction count is implied. Root independent A5 extraction has not been accessed by A4.")
    dump(OUT/"role_A4_fixed_extraction_manifest.json",final)
    print(json.dumps({"manifest_path":str(OUT/"role_A4_fixed_extraction_manifest.json"),"sha256":sha(OUT/"role_A4_fixed_extraction_manifest.json"),"focus_contexts":len(rows),"reference_complete":len(complete),"graph_deferred":len(rows)-len(complete),"unique_reference_graphs":len(distinct),"scientifically_qualified":0}))
if __name__=="__main__":main()
