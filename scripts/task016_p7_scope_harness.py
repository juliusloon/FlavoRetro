"""P7 scope replay/boundary audit and immutable, pre-holdout scientific freeze."""
import json
from pathlib import Path
from scripts.task016_p7_orchestrate import ContractError,require_fields,sha_file,sha_json,save_json,now
from flavoretro.reviewed_resources import canonical_side

def validate_scope_bank(bank,build_supports,replay,boundaries):
    if not isinstance(bank,list) or not bank:
        raise ContractError("empty scope bank")
    supports={r["instance_id"]:r for r in build_supports}
    if len(supports)!=len(build_supports): raise ContractError("duplicate support IDs")
    seen=set()
    report=[]
    for t in bank:
        require_fields(t,("template_id","support_instances","exact_sha256","scope_sha256","template_role","scope","scope_transformation"))
        tid=t["template_id"]
        if tid in seen:raise ContractError("duplicate scope ID")
        seen.add(tid)
        if t["template_role"]!="scope_template" or t["exact_sha256"]==t["scope_sha256"]:
            raise ContractError("exact replay masquerading as scope")
        ids=t["support_instances"]
        if len(set(ids))!=len(ids) or not set(ids)<=set(supports):raise ContractError("support universe mismatch")
        if len({canonical_side([supports[i]["acceptor"]]) for i in ids})<2:
            raise ContractError("scope needs two distinct canonical acceptors")
        trials=[r for r in replay if r["template_id"]==tid]
        if len(trials)!=len(ids) or {r["instance_id"] for r in trials}!=set(ids) or any(r["passed"] is not True for r in trials):
            raise ContractError("build support replay incomplete")
        controls=[r for r in boundaries if r["template_id"]==tid]
        if len(controls)<6 or len({r["control_id"] for r in controls})!=len(controls):
            raise ContractError("minimum six distinct preregistered controls required")
        if any(r["violated"] is not False for r in controls):raise ContractError("boundary violation")
        report.append(dict(template_id=tid,build_supports=len(ids),replay=len(trials),boundary_controls=len(controls),boundary_violations=0))
    if any(r["template_id"] not in seen for r in replay+boundaries):raise ContractError("unbound scope audit rows")
    return dict(passed=True,scopes=len(bank),scope_audits=report)

def replay_scope_bank(bank,supports):
    from flavoretro.glycoside_library_v7 import apply_template
    by_id={r["instance_id"]:r for r in supports}
    rows=[]
    for t in bank:
        for iid in t["support_instances"]:
            r=by_id[iid];outcomes=apply_template(t,r["target"])
            expected=canonical_side(r["reference_precursors"])
            rows.append(dict(template_id=t["template_id"],instance_id=iid,reference_precursors=expected,outcomes=outcomes,passed=expected in [o["precursors"] for o in outcomes]))
    return rows

def freeze_scope_bank(folder,bank,supports,replay,boundaries,identity,structure, *, family,epoch_id,additional_files=(),production_guard=None):
    folder=Path(folder)
    if (folder/"scope_manifest.json").exists():raise ContractError("scope already frozen; new epoch required")
    check=validate_scope_bank(bank,supports,replay,boundaries)
    if any(r.get("source_identity_verified") is not True for r in identity):raise ContractError("source identity not verified")
    if any(r.get("reconciled") is not True for r in structure):raise ContractError("dual structures not reconciled")
    # An upstream rejection cannot be hidden by omission of its support row.
    if {r["instance_id"] for r in structure}!={r["instance_id"] for r in supports}:raise ContractError("structure/support universe mismatch")
    if {r["pmcid"] for r in identity}!={r["provenance"]["pmcid"] for r in supports}:raise ContractError("source/support universe mismatch")
    paths=[]
    for n,v in [("scope_bank.json",bank),("build_supports.json",supports),("build_replay.json",replay),("boundary_results.json",boundaries),("source_identity.json",identity),("dual_structure_reconciliation.json",structure)]:
        save_json(folder/n,v,immutable=True);paths.append(folder/n)
    from scripts.task016_p7_orchestrate import ROOT
    bindings={p.name:sha_file(p) for p in paths}
    extra=list(additional_files)+([production_guard] if production_guard is not None else [])
    for value in extra:
        p=Path(value)
        p=p.resolve() if p.is_absolute() else (ROOT/p).resolve()
        if not p.is_relative_to(ROOT.resolve()) or not p.is_file():raise ContractError("additional scope evidence absent/outside workspace")
        bindings[str(p.relative_to(ROOT))]=sha_file(p)
    manifest=dict(task="TASK-016-P7",family=family,epoch_id=epoch_id,frozen_at=now(),files_sha256=bindings,scope_bank_sha256=sha_file(folder/"scope_bank.json"),scope_audit=check,holdout_extraction_started=False,read_model_outcome=False,review_type="agent_delegated",human_reviewed=False)
    save_json(folder/"scope_manifest.json",manifest,immutable=True)
    return manifest
