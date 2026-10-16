"""Old exposed calibration/regression only; fresh transfer remains not executed."""
import sys,json,os,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,rows
from scripts.operate import write,event
from flavoretro.resources import sha
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.reviewed_resources import load_review
from flavoretro.glycoside_library_v3 import load_registry
OUT=ROOT/'outputs/task016-p2/v2';T='TASK-016-P2'
BUDGET=dict(mode='quick',engine='optimized',seconds=12.0,iterations=20,depth=2,branching=12,nodes=120,top_k=5)
def save(n,v):write(T,str((OUT/n).relative_to(ROOT)),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def freeze():
    p=OUT/'experiment_contract.json'
    if p.exists():return json.loads(p.read_text())
    assert json.loads((OUT/'build_action_validation.json').read_text())['passed']
    hold=rows(ROOT/'outputs/task016-p1/v2/holdout_views.jsonl')
    oldC=[r for r in rows(ROOT/'outputs/task016-p1/v2/instances.jsonl') if r['category']=='C_formation']
    source=hold+oldC;targets=sorted({r['target'] for r in source});assert len(targets)==17
    refs=[dict(target=target,reference_signatures=sorted({r['reference_signature'] for r in source if r['target']==target}),instance_ids=sorted(r['instance_id'] for r in source if r['target']==target),category=next(r['category'] for r in source if r['target']==target),original_P1_role=next(r['template_role'] for r in source if r['target']==target)) for target in targets]
    models={r['path']:r['sha256'] for r in json.loads((ROOT/'metadata/sources.json').read_text())['files'] if r['role']=='external_model'}
    files=list((ROOT/'flavoretro').glob('*.py'))+[ROOT/p for p in ['configs/search.json','configs/glycoside-expansion.json','configs/glycoside-library-v2.json','configs/glycoside-library-v3.json']]
    c=dict(task=T,approval_type='agent_delegated',phase='old_calibration_and_regression',version='P2-legacy-D-v1',budget=BUDGET,seeds=[0,1,2],references=refs,matrix=[dict(target=t,seed=s,arm='D') for t in targets for s in [0,1,2]],primary_fresh_ABD_matrix=[],fresh_transfer_executed=False,G2_minimum_unmet=True,code_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},models_sha256=models,v3_manifest_sha256=sha(OUT/'template_source_manifest.json'),v2_manifest_sha256=sha(ROOT/'outputs/task016-p1/v2/template_source_manifest.json'),split_sha256=sha(OUT/'development_split_manifest.json'),review_binding=load_review().binding,stock_keys=sorted(load_review().keys),selection='fixed P1 twelve old targets plus all five exact C targets; no target selection based on new model outputs',validation_attempt_plan=51,validation_ceiling=213,engineering_ceiling=27,total_ceiling=240,wall_ceiling_seconds=60,scientific_thresholds_unchanged=True)
    save('experiment_contract.json',c);return c
def verify(c):
    for key in ['code_sha256','models_sha256']:assert all(sha(ROOT/p)==h for p,h in c[key].items()),'frozen runtime drift'
    assert sha(OUT/'template_source_manifest.json')==c['v3_manifest_sha256']
    assert sha(ROOT/'outputs/task016-p1/v2/template_source_manifest.json')==c['v2_manifest_sha256']
    assert load_review().binding==c['review_binding'] and sorted(load_review().keys)==c['stock_keys']
def run(c):
    os.environ.update(FLAVORETRO_TASK016_LEDGER=str(ROOT/'outputs/task016-p2/v1/run_ledger.jsonl'),FLAVORETRO_TASK016_PURPOSE='task016_p2_validation',FLAVORETRO_TASK016_TRACE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    path=OUT/'mcts_observations.jsonl';obs=rows(path);done={(r['target'],r['seed']) for r in obs}
    for cell in c['matrix']:
        if (cell['target'],cell['seed']) in done:continue
        verify(c);r=search(SearchRequest(smiles=cell['target'],seed=cell['seed'],candidate_stock=True,glycoside_expansion=True,glycoside_library_version='v3',**BUDGET),run_root=OUT/'legacy-runs')
        folder=OUT/'legacy-runs'/r['run_id'];m=json.loads((folder/'manifest.json').read_text())
        item=dict(**cell,run_id=r['run_id'],status=r['status'],result_path=str((folder/'result.json').relative_to(ROOT)),result_sha256=sha(folder/'result.json'),manifest_path=str((folder/'manifest.json').relative_to(ROOT)),wall_seconds=m['wall_seconds'],error=r.get('error'))
        with path.open('a') as f:f.write(json.dumps(item,ensure_ascii=False,sort_keys=True)+'\n')
        event(T,'legacy_D_observation',**item)
        print(len(rows(path)),cell['seed'],r['status'],round(m['wall_seconds'],2),flush=True)
    summarize(c)
def summarize(c):
    obs=rows(OUT/'mcts_observations.jsonl');checks=[];trace=[]
    for ref in c['references']:
        byseed=[]
        for seed in c['seeds']:
            o=next(r for r in obs if r['target']==ref['target'] and r['seed']==seed);r=json.loads((ROOT/o['result_path']).read_text())
            actual={e['signature'] for e in r.get('action_trace',[]) if e['stage']=='mcts_action_created' and e.get('signature')}
            byseed.append(dict(seed=seed,status=r['status'],reference_created=all(sig in actual for sig in ref['reference_signatures']),run_id=o['run_id'],wall_seconds=o['wall_seconds']))
            trace.extend(dict(seed=seed,run_id=o['run_id'],**e) for e in r.get('action_trace',[]))
        checks.append(dict(**ref,by_seed=byseed,all_three_seed_created=all(o['status']=='ok' and o['reference_created'] for o in byseed),new_transfer_gain=False))
    save('legacy_regression.json',dict(scope='previous exposed sources; no new transfer evidence',checks=checks,old_SS_targets=len([r for r in checks if r['category']=='sugar_sugar_formation']),old_SS_all_three_seed_created=sum(r['all_three_seed_created'] for r in checks if r['category']=='sugar_sugar_formation'),old_C_all_three_seed_created=sum(r['all_three_seed_created'] for r in checks if r['category']=='C_formation'),old_O_all_three_seed_created=sum(r['all_three_seed_created'] for r in checks if r['category']=='O_formation'),runs=len(obs),errors=sum(r['status']!='ok' for r in obs)))
    write(T,str((OUT/'action_trace.jsonl').relative_to(ROOT)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in trace))
    print('old SS',sum(r['all_three_seed_created'] for r in checks if r['category']=='sugar_sugar_formation'),'/4; no new transfer claim',flush=True)
if __name__=='__main__':
    c=freeze()
    if '--run' in sys.argv:run(c)
    else:print('Frozen17 old targets51 D-seed cells; no fresh A/B/D matrix')
