#!/usr/bin/env python3
"""TASK-016-P3 G5 verification: budget audit, protection check, byte replay,
old-version behaviour and delivery accounting."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts.task016_p3_sources import rows  # noqa: E402

V1 = ROOT / "outputs/task016-p3/v1"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    results = {}

    # 1. budget audit
    acc = json.loads((V1 / "source_accounting.json").read_text())
    ceilings = acc["ceilings"]
    results["source_budget"] = {
        "http": [acc["http_attempts"], ceilings["http"]],
        "bytes": [acc["bytes"], ceilings["bytes"]],
        "article_versions": [acc["article_versions"], ceilings["articles"]],
        "attachments": [acc["attachments"], ceilings["attachments"]],
        "metadata": [acc["metadata_records"], ceilings["metadata"]],
    }
    ledger_path = V1 / "run_ledger.jsonl"
    ledger = rows(ledger_path) if ledger_path.exists() else []
    started = [r for r in ledger if r.get("phase") == "started"]
    finished = [r for r in ledger if r.get("phase") in ("completed", "failed")]
    obs = rows(V1 / "mcts_observations.jsonl") if (V1 / "mcts_observations.jsonl").exists() else []
    results["search_budget"] = {
        "ledger_rows": len(ledger), "runs_started": len(started),
        "validation_observations": len(obs),
        "plan": 51, "validation_ceiling": 426, "total_ceiling": 480,
        "within_ceiling": len(ledger) <= 480,
    }

    # 2. protection: P2 protected set (1591 files) must be drift-free
    p2_base = json.loads((ROOT / "outputs/task016-p2/v1/execution-baseline.json").read_text())
    p2_protected = p2_base["protected_sha256"]
    drift = [rel for rel, h in p2_protected.items()
             if not (ROOT / rel).is_file() or sha(ROOT / rel) != h]
    results["p2_protected_files"] = len(p2_protected)
    results["p2_protected_drift"] = len(drift)
    results["p2_protected_drift_paths"] = drift[:20]

    # 3. byte replay of the deterministic payload
    replay_dir = Path("/tmp/p3-replay-verify")
    if replay_dir.exists():
        for f in ("templates.jsonl", "runtime_instances.jsonl", "template_source_manifest.json"):
            (replay_dir / f).unlink()
    env = dict(os.environ)
    env["FLAVORETRO_P3_REPLAY_DIR"] = str(replay_dir)
    subprocess.run([str(ROOT / ".venv-foundation/bin/python"), "-B",
                    str(ROOT / "scripts/task016_p3_build.py")],
                   cwd=ROOT, env=env, check=True, capture_output=True)
    replay = {}
    for f in ("templates.jsonl", "runtime_instances.jsonl", "template_source_manifest.json"):
        replay[f] = (sha(replay_dir / f) == sha(V1 / f))
    results["payload_byte_replay"] = replay

    # 4. old-version behaviour
    sys.path.insert(0, str(ROOT))
    from flavoretro.glycoside_library_v3 import load_registry as load_v3
    from flavoretro.glycoside_library_v4 import load_registry as load_v4
    from flavoretro.workspace import config
    v3 = load_v3()
    v4 = load_v4()
    results["registries"] = {
        "v3_binding": v3.binding["version"],
        "v4_binding": v4.binding["version"],
        "v3_templates": len(v3.templates),
        "v4_templates": len(v4.templates),
        "v4_templates_absent_from_v3": not any(
            t["template_id"].startswith("p3-scope:") for t in v3.templates),
        "v4_default_enabled": config("glycoside-library-v4.json")["default_enabled"],
        "v3_default_enabled": config("glycoside-library-v3.json")["default_enabled"],
    }

    # 5. delivery accounting
    delivery = {}
    for name in ("approval.json", "baseline_manifest.json", "query_plan.json",
                 "query_ledger.json", "discovery_selection.json", "source_accounting.json",
                 "metadata_dispositions.jsonl", "inherited_queue_review.jsonl",
                 "inherited_queue_crosswalk.jsonl", "candidate_reactions.jsonl",
                 "candidate_extraction_summary.json", "reaction_records.jsonl",
                 "identity_checks.jsonl", "old_new_reaction_map.jsonl",
                 "source_group_edges.jsonl", "exposure_ledger.jsonl", "split_manifest.json",
                 "panel_manifest.json", "heldout_references.jsonl", "unselected_records.jsonl",
                 "templates.jsonl", "runtime_instances.jsonl", "template_source_manifest.json",
                 "experiment_contract.json", "e_regression.json", "mcts_observations.jsonl",
                 "action_trace.jsonl", "round3_query_ledger.json", "round3_selection.json",
                 "round3_article_acquisition_manifest.json", "round3_recovery_chain.jsonl"):
        p = V1 / name
        delivery[name] = sha(p) if p.exists() else None
    results["delivery_sha256"] = {k: v for k, v in delivery.items() if v}
    results["delivery_missing"] = [k for k, v in delivery.items() if v is None]

    print(json.dumps(results, ensure_ascii=False, indent=1, sort_keys=True))
    (V1 / "verify_summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
