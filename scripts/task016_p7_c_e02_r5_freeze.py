"""Freeze actual R5 raw intake before original chemical extraction."""
import json
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,freeze_stage_manifest,verify_stage_chain,role_manifest
from scripts.task016_p7_c_e02_http import immutable_json,require_active,append,rows,C,E,BASE
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
B=E/"fresh/C-E02-R5";D=E/"stages/batches/C-E02-R5"
def main():
    cp=B/"supplemental_raw_file_request_plan.v2.json";contract=require_active(cp)
    initial=require_active(B/"raw_original_request_plan.json")
    raw=rows(B/"raw_original_request_execution.jsonl");supp=rows(B/"supplemental_raw_file_execution.jsonl")
    assert sorted(x["request_index"] for x in raw)==list(range(len(initial["requests"])))
    assert sorted(x["request_index"] for x in supp)==list(range(len(contract["requests"])))
    executed=raw+supp
    actual=[r for r in rows(C/"http_ledger.jsonl") if r.get("batch_id")=="C-E02-R5"]
    planned=[r for r in rows(C/"acquisition_plan.jsonl") if r.get("batch_id")=="C-E02-R5"]
    assert len(actual)==len(planned) and {x["attempt_id"] for x in actual}=={x["attempt_id"] for x in planned}
    query=json.loads((B/"query_audit.json").read_text());assert query["conserved"] and query["planned"]==query["executed"]==7
    files=[]
    for p in sorted(B.rglob("*")):
        if p.is_file() and p.suffix in [".json",".jsonl",".py"]:
            dest=D/"intake_snapshot"/p.relative_to(B);assert not dest.exists();write(TASK,str(dest.relative_to(ROOT)),p.read_text());files.append(dest)
    for n,r in [("http_ledger.snapshot.jsonl",actual),("http_plan.snapshot.jsonl",planned)]:
        p=D/"intake_snapshot"/n;save_rows(p,r);files.append(p)
    for r in actual:
        p=ROOT/r["path"];assert sha_file(p)==r["sha256"] and p.stat().st_size==r["bytes"];files.append(p)
    files.extend(ROOT/p for p in contract["files_sha256"]);files.extend([cp,Path(__file__)])
    counts={k:sum(x.get("actual_content_type")==k for x in executed) for k in ["PDF","HTML","JPEG","PNG"]}
    mp=D/"raw_intake_manifest.json"
    immutable_json(mp,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R5",frozen_at=now(),G4_pointer=contract["G4_pointer"],scope_pointer=contract["scope_pointer"],files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in dict.fromkeys(files)},queries=7,exact_MED_resolution_queries=1,exact_MED_PMIDs=13,permanent_alias_excluded=4,selected_original_source_ids=9,all_HTTP=len(actual),raw_bytes=sum(x["bytes"] for x in actual),raw_object_counts=counts,raw_only=True,chemical_extraction_started=False,source_identity_verified=False,source_qualified=0,fresh_admitted=0,human_reviewed=False,model_outcomes_read=False,source_saturation=False,ACS_metadata_query_cap_rejection_HTTP=0,license_status="Local-only pending item-level source license; failed/redirect bytes retained"))
    files.append(mp);g4=ROOT/contract["G4_pointer"]["path"]
    freeze_stage_manifest(D,"G5_FRESH_HOLDOUT_ACQUIRE",list(dict.fromkeys(files)),g4,expected_previous_sha=contract["G4_pointer"]["sha256"],family="C",epoch_id="C-E02")
    g5=D/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(g5,sha_file(g5))
    hints=rows(B/"exact_13_MED_primary_hint_metadata.jsonl");sources=[]
    for h in hints:
        if h["historical_source_overlap"]:continue
        sid=h["source_id"];objects=[];seen=set()
        for x in executed:
            if x["request"]["source_id"]!=sid or x.get("actual_content_type") not in ["PDF","HTML","JPEG","PNG"]:continue
            r=x["responses"][-1]
            if r["path"] in seen:continue
            seen.add(r["path"]);objects.append(dict(raw_pointer=pointer(ROOT/r["path"]),actual_content_type=x["actual_content_type"],claimed_locator_kind=x["request"]["kind"],raw_license=r.get("license"),original_identity_verified=False,HTML_is_not_automatically_article=True,evidence_eligible=False))
        sources.append(dict(source_id=sid,record_id=sid,doi=h["metadata_hint"]["doi"],source_hint=h["metadata_hint"],metadata_response_pointers=[h["raw_pointer"]],original_objects=objects,disposition="raw_objects_available_identity_pending" if objects else "public_access_deferred",evidence_eligible=False,source_identity_verified=False,fresh_admitted=False))
    assert len(sources)==9
    ip=D/"fresh_source_input_manifest.json"
    immutable_json(ip,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R5",created_at=now(),G5_pointer=pointer(g5),G4_pointer=contract["G4_pointer"],scope_pointer=contract["scope_pointer"],sources=sources,raw_only=True,contains_final_graphs=False,files_sha256={str(mp.relative_to(ROOT)):sha_file(mp)},permanent_exposure_files_sha256=contract["files_sha256"],name_synonym_identity_gate_required=True,permanent_name_hypotheses=19,source_alias_wrapper_required_for_admission=True,read_model_outcome=False,human_reviewed=False))
    rp=D/"role_A1_raw_intake_manifest.json";r=role_manifest("A1 C Source Scout","C-E02",[cp,g4],[mp,g5,ip],dict(processed=9,passed=0,rejected=0,pending=9),unprocessed=["A3 source-original identity","A4/A5 independent raw extraction","A6 source/reaction/graph/name alias closure"],read_holdout=False,read_model_outcome=False)
    r.update(chemical_extraction_count=0,physical_HTTP=len(actual),raw_object_counts=counts,all_originals_are_unqualified=True,scientific_ABE_cells=0)
    immutable_json(rp,r)
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R5",event_type="verified_existing_stage_registration",stage="G5_FRESH_HOLDOUT_ACQUIRE",stage_manifest_path=str(g5.relative_to(ROOT)),stage_manifest_sha256=sha_file(g5),registered_at=now(),approval_type="agent_delegated",human_reviewed=False,backdated=False))
    print(json.dumps(dict(G5=pointer(g5),input=pointer(ip),source_inputs=9,HTTP=len(actual),raw_objects=counts,qualification=0,fresh=0)))
if __name__=="__main__":main()
