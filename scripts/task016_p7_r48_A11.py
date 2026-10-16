"""R48 A11: actual public original bytes, dual-axis preregistration and evidence limits."""
import json,hashlib,collections
from pathlib import Path
from lxml import html
from scripts.operate import ROOT
from scripts.task016_p7_r18_PMC_originals import put,load,lines,sha,now
from scripts.task016_p7_orchestrate import verify_hashes,verify_stage_chain,STAGES
from scripts.task016_p7_c_e02_http import physical_attempts
from scripts import task016_p7_full_qualification_harness_v3 as fq
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"verification-v29-Iris-cross-axis-original-v1"
SHARED=B/"governance/R47-Iris-cross-axis-source-read-binding-v1"
ASSET=B/"C/E02/fresh/C-E02-R46-Iris-advertised-assets-v1"
checks=[]
def ck(name,ok,evidence=None):checks.append(dict(check=name,passed=bool(ok),evidence=evidence))
def main():
 assert not (ROOT/O).exists()
 binding=load(SHARED/"both_G5_ready_before_first_read.json")
 inputs=[SHARED/"both_G5_ready_before_first_read.json",SHARED/"A6/source_scientific_assessment.json",SHARED/"A6/all_16_assay_slot_dispositions.json",SHARED/"A6/original_figure_DOM_binding.json",SHARED/"A6/dual_text_reconciliation.json",ASSET/"raw_custody_summary.json",ASSET/"role_A2_raw_custody_manifest.json",B/"report_snapshots/progress-v29-physical-budget.json"]
 prior=lines(B/"governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl")
 ck("prior_v4_5204_rows",len(prior)==5204)
 ck("shared_source_prior_alias_literal_absent_not_graph_clearance",not any({"article:PMC13422134","doi:10.1002/cbic.70486","pmid:42530388"}.intersection(x["closure_tokens"]) for x in prior))
 ck("both_G5s_ready_before_any_first_scientific_read",binding["first_scientific_read_not_yet_started"] is True and len(binding["G5"])==2)
 all_events=[];source_exports=[]
 for family in ("C","SS"):
  cp=binding["contracts"][family];r=Path(cp["path"]).parent;g5=binding["G5"][family];g6=Path(g5["path"]).parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
  spec=fq.validate_full_qualification_contract(cp)["contract"]
  ck(family+"_actual_frozen_G4_and_list_bank_validate",spec["family"]==family and spec["raw_source_universe"]["sha256"]==sha(r/"raw_source_universe.json"))
  raw=load(r/"raw_source_universe.json")["source_candidates"][0]
  ck(family+"_seven_original_science_files_not_captcha",len(raw["raw_files"])==7 and raw["SI_access_disposition"]["valid_original_SI"] is False and raw["SI_access_disposition"]["challenge_not_solved"] is True)
  ck(family+"_full_alias_graph_clearance_still_false",raw["full_alias_or_graph_historical_clearance"] is False)
  for role in ("A3","A4","A5","A6"):
   p=r/("role_A3_manifest.json" if role=="A3" else role+"/role_manifest.json")
   obj=load(p);verify_hashes(obj["input_manifest_sha"]);verify_hashes(obj["output_file_sha"])
   ck(family+"_"+role+"_SHA_and_role_bound",obj["agent_role"]==role and obj["epoch_id"]==family+"-E02")
   ck(family+"_"+role+"_agent_delegated_no_model_read",obj["approval_type"]=="agent_delegated" and obj["human_reviewed"] is False and obj["read_model_outcome"] is False)
   inputs.append(p)
  a=load(r/"A4/available_original_scientific_text.json");b=load(r/"A5/available_original_scientific_text.json")
  ck(family+"_all103_blocks_exactly_equal",len(a["blocks"])==len(b["blocks"])==103 and [(x["text_SHA"],x["section_path"],x["tag"]) for x in a["blocks"]]==[(x["text_SHA"],x["section_path"],x["tag"]) for x in b["blocks"]])
  ck(family+"_all_source_text_hashes_recomputed",all(hashlib.sha256(x["text"].encode()).hexdigest()==x["text_SHA"] for obj in (a,b) for x in obj["blocks"]))
  ar=load(r/"A4/role_manifest.json");br=load(r/"A5/role_manifest.json")
  ck(family+"_independent_reader_processes_without_peer_outputs",ar["reader_id"]!=br["reader_id"] and ar["read_other_extractor_output"] is br["read_other_extractor_output"] is False and not set(ar["input_manifest_sha"]).intersection(br["output_file_sha"]) and not set(br["input_manifest_sha"]).intersection(ar["output_file_sha"]))
  ck(family+"_opaque_images_not_graph_transcription_claim",len(a["source_figures_opened_as_opaque_bytes"])==6 and len(b["source_figures_opened_as_opaque_bytes"])==6 and a["independent_graph_transcription"] is b["independent_graph_transcription"] is False)
  events=fq.evaluation_events(cp);all_events+=events
  ck(family+"_four_actual_start_end_read_receipts",len(events)==4 and collections.Counter(x["event_type"] for x in events)==dict(scientific_read_started=2,scientific_read_completed=2))
  exports=lines(r/"scientific_exposure_reads.jsonl");source_exports+=exports
  ck(family+"_five_permanent_exposure_exports",len(exports)==5 and all(x["development_exposed"] and x["exposure_type"]=="current_epoch_evaluation" and not x["future_fresh_eligible"] for x in exports))
  valid=fq.validate_full_science_round(cp,g5,fq.pointer(r/"full_round_manifest.json"))
  ck(family+"_executed_round_deferred_no_chemical_records_admitted",valid["round_execution_complete"] and valid["source_disposition_counts"]==dict(qualified=0,deferred=1,rejected=0) and valid["fresh_admitted"]==0 and not valid["G7_panel_formed"] and not valid["qualified_for_final_G7_review"])
  ck(family+"_zero_chemical_records_not_absence_claim",load(r/"full_round_validation.json")["no_reaction_records_means"]=="Chemical reaction records not yet transcribed, not reaction absence." and not load(r/"full_round_validation.json")["eligible_as_source_saturation_complete_round"])
  for ptr in (g5,fq.pointer(g6)):verify_stage_chain(ROOT/ptr["path"],ptr["sha256"])
  ck(family+"_G5_G6_actual_chain",True)
  inputs.extend([r/"full_round_manifest.json",r/"full_round_validation.json",Path(g5["path"]),g6])
 g5_times=[load(Path(x["path"]))["timestamp"] for x in binding["G5"].values()]
 ck("both_families_G5_precede_every_source_reader_event",all(e["timestamp"]>=max(g5_times) for e in all_events))
 ck("one_study_not_two_independent_groups",binding["independent_source_group_count"]==1 and len({x["source_id"] for x in source_exports})==1)
 original=load(ASSET/"A3_original_front_identity.json")
 ck("nine_actual_original_front_fields_match",len(original["field_checks"])==9 and all(original["field_checks"].values()) and original["scientific_body_read"] is False)
 custody=load(ASSET/"raw_custody_summary.json")
 ck("12_raw_requests_9_custody_3_pending",custody["physical_HTTP"]==12 and custody["physical_bytes"]==669700 and custody["counts"]==dict(processed=12,passed=9,rejected=0,pending=3))
 ck("six_original_JPEG_and_no_valid_SI_PDF",custody["valid_original_JPEG"]==6 and custody["valid_original_HTML"]==1 and custody["valid_SI_PDF"]==0 and custody["retained_Captcha_HTML"]==1)
 for row in custody["records"]:
  p=Path(row["raw_pointer"]["path"]);data=(ROOT/p).read_bytes();ck(row["query_id"]+"_exact_raw_SHA_size",sha(p)==row["raw_pointer"]["sha256"] and len(data)==row["raw_pointer"]["bytes"]);inputs.append(p)
 si=next(x for x in custody["records"] if x["query_id"]=="R46-SI")
 sitext=html.fromstring((ROOT/si["raw_pointer"]["path"]).read_bytes())
 ck("SI_HTTP200_is_actual_captcha_HTML_not_PDF",si["HTTP_status"]==200 and "reCAPTCHA" in sitext.xpath("string(//head/title)") and not (ROOT/si["raw_pointer"]["path"]).read_bytes().startswith(b"%PDF"))
 CK_source=load(SHARED/"A6/source_scientific_assessment.json");slots=load(SHARED/"A6/all_16_assay_slot_dispositions.json");fig=load(SHARED/"A6/original_figure_DOM_binding.json")
 ck("full_16_assay_slot_denominator_6_positive_10_ND",slots["original_denominator"]==16 and len(slots["slots"])==16 and sum(x["author_explicit_activity"] for x in slots["slots"])==6 and sum(x["source_reported_result"]=="N.D. = no product" for x in slots["slots"])==10)
 ck("ND_not_missing_and_numeric_conversions_not_invented",all(x["absence_not_converted_to_missing"] and x["numeric_conversion_not_digitized"] is None for x in slots["slots"]))
 ck("method_result_numbering_conflicts_preserved",len(CK_source["conflicts"])==4 and any(x["original_Figure4_slot"]==2 and x["methods_name_at_same_number"]=="formononetin" and x["results_text_name_at_same_number"]=="phloretin" and x["methods_vs_results_name_conflict"] for x in slots["slots"]))
 ck("no_C6_or_SS_O2_complete_positive_source_promoted",CK_source["source_reaction_eligible"] is None and CK_source["qualified_closure_groups_C"]==CK_source["qualified_closure_groups_SS"]==0 and not CK_source["whole_paper_C_or_SS_absence_claim"])
 ck("figure4_DOM_owner_uses_g001_not_guessed_number",next(x for x in fig["figures"] if x["source_figure_id"]=="cbic70486-fig-0004")["advertised_filename"]=="CBIC-27-e70486-g001.jpg" and fig["filename_suffix_is_not_figure_number"])
 ck("two_main_chemical_figures_visually_reviewed",sum(x["chemical_scope_relevant"] and x["A6_visually_inspected"] for x in fig["figures"])==2)
 ck("source_graph_stereo_precursor_and_history_pending",not CK_source["full_reaction_inventory_enumerated"] and not CK_source["full_source_alias_graph_named_history_review_complete"] and not CK_source["complete_reference_precursors"])
 active={}
 for row in lines(B/"epoch_ledger.jsonl"):
  if row.get("epoch_id") in ("C-E02","SS-E02") and row.get("status")=="active" and row.get("stage") in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT"):
   active[row["stage_manifest_path"]]=row["stage_manifest_sha256"]
 for p,h in active.items():verify_stage_chain(ROOT/p,h)
 ck("all23_current_registered_G5_G6_chains",len(active)==23)
 snap=load(B/"report_snapshots/progress-v29-physical-budget.json");old=load(B/"report_snapshots/progress-v28-physical-budget.json");physical=physical_attempts()
 ck("global_physical_HTTP_1128_delta12",len(physical)==snap["totals"]["HTTP"]==1128 and snap["totals"]["HTTP"]-old["totals"]["HTTP"]==12)
 ck("global_physical_bytes_1237357748_delta669700",sum(x["bytes"] for x in physical)==snap["totals"]["bytes"]==1237357748 and snap["totals"]["bytes"]-old["totals"]["bytes"]==669700)
 ck("MCTS_214_rows_original_SHA_unchanged",len(lines(B/"run_ledger.jsonl"))==214 and sha(B/"run_ledger.jsonl")==old["physical_prefixes"][str(B/"run_ledger.jsonl")]["prefix_sha256"])
 for family,expected in [("C","09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46"),("SS","a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f")]:
  ck(family+"_G4_frozen_SHA_unchanged",sha(B/f"{family}/E02/stages/G4_SCOPE_FREEZE.json")==expected)
  ck(family+"_actual_G7_G8_absent",all(not list((ROOT/B/f"{family}/E02/stages").rglob(stage+".json")) for stage in STAGES if stage.startswith(("G7_","G8_"))))
 result=dict(task=T,agent_role="A11",epoch_id="C-E02+SS-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,input_manifest_sha={str(p):sha(p) for p in dict.fromkeys(inputs)},checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),errors=[x for x in checks if not x["passed"]],unprocessed=[],source_HTTP_delta=12,source_bytes_delta=669700,source_independent_groups=1,source_assay_slots=16,source_positive_assay_slots=6,source_ND_assay_slots=10,scientific_sources_admitted=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,registered_current_G5_G6=23,source_saturation=False,independent_chemical_validation=False)
 put(O/"independent_A11_original_and_scope_boundary_audit.json",result);print(json.dumps({k:result[k] for k in ["passed","failed","registered_current_G5_G6","source_HTTP_delta"]}))
 if result["failed"]:raise RuntimeError("A11_FAILED")
if __name__=="__main__":main()
