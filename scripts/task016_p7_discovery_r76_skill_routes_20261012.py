"""TASK-016-P7 R76: skill-routed new discovery routes (metadata only, no science reads).

New route forms not previously executed in P7, following the nature-academic-search
skill's query-construction guidance (MeSH-qualified full-field queries, NCBI elink
related-article citation chase, EPMC PPR preprint sweep). Both families. Every HTTP
is preregistered, observable, and ledgered; titles/DOIs/PMCIDs are projected only.
No chemistry, no saturation over-claim inside this batch.
"""
import hashlib, json, urllib.parse, urllib.request, urllib.error, uuid
from pathlib import Path
from datetime import datetime, timezone

from scripts.operate import ROOT, write, event

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "discovery_r76_skill_routes_20261012"
RAW = Path("data/raw/task016-p7/discovery_r76_skill_routes_20261012")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
SS_EXPOSED_PMCIDS = ["PMC5856881", "PMC4282749", "PMC4494776", "PMC12611259"]
C_EXPOSED_PMCIDS = ["PMC13564134", "PMC2709393", "PMC7720146"]

def now(): return datetime.now(timezone.utc).isoformat()
def sha_file(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(T, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def append(p, v):
    write(T, str(p), ((ROOT / p).read_text() if (ROOT / p).exists() else "") + json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")

def plan_slots():
    s = []
    def add(qid, family, route, url, reason):
        s.append(dict(query_id=qid, family=family, route=route, url=url, reason=reason, kind="metadata", object_limit=2097152))
    # SS: MeSH-qualified full-field searches (new form; prior rounds were TITLE-only)
    add("R76-SS-SEARCH-01", "SS", "pubmed_esearch_fullfield",
        EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", term='sophoroside[All Fields] AND ("glucosyltransferase"[All Fields] OR "glycosyltransferase"[All Fields] OR UGT[All Fields])', retmax=100, retmode="json")),
        "MeSH-free full-field sweep for sophoroside-forming GT papers, all years (new form vs prior TITLE-only rounds)")
    add("R76-SS-SEARCH-02", "SS", "pubmed_esearch_mesh",
        EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", term='"Flavonoids"[MeSH Major Topic] AND (sophoroside[All Fields] OR "glucosyltransferase"[Title/Abstract])', retmax=100, retmode="json")),
        "MeSH-qualified flavonoid/GT intersection (new form)")
    # SS: official related-article citation chase from the four exposed O2 papers
    add("R76-SS-IDCONV-01", "SS", "ncbi_idconv_pmids",
        "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?" + urllib.parse.urlencode(dict(ids=",".join(SS_EXPOSED_PMCIDS), format="json")),
        "Resolve exposed SS PMCID set to PMIDs for elink")
    add("R76-SS-ELINK-01", "SS", "pubmed_elink_related", "TEMPLATE:idconv_pmids", "Related-article chase from exposed O2 GT papers")
    add("R76-SS-ELINK-02", "SS", "pubmed_esummary_related", "TEMPLATE:elink_related_ids", "Project titles/DOIs of related PMIDs")
    add("R76-SS-PPR-01", "SS", "europepmc_preprints",
        EPMC + urllib.parse.urlencode(dict(query='SRC:PPR AND (sophoroside OR "glucosyltransferase") AND (flavonol OR flavonoid)', format="json", pageSize=100)),
        "Preprint-only sweep (bioRxiv/RRS via EPMC PPR source; new route)")
    # C: C-glycosylation full-field + MeSH old-literature catch + chase
    add("R76-C-SEARCH-01", "C", "pubmed_esearch_fullfield",
        EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", term='("C-glycosyltransferase"[All Fields] OR "C-glucosyltransferase"[All Fields] OR "C-glycosylation"[All Fields] OR "C-glucosylation"[All Fields]) AND (flavone[All Fields] OR "Flavones"[MeSH])', retmax=100, retmode="json")),
        "Full-field C-glycosylation x flavone sweep, all years (new form)")
    add("R76-C-SEARCH-02", "C", "pubmed_esearch_mesh",
        EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", term='"Glucosyltransferases"[MeSH] AND "Flavones"[MeSH]', retmax=100, retmode="json")),
        "MeSH x MeSH old-literature catch including papers lacking C- terminology")
    add("R76-C-SUM-01", "C", "pubmed_esummary_search01", "TEMPLATE:search01_ids", "Project search01 hits")
    add("R76-C-SUM-02", "C", "pubmed_esummary_search02", "TEMPLATE:search02_ids", "Project search02 hits")
    add("R76-C-IDCONV-01", "C", "ncbi_idconv_pmids",
        "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?" + urllib.parse.urlencode(dict(ids=",".join(C_EXPOSED_PMCIDS), format="json")),
        "Resolve exposed C PMCID set to PMIDs for elink")
    add("R76-C-ELINK-01", "C", "pubmed_elink_related", "TEMPLATE:idconv_pmids", "Related-article chase from exposed C CGT papers")
    add("R76-C-ELINK-02", "C", "pubmed_esummary_related", "TEMPLATE:elink_related_ids", "Project titles/DOIs of related PMIDs")
    add("R76-C-PPR-01", "C", "europepmc_preprints",
        EPMC + urllib.parse.urlencode(dict(query='SRC:PPR AND ("C-glycosyltransferase" OR "C-glucosyltransferase")', format="json", pageSize=100)),
        "Preprint-only C-GT sweep (new route)")
    return s

def http_get(url):
    start = now(); status = None; err = None; data = b""
    req = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7-R76/1.0 (public science metadata)", "Accept-Encoding": "identity"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status; data = r.read(2097153)
            if len(data) > 2097152: data = data[:2097152]; err = "OBJECT_LIMIT_TRUNCATED"
    except urllib.error.HTTPError as e:
        status = e.code; err = "HTTP_" + str(e.code)
        try: data = e.read(2097153)[:2097152]
        except Exception: pass
    except Exception as e:
        err = type(e).__name__ + ":" + str(e)[:150]
    aid = "R76-" + uuid.uuid4().hex
    ptr = RAW / (aid + ".metadata")
    p = ROOT / ptr
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists(): raise RuntimeError("RAW_IMMUTABLE_EXISTS")
    p.write_bytes(data); p.chmod(0o444)
    event(T, "write_binary", path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    rec = dict(attempt_id=aid, url=url, final_url=url, kind="metadata", role="metadata",
               phase="P7_R76_skill_routes_discovery_metadata", batch_id="R76-skill-routes",
               status_code=status, bytes=len(data), status="available" if status == 200 and not err else "failed",
               error=err, path=str(ptr), sha256=hashlib.sha256(data).hexdigest(),
               started_at=start, finished_at=now(), scientific_body_content_read=False,
               chemical_extracted=False, metadata_only=True)
    event(T, "source_http", **rec)
    return rec, data

def jload(data):
    try: return json.loads(data)
    except Exception: return None

def prereg():
    if (ROOT / OUT).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    slots = plan_slots()
    save(OUT / "precontract.json", dict(task=T, batch="R76-skill-routes", created_at=now(),
        approval_type="agent_delegated", human_reviewed=False,
        purpose="nature-academic-search-routed new discovery routes for both families: MeSH-qualified full-field PubMed queries, NCBI elink related-article chase from exposed papers, EPMC PPR preprint sweeps; metadata only; titles/DOIs/PMCIDs projected; no science-body or SI content; no chemistry; no eligibility granted and no saturation claimed inside this batch",
        constraints=dict(metadata_only=True, no_source_bodies=True, no_si=True, no_new_mcts=True,
            no_retry=True, per_url_cap=2, no_paywall_or_access_control_bypass=True,
            not_fresh_from_metadata=True, no_eligibility_inferred=True),
        batch_limits=dict(HTTP=16, bytes=16 * 2097152),
        families=["C", "SS"],
        routes_note="MCP tools of the academic-search skill are unavailable in this environment (tool_search: 0 hits); this round implements the same query-construction guidance through the project's own preregistered observable HTTP path"))
    save(OUT / "query_plan.json", dict(task=T, planned=len(slots), slots=slots, registered_at=now()))
    print(json.dumps(dict(preregistered=len(slots))), flush=True)

def run():
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    state = {}
    for r in _exec_rows():
        if r.get("status_code") is None: continue
        qid = r["query_id"]
        ids = [h.get("pmid") for h in (r.get("hits") or []) if h.get("pmid")]
        if r["route"].endswith("esearch_fullfield") or r["route"].endswith("esearch_mesh"):
            state[qid + "_ids"] = ids
            if qid.endswith("-01"): state["search01_ids"] = ids
            if qid.endswith("-02"): state["search02_ids"] = ids
        elif r["route"] == "ncbi_idconv_pmids":
            if ids:
                state["idconv_pmids"] = ids
            else:
                rp = r.get("raw_pointer") or {}
                rp_path = rp.get("path")
                if rp_path and (ROOT / rp_path).is_file():
                    try:
                        rec = json.loads((ROOT / rp_path).read_text())
                        pmids = [row.get("pmid") for row in (rec.get("records") or []) if row.get("pmid")]
                        state["idconv_pmids"] = pmids
                    except Exception:
                        pass
        elif r["route"] == "pubmed_elink_related":
            state["elink_related_ids"] = ids
    for slot in plan["slots"]:
        qid = slot["query_id"]
        if any(r["query_id"] == qid and r.get("status_code") is not None for r in _exec_rows()): continue
        url = slot["url"]
        if url.startswith("TEMPLATE:"):
            key = url.split(":", 1)[1]
            ids = state.get(key) or []
            if not ids:
                append(OUT / "query_execution.jsonl", dict(query_id=qid, status="skipped_no_upstream_ids", url=None, records=[], error=None))
                continue
            if key == "idconv_pmids":
                url = EUTILS + "elink.fcgi?" + urllib.parse.urlencode(dict(dbfrom="pubmed", db="pubmed", id=",".join(str(x) for x in ids), linkname="pubmed_pubmed", retmode="json"))
            elif key == "elink_related_ids":
                url = EUTILS + "esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=",".join(str(x) for x in ids[:60]), retmode="json"))
            elif key.startswith("search0"):
                url = EUTILS + "esummary.fcgi?" + urllib.parse.urlencode(dict(db="pubmed", id=",".join(str(x) for x in ids[:100]), retmode="json"))
        rec, data = http_get(url)
        hits = []; upstream = []
        res = jload(data)
        route = slot["route"]
        if res is not None and rec["status"] == "available":
            if route.endswith("esearch_fullfield") or route.endswith("esearch_mesh"):
                ids = (res.get("esearchresult") or {}).get("idlist") or []
                state[qid + "_ids"] = ids
                if qid.endswith("-01"): state["search01_ids"] = ids
                if qid.endswith("-02"): state["search02_ids"] = ids
                upstream = ids
                hits = [dict(pmid=i) for i in ids]
            elif route == "ncbi_idconv_pmids":
                pmids = []
                for row in res.get("records", []) or []:
                    if row.get("pmid"): pmids.append(row["pmid"])
                state["idconv_pmids"] = pmids
                hits = [dict(pmcid=r.get("pmcid"), pmid=r.get("pmid"), live=r.get("live")) for r in res.get("records", []) or []]
            elif route == "pubmed_elink_related":
                rel = []
                for block in (res.get("linksets") or []):
                    for lb in block.get("linksetdbs", []) or []:
                        if lb.get("linkname") == "pubmed_pubmed":
                            rel.extend(lb.get("links", [])[:60])
                state["elink_related_ids"] = sorted(set(rel))
                hits = [dict(pmid=i) for i in sorted(set(rel))[:60]]
            elif route.startswith("pubmed_esummary"):
                for pid, doc in (res.get("result") or {}).get("uids", []) and []: pass
                uids = (res.get("result") or {}).get("uids") or []
                for uid in uids:
                    d = (res.get("result") or {}).get(uid) or {}
                    hits.append(dict(pmid=uid, title=d.get("title"), doi=(d.get("articleids") or [{}]) and next((x.get("value") for x in d.get("articleids", []) if x.get("idtype") == "doi"), None),
                                     pubdate=d.get("pubdate"), source=d.get("source"), pubtype=[p for p in (d.get("pubtype") or [])][:4]))
            elif route == "europepmc_preprints":
                for x in (res.get("resultList") or {}).get("result", []):
                    hits.append(dict(title=x.get("title"), doi=x.get("doi"), pmid=x.get("pmid"), pmcid=x.get("pmcid"),
                                     year=x.get("pubYear"), isOpenAccess=x.get("isOpenAccess"), source="PPR"))
        append(OUT / "query_execution.jsonl", dict(query_id=qid, family=slot["family"], route=route,
            url=url if not url.startswith("TEMPLATE:") else slot["url"],
            status=rec["status"], status_code=rec["status_code"], error=rec["error"],
            raw_pointer={k: rec[k] for k in ("path", "sha256", "bytes")},
            hits_count=len(hits), hits=hits[:100], upstream_ids=upstream[:100],
            scientific_body_content_read=False, chemical_extracted=False))
        print(json.dumps(dict(q=qid, status=rec["status_code"], hits=len(hits), err=rec["error"])), flush=True)

def _exec_rows():
    p = ROOT / OUT / "query_execution.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

def finish():
    plan = json.loads((ROOT / OUT / "query_plan.json").read_text())
    rows = _exec_rows()
    planned = plan["planned"]
    executed = len({r["query_id"] for r in rows if r.get("status_code") is not None})
    retried_skips = len(rows) - executed
    if planned != executed: raise RuntimeError("QUERY_CONSERVATION_FAILURE planned=%s executed=%s" % (planned, executed))
    # exposure cross-check (identifier-level; mechanical)
    exp_tokens = set()
    exp_files = ["exposure_ledger.jsonl", "governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl"]
    for rel in exp_files:
        for l in (ROOT / B / rel).read_text().splitlines():
            if not l.strip(): continue
            try:
                row = json.loads(l)
                exp_tokens.update(row.get("closure_tokens", []) or [])
            except Exception: pass
    leads = {}; titles = {}
    for r in rows:
        for h in r.get("hits") or []:
            key = h.get("doi") or ("pmid:" + str(h.get("pmid")) if h.get("pmid") else h.get("title"))
            if not key: continue
            leads.setdefault(key, dict(hit=h, routes=set()))
            leads[key]["routes"].add(r["query_id"])
            if h.get("title"): titles[key] = h["title"]
    new_leads = []
    for key, v in leads.items():
        h = v["hit"]
        toks = set()
        if h.get("doi"): toks.add("doi:" + str(h["doi"]).lower())
        if h.get("pmid"): toks.add("pmid:" + str(h["pmid"]))
        if h.get("pmcid"): toks.add("article:" + str(h["pmcid"]))
        overlap = sorted(toks & exp_tokens)
        if not overlap:
            new_leads.append(dict(key=key, title=titles.get(key), hit=h, routes=sorted(v["routes"])))
    # authoritative deduplicated physical accounting
    from scripts.task016_p7_c_e02_http import physical_attempts
    att = physical_attempts()
    phys = len(att); phys_bytes = sum(int(x.get("bytes") or 0) for x in att)
    summary = dict(task=T, at=now(), planned=planned, executed=executed, retried_skipped_rows=retried_skips,
        unique_hits=len(leads), new_identifier_leads=len(new_leads),
        new_leads=[dict(key=x["key"], title=x["title"], routes=x["routes"]) for x in new_leads[:80]],
        physical_HTTP_events_total=phys, physical_bytes_total=phys_bytes,
        MCTS_added=0, chemistry_examination_performed=False, fresh_admitted=0,
        saturation_claim=False, eligibility_inferred=False,
        note="Identifier-level exposure cross-check only: title/synonym-level closure remains a mandatory A6 step before any fresh use.")
    save(OUT / "disposition_summary.json", summary)
    write(T, str(OUT / "new_leads.jsonl"), "".join(json.dumps(dict(key=x["key"], title=x["title"], hit=x["hit"], routes=x["routes"]), ensure_ascii=False, sort_keys=True) + "\n" for x in new_leads))
    print(json.dumps(dict(planned=planned, executed=executed, unique=len(leads), new_leads=len(new_leads), phys=phys, phys_bytes=phys_bytes)), flush=True)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "prereg": prereg()
    elif mode == "run": run()
    elif mode == "finish": finish()
    else: raise SystemExit("prereg | run | finish")
