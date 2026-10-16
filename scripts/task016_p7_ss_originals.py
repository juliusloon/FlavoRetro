"""Post-freeze SS original-source intake, with exposed source exclusion."""
import argparse,json,re,sys,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,request,save,save_rows,rows,sha,now
from scripts.task016_p7_ss_fresh import historical
def guard():
    p=OUT/"scope_freeze.json"
    if not p.exists():raise RuntimeError("SS_SCOPE_NOT_FROZEN")
    f=json.loads(p.read_text())
    if not f["independently_verified"]:raise RuntimeError("SS_SCOPE_INDEPENDENT_VERIFICATION_PENDING")
    for name,expected in f["files_sha256"].items():
        path=ROOT/name if name.startswith(("outputs/","flavoretro/")) else OUT/name
        if sha(path)!=expected:raise RuntimeError("SS_SCOPE_SHA_DRIFT")
    return p,f
def metadata_lookup_doi(doi):
    url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query="DOI:"+doi,format="json",pageSize=3,resultType="core"))
    record=request(url,"metadata","Resolve bibliographic DOI hint to authoritative PMCID; no source eligibility inferred",phase="fresh",route="DOI_identity_lookup")
    if record["status_code"]!=200:return record,[]
    data=json.loads((ROOT/record["path"]).read_text())
    return record,data.get("resultList",{}).get("result",[])
def execute(limit=40):
    fp,freeze=guard();excluded=historical()
    candidates=rows(OUT/("fresh_source_dispositions_v2.jsonl" if (OUT/"fresh_source_dispositions_v2.jsonl").exists() else "fresh_source_dispositions.jsonl"))
    selected=[]
    for row in candidates:
        if row["historical_source"]:continue
        title=row["title"].lower()
        if any(key in title for key in ["rhamnosyltransferase","rutinoside","rutin biosynthesis","rutin synthesis","flavonol glycosyltransferase","sugar chain","disaccharide","flavonoid glycosyl"]):
            if any(key in title for key in ["review","perspective","plant cell wall","antiviral","rutin extraction"]):continue
            selected.append(row)
    selected.sort(key=lambda r:(not bool(r["pmcid"]),-len(r["routes"]),r["title"]))
    selected=selected[:limit]
    plan=[dict(selection_id="SS-FRESH-SOURCE:"+str(ix),discovery_key=row["discovery_key"],pmcid_hint=row["pmcid"],doi_hint=row["doi"],pmid_hint=row.get("pmid"),title_hint=row["title"],reason="post-freeze title-level primary enzyme/reaction/source intake; qualification by independent verifier later",source_closure_historical=False,registered_at=now(),scope_freeze_sha256=sha(fp)) for ix,row in enumerate(selected)]
    planpath=OUT/"fresh_original_source_plan.json"
    if planpath.exists():raise RuntimeError("FRESH_ORIGINAL_SOURCE_PLAN_ALREADY_REGISTERED")
    save("fresh_original_source_plan.json",dict(task_id="TASK-016-P7",epoch_id="SS-E01",scope_freeze_sha256=sha(fp),selections=plan,max_sources=limit,source_selection_uses_model_outcomes=False))
    disposition=[]
    pmcseen=set()
    for q in plan:
        pmcid=q["pmcid_hint"];lookup=None
        if not pmcid and q["doi_hint"]:
            lookup, matches=metadata_lookup_doi(q["doi_hint"])
            pmcids={m.get("pmcid") for m in matches if m.get("pmcid")}
            if len(pmcids)==1:pmcid=next(iter(pmcids))
        if not pmcid and q["pmid_hint"]:
            url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query="EXT_ID:"+str(q["pmid_hint"])+" AND SRC:MED",format="json",pageSize=3,resultType="core"))
            lookup=request(url,"metadata","Resolve citation PMID hint to authoritative PMCID",phase="fresh",route="citation_PMID_identity_lookup")
            if lookup["status_code"]==200:
                found=json.loads((ROOT/lookup["path"]).read_text()).get("resultList",{}).get("result",[])
                pmcids={m.get("pmcid") for m in found if m.get("pmcid")}
                if len(pmcids)==1:pmcid=next(iter(pmcids))
        record=dict(q,resolved_pmcid=pmcid,lookup=lookup,evidence_eligible=False,structure_complete=False,read_model_outcomes=False,chemically_read_at=None)
        if not pmcid:record.update(disposition="deferred_no_open_machine_readable_article",reason_code="no_pmcid_resolved")
        elif pmcid in excluded:record.update(disposition="rejected_historical_source_exposure",reason_code="source_in_project_exposure_ledger")
        elif pmcid in pmcseen:record.update(disposition="metadata_only_duplicate_source",reason_code="already_selected_same_pmcid")
        else:
            pmcseen.add(pmcid)
            meta=request(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.json","metadata","Acquire official original article identity, license and version descriptors",phase="fresh",route="PMC_authoritative_original")
            record["metadata"]=meta
            if meta["status_code"]!=200:
                xml=request(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML","xml","Official Europe PMC OA fulltext fallback after S3 metadata unavailable; no access-control circumvention",phase="fresh",route="EuropePMC_official_fulltext_fallback")
                record.update(xml=xml,disposition="deferred_identity_structure_independent_review" if xml["status_code"]==200 else "deferred_official_OA_not_available",reason_code="S3_metadata_failed_official_EPMC_XML_fallback",acquired_after_scope_freeze=True,media_urls=[],license="pending_source_JATS_license_read")
            else:
                m=json.loads((ROOT/meta["path"]).read_text())
                record["official_identity"]=dict(pmcid=m.get("pmcid"),doi=m.get("doi"),title=m.get("title"),citation=m.get("citation"),pmid=m.get("pmid"),license=m.get("license_code"))
                url=m.get("xml_url","").replace("s3://pmc-oa-opendata/","https://pmc-oa-opendata.s3.amazonaws.com/")
                if not url.startswith("https://pmc-oa-opendata.s3.amazonaws.com/"):record.update(disposition="deferred_original_XML_unavailable",reason_code="official_xml_url_absent")
                else:
                    xml=request(url,"xml","Post-scope original chemical source acquisition; source/structure admission still independent",phase="fresh",route="PMC_authoritative_original")
                    record.update(xml=xml,disposition="deferred_identity_structure_independent_review" if xml["status_code"]==200 else "deferred_original_XML_request_failed",reason_code="download_not_evidence_eligibility",acquired_after_scope_freeze=True,media_urls=m.get("media_urls",[]))
        disposition.append(record);save_rows("fresh_original_source_intake.jsonl",disposition)
    save("fresh_original_source_intake_summary.json",dict(task_id="TASK-016-P7",epoch_id="SS-E01",scope_freeze_sha256=sha(fp),planned=len(plan),executed=len(disposition),skipped=0,conserved=len(plan)==len(disposition),original_sources_downloaded=sum(bool(r.get("xml",{}).get("status_code")==200) for r in disposition),admitted=0,deferred=sum(r["disposition"].startswith("deferred") for r in disposition),rejected=sum(r["disposition"].startswith("rejected") for r in disposition),metadata_only=sum(r["disposition"].startswith("metadata_only") for r in disposition),source_structure_review_complete=False,saturation_claimed=False))
    print(dict(selected=len(plan),downloaded=sum(bool(r.get("xml",{}).get("status_code")==200) for r in disposition)))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--limit",type=int,default=40);args=p.parse_args();execute(args.limit)
