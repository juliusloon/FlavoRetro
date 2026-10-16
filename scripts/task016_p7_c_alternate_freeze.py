"""Freeze a specific alternative-source acquisition without binding appendable ledgers."""
import sys,json
from pathlib import Path
from scripts.task016_p7_orchestrate import save_json,sha_file,freeze_stage_manifest,verify_stage_chain,now
ROOT=Path.cwd();BASE=ROOT/"outputs/task016-p7/v1/C/E01"
def freeze(label,names,doi,pmid=None):
 folder=BASE/"stages/batches"/label;alt=BASE/"fresh/alternate";files=[alt/n for n in names];raw={};objects=[]
 def collect(v):
  if isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   if v.get("path") and v.get("sha256") and str(v["path"]).startswith("data/raw/"):
    p=ROOT/v["path"]
    if sha_file(p)!=v["sha256"]:raise RuntimeError("raw drift")
    raw[v["path"]]=v["sha256"]
   if v.get("attempt_id") and v.get("url") and v.get("path"):objects.append(v)
   for x in v.values():collect(x)
 for p in files:collect(json.loads(p.read_text()))
 files.extend(ROOT/p for p in raw);previous=BASE/"stages/G4_SCOPE_FREEZE.json"
 intake=folder/"fresh_source_input_manifest.json"
 save_json(intake,dict(task="TASK-016-P7",epoch_id="C-E01",family="C",batch_id=label,created_at=now(),contains_final_graphs=False,doi=doi,pmid=pmid,objects=objects,raw_pointers=raw,site_convention="source numbered ring carbon; sugar anomeric C1; unknown stays unknown",reaction_ids="source reaction records not assigned",source_identity_verified=False,evidence_eligible=False,fresh_admission_paused=True,scope_built_or_modified=False,human_reviewed=False),immutable=True)
 files.append(intake);freeze_stage_manifest(folder,"G5_FRESH_HOLDOUT_ACQUIRE",files,previous,expected_previous_sha=sha_file(previous),family="C",epoch_id="C-E01")
 stage=folder/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(stage,sha_file(stage));print(json.dumps(dict(G5_path=str(stage.relative_to(ROOT)),G5_SHA=sha_file(stage),input_path=str(intake.relative_to(ROOT)),input_SHA=sha_file(intake),raw_objects=len(raw))))
if __name__=="__main__":
 if sys.argv[1]=="chrysin":freeze("CHRYSIN_PUBLIC_SI",["springer_chrysin_primary_plan.json","springer_chrysin_primary_result.json","springer_chrysin_attachment_plan.json","springer_chrysin_attachment_result.json","springer_chrysin_SI_retry2_plan.json","springer_chrysin_SI_retry2_result.json"],"10.1007/s00253-017-8694-6","29308528")
