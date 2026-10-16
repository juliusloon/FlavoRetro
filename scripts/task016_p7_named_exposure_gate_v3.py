"""Final P7 panel entry: strict permanent-name reviews and immutable dependencies."""
from datetime import datetime,timezone
import json
import re
from scripts.task016_p7_named_exposure_gate_v1 import bound_file,json_sha,load_name_registry
from scripts.task016_p7_named_exposure_gate_v2 import CURRENT_REGISTRY_FILES_SHA256
from scripts.task016_p7_orchestrate import ContractError
TASK="TASK-016-P7"
DEPENDENCY_SHA256 = {'scripts/task016_p7_named_exposure_gate_v1.py': '54f22938e846fe407414dd99302419d05952784087a2e198545e65b45c11d2f4', 'scripts/task016_p7_named_exposure_gate_v2.py': '97bd0473b3ca863795e70fbcf099e671ca7d83e0fd15c7fd3f665b059c58b651', 'scripts/task016_p7_panel_harness.py': 'ca47c70543f129dd4b8771fea807eea1d297f7e13b62ce4c50005383cde90e88', 'scripts/task016_p7_closure_harness.py': '1712f7bf914a0c63e0131efa27df80b67e3f308dc860eb638c012209b7bf3a08', 'scripts/task016_p7_orchestrate.py': '9acbbcf7426eaa1c09b3686f2f14deea6f9dc931772b1b1809438afcba468a83'}

def _bound_dependencies(root):
    for path,digest in DEPENDENCY_SHA256.items():
        bound_file(root,{"path":path,"sha256":digest})

def _role_review(root, role, pointer, binding, candidate, candidate_sha):
    manifest=json.loads(bound_file(root,pointer).read_text())
    tasks=[manifest[k] for k in ("task","task_id") if k in manifest]
    if not tasks or any(t!=TASK for t in tasks):
        raise ContractError("named identity role task mismatch")
    if manifest.get("agent_role")!=role or manifest.get("epoch_id")!=candidate["epoch_id"]:
        raise ContractError("named identity role/epoch mismatch")
    if manifest.get("reviewed_candidate_sha256")!=candidate_sha:
        raise ContractError("named role candidate drift")
    if manifest.get("registry_files_sha256")!=CURRENT_REGISTRY_FILES_SHA256:
        raise ContractError("named role permanent registry mismatch")
    stamp=manifest.get("timestamp",manifest.get("created_at"))
    try:
        dt=datetime.fromisoformat(stamp.replace("Z","+00:00"))
    except (TypeError,ValueError,AttributeError):
        raise ContractError("named role timestamp missing or invalid") from None
    if dt.tzinfo is None or dt>datetime.now(timezone.utc):
        raise ContractError("named role timestamp must be actual timezone-aware past")
    inputs=manifest.get("input_manifest_sha")
    if not isinstance(inputs,dict) or not inputs:
        raise ContractError("named role input manifest required")
    for path,digest in inputs.items():
        bound_file(root,{"path":path,"sha256":digest})
    outputs=manifest.get("output_file_sha256",manifest.get("output_file_sha"))
    if not isinstance(outputs,dict) or outputs.get(binding["path"])!=binding["sha256"]:
        raise ContractError("named role output does not bind review")
    if "output_file_sha256" in manifest and "output_file_sha" in manifest and manifest["output_file_sha256"]!=manifest["output_file_sha"]:
        raise ContractError("named role output aliases conflict")
    counts=manifest.get("counts")
    expected={"processed":28,"passed":28,"rejected":0,"pending":0}
    if not isinstance(counts,dict) or any(type(counts.get(k)) is not int or counts[k]!=v for k,v in expected.items()):
        raise ContractError("all 28 named comparisons must pass without pending")
    if manifest.get("errors")!=[] or manifest.get("unprocessed")!=[]:
        raise ContractError("named role errors or unprocessed comparisons remain")
    if type(manifest.get("read_holdout")) is not bool or manifest.get("read_model_outcome") is not False or manifest.get("scope_modified") is not False:
        raise ContractError("named role holdout/model/scope boundary incomplete")
    if manifest.get("approval_type")!="agent_delegated" or manifest.get("human_reviewed") is not False:
        raise ContractError("named role approval attribution mismatch")
    pointers=manifest.get("source_evidence_pointers")
    if not isinstance(pointers,list) or not pointers:
        raise ContractError("named role source pointers required")
    for p in pointers:
        bound_file(root,p)

def validate_current_named_exposure_review(candidate, *, root, registry_files_sha256=None):
    _bound_dependencies(root)
    if registry_files_sha256 is not None and registry_files_sha256!=CURRENT_REGISTRY_FILES_SHA256:
        raise ContractError("current permanent name registry cannot be replaced or subset")
    if candidate.get("family") not in ("C","SS") or not isinstance(candidate.get("epoch_id"),str) or not candidate["epoch_id"].startswith(candidate["family"]+"-E"):
        raise ContractError("named candidate family/epoch missing")
    registry=load_name_registry(root,CURRENT_REGISTRY_FILES_SHA256)
    if len(registry)!=28:
        raise ContractError("permanent name record universe changed")
    binding=candidate.get("named_exposure_review")
    review=json.loads(bound_file(root,binding).read_text())
    candidate_sha=json_sha({k:v for k,v in candidate.items() if k!="named_exposure_review"})
    if review.get("candidate_sha256")!=candidate_sha or review.get("registry_files_sha256")!=CURRENT_REGISTRY_FILES_SHA256:
        raise ContractError("named review candidate/registry drift")
    if review.get("read_model_outcome") is not False or review.get("scope_modified") is not False:
        raise ContractError("named review model/scope boundary incomplete")
    roles=binding.get("role_manifests")
    if not isinstance(roles,dict) or set(roles)!={"A3","A6"}:
        raise ContractError("named review requires both fixed responsible roles")
    for role,pointer in roles.items():
        _role_review(root,role,pointer,binding,candidate,candidate_sha)
    checks=review.get("comparisons")
    if not isinstance(checks,list) or len(checks)!=28:
        raise ContractError("all 28 named comparisons required")
    seen=set()
    for check in checks:
        key=check.get("exposure_id")
        if key not in registry or key in seen or check.get("exposure_record_sha256")!=registry[key]["record_sha256"]:
            raise ContractError("named exposure record missing/duplicate/drift")
        seen.add(key)
        if check.get("decision")!="no_match":
            raise ContractError("matched or unresolved permanent name exposure")
        if check.get("identity_chain_verified") is not True or check.get("name_only_inference") is not False:
            raise ContractError("unverified named comparison")
        if not isinstance(check.get("reaction_context_reason"),str) or not check["reaction_context_reason"].strip():
            raise ContractError("named reaction-context reason required")
        pointers=check.get("official_identity_evidence")
        if not isinstance(pointers,list) or not pointers:
            raise ContractError("named comparison official evidence required")
        for p in pointers:
            if p.get("kind") not in ("official_source_identity","official_structure_database_identity") or not isinstance(p.get("locator"),str) or not p["locator"].strip():
                raise ContractError("official named identity locator required")
            bound_file(root,p)
    return {"candidate_sha256":candidate_sha,"permanent_name_records_compared":28,"matched":0,"unresolved":0,"documentary_gate_passed":True,"chemical_identity_automatically_verified":False,"fresh_admission_established":False}

def validate_final_panel(records, epoch, scopes, exposures=(), build=(), runtime_instances=(),
                         *, root, enforce_floor=True, registry_files_sha256=None):
    if enforce_floor is not True:
        raise ContractError("final P7 panel completion floor cannot be disabled")
    _bound_dependencies(root)
    if registry_files_sha256 is not None and registry_files_sha256!=CURRENT_REGISTRY_FILES_SHA256:
        raise ContractError("current permanent registry cannot be replaced or subset")
    if len(load_name_registry(root,CURRENT_REGISTRY_FILES_SHA256))!=28:
        raise ContractError("permanent name record universe changed")
    reviews=[validate_current_named_exposure_review(row,root=root) for row in records]
    from scripts.task016_p7_panel_harness import validate_panel
    result=validate_panel(records,epoch,scopes,exposures,build,runtime_instances,enforce_floor=True)
    if result.get("completion_floor_passed") is not True:
        raise ContractError("final P7 panel completion floor unproven")
    return {**result,"named_exposure_documentary_checks":reviews,"permanent_name_record_universe":28}
