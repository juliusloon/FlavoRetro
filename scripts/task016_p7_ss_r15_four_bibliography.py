"""SS-E02 R15: dual-provider bibliography check on four R14 emerging primary titles.

A3 publication preflight only. Does NOT inspect scientific original, abstracts,
chemical conditions, or decide scope/fresh admissibility.
"""
from __future__ import annotations
import urllib.parse,urllib.request,urllib.error,fcntl,hashlib,json,uuid,html,re
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_c_e02_http import physical_attempts,NoRedirect
from scripts.task016_p7_ss_sources import require_acquisition_phase
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1"
RAW=Path("data/raw/task016-p7/SS/E02/SS-E02-R15-four-new-primary-bibliography-v1")
R14=B/"SS/E02/fresh/SS-E02-R14-broad-title-discovery-v1"
R13=B/"SS/E02/fresh/SS-E02-R13-title-metadata-discovery-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
SCOPE=B/"SS/E02/scope_manifest.json"
LOCK=B/"source_budget_acquisition.lock"
CANDIDATES=["10.1021/acs.jafc.5c06227","10.1021/acs.jafc.4c03824","10.1111/tpj.16898","10.1021/acs.jafc.4c00488"]
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()] if (ROOT/p).exists() else []
def put(p,value):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS "+str(p))
 write(TASK,str(p),json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def append(p,row):
 write(TASK,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
def canonical_url(url):
 p=urllib.parse.urlsplit(url)
 return (p.hostname or "",urllib.parse.unquote(p.path).rstrip("/"),tuple(sorted(urllib.parse.parse_qsl(p.query,keep_blank_values=True))))
def totals(q):
 return dict(HTTP=len(q),bytes=sum(r["bytes"] for r in q),
 article_versions=sum(r.get("kind",r.get("role"))=="article_version" for r in q),
 attachments=sum(r.get("kind",r.get("role"))=="attachment" for r in q))
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE_R15_EXISTS")
 verify_stage_chain(ROOT/G4,sha(G4));verify_stage_chain(ROOT/G5,sha(G5))
 source=load(R14/"discovered_title_identity_dispositions.json")["all_titles"]
 candidate=[next(r for r in source if r.get("doi")==doi) for doi in CANDIDATES]
 assert len(candidate)==4 and len({r["doi"] for r in candidate})==4
 assert all(r.get("historical_exposure_token_literal_present") is False and r.get("old_R10_metadata_status")==[] for r in candidate)
 assert all(r["official_title_metadata"].get("isOpenAccess")=="N" for r in candidate)
 plans=[dict(query_id=f"SS-R15-CROSSREF-{i:02d}",url="https://api.crossref.org/works/"+urllib.parse.quote(x["doi"],safe=""),
   expected_DOI=x["doi"],kind="metadata",phase="fresh",family="SS",epoch_id="SS-E02",
   scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
   route="Crossref_exact_DOI_bibliography_only",object_limit=2097152,
   no_automatic_retry=True,no_redirect_follow=True) for i,x in enumerate(candidate,1)]
 with (ROOT/LOCK).open("a+") as fd:
  fcntl.flock(fd.fileno(),fcntl.LOCK_EX)
  gate=require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
  attempts=physical_attempts()
  for p in plans:p["prior_canonical_attempts"]=sum(canonical_url(p["url"])==canonical_url(x["url"]) for x in attempts)
  prior=dict(global_=totals(attempts),SS=totals([r for r in attempts if "SS" in Path(r.get("path") or "").parts]))
  fcntl.flock(fd.fileno(),fcntl.LOCK_UN)
 inputs=[R14/"discovered_title_identity_dispositions.json",
   R14/"query_execution.jsonl",R13/"bounded_metadata_audit.json",
   B/"SS/E02/fresh/SS-E02-R10-new-source-discovery-v1/strict_title_dispositions_v1.json",
   B/"exposure_ledger.jsonl",
   B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl",
   G4,G5,SCOPE,Path("scripts/task016_p7_ss_r15_four_bibliography.py")]
 put(O/"precontract.json",dict(task=TASK,family="SS",epoch_id="SS-E02",timestamp=now(),role="A2+A3_metadata_preflight",
   agent_approval="agent_delegated",human_reviewed=False,
   purpose="authoritative Crossref second bibliographic route for four previously unseen EPMC titles; NO science/full original",
   candidate_source_count=4,selected=candidate,
   registered_input_SHA={str(p):sha(p) for p in inputs},
   fresh_gate=gate,budget_before=prior,
   budget_limit=dict(max_HTTP=4,max_bytes=8388608,no_article_versions=True),
   source_custody=False,chemical_body_read=False,abstract_read=False,
   source_structure_qualified=False,full_A3_original_front_not_yet_performed=True,
   scope_not_adjusted=True,no_MCTS=True,no_automatic_fresh=True,
   title_assay_donor_product_unknown=True,
   provider_subscription_status_preserved=True))
 put(O/"query_plan.json",dict(task=TASK,planned=len(plans),queries=plans,registered_at=now(),precontract_SHA=sha(O/"precontract.json")))
 print(json.dumps(dict(R15_registered=4,global_before=prior["global_"]["HTTP"],SS_before=prior["SS"]["HTTP"])),flush=True)
def acquire(p):
 if p not in load(O/"query_plan.json")["queries"]:raise RuntimeError("PLAN_MISSING")
 for path,h in load(O/"precontract.json")["registered_input_SHA"].items():
  if sha(Path(path))!=h:raise RuntimeError("SHA_INPUT_DRIFT "+path)
 s=urllib.parse.urlsplit(p["url"])
 if s.scheme!="https" or s.hostname!="api.crossref.org" or not s.path.startswith("/works/"):
  raise RuntimeError("HOST_ROUTE_NOT_AUTHORITATIVE")
 with (ROOT/LOCK).open("a+") as handle:
  fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
  try:
   require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
   all_=physical_attempts()
   sub=[r for r in all_ if "SS" in Path(r.get("path") or "").parts]
   count=sum(canonical_url(r["url"])==canonical_url(p["url"]) for r in all_)
   if count>=2 or any(canonical_url(r["url"])==canonical_url(p["url"]) and r.get("status_code") in (401,403) for r in all_):
    return dict(query_id=p["query_id"],result="skipped_URL_cap_or_auth",HTTP=0)
   if totals(all_)["HTTP"]+1>8000 or totals(all_)["bytes"]+p["object_limit"]>8*1024**3 or totals(sub)["HTTP"]+1>2500 or totals(sub)["bytes"]+p["object_limit"]>2*1024**3:
    raise RuntimeError("SOURCE_HARD_BUDGET_STOP")
   if len(rows(O/"http_ledger.jsonl"))>=4:raise RuntimeError("R15_4_CAP")
   aid="SS-E02-R15-"+uuid.uuid4().hex;started=now()
   append(O/"physical_request_preregistration.jsonl",dict(attempt_id=aid,query_id=p["query_id"],
      url=p["url"],source_id=p["expected_DOI"],registered_at=started,kind="metadata",
      object_limit=p["object_limit"],precontract_SHA=sha(O/"precontract.json"),
      query_plan_SHA=sha(O/"query_plan.json"),prior_URLs=count,HTTP_before=totals(all_)["HTTP"]))
   data=b"";status=None;error=None;final=None;response=None
   try:
    req=urllib.request.Request(p["url"],headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 public research","Accept-Encoding":"identity"})
    try:response=urllib.request.build_opener(NoRedirect()).open(req,timeout=30)
    except urllib.error.HTTPError as e:response=e;error="HTTP_"+str(e.code)
    status=response.code;final=response.geturl()
    data=response.read(p["object_limit"]+1)
    if len(data)>p["object_limit"]:data=data[:p["object_limit"]];error="OBJECT_TRUNCATED"
    if final!=p["url"] or 300<=status<400:error="NO_AUTO_REDIRECT"
   except Exception as e:error=type(e).__name__+":"+str(e)[:90]
   finally:
    if response is not None:response.close()
   path=RAW/(aid+".metadata"); target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():raise RuntimeError("IMMUTABLE_RAW_EXISTS")
   target.write_bytes(data);target.chmod(0o444)
   event(TASK,"write_binary",path=str(path),before=None,after=sha(path),bytes=len(data))
   r=dict(attempt_id=aid,source_id=p["expected_DOI"],query_id=p["query_id"],url=p["url"],
       started_at=started,finished_at=now(),status_code=status,error=error,final_url=final,
       kind="metadata",role="metadata",phase="fresh",epoch_id="SS-E02",
       status="available" if status==200 and error is None else "failed",bytes=len(data),
       path=str(path),sha256=sha(path),precontract_SHA=sha(O/"precontract.json"),
       scientific_body_content_read=False,abstract_interpreted=False,chemical_extracted=False,
       no_auto_retry=True,no_auto_redirect=True,
       current_epoch_fresh_eligible=False)
   append(O/"http_ledger.jsonl",r);event(TASK,"source_http",**r)
   return r
  finally:fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
def execute():
 for q in load(O/"query_plan.json")["queries"]:
  if any(x["query_id"]==q["query_id"] for x in rows(O/"query_execution.jsonl")):continue
  r=acquire(q)
  record=None;error=None
  if r.get("status")=="available":
   try:
    x=json.loads((ROOT/r["path"]).read_text())["message"]
    record={key:x.get(key) for key in ("DOI","title","container-title","publisher","type","issued","published","volume","issue","page","article-number","link","license","URL","relation") if key in x}
   except Exception as exc:error=type(exc).__name__+":"+str(exc)[:90]
  append(O/"crossref_bibliography_projection.jsonl",dict(query_id=q["query_id"],DOI=q["expected_DOI"],
     original_raw={k:r.get(k) for k in ("path","sha256","bytes")},metadata=record,
     no_abstract_body_or_chemistry=True))
  append(O/"query_execution.jsonl",dict(query_id=q["query_id"],status=r.get("status"),
    HTTP=0 if r.get("HTTP")==0 else 1,DOI=q["expected_DOI"],raw_pointer={k:r.get(k) for k in ("path","sha256","bytes")},
    projected=record is not None,error=error or r.get("error")))
  print(json.dumps(dict(q=q["query_id"],status=r.get("status_code"),bibliography=record is not None,err=error or r.get("error"))),flush=True)
def canon(s):
 s=re.sub("<[^>]*>","",html.unescape(s or ""))
 return re.sub(r"[^a-z0-9]+","",s.casefold())
def finished():
 plans=load(O/"query_plan.json")["queries"]
 queries=rows(O/"query_execution.jsonl")
 if len(queries)!=4:raise RuntimeError("R15_FOUR_TERMINALS_REQUIRED")
 original={x["doi"]:x for x in load(R14/"discovered_title_identity_dispositions.json")["all_titles"]}
 records=[]
 for projection in rows(O/"crossref_bibliography_projection.jsonl"):
  doi=projection["DOI"]; m=projection["metadata"]; a=original[doi]
  if m:
   titles=m.get("title") or [];primary=titles[0] if titles else ""
   years=[str(d) for t in ("issued","published") for d in (m.get(t,{}).get("date-parts",[]) or [])[:1]]
   years=[x for row in years for x in row if isinstance(x,int)]
   expected=int(a["official_title_metadata"]["pubYear"])
   check=dict(DOI=m.get("DOI","").casefold()==doi.casefold(),
     title_literal=canon(primary)==canon(a["title"]),
     same_pub_year=expected in years,
     type_primary=m.get("type")=="journal-article",
     journal_title_present=bool(m.get("container-title")),
     publisher_present=bool(m.get("publisher")))
  else:check={}
  records.append(dict(doi=doi,PMID=a["pmid"],EPMC_title=a["title"],
   Crossref_title=m["title"][0] if m and m.get("title") else None,
   checks=check,bibliographic_two_official_routes_passed=bool(check) and all(check.values()),
   original_fulltext_available=False,legal_fulltext_status=a["official_title_metadata"].get("fullTextUrlList"),
   data_provider_access=a["official_title_metadata"].get("isOpenAccess"),
   source_original_identity_verified=False,scientific_body_read=False,
   product=None,acceptor=None,donor=None,site=None,stereo=None,
   frozen_scope_O2_support=None,source_exposure_status="unknown_requires_alias_graph",
   source_fresh_eligible=False))
 put(O/"A3_two_route_bibliographic_preflight.json",dict(task=TASK,epoch_id="SS-E02",timestamp=now(),
   records=records,planned_sources=4,passed=sum(x["bibliographic_two_official_routes_passed"] for x in records),
   failed=sum(bool(x["checks"]) and not all(x["checks"].values()) for x in records),
   pending=sum(not x["checks"] for x in records),full_originals=0,
   source_qualified_for_P7=0,fresh_admitted=0,
   claims_bounded_to_bibliography_only=True,not_A3_original_identity=True,
   not_source_absence_or_saturation=True,no_chemical_structure_or_model_read=True))
 put(O/"bounded_source_access_and_bibliography_audit.json",dict(task=TASK,epoch_id="SS-E02",
    planned=4,terminals=len(queries),HTTP=len(rows(O/"http_ledger.jsonl")),
    bytes=sum(x["bytes"] for x in rows(O/"http_ledger.jsonl")),
    bibliography_passed=sum(x["bibliographic_two_official_routes_passed"] for x in records),
    original_science_read=0,qualified_reactions=0,fresh=0,
    source_access="EuropePMC advertised subscription required for four at R14; Crossref metadata does not lift that restriction",
    next_step="seek lawful independently hosted full text or source-specific public SI; do not presume eligibility",
    saturation_claim=False))
 print(json.dumps(dict(checked=4,verified=sum(x["bibliographic_two_official_routes_passed"] for x in records),
   errors=sum(x["checks"] != {} and not all(x["checks"].values()) for x in records),
   full_originals=0,fresh=0)),flush=True)
if __name__=="__main__":
 import sys
 if len(sys.argv)!=2 or sys.argv[1] not in ("pre","run","finish"):raise SystemExit("pre|run|finish")
 {"pre":pre,"run":execute,"finish":finished}[sys.argv[1]]()

