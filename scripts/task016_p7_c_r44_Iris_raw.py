"""R44: prospective raw-only original custody for the selected Iris UGT707B2 study."""
import json,urllib.parse,xml.etree.ElementTree as ET,re,html
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as transport
from scripts.task016_p7_r18_PMC_originals import gate,put,sha,load,lines,now,can
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R44-Iris-original-custody-v1"
transport.C=ROOT/O;transport.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R44-Iris-original-custody-v1"
SID="PMC13422134";DOI="10.1002/cbic.70486"
M=B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1/metadata_unique_sources.jsonl"
def pre():
 assert not (ROOT/O).exists()
 selected=next(x for x in lines(M) if x["metadata"]["pmcid"]==SID)
 ga=gate("C");prior=lines(B/"governance/prior_exposure_inventory_v3/prior_exposure_rows.jsonl")+lines(B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1/scientific_exposure_reads.jsonl")
 aliases={"article:"+SID,"doi:"+DOI,"pmid:"+selected["metadata"]["pmid"]}
 assert not any(aliases.intersection(x["closure_tokens"]) for x in prior)
 inputs=[B/"C/E02/stages/G4_SCOPE_FREEZE.json",B/"SS/E02/stages/G4_SCOPE_FREEZE.json",B/"report_snapshots/progress-v28.json",M,Path(__file__).resolve().relative_to(ROOT),Path("scripts/task016_p7_c_e02_http.py")]
 queries=[dict(query_id="R44-XML",url="https://www.ebi.ac.uk/europepmc/webservices/rest/"+SID+"/fullTextXML",kind="article_version",limit=8*1024**2),dict(query_id="R44-Crossref",url="https://api.crossref.org/works/"+urllib.parse.quote(DOI,safe=""),kind="metadata",limit=2*1024**2),dict(query_id="R44-PMC-index",url="https://pmc-oa-opendata.s3.amazonaws.com/?"+urllib.parse.urlencode({"list-type":"2","prefix":SID+"."}),kind="metadata",limit=1024**2)]
 attempts=transport.physical_attempts()
 for q in queries:q["prior_canonical_URL_attempts"]=sum(can(x["url"])==can(q["url"]) for x in attempts)
 assert all(q["prior_canonical_URL_attempts"]<2 for q in queries)
 put(O/"precontract.json",dict(task=T,family="C",epoch_id="C-E02",batch_id=O.name,at=now(),approval_type="agent_delegated",human_reviewed=False,G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(p):sha(p) for p in inputs},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,selected_metadata_hint=selected,source_original_science_read=False,selection_reason="Primary UGT707B2 enzyme-characterization title; potential substrate diversity is a hypothesis, not C/SS eligibility. Exact current source aliases absent known prior inventory plus R39 reads. EPMC marks non-OA; attempt only lawful public services and retain pending access.",cross_axis_scope_read_permission=False,prospective_C_and_SS_G5_required_before_any_new_science=True,no_retry=True,no_redirect=True,max_HTTP_initial=3,max_HTTP_advertised_originals=3,scope_modified=False))
 put(O/"query_plan.json",dict(task=T,at=now(),precontract_SHA=sha(O/"precontract.json"),queries=queries))
 print(json.dumps(dict(planned=3,metadata_isOpenAccess=selected["metadata"]["isOpenAccess"],new_scientific_read=0)))
def run(plan):
 for q in load(O/plan)["queries"]:
  if any(x["query_id"]==q["query_id"] for x in lines(O/"query_execution.jsonl")):continue
  r=transport.acquire(ROOT/O/"precontract.json",q["url"],q["kind"],"Exact selected DOI/PMCID official public service; raw-only custody before any scientific qualification.",object_limit=q["limit"])
  row=dict(query_id=q["query_id"],source_id=SID,doi=DOI,raw_pointer={k:r[k] for k in ["path","sha256","bytes"]},status=r["status"],HTTP_status=r["status_code"],error=r.get("error"),advertised=q.get("advertised"))
  p=O/"query_execution.jsonl";write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(row,sort_keys=True)+"\n")
  print(json.dumps({k:row[k] for k in ["query_id","status","HTTP_status"]}),flush=True)
def originals():
 rows=lines(O/"query_execution.jsonl");index=next(x for x in rows if x["query_id"]=="R44-PMC-index");objects=[];queries=[]
 if index["status"]=="available":
  tree=ET.fromstring((ROOT/index["raw_pointer"]["path"]).read_bytes());ns={"s":"http://s3.amazonaws.com/doc/2006-03-01/"}
  for e in tree.findall("s:Contents",ns):objects.append(dict(key=e.findtext("s:Key",namespaces=ns),size=int(e.findtext("s:Size",namespaces=ns))))
  xml=next(x for x in rows if x["query_id"]=="R44-XML")
  # Original public PDF is independently usable as an opaque original if XML service is non-OA.
  selected=[x for x in objects if x["key"].endswith("/"+SID+".1.pdf")]
  if not selected:selected=[x for x in objects if Path(x["key"]).suffix==".pdf" and Path(x["key"]).name.startswith(SID+".")]
  if xml["status"]!="available":
   selected += [x for x in objects if Path(x["key"]).name==SID+".1.xml"]
  href=[]
  if xml["status"]=="available":
   tree=ET.fromstring((ROOT/xml["raw_pointer"]["path"]).read_bytes())
   href=[e.attrib["{http://www.w3.org/1999/xlink}href"] for sm in tree.iter("supplementary-material") for e in sm.iter() if "{http://www.w3.org/1999/xlink}href" in e.attrib]
   for h in set(href):
    name=Path(urllib.parse.urlsplit(h).path).name
    selected += [x for x in objects if Path(x["key"]).name==name]
  selected=list({x["key"]:x for x in selected}.values())
  assert len(selected)<=3
  for n,x in enumerate(selected,1):
   if not (0<x["size"]<=16*1024**2):continue
   queries.append(dict(query_id="R44-advertised-"+str(n),url="https://pmc-oa-opendata.s3.amazonaws.com/"+urllib.parse.quote(x["key"],safe="/"),kind="article_version" if Path(x["key"]).name.startswith(SID+".") else "attachment",limit=16*1024**2,advertised=x))
 else:href=[]
 put(O/"advertised_objects_projection.json",dict(task=T,at=now(),source_id=SID,objects=objects,original_SI_hrefs=href,metadata_only=True,scientific_body_read=False))
 put(O/"original_file_plan.json",dict(task=T,at=now(),queries=queries,planned=len(queries),index_raw_pointer=index["raw_pointer"],unadvertised_urls_guessed=False))
 print(json.dumps(dict(index_objects=len(objects),advertised_objects_selected=len(queries))))
if __name__=="__main__":
 import sys
 if sys.argv[1]=="pre":pre()
 elif sys.argv[1]=="run":run(sys.argv[2])
 elif sys.argv[1]=="originals":originals()
