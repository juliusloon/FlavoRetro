"""Production gate pinned to the complete current permanent-name registry."""
from scripts.task016_p7_named_exposure_gate_v1 import load_name_registry,validate_named_exposure_review
from scripts.task016_p7_orchestrate import ContractError

CURRENT_REGISTRY_FILES_SHA256 = {'outputs/task016-p7/v1/C/E02/pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl': '63de4b790ef33fcf95bbe28808ff1187c46d82eb77b8fa5cce8e1c49ead6c3ea', 'outputs/task016-p7/v1/C/E02/post_scope_internal_hypotheses/v1/permanent_name_hypothesis_exposure.jsonl': '3b756dc6532bfb5007c5193fac784e76a89e5e7faf25520108f5174d5fd468fb', 'outputs/task016-p7/v1/SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_unverified_name_exposures.jsonl': '61b37f18c0bfb6862751dd2ca9075ed8ed52bdbaaec8c94d6488076604be5138'}
CURRENT_PERMANENT_NAME_RECORDS = 28

def validate_current_named_exposure_review(candidate, *, root, registry_files_sha256=None):
    registry=CURRENT_REGISTRY_FILES_SHA256
    if registry_files_sha256 is not None and registry_files_sha256!=registry:
        raise ContractError("current permanent name registry cannot be replaced or subset")
    if len(load_name_registry(root,registry))!=CURRENT_PERMANENT_NAME_RECORDS:
        raise ContractError("current permanent name record universe changed")
    return validate_named_exposure_review(candidate,registry,root=root)

def validate_current_panel(records, epoch, scopes, exposures=(), build=(),
                           runtime_instances=(), *, root, enforce_floor=True,
                           registry_files_sha256=None):
    if registry_files_sha256 is not None and registry_files_sha256!=CURRENT_REGISTRY_FILES_SHA256:
        raise ContractError("current permanent name registry cannot be replaced or subset")
    if len(load_name_registry(root,CURRENT_REGISTRY_FILES_SHA256))!=28:
        raise ContractError("current permanent name record universe changed")
    reviews=[validate_current_named_exposure_review(row,root=root) for row in records]
    from scripts.task016_p7_panel_harness import validate_panel
    result=validate_panel(records,epoch,scopes,exposures,build,runtime_instances,enforce_floor=enforce_floor)
    return {**result,"named_exposure_documentary_checks":reviews,"permanent_name_record_universe":28}
