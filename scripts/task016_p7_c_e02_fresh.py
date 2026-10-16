"""C-E02 metadata discovery and G5 raw freeze. Never extracts reaction chemistry."""
from __future__ import annotations
import json
import re
import sys
import urllib.parse
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import (
    ROOT, TASK, ContractError, freeze_stage_manifest, now, role_manifest,
    save_json, sha_file, verify_stage_chain,
)
from scripts.task016_p7_source_harness import validate_query_accounting
from scripts.task016_p7_c_e02_http import (
    BASE, C, E, acquire, immutable_json, require_active, rows,
)
G4 = E / "stages/G4_SCOPE_FREEZE.json"
SCOPE = E / "scope_manifest.json"
DISCOVERY_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
EXPOSURE_FILES = (
    "outputs/task016-p7/v1/exposure_ledger.jsonl",
    "outputs/task016-p7/v1/epochs/C-E01/permanent_exposure_manifest.json",
    "outputs/task016-p7/v1/C/E01/permanent_exposure_closeout_v1/chemical_source_exposures.v2.jsonl",
    "outputs/task016-p7/v1/C/E01/permanent_exposure_closeout_v1/chemical_objects_and_fixtures_exposures.jsonl",
    "outputs/task016-p7/v1/C/E01/permanent_exposure_closeout_v1/permanent_source_blocklist.jsonl",
    "outputs/task016-p7/v1/C/E02/A6_design/v1/design_exposure_ledger.jsonl",
    "outputs/task016-p7/v1/C/E02/design_source_qualification/v1/science_source_review_v1/TcCGT_primary_source/permanent_design_source_exposure.json",
    "outputs/task016-p7/v1/C/E02/pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl",
    "outputs/task016-p7/v1/C/E02/pre_freeze_hypothesis_exposure/v1/permanent_exposure_manifest.json",
    "outputs/task016-p7/v1/epochs/SS-E01/closure_resolution_v1/effective_permanent_exposure_manifest.json",
    "outputs/task016-p7/v1/SS/E02_design/root_A6_graph_reconciliation/v1/permanent_design_exposure_manifest.json",
    "outputs/task016-p7/v1/SS/E02_design/root_A6_graph_reconciliation/v1/permanent_design_exposure_ledger.jsonl",
)
def rel(p):
    return str(Path(p).relative_to(ROOT))

def pointer(p):
    return dict(path=rel(p), sha256=sha_file(p))

def save_rows(p, rr):
    if p.exists():
        raise ContractError("immutable row output exists")
    write(TASK, rel(p), "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n" for r in rr))

def exposures():
    """Source-only projection; no graph values emitted or chemically inspected."""
    tokens = set()
    bound = {}
    def walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in {"source_tokens", "closure_tokens"} and isinstance(value, list):
                    tokens.update(x for x in value if isinstance(x, str) and x.startswith(("article:", "doi:", "pmid:")))
                if key in {"pmcid", "pmid", "doi", "source_pmcid"} and isinstance(value, str) and value:
                    prefix = "article:" if key in {"pmcid", "source_pmcid"} else key + ":"
                    tokens.add(prefix + (value.lower() if key == "doi" else value))
                if key in {"path", "source_package_manifest_path"} and isinstance(value, str) and value.startswith("outputs/task016-p7/v1/"):
                    p = ROOT / value
                    if p.is_file() and ("exposure" in p.name or "source_blocklist" in p.name):
                        if value not in bound:
                            consume(p)
                if key not in {"origins", "raw_chemical_fields"}:
                    walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)
    def consume(p):
        bound[rel(p)] = sha_file(p)
        walk(rows(p) if p.suffix == ".jsonl" else json.loads(p.read_text()))
    for name in EXPOSURE_FILES:
        p = ROOT / name
        if not p.is_file():
            raise ContractError("required permanent exposure input absent: " + name)
        if name not in bound:
            consume(p)
    return sorted(tokens), bound

def prepare(batch_id):
    if not re.fullmatch(r"C-E02-R[1-9][0-9]*", batch_id):
        raise ContractError("invalid batch ID")
    b = E / "fresh" / batch_id
    tokens, files = exposures()
    for p in (SCOPE, G4, ROOT / "scripts/task016_p7_c_e02_http.py", Path(__file__),
              ROOT / "scripts/task016_p7_source_harness.py"):
        files[rel(p)] = sha_file(p)
    verify_stage_chain(G4, sha_file(G4))
    queries = []
    keyword_queries = [
        ('("C-glycosyltransferase" OR "C-glucosyltransferase") AND flavone AND OPEN_ACCESS:Y', "primary_keyword"),
        ('("C-glycosylation" OR "C-glucosylation") AND ("6-C" OR "C6") AND OPEN_ACCESS:Y', "primary_keyword"),
        ('("UGT708" OR "CGT") AND flavone AND OPEN_ACCESS:Y', "enzyme_reverse"),
        ('("GtUF6CGT" OR "MiCGT" OR "UGT708A3" OR "UGT708C1") AND OPEN_ACCESS:Y', "enzyme_reverse"),
    ]
    for term, route in keyword_queries:
        queries.append(dict(query=term, route=route, url=DISCOVERY_BASE+"search?"+urllib.parse.urlencode(
            dict(query=term, format="json", resultType="lite", pageSize=100)), payload="search"))
    # Source identity checked in existing A3 records; citation relation is metadata.
    for pmid in ("29308528", "36434691", "31163097"):
        for endpoint in ("citations", "references"):
            queries.append(dict(query="MED/"+pmid+"/"+endpoint, route="citation_chase",
                                url=DISCOVERY_BASE+"MED/"+pmid+"/"+endpoint+"?"+urllib.parse.urlencode(dict(format="json",pageSize=100,page=1)),
                                payload=endpoint))
    for i, q in enumerate(queries, 1):
        q.update(query_id=batch_id+"-Q%02d"%i, database="EuropePMC", family="C",
                 scope_id="p7-C-E02:flavone_6_C_glucoside_C3_H", reason="Post-G4 metadata discovery; source closure checked before original download; no source qualification from scout",
                 max_pages=1, max_objects=100)
    plan = dict(task=TASK, family="C", epoch_id="C-E02", batch_id=batch_id, preregistered_at=now(),
                G4_pointer=pointer(G4), scope_pointer=pointer(SCOPE), files_sha256=files,
                historical_source_tokens=tokens, queries=queries,
                chemical_extraction_permitted=False, unknown_name_identity_fail_closed=True,
                metadata_title_selection_regex=r"C[- ]?(glycosyl|glucosyl)|glycosyltransferase|UGT708|\bCGT\b",
                maximum_primary_original_sources=20,
                primary_discovery_routes=["primary_keyword", "enzyme_reverse", "citation_chase"],
                route_completeness_not_assumed_from_one_metadata_page=True,
                hypothetical_name_exposure_count=16, future_holdout_name_synonym_identity_verification_required=True,
                read_model_outcome=False, human_reviewed=False, approval_type="agent_delegated")
    immutable_json(b / "query_plan.json", plan)
    require_active(b / "query_plan.json")
    print(json.dumps(dict(batch_id=batch_id, plan=pointer(b/"query_plan.json"), queries=len(queries), source_exclusion_tokens=len(tokens), chemistry_extracted=0)))

def source_hint(r):
    source = r.get("source")
    pmid = r.get("pmid") or (r.get("id") if source == "MED" else None)
    return {k:v for k,v in dict(pmcid=r.get("pmcid"), pmid=pmid, doi=r.get("doi"),
                                 title=r.get("title"), year=r.get("pubYear"), journal=r.get("journalTitle"),
                                 source=source, source_id=r.get("id"), is_open_access=r.get("isOpenAccess")).items()}

def hint_tokens(h):
    return set(("article:"+h["pmcid"],) if h.get("pmcid") else ()) | set(("pmid:"+str(h["pmid"]),) if h.get("pmid") else ()) | set(("doi:"+h["doi"].lower(),) if h.get("doi") else ())

def discover(batch_id):
    b = E / "fresh" / batch_id
    plan = require_active(b / "query_plan.json")
    if (b / "query_execution.jsonl").exists():
        raise ContractError("discovery round already fixed; no implicit rerun")
    discoveries = []
    executions = []
    rawpointers = []
    excluded = set(plan["historical_source_tokens"])
    for q in plan["queries"]:
        item = None
        rr = []
        failure = None
        total_hits = None
        try:
            item = acquire(b / "query_plan.json", q["url"], "metadata", q["query_id"]+" "+q["route"], object_limit=8*1024**2)
            rawpointers.append(pointer(ROOT/item["path"]))
            if item["status"] == "available":
                data = json.loads((ROOT/item["path"]).read_text())
                if q["payload"] == "search":
                    if "resultList" not in data or "result" not in data["resultList"]:
                        raise ContractError("metadata search response lacks result schema")
                    rr = data["resultList"]["result"]
                    total_hits = data.get("hitCount")
                else:
                    key = "citation" if q["payload"] == "citations" else "reference"
                    container = key+"List"
                    if container not in data:
                        # EuropePMC explicit zero-count responses can omit empty result lists.
                        count = data.get("hitCount")
                        if count != 0:
                            raise ContractError("citation response missing declared result schema")
                    else:
                        rr = data[container].get(key, [])
                    total_hits = data.get("hitCount")
            else:
                failure = item["error"] or ("HTTP "+str(item["status_code"]))
        except ContractError as exc:
            if item is None:
                executions.append(dict(query_id=q["query_id"], status="skipped", skip_reason=str(exc),
                                       returned_count=0, deduplicated_count=0, pending_identity_count=0,
                                       admitted=0,deferred=0,rejected=0,metadata_only=0,new_closure_groups=0))
                continue
            failure = str(exc)
        except (ValueError, UnicodeError) as exc:
            failure = type(exc).__name__ + ": " + str(exc)
        if not isinstance(rr, list) or len(rr) > q["max_objects"]:
            raise ContractError("source metadata result schema/page limit invalid")
        unique = {}
        for r in rr:
            if not isinstance(r, dict):
                raise ContractError("source metadata row is not object")
            h = source_hint(r)
            key = h.get("pmcid") or h.get("doi") or h.get("pmid") or (str(h.get("source"))+":"+str(h.get("source_id")))
            if key == "None:None":
                key = "unresolved:" + __import__("hashlib").sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()
            unique.setdefault(str(key), h)
        per = []
        for i, h in enumerate(unique.values(), 1):
            overlap = sorted(hint_tokens(h) & excluded)
            d = dict(record_id=q["query_id"]+"-D%03d"%i, query_id=q["query_id"],
                     disposition="rejected" if overlap else "metadata_only", source_hint=h,
                     metadata_only=True, chemical_extracted=False, evidence_eligible=False, source_identity_verified=False,
                     historical_source_overlap=overlap, reason="Permanent source exposure" if overlap else "Metadata hint; A3/A4/A5 and name/source closure gates pending",
                     raw_pointer=pointer(ROOT/item["path"]) if item else None)
            per.append(d)
        discoveries.extend(per)
        executions.append(dict(query_id=q["query_id"],status="executed",returned_count=len(rr),deduplicated_count=len(per),
                               pending_identity_count=sum(x["disposition"]=="metadata_only" for x in per), admitted=0,deferred=0,
                               rejected=sum(x["disposition"]=="rejected" for x in per),metadata_only=sum(x["disposition"]=="metadata_only" for x in per),
                               new_closure_groups=0,error=failure,reported_hit_count=total_hits,
                               metadata_page_is_not_full_chemical_round=True,http_attempt_id=item["attempt_id"] if item else None))
        print(json.dumps(dict(query_id=q["query_id"],returned=len(rr),rejected=sum(bool(x["historical_source_overlap"]) for x in per),error=failure)), flush=True)
    save_rows(b / "query_execution.jsonl", executions)
    save_rows(b / "source_dispositions.jsonl", discoveries)
    audit = validate_query_accounting(plan, executions, discoveries)
    audit.update(chemical_review_complete=False, new_qualified_groups=0, saturation=False, no_model_read=True)
    immutable_json(b / "query_audit.json", audit)
    immutable_json(b / "metadata_raw_manifest.json",dict(files_sha256={p["path"]:p["sha256"] for p in rawpointers},contains_reaction_graphs=False))

def plan_originals(batch_id):
    b = E / "fresh" / batch_id
    plan = require_active(b / "query_plan.json")
    audit = json.loads((b / "query_audit.json").read_text())
    if not audit["conserved"]:
        raise ContractError("metadata discovery not conserved")
    chosen = {}
    unresolved = []
    ignored = []
    for d in rows(b / "source_dispositions.jsonl"):
        if d["disposition"] == "rejected":
            continue
        h = d["source_hint"]
        title = h.get("title") or ""
        if not re.search(plan["metadata_title_selection_regex"], title, re.I):
            ignored.append(dict(record_id=d["record_id"], reason="Does not meet preregistered title metadata selection; chemical content not read"))
            continue
        if not h.get("pmcid"):
            unresolved.append(d["record_id"])
            continue
        chosen.setdefault(h["pmcid"], dict(record_id=d["record_id"], metadata_hint=h))
    picks = list(chosen.values())[:plan["maximum_primary_original_sources"]]
    files = {rel(b/n):sha_file(b/n) for n in ("query_plan.json","query_execution.jsonl","source_dispositions.jsonl","query_audit.json")}
    contract = dict(plan)
    contract.update(preregistered_at=now(),files_sha256=dict(plan["files_sha256"],**files), chosen=picks,
                    unresolved_identifier_hints=unresolved, metadata_title_nonmatches=ignored,
                    remaining_matching_hints=len(chosen)-len(picks),
                    license_gate="official PMC metadata explicit CC license and not retracted; original remains unqualified",
                    planned_original_api="PMC official OA opendata metadata index and its exact first-party XML URL",
                    chemical_extraction_permitted=False, contains_final_reaction_graphs=False)
    immutable_json(b / "original_intake_plan.json", contract)
    print(json.dumps(dict(chosen=len(picks), unresolved=len(unresolved), remaining=len(chosen)-len(picks))))


def acquire_originals(batch_id):
    b = E / "fresh" / batch_id
    cp = b / "original_intake_plan.json"
    contract = require_active(cp)
    if (b / "article_acquisition.json").exists():
        raise ContractError("original intake already terminal; no implicit rerun")
    results = []
    for selected in contract["chosen"]:
        pid = selected["metadata_hint"]["pmcid"]
        index = acquire(cp, "https://pmc-oa-opendata.s3.amazonaws.com/"+pid+".1/"+pid+".1.json",
                        "metadata", "Post-G4 official PMC OA identity/license index "+pid, object_limit=8*1024**2)
        m = None
        problem = None
        xml = None
        if index["status"] == "available":
            try:
                m = json.loads((ROOT / index["path"]).read_text())
                if not isinstance(m, dict):
                    raise ContractError("official PMC index not an object")
            except (ValueError, UnicodeError, ContractError) as exc:
                problem = type(exc).__name__ + ": " + str(exc)
        if m is not None:
            lic = m.get("license_code")
            if not isinstance(lic, str) or not lic.startswith("CC") or m.get("is_retracted") is not False:
                problem = "LICENSE_OR_EXPLICIT_RETRACTION_FLAG_UNRESOLVED"
            else:
                url = m.get("xml_url")
                if isinstance(url, str):
                    url = url.replace("s3://pmc-oa-opendata/", "https://pmc-oa-opendata.s3.amazonaws.com/")
                if not isinstance(url, str) or not url.startswith("https://pmc-oa-opendata.s3.amazonaws.com/"):
                    problem = "OFFICIAL_EXACT_XML_URL_UNRESOLVED"
                else:
                    xml = acquire(cp, url, "article_version", "Post-G4 official original for later independent A3/A4/A5 "+pid, license=lic)
        result = dict(pmcid=pid, source_hint=selected["metadata_hint"], record_id=selected["record_id"],
                      metadata=index, xml=xml, license=m.get("license_code") if m else None,
                      media_urls=m.get("media_urls",[]) if m else [],
                      status="raw_original_acquired_pending_A3_A4_A5" if xml and xml["status"] == "available" else "source_access_or_license_deferred",
                      deferred_reason=problem or (xml["error"] if xml and xml["status"] != "available" else index["error"] if index["status"]!="available" else None),
                      source_identity_verified=False, evidence_eligible=False, chemical_extracted=False,
                      G4_pointer=contract["G4_pointer"], downloaded_at=now(), future_freshness_not_yet_verified=True)
        results.append(result)
        append_path = b / "article_acquisition.progress.jsonl"
        from scripts.task016_p7_c_e02_http import append
        append(append_path,result)
        print(json.dumps(dict(pmcid=pid,status=result["status"],deferred_reason=result["deferred_reason"])),flush=True)
    immutable_json(b / "article_acquisition.json", results)
    immutable_json(b / "article_intake_summary.json",dict(planned=len(contract["chosen"]),terminal=len(results),
                   raw_originals_acquired=sum(r["status"]=="raw_original_acquired_pending_A3_A4_A5" for r in results),
                   source_deferred=sum(r["status"]=="source_access_or_license_deferred" for r in results),
                   chemical_extracted=0,source_qualified=0,fresh_admitted=0,chemical_round_complete=False,saturation=False))

def freeze_raw(batch_id):
    b = E / "fresh" / batch_id
    cp = b / "original_intake_plan.json"
    plan = require_active(cp)
    dest = E / "stages/batches" / batch_id
    names = ("query_plan.json","query_execution.jsonl","source_dispositions.jsonl","query_audit.json",
             "metadata_raw_manifest.json","original_intake_plan.json","article_acquisition.json","article_intake_summary.json")
    files = []
    raw = {}
    for name in names:
        p = b / name
        obj = rows(p) if p.suffix == ".jsonl" else json.loads(p.read_text())
        def collect(value):
            if isinstance(value, dict):
                if str(value.get("path","")).startswith("data/raw/") and value.get("sha256"):
                    rp = ROOT / value["path"]
                    if sha_file(rp) != value["sha256"]:
                        raise ContractError("raw source SHA drift")
                    raw[value["path"]] = value["sha256"]
                for child in value.values():
                    collect(child)
            elif isinstance(value,list):
                for child in value:
                    collect(child)
        collect(obj)
        target = dest / "intake_snapshot" / name
        if target.exists():
            raise ContractError("G5 raw snapshot exists")
        write(TASK,rel(target),p.read_text())
        files.append(target)
    batch_attempts = [r for r in rows(C / "http_ledger.jsonl") if r.get("epoch_id")=="C-E02" and r.get("batch_id")==batch_id]
    batch_plans = [r for r in rows(C / "acquisition_plan.jsonl") if r.get("epoch_id")=="C-E02" and r.get("batch_id")==batch_id]
    if {r["attempt_id"] for r in batch_attempts} != {r["attempt_id"] for r in batch_plans} or len(batch_attempts)!=len(batch_plans):
        raise ContractError("batch request plan/execution do not conserve")
    for r in batch_attempts:
        rp = ROOT / r["path"]
        if sha_file(rp)!=r["sha256"] or rp.stat().st_size!=r["bytes"]:
            raise ContractError("batch raw bytes/SHA drift")
        raw[r["path"]] = r["sha256"]
    for name, rr in (("http_ledger.snapshot.jsonl",batch_attempts),("http_plan.snapshot.jsonl",batch_plans)):
        target=dest/"intake_snapshot"/name
        save_rows(target,rr)
        files.append(target)
    files.extend(ROOT / p for p in raw)
    for p in plan["files_sha256"]:
        files.append(ROOT / p)
    manifest = dict(task=TASK,family="C",epoch_id="C-E02",batch_id=batch_id,frozen_at=now(),
                    G4_pointer=pointer(G4),scope_pointer=pointer(SCOPE),
                    files_sha256={rel(p):sha_file(p) for p in files},raw_only=True,chemical_extraction_started=False,
                    chemical_extraction_permitted_only_after_verified_G5=True,source_identity_verified=False,
                    source_scientific_qualified=0,fresh_admitted=0,unknown_name_identity_fail_closed=True,
                    permanent_name_hypotheses=16,permanent_name_exposure_pointer=pointer(ROOT/EXPOSURE_FILES[8]),
                    human_reviewed=False,read_model_outcome=False)
    mp=dest/"raw_intake_manifest.json"
    immutable_json(mp,manifest)
    files.append(mp)
    freeze_stage_manifest(dest,"G5_FRESH_HOLDOUT_ACQUIRE",list(dict.fromkeys(files)),G4,
                          expected_previous_sha=sha_file(G4),family="C",epoch_id="C-E02")
    stage=dest/"G5_FRESH_HOLDOUT_ACQUIRE.json"
    verify_stage_chain(stage,sha_file(stage))
    articles=json.loads((b/"article_acquisition.json").read_text())
    inputs=dict(task=TASK,family="C",epoch_id="C-E02",batch_id=batch_id,created_at=now(),
                G5_pointer=pointer(stage),G4_pointer=pointer(G4),contains_final_graphs=False,raw_only=True,
                sources=[dict(pmcid=r["pmcid"],source_hint=r["source_hint"],metadata_pointer=pointer(ROOT/r["metadata"]["path"]),
                              xml_pointer=pointer(ROOT/r["xml"]["path"]) if r.get("xml") and r["xml"]["status"]=="available" else None,
                              license=r["license"],media_urls=r["media_urls"],status=r["status"],
                              evidence_eligible=False,source_identity_verified=False) for r in articles],
                permanent_exposure_files_sha256=plan["files_sha256"],name_synonym_identity_gate_required=True,
                read_model_outcome=False,human_reviewed=False)
    inputpath=dest/"fresh_source_input_manifest.json"
    immutable_json(inputpath,inputs)
    role=role_manifest("A1 C Source Scout","C-E02",[cp,G4],[mp,stage,inputpath],
                       dict(processed=len(articles),passed=0,rejected=0,pending=len(articles)),
                       errors=[r["deferred_reason"] for r in articles if r.get("deferred_reason")],
                       unprocessed=["A3 source publication identity","Independent A4/A5 chemical extraction","A6 source/name/reaction closure qualification"],
                       read_holdout=False,read_model_outcome=False)
    role.update(passed_counter_is_not_HTTP_success=True,chemical_extraction_count=0,raw_originals=sum(r.get("xml") is not None and r["xml"]["status"]=="available" for r in articles))
    immutable_json(dest/"role_A1_raw_intake_manifest.json",role)
    from scripts.task016_p7_c_e02_http import append
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",event_type="verified_existing_stage_registration",
           stage="G5_FRESH_HOLDOUT_ACQUIRE",batch_id=batch_id,stage_manifest_path=rel(stage),stage_manifest_sha256=sha_file(stage),
           registered_at=now(),approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G5=pointer(stage),source_inputs=pointer(inputpath),raw_objects=len(raw),source_qualified=0,fresh_admitted=0)))

if __name__ == "__main__":
    command, batch = sys.argv[1:3]
    {"prepare":prepare, "discover":discover, "plan_originals":plan_originals, "acquire_originals":acquire_originals, "freeze_raw":freeze_raw}[command](batch)
