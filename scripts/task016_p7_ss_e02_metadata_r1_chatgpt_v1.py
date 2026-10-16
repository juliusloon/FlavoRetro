#!/usr/bin/env python3
"""Only metadata-hint discovery AFTER SS-E02 G4; no chemistry reads/admissions."""
from __future__ import annotations
import sys,json,hashlib,urllib.parse,urllib.request,urllib.error,uuid
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
from scripts.task016_p7_source_harness import validate_query_accounting
TASK="TASK-016-P7"
DIR=Path("outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R1-metadata")
RAW=Path("data/raw/task016-p7/SS/E02/SS-E02-R1-metadata")
G4=Path("outputs/task016-p7/v1/SS/E02/stages/G4_SCOPE_FREEZE.json")
SCOPE=Path("outputs/task016-p7/v1/SS/E02/scope_manifest.json")
SELF=Path("scripts/task016_p7_ss_e02_metadata_r1_chatgpt_v1.py")
def utc():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def store(p,text):
 p=Path(p)
 if (ROOT/p).exists():raise ContractError("immutable output exists "+str(p))
 write(TASK,str(p),text)
def jsonput(p,obj):
 store(p,json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def params():
 verify_stage_chain(G4,sha(G4))
 scope=json.loads((ROOT/SCOPE).read_text())
 if scope["epoch_id"]!="SS-E02" or scope["holdout_extraction_started"] is not False:
  raise ContractError("SS-E02 not source-frozen ahead of fresh")
 return scope
def make_plan():
 scope=params()
 q=[
 dict(query_id="SS-E02-R1-META-01",route="EuropePMC_REST",database="Europe PMC",
 query='flavonol glycoside 2 O glucosyltransferase Petunia kaempferol',
 family="SS",scope_id=scope["scope_audit"]["scope_audits"][0]["template_id"],
 reason="discover alternative flavonol 3-O hexose 2-O transfer publication metadata only",
 max_pages=1,max_objects=10),
 dict(query_id="SS-E02-R1-META-02",route="Crossref_work_bibliography",database="Crossref",
 query='flavonol 3 O glycoside 2 O glucosyltransferase UDP glucose',
 family="SS",scope_id=scope["scope_audit"]["scope_audits"][0]["template_id"],
 reason="independent DOI/publication index, not new chemistry evidence",
 max_pages=1,max_objects=10),
 dict(query_id="SS-E02-R1-META-03",route="NCBI_PubMed_ESearch",database="PubMed",
 query='flavonol glycoside 2-O glucosyltransferase UDP-glucose',
 family="SS",scope_id=scope["scope_audit"]["scope_audits"][0]["template_id"],
 reason="third independent citation metadata discovery route",
 max_pages=1,max_objects=10)]
 jsonput(DIR/"query_plan.json",dict(task=TASK,epoch_id="SS-E02",
  preregistered_at=utc(),queries=q,
  stage="G5 preregistration only; NOT frozen G5 acquired/qualified",
  scope_sha256=sha(SCOPE),
  frozen_G4_sha256=sha(G4),
  prior_exposure_not_eligible_as_fresh=True,metadata_only=True,
  no_fulltext_no_chemical_read=True,no_manual_SMILES=True,
  max_HTTP=3,allow_retries=False,max_concurrency=1,
  human_reviewed=False))
 jsonput(DIR/"preregistered_execution_boundary.json",dict(
  task=TASK,epoch_id="SS-E02",role="A2 metadata-only scout",
  timestamp=utc(),query_plan_sha256=sha(DIR/"query_plan.json"),
  G4_sha256=sha(G4),SCOPE_sha256=sha(SCOPE),code_sha256=sha(SELF),
  no_chemical_or_structure_extraction=True,no_A3_qualification=True,
  new_holder_cannot_become_fresh_without_separate_A3_A4_A5_A6=True,
  protected_historical_inputs_unchanged=True))
 print("SS-E02 R1 METADATA plan registered, three distinct routes; 0 HTTP")
def request_url(row):
 query=row["query"]
 if row["route"]=="EuropePMC_REST":
  return "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode({"query":query,"pageSize":10,"format":"json"})
 if row["route"]=="Crossref_work_bibliography":
  return "https://api.crossref.org/works?"+urllib.parse.urlencode({"query.bibliographic":query,"rows":10})
 if row["route"]=="NCBI_PubMed_ESearch":
  return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"+urllib.parse.urlencode({"db":"pubmed","term":query,"retmax":10,"retmode":"json"})
 raise ContractError("unknown route")
def extract(row,raw,status):
 if status != 200:return []
 try: value=json.loads(raw.decode("utf-8"))
 except (UnicodeDecodeError,json.JSONDecodeError):return []
 route=row["route"]
 if route=="EuropePMC_REST":
  records=value.get("resultList",{}).get("result",[])
  return [(str(x.get("id","")),dict(title=x.get("title"),DOI=x.get("doi"),
     PMID=x.get("pmid"),PMCID=x.get("pmcid"),journal=x.get("journalTitle"),
     year=x.get("pubYear"))) for x in records if x.get("id")]
 if route=="Crossref_work_bibliography":
  records=value.get("message",{}).get("items",[])
  return [(str(x.get("DOI","")),dict(title=(x.get("title") or [None])[0],
    DOI=x.get("DOI"),journal=(x.get("container-title") or [None])[0],
    year=(x.get("published",{}).get("date-parts",[[None]])[0] or [None])[0]))
    for x in records if x.get("DOI")]
 if route=="NCBI_PubMed_ESearch":
  records=value.get("esearchresult",{}).get("idlist",[])
  return [(str(i),dict(PMID=str(i),other_source_identity=None)) for i in records]
 return []
def run():
 scope=params()
 plan=json.loads((ROOT/DIR/"query_plan.json").read_text())
 reg=json.loads((ROOT/DIR/"preregistered_execution_boundary.json").read_text())
 if sha(DIR/"query_plan.json")!=reg["query_plan_sha256"] or sha(SELF)!=reg["code_sha256"]:
  raise ContractError("pre-HTTP query/code SHA drift")
 for output in ("query_execution.jsonl","discovery_dispositions.jsonl","physical_attempts.jsonl","raw_manifest.json","round_result.json"):
  if (ROOT/DIR/output).exists():raise ContractError("immutable round output exists")
 executions=[]; discoveries=[]; attempts=[]; objs=[]
 for row in plan["queries"]:
  url=request_url(row)
  request=urllib.request.Request(url,headers={"User-Agent":"FlavoRetro/0.1 evidence-audit metadata-only","Accept":"application/json"})
  started=utc();status=None;body=b"";error=None
  try:
   with urllib.request.urlopen(request,timeout=17) as reply:
    status=reply.status
    body=reply.read(1500000+1)
    if len(body)>1500000:raise ContractError("metadata HTTP >1.5MB cap")
  except urllib.error.HTTPError as e:
   status=e.code;body=e.read(1500000);error=str(e)
  except (urllib.error.URLError, TimeoutError, OSError) as e:
   status="network_error";error=repr(e)
  obj_path=None;digest=None
  if body:
   digest=hashlib.sha256(body).hexdigest()
   obj_path=RAW/(row["query_id"]+"-"+digest[:12]+".metadata")
   from scripts.operate import event
   p=ROOT/obj_path
   if p.exists():raise ContractError("immutable raw bytes path unexpectedly occupied")
   p.parent.mkdir(parents=True,exist_ok=True)
   p.write_bytes(body)
   event(TASK,"raw_metadata_acquired",path=str(obj_path),after=digest,bytes=len(body))
   objs.append(dict(query_id=row["query_id"],path=str(obj_path),sha256=digest,bytes=len(body),kind="metadata"))
  attempts.append(dict(query_id=row["query_id"],route=row["route"],url=url,http_status=status,
   started_at=started,ended_at=utc(),bytes=len(body),path=str(obj_path) if obj_path else None,
   sha256=digest,error=error,attempt_count=1,source_qualified=False))
  found=extract(row,body,status)
  ids=set();dedup=[]
  for source_id,metadata in found:
   if source_id not in ids:
    dedup.append((source_id,metadata));ids.add(source_id)
  for src,metadata in dedup:
   discoveries.append(dict(record_id=row["query_id"]+"/"+src,
    query_id=row["query_id"],disposition="metadata_only",
    source_hint=metadata,metadata_only=True,evidence_eligible=False,
    holdout_qualification="not_reviewed",A3_identity="not_run"))
  executions.append(dict(query_id=row["query_id"],status="executed",
   returned_count=len(found),deduplicated_count=len(dedup),
   pending_identity_count=0,admitted=0,deferred=0,rejected=0,
   metadata_only=len(dedup),new_closure_groups=0,
   url=url,http_status=status,network_error=error,
   body_stored_sha256=digest))
  print(row["query_id"],status,"returned",len(found),"metadata",len(dedup),flush=True)
 result=validate_query_accounting(plan,executions,discoveries)
 jsonput(DIR/"query_execution.jsonl","unreachable") if False else None
 store(DIR/"query_execution.jsonl","".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in executions))
 store(DIR/"discovery_dispositions.jsonl","".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in discoveries))
 store(DIR/"physical_attempts.jsonl","".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in attempts))
 jsonput(DIR/"raw_manifest.json",dict(task=TASK,epoch_id="SS-E02",
   objects=objs,http_requests=len(attempts),bytes=sum(x["bytes"] for x in attempts),
   article_versions=0,attachments=0))
 jsonput(DIR/"round_result.json",dict(task=TASK,epoch_id="SS-E02",
  status="metadata_only_complete_no_scientific_G6_admission",
  timestamp=utc(),query_accounting=result,
  http_requests=len(attempts),download_bytes=sum(x["bytes"] for x in attempts),
  post_freeze_metadata_hints=len(discoveries),
  new_source_identity_verified=0,new_structure_complete=0,
  fresh_eligible=0,source_closure_groups=0,
  no_fulltext_or_chemical_read=True,no_qualification=True,
  G5_scientific_acquisition_not_closed=True,G6_not_started=True,
  saturated=False,scientific_ABE_cells=0,metrics=None,
  G4_unchanged_sha256=sha(G4),scope_unchanged_sha256=sha(SCOPE),
  human_reviewed=False))
 print(json.dumps(dict(status="metadata_only",accounting=result,
  queries=3,physical_HTTP=3,fresh=0),ensure_ascii=False))
if __name__=="__main__":
 {"plan":make_plan,"run":run}[sys.argv[1]]()
