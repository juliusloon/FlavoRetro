"""Opt-in development run ledger. Disabled outside explicitly governed validation."""
import fcntl
import json
import os
from pathlib import Path
from datetime import datetime,timezone
from .workspace import root


P2_BASELINE_SHA256 = "795ae452638fbaa42436771b1f9f9209aabcfdfd376aa5da907f9b4aa475f9f2"

P1_BUDGET_REVISION_SHA256 = "497b5aeca99fa6df1c72d64418b53813d898d8371f5898de14721cce90d6c3cd"

P6_APPROVAL_SHA256 = "cb7780efa86d7513282754a724bedccae127ea2f01e8ed2ee37575b50066aba7"

P3_APPROVAL_SHA256 = "4b8ef3ba8559347085844689b3f0abb6e49cf409bccd023d60207f2830108570"


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
    elif path == (root() / "outputs/task016-p2/v1/run_ledger.jsonl").resolve():
        from .resources import sha
        baseline = root() / "outputs/task016-p2/v1/execution-baseline.json"
        if not baseline.is_file() or sha(baseline) != P2_BASELINE_SHA256:
            raise ValueError("P2 budget approval hash absent or drift")
        approval = json.loads(baseline.read_text())
        limits = approval.get("budgets", {})
        if (approval.get("task") != "TASK-016-P2"
                or approval.get("approval_type") != "human_direct"
                or limits.get("total_search_attempts") != 240
                or limits.get("validation_search_attempts") != 213
                or limits.get("engineering_search_attempts") != 27):
            raise ValueError("P2 approved budget invalid")
        ceiling = 240
        budget_binding = sha(baseline)
        purpose = os.environ.get("FLAVORETRO_TASK016_PURPOSE", "")
        if purpose not in {"task016_p2_validation", "task016_p2_engineering"}:
            raise ValueError("P2 search attempt requires an explicit governed purpose")
    elif path == (root() / "outputs/task016-p3/v1/run_ledger.jsonl").resolve():
        from .resources import sha
        baseline = root() / "outputs/task016-p3/v1/approval.json"
        if not baseline.is_file() or sha(baseline) != P3_APPROVAL_SHA256:
            raise ValueError("P3 budget approval hash absent or drift")
        approval = json.loads(baseline.read_text())
        limits = approval.get("budget", {})
        if (approval.get("task_id") != "TASK-016-P3"
                or approval.get("approval_type") != "agent_delegated"
                or limits.get("search_limit") != 480
                or limits.get("download_limit_gb") != 4):
            raise ValueError("P3 approved budget invalid")
        ceiling = 480
        budget_binding = sha(baseline)
        purpose = os.environ.get("FLAVORETRO_TASK016_PURPOSE", "")
        if purpose not in {"task016_p3_validation", "task016_p3_engineering"}:
            raise ValueError("P3 search attempt requires an explicit governed purpose")
    elif path == (root() / "outputs/task016-p6/v1/run_ledger.jsonl").resolve():
        from .resources import sha
        baseline = root() / "outputs/task016-p6/v1/approval.json"
        if not baseline.is_file() or sha(baseline) != P6_APPROVAL_SHA256:
            raise ValueError("P6 budget approval hash absent or drift")
        approval = json.loads(baseline.read_text())
        if (approval.get("task") != "TASK-016-P6"
                or approval.get("approval_type") != "agent_delegated"
                or approval.get("budgets", {}).get("total_search_attempts") != 480):
            raise ValueError("P6 approved budget invalid")
        ceiling = 480
        budget_binding = sha(baseline)
        purpose = os.environ.get("FLAVORETRO_TASK016_PURPOSE", "")
        if purpose not in {"p6_C_validation", "p6_SS_validation", "p6_legacy", "p6_revalidation", "p6_engineering"}:
            raise ValueError("P6 requires a fixed governed purpose")
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
        if path == (root() / "outputs/task016-p2/v1/run_ledger.jsonl").resolve():
            purpose = os.environ["FLAVORETRO_TASK016_PURPOSE"]
            limit = 213 if purpose == "task016_p2_validation" else 27
            reservations = [r for r in rows if r.get("phase") == "started"]
            if phase == "started" and sum(r.get("purpose") == purpose for r in reservations) >= limit:
                raise ValueError(f"P2 {purpose} {limit}-attempt ceiling reached")
            if phase != "started" and not any(r["run_id"] == run_id and r.get("purpose") == purpose for r in reservations):
                raise ValueError("P2 completion has no matching reservation")
        if path == (root() / "outputs/task016-p6/v1/run_ledger.jsonl").resolve():
            purpose = os.environ["FLAVORETRO_TASK016_PURPOSE"]
            limit = {"p6_C_validation": 81, "p6_SS_validation": 81, "p6_legacy": 51, "p6_revalidation": 213, "p6_engineering": 54}[purpose]
            reservations = [r for r in rows if r.get("phase") == "started"]
            if phase == "started" and sum(r.get("purpose") == purpose for r in reservations) >= limit:
                raise ValueError(f"P6 {purpose} {limit}-attempt ceiling reached")
            if phase != "started" and not any(r["run_id"] == run_id and r.get("purpose") == purpose for r in reservations):
                raise ValueError("P6 completion has no matching reservation")
        if budget_binding and any(r.get("budget_binding") != budget_binding for r in rows):
            raise ValueError("P1 run budget binding drift")
        handle.write(json.dumps(dict(run_id=run_id,phase=phase,**({"budget_binding": budget_binding, "ceiling": ceiling, **({"budget_revision_sha256": revision_binding} if revision_binding else {})} if budget_binding else {}),purpose=os.environ.get("FLAVORETRO_TASK016_PURPOSE","engineering_regression"),at=datetime.now(timezone.utc).isoformat(),**details),ensure_ascii=False)+"\n")
        handle.flush()
        fcntl.flock(handle, fcntl.LOCK_UN)
    return True
