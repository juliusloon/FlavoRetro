"""Freeze a new exact source-reconstruction registry; no source cache overwritten."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from flavoretro.resources import sha,dumps
from flavoretro.reaction_intake import canonical_side,local_path
import operate


def build(output="outputs/task022/literature/v1"):
    output=ROOT/output
    if output.exists():raise ValueError("registry version already exists")
    intake_path=ROOT/"outputs/task022/intake/v1/records.json"
    screening_path=ROOT/"outputs/task022/sources/development/exact_reconstruction_screen.json"
    records=json.loads(intake_path.read_text())
    screen=json.loads(screening_path.read_text())
    approvals={r["reaction_id"]:r for r in screen["records"]}
    selected=[];excluded=[]
    assets={str(intake_path.relative_to(ROOT)):sha(intake_path),str(screening_path.relative_to(ROOT)):sha(screening_path)}
    for record in records:
        decision=approvals.get(record["reaction_id"],{})
        if not decision.get("exact_source_reconstruction_candidate") or not decision.get("source_primary_pair_explicit") or record["qc"]["status"]!="source_bound_structure_candidate":
            excluded.append({"reaction_id":record["reaction_id"],"reason":decision.get("cautions",["missing explicit source-reconstruction approval"])})
            continue
        target,t_issues=canonical_side(record["products"])
        precursors,p_issues=canonical_side(record["reactants"])
        if not target or not precursors or t_issues or p_issues or len(record["products"])!=1:
            raise ValueError("invalid selected participants")
        for participants in (record["reactants"],record["products"]):
            for p in participants:
                identity=p["identity_source"]
                path=local_path(identity["snapshot_path"])
                if sha(path)!=identity["snapshot_sha256"]:raise ValueError("identity source drift")
                assets[str(path.relative_to(ROOT))]=sha(path)
        source=record["source"];path=local_path(source["local_path"])
        if sha(path)!=source["sha256"]:raise ValueError("primary source drift")
        assets[str(path.relative_to(ROOT))]=sha(path)
        selected.append({**record,"target":target,"precursors":precursors,
                         "exact_reconstruction_approved":True,"approval":"agent_delegated",
                         "scope_transfer_evidence":False,"review_cautions":decision.get("cautions",[]),
                         "runtime_role":"opt_in_exact_source_lookup_only"})
    relative=output.relative_to(ROOT)
    operate.write("TASK-022",str(relative/"records.json"),dumps(selected))
    operate.write("TASK-022",str(relative/"excluded.json"),dumps(excluded))
    manifest={"kind":"exact_source_reaction_registry","version":"task022-literature-v1",
              "records":str(relative/"records.json"),"records_sha256":sha(output/"records.json"),
              "assets":assets,"approval":"agent_delegated","human_reviewed":False,
              "default_enabled":False,"policy":{"prior":0.15,"scope":"exact_target_only"},
              "summary":{"records":len(selected),"targets":len({r["target"] for r in selected}),
                         "sources":len({r["source"]["doi"] for r in selected}),"excluded":len(excluded)},
              "boundary":"来源精确首步检索；不是范围迁移、实验验证或完整原子平衡方程。来源条件仅作上下文。"}
    operate.write("TASK-022",str(relative/"manifest.json"),dumps(manifest))
    print(json.dumps(manifest["summary"],ensure_ascii=False))


if __name__=="__main__":build(sys.argv[1] if len(sys.argv)>1 else "outputs/task022/literature/v1")
