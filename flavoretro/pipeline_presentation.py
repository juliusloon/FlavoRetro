"""Read-only presentation of TASK-022 recorded experiments.

An explicitly reopened experiment is labelled saved evidence, never a new run.
"""
import json
from pathlib import Path
import re
from .resources import sha
from .workspace import root, AssetError

BASE = Path("outputs/task022")


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def checked_path(path):
    path = path.resolve()
    if not path.is_relative_to((root() / BASE).resolve()):
        raise ValueError("invalid task evidence path")
    return path


def saved_cell(batch, cell_id):
    if not re.fullmatch(r"[a-z0-9_-]+", batch) or not re.fullmatch(r"[A-Za-z0-9_-]+", cell_id):
        raise ValueError("invalid experiment identifier")
    base = root() / BASE
    ledger = rows(base / "run_ledger.jsonl")
    starts = [r for r in ledger if r.get("event") == "reserved" and r.get("batch") == batch and r.get("cell_id") == cell_id]
    ends = [r for r in ledger if r.get("event") == "finished" and r.get("batch") == batch and r.get("cell_id") == cell_id]
    if (len(starts) != 1 or len(ends) != 1 or starts[0]["attempt_id"] != ends[0]["attempt_id"]
            or ends[0].get("status") != "completed"):
        raise AssetError("experiment not uniquely completed")
    artifacts = ends[0].get("artifacts", {})
    paths = [p for p in artifacts if Path(p).name == "manifest.json"]
    if len(paths) != 1:
        raise AssetError("experiment manifest absent")
    path = checked_path(root() / paths[0])
    if not path.is_file() or sha(path) != artifacts[paths[0]]:
        raise AssetError("experiment manifest drift")
    manifest = json.loads(path.read_text())
    if manifest.get("attempt_id") != starts[0]["attempt_id"] or "result.json" not in manifest.get("files", {}):
        raise AssetError("experiment manifest identity mismatch")
    for filename, expected in manifest["files"].items():
        candidate = checked_path(path.parent / filename)
        if Path(filename).name != filename or not candidate.is_file() or sha(candidate) != expected:
            raise AssetError("experiment file drift")
    result = json.loads((path.parent / "result.json").read_text())
    request = json.loads((path.parent / "request.json").read_text())
    if result.get("run_id") != starts[0]["attempt_id"] or result.get("request") != starts[0]["request"] or request != starts[0]["request"]:
        raise AssetError("experiment request/run identity mismatch")
    return {"execution_source": "explicit_saved_experiment", "integrity": "verified",
            "batch": batch, "cell_id": cell_id, "purpose": starts[0]["purpose"],
            "manifest": manifest, "result": result,
            "boundary": "显式读取已完成计算实验；来源曝光与用途见该批协议。树内首步、展示路线和库存闭合分别解释，独立化学验证仍未完成。"}


def progress():
    base = root() / BASE
    ledger = rows(base / "run_ledger.jsonl")
    starts = [r for r in ledger if r.get("event") == "reserved"]
    ends = [r for r in ledger if r.get("event") == "finished"]
    completed = {r["attempt_id"]: r for r in ends}
    experiments = []
    for path in sorted((base / "batches").glob("*/frozen.json")):
        frozen = json.loads(path.read_text())
        name = frozen["batch"]
        begun = [r for r in starts if r["batch"] == name]
        done = [r for r in begun if r["attempt_id"] in completed]
        # Summaries are labelled snapshots; opening a cell verifies all bytes.
        # Derive the batch folder from its ledger-bound manifest so new runners
        # remain visible without adding hard-coded output directory names.
        candidates = []
        for row in done:
            for artifact in completed[row["attempt_id"]].get("artifacts", {}):
                manifest = checked_path(root() / artifact)
                if manifest.name == "manifest.json" and manifest.parent.parent.name == name:
                    candidate = manifest.parent.parent / "summary.json"
                    if candidate not in candidates:
                        candidates.append(candidate)
        summary_path = next((p for p in candidates if p.is_file()), None)
        summary = None
        if summary_path is not None:
            value = json.loads(summary_path.read_text())
            summary = {k: v for k, v in value.items() if k != "cells"}
        # Analysis files are post-run snapshots, with their own SHA, separate
        # from ledger-bound raw cell integrity and pre-run method commitments.
        comparisons = {}; quality_loss_example = None; comparison_snapshot = None
        analysis_candidates = []
        for candidate in candidates:
            for parent in [candidate.parent, candidate.parent.parent, candidate.parent.parent.parent]:
                if not parent.resolve().is_relative_to((root() / BASE).resolve()): continue
                proposed = checked_path(parent / (name + "_comparison.json"))
                if proposed not in analysis_candidates: analysis_candidates.append(proposed)
        for analysis_path in analysis_candidates:
            if not analysis_path.is_file(): continue
            analysis = json.loads(analysis_path.read_text())
            if analysis.get("batch") != name: raise AssetError("comparison batch mismatch")
            comparisons = {arm: value["summary"] for arm, value in analysis.get("contrasts", {}).items()}
            for arm, contrast in analysis.get("contrasts", {}).items():
                losses = [pair for pair in contrast.get("pairs", []) if pair.get("quality_noninferior") is False]
                if losses and quality_loss_example is None: quality_loss_example = {**losses[0], "arm": arm}
            comparison_snapshot = {"path": str(analysis_path.relative_to(root())), "sha256": sha(analysis_path), "status": "postrun_analysis_snapshot"}
            break
        examples = []
        groups = {}
        for row in done:
            if completed[row["attempt_id"]]["status"] != "completed":
                continue
            group, arm = row["cell_id"].rsplit("-", 1)
            groups.setdefault(group, {})[arm] = row
        scheduled_arms = {cell["arm"] for cell in frozen["protocol"]["cells"]}
        ordered_arms = [a for a in ("N", "O", "O2", "O2R", "D", "D8") if a in scheduled_arms]
        ordered_arms += sorted(scheduled_arms - set(ordered_arms))
        paired = [group for group in sorted(groups) if scheduled_arms <= set(groups[group])]
        example_groups = [] if frozen["protocol"].get("saved_experiment_viewable") is False else paired[:2]
        if quality_loss_example and frozen["protocol"].get("saved_experiment_viewable") is not False:
            loss_group = quality_loss_example["target_id"] + "-" + str(quality_loss_example["seed"])
            if loss_group in paired and loss_group not in example_groups: example_groups.append(loss_group)
        for group in example_groups:
            for arm in ordered_arms:
                row = groups[group][arm]
                examples.append({"cell_id": row["cell_id"], "arm": arm,
                                 "result_url": "/api/pipeline-cell/" + name + "/" + row["cell_id"]})
        audit_path = base / "evaluation_audit" / (name + "_independent_audit.json")
        audit = json.loads(audit_path.read_text()) if audit_path.is_file() else {}
        expected = len(frozen["protocol"]["cells"])
        experiments.append({"batch": name, "purpose": frozen["protocol"]["purpose"],
                            "claim_boundary": frozen["protocol"]["claim_boundary"],
                            "expected_cells": expected, "started_cells": len(begun), "completed_cells": len(done),
                            "failed_cells": sum(completed[r["attempt_id"]]["status"] != "completed" for r in done),
                            "status": "completed" if len(done) == expected else "incomplete",
                            "frozen_sha256": sha(path), "summary": summary,
                            "stock": frozen["protocol"].get("stock", {"kind": "reviewed_candidate_stock", "entries": 17}),
                            "arms": frozen["protocol"].get("arms", {arm: arm for arm in ordered_arms}),
                            "summary_status": "recorded_snapshot" if summary else "not_available",
                            "audit_axes": audit.get("axes") if audit.get("complete") and audit.get("all_cells_normal") else None,
                            "audit_limitations": audit.get("limitations", []),
                            "method_execution_valid": audit.get("method_execution_valid_for_declared_frontier"),
                            "comparisons": comparisons, "comparison_snapshot": comparison_snapshot,
                            "quality_loss_example": quality_loss_example, "examples": examples})
    return {"task": "TASK-022", "approval": "agent_delegated", "human_reviewed": False,
            "search_attempts": len(starts), "finished_attempts": len(ends),
            "unfinished_attempts": len(starts) - len(ends), "experiments": experiments,
            "checkpoint": json.loads((base / "current.json").read_text()) if (base / "current.json").is_file() else None,
            "boundary": "各批次使用协议声明的共享模型、过滤器和库存；N为原生AiZynthFinder MCTS，O为通用优化，D为该批次声明的来源扩展。库存规模、扩展版本及分母见每批协议。首步召回、用户可见路线和完整库存闭合分别报告。"}


def teaching(base):
    """Append locally sourced teaching candidates without rewriting legacy cards."""
    pointer = root() / BASE / "teaching/current.json"
    if not pointer.exists():
        return base
    binding = json.loads(pointer.read_text())
    path = checked_path(root() / binding["path"])
    source = checked_path(root() / binding["source_snapshot"])
    if sha(path) != binding["sha256"] or sha(source) != binding["source_snapshot_sha256"]:
        raise AssetError("teaching source snapshot drift")
    data = json.loads(path.read_text())
    for item in data.get("supplemental_sources", []):
        extra = checked_path(root() / item["path"])
        if not extra.is_file() or sha(extra) != item["sha256"]:
            raise AssetError("teaching supplemental source drift")
    papers = base.get("paper_cards", []) + data["paper_cards"]
    lessons = base.get("reaction_lessons", []) + data["reaction_lessons"]
    return {**base, "paper_cards": papers, "reaction_lessons": lessons,
            "summary": {**base.get("summary", {}), "paper_count": len(papers),
                        "reaction_lesson_count": len(lessons), "agent_added_lessons": len(data["reaction_lessons"]),
                        "production_ready_lesson_count": sum(bool(x.get("production_ready")) for x in lessons)},
            "task022_teaching_binding": binding, "teacher_reviewed": False}
