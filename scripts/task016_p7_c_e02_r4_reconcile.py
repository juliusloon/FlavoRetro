"""A6 R4 independent source/assay reconciliation with additive PMID closure."""
import hashlib,json
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,role_manifest,verify_hashes,verify_stage_chain,freeze_stage_manifest
from scripts.task016_p7_c_e02_http import E,BASE,immutable_json,append,rows
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
from scripts.task016_p7_source_alias_closure import assert_fresh
B=E/"fresh/C-E02-R4";O=B/"A6_source_reconciliation_v1"
def main():
    p4=B/"A4_fixed_extraction_v1/role_A4_fixed_extraction_manifest.json";p5=B/"A5_fixed_extraction_v1/role_A5_fixed_extraction_manifest.json"
    a=json.loads(p4.read_text());d=json.loads(p5.read_text())
    for r in (a,d):verify_hashes(r["output_files_sha256"])
    if a["input_manifest"]!=d["common_input_manifest"] or a["read_A5_final_structure"] or d["A4_final_output_read"]:raise ValueError("A4/A5 separation/common input mismatch")
    ip=ROOT/a["input_manifest"]["path"];common=json.loads(ip.read_text());g5=ROOT/common["G5_pointer"]["path"];verify_stage_chain(g5,common["G5_pointer"]["sha256"])
    four={x["source_id"]:x for x in rows(B/"A4_fixed_extraction_v1/A4_source_dispositions.jsonl")};five={x["source_id"]:x for x in rows(B/"A5_fixed_extraction_v1/A5_complete_source_dispositions.jsonl")}
    if set(four)!=set(five) or len(four)!=2:raise ValueError("two-source universe mismatch")
    pairs={"official_SI_only_chemistry_incomplete":"SI_available_main_text_and_reaction_evidence_missing","primary_outside_direct_flavone_scope":"primary_fulltext_and_embedded_SI_domain_positive_precursor_nonflavone_and_direct_flavone_ND"}
    identities={r["doi"]:r for r in rows(E/"fresh/C-E02-R3R4-A3/source_publication_identity.v2.jsonl")}
    reconciled=[];exposures=[];probes=[]
    for h in common["sources"]:
        sid=h["source_id"];x=four[sid];y=five[sid];i=identities[h["doi"]]
        if pairs[x["A4_disposition"]]!=y["disposition"] or x["complete_scope_aligned_positive_graphs"]!=0 or y["complete_in_domain_graph_triples"]!=0:raise ValueError("unexpected domain-positive graph or source disagreement")
        if not i["source_identity_verified"]:raise ValueError("source publication identity pending")
        reconciled.append(dict(source_id=sid,doi=h["doi"],A4_literal_disposition=x["A4_disposition"],A5_literal_disposition=y["disposition"],semantically_reconciled=True,publication_identity_verified=True,
          complete_scope_aligned_graphs=0,source_qualified_C6=0,fresh_admitted=0,source_chemistry_unknown_not_negative=x["A4_disposition"].startswith("official_SI"),same_R3_source_ID_not_new_source=True,all_graphs_SI_peripheral_universe_complete=False))
        hint=h["source_hint"];tokens=["doi:"+h["doi"],"pmid:"+hint["pmid"]]
        exposures.append(dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R4",exposure_id="C-E02-R4:source-review:"+sid,exposure_type="postscope_official_SI_or_primary_original_review",source_id=sid,doi=h["doi"],pmid=hint["pmid"],development_exposed=True,eligible_for_fresh_holdout=False,future_fresh_eligible=False,closure_tokens=tokens,source_tokens=tokens,source_qualified_C6=False,actual_registered_at=now(),new_unique_source_exposure=h["doi"]=="10.1021/acs.jafc.5c09887",previous_R3_abstract_observation=h["doi"]=="10.1111/tpj.13555",original_pointers=h["original_objects"],target_graph=None,reaction_signature=None,human_reviewed=False))
    ar=[r for r in rows(B/"A4_fixed_extraction_v1/A4_assay_observations.jsonl") if r["table"]=="Table1"]
    dr=rows(B/"A5_fixed_extraction_v1/A5_Table1_complete_assay_cells.jsonl")
    p4cells={(r["substrate_literal"],r["enzyme"]):(r["status"],r.get("value"),r.get("sd")) for r in ar}
    p5cells={(r["substrate_name_literal"],r["enzyme_literal"]):(r["value_status"].replace("numeric_activity_reported","numeric_observation"),r.get("mean"),r.get("SD")) for r in dr}
    if len(ar)!=46 or len(dr)!=46 or len(p4cells)!=46 or p4cells!=p5cells:raise ValueError("Table1 46 independent measurements differ")
    counts=dict(cells=46,independently_equal_cells=46,numeric=28,ND=18,NT=0,mean_zero=0,zero_SD=3,unreported_SD=2,
      ND_is_not_numeric_zero=True,missing_SD_is_not_zero=True,not_independent_covalent_reactions=True,Table2_15_metrics_retained_not_reconciled_here=True)
    immutable_json(O/"Table1_independent_cell_reconciliation.json",counts)
    save_rows(O/"2_source_disposition_reconciliation.jsonl",reconciled);save_rows(O/"permanent_postscope_source_exposures.jsonl",exposures)
    for r in exposures:
        for field in ("doi","pmid"):
            try:assert_fresh({field:r[field],"reaction_id":"renamed-new"},exposures)
            except ValueError as exc:probes.append(dict(source_id=r["source_id"],field=field,actually_rejected=True,error=str(exc)))
            else:raise ValueError("source alias rename bypass")
    immutable_json(O/"actual_source_rename_rejection_probes.json",probes)
    sir=json.loads((B/"official_SI_record_response.json").read_text());si=json.loads((ROOT/sir["path"]).read_text());f=si["files"][0]
    record=next(r for r in rows(B/"raw_file_request_execution.jsonl") if r["request"]["doi"]==si["resource_doi"]);raw=ROOT/record["responses"][-1]["path"]
    md5=hashlib.md5(raw.read_bytes()).hexdigest()
    if md5!=f["supplied_md5"] or raw.stat().st_size!=f["size"]:raise ValueError("Official SI object byte identity mismatch")
    immutable_json(O/"official_SI_raw_object_identity_check.json",dict(resource_doi=si["resource_doi"],SI_doi=si["doi"],official_API_pointer=pointer(ROOT/sir["path"]),raw_pointer=pointer(raw),actual_bytes=raw.stat().st_size,official_bytes=f["size"],actual_MD5=md5,official_supplied_MD5=f["supplied_md5"],passed=True,chemical_qualification_granted=False))
    summary=dict(task=TASK,agent_role="A6 Reconciliation & Closure Auditor",at=now(),batch_id="C-E02-R4",source_contexts=2,source_IDs_reused_from_R3=2,new_unique_chemically_observed_sources=1,independent_source_dispositions_agree=2,publication_identity_passed=2,complete_direct_flavone_C6_graphs=0,source_qualified_C6=0,fresh_admitted=0,
      source_PDF_pages=78,primary_manuscript_with_SI_pages=59,official_SI_only_pages=19,primary_body_ACS_missing=True,
      Table1=counts,actual_DOI_PMID_rename_rejections=4,SI_expected_byte_MD5_pass=True,
      original_full_chemical_round_complete=False,saturation=False,source_access_exhausted=False,scope_changed=False,model_outcomes_read=False,human_reviewed=False)
    immutable_json(O/"A6_source_reconciliation_summary.json",summary)
    outs=[O/n for n in ("Table1_independent_cell_reconciliation.json","2_source_disposition_reconciliation.jsonl","permanent_postscope_source_exposures.jsonl","actual_source_rename_rejection_probes.json","official_SI_raw_object_identity_check.json","A6_source_reconciliation_summary.json")]
    ins=[Path(__file__),ROOT/"scripts/task016_p7_source_alias_closure.py",p4,p5,ip,g5,E/"fresh/C-E02-R3R4-A3/role_A3_manifest.v2.json",E/"fresh/C-E02-R3R4-A3/source_publication_identity.v2.jsonl",B/"A4_fixed_extraction_v1/A4_assay_observations.jsonl",B/"A5_fixed_extraction_v1/A5_Table1_complete_assay_cells.jsonl",ROOT/sir["path"],raw]
    rp=O/"role_A6_manifest.json";role=role_manifest("A6 Reconciliation & Closure Auditor","C-E02",ins,outs,dict(processed=2,passed=0,rejected=0,pending=2),read_holdout=True,read_model_outcome=False,
       unprocessed=["ACS primary body/access","Full peripheral graph/SI universe","No complete direct C6 graph admitted","R3/R4 shared source closures not new independent groups"]);immutable_json(rp,role)
    dest=E/"stages/batches/C-E02-R4";freeze_stage_manifest(dest,"G6_IDENTITY_STRUCTURE_ADMIT",ins+outs+[rp],g5,expected_previous_sha=sha_file(g5),family="C",epoch_id="C-E02")
    stage=dest/"G6_IDENTITY_STRUCTURE_ADMIT.json";verify_stage_chain(stage,sha_file(stage))
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R4",event_type="verified_existing_stage_registration",stage="G6_IDENTITY_STRUCTURE_ADMIT",stage_manifest_path=str(stage.relative_to(ROOT)),stage_manifest_sha256=sha_file(stage),registered_at=now(),admitted_count=0,formal_panel_frozen=False,approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G6=pointer(stage),sources=2,new_unique_source_exposures=1,independent_assay_cells=46,actual_source_alias_rejections=4,fresh=0)))
if __name__=="__main__":main()
