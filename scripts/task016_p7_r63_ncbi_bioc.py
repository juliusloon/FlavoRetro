"""P7 R63: source-capped acquisition from officially documented NCBI BioC-PMC OA API.

BioC is derived full-text projection, not publisher/source JATS or original supporting images.
"""
import json,hashlib
from pathlib import Path
from scripts.operate import ROOT,write
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R63-official-BioC-retrieval-v1"
RAW=Path("data/raw/task016-p7/C/E02/C-E02-R63-official-BioC-retrieval-v1")
G4=B/"C/E02/stages/G4_SCOPE_FREEZE.json"
R12=B/"C/E02/fresh/C-E02-R12/6_source_lawful_access_dispositions_v1.json"
R61=B/"C/E02/fresh/C-E02-R61-two-legacy-official-original-recovery-v1/raw_custody_summary.json"
PIDS=["PMC2709393","PMC7720146"]
API_DOC="https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def put(p,x):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE")
 write(T,str(p),json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 assert read(R61)["valid_JATS"]==0
 attempts=h.physical_attempts();qs=[]
 for pid in PIDS:
  u="https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/"+pid+"/unicode"
  assert not any(x["url"]==u for x in attempts)
  qs.append(dict(query_id="R63-"+pid,source_id=pid,url=u,kind="article_version",object_limit=16*1024*1024,expected_format="BioC XML derived from PMC OA subset",not_original_JATS=True))
 g4=dict(path=str(G4),sha256=sha(G4))
 files={str(p):sha(p) for p in [G4,R12,R61,Path("scripts/task016_p7_c_e02_http.py"),Path(__file__).resolve().relative_to(ROOT)]}
 put(O/"precontract.json",dict(task=T,batch_id=O.name,epoch_id="C-E02",family="C",agent_role="A2_raw_only",approval_type="agent_delegated",human_reviewed=False,G4_pointer=g4,files_sha256=files,chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,source_science_cleared=False,already_historical_design_exposed=True,reference_qualified=False,fresh_admitted=0,max_HTTP=2,no_redirect=True,no_credentials=True,no_login_or_challenge_bypass=True,no_auto_retry=True,no_science_read=True,API_docs=[API_DOC],note="Public official derived BioC service for sources with previously unavailable original JATS; never invent original-source status or future fresh eligibility."))
 put(O/"query_plan.json",dict(queries=qs,planned=2,expected_source_collection="PMC OA or author manuscript only",no_guessed_individual_files=True))
 print(json.dumps(dict(planned=2,original_JATS_expected=False)))
def run():
 h.C=ROOT/O;h.RAW=ROOT/RAW
 queries=read(O/"query_plan.json")["queries"];out=[]
 for q in queries:
  r=h.acquire(O/"precontract.json",q["url"],q["kind"],reason="Official NCBI BioC-PMC OA documented interface for historical original gap; preserve derived format and raw bytes",object_limit=q["object_limit"])
  dat=(ROOT/r["path"]).read_bytes()
  bioc=r["status_code"]==200 and (b"<collection" in dat[:300] or b"<collection>" in dat[:300])
  out.append(dict(source_id=q["source_id"],query_id=q["query_id"],status_code=r["status_code"],raw_pointer={f:r[f] for f in ("path","bytes","sha256")},valid_BioC_collection=bioc,original_JATS_qualified=False,read_scientific_body=False,full_structural_reaction_qualified=False,fresh_admitted=False))
  write(T,str(O/"query_execution.jsonl"),"".join(json.dumps(x,sort_keys=True)+"\n" for x in out))
 put(O/"raw_custody_summary.json",dict(task=T,HTTP=len(out),statuses=[x["status_code"] for x in out],valid_BioC_collections=sum(x["valid_BioC_collection"] for x in out),sources=out,unprocessed=0,no_scientific_body_read=True,original_JATS_custody_qualified=0,fresh_admitted=0,source_saturation=False))
 print(json.dumps(dict(HTTP=len(out),statuses=[x["status_code"] for x in out],BioC_collections=sum(x["valid_BioC_collection"] for x in out))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run}[sys.argv[1]]()
