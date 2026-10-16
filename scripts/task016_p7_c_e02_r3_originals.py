"""C-E02-R3 planned public originals. Raw bytes only until a new G5 freeze."""
import json,re,sys,urllib.parse
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import acquire,immutable_json,require_active,append
from scripts.task016_p7_c_e02_fresh import E,rows,pointer
B=E/"fresh/C-E02-R3"
P=B/"raw_original_request_plan.json"
def prepare():
    prior=B/"query_plan_R1_exposure_supplement.json"
    old=require_active(prior)
    discovery=rows(B/"metadata_discovery.jsonl")
    sources=sorted(discovery,key=lambda r:(
        0 if r["doi"]=="10.1021/acs.jafc.5c09887" else
        1 if re.search("direct flavone|natural and novel",r["source_hint"]["title"],re.I) else 2,r["record_id"]))[:20]
    requests=[];dispositions=[];seen=set()
    for r in sources:
        locators=r["locators"]
        for loc in locators:
            url=loc["url"]
            parts=urllib.parse.urlsplit(url)
            if parts.hostname in {"doi.org","dx.doi.org"} and urllib.parse.unquote(parts.path).strip("/").lower()!=r["doi"]:
                dispositions.append(dict(record_id=r["record_id"],url=url,disposition="rejected_wrong_location_DOI",
                    reason="Work-level DOI match does not verify each linked location; different DOI is not this original"))
                continue
            if url.startswith("http://"):
                url="https://"+url[7:]
            if not url.startswith("https://"):
                dispositions.append(dict(record_id=r["record_id"],url=url,disposition="deferred_non_HTTPS"))
                continue
            path=urllib.parse.urlsplit(url).path.lower()
            kind="attachment" if re.search(r"\.(jpg|jpeg|png|svg|gif)$",path) else "article_version" if path.endswith(".pdf") or "/pdfdirect/" in path else "metadata"
            if url in seen:continue
            seen.add(url)
            requests.append(dict(record_id=r["record_id"],source_id=r["source_id"],doi=r["doi"],url=url,kind=kind,
                locator_original=loc,expected="PDF bytes" if kind=="article_version" else "source-linked graphical attachment" if kind=="attachment" else "public metadata/landing page",
                license=loc.get("license"),license_status="provider locator assertion only; source license pending"))
        if not locators or not any(x["record_id"]==r["record_id"] and x["kind"]=="article_version" for x in requests):
            url="https://doi.org/"+r["doi"]
            if url not in seen:
                seen.add(url)
                requests.append(dict(record_id=r["record_id"],source_id=r["source_id"],doi=r["doi"],url=url,kind="metadata",
                    locator_original=None,expected="public DOI publisher metadata/landing page",license=None,
                    license_status="public access/local-only pending; no login or access bypass"))
    plan=dict(old)
    files=dict(plan["files_sha256"])
    for p in (prior,B/"metadata_discovery.jsonl",B/"metadata_discovery_summary.json",Path(__file__)):
        files[str(p.relative_to(ROOT))]=sha_file(p)
    plan.update(preregistered_at=now(),files_sha256=files,requests=requests,
      selected_source_ids=[r["source_id"] for r in sources],unselected_source_ids=[r["source_id"] for r in discovery if r not in sources],
      metadata_location_dispositions=dispositions,maximum_redirect_hops=2,read_R3_original_chemistry=False,
      no_silent_redirects=True,no_authenticated_access=True,chemical_extraction_permitted=False,
      original_type_must_be_checked_from_actual_bytes=True,
      DOI_priority_rule="Existing exact 2026 novel CGT and direct flavone/novel flavone title hints first; remaining by stable record ID; max20 original sources",
      request_conservation_universe=len(requests),source_scientific_qualified=0,fresh_admitted=0)
    immutable_json(P,plan)
    require_active(P)
    print(json.dumps(dict(original_source_hints=len(sources),initial_requests=len(requests),wrong_location_DOIs=len(dispositions),plan=pointer(P))))
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
                response=acquire(P,url,kind,"R3 planned public original/source-linked locator "+request["record_id"]+" hop"+str(hop),
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
                recovery=dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R3",registered_at=now(),
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
    summary=dict(task=TASK,batch_id="C-E02-R3",as_of=now(),planned_initial_requests=len(plan["requests"]),terminal_initial_requests=len(terminal),
      actual_HTTP=sum(len(r["responses"]) for r in terminal),PDF_objects=sum(r["terminal_disposition"]=="raw_PDF_obtained_pending_G5_A3_A4_A5" for r in terminal),
      graphic_objects=sum(r["terminal_disposition"]=="raw_graphic_obtained_pending_G5_A3_A4_A5" for r in terminal),
      HTML_objects=sum(r["terminal_disposition"]=="raw_HTML_landing_or_article_unqualified" for r in terminal),
      disposition_counts={d:sum(r["terminal_disposition"]==d for r in terminal) for d in sorted({r["terminal_disposition"] for r in terminal})},
      chemical_extracted=0,source_scientific_qualified=0,fresh_admitted=0,saturation=False,human_reviewed=False)
    immutable_json(B/"raw_original_request_summary.json",summary)
if __name__=="__main__":{"prepare":prepare,"run":run}[sys.argv[1]]()
