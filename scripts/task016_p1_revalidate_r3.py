"""Revalidate the whole changed source component; preserve provably unaffected controls."""
import json,os,shutil,subprocess,sys,tempfile,zipfile
from scripts.task016_p1_sources import ROOT,OUT,rows,save,TASK
from scripts.operate import event
from scripts.task016_p1_evaluate import request,verify_binding,signatures
from flavoretro.service import search
from flavoretro.resources import sha

def main():
    c=json.loads((OUT/'experiment_contract.r3.json').read_text());verify_binding(c)
    package=ROOT/'outputs/validation/task016-p1-package-r3';assert not package.exists();package.mkdir();src=package/'source';src.mkdir();shutil.copy2(ROOT/'pyproject.toml',src/'pyproject.toml');shutil.copytree(ROOT/'flavoretro',src/'flavoretro',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    b=subprocess.run([sys.executable,'-B','-m','build','--wheel','--no-isolation','--outdir',str(package/'dist')],cwd=src,text=True,capture_output=True);(package/'build.log').write_text(b.stdout+b.stderr);assert b.returncode==0,b.stderr;wheel=next((package/'dist').glob('*.whl'))
    p=subprocess.run([sys.executable,'-B','-m','pip','install','--no-deps','--target',str(package/'installed'),str(wheel)],text=True,capture_output=True);(package/'install.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    os.environ.update(FLAVORETRO_WORKSPACE=str(ROOT),FLAVORETRO_TASK016_LEDGER=str(OUT/'run_ledger.jsonl'),FLAVORETRO_TASK016_TRACE='1',FLAVORETRO_TASK016_PURPOSE='task016_p1_r3_C_component_revalidation')
    fresh=[];installed_probe=None
    for i,cell in enumerate(c['boundary_revision']['fresh_matrix']):
        verify_binding(c)
        if i==0:
            code="""import sys,json;sys.path.insert(0,sys.argv[1]);from flavoretro.service import search;from flavoretro.contracts import SearchRequest;from flavoretro.workspace import PACKAGE;r=search(SearchRequest.model_validate(json.loads(sys.argv[2])),run_root=sys.argv[3]);print(json.dumps(dict(run_id=r['run_id'],status=r['status'],package=str(PACKAGE),binding=r.get('domain_binding'))))"""
            with tempfile.TemporaryDirectory() as scratch:
                x=subprocess.run([sys.executable,'-I','-B','-c',code,str(package/'installed'),json.dumps(request(cell['target'],'C',cell['seed']).payload()),str(OUT/'paired-runs-r3')],cwd=scratch,env=os.environ,text=True,capture_output=True)
            (package/'installed-main-cell.log').write_text(x.stdout+x.stderr);assert x.returncode==0,x.stderr;installed_probe=json.loads(x.stdout);assert installed_probe['package'].startswith(str(package/'installed'));result=json.loads((OUT/'paired-runs-r3'/installed_probe['run_id']/'result.json').read_text())
        else:result=search(request(cell['target'],'C',cell['seed']),run_root=OUT/'paired-runs-r3')
        folder=OUT/'paired-runs-r3'/result['run_id'];manifest=json.loads((folder/'manifest.json').read_text());row=dict(**cell,run_id=result['run_id'],status=result['status'],result_path=str((folder/'result.json').relative_to(ROOT)),result_sha256=sha(folder/'result.json'),manifest_path=str((folder/'manifest.json').relative_to(ROOT)),wall_seconds=manifest['wall_seconds'],origin='fresh_r3_affected_source_component',error=result.get('error'))
        fresh.append(row);save('mcts_C_revalidation.r3.jsonl',fresh,True);event(TASK,'r3_C_observation_saved',**row);print(cell['seed'],result['status'],round(manifest['wall_seconds'],2),flush=True)
    assert len(fresh)==24 and all(r['status']=='ok' for r in fresh)
    old=rows(OUT/'mcts_observations.r2.jsonl');combined=[]
    for cell in c['matrix']:
        row=next((r for r in fresh if all(r[k]==cell[k] for k in ['target','seed','arm'])),None)
        if row is None:
            row=dict(next(r for r in old if all(r[k]==cell[k] for k in ['target','seed','arm'])));row['origin']='retained_r2_unaffected_generic_or_v1_control' if cell['arm']!='C' else 'retained_r2_proven_zero_domain_entire_tree'
        combined.append(row)
    save('mcts_observations.r3.jsonl',combined,True)
    results={r['run_id']:json.loads((ROOT/r['result_path']).read_text()) for r in combined};pairs=[];trace=[]
    for ref in c['references']:
        for seed in c['seeds']:
            obs={arm:next(r for r in combined if r['target']==ref['target'] and r['seed']==seed and r['arm']==arm) for arm in ['A','B','C']}
            for sig in ref['reactions']:
                matches={arm:sig in signatures(results[r['run_id']],'mcts_action_created') for arm,r in obs.items()};pairs.append(dict(target=ref['target'],seed=seed,reference_signature=sig,matches=matches,status={arm:r['status'] for arm,r in obs.items()},gain=not matches['A'] and matches['C'],loss_A=matches['A'] and not matches['C'],loss_B=matches['B'] and not matches['C'],run_ids={arm:r['run_id'] for arm,r in obs.items()},origins={arm:r['origin'] for arm,r in obs.items()}))
            for arm,r in obs.items():trace.extend(dict(arm=arm,seed=seed,run_id=r['run_id'],observation_origin=r['origin'],**e) for e in results[r['run_id']].get('action_trace',[]))
    save('paired_results.r3.jsonl',pairs,True);save('action_trace.r3.jsonl',trace,True)
    source=rows(OUT/'single_step_A_B_C.jsonl');checks=[]
    from scripts.task016_p1_evaluate import observe
    for target in c['primary_targets']:
        result=observe(target,'C');oldrow=next(r for r in source if r['arm']=='C' and r['target']==target);checks.append(dict(target=target,status=result['status'],actual_mcts_runs=0,generated_signature_set_equal=signatures(result,'generated')==signatures(oldrow,'generated'),retained_signature_set_equal=signatures(result,'after_truncation')==signatures(oldrow,'after_truncation'),filtered_signature_set_equal=signatures(result,'filtered_accepted')==signatures(oldrow,'filtered_accepted')))
    save('single_step_equivalence.r3.json',dict(passed=all(all(r[k] for k in ['generated_signature_set_equal','retained_signature_set_equal','filtered_signature_set_equal']) for r in checks),checks=checks,actual_mcts_runs=0));assert all(r['filtered_signature_set_equal'] for r in checks)
    report=dict(passed=installed_probe['status']=='ok',wheel=str(wheel.relative_to(ROOT)),wheel_sha256=sha(wheel),installed_probe=installed_probe,uses_main_matrix_cell=True,extra_service_attempts=0,source_payload_not_packaged=True,copied_v2_config_packaged=True,scope='fresh installed r3 wheel exercised one exact preregistered C matrix cell; generic default-off probe inherited from unchanged r2 active path')
    (package/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('r3 gains',len({p['target'] for p in pairs if all(q['gain'] for q in pairs if q['target']==p['target'])}),'new runs',len(fresh))
if __name__=='__main__':main()
