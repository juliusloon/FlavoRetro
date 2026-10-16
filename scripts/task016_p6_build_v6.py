"""G4 construct a qualified v3-based runtime, including the frozen P6 C scope.

Scientific preflight failures stop only their fresh matrices; engineering runtime
and legacy checks remain authorized. No panel instance enters this registry.
"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
from scripts.operate import write
from rdkit import rdBase

def main():
    if (OUT/"template_source_manifest.json").exists():raise RuntimeError("v6 runtime is already frozen")
    cm=load("c_scope_manifest.json")
    assert all(sha(OUT/n)==h for n,h in cm["files_sha256"].items())
    templates=rows(ROOT/"outputs/task016-p4/v1/templates.jsonl")+[load("c_scope_template.json")]
    instances=rows(ROOT/"outputs/task016-p4/v1/runtime_instances.jsonl")+rows(OUT/"c_build_supports.jsonl")
    assert len(templates)==2 and len(instances)==4
    save_rows("templates.jsonl",templates);save_rows("runtime_instances.jsonl",instances)
    parent=ROOT/"outputs/task016-p2/v2/template_source_manifest.json"
    manifest=dict(schema_version=2,version="task016_p6_v6",rdkit=rdBase.rdkitVersion,
      policy=dict(default_enabled=False,domain_cap_per_molecule=4,generic_protection=3,prior=0.2,weight=1.),
      files_sha256={n:sha(OUT/n) for n in ["templates.jsonl","runtime_instances.jsonl"]},
      review_binding=json.loads((ROOT/"outputs/task016-p4/v1/template_source_manifest.json").read_text())["review_binding"],
      qualified_v3=dict(manifest=str(parent.relative_to(ROOT)),sha256=sha(parent)),
      c_scope_manifest_sha256=sha(OUT/"c_scope_manifest.json"),holdout_in_runtime=False,
      excluded_by_construction=["C_hydroxyflavanone_C3","rhamnoside_glucoside_O6"],
      actionable=False,evidence_closed=False,prediction_conditions_verified=False,human_reviewed=False)
    save("template_source_manifest.json",manifest)
    settings=dict(default_enabled=False,manifest="outputs/task016-p6/v1/template_source_manifest.json",manifest_sha256=sha(OUT/"template_source_manifest.json"))
    encoded=json.dumps(settings,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    for path in ["configs/glycoside-library-v6.json","flavoretro/assets/configs/glycoside-library-v6.json"]:write(TASK,path,encoded)
    from flavoretro.glycoside_library_v6 import load_registry,GlycosideExpansion,DomainAwareQuickFilter
    from aizynthfinder.context.config import Configuration
    from aizynthfinder.chem import TreeMolecule
    from flavoretro.reviewed_resources import load_review,canonical_side
    r=load_registry();replay=[]
    exp=GlycosideExpansion("glycoside",Configuration());fil=DomainAwareQuickFilter("glycoside",Configuration(),model=str(ROOT/"data/raw/legacy/data/uspto_filter_model.onnx"))
    for inst in instances:
        mol=TreeMolecule(parent=None,smiles=inst["target"])
        actions,priors=exp.get_actions([mol]);found=False; evid=[]
        for action in actions:
            for i,outcome in enumerate(action.reactants):
                a=action.copy(index=i);fil.apply(a)
                ev=r.evidence(a);evid.append(ev)
                if canonical_side([m.smiles for m in outcome])==canonical_side(inst["reference_precursors"]):found=True
        replay.append(dict(instance_id=inst["instance_id"],reaction_id=inst.get("reaction_id"),passed=found,evidence=evid))
    assert all(x["passed"] for x in replay)
    save("v6_runtime_build_replay.json",dict(passed=sum(x["passed"] for x in replay),total=len(replay),replay=replay,binding=r.binding))
    review=load_review()
    save("runtime_baseline.json",dict(v3_manifest_sha256=sha(parent),v6_binding=r.binding,stock_keys=sorted(review.keys),review_binding=review.binding,
         code_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/"flavoretro").glob("*.py")},
         models_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/"data/raw/legacy/data").glob("*.onnx")}))
    print(dict(templates=len(r.templates),instances=len(r.instances),runtime_replay=f"{sum(x['passed'] for x in replay)}/{len(replay)}",stock_keys=len(review.keys)))
if __name__=="__main__":main()
