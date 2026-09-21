"""Lossless admission and deterministic local structure checks."""
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
from rdkit import Chem,rdBase
from rdkit.Chem import rdChemReactions
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''): h.update(chunk)
    return h.hexdigest()
def dumps(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
def outcome(token):
    missing=token is None or (isinstance(token,str) and token.strip() in ('','NA','N/A','not reported'))
    value=None
    if not missing and re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*%?',str(token).strip()):
        value=float(str(token).strip().rstrip('%'))
    return dict(raw=token,value=value,is_missing=missing,status='missing' if missing else 'numeric' if value is not None else 'unparsed',unit='percent_reported' if value is not None else None,basis='not_verified',measurement_method='not_verified')
def structure(smiles,expected=None):
    if not smiles: return {'status':'missing','canonical_smiles':None,'inchikey':None}
    try:
        mol=Chem.MolFromSmiles(smiles)
        if mol is None: raise ValueError('RDKit parse failure')
        canonical=Chem.MolToSmiles(mol,isomericSmiles=True); key=Chem.MolToInchiKey(mol)
        return dict(status='parsed',canonical_smiles=canonical,inchikey=key,expected_key_matches=key==expected if expected else None,unspecified_stereo=sum(v=='?' for _,v in Chem.FindMolChiralCenters(mol,includeUnassigned=True)),wildcard=any(a.GetAtomicNum()==0 for a in mol.GetAtoms()))
    except Exception as exc: return dict(status='parse_failure',error=str(exc),canonical_smiles=None,inchikey=None)
def rdf_records(path):
    text=path.read_text(errors='strict')
    for i,block in enumerate(b for b in re.split(r'(?=\$RFMT )',text) if '$RXN' in b):
        fields={m.group(1):m.group(2) for m in re.finditer(r'\$DTYPE (\S+)\n\$DATUM (.*?)(?=\n\$DTYPE |\n\$RFMT |\Z)',block,re.S)}
        record={'fields':fields,'block_sha256':hashlib.sha256(block.encode()).hexdigest()}
        components=[]; issues=[]
        try:
            rxn=rdChemReactions.ReactionFromRxnBlock(block[block.index('$RXN'):],sanitize=False,removeHs=False)
            for role,mols in [('reactant',rxn.GetReactants()),('product',rxn.GetProducts())]:
                for m in mols:
                    try: Chem.SanitizeMol(m)
                    except Exception as exc: issues.append('sanitize:'+str(exc))
                    components.append({'role':role,'structure':structure(Chem.MolToSmiles(m))})
        except Exception as exc: issues.append('rxn_parse:'+str(exc))
        yield i,record,components,issues,outcome(fields.get('RXN:VAR(1):PRO(1):YIELD'))
def build(output):
    output=Path(output)
    if output.exists(): raise ValueError('output exists; immutable version required')
    manifest=json.loads((ROOT/'metadata/sources.json').read_text()); files={x['source_path']:x for x in manifest['files']}
    for x in files.values():
        if sha(ROOT/x['path'])!=x['sha256']: raise ValueError('source hash drift '+x['path'])
    rows=[]
    def add(kind,path,locator,raw,**extra):
        src=files[path]; identity=hashlib.sha256(json.dumps([kind,src['sha256'],locator],ensure_ascii=False).encode()).hexdigest()
        row=dict(id=identity,kind=kind,source_path=src['path'],source_sha256=src['sha256'],locator=locator,raw=raw,review_status='agent_checked_candidate',human_review_status='not_performed',production_eligible=False,decision='retain_candidate',decision_reason='Source and computational checks are not independent chemistry or vendor evidence',**extra)
        rows.append(row); return row
    def read(rel): return json.loads((ROOT/files[rel]['path']).read_text())
    lit='templates/literature_curated/flavonoid_literature_reactions.json'
    for i,r in enumerate(read(lit)['entries']):
        source=r.get('source',{}); name=source.get('file_name')
        relocations=json.loads((ROOT/'metadata/note-relocations.json').read_text())
        matches=[relocations[name]] if name in relocations and relocations[name] in files else []
        token=r.get('raw_reaction_smiles')
        token_found=any(bool(token) and token in (ROOT/files[p]['path']).read_text() for p in matches)
        components=[{'role':role,'structure':structure(m.get('canonical_smiles') or m.get('raw'),m.get('inchikey'))} for role,key in [('reactant','reactants'),('product','products')] for m in r.get(key,[])]
        add('note_reaction',lit,f'/entries/{i}',r,components=components,upstream_sources=[files[p]['path'] for p in matches],upstream_reaction_token_found=token_found,upstream_reported_line=source.get('line'),source_status=('note_located_token_found' if token_found else 'note_located_token_unmatched') if matches else 'note_missing',outcome=outcome(r.get('yield')))
    for rel,x in sorted(files.items()):
        if rel.startswith('import_raw/') and rel.endswith('.rdf'):
            for i,raw,components,issues,value in rdf_records(ROOT/x['path']):
                add('scifinder_reaction',rel,f'RFMT/{i}',raw,components=components,issues=issues,outcome=value,source_status='raw_export_reparsed_not_primary_reviewed')
    library='outputs/publication/2026-09-10/library_v3/molecule_library.csv'
    for i,r in enumerate(csv.DictReader((ROOT/files[library]['path']).open())):
        add('molecule',library,f'row/{i+2}',r,structure=structure(r.get('smiles'),r.get('inchikey')),source_status='historical_database_claim',evaluation_scope=r.get('split_scope'))
    summary='outputs/publication/2026-09-10/library_v3/summary.json'
    for group in ['duplicate_names','failures']:
        for i,r in enumerate(read(summary)[group]): add('molecule_'+group,summary,f'/{group}/{i}',r,structure=structure(r.get('smiles')),source_status='retained_'+group)
    stock='templates/stock_layers/production_stock_registry.json'
    comparison=read('outputs/validation/stock-identity-review-20260912/stock_identity_review.json')
    byid={r['stock_id']:r for r in comparison['records']}
    for i,r in enumerate(read(stock)['records']):
        current=structure(r.get('smiles'),r.get('inchikey')); previous=byid.get(r['stock_id'],{}); reference=previous.get('name_reference') or {}; other=structure(reference.get('isomeric_smiles'))
        conflict=bool(current.get('inchikey') and other.get('inchikey') and current['inchikey'].split('-')[0]!=other['inchikey'].split('-')[0])
        add('stock',stock,f'/records/{i}',r,structure=current,name_reference=reference,name_conflict_recomputed=conflict,source_status='name_conflict' if conflict else 'identity_only_no_current_vendor',runtime_candidate_allowed=current['status']=='parsed' and not conflict and r.get('source_layer')!='virtual_bridge')
    template='templates/production/production_template_registry.json'
    for i,r in enumerate(read(template)['entries']):
        try: parsed=rdChemReactions.ReactionFromSmarts(r['canonical_retro_smarts']) is not None
        except Exception: parsed=False
        add('template',template,f'/entries/{i}',r,parse_success=parsed,source_status='unreviewed_primary_reaction',runtime_enabled=False)
    for rel,key,kind in [('config/product/literature_registry.json','papers','paper'),('outputs/publication/2026-09-10/scifinder_import/supplier_evidence.json','substances','supplier')]:
        for i,r in enumerate(read(rel)[key]):
            upstream=[x for x in files.values() if x['sha256']==r.get('source_sha256')]
            add(kind,rel,f'/{key}/{i}',r,source_status='historical_listing_not_current_supply' if kind=='supplier' else 'bibliographic_candidate',upstream_sources=[x['path'] for x in upstream])
    assert len({r['id'] for r in rows})==len(rows)
    counts=dict(Counter(r['kind'] for r in rows)); assert counts['note_reaction']==508 and counts['scifinder_reaction']==2301 and counts['stock']==49 and counts['molecule']==156
    output.mkdir(parents=True)
    (output/'records.json').write_text(dumps(rows)); (output/'manifest.json').write_text(dumps({'schema_version':1,'counts':counts,'sources_sha256':sha(ROOT/'metadata/sources.json'),'records_sha256':sha(output/'records.json'),'code_sha256':sha(__file__),'rdkit':rdBase.rdkitVersion,'production_records':0,'name_conflicts':sum(r.get('name_conflict_recomputed',False) for r in rows),'yield_zero':sum(r.get('outcome',{}).get('value')==0 for r in rows),'yield_missing':sum(r.get('outcome',{}).get('is_missing',False) for r in rows)}))
    for p in output.iterdir(): p.chmod(0o444)
    return json.loads((output/'manifest.json').read_text())
if __name__=='__main__':
    import sys
    print(dumps(build(sys.argv[1])))
