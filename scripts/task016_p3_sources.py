"""TASK-016-P3 bounded public acquisition; independent P3 counters and namespace.

Commands:
  plan    -- write query_plan.json (round R1 inherited queue, round R2 targeted discovery)
             and the frozen R1 intake list. No network.
  acquire -- execute R2 discovery (Europe PMC lite + citation tracing), title-based
             pre-registered selection, then R1+R2 article acquisition through the
             official PMC OA package route with SI text extraction and full accounting.

Budgets (approval.json): 4 GiB bytes / 4000 direct HTTP / 8000 metadata keys /
150 article versions / 300 attachments / per-file 256 MiB / per-URL 2 attempts /
concurrency 4. Reuse of verified prior raw files is not a new download.
"""
import hashlib, json, re, sys, threading, time, zipfile, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode, unquote, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P3"
OUT = ROOT / "outputs/task016-p3/v1"
RAW = ROOT / "data/raw/task016-p3/2026-10-07"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

MAX_BYTES = 4 * 1024 ** 3
MAX_HTTP = 4000
MAX_META = 8000
MAX_ARTICLES = 150
MAX_ATTACH = 300
PER_FILE = 256 * 1024 ** 2
ROLE_LIMIT = {
    "listing": 4 * 1024 ** 2,
    "metadata": 8 * 1024 ** 2,
    "discovery-json": 16 * 1024 ** 2,
    "citation-json": 16 * 1024 ** 2,
    "fullTextXML": 64 * 1024 ** 2,
    "supplement": PER_FILE,
}
INHERIT_LEDGERS = [
    ROOT / "outputs/task016-p1/v1/acquisition_attempts.jsonl",
    ROOT / "outputs/task016-p2/v1/acquisition_attempts.jsonl",
]
P2V2 = ROOT / "outputs/task016-p2/v2"
P2V1 = ROOT / "outputs/task016-p2/v1"
LOCK = threading.Lock()
B = "https://pmc-oa-opendata.s3.amazonaws.com/"


def rows(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []


def save(name, v, jl=False):
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in v) if jl else json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    write(TASK, str((OUT / name).relative_to(ROOT)), text)


def append(name, v):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")
    event(TASK, "append_evidence", path=str(p.relative_to(ROOT)), entry=v)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def get(url, provider, role, name=None, limit=None):
    """Bounded acquisition with P3 ceilings; verified reuse is not a new attempt."""
    limit = limit or ROLE_LIMIT.get(role, PER_FILE)
    with LOCK:
        history = rows(OUT / "acquisition_attempts.jsonl")
        inherited = []
        for p in INHERIT_LEDGERS:
            inherited.extend(rows(p))
        good = [r for r in history + inherited if r.get("url") == url and r.get("status") == "raw_available" and r.get("path")]
        if good:
            r = good[-1]
            assert hashlib.sha256((ROOT / r["path"]).read_bytes()).hexdigest() == r["sha256"]
            if r not in history:
                append("reused_files.jsonl", dict(**r, reuse_task=TASK, reused_at=stamp()))
            return r
        previous = [r for r in history if r.get("url") == url]
        if len(previous) >= 2:
            return previous[-1]
    for attempt in range(len(previous) + 1, 3):
        with LOCK:
            history = rows(OUT / "acquisition_attempts.jsonl")
            external = rows(OUT / "external_discovery_receipts.jsonl")
            reservations = rows(OUT / "acquisition_reservations.jsonl")
            assert len(reservations) + sum(r["request_units"] for r in external) < MAX_HTTP, "P3 HTTP attempt ceiling"
            total = sum(r.get("bytes", 0) for r in history)
            done = {(r["url"], r["attempt"]) for r in history}
            reserved = sum(r.get("limit", 0) for r in reservations if (r["url"], r["attempt"]) not in done)
            assert total + reserved + limit <= MAX_BYTES, "P3 raw byte ceiling"
            if role in ["fullTextXML", "supplement"]:
                cap = MAX_ARTICLES if role == "fullTextXML" else MAX_ATTACH
                assert len({r["url"] for r in history if r["content_role"] == role} | {url}) <= cap, "P3 article/attachment ceiling"
            key = hashlib.sha256(url.encode()).hexdigest()[:24]
            target = RAW / provider / key / (role + ".attempt-" + str(attempt))
            assert not target.exists(), "immutable raw snapshot"
            reservation = dict(url=url, provider=provider, content_role=role, name=name, attempt=attempt, status="in_progress", limit=limit, started_at=stamp())
            append("acquisition_reservations.jsonl", reservation)
        data = b""; status = None; error = None; headers = {}; wait = 1
        try:
            with urlopen(Request(url, headers={"User-Agent": "FlavoRetro-TASK016-P3/0.1"}), timeout=60) as response:
                status = response.status
                headers = {k: response.headers.get(k) for k in ["Content-Type", "ETag", "Last-Modified"]}
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError("per-file bound exceeded")
        except HTTPError as exc:
            status = exc.code
            error = str(exc)
            data = exc.read(min(limit, 1024 ** 2))
            try:
                wait = min(45, max(1, int(exc.headers.get("Retry-After", "1"))))
            except ValueError:
                wait = 2
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o444)
        result = dict(**{k: v for k, v in reservation.items() if k != "status"}, path=str(target.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), status_code=status, headers=headers, error=error, status="raw_available" if status == 200 and not error else "unavailable", acquired_at=stamp())
        with LOCK:
            append("acquisition_attempts.jsonl", result)
        event(TASK, "open_download", **result)
        if result["status"] == "raw_available" or status in [400, 401, 403, 404, 429]:
            return result
        if attempt < 2:
            time.sleep(wait)
    return result


# ---------------------------------------------------------------- plan

R1_TARGETED = [
    # pmcid, inherited link, question to resolve (contract G1 table)
    ("PMC9700910", "unresolved+withdrawn", "two withdrawn C8 encodings need complete sugar stereo bound to a single-step identity from the original TcCGT paper chain"),
    ("PMC10465961", "unresolved", "C-rhamnosyl intermediate vs dehydrated final product; single-step identity"),
    ("PMC6255700", "unresolved", "SS acceptor sugar/donor, 2/3 linkage and anomeric config for Ib3GGT products"),
    ("PMC3507004", "unresolved", "SS sambubioside complete acceptor/donor/linkage"),
    ("PMC12313340", "unresolved", "Q-g-r-g Glc(1->3)Rha on rutin; encode linkage identity"),
    ("PMC4282749", "unresolved", "closure overlap with old UGT79B6 reactions; no new holdout"),
    ("PMC4494776", "unresolved", "closure overlap with old K-sophoroside; build-only"),
    ("PMC10706860", "extension_review", "PcApiT apiin overlap; broader substrate activity not admitted"),
    ("PMC11502824", "extension_review", "chemical C-glycosylation SI graphic structures unencoded"),
    ("PMC12790375", "extension_review", "chemical C-glycosylation graphic structures unencoded"),
    ("PMC13035923", "extension_review", "chemical C-glycosylation SI graphic structures unencoded"),
    ("PMC13421352", "extension_review", "radical C-glycosylation; SI1 oversized in P2 - retry under 256 MiB budget"),
    ("PMC12993211", "extension_review", "body C-glycoside vs SI 7-O-glycoside conflict retained"),
    ("PMC7060329", "unresolved", "phloretin/nothofagin exact overlap; C-Ara MS-only assignment pending"),
]


def plan():
    pending = [json.loads(l) for l in (P2V2 / "metadata_dispositions.jsonl").read_text().splitlines()
               if json.loads(l)["disposition"] == "pending_source_only_title_candidate_not_acquired"]
    assert len(pending) == 35
    r1_items = [dict(pmcid=r["pmcid"], doi=r.get("doi"), title=re.sub("<[^>]+>", " ", r["title"]), inherited_disposition=r["disposition"], link="pending_title_candidate") for r in pending]
    r1_items += [dict(pmcid=p, doi=None, title=None, inherited_disposition=link, link=link, resolve=q) for p, link, q in R1_TARGETED]

    families = [
        # round R2: independent targeted discovery (Europe PMC lite unless noted)
        dict(family="c-enzyme-alias", purpose="gene/enzyme aliases of CGTs not queried in P2",
             queries=["(OsCGT OR GgCGT OR MiCGT OR ZjCGT OR CuCGT OR DcCGT OR SaCGT OR UGT708) AND OPEN_ACCESS:Y",
                      "(TcCGT) AND OPEN_ACCESS:Y",
                      "(GuCGT OR MaCGT OR PcCGT OR PlCGT OR WbGT OR CaCGT) AND OPEN_ACCESS:Y"]),
        dict(family="c-products", purpose="named flavonoid C-glycoside products with biosynthesis/CGT evidence",
             queries=["(isovitexin OR isoorientin OR vicenin OR shaftoside OR schaftoside OR lucenin) AND (biosynthesis OR glycosyltransferase OR CGT) AND OPEN_ACCESS:Y",
                      "(mangiferin OR neomangiferin OR aspalathin) AND (glycosyltransferase OR biosynthesis OR CGT) AND OPEN_ACCESS:Y"]),
        dict(family="c-intermediate", purpose="explicit 2-hydroxyflavanone/C-glycosyl intermediate single-step route",
             queries=["(2-hydroxyflavanone OR 2-hydroxynaringenin) AND (glycosyltransferase OR C-glycoside OR dehydratase) AND OPEN_ACCESS:Y",
                      "(C-glycosylation OR C-glucosylation) AND (enzymatic OR glycosyltransferase) AND (flavonoid OR phloroglucinol OR benzophenone OR xanthone) AND OPEN_ACCESS:Y"]),
        dict(family="c-chemical", purpose="chemical synthesis routes to flavonoid C-glycosides (incl. O-to-C rearrangement)",
             queries=["(vitexin OR isovitexin OR orientin OR isoorientin) AND (synthesis OR synthetic) AND OPEN_ACCESS:Y",
                      "(C-glycoside OR C-glucoside) AND (synthesis OR glycosylation) AND (flavone OR flavonol OR flavanone OR chromone) AND OPEN_ACCESS:Y",
                      "(O-to-C OR Fries) AND (glycoside OR glycosylation OR rearrangement) AND (flavonoid OR flavone) AND OPEN_ACCESS:Y"]),
        dict(family="ss-linkage", purpose="SS with different acceptor sugars / linkage sites",
             queries=["(gentiobioside OR laminaribioside) AND (flavonoid OR flavonol OR anthocyanin) AND (glycosyltransferase OR biosynthesis) AND OPEN_ACCESS:Y",
                      "(robinobioside OR neohesperidoside OR rutinoside) AND (glycosyltransferase OR biosynthesis OR rhamnosyltransferase) AND OPEN_ACCESS:Y",
                      "(apiosyltransferase OR apiin OR apiose) AND (flavone OR flavonoid) AND OPEN_ACCESS:Y",
                      "(glycosyltransferase OR rhamnosyltransferase OR xylosyltransferase OR arabinosyltransferase) AND (flavonol OR quercetin OR kaempferol OR anthocyanidin) AND (sophoroside OR sambubioside OR gentiobioside OR diglycoside OR triglycoside) AND OPEN_ACCESS:Y"]),
        dict(family="ss-enzyme-alias", purpose="SS enzyme aliases incl. UGT91/94 and flavonoid glycoside GTs",
             queries=["(Ib3GGT OR UGT94B1 OR CsFGT1 OR AcF3GGT OR Ph4CGT) AND OPEN_ACCESS:Y",
                      "(flavonol 3-O-glucoside) AND (glucosyltransferase OR glycosyltransferase) AND (sophoroside OR 2-O-glucosylated) AND OPEN_ACCESS:Y"]),
        dict(family="ss-chemical", purpose="chemical glycosylation of flavonoid glycoside acceptors",
             queries=["(glycosylation) AND (sophorose OR gentiobiose OR rutinose) AND (flavonoid OR quercetin OR kaempferol) AND (synthesis OR synthetic) AND OPEN_ACCESS:Y"]),
        dict(family="citation-chase", purpose="backward/forward citation tracing for TcCGT and PcApiT source chains",
             queries=["https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9700910/citations?pageSize=100&format=json",
                      "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10706860/citations?pageSize=100&format=json"]),
    ]
    qplan = []
    for fam in families:
        for q in fam["queries"]:
            if q.startswith("http"):
                url = q
                role = "citation-json"
            else:
                url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urlencode(
                    {"query": q, "format": "json", "pageSize": 100, "resultType": "lite"})
                role = "discovery-json"
            qplan.append(dict(family=fam["family"], purpose=fam["purpose"], interface="europepmc-lite" if role == "discovery-json" else "europepmc-citations",
                              query=q, url=url, role=role, pagination_cap=1, page_size=100,
                              dedup_key="pmcid", stop_reason="single page of 100 or hitCount<100; interface failure after 2 attempts"))
    plan_doc = dict(
        task=TASK, created_at=stamp(), approval="outputs/task016-p3/v1/approval.json",
        round_R1=dict(purpose="dispose inherited queue: 35 pending title candidates + targeted unresolved/withdrawn/extension leads",
                      interface="pmc-oa-opendata listing + fullTextXML/supplement", items=r1_items,
                      dedup_key="pmcid", stop_reason="all items processed or budget ceiling"),
        round_R2=dict(families=families, note="P2 core route 503 history retained; P3 uses lite/citation interfaces only; queries are new families, not re-runs of the failed 19"),
        queries=qplan,
        budgets=dict(bytes=MAX_BYTES, http=MAX_HTTP, metadata=MAX_META, articles=MAX_ARTICLES, attachments=MAX_ATTACH, per_file=PER_FILE),
    )
    save("query_plan.json", plan_doc)
    print("plan queries", len(qplan), "R1 items", len(r1_items))


# ---------------------------------------------------------------- acquire

RE_C = re.compile(r"c-glycosyltransferase|c-glucosyltransferase|c-rhamnosyltransferase|c-xylosyltransferase|c-glycosylation|c-glucosylation|c-glycoside|c-glucoside|c-glycosyl", re.I)
RE_SS = re.compile(r"sophoros|sambubios|gentiobios|rutinos|robinobios|neohesperid|apiosyl|apiin|apiose|sugar chain|diglycosid|triglycosid|second sugar|2''-o|3''-o|6''-o|1,2-rhamnosyl", re.I)
RE_CHEM = re.compile(r"synthesis|synthetic|glycosylation method|total synthesis|rearrangement", re.I)
RE_FLAV = re.compile(r"flavo|phloretin|dihydrochalcone|chromone|xanthone|benzophenone|mangiferin|vitexin|orientin|nothofagin|aspalathin|quercetin|kaempferol|naringenin|anthocyan|cyanidin|isoflavon|hesperetin|apigenin|luteolin|myricetin|genistein|tricetin", re.I)
RE_EXCL = re.compile(r"review|perspective|overview|ginsenoside|saponin|mogroside|terpenoid|triterpen|nucleoside|antibiotic|glycoprotein|n-glycos|glycolipid|steviol|crocin|crocetin|bibenzyl|polyphyllin|nosiheptide|lignin|oleanane|asiaticoside|madecassoside|rhamnogalacturonan|mycobacter|antibiotic resistance|immobilization|scaffold", re.I)


def classify(title):
    t = re.sub("<[^>]+>", " ", title or "")
    flav = bool(RE_FLAV.search(t))
    if RE_EXCL.search(t) and not flav:
        return None, "excluded non-flavonoid/review by frozen title rule"
    if RE_C.search(t) and flav:
        return "C_formation", "title rule: C-glycosyl bond + flavonoid-family context"
    if RE_SS.search(t) and (flav or RE_SS.search(t)):
        return "sugar_sugar_formation", "title rule: sugar-chain/linkage + flavonoid context"
    if RE_CHEM.search(t) and RE_C.search(t):
        return "C_formation_chemical", "title rule: chemical C-glycoside synthesis"
    return None, "title not a targeted C/SS primary study"


def discovery():
    plan_doc = json.loads((OUT / "query_plan.json").read_text())
    ledger = []
    records = []
    for q in plan_doc["queries"]:
        raw = get(q["url"], "europepmc", q["role"], q["family"])
        entry = dict(family=q["family"], query=q["query"], url=q["url"], status=raw["status"], sha256=raw["sha256"], path=raw["path"], hits=None, returned=0)
        if raw["status"] == "raw_available":
            try:
                d = json.loads((ROOT / raw["path"]).read_text())
                entry["hits"] = d.get("hitCount")
                rs = d.get("resultList", {}).get("result", []) or d.get("citationList", {}).get("citation", [])
                entry["returned"] = len(rs)
                for r in rs:
                    pmcid = r.get("pmcid")
                    if pmcid:
                        records.append(dict(pmcid=pmcid, doi=r.get("doi"), title=r.get("title") or r.get("source", ""),
                                            year=r.get("pubYear"), family=q["family"], raw_path=raw["path"], raw_sha256=raw["sha256"]))
            except ValueError as exc:
                entry["error"] = str(exc)
        ledger.append(entry)
        print("query", q["family"], entry["status"], entry["hits"], entry["returned"], flush=True)
    save("query_ledger.json", dict(executed=ledger, executed_at=stamp()))
    by = {}
    for r in records:
        by.setdefault(r["pmcid"], {**r, "families": []})
        by[r["pmcid"]]["families"].append(r["family"])
    save("discovery_records.jsonl", sorted(by.values(), key=lambda r: r["pmcid"]), True)
    return sorted(by.values(), key=lambda r: r["pmcid"])


def available_article(rec):
    """Official PMC OA package route; adapted from the P1 adapter with P3 budget binding."""
    pmc = rec["pmcid"]
    result = dict(pmcid=pmc, title=rec.get("title"), discovery=rec.get("families") or rec.get("link"), files=[], status="unavailable", review_type="agent_delegated", independent_chemical_validation=False)
    raw = get(B + "?" + urlencode({"list-type": 2, "prefix": pmc + ".", "max-keys": 100}), "pmc", "listing", pmc)
    result["files"].append(raw)
    if raw["status"] != "raw_available":
        return result
    try:
        keys = [el.text for el in ET.parse(ROOT / raw["path"]).findall(".//{*}Key")]
    except ET.ParseError:
        result["status"] = "invalid_listing"
        return result
    metas = []
    for key in sorted(k for k in keys if k.endswith(".json"))[:2]:
        m = get(B + key, "pmc", "metadata", pmc + "-" + hashlib.sha256(key.encode()).hexdigest()[:8])
        result["files"].append(m)
        if m["status"] == "raw_available":
            try:
                metas.append((json.loads((ROOT / m["path"]).read_text()), m))
            except ValueError:
                pass
    metas.sort(key=lambda t: (t[0].get("is_manuscript") in [True, "yes"], str(t[0].get("version"))))
    if not metas:
        x = get("https://www.ebi.ac.uk/europepmc/webservices/rest/" + pmc + "/fullTextXML", "europepmc", "fullTextXML", pmc)
        result["files"].append(x)
        if x["status"] == "raw_available":
            try:
                root = ET.parse(ROOT / x["path"]).getroot()
                lic = root.find(".//license")
                license_text = "".join(lic.itertext()) if lic is not None else ""
                if lic is None or "creativecommons.org" not in ET.tostring(lic, encoding="unicode"):
                    result["status"] = "license_pending"
                    return result
                result.update(status="fulltext_available", xml=x, license=license_text, article_version="EuropePMC-deposit", supplement_status="cloud_listing_empty; not acquired")
            except ET.ParseError:
                result["status"] = "format_error"
        return result
    meta, m = metas[0]
    license_code = meta.get("license_code")
    result.update(license=license_code, article_version=meta.get("version"), article_metadata=m)
    if meta.get("is_retracted") in [True, "yes"] or not str(license_code).startswith("CC"):
        result["status"] = "retracted_or_license_pending"
        return result
    urls = [meta.get("xml_url")] + [u for u in meta.get("media_urls", []) if unquote(urlparse(u).path).lower().endswith((".pdf", ".docx", ".xlsx", ".csv", ".zip", ".doc", ".xls"))][:4]
    for index, u in enumerate(urls):
        if not u:
            continue
        u = u.replace("s3://pmc-oa-opendata/", B)
        x = get(u, "pmc", "fullTextXML" if index == 0 else "supplement", pmc + "-v" + str(meta.get("version")) + "-" + str(index))
        result["files"].append(x)
        if x["status"] == "raw_available":
            expected = parse_qs(urlparse(u).query).get("md5", [None])[0]
            x["official_md5_verified"] = expected is not None and hashlib.md5((ROOT / x["path"]).read_bytes()).hexdigest() == expected
            if not x["official_md5_verified"]:
                x["semantic_status"] = "hash_failed"
                continue
            if index == 0:
                try:
                    ET.parse(ROOT / x["path"])
                except ET.ParseError:
                    x["semantic_status"] = "format_error"
                    continue
                result.update(status="fulltext_available", xml=x)
    return result


def retry_pmc13421352_si(manifest):
    """P2 SI1 failed at the 32 MiB boundary; retry once under the P3 256 MiB pre-registered budget."""
    p2_attempts = rows(P2V1 / "acquisition_attempts.jsonl")
    si = [r for r in p2_attempts if r.get("name") and "PMC13421352" in str(r.get("name")) and r["content_role"] == "supplement" and r["status"] != "raw_available"]
    seen = sorted({r["url"] for r in si})
    outcomes = []
    for url in seen:
        res = get(url, "pmc", "supplement", "PMC13421352-si-retry-256MiB", limit=PER_FILE)
        outcomes.append(dict(url=url, p2_status="unavailable_at_32MiB", p3_status=res["status"], sha256=res["sha256"], bytes=res["bytes"], path=res.get("path")))
        print("si-retry", url[:90], res["status"], res["bytes"], flush=True)
    return outcomes


def extract_si_text(articles):
    records = []
    for a in articles:
        pmc = a["pmcid"]
        if a["status"] != "fulltext_available":
            continue
        for f in a["files"]:
            if f["content_role"] != "supplement":
                continue
            if f["status"] != "raw_available" or not f.get("official_md5_verified", True):
                records.append(dict(pmcid=pmc, raw_path=f["path"], raw_sha256=f["sha256"], status="retained_unavailable", error=f.get("error")))
                continue
            path = ROOT / f["path"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == f["sha256"]
            data = path.read_bytes()

            def extract_one(label, blob):
                h = hashlib.sha256(blob).hexdigest()
                dest = OUT / "attachment-text" / pmc / (h[:24] + ".txt")
                text, status, error = None, "unparsed_format", None
                if blob.startswith(b"%PDF"):
                    r = subprocess.run(["pdftotext", "-layout", "-", "-"], input=blob, capture_output=True)
                    text = r.stdout.decode("utf8", "replace")
                    error = r.stderr.decode("utf8", "replace")[-1500:] or None
                    status = "parsed_text" if r.returncode == 0 and text.strip() else "empty_scanned_or_parse_failure"
                elif label.endswith(".xml"):
                    try:
                        text = "\n".join("".join(p.itertext()) for p in ET.fromstring(blob).findall(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"))
                        status = "parsed_text"
                    except Exception as ex:
                        error, status = str(ex), "parse_failure"
                rec = dict(pmcid=pmc, raw_path=f["path"], raw_sha256=f["sha256"], member=label, member_sha256=h, status=status, error=error, characters=len(text) if text else 0,
                           derived_text_path=None, identity_admission=False)
                if text is not None:
                    write(TASK, str(dest.relative_to(ROOT)), text)
                    rec["derived_text_path"] = str(dest.relative_to(ROOT))
                records.append(rec)

            if data.startswith(b"%PDF"):
                extract_one("attachment.pdf", data)
            elif zipfile.is_zipfile(path):
                with zipfile.ZipFile(path) as z:
                    for item in z.infolist():
                        if item.file_size > PER_FILE or item.is_dir():
                            continue
                        if item.filename == "word/document.xml" or item.filename.lower().endswith(".pdf"):
                            extract_one(item.filename, z.read(item))
                        elif item.filename.startswith("word/media/"):
                            records.append(dict(pmcid=pmc, raw_path=f["path"], raw_sha256=f["sha256"], member=item.filename, status="embedded_image_not_structurally_encoded", member_sha256=hashlib.sha256(z.read(item)).hexdigest()))
            else:
                records.append(dict(pmcid=pmc, raw_path=f["path"], raw_sha256=f["sha256"], status="retained_unparsed_format", identity_admission=False))
    return records


def acquire():
    plan_doc = json.loads((OUT / "query_plan.json").read_text())
    discovered = discovery()
    meta_count = len(discovered)
    assert meta_count <= MAX_META, "P3 metadata ceiling"
    selected = []
    for r in discovered:
        cat, reason = classify(r["title"])
        r["p3_category"] = cat
        r["selection_reason"] = reason
        if cat:
            selected.append(r)
    selected = selected[:80]
    save("discovery_selection.json", dict(rule="frozen title regex before any extraction/template/model outcome; agent_delegated", total=len(discovered), selected=len(selected), records=selected))

    r1 = plan_doc["round_R1"]["items"]
    intake = [dict(pmcid=i["pmcid"], title=i.get("title"), link=i["link"], families=None) for i in r1]
    intake += [dict(pmcid=r["pmcid"], title=r["title"], link="R2:" + ",".join(r["families"]), families=r["families"]) for r in selected if r["pmcid"] not in {i["pmcid"] for i in r1}]
    save("article_intake_plan.json", dict(version=1, selection="frozen source/title rule before extraction/templates/model results", records=intake))
    print("intake", len(intake), flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, item in enumerate(pool.map(available_article, intake)):
            results.append(item)
            save("article_acquisition_manifest.json", results)
            print(i + 1, item["pmcid"], item["status"], flush=True)

    si_retries = retry_pmc13421352_si(results)
    save("si_retry_manifest.json", si_retries)

    segments = []
    for item in results:
        if item["status"] != "fulltext_available":
            continue
        root = ET.parse(ROOT / item["xml"]["path"]).getroot()
        doi = root.find(".//article-id[@pub-id-type='doi']")
        for tag in ["p", "table-wrap", "fig"]:
            for n, el in enumerate(root.findall(".//body//" + tag)):
                text = " ".join("".join(el.itertext()).split())
                segments.append(dict(pmcid=item["pmcid"], doi=doi.text if doi is not None else None, locator=f"body//{tag}[{n+1}]", xml_id=el.get("id"), text=text,
                                     text_sha256=hashlib.sha256(text.encode()).hexdigest(), raw_path=item["xml"]["path"], raw_sha256=item["xml"]["sha256"],
                                     license=item.get("license"), article_version=item.get("article_version")))
    save("article_evidence_segments.jsonl", segments, True)

    att = extract_si_text(results)
    save("attachment_parse_manifest.jsonl", att, True)

    actual = rows(OUT / "acquisition_attempts.jsonl")
    accounting = dict(
        http_attempts=len(rows(OUT / "acquisition_reservations.jsonl")),
        external_units=sum(r["request_units"] for r in rows(OUT / "external_discovery_receipts.jsonl")),
        bytes=sum(r.get("bytes", 0) for r in actual),
        unique_raw_bytes=sum(r.get("bytes", 0) for r in actual if r["status"] == "raw_available"),
        metadata_records=len(discovered),
        article_versions=len({r["url"] for r in actual if r["content_role"] == "fullTextXML" and r["status"] == "raw_available"}),
        attachments=len({r["url"] for r in actual if r["content_role"] == "supplement" and r["status"] == "raw_available"}),
        reused_files=len(rows(OUT / "reused_files.jsonl")),
        articles_available=sum(r["status"] == "fulltext_available" for r in results),
        segments=len(segments), attachments_parsed=sum(1 for r in att if r["status"] == "parsed_text"),
        ceilings=dict(bytes=MAX_BYTES, http=MAX_HTTP, metadata=MAX_META, articles=MAX_ARTICLES, attachments=MAX_ATTACH),
    )
    save("source_accounting.json", accounting)
    dispositions = []
    for item in results:
        dispositions.append(dict(pmcid=item["pmcid"], link=item["discovery"], status=item["status"], license=item.get("license"),
                                 article_version=item.get("article_version"), xml_sha256=item.get("xml", {}).get("sha256"),
                                 n_files=len(item["files"]), next_step="evidence review for C/SS single-step admission" if item["status"] == "fulltext_available" else "acquisition failed/licence pending; retained with reason"))
    save("metadata_dispositions.jsonl", dispositions, True)
    print(json.dumps(accounting, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "plan":
        plan()
    else:
        acquire()
