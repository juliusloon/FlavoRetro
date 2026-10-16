"""Independent, bounded audit of SS-E02 R5 raw-only acquisition (P7 progress-v17)."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from scripts.operate import ROOT, write
from scripts.task016_p7_orchestrate import verify_stage_chain

TASK = "TASK-016-P7"
P = Path("outputs/task016-p7/v1")
B = P / "SS/E02/fresh/SS-E02-R5-original-acquisition-v1"
OUT = P / "verification-v17-ss-r5"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def read(p):
    return json.loads((ROOT / p).read_text())


def rows(p):
    return [json.loads(s) for s in (ROOT / p).read_text().splitlines() if s.strip()]


def main():
    if (ROOT / OUT).exists():
        raise RuntimeError("IMMUTABLE_VERIFICATION_EXISTS")
    pre = read(B / "precontract.json")
    for p, expected in pre["input_sha256"].items():
        if sha(Path(p)) != expected:
            raise RuntimeError("FROZEN_INPUT_DRIFT " + p)
    ledger = rows(P / "epoch_ledger.jsonl")
    stages = [r for r in ledger if r.get("epoch_id") == "SS-E02" and r.get("status") == "active"]
    g4 = [r for r in stages if r.get("stage") == "G4_SCOPE_FREEZE"][-1]
    g5 = [r for r in stages if r.get("stage") == "G5_FRESH_HOLDOUT_ACQUIRE"][-1]
    repair = read(P / "governance/SS_E02_R5_G5_binding_repair_v1/validation.json")
    assert repair["correction"]["stage_manifest_sha256"] == g5["stage_manifest_sha256"]
    assert g5["scope_manifest_sha256"] == g4["scope_manifest_sha256"]
    assert sha(Path(g4["scope_manifest_path"])) == g4["scope_manifest_sha256"]
    assert verify_stage_chain(ROOT / g4["stage_manifest_path"],g4["stage_manifest_sha256"])["stage"] == "G4_SCOPE_FREEZE"
    assert verify_stage_chain(ROOT / g5["stage_manifest_path"],g5["stage_manifest_sha256"])["stage"] == "G5_FRESH_HOLDOUT_ACQUIRE"
    lo_plan = read(B / "locator_query_plan.json")["queries"]
    or_plan = read(B / "original_query_plan.json")["queries"]
    lo = rows(B / "locator_query_execution.jsonl")
    orig = rows(B / "original_query_execution.jsonl")
    reqs = rows(B / "http_ledger.jsonl")
    rawmanifest = read(B / "raw_only_intake_manifest.json")
    totals = rawmanifest["counts"]
    assert len(lo_plan) == len(lo) == 9
    assert len(or_plan) == len(orig) == 9
    assert {x["query_id"] for x in lo_plan} == {x["query_id"] for x in lo}
    assert {x["query_id"] for x in or_plan} == {x["query_id"] for x in orig}
    assert len(reqs) == 18 == totals["HTTP"]
    assert len({r["attempt_id"] for r in reqs}) == len(reqs)
    assert all(r["phase"] == "fresh" and r["epoch_id"] == "SS-E02" for r in reqs)
    assert all(not r.get("scientific_body_content_read") and not r.get("chemical_extracted") and not r.get("evidence_eligible") and not r.get("fresh_eligible") for r in reqs)
    assert sum(x["physical_HTTP_added"] for x in lo + orig) == len(reqs)
    total_bytes = 0
    for x in reqs:
        path = Path(x["path"])
        assert sha(path) == x["sha256"]
        assert (ROOT / path).stat().st_size == x["bytes"]
        total_bytes += x["bytes"]
    assert total_bytes == totals["bytes"]
    assert totals["fixed_input_clusters"] == 39 and totals["selected_sources"] == 6
    assert totals["sources_with_valid_original_raw"] == 2
    assert totals["valid_original_raw_objects"] == 4
    assert totals["opaque_SI_objects"] == 1 and totals["XML_front_checks"] == 2
    assert totals["new_G5_G6_frozen"] == totals["fresh_admitted"] == totals["reaction_qualified"] == totals["new_MCTS"] == 0
    assert len(rawmanifest["sources"]) == 6
    assert all(s["fresh_admitted"] is False and s["reaction_qualified"] is False and s["scientific_body_figures_read"] is False for s in rawmanifest["sources"])
    audit = read(B / "HTTP_budget_audit.json")
    assert audit["raw_byte_SHA_manifest_match"] and audit["physical_attempts_dedup_matches_batch"]
    assert audit["budget_respected"]
    assert audit["this_batch"]["HTTP"] == 18 and audit["this_batch"]["bytes"] == total_bytes
    checks = {"precontract_all_SHA_bound":True,"G4_G5_scope_and_chain_intact":True,
        "query_locator_9of9":True,"query_original_9of9":True,
        "raw_SHA_size_18of18":True,"actual_request_bytes_conserve":True,
        "scientific_qualification_stays_zero":True,"no_scientific_content_read":True,
        "physical_budget_respected":True,"original_error_command_4480_not_erased":(ROOT/"operations/command-4480.log").exists()}
    result = {
      "task":TASK, "timestamp":datetime.now(timezone.utc).isoformat(),
      "audit_scope":"R5 raw-only official original/SI acquisition and preregistered SHA/ledger consistency; not source/scientific review",
      "checks":checks,"passed":sum(checks.values()),"failed":len(checks)-sum(checks.values()),
      "counts":{"HTTP":len(reqs),"bytes":total_bytes,"locator_planned":9,"locator_terminal":9,
        "original_planned":9,"original_terminal":9,"sources_selected":6,
        "sources_with_valid_original_raw":2,"raw_valid_original_objects":4,
        "opaque_SI":1,"fresh":0,"new_scientific_ABE":0},
      "latest_physical_budget_snapshot":audit["after"],
      "scope_G4_SHA":g4["stage_manifest_sha256"],"scope_content_SHA":g4["scope_manifest_sha256"],
      "G5_SHA":g5["stage_manifest_sha256"],
      "frozen_input_SHA":pre["input_sha256"],
      "raw_role_manifest_SHA":sha(B/"role_A2_raw_only_manifest.json"),
      "limitations":["2 sources with container-valid original bytes is not independent original article/reaction verification",
        "HTML/redirects and source review remain pending","R5 raw-only acquisition does not grant G5 science extraction permission",
        "source alias/name identity and historical exposure remain unclosed","C and SS final fresh holdouts both 0; A/B/E 0 cells; P2 incomplete"],
      "formal_task_completed":False,"approval":"agent_delegated", "human_reviewed":False
    }
    write(TASK,str(OUT/"independent_R5_verification.json"),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"passed":result["passed"],"failed":result["failed"],"HTTP":len(reqs),
      "bytes":total_bytes,"fresh":0,"task_completed":False},ensure_ascii=False))


if __name__ == "__main__":
    main()
