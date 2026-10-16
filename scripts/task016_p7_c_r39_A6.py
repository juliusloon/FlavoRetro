"""R39 A6: bounded source assessment, permanent exposures, round conservation and G6."""
import json,re,hashlib,collections
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts import task016_p7_full_qualification_harness_v3 as fq
from scripts.task016_p7_orchestrate import role_manifest,freeze_stage_manifest,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1"
F=B/"C/E02/fresh/C-E02-R41-A6-original-figure-supplement-v1"
O=R/"A6";SID="PMC13564134";RID="R39:PMC13564134:isoorientin-endpoint"
G5=B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=G5.parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
def main():
 assert not (ROOT/O).exists()
 cp=fq.pointer(R/"full_qualification_contract.json")
 spec=load(Path(cp["path"]))
 ax=load(R/"A4/original_scientific_paragraphs.json");bx=load(R/"A5/original_scientific_paragraphs.json")
 a=ax["paragraphs"];b=bx["paragraphs"];assert len(a)==len(b)==1531
 assert [(x["group"],x["index"]) for x in a]==[(x["group"],x["index"]) for x in b]
 diff=[]
 for x,y in zip(a,b):
  assert hashlib.sha256(x["text"].encode()).hexdigest()==x["text_SHA"] and hashlib.sha256(y["text"].encode()).hexdigest()==y["text_SHA"]
  assert re.sub(r"\s+","",x["text"])==re.sub(r"\s+","",y["text"])
  if x["text_SHA"]!=y["text_SHA"]:diff.append(dict(group=x["group"],index=x["index"],A4_text_SHA=x["text_SHA"],A5_text_SHA=y["text_SHA"],disposition="inline XML element whitespace only; original text preserved"))
 critical=[("main",26),("main",29),("main",31),("main",36),("main",44),("SI",24),("SI",27),("SI",34),("SI",670),("SI",671),("SI",672)]
 comparisons=[]
 for g,i in critical:
  x=next(x for x in a if (x["group"],x["index"])==(g,i));y=next(x for x in b if (x["group"],x["index"])==(g,i))
  comparisons.append(dict(group=g,index=i,A4_text_SHA=x["text_SHA"],A5_text_SHA=y["text_SHA"],content_equal_ignoring_whitespace=True,original_A4_text=x["text"],original_A5_text=y["text"]))
 put(O/"dual_parser_reconciliation.json",dict(task=T,source_id=SID,main_paragraphs_each=52,SI_paragraphs_each=1479,paragraphs_compared=1531,exact_text_SHA_equal=1531-len(diff),whitespace_only_differences=diff,non_whitespace_differences=[],critical_scientific_contexts=comparisons,both_parser_outputs=fq.pointer(R/"A4/original_scientific_paragraphs.json"),A5_parser_output=fq.pointer(R/"A5/original_scientific_paragraphs.json"),two_graph_transcriptions=False,independent_chemical_validation=False))
 # Hypothetical identity sanity check uses a preexisting build graph, not a new extraction.
 build=next(x for x in load(B/"C/E02/build_supports.json") if x["reaction_id"]=="C-CHRYSIN-LU6")
 mol=Chem.MolFromSmiles(build["target"]);neutral=rdMolDescriptors.CalcExactMolWt(mol);theory=neutral+1.007276466621;reported=449.2320
 mass=dict(task=T,source_id=SID,reported_mz=reported,reported_ion="[M+H]+",reported_in="SI paragraph27 and embedded image6 red-star peak",hypothetical_identity="isoorientin, using existing C-CHRYSIN-LU6 graph",build_graph_source=fq.pointer(B/"C/E02/build_supports.json"),formula=rdMolDescriptors.CalcMolFormula(mol),neutral_monoisotopic_mass=neutral,proton_mass_constant_Da=1.007276466621,theoretical_M_plus_H=theory,difference_Da=reported-theory,difference_ppm=(reported-theory)/theory*1e6,observation="Reported peak label and caption agree with each other but do not agree with the monoisotopic [M+H]+ of the hypothesized named structure. Preserve as unresolved; no correction, no automatic rejection of the entire study.",raw_value_preserved=True,new_candidate_graph_extracted=False,independent_chemical_validation=False)
 put(O/"reported_mass_identity_sanity_check.json",mass)
 renders=load(F/"A6_render_manifest.json")
 visual=[]
 for label,entry in [("Original Figure1 pathway",next(x for x in renders["pages"] if x["page"]==2)),("Original Figure6 UDP-Glc and endpoint titer",next(x for x in renders["pages"] if x["page"]==7)),("SI Figure5 degradation-control HPLC",next(x for x in renders["SI_images"] if x["member"].endswith("image5.tiff"))),("SI Figure6 mass spectrum",next(x for x in renders["SI_images"] if x["member"].endswith("image6.tiff")))]:
  fq.bound(entry);visual.append(dict(label=label,path=entry["path"],sha256=entry["sha256"],A6_visually_inspected=True))
 preview=Path("data/raw/task016-p7/C/E02/C-E02-R41-A6-original-figure-supplement-v1/A6-SI-image8-white-preview.png")
 visual.append(dict(label="SI Figure8 calibration curves; white preview of transparent source image8",**fq.pointer(preview),A6_visually_inspected=True))
 observations=dict(task=T,source_id=SID,DOI="10.1016/j.abiote.2026.100085",scope_relevant_author_report=True,author_reported_conversion="luteolin to isoorientin via flavone 6-C-glycosyltransferase in engineered yeast",experimental_context="de novo S. cerevisiae whole-cell pathway, glucose feed, endogenous UDP-glucose; not a purified standalone-enzyme assay",own_experiment_support=["main26 GyCGT1 integration into STL12, STI1 0.54 mg/L","main29 UDP-glucose engineering, STI5 3.17 mg/L","main31 one-step luteolin glycosylation statement","main36 purchased isoorientin standard","main44 HPLC/LC-MS methods","SI27 mass-spectrum caption","SI670-672 GyCGT1, Gentiana yunnanensis Franch., PZ535504"],earlier_route_citation="10.1186/s12934-018-0952-5 (2018), bibliography25; citation alone does not establish shared study cohort",literal_fields=dict(acceptor="luteolin",product="isoorientin",donor="UDP-glucose",enzyme="GyCGT1",organism="Gentiana yunnanensis Franch.",sequence_accession="PZ535504",site_report="6-C",anomer_or_D_configuration_independently_transcribed=None),visual_checks=visual,SI_Figure5_limit="BY4742 fed authentic isoorientin is a stability/degradation control. It is not a co-injection identification of the newly biosynthesized STI1 product.",SI_Figure8_limit="Calibration curves support reported quantitation, not independent position/stereo assignment.",source_reaction_eligible=None,unresolved_conflicts=["SI assigned [M+H]+ 449.2320 vs expected named-structure exact mass"],unresolved_requirements=["independent full acceptor/donor/product covalent graphs and sugar stereo","full reference precursors","verified source/cohort/alias closure vs prior exposure and 28 internal names","fixed-scope static complete-reference test"],potential_historical_overlap="Frozen build C-CHRYSIN-LU6 already has a luteolin C6-glucoside target; name/pathway resemblance is a warning, not a completed candidate full-graph comparison.",all_prior_graph_alias_comparisons_complete=False,full_named_candidate_review_complete=False,whole_paper_reaction_absence_claim=False,independent_chemical_validation=False,source_saturation_established=False)
 put(O/"source_scientific_assessment.json",observations)
 rows=fq.evaluation_events(cp);assert len(rows)==4
 exported=[]
 for e in rows:
  exported.append(dict(e,export_recorded_at=now(),scientific_content_read=e["event_type"]=="scientific_read_completed",future_epoch_reuse_allowed=False))
 pdfreceipt=load(F/"A6_scientific_read_receipt.json")
 exported.append(dict(pdfreceipt,event_type="A6_supplemental_original_read",export_recorded_at=now(),future_epoch_reuse_allowed=False))
 write(T,str(R/"scientific_exposure_reads.jsonl"),"".join(json.dumps(x,sort_keys=True,ensure_ascii=False)+"\n" for x in exported))
 evidence=[fq.pointer(p) for p in [O/"dual_parser_reconciliation.json",O/"reported_mass_identity_sanity_check.json",O/"source_scientific_assessment.json",F/"A6_scientific_read_receipt.json",F/"A6_render_manifest.json",R/"scientific_exposure_reads.jsonl"]]
 reason="Original text processed by two independent parsers and source-relevant figures reviewed by A6. Author reports direct luteolin C6-glucosylation in engineered yeast. Mass assignment conflict, full graph/stereo/precursor and historical closure remain unresolved; no source-complete or fresh candidate admitted."
 result=dict(task=T,agent_role="A6",epoch_id="C-E02",timestamp=now(),contract_sha256=cp["sha256"],source_dispositions=[dict(source_id=SID,execution_state="completed",terminal_for_this_round=True,disposition="deferred",reason=reason,evidence=evidence,original_routes_executed=["EuropePMC_fullTextXML","PMC_exact_index_advertised_SI"],additional_A6_original_route="official_index_advertised_PDF_supplement",scientific_body_read=True)],reaction_dispositions=[dict(source_id=SID,reaction_id=RID,disposition="deferred",terminal_for_this_round=True,reason=reason,evidence=evidence)],full_graphs_qualified=0,fresh_admitted=0,source_saturation_established=False,eligible_as_source_saturation_complete_round=False,saturation_counting_reason="Execution of the fixed documentary round can be complete while scientific qualifications remain deferred; do not count this as two completed saturation qualification rounds.",independent_graph_transcriptions=0,independent_chemical_validation=False,scope_modified=False,read_model_outcome=False)
 put(O/"round_result.json",result)
 inputs=[R/"raw_source_universe.json",R/"full_qualification_contract.json",R/"A4/round_result.json",R/"A5/round_result.json",R/"A4/role_manifest.json",R/"A5/role_manifest.json",R/"A4/original_scientific_paragraphs.json",R/"A5/original_scientific_paragraphs.json",F/"original_pdf_text.json",F/"A6_render_manifest.json",B/"C/E02/build_supports.json",Path(__file__).resolve().relative_to(ROOT)]
 outputs=[Path(x["path"]) for x in evidence]+[O/"round_result.json"]
 role=role_manifest("A6","C-E02",inputs,outputs,dict(processed=1,passed=0,rejected=0,pending=1),pointers=evidence,read_holdout=True,read_model_outcome=False)
 role.update(independent_chemical_validation=False,read_other_extractor_output=True,count_unit="one source processed, chemical qualification deferred",unprocessed=[])
 put(O/"role_manifest.json",role)
 roundobj=dict(task=T,batch_kind="full_qualification",timestamp=now(),contract_sha256=cp["sha256"],read_model_outcome=False,scope_modified=False,late_prior_design_addenda=[],**{key:fq.pointer(R/role/path) for role in ("A4","A5","A6") for key,path in [(role+"_result","round_result.json"),(role+"_role","role_manifest.json")]})
 put(R/"full_round_manifest.json",roundobj)
 valid=fq.validate_full_science_round(cp,fq.pointer(G5),fq.pointer(R/"full_round_manifest.json"))
 valid.update(at=now(),validator_path="scripts/task016_p7_full_qualification_harness_v3.py",validator_SHA=sha("scripts/task016_p7_full_qualification_harness_v3.py"),actual_G4_list_bank_and_all_original_receipts_used=True,independent_chemical_validation=False,eligible_as_source_saturation_complete_round=False,complete_execution_is_not_scientific_clearance=True)
 put(R/"full_round_validation.json",valid)
 assert valid["round_execution_complete"] and valid["fresh_admitted"]==0 and valid["reaction_disposition_counts"]==dict(qualified=0,deferred=1,rejected=0,unprocessed=0)
 paths=[R/"full_round_manifest.json",R/"full_round_validation.json"]+outputs+[O/"role_manifest.json"]+[R/role/name for role in ("A4","A5") for name in ("round_result.json","original_scientific_paragraphs.json","role_manifest.json")]
 freeze_stage_manifest(ROOT/G6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",paths,G5,expected_previous_sha=sha(G5),family="C",epoch_id="C-E02")
 verify_stage_chain(ROOT/G6,sha(G6))
 ledger=B/"epoch_ledger.jsonl"
 row=dict(task=T,epoch_id="C-E02",family="C",stage="G6_IDENTITY_STRUCTURE_ADMIT",status="active",event_type="R39_full_round_execution_and_deferred_science",at=now(),stage_manifest_path=str(G6),stage_manifest_sha256=sha(G6),round_validation=fq.pointer(R/"full_round_validation.json"),fresh_admitted=0,source_scientific_deferred=1,reaction_scientific_deferred=1,approval_type="agent_delegated",human_reviewed=False)
 write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,sort_keys=True)+"\n")
 event(T,"C_R39_G6_deferred_science",G6_SHA=sha(G6),fresh_admitted=0,round_execution_complete=True,source_saturation=False)
 print(json.dumps(dict(G6_SHA=sha(G6),round_execution_complete=valid["round_execution_complete"],source_deferred=1,reaction_deferred=1,paragraphs_compared=1531,whitespace_only=len(diff),mass_difference_Da=mass["difference_Da"],fresh_admitted=0,saturation=False)))
if __name__=="__main__":main()
