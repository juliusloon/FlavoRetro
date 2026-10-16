#!/usr/bin/env python3
"""P7 SS-E02 postfreeze R2 targeted original acquisition, without science reading."""
from __future__ import annotations
import sys,json,hashlib,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
from scripts.task016_p7_source_harness import validate_query_accounting,validate_acquisition
TASK="TASK-016-P7"
SOURCE="PMC11125054"
G4="outputs/task016-p7/v1/SS/E02/stages/G4_SCOPE_FREEZE.json"
R2="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-metadata/"
O="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-original/"
RAW="data/raw/task016-p7/SS/E02/SS-E02-R2-PMC11125054-original/"
SELF="scripts/task016_p7_ss_e02_pmc11125054_acquire_v1.py"
CAND={"PMCID":"PMC11125054","PMID":"38794460","DOI":"10.3390/plants13101390"}
QUERIES=[
 dict(query_id="SS-E02-R2-SRC-A",query="PMC11125054 official fullTextXML",
 route="EuropePMC_original_JATS",database="Europe PMC",
 family="SS",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
 reason="post-freeze raw original acquisition only; need later independent A3/A4/A5",
 max_pages=1,max_objects=1),
 dict(query_id="SS-E02-R2-SRC-B",query="PMID 38794460 official PubMed summary",
 route="NCBI_original_metadata_corrob",database="NCBI PubMed",
 family="SS",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
 reason="independent authoritative identity check against original JATS front",
 max_pages=1,max_objects=1)]
URLS={"SS-E02-R2-SRC-A":"https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11125054/fullTextXML",
      "SS-E02-R2-SRC-B":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=38794460&retmode=json"}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def save(p,v):
 if (ROOT/p).exists():raise ContractError("immutable output exists "+p)
 write(TASK,p,json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def linesave(p,rr):
 if (ROOT/p).exists():raise ContractError("immutable output exists "+p)
 write(TASK,p,"".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in rr))
def j(p):return json.loads((ROOT/p).read_text())
def pre():
 verify_stage_chain(G4,sha(G4))
 hint=[json.loads(x) for x in (ROOT/(R2+"discovery_dispositions.jsonl")).read_text().splitlines()]
 known=[r for r in hint if r["source_hint"].get("PMCID")==SOURCE]
 if len(known)!=1:raise ContractError("single preregistered metadata identity required")
 if known[0]["source_hint"]["DOI"]!=CAND["DOI"]:
  raise ContractError("DOI from metadata mismatch")
 save(O+"query_plan.json",dict(task=TASK,epoch_id="SS-E02",
  preregistered_at=now(),queries=QUERIES,
  max_HTTP=2,max_bytes_each=1500000,concurrency=1,retries=0,
  post_G4_sha=sha(G4),R2_meta_hint_sha=sha(R2+"discovery_dispositions.jsonl"),
  allowed_urls=URLS,source=CAND,all_findings_are_unreviewed_deferred=True,
  no_chemical_read_or_structural_qualification=True))
 save(O+"pre_execution_manifest.json",dict(task=TASK,epoch_id="SS-E02",
  at=now(),plan_sha256=sha(O+"query_plan.json"),code_sha256=sha(SELF),
  frozen_stage_sha256=sha(G4),source=CAND,existing_historical_exposure_not_automatically_cleared=True,
  request_headers="non-evasive, documented public API, no bypass",
  read_holdout=False,read_model_outcome=False,no_new_scientific_reaction=True))
 print("Preregistered official source JATS+MED metadata, 2 HTTP max, no original content read")
def run():
 verify_stage_chain(G4,sha(G4))
 pre=j(O+"pre_execution_manifest.json")
 plan=j(O+"query_plan.json")
 if pre["plan_sha256"]!=sha(O+"query_plan.json") or pre["code_sha256"]!=sha(SELF):
  raise ContractError("pre-reg code or plan drift")
 if sha(G4)!=pre["frozen_stage_sha256"]:raise ContractError("G4 drift")
 for name in ("query_execution.jsonl","discovery_dispositions.jsonl",
  "physical_attempts.jsonl","raw_manifest.json","round_result.json"):
  if (ROOT/(O+name)).exists():raise ContractError("existing immutable source outcome")
 execs=[];discs=[];attempts=[];objects=[]
 for q in plan["queries"]:
  url=URLS[q["query_id"]]
  req=urllib.request.Request(url,headers={"User-Agent":"FlavoRetro/0.1 TASK016P7 lawful original acquisition",
   "Accept":"application/xml, application/json"})
  status=None;body=b"";err=None
  started=now()
  try:
   with urllib.request.urlopen(req,timeout=18) as f:
    status=f.status
    body=f.read(1500001)
    if len(body)>1500000:raise ContractError("original exceeds frozen cap")
  except urllib.error.HTTPError as e:
   status=e.code;body=e.read(1500000);err=str(e)
  except (TimeoutError,urllib.error.URLError,OSError) as e:
   status="network_error";err=str(e)
  digest=None;path=None
  if body:
   digest=hashlib.sha256(body).hexdigest()
   path=RAW+q["query_id"]+"-"+digest[:12]+(".article_version" if q["route"]=="EuropePMC_original_JATS" else ".metadata")
   target=ROOT/path
   if target.exists():raise ContractError("raw collision")
   target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(body)
   event(TASK,"original_or_metadata_raw_download",path=path,after=digest,bytes=len(body))
   objects.append(dict(attempt_id=q["query_id"],path=path,sha256=digest,
    bytes=len(body),kind="article_version" if q["route"]=="EuropePMC_original_JATS" else "metadata"))
  admit=bool(status==200 and body and (
   (q["route"]=="EuropePMC_original_JATS" and b"<article" in body[:10000])
   or (q["route"]=="NCBI_original_metadata_corrob" and body.lstrip().startswith(b"{"))))
  execs.append(dict(query_id=q["query_id"],status="executed",returned_count=int(admit),
   deduplicated_count=int(admit),pending_identity_count=int(admit),
   admitted=0,deferred=int(admit),rejected=0,metadata_only=0,new_closure_groups=0,
   http_status=status,error=err,body_SHA256=digest))
  if admit:
   discs.append(dict(record_id=q["query_id"]+"/"+SOURCE,query_id=q["query_id"],
    disposition="deferred",source_hint=CAND,metadata_only=False,
    evidence_eligible=False,identity_verification_sha=None,
    chemical_original_content_read=False,source_assay_reviewed=False,
    why="identity/chemical dual extraction pending, no source-admission decision"))
  attempts.append(dict(attempt_id=q["query_id"],url=url,status=status,
   bytes=len(body),started_at=started,path=path,sha256=digest,
   recovery_chain=False,license=None,redistribution=False))
  print(q["query_id"],"HTTP",status,"bytes",len(body),"raw",admit,flush=True)
 count=validate_query_accounting(plan,execs,discs)
 physical=dict(objects=objects,http_requests=len(attempts),
  bytes=sum(x["bytes"] for x in attempts),
  article_versions=sum(x["kind"]=="article_version" for x in objects),
  attachments=0)
 validate_acquisition(attempts,physical,root=ROOT)
 linesave(O+"query_execution.jsonl",execs)
 linesave(O+"discovery_dispositions.jsonl",discs)
 linesave(O+"physical_attempts.jsonl",attempts)
 save(O+"raw_manifest.json",physical)
 save(O+"round_result.json",dict(task=TASK,epoch_id="SS-E02",
  timestamp=now(),source=CAND,accounting=count,raw_source_objects=objects,
  http_requests=len(attempts),bytes=physical["bytes"],
  scientific_identity_status="pending_independent_A3",
  A4_A5_original_chemical_read=False,G6_admitted=0,
  G5_branch="acquisition_only",fresh=0,new_closure_groups=0,
  source_saturation=False,MCTS=0,scientific_ABE_cells=0,
  human_reviewed=False,independent_chemical_validation=False))
 print(json.dumps(dict(HTTP=len(attempts),bytes=physical["bytes"],
  raw_original=physical["article_versions"],G6_admitted=0),ensure_ascii=False))
if __name__=="__main__":
 {"pre":pre,"run":run}[sys.argv[1]]()
