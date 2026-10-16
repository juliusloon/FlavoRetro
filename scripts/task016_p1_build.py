"""Build executable exact/scope v2 templates using only the frozen runtime view."""
import hashlib,json,re
from collections import Counter
from rdkit import Chem,rdBase,RDLogger
from scripts.task016_p1_sources import ROOT,OUT,save,rows
from flavoretro.glycoside_expansion import extract_template
from flavoretro.glycoside_library import apply_template,FLAVONE
from flavoretro.reviewed_resources import canonical_side,load_review
from flavoretro.open_glycoside_library import structural_formation
from flavoretro.resources import sha
RDLogger.DisableLog('rdApp.warning')

def subset(mol,keep):
    rw=Chem.RWMol(mol)
    for i in reversed(range(rw.GetNumAtoms())):
        if i not in keep:rw.RemoveAtom(i)
    return Chem.MolToSmiles(rw.GetMol(),isomericSmiles=True)

def scoped_smarts(t,r,center_class):
    left,right=t['smarts'].split('>>');product=Chem.MolFromSmiles(left);acceptor_smiles,donor=right.split('.',1);acceptor=Chem.MolFromSmiles(acceptor_smiles)
    formation=structural_formation(r['acceptor'],r['donor'],r['target']);idx=formation['product_atom_indices'];kept=set(idx['added'])|{idx['acceptor_site']}
    site=product.GetAtomWithIdx(idx['acceptor_site']);owner=next(a for a in site.GetNeighbors() if a.GetIdx()!=idx['anomeric']);kept.add(owner.GetIdx())
    if center_class=='glucoside_O2':
        ring=next(ring for ring in product.GetRingInfo().AtomRings() if owner.GetIdx() in ring and len(ring)==6 and sum(product.GetAtomWithIdx(i).GetAtomicNum()==8 for i in ring)==1)
        kept.update(ring)
        for i in ring:
            for n in product.GetAtomWithIdx(i).GetNeighbors():
                if n.GetIdx() not in idx['added']:
                    kept.add(n.GetIdx())
                    if n.GetAtomicNum()==6 and not n.GetIsAromatic():kept.update(x.GetIdx() for x in n.GetNeighbors() if x.GetAtomicNum()==8)
                    if n.GetAtomicNum()==8:
                        kept.update(x.GetIdx() for x in n.GetNeighbors() if x.GetIsAromatic())
    maps={product.GetAtomWithIdx(i).GetAtomMapNum() for i in kept if i not in idx['added']}
    return subset(product,kept)+'>>'+subset(acceptor,{a.GetIdx() for a in acceptor.GetAtoms() if a.GetAtomMapNum() in maps})+'.'+donor

def is_O3(r):
    mol=Chem.MolFromSmiles(r['target']);f=structural_formation(r['acceptor'],r['donor'],r['target'])['product_atom_indices'];site=mol.GetAtomWithIdx(f['acceptor_site']);owner=next(a for a in site.GetNeighbors() if a.GetIdx()!=f['anomeric'])
    return any(owner.GetIdx()==m[2] for m in mol.GetSubstructMatches(Chem.MolFromSmarts(FLAVONE),uniquify=False))

def build():
    assert not (OUT/'template_source_manifest.json').exists(),'runtime template manifest already frozen'
    split=json.loads((OUT/'development_split_manifest.json').read_text());assert sha(OUT/'runtime_instances.jsonl')==split['files_sha256']['runtime_instances.jsonl']
    instances=rows(OUT/'runtime_instances.jsonl');templates=[];support_groups={}
    for r in instances:support_groups.setdefault(r['covalent_signature'],[]).append(r)
    for sig,rr in sorted(support_groups.items()):
        r=rr[0];t=extract_template(r)
        t.update(template_id='p1-exact:'+hashlib.sha256(t['smarts'].encode()).hexdigest()[:20],template_role='exact_instance_template',support_instances=sorted(x['instance_id'] for x in rr),allowed_targets=[r['target']],required_context=dict(mode='enzymatic',donor_name=r['required_context']['donor_name']),donor=r['donor'],category=r['category'],sugar_type=r['sugar_type'],validation_status='pending')
        templates.append(t)
    exact=list(templates)
    scopes=[('glucose','phenolic_aryl_O','O_formation'),('glucose','flavonol_O3','O_formation'),('galactose','flavonol_O3','O_formation'),('rhamnose','flavonol_O3','O_formation'),('apiose','glucoside_O2','sugar_sugar_formation')]
    allcores=[FLAVONE,'O=C1CC(c2ccccc2)Oc2ccccc21','O=c1c(-c2ccccc2)coc2ccccc12','O=C(C=Cc1ccccc1)c1ccccc1','O=C(CCc1ccccc1)c1ccccc1']
    for sugar,center,category in scopes:
        eligible=[r for r in instances if r['sugar_type']==sugar and r['category']==category]
        if center!='glucoside_O2':eligible=[r for r in eligible if Chem.MolFromSmiles(r['target']).HasSubstructMatch(Chem.MolFromSmarts(FLAVONE)) and (is_O3(r)==(center=='flavonol_O3'))]
        if center=='glucoside_O2':eligible=sorted(eligible,key=lambda r:(r['annotation_case']['acceptor_name']!='apigenin 7-O-beta-D-glucoside',r['instance_id']))
        seed=eligible[0];base=next(t for t in exact if seed['instance_id'] in t['support_instances']);smarts=scoped_smarts(base,seed,center)
        t=dict(template_id='p1-scope:'+hashlib.sha256((smarts+center).encode()).hexdigest()[:20],template_role='scope_template',smarts=smarts,allowed_targets=[],required_context=dict(mode='enzymatic',donor_name=seed['required_context']['donor_name']),donor=seed['donor'],category=category,sugar_type=sugar,scope=dict(center_class=center,acceptor_cores=allcores if center=='glucoside_O2' else [FLAVONE],decoration_classes=['hydroxy','methoxy'] if center!='glucoside_O2' else ['existing source-parent glycosides retained'],interpretation='local source-supported bond/UDP-glycan transfer candidate; activity/site selectivity/enzyme/conditions unverified for novel exact products',enzyme_context='plant UDP-dependent glycosyltransferase candidate; no seed gene copied'),support_instances=[],validation_status='pending')
        for r in eligible:
            if canonical_side(r['reference_precursors']) in [o['precursors'] for o in apply_template(t,r['target'])]:t['support_instances'].append(r['instance_id'])
        t['support_instances']=sorted(t['support_instances']);distinct={r['acceptor'] for r in instances if r['instance_id'] in t['support_instances']}
        if len(distinct)<2:raise ValueError('insufficient multi-acceptor support '+str((sugar,center,len(distinct))))
        templates.append(t)
    validations=[]
    for t in templates:
        checks=[]
        for identifier in t['support_instances']:
            r=next(r for r in instances if r['instance_id']==identifier);out=apply_template(t,r['target']);checks.append(dict(kind='support_replay',instance_id=identifier,passed=canonical_side(r['reference_precursors']) in [o['precursors'] for o in out],outcome_indices=[o['outcome_index'] for o in out]))
        r=next(r for r in instances if r['instance_id']==t['support_instances'][0])
        for context in [dict(mode='chemical',donor_name=t['required_context']['donor_name']),dict(mode='enzymatic',donor_name='wrong UDP donor')]:checks.append(dict(kind='wrong_context_or_donor',context=context,passed=not apply_template(t,r['target'],context)))
        mol=Chem.MolFromSmiles(r['target']);center=structural_formation(r['acceptor'],r['donor'],r['target'])['product_atom_indices'];mol.GetAtomWithIdx(center['anomeric']).InvertChirality();wrong=Chem.MolToSmiles(mol,isomericSmiles=True)
        checks.append(dict(kind='wrong_anomeric_stereo',target=wrong,passed=not apply_template(t,wrong)))
        if t['template_role']=='scope_template':checks.append(dict(kind='outside_flavonoid_core',target='CO',passed=not apply_template(t,'CO')))
        # Source-derived phenolate representation control; no salt stripping/tautomer changes.
        mol=Chem.MolFromSmiles(r['target']);phenols=[a for a in mol.GetAtoms() if a.GetAtomicNum()==8 and a.GetDegree()==1 and a.GetFormalCharge()==0 and a.GetTotalNumHs()==1 and a.GetBonds()[0].GetBondType()==Chem.BondType.SINGLE and a.GetNeighbors()[0].GetIsAromatic()]
        if phenols:
            atom=phenols[0];atom.SetFormalCharge(-1);atom.SetNumExplicitHs(0);atom.SetNoImplicit(True);ionic=Chem.MolToSmiles(mol,isomericSmiles=True)
            checks.append(dict(kind='acid_representation_equivalence',ionic_target=ionic,original_strict_differs=canonical_side([ionic])!=canonical_side([r['target']]),passed=canonical_side(r['reference_precursors']) in [o['precursors'] for o in apply_template(t,ionic)]))
        passed=all(c['passed'] for c in checks);validations.append(dict(template_id=t['template_id'],role=t['template_role'],checks=checks,passed=passed))
        t['validation_status']='source_reconstruction_passed' if passed else 'blocked_validation_failed'
    save('template_validation.jsonl',validations,True)
    if not all(v['passed'] for v in validations):
        print('VALIDATION_FAILURES',[(v['template_id'],[c['kind'] for c in v['checks'] if not c['passed']]) for v in validations if not v['passed']]);return
    save('templates.jsonl',templates,True)
    save('applicability_contract.json',dict(schema_version=1,build_only=True,split_sha256=sha(OUT/'development_split_manifest.json'),local_scope_transfer=True,holdout_whitelists=False,scope_support=[dict(template_id=t['template_id'],support_instances=t['support_instances'],distinct_acceptors=len({r['acceptor'] for r in instances if r['instance_id'] in t['support_instances']}),scope=t['scope']) for t in templates if t['template_role']=='scope_template'],unverified=['novel exact product enzymatic activity','specific gene','conditions','yield','chemical feasibility','training overlap']))
    save('representation_rules.json',dict(version='acid-oxygen-protonation-v1',allowed='only singly bound negative acid O attached to P, aromatic C or carboxyl C -> neutral OH',preserved=['all covalent bonds','stereo','isotopes','other charge','salts/components','multiplicity'],predominant_species_inferred=False))
    save('template_groups.jsonl',[dict(transform_group=sugar+':'+category+':'+role,templates=[t['template_id'] for t in templates if (t['sugar_type'],t['category'],t['template_role'])==(sugar,category,role)]) for sugar,category,role in sorted({(t['sugar_type'],t['category'],t['template_role']) for t in templates})],True)
    fusion=dict(version='v2-protected-generic-fusion-v1',default_enabled=False,domain_cap_per_molecule=4,prior=0.2,weight=1.0,generic_protection=3,fixed_branch_cap=12,rank='same weighted prior + deterministic key as optimized A; retain first min(3,A distinct accepted outcomes) before v2 fusion; domain proposals ranked at prior0.2; all extra outcomes and alternatives governed by fixed cap',scope='entire v2 method, not isolated template ablation')
    save('fusion_contract.json',fusion);save('review_binding.json',load_review().binding)
    dependencies={}
    for r in instances:
        ref=r['provenance'];p=ref.get('raw_path',ref.get('source_ref',{}).get('path'))
        if p and (ROOT/p).is_file():dependencies[p]=sha(ROOT/p)
    policy={k:fusion[k] for k in ['default_enabled','domain_cap_per_molecule','prior','weight','generic_protection']}
    manifest=dict(schema_version=2,version='task016-p1-open-v2',rdkit=rdBase.rdkitVersion,review_binding=load_review().binding,policy=policy,files_sha256={n:sha(OUT/n) for n in ['templates.jsonl','runtime_instances.jsonl','template_validation.jsonl','applicability_contract.json','representation_rules.json','fusion_contract.json']},raw_dependencies_sha256=dependencies,claim='agent source annotation and structural reconstruction; candidate transfer, not independent chemistry validation')
    save('template_source_manifest.json',manifest)
    config=dict(version=2,default_enabled=False,manifest='outputs/task016-p1/v1/template_source_manifest.json',manifest_sha256=sha(OUT/'template_source_manifest.json'),status='development_candidate_scope_not_production')
    from scripts.operate import write
    for path in ['configs/glycoside-library-v2.json','flavoretro/assets/configs/glycoside-library-v2.json']:write('TASK-016-P1',path,json.dumps(config,indent=2)+'\n')
    print('validated templates',len(templates),'exact',len(exact),'scopes',len(scopes),'support checks',sum(c['kind']=='support_replay' for v in validations for c in v['checks']))
if __name__=='__main__':build()
