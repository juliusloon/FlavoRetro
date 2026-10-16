"""Use Crossref-registered public original links for R6, never authenticated access."""
import json,sys,urllib.parse
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import E,acquire,immutable_json,require_active,physical_attempts,rows,append
from scripts.task016_p7_c_e02_fresh import pointer
B=E/"fresh/C-E02-R6";P=B/"raw_original_request_plan.json"
def prepare():
    old=B/"exact_primary_location_query_plan.json";p=dict(require_active(old));rr=rows(B/"exact_location_query_execution.jsonl");attempts=physical_attempts();req=[];ignored=[];seen=set()
    for r in rr:
        if r["route"]!="Crossref_registered_public_links" or r["status_code"]!=200:continue
        raw=ROOT/r["raw_pointer"]["path"];d=json.loads(raw.read_text())["message"];assert d["DOI"].lower()==r["doi"]
        for x in d.get("link",[]):
            original=x["URL"];url="https://"+original[7:] if original.startswith("http://") else original;u=urllib.parse.urlsplit(url)
            assert u.scheme=="https" and not u.username and not u.password and not u.fragment
            if url in seen:continue
            seen.add(url);prior=[a for a in attempts if a["url"]==url]
            reused=next((a for a in reversed(prior) if a.get("status_code")==200 and not a.get("error")),None)
            if len(prior)>=2 and reused is None or any(a.get("status_code") in [401,403] for a in prior):
                ignored.append(dict(source_id=r["source_id"],locator=url,reason="prior_access_denial_or_URL_cap_no_retry",prior_attempts=len(prior)));continue
            kind="article_version" if "pdf" in (x.get("content-type","")+u.path).lower() or "/content/article/" in u.path or "full-xml" in u.path else "metadata"
            req.append(dict(record_id=r["source_id"],source_id=r["source_id"],doi=r["doi"],url=url,kind=kind,license=None,license_status="local_only_pending_source_license",reuse_pointer=pointer(ROOT/reused["path"]) if reused else None,locator_original=dict(url=original,origin="Exact DOI Crossref registered content link",raw_pointer=pointer(raw),crossref_content_type=x.get("content-type"),crossref_intended_application=x.get("intended-application")),expected="raw unqualified original/XML/landing bytes, authenticated denial is terminal"))
    files=dict(p["files_sha256"])
    for x in [old,B/"exact_location_query_execution.jsonl",B/"exact_location_query_conservation.json",Path(__file__)]:files[str(x.relative_to(ROOT))]=sha_file(x)
    p.update(files_sha256=files,preregistered_at=now(),requests=req,ignored=ignored,maximum_redirect_hops=2,no_silent_redirects=True,no_authenticated_access=True,request_conservation_universe=len(req),selected_source_ids=[x["source_id"] for x in p["sources"]],metadata_chemical_extraction_permitted=False,chemical_extraction_permitted=False,license_or_TDM_metadata_not_access_permission_certification=True)
    immutable_json(P,p);require_active(P)
    print(json.dumps(dict(plan=pointer(P),sources=8,requests=len(req),reused=sum(x["reuse_pointer"] is not None for x in req),ignored=len(ignored))))
def run():
    p=require_active(P);done={x["request_index"] for x in rows(B/"raw_original_request_execution.jsonl")}
    for n,q in enumerate(p["requests"]):
        if n in done:continue
        item=dict(request_index=n,request=q,responses=[],terminal_disposition=None,chemical_extracted=False,source_identity_verified=False,source_qualified=0,fresh_admitted=False)
        url=q["url"];kind=q["kind"]
        for hop in range(3):
            if hop==0 and q["reuse_pointer"]:
                r=next(x for x in physical_attempts() if x["path"]==q["reuse_pointer"]["path"]);item["reused_existing_response"]=True
            else:
                try:r=acquire(P,url,kind,"R6 Crossref registered public original content link "+q["record_id"]+" hop"+str(hop),object_limit=64*1024**2 if kind!="metadata" else 8*1024**2)
                except ValueError as exc:item.update(terminal_disposition="deferred_before_HTTP",error=str(exc));break
                item["responses"].append(r)
            if r.get("status_code") in [301,302,303,307,308] and r.get("headers",{}).get("location"):
                target=urllib.parse.urljoin(url,r["headers"]["location"]);u=urllib.parse.urlsplit(target)
                if hop==2 or u.scheme!="https" or u.username or u.password or target==url:item["terminal_disposition"]="redirect_deferred";break
                rp=B/"redirect_plans"/("request%02d-hop%d.json"%(n,hop+1))
                immutable_json(rp,dict(task=TASK,epoch_id="C-E02",at=now(),previous_response_pointer=pointer(ROOT/r["path"]),explicit_location=target,plan_pointer=pointer(P),no_hidden_redirect=True));url=target;continue
            if r.get("status_code")!=200 or r.get("error"):item["terminal_disposition"]="public_access_deferred";break
            body=(ROOT/r["path"]).read_bytes();typ=r.get("headers",{}).get("content-type","").lower()
            if body.startswith(b"%PDF"):actual="PDF"
            elif "html" in typ or body.lstrip().lower().startswith((b"<!doctype html",b"<html")):actual="HTML"
            elif "xml" in typ or body.lstrip().startswith(b"<?xml"):actual="XML"
            else:actual="other"
            item.update(terminal_disposition="raw_"+actual+"_pending_G5_original_identity_and_extraction",actual_content_type=actual,raw_terminal_pointer=pointer(ROOT/r["path"]));break
        assert item["terminal_disposition"] is not None
        item["finished_at"]=now();append(B/"raw_original_request_execution.jsonl",item)
        print(json.dumps(dict(request_index=n,HTTP=len(item["responses"]),disposition=item["terminal_disposition"])),flush=True)
    rr=rows(B/"raw_original_request_execution.jsonl");assert len(rr)==len(p["requests"]) and {x["request_index"] for x in rr}==set(range(len(p["requests"])))
    immutable_json(B/"raw_original_intake_summary.json",dict(task=TASK,at=now(),planned=len(p["requests"]),terminal=len(rr),pending=0,actual_HTTP=sum(len(x["responses"]) for x in rr),raw_type_counts={t:sum(x.get("actual_content_type")==t for x in rr) for t in ["PDF","HTML","XML","other"]},source_ids_reused_from_R5=8,chemical_extracted=0,source_qualified=0,fresh_admitted=0,complete_chemical_round=False,source_saturation=False,all_HTTP_denials_retained=True))
if __name__=="__main__":{"prepare":prepare,"run":run}[sys.argv[1]]()
