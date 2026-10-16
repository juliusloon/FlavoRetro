"""Frozen A/B/C diagnostics and real MCTS; references stay outside the generator."""
import copy,json,os,time
from pathlib import Path
from aizynthfinder.aizynthfinder import AiZynthFinder
from aizynthfinder.utils.exceptions import RejectionException
from flavoretro.contracts import SearchRequest
from flavoretro.worker import effective_configuration
from flavoretro.workspace import root,config
from flavoretro.reviewed_resources import load_review,reaction_signature
from flavoretro.resources import sha
from scripts.task016_p1_sources import OUT,ROOT,save,rows,TASK
from scripts.operate import event

BUDGET=dict(mode='quick',engine='optimized',seconds=12.0,iterations=20,depth=2,branching=12,nodes=120,top_k=5)
def request(target,arm,seed=0):return SearchRequest(smiles=target,seed=seed,candidate_stock=True,glycoside_expansion=arm!='A',glycoside_library_version='v2' if arm=='C' else 'v1',**BUDGET)
def freeze_experiment():
    revised=OUT/'experiment_contract.r2.json'
    if revised.exists():return json.loads(revised.read_text())
    path=OUT/'experiment_contract.json'
    if path.exists():return json.loads(path.read_text())
    assert json.loads((OUT/'build_action_validation.v3.json').read_text())['passed']
    hold=rows(OUT/'holdout_views.jsonl');targets=sorted({r['target'] for r in hold});assert 12<=len(targets)<=18
    refs=[dict(target=t,reactions=sorted({r['reference_signature'] for r in hold if r['target']==t}),covalent_groups=sorted({r['covalent_signature'] for r in hold if r['target']==t}),instance_ids=sorted(r['instance_id'] for r in hold if r['target']==t)) for t in targets]
    files=sorted((ROOT/'flavoretro').glob('*.py'))+[ROOT/p for p in ['configs/search.json','configs/glycoside-expansion.json','configs/glycoside-library-v2.json']]
    models={r['path']:r['sha256'] for r in json.loads((ROOT/'metadata/sources.json').read_text())['files'] if r['role']=='external_model'}
    for p,h in models.items():assert sha(ROOT/p)==h
    matrix=[dict(target=t,seed=s,arm=arm) for t in targets for s in [0,1,2] for arm in ['A','B','C']]
    c=dict(schema_version=1,version='task016-p1-ABC-development-v1',approval_type='agent_delegated',budget=BUDGET,worker_wall_limit=60,seeds=[0,1,2],matrix=matrix,primary_targets=targets,references=refs,selection='all 12 frozen source-closed development_holdout targets, lexical canonical SMILES; no generic model result selection',code_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},models_sha256=models,split_sha256=sha(OUT/'development_split_manifest.json'),v2_manifest_sha256=sha(OUT/'template_source_manifest.v2.json'),v1_manifest_sha256=sha(ROOT/'outputs/task016/v1/template_source_manifest.json'),fusion_contract_sha256=sha(OUT/'fusion_contract.json'),review_binding=load_review().binding,stock_keys=sorted(load_review().keys),arms=dict(A='generic optimized; no domain',B='generic + frozen TASK016 v1 exact ionic species',C='generic + v2 build-only exact and scope templates, acid-O representation, protected first3 accepted generic signatures; fixed branch12'),allowed_differences=['domain version and payload','v2 scope candidate generation','v2 versioned representation match','v2 protected generic fusion','domain guard routes and trace metadata'],matching='full canonical isomeric precursor multiset + target; stereo/isotopes/components/multiplicity preserved; representation-normalized secondary axis not new chemistry',training_overlap='unknown',blind=False,human_reviewed=False,main_attempts=len(matrix),reserved_engineering_ceiling=18,hard_total_ceiling=180)
    save('experiment_contract.json',c);return c

def verify_binding(c):
    for key in ['code_sha256','models_sha256']:assert all(sha(ROOT/p)==h for p,h in c[key].items()),'experiment runtime drift'
    assert sha(OUT/'development_split_manifest.json')==c['split_sha256'];assert sha(OUT/'fusion_contract.json')==c['fusion_contract_sha256'];assert load_review().binding==c['review_binding'];assert sorted(load_review().keys)==c['stock_keys']

def signatures(r,stage):return {e['signature'] for e in r.get('trace',r.get('action_trace',[])) if e['stage']==stage and e.get('signature')}
def observe(target,arm):
    started=time.monotonic();req=request(target,arm);review=load_review();registry=None
    if arm=='B':from flavoretro.glycoside_expansion import load_registry;registry=load_registry()
    if arm=='C':from flavoretro.glycoside_library import load_registry;registry=load_registry()
    effective=effective_configuration(req,req.phases()[0],config('search.json'),root()/'data/raw/legacy/data',review,registry.binding if registry else None);effective['search']['algorithm_config']['trace_actions']=True
    finder=AiZynthFinder(configdict=copy.deepcopy(effective));finder.expansion_policy.select(['uspto','ringbreaker']+(['glycoside'] if registry else []));finder.filter_policy.select(['reviewed_evidence','known_hazards','uspto_filter']);finder.stock.select(['candidate']);finder.target_smiles=target;finder.prepare_tree();finder.tree.root.expand();trace=list(finder.tree.action_trace);errors=[]
    for rank,action in enumerate(finder.tree.root._children_actions):
        try:outcomes=action.reactants
        except Exception as exc:errors.append(dict(rank=rank,error=str(exc)));continue
        for index,out in enumerate(outcomes):
            variant=action.copy(index=index);error=None
            try:finder.filter_policy(variant)
            except RejectionException as exc:error=str(exc)
            trace.append(dict(stage='filtered_rejected' if error else 'filtered_accepted',target=target,candidate_rank=rank,outcome_index=index,raw_outcome_index=variant.metadata.get('raw_outcome_indices',list(range(len(outcomes))))[index],precursor_smiles=[m.smiles for m in out],signature=reaction_signature([m.smiles for m in out],[target]),policy=action.metadata.get('policy_name'),template_id=str(action.metadata.get('template_id',action.metadata.get('template_code'))),metadata=copy.deepcopy(variant.metadata),reason=error))
    assert not finder.tree.root.children,'diagnostics must not create nodes'
    return dict(target=target,arm=arm,status='ok',trace=trace,template_errors=errors,effective_config=effective,wall_seconds=time.monotonic()-started,actual_mcts_runs=0,review_binding=review.binding,domain_binding=registry.binding if registry else None)

def diagnose(c):
    verify_binding(c);assert not (OUT/'single_step_A_B_C.jsonl').exists(),'diagnostics already frozen'
    observations=[]
    for target in c['primary_targets']:
        for arm in ['A','B','C']:
            try:r=observe(target,arm)
            except Exception as exc:r=dict(target=target,arm=arm,status='error',error=type(exc).__name__+': '+str(exc),trace=[],actual_mcts_runs=0)
            observations.append(r);save('single_step_A_B_C.jsonl',observations,True);print(arm,r['status'],'filtered',len(signatures(r,'filtered_accepted')),r.get('error',''),flush=True)
    refs=[]
    for ref in c['references']:
        obs={arm:next(r for r in observations if r['target']==ref['target'] and r['arm']==arm) for arm in ['A','B','C']}
        for sig in ref['reactions']:
            matches={arm:obs[arm]['status']=='ok' and sig in signatures(obs[arm],'filtered_accepted') for arm in obs}
            refs.append(dict(target=ref['target'],reference_signature=sig,matches=matches,status={arm:obs[arm]['status'] for arm in obs},known_gap=obs['A']['status']=='ok' and not matches['A'],gain=obs['A']['status']=='ok' and not matches['A'] and matches['C'],loss_A=matches['A'] and not matches['C'],loss_B=matches['B'] and not matches['C']))
    save('gap_register.jsonl',refs,True)
    displacements=[]
    for target in c['primary_targets']:
        obs={arm:next(r for r in observations if r['target']==target and r['arm']==arm) for arm in ['A','B','C']};protected=[]
        for e in obs['A']['trace']:
            if e['stage']=='filtered_accepted' and e['signature'] not in protected:protected.append(e['signature'])
        required=protected[:3];C=signatures(obs['C'],'filtered_accepted');A=signatures(obs['A'],'filtered_accepted')
        displacements.append(dict(target=target,required_generic_signatures=required,protected_missing=sorted(set(required)-C),other_displaced=sorted(A-C-set(required)),new_actions=sorted(C-A),displaced_value='unknown; generic candidates are not scored chemical ground truth'))
    save('candidate_displacement.json',dict(protection_violations=sum(bool(r['protected_missing']) for r in displacements),targets=displacements))
    print('single step gain',sum(r['gain'] for r in refs),'/',sum(r['known_gap'] for r in refs),'protection violations',sum(bool(r['protected_missing']) for r in displacements))

def mcts(c):
    from flavoretro.service import search
    verify_binding(c);os.environ.update(FLAVORETRO_TASK016_LEDGER=str(OUT/'run_ledger.jsonl'),FLAVORETRO_TASK016_TRACE='1',FLAVORETRO_TASK016_PURPOSE='task016_p1_ABC_development')
    existing=rows(OUT/'mcts_observations.r2.jsonl');done={(r['target'],r['seed'],r['arm']) for r in existing}
    for cell in c['matrix']:
        if (cell['target'],cell['seed'],cell['arm']) in done:continue
        verify_binding(c);result=search(request(cell['target'],cell['arm'],cell['seed']),run_root=OUT/'paired-runs');folder=OUT/'paired-runs'/result['run_id'];manifest=json.loads((folder/'manifest.json').read_text())
        r=dict(**cell,run_id=result['run_id'],status=result['status'],result_path=str((folder/'result.json').relative_to(ROOT)),result_sha256=sha(folder/'result.json'),manifest_path=str((folder/'manifest.json').relative_to(ROOT)),wall_seconds=manifest['wall_seconds'],error=result.get('error'))
        with (OUT/'mcts_observations.r2.jsonl').open('a') as f:f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
        event(TASK,'ABC_observation_saved',**r);print(cell['arm'],cell['seed'],result['status'],round(manifest['wall_seconds'],2),flush=True)
    summarize(c)

def summarize(c):
    observations=rows(OUT/'mcts_observations.r2.jsonl');pairs=[];traces=[]
    for ref in c['references']:
        for seed in c['seeds']:
            obs={arm:next(r for r in observations if r['target']==ref['target'] and r['seed']==seed and r['arm']==arm) for arm in ['A','B','C']};results={arm:json.loads((ROOT/r['result_path']).read_text()) for arm,r in obs.items()}
            for sig in ref['reactions']:
                matches={arm:r['status']=='ok' and sig in signatures(r,'mcts_action_created') for arm,r in results.items()};pairs.append(dict(target=ref['target'],seed=seed,reference_signature=sig,matches=matches,status={arm:r['status'] for arm,r in results.items()},gain=results['A']['status']=='ok' and not matches['A'] and matches['C'],loss_A=matches['A'] and not matches['C'],loss_B=matches['B'] and not matches['C'],run_ids={arm:r['run_id'] for arm,r in results.items()},nodes={arm:sum(p['node_count'] for p in r.get('phases',[])) for arm,r in results.items()}))
            for arm,result in results.items():
                traces.extend(dict(arm=arm,seed=seed,run_id=result['run_id'],**e) for e in result.get('action_trace',[]))
    save('paired_results.jsonl',pairs,True);save('action_trace.jsonl',traces,True)
    gaps=rows(OUT/'gap_register.jsonl');newtargets={p['target'] for p in pairs if all(q['gain'] for q in pairs if q['target']==p['target'])};ledger=rows(OUT/'run_ledger.jsonl');done=[r for r in ledger if r['phase']=='finished'];counts=json.loads((OUT/'counting_contract.json').read_text())['counts']
    save('metrics.json',dict(schema_version=1,scope='source-closed development holdout candidate coverage; training overlap unknown; no independent chemical activity/condition validation',library=counts,templates=dict(total=len(rows(OUT/'templates.jsonl')),exact=52,scope=5,new_exact=48,new_scope=5,new_total=53),candidate=dict(N=len(gaps),N_gap=sum(r['known_gap'] for r in gaps),gain_reactions=sum(r['gain'] for r in gaps),gain_targets=len({r['target'] for r in gaps if r['gain']}),recovery_rate=sum(r['gain'] for r in gaps)/sum(r['known_gap'] for r in gaps) if any(r['known_gap'] for r in gaps) else None,matches={arm:sum(r['matches'][arm] for r in gaps) for arm in ['A','B','C']},loss_A=sum(r['loss_A'] for r in gaps),loss_B=sum(r['loss_B'] for r in gaps)),actual_mcts=dict(matrix_attempts=len(observations),paired_cells=len(pairs),all_three_seed_gain_targets=len(newtargets),gain_targets=sorted(newtargets),gain_pairs=sum(p['gain'] for p in pairs),loss_A=sum(p['loss_A'] for p in pairs),loss_B=sum(p['loss_B'] for p in pairs),errors=sum(r['status']!='ok' for r in observations),by_seed={str(s):sum(p['gain'] for p in pairs if p['seed']==s) for s in c['seeds']}),run_budget=dict(attempts=len({r['run_id'] for r in ledger}),ceiling=180,finished=len(done),max_wall_seconds=max(r['wall_seconds'] for r in done),engineering_attempts=len({r['run_id'] for r in ledger})-len(observations),engineering_ceiling=18),protection_violations=json.loads((OUT/'candidate_displacement.json').read_text())['protection_violations'],human_reviewed=False,independent_chemical_validation=False,release_ready=False))
    print(json.dumps(json.loads((OUT/'metrics.json').read_text())['actual_mcts'],ensure_ascii=False))
if __name__=='__main__':
    import sys
    c=freeze_experiment()
    if '--diagnose' in sys.argv:diagnose(c)
    elif '--mcts' in sys.argv:mcts(c)
    else:print('experiment frozen',len(c['matrix']),'main attempts')
