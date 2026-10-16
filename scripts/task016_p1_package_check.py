"""Installed-wheel default/v2 probes, bounded by the TASK016P1 ledger."""
import json,os,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
from scripts.task016_p1_sources import ROOT,OUT,save,rows
from scripts.operate import event
from flavoretro.resources import sha

def check():
    target=ROOT/'outputs/validation/task016-p1-package';assert not target.exists();target.mkdir();src=target/'source';src.mkdir();shutil.copy2(ROOT/'pyproject.toml',src/'pyproject.toml');shutil.copytree(ROOT/'flavoretro',src/'flavoretro',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    build=subprocess.run([sys.executable,'-B','-m','build','--wheel','--no-isolation','--outdir',str(target/'dist')],cwd=src,text=True,capture_output=True);(target/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0,build.stderr
    wheel=next((target/'dist').glob('*.whl'))
    with zipfile.ZipFile(wheel) as z:
        names=z.namelist();assert all('flavoretro/'+n in names for n in ['glycoside_library.py','open_glycoside_library.py','assets/configs/glycoside-library-v2.json','glycoside_expansion.py']);assert not any('/outputs/' in n or '/data/raw/' in n for n in names)
    install=subprocess.run([sys.executable,'-B','-m','pip','install','--no-deps','--target',str(target/'installed'),str(wheel)],text=True,capture_output=True);(target/'install.log').write_text(install.stdout+install.stderr);assert install.returncode==0,install.stderr
    env={**os.environ,'FLAVORETRO_WORKSPACE':str(ROOT),'PYTHONDONTWRITEBYTECODE':'1','FLAVORETRO_TASK016_LEDGER':str(OUT/'run_ledger.jsonl'),'FLAVORETRO_TASK016_PURPOSE':'task016_p1_installed_package','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'};env.pop('FLAVORETRO_TASK016_TRACE',None)
    with tempfile.TemporaryDirectory() as scratch:
        probes=[]
        code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;from flavoretro.workspace import PACKAGE;r=search(SearchRequest.model_validate(json.loads(sys.argv[2])));print(json.dumps(dict(run_id=r['run_id'],status=r['status'],package=str(PACKAGE),review=r.get('review_binding'),created_domain=sum(e['stage']=='mcts_action_created' and e.get('policy')=='glycoside' for e in r.get('action_trace',[])),conditions_verified=any(e.get('metadata',{}).get('task016_evidence',{}).get('prediction_conditions_verified') for e in r.get('action_trace',[])))))"""
        reqs=[dict(smiles='CCOc1ccccc1',mode='quick',seconds=3.0,iterations=5,nodes=7,branching=2),dict(smiles=rows(OUT/'runtime_instances.jsonl')[0]['target'],mode='quick',glycoside_expansion=True,glycoside_library_version='v2',candidate_stock=True,seconds=12.0,iterations=20,depth=2,branching=12,nodes=120)]
        for i,req in enumerate(reqs):
            if i:env['FLAVORETRO_TASK016_TRACE']='1'
            r=subprocess.run([sys.executable,'-I','-B','-c',code,str(target/'installed'),json.dumps(req)],cwd=scratch,env=env,text=True,capture_output=True);(target/f'probe-{i}.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr;result=json.loads(r.stdout);assert result['status']=='ok' and result['package'].startswith(str(target/'installed'));assert not result['conditions_verified'];probes.append(result)
        assert probes[1]['created_domain']>0
        before=json.loads((ROOT/'outputs/task016/v1/default-off-regression.json').read_text())['after_run'];old=json.loads((ROOT/'outputs/task016/v1/engineering-runs'/before/'result.json').read_text());current=json.loads((ROOT/'outputs/runs'/probes[0]['run_id']/'result.json').read_text())
        excluded={'run_id','created_at','code','search_seconds','wall_seconds','first_solution_time','time'}
        def stable(v):
            if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k not in excluded}
            if isinstance(v,list):return [stable(x) for x in v]
            return v
        equal=stable(old)==stable(current);save('default_off_regression.json',dict(equal=equal,before_run=before,after_run=probes[0]['run_id'],excluded_fields=sorted(excluded),full_stable_fields_compared=True));assert equal,'default-off stable result changed'
        # Missing-asset probe does not run search; it checks copied packaged defaults.
        isolated_code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.workspace import config;from flavoretro.glycoside_library import load_registry;from flavoretro.workspace import AssetError;assert config('glycoside-library-v2.json')['default_enabled'] is False
try:load_registry()
except AssetError:print(json.dumps({'status':'missing_assets_fail_closed','default_off':True}))
else:raise AssertionError('missing registry accepted')"""
        env['FLAVORETRO_WORKSPACE']=scratch;env.pop('FLAVORETRO_TASK016_LEDGER',None);r=subprocess.run([sys.executable,'-I','-B','-c',isolated_code,str(target/'installed')],cwd=scratch,env=env,text=True,capture_output=True);(target/'missing-assets.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
    report=dict(passed=True,wheel=str(wheel.relative_to(ROOT)),wheel_sha256=sha(wheel),probes=probes,default_off_stable_fields_equal=equal,missing_assets_fail_closed=True,copied_config_packaged=True,source_payload_not_packaged=True,scope='installed Linux Python3.10 engineering test, not production release')
    (target/'report.json').write_text(json.dumps(report,indent=2)+'\n');event('TASK-016-P1','installed_package_verified',report=str((target/'report.json').relative_to(ROOT)),passed=True);print(json.dumps(report))
if __name__=='__main__':check()
