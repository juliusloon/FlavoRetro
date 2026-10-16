"""Isolated A6 C-E02-R1 source-level reconciliation; no scope/model mutation."""
import json
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest,freeze_stage_manifest,verify_stage_chain,verify_hashes
from scripts.task016_p7_c_e02_fresh import rows,pointer,save_rows,E
from scripts.task016_p7_c_e02_http import immutable_json,append
from scripts.task016_p7_closure_harness import assert_fresh
B=E/"fresh/C-E02-R1"
O=B/"A6_source_reconciliation_v1"
def main():
    a4p=B/"A4_fixed_extraction_v1/role_A4_fixed_extraction_manifest.json"
    a5p=B/"A5_fixed_extraction_v1/role_A5_fixed_extraction_manifest.json"
    a4=json.loads(a4p.read_text());a5=json.loads(a5p.read_text())
    verify_hashes(a4["output_files_sha256"])
    for value in a5["outputs"].values():
        if sha_file(ROOT/value["path"])!=value["sha256"]:raise ValueError("A5 output drift")
    if a4["input_manifest"]!=a5["input_manifest"]:raise ValueError("different common raw input")
    if a4["read_A5_final_structures"] or a5["read_A4_final_graphs"]:raise ValueError("independence failed")
    g5=ROOT/a4["G5_pointer"]["path"]
    verify_stage_chain(g5,a4["G5_pointer"]["sha256"])
    identity_path=B/"A3_source_identity_v1/source_publication_identity.v2.jsonl"
    identity={r["pmcid"]:r for r in rows(identity_path)}
    four={r["source_id"]:r for r in rows(B/"A4_fixed_extraction_v1/source_dispositions.jsonl")}
    five={r["pmcid"]:r for r in rows(B/"A5_fixed_extraction_v1/source_dispositions.fixed.jsonl")}
    if set(four)!=set(five) or len(four)!=10 or set(four)!=set(identity):raise ValueError("10-source identity/extraction universe differs")
    aliases={"off_domain_O_glycosylation":"off_domain_O_glycosylation",
      "off_domain_chemical_C_glycosylation":"off_domain_nonflavone_chemical_C",
      "off_domain_chemical_nonflavone_C_glycosylation":"off_domain_nonflavone_chemical_C",
      "off_domain_dihydrochalcone_C_glycosylation":"off_domain_nonflavone_enzymatic_C",
      "off_domain_nonflavone_enzymatic_C_glycosylation":"off_domain_nonflavone_enzymatic_C",
      "inference_only_no_primary_reaction_assay":"inference_only_genome_expression",
      "inference_only_genome_expression":"inference_only_genome_expression",
      "off_domain_putative_insect_detoxification":"off_domain_insect_putative_metabolites",
      "off_domain_insect_detoxification_with_putative_metabolites":"off_domain_insect_putative_metabolites"}
    reconciled=[];exposures=[];probes=[]
    for pid in sorted(four):
        x=four[pid];y=five[pid];i=identity[pid]
        da=x["A4_content_disposition"];db=y["disposition"]
        if aliases[da]!=aliases[db]:raise ValueError("source domain disposition disagreement")
        if x["direct_enzymatic_flavone_C6_reaction_count"]!=0 or y["direct_enzymatic_flavone_C6_evidence_records"]!=0:raise ValueError("unexpected direct C6 candidate needs graph-level review")
        if i["source_identity_verified"] is not True:raise ValueError("publication identity unresolved")
        reconciled.append(dict(pmcid=pid,doi=i["doi"],source_publication_identity_verified=True,
          source_role="post_scope_source_review",A4_literal_disposition=da,A5_literal_disposition=db,
          semantic_projection="Only equivalent source-domain labels; no chemical graph transformation",
          reconciled_domain_disposition=aliases[da],source_eligible_C6_reactions=0,source_scientific_qualified=False,
          full_source_graphs=0,current_fresh_eligible=False,
          reason="Supplied original XML shows another reaction axis/core or inference-only/putative metabolites; no direct enzymatic flavone C6 complete reaction",
          rejection_is_not_negative_C6_activity=True,all_peripheral_reactions_or_SI_universe_complete=False,
          pointers=[pointer(B/"A4_fixed_extraction_v1/source_dispositions.jsonl"),pointer(B/"A5_fixed_extraction_v1/source_dispositions.fixed.jsonl"),pointer(identity_path)],
          raw_original_pointers=i["source_evidence_pointers"][:2],human_reviewed=False))
        src=i["raw_JATS_publication_fields"]
        tokens=["article:"+pid]
        if src.get("doi"):tokens.append("doi:"+src["doi"].lower())
        if src.get("pmid"):tokens.append("pmid:"+src["pmid"])
        exposures.append(dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R1",
          exposure_id="C-E02-R1:reviewed-source:"+pid,exposure_type="post_scope_evaluation_source_review_off_domain_or_deferred",
          development_exposed=True,eligible_for_fresh_holdout=False,current_epoch_eligible=False,
          future_fresh_eligible=False,source_tokens=tokens,closure_tokens=tokens,source_pmcid=pid,doi=src.get("doi"),
          first_chemical_observation_exact_time=None,
          verified_scope_preceded_G5_and_both_extractor_role_starts=True,actual_registered_at=now(),
          source_publication_identity_verified=True,source_chemical_qualification=False,
          target_graph=None,reaction_signature=None,unknown_peripheral_graphs_not_guessed=True,
          exposure_not_evidence_eligibility=True,origin_pointers=[pointer(a4p),pointer(a5p),pointer(identity_path)],
          human_reviewed=False))
    save_rows(O/"10_source_disposition_reconciliation.jsonl",reconciled)
    save_rows(O/"permanent_postscope_source_exposures.jsonl",exposures)
    for r in exposures:
        for field,value in (("source_pmcid",r["source_pmcid"]),("doi",r["doi"])):
            if value is None:continue
            candidate={field:value,"reaction_id":"renamed-unseen"}
            try:assert_fresh(candidate,exposures)
            except ValueError as error:
                probes.append(dict(source_id=r["source_pmcid"],field=field,actually_rejected=True,error=str(error)))
            else:raise ValueError("source rename exposure bypass")
    immutable_json(O/"actual_source_rename_rejection_probes.json",probes)
    summary=dict(task=TASK,agent_role="A6 Reconciliation & Closure Auditor",created_at=now(),family="C",epoch_id="C-E02",batch_id="C-E02-R1",
      G4_pointer=a4["G4_pointer"],G5_pointer=a4["G5_pointer"],sources=10,publication_identity_passed=10,
      independent_extractor_source_dispositions_agree=10,source_domain_dispositions_reconciled=True,
      direct_enzymatic_flavone_C6_complete_reactions=0,current_fresh_admitted=0,source_qualified_C6=0,
      A4_observation_records=344,A5_text_candidate_records=134,A5_assay_or_screening_records=314,
      record_grain_difference_preserved=True,these_counts_are_not_independent_covalent_reactions=True,
      original_Table1_numeric_cells=96,original_Table1_explicit_zeros=33,
      source_XML_domain_review_terminal=True,all_original_figures_SI_and_peripheral_structure_universe_complete=False,
      original_pointers_and_missing_structures_retained=True,no_source_saturation_claim=True,
      source_rename_probes=len(probes),permanent_reviewed_sources=10,
      scope_changed=False,model_outcomes_read=False,independent_chemical_validation=False,human_reviewed=False)
    immutable_json(O/"A6_source_reconciliation_summary.json",summary)
    outs=[O/n for n in ("10_source_disposition_reconciliation.jsonl","permanent_postscope_source_exposures.jsonl","actual_source_rename_rejection_probes.json","A6_source_reconciliation_summary.json")]
    ins=[a4p,a5p,identity_path,g5,
      B/"A4_fixed_extraction_v1/reaction_and_assay_observations.jsonl",
      B/"A5_fixed_extraction_v1/reaction_text_universe.fixed.jsonl",
      B/"A5_fixed_extraction_v1/assay_observation_universe.fixed.jsonl",
      B/"A5_fixed_extraction_v1/output_source_pointer_validation.json"]
    role=role_manifest("A6 Reconciliation & Closure Auditor","C-E02",ins,outs,dict(processed=10,passed=0,rejected=10,pending=0),
      unprocessed=["Full peripheral graph/SI universe remains unknown; no admitted C6 reaction","R2 access and R3 legitimate source acquisition remain separate"],
      read_holdout=True,read_model_outcome=False)
    role.update(logical_process="root isolated A6 after both fixed A4/A5 roles; only source-domain labels reconciled",
       reaction_graph_disagreement_count=None,no_complete_C6_graphs_to_compare=True,source_qualified_count=0)
    rp=O/"role_A6_manifest.json"
    immutable_json(rp,role)
    stagefolder=E/"stages/batches/C-E02-R1"
    files=outs+[rp]+ins
    freeze_stage_manifest(stagefolder,"G6_IDENTITY_STRUCTURE_ADMIT",files,g5,expected_previous_sha=sha_file(g5),family="C",epoch_id="C-E02")
    stage=stagefolder/"G6_IDENTITY_STRUCTURE_ADMIT.json"
    verify_stage_chain(stage,sha_file(stage))
    append(ROOT/"outputs/task016-p7/v1/epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R1",
      event_type="verified_existing_stage_registration",stage="G6_IDENTITY_STRUCTURE_ADMIT",
      stage_manifest_path=str(stage.relative_to(ROOT)),stage_manifest_sha256=sha_file(stage),registered_at=now(),
      admitted_count=0,formal_panel_frozen=False,approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G6=pointer(stage),sources=10,source_qualified=0,fresh_admitted=0,permanent_exposures=10,actual_rename_rejections=len(probes))))
if __name__=="__main__":main()
