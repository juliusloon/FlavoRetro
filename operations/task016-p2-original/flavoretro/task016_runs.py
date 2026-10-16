"""Opt-in development run ledger. Disabled outside explicitly governed validation."""
import fcntl
import json
import os
from pathlib import Path
from datetime import datetime,timezone
from .workspace import root


P1_BUDGET_REVISION_SHA256 = "497b5aeca99fa6df1c72d64418b53813d898d8371f5898de14721cce90d6c3cd"


def append_run(run_id, phase, **details):
    value = os.environ.get("FLAVORETRO_TASK016_LEDGER")
    if not value:
        return False
    path = Path(value).resolve()
    ceiling = 120
    budget_binding = None
    revision_binding = None
    if path == (root() / "outputs/task016-p1/v1/run_ledger.jsonl").resolve():
        from .resources import sha
        baseline = root() / "outputs/task016-p1/v1/execution-baseline.json"
        approval = json.loads(baseline.read_text())
        if approval.get("task") != "TASK-016-P1" or approval.get("approval_type") != "agent_delegated" or approval["limits"]["service_attempts"] != 180:
            raise ValueError("P1 budget approval absent or invalid")
        ceiling = 180
        budget_binding = sha(baseline)
        revision_path = root() / "outputs/task016-p1/v2/budget_revision.json"
        if revision_path.exists():
            if sha(revision_path) != P1_BUDGET_REVISION_SHA256:
                raise ValueError("P1 budget revision hash drift")
            revision = json.loads(revision_path.read_text())
            if (revision.get("task") != "TASK-016-P1"
                    or revision.get("approval_type") != "agent_delegated"
                    or revision.get("original_baseline_sha256") != budget_binding
                    or revision.get("approved_limits", {}).get("service_attempts") != 240):
                raise ValueError("P1 budget revision approval absent or invalid")
            ceiling = 240
            revision_binding = sha(revision_path)
    elif not path.is_relative_to(root() / "outputs/task016"):
        raise ValueError("TASK-016 ledger must be inside governed task outputs")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        rows = [json.loads(line) for line in handle if line.strip()]
        ids = {r["run_id"] for r in rows if r.get("run_id")}
        if phase == "started" and (run_id in ids or len(ids) >= ceiling):
            raise ValueError(f"TASK-016 duplicate run or total {ceiling}-run ceiling reached")
        if budget_binding and any(r.get("budget_binding") != budget_binding for r in rows):
            raise ValueError("P1 run budget binding drift")
        handle.write(json.dumps(dict(run_id=run_id,phase=phase,**({"budget_binding": budget_binding, "ceiling": ceiling, **({"budget_revision_sha256": revision_binding} if revision_binding else {})} if budget_binding else {}),purpose=os.environ.get("FLAVORETRO_TASK016_PURPOSE","engineering_regression"),at=datetime.now(timezone.utc).isoformat(),**details),ensure_ascii=False)+"\n")
        handle.flush()
        fcntl.flock(handle, fcntl.LOCK_UN)
    return True
