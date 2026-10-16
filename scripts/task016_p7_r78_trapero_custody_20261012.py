"""R78: raw custody of the OA-eligible Trapero 2012 Crocus UGT707B1 original (PMC3425182).
Advertised-key PMC OA custody only; NO article/SI content read; no chemistry.
"""
import hashlib, json, re, urllib.parse, urllib.request, urllib.error, uuid
from pathlib import Path
from datetime import datetime, timezone

from scripts.operate import ROOT, write, event
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "SS/E02/fresh/SS-E02-R78-trapero2012-raw-custody-v1"
RAW = Path("data/raw/task016-p7/SS/E02/SS-E02-R78-trapero2012-raw-custody-v1")
LOCK = B / "source_budget_acquisition.lock"
PMCID = "PMC3425182"; DOI = "10.1104/pp.112.198069"; PMID = "22649274"

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

def http_get(url, kind, reason):
    with (ROOT / LOCK).open("a+") as f:
        import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            attempts = physical_attempts(); before = counter(attempts)
            sub = counter([r for r in attempts if "SS" in Path(r.get("path", "")).parts])
            same = [r for r in attempts if canonical(r["url"]) == canonical(url)]
            if len(same) >= 2: return dict(result="rejected_old_url", status_code=None)
            if before["HTTP"] + 1 > 8000: raise RuntimeError("GLOBAL_BUDGET_STOP")
            if sub["HTTP"] + 1 > 2500: raise RuntimeError("SS_BUDGET_STOP")
            aid = "R78-" + uuid.uuid4().hex; start = now()
            append(OUT / "physical_request_preregistration.jsonl", dict(attempt_id=aid, url=url, kind=kind,
                registered_at=start, precontract_SHA=sha_file(OUT / "precontract.json"), budget_before=before, SS_before=sub))
            data = b""; status = None; err = None
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 (public science metadata)", "Accept-Encoding": "identity"})
                try: resp = urllib.request.build_opener(NoRedirect()).open(req, timeout=90)
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
                       batch_id="R78-trapero2012-raw-custody", status_code=status, bytes=len(data),
                       status="available" if status == 200 and not err else "failed", error=err,
                       path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), started_at=start, finished_at=now(),
                       scientific_body_content_read=False, chemical_extracted=False, metadata_only=(kind == "metadata"),
                       no_content_read=True)
            event(T, "source_http", **rec)
            return rec
        finally:
            import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def save_obj_row(qid, rec):
    append(OUT / "query_execution.jsonl", dict(query_id=qid, status=rec.get("status"),
        status_code=rec.get("status_code"), url=rec.get("url"),
        raw_pointer={k: rec.get(k) for k in ("path", "sha256", "bytes")}, error=rec.get("error"),
        scientific_body_content_read=False, chemical_extracted=False))

def parse_keys(text):
    keys = []
    for block in text.split("<Contents>")[1:]:
        mk = re.search(r"<Key>([^<]+)</Key>", block)
        me = re.search(r"<ETag>&quot;([0-9a-f]{32})&quot;</ETag>", block)
        ms = re.search(r"<Size>(\d+)</Size>", block)
        if mk and me and ms: keys.append(dict(Key=mk.group(1), Size=int(ms.group(1)), ETag=me.group(1)))
    return keys

def prereg():
    if (ROOT / OUT).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    files = [B / "governance/R76-skill-routes-saturation-confirmation-v1/confirmation.json",
             Path("scripts/task016_p7_r78_trapero_custody_20261012.py")]
    save(OUT / "precontract.json", dict(task=T, epoch_id="SS-E02", family="SS", batch="R78-trapero2012-raw-custody",
        created_at=now(), approval_type="agent_delegated", human_reviewed=False,
        purpose="Raw custody of the Trapero 2012 Crocus UGT707B1 original (PMC3425182, Plant Physiol 159:1335) and advertised SI objects; ADVERTISED-KEY ONLY; no article/SI content read; no chemistry; content stays sealed until a future G5 preregistration; R29 caption-level mention documented as metadata-only prior hint (identifier-level exposure ledger: 0 rows)",
        lead=dict(pmcid=PMCID, doi=DOI, pmid=PMID,
                  title="Characterization of a glucosyltransferase enzyme involved in the formation of kaempferol and quercetin sophorosides in Crocus sativus",
                  journal="Plant Physiol 159(4):1335-1354 (2012)", enzyme="UGT707B1", genbank="HE793682"),
        prior_hint_note="SS-E02-R29 A4/A5 files mention UGT707B1/Trapero as the UGT79B6 paper Figure-3 caption enzyme name; that is a metadata-level hint recorded here, NOT chemical examination of this source",
        registered_input_SHA={str(p): sha_file(p) for p in files},
        batch_limits=dict(HTTP=9, bytes=9 * 8 * 1024**2, article_versions=2, attachments=7),
        constraints=dict(no_content_read=True, advertised_keys_only=True, no_redirect=True, no_retry=True,
            no_credentials=True, max_object=8 * 1024**2)))
    save(OUT / "query_plan.json", dict(task=T, planned=1, slots=[dict(
        query_id="R78-INDEX-01", kind="metadata",
        url="https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=" + PMCID + ".",
        reason="official PMC OA cloud exact-PMCID prefix index; advertised Key links only")], registered_at=now()))
    print(json.dumps(dict(preregistered=1)), flush=True)

def _rows(name):
    p = ROOT / OUT / name
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def run():
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    for slot in plan["slots"]:
        if any(r["query_id"] == slot["query_id"] and r.get("status_code") for r in _rows("query_execution.jsonl")): continue
        rec = http_get(slot["url"], slot["kind"], slot["reason"])
        keys = []
        if rec.get("status") == "available":
            text = (ROOT / rec["path"]).read_text(errors="replace")
            keys = parse_keys(text)
        save_obj_row(slot["query_id"], rec)
        write(T, str(OUT / "advertised_keys.json"), json.dumps(keys, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        print(json.dumps(dict(q=slot["query_id"], status=rec.get("status_code"), keys=len(keys), err=rec.get("error"))), flush=True)

def run_objects():
    keys = json.loads((ROOT / OUT / "advertised_keys.json").read_text())
    xmls = [k for k in keys if re.fullmatch(re.escape(PMCID) + r"\.(\d+)/" + re.escape(PMCID) + r"\.\1\.xml", k["Key"])]
    if not xmls: raise RuntimeError("NO_ADVERTISED_XML")
    chosen = max(xmls, key=lambda k: int(re.match(re.escape(PMCID) + r"\.(\d+)/", k["Key"]).group(1)))
    slots = [dict(query_id="R78-XML-01", kind="article_version",
                  url="https://pmc-oa-opendata.s3.amazonaws.com/" + chosen["Key"],
                  reason="advertised JATS original, highest version; sealed custody only")]
    sis = [k for k in keys if re.search(r"\.(pdf|zip|docx?|xlsx?|tar\.gz)$", k["Key"], re.I) and not k["Key"].endswith(PMCID + ".1/" + PMCID + ".1.pdf")]
    for i, k in enumerate(sis[:5], start=1):
        slots.append(dict(query_id="R78-SI-%02d" % i, kind="attachment",
                          url="https://pmc-oa-opendata.s3.amazonaws.com/" + k["Key"],
                          reason="advertised SI object; sealed custody only"))
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    plan["object_slots"] = slots; plan["chosen_xml"] = chosen; plan["si_keys"] = sis
    write(T, str(OUT / "query_plan.json"), json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    for s in slots:
        if any(r["query_id"] == s["query_id"] and r.get("status_code") for r in _rows("query_execution.jsonl")): continue
        rec = http_get(s["url"], s["kind"], s["reason"])
        save_obj_row(s["query_id"], rec)
        print(json.dumps(dict(q=s["query_id"], status=rec.get("status_code"), bytes=rec.get("bytes"), err=rec.get("error"))), flush=True)

def finish():
    exrows = _rows("query_execution.jsonl")
    att = physical_attempts()
    summary = dict(task=T, at=now(), executed_real_HTTP=len([r for r in exrows if r.get("status_code")]),
        rows=len(exrows), content_read=False, chemistry=False, design_decision_made=False,
        physical_HTTP_global=len(att), physical_bytes_global=sum(int(x.get("bytes") or 0) for x in att),
        MCTS_added=0, fresh_admitted=0,
        note="sealed raw custody; content-read sequencing deferred to future G5 preregistration with full prior-hint documentation")
    save(OUT / "raw_custody_summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("executed_real_HTTP", "physical_HTTP_global", "physical_bytes_global")}), flush=True)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "prereg": prereg()
    elif mode == "run": run()
    elif mode == "objects": run_objects()
    elif mode == "finish": finish()
    else: raise SystemExit("prereg | run | objects | finish")
