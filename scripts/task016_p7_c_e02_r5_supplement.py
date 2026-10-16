"""R5 public repository file and official SI; all raw-only before G5."""
import json,hashlib,urllib.parse,sys
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import E,acquire,immutable_json,require_active,append,rows
from scripts.task016_p7_c_e02_public_post import acquire_post
from scripts.task016_p7_c_e02_fresh import pointer
B=E/"fresh/C-E02-R5";P=B/"supplemental_public_source_plan.json"
def prepare():
 p=require_active(B/"raw_original_request_plan.json")
 raw=rows(B/"raw_original_request_execution.jsonl");html=[x for x in raw if x.get("actual_content_type")=="HTML"]
 assert html and html[0]["request"]["source_id"]=="C-E02-R5-PMID-31418788"
 response=html[0]["responses"][-1];body=(ROOT/response["path"]).read_text()
 href="/record/2002392/files/PCP60-2733.pdf";assert href in body
 url="https://soar-ir.repo.nii.ac.jp"+href
 get=[dict(record_id="C-E02-R5-PMID-31418788",source_id="C-E02-R5-PMID-31418788",doi="10.1093/pcp/pcz164",url=url,kind="article_version",license=None,locator_original=pointer(ROOT/response["path"]),expected="public author manuscript PDF"),dict(record_id="C-E02-R5-PMID-36259981",source_id="C-E02-R5-PMID-36259981",doi="10.1039/d2cc04279g",url="https://www.rsc.org/suppdata/d2/cc/d2cc04279g/d2cc04279g1.pdf",kind="attachment",license=None,locator_original="Explicit conventional RSC public SI route probe; path not yet identity verified; exact DOI from official MED",expected="unverified public SI locator probe; no source fact assumed")]
 payload={"resource_doi":"10.1021/jacs.9b12211"};posturl="https://api.figshare.com/v2/articles/search";digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 files=dict(p["files_sha256"])
 for q in [B/"raw_original_request_summary.json",B/"raw_original_request_execution.jsonl",Path(__file__),ROOT/"scripts/task016_p7_c_e02_public_post.py",ROOT/response["path"]]:files[str(q.relative_to(ROOT))]=sha_file(q)
 p.update(preregistered_at=now(),files_sha256=files,requests=get,permitted_POST_requests=[dict(url=posturl,payload_sha256=digest)],official_SI_metadata_POST=dict(url=posturl,payload=payload,source_id="C-E02-R5-PMID-31986016"),no_new_scope_or_chemistry=True)
 immutable_json(P,p);require_active(P)
def metadata():
 p=require_active(P);q=p["official_SI_metadata_POST"]
 r=acquire_post(P,q["url"],"metadata","R5 exact observed primary DOI official ACS Figshare resource lookup",payload=q["payload"],object_limit=8*1024**2)
 immutable_json(B/"JACS_official_SI_metadata_response.json",r)
 d=json.loads((ROOT/r["path"]).read_text()) if r["status"]=="available" else []
 matched=[x for x in d if isinstance(x,dict) and x.get("resource_doi","").lower()==q["payload"]["resource_doi"]]
 immutable_json(B/"JACS_official_SI_metadata_match.json",dict(task=TASK,at=now(),matches=matched,match_count=len(matched),parent_DOI=q["payload"]["resource_doi"],source_identity_qualified=False))
 print(json.dumps(dict(status=r["status_code"],matches=len(matched))))
def record():
 p=require_active(P);d=json.loads((B/"JACS_official_SI_metadata_match.json").read_text());assert d["match_count"]==1
 url=d["matches"][0]["url"];files=dict(p["files_sha256"])
 for q in [B/"JACS_official_SI_metadata_response.json",B/"JACS_official_SI_metadata_match.json"]:files[str(q.relative_to(ROOT))]=sha_file(q)
 p.update(preregistered_at=now(),files_sha256=files,record_url=url)
 cp=B/"JACS_official_SI_record_plan.json";immutable_json(cp,p)
 r=acquire(cp,url,"metadata","R5 exact official Figshare JACS SI record",object_limit=8*1024**2)
 immutable_json(B/"JACS_official_SI_record_response.json",r)
 print(json.dumps(dict(status=r["status_code"],bytes=r["bytes"])))
def files_prepare():
 p=require_active(P);req=list(p["requests"]);files=dict(p["files_sha256"])
 r=json.loads((B/"JACS_official_SI_record_response.json").read_text())
 if r["status"]=="available":
  d=json.loads((ROOT/r["path"]).read_text());assert d["resource_doi"].lower()=="10.1021/jacs.9b12211"
  for f in d["files"]:req.append(dict(record_id="C-E02-R5-PMID-31986016",source_id="C-E02-R5-PMID-31986016",doi=d["resource_doi"],url=f["download_url"],kind="attachment",license=d.get("license"),locator_original=pointer(ROOT/r["path"]),expected_bytes=f["size"],expected_MD5=f["computed_md5"],expected="official ACS SI raw file"))
 for q in [B/"JACS_official_SI_record_response.json",ROOT/r["path"]]:files[str(q.relative_to(ROOT))]=sha_file(q)
 p.update(preregistered_at=now(),files_sha256=files,requests=req,maximum_redirect_hops=2)
 cp=B/"supplemental_raw_file_request_plan.json";immutable_json(cp,p)
 print(json.dumps(dict(initial_file_requests=len(req))))
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

if __name__=="__main__":
 if sys.argv[1]=="files":
  P=B/"supplemental_raw_file_request_plan.json";run()
 else:{"prepare":prepare,"metadata":metadata,"record":record,"files-prepare":files_prepare}[sys.argv[1]]()
