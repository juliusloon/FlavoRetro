"""R52: only Crossref-declared VoR links for the CC BY-NC mungbean source."""
import json
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R51-mungbean-primary-custody-v1"
O=B/"C/E02/fresh/C-E02-R52-mungbean-declared-VoR-v1"
h.C=ROOT/O;h.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R52-mungbean-declared-VoR-v1"
def pre():
 assert not (ROOT/O).exists()
 rr=lines(R/"metadata_execution.jsonl");cross=next(x for x in rr if x["query_id"]=="R51-CROSSREF")
 m=cross["metadata"];assert any(x["URL"]=="http://creativecommons.org/licenses/by-nc/4.0/" and x["content-version"]=="vor" for x in m["license"])
 urls=[]
 for x in m["link"]:
  if x.get("content-version")=="vor" and x.get("content-type") in ("application/pdf","application/xml") and not any(y["url"]==x["URL"] for y in urls):
   urls.append(dict(url=x["URL"],expected_media=x["content-type"],declared_by="Crossref link VoR",kind="article_version",object_limit=16*1024**2))
 assert len(urls)==2
 files=[R/"precontract.json",R/"metadata_execution.jsonl",R/"original_access_execution.jsonl",R/"A3_bibliographic_identity.json",Path(__file__).resolve().relative_to(ROOT),Path("scripts/task016_p7_c_e02_http.py")]
 c=load(R/"precontract.json")
 put(O/"precontract.json",dict(task=T,at=now(),family="C",epoch_id="C-E02",batch_id=O.name,approval_type="agent_delegated",human_reviewed=False,G4_pointer=c["G4_pointer"],files_sha256={str(p):sha(p) for p in files},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,max_HTTP=2,no_abstract_or_scientific_body_read=True,no_retry=True,no_redirect=True,stop_on_429=True,no_login_challenge_bypass=True,source_qualification_allowed=False,known_publisher_landing_403_retained=True,Crossref_VoR_license="http://creativecommons.org/licenses/by-nc/4.0/",EPMC_isOpenAccess="N",access_metadata_conflict_retained=True,scope_modified=False))
 put(O/"query_plan.json",dict(task=T,at=now(),queries=urls,planned=2,not_guessed_URLs=True,no_TDM_token_or_credentials=True,license_preserved_no_general_redistribution_claim=True))
 print(json.dumps(dict(planned=2,declared_VoR_license="CC BY-NC 4.0",EPMC_isOpenAccess="N")))
def run():
 assert not (ROOT/O/"query_execution.jsonl").exists()
 out=[]
 for q in load(O/"query_plan.json")["queries"]:
  raw=h.acquire(ROOT/O/"precontract.json",q["url"],q["kind"],"Exact Crossref-declared VoR original under recorded CC BY-NC license; opaque intake only, no challenge/login bypass.",license="http://creativecommons.org/licenses/by-nc/4.0/",object_limit=q["object_limit"])
  data=(ROOT/raw["path"]).read_bytes()
  row=dict(url=q["url"],expected_media=q["expected_media"],HTTP_status=raw["status_code"],status=raw["status"],raw_pointer={k:raw[k] for k in ["path","sha256","bytes"]},magic_PDF=data.startswith(b"%PDF"),scientific_body_read=False)
  out.append(row)
  write(T,str(O/"query_execution.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
  if raw["status_code"]==429:break
 put(O/"raw_custody_summary.json",dict(task=T,at=now(),planned=2,executed=len(out),unprocessed=len(load(O/"query_plan.json")["queries"])-len(out),statuses=[x["HTTP_status"] for x in out],original_custody_available=sum(x["status"]=="available" for x in out),valid_PDF_count=sum(x["magic_PDF"] for x in out),Crossref_declared_CC_BY_NC_VoR=True,EPMC_isOpenAccess_N_retained=True,scientific_body_reads=0,source_qualified=0,fresh_admitted=0,source_saturation=False))
 print(json.dumps(dict(executed=len(out),HTTP=[x["HTTP_status"] for x in out],valid_PDF=sum(x["magic_PDF"] for x in out))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
