"""A6 source-only R5 reconciliation; pending stereo/donor and prior exposure cannot enter panel."""
import json
from pathlib import Path
from collections import Counter
from rdkit import Chem
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_hashes,verify_stage_chain,role_manifest,freeze_stage_manifest
from scripts.task016_p7_c_e02_http import E,BASE,immutable_json,append,rows
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
from scripts.task016_p7_closure_harness import canonical,closure_tokens
from scripts.task016_p7_source_alias_closure import assert_fresh
B=E/"fresh/C-E02-R5";P4=B/"A4_fixed_extraction_v1";P5=B/"A5_fixed_extraction_v1";O=B/"A6_source_reconciliation_v2"
def js(p):return json.loads(p.read_text())
def no_stereo(s):
    m=Chem.MolFromSmiles(s);assert m is not None
    Chem.RemoveStereochemistry(m)
    return Chem.MolToSmiles(m,canonical=True,isomericSmiles=True)
def main():
    r4=P4/"A4_role_manifest.json";r5=P5/"A5_role_manifest.json";a=js(r4);b=js(r5)
    f4={x["path"]:x["sha256"] for x in a["outputs"]};f5=b["all_output_files_sha256"]
    verify_hashes(f4);verify_hashes(f5)
    assert a["common_input"]["path"]==b["input_manifest"]["path"] and a["common_input"]["sha256"]==b["input_manifest"]["sha256"]
    assert not a["independence"]["A5_A6_model_read"] and not b["independence"]["A4_A6_final_structures_read"]
    ip=ROOT/a["common_input"]["path"];common=js(ip);g5=ROOT/common["G5_pointer"]["path"];verify_stage_chain(g5,common["G5_pointer"]["sha256"])
    ident=E/"fresh/C-E02-R5-A3/source_original_identity_verification.v4.json";i=js(ident)
    assert i["source_original_identity_verified"] and i["metadata_identity_verified"] and i["v3_missing_author_field_claim_corrected"]
    x4={x["source_id"]:x for x in rows(P4/"A4_nine_source_dispositions.jsonl")};x5={x["source_id"]:x for x in js(P5/"A5_source_dispositions.json")["sources"]}
    assert len(x4)==len(x5)==9 and set(x4)==set(x5)=={x["source_id"] for x in common["sources"]}
    dis=[]
    for sid,x in x4.items():
        y=x5[sid];original=sid=="C-E02-R5-PMID-31418788"
        assert (x["original_object_count"]>0)==original and (len(y["original_objects"])>0)==original
        assert x["fresh_admitted"] is False and y["fresh_admitted"] is False
        dis.append(dict(source_id=sid,doi=x["DOI_hint"],pmid=x["PMID_hint"],A4_literal=x["disposition"],A5_literal=y["A5_disposition"],semantically_reconciled=True,source_original_identity_verified=original,primary_chemically_observed=original,metadata_not_chemical_evidence=not original,source_qualified_C6=0,fresh_admitted=0,disposition="deferred_complete_donor_product_stereo_and_source_conflicts" if original else "deferred_public_primary_access_metadata_only"))
    # Activity and status projections are explicit; raw literals and all original objects remain untouched.
    c4={};
    for x in rows(P4/"A4_assay_table_cells.jsonl"):
        p=x["pointer"];t=int(p["table"])
        if t==1:key=(1,p["organ"],p["column"]+" activity")
        else:
            _,axis,name=x["id"].split(":",2);key=(3,name,axis+" C-glucosylation activity")
        status="ND" if x["value"] is None else "numeric"
        assert key not in c4;c4[key]=dict(value=x["value"],SD=x["SD"],status=status,raw_literal=x["literal"],raw_pointer=p)
    table2_fields={"protein_mg":"Protein","total_activity_pkat":"Total activity","specific_activity_pkat_per_mg":"Specific activity","purity_fold":"Purity","yield_percent":"Yield"}
    for x in js(P4/"A4_Table2_complete_purification.json"):
        for field,metric in table2_fields.items():c4[(2,{"Reactive Blue4-A":"Reactive Blue 4-A","Reactive Blue4-B":"Reactive Blue 4-B"}.get(x["step"],x["step"]),metric)]=dict(value=x[field],SD=None,status="numeric",raw_field=field,raw_pointer=x["pointer"])
    t4_fields={"Km_uM":("Km","Km_SD"),"kcat_per_s":("kcat","kcat_SD"),"kcat_over_Km_per_M_s":("kcat/Km",None)}
    for x in js(P4/"A4_Table4_complete_kinetics.json"):
        row="Apigenin" if x["substrate"]=="apigenin" else x["substrate"]
        for field,(metric,sd) in t4_fields.items():c4[(4,row,metric)]=dict(value=x[field],SD=x[sd] if sd else None,status="numeric",raw_field=field,raw_pointer=x["pointer"])
    t5=js(P5/"A5_literal_tables1_4.json");c5={(x["table"],x["row_literal"],x["metric"]):x for x in t5["cells"]}
    assert len(c4)==len(c5)==81 and set(c4)==set(c5),(len(c4),len(c5),sorted(set(c4)^set(c5)))
    cmp=[];counts=Counter();per=Counter()
    for key,x in c4.items():
        y=c5[key];equal=(x["value"],x["SD"],x["status"])==(y["value"],y["SD"],y["value_status"])
        if not equal:raise ValueError("Independent literal numeric/SD/status disagreement: "+str(key))
        counts[x["status"]]+=1;per[str(key[0])]+=1
        counts["explicit_numeric_zero"]+=int(x["value"] is not None and x["value"]==0)
        cmp.append(dict(table=key[0],row=key[1],metric=key[2],A4=x,A5=y,equal_values_SD_status=True))
    assert counts["numeric"]==70 and counts["ND"]==11 and counts["explicit_numeric_zero"]==0
    immutable_json(O/"81_independent_table_cell_comparisons.json",dict(cells=cmp,counts=dict(counts),per_table_counts=dict(per),activity_cells=30,purification_cells=45,kinetic_parameter_cells=6,independent_reaction_count_inferred=False,raw_literal_formatting_not_rewritten=True,explicit_projections=dict(A4_numeric_positive="numeric",A4_ND_categories="ND",A4_Table1_column="column + activity",A4_Table2=table2_fields,A4_Table2_row_label_alias={"Reactive Blue4-A":"Reactive Blue 4-A","Reactive Blue4-B":"Reactive Blue 4-B"},A4_Table4_substrate_apigenin="Apigenin",A4_Table4=t4_fields)))
    e4=js(P4/"A4_S5D_expression_values_including_zeros.json");e5=js(P5/"A5_expression_RPKM_literal_zeroes.json")["rows"]
    v4={(x["gene"],x["organ"]):x for x in e4};v5={(x["gene_literal"].split("(")[1].split(")")[0],x["organ_literal"]):x for x in e5}
    assert len(v4)==len(v5)==18 and set(v4)==set(v5)
    for k,x in v4.items():assert x["RPKM"]==v5[k]["RPKM"] and x["source_literal"]==v5[k]["literal"]
    assert sum(x["RPKM"]==0 for x in v4.values())==6
    immutable_json(O/"18_expression_values_separate_zero_reconciliation.json",dict(cells=18,zero_cells=6,all_values_and_raw_literals_equal=True,gene_projection="WjGT ID in original contig label parentheses",assay_reaction_cells=False,A4_pointer=pointer(P4/"A4_S5D_expression_values_including_zeros.json"),A5_pointer=pointer(P5/"A5_expression_RPKM_literal_zeroes.json")))
    graphs5={x["graph_id"]:x for x in js(P5/"A5_independent_source_graphs.json")["graphs"]};gcomp=[]
    for x in js(P4/"A4_independent_acceptor_scaffold_graphs.json"):
        y=graphs5[x["source_name"]+"_source_acceptor"]
        equal=canonical(x["canonical_isomeric_smiles"])==canonical(y["isomeric_SMILES"]);assert equal
        gcomp.append(dict(object_role="acceptor",name=x["source_name"],canonical_graph_equal=True,full_stereo_graph_equal=True,A4_source_pointer=x["pointer"],A5_source_pointer=y["source_pointer"]))
    p4=js(P4/"A4_Fig2D_product_constitution_and_stereo_pending.json");prod5=graphs5["isovitexin_source_product"]
    assert no_stereo(p4["canonical_SMILES_stereochemistry_unassigned"])==no_stereo(prod5["isomeric_SMILES"])
    assert len(p4["pending_absolute_stereo_centers"])==5 and p4["unreadable_atoms"]==[] and p4["full_stereo_graph"] is None
    immutable_json(O/"source_graph_partial_full_comparison.json",dict(complete_acceptor_matches=gcomp,complete_acceptor_graph_matches=2,product_constitution_matches=1,product_full_stereo_dual_match=False,product_stereo_pending_centers=p4["pending_absolute_stereo_centers"],A4_reading_limitation_not_source_absence=True,A5_complete_product_is_not_dual_verification=True,A4_product_pointer=pointer(P4/"A4_Fig2D_product_constitution_and_stereo_pending.json"),A5_product_pointer=pointer(P5/"A5_independent_source_graphs.json"),full_donor_graphs=0,full_reference_reactions=0,unresolved_material_source_RT_mass_conflicts=True))
    # Current freshness is checked against prior exposure, separately from future rename guards on this batch.
    old=ROOT/"outputs/task016-p7/v1/C/E01/fresh/alternate/A4_WASABI_product_graphs.jsonl";oldrows=rows(old);prior=[]
    for x in oldrows:
        prior.append(dict(**x,development_exposed=True,exposure_type="C-E01_fixed_endpoint_prior_to_C-E02",closure_tokens=sorted(closure_tokens(x))))
    renamed=dict(product_smiles=prod5["isomeric_SMILES"],doi="10.9999/renamed-not-real",reaction_id="renamed-current-R5-AP6")
    try:assert_fresh(renamed,prior)
    except ValueError as exc:historical_probe=dict(actually_rejected=True,error=str(exc),basis="exact graph target already fixed in prior C-E01 Wasabi source 10.1007/s10529-021-03165-3, distinct source from current2019 DOI",prior_pointer=pointer(old))
    else:raise ValueError("historical target bypass")
    hfile=E/"pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl";hyp=rows(hfile)
    names={x["acceptor_name_literal"].casefold():x for x in hyp}
    assert "apigenin" in names and "luteolin" in names
    immutable_json(O/"actual_prior_target_and_name_exposure_check.json",dict(historical_target_probe=historical_probe,literal_pre_G4_hypotheses_matches=[names[k] for k in ["apigenin","luteolin"]],unverified_hypotheses_not_upgraded_to_source_truth=True,name_graph_identity_universe_complete=False,current_fresh_admitted=0,postscope_self_review_not_used_to_retroactively_disqualify_current_freshness=True))
    exp=[]
    for gid,g in graphs5.items():
        token="target:"+canonical(g["isomeric_SMILES"])
        exp.append(dict(task=TASK,epoch_id="C-E02",batch_id="C-E02-R5",exposure_id="C-E02-R5:observed-source-graph:"+gid,exposure_type="postscope_original_structure_observation",development_exposed=True,future_fresh_eligible=False,eligible_for_fresh_holdout=False,source_id="C-E02-R5-PMID-31418788",doi="10.1093/pcp/pcz164",pmid="31418788",closure_tokens=["doi:10.1093/pcp/pcz164","pmid:31418788",token],product_smiles=g["isomeric_SMILES"],source_pointer=g["source_pointer"],graph_observed_in_A5=True,dual_complete_graph_verified=gid in ["apigenin_source_acceptor","luteolin_source_acceptor"],role_of_object_not_necessarily_reaction_product=gid!="isovitexin_source_product",source_qualified_reaction=False,actual_registered_at=now(),first_chemical_observation_timestamp_exact=None,registration_is_not_backdated=True,human_reviewed=False))
    save_rows(O/"permanent_postscope_source_graph_exposures.jsonl",exp)
    probes=[]
    for field,value in [("doi","10.1093/pcp/pcz164"),("pmid","31418788")]:
        try:assert_fresh({field:value,"reaction_id":"future-renamed"},exp)
        except ValueError as exc:probes.append(dict(field=field,actually_rejected=True,error=str(exc),future_intake_guard_only=True))
        else:raise ValueError("future source alias bypass")
    immutable_json(O/"actual_future_source_rename_probes.json",probes)
    save_rows(O/"9_source_disposition_reconciliation.jsonl",dis)
    summary=dict(task=TASK,agent_role="A6 Reconciliation & Closure Auditor",at=now(),batch_id="C-E02-R5",independent_source_dispositions_agree=9,primary_original_sources=1,primary_original_identity_passed=1,metadata_only_access_deferred=8,author_manuscript_pages=56,source_doi="10.1093/pcp/pcz164",source_direct_flavone_C6_positive_acceptors=2,complete_acceptor_graph_matches=2,complete_product_constitution_matches=1,complete_product_stereo_dual_matches=0,product_stereo_centers_pending=5,full_donor_graphs=0,complete_direct_flavone_C6_reference_reactions=0,source_qualified_C6=0,fresh_admitted=0,assay_activity_measurement_cells=30,purification_measurement_cells=45,kinetic_parameter_cells=6,independently_equal_table_cells=81,table_numeric=70,table_ND=11,table_NT=0,table_explicit_numeric_zero=0,expression_values=18,expression_explicit_zero=6,expression_zero_not_reaction_negative=True,actual_historical_target_rename_rejections=1,actual_future_DOI_PMID_rename_rejections=2,all_material_mass_RT_conflicts_preserved=True,full_chemical_round_complete=False,source_saturation=False,source_access_exhausted=False,scope_changed=False,scientific_ABE_cells=0,metrics=None,new_HTTP=0,new_MCTS=0,human_reviewed=False)
    immutable_json(O/"A6_source_reconciliation_summary.json",summary)
    out=[p for p in sorted(O.glob("*.json*")) if p.is_file()]
    ins=[Path(__file__),ROOT/"scripts/task016_p7_source_alias_closure.py",r4,r5,ip,g5,ident,old,hfile,P4/"A4_postfreeze_SHA_verification.json"]+[ROOT/p for p in f4]+[ROOT/p for p in f5]
    em=O/"permanent_exposure_manifest.json";immutable_json(em,dict(task=TASK,approval_type="agent_delegated",at=now(),human_reviewed=False,input_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in ins},output_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in out},new_graph_exposures=4,new_unique_source_exposures=0,source_already_registered_in_custodian_v1=True,future_intake_must_bind=True,chemical_qualification_granted=False));out.append(em)
    role=role_manifest("A6 Reconciliation & Closure Auditor","C-E02",ins,out,dict(processed=9,passed=0,rejected=0,pending=9),read_holdout=True,read_model_outcome=False,unprocessed=["8 primary article/SI access gaps","Full donor source identity/graph","A4 product absolute stereo serialization","Material RT/mass conflicts","All name/synonym/source closure universe","No fresh panel admitted"])
    role.update(root_authored_reconciliation=True,blind_chemical_validation=False,independent_chemical_validation=False,source_direct_positive_observations_not_new_fresh=True)
    rp=O/"role_A6_manifest.json";immutable_json(rp,role)
    dest=E/"stages/batches/C-E02-R5";freeze_stage_manifest(dest,"G6_IDENTITY_STRUCTURE_ADMIT",list(dict.fromkeys(ins+out+[rp])),g5,expected_previous_sha=sha_file(g5),family="C",epoch_id="C-E02")
    stage=dest/"G6_IDENTITY_STRUCTURE_ADMIT.json";verify_stage_chain(stage,sha_file(stage))
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R5",event_type="verified_existing_stage_registration",stage="G6_IDENTITY_STRUCTURE_ADMIT",stage_manifest_path=str(stage.relative_to(ROOT)),stage_manifest_sha256=sha_file(stage),registered_at=now(),admitted_count=0,formal_panel_frozen=False,approval_type="agent_delegated",human_reviewed=False,backdated=False))
    previous=BASE/"epochs/C-E02/epoch_state.v4.json";state=js(previous)
    state.update(actual_created_at=now(),previous_state_pointer=pointer(previous),G6_batches=4,R5_A4_A5_status="fixed_and_A6_reconciled_with_product_stereo_and_donor_pending",R5_A6_pointer=pointer(O/"A6_source_reconciliation_summary.json"),R5_historical_target_graph_alias_rejected=True)
    state["stage_branch_pointers"].append(pointer(stage));ep=BASE/"epochs/C-E02/epoch_state.v5.json";immutable_json(ep,state)
    print(json.dumps(dict(G6=pointer(stage),summary=pointer(O/"A6_source_reconciliation_summary.json"),epoch_state=pointer(ep),equal_measurement_cells=81,fresh=0)))
if __name__=="__main__":main()
