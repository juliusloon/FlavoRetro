"""Final panel adapter additionally checks every declared review-role output."""
import json
from scripts import task016_p7_named_exposure_gate_v3 as v3
from scripts.task016_p7_named_exposure_gate_v1 import bound_file
from scripts.task016_p7_orchestrate import ContractError
V3_SHA = 'c6612d267cb56ffdcd36296332f829bde9f466349faeecf6bb9d0a17ed6963c9'
def _check_all_role_outputs(candidate, root):
    bound_file(root,{"path":"scripts/task016_p7_named_exposure_gate_v3.py","sha256":V3_SHA})
    binding=candidate.get("named_exposure_review")
    if not isinstance(binding,dict) or not isinstance(binding.get("role_manifests"),dict) or set(binding["role_manifests"])!={"A3","A6"}:
        raise ContractError("both named review roles required")
    for pointer in binding["role_manifests"].values():
        manifest=json.loads(bound_file(root,pointer).read_text())
        outputs=manifest.get("output_file_sha256",manifest.get("output_file_sha"))
        if not isinstance(outputs,dict) or not outputs:
            raise ContractError("all declared role outputs required")
        for path,digest in outputs.items():
            bound_file(root,{"path":path,"sha256":digest})

def validate_current_named_exposure_review(candidate, *, root, registry_files_sha256=None):
    _check_all_role_outputs(candidate,root)
    return v3.validate_current_named_exposure_review(candidate,root=root,registry_files_sha256=registry_files_sha256)

def validate_final_panel(records, epoch, scopes, exposures=(), build=(), runtime_instances=(),
                         *, root, enforce_floor=True, registry_files_sha256=None):
    if enforce_floor is not True:
        raise ContractError("final P7 panel completion floor cannot be disabled")
    bound_file(root,{"path":"scripts/task016_p7_named_exposure_gate_v3.py","sha256":V3_SHA})
    for row in records:
        _check_all_role_outputs(row,root)
    return v3.validate_final_panel(records,epoch,scopes,exposures,build,runtime_instances,
      root=root,enforce_floor=True,registry_files_sha256=registry_files_sha256)
