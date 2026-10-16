"""Exact official MED resolution and public-location metadata for C-E02 R5 hints."""
import json,urllib.parse
from pathlib import Path
from scripts.task016_p7_c_e02_http import E,acquire,immutable_json,require_active,physical_attempts,rows
from scripts.task016_p7_c_e02_fresh import pointer,save_rows,hint_tokens
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
B=E/"fresh/C-E02-R5";CP=B/"primary_hint_identity_intake_plan.json"
IDS=("39563265","32637139","36259981","33056984","31986016","32144397","34061537","34489021","25479084","26331569","31418788","31399929","33486798")
def prepare():
 p=json.loads((B/"query_plan.json").read_text());rr=rows(B/"source_dispositions.jsonl")
 seen={str(x["source_hint"].get("pmid")):x for x in rr if x["disposition"]!="rejected"}
 assert set(IDS)<=set(seen)
 query="("+" OR ".join("EXT_ID:"+x for x in IDS)+") AND SRC:MED"
 url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=query,format="json",resultType="core",pageSize=100))
 files=dict(p["files_sha256"])
 for x in [B/"query_plan.json",B/"query_audit.json",B/"query_execution.jsonl",B/"source_dispositions.jsonl",Path(__file__),ROOT/"outputs/task016-p7/v1/SS/E02_design/second_acceptor_graph_identity_v1/permanent_exposure_manifest.json",ROOT/"outputs/task016-p7/v1/SS/E02_design/second_acceptor_graph_identity_v1/permanent_observed_graph_and_synonym_exposures.jsonl"]:files[str(x.relative_to(ROOT))]=sha_file(x)
 p.update(preregistered_at=now(),files_sha256=files,exact_MED_resolution_PMIDs=list(IDS),resolution_hint_provenance={x:dict(record_id=seen[x]["record_id"],raw_pointer=seen[x]["raw_pointer"]) for x in IDS},requests=[dict(query_id="C-E02-R5-ID-Q01",url=url,kind="metadata",max_objects=100,query=query)],metadata_keys_only=True,abstract_or_chemistry_extraction_allowed=False,official_location_metadata_only=True)
 immutable_json(CP,p);require_active(CP)
def resolve():
 p=require_active(CP);q=p["requests"][0]
 r=acquire(CP,q["url"],"metadata","C-E02-R5 13 exact observed PMID official core metadata; abstract chemistry not read",object_limit=8*1024**2)
 assert r["status"]=="available"
 data=json.loads((ROOT/r["path"]).read_text());rr=data["resultList"]["result"];assert len(rr)==13
 out=[]
 for x in rr:
  h={k:x.get(k) for k in ["id","source","pmid","doi","pmcid","title","pubYear","isOpenAccess"]};h["pmid"]=h["pmid"] or (x.get("id") if x.get("source")=="MED" else None)
  assert str(h["pmid"]) in IDS
  overlap=sorted(hint_tokens(h)&set(p["historical_source_tokens"]))
  out.append(dict(source_id="C-E02-R5-PMID-"+str(h["pmid"]),metadata_hint=h,full_text_URL_metadata=x.get("fullTextUrlList"),publication_status_metadata=x.get("pubTypeList"),raw_pointer=pointer(ROOT/r["path"]),historical_source_overlap=overlap,source_original_eligible_for_download=not overlap,source_identity_verified=False,chemical_extracted=False,fresh_admitted=False))
 assert {str(x["metadata_hint"]["pmid"]) for x in out}==set(IDS)
 save_rows(B/"exact_13_MED_primary_hint_metadata.jsonl",out)
 immutable_json(B/"exact_MED_resolution_audit.json",dict(task=TASK,at=now(),planned_queries=1,executed_queries=1,skipped_queries=0,identifier_PMIDs=13,resolved_PMIDs=13,raw_pointer=pointer(ROOT/r["path"]),source_qualified=0,chemical_extraction=False))
 print(json.dumps(dict(resolved=13,overlap=sum(bool(x["historical_source_overlap"]) for x in out),originals=0)))
def locations_prepare():
 p=require_active(CP);qq=[];ignored=[];attempts=physical_attempts()
 for x in rows(B/"exact_13_MED_primary_hint_metadata.jsonl"):
  if x["historical_source_overlap"]:ignored.append(dict(source_id=x["source_id"],reason="permanent_source_alias_exposure"));continue
  doi=x["metadata_hint"].get("doi")
  if not doi:ignored.append(dict(source_id=x["source_id"],reason="exact_DOI_missing"));continue
  url="https://api.openalex.org/works/https://doi.org/"+urllib.parse.quote(doi,safe="")
  prior=[r for r in attempts if r["url"]==url and r.get("status_code")==200 and not r.get("error")]
  qq.append(dict(source_id=x["source_id"],doi=doi,url=url,reuse_pointer=pointer(ROOT/prior[-1]["path"]) if prior else None,metadata_hint_pointer=pointer(B/"exact_13_MED_primary_hint_metadata.jsonl")))
 for x in [B/"exact_13_MED_primary_hint_metadata.jsonl",B/"exact_MED_resolution_audit.json"]:p["files_sha256"][str(x.relative_to(ROOT))]=sha_file(x)
 p.update(preregistered_at=now(),requests=qq,ignored=ignored,read_abstract=False,chemistry_extracted=False)
 immutable_json(B/"public_location_intake_plan.json",p)
 print(json.dumps(dict(request_or_reuse=len(qq),reuse=sum(x["reuse_pointer"] is not None for x in qq),ignored=len(ignored))))
def locations():
 cp=B/"public_location_intake_plan.json";p=require_active(cp);out=[]
 for q in p["requests"]:
  if q["reuse_pointer"]:raw=q["reuse_pointer"];response=None
  else:
   response=acquire(cp,q["url"],"metadata","R5 exact DOI OpenAlex public original locator only",object_limit=8*1024**2);raw=pointer(ROOT/response["path"])
  loc=[];failure=None
  try:
   d=json.loads((ROOT/raw["path"]).read_text())
   if response is not None and response["status"]!="available":raise ValueError("HTTP status "+str(response["status_code"]))
   assert (d.get("doi") or "").lower()=="https://doi.org/"+q["doi"].lower(),"OpenAlex DOI mismatch"
   for x in d.get("locations",[]):
    loc.append({k:x.get(k) for k in ["landing_page_url","pdf_url","is_oa","license","version","is_accepted","is_published","source"]})
  except Exception as e:failure=type(e).__name__+": "+str(e)
  row=dict(source_id=q["source_id"],doi=q["doi"],raw_pointer=raw,reused=q["reuse_pointer"] is not None,public_location_hints=loc,error=failure,source_qualified=0,chemical_extracted=False)
  out.append(row);save_rows(B/(q["source_id"]+"_public_locations.jsonl"),[row])
  print(json.dumps(dict(source_id=q["source_id"],reused=row["reused"],locations=len(loc),error=failure)),flush=True)
 save_rows(B/"13_hint_public_location_resolution.jsonl",out)
 immutable_json(B/"13_hint_public_location_audit.json",dict(task=TASK,at=now(),plan=len(p["requests"]),terminal=len(out),reused=sum(x["reused"] for x in out),source_qualified=0,raw_originals_obtained=0,chemistry_extracted=False))
if __name__=="__main__":
 import sys
 {"prepare":prepare,"resolve":resolve,"locations-prepare":locations_prepare,"locations":locations}[sys.argv[1]]()
