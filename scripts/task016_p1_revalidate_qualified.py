"""Fresh full C panel against explicitly inherited unchanged same-task actual A/B."""
import json,os,shutil,subprocess,sys,tempfile,zipfile
from scripts.task016_p1_sources import ROOT,OUT as ORIGINAL,rows,TASK
from scripts.task016_p1_qualify import QUALIFIED as OUT,save_at
from scripts.task016_p1_evaluate import request,signatures,observe
from scripts.operate import event,write
from flavoretro.service import search
from flavoretro.resources import sha
from flavoretro.reviewed_resources import load_review

def verify_binding(c):
    for k in ['code_sha256','models_sha256']:assert all(sha(ROOT/p)==h for p,h in c[k].items()),'qualified experiment binding drift'
    assert sha(OUT/'development_split_manifest.json')==c['split_sha256']
    assert sha(OUT/'fusion_contract.json')==c['fusion_contract_sha256']
    assert sha(OUT/'template_source_manifest.json')==c['v2_manifest_sha256']
    assert sha(OUT/'qualification_manifest.json')==c['source_qualification_revision']['qualification_manifest_sha256']
    assert sha(OUT/'budget_revision.json')==c['source_qualification_revision']['budget_revision_sha256']
    assert load_review().binding==c['review_binding'] and sorted(load_review().keys)==c['stock_keys']

def main():
    c=json.loads((OUT/'experiment_contract.json').read_text());verify_binding(c)
    assert not (OUT/'mcts_C_revalidation.jsonl').exists()
    package=ROOT/'outputs/validation/task016-p1-package-qualified';assert not package.exists();package.mkdir();src=package/'source';src.mkdir();shutil.copy2(ROOT/'pyproject.toml',src/'pyproject.toml');shutil.copytree(ROOT/'flavoretro',src/'flavoretro',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    b=subprocess.run([sys.executable,'-B','-m','build','--wheel','--no-isolation','--outdir',str(package/'dist')],cwd=src,text=True,capture_output=True);(package/'build.log').write_text(b.stdout+b.stderr);assert b.returncode==0,b.stderr;wheel=next((package/'dist').glob('*.whl'))
    with zipfile.ZipFile(wheel) as archive:
        names=archive.namelist();assert not any('/data/raw/' in n or '/outputs/' in n for n in names)
        assert archive.read('flavoretro/assets/configs/glycoside-library-v2.json')==(ROOT/'configs/glycoside-library-v2.json').read_bytes()
    p=subprocess.run([sys.executable,'-B','-m','pip','install','--no-deps','--target',str(package/'installed'),str(wheel)],text=True,capture_output=True);(package/'install.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    os.environ.update(FLAVORETRO_WORKSPACE=str(ROOT),FLAVORETRO_TASK016_LEDGER=str(ORIGINAL/'run_ledger.jsonl'),FLAVORETRO_TASK016_TRACE='1',FLAVORETRO_TASK016_PURPOSE='task016_p1_qualified_C_full_panel')
    fresh=[];installed_probe=None
    for i,cell in enumerate(c['source_qualification_revision']['fresh_matrix']):
        verify_binding(c)
        if i==0:
            code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;from flavoretro.workspace import PACKAGE;r=search(SearchRequest.model_validate(json.loads(sys.argv[2])),run_root=sys.argv[3]);print(json.dumps(dict(run_id=r['run_id'],status=r['status'],package=str(PACKAGE),binding=r.get('domain_binding'))))"""
            with tempfile.TemporaryDirectory() as scratch:x=subprocess.run([sys.executable,'-I','-B','-c',code,str(package/'installed'),json.dumps(request(cell['target'],'C',cell['seed']).payload()),str(OUT/'paired-runs')],cwd=scratch,env=os.environ,text=True,capture_output=True)
            (package/'installed-main-cell.log').write_text(x.stdout+x.stderr);assert x.returncode==0,x.stderr;installed_probe=json.loads(x.stdout);assert installed_probe['package'].startswith(str(package/'installed'));result=json.loads((OUT/'paired-runs'/installed_probe['run_id']/'result.json').read_text())
        else:result=search(request(cell['target'],'C',cell['seed']),run_root=OUT/'paired-runs')
        folder=OUT/'paired-runs'/result['run_id'];manifest=json.loads((folder/'manifest.json').read_text());row=dict(**cell,run_id=result['run_id'],status=result['status'],result_path=str((folder/'result.json').relative_to(ROOT)),result_sha256=sha(folder/'result.json'),manifest_path=str((folder/'manifest.json').relative_to(ROOT)),wall_seconds=manifest['wall_seconds'],origin='fresh_qualified_r4_entire_C_panel',error=result.get('error'))
        fresh.append(row);save_at(OUT,'mcts_C_revalidation.jsonl',fresh,True);event(TASK,'qualified_C_observation_saved',**row);print(i+1,cell['seed'],result['status'],round(manifest['wall_seconds'],2),flush=True)
    assert len(fresh)==36 and all(r['status']=='ok' for r in fresh)
    old=rows(ORIGINAL/'mcts_observations.r2.jsonl');combined=[]
    for cell in c['matrix']:
        r=next(r for r in (fresh if cell['arm']=='C' else old) if all(r[k]==cell[k] for k in ['target','seed','arm']));r=dict(r)
        if cell['arm']!='C':r['origin']='inherited_same_task_r2_unmodified_active_A_B'
        combined.append(r)
    save_at(OUT,'mcts_observations.jsonl',combined,True)
    results={r['run_id']:json.loads((ROOT/r['result_path']).read_text()) for r in combined};pairs=[];trace=[]
    for ref in c['references']:
        for seed in c['seeds']:
            obs={arm:next(r for r in combined if r['target']==ref['target'] and r['seed']==seed and r['arm']==arm) for arm in ['A','B','C']}
            for sig in ref['reactions']:
                matches={arm:r['status']=='ok' and sig in signatures(results[r['run_id']],'mcts_action_created') for arm,r in obs.items()};pairs.append(dict(target=ref['target'],seed=seed,reference_signature=sig,matches=matches,status={arm:r['status'] for arm,r in obs.items()},gain=obs['A']['status']=='ok' and not matches['A'] and matches['C'],loss_A=matches['A'] and not matches['C'],loss_B=matches['B'] and not matches['C'],run_ids={arm:r['run_id'] for arm,r in obs.items()},origins={arm:r['origin'] for arm,r in obs.items()}))
            for arm,r in obs.items():trace.extend(dict(arm=arm,seed=seed,run_id=r['run_id'],observation_origin=r['origin'],**e) for e in results[r['run_id']].get('action_trace',[]))
    save_at(OUT,'paired_results.jsonl',pairs,True);save_at(OUT,'action_trace.jsonl',trace,True)
    source=rows(ORIGINAL/'single_step_A_B_C.jsonl');diagnostics=[]
    for target in c['primary_targets']:
        for arm in ['A','B','C']:
            if arm=='C':r=observe(target,arm);r['origin']='fresh_qualified_r4_single_step_no_tree_search'
            else:r=dict(next(r for r in source if r['arm']==arm and r['target']==target));r['origin']='inherited_same_task_unmodified_active_A_B_diagnostic'
            diagnostics.append(r);save_at(OUT,'single_step_A_B_C.jsonl',diagnostics,True)
    gaps=[];displacements=[]
    for ref in c['references']:
        obs={arm:next(r for r in diagnostics if r['target']==ref['target'] and r['arm']==arm) for arm in ['A','B','C']}
        for sig in ref['reactions']:
            matches={arm:r['status']=='ok' and sig in signatures(r,'filtered_accepted') for arm,r in obs.items()};gaps.append(dict(target=ref['target'],reference_signature=sig,matches=matches,status={arm:r['status'] for arm,r in obs.items()},known_gap=obs['A']['status']=='ok' and not matches['A'],gain=obs['A']['status']=='ok' and not matches['A'] and matches['C'],loss_A=matches['A'] and not matches['C'],loss_B=matches['B'] and not matches['C']))
        distinct=[]
        for e in obs['A']['trace']:
            if e['stage']=='filtered_accepted' and e['signature'] not in distinct:distinct.append(e['signature'])
        required=distinct[:3];a=signatures(obs['A'],'filtered_accepted');cc=signatures(obs['C'],'filtered_accepted');displacements.append(dict(target=ref['target'],required_generic_signatures=required,protected_missing=sorted(set(required)-cc),other_displaced=sorted(a-cc-set(required)),new_actions=sorted(cc-a),displaced_value='unknown chemical value'))
    save_at(OUT,'gap_register.jsonl',gaps,True);save_at(OUT,'candidate_displacement.json',dict(protection_violations=sum(bool(r['protected_missing']) for r in displacements),targets=displacements))
    report=dict(passed=installed_probe['status']=='ok',wheel=str(wheel.relative_to(ROOT)),wheel_sha256=sha(wheel),installed_probe=installed_probe,uses_main_matrix_cell=True,extra_service_attempts=0,source_payload_not_packaged=True,copied_v2_config_packaged=True,scope='latest installed qualified r4 wheel exercised one preregistered C matrix cell; unchanged default-off active path inherited explicitly')
    write(TASK,str((package/'report.json').relative_to(ROOT)),json.dumps(report,indent=2)+'\n');print('new C runs',len(fresh),'gain targets',len({p['target'] for p in pairs if all(q['gain'] for q in pairs if q['target']==p['target'])}))
if __name__=='__main__':main()
