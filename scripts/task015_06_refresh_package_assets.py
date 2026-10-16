"""Refresh final wheel assets without exceeding the frozen real-MCTS budget."""
import json,os,shutil,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.workspace import root
from flavoretro.resources import dumps,sha
old=root()/'outputs/validation/task015-06-package'
out=root()/'outputs/validation/task015-06-package-v2';out.mkdir(exist_ok=False)
code={str(p.relative_to(root()/'flavoretro')):sha(p) for p in (root()/'flavoretro').glob('*.py')}
assert all(sha(old/'installed/flavoretro'/name)==digest for name,digest in code.items())
src=out/'source';src.mkdir();shutil.copy2(root()/'pyproject.toml',src/'pyproject.toml');shutil.copytree(root()/'flavoretro',src/'flavoretro',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
build=subprocess.run([sys.executable,'-B','-m','build','--wheel','--no-isolation','--outdir',str(out/'dist')],cwd=src,text=True,capture_output=True);(out/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0
wheel=next((out/'dist').glob('*.whl'))
install=subprocess.run([sys.executable,'-B','-m','pip','install','--no-deps','--target',str(out/'installed'),str(wheel)],text=True,capture_output=True);(out/'install.log').write_text(install.stdout+install.stderr);assert install.returncode==0
for folder in ['web','configs']:
 for p in (root()/folder).iterdir():
  if p.is_file():assert p.read_bytes()==(out/'installed/flavoretro/assets'/folder/p.name).read_bytes()
assert all(sha(out/'installed/flavoretro'/name)==digest for name,digest in code.items())
probe="import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.workspace import PACKAGE;from flavoretro.reviewed_resources import load_review;r=load_review();print(json.dumps({'package':str(PACKAGE),'binding':r.binding,'eligible_stock_keys':len(r.keys)}));assert len(r.keys)==17"
p=subprocess.run([sys.executable,'-I','-B','-c',probe,str(out/'installed')],cwd=out,env={**os.environ,'FLAVORETRO_WORKSPACE':str(root()),'FLAVORETRO_REVIEW_VALIDATION_LEGACY':'0','PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True);assert p.returncode==0,p.stderr
report={'wheel':str(wheel.relative_to(root())),'wheel_sha256':sha(wheel),'installed_probe':json.loads(p.stdout),'current_assets_installed_equal':True,'runtime_code_identical_to_previously_live_verified_install':code,'real_live_evidence':'outputs/validation/task015-06-package/report.json','additional_mcts_runs':0}
(out/'report.json').write_text(dumps(report));print(dumps({'final_wheel':report['wheel'],'assets_equal':True,'runtime_code_files_identical':len(code),'additional_mcts_runs':0}))
