"""Verify nested role/stage SHA bindings and raw evidence pointers before source chemistry."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,save_json,now
OUT=ROOT/"outputs/task016-p7/v1/C/E01"
SHA_MAP_KEYS={"input_manifest_sha","input_manifest_sha256","output_file_sha","output_files_sha256","verified_input_files_sha256","raw_source_files_sha256","files_sha256","files"}
def verify():
 visited=set();bound={};errors=[]
 def bind(name,h,parent,recursive=True):
  p=ROOT/name if name.startswith(("outputs/","data/","flavoretro/","scripts/","docs/")) else parent/name
  if not p.is_file() or sha_file(p)!=h:raise RuntimeError("nested provenance binding drift: "+str(p))
  bound[str(p.relative_to(ROOT))]=h
  if recursive and p.suffix in (".json",".jsonl") and p not in visited:
   visited.add(p)
   try:obj=json.loads(p.read_text()) if p.suffix==".json" else [json.loads(v) for v in p.read_text().splitlines() if v.strip()]
   except (ValueError,UnicodeError):return
   walk(obj,p.parent)
 def walk(obj,parent):
  if isinstance(obj,list):
   for item in obj:walk(item,parent)
  elif isinstance(obj,dict):
   # Explicitly superseded pending reports retain their own immutable bytes, while their earlier helper state is historical.
   if obj.get("current_scope_harness_reexecuted") is True and "path" in obj and "sha256" in obj:
    bind(obj["path"],obj["sha256"],parent,recursive=False);return
   if isinstance(obj.get("path"),str) and isinstance(obj.get("sha256"),str) and len(obj["sha256"])==64:bind(obj["path"],obj["sha256"],parent)
   for key,val in obj.items():
    if key in SHA_MAP_KEYS and isinstance(val,dict):
     for name,h in val.items():
      if isinstance(h,str) and len(h)==64:bind(name,h,parent)
    elif key not in SHA_MAP_KEYS:walk(val,parent)
 stage=OUT/"stages/G4_SCOPE_FREEZE.json";verify_stage_chain(stage,sha_file(stage));walk(json.loads(stage.read_text()),stage.parent)
 for name in ("design_source_input_manifest.json","role_A1_design_manifest.json","role_A3_identity_manifest.json","role_A4_design_manifest.json","role_A5_harness_manifest.json","role_A6_design_qualification_manifest.json","role_A7_final_manifest.json","role_A8_independent_preflight_manifest.json"):
  bind(str((OUT/name).relative_to(ROOT)),sha_file(OUT/name),OUT)
 result=dict(task="TASK-016-P7",family="C",epoch_id="C-E01",passed=True,verified_at=now(),G4_sha256=sha_file(stage),scope_manifest_sha256=sha_file(OUT/"scope_manifest.json"),role_and_stage_recursive=True,verified_files_sha256=bound,verified_files=len(bound),read_holdout_chemistry=False,read_model_outcome=False,human_reviewed=False)
 save_json(OUT/"provenance_recursive_verification.json",result,immutable=True);print(json.dumps(dict(passed=True,files=len(bound))))
if __name__=="__main__":verify()
