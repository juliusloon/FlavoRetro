"""Frozen engineering comparison and complete source-axis audit."""
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from unittest.mock import patch
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.reviewed_resources import load_review, row_signature
from flavoretro.resources import sha,dumps
from flavoretro.workspace import root

plan=json.loads((root()/'outputs/validation/task015-06-plan.json').read_text())
view=load_review()
rows=json.loads((root()/'data/derived/v3/records.json').read_text())
refs=[]
for row in rows:
    record=view.record(row['id'])
    if record.get('positive_source_support'):
        sig=row_signature(row); left,right=sig.split('>>')
        result=view.reaction(left.split('.'),right.split('.'))
        assert result['source_instance_supported'] and not result['actionable']
        refs.append({'record_id':row['id'],'card_number':record['card_number'],'strict_query_support':True,'yield':record.get('source_instance_yield')})
assert len(refs)==9
cells=[]
for target in plan['targets']:
    for seed in plan['seeds']:
        for mode in plan['views']:
            with patch.dict(os.environ,FLAVORETRO_REVIEW_VALIDATION_LEGACY='1' if mode=='legacy_validation' else '0'):
                result=search(SearchRequest(smiles=target['smiles'],seed=seed,**plan['request_budget']))
            cells.append({'target':target['name'],'seed':seed,'view':mode,'run_id':result['run_id'],'status':result['status'],
                'binding':result.get('review_binding',result.get('review_expected')),
                'routes':[{k:r[k] for k in ['route_id','score','steps','closure','evidence_closed','actionable']} for r in result['routes']]})
            (root()/'outputs/validation/task015-06-cells.json').write_text(dumps(cells))
comparisons=[]
for target in plan['targets']:
    for seed in plan['seeds']:
        pair=[c for c in cells if c['target']==target['name'] and c['seed']==seed]
        comparisons.append({'target':target['name'],'seed':seed,'both_ok':all(c['status']=='ok' for c in pair),'stable_route_fields_equal':pair[0]['routes']==pair[1]['routes']})
native=search(SearchRequest(smiles=plan['targets'][0]['smiles'],seed=0,engine='native',**plan['request_budget']))
source_matches=0
for cell in cells:
    if cell['view']!='adjudicated' or cell['status']!='ok':continue
    r=json.loads((root()/'outputs/runs'/cell['run_id']/'result.json').read_text())
    def count(node):
        return int(bool(node.get('review',{}).get('source_instance_supported')))+sum(count(c) for c in node.get('children',[]))
    source_matches+=sum(count(route['tree']) for route in r['routes'])
report={'review_binding':view.binding,'reference_queries':refs,'cells':cells,'comparisons':comparisons,
    'native':{'run_id':native['run_id'],'status':native['status'],'binding':native.get('review_binding'),'routes':len(native['routes'])},
    'strict_source_supported_route_step_occurrences':source_matches,'comparison_failure_count':sum(c['status']!='ok' for c in cells),
    'scope':'Reference-index queries and real MCTS are separate engineering evidence; no chemical accuracy claim'}
(root()/'outputs/validation/task015-06-runtime.json').write_text(dumps(report))
print(dumps({'comparison_runs':len(cells),'failures':report['comparison_failure_count'],'comparison_checks':comparisons,'native_status':native['status'],'strict_source_supported_route_step_occurrences':source_matches}))
assert all(c['both_ok'] and c['stable_route_fields_equal'] for c in comparisons)
assert native['status']=='ok' and native['review_binding']['mode']=='adjudicated'
