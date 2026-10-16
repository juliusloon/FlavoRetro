"""R56 A6: exact worksheet reconciliation, source evidence roles and pending chemistry."""
import json,collections,re,zipfile,hashlib
from decimal import Decimal,InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts.task016_p7_orchestrate import verify_hashes,freeze_stage_manifest,verify_stage_chain,role_manifest
from scripts.task016_p7_r56_read_receipts import O,G5
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
def main():
 assert not (ROOT/O/"A6").exists()
 cp=O/"pre_science_exposure_contract.json";c=load(cp);verify_hashes(c["input_manifest_sha"])
 a=load(O/"A4/all_original_stored_cells.json");b=load(O/"A5/all_original_stored_cells.json")
 assert a["worksheets"]==b["worksheets"]
 for role in ("A4","A5"):
  m=load(O/role/"role_manifest.json");verify_hashes(m["input_manifest_sha"]);verify_hashes(m["output_file_sha"])
  assert not m["read_other_extractor_output"] and not m["independent_graph_transcription"]
 ar=load(O/"A4/role_manifest.json");br=load(O/"A5/role_manifest.json")
 assert ar["reader_id"]!=br["reader_id"] and not set(ar["input_manifest_sha"])&set(br["output_file_sha"]) and not set(br["input_manifest_sha"])&set(ar["output_file_sha"])
 start=dict(task=T,family="SS",epoch_id="SS-E02",source_id=c["source_DOI"],reader_role="A6",event_type="scientific_supplement_reconciliation_started",timestamp=now(),G5=dict(path=str(G5),sha256=sha(G5)),raw_files=[c["raw_XLSX"]],approval_type="agent_delegated",human_reviewed=False)
 put(O/"A6/scientific_reconciliation_started.json",start)
 sheets=a["worksheets"];zero=[];blank=[];formula=[];dispositions=[]
 for s in sheets:
  cells=s["cells"];byref={x["reference"]:x for x in cells}
  title=byref["A1"]["resolved_value"]
  for cell in cells:
   row=dict(sheet=s["name"],**cell)
   if cell["resolved_value"] is None:blank.append(row)
   if cell["formula"] is not None:formula.append(row)
   if cell["cell_type"] in (None,"n") and cell["raw_value"] is not None:
    try:
     if Decimal(cell["raw_value"])==0:zero.append(row)
    except InvalidOperation:pass
  kind={"TableS1":"qRT-PCR_primers","TableS2":"UGT_cloning_primers","TableS3":"metabolite_name_formula_class_annotation","TableS4":"tissue_top_content_metabolites","TableS5":"differential_metabolite_counts","TableS6":"metabolite_KEGG_enrichment","TableS7":"top10_flavonoid_tissue_content","TableS8":"differential_gene_counts","TableS9":"gene_KEGG_enrichment","TableS10":"gene_GO_enrichment","TableS11":"flavonoid_gene_FPKM","TableS12":"qRT-PCR_selected_gene_FPKM","TableS13":"LbUGT_gene_transcript_mapping","TableS14":"other_species_phylogenetic_gene_proposed_functions"}[s["name"]]
  dispositions.append(dict(sheet=s["name"],original_title=title,dimension=s["dimension"],stored_cells=len(cells),evidence_kind=kind,direct_complete_SS_reaction_established=False,source_qualified=False,not_a_whole_paper_negative=True))
 assert len(sheets)==14 and sum(len(x["cells"]) for x in sheets)==4994 and len(zero)==43 and len(blank)==269 and len(formula)==15
 put(O/"A6/literal_worksheet_reconciliation.json",dict(task=T,at=now(),worksheets=14,stored_cells_each=4994,exact_cell_and_sheet_metadata_matches=4994,all_named_worksheets_equal=True,independent_parsers=2,independent_graph_transcriptions=0,source_qualified=False,inputs={str(O/r/"all_original_stored_cells.json"):sha(O/r/"all_original_stored_cells.json") for r in ("A4","A5")}))
 put(O/"A6/all14_worksheet_evidence_dispositions.json",dict(task=T,at=now(),worksheets=dispositions,processed_worksheets=14,unprocessed_named_worksheets=[],source_reaction_admitted=0))
 put(O/"A6/zero_blank_and_external_formula_preservation.json",dict(task=T,at=now(),numeric_zero_count=len(zero),numeric_zeros=zero,explicit_blank_count=len(blank),explicit_blanks=blank,formula_count=len(formula),formula_cells_with_original_cached_values=formula,formulas_evaluated=False,external_workbook_requested=False,cached_values_not_verified_by_recalculation=True,absence_not_filled=True,all_lexical_numeric_values_unrounded=True))
 table=next(x for x in sheets if x["name"]=="TableS3");rows=collections.defaultdict(dict)
 for cell in table["cells"]:rows[int(re.sub("[^0-9]","",cell["reference"]))][re.sub("[^A-Z]","",cell["reference"])]=cell["resolved_value"]
 annotations=[dict(source_row=i,source_cells=[col+str(i) for col in "ABCD"],formula_literal=rows[i]["A"],compound_name_literal=rows[i]["B"],class_I_literal=rows[i]["C"],class_II_literal=rows[i]["D"],evidence_kind="metabolomics annotation, not enzymatic formation reaction",source_identity_or_complete_structure_verified=False) for i in sorted(rows) if i>=3]
 assert len(annotations)==523
 write(T,str(O/"A6/all523_metabolite_annotation_rows.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in annotations))
 contexts=[]
 for i in [222,257,266,269,294,296,297]:
  x=next(x for x in annotations if x["source_row"]==i);contexts.append(dict(x,scope_relation="literal name hint only; no source reaction graph or site/stereo clearance",fresh_admitted=False))
 # Preserve package relationships and embedded external cache without opening any referenced file.
 raw=Path(c["raw_XLSX"]["path"]);cache=[]
 with zipfile.ZipFile(ROOT/raw) as z:
  for name in z.namelist():
   if name.startswith("xl/externalLinks/"):
    data=z.read(name)
    cache.append(dict(zip_entry=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),original_XML=data.decode("utf-8"),A6_only_package_review=True,external_reference_not_accessed=True))
 put(O/"A6/embedded_external_reference_XML_retained.json",dict(task=T,at=now(),package_parts=cache,parts_count=len(cache),external_workbook_accessed=False,not_independent_dual_graph_evidence=True))
 assessment=dict(task=T,agent_role="A6",at=now(),approval_type="agent_delegated",human_reviewed=False,source_DOI=c["source_DOI"],source_SI_DOI=c["source_SI_DOI"],official_raw=c["raw_XLSX"],scope_of_review="All14 named XLSX worksheets,4994 stored worksheet cells; A6 separately retains embedded external-reference XML. Previously read PDF SI remains separate; main article unavailable.",exact_dual_worksheet_agreement=True,independent_graph_transcriptions=0,metabolite_annotation_rows=523,source_specific_literal_contexts=contexts,numeric_zeros_preserved=43,explicit_blanks_preserved=269,formula_cached_value_pairs_preserved=15,formulas_not_evaluated=True,external_workbook_not_accessed=True,source_science_new_independent_group_increment=0,source_already_current_epoch_read=True,source_reaction_eligible=None,chemical_qualification="deferred",complete_acceptor_product_donor_graphs=0,complete_reference_precursors=False,frozen_SS_O2_enzymatic_reaction_established=False,C_annotation_not_admitted_without_C_prospective_contract=True,all_prior_source_graph_alias_and28_names_review_complete=False,source_whole_paper_no_SS_or_C_claim=False,whole_source_scientific_qualification_complete=False,eligible_as_source_saturation_complete_round=False,fresh_admitted=0,remaining_evidence=["main-original enzyme assay and product/site assignment","source-bound complete reaction graphs, sugar stereo and donor identity","all historical source/graph/alias and permanent28-name checks","actual frozen scope full-reference preflight"],evidence=[dict(path=str(O/"A6/all14_worksheet_evidence_dispositions.json"),sha256=sha(O/"A6/all14_worksheet_evidence_dispositions.json")),dict(path=str(O/"A6/all523_metabolite_annotation_rows.jsonl"),sha256=sha(O/"A6/all523_metabolite_annotation_rows.jsonl")),dict(path=str(O/"A6/zero_blank_and_external_formula_preservation.json"),sha256=sha(O/"A6/zero_blank_and_external_formula_preservation.json"))])
 put(O/"A6/source_scientific_assessment.json",assessment)
 exports=[]
 for role in ("A4","A5"):
  for fname in ["scientific_read_started.json","scientific_read_completed.json"]:
   x=load(O/role/fname);exports.append(dict(x,export_recorded_at=now(),exposure_type="current_epoch_evaluation",prior_design=False,current_epoch_eligibility="conditional_only_not_granted_by_supplement",source_event_pointer=dict(path=str(O/role/fname),sha256=sha(O/role/fname)),closure_tokens=["doi:"+c["source_DOI"],"doi:"+c["source_SI_DOI"]]))
 finish=dict(start,event_type="scientific_supplement_reconciliation_completed",timestamp=now(),raw_XLSX_scientific_read=True,scientific_content_read=True,bytes_opened=c["raw_XLSX"]["bytes"],current_epoch_eligibility="conditional_only_not_granted_by_supplement",exposure_type="current_epoch_evaluation",development_exposed=True,prior_design=False,future_fresh_eligible=False,closure_tokens=["doi:"+c["source_DOI"],"doi:"+c["source_SI_DOI"]],assessment_pointer=dict(path=str(O/"A6/source_scientific_assessment.json"),sha256=sha(O/"A6/source_scientific_assessment.json")))
 put(O/"A6/scientific_reconciliation_completed.json",finish);exports.append(finish)
 assert len(exports)==5
 write(T,str(O/"scientific_exposure_reads.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in exports))
 outputs=[p.relative_to(ROOT) for p in (ROOT/O/"A6").glob("*.json")]+[O/"A6/all523_metabolite_annotation_rows.jsonl",O/"scientific_exposure_reads.jsonl"]
 inputs=[cp,G5,raw,Path("scripts/task016_p7_r56_A6.py")]+[O/role/name for role in ("A4","A5") for name in ["all_original_stored_cells.json","role_manifest.json"]]
 m=role_manifest("A6","SS-E02",inputs,outputs,dict(processed=1,passed=0,rejected=0,pending=1),pointers=assessment["evidence"],read_holdout=True,read_model_outcome=False)
 m.update(count_unit="one already-read source supplemental review;523 annotation rows are not reactions",fresh_admitted=0,independent_graph_transcriptions=0,source_saturation=False,unprocessed_named_worksheets=[],scientific_qualification_pending=True)
 put(O/"A6/role_manifest.json",m)
 g6=G5.parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
 paths=inputs+outputs+[O/"A6/role_manifest.json"]
 freeze_stage_manifest(ROOT/g6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",paths,G5,expected_previous_sha=sha(G5),family="SS",epoch_id="SS-E02")
 verify_stage_chain(ROOT/g6,sha(g6))
 row=dict(task=T,epoch_id="SS-E02",family="SS",stage="G6_IDENTITY_STRUCTURE_ADMIT",status="active",at=now(),event_type="R56_official_tabular_SI_reconciled_source_deferred",stage_manifest_path=str(g6),stage_manifest_sha256=sha(g6),scope_manifest_path=str(B/"SS/E02/scope_manifest.json"),scope_manifest_sha256=sha(B/"SS/E02/scope_manifest.json"),source_count=1,new_source_independent_groups=0,fresh_admitted=0,complete_reaction_graphs=0,worksheet_count=14,stored_cells=4994,metabolite_annotation_rows=523,approval_type="agent_delegated",human_reviewed=False)
 ledger=B/"epoch_ledger.jsonl";write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
 print(json.dumps(dict(G6_SHA=sha(g6),worksheets=14,cells=4994,annotation_rows=523,numeric_zeros=43,explicit_blanks=269,external_formulas=15,source_deferred=1,fresh_admitted=0)))
if __name__=="__main__":main()
