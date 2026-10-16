#!/usr/bin/env python3
"""SS-E02 postfreeze metadata R2: bounded official bibliographic lookups.
Absolutely no chemical/source fulltext extraction, no source G6, no MCTS.
"""
from __future__ import annotations
import json,sys,hashlib,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
from scripts.task016_p7_source_harness import validate_query_accounting
TASK="TASK-016-P7"
G="outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R1/G5_FRESH_HOLDOUT_ACQUIRE.json"
AL="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R1-alias-audit-v1/role_A6_alias_manifest.json"
O="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-metadata/"
RAW="data/raw/task016-p7/SS/E02/SS-E02-R2-metadata/"
SELF="scripts/task016_p7_ss_e02_r2_metadata_v1.py"
def sha(p):return sha_file(ROOT/p)
def now():return datetime.now(timezone.utc).isoformat()
def save(path,obj):
 p=ROOT/path
 if p.exists():raise ContractError("immutable artifact already exists: "+path)
 write(TASK,path,json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def textsave(path,rows):
 p=ROOT/path
 if p.exists():raise ContractError("immutable artifact already exists: "+path)
 write(TASK,path,"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows))
def load(path):return json.loads((ROOT/path).read_text())
def check():
 verify_stage_chain(G,sha(G))
 assert load(AL)["fresh_admitted"]==0
def route(q):
 if q["route"]=="NCBI_PubMed_ESummary":
  return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"+urllib.parse.urlencode(
   {"db":"pubmed","id":"24916675,7646064","retmode":"json"})
 return "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(
  {"query":q["query"],"pageSize":20,"format":"json"})
def plan():
 check()
 queries=[
 dict(query_id="SS-E02-R2-A",query="24916675,7646064",
  route="NCBI_PubMed_ESummary",database="NCBI PubMed official ESummary",
  family="SS",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
  reason="identity resolution of two undecidable PMID-only R1 hints; not scientific reading",
  max_pages=1,max_objects=2),
 dict(query_id="SS-E02-R2-B",query='"flavonol 3-O-galactoside" glucosyltransferase',
  route="EuropePMC_REST_exact_galactoside",database="Europe PMC",
  family="SS",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
  reason="targeted second source discovery for parent galactoside O2 glucosylation",
  max_pages=1,max_objects=20),
 dict(query_id="SS-E02-R2-C",query='"flavonol 3-O-glucoside" glucosyltransferase',
  route="EuropePMC_REST_exact_glucoside",database="Europe PMC",
  family="SS",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
  reason="targeted independent parent glucoside O2 enzyme source clues",
  max_pages=1,max_objects=20)]
 save(O+"query_plan.json",dict(task=TASK,epoch_id="SS-E02",preregistered_at=now(),
  queries=queries,maximum_requests=3,max_bytes_per_response=1500000,
  max_concurrent=1,no_retries=True,scope_frozen_sha=sha(G),metadata_only=True,
  G5_branch_not_G6=True,no_structure_or_scientific_read=True,
  excluded="Cannot interpret query title/abstract as chemistry or fresh eligibility"))
 save(O+"execution_preregistration.json",dict(
  task=TASK,epoch_id="SS-E02",at=now(),frozen_G5_R1_sha=sha(G),
  prior_A6_alias_sha=sha(AL),plan_sha256=sha(O+"query_plan.json"),
  executing_code_sha256=sha(SELF),network_HTTP_limit=3,
  read_model_outcome=False,read_scientific_body=False,no_G6_admission=True))
 print("R2 preregistered 3 bounded metadata operations")
def parse(q,body,status):
 if status!=200:return []
 try: x=json.loads(body.decode("utf-8"))
 except (ValueError,UnicodeError):return []
 if q["route"]=="NCBI_PubMed_ESummary":
  res=x.get("result",{})
  out=[]
  for uid in res.get("uids",[])[:2]:
   r=res.get(uid,{})
   med=r.get("articleids",[]) or []
   first=lambda t:next((j.get("value") for j in med if j.get("idtype")==t),None)
   out.append(dict(key=str(uid),title=r.get("title"),year=str(r.get("pubdate",""))[:4] or None,
    DOI=first("doi"),PMID=uid,PMCID=first("pmc"),journal=r.get("fulljournalname"),
    article_ids=[dict(type=j.get("idtype"),value=j.get("value")) for j in med]))
  return out
 out=[]
 for r in x.get("resultList",{}).get("result",[])[:20]:
  k=r.get("pmid") or r.get("id")
  if not k:continue
  out.append(dict(key=str(k),title=r.get("title"),DOI=r.get("doi"),
   PMID=r.get("pmid"),PMCID=r.get("pmcid"),year=r.get("pubYear"),
   journal=r.get("journalTitle"),isOpenAccess=r.get("isOpenAccess")))
 return out
def run():
 check()
 reg=load(O+"execution_preregistration.json")
 if reg["plan_sha256"]!=sha(O+"query_plan.json") or reg["executing_code_sha256"]!=sha(SELF):
  raise ContractError("prereg/code SHA mismatch")
 for p in ("query_execution.jsonl","discovery_dispositions.jsonl",
   "physical_attempts.jsonl","raw_manifest.json","round_result.json"):
  if (ROOT/(O+p)).exists():raise ContractError("immutable R2 exists")
 planfile=load(O+"query_plan.json")
 execs=[];disc=[];attempts=[];objects=[]
 for q in planfile["queries"]:
  url=route(q)
  req=urllib.request.Request(url,headers={"User-Agent":"FlavoRetro/0.1 TASK-016-P7 metadata-only","Accept":"application/json"})
  at=now();status=None;body=b"";error=None
  try:
   with urllib.request.urlopen(req,timeout=17) as response:
    status=response.status
    body=response.read(1500001)
    if len(body)>1500000:raise ContractError("metadata response limit exceeded")
  except urllib.error.HTTPError as e:
   status=e.code;body=e.read(1500000);error=str(e)
  except (urllib.error.URLError,TimeoutError,OSError) as e:
   status="network_error";error=repr(e)
  rawpath=None;digest=None
  if body:
   digest=hashlib.sha256(body).hexdigest()
   rawpath=RAW+q["query_id"]+"-"+digest[:12]+".metadata"
   p=ROOT/rawpath
   if p.exists():raise ContractError("raw collision")
   p.parent.mkdir(parents=True,exist_ok=True)
   p.write_bytes(body)
   event(TASK,"raw_metadata_acquired",path=rawpath,bytes=len(body),after=digest)
   objects.append(dict(attempt_id=q["query_id"],path=rawpath,sha256=digest,
    bytes=len(body),kind="metadata"))
  extracted=parse(q,body,status)
  ids=set();unique=[]
  for r in extracted:
   if r["key"] not in ids:unique.append(r);ids.add(r["key"])
  for r in unique:
   disc.append(dict(record_id=q["query_id"]+"/"+r["key"],
    query_id=q["query_id"],disposition="metadata_only",
    source_hint=r,metadata_only=True,evidence_eligible=False,
    A3_identity="not_run",scientific_assay_eligible=False))
  execs.append(dict(query_id=q["query_id"],status="executed",
   returned_count=len(extracted),deduplicated_count=len(unique),
   pending_identity_count=0,admitted=0,deferred=0,rejected=0,
   metadata_only=len(unique),new_closure_groups=0,
   http_status=status,error=error,response_sha256=digest))
  attempts.append(dict(attempt_id=q["query_id"],url=url,status=status,
   started_at=at,bytes=len(body),sha256=digest,path=rawpath,
   recovery_chain=False,license=None,redistribution=False))
  print(q["query_id"],"HTTP",status,"hints",len(unique),flush=True)
 accounting=validate_query_accounting(planfile,execs,disc)
 textsave(O+"query_execution.jsonl",execs)
 textsave(O+"discovery_dispositions.jsonl",disc)
 textsave(O+"physical_attempts.jsonl",attempts)
 save(O+"raw_manifest.json",dict(objects=objects,http_requests=len(attempts),
  bytes=sum(r["bytes"] for r in attempts),article_versions=0,attachments=0))
 save(O+"round_result.json",dict(task=TASK,epoch_id="SS-E02",
  at=now(),status="metadata_only_R2_completed",accounting=accounting,
  actual_HTTP=len(attempts),bytes=sum(r["bytes"] for r in attempts),
  evidence_admitted=0,fresh_eligible=0,science_cells=0,
  new_qualified_groups=0,source_saturation=False,
  no_scientific_body_read=True,results_only_source_hints=True,
  raw_SHA_required=True,G4_unchanged_sha=sha(G),
  human_reviewed=False))
 print(json.dumps(dict(metadata_rows=len(disc),HTTP=len(attempts),
  bytes=sum(r["bytes"] for r in attempts),admitted=0),ensure_ascii=False))
if __name__=="__main__":
 {"plan":plan,"run":run}[sys.argv[1]]()
