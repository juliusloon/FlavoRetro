"""R56 isolated spreadsheet read receipts; no admission or graph guessing."""
import json,uuid,os
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now
from scripts.task016_p7_orchestrate import verify_hashes,verify_stage_chain,role_manifest
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"SS/E02/fresh/SS-E02-R56-Laportea-tabular-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R56-Laportea-tabular-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
def pre_read(role):
 assert role in ("A4","A5") and not (ROOT/O/role).exists()
 c=load(O/"pre_science_exposure_contract.json");verify_hashes(c["input_manifest_sha"])
 m=verify_stage_chain(ROOT/G5,sha(G5));assert m["files"][str(O/"pre_science_exposure_contract.json")]==sha(O/"pre_science_exposure_contract.json")
 raw=Path(c["raw_XLSX"]["path"]);assert sha(raw)==c["raw_XLSX"]["sha256"]
 reader=role+"-"+str(os.getpid())+"-"+uuid.uuid4().hex
 row=dict(task=T,epoch_id="SS-E02",family="SS",batch_id=O.name,source_id=c["source_DOI"],reader_role=role,reader_id=reader,event_type="scientific_read_started",timestamp=now(),G5=dict(path=str(G5),sha256=sha(G5)),raw_files=[c["raw_XLSX"]],scientific_content_read=False,read_other_extractor_output=False,exposure_type="current_epoch_supplemental_evaluation",development_exposed=True,current_epoch_fresh_eligibility="unresolved_inherited_source_qualification_not_granted",future_fresh_eligible=False,prior_source_science_exists=True,approval_type="agent_delegated",human_reviewed=False)
 put(O/role/"scientific_read_started.json",row)
 return c,raw,row
def complete(role,start,records,parser):
 out=O/role/"all_original_stored_cells.json"
 put(out,dict(task=T,source_DOI=start["source_id"],parser=parser,worksheets=records,all_stored_cells_preserved=True,absent_cells_not_invented=True,formulas_not_evaluated=True,independent_graph_transcription=False,source_reaction_qualified=False,scope_applicability=None))
 finish=dict(start,event_type="scientific_read_completed",timestamp=now(),scientific_content_read=True,bytes_opened=load(O/"pre_science_exposure_contract.json")["raw_XLSX"]["bytes"],status="completed",output_pointer=dict(path=str(out),sha256=sha(out)))
 put(O/role/"scientific_read_completed.json",finish)
 c=load(O/"pre_science_exposure_contract.json")
 inputs=[O/"pre_science_exposure_contract.json",G5,Path(c["raw_XLSX"]["path"]),Path("scripts/task016_p7_r56_read_receipts.py"),Path("scripts/task016_p7_r56_"+role+".py")]
 outputs=[out,O/role/"scientific_read_started.json",O/role/"scientific_read_completed.json"]
 m=role_manifest(role,"SS-E02",inputs,outputs,dict(processed=1,passed=1,rejected=0,pending=0),pointers=[c["raw_XLSX"]],read_holdout=True,read_model_outcome=False)
 m.update(reader_id=start["reader_id"],read_other_extractor_output=False,independent_graph_transcription=False,count_unit="one original XLSX extraction, not source/reaction admission",worksheet_count=len(records),stored_cells=sum(len(x["cells"]) for x in records),parser=parser)
 put(O/role/"role_manifest.json",m)
 print(json.dumps(dict(role=role,worksheets=len(records),stored_cells=sum(len(x["cells"]) for x in records),chemical_graphs=0,fresh_admitted=0)))
