"""Wheel/sdist and outside-checkout installed runtime checks with governed budgets."""
import json,os,subprocess,sys,shutil,tempfile,zipfile,tarfile
from pathlib import Path
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import save_json,sha_file
R=Path(__file__).resolve().parents[1];O=R/("outputs/task016-p7/v1/package"+("" if os.environ.get("TASK016_P7_PACKAGE_REVISION","v1")=="v1" else "-"+os.environ["TASK016_P7_PACKAGE_REVISION"]));T=R/("outputs/validation/task016-p7-package-"+os.environ.get("TASK016_P7_PACKAGE_REVISION","v1"))
def logged(name,args,**kwargs):
    event("TASK-016-P7","package_command",argv=args,cwd=str(kwargs.get("cwd",R)))
    result=subprocess.run(args,text=True,capture_output=True,**kwargs)
    write("TASK-016-P7",str((T/name).relative_to(R)),result.stdout+result.stderr)
    if result.returncode:raise RuntimeError("package check failed; see "+name)
    return result

def main():
    if T.exists():raise RuntimeError("preserve previous package attempt; new version required")
    source=T/"source";source.mkdir(parents=True)
    shutil.copy2(R/"pyproject.toml",source/"pyproject.toml")
    shutil.copytree(R/"flavoretro",source/"flavoretro",ignore=shutil.ignore_patterns("__pycache__","*.pyc","._*"))
    event("TASK-016-P7","package_source_snapshot",path=str(source.relative_to(R)))
    logged("build.log",[sys.executable,"-B","-m","build","--wheel","--sdist","--no-isolation","--outdir",str(T/"dist")],cwd=source)
    wheel=next((T/"dist").glob("*.whl"));sdist=next((T/"dist").glob("*.tar.gz"))
    with zipfile.ZipFile(wheel) as archive:
        names=archive.namelist()
        required=["glycoside_library_v7.py","glycoside_scope_c_v7.py","glycoside_scope_ss_v7.py","assets/configs/glycoside-library-v7.json","glycoside_library_v6.py","assets/configs/glycoside-library-v6.json"]
        if not all("flavoretro/"+x in names for x in required):raise RuntimeError("wheel missing P7 runtime or unchanged baseline")
        if archive.read("flavoretro/assets/configs/glycoside-library-v7.json")!=(R/"configs/glycoside-library-v7.json").read_bytes():raise RuntimeError("wheel/checkout config drift")
        if any("/data/raw/" in x or "/outputs/" in x for x in names):raise RuntimeError("source payload packaged")
    with tarfile.open(sdist) as archive:
        names=archive.getnames()
        if any("/data/raw/" in x or "/outputs/" in x for x in names) or not any(x.endswith("/flavoretro/glycoside_library_v7.py") for x in names):raise RuntimeError("sdist boundary failed")
    installed=T/"installed"
    logged("install.log",[sys.executable,"-B","-m","pip","install","--no-deps","--target",str(installed),str(wheel)])
    env={**os.environ,"FLAVORETRO_WORKSPACE":str(R),"FLAVORETRO_TASK016_LEDGER":str(R/"outputs/task016-p7/v1/run_ledger.jsonl"),"FLAVORETRO_TASK016_PURPOSE":"p7_engineering","PYTHONDONTWRITEBYTECODE":"1","OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"}
    env.pop("FLAVORETRO_TASK016_SYNTHETIC_FIXTURE",None)
    from flavoretro.glycoside_library_v6 import load_registry as load6
    from flavoretro.glycoside_library_v7 import load_registry as load7
    baseline=load6();current=load7()
    c_support=next(x for x in baseline.increment_instances.values())
    supports=[next(current.increment_instances[i] for t in current.increment_templates if t["scope"]["family"]==family for i in t["support_instances"]) for family in ["C","SS"]]
    requests=[dict(smiles="CCOc1ccccc1",mode="quick",seconds=3.0,iterations=5,nodes=7,branching=2)]
    params=dict(mode="quick",engine="optimized",candidate_stock=True,seconds=12.0,iterations=20,nodes=120,depth=2,branching=12,seed=0,top_k=5,glycoside_expansion=True)
    requests.append(dict(params,smiles=c_support["target"],glycoside_library_version="v6"))
    requests.extend(dict(params,smiles=x["target"],glycoside_library_version="v7") for x in supports)
    code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;from flavoretro.workspace import PACKAGE;r=search(SearchRequest.model_validate(json.loads(sys.argv[2])));print(json.dumps(dict(run_id=r['run_id'],status=r['status'],execution_source=r['execution_source'],package=str(PACKAGE),domain_binding=r.get('domain_binding'))))"""
    probes=[]
    with tempfile.TemporaryDirectory() as scratch:
        for index,request in enumerate(requests):
            if index:env["FLAVORETRO_TASK016_TRACE"]="1"
            else:env.pop("FLAVORETRO_TASK016_TRACE",None)
            result=logged(f"probe-{index}.log",[sys.executable,"-I","-B","-c",code,str(installed),json.dumps(request)],cwd=scratch,env=env)
            probe=json.loads(result.stdout)
            if probe["status"]!="ok" or probe["execution_source"]!="live_aizynthfinder_mcts" or not probe["package"].startswith(str(installed)):raise RuntimeError("installed runtime probe failed")
            if index:
                expected=c_support if index==1 else supports[index-2]
                raw=R/"outputs/runs"/probe["run_id"]/"result.json";r=json.loads(raw.read_text())
                created=[e for e in r.get("action_trace",[]) if e["stage"]=="mcts_action_created" and e.get("signature")==expected["reference_signature"] and e.get("created_node_count",0)>0]
                if not created:raise RuntimeError("installed full reference not created")
                probe["full_reference_created"]=True
            probes.append(probe)
        missing="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.workspace import config,AssetError;from flavoretro.glycoside_library_v7 import load_registry;assert config('glycoside-library-v7.json')['default_enabled'] is False
try:load_registry()
except AssetError:print(json.dumps(dict(missing_assets_fail_closed=True,default_off=True)))
else:raise AssertionError('missing P7 payload accepted')"""
        env["FLAVORETRO_WORKSPACE"]=scratch;env.pop("FLAVORETRO_TASK016_LEDGER",None)
        logged("missing-assets.log",[sys.executable,"-I","-B","-c",missing,str(installed)],cwd=scratch,env=env)
    excluded={"run_id","created_at","code","search_seconds","wall_seconds","first_solution_time","time"}
    def stable(value):
        if isinstance(value,dict):return {k:stable(v) for k,v in value.items() if k not in excluded}
        if isinstance(value,list):return [stable(v) for v in value]
        return value
    previous=json.loads((R/"outputs/task016-p6/v1/default_off_regression.json").read_text())
    before=R/"outputs/runs"/previous["current_run_id"]/"result.json"
    after=R/"outputs/runs"/probes[0]["run_id"]/"result.json"
    equal=stable(json.loads(before.read_text()))==stable(json.loads(after.read_text()))
    save_json(O/"default_off_regression.json",dict(equal=equal,previous_path=str(before.relative_to(R)),current_run_id=probes[0]["run_id"],excluded_fields=sorted(excluded),current_result_sha256=sha_file(after),previous_result_sha256=sha_file(before)))
    if not equal:raise RuntimeError("default-off stable result changed")
    save_json(O/"validation.json",dict(passed=True,wheel=str(wheel.relative_to(R)),wheel_sha256=sha_file(wheel),sdist=str(sdist.relative_to(R)),sdist_sha256=sha_file(sdist),probes=probes,real_MCTS=len(probes),synthetic_fixture=0,missing_assets_fail_closed=True,config_copies_equal=True,source_payload_not_packaged=True,default_off_stable_fields_equal=True,scope="installed Linux/Python3.10 engineering checks; build reconstruction only, no fresh transfer or release claim"))
    print(dict(passed=True,real_MCTS=len(probes),default_off_equal=equal))
if __name__=="__main__":main()
