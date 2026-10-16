"""Build a wheel in an isolated copy; test installed code and frozen workspace."""
import json,os,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.workspace import root
from flavoretro.resources import dumps

out=root()/'outputs/validation/task016-package';out.mkdir(exist_ok=False)
src=out/'source';src.mkdir()
shutil.copy2(root()/'pyproject.toml',src/'pyproject.toml')
shutil.copytree(root()/'flavoretro',src/'flavoretro',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
build=subprocess.run([sys.executable,'-B','-m','build','--wheel','--no-isolation','--outdir',str(out/'dist')],cwd=src,text=True,capture_output=True)
(out/'build.log').write_text(build.stdout+build.stderr)
assert build.returncode==0
wheel=next((out/'dist').glob('*.whl'))
with zipfile.ZipFile(wheel) as z:
    names=z.namelist()
    assert 'flavoretro/reviewed_resources.py' in names
    assert all('flavoretro/'+n in names for n in ['glycoside_expansion.py','open_reactions.py','task016_runs.py','assets/configs/glycoside-expansion.json'])
    assert not any('/outputs/' in n or '/data/raw/' in n or n.endswith('/index.json') for n in names)
install=subprocess.run([sys.executable,'-B','-m','pip','install','--no-deps','--target',str(out/'installed'),str(wheel)],text=True,capture_output=True)
(out/'install.log').write_text(install.stdout+install.stderr)
assert install.returncode==0
with tempfile.TemporaryDirectory() as scratch:
    code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.workspace import PACKAGE;from flavoretro.service import search;from flavoretro.contracts import SearchRequest;r=search(SearchRequest(smiles='CCOc1ccccc1',mode='quick',seconds=3.0,iterations=5,nodes=7,branching=2));print(json.dumps({'package':str(PACKAGE),'run_id':r['run_id'],'status':r['status'],'review':r.get('review_binding',r.get('review_expected')),'routes':len(r['routes'])}));assert r['status']=='ok' and r['routes'] and r['review_binding']['mode']=='adjudicated'"""
    env={**os.environ,'FLAVORETRO_WORKSPACE':str(root()),'PYTHONDONTWRITEBYTECODE':'1','FLAVORETRO_REVIEW_VALIDATION_LEGACY':'0'}
    probe=subprocess.run([sys.executable,'-I','-B','-c',code,str(out/'installed')],cwd=scratch,env=env,text=True,capture_output=True)
    (out/'installed-live.log').write_text(probe.stdout+probe.stderr)
    assert probe.returncode==0,probe.stderr
    installed=json.loads(probe.stdout)
    assert installed['package'].startswith(str(out/'installed'))
    contract=json.loads((root()/'outputs/task016/v1/development_contract.json').read_text())
    env['FLAVORETRO_TASK016_TRACE']='1'
    domain_code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;r=search(SearchRequest(smiles=sys.argv[2],mode='quick',glycoside_expansion=True,candidate_stock=True,seconds=12.0,iterations=20,depth=2,branching=12,nodes=120));events=[e for e in r.get('action_trace',[]) if e['stage']=='mcts_action_created' and e.get('policy')=='glycoside'];assert r['status']=='ok' and events;assert all(e['metadata']['task016_evidence']['prediction_conditions_verified'] is False for e in events);print(json.dumps({'run_id':r['run_id'],'status':r['status'],'created_domain_actions':len(events),'binding':r['domain_binding']}))"""
    domain=subprocess.run([sys.executable,'-I','-B','-c',domain_code,str(out/'installed'),contract['primary_targets'][0]],cwd=scratch,env=env,text=True,capture_output=True)
    (out/'installed-domain.log').write_text(domain.stdout+domain.stderr)
    assert domain.returncode==0,domain.stderr
    domain_result=json.loads(domain.stdout)
    env['FLAVORETRO_WORKSPACE']=scratch
    env.pop('FLAVORETRO_TASK016_LEDGER',None)
    missing="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;r=search(SearchRequest(smiles='CCO',mode='quick'));assert r['status']=='error' and r['error']['code']=='review_assets_error';print(json.dumps(r))"""
    fail=subprocess.run([sys.executable,'-I','-B','-c',missing,str(out/'installed')],cwd=scratch,env=env,text=True,capture_output=True)
    assert fail.returncode==0,fail.stderr
    missing_result=json.loads(fail.stdout)
    shutil.copytree(Path(scratch)/'outputs/runs',out/'missing-assets-runs')
report={'domain_module_and_config_packaged':True,'wheel':str(wheel.relative_to(root())),'wheel_contains_review_module':True,'local_payload_not_packaged':True,'installed_live':installed,'installed_domain':domain_result,'missing_assets_result':missing_result,'scope':'Linux Python 3.10 installed-wheel engineering validation; no release/chemistry claim'}
(out/'report.json').write_text(dumps(report))
print(dumps(report))
