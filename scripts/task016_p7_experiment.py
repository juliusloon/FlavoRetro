"""Physical panel/contract freeze and isolated live A/B/E cells; no source selection."""
import argparse,json,os
from pathlib import Path
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import save_json,sha_file,now
from scripts.task016_p7_experiment_harness import freeze_contract,validate_runner_inputs,load_raw_cells,recompute_metrics
from scripts.task016_p7_closure_harness import assert_zero_leakage,canonical,closure_groups
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.reviewed_resources import load_review,canonical_side
from flavoretro.glycoside_library_v7 import load_registry,apply_template
R=Path(__file__).resolve().parents[1];BASE=R/"outputs/task016-p7/v1"
PARAMETERS=dict(mode="quick",engine="optimized",candidate_stock=True,seconds=12.0,iterations=20,depth=2,branching=12,nodes=120,top_k=5)

def rows(path):return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def location(family):return BASE/("C/E01" if family=="C" else "SS")/"experiment"
def freeze(family,panel_path,preflight_path):
    out=location(family);p=out/"frozen_contract.json"
    if p.exists():raise RuntimeError("scientific contract immutable; use new epoch or explicit whole-matrix revalidation")
    panel_path=(R/panel_path).resolve();preflight_path=(R/preflight_path).resolve()
    if not all(x.is_relative_to(R) and x.is_file() for x in [panel_path,preflight_path]):raise RuntimeError("panel preflight input missing")
    a8=json.loads(preflight_path.read_text())
    if a8.get("agent_role")!="A8" or a8.get("passed") is not True or a8.get("panel_sha256")!=sha_file(panel_path):raise RuntimeError("current physical panel lacks independent passed A8")
    references=rows(panel_path)
    if not 6<=len(references)<=9 or len(closure_groups(references))<2:raise RuntimeError("fresh family panel floor failed")
    registry=load_registry();qualified=[t for t in registry.increment_templates if t["scope"]["family"]==family]
    history=rows(BASE/"exposure_ledger.jsonl")
    assert_zero_leakage(list(registry.increment_instances.values()),references,history,list(registry.instances.values()))
    for ref in references:
        flags=["runtime_complete","source_identity_verified","structure_complete","reference_precursor_complete","scope_applicability"]
        if ref.get("family")!=family or any(ref.get(f) is not True for f in flags) or ref.get("leakage") is not False or ref.get("exact_seed_instance_match") is not False:raise RuntimeError("unqualified scientific panel row")
        full=canonical_side(ref["reference_precursors"])
        if full!=canonical_side([ref["acceptor_smiles"],ref["donor_smiles"]]) or not any(full in [o["precursors"] for o in apply_template(t,ref["product_smiles"])] for t in qualified):raise RuntimeError("physical frozen scope full reference preflight failed")
    scope_paths=[BASE/"C/E01/scope_manifest.json",BASE/"SS/scope_freeze.json"]
    code=list((R/"flavoretro").glob("*.py"))+[R/"scripts/task016_p7_experiment.py",R/"scripts/task016_p7_experiment_harness.py",R/"scripts/task016_p7_closure_harness.py",R/"scripts/task016_p7_orchestrate.py"]
    runtime=[R/registry.binding["manifest"],R/"configs/glycoside-library-v7.json",R/"configs/glycoside-library-v6.json",R/"configs/search.json"]
    model_hashes={x["path"]:x["sha256"] for x in json.loads((R/"metadata/sources.json").read_text())["files"] if x["role"]=="external_model"}
    review=load_review()
    contract=dict(task="TASK-016-P7",family=family,epoch_id=family+"-E01",frozen_at=now(),panels={family:dict(path=str(panel_path.relative_to(R)),sha256=sha_file(panel_path),N=len(references),groups=len(closure_groups(references)),preflight_path=str(preflight_path.relative_to(R)),preflight_sha256=sha_file(preflight_path))},scope_bank_sha={str(p.relative_to(R)):sha_file(p) for p in scope_paths},runtime_manifest_sha={str(p.relative_to(R)):sha_file(p) for p in runtime},code_sha={str(p.relative_to(R)):sha_file(p) for p in code},model_hashes=model_hashes,review_binding=review.binding,stock_keys=sorted(review.keys),search_parameters=PARAMETERS,budget=dict(first_family_limit=81,total_limit=600,wall_ceiling_seconds=60),metrics_definition=dict(unit="complete reference per fixed target over all three seeds",gap="all A/B normal and zero reference retention in every A/B seed",gain="gap plus all three E seeds retain complete reference via non-exact qualified P7 scope",node_transfer="all A/B normal with zero reference tree children; all E create non-exact scope reference tree child",thresholds=dict(min_targets=6,min_groups=2,min_G=3,min_ratio=.5,min_gain_groups=2,min_node_targets=3,min_node_groups=2,reference_loss=0,generic_top3_protection_violations=0)),arms={"A":"generic_all_task016_off","B":"frozen_p6_v6","E":"p7_v7"},seeds=[0,1,2],matrix=[dict(family=family,target_id=x["target_id"],arm=arm,seed=seed) for x in references for arm in ["A","B","E"] for seed in [0,1,2]],qualified_p7_scope_ids=[t["template_id"] for t in qualified],domain_binding=registry.binding,human_reviewed=False)
    frozen=freeze_contract(contract);validate_runner_inputs(frozen,contract)
    save_json(p,frozen,immutable=True);return frozen

def verify(frozen):
    c=frozen["contract"];validate_runner_inputs(frozen,c)
    for p in c["panels"].values():
        if sha_file(R/p["preflight_path"])!=p["preflight_sha256"]:raise RuntimeError("independent preflight drift")
    if load_registry().binding!=c["domain_binding"] or load_review().binding!=c["review_binding"] or sorted(load_review().keys)!=c["stock_keys"]:raise RuntimeError("domain/review/stock changed")

def run(family):
    out=location(family);frozen=json.loads((out/"frozen_contract.json").read_text());c=frozen["contract"]
    if c["family"]!=family:raise RuntimeError("wrong family runner")
    os.environ.update(FLAVORETRO_TASK016_LEDGER=str(BASE/"run_ledger.jsonl"),FLAVORETRO_TASK016_PURPOSE="p7_"+family+"_validation",FLAVORETRO_TASK016_TRACE="1",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1")
    os.environ.pop("FLAVORETRO_TASK016_SYNTHETIC_FIXTURE",None)
    panel=rows(R/c["panels"][family]["path"]);by_id={x["target_id"]:x for x in panel}
    p=out/"observations.jsonl";observed=rows(p) if p.exists() else [];seen={(x["target_id"],x["arm"],x["seed"]) for x in observed}
    if len(seen)!=len(observed):raise RuntimeError("duplicate matrix cells; cannot subset-repair implementation bug")
    for cell in c["matrix"]:
        identity=(cell["target_id"],cell["arm"],cell["seed"])
        if identity in seen:continue
        verify(frozen);request=dict(c["search_parameters"],smiles=by_id[cell["target_id"]]["product_smiles"],seed=cell["seed"])
        if cell["arm"]!="A":request.update(glycoside_expansion=True,glycoside_library_version={"B":"v6","E":"v7"}[cell["arm"]])
        result=search(SearchRequest.model_validate(request),run_root=out/"runs");folder=out/"runs"/result["run_id"]
        manifest=folder/"manifest.json";physical=folder/"result.json"
        row=dict(**cell,run_id=result["run_id"],status=result["status"],result_path=str(physical.relative_to(R)),result_sha256=sha_file(physical),manifest_path=str(manifest.relative_to(R)),manifest_sha256=sha_file(manifest),contract_sha=frozen["contract_sha"],started=True,terminal=True,synthetic_fixture=False,error=result.get("error"))
        observed.append(row);write("TASK-016-P7",str(p.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in observed));event("TASK-016-P7","frozen_ABE_cell",**row)
        print(dict(family=family,done=len(observed),planned=len(c["matrix"]),arm=cell["arm"],seed=cell["seed"],status=result["status"]),flush=True)
    verify(frozen);metric=recompute_metrics(frozen,load_raw_cells(observed),panel);save_json(out/"metrics.json",metric,immutable=True);print(dict(family=family,completion_passed=metric["metrics_by_family"][family]["completion_passed"]),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("family",choices=["C","SS"]);p.add_argument("--panel");p.add_argument("--preflight");p.add_argument("--run",action="store_true");a=p.parse_args()
    if a.run:run(a.family)
    elif a.panel and a.preflight:freeze(a.family,a.panel,a.preflight)
    else:p.error("supply panel and independent preflight, or --run an existing frozen contract")
