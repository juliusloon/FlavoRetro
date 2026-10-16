"""Configuration-driven source assay admission without template/model access."""
import hashlib,json,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
from rdkit import Chem,RDLogger
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p1_sources import ROOT,OUT,save,rows
from scripts.task016_p1_encode import named_flavone,position_oxygen,glycan_stub,attach_stub,glucoside_2_oxygen,convert_C_glucose
from flavoretro.open_glycoside_library import normalize_species,structural_formation,covalent_signature
from flavoretro.reviewed_resources import canonical_side,reaction_signature
RDLogger.DisableLog('rdApp.warning')
CM_PATH=ROOT/'data/raw/task016-p1/2026-10-06/enzymemap/compound_to_smiles.json/bulk-file.attempt-1'
CM=json.loads(CM_PATH.read_text());RHEA=rows(OUT/'rhea_knowledge_records.jsonl')
INDEX={};PAIRS=[]
for r in RHEA:
    if r['parse_status']!='parsed':continue
    eq=r['raw']['Equation'];left,right=eq.split(' = ')
    if 'UDP-' not in left or 'UDP' not in right:continue
    a=[s for s in r['reactants'] if 'P' not in s and Chem.MolFromSmiles(s).GetNumAtoms()>10]
    d=[s for s in r['reactants'] if 'P' in s]
    p=[s for s in r['products'] if 'P' not in s and Chem.MolFromSmiles(s).GetNumAtoms()>10]
    if len(a)!=1 or len(d)!=1 or len(p)!=1:continue
    an=[n for n in left.split(' + ') if not n.startswith('UDP-') and n not in ['H(+)','H2O']]
    pn=[n for n in right.split(' + ') if n not in ['UDP','H(+)','H2O']]
    if len(an)!=1 or len(pn)!=1:continue
    source=dict(provider='Rhea',record_id=r['record_id'],query_snapshot=r['query_snapshot'],bulk_path='data/raw/task016/discovery/2026-10-06/rhea_smiles',role='compound identity / encoded species; not assay confirmation')
    for name,s in [(an[0],a[0]),(pn[0],p[0]),(next(n for n in left.split(' + ') if n.startswith('UDP-')),d[0])]:INDEX.setdefault(name.lower(),[]).append((s,source))
    PAIRS.append(dict(acceptor_name=an[0],target_name=pn[0],acceptor=a[0],donor=d[0],target=p[0],source=source))
for file in ['identity_manifest.json','identity_additional_manifest.json','identity_epimedium_manifest.json']:
    for r in json.loads((OUT/file).read_text()):
        if r['status']!='raw_available':continue
        for value in json.loads((ROOT/r['path']).read_text()).get('PropertyTable',{}).get('Properties',[]):
            INDEX.setdefault(r['compound_name'].lower(),[]).append((value.get('SMILES',value.get('IsomericSMILES')),dict(provider='PubChem',cid=value['CID'],raw_path=r['path'],raw_sha256=r['sha256'],role='database identity; not assay evidence')))
def resolve(name):
    options=INDEX.get(name.lower(),[])
    if not options:
        options=[(s,dict(provider='EnzymeMap compound identity',raw_path=str(CM_PATH.relative_to(ROOT)),raw_sha256=hashlib.sha256(CM_PATH.read_bytes()).hexdigest(),name=name,role='machine-resolved database compound; not assay evidence')) for s in CM.get(name,[])]
    normalized={normalize_species(s)['normalized']:(s,p) for s,p in options}
    if len(normalized)!=1:raise ValueError('compound identity unresolved or conflicting: '+name+'; candidates='+str(len(normalized)))
    result=next(iter(normalized.items()));return result[0],dict(**result[1][1],original_smiles=result[1][0],representation=normalize_species(result[1][0]))
DONOR_NAMES=dict(glucose='UDP-alpha-D-glucose',galactose='UDP-alpha-D-galactose',rhamnose='UDP-beta-L-rhamnose',glucuronate='UDP-alpha-D-glucuronate',xylose='UDP-alpha-D-xylose',apiose='UDP-alpha-D-apiose')
DONORS={s:resolve(n) for s,n in DONOR_NAMES.items()}
q3=next(p for p in PAIRS if p['target_name']=='quercetin 3-O-beta-D-glucoside')
GLC_STUB=glycan_stub(normalize_species(q3['acceptor'])['normalized'],DONORS['glucose'][0],normalize_species(q3['target'])['normalized'])
api=next(p for p in PAIRS if p['target_name'].startswith('7-O-(beta-D-apio'))
API_STUB=glycan_stub(normalize_species(api['acceptor'])['normalized'],DONORS['apiose'][0],resolve('apiin')[0])
phloretin,phlor_authority=resolve('phloretin');nothofagin,noth_authority=resolve('nothofagin')
C_STUB=glycan_stub(phloretin,DONORS['glucose'][0],nothofagin)
assert attach_stub(phloretin,C_STUB,structural_formation(phloretin,DONORS['glucose'][0],nothofagin)['product_atom_indices']['acceptor_site'])==nothofagin
# A same-chemistry encoding check verifies the beta-apiose fragment, never a held-out template.
assert attach_stub(normalize_species(api['acceptor'])['normalized'],API_STUB,glucoside_2_oxygen(normalize_species(api['acceptor'])['normalized']))==resolve('apiin')[0]
MANIFEST=json.loads((OUT/'article_acquisition_manifest.json').read_text())
if (OUT/'article_acquisition_addendum.json').exists():MANIFEST+=json.loads((OUT/'article_acquisition_addendum.json').read_text())
PAPERS={r['pmcid']:r for r in MANIFEST if r['status']=='fulltext_available'}
def evidence(case):
    r=PAPERS[case['pmcid']];root=ET.parse(ROOT/r['xml']['path']).getroot();ps=root.findall('.//body//p');loc=[]
    for anchor in case['locators']:
        n=int(re.search(r'\[(\d+)\]',anchor).group(1));t=' '.join(''.join(ps[n-1].itertext()).split())
        loc.append(dict(locator=anchor,text_sha256=hashlib.sha256(t.encode()).hexdigest()))
    doi=root.find(".//article-id[@pub-id-type='doi']")
    return dict(pmcid=case['pmcid'],doi=doi.text if doi is not None else None,raw_path=r['xml']['path'],raw_sha256=r['xml']['sha256'],license=r['license'],locators=loc,source_quality=case['source_quality'],identification=case.get('identification',case.get('source_assignment')),article_version=r.get('article_version'))
def materialize(case):
    donor,dp=DONORS[case['sugar']];mode=case['structure_mode'];a=None;p=None;auth=[]
    if mode=='rhea_name':
        aliases={'quercetin 3-O-beta-D-galactoside':'hyperoside','pelargonidin 3-O-beta-D-galactoside':'pelargonidin 3-O-beta-D-galactoside betaine'}
        name=aliases.get(case['target_name'],case['target_name']);matches=[r for r in PAIRS if r['acceptor_name']==case['acceptor_name'] and r['target_name']==name]
        if not matches:
            a,ap=resolve(case['acceptor_name']);p,pp=resolve(case['target_name']);auth+=[ap,pp]
        else:
            r=matches[0];a=normalize_species(r['acceptor'])['normalized'];p=normalize_species(r['target'])['normalized'];auth.append(r['source'])
    elif mode in ['position_encoding','names']:
        a,ap=resolve(case['acceptor_name']);auth.append(ap)
        if mode=='names':p,pp=resolve(case['target_name']);auth.append(pp)
        else:p=attach_stub(a,GLC_STUB,position_oxygen(a,case['position']));auth.append(dict(provider='agent source identity encoding',position=case['position'],glycan_fragment_source=q3['source'],role='source named compound, machine encoded; no invented assay'))
    elif mode=='named_flavone_sugar_2_encoding':
        a=named_flavone(case['hydroxyls'],case.get('methoxys',[]));a=attach_stub(a,GLC_STUB,position_oxygen(a,case['base_position']))
        p=attach_stub(a,API_STUB,glucoside_2_oxygen(a));auth.append(dict(provider='agent fully named source compound encoding',source='PMC10589286 Fig3 compound12, CAS20633-86-7',hydroxyl_positions=case['hydroxyls'],base_glucosyl_position=case['base_position'],apiosyl_position=2))
    elif mode=='sugar_2_encoding':
        a,ap=resolve(case['acceptor_name']);auth.append(ap)
        p=attach_stub(a,API_STUB if case['sugar']=='apiose' else GLC_STUB,glucoside_2_oxygen(a));auth.append(dict(provider='agent source identity encoding',position='acceptor glucoside O2',glycan_fragment_source=api['source'] if case['sugar']=='apiose' else q3['source']))
    elif mode in ['named_flavone_encoding','second_step_encoding']:
        a=named_flavone(case['hydroxyls'],case['methoxys'])
        if mode=='second_step_encoding':a=attach_stub(a,GLC_STUB,position_oxygen(a,102))
        p=attach_stub(a,GLC_STUB,position_oxygen(a,case['position']));auth.append(dict(provider='agent source identity encoding',source_figure='PMC11365401/gr1',hydroxyl_positions=case['hydroxyls'],methoxy_positions=case['methoxys'],glycosyl_position=case['position'],NMR_status=case['identification']))
    elif mode=='C_sugar_encoding':
        a=phloretin;p=nothofagin if case['sugar']=='glucose' else convert_C_glucose(nothofagin,case['sugar']);auth+=[phlor_authority,noth_authority,dict(provider='agent source NMR name encoding',sugar=case['sugar'],transformation='explicit beta-D glycan change on source phloretin 3-prime C-glycoside')]
    elif mode=='C_second_encoding':
        a=convert_C_glucose(nothofagin,case['first_sugar']);mol=Chem.MolFromSmiles(a)
        # Source phloroglucinol ring is symmetric before the first substitution.
        q=Chem.MolFromSmarts('[cH]1[c]([O;H1])[c]([C](=O))[c]([O;H1])[c]([C;R])[c]1[O;H1]')
        matches=mol.GetSubstructMatches(q)
        if len(matches)!=1:raise ValueError('second C site not uniquely identified')
        p=attach_stub(a,C_STUB,matches[0][0]);auth+=[phlor_authority,noth_authority,dict(provider='agent source NMR name encoding',position='opposite unsubstituted C3prime/C5prime on source symmetric phloroglucinol ring',first_sugar=case['first_sugar'])]
    else:raise ValueError('unknown encoding mode')
    a,p=canonical_side([a]),canonical_side([p])
    center=structural_formation(a,donor,p)
    prov=evidence(case)
    key=hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()[:20]
    return dict(instance_id=case['pmcid']+':'+case['enzyme']+':'+key,record_type='specific_forward_assay_source_annotation',review_type='agent_delegated',human_reviewed=False,independent_chemical_validation=False,development_exposed=True,template_role='unassigned_before_split',source_quality=case['source_quality'],original_reference=prov,provenance=prov,actual_assay_group=case['pmcid']+':'+case['enzyme']+':'+case['acceptor_name']+':'+case['sugar'],physical_replicates=None,acceptor=a,donor=donor,target=p,reference_precursors=sorted([a,donor]),reference_signature=reaction_signature([a,donor],[p]),covalent_signature=covalent_signature(a,donor,p),original_structures=auth,normalization=dict(version='acid-oxygen-protonation-v1',donor=dp),formation=center,category=center['family'],position=case.get('position'),sugar_type=case['sugar'],catalyst_mode='enzymatic',required_context=dict(mode='enzymatic',enzyme=case['enzyme'],donor_name=DONOR_NAMES[case['sugar']],donor_delivery=case.get('donor_delivery','source UDP donor assay')),source_yield=dict(value=None,status='not numerically extracted; activity/kinetics not yield; source numeric values retained separately'),source_conditions=dict(status='source context retained in raw article, not normalized product-specific condition assertions'),prediction_conditions_verified=False,actionable=False,annotation_case=case,inherited=False)
if __name__=='__main__':
    assert not (OUT/'development_split_manifest.json').exists(),'frozen split: use a new version to change inputs'
    contract=json.loads((OUT/'assay_annotations.json').read_text());instances=[];dispositions=[]
    for n,case in enumerate(contract['cases']):
        try:
            row=materialize(case);instances.append(row);d=dict(case_number=n,pmcid=case['pmcid'],enzyme=case['enzyme'],target_name=case['target_name'],disposition='admitted',instance_id=row['instance_id'])
        except Exception as e:d=dict(case_number=n,pmcid=case['pmcid'],enzyme=case['enzyme'],target_name=case['target_name'],disposition='retained_unresolved',error=type(e).__name__+': '+str(e))
        dispositions.append(d)
    for old in rows(ROOT/'outputs/task016/v1/instances.jsonl'):
        a,d,p=[normalize_species(old[k])['normalized'] for k in ['acceptor','donor','target']]
        instances.append(dict(**{k:v for k,v in old.items() if k not in ['acceptor','donor','target','reference_signature','reference_precursors','category','required_context']},acceptor=a,donor=d,target=p,reference_precursors=sorted([a,d]),reference_signature=reaction_signature([a,d],[p]),covalent_signature=covalent_signature(a,d,p),original_reference=old['provenance'],original_structures=[dict(original_smiles=old[k],representation=normalize_species(old[k])) for k in ['acceptor','donor','target']],formation=structural_formation(a,d,p),category='O_formation',required_context=dict(mode='enzymatic',enzyme=old['required_context']['enzyme'],donor_name='UDP-alpha-D-glucose'),sugar_type='glucose',actual_assay_group=old['instance_id'],template_role='development_build',inherited=True))
    save('provisional_instances.jsonl',sorted(instances,key=lambda x:x['instance_id']),True);save('assay_record_dispositions.jsonl',dispositions,True)
    print('case_denominator',len(dispositions),'admitted',len(instances)-4,'unresolved',sum(x['disposition']!='admitted' for x in dispositions),'unique_covalent_groups',len({x['covalent_signature'] for x in instances}))
    for d in dispositions:
        if d['disposition']!='admitted':print(d['pmcid'],d['target_name'],d['error'])
