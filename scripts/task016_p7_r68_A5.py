"""Isolated current-epoch follow-up reader for permanently historical sources."""
import json,os,hashlib
from pathlib import Path
from scripts.operate import ROOT
from scripts.task016_p7_r18_PMC_originals import put,load,sha,now
from scripts.task016_p7_orchestrate import verify_hashes,verify_stage_chain,role_manifest
from scripts.task016_p7_r47_A5 import parse
A5="A5"
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R68-two-historical-PMC-science-v1"
G5=B/"C/E02/stages/batches/C-E02-R68-two-historical-PMC-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
def main():
 c=load(O/"pre_science_contract.json");verify_hashes(c["input_manifest_sha"]);verify_stage_chain(ROOT/G5,sha(G5))
 rid="R68-"+A5+"-"+str(os.getpid())
 for source in c["sources"]:
  sid=source["pmcid"];raw=source["original_raw"];dest=O/A5/sid
  assert not (ROOT/dest).exists()
  common=dict(task=T,approval_type="agent_delegated",human_reviewed=False,family="C",epoch_id="C-E02",reader_role=A5,reader_id=rid,source_id=sid,DOI=source["DOI"],raw_files=[raw],G5=dict(path=str(G5),sha256=sha(G5)),development_exposed=True,prior_design=True,exposure_type="historical_development_exposure",future_fresh_eligible=False,current_epoch_fresh_eligible=False,read_other_extractor_output=False,read_model_outcome=False)
  started=dict(common,event_type="scientific_read_started",timestamp=now(),scientific_content_read=False)
  put(dest/"scientific_read_started.json",started)
  data=(ROOT/raw["path"]).read_bytes();assert hashlib.sha256(data).hexdigest()==raw["sha256"]
  blocks=[]
  for x in parse(data):
   text=" ".join(x["text"].split());blocks.append(dict(x,text=text,text_SHA=hashlib.sha256(text.encode()).hexdigest(),source_file=raw["path"],source_SHA=raw["sha256"]))
  assert blocks
  out=dest/"original_article_text_blocks.json"
  put(out,dict(task=T,agent_role=A5,source_id=sid,blocks=blocks,all_article_text_blocks_processed=True,source_images_not_downloaded_or_transcribed=True,independent_graph_transcription=False,chemical_reaction_enumeration_complete=False,read_other_extractor_output=False,scope_modified=False,fresh_admitted=0))
  ended=dict(common,event_type="scientific_read_completed",timestamp=now(),scientific_content_read=True,output_pointer=dict(path=str(out),sha256=sha(out)),stored_text_blocks=len(blocks))
  put(dest/"scientific_read_completed.json",ended)
  manifest=role_manifest(A5,"C-E02",[O/"pre_science_contract.json",G5,Path(raw["path"]),Path(__file__).resolve().relative_to(ROOT)],[out,dest/"scientific_read_started.json",dest/"scientific_read_completed.json"],dict(processed=1,passed=0,rejected=0,pending=1),pointers=[raw],read_holdout=True,read_model_outcome=False)
  manifest.update(reader_id=rid,read_other_extractor_output=False,independent_graph_transcription=False,count_unit="one historical source text extraction, chemistry qualification not granted")
  put(dest/"role_manifest.json",manifest)
  print(json.dumps(dict(role=A5,source=sid,text_blocks=len(blocks),full_graphs=0)))
if __name__=="__main__":main()
