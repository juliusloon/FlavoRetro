#!/usr/bin/env python3
"""TASK-016-P3 round-3 supplementary discovery.

Two completed plan rounds (19 queries, 8 families) left the holdout-capable
source pool at one C component (PMC13035923, chemical) and one SS component
(PMC13324211).  This round targets only sources that can form NEW holdout
groups: original papers behind secondary-review enzyme records, sibling
chemical C-glycosylation syntheses, and 1->2 rhamnosyl/glucosyl
transferases on flavonoid glycosides.  Reuses the P3 bounded acquisition
machinery (same ceilings, same ledgers); never re-runs the R1/R2 queries."""

import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import task016_p3_sources as S  # P3 bounded get()/ledgers; same task budgets

OUT = S.OUT
RAW = S.RAW / "round3"
B = "https://pmc-oa-opendata.s3.amazonaws.com/"

FAMILIES = [
    dict(
        family="ss-rha-originals",
        purpose="original papers behind secondary-review 2''-O-rhamnosyltransferase records on flavonoid glucosides (e.g. CsUGT79B28) and neohesperidoside-forming GTs",
        queries=[
            "(UGT79B28 OR neohesperidosyltransferase OR 1-2-rhamnosyltransferase) AND (flavonoid OR flavone OR naringenin OR apigenin OR hesperetin) AND OPEN_ACCESS:Y",
            "(rhamnosyltransferase) AND (7-O-glucoside OR neohesperidoside OR hesperidin OR neohesperidin OR naringin) AND (flavonoid OR flavanone OR flavone) AND OPEN_ACCESS:Y",
        ],
    ),
    dict(
        family="ss-12-glucosyl",
        purpose="1->2 glucosyltransferases forming sophoroside/2-O-glucosyl bonds on flavonoid glycosides (UGT79 family, F3GGT siblings)",
        queries=[
            "(UGT79B31 OR UGT79B6 OR 1,2-glucosyltransferase) AND (flavonol OR quercetin OR kaempferol OR flavonoid) AND OPEN_ACCESS:Y",
            "(sophorosyltransferase OR diglucosylated OR 2-O-glucosyltransferase) AND (flavonol OR anthocyanidin OR flavonoid) AND (UDP-glucose) AND OPEN_ACCESS:Y",
        ],
    ),
    dict(
        family="c-chemical-aryl",
        purpose="chemical C-aryl glycoside synthesis applicable to flavonoid aglycones (Suzuki/Ni/Stille/C-H routes)",
        queries=[
            "(C-aryl glycoside) AND (synthesis OR Suzuki OR nickel OR stannyl) AND (flavone OR chromone OR xanthone OR resorcinol OR phloroglucinol) AND OPEN_ACCESS:Y",
            "(C-glycosylation) AND (palladium OR nickel) AND (phenol OR aryl) AND (anomeric OR stereospecific) AND OPEN_ACCESS:Y",
        ],
    ),
    dict(
        family="c-direct-flavone",
        purpose="direct flavone/aglycone C-glycosyltransferases independent of the 2-hydroxyflavanone route",
        queries=[
            "(C-glycosyltransferase) AND (apigenin OR luteolin OR chrysin OR tricin OR flavone) AND NOT (2-hydroxyflavanone) AND OPEN_ACCESS:Y",
            "(C-glucosyltransferase) AND (benzophenone OR xanthone OR mangiferin OR norathyriol) AND OPEN_ACCESS:Y",
        ],
    ),
    dict(
        family="citation-chase-r3",
        purpose="citation neighborhoods of the two unexposed holdout-capable components found so far",
        queries=[
            "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC/PMC13035923/citations?pageSize=100&format=json",
            "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC/PMC13324211/citations?pageSize=100&format=json",
        ],
    ),
]


def classify_round3(title):
    cat, reason = S.classify(title)
    if cat:
        return cat, reason
    t = (title or "")
    if ("rhamnosyltransferase" in t.lower() or "UGT79" in t) and S.RE_FLAV.search(t):
        return "sugar_sugar_formation", "round3 rule: rhamnosyl/UGT79 transferase + flavonoid context"
    return None, "round3 title rule: not a targeted primary study"


RECOVERY_LOG = OUT / "round3_recovery_chain.jsonl"


def recover_direct(url, provider, role, name, limit=None):
    """One documented recovery attempt for round-3 URLs whose recorded
    attempts all failed locally (connection refused by the dead 127.0.0.1
    proxy, status_code None: the remote was never reached).  Appends to the
    same P3 attempt ledger plus a dedicated recovery chain file; never
    touches URLs that failed against the remote."""
    import json as _json
    import time as _time
    from urllib.request import ProxyHandler, build_opener
    limit = limit or S.ROLE_LIMIT.get(role, S.PER_FILE)
    attempts = [a for a in S.rows(OUT / "acquisition_attempts.jsonl") if a.get("url") == url]
    if any(a.get("status") == "raw_available" for a in attempts):
        return attempts[-1]
    if attempts and any(a.get("status_code") is not None for a in attempts):
        return attempts[-1]  # remote responded before: honour the 2-try rule
    entry = dict(url=url, provider=provider, content_role=role, name=name,
                 attempt=len(attempts) + 1,
                 recovery_reason="all prior attempts failed with local connection-refused (dead proxy) or unreachable endpoint form; remote never reached",
                 recovery_attempt=1, started_at=S.stamp())
    data, status, error = b"", None, None
    try:
        opener = build_opener(ProxyHandler({}))
        with opener.open(url, timeout=60) as response:
            status = response.status
            data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError("per-file bound exceeded")
    except Exception as exc:  # noqa: BLE001 - recorded verbatim
        error = f"{type(exc).__name__}: {exc}"
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    target = RAW / provider / key / (role + ".recovery-1")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    target.chmod(0o444)
    result = dict(**{k: v for k, v in entry.items() if k != "started_at"},
                  path=str(target.relative_to(ROOT)),
                  sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                  status_code=status, error=error,
                  status="raw_available" if status == 200 and not error else "unavailable",
                  acquired_at=S.stamp())
    S.append("acquisition_attempts.jsonl", result)
    with RECOVERY_LOG.open("a") as f:
        f.write(_json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
    if result["status"] != "raw_available":
        _time.sleep(2)
    return result


def main():
    qplan = []
    for fam in FAMILIES:
        for q in fam["queries"]:
            if q.startswith("http"):
                url, role = q, "citation-json"
            else:
                url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                       + urlencode({"query": q, "format": "json", "pageSize": 100,
                                    "resultType": "lite"}))
                role = "discovery-json"
            qplan.append(dict(family=fam["family"], purpose=fam["purpose"],
                              interface="europepmc-lite" if role == "discovery-json" else "europepmc-citations",
                              query=q, url=url, role=role, pagination_cap=1, page_size=100,
                              dedup_key="pmcid",
                              stop_reason="single page of 100 or hitCount<100; 2 attempts max"))

    ledger, records = [], {}
    for q in qplan:
        raw = recover_direct(q["url"], "europepmc", q["role"], q["family"])
        entry = dict(family=q["family"], query=q["query"], url=q["url"], status=raw["status"],
                     sha256=raw["sha256"], path=raw["path"], hits=None, returned=0)
        if raw["status"] == "raw_available":
            try:
                d = __import__("json").loads((ROOT / raw["path"]).read_text())
                entry["hits"] = d.get("hitCount")
                rs = d.get("resultList", {}).get("result", []) or d.get("citationList", {}).get("citation", [])
                entry["returned"] = len(rs)
                for r in rs:
                    pmcid = r.get("pmcid")
                    if not pmcid:
                        continue
                    if pmcid not in records:
                        records[pmcid] = dict(pmcid=pmcid, doi=r.get("doi"),
                                              title=r.get("title") or r.get("source", ""),
                                              year=r.get("pubYear"), families=[])
                    records[pmcid]["families"].append(q["family"])
            except ValueError as exc:
                entry["error"] = str(exc)
        ledger.append(entry)
        print("query", q["family"], entry["status"], entry["hits"], entry["returned"], flush=True)

    (OUT / "round3_query_ledger.json").write_text(
        __import__("json").dumps(dict(executed=ledger, executed_at=S.stamp()), ensure_ascii=False, indent=2) + "\n")

    have = {a["pmcid"] for a in __import__("json").loads((OUT / "article_acquisition_manifest.json").read_text())}
    screened = []
    for r in sorted(records.values(), key=lambda x: x["pmcid"]):
        cat, reason = classify_round3(r["title"])
        r["p3_category"] = cat
        r["selection_reason"] = reason
        r["already_acquired_p3"] = r["pmcid"] in have
        screened.append(r)
    selected = [r for r in screened if r["p3_category"] and not r["already_acquired_p3"]][:40]
    (OUT / "round3_selection.json").write_text(
        __import__("json").dumps(dict(
            rule="round3 frozen title rule before any extraction/template/model outcome; dedup against acquired P3 articles; agent_delegated",
            total=len(screened), selected=len(selected), records=screened),
            ensure_ascii=False, indent=2) + "\n")
    print("screened", len(screened), "selected-new", len(selected), flush=True)

    results = []
    for n, rec in enumerate(selected):
        item = S.available_article(rec)
        results.append(item)
        print(n + 1, item["pmcid"], item["status"], flush=True)
    (OUT / "round3_article_acquisition_manifest.json").write_text(
        __import__("json").dumps(results, ensure_ascii=False, indent=2) + "\n")

    segments = []
    for item in results:
        if item.get("status") != "fulltext_available" or not item.get("xml"):
            continue
        root = ET.parse(ROOT / item["xml"]["path"]).getroot()
        doi = root.find(".//article-id[@pub-id-type='doi']")
        for tag in ["p", "table-wrap", "fig"]:
            for n, el in enumerate(root.findall(".//body//" + tag)):
                text = " ".join("".join(el.itertext()).split())
                segments.append(dict(pmcid=item["pmcid"], doi=doi.text if doi is not None else None,
                                     locator=f"body//{tag}[{n+1}]", xml_id=el.get("id"), text=text,
                                     text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                                     raw_path=item["xml"]["path"], raw_sha256=item["xml"]["sha256"],
                                     license=item.get("license"), article_version=item.get("article_version"),
                                     round3=True))
    with (OUT / "round3_evidence_segments.jsonl").open("w") as f:
        for s in segments:
            f.write(__import__("json").dumps(s, ensure_ascii=False, sort_keys=True) + "\n")

    att = S.extract_si_text(results)
    (OUT / "round3_attachment_parse_manifest.jsonl").write_text(
        "".join(__import__("json").dumps(a, ensure_ascii=False, sort_keys=True) + "\n" for a in att))

    avail = [r for r in results if r.get("status") == "fulltext_available"]
    print(f"round3 acquired-fulltext {len(avail)}/{len(results)}; segments {len(segments)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
