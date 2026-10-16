"""Frozen historical ID regression; no fresh holdout or transfer claim."""
import json,os,sys
from pathlib import Path
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import sha_file,save_json,now
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.reviewed_resources import load_review,canonical_side,reaction_signature
from flavoretro.open_glycoside_library import normalize_species
from flavoretro.glycoside_library_v7 import load_registry
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/regression"
PARAMETERS=dict(mode="quick",engine="optimized",seconds=12.0,iterations=20,depth=2,branching=12,nodes=120,top_k=5)
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def freeze():
    path=O/"contract.json"
    if path.exists():return json.loads(path.read_text())
    old=R/"outputs/task016-p6/v1/experiment_contract.json"
    p1metrics=R/"outputs/task016-p1/v2/metrics.json"
    p1refs=R/"outputs/task016-p1/v2/holdout_views.jsonl"
    taskrefs=R/"outputs/task016/v1/instances.jsonl"
    parent=json.loads(old.read_text());refs=parent["references"]
    gained=set(json.loads(p1metrics.read_text())["actual_mcts"]["gain_targets"])
    p1canaries=[dict(instance_id=x["instance_id"],target=x["target"],reference_signatures=[x["reference_signature"]],reference_precursors=x["reference_precursors"],canary_kind="P1_frozen_success") for x in rows(p1refs) if x["target"] in gained]
    if len(p1canaries)!=7:raise ValueError("frozen P1 canary ID universe drift")
    oldcanaries=[]
    for x in rows(taskrefs):
        precursor=[normalize_species(p)["normalized"] for p in x["reference_precursors"]]
        target=normalize_species(x["target"])["normalized"]
        signature=reaction_signature([canonical_side(precursor)],[target])
        oldcanaries.append(dict(instance_id=x["instance_id"],target=x["target"],reference_signatures=[signature],raw_reference_signature=x["reference_signature"],reference_precursors=precursor,canary_kind="TASK016_frozen_exact",representation_rule="existing normalize_species protonation normalization only; original source ID/graph/signature preserved"))
    if len(oldcanaries)!=4:raise ValueError("TASK016 canary ID universe drift")
    unique={x["target"] for x in refs+oldcanaries+p1canaries}
    matrix=[dict(target=t,seed=s,arm="E") for t in sorted(unique) for s in [0,1,2]]
    if len(matrix)>90:raise ValueError("legacy/canary budget exceeded")
    registry=load_registry();review=load_review()
    code=list((R/"flavoretro").glob("*.py"))+[R/"scripts/task016_p7_regression.py"]
    protected=[old,p1metrics,p1refs,taskrefs,R/"outputs/task016-p6/v1/e_regression.json",R/registry.binding["manifest"],R/"configs/search.json",R/"configs/glycoside-library-v7.json"]
    models={x["path"]:x["sha256"] for x in json.loads((R/"metadata/sources.json").read_text())["files"] if x["role"]=="external_model"}
    contract=dict(task="TASK-016-P7",phase="final_v7_old17_and_frozen_TASK016_P1_canaries",frozen_at=now(),parameters=PARAMETERS,seeds=[0,1,2],references=refs,TASK016_exact_canaries=oldcanaries,P1_success_canaries=p1canaries,matrix=matrix,files_sha256={str(p.relative_to(R)):sha_file(p) for p in code+protected},models_sha256=models,review_binding=review.binding,stock_keys=sorted(review.keys),domain_binding=registry.binding,actual_search_plan=len(matrix),approved_category_limit=90,source_ids_unchanged=True,human_reviewed=False)
    save_json(path,contract,immutable=True);return contract

def verify(c):
    for mapping in (c["files_sha256"],c["models_sha256"]):
        for p,h in mapping.items():
            if not (R/p).is_file() or sha_file(R/p)!=h:raise ValueError("frozen regression drift: "+p)
    if load_registry().binding!=c["domain_binding"] or load_review().binding!=c["review_binding"] or sorted(load_review().keys)!=c["stock_keys"]:raise ValueError("frozen registry/review/stock drift")

def run(c):
    os.environ.update(FLAVORETRO_TASK016_LEDGER=str(R/"outputs/task016-p7/v1/run_ledger.jsonl"),FLAVORETRO_TASK016_PURPOSE="p7_legacy_canary",FLAVORETRO_TASK016_TRACE="1",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1")
    path=O/"observations.jsonl";observed=rows(path) if path.exists() else []
    done={(x["target"],x["seed"]) for x in observed}
    if len(done)!=len(observed):raise ValueError("duplicate raw regression cells")
    for cell in c["matrix"]:
        if (cell["target"],cell["seed"]) in done:continue
        verify(c)
        result=search(SearchRequest(smiles=cell["target"],seed=cell["seed"],candidate_stock=True,glycoside_expansion=True,glycoside_library_version="v7",**c["parameters"]),run_root=O/"runs")
        folder=O/"runs"/result["run_id"];manifest=json.loads((folder/"manifest.json").read_text())
        item=dict(**cell,run_id=result["run_id"],status=result["status"],result_path=str((folder/"result.json").relative_to(R)),result_sha256=sha_file(folder/"result.json"),manifest_path=str((folder/"manifest.json").relative_to(R)),manifest_sha256=sha_file(folder/"manifest.json"),wall_seconds=manifest["wall_seconds"],error=result.get("error"),synthetic_fixture=False)
        observed.append(item);write("TASK-016-P7",str(path.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in observed));event("TASK-016-P7","historical_regression_cell",**item)
        print(dict(completed=len(observed),planned=len(c["matrix"]),seed=cell["seed"],status=result["status"]),flush=True)
    summarize(c)

def summarize(c):
    observations=rows(O/"observations.jsonl")
    if len(observations)!=len(c["matrix"]):raise ValueError("incomplete historical matrix")
    raw={}
    for o in observations:
        p=R/o["result_path"]
        if sha_file(p)!=o["result_sha256"]:raise ValueError("raw regression SHA drift")
        r=json.loads(p.read_text())
        if r["run_id"]!=o["run_id"] or r["execution_source"]!="live_aizynthfinder_mcts":raise ValueError("not genuine unique MCTS result")
        raw[(o["target"],o["seed"])]=(o,r)
    def checks(refs):
        out=[]
        for ref in refs:
            by_seed=[]
            for seed in c["seeds"]:
                o,r=raw[(ref["target"],seed)]
                signatures={e["signature"] for e in r.get("action_trace",[]) if e["stage"]=="mcts_action_created" and e.get("created_node_count",0)>0}
                by_seed.append(dict(seed=seed,status=r["status"],run_id=o["run_id"],reference_created=set(ref["reference_signatures"])<=signatures))
            out.append(dict(**ref,by_seed=by_seed,all_three_seed_created=all(x["status"]=="ok" and x["reference_created"] for x in by_seed)))
        return out
    legacy=checks(c["references"]);exact=checks(c["TASK016_exact_canaries"]);p1=checks(c["P1_success_canaries"])
    previous={x["target"]:x for x in json.loads((R/"outputs/task016-p6/v1/e_regression.json").read_text())["checks"]}
    loss=[x["target"] for x in legacy if previous[x["target"]]["all_three_seed_created"] and not x["all_three_seed_created"]]
    result=dict(task="TASK-016-P7",scope="historical capability retention only",actual_MCTS=len(observations),synthetic_fixture=0,planned=len(c["matrix"]),checks=legacy,TASK016_exact_canaries=exact,P1_success_canaries=p1,new_reference_loss=loss,errors=sum(x["status"]!="ok" for x in observations),passed=not loss and all(x["all_three_seed_created"] for x in exact+p1) and all(x["status"]=="ok" for x in observations),raw_observation_sha256=sha_file(O/"observations.jsonl"),contract_sha256=sha_file(O/"contract.json"),human_reviewed=False)
    save_json(O/"validation.json",result)
    print(dict(passed=result["passed"],actual_MCTS=len(observations),legacy_reference_loss=len(loss),TASK016_canaries=sum(x["all_three_seed_created"] for x in exact),P1_canaries=sum(x["all_three_seed_created"] for x in p1)),flush=True)
    return result
if __name__=="__main__":
    c=freeze()
    if "--run" in sys.argv:run(c)
    elif "--summarize" in sys.argv:summarize(c)
    else:print(dict(planned=len(c["matrix"]),contract=str((O/"contract.json").relative_to(R))))
