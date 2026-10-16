"""A11 independent verification of the TASK-016-P7 reaction eligibility ledger v1.

Independence rules:
  * does not import the builder script;
  * re-derives the expected per-source disposition counts directly from the upstream
    v2 disposition artifacts, not from the ledger;
  * re-derives the isoorientin name-exposure counts directly from the raw ledgers;
  * re-hashes every declared input, every evidence pointer, and the frozen G4 scopes;
  * fails closed on any mismatch.

This verifier performs no HTTP, opens no PDF, modifies no scope, and runs no MCTS.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from operate import event, write  # noqa: E402

T = "TASK-016-P7"
B = Path("outputs/task016-p7/v1")
OUT = B / "reaction_eligibility_ledger_v1"
V2 = B / "G6_owner_16_historical_source_review_v2"
PROG = B / "report_snapshots/progress-G6-new-source-v1.json"

EXPOSURE_LEDGERS = [
    B / "SS/E01_permanent_exposure/permanent_chemical_exposure_ledger.jsonl",
    B / "SS/E01_permanent_exposure/v2/permanent_chemical_exposure_ledger.jsonl",
    B / "epochs/SS-E01/closure_resolution_v1/effective_permanent_exposure_ledger.jsonl",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def rel(p) -> str:
    return str(p)


def load(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def main():
    checks = []

    def check(name, ok, detail=None):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    ledger = [json.loads(l) for l in (ROOT / OUT / "reaction_eligibility_ledger_v1.jsonl").read_text(encoding="utf-8").splitlines()]
    coverage = [json.loads(l) for l in (ROOT / OUT / "source_coverage_ledger_v1.jsonl").read_text(encoding="utf-8").splitlines()]
    summary = load(OUT / "ledger_summary_v1.json")
    inputs = load(OUT / "INPUT_MANIFEST.json")
    defects = load(OUT / "known_defects_and_discrepancies_v1.json")
    prog = load(PROG)

    # 1. input manifest integrity
    bad = [r["path"] for r in inputs["inputs"] if sha256_file(ROOT / r["path"]) != r["sha256"]]
    check("all_input_SHA256_match", not bad, bad)
    bad2 = [r["path"] for r in inputs["exposure_ledgers_read_only"]
            if sha256_file(ROOT / r["path"]) != r["sha256"]]
    check("exposure_ledger_SHA256_match", not bad2, bad2)

    # 2. frozen G4 scope untouched
    g4c = sha256_file(ROOT / B / "C/E02/stages/G4_SCOPE_FREEZE.json")
    g4s = sha256_file(ROOT / B / "SS/E02/stages/G4_SCOPE_FREEZE.json")
    check("G4_C_scope_SHA_unchanged", g4c == prog["G4_C_SHA"], {"on_disk": g4c, "snapshot": prog["G4_C_SHA"]})
    check("G4_SS_scope_SHA_unchanged", g4s == prog["G4_SS_SHA"], {"on_disk": g4s, "snapshot": prog["G4_SS_SHA"]})

    # 3. independent re-derivation of the 16 named source dispositions
    expected_rejected = expected_deferred = 0
    expected_sources = 0
    upstream_map = {}
    for fam in ("C", "SS"):
        d = load(V2 / fam / "G6_bounded_scientific_dispositions.json")
        for s in d["sources"]:
            expected_sources += 1
            up = s["disposition"]
            st = {"rejected_for_current_scope_example": "rejected", "deferred": "deferred"}[up]
            upstream_map[f"OWNER16:{fam}:{s['owner_source_number']}"] = st
            expected_rejected += st == "rejected"
            expected_deferred += st == "deferred"
    check("independent_source_count_16", expected_sources == 16, expected_sources)
    check("independent_rejected_14", expected_rejected == 14, expected_rejected)
    check("independent_deferred_2", expected_deferred == 2, expected_deferred)

    ledger_named = [r for r in ledger if r["row_kind"] == "located_example_reaction"
                    and r["source_ref"].startswith("OWNER16:")]
    mism = [
        (r["source_ref"], r["status"], upstream_map.get(r["source_ref"]))
        for r in ledger_named if upstream_map.get(r["source_ref"]) != r["status"]
    ]
    check("ledger_named_rows_match_upstream", len(ledger_named) == 16 and not mism,
          {"rows": len(ledger_named), "mismatch": mism})

    # 4. independent re-derivation of isoorientin exposure counting
    instances = 0
    keys = set()
    non_null_graph = 0
    for f in EXPOSURE_LEDGERS:
        for line in (ROOT / f).read_text(encoding="utf-8").splitlines():
            if "isoorientin" not in line.lower():
                continue
            instances += 1
            rec = json.loads(line)
            keys.add(hashlib.sha256(json.dumps(
                {k: rec.get(k) for k in ("assay_id", "closure_tokens", "record_type",
                                         "acceptor_source_name", "donor_source_name")},
                sort_keys=True).encode()).hexdigest())
            for gf in ("acceptor_smiles", "donor_smiles", "product_smiles", "target_graph",
                       "site", "reaction_signature", "reaction_id"):
                if rec.get(gf) is not None:
                    non_null_graph += 1
    check("isoorientin_instances_36", instances == 36, instances)
    check("isoorientin_distinct_12", len(keys) == 12, len(keys))
    check("isoorientin_no_structural_graph_fields", non_null_graph == 0, non_null_graph)

    name_rows = [r for r in ledger if r["row_kind"] == "name_exposure_boundary"]
    check("name_exposure_row_present_exactly_once", len(name_rows) == 1, len(name_rows))
    if name_rows:
        a = name_rows[0]["audit"]
        check("ledger_isoorientin_counts_selfconsistent",
              a["row_instances_total"] == instances and a["distinct_records"] == len(keys),
              {"ledger": a["row_instances_total"], "verified": instances})
        check("name_exposure_status_deferred", name_rows[0]["status"] == "deferred",
              name_rows[0]["status"])

    # 5. no promotion invariants
    check("admitted_total_zero", summary["admitted_total"] == 0, summary["admitted_total"])
    check("fresh_C_zero", summary["fresh_C"] == 0)
    check("fresh_SS_zero", summary["fresh_SS"] == 0)
    check("metrics_null", summary["metrics"] is None)
    check("scientific_ABE_cells_zero", summary["scientific_ABE_cells"] == 0)
    check("no_row_runtime_complete", all(not r["runtime_complete"] for r in ledger))
    check("no_row_article_level_exclusion", all(not r["article_level_exclusion_claimed"] for r in ledger))
    check("all_rows_fresh_ineligible",
          all(not r["fresh_eligible"] for r in ledger),
          [r["row_id"] for r in ledger if r["fresh_eligible"]])
    check("no_row_new_chemistry_judgement", all(not r["new_chemistry_judgement"] for r in ledger))
    check("scope_not_modified", summary["scope_modified"] is False)
    check("MCTS_untouched", summary["MCTS_untouched"] is True)

    # 6. every source has an explicit residual not_yet_assessed row
    res = {r["source_ref"] for r in ledger if r["row_kind"] == "article_residual_unassessed"}
    cov_refs = {c["source_ref"] for c in coverage}
    check("coverage_17_sources", len(coverage) == 17, len(coverage))
    check("every_source_has_residual_marker", cov_refs <= res, sorted(cov_refs - res))
    check("residual_rows_are_not_yet_assessed",
          all(r["status"] == "not_yet_assessed"
              for r in ledger if r["row_kind"] == "article_residual_unassessed"))
    check("no_article_universe_claimed_exhausted",
          not summary["article_reaction_universe_exhausted_any"])

    # 7. every evidence pointer resolves and matches
    ptr_bad = []
    for r in ledger:
        for p in r.get("evidence_pointers", []):
            fp = ROOT / p["path"]
            if not fp.exists() or sha256_file(fp) != p["sha256"]:
                ptr_bad.append((r["row_id"], p["path"]))
    check("all_evidence_pointers_resolve", not ptr_bad, ptr_bad[:10])

    # 8. source coverage row dispositions consistent with the ledger
    cov_bad = []
    for c in coverage:
        if c["source_ref"].startswith("OWNER16:"):
            lr = [r for r in ledger if r["source_ref"] == c["source_ref"]
                  and r["row_kind"] == "located_example_reaction"]
            if len(lr) != 1 or lr[0]["status"] not in c["located_reaction_status_counts"]:
                cov_bad.append(c["source_ref"])
    check("coverage_matches_ledger_rows", not cov_bad, cov_bad)

    # 9. defects recorded without touching prior artifacts
    check("defects_recorded_3", len(defects["defects"]) == 3, len(defects["defects"]))
    check("prior_artifacts_not_modified",
          defects["prior_artifacts_modified"] is False,
          )
    for d in defects["defects"]:
        check(f"prior_artifact_{d['defect_id']}_sha_still_matches",
              sha256_file(ROOT / d["artifact"]) == d["artifact_sha256"])

    # 10. physical budget unchanged (no new HTTP this round)
    check("no_new_HTTP",
          summary["physical_HTTP_total_unchanged"] == prog["HTTP_total"],
          {"ledger": summary["physical_HTTP_total_unchanged"], "snapshot": prog["HTTP_total"]})
    check("no_new_bytes",
          summary["physical_source_bytes_total_unchanged"] == prog["physical_source_bytes_total"])

    failed = [c for c in checks if not c["ok"]]
    out = {
        "task": T,
        "audit": "A11_independent_reaction_eligibility_ledger_v1",
        "agent_role": "A11",
        "human_reviewed": False,
        "at": datetime.now(timezone.utc).isoformat(),
        "ledger_sha256": sha256_file(ROOT / OUT / "reaction_eligibility_ledger_v1.jsonl"),
        "coverage_sha256": sha256_file(ROOT / OUT / "source_coverage_ledger_v1.jsonl"),
        "summary_sha256": sha256_file(ROOT / OUT / "ledger_summary_v1.json"),
        "checks_total": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "checks": checks,
        "independent_rederivations": {
            "named_sources": expected_sources,
            "rejected": expected_rejected,
            "deferred": expected_deferred,
            "isoorientin_row_instances": instances,
            "isoorientin_distinct_records": len(keys),
        },
        "no_new_HTTP": True,
        "no_new_source_read": True,
        "scope_modified": False,
        "MCTS_ran": False,
        "fresh_C": 0,
        "fresh_SS": 0,
        "metrics": None,
    }
    target = ROOT / OUT / "A11_independent_ledger_verification_v1.json"
    if target.exists():
        # immutable: re-runs compare against the frozen record instead of rewriting it
        stored = load(OUT / "A11_independent_ledger_verification_v1.json")
        same = (
            stored["passed"] == out["passed"]
            and stored["failed"] == out["failed"]
            and stored["ledger_sha256"] == out["ledger_sha256"]
            and stored["coverage_sha256"] == out["coverage_sha256"]
            and stored["summary_sha256"] == out["summary_sha256"]
        )
        event(T, "reaction_ledger_A11_recheck", passed=out["passed"],
              failed=out["failed"], matches_frozen_record=bool(same))
        print(json.dumps({"mode": "recheck", "matches_frozen_record": bool(same),
                          "passed": out["passed"], "failed": out["failed"],
                          "failed_checks": [c["check"] for c in failed]},
                         ensure_ascii=False, indent=1))
        raise SystemExit(0 if (same and not failed) else 1)
    write(T, str(OUT / "A11_independent_ledger_verification_v1.json"),
          json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    event(T, "reaction_ledger_A11_verify", passed=out["passed"], failed=out["failed"])
    print(json.dumps({"passed": out["passed"], "failed": out["failed"],
                      "failed_checks": [c["check"] for c in failed]}, ensure_ascii=False, indent=1))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
