"""SS scope freeze requires external independent A3/A5 qualification."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,save,save_rows,sha,rows,now
from flavoretro.reviewed_resources import canonical_side
from flavoretro.glycoside_scope_ss_v7 import apply_template
from scripts.operate import event
def freeze(verification_path,preflight_path):
    if (OUT/"scope_freeze.json").exists():raise RuntimeError("SS_SCOPE_BANK_ALREADY_FROZEN")
    path=ROOT/verification_path
    v=json.loads(path.read_text())
    preflight=ROOT/preflight_path
    pre=json.loads(preflight.read_text())
    for field in ["agent_role","passed","qualification_path","qualification_sha256","verified_input_files_sha256"]:
        if field not in pre:raise RuntimeError("EXTERNAL_PREFLIGHT_SCHEMA_MISSING:"+field)
    if pre["agent_role"]!="A8" or pre["passed"] is not True:raise RuntimeError("INDEPENDENT_SCOPE_PREFLIGHT_REQUIRED")
    if pre["qualification_path"]!=str(path.relative_to(ROOT)) or pre["qualification_sha256"]!=sha(path):raise RuntimeError("SCOPE_PREFLIGHT_QUALIFICATION_SHA_MISMATCH")
    required=json.loads((OUT/"scope_independent_preflight_request.json").read_text())["requested_input_files_sha256"]
    for rp,rh in required.items():
        if pre["verified_input_files_sha256"].get(rp)!=rh:raise RuntimeError("PREFLIGHT_REQUIRED_FORMAL_INPUT_MISSING_OR_DIFFERENT:"+rp)
    for p,h in pre["verified_input_files_sha256"].items():
        if sha(ROOT/p)!=h:raise RuntimeError("PREFLIGHT_INPUT_SHA_DRIFT")
    for field in ["agent_role","passed","source_identity_verified","dual_structure_reconciled","approved_scope_ids","approved_reaction_ids","input_manifest_sha","verified_input_files_sha256"]:
        if field not in v:raise RuntimeError("INDEPENDENT_VERIFICATION_SCHEMA_MISSING:"+field)
    if v["agent_role"] not in ["A6","A6 Reconciliation & Closure Auditor","A3/A5/A6 independent qualification"]:raise RuntimeError("SCOPE_BUILDER_CANNOT_QUALIFY_OWN_SOURCE")
    if not all(v[field] is True for field in ["passed","source_identity_verified","dual_structure_reconciled"]):raise RuntimeError("SOURCE_OR_DUAL_STRUCTURE_NOT_QUALIFIED")
    if v["input_manifest_sha"]!=sha(OUT/"design_source_input_manifest.json"):raise RuntimeError("RAW_INPUT_MANIFEST_SHA_DRIFT")
    for verified_path,verified_sha in v["verified_input_files_sha256"].items():
        if sha(ROOT/verified_path)!=verified_sha:raise RuntimeError("INDEPENDENT_QUALIFICATION_INPUT_SHA_DRIFT")
    raw=json.loads((OUT/"design_source_input_manifest.json").read_text())
    for p,h in raw["raw_input_files_sha256"].items():
        if sha(ROOT/p)!=h:raise RuntimeError("RAW_INPUT_FILE_SHA_DRIFT")
    templates=[t for t in rows(OUT/"scope_templates_formal.jsonl") if t["template_id"] in v["approved_scope_ids"]]
    supports=[r for r in rows(OUT/"design_extractor_A4.jsonl") if r["instance_id"] in v["approved_reaction_ids"]]
    if set(v["approved_scope_ids"])!={t["template_id"] for t in templates}:raise RuntimeError("UNKNOWN_QUALIFIED_SCOPE_ID")
    replay=json.loads((OUT/"scope_build_replay.json").read_text());boundary=json.loads((OUT/"scope_boundaries.json").read_text())
    for t in templates:
        members=[r for r in supports if r["instance_id"] in t["support_instances"]]
        if len(members)!=len(t["support_instances"]) or len({canonical_side([r["acceptor"]]) for r in members})<2:raise RuntimeError("QUALIFIED_SCOPE_DISTINCT_ACCEPTOR_OR_SUPPORT_MISSING")
        if any(canonical_side(r["reference_precursors"]) not in [o["precursors"] for o in apply_template(t,r["target"])] for r in members):raise RuntimeError("FORMAL_GUARD_SUPPORT_REPLAY_FAILED")
        bs=[b for b in boundary["records"] if b["scope_id"]==t["template_id"]]
        if len(bs)<6 or any(apply_template(t,b["target"]) for b in bs):raise RuntimeError("BOUNDARY_GATE_FAILED")
        t["validation_status"]="source_reconstruction_passed"
        t["source_qualification"]=dict(verification_path=str(path.relative_to(ROOT)),verification_sha256=sha(path),input_manifest_sha=v["input_manifest_sha"],human_reviewed=False)
    for r in supports:
        r["structure_complete"]=True;r["evidence_eligible"]=True;r["chemical_admission"]="independently_source_identity_and_dual_graph_qualified"
        r["independent_qualification"]=dict(path=str(path.relative_to(ROOT)),sha256=sha(path))
    save_rows("templates.jsonl",templates);save_rows("runtime_instances.jsonl",supports)
    paths=["templates.jsonl","runtime_instances.jsonl","design_source_input_manifest.json","design_exact_templates.jsonl","formal_runtime_projection.json","scope_templates_formal.jsonl","scope_boundary_plan.json","scope_build_replay.json","scope_boundaries.json"]
    files={str((OUT/p).relative_to(ROOT)):sha(OUT/p) for p in paths}
    files["flavoretro/glycoside_scope_ss_v7.py"]=sha(ROOT/"flavoretro/glycoside_scope_ss_v7.py")
    files[str(path.relative_to(ROOT))]=sha(path)
    files[str(preflight.relative_to(ROOT))]=sha(preflight)
    save("scope_freeze.json",dict(task_id="TASK-016-P7",epoch_id="SS-E01",family="SS",frozen_at=now(),agent_role="A7 Scope Builder; independent A3/A5/A6 qualification consumed",independently_verified=True,scope_ids=[t["template_id"] for t in templates],qualified_scopes=len(templates),qualified_supports=len(supports),build_replay=sum(len(t["support_instances"]) for t in templates),boundary_violations=0,read_holdout=False,read_model_outcomes=False,files_sha256=files,approval_type="agent_delegated",human_reviewed=False))
    save("A7_SS_scope_freeze_manifest.json",dict(agent_role="A7 Scope Builder",task_id="TASK-016-P7",epoch_id="SS-E01",at=now(),input_manifest_sha=sha(path),output_sha256={"scope_freeze.json":sha(OUT/"scope_freeze.json"),**files},source_evidence_authority="external independent A3/A5/A6 verification only",processed_scopes=len(templates),passed_scopes=len(templates),errors=[],read_holdout=False,read_model_outcomes=False))
    event("TASK-016-P7","SS_scope_bank_frozen",epoch_id="SS-E01",sha256=sha(OUT/"scope_freeze.json"),scopes=len(templates))
    print(dict(scope_freeze_sha256=sha(OUT/"scope_freeze.json"),scopes=len(templates),supports=len(supports)))
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("verification_path");parser.add_argument("preflight_path");args=parser.parse_args();freeze(args.verification_path,args.preflight_path)
