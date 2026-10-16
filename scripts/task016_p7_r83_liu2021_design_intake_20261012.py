"""R83: C-E03 design intake - liu2021 (JAFC 2021, 10.1021/acs.jafc.1c00602).

Owner-approved sequencing: this C8-cluster original is read NOW as C-E03 design
corpus (intake_manifest fresh_sequencing.C8_cluster), becoming a late_prior_design
source; he2019/qiu2021/thesis remain unread as the prospective fresh pool.
"""
import hashlib, json, re, subprocess, tempfile, urllib.parse, urllib.request, urllib.error, uuid
from pathlib import Path
from datetime import datetime, timezone
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "C/E03/design/C-E03-R83-liu2021-design-intake-v1"
RAW = Path("data/raw/task016-p7/C/E03/C-E03-R83-liu2021-crossref-custody-v1")
LOCK = B / "source_budget_acquisition.lock"
PDF = dict(path="data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P2-2-liu2021.pdf",
           sha256="13e8307b75d4abcfcfbcf7f94d17ef03ccc169c6109f430c05b28e3519d8701f")
DOI = "10.1021/acs.jafc.1c00602"
TOKENS = ["doi:10.1021/acs.jafc.1c00602"]
CTX = re.compile(r"C-glycos|C-glucos|\b8-C\b|\b6-C\b|C-8|C-6|CGT|C-glucosyltransferase|glycosyltransferase|luteolin|chrysin|apigenin|scutellarein|kaempferol|quercetin|tricin|UE[TC]|UDP|NMR|HMBC|NOESY|standard|specificity|donor|sugar donor", re.I)
READERS = [("A4", "a4-pdftotext-layout-v1", ["-layout"]), ("A5", "a5-pdftotext-raw-v1", ["-raw"])]

def now2(): return datetime.now(timezone.utc).isoformat()
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
            sub = counter([r for r in attempts if "C" in Path(r.get("path", "")).parts])
            same = [r for r in attempts if canonical(r["url"]) == canonical(url)]
            if len(same) >= 2: return dict(result="rejected_old_url", status_code=None)
            if before["HTTP"] + 1 > 8000: raise RuntimeError("GLOBAL_BUDGET_STOP")
            aid = "R83-" + uuid.uuid4().hex; start = now2()
            append(OUT / "physical_request_preregistration.jsonl", dict(attempt_id=aid, url=url, kind=kind,
                registered_at=start, batch_SHA=sha_file(OUT / "precontract.json"), budget_before=before))
            data = b""; status = None; err = None
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 (public science metadata)", "Accept-Encoding": "identity"})
                try: resp = urllib.request.build_opener(NoRedirect()).open(req, timeout=90)
                except urllib.error.HTTPError as e: resp = e; err = "HTTP_" + str(e.code)
                status = resp.code
                data = resp.read(2 * 1024**2 + 1)
                if len(data) > 2 * 1024**2: data = data[:2 * 1024**2]; err = "OBJECT_LIMIT_TRUNCATED"
            except Exception as e: err = type(e).__name__ + ":" + str(e)[:150]
            finally:
                try: resp.close()
                except Exception: pass
            ptr = RAW / (aid + ".bin"); p = ROOT / ptr
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists(): raise RuntimeError("RAW_IMMUTABLE_EXISTS")
            p.write_bytes(data); p.chmod(0o444)
            event(T, "write_binary", path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            rec = dict(attempt_id=aid, url=url, kind=kind, role=kind, phase="metadata_identity_only",
                       batch_id="C-E03-R83-liu2021-design-intake", status_code=status, bytes=len(data),
                       status="available" if status == 200 and not err else "failed", error=err,
                       path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), started_at=start, finished_at=now2(),
                       scientific_body_content_read=False, chemical_extracted=False, metadata_only=True, no_content_read=True)
            event(T, "source_http", **rec)
            return rec
        finally:
            import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def extract(pdf_bytes, mode):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes); path = f.name
    try:
        return subprocess.run(["pdftotext"] + mode + [path, "-"], capture_output=True, text=True, check=True).stdout
    finally:
        Path(path).unlink(missing_ok=True)

def harvest(text):
    lines = []
    for i, ln in enumerate(text.splitlines()):
        if CTX.search(ln) and len(ln.strip()) > 25:
            lines.append(dict(line=i + 1, text=ln.strip()[:400]))
    paras = []
    for pp in re.split(r"\n\s*\n", text):
        if len(pp) > 200 and CTX.search(pp):
            paras.append(re.sub(r"\s+", " ", pp)[:1500])
    return dict(lines=lines[:200], paragraphs=paras[:30])

def main():
    if (ROOT / OUT).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    save(OUT / "precontract.json", dict(task=T, epoch_id="C-E03", family="C",
        batch="C-E03-R83-liu2021-design-intake", created_at=now2(),
        approval_type="agent_delegated", human_reviewed=False,
        purpose="C-E03 design-corpus intake: dual-acceptor C8 scope build supports from liu2021 (JAFC 2021); reading sanctioned by owner-approved continuation plan (intake_manifest fresh_sequencing.C8_cluster: content reads DEFERRED to C-E03 design/freeze sequencing)",
        sequencing_consequence="liu2021 becomes late_prior_design (build-support corpus); he2019/qiu2021/thesis remain unread prospective fresh pool",
        registered_input_SHA={PDF["path"]: PDF["sha256"]},
        planned_routes=["crossref_metadata_identity", "owner_supplied_pdf_dual_reader_read"],
        limits=dict(HTTP=3, bytes=4 * 1024**2), no_paywall_bypass=True))
    # identity: front matter + Crossref metadata
    data = (ROOT / PDF["path"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == PDF["sha256"], "CUSTODY_DRIFT"
    fm = {}
    for mode in (["-layout"],):
        txt = extract(data, mode)
        head = "\n".join(txt.splitlines()[:40])
        fm["front_matter_head"] = head[:2000]
    rec = http_get("https://api.crossref.org/works/" + DOI, "metadata", "publisher metadata identity for liu2021 (design corpus)")
    save(OUT / "query_plan.json", dict(task=T, planned=1, slots=[dict(kind="metadata", query_id="R83-CR-01", url="https://api.crossref.org/works/" + DOI, reason="publisher metadata identity reconciliation for the preregistered DOI")], registered_at=now2()))
    append(OUT / "query_execution.jsonl", dict(query_id="R83-CR-01", status=rec.get("status"), status_code=rec.get("status_code"),
        url=rec.get("url"), raw_pointer={k: rec.get(k) for k in ("path", "sha256", "bytes")}, error=rec.get("error"),
        scientific_body_content_read=False, chemical_extracted=False))
    crossref = None
    if rec.get("status") == "available":
        try:
            j = json.loads((ROOT / rec["path"]).read_text())
            m = j["message"]
            crossref = dict(DOI=m.get("DOI"), title=(m.get("title") or [None])[0],
                container_title=(m.get("container-title") or [None])[0], year=(m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                volume=m.get("volume"), page=m.get("page"), publisher=m.get("publisher"))
        except Exception as e:
            crossref = dict(parse_error=type(e).__name__ + ":" + str(e)[:120])
    save(OUT / "A3_identity.json", dict(task=T, at=now2(), source_id="C-E03-R83-S01-liu2021", DOI=DOI,
        expected_from_intake_manifest=dict(expected_doi=DOI, expected_year=2021, file="P2-2-liu2021.pdf", sha256=PDF["sha256"], identity_status="provisionally_verified_front_matter_only"),
        crossref=crossref, front_matter_head_sha256=hashlib.sha256(fm["front_matter_head"].encode()).hexdigest(),
        unresolved_conflicts=[], identity_lane="design corpus (late_prior_design); A3-grade fresh identity reconciliation deferred to any future G5 preregistration",
        approval_type="agent_delegated", human_reviewed=False))
    # dual readers
    outs = {}
    for role, rid, mode in READERS:
        dest = OUT / role
        common = dict(task=T, approval_type="agent_delegated", human_reviewed=False, family="C", epoch_id="C-E03",
            batch_id="C-E03-R83-liu2021-design-intake", reader_role=role, reader_id="R83-" + role + "-" + str(uuid.uuid4().hex[:8]),
            source_id="C-E03-R83-S01-liu2021", DOI=DOI, closure_tokens=TOKENS, raw_files=[PDF], development_exposed=True,
            prior_design=True, exposure_type="late_prior_design", future_fresh_eligible=False, current_epoch_fresh_eligible=False,
            read_other_extractor_output=False, read_model_outcome=False,
            scientific_read_lane="C-E03 design-corpus read (owner-approved C8 sequencing)")
        put(dest / "scientific_read_started.json", dict(common, event_type="scientific_read_started", timestamp=now2(), scientific_content_read=False))
        text = extract(data, mode)
        obs = harvest(text)
        out = dest / "article_text_harvest.json"
        put(out, dict(common, event_type="scientific_read_completed", timestamp=now2(), scientific_content_read=True,
            parser_mode=str(mode), chars=len(text), output_pointer=None,
            reaction_claim_lines=obs["lines"], reaction_claim_paragraphs=obs["paragraphs"],
            chemical_reaction_enumeration_complete=False, structure_records_deferred_to_A6=True))
        put(dest / "role_manifest.json", dict(common, agent_role=role, epoch_id="C-E03", timestamp=now2(),
            input_manifest_sha={PDF["path"]: PDF["sha256"], str(OUT / "precontract.json"): sha_file(OUT / "precontract.json")},
            output_file_sha={str(out): sha(out)}, counts=dict(processed=1, passed=0, rejected=0, pending=1),
            errors=[], read_holdout=True, read_model_outcome=False, source_evidence_pointers=[PDF],
            count_unit="one design-corpus text extraction; no fresh qualification granted"))
        outs[role] = dict(chars=len(text), lines=len(obs["lines"]), paragraphs=len(obs["paragraphs"]), output=str(out))
        event(T, "R83_design_read_completed", role=role, chars=len(text))
    rows = []
    for role in ("A4", "A5"):
        for ev in ("scientific_read_started.json", "scientific_read_completed.json"):
            row = json.loads((ROOT / OUT / role / ev).read_text())
            rows.append({k: row[k] for k in ("task", "approval_type", "human_reviewed", "family", "epoch_id", "batch_id",
                "reader_role", "reader_id", "source_id", "DOI", "closure_tokens", "raw_files", "development_exposed",
                "prior_design", "exposure_type", "future_fresh_eligible", "current_epoch_fresh_eligible",
                "read_other_extractor_output", "read_model_outcome", "event_type", "timestamp", "scientific_content_read")})
    write(T, str(OUT / "scientific_exposure_reads.jsonl"), "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    save(OUT / "A0_batch_summary.json", dict(task=T, at=now2(), batch="C-E03-R83-liu2021-design-intake", DOI=DOI,
        custody=PDF, crossref_status=rec.get("status"), readers=outs, exposure_rows=len(rows),
        next_step="A6 design-evidence determination: which dual acceptors and what C-site structural evidence; then G2/G3 scope build",
        approval_type="agent_delegated", human_reviewed=False))
    print(json.dumps(dict(crossref=rec.get("status"), a4_chars=outs["A4"]["chars"], a5_chars=outs["A5"]["chars"],
                          a4_lines=outs["A4"]["lines"], a5_lines=outs["A5"]["lines"])))

if __name__ == "__main__":
    main()
