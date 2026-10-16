"""Explicit full 4x3 canary revalidation after trace-product representation bug."""
import json,os
from pathlib import Path
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import save_json,sha_file,now
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.reviewed_resources import canonical_side,reaction_signature,load_review
from flavoretro.open_glycoside_library import normalize_species
from flavoretro.glycoside_library_v7 import load_registry
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/regression/canary_recovery_v2"
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def trace_reference(record):
    precursors=[normalize_species(x)["normalized"] for x in record["reference_precursors"]]
    # Production trace_action retains its TreeMolecule's input target charge.
    # Library normalization affects the emitted precursors, not that target.
    return reaction_signature([canonical_side(precursors)],[record["target"]])
def freeze():
    p=O/"contract.json"
    if p.exists():return json.loads(p.read_text())
    old=R/"outputs/task016-p7/v1/regression/contract.json"
    previous=json.loads(old.read_text());source=R/"outputs/task016/v1/instances.jsonl"
    refs=rows(source)
    if {x["instance_id"] for x in refs}!={x["instance_id"] for x in previous["TASK016_exact_canaries"]}:raise RuntimeError("frozen original canary ID universe drift")
    for x in refs:x["expected_trace_signature"]=trace_reference(x)
    inputs=[old,source,R/"outputs/task016-p7/v1/regression/validation.json",R/"scripts/task016_p7_canary_recovery.py",R/"flavoretro/search.py",R/"flavoretro/open_glycoside_library.py"]
    c=dict(task="TASK-016-P7",approval_type="agent_delegated",frozen_at=now(),revalidation_reason="Evaluator normalized the original charged target although live trace retains input target charge. Scope, runtime, search parameters and original canary IDs are unchanged. Preserve v1 false evaluation and all63 raw runs; re-run all affected4x3 cells.",references=refs,matrix=[dict(instance_id=x["instance_id"],target=x["target"],seed=s) for x in refs for s in [0,1,2]],parameters=previous["parameters"],files_sha256={str(p.relative_to(R)):sha_file(p) for p in inputs},production_code_sha256={p:h for p,h in previous["files_sha256"].items() if p.startswith("flavoretro/")},models_sha256=previous["models_sha256"],domain_binding=load_registry().binding,review_binding=load_review().binding,stock_keys=sorted(load_review().keys),purpose="p7_revalidation",planned=12,human_reviewed=False,scientific_transfer_matrix_affected=False,normalization_rule="existing normalize_species on emitted precursor species; canonical raw charged original target for live trace comparison")
    save_json(p,c,immutable=True);return c

def verify(c):
    for mapping in [c["files_sha256"],c["production_code_sha256"],c["models_sha256"]]:
        if any(not (R/p).is_file() or sha_file(R/p)!=h for p,h in mapping.items()):raise RuntimeError("frozen canary revalidation input drift")
    if load_registry().binding!=c["domain_binding"] or load_review().binding!=c["review_binding"] or sorted(load_review().keys)!=c["stock_keys"]:raise RuntimeError("registry/review/stock drift")

def run():
    c=freeze();verify(c)
    os.environ.update(FLAVORETRO_TASK016_LEDGER=str(R/"outputs/task016-p7/v1/run_ledger.jsonl"),FLAVORETRO_TASK016_PURPOSE="p7_revalidation",FLAVORETRO_TASK016_TRACE="1",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1");os.environ.pop("FLAVORETRO_TASK016_SYNTHETIC_FIXTURE",None)
    p=O/"observations.jsonl";obs=rows(p) if p.exists() else [];seen={(x["instance_id"],x["seed"]) for x in obs}
    for cell in c["matrix"]:
        if (cell["instance_id"],cell["seed"]) in seen:continue
        verify(c);r=search(SearchRequest(smiles=cell["target"],seed=cell["seed"],candidate_stock=True,glycoside_expansion=True,glycoside_library_version="v7",**c["parameters"]),run_root=O/"runs");folder=O/"runs"/r["run_id"]
        row=dict(**cell,run_id=r["run_id"],status=r["status"],result_path=str((folder/"result.json").relative_to(R)),result_sha256=sha_file(folder/"result.json"),manifest_path=str((folder/"manifest.json").relative_to(R)),manifest_sha256=sha_file(folder/"manifest.json"),synthetic_fixture=False)
        obs.append(row);write("TASK-016-P7",str(p.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in obs));event("TASK-016-P7","full_canary_revalidation",**row)
    checks=[]
    for ref in c["references"]:
        seeds=[]
        for seed in [0,1,2]:
            o=next(x for x in obs if x["instance_id"]==ref["instance_id"] and x["seed"]==seed);r=json.loads((R/o["result_path"]).read_text())
            if sha_file(R/o["result_path"])!=o["result_sha256"] or r["execution_source"]!="live_aizynthfinder_mcts":raise RuntimeError("canary raw provenance drift")
            matched=[x for x in r.get("action_trace",[]) if x["stage"]=="mcts_action_created" and x.get("signature")==ref["expected_trace_signature"] and x.get("created_node_count",0)>0]
            seeds.append(dict(seed=seed,run_id=o["run_id"],status=r["status"],reference_created=bool(matched),exact_seed_instance_match=any(x.get("metadata",{}).get("task016_evidence",{}).get("exact_seed_instance_match") is True for x in matched)))
        checks.append(dict(instance_id=ref["instance_id"],expected_trace_signature=ref["expected_trace_signature"],by_seed=seeds,all_three_seed_created=all(x["status"]=="ok" and x["reference_created"] and x["exact_seed_instance_match"] for x in seeds)))
    result=dict(task="TASK-016-P7",passed=len(obs)==12 and all(x["all_three_seed_created"] for x in checks),planned=12,real_MCTS=len(obs),synthetic_fixture=0,checks=checks,original_failed_evaluation_preserved=True,all_affected_cells_rerun=True,contract_sha256=sha_file(O/"contract.json"),observations_sha256=sha_file(p),scope="historical exact instance reconstruction; not scope transfer")
    save_json(O/"validation.json",result,immutable=True);print(dict(passed=result["passed"],real_MCTS=len(obs),exact_canaries=sum(x["all_three_seed_created"] for x in checks)))
if __name__=="__main__":run()
