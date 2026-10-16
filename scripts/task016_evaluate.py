"""Fixed, small paired development MCTS comparison; every attempt stays in the ledger."""
import json,os,sys,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.workspace import root
from flavoretro.resources import sha
from flavoretro.service import search
from flavoretro.contracts import SearchRequest
from scripts.operate import write


def read_jsonl(path):return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
def ratio(n,d):return n/d if d else None

def signatures(observation,stage):
    return {e['signature'] for e in observation.get('trace',observation.get('action_trace',[])) if e['stage']==stage and e.get('signature')}


def summarize_pairs(pairs,N):
    gains=sum(p['gain'] for p in pairs);losses=sum(p['loss'] for p in pairs)
    return dict(M=len(pairs),gain_pairs=gains,loss_pairs=losses,gain_rate=ratio(gains,len(pairs)),target_gains=len({p['target'] for p in pairs if p['gain']}),by_seed={str(s):dict(M=sum(p['seed']==s for p in pairs),gains=sum(p['seed']==s and p['gain'] for p in pairs),losses=sum(p['seed']==s and p['loss'] for p in pairs)) for s in sorted({p['seed'] for p in pairs})},failures=sum(p['baseline_status']!='ok' or p['augmented_status']!='ok' for p in pairs),N_reference=N)


def metrics(folder,pairs):
    contract=json.loads((folder/'development_contract.json').read_text());refs=read_jsonl(folder/'reference_precursors.jsonl');a={r['target']:r for r in read_jsonl(folder/'baseline_observations.jsonl')};b={r['target']:r for r in read_jsonl(folder/'augmented_observations.jsonl')};rows=[]
    for ref in refs:
        aa,bb=a[ref['target']],b[ref['target']];am=aa['status']=='ok' and ref['reference_signature'] in signatures(aa,'filtered_accepted');bm=bb['status']=='ok' and ref['reference_signature'] in signatures(bb,'filtered_accepted')
        gap=aa['status']=='ok' and not am
        rows.append(dict(instance_id=ref['instance_id'],target=ref['target'],baseline_status=aa['status'],augmented_status=bb['status'],baseline_match=am,augmented_match=bm,known_gap=gap,gain=gap and bm,loss=am and not bm))
    N=contract['N'];gap=sum(r['known_gap'] for r in rows);G=sum(r['gain'] for r in rows);A=sum(r['baseline_match'] for r in rows);B=sum(r['augmented_match'] for r in rows)
    ledger=read_jsonl(folder/'run_ledger.jsonl');ids={r['run_id'] for r in ledger if r.get('run_id')};done=[r for r in ledger if r.get('phase')=='finished' or r.get('sequence')==1]
    walls=[r['wall_seconds'] for r in done if r.get('wall_seconds') is not None]
    failed=[r for r in done if r['status']!='ok'];unknown=sum(r['baseline_status']!='ok' for r in rows)
    return dict(schema_version=1,scope='development_exposed, source-species restricted candidate coverage; not chemical accuracy, generalization, or blind benchmark',candidate_coverage=dict(N=N,N_gap=gap,N_support=0,M_support=0,baseline_matches=A,augmented_matches=B,C_A=ratio(A,N),C_B=ratio(B,N),G=G,recovery_rate=ratio(G,gap),net_percentage_points=100*(B-A)/N if N else None,losses=sum(r['loss'] for r in rows),baseline_unknown=unknown,unknown_rate=ratio(unknown,N),reference_rows=rows),actual_mcts=summarize_pairs(pairs,N),run_budget=dict(reserved_or_attempted=len(ids),ceiling=120,ledger_completed=len(done),failed_attempts=len(failed),max_wall_seconds=max(walls) if walls else None,wall_limit=60,counts_include_synthetic_service_error_fixtures='ledger conservatively reserves these too; reports classify execution_source'),paired_cost=dict(mean_wall_delta=statistics.mean(p['augmented_wall_seconds']-p['baseline_wall_seconds'] for p in pairs) if pairs else None,mean_node_delta=statistics.mean(p['augmented_nodes']-p['baseline_nodes'] for p in pairs) if pairs else None),closure=dict(evidence_closed=0,status='partial/surrogate only; fixed stock is not certified supply'),training_overlap='unknown',independent_chemical_validation=False,release_ready=False)


def main():
    folder=root()/'outputs/task016/v1';contract=json.loads((folder/'development_contract.json').read_text());binding=json.loads((folder/'development_runtime_binding.json').read_text())
    for group in ['code_sha256','model_sha256']:
        assert all(sha(root()/p)==h for p,h in binding[group].items()),'frozen runtime drift'
    requests=[dict(target=target,seed=seed,group=group,domain_enabled=group=='B') for target in contract['primary_targets'] for seed in contract['seeds'] for group in ['A','B']]
    frozen=dict(requests=requests,evaluation_script_sha256=sha(__file__),runtime_binding_sha256=sha(folder/'development_runtime_binding.json'),contract_sha256=sha(folder/'development_contract.json'),budget=contract['budget'],worker_wall_limit=60)
    path=folder/'mcts_execution_contract.json'
    assert not path.exists(),'immutable MCTS execution already started'
    write('TASK-016',str(path.relative_to(root())),json.dumps(frozen,indent=2)+'\n')
    os.environ['FLAVORETRO_TASK016_LEDGER']=str(folder/'run_ledger.jsonl');os.environ['FLAVORETRO_TASK016_TRACE']='1';os.environ['FLAVORETRO_TASK016_PURPOSE']='paired_development'
    observations=[];pairs=[]
    refs=read_jsonl(folder/'reference_precursors.jsonl')
    for cell in requests:
        request=SearchRequest(smiles=cell['target'],seed=cell['seed'],candidate_stock=contract['candidate_stock'],glycoside_expansion=cell['domain_enabled'],**contract['budget'])
        result=search(request,run_root=folder/'paired-runs');manifest=json.loads((folder/'paired-runs'/result['run_id']/'manifest.json').read_text())
        obs={**cell,'result':result,'manifest':manifest};observations.append(obs)
        write('TASK-016',str((folder/'mcts_observations.jsonl').relative_to(root())),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in observations))
        if cell['group']=='B':
            before=observations[-2];a=before['result'];b=result;ref=next(r for r in refs if r['target']==cell['target']);signature=ref['reference_signature'];am=a['status']=='ok' and signature in signatures(a,'mcts_action_created');bm=b['status']=='ok' and signature in signatures(b,'mcts_action_created')
            pair=dict(target=cell['target'],seed=cell['seed'],baseline_run_id=a['run_id'],augmented_run_id=b['run_id'],baseline_status=a['status'],augmented_status=b['status'],baseline_matched_action_created=am,augmented_matched_action_created=bm,gain=a['status']=='ok' and not am and bm,loss=am and not bm,baseline_wall_seconds=before['manifest']['wall_seconds'],augmented_wall_seconds=manifest['wall_seconds'],baseline_nodes=sum(p['node_count'] for p in a.get('phases',[])),augmented_nodes=sum(p['node_count'] for p in b.get('phases',[])),baseline_iterations=sum(p['search_stats'].get('iterations',0) for p in a.get('phases',[])),augmented_iterations=sum(p['search_stats'].get('iterations',0) for p in b.get('phases',[])),new_exact_actions_by_stage={stage:len(signatures(b,stage)-signatures(a,stage)) for stage in ['generated','after_truncation','filtered_accepted','mcts_action_created']},reference_signature=signature,baseline_phases=a.get('phases',[]),augmented_phases=b.get('phases',[]))
            pairs.append(pair);write('TASK-016',str((folder/'paired_results.jsonl').relative_to(root())),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in pairs));print(json.dumps({k:pair[k] for k in ['seed','baseline_status','augmented_status','gain','loss','baseline_nodes','augmented_nodes']})+' target='+cell['target'],flush=True)
    write('TASK-016',str((folder/'metrics.json').relative_to(root())),json.dumps(metrics(folder,pairs),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
