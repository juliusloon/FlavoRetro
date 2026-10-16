"""TASK-016-P7 bounded R61: second/final official EPMC fullTextXML attempt for two legacy C source gaps.
No scientific body reading, no claim of fresh status, never bypass access controls.
"""
import json
import hashlib
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7"
B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R61-two-legacy-official-original-recovery-v1"
R=Path("data/raw/task016-p7/C/E02/C-E02-R61-two-legacy-official-original-recovery-v1")
SOURCE=B/"C/E02/fresh/C-E02-R12/6_source_lawful_access_dispositions_v1.json"
G4=B/"C/E02/stages/G4_SCOPE_FREEZE.json"
DOIS={"PMC2709393":"10.1074/jbc.M109.009258","PMC7720146":None}
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def put(p,x):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE")
 write(T,str(p),json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
def pre():
 if (ROOT/O).exists():raise RuntimeError("BATCH_EXISTS")
 src=load(SOURCE)
 assert {x["source_id"] for x in src["sources"] if x["source_id"].startswith("PMC")}==set(DOIS)
 attempts=h.physical_attempts()
 qs=[]
 for i,pid in enumerate(DOIS,1):
  url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+pid+"/fullTextXML"
  previous=[x for x in attempts if x["url"]==url]
  if len(previous)!=1 or previous[0]["status_code"]!=500:
   raise RuntimeError("PRIOR_STATUS_NOT_EXACTLY_ONE_500:"+pid)
  qs.append(dict(query_id="R61-XML-"+str(i),pmcid=pid,url=url,kind="article_version",object_limit=16*1024*1024,prior_500=dict(path=previous[0]["path"],sha256=previous[0]["sha256"]),expected_new_attempt=2))
 g4=dict(path=str(G4),sha256=sha(G4))
 files={str(x):sha(x) for x in [SOURCE,G4,Path("scripts/task016_p7_c_e02_http.py"),Path(__file__).resolve().relative_to(ROOT)]}
 put(O/"precontract.json",dict(task=T,batch_id=O.name,epoch_id="C-E02",family="C",approval_type="agent_delegated",human_reviewed=False,agent_role="A2_raw_only",G4_pointer=g4,files_sha256=files,chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,source_science_cleared=False,already_historical_design_exposed=True,reference_qualified=False,fresh_admitted=0,max_HTTP=2,no_redirect=True,no_credentials=True,no_login_or_challenge_bypass=True,no_automatic_retry=True,lawful_route="Exact documented Europe PMC fullTextXML with prior transient HTTP 500; second and final URL attempt only",no_science_read=True))
 put(O/"query_plan.json",dict(queries=qs,planned=len(qs),source_existing=SOURCE.as_posix(),all_prior_status500=True,HTTP_budget_reserved=2))
 print(json.dumps(dict(preregistered=2,valid_prior_500=2)))
def run():
 q=load(O/"query_plan.json")["queries"]
 if (ROOT/O/"query_execution.jsonl").exists():raise RuntimeError("IMMUTABLE")
 h.C=ROOT/O;h.RAW=ROOT/R
 results=[]
 for one in q:
  r=h.acquire(O/"precontract.json",one["url"],one["kind"],reason="P7 R12 legacy PMCID original missing; final bounded legal API retry after one documented 500; no fresh chemistry claims",object_limit=one["object_limit"])
  payload=(ROOT/r["path"]).read_bytes()
  valid= r["status_code"]==200 and (payload.lstrip().startswith(b"<?xml") or payload.lstrip().startswith(b"<article") or payload.lstrip().startswith(b"<!DOCTYPE article"))
  item=dict(query_id=one["query_id"],pmcid=one["pmcid"],status_code=r["status_code"],raw_pointer={x:r[x] for x in ["path","sha256","bytes"]},valid_Article_JATS_start=valid,evidence_eligible=False,no_scientific_read=True,reason_if_unavailable="HTTP not 200 or invalid actual JATS original" if not valid else None)
  results.append(item)
  write(T,str(O/"query_execution.jsonl"),"".join(json.dumps(x,sort_keys=True)+"\n" for x in results))
 put(O/"raw_custody_summary.json",dict(task=T,processed=len(results),planned=2,HTTP=2,valid_JATS=sum(x["valid_Article_JATS_start"] for x in results),pending=2-sum(x["valid_Article_JATS_start"] for x in results),sources=results,source_historical_exposed=True,chemical_body_read=False,source_qualified=0,fresh_admitted=0,source_saturation=False))
 print(json.dumps(dict(HTTP=2,statuses=[x["status_code"] for x in results],valid_JATS=sum(x["valid_Article_JATS_start"] for x in results))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
