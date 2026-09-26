"""Local workbench; shared live service, explicit bounded resource endpoints."""

import argparse, json, re, threading, uuid, sys, os
from datetime import datetime, timezone
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from .resources import dumps, sha
from .workspace import root, active_data, config, PACKAGE, AssetError
from .database import query, metadata as index_metadata
from .policies import records
from .contracts import SearchRequest
from .service import search
from .topology import audit as topology_audit

GATE = threading.BoundedSemaphore(1)
RUN_PATTERN = r"\d{8}T\d{6}-[0-9a-f]{32}"
EVALUATION_PATTERN = r"development-[0-9a-f]{32}"

def saved_run(name):
    if not re.fullmatch(RUN_PATTERN, name):
        raise ValueError("invalid_run_id")
    folder = root() / "outputs/runs" / name
    manifest = json.loads((folder / "manifest.json").read_text())
    if manifest.get("run_id") != name or "result.json" not in manifest.get("files", {}):
        raise AssetError("run_integrity_failed")
    for filename, expected in manifest["files"].items():
        try:
            valid = Path(filename).name == filename and sha(folder / filename) == expected
        except OSError:
            valid = False
        if not valid:
            raise AssetError("run_integrity_failed")
    return {"execution_source":"explicit_saved_run", "integrity":"verified", "manifest":manifest,
        "result":json.loads((folder / "result.json").read_text())}

def run_list(offset=0, limit=25):
    if offset < 0 or not 1 <= limit <= 100:
        raise ValueError("invalid pagination")
    paths = sorted((root() / "outputs/runs").glob("*/manifest.json"), reverse=True)
    selected = [p for p in paths if re.fullmatch(RUN_PATTERN,p.parent.name)]
    rows = []
    for p in selected[offset:offset+limit]:
        try:
            saved = saved_run(p.parent.name)
            result = saved["result"]
            rows.append({"run_id":p.parent.name,"status":result["status"],"integrity":"verified",
                "resource_version":result.get("resource_version","historical_unspecified"),
                "smiles":result.get("request",{}).get("smiles"),"routes":len(result["routes"])})
        except (OSError, ValueError, KeyError) as exc:
            rows.append({"run_id":p.parent.name,"status":"integrity_failed","message":str(exc)})
    return {"total":len(selected),"runs":rows,"execution_source":"explicit_saved_run_list"}

def evaluation_job(name):
    if not re.fullmatch(EVALUATION_PATTERN,name):
        raise ValueError("invalid_evaluation_id")
    folder = root() / "outputs/evaluation" / name
    if (folder / "job.json").is_file():
        job = json.loads((folder / "job.json").read_text())
    else:
        summary = json.loads((folder / "summary.json").read_text())
        job = {"evaluation_id":name,"status":"completed_with_failures" if summary["failures"] else "completed",
            "completed_cells":summary["completed_cells"],"summary":summary}
    if job.get("status") == "running" and job.get("owner_pid") != os.getpid():
        job = {**job,"status":"interrupted_or_untracked", "error":"该未完成记录不属于当前服务进程；保留进度，不自动恢复或声称仍在运行。"}
    return job

def start_evaluation():
    from .evaluation import compare
    # Validate assets before creating a job; GATE is acquired by the HTTP caller.
    active_data(); index_metadata()
    name = "development-" + uuid.uuid4().hex
    folder = root() / "outputs/evaluation" / name
    folder.mkdir(parents=True,exist_ok=False)
    state = {"evaluation_id":name,"status":"running","completed_cells":0,"expected_cells":12,
        "scope":"development_engine_comparison_not_blind","same_node_ceiling":False,
        "owner_pid":os.getpid(),
        "created_at":datetime.now(timezone.utc).isoformat()}
    def persist():
        temporary = folder / "job.tmp"
        temporary.write_text(dumps(state)); temporary.replace(folder / "job.json")
    persist()
    def progress(cells):
        state.update(completed_cells=len(cells),cells=cells);persist()
    def run():
        try:
            _, summary = compare(folder,progress)
            state.update(status="completed_with_failures" if summary["failures"] else "completed",summary=summary)
        except Exception as exc:
            state.update(status="error",error=str(exc))
        finally:
            try:
                persist()
            finally:
                GATE.release()
    threading.Thread(target=run,daemon=True).start()
    return state.copy()


# Topology presentation boundary: candidates stay labelled graph synthons.
TOPOLOGY_BOUNDARY = "labelled graph synthons, not reagents"
TOPOLOGY_BOND_COLORS = {
    "aryl_O_candidate": (0.10, 0.45, 0.90),
    "sugar_sugar_O_candidate": (0.10, 0.60, 0.30),
    "aryl_C_candidate": (0.55, 0.20, 0.75),
    "other_O_candidate": (0.90, 0.55, 0.10),
    "N_candidate": (0.85, 0.20, 0.20),
    "phosphate_donor_control": (0.50, 0.50, 0.50),
}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, kind="application/json; charset=utf-8"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(data)
        except BrokenPipeError:
            pass

    def json(self, status, value):
        self.send(status, dumps(value))

    def do_GET(self):
        ROOT = root()
        url = urlsplit(self.path)
        q = parse_qs(url.query)
        try:
            if url.path == "/api/health":
                return self.json(
                    200,
                    {
                        "status": "ok",
                        "project": "FlavoRetro",
                        "release_ready": False,
                        "execution": "fresh_mcts_per_request",
                        "python":sys.executable,
                    },
                )
            if url.path == "/api/status":
                folder, summary, pointer = active_data()
                return self.json(
                    200,
                    {
                        "resources": summary,
                        "resource_version": pointer["version"],
                        "database": index_metadata()[1],
                        "resource_manifest_sha256": pointer["manifest_sha256"],
                        "state": (ROOT / "STATE.md").read_text() if (ROOT / "STATE.md").is_file() else "工作区无 STATE.md；资产和科学门槛以清单为准。",
                        "profiles": config("search.json"),
                        "foundation": json.loads((ROOT / "metadata/foundation.json").read_text()) if (ROOT / "metadata/foundation.json").is_file() else {"gates":{},"status":"not_recorded"},
                        "github": json.loads((ROOT / "outputs/validation/task012-sync.json").read_text()) if (ROOT / "outputs/validation/task012-sync.json").is_file() else {"status":"not_verified_in_workspace"},
                        "installation":{"python":sys.executable,"package":str(PACKAGE),"workspace":str(ROOT)},
                        "rebuild_commands":["python -m flavoretro.resources <new-version-dir> --workspace <workspace>","python -m flavoretro.database --build --workspace <workspace>"],
                    },
                )
            if url.path == "/api/targets":
                return self.json(
                    200,
                    [
                        {"name": r["raw"]["query_name"], "smiles": r["raw"]["smiles"]}
                        for r in records()
                        if r["kind"] == "molecule"
                        and r["raw"]["query_name"].lower()
                        in [
                            "hesperidin",
                            "hesperetin",
                            "quercetin",
                            "naringenin",
                            "rutin",
                        ]
                    ],
                )
            if url.path == "/api/records":
                return self.json(200, query(kind=q.get("kind", [""])[0], q=q.get("q", [""])[0],
                    offset=int(q.get("offset", ["0"])[0]), limit=int(q.get("limit", ["25"])[0]),
                    issue=q.get("issue", [""])[0], source_status=q.get("source_status", [""])[0],
                    outcome=q.get("outcome", [""])[0]))
            if url.path == "/api/teaching":
                return self.json(
                    200,
                    config("teaching_guidance.json"),
                )
            if url.path == "/api/literature-teaching":
                return self.json(
                    200,
                    config("literature_teaching_layer.json"),
                )
            if url.path == "/api/topology":
                smiles = SearchRequest(smiles=q.get("smiles", [""])[0]).smiles
                result = topology_audit(smiles)
                result["canonical_smiles"] = smiles
                result["boundary"] = TOPOLOGY_BOUNDARY
                return self.json(200, result)
            if url.path == "/api/molecule":
                smiles = SearchRequest(smiles=q.get("smiles", [""])[0]).smiles
                mol = Chem.MolFromSmiles(smiles)
                drawer = rdMolDraw2D.MolDraw2DSVG(340, 210)
                if q.get("topology", [""])[0] == "1":
                    sites = topology_audit(smiles)["sites"]
                    bonds = [s["bond_index"] for s in sites]
                    colors = {
                        s["bond_index"]: TOPOLOGY_BOND_COLORS.get(
                            s["family"], (0.5, 0.5, 0.5)
                        )
                        for s in sites
                    }
                    # Positional highlight args: atoms, bonds, atom colors, bond colors.
                    drawer.DrawMolecule(mol, [], bonds, {}, colors)
                else:
                    drawer.DrawMolecule(mol)
                drawer.FinishDrawing()
                return self.send(200, drawer.GetDrawingText(), "image/svg+xml")
            if url.path == "/api/preflight":
                from .evaluation import preflight
                return self.json(200,preflight())
            if url.path == "/api/runs":
                return self.json(200,run_list(int(q.get("offset",["0"])[0]),int(q.get("limit",["25"])[0])))
            if url.path.startswith("/api/runs/"):
                try:
                    return self.json(200,saved_run(url.path.rsplit("/",1)[-1]))
                except AssetError as exc:
                    return self.json(409,{"error":"run_integrity_failed","message":str(exc)})
            if url.path == "/api/evaluations":
                jobs=[]
                for folder in sorted((ROOT / "outputs/evaluation").glob("development-*"),reverse=True):
                    if re.fullmatch(EVALUATION_PATTERN,folder.name):
                        try:
                            job=evaluation_job(folder.name)
                            jobs.append({k:v for k,v in job.items() if k not in {"cells","summary"}})
                        except (ValueError,OSError,KeyError):
                            jobs.append({"evaluation_id":folder.name,"status":"integrity_or_format_error"})
                return self.json(200,{"evaluations":jobs})
            if url.path.startswith("/api/evaluations/"):
                return self.json(200,evaluation_job(url.path.rsplit("/",1)[-1]))
            static = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
            if url.path in static:
                name = static[url.path]
                kind = {
                    "html": "text/html",
                    "js": "text/javascript",
                    "css": "text/css",
                }[name.rsplit(".", 1)[1]]
                return self.send(
                    200, (PACKAGE / "assets/web" / name).read_bytes(), kind + "; charset=utf-8"
                )
            return self.json(404, {"error": "not_found"})
        except AssetError as exc:
            return self.json(503, {"error": "missing_or_invalid_assets", "message": str(exc)})
        except FileNotFoundError:
            return self.json(404, {"error": "not_found"})
        except ValueError as exc:
            return self.json(400, {"error": "invalid_request", "message": str(exc)})

    def do_POST(self):
        if self.path == "/api/evaluations":
            try:
                length=int(self.headers.get("Content-Length","0"))
                if not 0 < length <= 16384:
                    return self.json(413,{"error":"body_size"})
                value=json.loads(self.rfile.read(length))
                if value != {"kind":"development"}:
                    raise ValueError("only the fixed 12-cell development comparison is supported")
            except (ValueError,TypeError) as exc:
                return self.json(400,{"error":"invalid_request","message":str(exc)})
            if not GATE.acquire(blocking=False):
                return self.json(429,{"error":"search_busy","message":"已有搜索或开发对照正在运行，请稍后再试"})
            try:
                state=start_evaluation()
            except (ValueError,OSError) as exc:
                GATE.release()
                return self.json(503,{"error":"evaluation_unavailable","message":str(exc)})
            return self.json(202,state)
        if self.path != "/api/search":
            return self.json(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                return self.json(413, {"error": "body_size"})
            request = SearchRequest.model_validate(json.loads(self.rfile.read(length)))
        except (ValueError, TypeError) as exc:
            return self.json(400, {"error": "invalid_request", "message": str(exc)})
        if not GATE.acquire(blocking=False):
            return self.json(
                429, {"error": "search_busy", "message": "已有搜索正在运行，请稍后再试"}
            )
        try:
            result = search(request)
            return self.json(200 if result["status"] == "ok" else 503, result)
        finally:
            GATE.release()

    def log_message(self, fmt, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--workspace")
    args = parser.parse_args()
    from .workspace import configure
    configure(args.workspace)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"FlavoRetro http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
