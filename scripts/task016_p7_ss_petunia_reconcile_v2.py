"""Petunia A6 source-qualified design supports; no fresh or scope claim."""
import json,re,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,Descriptors
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_hashes,role_manifest
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
from scripts.task016_p7_closure_harness import canonical
B=BASE/"SS/E02_design/reference_discovery_r2";A=B/"Petunia_A4_v1";D=B/"Petunia_A5_v1";O=B/"Petunia_A6_v1"
def js(p):return json.loads(p.read_text())
def norm(s):return re.sub(r"\s+","",s).casefold()
def main():
    ins=[Path(__file__),B/"Petunia_root_A6_precomparison_SHA_v2.json",B/"Petunia_dual_extraction_assignment_v2.json",B/"raw_closeout_v1/Petunia_only_design_common_raw_input.json",B/"A3_publication_identity_v1/A3_summary.json"]
    for p in (A/"role_A4_manifest.json",D/"role_A5_fixed_manifest.json"):
        r=js(p);ins.append(p);m=r["input_manifest_sha"] if isinstance(r["input_manifest_sha"],dict) else r["input_file_sha"]
        verify_hashes(m);verify_hashes(r["output_file_sha"]);ins.extend(ROOT/q for q in m);ins.extend(ROOT/q for q in r["output_file_sha"])
        assert not r["read_model_outcome"] and not r["read_holdout"]
    for p in [A/"A4_final_complete_source_transcriptions.v2.jsonl",A/"A4_final_extraction_records.v2.jsonl",A/"A4_independent_source_F1_F4_atom_and_stereo_transcription.json",A/"A4_official_UDPglucose_raw_identity_and_representation.json",D/"A5_complete_source_graph_inventory.json",D/"A5_specific_assay_product_to_structure_chains.v2.jsonl"]:assert p.is_file()
    a=js(A/"A4_independent_source_F1_F4_atom_and_stereo_transcription.json")["records"]
    d={x["source_compound_label"]:x for x in js(D/"A5_complete_source_graph_inventory.json")["graphs"]}
    mappings={"F1":("K_Glc1_2Gal","K3Gal"),"F2":("Q_Glc1_2Gal","Q3Gal"),"F3":("K_Glc1_2Glc","K3Glc"),"F4":("Q_Glc1_2Glc","Q3Glc")}
    graphs=[]
    for x in a:
        for k,gid in zip(("product","acceptor"),mappings[x["source_code"]]):
            g=x[k];h=d[gid];s=canonical(g["canonical_isomeric_smiles"]);assert s==canonical(h["canonical_isomeric_SMILES"])
            assert g["molecular_formula"]==h["formula_derived_from_graph"]==rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(s))
            assert g["standard_inchi"]==Chem.MolToInchi(Chem.MolFromSmiles(s))
            assert g["fixed_h_inchi"]==Chem.MolToInchi(Chem.MolFromSmiles(s),options="/FixedH")
            graphs.append(dict(source_code=x["source_code"],object_role=k,label=gid,canonical=s,full_stereo_equal=True,formula_equal=True,standard_InChI_equal=True,FixedH_equal=True,A4_graph=g,A5_graph=h,source_pointer=x["source_pointer"],assay_identity_separately_decided=True))
    donor4=js(A/"A4_official_UDPglucose_raw_identity_and_representation.json");dg=donor4["official_SMILES_representation"]["canonical_isomeric_smiles"];assert canonical(dg)==canonical(d["UDPGlc_official_CID8629"]["canonical_isomeric_SMILES"])
    graphs.append(dict(label="UDPGlc_official_CID8629",object_role="donor_reference",canonical=canonical(dg),full_stereo_equal=True,formula_equal=True,actual_physical_species_unknown=True,source_identity_binding=donor4["official_raw_pointer"]))
    t4=[json.loads(x) for x in (A/"A4_assay_Table1_specificity_26cells.jsonl").read_text().splitlines()]+[json.loads(x) for x in (A/"A4_assay_Table2_UDP_inhibition_10cells.jsonl").read_text().splitlines()]
    t5=[json.loads(x) for x in (D/"A5_all_relevant_assay_table_outcomes.jsonl").read_text().splitlines()]
    def key4(x):
        if x["table"]=="Tab2":return ("Table2_UDP_inhibition",float(x["added_UDP_concentration_mM"]),{"Kae 3-O-galactoside":"K3Gal","Kae 3-O-glucoside":"K3Glc"}[x["acceptor_literal"]])
        if x["experiment"]=="acceptor specificity":return ("Table1_acceptor",norm(x["sugar_acceptor_literal"]),"UDP-glucose")
        return ("Table1_donor",norm(x["sugar_donor_literal"]),{"Kae 3-O-galactoside":"K3Gal","Kae 3-O-glucoside":"K3Glc"}[x["sugar_acceptor_literal"]])
    def key5(x):
        if x["table"]=="Table2_UDP_inhibition":return (x["table"],x["UDP_concentration_mM"],x["context"].split("acceptor")[0])
        if x["table"]=="Table1_acceptor":return (x["table"],norm(x["row_label"]),"UDP-glucose")
        return (x["table"],norm(x["row_label"]),x["context"].split("acceptor")[0])
    v4={key4(x):x for x in t4};v5={key5(x):x for x in t5}
    assert len(v4)==len(v5)==36 and set(v4)==set(v5)
    tables=[]
    for k,x in v4.items():
        y=v5[k];m=x["measurement"];stat={"numeric":"numeric","not_detected":"ND","trace":"Trace"}[m["status"]]
        assert (m["mean"],m["sd"],stat)==(y["value"],y["plus_minus"],y["status"]),k
        assert norm(m["source_literal"])==norm(y["raw_literal"])
        tables.append(dict(key=list(k),A4=x,A5=y,equal_value_width_status_and_literal=True,Table1_width_not_independently_asserted_SD=x["table"]=="Tab1"))
    counts=Counter(x["status"] for x in t5);assert counts==dict(numeric=23,ND=12,Trace=1)
    m4=js(A/"A4_original_mass_RT_and_diagnostic_comparison.json")["spectra"];m5=js(D/"A5_source_MS_literals_and_retention.json");mass=[]
    assert len(m4)==12 and len(m5["Fig2c"])==8 and len(m5["FigS1"])==4
    order=m5["FigS1"]+m5["Fig2c"]
    for x,y in zip(m4,order):
        assert x["source_peak_mz_literals"]==y["observed_mz_labels_raw"]
        rt=y.get("retention_min_raw");assert x["retention_time_min"]==(float(rt) if rt is not None else None)
        mass.append(dict(A4=x,A5=y,mz_literal_equal=True,retention_equal=True,source_adduct_label=None,source_neutral_formula=None,actual_mz_not_replaced=True))
    raw=ROOT/"data/raw/task016-p7/SS/reference_discovery_r2/originals/SS-REF-ORIG-R2-d94d8131c3734af38dee07d8ca0fba65.article_version"
    tree=ET.fromstring(raw.read_bytes());ps=[" ".join("".join(x.itertext()).split()) for x in tree.findall(".//body//p")]
    assert "converted kaempferol 3-O-galactoside" in ps[22] and "glucosylation of kaempferol 3-O-glucoside" in ps[22]
    c4=[json.loads(x) for x in (A/"A4_final_complete_source_transcriptions.v2.jsonl").read_text().splitlines()]
    c5=[json.loads(x) for x in (D/"A5_specific_assay_product_to_structure_chains.v2.jsonl").read_text().splitlines()]
    q=[];curated=[]
    for x in c4:
        gid="K3Gal" if "galactoside" in x["acceptor_literal"] else "K3Glc";y=next(z for z in c5 if z.get("acceptor")==gid)
        assert canonical(x["acceptor"])==canonical(d[gid]["canonical_isomeric_SMILES"])
        prod=mappings["F1" if gid=="K3Gal" else "F3"][0]
        assert canonical(x["product"])==canonical(d[prod]["canonical_isomeric_SMILES"])
        assert x["reference_precursor_complete"] and x["source_single_catalytic_step"]
        assert y["reference_precursor_graph"]==y["acceptor_graph"]
        assert canonical(x["donor"])==canonical(dg)
        q.append(dict(record_id="SS-PETUNIA-"+gid,source_id="PMC5856881",doi="10.1007/s00425-017-2822-5",pmid="29214446",enzyme="UGT79B31",acceptor=canonical(x["acceptor"]),donor=canonical(dg),product=canonical(x["product"]),reference_precursors=[canonical(x["acceptor"]),canonical(dg)],site="parent hexose O2",parent_sugar="beta-D-Galp" if gid=="K3Gal" else "beta-D-Glcp",transferred_sugar="beta-D-Glcp",direction="single enzyme glycosyl transfer from pre-glycosylated acceptor",source_qualified_design_support=True,source_identity_verified=True,dual_full_graph_complete=True,source_original_chain=x["actual_assay_product_identity_chain"],A4_record=x,A5_record=y,physical_assay_salt_hydration_protonation=None,source_neutral_formula=None,source_neutral_exact_mass=None,source_positive_mz=x["source_product_mass"],source_neutral_mass_formula_not_invented=True,structure_origin="original Fig2a double independent transcription + actual named assay/body23/Fig3/S1",fresh_eligible=False,human_reviewed=False,independent_chemical_validation=False,scope_qualification_not_granted_here=True))
    assert len(q)==2 and len({x["acceptor"] for x in q})==2 and len({x["product"] for x in q})==2
    universe=[json.loads(x) for x in (A/"A4_final_extraction_records.v2.jsonl").read_text().splitlines()];assert len(universe)==24
    ucounts=Counter(x["disposition"] for x in universe)
    # Write only after all exact graph/table/mass/source checks above have passed.
    immutable_json(O/"9_dual_full_graph_comparisons.json",dict(task=TASK,at=now(),graphs=graphs,matched=9,A5_aglycone_reference_graphs_not_counted_as_single_step_precursors=2))
    immutable_json(O/"36_original_table_comparisons.json",dict(task=TASK,at=now(),records=tables,counts=dict(counts),all_equal=True,explicit_zero_means=0,error_width_zero=1,zero_UDP_concentration_controls=2,cell_count_not_independent_reaction_count=True))
    immutable_json(O/"12_spectra_36_mz_and_retention_comparisons.json",dict(task=TASK,at=now(),records=mass,mz_literal_count=36,retention_numeric_count=11,retention_blank_count=1,adduct_MplusH_is_diagnostic_not_explicit_source_label=True,actual_original_images_root_viewed=[pointer(ROOT/"data/raw/task016-p7/SS/reference_discovery_r2/originals/SS-REF-ORIG-R2-fb6d98f3de514ff987112288399c11a8.attachment"),pointer(ROOT/"data/raw/task016-p7/SS/reference_discovery_r2/originals/SS-REF-ORIG-R2-510793629cfe4673b475b21ea4be9221.attachment"),pointer(A/"derivatives/EPS_render_001.png")]))
    immutable_json(O/"actual_source_identity_and_assay_chain.json",dict(task=TASK,at=now(),original_XML=pointer(raw),body_paragraphs=[dict(index=i,source_literal=ps[i-1]) for i in (13,14,20,23)],A3_front_identity=pointer(B/"A3_publication_identity_v1/A3_summary.json"),source_F4_tentative_mass_only=True,Q_assay_specific_product_chain_not_completed=True,source_formula_and_neutral_mass_not_printed_not_new_failure=True,assay_standard_buffer_reference_not_protein_buffer=True,assay_concentration_and_duration_unknown=True,no_universal_NMR_standard_purification_or_full_UDP_drawing_gate=True))
    save_rows(O/"2_source_qualified_design_supports.jsonl",q)
    immutable_json(O/"24_source_assay_dispositions.json",dict(task=TASK,at=now(),records=universe,original_disposition_counts=dict(ucounts),source_qualified_design_supports=2,reported_ND_controls=12,partial=10,source_measured_zero_not_imputed=True,passed_definition="2 specific K assays with complete dual original graph and identity chain; not a scope or fresh panel"))
    exp=[]
    for gid,g in d.items():
        sm=canonical(g["canonical_isomeric_SMILES"]);exp.append(dict(task=TASK,epoch_id="SS-E02-design",source_id="PMC5856881",doi="10.1007/s00425-017-2822-5",pmid="29214446",exposure_id="Petunia-A6:"+gid,development_exposed=True,eligible_for_fresh_holdout=False,future_fresh_eligible=False,product_smiles=sm,closure_tokens=["doi:10.1007/s00425-017-2822-5","pmid:29214446","article:PMC5856881","target:"+sm],object_role=gid,assay_identity_not_implied_from_depiction=True,dual_complete_graph_verified=gid not in ("kaempferol_reference_precursor","quercetin_reference_precursor"),actual_registered_at=now(),first_global_observation_timestamp=None,not_backdated=True,human_reviewed=False))
    save_rows(O/"permanent_11_observed_graph_exposures.jsonl",exp)
    summary=dict(task=TASK,agent_role="A6 Reconciliation & Closure Auditor",created_at=now(),source_id="PMC5856881",source_qualified_design_supports=2,distinct_complete_canonical_acceptors=2,distinct_covalent_reactions=2,shared_source_closure_groups=1,all_design_not_fresh=True,dual_complete_graph_matches=9,table_cells_equal=36,table_counts=dict(counts),mz_literal_equal=36,retention_numeric_equal=11,retention_blank=1,original_reaction_pairs=24,source_ND=12,partial=10,Q_product_assay_chain_pending=True,F4_source_mass_only_assignment=True,source_neutral_formula_mass_not_reported=True,actual_salt_hydration_protonation_unknown=True,A5_precursor_v1_error_preserved=True,A5_donor_pointer_error_preserved=True,A4_DOCX_projection_error_preserved=True,A6_root_authored=True,independent_chemical_validation=False,no_scope_frozen=True,old_api7Glc_UDPApi_stratum_not_merged=True,prior_Kgal_UDPGlc_support_is_same_acceptor=True,A7_must_decide_explicit_parent_Glc_Gal_epimer_boundary_before_any_fresh=True,other5_scientific_sources_not_read=True,fresh_admitted=0,new_HTTP=0,new_MCTS=0,scientific_ABE_cells=0,metrics=None,full_chemical_round=False,source_saturation=False,human_reviewed=False)
    immutable_json(O/"A6_source_reconciliation_summary.json",summary)
    ins=list(dict.fromkeys(ins));outs=sorted(p for p in O.glob("*.json*") if p.is_file())
    pm=O/"permanent_exposure_manifest.json";prior=B/"source_exposure_custodian_v1/permanent_exposure_manifest.json";ins.append(prior)
    immutable_json(pm,dict(task=TASK,created_at=now(),inherited_source_custodian=pointer(prior),input_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in ins},output_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in outs},future_intake_must_bind=True,graph_exposures=11,source_already_design_exposed=True,chemical_qualification_granted_only_for_2_specific_design_assays=True,human_reviewed=False));outs.append(pm)
    role=role_manifest("A6 Reconciliation & Closure Auditor","SS-E02-design",ins,outs,dict(processed=24,passed=2,rejected=12,pending=10),pointers=[pointer(raw)],read_holdout=False,read_model_outcome=False,errors=["Precomparison v1 misread A5 input_manifest_sha digest as file map; corrected v2 before graph/assay comparison"],unprocessed=["10 partial specific reactions; no product identity upgrade from generic activity","Exact assay concentration/time and physical species unknown","A7 scope boundaries and replay/negative controls not performed","No fresh panel or final experiment"])
    role.update(root_authored=True,independent_chemical_validation=False,A4_A5_current_role_isolation_preserved=True,other5_scientific_sources_read=False,all_design_not_fresh=True);rp=O/"role_A6_manifest.json";immutable_json(rp,role)
    print(json.dumps(dict(summary=pointer(O/"A6_source_reconciliation_summary.json"),role=pointer(rp),supports=pointer(O/"2_source_qualified_design_supports.jsonl"),exposure=pointer(pm),fresh=0)))
if __name__=="__main__":main()
