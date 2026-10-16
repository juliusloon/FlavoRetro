"""Write the progress snapshot for the reaction-level eligibility ledger round (v1)."""
from __future__ import annotations

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
SNAP = B / "report_snapshots/progress-reaction-ledger-v1.json"


def sha(p: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    s = json.loads((ROOT / OUT / "ledger_summary_v1.json").read_text(encoding="utf-8"))
    a11 = json.loads((ROOT / OUT / "A11_independent_ledger_verification_v1.json")
                     .read_text(encoding="utf-8"))
    prog = json.loads((ROOT / B / "report_snapshots/progress-G6-new-source-v1.json")
                      .read_text(encoding="utf-8"))
    items = [
        "precontract.json", "INPUT_MANIFEST.json",
        "reaction_eligibility_ledger_v1.jsonl", "source_coverage_ledger_v1.jsonl",
        "ledger_summary_v1.json", "known_defects_and_discrepancies_v1.json",
        "A11_independent_ledger_verification_v1.json", "README.md",
        "README.v1-superseded-render.md",
    ]
    snap = {
        "task": T,
        "milestone": "G6_reaction_level_eligibility_ledger_v1_offline_consolidation",
        "stage": "G6_IDENTITY_STRUCTURE_ADMIT",
        "layer": "reaction_eligibility_ledger_v1",
        "status": "In Progress",
        "at": datetime.now(timezone.utc).isoformat(),
        "authorization": "human_direct",
        "approval_note": "Owner chose option A (offline per-article per-reaction eligibility ledger) with human_direct record for this round; stage decisions agent_delegated.",
        "artifacts": {n: {"path": str(OUT / n), "sha256": sha(ROOT / OUT / n)} for n in items},
        "harnesses": {
            "builder": {"path": "scripts/task016_p7_reaction_ledger_v1.py",
                        "sha256": sha(ROOT / "scripts/task016_p7_reaction_ledger_v1.py")},
            "renderer": {"path": "scripts/task016_p7_reaction_ledger_report_v1.py",
                         "sha256": sha(ROOT / "scripts/task016_p7_reaction_ledger_report_v1.py")},
            "independent_verifier": {"path": "scripts/task016_p7_reaction_ledger_A11_v1.py",
                                     "sha256": sha(ROOT / "scripts/task016_p7_reaction_ledger_A11_v1.py")},
        },
        "denominator": s["denominator"],
        "rows_total": s["rows_total"],
        "rows_by_status": s["rows_by_status"],
        "rows_by_kind": s["rows_by_kind"],
        "admitted_total": s["admitted_total"],
        "complete_reaction_admission": s["complete_reaction_admission"],
        "fresh_C": 0,
        "fresh_SS": 0,
        "metrics": None,
        "scientific_ABE_cells": 0,
        "sources_with_residual_marker": s["sources_with_residual_marker"],
        "article_reaction_universe_exhausted_any": s["article_reaction_universe_exhausted_any"],
        "article_level_exclusion_rows": s["article_level_exclusion_rows"],
        "can_freeze_G7_panel": False,
        "G6_global_complete": False,
        "G7_panel_real": False,
        "G8_preflight_real": False,
        "new_G9_frozen": False,
        "G4_C_SHA": prog["G4_C_SHA"],
        "G4_SS_SHA": prog["G4_SS_SHA"],
        "G4_unchanged": True,
        "isoorientin_name_exposure_audit": s["isoorientin_name_exposure_audit"],
        "defects_found_in_prior_artifacts": s["defect_ids"],
        "prior_artifacts_modified": False,
        "A11_independent_verification": {
            "path": str(OUT / "A11_independent_ledger_verification_v1.json"),
            "sha256": sha(ROOT / OUT / "A11_independent_ledger_verification_v1.json"),
            "checks_total": a11["checks_total"],
            "passed": a11["passed"],
            "failed": a11["failed"],
            "independent_rederivations": a11["independent_rederivations"],
        },
        "engineering": {
            "full_unittest": {
                "command": ".venv-foundation/bin/python -B -m unittest discover -s tests",
                "count": 286, "failed": 0, "errors": 0,
                "log": "operations/command-5434.log",
                "sha256": sha(ROOT / "operations/command-5434.log"),
            },
            "git_diff_check": "clean",
            "self_reported_execution_errors": [
                {
                    "error_id": "REL-E1",
                    "what": "first full-suite invocation used system python3 instead of the project venv",
                    "result": "198 tests, 1 failure, 29 errors, 5 skipped",
                    "log": "operations/command-5433.log",
                    "sha256": sha(ROOT / "operations/command-5433.log"),
                    "diagnosis": "28x ModuleNotFoundError: aizynthfinder plus cascading test-module ImportErrors; environment/interpreter mismatch, not a code regression",
                    "action": "re-ran with the canonical interpreter; 286/286 OK; failing log preserved",
                },
                {
                    "error_id": "REL-E2",
                    "what": "first README render listed the prospective source in the C-axis table with a null owner number",
                    "result": "rendering defect only; no data row or SHA affected",
                    "action": "defective render preserved as README.v1-superseded-render.md; generator fixed; data unchanged",
                },
            ],
        },
        "no_new_http": True,
        "no_new_source_read": True,
        "raw_pdf_opened": False,
        "physical_HTTP_total_unchanged": prog["HTTP_total"],
        "physical_source_bytes_total_unchanged": prog["physical_source_bytes_total"],
        "scope_modified": False,
        "MCTS_untouched": True,
        "human_reviewed": False,
        "independent_chemistry": False,
        "git_commit_push": False,
        "roadmap_P2_closed": False,
        "next_actions": [
            "issue an explicit A6 ruling on the isoorientin name-level exposure (12 distinct records, no graph/site fields) before any C-side fresh claim",
            "obtain source-bound full atom/bond graph + anomer stereo + reference precursor for the PMC13564134 C6 claim",
            "resolve item 10 (Iris SI to main-article attachment) and item 14 (inner-sugar O2 linkage) from existing custody, no new exposure needed for the ruling itself",
            "enumerate per-article reaction universes only where a prospective, post-freeze source is lawfully available",
        ],
        "no_promotion_note": "fresh C/SS remain 0; G6 remains incomplete; G7-G10 not started; P7/Roadmap P2 still In Progress.",
    }
    if (ROOT / SNAP).exists():
        raise RuntimeError("immutable snapshot exists")
    write(T, str(SNAP), json.dumps(snap, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    event(T, "reaction_ledger_progress_snapshot", path=str(SNAP))
    print(json.dumps({"snapshot": str(SNAP), "rows_total": snap["rows_total"],
                      "A11": f"{a11['passed']}/{a11['checks_total']}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
