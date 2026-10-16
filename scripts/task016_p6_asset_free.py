"""Asset-free contracts while counting service fixtures in the original P2 ledger."""
import sys,os,json,shutil,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'outputs/validation/task016-p6-asset-free-r2';assert not out.exists();out.mkdir(parents=True)
for n in ['flavoretro','tests','configs','scripts']:shutil.copytree(ROOT/n,out/n,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(ROOT/'outputs/validation/task015-dependencies/ord_schema',out/'outputs/validation/task015-dependencies/ord_schema',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for n in ['PROJECT.md','pyproject.toml']:shutil.copy2(ROOT/n,out/n)
code="""import sys,unittest;from pathlib import Path;from unittest.mock import patch;sys.path.insert(0,sys.argv[1]);suite=unittest.defaultTestLoader.discover(sys.argv[1]+'/tests');import json;excluded=set(json.loads((Path(sys.argv[2])/'outputs/task016-p6/v1/asset_free_skip_plan.json').read_text())['explicit_source_dependent_tests'])
def mark(s):
    for item in s:
        if isinstance(item,unittest.TestSuite):mark(item)
        elif item.id() in excluded:setattr(item,item._testMethodName,unittest.skip('historical source payload intentionally absent')(getattr(item,item._testMethodName)))
mark(suite)

with patch('flavoretro.task016_runs.root',return_value=Path(sys.argv[2])): result=unittest.TextTestRunner(verbosity=2).run(suite)
print('CONTRACT_RESULT',result.testsRun,len(result.skipped),len(result.failures),len(result.errors));sys.exit(not result.wasSuccessful())"""
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','FLAVORETRO_WORKSPACE':str(out),'FLAVORETRO_TASK016_LEDGER':str(ROOT/'outputs/task016-p6/v1/run_ledger.jsonl'),'FLAVORETRO_TASK016_PURPOSE':'p6_engineering','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
event('TASK-016-P6','asset_free_test_command',argv=[sys.executable,'-I','-B','-c',code,str(out),str(ROOT)],ledger='original P2 engineering ledger; no separate fixture budget')
r=subprocess.run([sys.executable,'-I','-B','-c',code,str(out),str(ROOT)],cwd=out,env=env,text=True,capture_output=True)
write('TASK-016-P6','outputs/task016-p6/v1/asset_free_regression.log',r.stdout+r.stderr)
line=next((l for l in r.stdout.splitlines() if l.startswith('CONTRACT_RESULT')),None)
if line:
    _,total,skips,failures,errors=line.split();report=dict(exit_code=r.returncode,total_tests=int(total),skipped=int(skips),passed=int(total)-int(skips)-int(failures)-int(errors),failures=int(failures),errors=int(errors),snapshot=str(out.relative_to(ROOT)),ledger_counted=True)
else:report=dict(exit_code=r.returncode,error=r.stdout+r.stderr)
write('TASK-016-P6','outputs/task016-p6/v1/asset_free_regression.json',json.dumps(report,indent=2)+'\n')
print(json.dumps(report));assert r.returncode==0,r.stdout+r.stderr
