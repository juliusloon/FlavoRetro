"""R77: raw custody of the OA Shi 2026 TcCGT1-engineering original + advertised SI.
Metadata-level only: no article/SI content read, no chemistry, no design decision.
"""
import hashlib, json, re, urllib.parse, urllib.request, urllib.error, uuid
from pathlib import Path
from datetime import datetime, timezone

from scripts.operate import ROOT, write, event
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "C/E02/fresh/C-E02-R77-shi2026-TcCGT1-raw-custody-v1"
RAW = Path("data/raw/task016-p7/C/E02/C-E02-R77-shi2026-raw-custody-v1")
LOCK = B / "source_budget_acquisition.lock"
PMCID = "PMC12993211"; DOI = "10.1016/j.synbio.2026.02.011"; PMID = "41852688"
INDEX_URL = "https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=" + PMCID + "."

def now(): return datetime.now(timezone.utc).isoformat()
def sha_file(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(T, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def append(p, v):
    write(T, str(p), ((ROOT / p).read_text() if (ROOT / p).exists() else "") + json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")

def canonical(url):
    u = urllib.parse.urlsplit(url)
    return (u.hostname or "", urllib.parse.unquote(u.path).rstrip("/"), tuple(sorted(urllib.parse.parse_qsl(u.query, keep_blank_values=True))))

def counter(rr):
    return dict(HTTP=len(rr), bytes=sum(int(x.get("bytes", 0)) for x in rr),
                article_versions=sum(x.get("kind", x.get("role")) in ("article_version", "xml") for x in rr),
                attachments=sum(x.get("kind", x.get("role")) == "attachment" for x in rr))

def prereg():
    if (ROOT / OUT).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    files = [B / "governance/R76-skill-routes-saturation-confirmation-v1/confirmation.json",
             Path("scripts/task016_p7_r77_shi2026_custody_20261012.py")]
    save(OUT / "precontract.json", dict(task=T, epoch_id="C-E02", family="C", batch="R77-shi2026-raw-custody",
        created_at=now(), approval_type="agent_delegated", human_reviewed=False,
        purpose="Raw custody of the OA Shi 2026 TcCGT1-engineering original (PMC12993211, CC BY) and its advertised SI objects for the newly identified flavone-8C design direction; ADVERTISED-KEY ONLY; no article/SI content read; no chemistry; no design or scope decision; content stays sealed until any future G5 preregistration",
        lead=dict(pmcid=PMCID, doi=DOI, pmid=PMID,
                  title="Structure-coevolution dual-guided engineering of C-glycosyltransferase enables high-level biosynthesis of vitexin in Yarrowia lipolytica",
                  journal="Synth Syst Biotechnol 13:350-361 (2026)", license="cc-by", isOpenAccess="Y", inEPMC="Y"),
        registered_input_SHA={str(p): sha_file(p) for p in files},
        batch_limits=dict(HTTP=8, bytes=8 * 8 * 1024**2, article_versions=2, attachments=6),
        constraints=dict(no_content_read=True, advertised_keys_only=True, no_redirect=True,
            no_retry=True, no_credentials=True, max_object=8 * 1024**2)))

    save(OUT / "query_plan.json", dict(task=T, planned=1, slots=[dict(
        query_id="R77-INDEX-01", kind="metadata", url=INDEX_URL,
        reason="official PMC OA cloud exact-PMCID prefix index; advertised Key links only")], registered_at=now()))
    print(json.dumps(dict(preregistered=1)), flush=True)

def acquire(contract, url, kind, reason):
    with (ROOT / LOCK).open("a+") as f:
        import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            attempts = physical_attempts(); before = counter(attempts)
            same = [r for r in attempts if canonical(r["url"]) == canonical(url)]
            if len(same) >= 2: return dict(result="rejected_old_url", HTTP=0)
            if before["HTTP"] + 1 > 8000: raise RuntimeError("GLOBAL_BUDGET_STOP")
            aid = "R77-" + uuid.uuid4().hex; start = now()
            append(OUT / "physical_request_preregistration.jsonl", dict(attempt_id=aid, url=url, kind=kind,
                registered_at=start, precontract_SHA=sha_file(OUT / "precontract.json"), budget_before=before))
            data = b""; status = None; err = None
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 (public science metadata)", "Accept-Encoding": "identity"})
                try: resp = urllib.request.build_opener(NoRedirect()).open(req, timeout=60)
                except urllib.error.HTTPError as e: resp = e; err = "HTTP_" + str(e.code)
                status = resp.code
                data = resp.read(8 * 1024**2 + 1)
                if len(data) > 8 * 1024**2: data = data[:8 * 1024**2]; err = "OBJECT_LIMIT_TRUNCATED"
            except Exception as e: err = type(e).__name__ + ":" + str(e)[:150]
            finally:
                try: resp.close()
                except Exception: pass
            ptr = RAW / (aid + ".bin"); p = ROOT / ptr
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists(): raise RuntimeError("RAW_IMMUTABLE_EXISTS")
            p.write_bytes(data); p.chmod(0o444)
            event(T, "write_binary", path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            rec = dict(attempt_id=aid, url=url, kind=kind, role=kind, phase="raw_custody_no_content_read",
                       batch_id="R77-shi2026-raw-custody", status_code=status, bytes=len(data),
                       status="available" if status == 200 and not err else "failed", error=err,
                       path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), started_at=start, finished_at=now(),
                       scientific_body_content_read=False, chemical_extracted=False, metadata_only=(kind == "metadata"),
                       no_content_read=True)
            event(T, "source_http", **rec)
            return rec
        finally:
            import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def recover_index_row():
    """Recovery per the failure-discipline: the index HTTP already succeeded and is
    ledgered; parse its sealed raw bytes and write the missing execution row. No new HTTP."""
    target_url = INDEX_URL
    ev = None
    marker = '"source_http"'
    for line in (ROOT / "operations/events.jsonl").read_text().splitlines():
        if marker not in line or target_url not in line: continue
        try: e = json.loads(line)
        except Exception: continue
        if e.get("action") == "source_http" and e.get("url") == target_url: ev = e
    if not ev: raise RuntimeError("INDEX_ATTEMPT_NOT_FOUND")
    raw = ROOT / ev["path"]
    if hashlib.sha256(raw.read_bytes()).hexdigest() != ev["sha256"]: raise RuntimeError("RAW_DRIFT")
    text = raw.read_text(errors="replace")
    keys = []
    for block in text.split("<Contents>")[1:]:
        mk = re.search(r"<Key>([^<]+)</Key>", block)
        me = re.search(r"<ETag>&quot;([0-9a-f]{32})&quot;</ETag>", block)
        ms = re.search(r"<Size>(\d+)</Size>", block)
        if mk and me and ms:
            keys.append(dict(Key=mk.group(1), Size=int(ms.group(1)), ETag=me.group(1)))
    prior = _rows("query_execution.jsonl")
    already = [r for r in prior if r["query_id"] == "R77-INDEX-01" and r.get("status_code")]
    if already and len((already[-1].get("advertised_keys") or [])) >= len(keys):
        print(json.dumps(dict(recovered="R77-INDEX-01", keys=len(already[-1]["advertised_keys"]), note="existing row complete")), flush=True)
        return
    append(OUT / "query_execution.jsonl", dict(query_id="R77-INDEX-01", status=ev.get("status"),
        status_code=ev.get("status_code"), raw_pointer={"path": ev["path"], "sha256": ev["sha256"], "bytes": ev["bytes"]},
        advertised_keys=keys, error=ev.get("error"), recovery_no_new_http=True,
        correction_of="prior recovery row had cross-record Key/ETag/Size pairing due to S3 element order (ETag precedes Size); prior row preserved",
        parse_note="per-Contents-block parse"))
    print(json.dumps(dict(recovered="R77-INDEX-01", keys=len(keys), corrected=True)), flush=True)

def run():
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    for slot in plan["slots"]:
        if any(r["query_id"] == slot["query_id"] and r.get("status_code") for r in _rows("query_execution.jsonl")): continue
        rec = acquire(OUT / "precontract.json", slot["url"], slot["kind"], slot["reason"])
        data = (ROOT / rec["path"]).read_bytes()
        keys = []
        if rec["status"] == "available" and slot["kind"] == "metadata":
            # ListBucketResult XML parse of advertised keys (text only: Key/Size/ETag)
            text = data.decode("utf-8", errors="replace")
            for m in re.finditer(r"<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>.*?<ETag>&quot;([0-9a-f]{32})&quot;</ETag>", text, re.S):
                keys.append(dict(Key=m.group(1), Size=int(m.group(2)), ETag=m.group(3)))
        append(OUT / "query_execution.jsonl", dict(query_id=slot["query_id"], status=rec["status"],
            status_code=rec["status_code"], raw_pointer={k: rec[k] for k in ("path", "sha256", "bytes")},
            advertised_keys=keys, error=rec["error"]))
        print(json.dumps(dict(q=slot["query_id"], status=rec["status_code"], keys=len(keys), err=rec["error"])), flush=True)

def _rows(name):
    p = ROOT / OUT / name
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def run_objects():
    idx_rows = [r for r in _rows("query_execution.jsonl") if r["query_id"] == "R77-INDEX-01" and r.get("status_code")]
    if not idx_rows: raise RuntimeError("INDEX_ROW_MISSING")
    ex = idx_rows[-1]
    keys = ex["advertised_keys"]
    xmls = [k for k in keys if re.fullmatch(re.escape(PMCID) + r"\.(\d+)/" + re.escape(PMCID) + r"\.\1\.xml", k["Key"])]
    if not xmls: raise RuntimeError("NO_ADVERTISED_XML")
    chosen = max(xmls, key=lambda k: int(re.match(re.escape(PMCID) + r"\.(\d+)/", k["Key"]).group(1)))
    url = "https://pmc-oa-opendata.s3.amazonaws.com/" + chosen["Key"]
    slots = [dict(query_id="R77-XML-01", kind="article_version", url=url, reason="advertised JATS original, highest version; sealed custody only")]
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    plan["object_slots"] = slots; plan["chosen_xml"] = chosen
    write(T, str(OUT / "query_plan.json"), json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    for s in slots:
        if any(r["query_id"] == s["query_id"] and r.get("status_code") for r in _rows("query_execution.jsonl")): continue
        rec = acquire(OUT / "precontract.json", s["url"], s["kind"], s["reason"])
        append(OUT / "query_execution.jsonl", dict(query_id=s["query_id"], status=rec["status"],
            status_code=rec["status_code"], raw_pointer={k: rec[k] for k in ("path", "sha256", "bytes")}, error=rec["error"]))
        print(json.dumps(dict(q=s["query_id"], status=rec["status_code"], bytes=rec["bytes"], err=rec["error"])), flush=True)

def finish():
    exrows = _rows("query_execution.jsonl")
    att = physical_attempts()
    summary = dict(task=T, at=now(), executed_real_HTTP=len([r for r in exrows if r.get("status_code")]),
        rows=len(exrows), content_read=False, chemistry=False, design_decision_made=False,
        physical_HTTP_global=len(att), physical_bytes_global=sum(int(x.get("bytes") or 0) for x in att),
        MCTS_added=0, note="sealed raw custody; SI objects deliberately NOT fetched in this batch (content-read sequencing deferred to future G5)")
    save(OUT / "raw_custody_summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("executed_real_HTTP", "physical_HTTP_global", "physical_bytes_global")}), flush=True)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "prereg": prereg()
    elif mode == "run": run()
    elif mode == "objects": run_objects()
    elif mode == "recover": recover_index_row()
    elif mode == "finish": finish()
    else: raise SystemExit("prereg | run | objects | finish")
