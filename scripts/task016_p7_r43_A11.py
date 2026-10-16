"""R43 A11: verify actual R37-41 custody, prospective v3 bindings and bounded science."""
import json,hashlib,re,collections
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import load,lines,sha,put,now
from scripts.task016_p7_orchestrate import verify_stage_chain,verify_hashes
from scripts.task016_p7_c_e02_http import physical_attempts
from scripts import task016_p7_full_qualification_harness_v3 as fq
T="TASK-016-P7";B=Path("outputs/task016-p7/v1");O=B/"verification-v28-C-R39-full-qualification"
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1"
F=B/"C/E02/fresh/C-E02-R41-A6-original-figure-supplement-v1"
G5=B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=G5.parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
checks=[]
def ck(name,ok,evidence=None):checks.append(dict(check=name,passed=bool(ok),evidence=evidence))
def main():
 out=O/"independent_A11_actual_qualification_audit.json";assert not (ROOT/out).exists()
 cp=fq.pointer(R/"full_qualification_contract.json");sp=load(Path(cp["path"]))
 inputs=[Path(cp["path"]),R/"full_round_manifest.json",R/"full_round_validation.json",R/"A6/source_scientific_assessment.json",R/"A6/reported_mass_identity_sanity_check.json",R/"A6/dual_parser_reconciliation.json",R/"scientific_exposure_reads.jsonl",O/"counterfactuals/red_team_results.json",B/"report_snapshots/progress-v28-physical-budget.json",G5,G6]
 checked=fq.validate_full_qualification_contract(cp);ck("actual_prospective_contract_and_frozen_list_bank_validate",checked["source_candidates"]==1 and checked["admitted"]==0 and not checked["actual_G7_panel_ready"])
 ck("actual_v3_implementation_pinned",sp["implementation_files_sha256"]["scripts/task016_p7_full_qualification_harness_v3.py"]==sha("scripts/task016_p7_full_qualification_harness_v3.py"))
 ck("5199_prior_rows_and_zero_known_alias_intersections",len(checked["meta"]["prior"])==5199 and not any(set(checked["meta"]["sources"][0]["official_aliases"]).intersection(x["closure_tokens"]) for x in checked["meta"]["prior"]))
 ck("negative_alias_match_does_not_grant_graph_clearance",checked["meta"]["sources"][0]["full_alias_or_graph_historical_clearance"] is False)
 a3=load(R/"A3_source_results.json")
 ck("all_available_A3_identity_fields_verified",len(a3["sources"])==1 and all(a3["sources"][0]["field_checks"].values()) and a3["sources"][0]["unresolved_conflicts"]==[])
 events=fq.evaluation_events(cp);g5=load(G5)
 ck("two_real_scientific_readers_have_start_and_end_receipts",len(events)==4 and collections.Counter(x["event_type"] for x in events)==dict(scientific_read_started=2,scientific_read_completed=2))
 ck("actual_G5_precedes_all_reader_events",all(x["timestamp"]>=g5["timestamp"] and x["G5"]["sha256"]==sha(G5) for x in events))
 ids={x["reader_role"]:x["reader_id"] for x in events};ck("distinct_isolated_process_reader_ids",len(set(ids.values()))==2)
 for role in ("A3","A4","A5","A6"):
  p=R/("role_A3_manifest.json" if role=="A3" else role+"/role_manifest.json")
  roleobj=load(p);verify_hashes(roleobj["input_manifest_sha"]);verify_hashes(roleobj["output_file_sha"])
  ck(role+"_immutable_inputs_and_outputs_SHA",True);inputs.append(p)
  ck(role+"_approval_and_no_model_read",roleobj["human_reviewed"] is False and roleobj["approval_type"]=="agent_delegated" and roleobj["read_model_outcome"] is False)
 a=load(R/"A4/role_manifest.json");b=load(R/"A5/role_manifest.json")
 ck("extractor_no_peer_output_input",not set(a["input_manifest_sha"]).intersection(b["output_file_sha"]) and not set(b["input_manifest_sha"]).intersection(a["output_file_sha"]) and a["read_other_extractor_output"] is b["read_other_extractor_output"] is False)
 c=load(R/"A6/dual_parser_reconciliation.json")
 ck("all_1531_paragraphs_conserved",c["paragraphs_compared"]==1531 and c["main_paragraphs_each"]==52 and c["SI_paragraphs_each"]==1479 and c["exact_text_SHA_equal"]==1489 and len(c["whitespace_only_differences"])==42 and c["non_whitespace_differences"]==[])
 ck("eleven_critical_contexts_match",len(c["critical_scientific_contexts"])==11 and all(x["content_equal_ignoring_whitespace"] for x in c["critical_scientific_contexts"]))
 ck("no_dual_graph_transcription_claim",not c["two_graph_transcriptions"] and a["independent_graph_transcription"] is b["independent_graph_transcription"] is False)
 s=load(R/"A6/source_scientific_assessment.json");mass=load(R/"A6/reported_mass_identity_sanity_check.json")
 ck("scope_related_positive_author_report_retained",s["scope_relevant_author_report"] is True and s["literal_fields"]["enzyme"]=="GyCGT1" and s["literal_fields"]["sequence_accession"]=="PZ535504")
 ck("reported_mass_conflict_preserved",mass["reported_mz"]==449.2320 and mass["formula"]=="C21H20O11" and 0.124<mass["difference_Da"]<0.125 and len(s["unresolved_conflicts"])==1)
 ck("no_candidate_graph_invented_for_mass_check",mass["new_candidate_graph_extracted"] is False and mass["build_graph_source"]["sha256"]==sha(B/"C/E02/build_supports.json"))
 ck("no_whole_paper_absence_or_independent_chemistry_claim",not s["whole_paper_reaction_absence_claim"] and not s["independent_chemical_validation"] and s["source_reaction_eligible"] is None)
 for im in s["visual_checks"]:fq.bound(im)
 ck("five_A6_scope_relevant_visual_reviews_bound",len(s["visual_checks"])==5 and all(x["A6_visually_inspected"] for x in s["visual_checks"]))
 exposure=lines(R/"scientific_exposure_reads.jsonl")
 ck("five_permanent_read_event_exports_retained",len(exposure)==5 and all(x["development_exposed"] and x["exposure_type"]=="current_epoch_evaluation" and not x["future_fresh_eligible"] for x in exposure))
 valid=fq.validate_full_science_round(cp,fq.pointer(G5),fq.pointer(R/"full_round_manifest.json"))
 ck("actual_round_execution_complete_and_science_deferred",valid["round_execution_complete"] and valid["source_disposition_counts"]==dict(qualified=0,deferred=1,rejected=0) and valid["reaction_disposition_counts"]==dict(qualified=0,deferred=1,rejected=0,unprocessed=0) and valid["unprocessed"]==[])
 ck("no_automatic_G7_or_fresh_admission",valid["fresh_admitted"]==0 and not valid["qualified_for_final_G7_review"] and not valid["G7_panel_formed"])
 ck("saturation_counting_explicitly_excluded",not load(R/"full_round_validation.json")["eligible_as_source_saturation_complete_round"] and not valid["source_saturation_established"])
 metadata=load(B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1/metadata_round_summary.json")
 # Check raw denominator without relying on display-label field names.
 sources=lines(B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1/metadata_unique_sources.jsonl")
 ck("recent_metadata_312_unique_sources",len(sources)==312 and len(load(R/"raw_source_universe.json")["metadata_only_dispositions"])==311)
 new=[]
 for name,expected in [("C-E02-R37-recent-C-primary-metadata-v1",6),("C-E02-R38-isoorientin-original-custody-v1",2),("C-E02-R40-advertised-SI-custody-v1",2),("C-E02-R41-A6-original-figure-supplement-v1",1)]:
  p=B/"C/E02/fresh"/name/"http_ledger.jsonl";rows=lines(p);new+=rows;inputs.append(p)
  ck(name+"_HTTP_plan_conserved",len(rows)==expected and all(x["status_code"]==200 for x in rows))
  for row in rows:
   raw=Path(row["path"]);ck(name+"_"+Path(raw).suffix+"_raw_SHA_size",sha(raw)==row["sha256"] and (ROOT/raw).stat().st_size==row["bytes"]);inputs.append(raw)
 ck("exact_new_HTTP_is_11",len(new)==11)
 for p,h in [(G5,"6436ddb72d9e2529870418eeac257c362c2817f9bb1f7fb2432a26e5df23af79"),(G6,"75f58fdbf737f89dc58aef3bb8a035ab1b2b9681aae8bc679bf8d97f3a1b1777")]:
  verify_stage_chain(ROOT/p,h);ck("actual_chain_"+p.name,sha(p)==h)
 registered={}
 for row in lines(B/"epoch_ledger.jsonl"):
  if row.get("epoch_id") in ("C-E02","SS-E02") and row.get("status")=="active" and row.get("stage") in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT"):
   registered[row["stage_manifest_path"]]=row["stage_manifest_sha256"]
 for p,h in registered.items():verify_stage_chain(ROOT/p,h)
 ck("all_19_active_G5_G6_stage_chains",len(registered)==19)
 snap=load(B/"report_snapshots/progress-v28-physical-budget.json");old=load(B/"report_snapshots/progress-v27-physical-budget.json");actual=physical_attempts()
 ck("independent_HTTP_recount_and_exact_delta",len(actual)==snap["totals"]["HTTP"]==1116 and snap["totals"]["HTTP"]-old["totals"]["HTTP"]==11)
 ck("independent_byte_recount_and_exact_delta",sum(x["bytes"] for x in actual)==snap["totals"]["bytes"]==1236688048 and sum(x["bytes"] for x in new)==4724715)
 ck("no_MCTS_added",len(lines(B/"run_ledger.jsonl"))==214 and sha(B/"run_ledger.jsonl")==old["physical_prefixes"][str(B/"run_ledger.jsonl")]["prefix_sha256"])
 for family,expected in [("C","09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46"),("SS","a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f")]:
  ck(family+"_G4_original_SHA_unchanged",sha(B/f"{family}/E02/stages/G4_SCOPE_FREEZE.json")==expected)
  ck(family+"_no_actual_G7_G8",not any((ROOT/B/f"{family}/E02/stages").rglob("G7_CLOSURE_PANEL_FREEZE.json")) and not any((ROOT/B/f"{family}/E02/stages").rglob("G8_PREFLIGHT.json")))
 rt=load(O/"counterfactuals/red_team_results.json")
 ck("18_fail_closed_counterfactual_checks_passed",rt["passed"]==18 and rt["failed"]==0 and rt["actual_fresh_admitted"]==0)
 result=dict(task=T,agent_role="A11",epoch_id="C-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,input_manifest_sha={str(p):sha(p) for p in dict.fromkeys(inputs)},checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),errors=[x for x in checks if not x["passed"]],unprocessed=[],source_HTTP_delta=11,source_bytes_delta=4724715,new_MCTS=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,registered_current_stage_chains=len(registered),qualified_candidate_path_live_exercised=False,source_saturation=False)
 put(out,result);print(json.dumps({k:result[k] for k in ["passed","failed","source_HTTP_delta","registered_current_stage_chains"]}))
 if result["failed"]:raise RuntimeError("A11_FAILED")
if __name__=="__main__":main()
