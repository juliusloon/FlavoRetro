"""C-E02 raw fresh intake transport. No chemistry extraction or qualification."""
from __future__ import annotations
import fcntl
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import Counter
from pathlib import Path
from scripts.operate import event, write
from scripts.task016_p7_orchestrate import (
    ROOT, TASK, ContractError, now, sha_file, verify_hashes, verify_stage_chain,
)
BASE = ROOT / "outputs/task016-p7/v1"
C = BASE / "C"
E = C / "E02"
RAW = ROOT / "data/raw/task016-p7/C/E02"
HEADER_KEYS = {"content-type", "content-length", "content-encoding", "etag",
               "last-modified", "date", "location"}
KINDS = {"metadata", "article_version", "attachment"}

def rows(path):
    p = Path(path)
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

def immutable_json(path, value):
    p = Path(path)
    if p.exists():
        raise ContractError("immutable output exists: " + str(p))
    write(TASK, str(p.relative_to(ROOT)), json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n")

def append(path, value):
    p = Path(path)
    text = p.read_text() if p.exists() else ""
    write(TASK, str(p.relative_to(ROOT)), text + json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")

def require_active(contract_path):
    p = Path(contract_path)
    if not p.is_absolute():
        p = ROOT / p
    if not p.resolve().is_relative_to(E.resolve()):
        raise ContractError("C-E02 intake contract outside its namespace")
    contract = json.loads(p.read_text())
    if contract.get("task") != TASK or contract.get("epoch_id") != "C-E02" or contract.get("family") != "C":
        raise ContractError("wrong fresh intake task/epoch/family")
    stage = ROOT / contract["G4_pointer"]["path"]
    g4 = verify_stage_chain(stage, contract["G4_pointer"]["sha256"])
    if g4["stage"] != "G4_SCOPE_FREEZE" or g4["epoch_id"] != "C-E02":
        raise ContractError("intake predecessor is not C-E02 G4")
    terminal_types = {"epoch_incomplete_decision", "epoch_invalidation", "epoch_invalidated", "epoch_closed", "epoch_complete"}
    terminal_states = {"development_epoch_incomplete", "invalidated", "closed", "complete", "completed"}
    registered = [r for r in rows(BASE / "epoch_ledger.jsonl") if r.get("epoch_id") == "C-E02" and r.get("family") == "C"]
    if not registered or any(r.get("event_type") in terminal_types or r.get("status") in terminal_states for r in registered):
        raise ContractError("C-E02 epoch is absent or terminal")
    if (BASE / "epochs/C-E02/incomplete_decision.json").exists():
        raise ContractError("C-E02 terminal decision exists")
    verify_hashes(contract["files_sha256"])
    if contract.get("chemical_extraction_permitted") is not False:
        raise ContractError("raw intake cannot authorize chemistry extraction")
    if contract.get("unknown_name_identity_fail_closed") is not True:
        raise ContractError("intake lost unresolved name exposure gate")
    return contract

def physical_attempts():
    """Deduplicate physical source events across snapshots and live ledgers."""
    found = {}
    paths = sorted(p for p in BASE.rglob("*") if p.is_file() and p.suffix in {".json", ".jsonl"} and
                   (p.name == "http_ledger.jsonl" or "http_attempt" in p.name))
    for p in paths:
        rr = rows(p) if p.suffix == ".jsonl" else json.loads(p.read_text())
        if not isinstance(rr, list):
            raise ContractError("HTTP ledger is not a row list")
        for r in rr:
            key = (r["url"], r["started_at"], r["path"])
            if key in found and any(found[key][k] != r[k] for k in ("sha256", "bytes")):
                raise ContractError("conflicting physical HTTP accounting")
            found[key] = r
    for r in rows(ROOT / "operations/events.jsonl"):
        if r.get("task") == TASK and r.get("action") == "source_http":
            key = (r["url"], r["started_at"], r["path"])
            if key in found and any(found[key][k] != r[k] for k in ("sha256", "bytes")):
                raise ContractError("HTTP operation differs from physical ledger")
            found.setdefault(key, r)
    return list(found.values())

def budget(attempts, kind, object_limit):
    totals = Counter(HTTP=len(attempts), bytes=sum(r["bytes"] for r in attempts))
    c_rows = [r for r in attempts if "C" in Path(r["path"] or "").parts]
    family = Counter(HTTP=len(c_rows), bytes=sum(r["bytes"] for r in c_rows))
    for rr, counts in ((attempts, totals), (c_rows, family)):
        counts["article_versions"] = sum(r.get("kind", r.get("role")) in {"article_version", "xml"} for r in rr)
        counts["attachments"] = sum(r.get("kind", r.get("role")) == "attachment" for r in rr)
    for counts, limits in ((totals, dict(HTTP=8000, bytes=8*1024**3, article_versions=400, attachments=800)),
                           (family, dict(HTTP=2500, bytes=2*1024**3, article_versions=120, attachments=200))):
        projected = counts.copy()
        projected["HTTP"] += 1
        projected["bytes"] += object_limit + 1
        if kind == "article_version":
            projected["article_versions"] += 1
        if kind == "attachment":
            projected["attachments"] += 1
        if any(projected[k] > v for k, v in limits.items()):
            raise ContractError("source request would exceed hard budget")
    return dict(global_before=dict(totals), C_before=dict(family))

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def acquire(contract_path, url, kind, reason, *, license=None, recovery_pointer=None, object_limit=64*1024**2):
    if kind not in KINDS or not isinstance(reason, str) or not reason.strip():
        raise ContractError("unknown source kind or empty reason")
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ContractError("source URL must be public HTTPS without credentials/fragment")
    if not isinstance(object_limit, int) or isinstance(object_limit, bool) or not (1 <= object_limit <= 64*1024**2):
        raise ContractError("invalid object byte cap")
    lock = BASE / "source_budget_acquisition.lock"
    if not lock.exists():
        write(TASK, str(lock.relative_to(ROOT)), "")
    with lock.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            contract = require_active(contract_path)
            if any((E / "stages/batches" / contract["batch_id"]).glob("G5_FRESH_HOLDOUT_ACQUIRE.json")):
                raise ContractError("frozen raw batch cannot receive new source requests")
            attempts = physical_attempts()
            prior = [r for r in attempts if r["url"] == url]
            recovery = False
            if len(prior) >= 2:
                if len(prior) >= 3 or recovery_pointer is None:
                    raise ContractError("single URL attempt cap exceeded")
                rp = ROOT / recovery_pointer["path"]
                if sha_file(rp) != recovery_pointer["sha256"]:
                    raise ContractError("recovery plan SHA drift")
                plan = json.loads(rp.read_text())
                if plan.get("url") != url or plan.get("epoch_id") != "C-E02" or not plan.get("recovery_reason"):
                    raise ContractError("recovery URL/epoch/reason missing")
                recovery = True
            before = budget(attempts, kind, object_limit)
            aid = "C-E02-RAW-" + uuid.uuid4().hex
            started = now()
            contract_rel = str(Path(contract_path).resolve().relative_to(ROOT))
            request_plan = dict(attempt_id=aid, url=url, kind=kind, reason=reason, phase="fresh",
                                registered_at=started, epoch_id="C-E02", batch_id=contract["batch_id"],
                                intake_contract_path=contract_rel, intake_contract_sha256=sha_file(contract_path),
                                limit_bytes=object_limit, recovery_chain=recovery,
                                recovery_pointer=recovery_pointer, budget_before=before)
            append(C / "acquisition_plan.jsonl", request_plan)
            data = bytearray()
            code = None
            error = None
            headers = {}
            final_url = url
            response = None
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 public research", "Accept-Encoding": "identity"})
                try:
                    response = urllib.request.build_opener(NoRedirect()).open(request, timeout=30)
                except urllib.error.HTTPError as exc:
                    response = exc
                    error = "HTTPError: " + str(exc.code)
                code = response.code
                final_url = response.geturl()
                headers = {k.lower(): v for k, v in response.headers.items() if k.lower() in HEADER_KEYS}
                while len(data) <= object_limit:
                    chunk = response.read(min(64*1024, object_limit+1-len(data)))
                    if not chunk:
                        break
                    data.extend(chunk)
                if len(data) > object_limit:
                    error = "OBJECT_BYTE_CAP_EXCEEDED; captured prefix retained"
                if final_url != url:
                    error = "UNPLANNED_REDIRECT; no redirected request permitted"
                if 300 <= code < 400:
                    error = "REDIRECT_DEFERRED; Location requires separate planned request"
            except Exception as exc:
                error = type(exc).__name__ + ": " + str(exc)
                if getattr(exc, "partial", None):
                    data.extend(exc.partial[:max(0, object_limit+1-len(data))])
            finally:
                if response is not None:
                    response.close()
            raw = RAW / (aid + "." + kind)
            raw.parent.mkdir(parents=True, exist_ok=True)
            if raw.exists():
                raise ContractError("immutable raw UUID collision")
            raw.write_bytes(bytes(data))
            raw.chmod(0o444)
            digest = sha_file(raw)
            event(TASK, "write_binary", path=str(raw.relative_to(ROOT)), before=None, after=digest,
                  bytes=len(data), source_path=url, source_sha256=None, source_page=None)
            item = dict(attempt_id=aid, url=url, final_url=final_url, kind=kind, phase="fresh",
                        epoch_id="C-E02", batch_id=contract["batch_id"], reason=reason,
                        status="available" if code == 200 and error is None else "failed",
                        status_code=code, error=error, bytes=len(data), path=str(raw.relative_to(ROOT)), sha256=digest,
                        license=license, redistribution="local_only_pending_or_source_license", started_at=started,
                        finished_at=now(), recovery_chain=recovery, recovery_reason=(plan["recovery_reason"] if recovery else None),
                        recovery_pointer=recovery_pointer, headers=headers,
                        intake_contract_path=contract_rel, intake_contract_sha256=sha_file(contract_path),
                        G4_pointer=contract["G4_pointer"], chemical_extracted=False, evidence_eligible=False)
            append(C / "http_ledger.jsonl", item)
            event(TASK, "source_http", **item)
            live = rows(C / "http_ledger.jsonl")
            manifest = dict(objects=[{k:r[k] for k in ("attempt_id", "path", "sha256", "bytes", "kind")} for r in live if r["path"] is not None],
                            bytes=sum(r["bytes"] for r in live), http_requests=len(live),
                            article_versions=sum(r["kind"] == "article_version" for r in live),
                            attachments=sum(r["kind"] == "attachment" for r in live))
            write(TASK, str((C / "raw_manifest.json").relative_to(ROOT)), json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
            return item
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
