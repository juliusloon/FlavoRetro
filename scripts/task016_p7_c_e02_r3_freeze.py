"""Freeze R3 raw public discovery for isolated identity and extraction roles."""
import json
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,freeze_stage_manifest,verify_stage_chain,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json,require_active,append,rows,C,E,BASE
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
B=E/"fresh/C-E02-R3"
D=E/"stages/batches/C-E02-R3"
def main():
    cp=B/"raw_original_request_plan.json"
    contract=require_active(cp)
    executed=rows(B/"raw_original_request_execution.jsonl")
    if sorted(r["request_index"] for r in executed)!=list(range(len(contract["requests"]))):
        raise ValueError("initial raw request universe incomplete")
    actual=[r for r in rows(C/"http_ledger.jsonl") if r.get("batch_id")=="C-E02-R3"]
    plans=[r for r in rows(C/"acquisition_plan.jsonl") if r.get("batch_id")=="C-E02-R3"]
    if len(actual)!=len(plans) or {r["attempt_id"] for r in actual}!={r["attempt_id"] for r in plans}:
        raise ValueError("R3 HTTP plan/execution universe does not conserve")
    files=[]
    for path in sorted(B.rglob("*")):
        if path.is_file() and path.suffix in {".json",".jsonl",".py"}:
            target=D/"intake_snapshot"/path.relative_to(B)
            write(TASK,str(target.relative_to(ROOT)),path.read_text())
            files.append(target)
    for name,rr in (("http_ledger.snapshot.jsonl",actual),("http_plan.snapshot.jsonl",plans)):
        path=D/"intake_snapshot"/name;save_rows(path,rr);files.append(path)
    for r in actual:
        p=ROOT/r["path"]
        if sha_file(p)!=r["sha256"] or p.stat().st_size!=r["bytes"]:raise ValueError("raw byte or SHA drift")
        files.append(p)
    files.extend(ROOT/p for p in contract["files_sha256"])
    files.extend([cp,Path(__file__)])
    mp=D/"raw_intake_manifest.json"
    immutable_json(mp,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R3",frozen_at=now(),
      G4_pointer=contract["G4_pointer"],scope_pointer=contract["scope_pointer"],
      files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in dict.fromkeys(files)},
      metadata_sources=21,metadata_HTTP=36,original_locator_requests=30,original_locator_HTTP=52,
      all_HTTP=len(actual),raw_bytes=sum(r["bytes"] for r in actual),
      raw_only=True,chemical_extraction_started=False,source_identity_verified=False,
      source_qualified=0,fresh_admitted=0,human_reviewed=False,model_outcomes_read=False,
      budget_accounting="Physical kind-based requests, including redirects/failed bodies; final HTML article-vs-landing identity pending",
      license_status="Local research access only; provider OA assertions require original-item verification"))
    files.append(mp)
    g4=ROOT/contract["G4_pointer"]["path"]
    freeze_stage_manifest(D,"G5_FRESH_HOLDOUT_ACQUIRE",list(dict.fromkeys(files)),g4,
      expected_previous_sha=contract["G4_pointer"]["sha256"],family="C",epoch_id="C-E02")
    g5=D/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(g5,sha_file(g5))
    hints={r["record_id"]:r for r in rows(B/"metadata_discovery.jsonl")}
    sources=[]
    for rid,r in hints.items():
        requests=[x for x in executed if x["request"]["record_id"]==rid]
        originals=[]
        for x in requests:
            if x.get("actual_content_type") not in {"PDF","JPEG","PNG","HTML"}:continue
            response=x["responses"][-1]
            originals.append(dict(raw_pointer=pointer(ROOT/response["path"]),actual_content_type=x["actual_content_type"],
              claimed_locator_kind=x["request"]["kind"],request_index=x["request_index"],
              raw_license=response.get("license"),original_identity_verified=False,
              HTML_is_not_automatically_article=True,evidence_eligible=False))
        sources.append(dict(source_id=r["source_id"],record_id=rid,doi=r["doi"],source_hint=r["source_hint"],
          metadata_response_pointers=[pointer(ROOT/x["path"]) for x in actual if x["kind"]=="metadata" and x["reason"].startswith("R3 metadata") and rid in x["reason"]],
          original_objects=originals,disposition="raw_objects_available_identity_pending" if originals else "public_access_or_selection_deferred",
          evidence_eligible=False,source_identity_verified=False,fresh_admitted=False))
    ip=D/"fresh_source_input_manifest.json"
    immutable_json(ip,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R3",created_at=now(),
      G5_pointer=pointer(g5),G4_pointer=contract["G4_pointer"],scope_pointer=contract["scope_pointer"],
      sources=sources,raw_only=True,contains_final_graphs=False,files_sha256={str(mp.relative_to(ROOT)):sha_file(mp)},
      permanent_exposure_files_sha256=contract["files_sha256"],name_synonym_identity_gate_required=True,
      read_model_outcome=False,human_reviewed=False))
    rp=D/"role_A1_raw_intake_manifest.json"
    role=role_manifest("A1 C Source Scout","C-E02",[cp,g4],[mp,g5,ip],dict(processed=21,passed=0,rejected=0,pending=21),
      unprocessed=["A3 original identity and license","independent A4/A5 extraction","A6 closure and original-type audit"],read_holdout=False,read_model_outcome=False)
    role.update(chemical_extraction_count=0,physical_HTTP=len(actual),original_locator_HTTP=52,
      PDF_objects=2,graphic_objects=1,HTML_objects=8,all_originals_are_unqualified=True)
    immutable_json(rp,role)
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R3",
      event_type="verified_existing_stage_registration",stage="G5_FRESH_HOLDOUT_ACQUIRE",stage_manifest_path=str(g5.relative_to(ROOT)),
      stage_manifest_sha256=sha_file(g5),registered_at=now(),approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G5=pointer(g5),source_inputs=pointer(ip),all_HTTP=len(actual),sources=21,qualified=0,fresh=0)))
if __name__=="__main__":main()
