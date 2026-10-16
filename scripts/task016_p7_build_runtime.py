"""Assemble immutable v7 payload from independently qualified frozen family banks."""
import json
from pathlib import Path
from rdkit import rdBase
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import sha_file,save_json,now
from flavoretro.glycoside_library_v6 import load_registry as load_v6
from flavoretro.reviewed_resources import canonical_side,reaction_signature
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1"
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def main():
    target=O/"runtime"
    if (target/"template_source_manifest.json").exists():raise RuntimeError("v7 scientific runtime already frozen; new version required")
    banks=[];templates=[];instances=[];projections=[]
    c=O/"C/E01/scope_manifest.json";ss=O/"SS/scope_freeze.json"
    if c.exists():
        banks.append(dict(path=str(c.relative_to(R)),sha256=sha_file(c)))
        source_templates=json.loads((c.parent/"scope_bank.json").read_text())
        source_instances=json.loads((c.parent/"build_supports.json").read_text())
        qualification=c.parent/"design_independent_qualification.json"
        preflight=c.parent/"A8_independent_preflight.json"
        q=json.loads(qualification.read_text());a8=json.loads(preflight.read_text())
        if q.get("passed") is not True or a8.get("passed") is not True:raise RuntimeError("C source qualification/A8 incomplete")
        if {t["template_id"] for t in source_templates}!=set(q["approved_scope_ids"]) or {i["instance_id"] for i in source_instances}!=set(q["approved_reaction_ids"]):raise RuntimeError("C runtime projection changed scientific ID universe")
        for t in source_templates:
            if t["validation_status"]!="source_identity_and_dual_structure_qualified_scope_replayed_boundary_passed":raise RuntimeError("C source status unqualified")
            value=dict(t,validation_status="source_reconstruction_passed",source_qualification=dict(verification_path=str(qualification.relative_to(R)),verification_sha256=sha_file(qualification),human_reviewed=False))
            templates.append(value)
        for i in source_instances:
            if i.get("evidence_eligible") is not True or i.get("source_identity_status")!="independently_verified_A3" or i.get("dual_structure_status")!="reconciled_A6_with_explicit_donor_serialization":raise RuntimeError("C source support unqualified")
            signature=reaction_signature([canonical_side(i["reference_precursors"])],[canonical_side([i["target"]])])
            instances.append(dict(i,template_role="development_build",structure_complete=True,reference_precursor_complete=True,reference_signature=signature))
        projections.append(dict(family="C",science_changed=False,metadata_only=True,template_fields_added_or_normalized=["validation_status","source_qualification"],instance_fields_added=["template_role","structure_complete","reference_precursor_complete","reference_signature"],source_scope_manifest_sha256=sha_file(c),source_qualification_sha256=sha_file(qualification),independent_A8_sha256=sha_file(preflight),original_templates_sha256=sha_file(c.parent/"scope_bank.json"),original_supports_sha256=sha_file(c.parent/"build_supports.json"),original_frozen_files_preserved=True))
    if ss.exists():
        banks.append(dict(path=str(ss.relative_to(R)),sha256=sha_file(ss)))
        templates.extend(rows(ss.parent/"templates.jsonl"));instances.extend(rows(ss.parent/"runtime_instances.jsonl"))
    if not templates:raise RuntimeError("no qualified frozen P7 scope bank")
    for t in templates:
        if t["validation_status"]!="source_reconstruction_passed":raise RuntimeError("unqualified scope")
    for inst in instances:
        if inst["template_role"]!="development_build" or inst.get("human_reviewed") is not False:raise RuntimeError("invalid runtime source role")
        if inst.get("structure_complete") is not True:raise RuntimeError("incomplete structure in runtime")
        actual=reaction_signature([canonical_side(inst["reference_precursors"])],[canonical_side([inst["target"]])])
        if actual!=inst["reference_signature"]:raise RuntimeError("runtime reference signature mismatch")
    if len({x["template_id"] for x in templates})!=len(templates) or len({x["instance_id"] for x in instances})!=len(instances):raise RuntimeError("duplicate P7 science IDs")
    for name,v in [("templates.jsonl",templates),("runtime_instances.jsonl",instances)]:
        write("TASK-016-P7",str((target/name).relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in v))
    save_json(target/"runtime_projection.json",dict(projections=projections,scope_manifests=banks,only_source_qualified_build_inputs=True),immutable=True)
    v6=load_v6();parent=R/v6.binding["manifest"]
    manifest=dict(schema_version=2,version="task016-p7-v7",rdkit=rdBase.rdkitVersion,default_enabled=False,created_at=now(),files_sha256={n:sha_file(target/n) for n in ["templates.jsonl","runtime_instances.jsonl","runtime_projection.json"]},qualified_v6=dict(manifest=str(parent.relative_to(R)),sha256=sha_file(parent)),scope_manifests=banks,policy=v6.settings,review_binding=json.loads(parent.read_text())["review_binding"],holdout_in_runtime=False,human_reviewed=False,actionable=False,evidence_closed=False,prediction_conditions_verified=False)
    save_json(target/"template_source_manifest.json",manifest,immutable=True)
    settings=dict(default_enabled=False,manifest=str((target/"template_source_manifest.json").relative_to(R)),manifest_sha256=sha_file(target/"template_source_manifest.json"))
    for name in ["configs/glycoside-library-v7.json","flavoretro/assets/configs/glycoside-library-v7.json"]:
        write("TASK-016-P7",name,json.dumps(settings,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    from flavoretro.glycoside_library_v7 import load_registry,apply_template
    registry=load_registry();checks=[]
    for inst in instances:
        supporting=[registry.by_id[tid] for tid in registry.by_id if inst["instance_id"] in registry.by_id[tid]["support_instances"]]
        passed=any(canonical_side(inst["reference_precursors"]) in [o["precursors"] for o in apply_template(t,inst["target"])] for t in supporting)
        checks.append(dict(instance_id=inst["instance_id"],passed=passed))
    save_json(target/"build_replay.json",dict(passed=all(c["passed"] for c in checks),checks=checks,templates=len(registry.templates),instances=len(registry.instances),increment_templates=len(templates),increment_instances=len(instances),binding=registry.binding))
    if not all(x["passed"] for x in checks):raise RuntimeError("v7 registry build replay failed")
    event("TASK-016-P7","v7_runtime_frozen",templates=len(registry.templates),instances=len(registry.instances),increment_templates=len(templates),increment_instances=len(instances),manifest_sha256=settings["manifest_sha256"])
    print(dict(templates=len(registry.templates),instances=len(registry.instances),new_scopes=len(templates),new_supports=len(instances),replayed=len(checks)))
if __name__=="__main__":main()
