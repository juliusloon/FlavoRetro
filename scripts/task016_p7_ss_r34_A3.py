"""R34 A3 source-SI front validation after G5; no whole-body extraction."""
import json,re,html,hashlib
from pathlib import Path
import fitz
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts.task016_p7_orchestrate import verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R34-three-ACS-SI-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
def norm(t):
 t="\n".join(x for x in html.unescape(t).splitlines() if not x.strip().isdigit())
 return re.sub(r"[^a-z0-9]","",re.sub(r"<[^>]*>","",t).casefold())
def main():
 verify_stage_chain(ROOT/G5,sha(G5));c=load(R/"pre_science_exposure_contract.json")
 records=[]
 for x in c["source_universe"]:
  assert sha(Path(x["original_path"]))==x["original_SHA"]
  receipt=dict(task=T,agent_role="A3",epoch_id="SS-E02",source_id=x["DOI"],doi=x["DOI"],pmid=x["PMID"],at=now(),original_SHA=x["original_SHA"],G5_SHA=sha(G5),exposure_type="post_scope_evaluation",permanent_future_epoch_exposure=True,current_epoch_fresh_qualified=False,read_scope="SI first page front; mixed page scientific lines if any conservatively exposed")
  p=R/"scientific_exposure_reads.jsonl";write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(receipt,sort_keys=True)+"\n")
  with fitz.open(ROOT/x["original_path"]) as doc:
   text=doc[0].get_text();pages=doc.page_count
  title_ok=norm(x["title"]) in norm(text)
  rec=dict(source_id=x["DOI"],title=x["title"],original_path=x["original_path"],original_SHA=x["original_SHA"],page_count=pages,first_page_text=text,first_page_text_SHA=hashlib.sha256(text.encode()).hexdigest(),exact_normalized_title_present=title_ok,official_resource_DOI_MD5_bibliography_chain=True,original_SI_identity_verified=title_ok,main_article_fulltext_available=False,DOI_on_first_page=(x["DOI"].casefold() in text.casefold()),scientific_reaction_qualification=False)
  records.append(rec)
 put(R/"A3"/"original_SI_front_identity.json",dict(task=T,agent_role="A3",epoch_id="SS-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,G5_SHA=sha(G5),input_manifest_sha={str(R/"pre_science_exposure_contract.json"):sha(R/"pre_science_exposure_contract.json"),str(G5):sha(G5)},records=records,counts=dict(processed=3,passed=sum(x["original_SI_identity_verified"] for x in records),rejected=0,pending=sum(not x["original_SI_identity_verified"] for x in records)),errors=[],unprocessed=[],read_holdout=True,read_model_outcome=False))
 print(json.dumps([dict(doi=x["source_id"],pages=x["page_count"],title_match=x["exact_normalized_title_present"]) for x in records]))
if __name__=="__main__":main()
