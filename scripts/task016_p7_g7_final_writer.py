"""TASK-016-P7 final G7 writer. Refuse to write without v4 official-name review.

No discovery, source read, scope modification or scientific experiments occur here.
No bypass flag exists. The final panel minimum is always enforced.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from scripts.operate import ROOT, write, event
from scripts.task016_p7_orchestrate import (
    ContractError, sha_file, sha_json, verify_stage_chain, freeze_stage_manifest, now,
)
from scripts.task016_p7_named_exposure_gate_v1 import bound_file
from scripts import task016_p7_named_exposure_gate_v4 as named_gate
from scripts.task016_p7_source_alias_closure import assert_zero_leakage as assert_alias_zero_leakage

TASK="TASK-016-P7"
BASE=Path("outputs/task016-p7/v1")
REQ=BASE/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json"
SOURCE_LEDGER=BASE/"exposure_ledger.jsonl"
PRIOR_LEDGER=BASE/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl"
REQUIRED={
    "schema_version","task","family","epoch_id","g4_stage","g6_stage",
    "scope_manifest","epoch_state","scope_bank","records","build","exposures",
    "runtime_instances","requirement","historical_exposure","prior_exposure",
    "current_exposure_receipt",
    "no_model_outcome_read","no_scope_or_panel_change_after_results",
}
POINTER_FIELDS={
    "g4_stage","g6_stage","scope_manifest","epoch_state","scope_bank",
    "records","build","exposures","runtime_instances","requirement",
    "historical_exposure","prior_exposure","current_exposure_receipt",
}

def rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]

def _data(pointer,root,expected_type):
    file=bound_file(root,pointer)
    if file.suffix==".jsonl":
        value=rows(file)
    else:
        value=json.loads(file.read_text())
    if not isinstance(value,expected_type):
        raise ContractError("G7 input wrong data type: "+str(pointer.get("path")))
    return value

def verify_current_exposure_receipt(request, *, root, ledger):
    """Fail closed on omitted current-epoch exposure and incomplete G5/G6 coverage.

    A6 and independent A11 role manifests must bind the actual exposure rows and
    every registered source-qualification stage; metadata alone is not chemistry.
    """
    receipt=_data(request["current_exposure_receipt"],root,dict)
    if (receipt.get("task"),receipt.get("epoch_id"),receipt.get("family"))!=(
       TASK,request["epoch_id"],request["family"]):
        raise ContractError("current exposure receipt belongs to another epoch")
    if receipt.get("epoch_ledger_sha256")!=sha_file(root/BASE/"epoch_ledger.jsonl"):
        raise ContractError("current exposure audit is stale versus epoch ledger")
    if receipt.get("effective_exposure_sha256")!=request["exposures"]["sha256"]:
        raise ContractError("current exposure receipt does not bind complete row input")
    if receipt.get("closure_complete") is not True or receipt.get("source_alias_unresolved")!=0 or receipt.get("disposition_pending")!=0:
        raise ContractError("current exposure and source alias closure unresolved")
    stage_map={}
    for row in ledger:
        if row.get("epoch_id")!=request["epoch_id"] or row.get("status")!="active" or row.get("stage") not in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT"):
            continue
        path=row.get("stage_manifest_path");digest=row.get("stage_manifest_sha256")
        if not isinstance(path,str) or not isinstance(digest,str):
            raise ContractError("registered exposure stage lacks SHA")
        if path in stage_map and stage_map[path]!=digest:
            raise ContractError("conflicting stage SHA in registry")
        stage_map[path]=digest
    if not stage_map or not any("/G6_IDENTITY_STRUCTURE_ADMIT.json" in k for k in stage_map):
        raise ContractError("no final G6 source exposure stage registered")
    if receipt.get("registered_stage_sha256")!=stage_map:
        raise ContractError("current exposure proof skips G5/G6 registrations")
    for path,digest in stage_map.items():
        bound_file(root,{"path":path,"sha256":digest})
        verify_stage_chain(root/path,digest)
    roles=receipt.get("role_manifests")
    if not isinstance(roles,dict) or set(roles)!={"A6","A11"}:
        raise ContractError("current source exposure proof requires A6+A11")
    a6=json.loads(bound_file(root,roles["A6"]).read_text())
    a11=json.loads(bound_file(root,roles["A11"]).read_text())
    if a6.get("agent_role")!="A6" or a11.get("agent_role")!="A11":
        raise ContractError("current exposure proof role mismatch")
    if a6.get("epoch_id")!=request["epoch_id"] or a11.get("epoch_id")!=request["epoch_id"]:
        raise ContractError("current exposure proof role epoch mismatch")
    outputs=a6.get("output_file_sha256")
    if not isinstance(outputs,dict) or outputs.get(request["exposures"]["path"])!=request["exposures"]["sha256"]:
        raise ContractError("A6 did not bind effective current exposure rows")
    inputs=a11.get("input_manifest_sha")
    if not isinstance(inputs,dict) or any(inputs.get(p)!=digest for p,digest in {**stage_map,request["exposures"]["path"]:request["exposures"]["sha256"]}.items()):
        raise ContractError("A11 did not independently check every stage and current exposure")
    if a6.get("read_model_outcome") is not False or a11.get("read_model_outcome") is not False:
        raise ContractError("current source closure contaminated by model outcome")
    for role in (a6,a11):
        if role.get("errors")!=[] or role.get("unprocessed")!=[]:
            raise ContractError("current exposure reviewer left errors or unresolved work")
        for field in ("input_manifest_sha","output_file_sha256"):
            if not isinstance(role.get(field),dict) or not role[field]:
                raise ContractError("review role missing bound evidence")
            for p,digest in role[field].items():
                bound_file(root,{"path":p,"sha256":digest})
    return len(stage_map)

def validate_contract(request, *, root=ROOT):
    """Pure read-only validation. Returns only if all pre-write hard gates pass."""
    root=Path(root).resolve()
    if not isinstance(request,dict) or set(request)!=REQUIRED:
        raise ContractError("G7 contract must list all required frozen inputs, no bypass fields")
    if request["schema_version"]!=1 or request["task"]!=TASK:
        raise ContractError("G7 task/schema mismatch")
    family=request["family"];epoch=request["epoch_id"]
    if family not in ("C","SS") or epoch!=family+"-E02":
        raise ContractError("G7 only supports current independently frozen E02 epochs")
    if request["no_model_outcome_read"] is not True or request["no_scope_or_panel_change_after_results"] is not True:
        raise ContractError("G7 pre-scientific/outcome boundary must be explicit")
    for k in POINTER_FIELDS:
        p=request[k]
        if not isinstance(p,dict) or set(p)!={"path","sha256"}:
            raise ContractError("G7 "+k+" pointer must be an exact file-SHA pair")
    if request["requirement"]["path"]!=str(REQ):
        raise ContractError("G7 named exposure v4 requirement cannot be swapped")
    if request["historical_exposure"]["path"]!=str(SOURCE_LEDGER) or request["prior_exposure"]["path"]!=str(PRIOR_LEDGER):
        raise ContractError("G7 full historical exposure inputs cannot be omitted or replaced")
    if request["g4_stage"]["path"]!=str(BASE/f"{family}/E02/stages/G4_SCOPE_FREEZE.json"):
        raise ContractError("G7 must use the canonical frozen G4")
    g6_path=request["g6_stage"]["path"]
    prefix=str(BASE/f"{family}/E02/stages/batches/")
    if not g6_path.startswith(prefix) or not g6_path.endswith("/G6_IDENTITY_STRUCTURE_ADMIT.json"):
        raise ContractError("G7 must consume a registered G6 batch stage")
    out=BASE/f"{family}/E02/stages/G7_CLOSURE_PANEL_FREEZE.json"
    if (root/out).exists():
        raise ContractError("G7 immutable stage already exists")
    # Hash every declared input before evaluating any chemical or panel claim.
    for k in POINTER_FIELDS:
        bound_file(root,request[k])
    req=_data(request["requirement"],root,dict)
    if req.get("validator_path")!="scripts/task016_p7_named_exposure_gate_v4.py" or req.get("call")!="validate_final_panel" or req.get("production_floor_cannot_be_disabled") is not True:
        raise ContractError("G7 required v4 validator missing")
    if req.get("permanent_name_record_count")!=28 or req.get("registry_files_sha256") is None:
        raise ContractError("G7 full 28 permanent name universe missing")
    if sha_file(root/req["validator_path"])!=req["validator_sha256"]:
        raise ContractError("G7 v4 validator code drift")
    for path,digest in req.get("implementation_files_sha256",{}).items():
        if sha_file(root/path)!=digest:raise ContractError("G7 dependency code SHA drift")
    stage4=verify_stage_chain(root/request["g4_stage"]["path"],request["g4_stage"]["sha256"])
    stage6=verify_stage_chain(root/request["g6_stage"]["path"],request["g6_stage"]["sha256"])
    if (stage4["stage"],stage6["stage"])!=("G4_SCOPE_FREEZE","G6_IDENTITY_STRUCTURE_ADMIT"):
        raise ContractError("G7 stage chain invalid")
    if any(stage["family"]!=family or stage["epoch_id"]!=epoch for stage in (stage4,stage6)):
        raise ContractError("G7 stage family/epoch mismatch")
    ledger=rows(root/BASE/"epoch_ledger.jsonl")
    registered=any(r.get("epoch_id")==epoch and r.get("stage")=="G6_IDENTITY_STRUCTURE_ADMIT"
         and r.get("stage_manifest_path")==g6_path
         and r.get("stage_manifest_sha256")==request["g6_stage"]["sha256"]
         and r.get("status")=="active" for r in ledger)
    if not registered:raise ContractError("G7 G6 not registered in real epoch ledger")
    if any(r.get("epoch_id")==epoch and r.get("status") in ("closed","complete","development_epoch_incomplete") for r in ledger):
        raise ContractError("G7 epoch closed")
    sm=_data(request["scope_manifest"],root,dict)
    if (sm.get("family"),sm.get("epoch_id"))!=(family,epoch):
        raise ContractError("G7 scope manifest wrong epoch")
    if request["scope_manifest"]["path"]!=str(BASE/f"{family}/E02/scope_manifest.json"):
        raise ContractError("G7 cannot use a substituted scope freeze")
    state=_data(request["epoch_state"],root,dict)
    scopes=_data(request["scope_bank"],root,dict)
    if state.get("status")!="active" or state.get("family")!=family or state.get("epoch_id")!=epoch:
        raise ContractError("G7 requires active epoch state")
    if state.get("scope_sha")!=sha_json(scopes) or sm.get("scope_bank_sha256")!=sha_file(root/request["scope_bank"]["path"]):
        raise ContractError("G7 frozen scope hash mismatch")
    panel=_data(request["records"],root,list)
    if len(panel)<6 or len(panel)>9:
        raise ContractError("G7 requires 6-9 qualified targets; no empty or reduced panel")
    build=_data(request["build"],root,list)
    exposure=_data(request["exposures"],root,list)
    instance=_data(request["runtime_instances"],root,list)
    history=_data(request["historical_exposure"],root,list)
    prior=_data(request["prior_exposure"],root,list)
    if not history or not prior or not exposure:
        raise ContractError("G7 cannot ignore previous or current exposure ledgers")
    verify_current_exposure_receipt(request,root=root,ledger=ledger)
    # Never allow a request to replace the prior ledger with an empty subset.
    combined=history+prior+exposure
    result=named_gate.validate_final_panel(
        panel,state,scopes,combined,build,instance,
        root=root,enforce_floor=True,registry_files_sha256=req["registry_files_sha256"])
    alias_result=assert_alias_zero_leakage(build,panel,combined,instance)
    if any(alias_result.get(k)!=0 for k in ("reaction_leakage","source_assay_closure_leakage","exact_runtime_instance_leakage","scope_design_leakage")):
        raise ContractError("G7 explicit PMID/source-alias closure not zero")
    if result.get("completion_floor_passed") is not True or result.get("N")!=len(panel):
        raise ContractError("G7 panel completion and denominator invalid")
    if len(result.get("named_exposure_documentary_checks",[]))!=len(panel):
        raise ContractError("G7 mandatory v4 checks absent")
    return result

def freeze(request_path):
    """Only full validation may reach either persistent panel or G7 stage write."""
    path=Path(request_path)
    if not path.is_absolute():path=ROOT/path
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ContractError("G7 request cannot be outside workspace")
    request=json.loads(path.read_text())
    report=validate_contract(request,root=ROOT) # no prior writes
    family=request["family"]
    out=BASE/f"{family}/E02/panel_G7_final"
    dest=BASE/f"{family}/E02/stages"
    if (ROOT/out).exists() or (ROOT/dest/"G7_CLOSURE_PANEL_FREEZE.json").exists():
        raise ContractError("immutable G7 output exists")
    evidence={"task":TASK,"family":family,"epoch_id":request["epoch_id"],
        "at":now(),"approval_type":"agent_delegated","human_reviewed":False,
        "preflight":report,"request_path":str(path.relative_to(ROOT)),
        "request_SHA":sha_file(path),"actual_G7_v4_writer":True,
        "validator":"scripts/task016_p7_named_exposure_gate_v4.py",
        "no_scientific_model_outcome_read":True,"no_G10_started_by_writer":True}
    # Persistent stage entries are only reached after all validation including v4.
    output=out/"validated_panel_G7.json"
    write(TASK,str(output),json.dumps(evidence,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    files=[path,output]
    files += [Path(request[k]["path"]) for k in POINTER_FIELDS]
    freeze_stage_manifest(dest,"G7_CLOSURE_PANEL_FREEZE",files,
        request["g6_stage"]["path"],expected_previous_sha=request["g6_stage"]["sha256"],
        family=family,epoch_id=request["epoch_id"])
    event(TASK,"G7_v4_named_exposure_and_science_panel_frozen",
        family=family,targets=report["N"],closure_groups=report["closure_groups"],
        writer_path="scripts/task016_p7_g7_final_writer.py")
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--request",required=True,help="SHA-bound local JSON contract")
    args=parser.parse_args()
    print(json.dumps(freeze(args.request),ensure_ascii=False,sort_keys=True))
if __name__=="__main__":main()

