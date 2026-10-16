"""Explicit permanent-name exposure review before fresh panel admission.

This validates bound documentary comparisons. It neither resolves identities nor
establishes reaction evidence, and never interprets a chemical name as a graph.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.task016_p7_orchestrate import ContractError

def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def json_sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def bound_file(root, pointer):
    if not isinstance(pointer,dict) or set(("path","sha256"))-pointer.keys():
        raise ContractError("name review evidence pointer incomplete")
    root=Path(root).resolve()
    p=(root/pointer["path"]).resolve()
    if not p.is_relative_to(root):
        raise ContractError("name review evidence outside root")
    if not p.is_file() or file_sha(p)!=pointer["sha256"]:
        raise ContractError("name review evidence missing or SHA drift")
    return p

def load_name_registry(root, files_sha256):
    if not isinstance(files_sha256,dict) or not files_sha256:
        raise ContractError("permanent name registry required")
    records={}
    for rel,digest in files_sha256.items():
        p=bound_file(root,{"path":rel,"sha256":digest})
        for line in p.read_text().splitlines():
            if not line.strip(): continue
            row=json.loads(line)
            key=row.get("exposure_id")
            if not key or key in records or row.get("future_fresh_eligible") is not False:
                raise ContractError("invalid or duplicate permanent name exposure")
            records[key]={"record":row,"record_sha256":json_sha(row)}
    if not records:
        raise ContractError("empty permanent name registry")
    return records

def validate_named_exposure_review(candidate, registry_files_sha256, *, root):
    records=load_name_registry(root,registry_files_sha256)
    binding=candidate.get("named_exposure_review")
    if not isinstance(binding,dict):
        raise ContractError("fresh target lacks permanent name identity review")
    review_path=bound_file(root,binding)
    review=json.loads(review_path.read_text())
    bare={k:v for k,v in candidate.items() if k!="named_exposure_review"}
    candidate_sha=json_sha(bare)
    if review.get("candidate_sha256")!=candidate_sha:
        raise ContractError("named review binds another candidate")
    if review.get("registry_files_sha256")!=registry_files_sha256:
        raise ContractError("named review omits or changes permanent registry")
    if review.get("read_model_outcome") is not False or review.get("scope_modified") is not False:
        raise ContractError("named review model outcome/scope boundary missing")
    roles=binding.get("role_manifests")
    if not isinstance(roles,dict) or set(roles)!={"A3","A6"}:
        raise ContractError("named review requires fixed A3 and A6 roles")
    for role,pointer in roles.items():
        manifest=json.loads(bound_file(root,pointer).read_text())
        if manifest.get("agent_role")!=role or manifest.get("reviewed_candidate_sha256")!=candidate_sha:
            raise ContractError("named role does not bind candidate and responsibility")
        if manifest.get("output_file_sha256",{}).get(binding["path"])!=binding["sha256"]:
            raise ContractError("named role does not bind review output")
        if manifest.get("registry_files_sha256")!=registry_files_sha256:
            raise ContractError("named role registry drift")
    comparisons=review.get("comparisons")
    if not isinstance(comparisons,list) or len(comparisons)!=len(records):
        raise ContractError("named exposure comparison universe incomplete")
    seen=set()
    for check in comparisons:
        key=check.get("exposure_id")
        if key not in records or key in seen:
            raise ContractError("unknown or duplicate named exposure comparison")
        seen.add(key)
        if check.get("exposure_record_sha256")!=records[key]["record_sha256"]:
            raise ContractError("named exposure record drift")
        if check.get("decision")!="no_match":
            raise ContractError("matched or unresolved permanent name exposure")
        if check.get("identity_chain_verified") is not True or check.get("name_only_inference") is not False:
            raise ContractError("unverified named identity comparison")
        if not isinstance(check.get("reaction_context_reason"),str) or not check["reaction_context_reason"].strip():
            raise ContractError("named identity comparison lacks reaction context")
        pointers=check.get("official_identity_evidence")
        if not isinstance(pointers,list) or not pointers:
            raise ContractError("official named identity evidence required")
        for pointer in pointers:
            if pointer.get("kind") not in ("official_source_identity","official_structure_database_identity"):
                raise ContractError("name/agent memory cannot establish official identity")
            if not isinstance(pointer.get("locator"),str) or not pointer["locator"].strip():
                raise ContractError("official named identity locator required")
            bound_file(root,pointer)
    return {"candidate_sha256":candidate_sha,"permanent_name_records_compared":len(records),
            "matched":0,"unresolved":0,"documentary_gate_passed":True,
            "chemical_identity_automatically_verified":False,"fresh_admission_established":False}

def validate_panel_with_named_exposure(records, epoch, scopes, exposures=(), build=(),
                                      runtime_instances=(), *, registry_files_sha256, root,
                                      enforce_floor=True):
    reviews=[validate_named_exposure_review(row,registry_files_sha256,root=root) for row in records]
    from scripts.task016_p7_panel_harness import validate_panel
    result=validate_panel(records,epoch,scopes,exposures,build,runtime_instances,
                          enforce_floor=enforce_floor)
    return {**result,"named_exposure_documentary_checks":reviews}
