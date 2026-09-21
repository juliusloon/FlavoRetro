"""Local workbench; shared live service, explicit bounded resource endpoints."""

import argparse, json, re, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from .resources import ROOT, dumps, sha
from .policies import records
from .contracts import SearchRequest
from .service import search

GATE = threading.BoundedSemaphore(1)


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
                    },
                )
            if url.path == "/api/status":
                summary = json.loads(
                    (ROOT / "data/derived/v1/manifest.json").read_text()
                )
                return self.json(
                    200,
                    {
                        "resources": summary,
                        "state": (ROOT / "STATE.md").read_text(),
                        "profiles": json.loads(
                            (ROOT / "configs/search.json").read_text()
                        ),
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
                rows = records()
                kind = q.get("kind", [""])[0]
                term = q.get("q", [""])[0].casefold()
                rows = [
                    r
                    for r in rows
                    if (not kind or r["kind"] == kind)
                    and (
                        not term or term in json.dumps(r, ensure_ascii=False).casefold()
                    )
                ]
                offset = max(0, int(q.get("offset", ["0"])[0]))
                limit = min(100, max(1, int(q.get("limit", ["25"])[0])))
                return self.json(
                    200, {"total": len(rows), "records": rows[offset : offset + limit]}
                )
            if url.path == "/api/molecule":
                mol = Chem.MolFromSmiles(
                    SearchRequest(smiles=q.get("smiles", [""])[0]).smiles
                )
                drawer = rdMolDraw2D.MolDraw2DSVG(340, 210)
                drawer.DrawMolecule(mol)
                drawer.FinishDrawing()
                return self.send(200, drawer.GetDrawingText(), "image/svg+xml")
            if url.path.startswith("/api/runs/"):
                name = url.path.rsplit("/", 1)[-1]
                if not re.fullmatch(r"\d{8}T\d{6}-[0-9a-f]{32}", name):
                    return self.json(400, {"error": "invalid_run_id"})
                folder = ROOT / "outputs/runs" / name
                manifest = json.loads((folder / "manifest.json").read_text())
                result = folder / "result.json"
                if sha(result) != manifest["files"]["result.json"]:
                    return self.json(409, {"error": "run_integrity_failed"})
                return self.json(
                    200,
                    {
                        "execution_source": "explicit_saved_run",
                        "result": json.loads(result.read_text()),
                    },
                )
            static = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
            if url.path in static:
                name = static[url.path]
                kind = {
                    "html": "text/html",
                    "js": "text/javascript",
                    "css": "text/css",
                }[name.rsplit(".", 1)[1]]
                return self.send(
                    200, (ROOT / "web" / name).read_bytes(), kind + "; charset=utf-8"
                )
            return self.json(404, {"error": "not_found"})
        except FileNotFoundError:
            return self.json(404, {"error": "not_found"})
        except ValueError as exc:
            return self.json(400, {"error": "invalid_request", "message": str(exc)})

    def do_POST(self):
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
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"FlavoRetro http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
