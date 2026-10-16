"""CLI and HTTP share this isolated live execution boundary."""

import json, os, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from .contracts import SearchRequest
from .resources import dumps, sha
from .workspace import root as workspace_root, PACKAGE, AssetError, config
from .reviewed_resources import load_review


def search(request: SearchRequest, run_root=None):
    ROOT = workspace_root()
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex
    )
    root = Path(run_root) if run_root else ROOT / "outputs/runs"
    folder = root / run_id
    folder.mkdir(parents=True, exist_ok=False)
    req = request.payload()
    (folder / "request.json").write_text(dumps(req))
    envelope = {"run_id": run_id, "request": req, "output": str(folder / "result.json")}
    start = time.monotonic()
    error = None
    from .task016_runs import append_run
    governed = append_run(run_id, "started", request=req)
    worker_started = False
    env = {
        **os.environ,
        "PYTHONHASHSEED": str(request.seed),
        "PYTHONPATH": str(PACKAGE.parent),
        "FLAVORETRO_WORKSPACE": str(ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MPLCONFIGDIR": str(ROOT / "outputs/cache/matplotlib"),
    }
    try:
        envelope["review_binding"] = load_review().binding
        (folder / "review-binding.json").write_text(dumps(envelope["review_binding"]))
        if request.glycoside_expansion:
            if request.glycoside_library_version == "v6":
                from .glycoside_library_v6 import load_registry
            elif request.glycoside_library_version == "v3":
                from .glycoside_library_v3 import load_registry
            elif request.glycoside_library_version == "v4":
                from .glycoside_library_v4 import load_registry
            elif request.glycoside_library_version == "v2":
                from .glycoside_library import load_registry
            else:
                from .glycoside_expansion import load_registry
            envelope["domain_binding"] = load_registry().binding
            (folder / "domain-binding.json").write_text(dumps(envelope["domain_binding"]))
        with (folder / "worker.log").open("w") as log:
            worker_started = True
            proc = subprocess.run(
                [sys.executable, "-B", "-m", "flavoretro.worker"],
                input=json.dumps(envelope),
                text=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=ROOT,
                env=env,
                timeout=max(0.1, 60 - (time.monotonic() - start)) if governed else sum(p["seconds"] for p in request.phases()) + 90,
            )
        if proc.returncode:
            error = {
                "code": "engine_error",
                "message": "MCTS execution failed; inspect run worker.log",
                "returncode": proc.returncode,
            }
    except AssetError as exc:
        error = {"code": "review_assets_error", "message": str(exc)}
        (folder / "worker.log").write_text(str(exc) + "\n")
    except subprocess.TimeoutExpired:
        error = {
            "code": "timeout",
            "message": "Isolated MCTS exceeded wall-clock budget; worker terminated",
        }
    if error:
        result = {
            "run_id": run_id,
            "status": "error",
            "error": error,
            "execution_source": "live_attempt_failed",
            "routes": [],
            "release_ready": False,
            "review_expected": envelope.get("review_binding", config("search.json").get("reviewed_resources", {})),
        }
        (folder / "result.json").write_text(dumps(result))
    else:
        result = json.loads((folder / "result.json").read_text())
    manifest = {
        "run_id": run_id,
        "status": result["status"],
        **({"domain_binding": result.get("domain_binding", envelope.get("domain_binding"))} if request.glycoside_expansion else {}),
        "review_binding": result.get("review_binding", result.get("review_expected")),
        "wall_seconds": time.monotonic() - start,
        "files": {p.name: sha(p) for p in folder.iterdir() if p.is_file()},
    }
    (folder / "manifest.json").write_text(dumps(manifest))
    if governed:
        append_run(run_id, "finished", status=result["status"], worker_started=worker_started, wall_seconds=manifest["wall_seconds"], execution_source=result.get("execution_source"), manifest=str(folder / "manifest.json"), error=result.get("error"))
    for p in folder.iterdir():
        p.chmod(0o444)
    return result
