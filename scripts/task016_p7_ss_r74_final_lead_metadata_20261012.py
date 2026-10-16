"""SS-E02 R74: final fresh-lead legal-OA resolution; metadata only, no content reads.

Discovers whether any legal open-access copy exists for the only mechanically
fresh remaining SS-E02 candidate (Jourdan & Mansell 1982, pea flavonol
triglucoside glucosyltransferases, metadata-only R11 hint) and five old-literature
sibling leads. Crossref identity + OpenAlex OA status. No article body, no SI,
no chemistry, no saturation over-claim inside this batch.
"""
from __future__ import annotations
import fcntl, json, uuid, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone
from scripts.operate import ROOT, write, event
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect
from scripts.task016_p7_ss_sources import require_acquisition_phase
from scripts.task016_p7_orchestrate import sha_file, verify_stage_chain

TASK = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1"
RAW = Path("data/raw/task016-p7/SS/E02/SS-E02-R74-final-lead-metadata-v1")
LOCK = B / "source_budget_acquisition.lock"
G4 = B / "SS/E02/stages/G4_SCOPE_FREEZE.json"
G5 = B / "SS/E02/stages/batches/SS-E02-R73-five-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
SCOPE = B / "SS/E02/scope_manifest.json"
EPOCH = "SS-E02"; SCOPE_ID = "p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1"

# (lead_id, doi, label, prior_local_status)
LEADS = [
 ("SS-R74-L01", "10.1016/0003-9861(82)90569-0",
  "Jourdan & Mansell 1982 ABB 213:434-443, isolation/partial characterization of three Pisum sativum glucosyltransferases (flavonol triglucoside biosynthesis)",
  "R11 metadata-only discovery hint (R11-RESOLVE-DB-01-O0014); identity_not_verified; historical_source_token_overlap empty; never chemically examined; no exposure-ledger row"),
 ("SS-R74-L02", "10.1016/S0031-9422(00)84283-1",
  "Kamsteeg et al. 1979 Phytochemistry 18:659 (session web lead from 1982 reference list)",
  "not located in P7 metadata stores; content unknown"),
 ("SS-R74-L03", "10.1016/S0044-328X(78)80261-X",
  "Kho et al. 1978 Z. Pflanzenphysiol 88:449 (session web lead from 1982 reference list)",
  "not located in P7 metadata stores; content unknown"),
 ("SS-R74-L04", "10.1016/0005-2744(73)90027-2",
  "Sutter & Grisebach 1973 BBA 309:289 (session web lead from 1982 reference list)",
  "single SS-side metadata hint disposition file only; content unknown"),
 ("SS-R74-L05", "10.1016/S0031-9422(00)91452-3",
  "Heinsbroek et al. 1979 Phytochemistry 18:935 (session web lead from 1982 reference list)",
  "C-E01-era metadata dispositions only; content unknown"),
 ("SS-R74-L06", "10.1515/znc-1977-9-1017",
  "Saylor & Mansell 1977 Z. Naturforsch. 32c (session web lead from 1982 reference list)",
  "C-E02-R11 metadata observations only; content unknown"),
]

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return sha_file(ROOT / p)
def read(p): return json.loads((ROOT / p).read_text())
def lines(p): return [json.loads(l) for l in (ROOT / p).read_text().splitlines() if l.strip()] if (ROOT / p).exists() else []
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(TASK, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def append(p, v):
    write(TASK, str(p), ((ROOT / p).read_text() if (ROOT / p).exists() else "") + json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")

def canonical(url):
    u = urllib.parse.urlsplit(url)
    return (u.hostname or "", urllib.parse.unquote(u.path).rstrip("/"), tuple(sorted(urllib.parse.parse_qsl(u.query, keep_blank_values=True))))

def counter(rr):
    return dict(HTTP=len(rr), bytes=sum(int(x.get("bytes", 0)) for x in rr),
                article_versions=sum(x.get("kind", x.get("role")) in ("article_version", "xml", "original_pdf") for x in rr),
                attachments=sum(x.get("kind", x.get("role")) == "attachment" for x in rr))

def plans():
    out = []
    doi = LEADS[0][1]
    out.append(dict(query_id="SS-R74-Q01", lead_id=LEADS[0][0], doi=doi,
        url="https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""),
        route="Crossref_exact_DOI_bibliographic_identity", kind="metadata",
        object_limit=2097152, max_pages=1, automatic_retry=False, automatic_redirect=False,
        scientific_content_read=False,
        permitted_projection=["DOI","title","author","container-title","volume","issue","page","published","publisher","type","is-referenced-by"]))
    for i, (lid, doi, label, prior) in enumerate(LEADS, start=2):
        out.append(dict(query_id="SS-R74-Q%02d" % i, lead_id=lid, doi=doi,
            url="https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe=""),
            route="OpenAlex_official_work_record_OA_status_and_legal_OA_location_resolution", kind="metadata",
            object_limit=2097152, max_pages=1, automatic_retry=False, automatic_redirect=False,
            scientific_content_read=False,
            permitted_projection=["id","doi","title","publication_year","host_venue","primary_location","open_access","best_oa_location","authorships","type"]))
    return out

def prereg():
    if (ROOT / OUT).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    verify_stage_chain(ROOT / G4, sha(G4)); verify_stage_chain(ROOT / G5, sha(G5))
    ps = plans()
    with (ROOT / LOCK).open("a+") as l:
        fcntl.flock(l.fileno(), fcntl.LOCK_EX)
        gate = require_acquisition_phase("fresh", epoch_id=EPOCH, scope_id=SCOPE_ID)
        attempts = physical_attempts()
        for q in ps: q["prior_exact_canonical_URL_attempts"] = sum(canonical(x["url"]) == canonical(q["url"]) for x in attempts)
        budget = dict(global_before=counter(attempts), SS_before=counter([r for r in attempts if "SS" in Path(r.get("path", "")).parts]))
        fcntl.flock(l.fileno(), fcntl.LOCK_UN)
    save(OUT / "precontract.json", dict(task=TASK, epoch_id=EPOCH, batch="SS-E02-R74",
        created_at=now(), approval_type="agent_delegated", human_reviewed=False,
        purpose="Legal-OA resolution for the only mechanically fresh remaining SS-E02 candidate and five old-literature sibling leads; Crossref identity + OpenAlex OA status; metadata only; no article/SI content read; no chemistry; no saturation over-claim inside this batch",
        registered_input_SHA={str(p): sha(p) for p in (G4, G5, SCOPE, Path("scripts/task016_p7_ss_r74_final_lead_metadata_20261012.py"),
            B / "exposure_ledger.jsonl", B / "governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl",
            B / "SS/E02/fresh/SS-E02-R10-new-source-discovery-v1/strict_title_dispositions_v1.json")},
        leads=[dict(lead_id=lid, doi=doi, label=label, prior_local_status=prior) for lid, doi, label, prior in LEADS],
        phase_gate=gate, budget_before=budget,
        batch_limits=dict(HTTP=7, bytes=7 * 2097152, article_versions=0, attachments=0),
        constraints=dict(metadata_only=True, no_source_bodies=True, no_si=True, no_new_mcts=True,
            old_URL_attempt_count_included=True, per_URL_cap=2, no_retry=True, no_redirect_follow=True,
            no_paywall_or_access_control_bypass=True, no_credentials=True,
            source_scientific_scope_status="unknown", not_fresh_from_metadata=True,
            no_eligibility_or_source_saturation_inferred=True,
            primary_lead_same_cohort_closure_risk_with_exposed_1979_pea_paper="must_be_adjudicated_by_A6_before_any_fresh_use")))
    save(OUT / "query_plan.json", dict(task=TASK, phase="fresh", queries=ps, planned=len(ps),
        registered_at=now(), precontract_sha=sha(OUT / "precontract.json")))
    print(json.dumps(dict(preregistered=len(ps), global_HTTP=budget["global_before"]["HTTP"], SS_HTTP=budget["SS_before"]["HTTP"])), flush=True)

HOSTS = {"api.crossref.org", "api.openalex.org"}

def acquire(q):
    if q not in read(OUT / "query_plan.json")["queries"]: raise RuntimeError("QUERY_NOT_PREREGISTERED")
    for p, h in read(OUT / "precontract.json")["registered_input_SHA"].items():
        if sha(Path(p)) != h: raise RuntimeError("REGISTERED_INPUT_DRIFT " + p)
    u = urllib.parse.urlsplit(q["url"])
    if u.scheme != "https" or u.hostname not in HOSTS: raise RuntimeError("UNAPPROVED_HOST")
    with (ROOT / LOCK).open("a+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            require_acquisition_phase("fresh", epoch_id=EPOCH, scope_id=SCOPE_ID)
            attempts = physical_attempts(); before = counter(attempts)
            sub = counter([r for r in attempts if "SS" in Path(r.get("path", "")).parts])
            same = [r for r in attempts if canonical(r["url"]) == canonical(q["url"])]
            if len(same) >= 2 or any(r.get("status_code") in (401, 403) for r in same):
                return dict(query_id=q["query_id"], result="rejected_old_url", HTTP=0)
            if before["HTTP"] + 1 > 8000 or before["bytes"] + q["object_limit"] > 8 * 1024**3: raise RuntimeError("GLOBAL_BUDGET_STOP")
            if sub["HTTP"] + 1 > 2500 or sub["bytes"] + q["object_limit"] > 2 * 1024**3: raise RuntimeError("SS_BUDGET_STOP")
            if len(lines(OUT / "http_ledger.jsonl")) >= 7: raise RuntimeError("BATCH_HTTP_MAX")
            aid = "SS-E02-R74-" + uuid.uuid4().hex
            start = now()
            prereg = dict(attempt_id=aid, query_id=q["query_id"], url=q["url"], family="SS", epoch_id=EPOCH,
                source_id=q["lead_id"], kind="metadata", phase="fresh", registered_at=start,
                object_limit=q["object_limit"], prior_canonical_url_count=len(same),
                precontract_SHA=sha(OUT / "precontract.json"), query_plan_SHA=sha(OUT / "query_plan.json"),
                budget_before=before, SS_before=sub, scope_G4_SHA=sha(G4),
                method="GET", automatic_retry=False, automatic_redirect=False)
            append(OUT / "physical_request_preregistration.jsonl", prereg)
            data = b""; status = None; error = None; location = None; response = None
            try:
                request = urllib.request.Request(q["url"], headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 (public science metadata)", "Accept-Encoding": "identity"})
                try: response = urllib.request.build_opener(NoRedirect()).open(request, timeout=30)
                except urllib.error.HTTPError as e: response = e; error = f"HTTP_{e.code}"
                status = response.code; location = response.geturl()
                data = response.read(q["object_limit"] + 1)
                if len(data) > q["object_limit"]: data = data[:q["object_limit"]]; error = "OBJECT_LIMIT_TRUNCATED"
                if location != q["url"] or 300 <= status < 400: error = "NO_REDIRECT_FOLLOW"
            except Exception as e: error = type(e).__name__ + ":" + str(e)[:150]
            finally:
                if response is not None: response.close()
            raw = RAW / (aid + ".metadata"); p = ROOT / raw
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists(): raise RuntimeError("RAW_IMMUTABLE_EXISTS")
            p.write_bytes(data); p.chmod(0o444); event(TASK, "write_binary", path=str(raw), before=None, after=sha(raw), bytes=len(data))
            rec = dict(attempt_id=aid, query_id=q["query_id"], source_id=q["lead_id"], url=q["url"],
                final_url=location, kind="metadata", role="metadata", phase="fresh", epoch_id=EPOCH,
                batch_id="SS-E02-R74-final-lead-metadata-v1", status_code=status, bytes=len(data),
                status="available" if status == 200 and error is None else "failed",
                error=error, path=str(raw), sha256=sha(raw), started_at=start, finished_at=now(),
                scientific_body_content_read=False, chemical_extracted=False, metadata_only=True,
                no_recovery=True, no_redirect_follow=True, precontract_SHA=sha(OUT / "precontract.json"))
            append(OUT / "http_ledger.jsonl", rec); event(TASK, "source_http", **rec)
            return rec
        finally: fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def run():
    for q in read(OUT / "query_plan.json")["queries"]:
        if any(r["query_id"] == q["query_id"] for r in lines(OUT / "query_execution.jsonl")): continue
        r = acquire(q)
        records = None; error = None
        if r.get("status") == "available":
            try:
                data = json.loads((ROOT / r["path"]).read_text())
                if q["route"].startswith("Crossref"):
                    msg = data.get("message", {})
                    records = {k: msg.get(k) for k in q["permitted_projection"] if k in msg}
                else:
                    records = {k: data.get(k) for k in q["permitted_projection"] if k in data}
            except Exception as exc: error = type(exc).__name__ + ":" + str(exc)[:100]
        append(OUT / "query_execution.jsonl", dict(query_id=q["query_id"], lead_id=q["lead_id"], doi=q["doi"],
            route=q["route"], status=r.get("status"), status_code=r.get("status_code"),
            raw_pointer={k: r.get(k) for k in ("path", "sha256", "bytes")},
            records=records, error=error or r.get("error"),
            scientific_body_content_read=False, chemical_extracted=False))
        print(json.dumps(dict(q=q["query_id"], lead=q["lead_id"], status=r.get("status_code"), err=error or r.get("error"))), flush=True)

def finish():
    executions = lines(OUT / "query_execution.jsonl"); plan = read(OUT / "query_plan.json")["queries"]
    planned = len(plan); executed = len(executions)
    assert planned == executed, "QUERY_CONSERVATION_FAILURE"
    by_lead = {}
    for e in executions: by_lead.setdefault(e["lead_id"], []).append(e)
    dispositions = []
    for lid, doi, label, prior in LEADS:
        es = by_lead.get(lid, [])
        cross = next((e for e in es if e["route"].startswith("Crossref")), None)
        oa = next((e for e in es if e["route"].startswith("OpenAlex")), None)
        identity = (cross or {}).get("records")
        oa_rec = (oa or {}).get("records")
        is_oa = bool(oa_rec and isinstance(oa_rec.get("open_access"), dict) and oa_rec["open_access"].get("is_oa"))
        best = oa_rec.get("best_oa_location") if isinstance(oa_rec, dict) else None
        if is_oa and isinstance(best, dict) and (best.get("pdf_url") or best.get("landing_page_url")):
            disposition = "legal_OA_copy_located_pending_preregistered_acquisition"
        else:
            disposition = "no_legal_OA_copy_located_access_blocked_at_metadata_level"
        dispositions.append(dict(lead_id=lid, doi=doi, label=label, prior_local_status=prior,
            crossref_identity=identity, openalex_oa=oa_rec,
            legal_oa_copy_located=is_oa and isinstance(best, dict) and bool(best.get("pdf_url") or best.get("landing_page_url")),
            disposition=disposition,
            article_level_exclusion_claimed=False, reaction_universe_enumerated=False,
            scientific_body_content_read=False, fresh_admitted=0))
    attempts = physical_attempts()
    summary = dict(task=TASK, agent_role="A0_raw_custody", approval_type="agent_delegated", human_reviewed=False,
        at=now(), planned=planned, executed=executed,
        terminal=len([e for e in executions if e.get("status_code") is not None]),
        leads=[d["lead_id"] for d in dispositions],
        legal_OA_leads=[d["lead_id"] for d in dispositions if d["legal_oa_copy_located"]],
        access_blocked_leads=[d["lead_id"] for d in dispositions if not d["legal_oa_copy_located"]],
        potential_originals_for_A3=0, main_original_identity_pass=0, chemical_scientific_content_read=False,
        source_qualified=0, fresh_admitted=0, source_saturation_claim_in_batch=False,
        physical_HTTP_global=len(attempts), physical_bytes_global=sum(x["bytes"] for x in attempts),
        raw_bytes_added=sum(int(e.get("raw_pointer", {}).get("bytes", 0) or 0) for e in executions), MCTS_added=0)
    save(OUT / "final_lead_dispositions.json", dict(task=TASK, at=now(), epoch_id=EPOCH,
        batch="SS-E02-R74-final-lead-metadata-v1", dispositions=dispositions,
        conservation=dict(planned=planned, executed=executed),
        notes=["Pea 1982 (L01) remains the only mechanically fresh SS-E02 candidate found by this session's discovery; same-cohort closure risk with the development-exposed 1979 pea paper must be adjudicated by independent A6 before any fresh use; complete structure/stereo evidence inside the paywalled original is unverified.",
               "This batch proves only metadata/OA-status facts; it neither qualifies nor excludes any source's chemistry."]))
    save(OUT / "raw_custody_summary.json", summary)
    write(TASK, str(OUT / "physical_final_snapshot.jsonl"), "".join(json.dumps(x, sort_keys=True) + "\n" for x in attempts))
    print(json.dumps({k: summary[k] for k in ("planned", "executed", "legal_OA_leads", "access_blocked_leads", "physical_HTTP_global", "physical_bytes_global")}), flush=True)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "prereg": prereg()
    elif mode == "run": run()
    elif mode == "finish": finish()
    else: raise SystemExit("prereg | run | finish")
