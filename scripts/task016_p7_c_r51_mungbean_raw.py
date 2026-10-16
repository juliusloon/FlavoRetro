"""R51: one new C primary-study identity and advertised lawful access routes."""
import json,urllib.parse
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now,can
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7";B=Path("outputs/task016-p7/v1");DOI="10.1111/tpj.70932"
O=B/"C/E02/fresh/C-E02-R51-mungbean-primary-custody-v1"
R=B/"C/E02/fresh/C-E02-R50-R49-cursor-boundary-v1"
h.C=ROOT/O;h.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R51-mungbean-primary-custody-v1"
def pre():
 assert not (ROOT/O).exists()
 hints=lines(R/"title_hint_prior_triage.jsonl")
 selected=next(x for x in hints if x["metadata"]["doi"]==DOI)
 assert selected["known_prior_scientific_token_matches"]==[]
 put(O/"selected_bibliography.json",selected)
 old=load(R/"precontract.v2.json")
 files=[R/"title_hint_prior_triage.jsonl",R/"metadata_boundary_and_triage_summary.json",Path(__file__).resolve().relative_to(ROOT),Path("scripts/task016_p7_c_e02_http.py"),O/"selected_bibliography.json"]
 put(O/"precontract.json",dict(task=T,at=now(),family="C",epoch_id="C-E02",batch_id=O.name,approval_type="agent_delegated",human_reviewed=False,G4_pointer=old["G4_pointer"],files_sha256={str(p):sha(p) for p in files},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,max_HTTP=4,max_originals=2,selected_DOI=DOI,no_abstract_or_scientific_body_read=True,metadata_fields_only=["DOI","title","container-title","published","volume","issue","article-number","page","resource","URL","link","license","open_access","locations","best_oa_location"],no_retry=True,no_redirect=True,stop_on_429=True,source_qualified=False,fresh_eligible=False))
 queries=[dict(query_id="R51-CROSSREF",url="https://api.crossref.org/works/"+urllib.parse.quote(DOI,safe=""),kind="metadata",object_limit=2*1024**2),dict(query_id="R51-OPENALEX",url="https://api.openalex.org/works/https://doi.org/"+DOI+"?"+urllib.parse.urlencode(dict(select="id,doi,title,publication_year,type,open_access,locations,best_oa_location,primary_location,ids")),kind="metadata",object_limit=4*1024**2)]
 put(O/"query_plan.json",dict(task=T,at=now(),queries=queries,original_followup="Only URLs literally declared by Crossref resource.primary.URL or OpenAlex public OA locations; preregister exact followups before HTTP; <=2 originals. No guessed SI, no TDM rights assertion.",max_HTTP=4))
 print(json.dumps(dict(selected_DOI=DOI,metadata=2,original_max=2,science_read=False)))
def metadata():
 assert not (ROOT/O/"metadata_execution.jsonl").exists()
 out=[]
 for q in load(O/"query_plan.json")["queries"]:
  raw=h.acquire(ROOT/O/"precontract.json",q["url"],q["kind"],"Exact DOI bibliography and public-access locators only; scientific abstract/body not projected.",object_limit=q["object_limit"])
  row=dict(query_id=q["query_id"],raw_pointer={k:raw[k] for k in ["path","sha256","bytes"]},HTTP_status=raw["status_code"],status=raw["status"])
  if raw["status"]=="available":
   obj=load(Path(raw["path"]))
   if q["query_id"]=="R51-CROSSREF":
    m=obj["message"];row["metadata"]={k:m.get(k) for k in ["DOI","title","container-title","publisher","published","volume","issue","article-number","page","resource","URL","link","license"]}
   else:row["metadata"]={k:obj.get(k) for k in ["id","doi","title","publication_year","type","open_access","locations","best_oa_location","primary_location","ids"]}
  out.append(row)
  write(T,str(O/"metadata_execution.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
  if raw["status_code"]==429:break
 print(json.dumps(dict(requests=len(out),statuses=[x["HTTP_status"] for x in out])))
def access_pre():
 rr=lines(O/"metadata_execution.jsonl");assert len(rr)==2
 cross=next(x for x in rr if x["query_id"]=="R51-CROSSREF")
 assert cross["status"]=="available" and cross["metadata"]["DOI"].lower()==DOI
 m=cross["metadata"];hint=load(O/"selected_bibliography.json")["metadata"]
 import re,html
 norm=lambda s:re.sub(r"[^a-z0-9]+","",html.unescape(s.lower()))
 title=m["title"][0];assert norm(title)==norm(hint["title"])
 checks=dict(DOI=m["DOI"].lower()==hint["doi"].lower(),title=norm(title)==norm(hint["title"]),journal=m["container-title"][0].lower().replace("the ","") in ("plant journal","plant j"),year=m["published"]["date-parts"][0][0]==int(hint["pubYear"]),volume=str(m["volume"])==hint["journalVolume"],issue=str(m["issue"])==hint["issue"],article_number=str(m.get("article-number") or m.get("page"))==hint["pageInfo"])
 put(O/"A3_bibliographic_identity.json",dict(task=T,at=now(),DOI=DOI,PMID=hint["pmid"],PMCID=None,field_checks=checks,all_fields_match=all(checks.values()),Crossref_metadata=m,EPMC_metadata=hint,original_front_identity_verified=False,scientific_content_read=False,source_qualified=False,full_graph_alias_historical_clearance=False,official_aliases=["doi:"+DOI,"pmid:"+hint["pmid"]]))
 candidates=[]
 u=m.get("resource",{}).get("primary",{}).get("URL")
 if u and u.startswith("https://"):candidates.append(dict(url=u,declared_by="Crossref resource.primary.URL"))
 alex=next(x for x in rr if x["query_id"]=="R51-OPENALEX")
 if alex["status"]=="available":
  a=alex["metadata"]
  for loc in a.get("locations") or []:
   if loc.get("is_oa"):
    for field in ["pdf_url","landing_page_url"]:
     u=loc.get(field)
     if u and u.startswith("https://") and not any(can(x["url"])==can(u) for x in candidates):
      candidates.append(dict(url=u,declared_by="OpenAlex public is_oa location "+field))
 existing=h.physical_attempts()
 candidates=[x for x in candidates if sum(can(y["url"])==can(x["url"]) for y in existing)<2][:2]
 put(O/"original_access_plan.json",dict(task=T,at=now(),originals=candidates,metadata_sources=[{k:x[k] for k in ["query_id","raw_pointer"]} for x in rr],max_HTTP=len(candidates),source_qualification_allowed=False,no_scientific_body_read_before_G5=True,no_access_control_bypass=True))
 print(json.dumps(dict(identity=checks,originals=candidates)))
def original():
 p=load(O/"original_access_plan.json")
 assert not (ROOT/O/"original_access_execution.jsonl").exists()
 rows=[]
 for x in p["originals"]:
  raw=h.acquire(ROOT/O/"precontract.json",x["url"],"article_version","Only public URL advertised by bibliographic source; original body held opaque before G5, no login/challenge bypass.",object_limit=16*1024**2)
  rows.append(dict(declared_by=x["declared_by"],url=x["url"],raw_pointer={k:raw[k] for k in ["path","sha256","bytes"]},HTTP_status=raw["status_code"],status=raw["status"],scientific_body_read=False))
  write(T,str(O/"original_access_execution.jsonl"),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows))
  if raw["status_code"]==429:break
 put(O/"raw_custody_summary.json",dict(task=T,at=now(),source_count=1,metadata_requests=len(lines(O/"metadata_execution.jsonl")),original_requests=len(rows),original_statuses=[x["HTTP_status"] for x in rows],original_custody_available=sum(x["status"]=="available" for x in rows),no_scientific_body_read=True,source_qualified=False,fresh_admitted=0,source_saturation=False,original_front_identity_verified=False))
 print(json.dumps(dict(original_requests=len(rows),HTTP=[x["HTTP_status"] for x in rows],science_read=False)))
if __name__=="__main__":
 import sys
 {"pre":pre,"metadata":metadata,"access_pre":access_pre,"original":original}[sys.argv[1]]()
