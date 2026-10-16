"""R40 exact official PMC S3 object-index SI custody for C-R38, no science."""
import json,urllib.parse,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as transport
from scripts.task016_p7_r18_PMC_originals import gate,put,sha,load,lines,now
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R40-advertised-SI-custody-v1";SID="PMC13564134"
A3=B/"C/E02/fresh/C-E02-R38-isoorientin-original-custody-v1/A3_original_front_identity.json"
transport.C=ROOT/O;transport.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R40-advertised-SI-custody-v1"
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 ga=gate("C");a=load(A3)
 tree=ET.fromstring((ROOT/a["original_raw"]["path"]).read_bytes())
 href=[x.attrib["{http://www.w3.org/1999/xlink}href"] for sm in tree.iter("supplementary-material") for x in sm.iter() if "{http://www.w3.org/1999/xlink}href" in x.attrib]
 assert href and set(href)=={"mmc1.docx"}  # JATS repeats the same advertised media link; original occurrences retained.
 inputs=[A3,Path(a["original_raw"]["path"]),B/"C/E02/stages/G4_SCOPE_FREEZE.json",Path("scripts/task016_p7_c_r40_SI.py")]
 put(O/"precontract.json",dict(task=T,family="C",epoch_id="C-E02",batch_id="C-E02-R40-advertised-SI-custody-v1",at=now(),approval_type="agent_delegated",human_reviewed=False,G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(p):sha(p) for p in inputs},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,advertised_SI_hrefs=href,source_XML_SHA=a["original_raw"]["sha256"],route_basis="Same official PMC exact object-index parameter schema already verified in SS-R11: prefix exact PMCID followed by period. Object downloads only actual index Contents/Key.",max_HTTP=2,max_attachment_bytes=8*1024**2,no_scientific_read=True,no_guessed_SI_URL=True))
 put(O/"index_plan.json",dict(task=T,queries=[dict(query_id="R40-index",url="https://pmc-oa-opendata.s3.amazonaws.com/?"+urllib.parse.urlencode({"list-type":"2","prefix":SID+"."}),kind="metadata",limit=1024**2)]))
 print("registered official exact PMC object index")
def run(plan):
 for q in load(O/plan)["queries"]:
  if any(r["query_id"]==q["query_id"] for r in lines(O/"execution.jsonl")):continue
  r=transport.acquire(ROOT/O/"precontract.json",q["url"],q["kind"],"Exact documented public PMC index or index-advertised nonfigure SI object; raw custody only.",object_limit=q["limit"])
  out=dict(query_id=q["query_id"],raw_pointer={k:r[k] for k in ["path","sha256","bytes"]},status=r["status"],HTTP_status=r["status_code"])
  p=O/"execution.jsonl";write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(out,sort_keys=True)+"\n")
  print(json.dumps(dict(query_id=q["query_id"],HTTP_status=r["status_code"],bytes=r["bytes"])),flush=True)
def files():
 r=next(x for x in lines(O/"execution.jsonl") if x["query_id"]=="R40-index")
 qs=[];objects=[]
 if r["status"]=="available":
  tree=ET.fromstring((ROOT/r["raw_pointer"]["path"]).read_bytes());ns={"s":"http://s3.amazonaws.com/doc/2006-03-01/"}
  for e in tree.findall("s:Contents",ns):
   key=e.findtext("s:Key",namespaces=ns);size=int(e.findtext("s:Size",namespaces=ns))
   objects.append(dict(key=key,size=size))
  matches=[x for x in objects if x["key"].startswith(SID+".") and Path(x["key"]).name=="mmc1.docx" and 0<x["size"]<=8*1024**2]
  if len(matches)==1:
   f=matches[0];qs=[dict(query_id="R40-SI",url="https://pmc-oa-opendata.s3.amazonaws.com/"+urllib.parse.quote(f["key"],safe="/"),kind="attachment",limit=8*1024**2,advertised_key=f["key"],advertised_size=f["size"])]
 put(O/"object_index_projection.json",dict(task=T,at=now(),source_id=SID,objects=objects,science_body_read=False,only_unique_exact_advertised_SI_selected=True))
 put(O/"file_plan.json",dict(task=T,at=now(),queries=qs,planned=len(qs),projection_SHA=sha(O/"object_index_projection.json")))
 print(json.dumps(dict(index_objects=len(objects),selected_exact_SI=len(qs))))
if __name__=="__main__":
 import sys
 if sys.argv[1]=="pre":pre()
 elif sys.argv[1]=="files":files()
 elif sys.argv[1]=="run":run(sys.argv[2])
