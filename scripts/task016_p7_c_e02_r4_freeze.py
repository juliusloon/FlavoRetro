"""Freeze exact DOI SI and public repository original bytes, before chemistry extraction."""
import json
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,freeze_stage_manifest,verify_stage_chain,role_manifest
from scripts.task016_p7_c_e02_http import E,C,BASE,rows,require_active,immutable_json,append
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
B=E/"fresh/C-E02-R4";D=E/"stages/batches/C-E02-R4"
def main():
    cp=B/"raw_file_request_plan.json";plan=require_active(cp)
    execs=rows(B/"raw_file_request_execution.jsonl")
    if sorted(x["request_index"] for x in execs)!=list(range(len(plan["requests"]))):raise ValueError("R4 original requests not conserved")
    actual=[r for r in rows(C/"http_ledger.jsonl") if r.get("batch_id")=="C-E02-R4"]
    plans=[r for r in rows(C/"acquisition_plan.jsonl") if r.get("batch_id")=="C-E02-R4"]
    if len(actual)!=len(plans) or {x["attempt_id"] for x in actual}!={x["attempt_id"] for x in plans}:raise ValueError("R4 actual HTTP accounting incomplete")
    files=[]
    for p in sorted(B.rglob("*")):
        if p.is_file() and p.suffix in {".json",".jsonl",".py"}:
            target=D/"intake_snapshot"/p.relative_to(B)
            write(TASK,str(target.relative_to(ROOT)),p.read_text());files.append(target)
    for name,rr in (("http_ledger.snapshot.jsonl",actual),("http_plan.snapshot.jsonl",plans)):
        p=D/"intake_snapshot"/name;save_rows(p,rr);files.append(p)
    for r in actual:
        p=ROOT/r["path"]
        if sha_file(p)!=r["sha256"] or p.stat().st_size!=r["bytes"]:raise ValueError("Raw SHA or byte drift")
        files.append(p)
    r3in=E/"stages/batches/C-E02-R3/fresh_source_input_manifest.json"
    files.extend([cp,r3in,Path(__file__),ROOT/"scripts/task016_p7_c_e02_r4_originals.py",ROOT/"scripts/task016_p7_c_e02_public_post.py"])
    files.extend(ROOT/p for p in plan["files_sha256"])
    mp=D/"raw_intake_manifest.json"
    immutable_json(mp,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R4",frozen_at=now(),G4_pointer=plan["G4_pointer"],
      scope_pointer=plan["scope_pointer"],files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in dict.fromkeys(files)},
      all_HTTP=len(actual),raw_bytes=sum(x["bytes"] for x in actual),metadata_HTTP=2,original_file_HTTP=4,
      POST_requests=1,GET_requests=5,planned_file_downloads=2,terminal_file_downloads=2,PDF_originals=2,
      raw_only=True,chemical_extraction_started=False,qualified=0,fresh_admitted=0,read_model_outcome=False,human_reviewed=False,
      repository_proposal_dispositions=plan["repository_proposal_dispositions"],
      original_identity_status="Official SI parent DOI verified from public API; chemical content and full publication identity pending A3/A4/A5"))
    files.append(mp);g4=ROOT/plan["G4_pointer"]["path"]
    freeze_stage_manifest(D,"G5_FRESH_HOLDOUT_ACQUIRE",list(dict.fromkeys(files)),g4,expected_previous_sha=plan["G4_pointer"]["sha256"],family="C",epoch_id="C-E02")
    g5=D/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(g5,sha_file(g5))
    hints={s["doi"]:s for s in json.loads(r3in.read_text())["sources"]}
    sir=json.loads((B/"official_SI_record_response.json").read_text())
    sources=[]
    for x in execs:
        req=x["request"];r=x["responses"][-1];h=hints[req["doi"]]
        sources.append(dict(source_id=h["source_id"],doi=req["doi"],source_hint=h["source_hint"],
          original_objects=[dict(raw_pointer=pointer(ROOT/r["path"]),actual_content_type=x.get("actual_content_type"),
          object_role="official_publisher_SI" if req["kind"]=="attachment" else "public_author_manuscript",source_identity_verified=False,evidence_eligible=False)],
          relationship_metadata_pointer=pointer(ROOT/sir["path"]) if req["kind"]=="attachment" else req["locator_origin"],
          license=req.get("license"),redistribution="local_only_pending_or_source_license",source_identity_verified=False,evidence_eligible=False))
    ip=D/"fresh_source_input_manifest.json"
    immutable_json(ip,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R4",created_at=now(),G5_pointer=pointer(g5),G4_pointer=plan["G4_pointer"],
      scope_pointer=plan["scope_pointer"],sources=sources,raw_only=True,contains_final_graphs=False,
      permanent_exposure_files_sha256=plan["files_sha256"],name_synonym_identity_gate_required=True,read_model_outcome=False,human_reviewed=False))
    rp=D/"role_A1_raw_intake_manifest.json";role=role_manifest("A1 C Source Scout","C-E02",[cp,g4,r3in],[mp,g5,ip],dict(processed=2,passed=0,rejected=0,pending=2),
      unprocessed=["A3 original publication identity","independent A4/A5 chemical extraction","A6 source/name/structure closure"],read_holdout=False,read_model_outcome=False)
    role.update(physical_HTTP=len(actual),chemical_extraction_count=0,source_qualified=0,fresh_admitted=0)
    immutable_json(rp,role)
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R4",event_type="verified_existing_stage_registration",
      stage="G5_FRESH_HOLDOUT_ACQUIRE",stage_manifest_path=str(g5.relative_to(ROOT)),stage_manifest_sha256=sha_file(g5),registered_at=now(),approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G5=pointer(g5),input_manifest=pointer(ip),source_PDFs=2,HTTP=len(actual),qualified=0,fresh=0)))
if __name__=="__main__":main()
