"""R79: access-verification batch for the originals-request list + EfCGT1 raw custody,
then the unified originals-request list and progress-v37 documents."""
import hashlib, json, re, urllib.parse, urllib.request, urllib.error, uuid
from pathlib import Path
from datetime import datetime, timezone

from scripts.operate import ROOT, write, event
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "governance/R79-originals-request-v1"
R79M = B / "discovery_r79_access_verification_20261012"
R79RAW = Path("data/raw/task016-p7/discovery_r79_access_verification_20261012")

def now(): return datetime.now(timezone.utc).isoformat()
def sha_file(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(T, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def append(p, v):
    write(T, str(p), ((ROOT / p).read_text() if (ROOT / p).exists() else "") + json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")

LIST_DOIS = [
    ("10.1002/anie.201905505", "C8-TcCGT1-original"),
    ("10.1021/acs.jafc.1c00602", "C8-JAFC2021-SuSy"),
    ("10.1016/j.bioorg.2021.104926", "C8-BioOrg2021"),
    ("10.1111/j.1365-313x.2005.02383.x", "SS-Morita2005-IpA3G2GlcT"),
    ("10.1111/pbi.70155", "C-EfCGT1-2025-PMC-check"),
]

def http_get(url, kind, reason):
    attempts = physical_attempts(); before = dict(HTTP=len(attempts), bytes=sum(int(x.get("bytes") or 0) for x in attempts))
    aid = "R79-" + uuid.uuid4().hex; start = now()
    append(R79M / "physical_request_preregistration.jsonl", dict(attempt_id=aid, url=url, kind=kind, registered_at=start, budget_before=before))
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
    ptr = R79RAW / (aid + ".bin"); p = ROOT / ptr
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists(): raise RuntimeError("RAW_IMMUTABLE_EXISTS")
    p.write_bytes(data); p.chmod(0o444)
    event(T, "write_binary", path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    rec = dict(attempt_id=aid, url=url, kind=kind, role=kind, phase="access_verification_and_raw_custody_no_content_read",
        batch_id="R79-originals-request", status_code=status, bytes=len(data),
        status="available" if status == 200 and not err else "failed", error=err,
        path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), started_at=start, finished_at=now(),
        scientific_body_content_read=False, chemical_extracted=False, metadata_only=(kind == "metadata"), no_content_read=True)
    event(T, "source_http", **rec)
    return rec

def prereg():
    if (ROOT / R79M).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    slots = [dict(query_id="R79-OA-%02d" % i, kind="metadata",
                  url="https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe=""),
                  reason="OpenAlex official OA-status verification for originals-request list entry " + label)
             for i, (doi, label) in enumerate(LIST_DOIS, start=1)]
    slots += [dict(query_id="R79-EFCGT-INDEX", kind="metadata",
                   url="https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix=PMC12310836.",
                   reason="official PMC OA index for the OA EfCGT1 (PBJ 2025) original; raw custody only, no content read")]
    save(R79M / "precontract.json", dict(task=T, batch="R79-originals-request", created_at=now(),
        approval_type="agent_delegated", human_reviewed=False,
        purpose="OA-status verification for the unified originals-request list entries + raw custody of the OA EfCGT1 original; metadata/custody only; no content reads; no chemistry",
        batch_limits=dict(HTTP=8, bytes=8 * 8 * 1024**2)))
    save(R79M / "query_plan.json", dict(task=T, planned=len(slots), slots=slots, registered_at=now()))
    print(json.dumps(dict(preregistered=len(slots))), flush=True)

def run():
    plan = json.loads((ROOT / R79M / "query_plan.json").read_text())
    for slot in plan["slots"]:
        if any(r["query_id"] == slot["query_id"] and r.get("status_code") for r in _rows("query_execution.jsonl")): continue
        rec = http_get(slot["url"], slot["kind"], slot["reason"])
        proj = None; keys = []
        if rec.get("status") == "available":
            try:
                data = (ROOT / rec["path"]).read_bytes()
                if slot["kind"] == "metadata" and "openalex" in slot["url"]:
                    d = json.loads(data)
                    oa = d.get("open_access") or {}
                    proj = dict(doi=(d.get("doi") or "").replace("https://doi.org/", ""), title=d.get("title"),
                                year=d.get("publication_year"), is_oa=oa.get("is_oa"), oa_status=oa.get("oa_status"),
                                any_repository=oa.get("any_repository_has_fulltext"),
                                best_pdf=(d.get("best_oa_location") or {}).get("pdf_url") if isinstance(d.get("best_oa_location"), dict) else None)
                elif "list-type=2" in slot["url"]:
                    text = data.decode("utf-8", errors="replace")
                    for block in text.split("<Contents>")[1:]:
                        mk = re.search(r"<Key>([^<]+)</Key>", block); ms = re.search(r"<Size>(\d+)</Size>", block)
                        if mk and ms: keys.append(dict(Key=mk.group(1), Size=int(ms.group(1))))
            except Exception as e: proj = {"parse_error": str(e)[:120]}
        append(R79M / "query_execution.jsonl", dict(query_id=slot["query_id"], url=slot["url"], kind=slot["kind"],
            status=rec.get("status"), status_code=rec.get("status_code"),
            raw_pointer={k: rec.get(k) for k in ("path", "sha256", "bytes")},
            projection=proj, advertised_keys=keys, error=rec.get("error"),
            scientific_body_content_read=False, chemical_extracted=False))
        print(json.dumps(dict(q=slot["query_id"], status=rec.get("status_code"), err=rec.get("error"))), flush=True)

def _rows(name):
    p = ROOT / R79M / name
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def fetch_efcgt_xml():
    rows = [r for r in _rows("query_execution.jsonl") if r["query_id"] == "R79-EFCGT-INDEX" and r.get("status_code")]
    if not rows: raise RuntimeError("INDEX_MISSING")
    keys = rows[-1]["advertised_keys"]
    xmls = [k for k in keys if re.fullmatch(r"PMC12310836\.(\d+)/PMC12310836\.\1\.xml", k["Key"])]
    if not xmls:
        print(json.dumps(dict(note="EfCGT1 not in PMC OA bulk subset; canonical-HTML route deferred to its own G5 batch")), flush=True); return
    chosen = max(xmls, key=lambda k: int(re.match(r"PMC12310836\.(\d+)/", k["Key"]).group(1)))
    rec = http_get("https://pmc-oa-opendata.s3.amazonaws.com/" + chosen["Key"], "article_version",
                   "advertised OA JATS original for EfCGT1; sealed custody only, no content read")
    append(R79M / "query_execution.jsonl", dict(query_id="R79-EFCGT-XML", status=rec.get("status"),
        status_code=rec.get("status_code"), raw_pointer={k: rec.get(k) for k in ("path", "sha256", "bytes")}, error=rec.get("error")))
    print(json.dumps(dict(q="R79-EFCGT-XML", status=rec.get("status_code"), bytes=rec.get("bytes"))), flush=True)

def finish():
    rows = [r for r in _rows("query_execution.jsonl") if r.get("status_code")]
    att = physical_attempts()
    oa = {r["query_id"]: r.get("projection") for r in rows if r["query_id"].startswith("R79-OA")}
    save(R79M / "access_verification_summary.json", dict(task=T, at=now(), planned=7, executed=len(rows),
        physical_HTTP_global=len(att), physical_bytes_global=sum(int(x.get("bytes") or 0) for x in att),
        openalex=oa, MCTS_added=0, content_read=False))
    print(json.dumps(dict(executed=len(rows), phys=len(att), phys_bytes=sum(int(x.get("bytes") or 0) for x in att))), flush=True)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "prereg": prereg()
    elif mode == "run": run()
    elif mode == "efcgt": fetch_efcgt_xml()
    elif mode == "finish": finish()
    else: raise SystemExit("prereg | run | efcgt | finish")
