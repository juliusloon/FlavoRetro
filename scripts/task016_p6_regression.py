"""P6 final frozen v6 legacy 17 x 3 check; no fresh transfer claim.

Same P1 target set and P2/P3 parameters; source losses compared to frozen P3.
"""
import sys,json,os,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p6_common import ROOT,rows
from scripts.operate import write,event
from flavoretro.resources import sha
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.reviewed_resources import load_review
from flavoretro.glycoside_library_v6 import load_registry
OUT=ROOT/'outputs/task016-p6/v1';T='TASK-016-P6'
BUDGET=dict(mode='quick',engine='optimized',seconds=12.0,iterations=20,depth=2,branching=12,nodes=120,top_k=5)

def save(n,v):write(T,str((OUT/n).relative_to(ROOT)),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')

def freeze():
    p=OUT/'experiment_contract.json'
    if p.exists():return json.loads(p.read_text())
    split=dict(holdout_targets_by_class={})
    hold=[r for r in rows(ROOT/'outputs/task016-p1/v2/holdout_views.jsonl')]
    oldC=[r for r in rows(ROOT/'outputs/task016-p1/v2/instances.jsonl') if r['category']=='C_formation']
    source=hold+oldC;targets=sorted({r['target'] for r in source});assert len(targets)==17
    refs=[dict(target=target,reference_signatures=sorted({r['reference_signature'] for r in source if r['target']==target}),instance_ids=sorted(r['instance_id'] for r in source if r['target']==target),category=next(r['category'] for r in source if r['target']==target)) for target in targets]
    models={r['path']:r['sha256'] for r in json.loads((ROOT/'metadata/sources.json').read_text())['files'] if r['role']=='external_model'}
    files=list((ROOT/'flavoretro').glob('*.py'))+[ROOT/p for p in ['configs/search.json','configs/glycoside-expansion.json','configs/glycoside-library-v2.json','configs/glycoside-library-v3.json','configs/glycoside-library-v6.json']]
    c=dict(task=T,approval_type='agent_delegated',phase='old_calibration_and_regression_v6_E_arm',version='P6-legacy-E-v1',budget=BUDGET,seeds=[0,1,2],references=refs,matrix=[dict(target=t,seed=s,arm='E') for t in targets for s in [0,1,2]],fresh_ABE_matrix=dict(executed=False,reason='C stop 6 scope_holdout_domain_mismatch; SS stop 1 runtime panel shortage; metrics null'),holdout_targets=dict(C=6,SS=1),code_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},models_sha256=models,v6_manifest_sha256=sha(OUT/'template_source_manifest.json'),v3_manifest_sha256=sha(ROOT/'outputs/task016-p2/v2/template_source_manifest.json'),review_binding=load_review().binding,stock_keys=sorted(load_review().keys),selection='fixed P1 twelve old targets plus all five exact C targets; no target selection based on new model outputs',validation_attempt_plan=51,validation_ceiling=426,engineering_ceiling=54,total_ceiling=480,wall_ceiling_seconds=60,scientific_thresholds_unchanged=True)
    save('experiment_contract.json',c);return c

def verify(c):
    for key in ['code_sha256','models_sha256']:assert all(sha(ROOT/p)==h for p,h in c[key].items()),'frozen runtime drift'
    assert sha(OUT/'template_source_manifest.json')==c['v6_manifest_sha256']
    assert sha(ROOT/'outputs/task016-p2/v2/template_source_manifest.json')==c['v3_manifest_sha256']
    assert load_review().binding==c['review_binding'] and sorted(load_review().keys)==c['stock_keys']

def run(c):
    os.environ.update(FLAVORETRO_TASK016_LEDGER=str(ROOT/'outputs/task016-p6/v1/run_ledger.jsonl'),FLAVORETRO_TASK016_PURPOSE='p6_legacy',FLAVORETRO_TASK016_TRACE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    path=OUT/'mcts_observations.jsonl';obs=rows(path) if path.exists() else []; done={(r['target'],r['seed']) for r in obs}
    ledger=rows(ROOT/'outputs/task016-p6/v1/run_ledger.jsonl') if (ROOT/'outputs/task016-p6/v1/run_ledger.jsonl').exists() else []
    used=len([r for r in ledger if r.get('purpose')=='p6_legacy' or 'attempt' in str(r).lower()]) or len(ledger)
    assert len(ledger)+ (51-len(done)) <= 426, 'validation ceiling'
    for cell in c['matrix']:
        if (cell['target'],cell['seed']) in done:continue
        verify(c);r=search(SearchRequest(smiles=cell['target'],seed=cell['seed'],candidate_stock=True,glycoside_expansion=True,glycoside_library_version='v6',**BUDGET),run_root=OUT/'e-runs')
        folder=OUT/'e-runs'/r['run_id'];m=json.loads((folder/'manifest.json').read_text())
        item=dict(**cell,run_id=r['run_id'],status=r['status'],result_path=str((folder/'result.json').relative_to(ROOT)),result_sha256=sha(folder/'result.json'),manifest_path=str((folder/'manifest.json').relative_to(ROOT)),wall_seconds=m['wall_seconds'],error=r.get('error'))
        with path.open('a') as f:f.write(json.dumps(item,ensure_ascii=False,sort_keys=True)+'\n')
        event(T,'E_arm_observation',**item)
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
        checks.append(dict(**ref,by_seed=byseed,all_three_seed_created=all(o['status']=='ok' and o['reference_created'] for o in byseed)))
    old=json.loads((ROOT/'outputs/task016-p3/v1/e_regression.json').read_text()); previous={r['target']:r for r in old['checks']}
    loss=[r['target'] for r in checks if previous[r['target']]['all_three_seed_created'] and not r['all_three_seed_created']]
    save('e_regression.json',dict(new_reference_loss=loss,scope='E arm (v6 chain) on the frozen 17 old targets; old-capability retention only, no fresh transfer claim',checks=checks,old_SS_targets=len([r for r in checks if r['category']=='sugar_sugar_formation']),old_SS_all_three_seed_created=sum(r['all_three_seed_created'] for r in checks if r['category']=='sugar_sugar_formation'),old_C_all_three_seed_created=sum(r['all_three_seed_created'] for r in checks if r['category']=='C_formation'),old_O_all_three_seed_created=sum(r['all_three_seed_created'] for r in checks if r['category']=='O_formation'),runs=len(obs),errors=sum(r['status']!='ok' for r in obs)))
    write(T,str((OUT/'action_trace.jsonl').relative_to(ROOT)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in trace))
    assert not loss, 'new legacy reference loss'
    print('E arm: old SS',sum(r['all_three_seed_created'] for r in checks if r['category']=='sugar_sugar_formation'),'/4; C',sum(r['all_three_seed_created'] for r in checks if r['category']=='C_formation'),'/5; O',sum(r['all_three_seed_created'] for r in checks if r['category']=='O_formation'),'/8; runs',len(obs),flush=True)

if __name__=='__main__':
    c=freeze()
    if '--run' in sys.argv:run(c)
    else:print('Frozen 17 old targets x 3 seeds E-arm contract; run with --run')
