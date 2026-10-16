"""P7 SS scout: immutable official HTTP acquisition with preregistration."""
import argparse, hashlib, json, sys, time, re, urllib.request, urllib.parse, urllib.error
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write,event
TASK="TASK-016-P7"; OUT=ROOT/"outputs/task016-p7/v1/SS"; RAW=ROOT/"data/raw/task016-p7/SS"
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):
    digest=hashlib.sha256()
    with Path(p).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):digest.update(chunk)
    return digest.hexdigest()
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []
def save(name,value):write(TASK,str((OUT/name).relative_to(ROOT)),json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def save_rows(name,values):write(TASK,str((OUT/name).relative_to(ROOT)),"".join(json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n" for v in values))
def append(name,row):save_rows(name,rows(OUT/name)+[row])
def require_acquisition_phase(phase,epoch_id="SS-E01",scope_id=None):
    """Gate real fresh I/O from authoritative epoch registration, never old scope presence."""
    if not isinstance(phase,str) or phase not in {"design","fresh"}:
        evidence={"epoch_id":epoch_id,"phase":phase,"scope_id":scope_id,"helper_sha256":sha(Path(__file__))}
        closed=ROOT/f"outputs/task016-p7/v1/epochs/{epoch_id}/incomplete_decision.json"
        if closed.is_file():
            evidence["closed_decision_path"]=str(closed.relative_to(ROOT));evidence["closed_decision_sha256"]=sha(closed)
        event(TASK,"SS_acquisition_phase_gate_rejected",reason="SS_UNKNOWN_ACQUISITION_PHASE",**evidence)
        raise RuntimeError("SS_UNKNOWN_ACQUISITION_PHASE")
    if phase == "design":
        return dict(epoch_id=epoch_id,phase=phase,fresh_gate_required=False)
    evidence={"epoch_id":epoch_id,"phase":phase,"scope_id":scope_id}
    def reject(reason):
        event(TASK,"SS_fresh_acquisition_gate_rejected",reason=reason,**evidence)
        raise RuntimeError(reason)
    if not re.fullmatch(r"SS-E[0-9]+",epoch_id):reject("SS_INVALID_EPOCH_ID")
    ledger=ROOT/"outputs/task016-p7/v1/epoch_ledger.jsonl"
    if not ledger.exists():reject("SS_EPOCH_REGISTRY_MISSING")
    evidence["epoch_ledger_path"]=str(ledger.relative_to(ROOT));evidence["epoch_ledger_sha256"]=sha(ledger)
    entries=[r for r in rows(ledger) if r.get("epoch_id")==epoch_id and r.get("family")=="SS"]
    decision=ROOT/f"outputs/task016-p7/v1/epochs/{epoch_id}/incomplete_decision.json"
    if decision.exists():
        evidence["closed_decision_path"]=str(decision.relative_to(ROOT));evidence["closed_decision_sha256"]=sha(decision)
        closed=json.loads(decision.read_text());evidence["closed_status"]=closed.get("status")
        if closed.get("epoch_id")!=epoch_id or closed.get("family")!="SS":reject("SS_CLOSED_DECISION_IDENTITY_MISMATCH")
        wrapper=closed.get("permanent_exposure_manifest",{})
        if wrapper.get("path") and (ROOT/wrapper["path"]).is_file():
            evidence["permanent_exposure_manifest_path"]=wrapper["path"]
            evidence["permanent_exposure_manifest_sha256"]=sha(ROOT/wrapper["path"])
        reject("SS_CLOSED_EPOCH_FRESH_FORBIDDEN")
    if any(r.get("event_type")=="epoch_incomplete_decision" or r.get("status") in {"development_epoch_incomplete","complete","closed","withdrawn","cancelled"} for r in entries):reject("SS_REGISTERED_CLOSED_EPOCH_FRESH_FORBIDDEN")
    g4=[r for r in entries if r.get("stage")=="G4_SCOPE_FREEZE" and r.get("status")=="active"]
    g5=[r for r in entries if r.get("stage")=="G5_FRESH_HOLDOUT_ACQUIRE" and r.get("status")=="active"]
    if not g4 or not g5:reject("SS_NEW_EPOCH_G4_G5_NOT_REGISTERED")
    from scripts.task016_p7_orchestrate import verify_stage_chain
    for stage,entry in [("G4",g4[-1]),("G5",g5[-1])]:
        path=ROOT/entry["stage_manifest_path"];evidence[stage+"_manifest_path"]=entry["stage_manifest_path"]
        evidence[stage+"_manifest_sha256"]=sha(path) if path.is_file() else None
        if not path.is_file() or sha(path)!=entry["stage_manifest_sha256"]:reject("SS_REGISTERED_STAGE_SHA_MISMATCH")
        try:verify_stage_chain(path,entry["stage_manifest_sha256"])
        except Exception:reject("SS_REGISTERED_STAGE_CHAIN_INVALID")
        manifest=json.loads(path.read_text())
        if manifest.get("epoch_id")!=epoch_id or manifest.get("family")!="SS":reject("SS_REGISTERED_STAGE_EPOCH_MISMATCH")
    scope_path=g4[-1].get("scope_manifest_path");scope_sha=g4[-1].get("scope_manifest_sha256")
    if not scope_path or not scope_sha or not (ROOT/scope_path).is_file() or sha(ROOT/scope_path)!=scope_sha:reject("SS_NEW_EPOCH_SCOPE_BINDING_INVALID")
    scope=json.loads((ROOT/scope_path).read_text())
    if scope.get("epoch_id")!=epoch_id or scope.get("family")!="SS":reject("SS_OLD_SCOPE_CANNOT_AUTHORIZE_NEW_EPOCH")
    if g5[-1].get("scope_manifest_sha256")!=scope_sha:reject("SS_G5_SCOPE_BINDING_MISMATCH")
    event(TASK,"SS_fresh_acquisition_gate_passed",scope_manifest_path=scope_path,scope_manifest_sha256=scope_sha,**evidence)
    return evidence

def request(url,role,reason,phase="design",scope_id=None,route="official_direct",max_bytes=80*1024*1024,http_method="GET",request_body=None,epoch_id="SS-E01"):
    require_acquisition_phase(phase,epoch_id,scope_id)
    budget_root=ROOT/"outputs/task016-p7/v1/SS"
    previous=[r for p in budget_root.rglob("http_ledger.jsonl") if "superseded" not in p.parts for r in rows(p)]
    if len(previous)>=2500 or sum(r["bytes"] for r in previous)>=2*1024**3:raise RuntimeError("SS_HTTP_BUDGET_EXCEEDED")
    if role in {"xml","original_pdf"} and sum(r["role"] in {"xml","original_pdf"} for r in previous)>=120:raise RuntimeError("SS_ARTICLE_VERSION_BUDGET_EXCEEDED")
    if role=="attachment" and sum(r["role"]=="attachment" for r in previous)>=200:raise RuntimeError("SS_ATTACHMENT_BUDGET_EXCEEDED")
    if not isinstance(max_bytes,int) or max_bytes<=0 or max_bytes>2*1024**3-sum(r["bytes"] for r in previous)-1:raise RuntimeError("OBJECT_RESERVATION_EXCEEDS_SS_BYTE_BUDGET")
    attempts=sum(r["url"]==url for r in previous)
    if attempts>=2:raise RuntimeError("URL_ATTEMPT_LIMIT")
    qid=f"SS-Q{len(rows(OUT/'query_plan.jsonl'))+1:05d}"
    append("query_plan.jsonl",dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),query=url,database=url.split("/")[2],scope_id=scope_id,family="SS",epoch_id=epoch_id,phase=phase,reason=reason,max_pages=1,max_objects=1,maximum_bytes=max_bytes,route=route,http_method=http_method,request_body_sha256=hashlib.sha256(request_body).hexdigest() if request_body else None,request_body_utf8=request_body.decode("utf-8") if request_body else None,registered_at=now()))
    if http_method not in {"GET","POST"} or (http_method=="POST" and request_body is None):raise RuntimeError("INVALID_READONLY_QUERY_METHOD")
    started=now(); status=None; data=b""; error=None; headers={}
    try:
        req=urllib.request.Request(url,data=request_body,method=http_method,headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 (public scientific research)",**({"Content-Type":"application/json"} if request_body else {})})
        with urllib.request.urlopen(req,timeout=40) as res:status=res.status;headers={k:v for k,v in res.headers.items() if k.lower() in {"content-type","etag","last-modified","content-length"}};data=res.read(max_bytes+1)
        if len(data)>max_bytes:raise RuntimeError("OBJECT_TOO_LARGE")
        declared_md5=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("md5",[None])[0]
        if declared_md5 and hashlib.md5(data).hexdigest()!=declared_md5:raise RuntimeError("OFFICIAL_RAW_MD5_MISMATCH")
    except urllib.error.HTTPError as exc:status=exc.code;data=exc.read();error=str(exc)
    except Exception as exc:error=f"{type(exc).__name__}: {exc}"
    path=RAW/(hashlib.sha256(url.encode()).hexdigest()+f".attempt-{attempts+1}.{role}")
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise RuntimeError("IMMUTABLE_PATH_EXISTS")
    path.write_bytes(data)
    declared_md5=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get("md5",[None])[0]
    event(TASK,"raw_bytes",path=str(path.relative_to(ROOT)),sha256=sha(path),bytes=len(data),role=role,phase=phase)
    record=dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),url=url,http_method=http_method,request_body_sha256=hashlib.sha256(request_body).hexdigest() if request_body else None,role=role,route=route,epoch_id=epoch_id,phase=phase,started_at=started,finished_at=now(),status_code=status,bytes=len(data),path=str(path.relative_to(ROOT)),sha256=sha(path),headers=headers,error=error,official_md5_verified=(hashlib.md5(data).hexdigest()==declared_md5) if declared_md5 else None)
    append("http_ledger.jsonl",record)
    append("query_execution.jsonl",dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),executed_at=now(),status="terminal",status_code=status,error=error,returned_objects=1 if status==200 else 0,metadata_only=role=="metadata",admitted=0,deferred=1 if status==200 else 0,rejected=1 if status!=200 else 0))
    return record
def design_sources():
    sources=json.loads((ROOT/"outputs/task016-p6/v1/source_identity_checks.json").read_text())
    wanted=["PMC13084081","PMC9706480","PMC12120870"]
    p3=rows(ROOT/"outputs/task016-p3/v1/article_acquisition_manifest.json") if False else json.loads((ROOT/"outputs/task016-p3/v1/round3_article_acquisition_manifest.json").read_text())
    out=[]
    for pmcid in wanted:
        prior=next((r for r in sources if r["pmcid"]==pmcid),None)
        if prior:
            xml=prior["xml"];append("reused_files.jsonl",dict(path=xml["path"],sha256=sha(ROOT/xml["path"]),phase="design",pmcid=pmcid,historical_development_exposure=True))
            meta=request(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.json","metadata","authoritative source identity metadata, independent verifier pending")
            urls=prior.get("media_urls",[])
        else:
            meta=request(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.json","metadata","historical article design metadata; independent verifier pending")
            if meta["status_code"]!=200:out.append(dict(pmcid=pmcid,meta=meta,disposition="identity_deferred"));continue
            m=json.loads((ROOT/meta["path"]).read_text())
            print("METADATA KEYS",pmcid,list(m))
            xmlurl=m.get("xml",{}).get("url") if isinstance(m.get("xml"),dict) else m.get("xml")
            urls=m.get("files",[])
            xml=request(f"https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.xml","xml","historical fulltext for design")
        record=dict(pmcid=pmcid,metadata=meta,xml=xml,historical_development_exposure=True,evidence_eligible=False,pending_verifier="A3",attachments=[])
        # media URLs supplied by official article metadata or frozen official source.
        if not urls and meta["status_code"]==200:
            m=json.loads((ROOT/meta["path"]).read_text());urls=[v for k,v in m.items() if isinstance(v,str) and v.startswith("s3://")]
        for u in urls:
            if isinstance(u,dict):u=u.get("url","")
            if not isinstance(u,str):continue
            if u.startswith("s3://pmc-oa-opendata/"):u="https://pmc-oa-opendata.s3.amazonaws.com/"+u.split("s3://pmc-oa-opendata/",1)[1]
            if (pmcid=="PMC13084081" and any(f in u for f in ["gr2.jpg","mmc1.pdf","mmc2.xlsx"])) or (pmcid=="PMC12120870" and any(f in u for f in ["g002.jpg","g003.jpg","s001.pdf"])):
                record["attachments"].append(request(u,"attachment","SS design structural figure/SI"))
        out.append(record)
    save("design_source_intake.json",out)
    manifest("A2_SS_Source_Scout",["outputs/task016-p6/v1/source_identity_checks.json"],["design_source_intake.json","query_plan.jsonl","query_execution.jsonl","http_ledger.jsonl","reused_files.jsonl"])
def pubchem(names):
    records=[]
    for name in names:
        base="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"+urllib.parse.quote(name,safe="")
        prop=request(base+"/property/Title,IUPACName,MolecularFormula,InChI,InChIKey,IsomericSMILES/JSON","structure_database","source-named identity lookup; no structure admissibility assumed",route="PubChem_identity")
        syn=request(base+"/synonyms/JSON","metadata","source-name synonyms to verify identity chain",route="PubChem_identity")
        records.append(dict(name=name,properties=prop,synonyms=syn,evidence_eligible=False,structure_complete=False))
        time.sleep(.2)
    save("pubchem_design_intake.json",records)
def manifest(role,inputs,outputs):
    save(role+"_manifest.json",dict(agent_role=role,task_id=TASK,epoch_id="SS-E01",at=now(),input_sha256={p:sha(ROOT/p) for p in inputs},output_sha256={str(OUT/p):sha(OUT/p) for p in outputs if (OUT/p).exists()},read_holdout=False,read_model_outcomes=False,evidence_eligible_authority=False))
def inspect():
    for rec in json.loads((OUT/"design_source_intake.json").read_text()):
        p=ROOT/rec["xml"]["path"]
        try:root=ET.fromstring(p.read_bytes())
        except Exception as exc:print(rec["pmcid"],"XML ERROR",exc);continue
        print("\nARTICLE",rec["pmcid"],"XML",p)
        for ix, el in enumerate(root.findall(".//body//p")):
            text=" ".join("".join(el.itertext()).split())
            if any(k in text.lower() for k in ["hesperetin","astragalin","flavonoid glycoside","quercetin-3","kaempferol-3","acacetin","rhamnosylat"]): print(f"body//p[{ix+1}]",text)
        for f in root.findall(".//fig"):
            print("FIG",f.get("id")," ".join("".join(f.itertext()).split())[:600])
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("mode");parser.add_argument("names",nargs="*");args=parser.parse_args()
    if args.mode=="design_sources":design_sources()
    elif args.mode=="pubchem":pubchem(args.names)
    elif args.mode=="inspect":inspect()
