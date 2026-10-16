"""P7 C formal boundary universe: preregister immutable plan, then execute."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import save_json,sha_file,sha_json
from scripts.task016_p7_c_scope import mutate_controls
from scripts.task016_p7_scope_harness import replay_scope_bank,validate_scope_bank
from flavoretro.glycoside_library_v7 import apply_template
TASK="TASK-016-P7";OUT=ROOT/"outputs/task016-p7/v1/C/E01"
def rows(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def preregister():
 if (OUT/"boundary_plan.json").exists():raise RuntimeError("boundary universe immutable")
 rr=[r for r in rows(OUT/"design_candidates.jsonl") if r["center_class"]!="benzophenone_3_C_glucoside"]
 bank=[t for t in rows(OUT/"scope_proposals.jsonl") if t["scope"]["center_class"]!="benzophenone_3_C_glucoside"]
 for t in bank:t["scope"]["family"]="C"
 save_json(OUT/"formal_scope_candidates.json",bank,immutable=True)
 save_json(OUT/"formal_build_candidates.json",rr,immutable=True)
 controls=[]
 for t in bank:
  support=next(r for r in rr if r["center_class"]==t["scope"]["center_class"])
  for name,target in mutate_controls(support,t):
   controls.append(dict(template_id=t["template_id"],control_id=t["template_id"]+":"+name,control=name,target=target,expected="refused",fixture_only=True,source_build_instance_id=support["instance_id"]))
 plan=dict(task=TASK,family="C",epoch_id="C-E01",preregistered_at=datetime.now(timezone.utc).isoformat(),read_holdout=False,read_model_outcome=False,control_count=len(controls),controls=controls,files_sha256={"formal_scope_candidates.json":sha_file(OUT/"formal_scope_candidates.json"),"formal_build_candidates.json":sha_file(OUT/"formal_build_candidates.json")},production_guard_sha256=sha_file(ROOT/"flavoretro/glycoside_scope_c_v7.py"),pre_freeze_design_probes_already_observed=True,formal_boundary_results_executed_after_this_plan=True,human_reviewed=False)
 save_json(OUT/"boundary_plan.json",plan,immutable=True)
 print(json.dumps(dict(boundary_plan_sha256=sha_file(OUT/"boundary_plan.json"),controls=len(controls),scopes=len(bank))))
def execute():
 plan=json.loads((OUT/"boundary_plan.json").read_text())
 for name,h in plan["files_sha256"].items():
  if sha_file(OUT/name)!=h:raise RuntimeError("immutable boundary input drift")
 if sha_file(ROOT/"flavoretro/glycoside_scope_c_v7.py")!=plan["production_guard_sha256"]:raise RuntimeError("production guard changed")
 bank=json.loads((OUT/"formal_scope_candidates.json").read_text());rr=json.loads((OUT/"formal_build_candidates.json").read_text())
 replay=replay_scope_bank(bank,rr);boundaries=[]
 for c in plan["controls"]:
  t=next(t for t in bank if t["template_id"]==c["template_id"]);out=apply_template(t,c["target"])
  boundaries.append(dict(c,violated=bool(out),outcomes=out,boundary_plan_sha256=sha_file(OUT/"boundary_plan.json")))
 check=validate_scope_bank(bank,rr,replay,boundaries)
 save_json(OUT/"formal_build_replay.json",replay,immutable=True);save_json(OUT/"formal_boundary_results.json",boundaries,immutable=True)
 save_json(OUT/"formal_scope_validation.json",dict(check,boundary_plan_sha256=sha_file(OUT/"boundary_plan.json"),production_guard_sha256=plan["production_guard_sha256"],executed_at=datetime.now(timezone.utc).isoformat()),immutable=True)
 print(json.dumps(check))
if __name__=="__main__":{"preregister":preregister,"execute":execute}[sys.argv[1]]()
