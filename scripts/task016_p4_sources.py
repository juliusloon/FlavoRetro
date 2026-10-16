"""TASK-016-P4 G3: bounded targeted acquisition for the C-class holdout shortfall.

Commands:
  plan     -- write the frozen query plan and intake list. No network.
  acquire  -- run the plan, then acquire full text + SI through the official PMC OA
              package route, with SI text extraction and full accounting.

Independent P4 counters and namespace. Budgets come from approval.json:
2 GiB bytes / 2000 direct HTTP / 5000 metadata keys / 100 article versions /
180 attachments / per-file 256 MiB / per-URL 2 attempts / concurrency 4.

Purpose is narrow: the G4 panel reached SS 8 targets / 3 groups but C only
1 target / 1 group, because 7 of the 8 structure-complete C reactions come from
development-exposed sources. This stage looks for C-glycosylation primary studies
whose products carry an explicit complete structural assignment, and it prefers
acceptors outside the P1/P2 exposure closure.
"""
import hashlib
import json
import re
import sys
import threading
import time
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
RAW = ROOT / "data/raw/task016-p4/2026-10-07"
sys.path.insert(0, str(ROOT))
from scripts.operate import event, write

MAX_BYTES = 2 * 1024 ** 3
MAX_HTTP = 2000
MAX_META = 5000
MAX_ARTICLES = 100
MAX_ATTACH = 180
PER_FILE = 256 * 1024 ** 2
ROLE_LIMIT = {
    "listing": 4 * 1024 ** 2,
    "metadata": 8 * 1024 ** 2,
    "discovery-json": 16 * 1024 ** 2,
    "citation-json": 16 * 1024 ** 2,
    "fullTextXML": 64 * 1024 ** 2,
    "supplement": PER_FILE,
}
LOCK = threading.Lock()
B = "https://pmc-oa-opendata.s3.amazonaws.com/"

# Reuse of an already-verified P1/P2/P3 raw file is not a new download.
INHERIT_LEDGERS = [
    ROOT / "outputs/task016-p1/v1/acquisition_attempts.jsonl",
    ROOT / "outputs/task016-p2/v1/acquisition_attempts.jsonl",
    ROOT / "outputs/task016-p3/v1/acquisition_attempts.jsonl",
]


def rows(p):
    if not Path(p).exists():
        return []
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(name, v, jl=False):
    text = ("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in v)
            if jl else json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    write(TASK, str((OUT / name).relative_to(ROOT)), text)


def append(name, v):
    p = OUT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")
    event(TASK, "append_evidence", path=str(p.relative_to(ROOT)), entry=v)


def get(url, provider, role, name=None, limit=None):
    limit = limit or ROLE_LIMIT.get(role, PER_FILE)
    with LOCK:
        history = rows(OUT / "acquisition_attempts.jsonl")
        inherited = []
        for p in INHERIT_LEDGERS:
            inherited.extend(rows(p))
        good = [r for r in history + inherited
                if r.get("url") == url and r.get("status") == "raw_available" and r.get("path")]
        if good:
            r = good[-1]
            if hashlib.sha256((ROOT / r["path"]).read_bytes()).hexdigest() == r["sha256"]:
                if r not in history:
                    append("reused_files.jsonl", dict(**r, reuse_task=TASK, reused_at=stamp()))
                return r
        previous = [r for r in history if r.get("url") == url]
        if len(previous) >= 2:
            return previous[-1]
    for attempt in range(len(previous) + 1, 3):
        with LOCK:
            history = rows(OUT / "acquisition_attempts.jsonl")
            assert len(history) < MAX_HTTP, "P4 HTTP attempt ceiling"
            total = sum(r.get("bytes", 0) for r in history)
            assert total + limit <= MAX_BYTES, "P4 raw byte ceiling"
            assert len([r for r in history if r["content_role"] == role]) < (
                MAX_ARTICLES if role == "fullTextXML" else MAX_ATTACH if role == "supplement" else 10 ** 9), \
                f"P4 {role} ceiling"
            assert len({r["url"] for r in history}) < MAX_META, "P4 metadata ceiling"
            key = hashlib.sha256(url.encode()).hexdigest()[:24]
            target = RAW / provider / key / (role + ".attempt-" + str(attempt))
            assert not target.exists(), "immutable raw snapshot"
            reservation = dict(url=url, provider=provider, content_role=role, name=name,
                               attempt=attempt, status="in_progress", limit=limit, started_at=stamp())
            append("acquisition_reservations.jsonl", reservation)
        data = b""
        status = None
        error = None
        headers = {}
        wait = 1
        try:
            with urlopen(Request(url, headers={"User-Agent": "FlavoRetro-TASK016-P4/0.1"}),
                         timeout=60) as response:
                status = response.status
                headers = {k: response.headers.get(k)
                           for k in ["Content-Type", "ETag", "Last-Modified"]}
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
        result = dict(**{k: v for k, v in reservation.items() if k != "status"},
                      path=str(target.relative_to(ROOT)),
                      sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                      status_code=status, headers=headers, error=error,
                      status="raw_available" if status == 200 and not error else "unavailable",
                      acquired_at=stamp())
        with LOCK:
            append("acquisition_attempts.jsonl", result)
        event(TASK, "open_download", **result)
        if result["status"] == "raw_available" or status in [400, 401, 403, 404, 429]:
            return result
        if attempt < 2:
            time.sleep(wait)
    return result


# ---------------------------------------------------------------- plan

FAMILIES = [
    dict(family="c-named-product-nmr",
         purpose="flavonoid C-glycosides whose products are isolated and fully assigned",
         queries=[
             "(C-glycosyltransferase OR C-glucosyltransferase) AND (vitexin OR isovitexin OR orientin OR isoorientin OR vicenin OR lucenin OR mangiferin OR neomangiferin) AND OPEN_ACCESS:Y",
             "(flavonoid C-glycoside OR flavone C-glucoside) AND (NMR OR structure elucidation) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-direct-flavone",
         purpose="direct C-glycosylation of flavones/flavonols, product identity by standard or NMR",
         queries=[
             "(apigenin OR luteolin OR kaempferol OR quercetin OR myricetin OR tricetin) AND (C-glycosylation OR C-glucosylation) AND (glycosyltransferase OR biosynthesis OR engineered) AND OPEN_ACCESS:Y",
             "(6-C-glucosyltransferase OR 8-C-glucosyltransferase OR C-glycosyltransferase) AND (flavone OR flavonol) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-dihydrochalcone",
         purpose="phloretin-type C-glycosylation steps outside the P1/P2 exposure closure",
         queries=[
             "(phloretin OR dihydrochalcone OR phloroglucinol) AND (C-glycosylation OR C-glucosylation) AND (glycosyltransferase OR biosynthesis OR biotransformation) AND OPEN_ACCESS:Y",
             "(nothofagin OR phloretin C-glucoside OR 3'-C-glucosyl) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-chemical-synthesis",
         purpose="chemical C-glycosylation with explicit complete product assignment",
         queries=[
             "(C-glycoside OR C-glucoside) AND (synthesis OR glycosylation) AND (flavone OR flavonol OR flavanone) AND (regioselective OR ortho-directed OR Friedel-Crafts) AND OPEN_ACCESS:Y",
             "(O-to-C OR Fries rearrangement) AND (glycoside OR glycosylation) AND (flavonoid OR flavone) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-new-scaffold",
         purpose="C-glycosylation on acceptors outside the P1/P2 closure: xanthone, benzophenone, chromone, anthocyanidin",
         queries=[
             "(mangiferin OR aspalathin OR gambogic OR xanthone C-glycoside OR benzophenone C-glycoside) AND (glycosyltransferase OR biosynthesis OR C-glycosylation) AND OPEN_ACCESS:Y",
             "(chromone OR benzophenone) AND (C-glycosyltransferase OR C-glycosylation) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-anthocyanin",
         purpose="anthocyanin C-glycosides as a structurally distinct C class",
         queries=[
             "(anthocyanidin OR cyanidin OR delphinidin) AND (C-glycosylation OR C-glucosylation) AND (glycosyltransferase OR biosynthesis) AND OPEN_ACCESS:Y",
         ]),
]

# Sources already inside the P1/P2 development closure. Their chemistry cannot
# seed a clean holdout, so they are only fetched if a query needs them for context.
KNOWN_EXPOSED = {
    "PMC10589286", "PMC11975207", "PMC7558026", "PMC10602602", "PMC10706860",
    "PMC12313340", "PMC4282749", "PMC6255700", "PMC9700910", "PMC7060329",
    "PMC10465961", "PMC12993211", "PMC12658608", "PMC12844164", "PMC4494776",
    "PMC3507004", "PMC12494026", "PMC12984077", "PMC11502824", "PMC12790375",
    "PMC13421352", "PMC10856022", "PMC11273223", "PMC12246196",
}



# Round R2: title-scoped queries. The round-1 body queries were dominated by
# review/omics noise and by papers P3 already held, so R2 constrains the title
# field and names the enzyme/product directly.
FAMILIES_R2 = [
    dict(family="c-title-enzyme",
         purpose="primary studies characterising a novel C-glycosyltransferase, by title",
         queries=[
             "TITLE:\"C-glycosyltransferase\" AND OPEN_ACCESS:Y",
             "TITLE:(\"C-glycosyltransferase\") AND (Dendrobium OR Anemarrhena OR orchid OR bromeliad OR Cyclamen OR Gentiana) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-title-named-product",
         purpose="biosynthesis or flow synthesis of a named C-glycoside, by title",
         queries=[
             "TITLE:(biosynthesis) AND TITLE:(vitexin OR isovitexin OR orientin OR isoorientin) AND OPEN_ACCESS:Y",
             "TITLE:(nothofagin OR phloretin) AND (TITLE:(glycosyltransferase) OR TITLE:(biocatalytic) OR TITLE:(\"Leloir\")) AND OPEN_ACCESS:Y",
             "TITLE:(\"Leloir glycosyltransferases\") AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-title-chemoenzymatic",
         purpose="chemo-enzymatic C-glycosylation with product isolation",
         queries=[
             "(TITLE:(chemo-enzymatic) OR TITLE:(chemoenzymatic)) AND (C-glycosyltransferase OR C-glycosylation) AND OPEN_ACCESS:Y",
             "TITLE:(\"C-glycosyl flavone\" OR \"C-glycosylflavonol\" OR \"C-glucosylflavonol\") AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-mechanism",
         purpose="mechanistic C-glycosylation studies that assign product structure",
         queries=[
             "TITLE:(C-glycosylation) AND (TITLE:(enzymatic) OR TITLE:(mechanistic) OR TITLE:(mechanism)) AND OPEN_ACCESS:Y",
             "TITLE:(\"C-glycosyltransferase\") AND (substrate OR promiscuity OR specificity) AND OPEN_ACCESS:Y",
         ]),
]

def plan():
    qplan = []
    for fam in FAMILIES:
        for q in fam["queries"]:
            url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                   + urlencode({"query": q, "format": "json", "pageSize": 100,
                                "resultType": "lite"}))
            qplan.append(dict(family=fam["family"], purpose=fam["purpose"],
                              interface="europepmc-lite", query=q, url=url,
                              role="discovery-json", pagination_cap=1, page_size=100,
                              dedup_key="pmcid",
                              stop_reason="single page of 100 or hitCount<100; "
                                          "interface failure after 2 attempts"))
    qplan_r2 = []
    for fam in FAMILIES_R2:
        for q in fam["queries"]:
            url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                   + urlencode({"query": q, "format": "json", "pageSize": 50,
                                "resultType": "lite"}))
            qplan_r2.append(dict(family=fam["family"], purpose=fam["purpose"],
                                 interface="europepmc-lite-title", query=q, url=url,
                                 role="discovery-json", pagination_cap=1, page_size=50,
                                 dedup_key="pmcid",
                                 stop_reason="single page of 50 or hitCount<50"))
    save("query_plan.json", dict(
        task=TASK, created_at=stamp(),
        round_R2=dict(families=FAMILIES_R2,
                      note="title-scoped round added after round R1 returned only sources P3 "
                           "already held; R1 selection is preserved unchanged and R2 is appended, "
                           "still before any A/B/E number existed"),
        queries_r2=qplan_r2,
        approval="outputs/task016-p4/v1/approval.json",
        gap_addressed="G4 panel: C_formation 1 target / 1 group against a >=6 target / >=2 group gate",
        selection_intent="find C-glycosylation primary studies with an explicit complete "
                         "product structural assignment, preferring acceptors outside the "
                         "P1/P2 development exposure closure",
        known_excluded_exposed_sources=sorted(KNOWN_EXPOSED),
        queries=qplan,
        budgets=dict(bytes=MAX_BYTES, http=MAX_HTTP, metadata=MAX_META,
                     articles=MAX_ARTICLES, attachments=MAX_ATTACH, per_file=PER_FILE)))
    print("plan queries", len(qplan))


# ---------------------------------------------------------------- title rule

# Titles arrive with inline markup such as "<i>C</i>-glycosyltransferase", so the
# literal term never matches. Normalise the markup away before any title rule runs,
# otherwise real C-glycosylation enzyme papers are silently rejected.
def clean_title(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    return re.sub(r"\s+", " ", t).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()


RE_C = re.compile(r"c-glycosyltransferase|c-glucosyltransferase|c-rhamnosyltransferase|"
                  r"c-xylosyltransferase|c-glycosylation|c-glucosylation|c-glycoside|"
                  r"c-glucoside|c-glycosyl|c-glycosylated", re.I)
RE_FLAV = re.compile(r"flavo|phloretin|dihydrochalcone|phloroglucinol|chromone|xanthone|"
                     r"benzophenone|mangiferin|vitexin|orientin|isovitexin|isoorientin|"
                     r"nothofagin|aspalathin|quercetin|kaempferol|naringenin|anthocyan|"
                     r"cyanidin|delphinidin|apigenin|luteolin|myricetin|hesperetin|"
                     r"genistein|isoflavon|neoflavon|polyphenol|flavonol|flavone|flavanone|"
                     r"sugar|dendrobium|anemarrhena|orchid|bromeliad|urginea|plant|"
                     r"natural product|biosynth|glycosyltransfer", re.I)
RE_EXCL = re.compile(r"review|perspective|overview|protocol|methodology|in silico|docking|"
                     r"network pharmacol|molecular dynamics|omics|transcriptom|metabolom|"
                     r"gut microbi|bioinformatics| QSAR|machine learning", re.I)
RE_STRUCT = re.compile(r"nuclear magnetic resonance|\bNMR\b|structure elucidation|"
                       r"crystal structure|X-ray|spectroscopic|characteriz|isolation and|"
                       r"standard", re.I)


def classify(title):
    t = clean_title(title)
    if not RE_C.search(t):
        return None, "title lacks a C-glycosylation term after markup normalisation"
    if RE_EXCL.search(t):
        return None, "excluded review/in silico/omics title by frozen rule"
    if not RE_FLAV.search(t):
        return None, "C-glycosylation term present but no flavonoid-family or plant/biocatalysis context"
    return ("C_formation",
            "C-glycosylation term after markup normalisation + flavonoid/plant context"
            + ("; structural-assignment hint present" if RE_STRUCT.search(t) else ""))


def discovery():
    plan_doc = json.loads((OUT / "query_plan.json").read_text())
    ledger, records = [], []
    for q in list(plan_doc["queries"]) + list(plan_doc.get("queries_r2") or []):
        raw = get(q["url"], "europepmc", q["role"], q["family"])
        entry = dict(family=q["family"], query=q["query"], url=q["url"],
                     status=raw["status"], sha256=raw["sha256"], path=raw["path"],
                     hits=None, returned=0)
        if raw["status"] == "raw_available":
            try:
                d = json.loads((ROOT / raw["path"]).read_text())
                entry["hits"] = d.get("hitCount")
                rs = d.get("resultList", {}).get("result", []) or []
                entry["returned"] = len(rs)
                for r in rs:
                    pmcid = r.get("pmcid")
                    if pmcid:
                        records.append(dict(pmcid=pmcid, doi=r.get("doi"),
                                            title=r.get("title") or "",
                                            year=r.get("pubYear"), family=q["family"],
                                            raw_path=raw["path"], raw_sha256=raw["sha256"]))
            except ValueError as exc:
                entry["error"] = str(exc)
        ledger.append(entry)
        print("query", q["family"], entry["status"], entry["hits"], entry["returned"], flush=True)
    save("query_ledger.json", dict(executed=ledger, executed_at=stamp()))

    by = {}
    for r in records:
        e = by.setdefault(r["pmcid"], {**r, "families": []})
        if r["family"] not in e["families"]:
            e["families"].append(r["family"])
    selected, rejected = [], []
    for pmc, rec in sorted(by.items()):
        cls, why = classify(rec["title"])
        entry = dict(**rec,
                     selected_class=cls, selection_reason=why,
                     in_known_exposed_closure=pmc in KNOWN_EXPOSED,
                     selection_is_title_only=True)
        (selected if cls and pmc not in KNOWN_EXPOSED else rejected).append(entry)
    # exposed-closure hits are kept visible but never become intake candidates
    save("discovery_records.jsonl", sorted(by.values(), key=lambda r: r["pmcid"]), True)
    save("discovery_selection.json", dict(
        created_at=stamp(),
        rule="title-level pre-registered selection only; no A/B/E output existed at this "
             "point and no product structure has been judged yet",
        selected=[r["pmcid"] for r in selected],
        selected_count=len(selected),
        rejected_as_exposed_closure=[r["pmcid"] for r in rejected if r["in_known_exposed_closure"]],
        rejected_by_title_rule=[r["pmcid"] for r in rejected if not r["in_known_exposed_closure"]],
    ), )
    save("discovery_selection.jsonl", selected + rejected, True)
    return selected


def available_article(rec):
    pmc = rec["pmcid"]
    result = dict(pmcid=pmc, title=rec.get("title"),
                  discovery=rec.get("families"), files=[], status="unavailable",
                  review_type="agent_delegated", independent_chemical_validation=False)
    raw = get(B + "?" + urlencode({"list-type": 2, "prefix": pmc + ".", "max-keys": 100}),
              "pmc", "listing", pmc)
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
        m = get(B + key, "pmc", "metadata",
                pmc + "-" + hashlib.sha256(key.encode()).hexdigest()[:8])
        result["files"].append(m)
        if m["status"] == "raw_available":
            try:
                metas.append((json.loads((ROOT / m["path"]).read_text()), m))
            except ValueError:
                pass
    metas.sort(key=lambda t: (t[0].get("is_manuscript") in [True, "yes"], str(t[0].get("version"))))
    if not metas:
        x = get("https://www.ebi.ac.uk/europepmc/webservices/rest/" + pmc + "/fullTextXML",
                "europepmc", "fullTextXML", pmc)
        result["files"].append(x)
        if x["status"] == "raw_available":
            try:
                root = ET.parse(ROOT / x["path"]).getroot()
                lic = root.find(".//license")
                if lic is None or "creativecommons.org" not in ET.tostring(lic, encoding="unicode"):
                    result["status"] = "license_pending"
                    return result
                result.update(status="fulltext_available", xml=x,
                               license="".join(lic.itertext()),
                               article_version="EuropePMC-deposit",
                               supplement_status="cloud_listing_empty; not acquired")
            except ET.ParseError:
                result["status"] = "format_error"
        return result
    meta, m = metas[0]
    license_code = meta.get("license_code")
    result.update(license=license_code, article_version=meta.get("version"),
                  article_metadata=m)
    if meta.get("is_retracted") in [True, "yes"] or not str(license_code).startswith("CC"):
        result["status"] = "retracted_or_license_pending"
        return result
    urls = [meta.get("xml_url")] + [
        u for u in meta.get("media_urls", [])
        if unquote(urlparse(u).path).lower().endswith(
            (".pdf", ".docx", ".xlsx", ".csv", ".zip", ".doc", ".xls"))][:4]
    for index, u in enumerate(urls):
        if not u:
            continue
        u = u.replace("s3://pmc-oa-opendata/", B)
        x = get(u, "pmc", "fullTextXML" if index == 0 else "supplement",
                pmc + "-v" + str(meta.get("version")) + "-" + str(index))
        result["files"].append(x)
        if x["status"] != "raw_available":
            continue
        if index == 0:
            result["xml"] = x
            result["status"] = "fulltext_available"
        else:
            result.setdefault("supplements", []).append(x)
            result["supplement_status"] = "acquired"
    return result


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        plan()
        return 0
    if cmd == "acquire":
        selected = discovery()
        print("selected for acquisition:", len(selected), flush=True)
        articles = []
        with ThreadPoolExecutor(max_workers=4) as pool:
            for res in pool.map(available_article, selected):
                articles.append(res)
                print("article", res["pmcid"], res["status"], flush=True)
        save("article_acquisition_manifest.json", dict(
            task=TASK, created_at=stamp(), articles=articles), )
        # SI text extraction so structures stated only in SI can be reviewed later
        segs = []
        for art in articles:
            for sup in art.get("supplements") or []:
                p = ROOT / sup["path"]
                if p.suffix.lower() not in (".pdf", ".docx", ".xlsx", ".txt", ".zip"):
                    continue
                rec = dict(pmcid=art["pmcid"], path=sup["path"], sha256=sup["sha256"],
                           bytes=sup["bytes"], extracted_chars=0, method=None)
                try:
                    if p.suffix.lower() == ".txt":
                        txt = p.read_text(errors="replace")
                    elif p.suffix.lower() == ".zip":
                        with zipfile.ZipFile(p) as z:
                            txt = "\n".join(
                                z.read(n).decode("utf-8", "replace")
                                for n in z.namelist() if n.lower().endswith(".txt"))
                    else:
                        rec["method"] = "deferred_binary_no_text_extractor"
                        segs.append(rec)
                        continue
                    tp = OUT / "attachment-text" / art["pmcid"] / p.name
                    write(TASK, str(tp.relative_to(ROOT)), txt)
                    rec.update(extracted_chars=len(txt), method="plain_text",
                               text_path=str(tp.relative_to(ROOT)))
                except Exception as exc:
                    rec["method"] = f"failed:{type(exc).__name__}"
                segs.append(rec)
        save("attachment_parse_manifest.jsonl", segs, True)

        hist = rows(OUT / "acquisition_attempts.jsonl")
        save("source_accounting.json", dict(
            task=TASK, created_at=stamp(),
            http_attempts=len(hist),
            http_ceiling=MAX_HTTP,
            bytes=sum(r.get("bytes", 0) for r in hist),
            bytes_ceiling=MAX_BYTES,
            article_versions=len({r["url"] for r in hist if r["content_role"] == "fullTextXML"}),
            article_ceiling=MAX_ARTICLES,
            attachments=len({r["url"] for r in hist if r["content_role"] == "supplement"}),
            attachment_ceiling=MAX_ATTACH,
            distinct_urls=len({r["url"] for r in hist}),
            metadata_ceiling=MAX_META,
            unavailable=[dict(url=r["url"], status_code=r.get("status_code"),
                              error=r.get("error")) for r in hist
                         if r["status"] != "raw_available"],
            reuse_of_prior_task_files=len(rows(OUT / "reused_files.jsonl")),
            note="P4 budget is independent; no P1/P2/P3 ledger was modified",
        ))
        print("accounting written; http attempts", len(hist))
        return 0
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    sys.exit(main())
