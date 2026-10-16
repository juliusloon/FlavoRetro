"""Prospective G5 exposure time strata and complete-round documentary checks.

Source discovery/access is not scientific admission. Own post-G5 evaluation
receipts stay permanent but are not retroactively classified as prior design.
All actual G7 panels still require the pinned v4 final panel gate and its floor.
"""
from __future__ import annotations
import copy, hashlib, json, re, uuid, fcntl
from datetime import datetime, timezone
from pathlib import Path
from scripts.operate import write, ROOT
from scripts.task016_p7_orchestrate import ContractError, verify_stage_chain, sha_json
from scripts.task016_p7_source_alias_closure import closure_tokens, assert_fresh
from scripts.task016_p7_structure_harness import reconcile
from scripts.task016_p7_closure_harness import canonical
from scripts.task016_p7_named_exposure_gate_v4 import validate_current_named_exposure_review

TASK="TASK-016-P7"
SCHEMA="p7-full-qualification-v1"
POLICY_SHA="3dca11316e8dca06c6dea7c4a9a1f33888c2a209b3835de78030ac75aa035d03"
R8_EXCLUDED={"PMC13387883","PMC5517534","article:PMC13387883","article:PMC5517534","doi:10.1111/pbi.70674","doi:10.1038/s41598-017-06453-z"}
TERMINAL={"qualified","deferred","rejected"}
def require(value,message):
    if not value: raise ContractError(message)
def now(): return datetime.now(timezone.utc).isoformat()
def stamp(value):
    try: result=datetime.fromisoformat(value.replace("Z","+00:00"))
    except (ValueError,TypeError,AttributeError): raise ContractError("invalid actual timezone-aware timestamp") from None
    require(result.tzinfo is not None and result<=datetime.now(timezone.utc),"timestamp is naive or in the future")
    return result
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bound(pointer,root=ROOT):
    require(isinstance(pointer,dict) and isinstance(pointer.get("path"),str),"immutable pointer required")
    path=(Path(root)/pointer["path"]).resolve()
    require(path.is_relative_to(Path(root).resolve()) and path.is_file(),"bound file missing/outside root")
    require(digest(path)==pointer.get("sha256"),"bound file SHA drift")
    return path
def load(pointer,root=ROOT): return json.loads(bound(pointer,root).read_text())
def pointer(path,root=ROOT):
    path=Path(path)
    if not path.is_absolute():path=Path(root)/path
    require(path.resolve().is_relative_to(Path(root).resolve()),"pointer outside root")
    return {"path":str(path.relative_to(root)),"sha256":digest(path)}
def persist(path,value,root=ROOT):
    path=Path(root)/path
    require(not path.exists(),"immutable output already exists")
    require(path.resolve().is_relative_to(Path(ROOT).resolve()),"operate write must remain in workspace")
    write(TASK,str(path),json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return pointer(path,root)
def _hash_map(values,root):
    require(isinstance(values,dict) and values,"nonempty immutable file universe required")
    for p,v in values.items():bound({"path":p,"sha256":v},root)
def _role(ptr,role,epoch,root,allow_pending=False):
    obj=load(ptr,root)
    require(obj.get("task")==TASK and obj.get("agent_role")==role and obj.get("epoch_id")==epoch,"role task/responsibility/epoch mismatch")
    stamp(obj.get("timestamp"))
    require(obj.get("approval_type")=="agent_delegated" and obj.get("human_reviewed") is False,"role attribution")
    require(type(obj.get("read_holdout")) is bool and obj.get("read_model_outcome") is False,"role read boundary")
    require(obj.get("errors")==[],"role execution errors remain")
    counts=obj.get("counts")
    require(isinstance(counts,dict) and all(type(counts.get(k)) is int and counts[k]>=0 for k in ("processed","passed","rejected","pending")),"role counts schema")
    require(counts["processed"]==counts["passed"]+counts["rejected"]+counts["pending"],"role count conservation")
    if not allow_pending: require(counts["pending"]==0 and obj.get("unprocessed")==[],"role unprocessed work remains")
    else: require(isinstance(obj.get("unprocessed"),list),"role unprocessed list required")
    _hash_map(obj.get("input_manifest_sha"),root)
    outputs=obj.get("output_file_sha",obj.get("output_file_sha256"))
    if "output_file_sha" in obj and "output_file_sha256" in obj:require(obj["output_file_sha"]==obj["output_file_sha256"],"role output aliases conflict")
    _hash_map(outputs,root)
    require(isinstance(obj.get("source_evidence_pointers"),list),"role source pointer list required")
    for p in obj["source_evidence_pointers"]:bound(p,root)
    return obj,outputs
def _evidence(values,root):
    require(isinstance(values,list) and values,"actual evidence pointers required")
    for p in values:bound(p,root)
def _rows(ptr,root):
    path=bound(ptr,root)
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def _exposure_rows(manifest_ptr,root):
    m=load(manifest_ptr,root)
    require(m.get("task")==TASK and m.get("coverage_status")=="inventory_complete_unknown_semantics_retained","exposure inventory coverage not documented")
    _hash_map(m.get("origin_files_sha256"),root)
    _hash_map(m.get("exposure_files_sha256"),root)
    role,outputs=_role(m["coverage_role"],"A0",m["epoch_id"],root)
    require(all(role["input_manifest_sha"].get(p)==v for p,v in m["origin_files_sha256"].items()),"coverage role omits origins")
    rows=[]
    for p,v in m["exposure_files_sha256"].items():
        require(outputs.get(p)==v,"coverage role omits immutable exposure snapshot")
        rows.extend(_rows({"path":p,"sha256":v},root))
    require(len(rows)==m.get("row_count") and rows,"exposure row universe mismatch")
    for row in rows:
        require(type(row.get("development_exposed")) is bool and isinstance(row.get("closure_tokens"),list) and isinstance(row.get("exposure_type"),str),"exposure row schema incomplete")
        if row["development_exposed"] is False:
            require(row["exposure_type"]=="metadata_only" and row.get("scientific_content_read") is False,"chemical exposure cannot masquerade as metadata")
        closure_tokens(row)
    return rows
def _supplements(values,root):
    require(isinstance(values,list),"late-prior-design list required, even when empty")
    rows=[]
    for ptr in values:
        for row in _rows(ptr,root):
            require(row.get("development_exposed") is True and row.get("exposure_type") in ("late_prior_design","historical_design","screen_only"),"late supplement must retain prior/design exclusion")
            require(isinstance(row.get("closure_tokens"),list),"late-prior closure tokens required")
            rows.append(row)
    return rows
def _aliases(source):
    aliases=source.get("official_aliases")
    require(isinstance(aliases,list) and aliases and len(aliases)==len(set(aliases)),"explicit source aliases required")
    for t in aliases:
        require(isinstance(t,str) and re.fullmatch(r"(?:article:PMC[1-9][0-9]*|pmid:[1-9][0-9]*|doi:10\.[0-9]{4,9}/\S+)",t),"malformed explicit source alias")
    require(all(not token.startswith("doi:") or token=="doi:"+token[4:].lower() for token in aliases),"official DOI aliases must be canonical lowercase")
    return set(aliases)
def _state_epoch_open(spec,root):
    state=load(spec["epoch_state"],root)
    require(state.get("epoch_id")==spec["epoch_id"] and state.get("family","SS")==spec["family"],"epoch state mismatch")
    require(state.get("status")=="active" or str(state.get("status","")).startswith("G4_frozen"),"epoch is not active and frozen")
    pref=spec["epoch_ledger_prefix"];p=(Path(root)/pref["path"]).resolve()
    require(p.is_relative_to(Path(root).resolve()) and p.is_file(),"epoch registry missing")
    with p.open("rb") as f:prefix=f.read(pref["prefix_bytes"])
    require(len(prefix)==pref["prefix_bytes"] and hashlib.sha256(prefix).hexdigest()==pref["prefix_sha256"],"epoch registry original prefix drift")
    rows=[json.loads(s) for s in p.read_text().splitlines() if s.strip()]
    events=[r for r in rows if r.get("epoch_id")==spec["epoch_id"]]
    require(events,"epoch has no registered stage")
    require(not any(r.get("event_type") in {"epoch_incomplete_decision","epoch_invalidation","epoch_invalidated","epoch_closed","epoch_complete"} or r.get("status") in {"development_epoch_incomplete","invalidated","closed","complete","completed"} for r in events),"closed epoch cannot start qualification")
    def same_g4(row):
        digests=[row[k] for k in ("stage_manifest_sha256","manifest_sha256","manifest_sha") if k in row]
        paths=[row[k] for k in ("stage_manifest_path","manifest_path") if k in row]
        return (row.get("task")==TASK and row.get("family")==spec["family"]
                and row.get("stage")=="G4_SCOPE_FREEZE" and bool(digests) and bool(paths)
                and set(digests)=={spec["G4"]["sha256"]}
                and all((Path(root)/v).resolve()==(Path(root)/spec["G4"]["path"]).resolve() for v in paths))
    require(any(same_g4(row) for row in events),"frozen G4 path/SHA not registered consistently")
def _validate_spec(spec,root):
    require(spec.get("task")==TASK and spec.get("schema")==SCHEMA and spec.get("batch_kind")=="full_qualification","full qualification contract required")
    require(spec.get("approval_type")=="agent_delegated" and spec.get("human_reviewed") is False,"contract attribution")
    created=stamp(spec["created_at"])
    _hash_map(spec.get("implementation_files_sha256"),root)
    require(spec["implementation_files_sha256"].get("scripts/task016_p7_full_qualification_harness_v3.py")==digest(Path(root)/"scripts/task016_p7_full_qualification_harness_v3.py"),"actual qualification validator implementation is not pinned")
    policy=load(spec["policy"],root)
    require(spec["policy"]["sha256"]==POLICY_SHA and policy.get("approval_type")=="agent_delegated","prospective policy drift")
    g4=verify_stage_chain(spec["G4"]["path"],spec["G4"]["sha256"],root=Path(root))
    require(g4["stage"]=="G4_SCOPE_FREEZE" and (g4["family"],g4["epoch_id"])==(spec["family"],spec["epoch_id"]),"wrong G4")
    require(stamp(g4["timestamp"])<=created,"contract predates scope freeze")
    _state_epoch_open(spec,root)
    sm=load(spec["scope_manifest"],root);bank=load(spec["scope_bank"],root)
    require(isinstance(sm,dict) and (sm.get("family"),sm.get("epoch_id"))==(spec["family"],spec["epoch_id"]),"scope family/epoch mismatch")
    require(isinstance(bank,list) and bank and all(isinstance(row,dict) for row in bank),"actual immutable scope bank must be a nonempty row list")
    require(all(row.get("template_role")=="scope_template" and isinstance(row.get("scope"),dict)
                and row["scope"].get("family")==spec["family"]
                and isinstance(row.get("template_id"),str) and row["template_id"]
                and isinstance(row.get("scope_sha256"),str) and len(row["scope_sha256"])==64 for row in bank),"scope bank row context")
    require(len({row["template_id"] for row in bank})==len(bank),"duplicate scope bank template IDs")
    require(g4["files"].get(spec["scope_bank"]["path"])==spec["scope_bank"]["sha256"],"G4 does not bind scope bank")
    require(g4["files"].get(spec["scope_manifest"]["path"])==spec["scope_manifest"]["sha256"],"G4 does not bind scope manifest")
    require(sm["scope_bank_sha256"]==spec["scope_bank"]["sha256"],"scope bank physical SHA mismatch")
    require(sm["read_model_outcome"] is False,"scope used model outcome")
    stamp(sm["frozen_at"])
    require(spec["scope_bank_file_sha256"]==spec["scope_bank"]["sha256"] and spec["scope_bank_json_sha256"]==sha_json(bank),"physical and canonical scope digest drift")
    for rel,v in sm["files_sha256"].items():
        path=rel if rel.startswith(("outputs/","scripts/","flavoretro/")) else str(Path(spec["scope_manifest"]["path"]).parent/rel)
        bound({"path":path,"sha256":v},root)
    raw=load(spec["raw_source_universe"],root)
    require(raw.get("task")==TASK and raw.get("scientific_content_read") is False and raw.get("final_structures_provided") is False,"raw-only source universe required")
    sources=raw.get("source_candidates")
    require(isinstance(sources,list) and sources,"pre-read selected-source universe empty")
    ids=[s.get("source_id") for s in sources]
    require(all(isinstance(x,str) and x for x in ids) and len(set(ids))==len(ids) and ids==spec["source_candidate_ids"],"selected-source universe drift")
    require(isinstance(raw.get("metadata_only_dispositions"),list),"metadata dispositions must be separate")
    for src in sources:
        aliases=_aliases(src)
        require(not ({src["source_id"]}|aliases).intersection(R8_EXCLUDED),"R8 screen-only source cannot be reactivated")
        require(src.get("prior_scientific_read") is False,"source previously read or prior exposure unknown")
        require(src.get("raw_status") in ("available","access_pending"),"raw status must remain explicit")
        require(isinstance(src.get("raw_files"),list),"raw file universe missing")
        if src["raw_status"]=="available":_evidence(src["raw_files"],root)
        else:require(src["raw_files"]==[],"access-pending original cannot claim raw availability")
        routes=src.get("planned_original_routes")
        require(isinstance(routes,list) and routes and len(routes)==len(set(routes)),"original/SI acquisition route plan missing")
    a3=load(spec["A3_source_results"],root);role,outputs=_role(spec["A3_role"],"A3",spec["epoch_id"],root,allow_pending=True)
    require(outputs.get(spec["A3_source_results"]["path"])==spec["A3_source_results"]["sha256"],"A3 role does not bind source results")
    require(role["input_manifest_sha"].get(spec["raw_source_universe"]["path"])==spec["raw_source_universe"]["sha256"],"A3 omits fixed source universe")
    results=a3.get("sources")
    require(isinstance(results,list) and {r.get("source_id") for r in results}==set(ids) and len(results)==len(ids),"A3 source denominator")
    require(role["counts"]["processed"]==len(ids),"A3 processed denominator")
    for r in results:
        require(r.get("identity_status") in ("verified","deferred","rejected"),"A3 must retain pending/deferred identity")
        if r["identity_status"]=="verified":
            src=next(s for s in sources if s["source_id"]==r["source_id"])
            require(set(r.get("official_aliases",[]))==_aliases(src) and r.get("unresolved_conflicts")==[],"A3 aliases or identity conflict")
            _evidence(r.get("evidence"),root)
    prior=_exposure_rows(spec["prior_exposure_snapshot"],root)
    prior+=_supplements(spec["late_prior_design_files"],root)
    req=load(spec["future_G7_requirement"],root)
    require(req.get("call")=="validate_final_panel" and req.get("validator_path")=="scripts/task016_p7_named_exposure_gate_v4.py" and req.get("permanent_name_record_count")==28 and req.get("production_floor_cannot_be_disabled") is True,"final G7 requirement is not v4 pinned full floor")
    _hash_map(req["implementation_files_sha256"],root)
    _hash_map(req["registry_files_sha256"],root)
    require(spec.get("automatic_admission") is False and spec.get("future_epoch_reuse_allowed") is False,"contract cannot grant automatic or future admission")
    return {"sources":sources,"A3":results,"prior":prior,"scope":sm,"bank":bank}
def freeze_full_qualification_contract(path,spec,*,root=ROOT):
    """Freeze before G5. A3/access-deferred selected sources remain in denominator."""
    spec=copy.deepcopy(spec)
    spec.update(task=TASK,schema=SCHEMA,batch_kind="full_qualification",created_at=now(),approval_type="agent_delegated",human_reviewed=False,automatic_admission=False,future_epoch_reuse_allowed=False)
    bank=load(spec["scope_bank"],root);raw=load(spec["raw_source_universe"],root)
    spec["scope_bank_file_sha256"]=spec["scope_bank"]["sha256"];spec["scope_bank_json_sha256"]=sha_json(bank)
    spec["source_candidate_ids"]=[s["source_id"] for s in raw["source_candidates"]]
    deps=["scripts/task016_p7_full_qualification_harness_v3.py","scripts/task016_p7_orchestrate.py","scripts/task016_p7_source_alias_closure.py","scripts/task016_p7_structure_harness.py"]
    req=load(spec["future_G7_requirement"],root);deps+=list(req["implementation_files_sha256"])
    spec["implementation_files_sha256"]={p:digest(Path(root)/p) for p in sorted(set(deps))}
    _validate_spec(spec,root)
    eventdir=(Path(root)/spec["evaluation_events_directory"]).resolve()
    require(eventdir.is_relative_to(Path(root).resolve()) and not eventdir.exists(),"new isolated evaluation event directory required")
    result=persist(path,spec,root)
    lock=eventdir/".read.lock"
    write(TASK,str(lock),"P7 actual reader serialization lock; not scientific content.\n")
    return result
def validate_full_qualification_contract(contract,*,root=ROOT):
    spec=load(contract,root);meta=_validate_spec(spec,root)
    return {"contract":spec,"meta":meta,"admitted":0,"source_candidates":len(meta["sources"]),"source_identity_pending":sum(r["identity_status"]=="deferred" for r in meta["A3"]),"actual_G7_panel_ready":False}
def _g5(contract,spec,g5,root):
    obj=verify_stage_chain(g5["path"],g5["sha256"],root=Path(root))
    require(obj["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE" and (obj["family"],obj["epoch_id"])==(spec["family"],spec["epoch_id"]),"wrong G5")
    require(obj["input_manifest_sha"]==spec["G4"]["sha256"] and obj["files"].get(contract["path"])==contract["sha256"],"G5 must bind this preregistered contract and G4")
    require(stamp(obj["timestamp"])>=stamp(spec["created_at"]),"G5 before actual contract freeze")
    return obj
def evaluation_events(contract,*,root=ROOT):
    spec=load(contract,root);folder=(Path(root)/spec["evaluation_events_directory"]).resolve()
    require(folder.is_relative_to(Path(root).resolve()),"event directory outside root")
    rows=[]
    if folder.exists():
        for path in sorted(folder.glob("*.json")):
            row=json.loads(path.read_text())
            require(row.get("contract_sha256")==contract["sha256"] and row.get("epoch_id")==spec["epoch_id"] and row.get("batch_id")==spec["batch_id"],"evaluation event belongs to another contract")
            require(row.get("future_fresh_eligible") is False and row.get("development_exposed") is True and row.get("exposure_type")=="current_epoch_evaluation","evaluation exposure must remain permanent")
            require(row.get("source_id") in spec["source_candidate_ids"],"unregistered evaluation source")
            stamp(row["timestamp"])
            if row["event_type"]=="scientific_read_completed":bound(row["start_event"],root)
            else:require(row["event_type"]=="scientific_read_started","unknown evaluation event")
            rows.append(row)
    return rows
def _open_for_first_scientific_read(contract,g5,source_id,reader_role,reader_id,*,root=ROOT):
    """Log conservatively before opening scientific bytes; return bytes, not eligibility."""
    verified=validate_full_qualification_contract(contract,root=root);spec=verified["contract"];meta=verified["meta"]
    stage=_g5(contract,spec,g5,root)
    require(reader_role in ("A4","A5") and isinstance(reader_id,str) and reader_id,"isolated reader identity required")
    src=next((s for s in meta["sources"] if s["source_id"]==source_id),None);require(src is not None,"source not preregistered")
    a3=next(r for r in meta["A3"] if r["source_id"]==source_id)
    require(a3["identity_status"]=="verified" and src["raw_status"]=="available","pending identity/access cannot be scientifically opened")
    tokens=set(_aliases(src))
    for old in meta["prior"]:
        if old["development_exposed"]:require(not tokens.intersection(closure_tokens(old)),"known prior/design source blocks fresh evaluation")
    previous=evaluation_events(contract,root=root)
    require(not any(e["source_id"]==source_id and e["reader_role"]==reader_role for e in previous),"reader already registered; explicit recovery contract needed")
    require(not any(e["reader_role"]!=reader_role and e["reader_id"]==reader_id for e in previous),"A4/A5 require distinct isolated reader identities")
    token=uuid.uuid4().hex
    started={"task":TASK,"event_type":"scientific_read_started","timestamp":now(),"contract_sha256":contract["sha256"],"epoch_id":spec["epoch_id"],"batch_id":spec["batch_id"],"source_id":source_id,"reader_role":reader_role,"reader_id":reader_id,"G5":g5,"raw_files":src["raw_files"],"closure_tokens":sorted(tokens),"development_exposed":True,"exposure_type":"current_epoch_evaluation","future_fresh_eligible":False,"current_epoch_eligibility":"conditional_only","scientific_bytes_opened":False,"prior_design":False}
    require(stamp(started["timestamp"])>=stamp(stage["timestamp"]),"read before G5")
    start=persist(Path(spec["evaluation_events_directory"])/(token+".start.json"),started,root)
    payload={}
    try:
        for raw in src["raw_files"]:payload[raw["path"]]=bound(raw,root).read_bytes()
    except Exception as exc:
        end={**started,"event_type":"scientific_read_completed","timestamp":now(),"start_event":start,"status":"failed","error":type(exc).__name__,"scientific_bytes_opened":bool(payload)}
        persist(Path(spec["evaluation_events_directory"])/(token+".end.json"),end,root);raise
    end={**started,"event_type":"scientific_read_completed","timestamp":now(),"start_event":start,"status":"completed","scientific_bytes_opened":True,"bytes_opened":sum(len(v) for v in payload.values())}
    receipt=persist(Path(spec["evaluation_events_directory"])/(token+".end.json"),end,root)
    return {"payloads":payload,"receipt":receipt,"fresh_admitted":False,"permanent_future_exclusion":True}
def open_for_first_scientific_read(contract,g5,source_id,reader_role,reader_id,*,root=ROOT):
    """Serialize independent registrations before returning scientific bytes."""
    spec=load(contract,root)
    lock=(Path(root)/spec["evaluation_events_directory"]/".read.lock").resolve()
    require(lock.is_relative_to(Path(root).resolve()) and lock.is_file(),"reader lock missing")
    with lock.open("r+") as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        try:return _open_for_first_scientific_read(contract,g5,source_id,reader_role,reader_id,root=root)
        finally:fcntl.flock(handle,fcntl.LOCK_UN)

def _round_role(ptr,role,spec,artifact,root):
    obj,outputs=_role(ptr,role,spec["epoch_id"],root,allow_pending=True)
    require(outputs.get(artifact["path"])==artifact["sha256"],"round role omits principal output")
    require(obj.get("read_other_extractor_output") is False if role in ("A4","A5") else True,"extractor read peer final output")
    require(obj["input_manifest_sha"].get(spec["raw_source_universe"]["path"])==spec["raw_source_universe"]["sha256"],"round role omitted common raw-only universe")
    return obj,outputs
def validate_full_science_round(contract,g5,round_manifest,*,root=ROOT):
    """Round execution completeness != source eligibility or G7 admission.

    Final evidence-bound deferred is terminal for this round. An unexecuted
    access plan, unprocessed source or metadata-only screen is not terminal.
    """
    checked=validate_full_qualification_contract(contract,root=root);spec=checked["contract"];meta=checked["meta"];_g5(contract,spec,g5,root)
    r=load(round_manifest,root)
    require(r.get("task")==TASK and r.get("batch_kind")=="full_qualification" and r.get("contract_sha256")==contract["sha256"],"metadata/raw-only is not full qualification")
    require(r.get("read_model_outcome") is False and r.get("scope_modified") is False,"round model/scope boundary")
    stamp(r["timestamp"])
    a=load(r["A4_result"],root);b=load(r["A5_result"],root);six=load(r["A6_result"],root)
    ar,ao=_round_role(r["A4_role"],"A4",spec,r["A4_result"],root);br,bo=_round_role(r["A5_role"],"A5",spec,r["A5_result"],root)
    cr,co=_round_role(r["A6_role"],"A6",spec,r["A6_result"],root)
    require(ar.get("reader_id") and br.get("reader_id") and ar["reader_id"]!=br["reader_id"],"extractor process/reader identity not independent")
    require(not set(ar["input_manifest_sha"]).intersection(bo) and not set(br["input_manifest_sha"]).intersection(ao),"extractor input includes peer final output")
    for obj,role in ((a,"A4"),(b,"A5"),(six,"A6")):
        require(obj.get("agent_role")==role and obj.get("contract_sha256")==contract["sha256"],"round result role/contract mismatch")
    sources=set(spec["source_candidate_ids"]);plans={s["source_id"]:set(s["planned_original_routes"]) for s in meta["sources"]}
    pending=[];source_counts={"qualified":0,"deferred":0,"rejected":0};rxns={}
    event_rows=evaluation_events(contract,root=root)
    for obj,role,ro in ((a,"A4",ar),(b,"A5",br),(six,"A6",cr)):
        pending.extend(role+":unprocessed:"+str(x) for x in ro["unprocessed"])
        rows=obj.get("source_dispositions")
        require(isinstance(rows,list) and len(rows)==len(sources) and {x.get("source_id") for x in rows}==sources,"source denominator changed after reading")
        reaction_rows=obj.get("reaction_records" if role!="A6" else "reaction_dispositions")
        require(isinstance(reaction_rows,list) and len({x.get("reaction_id") for x in reaction_rows})==len(reaction_rows),"reaction denominator duplicates")
        for row in reaction_rows:require(row.get("source_id") in sources and isinstance(row.get("reaction_id"),str),"reaction source/id missing")
        rxns[role]={x["reaction_id"]:x for x in reaction_rows}
        for row in rows:
            sid=row["source_id"];state=row.get("execution_state")
            require(state in ("completed","unprocessed"),"source execution_state missing")
            if state=="unprocessed":pending.append(role+":"+sid);continue
            require(row.get("terminal_for_this_round") is True and row.get("disposition") in TERMINAL and isinstance(row.get("reason"),str) and row["reason"].strip(),"final source disposition/reason required")
            _evidence(row.get("evidence"),root)
            done=row.get("original_routes_executed")
            require(isinstance(done,list) and set(done)==plans[sid],"original access route plan not conserved/completed")
            require(type(row.get("scientific_body_read")) is bool,"actual body read must remain explicit")
            src=next(s for s in meta["sources"] if s["source_id"]==sid)
            identity=next(z for z in meta["A3"] if z["source_id"]==sid)
            if role in ("A4","A5") and src["raw_status"]=="available" and identity["identity_status"]=="verified" and row["scientific_body_read"] is False:
                pending.append(role+":available_original_not_scientifically_processed:"+sid)
            if row["scientific_body_read"] is False:
                require(row["disposition"]!="qualified","unread or missing original cannot be scientifically qualified")
            if role in ("A4","A5") and row["scientific_body_read"]:
                require(any(e["event_type"]=="scientific_read_completed" and e.get("status")=="completed" and e["source_id"]==sid and e["reader_role"]==role and e["reader_id"]==ro["reader_id"] and stamp(e["timestamp"])<=stamp(ro["timestamp"]) for e in event_rows),"scientific read lacks prospective G5 receipt")
            if role=="A6":source_counts[row["disposition"]]+=1
    union=set(rxns["A4"])|set(rxns["A5"]);require(set(rxns["A6"])==union,"A6 must dispose complete A4/A5 reaction union")
    exposure=meta["prior"]+_supplements(r.get("late_prior_design_addenda"),root)
    qualified=[];qualified_sources=set();reaction_counts={"qualified":0,"deferred":0,"rejected":0,"unprocessed":0}
    for rid,row in rxns["A6"].items():
        disposition=row.get("disposition")
        require(disposition in TERMINAL|{"unprocessed"},"reaction disposition missing")
        reaction_counts[disposition]+=1
        if disposition=="unprocessed":pending.append("A6:reaction:"+rid);continue
        require(row.get("terminal_for_this_round") is True and isinstance(row.get("reason"),str) and row["reason"].strip(),"final reaction reason missing")
        _evidence(row.get("evidence"),root)
        if disposition!="qualified":continue
        require(not pending,"qualified reaction cannot rely on unprocessed source workflow")
        require(rid in rxns["A4"] and rid in rxns["A5"],"qualified reaction missing one extractor")
        x=rxns["A4"][rid];y=rxns["A5"][rid]
        require(x.get("structure_record") and y.get("structure_record"),"qualified full structure records absent")
        sx=load(x["structure_record"],root);sy=load(y["structure_record"],root)
        require(sx["input_manifest_sha"]==spec["raw_source_universe"]["sha256"] and sy["input_manifest_sha"]==spec["raw_source_universe"]["sha256"],"structure input binding")
        compared=reconcile(sx,sy,root=Path(root))
        require(compared["structure_complete"] is True,"dual structures unresolved")
        candidate=load(row["candidate"],root)
        require((candidate.get("family"),candidate.get("epoch_id"),candidate.get("reaction_id"))==(spec["family"],spec["epoch_id"],rid),"candidate context")
        require(candidate.get("source_id")==row["source_id"],"candidate source provenance")
        src=next(s for s in meta["sources"] if s["source_id"]==row["source_id"])
        require(set(candidate.get("official_aliases",[]))==_aliases(src),"candidate source alias union lost")
        a3=next(z for z in meta["A3"] if z["source_id"]==row["source_id"])
        require(a3["identity_status"]=="verified","qualified candidate requires passed A3")
        for f in ("acceptor","donor","product"):require(canonical(candidate[f+"_smiles"])==compared[f+"_smiles"],"candidate graph differs from extraction")
        require(all(candidate.get(f) is True for f in ("runtime_complete","source_identity_verified","structure_complete","reference_precursor_complete","scope_applicability")) and candidate.get("leakage") is False and candidate.get("exact_seed_instance_match") is False,"candidate hard flags incomplete")
        sourceproof=load(row["source_qualification"],root)
        require(sourceproof.get("agent_role")=="A6" and sourceproof.get("reaction_id")==rid and sourceproof.get("source_id")==row["source_id"] and sourceproof.get("source_reaction_eligible") is True and sourceproof.get("unresolved_conflicts")==[],"A6 source eligibility unresolved")
        _evidence(sourceproof.get("evidence"),root)
        proof=load(row["static_applicability"],root)
        require(proof.get("scope_bank_file_sha256")==spec["scope_bank_file_sha256"] and proof.get("static_only") is True and proof.get("scope_modified") is False and proof.get("complete_reference") is True,"frozen scope static proof missing")
        refs=sorted(canonical(z) for z in candidate["reference_precursors"])
        require(refs==compared["reference_precursors"]==sorted(canonical(z) for z in proof["precursors"]),"full static reference mismatch")
        assert_fresh({**candidate,"closure_tokens":list(set(candidate.get("closure_tokens",[]))|_aliases(src))},exposure)
        validate_current_named_exposure_review(candidate,root=root)
        require(any(e["event_type"]=="scientific_read_completed" and e.get("status")=="completed" and e["source_id"]==row["source_id"] and e["reader_role"]=="A4" for e in event_rows) and any(e["event_type"]=="scientific_read_completed" and e.get("status")=="completed" and e["source_id"]==row["source_id"] and e["reader_role"]=="A5" for e in event_rows),"qualified reaction needs both actual scientific reads")
        qualified.append(candidate["target_id"]);qualified_sources.add(row["source_id"])
    for source in six["source_dispositions"]:
        if source.get("disposition")=="qualified":require(source["source_id"] in qualified_sources,"source declared qualified without any qualified reaction")
    # Disposition completion is not inferred from zero admitted or a body count.
    complete=not pending
    return {"task":TASK,"round_execution_complete":complete,"source_candidates":len(sources),"source_disposition_counts":source_counts,"reaction_candidates":len(union),"reaction_disposition_counts":reaction_counts,"scientific_qualification_pending":source_counts["deferred"]+reaction_counts["deferred"],"qualified_for_final_G7_review":qualified,"fresh_admitted":0,"G7_panel_formed":False,"scope_bank_file_sha256":spec["scope_bank_file_sha256"],"scope_bank_json_sha256":spec["scope_bank_json_sha256"],"unprocessed":pending,"source_saturation_established":False,"requires_separate_three_routes_two_complete_rounds_A11_A12_review":True}
