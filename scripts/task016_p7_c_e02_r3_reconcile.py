"""A6 R3 source/assay reconciliation. No scope changes or reaction qualification by table count."""
import json
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest,verify_hashes,verify_stage_chain,freeze_stage_manifest
from scripts.task016_p7_c_e02_http import E,BASE,immutable_json,append,rows
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
from scripts.task016_p7_closure_harness import assert_fresh
B=E/"fresh/C-E02-R3";O=B/"A6_source_reconciliation_v1"
def main():
    p4=B/"A4_fixed_extraction_v1/role_A4_fixed_extraction_manifest.json";p5=B/"A5_fixed_extraction_v1/role_A5_fixed_extraction_manifest.json"
    four=json.loads(p4.read_text());five=json.loads(p5.read_text())
    for r in (four,five):verify_hashes(r["output_files_sha256"])
    if four["input_manifest"]!=five["common_input_manifest"] or four["read_A5_final_structure"] or five["A4_final_outputs_read"]:raise ValueError("Independent roles/common raw input invalid")
    ip=ROOT/four["input_manifest"]["path"];common=json.loads(ip.read_text());g5=ROOT/common["G5_pointer"]["path"];verify_stage_chain(g5,common["G5_pointer"]["sha256"])
    a={r["source_id"]:r for r in rows(B/"A4_fixed_extraction_v1/A4_source_dispositions.jsonl")}
    d={r["source_id"]:r for r in rows(B/"A5_fixed_extraction_v1/A5_complete_source_dispositions.jsonl")}
    if set(a)!=set(d) or len(a)!=21:raise ValueError("source universe differs")
    pairs={"no_original_in_frozen_input":"no_readable_original_in_frozen_batch_chemistry_unknown","redirect_stub_only":"redirect_placeholder_primary_and_SI_missing","secondary_review_only":"readable_secondary_review_not_primary_qualified","repository_landing_abstract_only":"repository_abstract_only_primary_and_SI_missing","graphical_abstract_partial_only":"graphic_only_primary_and_SI_missing","primary_hydroxyflavanone_C_transfer_outside_direct_flavone_scope":"readable_primary_plus_embedded_SI_out_of_domain_positive_contexts_and_direct_flavone_ND"}
    reconciled=[];exposures=[];probes=[];hints={s["source_id"]:s for s in common["sources"]}
    identities={r["doi"]:r for r in rows(E/"fresh/C-E02-R3R4-A3/source_publication_identity.v2.jsonl")}
    for sid in sorted(a):
        x=a[sid];y=d[sid];h=hints[sid]
        if pairs[x["A4_disposition"]]!=y["disposition"]:raise ValueError("Source disposition disagreement")
        if x["complete_scope_aligned_positive_graphs"]!=0 or y["complete_graph_fresh_candidates"]!=0 or y["source_qualified_direct_flavone_C6_positive"]!=0:raise ValueError("Nonzero candidate requires graph-level review")
        i=identities.get(h["doi"])
        reconciled.append(dict(source_id=sid,doi=h["doi"],A4_literal_disposition=x["A4_disposition"],A5_literal_disposition=y["disposition"],source_disposition_semantically_reconciled=True,
           semantic_reconciliation="Only explicit paired labels; no graph/stereo/value transformation",current_publication_identity=i["source_identity_verified"] if i else None,
           original_identity_reference_includes_later_R4_source_front=h["doi"]=="10.1111/tpj.13555",source_qualified_C6=0,complete_scope_aligned_C6_graphs=0,fresh_admitted=0,
           absent_original_is_not_negative_activity=True,source_full_chemical_universe_complete=False,source_saturation=False,
           evidence_pointers=[pointer(B/"A4_fixed_extraction_v1/A4_source_dispositions.jsonl"),pointer(B/"A5_fixed_extraction_v1/A5_complete_source_dispositions.jsonl")]))
        if x["A4_disposition"] not in {"no_original_in_frozen_input","redirect_stub_only"}:
            hint=h["source_hint"];tokens=["doi:"+h["doi"]]
            if hint.get("pmid"):tokens.append("pmid:"+hint["pmid"])
            exposures.append(dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R3",exposure_id="C-E02-R3:postscope-source:"+sid,
              source_id=sid,doi=h["doi"],pmid=hint.get("pmid"),source_tokens=tokens,closure_tokens=tokens,development_exposed=True,eligible_for_fresh_holdout=False,future_fresh_eligible=False,
              exposure_type="post_scope_source_chemical_review_or_abstract_graphic_observation",source_qualified_C6=False,raw_objects=h["original_objects"],actual_registered_at=now(),
              exact_first_chemical_observation_time=None,after_G5_verified_by_fixed_independent_roles=True,unknown_peripheral_graphs_not_guessed=True,
              target_graph=None,reaction_signature=None,review_secondary_citation_exposure_resolution_pending=x["A4_disposition"]=="secondary_review_only",human_reviewed=False))
    ar=[r for r in rows(B/"A4_fixed_extraction_v1/A4_assay_observations.jsonl") if r["table"]=="Table1"]
    dr=rows(B/"A5_fixed_extraction_v1/A5_Table1_complete_assay_cells.jsonl")
    aliases={"purified_CGTa":"CGTa","purified_CGTb":"CGTb","recombinant_FeCGTa":"FeCGTa","recombinant_FeCGTb":"FeCGTb"}
    project4={(r["substrate_literal"],aliases[r["enzyme"]]):(r["status"],r.get("value"),r.get("sd")) for r in ar}
    project5={(r["substrate_name_literal"],r["enzyme_literal"]):(r["value_status"].replace("numeric_activity_reported","numeric_observation"),r.get("mean"),r.get("SD")) for r in dr}
    if len(ar)!=68 or len(dr)!=68 or len(project4)!=68 or project4!=project5:raise ValueError("68 raw-assay cells not independently equal")
    cells=dict(cells=68,actual_independently_equal=68,numeric=30,ND=24,NT=14,mean_zero=0,SD_zero=1,
      not_independent_covalent_reactions=True,ND_does_not_equal_numeric_zero=True,NT_does_not_equal_missing_or_negative=True,
      enzyme_label_aliases=aliases,raw_spelling_Luteorin_retained=True)
    immutable_json(O/"Table1_independent_cell_reconciliation.json",cells)
    save_rows(O/"21_source_disposition_reconciliation.jsonl",reconciled);save_rows(O/"permanent_postscope_source_exposures.jsonl",exposures)
    if len(exposures)!=4:raise ValueError("four chemically observed sources expected")
    for r in exposures:
        for field,value in (("doi",r["doi"]),("pmid",r["pmid"])):
            if value is None:continue
            try:assert_fresh({field:value,"reaction_id":"new-renamed-id"},exposures)
            except ValueError as exc:probes.append(dict(source_id=r["source_id"],field=field,actually_rejected=True,error=str(exc)))
            else:raise ValueError("new source rename bypass")
    immutable_json(O/"actual_source_rename_rejection_probes.json",probes)
    summary=dict(task=TASK,agent_role="A6 Reconciliation & Closure Auditor",at=now(),batch_id="C-E02-R3",sources=21,source_dispositions_reconciled=21,
      distinct_chemically_observed_sources=4,metadata_or_redirect_only_sources=17,direct_C6_complete_graphs=0,source_qualified_C6=0,fresh_admitted=0,
      raw_objects=11,PDFs=2,graphics=1,HTML=8,HTML_full_articles=0,primary_PDFs=1,secondary_review_PDFs=1,
      Table1=cells,actual_source_rename_rejections=len(probes),original_manuscript_title_variant_pending=1,
      source_full_chemical_round_complete=False,saturation=False,source_access_exhausted=False,graph_disagreement_count=None,
      raw_graph_count_zero_not_negative_activity=True,scope_changed=False,model_outcomes_read=False,human_reviewed=False)
    immutable_json(O/"A6_source_reconciliation_summary.json",summary)
    ins=[p4,p5,ip,g5,E/"fresh/C-E02-R3R4-A3/role_A3_manifest.v2.json",E/"fresh/C-E02-R3R4-A3/source_publication_identity.v2.jsonl",B/"A4_fixed_extraction_v1/A4_assay_observations.jsonl",B/"A5_fixed_extraction_v1/A5_Table1_complete_assay_cells.jsonl"]
    outs=[O/n for n in ("Table1_independent_cell_reconciliation.json","21_source_disposition_reconciliation.jsonl","permanent_postscope_source_exposures.jsonl","actual_source_rename_rejection_probes.json","A6_source_reconciliation_summary.json")]
    rp=O/"role_A6_manifest.json";role=role_manifest("A6 Reconciliation & Closure Auditor","C-E02",ins,outs,dict(processed=21,passed=0,rejected=0,pending=21),read_holdout=True,read_model_outcome=False,
       unprocessed=["Original source access gaps and final identity variant","Full peripheral chemistry/figures/SI","Secondary review citation/graph exposure closure","No eligible direct C6 graph exists in supplied R3 bytes"])
    role.update(role_is_isolated_process_after_fixed_both_extractors=True,scope_mutated=False);immutable_json(rp,role)
    dest=E/"stages/batches/C-E02-R3";freeze_stage_manifest(dest,"G6_IDENTITY_STRUCTURE_ADMIT",ins+outs+[rp],g5,expected_previous_sha=sha_file(g5),family="C",epoch_id="C-E02")
    stage=dest/"G6_IDENTITY_STRUCTURE_ADMIT.json";verify_stage_chain(stage,sha_file(stage))
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R3",event_type="verified_existing_stage_registration",stage="G6_IDENTITY_STRUCTURE_ADMIT",stage_manifest_path=str(stage.relative_to(ROOT)),stage_manifest_sha256=sha_file(stage),registered_at=now(),admitted_count=0,formal_panel_frozen=False,approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G6=pointer(stage),sources=21,assay_cells_independently_equal=68,permanent_source_exposures=4,actual_rename_rejections=len(probes),fresh_admitted=0)))
if __name__=="__main__":main()
