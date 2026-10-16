"""R34 A4 isolated Poppler original extraction; no A5 artifacts read."""
ROLE="A4";PARSER="Poppler pdftotext layout"
PATTERN=r"UDP[\s-]*(?:glucose|glc|galactose|rhamnose)|(?:1\s*[→-]\s*[236])|(?:2|6)[′'\"″]{1,3}\s*[-]?\s*O|substrate\s+(?:specificity|preference)|enzyme\s+(?:activity|assay)|sophor|gentiob|glycosylated"
CONTEXT=200
def extract(path):
 result=subprocess.run(["pdftotext","-layout","-enc","UTF-8",str(path),"-"],check=True,capture_output=True)
 texts=result.stdout.decode("utf-8").split("\f")
 if texts[-1].strip()=="":texts.pop()
 return texts

import json,hashlib,re,subprocess
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now
from scripts.task016_p7_orchestrate import verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R34-three-ACS-SI-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
def main():
 verify_stage_chain(ROOT/G5,sha(G5))
 contract=load(R/"pre_science_exposure_contract.json")
 a3=load(R/"A3/original_SI_front_identity.json")
 assert all(x["original_SI_identity_verified"] for x in a3["records"])
 outputs=[];records=[]
 for x in contract["source_universe"]:
  assert sha(Path(x["original_path"]))==x["original_SHA"]
  receipt=dict(task=T,agent_role=ROLE,epoch_id="SS-E02",source_id=x["DOI"],doi=x["DOI"],pmid=x["PMID"],at=now(),original_SHA=x["original_SHA"],G5_SHA=sha(G5),exposure_type="post_scope_evaluation",permanent_future_epoch_exposure=True,current_epoch_fresh_qualified=False,read_scope="all SI pages by "+PARSER,peer_final_read=False)
  p=R/"scientific_exposure_reads.jsonl";write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(receipt,sort_keys=True)+"\n")
  pages=extract(ROOT/x["original_path"])
  assert len(pages)==next(a["page_count"] for a in a3["records"] if a["source_id"]==x["DOI"])
  data=[dict(page=i,text=t,text_SHA=hashlib.sha256(t.encode()).hexdigest()) for i,t in enumerate(pages,1)]
  key=x["DOI"].rsplit("/",1)[-1]
  out=R/ROLE/(key+".pages.json")
  put(out,dict(task=T,agent_role=ROLE,source_id=x["DOI"],original_SHA=x["original_SHA"],G5_SHA=sha(G5),parser=PARSER,pages=data,peer_final_read=False))
  outputs.append(out)
  contexts=[]
  for i,t in enumerate(pages,1):
   for match in re.finditer(PATTERN,t,re.I):
    start=max(0,match.start()-CONTEXT);end=min(len(t),match.end()+CONTEXT)
    contexts.append(dict(page=i,start=start,end=end,text=t[start:end],trigger=match.group(0)))
  records.append(dict(source_id=x["DOI"],original_SHA=x["original_SHA"],pages_path=str(out),pages_SHA=sha(out),evidence_contexts=contexts,acceptor_graph=None,donor_graph=None,product_graph=None,site_assignment=None,stereo_assignment=None,reference_precursors=None,chemical_reaction_qualified=False,unresolved=["Semantic assay interpretation and graphic structures require reconciliation; text contexts alone are not complete reaction graphs"],peer_final_read=False))
 result=R/ROLE/"independent_original_text_extraction.json"
 put(result,dict(task=T,agent_role=ROLE,epoch_id="SS-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,parser=PARSER,input_manifest_sha={str(G5):sha(G5),str(R/"pre_science_exposure_contract.json"):sha(R/"pre_science_exposure_contract.json"),str(R/"A3/original_SI_front_identity.json"):sha(R/"A3/original_SI_front_identity.json")},output_file_sha={str(p):sha(p) for p in outputs},records=records,counts=dict(processed=3,passed=3,rejected=0,pending=0),count_unit="independent original PDF text custody, not chemistry admission",errors=[],unprocessed=[],read_holdout=True,read_model_outcome=False,peer_final_read=False))
 print(json.dumps(dict(role=ROLE,sources=3,pages=sum(len(json.loads((ROOT/p).read_text())["pages"]) for p in outputs),chemical_admitted=0)))
if __name__=="__main__":main()
