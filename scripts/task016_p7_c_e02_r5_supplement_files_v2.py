"""R5 supplemental GET-only files after public metadata endpoint cap rejection."""
import json,sys,urllib.parse
from scripts.task016_p7_orchestrate import ROOT,TASK,now
from scripts.task016_p7_c_e02_http import E,acquire,immutable_json,require_active,append,rows
from scripts.task016_p7_c_e02_fresh import pointer
B=E/"fresh/C-E02-R5";P=B/"supplemental_raw_file_request_plan.v2.json"
def run():
    plan=require_active(P)
    done=rows(B/"supplemental_raw_file_execution.jsonl")
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
                rp=B/"redirect_plans"/("supplemental-%03d-hop%d.json"%(index,hop+1))
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
        append(B/"supplemental_raw_file_execution.jsonl",item)
        print(json.dumps(dict(request_index=index,doi=request["doi"],HTTP=len(item["responses"]),disposition=item["terminal_disposition"])),flush=True)
    terminal=rows(B/"supplemental_raw_file_execution.jsonl")
    if len(terminal)!=len(plan["requests"]) or len({x["request_index"] for x in terminal})!=len(terminal):raise ValueError("original request accounting differs")
    summary=dict(task=TASK,batch_id="C-E02-R5",as_of=now(),planned_initial_requests=len(plan["requests"]),terminal_initial_requests=len(terminal),
      actual_HTTP=sum(len(r["responses"]) for r in terminal),PDF_objects=sum(r["terminal_disposition"]=="raw_PDF_obtained_pending_G5_A3_A4_A5" for r in terminal),
      graphic_objects=sum(r["terminal_disposition"]=="raw_graphic_obtained_pending_G5_A3_A4_A5" for r in terminal),
      HTML_objects=sum(r["terminal_disposition"]=="raw_HTML_landing_or_article_unqualified" for r in terminal),
      disposition_counts={d:sum(r["terminal_disposition"]==d for r in terminal) for d in sorted({r["terminal_disposition"] for r in terminal})},
      chemical_extracted=0,source_scientific_qualified=0,fresh_admitted=0,saturation=False,human_reviewed=False)
    immutable_json(B/"supplemental_raw_file_intake_summary.json",summary)


if __name__=="__main__":run()
