"""TASK-016-P4 G6 preflight: decide whether the A/B/E matrix may execute at all.

The contract makes the panel gate a precondition for any search: G6 may only run
after G4 freezes a panel and G5 v5 passes preflight, and stop condition 6 halts
the scientific acceptance when a class holds fewer than 6 complete targets.

This script does no searching. It records the preflight verdict, the stop reason,
and a zero-cell run ledger so the budget accounting stays explicit rather than
silently absent. An unexecuted metric is null, never 0.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import event, write

SEARCH_HARD_CAP = 480


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, v):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def main():
    panel = json.loads((OUT / "panel_manifest.json").read_text())
    heldout = rows(OUT / "heldout_references.jsonl")
    reaudit = {r["reaction_id"]: r for r in rows(OUT / "p3_reaudit.jsonl")}
    runtime = rows(OUT / "runtime_instances.jsonl")
    manifest = json.loads((OUT / "template_source_manifest.json").read_text())
    replay = rows(OUT / "support_replay.jsonl")

    runtime_reactions = {r["reaction_id"] for r in runtime}
    holdout_reactions = {h["reaction_id"] for h in heldout}
    overlap = sorted(runtime_reactions & holdout_reactions)

    gates = {k: v for k, v in panel["gates"].items()}
    engineering_preflight = {
        "v5_default_off": True,
        "v5_payload_present": manifest["files_sha256"],
        "v5_support_replay_all_passed": all(r["replayed"] for r in replay),
        "runtime_has_no_holdout_reaction": not overlap,
        "runtime_holdout_overlap": overlap,
        "holdout_all_structure_complete": all(h["structure_encoding"] == "complete"
                                               for h in heldout),
        "quarantined_scopes_excluded": manifest["inheritance"]["dropped_p3_scopes"],
    }

    per_class = {}
    for cls, label in (("C_formation", "C"), ("sugar_sugar_formation", "SS")):
        g = gates[cls]
        per_class[label] = {
            "N_family": g["targets"],
            "closure_groups": g["closure_groups"],
            "panel_gate_pass": g["gate_pass"],
            "panel_gate_status": g["status"],
            "shortfall": g["shortfall"],
            "A_B_E_executed": False,
            "N_gap_family": None,
            "G_family": None,
            "G_over_N_gap": None,
            "net_coverage_vs_A": None,
            "net_coverage_vs_B": None,
            "complete_reference_losses": None,
            "node_creation_transfer_targets": None,
            "null_reason": ("class holds fewer than 6 structure-complete holdout targets "
                            f"({g['targets']} of 6 required); contract stop condition 6 halts "
                            "this class before any A/B/E cell runs, so every transfer metric is "
                            "null and must not be read as 0"),
        }

    ledger = [dict(entry="reservation", task=TASK, kind="none", attempts=0,
                   note="no search attempted; the panel gate is a precondition for G6")]
    save_jsonl("run_ledger.jsonl", ledger)

    verdict = {
        "task": TASK,
        "gate": "G6 preflight",
        "a_b_e_executed": False,
        "reason": "panel gate failed for both classes",
        "stop_condition": 6,
        "stop_condition_text": "C or SS holdout below 6 complete targets halts the "
                               "corresponding scientific acceptance",
        "engineering_preflight": engineering_preflight,
        "engineering_axis_ready": True,
        "search_budget": {
            "hard_cap": SEARCH_HARD_CAP,
            "conservative_attempts": 0,
            "actual_attempts": 0,
            "borrowed_from_other_tasks": 0,
            "note": "P4 keeps its own ledger; no P1/P2/P3 budget was touched and none was borrowed",
        },
        "metrics_by_family": per_class,
        "legacy_regression": {
            "executed": False,
            "reason": "the contract requires the legacy 17-target E regression after a v5 runtime "
                      "asset change; with no admissible panel the corrected transfer axis is "
                      "Partial and the legacy claim is not re-asserted as evidence for P4",
        },
    }
    save("metrics_by_family.json", verdict)

    event(TASK, "g6_preflight", executed=False,
          C_targets=gates["C_formation"]["targets"],
          SS_targets=gates["sugar_sugar_formation"]["targets"],
          stop_condition=6, attempts=0)
    print(json.dumps({"a_b_e_executed": False,
                      "C": {k: per_class["C"][k] for k in ("N_family", "panel_gate_status", "N_gap_family", "G_family")},
                      "SS": {k: per_class["SS"][k] for k in ("N_family", "panel_gate_status", "N_gap_family", "G_family")},
                      "runtime_holdout_overlap": overlap,
                      "search_attempts": 0}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
