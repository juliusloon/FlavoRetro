"""Full tests in source-only snapshot; scientific local assets deliberately excluded."""
import json,os,shutil,subprocess,sys
from pathlib import Path
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import save_json,sha_file
R=Path(__file__).resolve().parents[1];revision=os.environ.get("TASK016_P7_ASSET_FREE_REVISION","v1");T=R/("outputs/validation/task016-p7-asset-free-"+revision);O=R/("outputs/task016-p7/v1/engineering"+("" if revision=="v1" else "-"+revision))
def main():
    if T.exists():raise RuntimeError("asset-free attempt already exists; preserve and use new version")
    T.mkdir(parents=True)
    for name in ["flavoretro","tests","configs","scripts"]:shutil.copytree(R/name,T/name,ignore=shutil.ignore_patterns("__pycache__","*.pyc","._*"))
    dependency="outputs/validation/task015-dependencies/ord_schema"
    shutil.copytree(R/dependency,T/dependency,ignore=shutil.ignore_patterns("__pycache__","*.pyc","._*"))
    for name in ["PROJECT.md","pyproject.toml"]:shutil.copy2(R/name,T/name)
    previous=R/"outputs/task016-p6/v1/asset_free_skip_plan.json"
    plan=dict(task="TASK-016-P7",explicit_source_dependent_tests=json.loads(previous.read_text())["explicit_source_dependent_tests"],inherited_plan_sha256=sha_file(previous),runtime_asset_dependent_tests_auto_skip=True,scientific_assets_absent=True,original_tests_unchanged=True)
    save_json(O/"asset_free_skip_plan.json",plan,immutable=True)
    code="""import json,sys,unittest;from pathlib import Path;from unittest.mock import patch;sys.path.insert(0,sys.argv[1]);suite=unittest.defaultTestLoader.discover(sys.argv[1]+'/tests');excluded=set(json.loads(Path(sys.argv[3]).read_text())['explicit_source_dependent_tests'])
def mark(s):
    for item in s:
        if isinstance(item,unittest.TestSuite):mark(item)
        elif item.id() in excluded:setattr(item,item._testMethodName,unittest.skip('historical scientific payload intentionally absent')(getattr(item,item._testMethodName)))
mark(suite)
with patch('flavoretro.task016_runs.root',return_value=Path(sys.argv[2])):result=unittest.TextTestRunner(verbosity=2).run(suite)
print('CONTRACT_RESULT',result.testsRun,len(result.skipped),len(result.failures),len(result.errors));sys.exit(not result.wasSuccessful())"""
    env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1","FLAVORETRO_WORKSPACE":str(T),"FLAVORETRO_TASK016_LEDGER":str(R/"outputs/task016-p7/v1/run_ledger.jsonl"),"FLAVORETRO_TASK016_PURPOSE":"p7_engineering","FLAVORETRO_TASK016_SYNTHETIC_FIXTURE":"1","OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1"}
    event("TASK-016-P7","asset_free_test_command",snapshot=str(T.relative_to(R)),argv=[sys.executable,"-I","-B","-c",code,str(T),str(R),str(O/"asset_free_skip_plan.json")],scientific_assets_excluded=True)
    result=subprocess.run([sys.executable,"-I","-B","-c",code,str(T),str(R),str(O/"asset_free_skip_plan.json")],cwd=T,env=env,text=True,capture_output=True)
    log=O/"asset_free_regression.log";write("TASK-016-P7",str(log.relative_to(R)),result.stdout+result.stderr)
    line=next((s for s in result.stdout.splitlines() if s.startswith("CONTRACT_RESULT")),None)
    if not line:raise RuntimeError("asset-free test report absent")
    _,total,skips,failures,errors=line.split()
    report=dict(task="TASK-016-P7",exit_code=result.returncode,total_tests=int(total),skipped=int(skips),passed=int(total)-int(skips)-int(failures)-int(errors),failures=int(failures),errors=int(errors),snapshot=str(T.relative_to(R)),scientific_assets_absent=True,log_sha256=sha_file(log),search_attempts_counted_in_original_P7_engineering_ledger=True,explicit_skip_plan_path=str((O/"asset_free_skip_plan.json").relative_to(R)),explicit_skip_plan_sha256=sha_file(O/"asset_free_skip_plan.json"))
    save_json(O/"asset_free_regression.json",report);print(report)
    if result.returncode:raise RuntimeError("asset-free regression failed; see raw log")
if __name__=="__main__":main()
