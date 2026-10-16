"""TASK-016-P5 G1: bounded targeted acquisition for the C and SS panel shortfalls.

Commands:
  plan     -- write the frozen query plan. No network.
  acquire  -- run the plan, then acquire full text + SI through the official PMC OA
              package route, with SI text extraction and three-way accounting.

Independent P5 counters and namespace. Budgets come from approval.json:
4 GiB bytes / 3000 direct HTTP / 5000 metadata keys / 200 article versions /
360 attachments / per-file 256 MiB / per-URL 2 attempts / concurrency 4.

Purpose is narrow and differs from P4. P4 chased C holdout targets only and ended
with C=1/SS=5 because 7 of the 8 structure-complete C reactions come from
development-exposed sources. P5 must simultaneously satisfy two independent
needs, so this stage looks for BOTH:
  * build-side C candidates: a new C scope needs >=2 distinct canonical acceptors
    whose exact structures are fully assigned and whose sources are build-only;
  * leakage-free holdout candidates for both C and SS.

Three accounting ledgers are kept separate on purpose, because P4's report prose
(23 HTTP / 1.13 MB / 40 reuse) was a discovery-stage figure while the frozen
whole-task ledger was 45 HTTP / 63,180,976 B / 74 reuse / 5 article versions /
9 attachments. P5 reports discovery, new-download and whole-task separately.
"""
import hashlib
import json
import re
import sys
import threading
import time
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, unquote, urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
RAW = ROOT / "data/raw/task016-p5/2026-10-07"
sys.path.insert(0, str(ROOT))
from scripts.operate import event, write

MAX_BYTES = 4 * 1024 ** 3
MAX_HTTP = 3000
MAX_META = 5000
MAX_ARTICLES = 200
MAX_ATTACH = 360
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

# Reuse of an already-verified P1-P4 raw file is not a new download, but it must
# be re-registered with its SHA and exposure grade.
INHERIT_LEDGERS = [
    ROOT / "outputs/task016-p1/v1/acquisition_attempts.jsonl",
    ROOT / "outputs/task016-p2/v1/acquisition_attempts.jsonl",
    ROOT / "outputs/task016-p3/v1/acquisition_attempts.jsonl",
    ROOT / "outputs/task016-p4/v1/acquisition_attempts.jsonl",
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
            assert len(history) < MAX_HTTP, "P5 HTTP attempt ceiling"
            total = sum(r.get("bytes", 0) for r in history)
            assert total + limit <= MAX_BYTES, "P5 raw byte ceiling"
            assert len([r for r in history if r["content_role"] == role]) < (
                MAX_ARTICLES if role == "fullTextXML"
                else MAX_ATTACH if role == "supplement" else 10 ** 9), f"P5 {role} ceiling"
            assert len({r["url"] for r in history}) < MAX_META, "P5 metadata ceiling"
            key = hashlib.sha256(url.encode()).hexdigest()[:24]
            target = RAW / provider / key / (role + ".attempt-" + str(attempt))
            assert not target.exists(), "immutable raw snapshot"
            reservation = dict(url=url, provider=provider, content_role=role, name=name,
                               attempt=attempt, status="in_progress", limit=limit,
                               started_at=stamp())
            append("acquisition_reservations.jsonl", reservation)
        data = b""
        status = None
        error = None
        headers = {}
        wait = 1
        try:
            with urlopen(Request(url, headers={"User-Agent": "FlavoRetro-TASK016-P5/0.1"}),
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

FAMILIES_C = [
    dict(family="c-title-cgt",
         purpose="primary studies characterising a novel C-glycosyltransferase, by title",
         queries=[
             "TITLE:\"C-glycosyltransferase\" AND OPEN_ACCESS:Y",
             "TITLE:(\"C-glycosyltransferase\") AND (Dendrobium OR Anemarrhena OR orchid OR "
             "bromeliad OR Cyclamen OR Gentiana OR wheat OR mangrove OR Oryza) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-title-named-product",
         purpose="biosynthesis or flow synthesis of a named C-glycoside, by title",
         queries=[
             "TITLE:(biosynthesis) AND TITLE:(vitexin OR isovitexin OR orientin OR isoorientin "
             "OR mangiferin OR puerarin) AND OPEN_ACCESS:Y",
             "TITLE:(chemoenzymatic OR chemo-enzymatic) AND (C-glycosylation OR "
             "C-glycosyltransferase) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-title-scope",
         purpose="substrate-scope tables that yield several distinct complete acceptors",
         queries=[
             "TITLE:(\"C-glycosyltransferase\") AND (substrate OR promiscuity OR specificity "
             "OR scope) AND OPEN_ACCESS:Y",
             "TITLE:(\"C-glycosylation\") AND (TITLE:(enzymatic) OR TITLE:(mechanistic) OR "
             "TITLE:(mechanism)) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-flavone-position",
         purpose="8-C and 6-C flavone/flavonol glucosylation, the positions adjacent to the "
                 "already-admitted kaempferol/quercetin 8-C pair",
         queries=[
             "(8-C-glucosyl OR 6-C-glucosyl OR \"8-C-glucoside\" OR \"6-C-glucoside\") AND "
             "(flavone OR flavonol OR apigenin OR luteolin OR kaempferol OR quercetin OR "
             "myricetin OR tricetin) AND OPEN_ACCESS:Y",
             "(\"C-glucosyltransferase\" OR \"C-glycosyltransferase\") AND "
             "(flavone OR flavonol) AND (UDP-glucose OR UDP-glc) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-new-scaffold",
         purpose="C-glycosylation on acceptors outside the whole P1-P4 closure",
         queries=[
             "(xanthone OR benzophenone OR chromone OR anthraquinone OR naphthoquinone OR "
             "stilbene) AND (C-glycosylation OR C-glycosyltransferase OR "
             "\"C-glucoside\") AND OPEN_ACCESS:Y",
             "(mangiferin OR neomangiferin OR aspalathin OR penta-O-galloyl-glucose) AND "
             "(C-glycosylation OR biosynthesis) AND OPEN_ACCESS:Y",
         ]),
    dict(family="c-isoflavone-chalcone",
         purpose="isoflavone and chalcone C-glycosides as a structurally distinct C class",
         queries=[
             "(puerarin OR daidzein OR genistein OR \"isoflavone C-glycoside\") AND "
             "(C-glycosylation OR C-glycosyltransferase OR biosynthesis) AND OPEN_ACCESS:Y",
             "(chalcone OR phloroglucinol OR acetophenone) AND (C-glycosylation OR "
             "\"C-glucosylation\") AND OPEN_ACCESS:Y",
         ]),
]

FAMILIES_SS = [
    dict(family="ss-title-rhat",
         purpose="primary studies on novel rhamnosyltransferases, by title",
         queries=[
             "TITLE:(rhamnosyltransferase) AND OPEN_ACCESS:Y",
             "TITLE:(\"rhamnosyltransferase\") AND (flavonoid OR flavonol OR flavone OR "
             "glycoside OR \"O-rhamnosylation\") AND OPEN_ACCESS:Y",
         ]),
    dict(family="ss-title-named-rhamnoside",
         purpose="named rhamnoside biosynthesis with product isolation, by title",
         queries=[
             "TITLE:(rutinoside OR neohesperidoside OR \"O-rhamnosylation\" OR rhamnoside) "
             "AND (TITLE:(biosynthesis) OR TITLE:(glycosyltransferase)) AND OPEN_ACCESS:Y",
             "TITLE:(\"1->6\" OR \"1→6\") AND TITLE:(rhamnosylation OR rhamnosyltransferase) "
             "AND OPEN_ACCESS:Y",
         ]),
    dict(family="ss-title-xylt-apiose",
         purpose="new xylosyltransferase / apiose transferase substrate scopes",
         queries=[
             "TITLE:(xylosyltransferase OR \"apiose\") AND OPEN_ACCESS:Y",
             "TITLE:(pentosyltransferase OR \"UDPXyl\" OR \"UDP-xylose\") AND "
             "(glycosyltransferase OR substrate) AND OPEN_ACCESS:Y",
         ]),
    dict(family="ss-substrate-scope",
         purpose="substrate-scope tables on glycosylated acceptors that yield several "
                 "distinct complete acceptors",
         queries=[
             "(rhamnosyltransferase OR \"UDP-rhamnose\") AND (substrate OR promiscuity OR "
             "specificity) AND OPEN_ACCESS:Y",
             "(\"O-glycosylation\" AND glycoside AND \"second sugar\") AND "
             "(glycosyltransferase) AND OPEN_ACCESS:Y",
         ]),
    dict(family="ss-new-acceptor",
         purpose="rhamnosylation/xylosylation of acceptors outside the whole P1-P4 closure",
         queries=[
             "(rhamnosylation OR xylosylation) AND (anthocyanidin OR \"anthocyanin\" OR "
             "coumarin OR lignan OR \"phenolic glycoside\") AND (glycosyltransferase OR "
             "UDP-sugar) AND OPEN_ACCESS:Y",
             "(\"O-rhamnosyltransferase\" OR \"rhamnosyltransferase\") AND "
             "(bacteria OR fungus OR insect OR \"marine\") AND OPEN_ACCESS:Y",
         ]),
]

# Every source already inside the P1-P4 development closure. Their chemistry can
# serve a build scope but can never seed a clean holdout target.
KNOWN_EXPOSED = {
    # P1/P2 runtime payload and P2 unresolved list
    "PMC10589286", "PMC11975207", "PMC7558026", "PMC10602602", "PMC10706860",
    "PMC12313340", "PMC4282749", "PMC6255700", "PMC9700910", "PMC7060329",
    "PMC10465961", "PMC12993211", "PMC12658608", "PMC12844164", "PMC4494776",
    "PMC3507004", "PMC12494026", "PMC12984077", "PMC11502824", "PMC12790375",
    "PMC13421352", "PMC10856022", "PMC11273223", "PMC12246196",
    # P3 sources
    "PMC6036675", "PMC9563126", "PMC13084081", "PMC13324211", "PMC9706480",
    "PMC10602597", "PMC12120870", "PMC13140228", "PMC12993211", "PMC10465961",
    # P4 sources
    "PMC13035923", "PMC11480083", "PMC8841362", "PMC8196924", "PMC3883091",
    "PMC7326982", "PMC11728773", "PMC10628242",
}


def plan():
    queries = []
    for fam in FAMILIES_C + FAMILIES_SS:
        for q in fam["queries"]:
            url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                   + urlencode({"query": q, "format": "json", "pageSize": 100,
                                "resultType": "lite"}))
            queries.append(dict(family=fam["family"], purpose=fam["purpose"],
                                intent="C_build_side" if fam["family"].startswith("c-")
                                else "C_or_SS_holdout_side",
                                interface="europepmc-lite", query=q, url=url,
                                role="discovery-json", pagination_cap=1, page_size=100,
                                dedup_key="pmcid",
                                stop_reason="single page of 100 or hitCount<100; "
                                            "interface failure after 2 attempts"))
    save("query_plan.json", dict(
        task=TASK, created_at=stamp(),
        approval="outputs/task016-p5/v1/approval.json",
        gap_addressed="C holdout 1/6 and SS holdout 5/6 against the >=6 target / >=2 group "
                      "gate, plus the absence of any qualified C build-side scope in v5",
        selection_intent="find (a) C-glycosylation primary studies with explicit complete "
                         "product assignment that can support a new build-side C scope, and "
                         "(b) further C and sugar-sugar primary studies with leakage-free "
                         "holdout potential; no A/B/E number exists at this point",
        known_excluded_exposed_sources=sorted(KNOWN_EXPOSED),
        queries=queries,
        budgets=dict(bytes=MAX_BYTES, http=MAX_HTTP, metadata=MAX_META,
                     articles=MAX_ARTICLES, attachments=MAX_ATTACH, per_file=PER_FILE)))
    print("plan queries", len(queries))


# ---------------------------------------------------------------- title rule

def clean_title(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    return re.sub(r"\s+", " ", t).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()


RE_C = re.compile(r"c-glycosyltransferase|c-glucosyltransferase|c-rhamnosyltransferase|"
                  r"c-xylosyltransferase|c-glycosylation|c-glucosylation|c-glycoside|"
                  r"c-glucoside|c-glycosyl|c-glycosylated", re.I)
RE_SS = re.compile(r"rhamnosyltransferase|rhamnosylation|xylosyltransferase|xylosylation|"
                   r"apiose|rutinoside|neohesperidoside|rhamnoside|"
                   r"pentosyltransferase|arabinosyltransferase|"
                   r"\"O-rhamnosyl|\"O-glycosyl", re.I)
RE_FLAV = re.compile(r"flavo|phloretin|dihydrochalcone|phloroglucinol|chromone|xanthone|"
                     r"benzophenone|mangiferin|vitexin|orientin|isovitexin|isoorientin|"
                     r"nothofagin|aspalathin|quercetin|kaempferol|naringenin|hesperetin|"
                     r"anthocyan|cyanidin|delphinidin|apigenin|luteolin|myricetin|"
                     r"genistein|isoflavon|neoflavon|polyphenol|flavonol|flavone|flavanone|"
                     r"glycoside|rhamnose|xylose|apiose|sugar|dendrobium|anemarrhena|orchid|"
                     r"bromeliad|urginea|mangrove|plant|natural product|biosynth|"
                     r"glycosyltransfer", re.I)
RE_EXCL = re.compile(r"review|perspective|overview|protocol|methodology|in silico|docking|"
                     r"network pharmacol|molecular dynamics|omics|transcriptom|metabolom|"
                     r"gut microbi|bioinformatics| QSAR|machine learning|"
                     r"systematic review|meta-analysis", re.I)
RE_STRUCT = re.compile(r"nuclear magnetic resonance|\bNMR\b|structure elucidation|"
                       r"crystal structure|X-ray|spectroscopic|characteriz|isolation and|"
                       r"standard|substrate|scope|promiscuit", re.I)


def classify(title):
    t = clean_title(title)
    if RE_EXCL.search(t):
        return None, "excluded review/in silico/omics title by frozen rule"
    has_c, has_ss = bool(RE_C.search(t)), bool(RE_SS.search(t))
    if not (has_c or has_ss):
        return None, "title lacks a C-glycosylation or sugar-sugar glycosylation term"
    if not RE_FLAV.search(t):
        return None, "glycosylation term present but no flavonoid/sugar/biocatalysis context"
    cls = "C_formation" if has_c else "sugar_sugar_formation"
    return (cls, f"{'C-glycosylation' if has_c else 'sugar-sugar glycosylation'} term after "
                 f"markup normalisation + flavonoid/sugar/biocatalysis context"
                 + ("; structural-assignment or substrate-scope hint present"
                    if RE_STRUCT.search(t) else ""))


def discovery():
    plan_doc = json.loads((OUT / "query_plan.json").read_text())
    ledger, records = [], []
    for q in (list(plan_doc["queries"])
              + list(plan_doc.get("queries_r2") or [])
              + list(plan_doc.get("queries_round2") or [])):
        raw = get(q["url"], "europepmc", q["role"], q["family"])
        entry = dict(family=q["family"], intent=q["intent"], query=q["query"], url=q["url"],
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
                                            intent=q["intent"],
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
                     selection_is_title_only=True,
                     note=("already inside the P1-P4 development exposure closure; it may "
                           "support a build scope but can never seed a holdout target"
                           if pmc in KNOWN_EXPOSED else None))
        # exposed-closure sources are still acquired: they are the legitimate
        # build-side route when a new scope needs >=2 distinct acceptors.
        (selected if cls else rejected).append(entry)
    save("discovery_records.jsonl", sorted(by.values(), key=lambda r: r["pmcid"]), True)
    save("discovery_selection.json", dict(
        created_at=stamp(),
        rule="title-level pre-registered selection only; no A/B/E output existed at this "
             "point and no product structure has been judged yet",
        selected=[r["pmcid"] for r in selected],
        selected_count=len(selected),
        selected_from_exposed_closure=[r["pmcid"] for r in selected
                                       if r["in_known_exposed_closure"]],
        selected_clean=[r["pmcid"] for r in selected
                        if not r["in_known_exposed_closure"]],
        rejected_by_title_rule=[r["pmcid"] for r in rejected],
    ))
    save("discovery_selection.jsonl", selected + rejected, True)
    return selected


def available_article(rec):
    pmc = rec["pmcid"]
    result = dict(pmcid=pmc, title=rec.get("title"),
                  discovery=rec.get("families"), intent=rec.get("intent"),
                  in_known_exposed_closure=rec.get("in_known_exposed_closure"),
                  files=[], status="unavailable",
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
            task=TASK, created_at=stamp(), articles=articles))
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
        accounting()
        return 0
    raise SystemExit(f"unknown command {cmd}")


def accounting():
    """Three ledgers, never collapsed into one number.

    discovery   - query/interface attempts only
    new_download- P5 rows with a P5 raw path (a genuine new transfer)
    whole_task  - every P5 attempt plus re-registered reuse of P1-P4 files
    """
    hist = rows(OUT / "acquisition_attempts.jsonl")
    reused = rows(OUT / "reused_files.jsonl")
    inherited = []
    for p in INHERIT_LEDGERS:
        inherited.extend(rows(p))
    discovery_rows = [r for r in hist if r["content_role"] == "discovery-json"]
    new_rows = [r for r in hist if r["path"].startswith("data/raw/task016-p5")]
    save("source_accounting.json", dict(
        task=TASK, created_at=stamp(),
        discovery=dict(
            note="interface/query attempts only; this is NOT the task total",
            query_attempts=len(discovery_rows),
            distinct_query_urls=len({r["url"] for r in discovery_rows}),
            bytes=sum(r.get("bytes", 0) for r in discovery_rows)),
        new_download=dict(
            note="files genuinely transferred into data/raw/task016-p5 during P5",
            attempts=len(new_rows),
            distinct_urls=len({r["url"] for r in new_rows}),
            bytes=sum(r.get("bytes", 0) for r in new_rows)),
        whole_task=dict(
            note="every P5 HTTP attempt plus re-registered reuse of already-frozen P1-P4 files; "
                 "this is the figure comparable to the P4 whole-task ledger",
            http_attempts=len(hist),
            http_ceiling=MAX_HTTP,
            bytes=sum(r.get("bytes", 0) for r in hist),
            bytes_ceiling=MAX_BYTES,
            distinct_urls=len({r["url"] for r in hist}),
            metadata_ceiling=MAX_META,
            article_versions=len({r["url"] for r in hist if r["content_role"] == "fullTextXML"}),
            article_ceiling=MAX_ARTICLES,
            attachments=len({r["url"] for r in hist if r["content_role"] == "supplement"}),
            attachment_ceiling=MAX_ATTACH,
            reused_prior_task_files=len(reused),
            prior_task_files_inherited_total=len(inherited)),
        ceilings=dict(bytes=MAX_BYTES, http=MAX_HTTP, articles=MAX_ARTICLES,
                      attachments=MAX_ATTACH, metadata=MAX_META, per_file=PER_FILE),
        unavailable=[dict(url=r["url"], status_code=r.get("status_code"), error=r.get("error"))
                     for r in hist if r["status"] != "raw_available"],
        p4_whole_task_reference=dict(
            http_attempts=45, bytes=63180976, reuse_of_prior_task_files=74,
            article_versions=5, attachments=9,
            note="frozen P4 source_accounting.json; P5 does not borrow any P4 budget"),
        note="P5 budget is independent; no P1-P4 ledger was modified",
    ))
    print("accounting written; P5 http attempts", len(hist),
          "new bytes", sum(r.get("bytes", 0) for r in new_rows))


if __name__ == "__main__":
    sys.exit(main())