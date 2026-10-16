"""R5 raw originals via observed public source locators, before G5 and chemistry."""
import json,re,sys,urllib.parse
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import acquire,immutable_json,require_active,append
from scripts.task016_p7_c_e02_fresh import E,rows,pointer
B=E/"fresh/C-E02-R5";P=B/"raw_original_request_plan.json"
def prepare():
    prior=B/"public_location_intake_plan.json";p=require_active(prior)
    metadata=rows(B/"exact_13_MED_primary_hint_metadata.jsonl")
    locations={x["source_id"]:x for x in rows(B/"13_hint_public_location_resolution.jsonl")}
    req=[];ignored=[];seen=set();selected=[]
    def add(sid,doi,url,origin,license=None):
        original=url
        if url.startswith("http://"):url="https://"+url[7:]
        u=urllib.parse.urlsplit(url)
        if u.scheme!="https" or u.username or u.password:ignored.append(dict(source_id=sid,reason="non_public_HTTPS",locator=original));return
        if u.hostname in {"doi.org","dx.doi.org"} and urllib.parse.unquote(u.path).strip("/").lower()!=doi.lower():ignored.append(dict(source_id=sid,reason="DOI_locator_mismatch"));return
        if url in seen:return
        seen.add(url);kind="article_version" if u.path.lower().endswith(".pdf") or "/pdfdirect/" in u.path.lower() else "metadata"
        req.append(dict(record_id=sid,source_id=sid,doi=doi,url=url,kind=kind,license=license,license_status="local_only_pending_source_license",locator_original=dict(url=original,origin=origin),expected="raw original/landing bytes pending G5/identity/dual extraction"))
    for m in metadata:
        if not m["source_original_eligible_for_download"]:ignored.append(dict(source_id=m["source_id"],reason="permanent_exposure_after_exact_MED_resolution",overlap=m["historical_source_overlap"]));continue
        sid=m["source_id"];doi=m["metadata_hint"]["doi"];selected.append(sid)
        for x in (m.get("full_text_URL_metadata") or {}).get("fullTextUrl",[]):
            if x.get("availabilityCode") in ["OA","F"] and x.get("documentStyle")=="pdf":add(sid,doi,x["url"],"official MED Free/OA fulltext URL metadata")
        for x in locations[sid]["public_location_hints"]:
            if x.get("pdf_url"):add(sid,doi,x["pdf_url"],"exact DOI OpenAlex pdf locator",x.get("license"))
            url=x.get("landing_page_url")
            if url and urllib.parse.urlsplit(url).hostname not in ["doi.org","pubmed.ncbi.nlm.nih.gov"]:add(sid,doi,url,"exact DOI OpenAlex repository locator",x.get("license"))
        add(sid,doi,"https://doi.org/"+doi,"exact authoritative MED DOI")
    files=dict(p["files_sha256"])
    for q in [prior,B/"13_hint_public_location_resolution.jsonl",B/"13_hint_public_location_audit.json",Path(__file__),ROOT/"scripts/task016_p7_c_e02_r3_originals.py"]:files[str(q.relative_to(ROOT))]=sha_file(q)
    p.update(preregistered_at=now(),files_sha256=files,requests=req,selected_source_ids=selected,metadata_location_dispositions=ignored,maximum_redirect_hops=2,no_silent_redirects=True,no_authenticated_access=True,chemical_extraction_permitted=False,source_scientific_qualified=0,fresh_admitted=0,request_conservation_universe=len(req),source_selection="All9 previously metadata-only exact_MED hints without permanent aliases; original chemistry not read")
    immutable_json(P,p);require_active(P)
    print(json.dumps(dict(sources=len(selected),initial_requests=len(req),plan=pointer(P))))
def run():
    plan=require_active(P)
    done=rows(B/"raw_original_request_execution.jsonl")
    finished={r["request_index"] for r in done}
    for index,request in enumerate(plan["requests"]):
        if index in finished:continue
        item=dict(request_index=index,request=request,responses=[],redirect_recovery_plans=[],terminal_disposition=None)
        url=request["url"];kind=request["kind"]
        for hop in range(plan["maximum_redirect_hops"]+1):
            try:
                response=acquire(P,url,kind,"R5 planned public original/source-linked locator "+request["record_id"]+" hop"+str(hop),
                    license=request["license"],object_limit=64*1024**2 if kind!="metadata" else 8*1024**2)
            except ValueError as exc:
                item["terminal_disposition"]="deferred_before_HTTP"
                item["error"]=str(exc);break
            item["responses"].append(response)
            if response["status_code"] in (301,302,303,307,308) and response["headers"].get("location"):
                target=urllib.parse.urljoin(url,response["headers"]["location"])
                parts=urllib.parse.urlsplit(target)
                if parts.scheme!="https" or parts.username or parts.password or target==url:
                    item["terminal_disposition"]="redirect_deferred_unsafe_or_same_URL";break
                if hop==plan["maximum_redirect_hops"]:
                    item["terminal_disposition"]="redirect_chain_budget_deferred";break
                rp=B/"redirect_plans"/("request-%03d-hop%d.json"%(index,hop+1))
                recovery=dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R5",registered_at=now(),
                    previous_request_pointer=pointer(ROOT/response["path"]),previous_URL=url,explicit_location=target,
                    inherited_plan_pointer=pointer(P),reason="Explicit public Location follow as a separate accounted request; no hidden redirect",
                    chemical_extraction_permitted=False)
                immutable_json(rp,recovery);item["redirect_recovery_plans"].append(pointer(rp))
                url=target
                continue
            if response["status"]!="available":
                item["terminal_disposition"]="public_access_deferred";break
            body=(ROOT/response["path"]).read_bytes()
            content=response["headers"].get("content-type","").lower()
            if body.startswith(b"%PDF"):
                item["terminal_disposition"]="raw_PDF_obtained_pending_G5_A3_A4_A5";item["actual_content_type"]="PDF"
            elif body.startswith((b"\xff\xd8\xff",b"\x89PNG")):
                item["terminal_disposition"]="raw_graphic_obtained_pending_G5_A3_A4_A5";item["actual_content_type"]="JPEG" if body.startswith(b"\xff") else "PNG"
            elif "html" in content or body.lstrip().lower().startswith((b"<!doctype html",b"<html")):
                item["terminal_disposition"]="raw_HTML_landing_or_article_unqualified";item["actual_content_type"]="HTML"
            else:
                item["terminal_disposition"]="raw_other_content_unqualified";item["actual_content_type"]=content or "unknown"
            break
        if not item["terminal_disposition"]:raise ValueError("raw request lacks terminal disposition")
        item.update(chemical_extracted=False,source_identity_verified=False,evidence_eligible=False,fresh_admitted=False,finished_at=now())
        append(B/"raw_original_request_execution.jsonl",item)
        print(json.dumps(dict(request_index=index,doi=request["doi"],HTTP=len(item["responses"]),disposition=item["terminal_disposition"])),flush=True)
    terminal=rows(B/"raw_original_request_execution.jsonl")
    if len(terminal)!=len(plan["requests"]) or len({x["request_index"] for x in terminal})!=len(terminal):raise ValueError("original request accounting differs")
    summary=dict(task=TASK,batch_id="C-E02-R5",as_of=now(),planned_initial_requests=len(plan["requests"]),terminal_initial_requests=len(terminal),
      actual_HTTP=sum(len(r["responses"]) for r in terminal),PDF_objects=sum(r["terminal_disposition"]=="raw_PDF_obtained_pending_G5_A3_A4_A5" for r in terminal),
      graphic_objects=sum(r["terminal_disposition"]=="raw_graphic_obtained_pending_G5_A3_A4_A5" for r in terminal),
      HTML_objects=sum(r["terminal_disposition"]=="raw_HTML_landing_or_article_unqualified" for r in terminal),
      disposition_counts={d:sum(r["terminal_disposition"]==d for r in terminal) for d in sorted({r["terminal_disposition"] for r in terminal})},
      chemical_extracted=0,source_scientific_qualified=0,fresh_admitted=0,saturation=False,human_reviewed=False)
    immutable_json(B/"raw_original_request_summary.json",summary)
if __name__=="__main__":{"prepare":prepare,"run":run}[sys.argv[1]]()
