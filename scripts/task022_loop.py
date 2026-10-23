"""TASK-022 immutable batches, cumulative attempts, and recoverable checkpoints.

Run through scripts/operate.py. Old TASK-016/017 ledgers are never modified.
An interrupted reserved cell is retained, not silently rerun under the same ID.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import uuid
import operate

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "outputs/task022"
PURPOSES = {"engineering", "development", "historical_descriptive", "prospective_source_computational"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def relative(path):
    p = Path(path)
    p = (ROOT / p).resolve() if not p.is_absolute() else p.resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError("asset outside FlavoRetro workspace")
    return p.relative_to(ROOT).as_posix()


def write(path, value):
    operate.write("TASK-022", relative(path), canonical(value))


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


@contextmanager
def lock():
    BASE.mkdir(parents=True, exist_ok=True)
    with (BASE / ".loop.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def append(path, event):
    event = {"at": datetime.now(timezone.utc).isoformat(), **event}
    with path.open("a") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
    operate.event("TASK-022", "append", path=relative(path), event=event, after=sha(path))
    return event


def approval():
    path = BASE / "approval.json"
    item = json.loads(path.read_text())
    if item.get("task") != "TASK-022" or item.get("approval") != "agent_delegated" or item.get("human_reviewed") is not False:
        raise ValueError("invalid TASK-022 delegation")
    if sha(ROOT / relative(item["contract"])) != item["contract_sha256"]:
        raise ValueError("contract drift; add a separately approved revision")
    if type(item.get("max_search_attempts")) is not int or item["max_search_attempts"] <= 0:
        raise ValueError("invalid cumulative budget")
    return item, sha(path)


def batch_path(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("batch name must use lowercase alphanumeric, dash, underscore")
    return BASE / "batches" / name / "frozen.json"


def freeze_batch(name, protocol, assets):
    """Call before running any cell. Protocol contains every exact request."""
    with lock():
        _, binding = approval()
        path = batch_path(name)
        if path.exists():
            raise ValueError("batch already frozen; use a new version")
        if protocol.get("purpose") not in PURPOSES:
            raise ValueError("explicit valid experiment purpose required")
        cells = protocol.get("cells", [])
        if not cells or len(cells) > 300:
            raise ValueError("batch must contain 1..300 predeclared cells")
        ids = [cell.get("cell_id") for cell in cells]
        if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
            raise ValueError("cell IDs must be unique nonempty strings")
        if any(not isinstance(cell.get("request"), dict) for cell in cells):
            raise ValueError("each cell needs its exact request")
        for field in ("claim_boundary", "metrics", "stopping_rule", "approval"):
            if not protocol.get(field):
                raise ValueError("protocol field missing: " + field)
        if protocol["approval"] != "agent_delegated":
            raise ValueError("cannot claim human protocol review")
        asset_hashes = {relative(p): sha(ROOT / relative(p)) for p in assets}
        if not asset_hashes:
            raise ValueError("freeze actual method and data assets")
        payload = {"schema": 1, "batch": name, "approval_sha256": binding,
                   "protocol": protocol, "assets": asset_hashes,
                   "frozen_at": datetime.now(timezone.utc).isoformat()}
        write(path, payload)
        append(BASE / "events.jsonl", {"event": "batch_frozen", "batch": name, "path": relative(path), "sha256": sha(path)})
        return payload


def check_batch(name):
    path = batch_path(name)
    frozen = json.loads(path.read_text())
    _, binding = approval()
    if binding != frozen["approval_sha256"]:
        raise ValueError("approval binding drift")
    recorded = [r for r in rows(BASE / "events.jsonl") if r.get("event") == "batch_frozen" and r.get("batch") == name]
    if len(recorded) != 1 or recorded[0]["sha256"] != sha(path):
        raise ValueError("frozen batch manifest drift")
    for rel, expected in frozen["assets"].items():
        if sha(ROOT / relative(rel)) != expected:
            raise ValueError("frozen asset drift: " + rel)
    return frozen


def reserve_cell(name, cell_id):
    """Atomically charge the cumulative budget before invoking service.search."""
    with lock():
        frozen = check_batch(name)
        approved, _ = approval()
        ledger = rows(BASE / "run_ledger.jsonl")
        starts = [r for r in ledger if r["event"] == "reserved"]
        if len(starts) >= approved["max_search_attempts"]:
            raise ValueError("TASK-022 cumulative search budget exhausted")
        if any(r["batch"] == name and r["cell_id"] == cell_id for r in starts):
            raise ValueError("cell already attempted; retain its original failure/interruption")
        cells = [c for c in frozen["protocol"]["cells"] if c["cell_id"] == cell_id]
        if len(cells) != 1:
            raise ValueError("cell absent from frozen protocol")
        return append(BASE / "run_ledger.jsonl", {
            "event": "reserved", "attempt_id": uuid.uuid4().hex, "batch": name,
            "cell_id": cell_id, "purpose": frozen["protocol"]["purpose"],
            "batch_sha256": sha(batch_path(name)), "approval_sha256": frozen["approval_sha256"],
            "request": cells[0]["request"], "attempt_number": len(starts) + 1})


def finish_cell(attempt_id, *, status, run_manifest=None, error=None):
    if status not in {"completed", "failed", "interrupted"}:
        raise ValueError("invalid terminal state")
    with lock():
        ledger = rows(BASE / "run_ledger.jsonl")
        matches = [r for r in ledger if r.get("attempt_id") == attempt_id]
        if len(matches) != 1 or matches[0]["event"] != "reserved":
            raise ValueError("attempt absent or already terminal")
        start = matches[0]
        artifacts = {}
        if run_manifest:
            rel = relative(run_manifest)
            artifacts[rel] = sha(ROOT / rel)
        if status == "completed" and not artifacts:
            raise ValueError("completed run requires a saved manifest")
        if status != "completed" and not error:
            raise ValueError("retain failure/interruption reason")
        return append(BASE / "run_ledger.jsonl", {
            "event": "finished", "attempt_id": attempt_id, "batch": start["batch"],
            "cell_id": start["cell_id"], "status": status,
            "artifacts": artifacts, "error": error})


def checkpoint(stage, outcome, evidence, next_action, status="in_progress"):
    if not outcome.strip() or not next_action.strip():
        raise ValueError("checkpoint must explain progress and concrete next action")
    with lock():
        bindings = {relative(p): sha(ROOT / relative(p)) for p in evidence}
        item = append(BASE / "events.jsonl", {"event": "checkpoint", "stage": stage,
            "status": status, "outcome": outcome, "evidence": bindings, "next_action": next_action})
        write(BASE / "current.json", item)
        return item


def status():
    ledger = rows(BASE / "run_ledger.jsonl")
    starts = [r for r in ledger if r["event"] == "reserved"]
    ends = {r["attempt_id"]: r for r in ledger if r["event"] == "finished"}
    return {"search_attempts": len(starts), "terminal": len(ends),
            "unfinished": [r for r in starts if r["attempt_id"] not in ends],
            "by_purpose": {p: sum(r["purpose"] == p for r in starts) for p in sorted(PURPOSES)},
            "latest_checkpoint": json.loads((BASE / "current.json").read_text()) if (BASE / "current.json").exists() else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "verify"])
    parser.add_argument("--batch")
    args = parser.parse_args()
    print(canonical(check_batch(args.batch) if args.action == "verify" else status()))


if __name__ == "__main__":
    main()
