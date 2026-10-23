"""Self-contained literature handoff from an integrity-checked, actual MCTS run."""
import hashlib
import json
from .resources import sha
from .workspace import root

SCHEMA = 'flavoretro.lab-handoff.v1'

def digest_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()).hexdigest()

def root_evidence(tree):
    children = tree.get('children', [])
    if tree.get('type') != 'mol' or len(children) != 1 or children[0].get('type') != 'reaction':
        return None
    reaction=children[0]
    evidence=reaction.get('metadata', {}).get('task022_evidence', {})
    return (evidence, [c['smiles'] for c in reaction.get('children', []) if c.get('type')=='mol'])

def packet(envelope, route_id, source_id):
    result=envelope['result']
    if envelope.get('integrity') != 'verified' or result.get('execution_source') != 'live_aizynthfinder_mcts':
        raise ValueError('handoff_requires_verified_live_mcts')
    route=next((r for r in result['routes'] if r['route_id']==route_id), None)
    if route is None:
        raise ValueError('unknown_route')
    found=None
    for tree in [route['tree']]+[v['tree'] for v in route.get('source_variants', [])]:
        item=root_evidence(tree)
        if item and item[0].get('lab_case',{}).get('source_id') == source_id:
            found=(tree,*item);break
    if not found:
        raise ValueError('no_generated_source_witness_for_case')
    tree, evidence, precursors=found
    from rdkit import Chem
    molecule=Chem.MolFromSmiles(tree['smiles'])
    source=evidence['source']
    selection={**evidence['lab_case'],'source_reaction_id':evidence['source_reaction_id'], 'doi':source['doi'],'source_sha256':source['sha256']}
    literature={selection['source_id']:{**selection,'mcts_action':True}}
    # Contexts have a separate role and never become executable reactions here.
    for context in result.get('development_contexts', []):
        s=context['source']; c=context['lab_case']
        literature[c['source_id']]={**c,'doi':s['doi'],'source_sha256':s['sha256'],'mcts_action':False}
    # Only other actually generated source witnesses are transferred as routes.
    for candidate in result['routes']:
        for actual in [candidate['tree']]+[v['tree'] for v in candidate.get('source_variants', [])]:
            item=root_evidence(actual)
            if not item or not item[0].get('lab_case'): continue
            e=item[0];s=e['source'];c=e['lab_case']
            literature[c['source_id']]={**c,'source_reaction_id':e['source_reaction_id'],'doi':s['doi'],'source_sha256':s['sha256'],'mcts_action':True}
    run_folder=root()/'outputs/runs'/result['run_id']
    value=dict(schema=SCHEMA,
      run=dict(id=result['run_id'], execution_source=result['execution_source'], result_sha256=envelope['manifest']['files']['result.json'], manifest_sha256=sha(run_folder/'manifest.json')),
      route=dict(id=route_id, tree_sha256=digest_json(tree), steps=route['steps'], closure=route['closure']),
      target=dict(smiles=Chem.MolToSmiles(molecule,isomericSmiles=True), inchikey=Chem.MolToInchiKey(molecule)),
      selection=selection, witness=dict(product_smiles=tree['smiles'],precursor_smiles=sorted(precursors)),
      literature=sorted(literature.values(),key=lambda r:r['route_id']),
      observations=[],quantitative_result=None,teacher_approved=False,independent_chemical_validation=False)
    value['packet_sha256']=digest_json(value)
    return value
