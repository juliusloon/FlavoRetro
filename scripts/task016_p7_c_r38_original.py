"""C R38: acquire one previously metadata-only 2026 primary original, raw custody only."""
import json,urllib.parse,xml.etree.ElementTree as ET,re,html
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as transport
from scripts.task016_p7_r18_PMC_originals import gate,put,sha,load,lines,now,can
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R38-isoorientin-original-custody-v1"
RAW=Path("data/raw/task016-p7/C/E02/C-E02-R38-isoorientin-original-custody-v1")
transport.C=ROOT/O;transport.RAW=ROOT/RAW
SID="PMC13564134";DOI="10.1016/j.abiote.2026.100085"
M=B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1/metadata_unique_sources.jsonl"
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 selected=next(x for x in lines(M) if x["metadata"]["pmcid"]==SID)
 ga=gate("C");inputs=[B/"C/E02/stages/G4_SCOPE_FREEZE.json",B/"C/E02/scope_manifest.json",M,Path("scripts/task016_p7_c_r38_original.py"),Path("scripts/task016_p7_c_e02_http.py")]
 qs=[dict(query_id="C-R38-XML",url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+SID+"/fullTextXML",kind="article_version",object_limit=6*1024**2),dict(query_id="C-R38-CROSSREF",url="https://api.crossref.org/works/"+urllib.parse.quote(DOI,safe=""),kind="metadata",object_limit=2*1024**2)]
 attempts=transport.physical_attempts()
 put(O/"precontract.json",dict(task=T,family="C",epoch_id="C-E02",batch_id="C-E02-R38-isoorientin-original-custody-v1",at=now(),approval_type="agent_delegated",human_reviewed=False,agent_role="A1/A2_raw_only",G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(p):sha(p) for p in inputs},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,selected_metadata_hint=selected,selection_reason="Only newly selected original: recent direct isoorientin biosynthesis title; old original-read PMCs and explicitly other-core titles not re-read as fresh. Literal exposure absence is not alias/graph clearance.",source_original_science_read=False,max_HTTP=2,source_budget_before_HTTP=len(attempts),no_retry=True,no_redirect=True,source_freshness_automatically_established=False,scope_modified=False))
 for q in qs:q["prior_canonical_URL_attempts"]=sum(can(x["url"])==can(q["url"]) for x in attempts)
 put(O/"query_plan.json",dict(task=T,at=now(),planned=2,queries=qs,precontract_SHA=sha(O/"precontract.json")))
 print(json.dumps(dict(planned=2,original_prior_attempts=qs[0]["prior_canonical_URL_attempts"])))
def run():
 for q in load(O/"query_plan.json")["queries"]:
  if any(x["query_id"]==q["query_id"] for x in lines(O/"query_execution.jsonl")):continue
  if q["prior_canonical_URL_attempts"]>=2:raise RuntimeError("PRIOR_CAP")
  r=transport.acquire(ROOT/O/"precontract.json",q["url"],q["kind"],"Exact selected source original or authoritative DOI metadata custody; no science-body reading.",object_limit=q["object_limit"])
  p=O/"query_execution.jsonl";out=dict(query_id=q["query_id"],source_id=SID,doi=DOI,raw_pointer={k:r[k] for k in ["path","sha256","bytes"]},HTTP_status=r["status_code"],status=r["status"],error=r.get("error"))
  write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(out,sort_keys=True)+"\n")
  print(json.dumps(dict(query_id=q["query_id"],status=r["status_code"],bytes=r["bytes"])),flush=True)
def front():
 ex=lines(O/"query_execution.jsonl");assert len(ex)==2
 raw=next(r for r in ex if r["query_id"]=="C-R38-XML");meta=next(r for r in ex if r["query_id"]=="C-R38-CROSSREF")
 assert raw["status"]==meta["status"]=="available"
 x=ET.fromstring((ROOT/raw["raw_pointer"]["path"]).read_bytes());f=x.find("./front");a=f.find("./article-meta")
 def txt(e):return " ".join("".join(e.itertext()).split()) if e is not None else None
 ids={e.get("pub-id-type"):txt(e) for e in a.findall("./article-id")}
 title=txt(a.find("./title-group/article-title"));doi=ids["doi"];year=[txt(e) for e in a.findall("./pub-date/year")]
 c=json.loads((ROOT/meta["raw_pointer"]["path"]).read_bytes())["message"];m=load(O/"precontract.json")["selected_metadata_hint"]["metadata"]
 def norm(t):return re.sub(r"[^a-z0-9]","",re.sub("<[^>]*>","",html.unescape(t)).casefold())
 assert ids.get("pmcid")==SID and doi.casefold()==c["DOI"].casefold()==DOI
 assert norm(title)==norm(c["title"][0])==norm(m["title"])
 assert m["pubYear"] in year
 result=dict(task=T,agent_role="A3_front_only",epoch_id="C-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,source_id=SID,PMCID=SID,PMID=ids.get("pmid"),DOI=doi,title=title,journal=txt(f.find("./journal-meta/journal-title-group/journal-title")),years=year,volume=txt(a.find("./volume")),issue=txt(a.find("./issue")),fpage=txt(a.find("./fpage")),lpage=txt(a.find("./lpage")),article_number=txt(a.find("./elocation-id")),official_aliases=["article:"+SID,"doi:"+DOI,"pmid:"+ids["pmid"]],original_raw=raw["raw_pointer"],Crossref_raw=meta["raw_pointer"],Crossref_title=c["title"],Crossref_container=c["container-title"],Crossref_publisher=c["publisher"],licence=txt(a.find("./permissions")),original_identity_verified=True,scientific_body_read=False,chemical_eligibility=None,fresh_eligibility=None,prior_alias_graph_clearance=False)
 put(O/"A3_original_front_identity.json",result)
 print(json.dumps(dict(original_front_verified=True,PMCID=SID,DOI=doi,years=year)))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"front":front}[sys.argv[1]]()
