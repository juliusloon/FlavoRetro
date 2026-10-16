"""Single-step policy observations, with no tree_search or actual MCTS run."""
import copy,json,os,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from aizynthfinder.aizynthfinder import AiZynthFinder
from aizynthfinder.utils.exceptions import RejectionException
from flavoretro.contracts import SearchRequest
from flavoretro.worker import effective_configuration
from flavoretro.workspace import root,config
from flavoretro.reviewed_resources import load_review,reaction_signature
from flavoretro.glycoside_expansion import load_registry
from flavoretro.resources import sha
from scripts.operate import write


def observe(target, enabled, contract):
    started=time.monotonic();registry=load_registry() if enabled else None
    request=SearchRequest(smiles=target,glycoside_expansion=enabled,candidate_stock=contract['candidate_stock'],seed=0,**contract['budget'])
    settings=config('search.json');review=load_review();budget=request.phases()[0]
    effective=effective_configuration(request,budget,settings,root()/'data/raw/legacy/data',review,registry.binding if registry else None)
    effective['search']['algorithm_config']['trace_actions']=True
    finder=AiZynthFinder(configdict=copy.deepcopy(effective));finder.expansion_policy.select(['uspto','ringbreaker']+(['glycoside'] if enabled else []));finder.filter_policy.select(['reviewed_evidence','known_hazards','uspto_filter']);finder.stock.select(['candidate']);finder.target_smiles=target;finder.prepare_tree()
    start=time.monotonic();finder.tree.root.expand();generation_seconds=time.monotonic()-start
    trace=list(finder.tree.action_trace);filter_seconds=0;template_errors=[]
    for action in finder.tree.root._children_actions:
        try:
            outcomes=action.reactants
        except Exception as exc:
            template_errors.append(dict(template_id=str(action.metadata.get('template_code')),error=str(exc)));continue
        for index,outcome in enumerate(outcomes):
            variant=action.copy(index=index);start=time.monotonic()
            error=None
            try:
                finder.filter_policy(variant)
            except RejectionException as exc:
                error=str(exc)
            filter_seconds+=time.monotonic()-start
            trace.append(dict(stage='filtered_rejected' if error else 'filtered_accepted',target=target,outcome_index=index,precursor_smiles=[m.smiles for m in outcome],signature=reaction_signature([m.smiles for m in outcome],[target]),policy=action.metadata.get('policy_name'),template_id=str(action.metadata.get('template_id',action.metadata.get('template_code'))),metadata=copy.deepcopy(variant.metadata),reason=error))
    assert not finder.tree.root.children, 'single-step diagnostics must not create tree nodes'
    return dict(target=target,status='ok',domain_enabled=enabled,wall_seconds=time.monotonic()-started,generation_seconds=generation_seconds,filter_seconds=filter_seconds,template_errors=template_errors,trace=trace,effective_config=effective,review_binding=review.binding,domain_binding=registry.binding if registry else None,actual_mcts_runs=0,coverage_scope='model cutoff_number=12 per generic policy, fusion branch cap=12, all retained outcomes filtered; no absolute model inability claim')


if __name__=='__main__':
    enabled='--augmented' in sys.argv
    folder=root()/'outputs/task016/v1';contract=json.loads((folder/'development_contract.json').read_text());name='augmented_observations.jsonl' if enabled else 'baseline_observations.jsonl'
    assert not (folder/name).exists(), 'immutable observations already exist'
    freeze=folder/'development_runtime_binding.json'
    code_paths=sorted(Path('flavoretro').glob('*.py'))+[Path('configs/search.json'),Path('configs/glycoside-expansion.json'),Path(__file__).relative_to(root())]
    model_manifest=json.loads((root()/'metadata/sources.json').read_text())
    models={r['path']:r['sha256'] for r in model_manifest['files'] if r['role']=='external_model'}
    current=dict(code_sha256={str(p):sha(root()/p) for p in code_paths},model_sha256=models,development_contract_sha256=sha(folder/'development_contract.json'),template_manifest_sha256=sha(folder/'template_source_manifest.json'))
    assert all(sha(root()/p)==h for p,h in models.items())
    if freeze.exists():assert json.loads(freeze.read_text())==current,'runtime/code/model drift after preregistration'
    else:write('TASK-016',str(freeze.relative_to(root())),json.dumps(current,indent=2)+'\n')
    rows=[]
    for target in contract['primary_targets']:
        try:row=observe(target,enabled,contract)
        except Exception as exc:row=dict(target=target,status='error',domain_enabled=enabled,error=f'{type(exc).__name__}: {exc}',trace=[],actual_mcts_runs=0)
        rows.append(row);print(json.dumps(dict(target=target,status=row['status'],filtered=sum(e['stage']=='filtered_accepted' for e in row['trace']),error=row.get('error')),ensure_ascii=False))
    write('TASK-016',str((folder/name).relative_to(root())),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
    if not enabled:
        refs=[json.loads(l) for l in (folder/'reference_precursors.jsonl').read_text().splitlines()];gaps=[]
        for ref in refs:
            row=next(r for r in rows if r['target']==ref['target']);matches={stage:any(e['stage']==stage and e.get('signature')==ref['reference_signature'] for e in row['trace']) for stage in ['generated','after_truncation','filtered_accepted']}
            gaps.append(dict(instance_id=ref['instance_id'],target=ref['target'],reference_signature=ref['reference_signature'],baseline_status=row['status'],stages=matches,known_gap=row['status']=='ok' and not matches['filtered_accepted'],scope='frozen development query; not absolute model inability'))
        write('TASK-016',str((folder/'gap_register.jsonl').relative_to(root())),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in gaps))
