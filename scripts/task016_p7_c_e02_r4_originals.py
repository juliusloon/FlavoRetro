"""C-E02-R4 source-linked repositories and exact DOI public SI raw intake."""
import json,sys,urllib.parse
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import acquire,immutable_json,require_active,append,rows,E
from scripts.task016_p7_c_e02_fresh import pointer
B=E/"fresh/C-E02-R4"
P=B/"query_plan.json"
def derive(name,changes,inputs):
    c=dict(require_active(P));f=dict(c["files_sha256"])
    for p in [P,Path(__file__)]+inputs:f[str(p.relative_to(ROOT))]=sha_file(p)
    c.update(preregistered_at=now(),files_sha256=f,**changes)
    cp=B/name;immutable_json(cp,c);return cp
def metadata():
    response=json.loads((B/"official_SI_metadata_response.json").read_text())
    if response["status"]!="available":raise ValueError("No available official SI metadata")
    candidates=json.loads((ROOT/response["path"]).read_text())
    match=[r for r in candidates if r.get("resource_doi","").lower()=="10.1021/acs.jafc.5c09887"]
    if len(match)!=1:raise ValueError("Exact source DOI official SI record unresolved")
    r=match[0];url=r["url_public_api"]
    if not url.startswith("https://api.figshare.com/v2/articles/"):raise ValueError("Unexpected official API route")
    cp=derive("official_SI_record_plan.json",dict(requests=[dict(url=url,kind="metadata",resource_doi=r["resource_doi"],record_id=r["id"])]),[B/"official_SI_metadata_response.json",ROOT/response["path"]])
    item=acquire(cp,url,"metadata","R4 exact original DOI official public SI record",object_limit=8*1024**2)
    immutable_json(B/"official_SI_record_response.json",item)
    print(json.dumps({k:item[k] for k in ("status","status_code","bytes","path","sha256")}))
def originals():
    prior=require_active(P)
    response=json.loads((B/"official_SI_record_response.json").read_text())
    requested=[];si=None
    if response["status"]=="available":
        si=json.loads((ROOT/response["path"]).read_text())
        if si.get("resource_doi","").lower()!="10.1021/acs.jafc.5c09887":raise ValueError("SI article primary DOI mismatch")
        for f in si.get("files",[]):
            requested.append(dict(doi=si["resource_doi"],url=f["download_url"],kind="attachment",name=f["name"],expected_bytes=f["size"],
               license=si.get("license"),public_API_record=pointer(ROOT/response["path"]),source_id="doi:"+si["resource_doi"]))
    # Every repository proposal retains an explicit disposition; existing exact bytes are inherited, not re-requested.
    existing=rows(E/"fresh/C-E02-R3/raw_original_request_execution.jsonl")
    dispositions=[]
    for r in prior["requests"]:
        u=r["url"]
        inherited=next((x for x in existing if x["request"]["url"]==u and x.get("actual_content_type")=="PDF"),None)
        if inherited:
            dispositions.append(dict(request=r,disposition="inherited_existing_exact_URL_PDF_no_repeat",raw_pointer=pointer(ROOT/inherited["responses"][-1]["path"])))
        elif "/file_details/" in urllib.parse.urlsplit(u).path:
            dispositions.append(dict(request=r,disposition="metadata_file_details_descriptor_not_downloaded",reason="Direct source file link also present; descriptor is not a PDF original"))
        elif r["doi"]=="10.1039/d0np00040j":
            dispositions.append(dict(request=r,disposition="same_repository_review_version_already_available_no_repeat",reason="Review PDF already in R3; secondary review not independent primary reaction support"))
        else:requested.append(dict(r,license=None))
    cp=derive("raw_file_request_plan.json",dict(requests=requested,repository_proposal_dispositions=dispositions,original_source_discovery_chemistry_read=False),[B/"official_SI_record_response.json",ROOT/response["path"]])
    executions=[]
    for n,r in enumerate(requested):
        record=dict(request_index=n,request=r,responses=[],redirect_recovery_plans=[])
        url=r["url"]
        for hop in range(3):
            item=acquire(cp,url,r["kind"],"R4 source-linked original raw file "+r["doi"]+" hop"+str(hop),license=r.get("license"))
            record["responses"].append(item)
            if item["status_code"] in (301,302,303,307,308) and item["headers"].get("location"):
                target=urllib.parse.urljoin(url,item["headers"]["location"]);parts=urllib.parse.urlsplit(target)
                if hop==2 or parts.scheme!="https" or parts.username or parts.password or target==url:
                    record["disposition"]="redirect_budget_or_public_HTTPS_gate_deferred";break
                rp=B/"redirect_plans"/("file-%02d-hop%d.json"%(n,hop+1))
                immutable_json(rp,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R4",at=now(),previous_response_pointer=pointer(ROOT/item["path"]),explicit_Location=target,inherited_contract=pointer(cp),raw_only=True))
                record["redirect_recovery_plans"].append(pointer(rp));url=target;continue
            if item["status"]!="available":record["disposition"]="public_access_deferred";break
            body=(ROOT/item["path"]).read_bytes()
            record["actual_content_type"]="PDF" if body.startswith(b"%PDF") else "HTML" if "html" in item["headers"].get("content-type","").lower() else "unknown"
            record["disposition"]="raw_PDF_pending_G5_A3_A4_A5" if record["actual_content_type"]=="PDF" else "raw_nonPDF_unqualified"
            break
        record.update(finished_at=now(),source_identity_verified=False,evidence_eligible=False,chemical_extracted=False)
        append(B/"raw_file_request_execution.jsonl",record);executions.append(record)
        print(json.dumps(dict(doi=r["doi"],status=record["disposition"],HTTP=len(record["responses"]),bytes=sum(x["bytes"] for x in record["responses"])),ensure_ascii=False),flush=True)
    immutable_json(B/"raw_file_intake_summary.json",dict(task=TASK,batch_id="C-E02-R4",at=now(),repository_proposals=len(prior["requests"]),
      proposals_deferred_or_inherited=len(dispositions),planned_downloads=len(requested),terminal_downloads=len(executions),
      actual_HTTP=sum(len(x["responses"]) for x in executions),raw_PDFs=sum(x.get("actual_content_type")=="PDF" for x in executions),
      chemical_extracted=0,source_qualified=0,fresh_admitted=0,saturation=False))
if __name__=="__main__":{"metadata":metadata,"originals":originals}[sys.argv[1]]()
