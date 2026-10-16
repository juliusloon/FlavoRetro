"""Independent local SS asset/accounting audit; never runs MCTS or changes scope."""
import json,sys
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,rows,sha,save,now
from flavoretro.glycoside_scope_ss_v7 import apply_template
from flavoretro.reviewed_resources import canonical_side
def verify():
    checks=[]
    raw_input=json.loads((OUT/"design_source_input_manifest.json").read_text())
    checks.append(dict(name="raw_source_input_SHA",passed=all(sha(ROOT/p)==h for p,h in raw_input["raw_input_files_sha256"].items())))
    templates=rows(OUT/"templates.jsonl") if (OUT/"scope_freeze.json").exists() else rows(OUT/"scope_templates_proposed.jsonl")
    supports=rows(OUT/"runtime_instances.jsonl") if (OUT/"scope_freeze.json").exists() else rows(OUT/"design_extractor_A4.jsonl")
    plan=json.loads((OUT/"scope_boundary_plan.json").read_text());plan_sha=sha(OUT/"scope_boundary_plan.json")
    results=json.loads((OUT/"scope_boundaries.json").read_text())
    replays=json.loads((OUT/"scope_build_replay.json").read_text())
    byid={t["template_id"]:t for t in templates}
    checks.append(dict(name="each_scope_two_distinct_canonical_acceptors",passed=all(len({canonical_side([r["acceptor"]]) for r in supports if r["instance_id"] in t["support_instances"]})>=2 for t in templates)))
    replay_checks=[canonical_side(r["reference_precursors"]) in [o["precursors"] for o in apply_template(t,r["target"])] for t in templates for r in supports if r["instance_id"] in t["support_instances"]]
    checks.append(dict(name="production_guard_all_build_support_replay",passed=all(replay_checks),observed=sum(replay_checks),total=len(replay_checks)))
    checks.append(dict(name="minimum_six_preregistered_controls_per_scope",passed=all(sum(c["scope_id"]==t["template_id"] for c in plan["controls"])>=6 for t in templates)))
    violated=[c for c in plan["controls"] if apply_template(byid[c["scope_id"]],c["target"])]
    checks.append(dict(name="boundary_recompute_zero_violations",passed=len(violated)==0,total=len(plan["controls"]),violations=len(violated)))
    checks.append(dict(name="all_boundary_results_bind_prior_plan_SHA_and_time",passed=all(r["boundary_plan_sha256"]==plan_sha and datetime.fromisoformat(r["executed_at"])>=datetime.fromisoformat(plan["registered_at"]) for r in results["records"]+replays["records"])))
    checks.append(dict(name="flavanone_source_C2_inversion_control_registered",passed=any(c["control"]=="wrong_flavanone_C2_stereo" for c in plan["controls"])))
    http=[];query_counts=[]
    for ledger in OUT.rglob("http_ledger.jsonl"):
        if "superseded" in ledger.parts:continue
        requests=rows(ledger);plans=rows(ledger.parent/"query_plan.jsonl");executed=rows(ledger.parent/"query_execution.jsonl")
        query_counts.append(len(requests)==len(plans)==len(executed))
        http.extend(requests)
    checks.append(dict(name="HTTP_query_plan_execution_conservation",passed=all(query_counts)))
    checks.append(dict(name="raw_byte_count_and_SHA",passed=all((ROOT/r["path"]).stat().st_size==r["bytes"] and sha(ROOT/r["path"])==r["sha256"] for r in http)))
    checks.append(dict(name="HTTP_namespace_query_keys_unique",passed=len({(r["ledger_namespace"],r["query_id"]) for r in http})==len(http)))
    budget=dict(http_requests=len(http),downloaded_bytes=sum(r["bytes"] for r in http),article_versions=sum(r["role"] in {"xml","original_pdf"} for r in http),attachments=sum(r["role"]=="attachment" for r in http))
    checks.append(dict(name="SS_source_hard_budget",passed=budget["http_requests"]<=2500 and budget["downloaded_bytes"]<=2*1024**3 and budget["article_versions"]<=120 and budget["attachments"]<=200))
    if (OUT/"scope_freeze.json").exists():
        f=json.loads((OUT/"scope_freeze.json").read_text())
        checks.append(dict(name="scope_freeze_file_SHA",passed=all(sha(ROOT/p if p.startswith(("outputs/","flavoretro/")) else OUT/p)==h for p,h in f["files_sha256"].items())))
        checks.append(dict(name="independent_qualification_required",passed=f["independently_verified"] is True))
    value=dict(task_id="TASK-016-P7",epoch_id="SS-E01",agent_role="A8 local replay harness; external identity and A5 remain required",at=now(),read_holdout=False,read_model_outcomes=False,scope_scientifically_frozen=(OUT/"scope_freeze.json").exists(),checks=checks,failed=sum(not c["passed"] for c in checks),budget=budget,independent_chemistry=False,human_reviewed=False)
    save("SS_local_asset_verification.json",value);print(json.dumps(value,ensure_ascii=False,indent=1))
    if value["failed"]:raise RuntimeError("SS_LOCAL_ASSET_AUDIT_FAILED")
if __name__=="__main__":verify()
