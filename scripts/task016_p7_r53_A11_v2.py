"""R53 A11: raw-backed pagination conservation and lawful-access evidence bounds."""
import json,collections,hashlib,re,html,urllib.parse
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts.task016_p7_orchestrate import verify_hashes,verify_stage_chain,STAGES
from scripts.task016_p7_c_e02_http import physical_attempts
from scripts.task016_p7_source_alias_closure import closure_tokens
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
OLD=B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1"
R49=B/"C/E02/fresh/C-E02-R49-R37-cursor-completion-v1"
R50=B/"C/E02/fresh/C-E02-R50-R49-cursor-boundary-v1"
R51=B/"C/E02/fresh/C-E02-R51-mungbean-primary-custody-v1"
R52=B/"C/E02/fresh/C-E02-R52-mungbean-declared-VoR-v1"
O=B/"verification-v30-metadata-cursor-and-access-v1"
checks=[];inputs=[]
def ck(name,ok,evidence=None):checks.append(dict(check=name,passed=bool(ok),evidence=evidence))
def key(m):return "doi:"+m["doi"].lower() if m.get("doi") else str(m.get("source"))+"-"+str(m.get("id"))
def raw(ptr):
 p=Path(ptr["path"]);data=(ROOT/p).read_bytes()
 ck(str(p)+"_raw_SHA_bytes",sha(p)==ptr["sha256"] and ("bytes" not in ptr or len(data)==ptr["bytes"]))
 inputs.append(p);return data
def main():
 global inputs
 assert not (ROOT/O).exists()
 for folder,contract in [(R49,"precontract.json"),(R50,"precontract.v2.json"),(R51,"precontract.json"),(R52,"precontract.json")]:
  p=folder/contract;d=load(p);verify_hashes(d["files_sha256"]);inputs.append(p)
  ck(folder.name+"_actual_intake_frozen_scope_and_roles",d["family"]=="C" and d["epoch_id"]=="C-E02" and not d["chemical_extraction_permitted"] and d["unknown_name_identity_fail_closed"] and d["approval_type"]=="agent_delegated" and d["human_reviewed"] is False)
 pages=lines(R49/"page_execution.jsonl");chains=load(R49/"chain_plan.json")["chains"]
 allobs=[];firstobs=[]
 fields=load(R49/"precontract.json")["metadata_fields"]
 for row in lines(OLD/"query_execution.jsonl"):
  obj=json.loads(raw(dict(path=row["raw_path"],sha256=row["raw_SHA"],bytes=row["raw_bytes"])))
  rr=obj.get("resultList",{}).get("result",[])
  ck(row["query_id"]+"_original_raw_count",len(rr)==row["returned"] and obj["hitCount"]==row["hitCount"])
  for m in rr:firstobs.append(dict(metadata={k:m.get(k) for k in fields},pointer=dict(path=row["raw_path"],sha256=row["raw_SHA"]),query_id=row["query_id"],page=0))
 ck("six_original_queries_and331_raw_observations",len(lines(OLD/"query_execution.jsonl"))==6 and len(firstobs)==331)
 for c in chains:
  rr=[x for x in pages if x["original_query_id"]==c["original_query_id"]]
  cursor=c["initial_cursor"]
  ck(c["original_query_id"]+"_contiguous_declared_pages",len(rr)==c["max_additional_pages"] and [x["additional_page"] for x in rr]==list(range(1,len(rr)+1)))
  for r in rr:
   obj=json.loads(raw(r["raw_pointer"]));projected=[{k:x.get(k) for k in fields} for x in obj.get("resultList",{}).get("result",[])]
   ck(c["original_query_id"]+"_page"+str(r["additional_page"])+"_exact_raw_projection_cursor",r["HTTP_status"]==200 and r["requested_cursor"]==cursor and hashlib.sha256(cursor.encode()).hexdigest()==r["requested_cursor_SHA"] and r["results"]==projected and len(projected)==r["returned"] and r["returned_next_cursor"]==obj.get("nextCursorMark"))
   cursor=obj.get("nextCursorMark")
   allobs.extend(dict(metadata=m,pointer=r["raw_pointer"],query_id=c["original_query_id"],page=r["additional_page"]) for m in projected)
  boundary=next(x for x in lines(R50/"query_execution.jsonl") if x["query_id"]==c["original_query_id"])
  obj=json.loads(raw(boundary["raw_pointer"]))
  ck(c["original_query_id"]+"_actual_empty_cursor_end",boundary["requested_cursor"]==cursor and boundary["HTTP_status"]==200 and boundary["returned"]==0 and obj.get("resultList",{}).get("result",[])==[] and boundary["cursor_exhaustion_observed"] is True)
 ck("59_additional_pages_5726_observations",len(pages)==59 and len(allobs)==5726)
 raw_index={}
 for x in allobs:raw_index.setdefault(key(x["metadata"]),x["metadata"])
 output=lines(R49/"metadata_unique_sources.jsonl")
 ck("5491_deduplicated_sources_exactly_match_raw_first_observations",len(output)==5491 and {key(x["metadata"]):x["metadata"] for x in output}==raw_index)
 firstkeys={key(x["metadata"]) for x in firstobs}
 ck("5451_new_literal_sources40_overlap_not_fresh",sum(k not in firstkeys for k in raw_index)==5451 and len(set(raw_index)&firstkeys)==40)
 combined=firstobs+allobs;groups=collections.defaultdict(list)
 for x in combined:groups[key(x["metadata"])].append(x)
 ck("full_R37_R49_union6057_observations5763_metadata_groups",len(combined)==6057 and len(groups)==5763)
 variants=[]
 for k,gg in groups.items():
  changed={f:sorted({json.dumps(x["metadata"].get(f),ensure_ascii=False,sort_keys=True) for x in gg}) for f in fields if len({json.dumps(x["metadata"].get(f),ensure_ascii=False,sort_keys=True) for x in gg})>1}
  if changed:
   variants.append(dict(literal_metadata_key=k,observation_count=len(gg),differing_raw_fields=changed,all_observations=gg,scientific_identity_decision=None,raw_values_preserved=True))
 write(T,str(O/"literal_metadata_variants_retained.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in variants))
 hints=lines(R49/"title_enzyme_hints.jsonl");triage=lines(R50/"title_hint_prior_triage.jsonl")
 prior=lines(B/"governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl")
 tokens={t for r in prior if r["development_exposed"] for t in r["closure_tokens"]}
 later=[x for f in ("C","SS") for x in lines(B/f"{f}/E02/fresh/{f}-E02-R47-Iris-prospective-qualification-v1/scientific_exposure_reads.jsonl")]
 for x in later:tokens.update(closure_tokens(x))
 expected=[sorted(set(x["official_hint_aliases"])&tokens) for x in hints]
 ck("prior_inventory5204_plus10_later_current_evaluation_rows",len(prior)==5204 and len(later)==10)
 ck("all95_title_hints_literal_prior_triage_independently_recomputed",len(hints)==len(triage)==95 and [x["known_prior_scientific_token_matches"] for x in triage]==expected and sum(bool(x) for x in expected)==27)
 ck("68_token_absences_not_full_identity_clearance",sum(not x for x in expected)==68 and all(not x["full_source_graph_alias_clearance"] and x["chemical_scope_disposition"] is None and not x["source_qualified"] and x["not_selected_is_not_chemical_rejection"] for x in triage))
 ck("metadata_body_abstract_not_projected",not {"abstract","abstractText","fullText","body","smiles"}.intersection(fields) and all(set(x["metadata"])==set(fields) for x in combined))
 summary=load(R49/"metadata_pagination_summary.json");boundary=load(R50/"metadata_boundary_and_triage_summary.json")
 ck("bounded_initial_coverage_and_later_true_cursor_end_not_conflated",all(x["initial_count_covered"] and not x["cursor_exhaustion_observed"] for x in summary["chains"]) and boundary["all_cursor_exhaustion_observed"])
 ck("no_chemical_round_or_saturation_from_metadata",not summary["complete_full_qualification_round"] and not boundary["complete_chemical_qualification_round"] and not summary["source_saturation"] and not boundary["source_saturation"] and summary["fresh_admitted"]==0)
 repair=load(R50/"pre_HTTP_contract_rejection_retained.json");http50=lines(R50/"http_ledger.jsonl")
 ck("R50_contract_rejection0HTTP_old_bytes_retained",repair["physical_HTTP_before_repair"]==0 and not repair["old_frozen_files_modified"] and sha(R50/"precontract.json")==repair["old_contract_SHA"] and sha(Path("scripts/task016_p7_c_r50_boundary.py"))==repair["old_script_SHA"] and all(x["intake_contract_sha256"]==sha(R50/"precontract.v2.json") for x in http50))
 rr=lines(R51/"metadata_execution.jsonl")
 cross=next(x for x in rr if x["query_id"]=="R51-CROSSREF");m=json.loads(raw(cross["raw_pointer"]))["message"]
 alex=next(x for x in rr if x["query_id"]=="R51-OPENALEX");raw(alex["raw_pointer"])
 norm=lambda s:re.sub("[^a-z0-9]","",html.unescape(s).lower())
 hint=load(R51/"selected_bibliography.json")["metadata"];a3=load(R51/"A3_bibliographic_identity.json")
 ck("new_source_seven_bibliographic_fields_recomputed",m["DOI"].lower()==hint["doi"].lower()=="10.1111/tpj.70932" and norm(m["title"][0])==norm(hint["title"]) and m["container-title"]==["The Plant Journal"] and m["published"]["date-parts"][0][0]==int(hint["pubYear"]) and str(m["volume"])==hint["journalVolume"] and str(m["issue"])==hint["issue"] and m["article-number"]==hint["pageInfo"] and len(a3["field_checks"])==7 and all(a3["field_checks"].values()))
 ck("original_front_identity_remains_unverified",not a3["original_front_identity_verified"] and not a3["scientific_content_read"] and not a3["full_graph_alias_historical_clearance"])
 original=lines(R51/"original_access_execution.jsonl")+lines(R52/"query_execution.jsonl")
 for x in original:raw(x["raw_pointer"])
 ck("three_declared_publisher_original_routes_all403_no_PDF",len(original)==3 and all(x["HTTP_status"]==403 and not x["scientific_body_read"] and not (ROOT/x["raw_pointer"]["path"]).read_bytes().startswith(b"%PDF") for x in original))
 declared={m["resource"]["primary"]["URL"]}|{x["URL"] for x in m["link"]}
 ck("original_URLs_literally_declared_not_guessed",all(x["url"] in declared for x in original))
 ck("OA_metadata_disagreement_and_real403_preserved",hint["isOpenAccess"]=="N" and any(x["URL"]=="http://creativecommons.org/licenses/by-nc/4.0/" and x["content-version"]=="vor" for x in m["license"]) and load(R52/"precontract.json")["access_metadata_conflict_retained"])
 ck("OpenAlex429_no_success_or_body_read_claim",alex["HTTP_status"]==429 and alex["status"]!="available")
 new_http=[x for folder in (R49,R50,R51,R52) for x in lines(folder/"http_ledger.jsonl")]
 ck("67_physical_HTTP_all_retained_with4failures",len(new_http)==67 and sum(x["status_code"]!=200 for x in new_http)==4 and len({(x["url"],x["started_at"],x["path"]) for x in new_http})==67)
 before=load(B/"report_snapshots/progress-v29-physical-budget.json");snap=load(B/"report_snapshots/progress-v30-physical-budget.v2.json");actual=physical_attempts()
 ck("current_budget1195_HTTP_raw_backed_delta67",len(actual)==snap["totals"]["HTTP"]==1195 and snap["totals"]["HTTP"]-before["totals"]["HTTP"]==len(new_http))
 ck("current_budget1242534214bytes_raw_backed_delta5176466",sum(x["bytes"] for x in actual)==snap["totals"]["bytes"]==1242534214 and snap["totals"]["bytes"]-before["totals"]["bytes"]==sum(x["bytes"] for x in new_http)==5176466)
 ck("pre_R52_budget_snapshot_retained_as_earlier_capture",load(B/"report_snapshots/progress-v30-physical-budget.json")["totals"]["HTTP"]==1193)
 active={}
 for x in lines(B/"epoch_ledger.jsonl"):
  if x.get("epoch_id") in ("C-E02","SS-E02") and x.get("status")=="active" and x.get("stage") in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT"):active[x["stage_manifest_path"]]=x["stage_manifest_sha256"]
 for p,s in active.items():verify_stage_chain(ROOT/p,s)
 ck("all23_existing_G5_G6_chains_intact_no_new_scientific_G5",len(active)==23)
 ck("MCTS214_rows_entire_SHA_unchanged",len(lines(B/"run_ledger.jsonl"))==214 and sha(B/"run_ledger.jsonl")==load(B/"report_snapshots/progress-v29.json")["MCTS_run_ledger_SHA"])
 for f,s in [("C","09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46"),("SS","a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f")]:
  ck(f+"_G4_frozen_SHA_unchanged",sha(B/f"{f}/E02/stages/G4_SCOPE_FREEZE.json")==s)
  ck(f+"_actual_G7_G8_absent",all(not list((ROOT/B/f"{f}/E02/stages").rglob(stage+".json")) for stage in STAGES if stage.startswith(("G7_","G8_"))))
 inputs += [R49/x for x in ["chain_plan.json","page_execution.jsonl","metadata_unique_sources.jsonl","title_enzyme_hints.jsonl","metadata_pagination_summary.json"]]+[R50/x for x in ["query_execution.jsonl","title_hint_prior_triage.jsonl","metadata_boundary_and_triage_summary.json","pre_HTTP_contract_rejection_retained.json"]]+[R51/x for x in ["metadata_execution.jsonl","original_access_execution.jsonl","A3_bibliographic_identity.json"]]+[R52/x for x in ["query_execution.jsonl","raw_custody_summary.json"]]+[B/"report_snapshots/progress-v30-physical-budget.v2.json",O/"literal_metadata_variants_retained.jsonl"]
 result=dict(task=T,agent_role="A11",epoch_id="C-E02+SS-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,input_manifest_sha={str(p):sha(p) for p in dict.fromkeys(inputs)},checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),errors=[x for x in checks if not x["passed"]],unprocessed=[],new_HTTP=67,new_bytes=5176466,total_HTTP=1195,total_bytes=1242534214,additional_metadata_observations=5726,additional_unique_metadata=5491,all_query_union_metadata_observations=6057,all_query_union_metadata_groups=5763,duplicate_observations_preserved=294,literal_field_variant_groups=len(variants),title_hints=95,prior_literal_hits=27,unmatched_no_clearance=68,original_access_pending_sources=1,new_source_science_reads=0,new_complete_chemical_records=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,source_saturation=False,complete_qualification_round=False,independent_chemical_validation=False)
 put(O/"independent_A11_cursor_raw_and_access_audit.json",result)
 print(json.dumps({k:result[k] for k in ["passed","failed","new_HTTP","new_bytes","literal_field_variant_groups","fresh_C","fresh_SS"]}))
 if result["failed"]:raise RuntimeError("A11_FAILED")
if __name__=="__main__":main()
