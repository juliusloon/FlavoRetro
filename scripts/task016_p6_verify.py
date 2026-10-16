"""Independent final P6 audit; does not launch science or alter frozen inputs."""
import collections
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
from scripts.task016_p6_c_scope import construct_scope
from scripts.task016_p6_c_probe import probe_frozen
from scripts.task016_p6_regression import verify
from flavoretro.glycoside_scope import runtime_complete,apply_c_scope
from flavoretro.glycoside_library_v6 import load_registry
from flavoretro.reviewed_resources import canonical_side,load_review

def main():
    checks=[]
    def check(name,value,details=None):
        checks.append(dict(name=name,passed=bool(value),details=details))
    protected=load("protected_hashes.json")
    drift=[p for p,h in protected.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    check("protected_historical_files",not drift,dict(files=len(protected),drift=drift))
    cm=load("c_scope_manifest.json");cp=load("c_panel_manifest.json");sp=load("ss_panel_manifest.json")
    check("c_scope_manifest",all(sha(OUT/n)==h for n,h in cm["files_sha256"].items()))
    check("c_panel_manifest",sha(OUT/"c_heldout_references.jsonl")==cp["reference_sha256"])
    check("ss_panel_manifest",sha(OUT/"ss_heldout_references.jsonl")==sp["references_sha256"])
    supports=rows(OUT/"c_build_supports.jsonl");template=load("c_scope_template.json")
    exact,scope,_=construct_scope(supports[0])
    frozen_exact=rows(OUT/"c_exact_templates.jsonl")
    check("independent_exact_scope_rebuild",exact["smarts"]==template["exact_instance_template"] and scope==template["scope_template"] and all(construct_scope(r)[0]["smarts"]==f["smarts"] for r,f in zip(supports,frozen_exact)))
    check("all_build_supports",all(canonical_side(s["reference_precursors"]) in [o["precursors"] for o in apply_c_scope(template,s["target"])] for s in supports),dict(total=2))
    boundaries=load("c_scope_boundary_results.json")["controls"]
    check("scope_boundary_replay",all(not apply_c_scope(template,r["target"]) for r in boundaries),dict(total=len(boundaries)))
    probe=probe_frozen(OUT/"c_scope_template.json",OUT/"c_heldout_references.jsonl",load("c_preflight.json")["scope_hash"],cp["reference_sha256"])
    check("independent_frozen_applicability_replay",probe==rows(OUT/"c_scope_applicability.jsonl"))
    registry=load_registry()
    expected_t=rows(ROOT/"outputs/task016-p4/v1/templates.jsonl")+[template]
    expected_i=rows(ROOT/"outputs/task016-p4/v1/runtime_instances.jsonl")+supports
    encode=lambda rs:"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rs)
    check("increment_payload_byte_rebuild",encode(expected_t)==(OUT/"templates.jsonl").read_text() and encode(expected_i)==(OUT/"runtime_instances.jsonl").read_text())
    hold=rows(OUT/"c_heldout_references.jsonl")+rows(OUT/"ss_heldout_references.jsonl")
    build_signatures={r["reference_signature"] for r in registry.instances.values()}
    check("complete_runtime_panels",all(runtime_complete(r) for r in hold),dict(C=cp["gate"],SS=sp["gate"]))
    check("no_holdout_reaction_in_runtime",not ({r["canonical_reaction_signature"] for r in hold}&build_signatures))
    check("no_build_holdout_closure_leakage",not cp["gate"]["closure_leakage"] and not sp["gate"]["closure_leakage"])
    contract=load("experiment_contract.json");verify(contract)
    save("runtime_baseline_final.json",dict(experiment_contract_sha256=sha(OUT/"experiment_contract.json"),code_sha256=contract["code_sha256"],models_sha256=contract["models_sha256"],review_binding=contract["review_binding"],stock_keys=contract["stock_keys"],initial_runtime_snapshot="runtime_baseline.json",initial_fingerprint_superseded_before_first_real_matrix=True))
    check("frozen_runtime_models_stock_review",True,dict(stock_keys=len(load_review().keys)))
    obs=rows(OUT/"mcts_observations.jsonl")
    check("51_legacy_results_bound",len(obs)==51 and all(r["status"]=="ok" and sha(ROOT/r["result_path"])==r["result_sha256"] for r in obs))
    legacy=load("e_regression.json")
    check("legacy_no_new_reference_loss",not legacy["new_reference_loss"] and (legacy["old_SS_all_three_seed_created"],legacy["old_C_all_three_seed_created"],legacy["old_O_all_three_seed_created"])==(4,5,7),legacy)
    source=load("article_acquisition_manifest.json")["articles"]
    check("source_identities_and_publication_metadata",len(source)==30 and all(r["evidence_eligible"] and r["publication_metadata_check"]["passed"] for r in source))
    acquisition=rows(OUT/"acquisition_attempts.jsonl");reused=rows(OUT/"reused_files.jsonl")
    new_raw=[r for r in acquisition if r.get("path")]
    check("acquired_and_reused_raw_sha",all(sha(ROOT/r["path"])==r["sha256"] for r in new_raw+reused))
    source_cost=dict(governed_http_requests=len(acquisition),downloaded_bytes=sum(r.get("bytes",0) for r in acquisition),status_counts=dict(collections.Counter(r["status"] for r in acquisition)),request_role_counts=dict(collections.Counter(r["role"] for r in acquisition)),verified_article_versions=len(source),new_article_versions=len({r["xml"]["path"] for r in source if not r["xml"].get("reused")}),reused_article_versions=len({r["xml"]["path"] for r in source if r["xml"].get("reused")}),attachment_requests=sum(r["role"]=="jpg" for r in acquisition),reused_file_records=len(reused),web_discovery_hint_transport_not_metered=True,source_exhaustion_claimed=False)
    check("source_budget",source_cost["governed_http_requests"]<=3000 and source_cost["downloaded_bytes"]<=4*1024**3 and source_cost["verified_article_versions"]<=200 and source_cost["attachment_requests"]<=360,source_cost)
    save("source_budget_audit.json",source_cost)
    ledger=rows(OUT/"run_ledger.jsonl");starts=[r for r in ledger if r["phase"]=="started"];ends=[r for r in ledger if r["phase"]=="finished"]
    counts=collections.Counter(r["purpose"] for r in starts)
    limits=dict(p6_C_validation=81,p6_SS_validation=81,p6_legacy=51,p6_revalidation=213,p6_engineering=54)
    check("independent_budget_ledger",len(starts)<=480 and len(starts)==len(ends) and len({r["run_id"] for r in starts})==len(starts) and all(counts[k]<=v for k,v in limits.items()))
    fixtures=[r for r in ends if r["status"]=="error"]
    check("error_entries_are_explicit_service_fixtures",len(fixtures)==6 and all(r["purpose"]=="p6_engineering" and r["manifest"].startswith("/tmp/") and r["wall_seconds"]<0.1 for r in fixtures))
    budget=dict(total_reserved=len(starts),total_limit=480,by_purpose={k:dict(reserved=counts[k],limit=v) for k,v in limits.items()},actual_successful_mcts=sum(r["status"]=="ok" for r in ends),actual_mcts_failures=0,synthetic_error_fixture_reservations=len(fixtures),fixture_scope="two mocked service error/timeout cases in full local suite and each of two isolated no-asset suites",fixture_run_ids=[r["run_id"] for r in fixtures],unmatched_reservations=[],ledger_sha256=sha(OUT/"run_ledger.jsonl"))
    save("budget_audit.json",budget)
    check("scientific_cells_zero_for_stopped_axes",counts["p6_C_validation"]==counts["p6_SS_validation"]==0 and load("c_preflight.json")["stop_condition"]==6 and load("ss_preflight.json")["stop_condition"]==1)
    families={}
    for name,pre,n,groups in [("C",load("c_preflight.json"),6,4),("SS",load("ss_preflight.json"),1,1)]:
        families[name]=dict(status="NotExecuted",preflight_passed=pre["passed"],stop_condition=pre["stop_condition"],reason=pre["reason"],N=n,closure_groups=groups,ABE_cells=0,N_gap=None,G=None,G_over_N_gap=None,net_complete_reference_coverage_vs_A=None,net_complete_reference_coverage_vs_B=None,reference_loss=None,three_seed_node_transfer_targets=None,successful_transfer_closure_groups=None,metric_status="not_evaluable_preflight_stop")
    save("metrics_by_family.json",families)
    events=rows(ROOT/"operations/events.jsonl")
    test=next(e for e in reversed(events) if e.get("task")==TASK and e.get("action")=="command_end" and "unittest" in e.get("argv",[]) and "discover" in e.get("argv",[]))
    testlog=(ROOT/test["log"]).read_text();m=re.search(r"Ran (\d+) tests",testlog)
    local=dict(tests=int(m.group(1)),passed=int(m.group(1)),skipped=0,returncode=test["returncode"],log=test["log"],log_sha256=sha(ROOT/test["log"]))
    check("full_local_test_suite",local["tests"]>=177 and test["returncode"]==0 and testlog.rstrip().endswith("OK"))
    save("local_test_validation.json",local)
    free=load("asset_free_regression.json");package=load("package_validation.json")
    check("no_asset_pure_contracts",free["exit_code"]==0 and free["passed"]==147 and free["skipped"]==30,free)
    check("installed_wheel_sdist_default_off_fail_closed",package["passed"] and package["default_off_stable_fields_equal"] and package["config_copies_equal"] and package["missing_assets_fail_closed"] and all(p["created_c_scope_reference"]>0 for p in package["probes"][1:]),package)
    check("config_copy_equal",(ROOT/"configs/glycoside-library-v6.json").read_bytes()==(ROOT/"flavoretro/assets/configs/glycoside-library-v6.json").read_bytes())
    check("evidence_flags_not_promoted",all(not r.get(k,False) for r in hold+expected_i for k in ["human_reviewed","actionable","evidence_closed","prediction_conditions_verified"]))
    save("audit.json",dict(task=TASK,overall_status="Partial",engineering_passed=all(c["passed"] for c in checks),failed_checks=[c["name"] for c in checks if not c["passed"]],checks=checks,statuses=dict(p5_error_reconciliation="Completed",C_scope_implementation="Completed",C_runtime_panel="Completed",C_transfer="NotExecuted",SS_runtime_panel="Partial",SS_transfer="NotExecuted",legacy_regression="Completed",engineering_delivery="Completed"),science_metrics_are_null=True))
    print(json.dumps(dict(checks=len(checks),failed=[c["name"] for c in checks if not c["passed"]],budget=budget,source=source_cost),ensure_ascii=False))
    assert all(c["passed"] for c in checks),"final audit failed"
if __name__=="__main__":main()
