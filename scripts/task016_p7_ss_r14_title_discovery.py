"""SS-E02 R14: source-budgeted title/ID discovery, no chemistry-body projection."""
from __future__ import annotations
import fcntl,hashlib,json,uuid,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
from scripts.task016_p7_ss_sources import require_acquisition_phase
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
TASK="TASK-016-P7"; B=Path("outputs/task016-p7/v1")
OUT=B/"SS/E02/fresh/SS-E02-R14-broad-title-discovery-v1"
RAW=Path("data/raw/task016-p7/SS/E02/SS-E02-R14-broad-title-discovery-v1")
LOCK=B/"source_budget_acquisition.lock"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
SCOPE=B/"SS/E02/scope_manifest.json"
EPOCH="SS-E02";SCOPE_ID="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1"
QUERIES=[
("SS-R14-01",'TITLE:"flavonol" AND TITLE:"glycosyltransferase"'),
("SS-R14-02",'TITLE:"glucosyltransferase" AND TITLE:"2″-O"'),
("SS-R14-03",'TITLE:"sophoroside" AND TITLE:"transferase"'),
("SS-R14-04",'TITLE:"diglucoside" AND TITLE:"glycosyltransferase"'),
("SS-R14-05",'TITLE:"3-O-glucoside" AND TITLE:"2″"'),
("SS-R14-06",'TITLE:"glycosyltransferase" AND TITLE:"pollen"'),
("SS-R14-07",'TITLE:"2-O-glucosylation" AND TITLE:"flavonol"'),
("SS-R14-08",'TITLE:"3-O-glycoside" AND TITLE:"glucosyltransferase"'),
]
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def read(p):return json.loads((ROOT/p).read_text())
def lines(p):return [json.loads(l) for l in (ROOT/p).read_text().splitlines() if l.strip()] if (ROOT/p).exists() else []
def save(p,v):
 if (ROOT/p).exists():raise RuntimeError("OUTPUT_ALREADY_EXISTS "+str(p))
 write(TASK,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def append(p,v):
 write(TASK,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n")
def canonical(url):
 u=urllib.parse.urlsplit(url)
 return (u.hostname or "",urllib.parse.unquote(u.path).rstrip("/"),tuple(sorted(urllib.parse.parse_qsl(u.query,keep_blank_values=True))))
def counter(rr):
 return dict(HTTP=len(rr),bytes=sum(int(x.get("bytes",0)) for x in rr),
  article_versions=sum(x.get("kind",x.get("role")) in ("article_version","xml","original_pdf") for x in rr),
  attachments=sum(x.get("kind",x.get("role"))=="attachment" for x in rr))
def prereg():
 if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
 verify_stage_chain(ROOT/G4,sha(G4));verify_stage_chain(ROOT/G5,sha(G5))
 plans=[]
 for qid,query in QUERIES:
  url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode({
   "query":query,"format":"json","resultType":"core","pageSize":100,"page":1})
  plans.append(dict(query_id=qid,url=url,source_id=qid,search_query=query,phase="fresh",
    family="SS",epoch_id=EPOCH,scope_id=SCOPE_ID,kind="metadata",
    route="EuropePMC_title_only_public_search",object_limit=2097152,
    max_pages=1,automatic_retry=False,automatic_redirect=False,
    metadata_projection_fields=["id","pmid","pmcid","doi","title","pubYear","journalTitle","pubTypeList","isOpenAccess","license","fullTextUrlList"],
    abstract_body_or_chemical_data_not_projected=True))
 with (ROOT/LOCK).open("a+") as l:
  fcntl.flock(l.fileno(),fcntl.LOCK_EX)
  gate=require_acquisition_phase("fresh",epoch_id=EPOCH,scope_id=SCOPE_ID)
  attempts=physical_attempts()
  for q in plans:q["prior_exact_canonical_URL_attempts"]=sum(canonical(x["url"])==canonical(q["url"]) for x in attempts)
  budget=dict(global_before=counter(attempts),SS_before=counter([r for r in attempts if "SS" in Path(r.get("path","")).parts]))
  fcntl.flock(l.fileno(),fcntl.LOCK_UN)
 save(OUT/"precontract.json",dict(task=TASK,epoch_id=EPOCH,batch="SS-E02-R14",
  created_at=now(),approval_type="agent_delegated",human_reviewed=False,
  purpose="metadata-only narrow title search after G4; no chemical science reads",
  registered_input_SHA={str(p):sha(p) for p in (G4,G5,SCOPE,Path("scripts/task016_p7_ss_r14_title_discovery.py"),B/"SS/E02/fresh/SS-E02-R10-new-source-discovery-v1/strict_title_dispositions_v1.json",B/"exposure_ledger.jsonl",B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl")},
  phase_gate=gate,budget_before=budget,
  batch_limits=dict(HTTP=8,bytes=8*2097152,article_versions=0,attachments=0),
  constraints=dict(metadata_only=True,no_source_bodies=True,no_si=True,no_new_mcts=True,
   old_URL_attempt_count_included=True,per_URL_cap=2,no_retry=True,
   no_redirect_follow=True,source_scientific_scope_status="unknown",
   not_fresh_from_titles=True,no_eligibility_or_source_saturation_inferred=True)))
 save(OUT/"query_plan.json",dict(task=TASK,phase="fresh",queries=plans,planned=len(plans),
    registered_at=now(),precontract_sha=sha(OUT/"precontract.json")))
 print(json.dumps(dict(preregistered=len(plans),global_HTTP=budget["global_before"]["HTTP"],SS_HTTP=budget["SS_before"]["HTTP"])),flush=True)
def acquire(q):
 if q not in read(OUT/"query_plan.json")["queries"]:raise RuntimeError("QUERY_NOT_PREREGISTERED")
 for p,h in read(OUT/"precontract.json")["registered_input_SHA"].items():
  if sha(Path(p))!=h:raise RuntimeError("REGISTERED_INPUT_DRIFT "+p)
 u=urllib.parse.urlsplit(q["url"])
 if u.scheme!="https" or u.hostname!="www.ebi.ac.uk" or u.path!="/europepmc/webservices/rest/search":raise RuntimeError("UNAPPROVED_HOST")
 with (ROOT/LOCK).open("a+") as f:
  fcntl.flock(f.fileno(),fcntl.LOCK_EX)
  try:
   require_acquisition_phase("fresh",epoch_id=EPOCH,scope_id=SCOPE_ID)
   attempts=physical_attempts();before=counter(attempts)
   sub=counter([r for r in attempts if "SS" in Path(r.get("path","")).parts])
   same=[r for r in attempts if canonical(r["url"])==canonical(q["url"])]
   if len(same)>=2 or any(r.get("status_code") in (401,403) for r in same):return dict(query_id=q["query_id"],result="rejected_old_url",HTTP=0)
   if before["HTTP"]+1>8000 or before["bytes"]+q["object_limit"]>8*1024**3:raise RuntimeError("GLOBAL_BUDGET_STOP")
   if sub["HTTP"]+1>2500 or sub["bytes"]+q["object_limit"]>2*1024**3:raise RuntimeError("SS_BUDGET_STOP")
   if len(lines(OUT/"http_ledger.jsonl"))>=8:raise RuntimeError("BATCH_HTTP_MAX")
   aid="SS-E02-R14-"+uuid.uuid4().hex
   start=now()
   prereg=dict(attempt_id=aid,query_id=q["query_id"],url=q["url"],family="SS",epoch_id=EPOCH,
     source_id=q["source_id"],kind="metadata",phase="fresh",registered_at=start,
     object_limit=q["object_limit"],prior_canonical_url_count=len(same),
     precontract_SHA=sha(OUT/"precontract.json"),query_plan_SHA=sha(OUT/"query_plan.json"),
     budget_before=before,SS_before=sub,scope_G4_SHA=sha(G4),scope_G5_SHA=sha(G5),
     method="GET",automatic_retry=False,automatic_redirect=False)
   append(OUT/"physical_request_preregistration.jsonl",prereg)
   data=b"";status=None;error=None;location=None;response=None
   try:
    request=urllib.request.Request(q["url"],headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 (public science metadata)","Accept-Encoding":"identity"})
    try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=30)
    except urllib.error.HTTPError as e:response=e;error=f"HTTP_{e.code}"
    status=response.code;location=response.geturl()
    data=response.read(q["object_limit"]+1)
    if len(data)>q["object_limit"]:data=data[:q["object_limit"]];error="OBJECT_LIMIT_TRUNCATED"
    if location!=q["url"] or 300<=status<400:error="NO_REDIRECT_FOLLOW"
   except Exception as e:error=type(e).__name__+":"+str(e)[:150]
   finally:
    if response is not None:response.close()
   raw=RAW/(aid+".metadata");p=ROOT/raw
   p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():raise RuntimeError("RAW_IMMUTABLE_EXISTS")
   p.write_bytes(data);p.chmod(0o444);event(TASK,"write_binary",path=str(raw),before=None,after=sha(raw),bytes=len(data))
   rec=dict(attempt_id=aid,query_id=q["query_id"],source_id=q["source_id"],url=q["url"],
    final_url=location,kind="metadata",role="metadata",phase="fresh",epoch_id=EPOCH,
    batch_id="SS-E02-R14-broad-title-discovery-v1",status_code=status,bytes=len(data),
    status="available" if status==200 and error is None else "failed",
    error=error,path=str(raw),sha256=sha(raw),started_at=start,finished_at=now(),
    scientific_body_content_read=False,chemical_extracted=False,metadata_only=True,
    no_recovery=True,no_redirect_follow=True,precontract_SHA=sha(OUT/"precontract.json"))
   append(OUT/"http_ledger.jsonl",rec);event(TASK,"source_http",**rec)
   return rec
  finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)
def run():
 for q in read(OUT/"query_plan.json")["queries"]:
  if any(r["query_id"]==q["query_id"] for r in lines(OUT/"query_execution.jsonl")):continue
  r=acquire(q)
  records=[];hits=None;error=None
  if r.get("status")=="available":
   try:
    data=json.loads((ROOT/r["path"]).read_text())
    hits=int(data.get("hitCount",0))
    for row in data.get("resultList",{}).get("result",[]):
     records.append({k:row[k] for k in ("id","pmid","pmcid","doi","title","pubYear","journalTitle","pubTypeList","isOpenAccess","license","fullTextUrlList") if k in row})
   except Exception as exc:error=type(exc).__name__+":"+str(exc)[:100]
  append(OUT/"title_metadata_projection.jsonl",dict(query_id=q["query_id"],hit_count=hits,
   project_count=len(records),metadata_records=records,
   input_original_SHA=r.get("sha256"),read_abstract=False,read_body=False,
   chemical_inference=False,pagination_unprocessed=bool(hits is not None and hits>len(records))))
  append(OUT/"query_execution.jsonl",dict(query_id=q["query_id"],status=r.get("status"),
   HTTP=0 if r.get("HTTP")==0 else 1,raw_pointer={k:r.get(k) for k in ("path","sha256","bytes")},
   hit_count=hits,records=len(records),error=error or r.get("error")))
  print(json.dumps(dict(q=q["query_id"],status=r.get("status_code"),hits=hits,records=len(records),err=error or r.get("error"))),flush=True)
def finish():
 executions=lines(OUT/"query_execution.jsonl");queries=read(OUT/"query_plan.json")["queries"]
 if len(executions)!=len(queries):raise RuntimeError("INCOMPLETE_BATCH")
 projs=lines(OUT/"title_metadata_projection.jsonl")
 cluster=json.loads((ROOT/B/"SS/E02/fresh/SS-E02-R10-new-source-discovery-v1/strict_identifier_clusters.json").read_text())["clusters"]
 all_old={x.casefold():row for row in cluster for x in row.get("identifier_tokens",[])}
 history= (ROOT/B/"exposure_ledger.jsonl").read_text().casefold()
 prior=(ROOT/B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl").read_text().casefold()
 universe={}
 for result in projs:
  for r in result["metadata_records"]:
   identities=[f"article:{r['pmcid']}".casefold()] if r.get("pmcid") else []
   identities += [f"doi:{r['doi']}".casefold()] if r.get("doi") else []
   identities += [f"pmid:{r['pmid']}".casefold()] if r.get("pmid") else []
   key=(r.get("doi") or r.get("pmcid") or r.get("pmid") or r.get("title") or "").casefold()
   if key not in universe:
    statuses=[all_old[x].get("project_exposure","unknown") for x in identities if x in all_old]
    old_hints=any(x in history or x in prior for x in identities)
    universe[key]=dict(source_id=r.get("pmcid"),doi=r.get("doi"),pmid=r.get("pmid"),title=r.get("title"),
      official_title_metadata=r,identifier_tokens=identities,
      old_R10_metadata_status=statuses,
      historical_exposure_token_literal_present=old_hints,
      freshness_status="known_exposed_or_unknown_pending_strict_alias_review" if old_hints or "known_exposed" in statuses else "unknown_not_certified_unexposed",
      scientific_qualification=False,source_original_acquired=False,full_reaction_structure=False,
      fresh_admitted=False,queries=[result["query_id"]])
   else:universe[key]["queries"].append(result["query_id"])
 allrows=list(universe.values());selected=[r for r in allrows if ("glucosyltransferase" in (r.get("title") or "").casefold() or "sophoroside" in (r.get("title") or "").casefold())]
 save(OUT/"discovered_title_identity_dispositions.json",dict(task=TASK,epoch_id=EPOCH,
    timestamp=now(),distinct_titles=len(allrows),keyword_related_titles=len(selected),
    all_titles=allrows,keyword_related=selected,
    title_is_not_reaction_evidence=True,raw_science_not_read=True,scientific_fresh=0,
    saturation_not_established=True,no_scope_change=True,formal_review=False))
 physical=lines(OUT/"http_ledger.jsonl")
 save(OUT/"bounded_metadata_audit.json",dict(task=TASK,epoch_id=EPOCH,
    planned_queries=len(queries),terminals=len(executions),actual_HTTP=len(physical),
    actual_bytes=sum(r["bytes"] for r in physical),source_titles=len(allrows),
    metadata_projection_only=True,new_article_originals=0,qualified_reactions=0,
    fresh=0,unprocessed=[q["query_id"] for q in queries if not any(r["query_id"]==q["query_id"] for r in executions)],
    original_reads=0,scope_changed=False,failed_HTTP=[r["query_id"] for r in physical if r["status"]!="available"]))
 print(json.dumps(dict(planned=len(queries),actual_HTTP=len(physical),metadata_titles=len(allrows),relevant_titles=len(selected))),flush=True)
if __name__=="__main__":
 import sys
 if len(sys.argv)!=2 or sys.argv[1] not in ("pre","run","finish"):raise SystemExit("usage: pre|run|finish")
 {"pre":prereg,"run":run,"finish":finish}[sys.argv[1]]()

