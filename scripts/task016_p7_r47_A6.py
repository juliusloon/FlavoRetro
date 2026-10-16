"""R47 A6: source numbering conflicts, 16-slot assay inventory, both axes deferred."""
import json,re,collections,urllib.parse
from pathlib import Path
from lxml import html
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import put,load,lines,sha,now
from scripts.task016_p7_orchestrate import role_manifest,freeze_stage_manifest,verify_stage_chain
from scripts import task016_p7_full_qualification_harness_v3 as fq
T="TASK-016-P7";B=Path("outputs/task016-p7/v1");SID="PMC13422134"
SHARED=B/"governance/R47-Iris-cross-axis-source-read-binding-v1";O=SHARED/"A6"
ASSET=B/"C/E02/fresh/C-E02-R46-Iris-advertised-assets-v1"
ROUTES=["EPMC_XML_attempt","PMC_public_open_data_index_attempt","PMC_public_HTML","Crossref_declared_publisher_HTML_attempt","PMC_advertised_SI_and_images_attempt"]
def main():
 assert not (ROOT/O).exists()
 ready=load(SHARED/"both_G5_ready_before_first_read.json")
 per={}
 for family in ("C","SS"):
  cp=ready["contracts"][family];r=Path(cp["path"]).parent;version=[]
  for role in ("A4","A5"):
   artifact=load(r/role/"available_original_scientific_text.json");blocks=artifact["blocks"]
   assert len(blocks)==103 and artifact["independent_graph_transcription"] is False
   for row in blocks:assert hashlib_sha(row["text"])==row["text_SHA"]
   version.append(blocks)
  a,b=version;assert [(x["index"],x["tag"],x["section_path"],x["text_SHA"]) for x in a]==[(x["index"],x["tag"],x["section_path"],x["text_SHA"]) for x in b]
  per[family]=dict(cp=cp,r=r,a=a,b=b)
 assert [x["text_SHA"] for x in per["C"]["a"]]==[x["text_SHA"] for x in per["SS"]["a"]]
 selected=[25,35,58,64,67,68,77,79]
 critical=[dict(index=x["index"],tag=x["tag"],section_path=x["section_path"],text=x["text"],text_SHA=x["text_SHA"]) for x in per["C"]["a"] if x["index"] in selected]
 put(O/"dual_text_reconciliation.json",dict(task=T,at=now(),source_id=SID,blocks_each=103,exact_text_SHA_match=103,locator_match=103,differences=[],critical_scientific_contexts=critical,both_families_share_same_source_and_text=True,independent_source_groups=1,independent_graph_transcriptions=0,independent_chemical_validation=False))
 original=load(ASSET/"A3_original_front_identity.json")["original_raw"]
 root=html.fromstring((ROOT/original["path"]).read_bytes())
 plans=load(ASSET/"advertised_asset_plan.json")["queries"];executed=lines(ASSET/"asset_execution.jsonl")
 figure_rows=[]
 for im in root.xpath("//article//img[@src]"):
  url=im.get("src");q=next(x for x in plans if x["url"]==url);e=next(x for x in executed if x["query_id"]==q["query_id"])
  fig=next((x for x in im.iterancestors() if x.tag=="figure" and x.get("id")),None)
  figure_id=fig.get("id") if fig is not None else "graphical_abstract"
  # Source filenames do not encode figure numbering; bind DOM owner explicitly.
  figure_rows.append(dict(source_figure_id=figure_id,source_url=url,advertised_filename=Path(urllib.parse.urlsplit(url).path).name,raw_pointer=e["raw_pointer"],A6_visually_inspected=figure_id in {"cbic70486-fig-0002","cbic70486-fig-0003","cbic70486-fig-0004","graphical_abstract"},chemical_scope_relevant=figure_id in {"cbic70486-fig-0003","cbic70486-fig-0004"}))
 assert len(figure_rows)==6
 put(O/"original_figure_DOM_binding.json",dict(task=T,source_id=SID,at=now(),original_HTML=original,figures=figure_rows,filename_suffix_is_not_figure_number=True))
 methods={1:"tectorigenin",2:"formononetin",3:"genistein",4:"daidzein",5:"apigenin",6:"luteolin",7:"naringenin",8:"eriodictyol",9:"hesperetin",10:"kaempferol",11:"isorhamnetin",12:"phloretin",13:"3,4-dichloroaniline",14:"3,4-dichlorobenzenethiol",15:"emodin",16:"tectoridin"}
 named_results={1:"tectorigenin",2:"phloretin",3:"kaempferol",4:"luteolin",5:"apigenin",6:"emodin"}
 classes={1:"isoflavone",2:"dihydrochalcone",3:"flavonol",4:"flavone",5:"flavone",6:"anthraquinone",7:"flavonol",8:"flavonol",9:"flavonol",10:"flavanone",11:"flavanone",12:"isoflavone",13:"glycoside",14:"glycoside",15:"glycoside",16:"glycoside"}
 slots=[]
 for i in range(1,17):
  result_name=named_results.get(i)
  slots.append(dict(original_Figure4_slot=i,methods_name_at_same_number=methods[i],results_text_name_at_same_number=result_name,results_text_substrate_class=classes[i],source_reported_result="O-glycoside product(s) detected" if i<=6 else "N.D. = no product",author_explicit_activity=i<=6,numeric_conversion_not_digitized=None,methods_vs_results_name_conflict=result_name is not None and result_name!=methods[i],drawn_structure_transcribed=False,complete_sugar_stereo=None,qualifying_fresh=False,absence_not_converted_to_missing=True))
 put(O/"all_16_assay_slot_dispositions.json",dict(task=T,at=now(),source_id=SID,original_denominator=16,source_reported_positive_substrate_slots=6,source_reported_ND_slots=10,slots=slots,denominator_is_assay_slots_not_unique_reaction_products=True,product_count_unresolved=True,methods_and_results_numbering_preserved=True,Figure4_glc_labels_not_complete_sugar_graphs=True,no_SI_content_read=True))
 conflicts=[dict(kind="numbering",basis="Methods block25 vs Results block64 and Figure4",examples=[dict(name="phloretin",methods=12,results=2),dict(name="luteolin",methods=6,results=4),dict(name="kaempferol",methods=10,results=3),dict(name="emodin",methods=15,results=6)],resolved=False),dict(kind="standard_number",basis="Methods block25 vs Results block58 and Figure3",name="tectoridin",methods=16,results_and_Figure3=14,resolved=False),dict(kind="substrate_classes",basis="Methods13/14 are aniline/thiol; Results/Figure4 classify13-16 as glycosides",resolved=False),dict(kind="ion_polarity_annotation",basis="Results58 writes [M+H-162] negative sign while Figure3 positive-ion labels use positive polarity",resolved=False)]
 assessment=dict(task=T,at=now(),source_id=SID,DOI="10.1002/cbic.70486",enzyme="UGT707B2",organism="Iris tectorum",available_main_scientifically_reviewed=True,own_assay_context="purified enzyme in vitro; UDP-glucose; heat-inactivated control",author_named_reaction="tectorigenin to tectoridin, 7-O-glycosylation",named_reaction_product_full_graph_independently_transcribed=False,other_main_reported_products="LC-MS preliminarily assigned O-glycosides for six substrate slots, sites for other products not structurally resolved in available main",observed_Figure4_denominator=16,author_reported_positive_slots=6,author_reported_ND_slots=10,source_ND_semantics="no product under reported assay, not missing; not a transferable negative for a different substrate domain",conflicts=conflicts,C_frozen_scope_assessment="Available main positive products are reported as O-glycosides, including a 7-O isoflavone standard match. No complete C3-H flavone C6 beta-D-Glc reaction qualified.",SS_frozen_scope_assessment="Multiple O-glycoside products do not establish sugar-residue O2 elongation. Figure4 glycoside slots13-16 are N.D.; no complete frozen flavonol3-O parent/terminal sugar reaction qualified. Their complete graphs were not independently transcribed, so do not call these frozen-SS negative controls.",SI_access_status="Original advertised SI link returned CAPTCHA HTML, retained; no challenge solving and no SI PDF read.",whole_paper_C_or_SS_absence_claim=False,source_reaction_eligible=None,full_reaction_inventory_enumerated=False,full_source_alias_graph_named_history_review_complete=False,complete_reference_precursors=False,qualified_closure_groups_C=0,qualified_closure_groups_SS=0,source_saturation=False,independent_chemical_validation=False,scope_modified=False,read_model_outcome=False,source_independence_groups=1)
 put(O/"source_scientific_assessment.json",assessment)
 evidence=[fq.pointer(O/x) for x in ["dual_text_reconciliation.json","original_figure_DOM_binding.json","all_16_assay_slot_dispositions.json","source_scientific_assessment.json"]]+[fq.pointer(ASSET/"raw_custody_summary.json")]
 for family in ("C","SS"):
  rec=per[family];r=rec["r"];cp=rec["cp"];g5=ready["G5"][family]
  events=fq.evaluation_events(cp);assert len(events)==4
  exported=[dict(x,export_recorded_at=now(),scientific_content_read=x["event_type"]=="scientific_read_completed",future_epoch_reuse_allowed=False) for x in events]
  exported.append(dict(task=T,source_id=SID,epoch_id=family+"-E02",event_type="A6_source_reconciliation_completed",timestamp=now(),reader_role="A6",contract_sha256=cp["sha256"],G5=g5,closure_tokens=["article:"+SID,"doi:10.1002/cbic.70486","pmid:42530388"],development_exposed=True,scientific_content_read=True,exposure_type="current_epoch_evaluation",future_fresh_eligible=False,current_epoch_eligibility="conditional_only",future_epoch_reuse_allowed=False,read_time_basis="A6 review recorded at completion after actual A4/A5 receipts; no fabricated before-read timestamp.",evidence=evidence))
  ep=r/"scientific_exposure_reads.jsonl";write(T,str(ep),"".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in exported))
  reason="Available original and 16 assay slots assessed; main supports O-glycosylation. SI access, conflicting compound numbering, complete chemical reaction/graph/site/stereo/precursor inventory and historical closure are unresolved. Source is deferred; no complete "+family+" frozen-scope reaction admitted."
  result=dict(task=T,agent_role="A6",epoch_id=family+"-E02",timestamp=now(),contract_sha256=cp["sha256"],source_dispositions=[dict(source_id=SID,execution_state="completed",terminal_for_this_round=True,disposition="deferred",reason=reason,evidence=evidence,original_routes_executed=ROUTES,scientific_body_read=True)],reaction_dispositions=[],no_reaction_records_does_not_mean_no_reactions_in_paper=True,source_assay_inventory=fq.pointer(O/"all_16_assay_slot_dispositions.json"),chemical_reaction_enumeration_complete=False,complete_graphs=0,fresh_admitted=0,eligible_as_source_saturation_complete_round=False,independent_chemical_validation=False,scope_modified=False,read_model_outcome=False)
  put(r/"A6/round_result.json",result)
  inputs=[r/"raw_source_universe.json",r/"full_qualification_contract.json"]+[r/role/name for role in ("A4","A5") for name in ("available_original_scientific_text.json","round_result.json","role_manifest.json")]+[ASSET/"raw_custody_summary.json",ASSET/"asset_execution.jsonl",ASSET/"advertised_asset_plan.json",Path(__file__).resolve().relative_to(ROOT)]
  outputs=[Path(x["path"]) for x in evidence]+[r/"A6/round_result.json",ep]
  role=role_manifest("A6",family+"-E02",inputs,outputs,dict(processed=1,passed=0,rejected=0,pending=1),pointers=evidence,read_holdout=True,read_model_outcome=False)
  role.update(count_unit="one shared source scientifically assessed, chemical qualification deferred",independent_chemical_validation=False)
  put(r/"A6/role_manifest.json",role)
  rm=dict(task=T,batch_kind="full_qualification",timestamp=now(),contract_sha256=cp["sha256"],read_model_outcome=False,scope_modified=False,late_prior_design_addenda=[],**{key:fq.pointer(r/role/name) for role in ("A4","A5","A6") for key,name in [(role+"_result","round_result.json"),(role+"_role","role_manifest.json")]})
  put(r/"full_round_manifest.json",rm)
  valid=fq.validate_full_science_round(cp,g5,fq.pointer(r/"full_round_manifest.json"))
  assert valid["round_execution_complete"] and valid["fresh_admitted"]==0 and valid["reaction_candidates"]==0
  valid.update(at=now(),eligible_as_source_saturation_complete_round=False,no_reaction_records_means="Chemical reaction records not yet transcribed, not reaction absence.",complete_source_scientific_clearance=False,shared_source_independence_groups=1,SI_original_access_pending=True,source_assay_slots=16,author_positive_assay_slots=6,author_ND_assay_slots=10)
  put(r/"full_round_validation.json",valid)
  g6=Path(g5["path"]).parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
  paths=[r/"full_round_manifest.json",r/"full_round_validation.json",r/"A6/round_result.json",r/"A6/role_manifest.json",ep]+[Path(x["path"]) for x in evidence]+[r/role/name for role in ("A4","A5") for name in ("available_original_scientific_text.json","round_result.json","role_manifest.json")]
  freeze_stage_manifest(ROOT/g6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",paths,Path(g5["path"]),expected_previous_sha=g5["sha256"],family=family,epoch_id=family+"-E02")
  verify_stage_chain(ROOT/g6,sha(g6))
  row=dict(task=T,epoch_id=family+"-E02",family=family,stage="G6_IDENTITY_STRUCTURE_ADMIT",status="active",event_type="R47_available_main_O_glycosylation_deferred",at=now(),stage_manifest_path=str(g6),stage_manifest_sha256=sha(g6),source_count=1,shared_source_group="PMC13422134",fresh_admitted=0,approval_type="agent_delegated",human_reviewed=False)
  ledger=B/"epoch_ledger.jsonl";write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,sort_keys=True)+"\n")
  print(json.dumps(dict(family=family,G6_SHA=sha(g6),source_deferred=1,original_assay_slots=16,source_reported_positive=6,source_reported_ND=10,fresh_admitted=0,saturation=False)),flush=True)
def hashlib_sha(s):
 import hashlib
 return hashlib.sha256(s.encode()).hexdigest()
if __name__=="__main__":main()
