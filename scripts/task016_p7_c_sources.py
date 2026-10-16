"""P7 C scout immutable official acquisition. Eligibility belongs to A3/A4/A5."""
import json,sys,hashlib,urllib.request,urllib.error,urllib.parse,uuid,fcntl
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write,event
TASK="TASK-016-P7";OUT=ROOT/"outputs/task016-p7/v1/C";RAW=ROOT/"data/raw/task016-p7/C"
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()] if Path(p).exists() else []
def save(n,x):write(TASK,str((OUT/n).relative_to(ROOT)),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def save_rows(n,x):write(TASK,str((OUT/n).relative_to(ROOT)),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in x))
def append(n,r):save_rows(n,rows(OUT/n)+[r])
def raw_manifest():
 rr=rows(OUT/"http_ledger.jsonl")
 save("raw_manifest.json",dict(objects=[dict(attempt_id=r["attempt_id"],path=r["path"],sha256=r["sha256"],bytes=r["bytes"],kind=r["kind"]) for r in rr if r["path"] is not None],bytes=sum(r["bytes"] for r in rr),http_requests=len(rr),article_versions=sum(r["kind"]=="article_version" for r in rr),attachments=sum(r["kind"]=="attachment" for r in rr)))
def require_epoch_open(epoch_id="C-E01"):
 ledger=ROOT/"outputs/task016-p7/v1/epoch_ledger.jsonl"
 if not ledger.is_file():raise RuntimeError("C_EPOCH_LEDGER_MISSING")
 rr=[r for r in rows(ledger) if r.get("family")=="C" and r.get("epoch_id")==epoch_id]
 if not rr:raise RuntimeError("C_EPOCH_NOT_REGISTERED")
 terminal_types={"epoch_incomplete_decision","epoch_invalidation","epoch_invalidated","epoch_closed","epoch_complete"}
 terminal_status={"development_epoch_incomplete","invalidated","closed","complete","completed"}
 for r in rr:
  if r.get("event_type") in terminal_types or r.get("status") in terminal_status:
   decision=r.get("decision_manifest_path")
   expected=r.get("decision_manifest_sha256")
   if decision and expected and (not (ROOT/decision).is_file() or sha(ROOT/decision)!=expected):
    raise RuntimeError("C_CLOSED_EPOCH_DECISION_SHA_MISMATCH")
   raise RuntimeError("C_EPOCH_CLOSED:"+epoch_id)
 decision=ROOT/"outputs/task016-p7/v1/epochs"/epoch_id/"incomplete_decision.json"
 if decision.exists():raise RuntimeError("C_EPOCH_CLOSED:"+epoch_id)
 return True
def require_fresh_scope(epoch_id="C-E01"):
 # A prior frozen bank never reopens a terminal epoch. Future fresh namespaces
 # require a separately implemented/registered intake bound to their own G4/G5.
 require_epoch_open(epoch_id)
 if epoch_id!="C-E01":raise RuntimeError("C_NEW_EPOCH_FRESH_NAMESPACE_NOT_INITIALIZED")
 freeze=OUT/"E01/scope_manifest.json";stage=OUT/"E01/stages/G4_SCOPE_FREEZE.json"
 if not freeze.exists() or not stage.exists():raise RuntimeError("C_SCOPE_NOT_FROZEN")
 from scripts.task016_p7_orchestrate import verify_stage_chain
 verify_stage_chain(stage,sha(stage))
 m=json.loads(freeze.read_text());g=json.loads(stage.read_text())
 if m["family"]!="C" or m["epoch_id"]!="C-E01" or g["stage"]!="G4_SCOPE_FREEZE" or str(freeze.relative_to(ROOT)) not in g["files"] or g["files"][str(freeze.relative_to(ROOT))]!=sha(freeze):raise RuntimeError("C_SCOPE_STAGE_BINDING_MISMATCH")
 for name,h in m["files_sha256"].items():
  path=ROOT/name if name.startswith(("outputs/","flavoretro/","scripts/","data/")) else freeze.parent/name
  if sha(path)!=h:raise RuntimeError("C_SCOPE_FREEZE_DRIFT")
 return sha(freeze)
def _get_locked(url,kind,reason,phase="design",license=None):
 if phase not in ("design","fresh"):raise ValueError("C_UNKNOWN_SOURCE_PHASE")
 if phase=="fresh":require_fresh_scope()
 rr=rows(OUT/"http_ledger.jsonl")
 if len(rr)>=2500 or sum(r["bytes"] for r in rr)>=2*1024**3:raise RuntimeError("C_BUDGET_LIMIT")
 if kind=="article_version" and sum(r["kind"]=="article_version" for r in rr)>=120:raise RuntimeError("C_ARTICLE_VERSION_LIMIT")
 if kind=="attachment" and sum(r["kind"]=="attachment" for r in rr)>=200:raise RuntimeError("C_ATTACHMENT_LIMIT")
 attempts=sum(r["url"]==url for r in rr)
 if attempts>=2:raise RuntimeError("URL_ATTEMPT_LIMIT")
 aid="C-SCOUT-"+uuid.uuid4().hex;started=now()
 append("acquisition_plan.jsonl",dict(attempt_id=aid,url=url,kind=kind,reason=reason,phase=phase,registered_at=started,limit_bytes=80*1024**2))
 data=b"";status_code=None;error=None;headers={}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 public research"}),timeout=30) as response:
   status_code=response.status;headers=dict(response.headers);data=response.read(80*1024**2+1)
  if len(data)>80*1024**2:raise ValueError("OBJECT_LIMIT")
 except urllib.error.HTTPError as e:status_code=e.code;data=e.read(1024**2);error=str(e)
 except Exception as e:error=type(e).__name__+": "+str(e)
 ext=Path(urllib.parse.urlparse(url).path).suffix or "."+kind
 path=RAW/(hashlib.sha256(url.encode()).hexdigest()+f".attempt-{attempts+1}"+ext)
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise RuntimeError("IMMUTABLE_PATH_EXISTS")
 path.write_bytes(data);path.chmod(0o444)
 r=dict(attempt_id=aid,url=url,kind=kind,phase=phase,reason=reason,status="available" if status_code==200 and error is None else "failed",status_code=status_code,error=error,bytes=len(data),path=str(path.relative_to(ROOT)),sha256=sha(path),license=license,redistribution="local_only_pending_or_source_license",started_at=started,finished_at=now(),recovery_chain=False,headers=headers)
 append("http_ledger.jsonl",r);event(TASK,"source_http",**r);raw_manifest()
 return r
def get(url,kind,reason,phase="design",license=None):
 # One lock covers reservation, all budget and retry checks, physical request,
 # plan and completion append. UUID IDs also remain unique across workers.
 lock=OUT/"http_acquisition.lock"
 if not lock.exists():write(TASK,str(lock.relative_to(ROOT)),"")
 with lock.open("a+") as handle:
  fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
  event(TASK,"source_acquisition_lock_acquired",lock_path=str(lock.relative_to(ROOT)),worker="C-SCOUT")
  try:return _get_locked(url,kind,reason,phase=phase,license=license)
  finally:fcntl.flock(handle.fileno(),fcntl.LOCK_UN)

def design_figures():
 identities=json.load(open(ROOT/"outputs/task016-p6/v1/source_identity_checks.json"));selected=[]
 for pid,keys in [("PMC11480083",["Fig2_HTML"]),("PMC9700910",["Fig1_HTML","Fig9_HTML","MOESM1_ESM"])]:
  r=next(x for x in identities if x["pmcid"]==pid)
  for u in r["media_urls"]:
   if any(k in u for k in keys):
    selected.append(dict(pmcid=pid,object=get(u.replace("s3://pmc-oa-opendata/","https://pmc-oa-opendata.s3.amazonaws.com/"),"attachment","independent design source graph / NMR SI verification",license=r["license"]),metadata_verified=False,evidence_eligible=False,phase="design",historical_development_exposed=True))
 save("design_figure_intake.json",selected);print(json.dumps(selected,indent=2))

def query_plan(round_number):
 if round_number not in (1,2):raise ValueError("bounded rounds 1/2")
 scope="C-E01-scope-bank-v1";base="https://www.ebi.ac.uk/europepmc/webservices/rest/"
 if round_number==1:
  keywords=[
   '("C-glycosyltransferase" OR "C-glucosyltransferase") AND (flavone OR "gallic acid" OR flavonol) AND OPEN_ACCESS:Y',
   '("GtUF6CGT" OR "UGT708" OR "TcCGT" OR "MiCGT") AND OPEN_ACCESS:Y',
   '("C-glycosylation") AND (chrysin OR acacetin OR diosmetin OR tricin OR isorhamnetin) AND OPEN_ACCESS:Y',
   '(flavone OR apigenin OR luteolin OR chrysin) AND (C-glycosyltransferase OR C-glucosyltransferase) AND OPEN_ACCESS:Y',
   '("gallic acid" OR "methylgallic") AND (C-glucosylation OR C-glycosyltransferase) AND OPEN_ACCESS:Y',
   '(flavone) AND ("direct C-glycosylation" OR "6-C-glucoside") AND OPEN_ACCESS:Y',
  ];bibliographic="C glycosyltransferase flavone flavonol gallic acid substrate promiscuity";citations=["PMC6036675","PMC11053098"]
 else:
  keywords=[
   '("C-glycosyltransferase") AND ("substrate scope" OR "substrate specificity" OR promiscuous) AND OPEN_ACCESS:Y',
   '("C-glycosylation") AND (flavonol OR kaempferol OR quercetin OR myricetin) AND OPEN_ACCESS:Y',
   '("C-glycosyltransferase") AND (Gentiana OR Trollius OR mango OR Mangifera) AND OPEN_ACCESS:Y',
   '(gallic OR "hydroxybenzoic acid" OR "methylgallic acid") AND (C-glycoside OR C-glucoside OR C-glucosylation) AND OPEN_ACCESS:Y',
   '(flavone OR flavonol) AND (C-glycosylation OR C-glucosylation) AND (engineering OR characterization) AND OPEN_ACCESS:Y',
   '("C6" OR "6-C") AND (glycosyltransferase OR glucosyltransferase) AND OPEN_ACCESS:Y',
  ];bibliographic="enzymatic direct C glucosylation methylated flavones flavonols phenolic acid";citations=["PMC9700910","PMC6036675","PMC11053098"]
 rr=[]
 for kw in keywords:rr.append(dict(query=kw,route="EuropePMC_keyword_search",database="EuropePMC",url=base+"search?"+urllib.parse.urlencode(dict(query=kw,format="json",resultType="core",pageSize=100))))
 rr.append(dict(query=bibliographic,route="Crossref_bibliographic_search",database="Crossref",url="https://api.crossref.org/works?"+urllib.parse.urlencode({"query.bibliographic":bibliographic,"rows":80})))
 identity=json.loads((OUT/"E01/design_independent_qualification.json").read_text())["source_identity"]
 for pid in citations:
  verified=next(r for r in identity if r["pmcid"]==pid)
  pmid=verified["field_checks"]["pmid"]["authoritative_values"][0]["value"]
  rr.append(dict(query="forward citations of "+pid+" (MED/"+str(pmid)+")",route="EuropePMC_citation_chase",database="EuropePMC",url=base+"MED/"+str(pmid)+"/citations?"+urllib.parse.urlencode(dict(format="json",pageSize=100))))
 for i,r in enumerate(rr):r.update(query_id=f"C-E01-R{round_number}-Q{i+1:02d}",family="C",scope_id=scope,reason="post-freeze fresh source metadata discovery; historical sources excluded; no chemistry eligibility assumed",max_pages=1,max_objects=100)
 return dict(task=TASK,epoch_id="C-E01",round_id=f"C-R{round_number}",queries=rr,preregistered_at=now())
def discovery_round(round_number):
 require_fresh_scope()
 plan=query_plan(round_number);plan.update(scope_manifest_sha256=require_fresh_scope(),scope_ids=[r["template_id"] for r in json.loads((OUT/"E01/scope_bank.json").read_text())]);planpath=f"E01/fresh/R{round_number}/query_plan.json"
 if (OUT/planpath).exists():raise RuntimeError("ROUND_ALREADY_STARTED; resume requires explicit plan handling")
 save(planpath,plan)
 history=rows(ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl")
 historical={t for r in history for t in r.get("source_tokens",[])}
 executions=[];discoveries=[]
 for q in plan["queries"]:
  raw=get(q["url"],"discovery","pre-registered "+q["query_id"],phase="fresh")
  data=None
  if raw["status"]=="available":
   try:data=json.loads((ROOT/raw["path"]).read_text())
   except Exception:pass
  if data:
   rr=data.get("resultList",{}).get("result",[]) if q["route"]=="EuropePMC_keyword_search" else data.get("message",{}).get("items",[]) if q["route"]=="Crossref_bibliographic_search" else data.get("citationList",{}).get("citation",[])
  else:rr=[]
  dedup={};hist_count=0
  for i,r in enumerate(rr):
   pid=r.get("pmcid");doi=r.get("doi") or r.get("DOI");rid=pid or doi or str(r.get("id")) or str(i)
   if rid in dedup:continue
   title=r.get("title") or r.get("articleTitle")
   if isinstance(title,list):title=" ".join(title)
   hist=bool(("article:"+pid if pid else None) in historical or ("doi:"+str(doi).lower() if doi else None) in historical)
   disposition="rejected" if hist else "metadata_only"
   if hist:hist_count+=1
   row=dict(record_id=rid,query_id=q["query_id"],disposition=disposition,source_hint=dict(pmcid=pid,doi=doi,pmid=r.get("pmid") or (r.get("id") if r.get("source")=="MED" else None),title=title,record=r),metadata_only=True,evidence_eligible=False,historical_source_exposed=hist,reason="historical source closure; design only" if hist else "fresh metadata-only source hint pending independent identity and chemical extraction",raw_pointer=dict(path=raw["path"],sha256=raw["sha256"]),discovered_at=now(),scope_bank_manifest_sha256=sha(OUT/"E01/scope_manifest.json"))
   dedup[rid]=row
  discoveries.extend(dedup.values())
  executions.append(dict(query_id=q["query_id"],status="executed",returned_count=len(rr),deduplicated_count=len(dedup),pending_identity_count=len(dedup)-hist_count,admitted=0,deferred=0,rejected=hist_count,metadata_only=len(dedup)-hist_count,new_closure_groups=0,raw_pointer=raw,finished_at=now()))
  save_rows(f"E01/fresh/R{round_number}/query_execution.jsonl",executions);save_rows(f"E01/fresh/R{round_number}/source_dispositions.jsonl",discoveries)
  print(json.dumps(dict(query_id=q["query_id"],http_status=raw["status_code"],returned=len(rr),unique=len(dedup),historical=hist_count)),flush=True)
 from scripts.task016_p7_source_harness import validate_query_accounting
 audit=validate_query_accounting(plan,executions,discoveries);save(f"E01/fresh/R{round_number}/query_audit.json",audit)
 save(f"E01/fresh/R{round_number}/round_manifest.json",dict(task=TASK,epoch_id="C-E01",family="C",round_id=f"C-R{round_number}",complete=False,query_complete=True,routes=audit["routes"],new_qualified_closure_groups=0,pending_chemical_disposition=True,scope_manifest_sha256=sha(OUT/"E01/scope_manifest.json"),metadata_only_count=sum(r["disposition"]=="metadata_only" for r in discoveries),historical_rejected=sum(r["disposition"]=="rejected" for r in discoveries),raw_query_audit=audit))
 print(json.dumps(audit))

def resolve_hints(round_number):
 require_fresh_scope()
 import re
 folder=OUT/f"E01/fresh/R{round_number}";discovered=rows(folder/"source_dispositions.jsonl")
 if (folder/"identifier_resolution_plan.json").exists():raise RuntimeError("identifier resolution plan already executed; resume explicitly")
 selected={}
 for r in discovered:
  h=r["source_hint"];title=h.get("title") or ""
  if r["disposition"]!="metadata_only" or h.get("pmcid"):continue
  if not re.search(r"C[- ](?:glycosyl|glucosyl)|CGT|UGT708|gallic acid|[Cc]arbon.*glycosyl",title,re.I) or re.search(r"review|perspective|overview|bibliometric|clinical",title,re.I):continue
  key=h.get("doi") or h.get("pmid")
  if key:selected.setdefault(str(key),r)
 plans=[]
 for key,r in selected.items():
  h=r["source_hint"];query='DOI:"'+str(h["doi"]).replace('"','')+'"' if h.get("doi") else 'EXT_ID:'+str(h["pmid"])+' AND SRC:MED'
  plans.append(dict(record_id=r["record_id"],identifier=key,query=query,url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=query,format="json",resultType="core",pageSize=10)),metadata_only=True,evidence_eligible=False))
 save(f"E01/fresh/R{round_number}/identifier_resolution_plan.json",dict(task=TASK,epoch_id="C-E01",registered_at=now(),scope_manifest_sha256=require_fresh_scope(),plans=plans))
 save_rows(f"E01/fresh/R{round_number}/source_dispositions_initial.jsonl",discovered)
 historical={t for r in rows(ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl") for t in r.get("source_tokens",[])};resolved=[]
 for p in plans:
  raw=get(p["url"],"metadata","post-freeze original identifier resolution "+str(p["identifier"]),phase="fresh");rr=[]
  if raw["status"]=="available":
   try:rr=json.loads((ROOT/raw["path"]).read_text()).get("resultList",{}).get("result",[])
   except ValueError:pass
  primary=next((v for v in rr if v.get("pmcid")),rr[0] if rr else None)
  result=dict(p,raw_pointer=raw,matched=primary is not None,authoritative_metadata=primary,source_identity_verified=False,chemical_extracted=False,finished_at=now())
  resolved.append(result)
  for r in discovered:
   h=r["source_hint"]
   if str(h.get("doi") or h.get("pmid"))!=p["identifier"]:continue
   r["identifier_resolution"]=result
   if primary:
    for k in ("pmcid","doi","pmid"):
     value=primary.get(k) or (primary.get("id") if k=="pmid" and primary.get("source")=="MED" else None)
     if value:h[k]=value
    pid=h.get("pmcid");doi=h.get("doi");hist=bool(("article:"+pid if pid else None) in historical or ("doi:"+str(doi).lower() if doi else None) in historical)
    if hist:r.update(disposition="rejected",historical_source_exposed=True,reason="resolved original source intersects historical design/development source closure")
  save(f"E01/fresh/R{round_number}/identifier_resolution_results.json",resolved)
  save_rows(f"E01/fresh/R{round_number}/source_dispositions.jsonl",discovered)
 executions=rows(folder/"query_execution.jsonl")
 for e in executions:
  associated=[r for r in discovered if r["query_id"]==e["query_id"]]
  for d in ("admitted","deferred","rejected","metadata_only"):e[d]=sum(r["disposition"]==d for r in associated)
  e["pending_identity_count"]=e["metadata_only"]+e["deferred"]
 save_rows(f"E01/fresh/R{round_number}/query_execution.jsonl",executions)
 from scripts.task016_p7_source_harness import validate_query_accounting
 audit=validate_query_accounting(json.loads((folder/"query_plan.json").read_text()),executions,discovered);save(f"E01/fresh/R{round_number}/query_audit.json",audit)
 print(json.dumps(dict(identifier_hints=len(plans),metadata_matched=sum(r["matched"] for r in resolved),fresh_sources_resolved=sum(bool(r.get("authoritative_metadata",{}).get("pmcid")) for r in resolved if r.get("authoritative_metadata")))))

def acquire_selected(round_number):
 require_fresh_scope()
 folder=OUT/f"E01/fresh/R{round_number}"
 discoveries=rows(folder/"source_dispositions.jsonl")
 if (folder/"article_plan.json").exists():raise RuntimeError("article plan already executed; resume explicitly")
 import re
 hints={}
 unresolved_ids=[]
 for r in discoveries:
  if r["disposition"]!="metadata_only":continue
  h=r["source_hint"];pid=h.get("pmcid");title=h.get("title") or ""
  if isinstance(title,list):title=" ".join(title)
  if not re.search(r"C[- ](?:glycosyl|glucosyl)|CGT|UGT708|gallic acid|[Cc]arbon.*glycosyl",title,re.I):continue
  if re.search(r"review|perspective|overview|bibliometric|clinical",title,re.I):continue
  if pid:hints.setdefault(pid,r)
  else:unresolved_ids.append(r)
 already={r["pmcid"] for r in rows(OUT/"fresh_article_acquisition.jsonl")}
 chosen=[r for pid,r in hints.items() if pid not in already][:60]
 plan=dict(task=TASK,family="C",epoch_id="C-E01",round_id=f"C-R{round_number}",registered_at=now(),source_scope_manifest_sha256=require_fresh_scope(),maximum_article_versions=120,selection="metadata title C-glycosyl/CGT/UGT708 primary hints only; no structure/model screening",chosen=[dict(pmcid=r["source_hint"]["pmcid"],query_id=r["query_id"],metadata_hint=r["source_hint"]) for r in chosen],unresolved_id_hints=len(unresolved_ids),previous_acquired=len(already),metadata_only=True,evidence_eligible=False)
 save(f"E01/fresh/R{round_number}/article_plan.json",plan)
 records=[]
 for r in chosen:
  pid=r["source_hint"]["pmcid"];meta=get(f"https://pmc-oa-opendata.s3.amazonaws.com/{pid}.1/{pid}.1.json","metadata","fresh authoritative metadata for independently reviewed source "+pid,phase="fresh")
  m=None
  if meta["status"]=="available":
   try:m=json.loads((ROOT/meta["path"]).read_text())
   except ValueError:pass
  xml=None;lic=m.get("license_code") if m else None
  if m and str(lic).startswith("CC") and not m.get("is_retracted"):
   u=m.get("xml_url","")
   if u.startswith("s3://pmc-oa-opendata/"):u=u.replace("s3://pmc-oa-opendata/","https://pmc-oa-opendata.s3.amazonaws.com/")
   if u.startswith("https://pmc-oa-opendata.s3.amazonaws.com/"):xml=get(u,"article_version","fresh original source for independent chemical extraction after C scope freeze",phase="fresh",license=lic)
  item=dict(pmcid=pid,source_hint=r["source_hint"],metadata=meta,xml=xml,license=lic,media_urls=m.get("media_urls",[]) if m else [],status="downloaded_pending_identity_and_chemical_disposition" if xml and xml["status"]=="available" else "source_access_or_license_deferred",source_identity_verified=False,evidence_eligible=False,scope_manifest_sha256=require_fresh_scope(),download_completed_at=now(),read_scope_design_corpus=False,source_identity_verifier_pending="A3")
  records.append(item);append("fresh_article_acquisition.jsonl",item);save(f"E01/fresh/R{round_number}/article_acquisition.json",records)
  print(json.dumps(dict(pmcid=pid,status=item["status"],license=lic)),flush=True)
 save(f"E01/fresh/R{round_number}/unresolved_id_hints.json",unresolved_ids)
 save(f"E01/fresh/R{round_number}/article_intake_summary.json",dict(planned=len(chosen),terminal=len(records),downloaded=sum(x["xml"] is not None and x["xml"]["status"]=="available" for x in records),source_access_deferred=sum(x["xml"] is None or x["xml"]["status"]!="available" for x in records),pending_independent_chemical_admission=True,remaining_metadata_hints=len(hints)-len(chosen),unresolved_id_hints=len(unresolved_ids)))
 print(json.dumps(dict(articles=len(records),downloaded=sum(x["xml"] is not None and x["xml"]["status"]=="available" for x in records),unresolved_id_hints=len(unresolved_ids))))
if __name__=="__main__":
 if sys.argv[1]=="design_figures":design_figures()
 elif sys.argv[1]=="round":discovery_round(int(sys.argv[2]))
 elif sys.argv[1]=="resolve":resolve_hints(int(sys.argv[2]))
 elif sys.argv[1]=="acquire":acquire_selected(int(sys.argv[2]))
