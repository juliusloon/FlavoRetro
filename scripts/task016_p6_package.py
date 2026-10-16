"""Installed-wheel v3/default probes and copied missing-asset defaults."""
import sys,os,json,subprocess,shutil,tempfile,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
from flavoretro.resources import sha
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/task016-p6/v1';target=ROOT/'outputs/validation/task016-p6-package';assert not target.exists();target.mkdir(parents=True);src=target/'source';src.mkdir()
shutil.copy2(ROOT/'pyproject.toml',src/'pyproject.toml');shutil.copytree(ROOT/'flavoretro',src/'flavoretro',ignore=shutil.ignore_patterns('__pycache__','*.pyc','._*'))
def logged(name,args,**kwargs):
    event('TASK-016-P6','package_command',argv=args,cwd=str(kwargs.get('cwd',ROOT)))
    r=subprocess.run(args,text=True,capture_output=True,**kwargs);write('TASK-016-P6',str((target/name).relative_to(ROOT)),r.stdout+r.stderr);assert r.returncode==0,r.stderr;return r
logged('build.log',[sys.executable,'-B','-m','build','--wheel','--sdist','--no-isolation','--outdir',str(target/'dist')],cwd=src)
wheel=next((target/'dist').glob('*.whl'))
with zipfile.ZipFile(wheel) as z:
    names=z.namelist();assert all('flavoretro/'+n in names for n in ['glycoside_library_v6.py','glycoside_library.py','assets/configs/glycoside-library-v6.json'])
    assert z.read('flavoretro/assets/configs/glycoside-library-v6.json')==(ROOT/'configs/glycoside-library-v6.json').read_bytes()
    assert not any('/data/raw/' in n or '/outputs/' in n for n in names)
logged('install.log',[sys.executable,'-B','-m','pip','install','--no-deps','--target',str(target/'installed'),str(wheel)])
env={**os.environ,'FLAVORETRO_WORKSPACE':str(ROOT),'FLAVORETRO_TASK016_LEDGER':str(ROOT/'outputs/task016-p6/v1/run_ledger.jsonl'),'FLAVORETRO_TASK016_PURPOSE':'p6_engineering','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;from flavoretro.workspace import PACKAGE,root;builds=[json.loads(l) for l in (root()/'outputs/task016-p6/v1/c_build_supports.jsonl').read_text().splitlines()];r=search(SearchRequest.model_validate(json.loads(sys.argv[2])));print(json.dumps(dict(run_id=r['run_id'],status=r['status'],package=str(PACKAGE),domain_binding=r.get('domain_binding'),created_domain=sum(e['stage']=='mcts_action_created' and e.get('policy')=='glycoside' for e in r.get('action_trace',[])),created_c_scope_reference=sum(e['stage']=='mcts_action_created' and e.get('metadata',{}).get('task016_evidence',{}).get('namespace')=='task016_p6' and e.get('signature') in {s['reference_signature'] for s in builds} for e in r.get('action_trace',[])),conditions_verified=any(e.get('metadata',{}).get('task016_evidence',{}).get('prediction_conditions_verified') for e in r.get('action_trace',[])))))"""
builds=[json.loads(l) for l in (OUT/'c_build_supports.jsonl').read_text().splitlines()]
requests=[dict(smiles='CCOc1ccccc1',mode='quick',seconds=3.0,iterations=5,nodes=7,branching=2)]+[dict(smiles=s['target'],mode='quick',glycoside_expansion=True,glycoside_library_version='v6',candidate_stock=True,seconds=12.0,iterations=20,nodes=120,depth=2,branching=12,seed=0) for s in builds]

probes=[]
with tempfile.TemporaryDirectory() as scratch:
    env.pop('FLAVORETRO_TASK016_TRACE',None)
    for i,req in enumerate(requests):
        if i:env['FLAVORETRO_TASK016_TRACE']='1'
        result=logged(f'probe-{i}.log',[sys.executable,'-I','-B','-c',code,str(target/'installed'),json.dumps(req)],cwd=scratch,env=env)
        r=json.loads(result.stdout);assert r['status']=='ok' and r['package'].startswith(str(target/'installed')) and not r['conditions_verified'];probes.append(r)
    assert all(p['created_c_scope_reference'] for p in probes[1:])
    missing="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.workspace import config,AssetError;from flavoretro.glycoside_library_v6 import load_registry;assert config('glycoside-library-v6.json')['default_enabled'] is False
try:load_registry()
except AssetError:print(json.dumps(dict(missing_assets_fail_closed=True,default_off=True)))
else:raise AssertionError('missing registry accepted')"""
    env['FLAVORETRO_WORKSPACE']=scratch;env.pop('FLAVORETRO_TASK016_LEDGER',None)
    logged('missing-assets.log',[sys.executable,'-I','-B','-c',missing,str(target/'installed')],cwd=scratch,env=env)
excluded={'run_id','created_at','code','search_seconds','wall_seconds','first_solution_time','time'}
def stable(v):
    if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k not in excluded}
    if isinstance(v,list):return [stable(x) for x in v]
    return v
previous=json.loads((ROOT/'outputs/task016-p1/v2/default_off_regression.json').read_text());prior_id=previous.get('after_run',previous.get('before_run'))
path=ROOT/'outputs/runs'/prior_id/'result.json'
if not path.is_file():
    earlier=json.loads((ROOT/'outputs/task016/v1/default-off-regression.json').read_text());path=ROOT/'outputs/task016/v1/engineering-runs'/earlier['after_run']/'result.json'
current=ROOT/'outputs/runs'/probes[0]['run_id']/'result.json';equal=stable(json.loads(path.read_text()))==stable(json.loads(current.read_text()));assert equal,'default stable result changed'
write('TASK-016-P6',str((OUT/'default_off_regression.json').relative_to(ROOT)),json.dumps(dict(equal=equal,previous_path=str(path.relative_to(ROOT)),current_run_id=probes[0]['run_id'],excluded_fields=sorted(excluded)),indent=2)+'\n')
from flavoretro.glycoside_expansion import load_registry as load_v1,apply_template as apply_v1
from flavoretro.glycoside_library import load_registry as load_v2,apply_template
v1=load_v1();v2=load_v2()
from flavoretro.reviewed_resources import canonical_side
v1ok=all(canonical_side(r['reference_precursors']) in [o['precursors'] for o in apply_v1(t,r['target'])] for t in v1.templates for iid in t['support_instances'] for r in [v1.instances[iid]])
v2ok=all(canonical_side(r['reference_precursors']) in [o['precursors'] for o in apply_template(t,r['target'])] for t in v2.templates for iid in t['support_instances'] for r in [v2.instances[iid]])
assert v1ok and v2ok
write('TASK-016-P6',str((OUT/'v1_v2_regression.json').relative_to(ROOT)),json.dumps(dict(v1_supports_passed=v1ok,v2_supports_passed=v2ok,v1_binding=v1.binding,v2_binding=v2.binding,actual_search_attempts=0),indent=2)+'\n')
import tarfile
sdist=next((target/'dist').glob('*.tar.gz'))
with tarfile.open(sdist) as archive:
    sdist_names=archive.getnames();assert not any('/data/raw/' in n or '/outputs/' in n for n in sdist_names)
    assert any(n.endswith('/flavoretro/glycoside_library_v6.py') for n in sdist_names)
report=dict(passed=True,sdist=str(sdist.relative_to(ROOT)),sdist_sha256=sha(sdist),wheel=str(wheel.relative_to(ROOT)),wheel_sha256=sha(wheel),probes=probes,default_off_stable_fields_equal=equal,missing_assets_fail_closed=True,source_payload_not_packaged=True,config_copies_equal=True,scope='installed Linux/Python3.10 engineering; C build reconstruction with exact seed matches, not heldout transfer or release')
write('TASK-016-P6',str((OUT/'package_validation.json').relative_to(ROOT)),json.dumps(report,indent=2)+'\n');print(json.dumps(report))
