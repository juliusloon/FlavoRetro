"""C R37: six recent-primary literature queries, metadata-only, bounded and conserved."""
import json,urllib.parse
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as transport
from scripts.task016_p7_r18_PMC_originals import gate,put,sha,load,lines,now,can
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1"
RAW=Path("data/raw/task016-p7/C/E02/C-E02-R37-recent-C-primary-metadata-v1")
transport.C=ROOT/O
transport.RAW=ROOT/RAW
CONTRACT=ROOT/O/"precontract.json"
DATE=" AND FIRST_PDATE:[2022-01-01 TO 2026-10-11]"
QUERIES=[
 '(TITLE:"C-glycosyltransferase" OR TITLE:"C-glucosyltransferase")'+DATE,
 '(TITLE:"C-glycosylation" AND (flavone OR flavonoid))'+DATE,
 '(flavone AND C-glycosylation AND (enzyme OR biosynthesis OR glucosyltransferase))'+DATE,
 '((vitexin OR isovitexin OR orientin OR isoorientin) AND (glycosyltransferase OR synthesis))'+DATE,
 '(C6 AND glycosyltransferase)'+DATE,
 '("flavone 6" AND glucosyltransferase)'+DATE,
]
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 ga=gate("C");prior=transport.physical_attempts()
 inputs=[B/"C/E02/stages/G4_SCOPE_FREEZE.json",B/"C/E02/scope_manifest.json",B/"C/E02/fresh/C-E02-R11/metadata_candidate_groups_v2.jsonl",Path("scripts/task016_p7_c_r37_metadata.py"),Path("scripts/task016_p7_c_e02_http.py")]
 qs=[]
 for i,q in enumerate(QUERIES,1):
  url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=q,format="json",resultType="lite",pageSize=100))
  qs.append(dict(query_id=f"C-R37-Q{i}",query=q,url=url,max_pages=1,max_objects=100,reason="Recent original C-glucosylation/flavone source discovery after R11. Title/bibliographic metadata only; not scope or chemical evidence.",prior_canonical_URL_attempts=sum(can(r["url"])==can(url) for r in prior)))
 put(O/"precontract.json",dict(task=T,epoch_id="C-E02",family="C",batch_id="C-E02-R37-recent-C-primary-metadata-v1",at=now(),approval_type="agent_delegated",human_reviewed=False,agent_role="A1/A2_metadata_only",G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(p):sha(p) for p in inputs},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,metadata_fields=["id","source","pmid","pmcid","doi","title","authorString","journalTitle","pubYear","journalVolume","issue","pageInfo","isOpenAccess","inPMC","inEPMC","firstPublicationDate"],no_abstract_or_science_body_read=True,max_HTTP=6,max_bytes=6*2*1024**2,automatic_retry=False,automatic_redirect=False,output_namespace_override=dict(C=str(transport.C.relative_to(ROOT)),RAW=str(transport.RAW.relative_to(ROOT))),existing_frozen_HTTP_ledgers_not_appended=True,three_discovery_route_requirement_not_claimed_from_six_same_API_queries=True))
 put(O/"query_plan.json",dict(task=T,at=now(),planned=6,queries=qs,precontract_SHA=sha(O/"precontract.json")))
 print(json.dumps(dict(planned=6,global_HTTP_before=len(prior))))
def run():
 plan=load(O/"query_plan.json");halt=False
 for q in plan["queries"]:
  if any(r["query_id"]==q["query_id"] for r in lines(O/"query_execution.jsonl")):continue
  if halt or q["prior_canonical_URL_attempts"]>=2:
   r=dict(query_id=q["query_id"],HTTP=0,status="deferred_host_throttle_or_prior_URL_cap")
  else:
   raw=transport.acquire(CONTRACT,q["url"],"metadata",q["reason"],object_limit=2*1024**2)
   halt=raw.get("status_code")==429
   r=dict(query_id=q["query_id"],HTTP=1,status=raw["status"],HTTP_status=raw["status_code"],raw_path=raw["path"],raw_SHA=raw["sha256"],raw_bytes=raw["bytes"],returned=0,results=[],next_page_unprocessed=False)
   if raw["status"]=="available":
    data=json.loads((ROOT/raw["path"]).read_bytes());results=data.get("resultList",{}).get("result",[])
    assert isinstance(results,list) and len(results)<=100
    keys=load(O/"precontract.json")["metadata_fields"]
    r.update(hitCount=data["hitCount"],returned=len(results),results=[{k:x.get(k) for k in keys} for x in results],next_page_unprocessed=int(data["hitCount"])>len(results))
  p=O/"query_execution.jsonl";write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n")
  print(json.dumps({k:r.get(k) for k in ["query_id","HTTP_status","returned","hitCount","status"]}),flush=True)
def finish():
 qs=load(O/"query_plan.json")["queries"];rr=lines(O/"query_execution.jsonl")
 assert {x["query_id"] for x in qs}=={x["query_id"] for x in rr} and len(rr)==6
 old=lines(B/"C/E02/fresh/C-E02-R11/metadata_candidate_groups_v2.jsonl")
 prior={t.casefold() for x in old for t in x.get("alias_tokens",[])}
 index={}
 for r in rr:
  for x in r.get("results",[]):
   tokens={"doi:"+x["doi"].casefold()} if x.get("doi") else set()
   if x.get("pmcid"):tokens.add("article:"+x["pmcid"].casefold())
   if x.get("pmid"):tokens.add("pmid:"+x["pmid"])
   if x.get("source")=="MED" and x.get("id"):tokens.add("pmid:"+x["id"])
   key=("doi:"+x["doi"].casefold()) if x.get("doi") else (x.get("source","")+"-"+x.get("id",""))
   index.setdefault(key,dict(metadata=x,alias_tokens=sorted(tokens),previous_R11_literal_match=sorted(tokens&prior),observed_queries=[],scientific_qualification=None,fresh_eligible=None))
   index[key]["observed_queries"].append(r["query_id"])
 out=O/"metadata_unique_sources.jsonl"
 write(T,str(out),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in index.values()))
 put(O/"metadata_round_summary.json",dict(task=T,agent_role="A1/A2_metadata_only",at=now(),approval_type="agent_delegated",planned=6,terminal=6,HTTP=sum(x["HTTP"] for x in rr),observations=sum(x.get("returned",0) for x in rr),unique_metadata_sources=len(index),previous_R11_literal_hits=sum(bool(x["previous_R11_literal_match"]) for x in index.values()),new_to_R11_literal_only=sum(not x["previous_R11_literal_match"] for x in index.values()),unprocessed_next_pages=sum(x.get("next_page_unprocessed",False) for x in rr),source_identity_verified=0,chemical_admitted=0,fresh_admitted=0,complete_full_qualification_round=False,source_saturation=False,output_SHA=sha(out)))
 print(json.dumps(dict(unique=len(index),new_to_R11_literal_only=sum(not x["previous_R11_literal_match"] for x in index.values()))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"finish":finish}[sys.argv[1]]()
