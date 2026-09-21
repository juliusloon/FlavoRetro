"""New, bounded development comparisons; never historical acceptance replay."""
import argparse,json,uuid
from datetime import datetime,timezone
from .contracts import SearchRequest
from .service import search
from .resources import ROOT,dumps,sha
from .policies import records

def preflight():
    return {'formal_run_ready':False,'release_ready':False,'reasons':['No independently source-reviewed production template and stock projection','No independent chemical labels or preregistered panel','Development comparisons are not formal blind evaluation']}
def compare():
    rows=records();targets=[r for r in rows if r['kind']=='molecule' and r['raw']['query_name'].lower() in ('hesperidin','hesperetin','quercetin')]
    assert len(targets)==3
    folder=ROOT/'outputs/evaluation'/('development-'+uuid.uuid4().hex);folder.mkdir(parents=True,exist_ok=False)
    contract={'scope':'development_engine_comparison_not_blind','targets':[r['id'] for r in targets],'seeds':[0,1],'engines':['native','optimized'],'candidate_stock':True,'seconds':2.0,'iterations':10,'depth':4,'same_node_ceiling':False,'resource_sha256':sha(ROOT/'data/derived/v1/records.json'),'config_sha256':sha(ROOT/'configs/search.json')}
    (folder/'contract.json').write_text(dumps(contract));cells=[]
    for r in targets:
        for seed in contract['seeds']:
            for engine in contract['engines']:
                result=search(SearchRequest(smiles=r['raw']['smiles'],mode='quick',seed=seed,engine=engine,candidate_stock=True,seconds=2.0,iterations=10))
                cell={'target':r['raw']['query_name'],'seed':seed,'engine':engine,'run_id':result['run_id'],'status':result['status'],'routes':len(result['routes']),'evidence_closed':sum(x['evidence_closed'] for x in result['routes']),'native_solved':sum(x['native_solved'] for x in result['routes']),'search_seconds':sum(x['search_seconds'] for x in result.get('phases',[]))}
                cells.append(cell);(folder/(r['id']+'-'+str(seed)+'-'+engine+'.json')).write_text(dumps(cell))
    report={'contract_sha256':sha(folder/'contract.json'),'expected_cells':12,'completed_cells':len(cells),'failures':sum(x['status']!='ok' for x in cells),'cells':cells,'claim':'Engineering development observation only; no chemical superiority conclusion'}
    (folder/'summary.json').write_text(dumps(report))
    for p in folder.iterdir():p.chmod(0o444)
    return str(folder),report
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--development',action='store_true');args=parser.parse_args()
    if args.development:
        folder,result=compare();print(dumps({'folder':folder,**result}))
    else:print(dumps(preflight()))
