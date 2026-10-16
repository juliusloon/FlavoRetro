"""Immutable G5 per-round raw intake; fork batches from the same immutable G4."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import save_json,sha_file,freeze_stage_manifest,verify_stage_chain,now
OUT=ROOT/"outputs/task016-p7/v1/C/E01"
def freeze_round(number):
 src=OUT/f"fresh/R{number}";dest=OUT/f"stages/batches/R{number}";snapshot=dest/"intake_snapshot";files=[];pointers={}
 for name in ("query_plan.json","query_execution.jsonl","query_audit.json","source_dispositions.jsonl","identifier_resolution_plan.json","identifier_resolution_results.json","article_plan.json","article_acquisition.json","article_intake_summary.json","unresolved_id_hints.json"):
  p=src/name
  if not p.exists():raise RuntimeError("unterminated intake: "+name)
  to=snapshot/name
  if to.exists():raise RuntimeError("G5 batch snapshot already written")
  write("TASK-016-P7",str(to.relative_to(ROOT)),p.read_text());files.append(to)
 def collect(value):
  if isinstance(value,list):
   for x in value:collect(x)
  elif isinstance(value,dict):
   if value.get("path") and value.get("sha256") and str(value["path"]).startswith("data/raw/"):
    path=ROOT/value["path"]
    if not path.is_file() or sha_file(path)!=value["sha256"]:raise RuntimeError("raw intake pointer drift")
    pointers[value["path"]]=value["sha256"]
   for x in value.values():collect(x)
 for p in files:
  obj=json.loads(p.read_text()) if p.suffix==".json" else [json.loads(x) for x in p.read_text().splitlines() if x.strip()];collect(obj)
 files.extend(ROOT/name for name in pointers)
 intake=dict(task="TASK-016-P7",family="C",epoch_id="C-E01",batch_id=f"C-R{number}",frozen_at=now(),scope_manifest_sha256=sha_file(OUT/"scope_manifest.json"),files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in files},snapshot_of_live_intake_files=True,original_live_files_may_receive_later_terminal_disposition=True,chemical_extraction_started=False,raw_only=True,human_reviewed=False)
 save_json(dest/"raw_intake_manifest.json",intake,immutable=True);files.append(dest/"raw_intake_manifest.json")
 previous=OUT/"stages/G4_SCOPE_FREEZE.json";freeze_stage_manifest(dest,"G5_FRESH_HOLDOUT_ACQUIRE",files,previous,expected_previous_sha=sha_file(previous),family="C",epoch_id="C-E01")
 stage=dest/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(stage,sha_file(stage))
 # Common raw-only source inputs precede both independent extractors; no final graph is included.
 acquisition=json.loads((snapshot/"article_acquisition.json").read_text())
 manifest=dict(task="TASK-016-P7",family="C",epoch_id="C-E01",batch_id=f"C-R{number}",created_at=now(),contains_final_graphs=False,scope_manifest_sha256=sha_file(OUT/"scope_manifest.json"),G5_pointer=dict(path=str(stage.relative_to(ROOT)),sha256=sha_file(stage)),sources=[dict(pmcid=r["pmcid"],metadata_pointer={k:r["metadata"][k] for k in ("path","sha256")},xml_pointer={k:r["xml"][k] for k in ("path","sha256")} if r.get("xml") else None,license=r["license"],media_urls=r["media_urls"],reaction_ids="not assigned; source chemistry uninspected",site_convention="source numbered site and sugar anomeric C1; unknown must stay unknown",source_identity_verified=False,evidence_eligible=False) for r in acquisition],read_model_outcome=False,human_reviewed=False)
 save_json(dest/"fresh_source_input_manifest.json",manifest,immutable=True)
 print(json.dumps(dict(G5_path=str(stage.relative_to(ROOT)),G5_sha256=sha_file(stage),input_manifest_path=str((dest/"fresh_source_input_manifest.json").relative_to(ROOT)),input_manifest_sha256=sha_file(dest/"fresh_source_input_manifest.json"),sources=len(acquisition),raw_objects=len(pointers))))
if __name__=="__main__":freeze_round(int(sys.argv[1]))
