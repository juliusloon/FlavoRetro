"""Freeze C-E02-R7 raw bytes with actual late permanent exposure closure; no chemistry."""
import json
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,freeze_stage_manifest,verify_stage_chain,role_manifest,verify_hashes
from scripts.task016_p7_c_e02_http import immutable_json,require_active,append,rows,C,E,BASE,physical_attempts
B=E/"fresh/C-E02-R7"
D=E/"stages/batches/C-E02-R7"
X=BASE/"SS/E02_design/new_source_actual_exposure_custodian_v3"
def pointer(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def main():
    if (D/"G5_FRESH_HOLDOUT_ACQUIRE.json").exists():raise RuntimeError("R7 G5 already frozen; do not overwrite/replay")
    cp=B/"query_plan.json";contract=require_active(cp)
    expected={B/"common_raw_only_source_input_v1.json":"43e9245a8639f1358549bb4f5a7f49a862f3ada65ade00acb11cc7ab67a843ce",B/"role_A2_raw_only_manifest_v1.json":"e7cac81d67e6edf20f72d7b4b265a1196ec5f05d27cdf9827b3519a68d9f0fd5",X/"permanent_exposure_manifest.json":"faf4a7031c191b33783cb7087c80fc35596b8ad09ff139b19d6423287743efb9"}
    for p,h in expected.items():assert sha_file(p)==h,"fixed input SHA drift"
    common=json.loads((B/"common_raw_only_source_input_v1.json").read_text());verify_hashes(common["files_sha256"])
    exposure=json.loads((X/"permanent_exposure_manifest.json").read_text());verify_hashes(exposure["input_files_sha256"])
    assert exposure["A5_metadata_abstract_only_sources"]==7 and exposure["source_unique_actual_scientific_design_exposures"]==12
    assert exposure["all_first_read_timestamps_unknown_not_backdated"] and exposure["source_qualification_granted"]==0
    actual=[r for r in physical_attempts() if r.get("batch_id")=="C-E02-R7"]
    planned=[r for r in rows(C/"acquisition_plan.jsonl") if r.get("batch_id")=="C-E02-R7"]
    inventory=rows(B/"raw_intake_inventory.v2.jsonl")
    assert len(actual)==len(planned)==len(inventory)==52
    assert {r["attempt_id"] for r in actual}=={r["attempt_id"] for r in planned}=={r["attempt_id"] for r in inventory}
    assert sum(r["bytes"] for r in actual)==25193994
    assert sum(bool(r["usable_original_bytes"]) for r in inventory)==27
    assert len({r["source_locator_id"] for r in inventory if r["usable_original_bytes"]})==3
    assert common["read_scientific_original_body"] is False and common["structure_extraction_permitted"] is False
    pre=BASE/"C/E02/pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl"
    post=BASE/"C/E02/post_scope_internal_hypotheses/v1/permanent_name_hypothesis_exposure.jsonl"
    assert len(rows(pre))+len(rows(post))==19
    g4=ROOT/contract["G4_pointer"]["path"]
    assert contract["G4_pointer"]["sha256"]=="09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46"
    verify_stage_chain(g4,contract["G4_pointer"]["sha256"])
    files=[cp,Path(__file__).resolve(),B/"common_raw_only_source_input_v1.json",B/"role_A2_raw_only_manifest_v1.json",pre,post]
    files.extend(ROOT/p for p in common["files_sha256"])
    files.extend(ROOT/p for p in exposure["input_files_sha256"])
    files.extend(p for p in X.iterdir() if p.is_file())
    for p in sorted(B.iterdir()):
        if p.is_file() and p.suffix in [".json",".jsonl"]:
            dest=D/"intake_snapshot"/p.name
            if dest.exists():raise RuntimeError("immutable intake snapshot exists")
            write(TASK,str(dest.relative_to(ROOT)),p.read_text())
            assert sha_file(dest)==sha_file(p)
            files.append(dest)
    for r in actual:
        p=ROOT/r["path"];assert sha_file(p)==r["sha256"] and p.stat().st_size==r["bytes"];files.append(p)
    files=list(dict.fromkeys(files))
    mp=D/"raw_intake_manifest.json"
    immutable_json(mp,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R7",frozen_at=now(),G4_pointer=contract["G4_pointer"],scope_pointer=contract["scope_pointer"],original_common_raw_input=pointer(B/"common_raw_only_source_input_v1.json"),original_A2_role=pointer(B/"role_A2_raw_only_manifest_v1.json"),files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in files},permanent_exposure_v3=pointer(X/"permanent_exposure_manifest.json"),permanent_name_hypotheses=19,prior_R7_pending_exposure_statements_resolved_by_actual_v3=True,prior_R7_queryplans_unchanged=True,late_exposure_closure_bound_at=now(),historical_scope_G4_unchanged=True,selected_source_ids=9,full_original_bytes_sources=3,usable_original_objects=27,discovery_metadata_rows=228,all_HTTP=52,raw_bytes=25193994,raw_only=True,chemical_extraction_started=False,source_identity_verified=False,source_qualified=0,fresh_admitted=0,complete_chemical_rounds=0,source_saturation=False,human_reviewed=False,model_outcomes_read=False,approval_type="agent_delegated",source_qualification_occurs_later_A3_A4_A5_A6_not_required_or_claimed_by_A0_freeze=True))
    files.append(mp)
    freeze_stage_manifest(D,"G5_FRESH_HOLDOUT_ACQUIRE",files,g4,expected_previous_sha=contract["G4_pointer"]["sha256"],family="C",epoch_id="C-E02")
    g5=D/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(g5,sha_file(g5))
    identity=json.loads((B/"source_metadata_identity_inventory.v2.json").read_text());sources=[]
    for h in identity["sources"]:
        ts=h["source_alias_tokens_observed"];doi=h.get("doi") or next((t[4:] for t in ts if t.startswith("doi:")),None);pmcid=h.get("pmcid");pmid=h.get("pmid") or next((t[5:] for t in ts if t.startswith("pmid:")),None)
        sid=pmcid or ("DOI:"+doi if doi else "PMID:"+pmid);objects=[]
        for x in inventory:
            if x.get("source_locator_id")!=h["source_locator_id"] or not x["usable_original_bytes"]:continue
            objects.append(dict(raw_pointer=x["raw_pointer"],actual_content_type=x["container_qc"]["container"],claimed_locator_kind=x["role"],MD5_pass=x["container_qc"].get("MD5_pass"),original_identity_verified=False,evidence_eligible=False))
        meta=[h["metadata_pointer"]]+[r["MED_record_raw_pointer"] for r in h["official_MED_metadata_records"]]
        if h.get("reused_official_repository_metadata_pointer"):meta.append(h["reused_official_repository_metadata_pointer"])
        sources.append(dict(source_id=sid,record_id=sid,source_locator_id=h["source_locator_id"],doi=doi,pmid=pmid,pmcid=pmcid,source_alias_tokens_observed=ts,source_hint=dict(title=h["title"]),metadata_response_pointers=meta,source_front_metadata=h.get("source_front_metadata"),original_objects=objects,disposition="raw_objects_available_identity_pending" if objects else "public_access_or_locator_deferred",metadata_disagreements=h.get("metadata_disagreements",[]),evidence_eligible=False,source_identity_verified=False,fresh_admitted=False))
    assert len(sources)==9 and sum(bool(s["original_objects"]) for s in sources)==3 and sum(len(s["original_objects"]) for s in sources)==27
    ip=D/"fresh_source_input_manifest.json"
    immutable_json(ip,dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R7",created_at=now(),G5_pointer=pointer(g5),G4_pointer=contract["G4_pointer"],scope_pointer=contract["scope_pointer"],sources=sources,raw_only=True,contains_final_graphs=False,files_sha256={str(mp.relative_to(ROOT)):sha_file(mp),str((B/"source_metadata_identity_inventory.v2.json").relative_to(ROOT)):sha_file(B/"source_metadata_identity_inventory.v2.json")},permanent_exposure_v3=pointer(X/"permanent_exposure_manifest.json"),permanent_exposure_files_sha256={**contract["files_sha256"],**{str(p.relative_to(ROOT)):sha_file(p) for p in X.iterdir() if p.is_file()}},permanent_name_hypotheses=19,name_synonym_identity_gate_required=True,unresolved_abstract_identity_excerpts_fail_closed=True,source_alias_wrapper_required_for_admission=True,scientific_qualification_granted=False,read_model_outcome=False,human_reviewed=False,prior_common_pending_exposure_statement_superseded_at_actual_G5_time=True))
    rp=D/"role_A0_raw_intake_freeze_manifest.json"
    role=role_manifest("A0 C-R7 raw intake custodian","C-E02",[cp,g4,X/"permanent_exposure_manifest.json"],[mp,g5,ip],dict(processed=9,passed=0,rejected=0,pending=9),unprocessed=["independent A3 publication identity","independent A4/A5 extraction","A6 reaction/graph/name/source closure"],read_holdout=False,read_model_outcome=False)
    role.update(chemical_extraction_count=0,physical_HTTP=52,usable_original_objects=27,original_bytes_sources=3,source_qualification_granted=0,fresh_admitted=0,complete_chemical_rounds=0,all_sources_unqualified_by_this_role=True,approval_type="agent_delegated")
    immutable_json(rp,role)
    append(BASE/"epoch_ledger.jsonl",dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R7",event_type="verified_existing_stage_registration",stage="G5_FRESH_HOLDOUT_ACQUIRE",stage_manifest_path=str(g5.relative_to(ROOT)),stage_manifest_sha256=sha_file(g5),registered_at=now(),approval_type="agent_delegated",human_reviewed=False,backdated=False,source_qualified=0,fresh_admitted=0))
    print(json.dumps(dict(G5=pointer(g5),input=pointer(ip),raw_contract=pointer(mp),source_inputs=9,full_original_bytes_sources=3,usable_original_objects=27,HTTP=52,raw_bytes=25193994,qualification=0,fresh=0)))
if __name__=="__main__":main()
