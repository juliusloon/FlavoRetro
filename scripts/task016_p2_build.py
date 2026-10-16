"""Frozen build-only v3 scopes; inherited templates and source checks retained."""
import sys,json,hashlib,copy,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rdkit import Chem,rdBase
from scripts.task016_p2_sources import ROOT
from scripts.operate import write,event
from scripts.task016_p1_build import subset,scoped_smarts
from scripts.task016_p1_encode import glycan_stub
from flavoretro.glycoside_expansion import extract_template
from flavoretro.glycoside_library import apply_template,FLAVONE
from flavoretro.open_glycoside_library import structural_formation
from flavoretro.reviewed_resources import canonical_side,load_review
from flavoretro.resources import sha
OUT=ROOT/'outputs/task016-p2/v2';T='TASK-016-P2';NO_CONFIG=False
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def save(n,v,jl=False):write(T,str((OUT/n).relative_to(ROOT)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in v) if jl else json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def sugar_epimer_query(smarts,r):
    left,right=smarts.split('>>');mol=Chem.MolFromSmiles(left)
    f=structural_formation(r['acceptor'],r['donor'],r['target']);full=Chem.MolFromSmiles(extract_template(r)['smarts'].split('>>')[0])
    site=f['product_atom_indices']['acceptor_site'];c2=next(a.GetIdx() for a in full.GetAtomWithIdx(site).GetNeighbors() if a.GetIdx()!=f['product_atom_indices']['anomeric'])
    ring=next(r for r in full.GetRingInfo().AtomRings() if c2 in r and len(r)==6 and sum(full.GetAtomWithIdx(i).GetAtomicNum()==8 for i in r)==1)
    c3=next(a.GetIdx() for a in full.GetAtomWithIdx(c2).GetNeighbors() if a.GetIdx() in ring and a.GetAtomicNum()==6 and any(n.GetAtomicNum()==8 and n.GetIdx() not in ring and n.GetDegree()==1 for n in a.GetNeighbors()))
    c4=next(a.GetIdx() for a in full.GetAtomWithIdx(c3).GetNeighbors() if a.GetIdx() in ring and a.GetAtomicNum()==6 and a.GetIdx()!=c2)
    number=full.GetAtomWithIdx(c4).GetAtomMapNum()
    # Partial aromatic SMARTS are valid reaction queries, not standalone SMILES.
    # Remove only C4 chirality on both mapped sides; RDKit carries conserved stereo.
    pattern=r"\[[^\]]+:"+str(number)+r"\]"
    return re.sub(pattern,lambda m:m.group(0).replace('@@','').replace('@',''),smarts)

def build():
    assert not (OUT/'template_source_manifest.json').exists(),'manifest frozen'
    records=rows(OUT/'runtime_instances.jsonl');by={r['instance_id']:r for r in records}
    templates=copy.deepcopy(rows(ROOT/'outputs/task016-p1/v2/templates.jsonl'))
    SS=[r for r in records if r['category']=='sugar_sugar_formation' and r['provenance'].get('pmcid') in ['PMC5856881','PMC9786081']]
    C=[r for r in records if r['category']=='C_formation' and r['provenance'].get('pmcid')=='PMC11975207']
    phlor=next(r['acceptor'] for r in records if r['category']=='C_formation' and r['provenance'].get('pmcid')=='PMC7558026')
    # All declared scopes/patterns derive from build-only source contexts before searches.
    specs=[('phloretin_mono_C_second',C),('hexoside_O2',[r for r in SS if r['sugar_type']=='glucose']),('rhamnoside_O2',[r for r in SS if r['sugar_type']=='xylose'])]
    allcores=[FLAVONE,'O=C1CC(c2ccccc2)Oc2ccccc21','O=c1c(-c2ccccc2)coc2ccccc12','O=C(C=Cc1ccccc1)c1ccccc1','O=C(CCc1ccccc1)c1ccccc1']
    for center,support in specs:
        support=sorted(support,key=lambda r:r['instance_id']);assert len({r['acceptor'] for r in support})>=2
        seed=support[0];base=extract_template(seed);patterns=[]
        if center=='phloretin_mono_C_second':
            left,right=base['smarts'].split('>>');product=Chem.MolFromSmiles(left);a,d=right.split('.',1);acceptor=Chem.MolFromSmiles(a)
            idx=structural_formation(seed['acceptor'],seed['donor'],seed['target'])['product_atom_indices'];core=Chem.MolFromSmarts(phlor);matches=product.GetSubstructMatches(core);assert matches
            keep=set(matches[0])|set(idx['added']);maps={product.GetAtomWithIdx(i).GetAtomMapNum() for i in keep if i not in idx['added']}
            smarts=subset(product,keep)+'>>'+subset(acceptor,{x.GetIdx() for x in acceptor.GetAtoms() if x.GetAtomMapNum() in maps})+'.'+d
            for r in support:
                parent=next(x for x in records if x['category']=='C_formation' and x['target']==r['acceptor'])
                patterns.append(glycan_stub(parent['acceptor'],parent['donor'],parent['target']))
            cores=[phlor]
        else:
            smarts=scoped_smarts(base,seed,'glucoside_O2')
            if center=='hexoside_O2':smarts=sugar_epimer_query(smarts,seed)
            # Parent sugar fragments use source-confirmed O-glycosides, preserving exact stereo.
            for r in support:
                parent=next((x for x in records if x['category']=='O_formation' and x['target']==r['acceptor']),None)
                if parent:patterns.append(glycan_stub(parent['acceptor'],parent['donor'],parent['target']))
            if center=='rhamnoside_O2':
                # One source rhamnosyl fragment on a different flavonol provides sugar identity only.
                parent=next(x for x in records if x['category']=='O_formation' and x['sugar_type']=='rhamnose')
                patterns=[glycan_stub(parent['acceptor'],parent['donor'],parent['target'])]
                cores=['O=[c:4]1[c:3]([O])[c:2](-[c:101]2[c:102][c:103][c:104]([O][CH3])[c:105][c:106]2)[o:1][c:109]2[c:8]([CH2][CH]=[C]([CH3])[CH3])[c:7]([O])[c:6][c:5]([O])[c:110]12']
            else:cores=[FLAVONE]  # Source Kaempferol Glc/Gal; no anthocyanin extrapolation.
        assert patterns,center
        t=dict(template_id='p2-scope:'+hashlib.sha256((smarts+center).encode()).hexdigest()[:20],template_role='scope_template',smarts=smarts,allowed_targets=[],required_context=dict(mode='enzymatic',donor_name=seed['required_context']['donor_name']),donor=seed['donor'],category=seed['category'],sugar_type=seed['sugar_type'],scope=dict(namespace='task016_p2',center_class=center,parent_glycan_patterns=sorted(set(patterns)),acceptor_cores=cores,interpretation='build-source structural candidate range; new activity, enzyme, site selectivity, conditions and yield unverified',enzyme_context='source UDP candidate class; seed gene not copied',declaration='source parent sugar and connection preserved; glucose/galactose C4 epimers permitted only by explicit parent identity guard; C scope restricted to mono-C Gal/Xyl phloroglucinol dihydrochalcone'),support_instances=[r['instance_id'] for r in support],validation_status='pending')
        templates.insert(0,t)
    validations=[]
    for t in templates:
        checks=[]
        for iid in t['support_instances']:
            r=by[iid];out=apply_template(t,r['target']);checks.append(dict(kind='support_replay',instance_id=iid,passed=canonical_side(r['reference_precursors']) in [o['precursors'] for o in out]))
        r=by[t['support_instances'][0]]
        if t['template_id'].startswith('p2-scope:'):
            for ctx in [dict(mode='chemical',donor_name=t['required_context']['donor_name']),dict(mode='enzymatic',donor_name='wrong UDP donor')]:checks.append(dict(kind='wrong_context_or_donor',passed=not apply_template(t,r['target'],ctx)))
            mol=Chem.MolFromSmiles(r['target']);idx=structural_formation(r['acceptor'],r['donor'],r['target'])['product_atom_indices']['anomeric'];mol.GetAtomWithIdx(idx).InvertChirality();wrong=Chem.MolToSmiles(mol,isomericSmiles=True)
            checks.append(dict(kind='wrong_anomeric_stereo',target=wrong,passed=not apply_template(t,wrong)))
            # Meaningful source-derived contrasting parent identity/site, not just CO.
            other=next(q for q in records if q['category']!=r['category'] and q['sugar_type']==r['sugar_type'])
            checks.append(dict(kind='outside_declared_parent_center',target=other['target'],passed=not apply_template(t,other['target'])))
        passed=all(q['passed'] for q in checks);t['validation_status']='source_reconstruction_passed' if passed else 'blocked_validation_failed';validations.append(dict(template_id=t['template_id'],role=t['template_role'],checks=checks,passed=passed))
    save('template_validation.jsonl',validations,True);save('templates.provisional.jsonl',templates,True)
    failed=[(v['template_id'],[q for q in v['checks'] if not q['passed']]) for v in validations if not v['passed']]
    if failed:print('FAILED',failed,flush=True);return
    save('templates.jsonl',templates,True)
    save('applicability_contract.json',dict(build_only=True,split_sha256=sha(OUT/'development_split_manifest.json'),new_scope_support=[dict(template_id=t['template_id'],category=t['category'],scope=t['scope'],distinct_acceptors=len({by[i]['acceptor'] for i in t['support_instances']})) for t in templates if t['template_id'].startswith('p2-scope:')],holdout_whitelists=False,new_transfer_evidence=False))
    save('representation_rules.json',json.loads((ROOT/'outputs/task016-p1/v2/representation_rules.json').read_text()))
    fusion=dict(version='v3-protected-generic-fusion-v1',default_enabled=False,domain_cap_per_molecule=4,prior=0.2,weight=1.0,generic_protection=3,fixed_branch_cap=12,ordering='new scopes in stable declared center order before byte-preserved inherited templates; no model/holdout outputs observed',reason='source-supported missing C/Glc/Xyl centers; inherited O unchanged',tuning=False)
    save('fusion_contract.json',fusion);save('review_binding.json',load_review().binding)
    dependencies={r['provenance']['raw_path']:sha(ROOT/r['provenance']['raw_path']) for r in records if r['provenance'].get('raw_path')}
    manifest=dict(schema_version=2,version='task016-p2-qualified-v3',rdkit=rdBase.rdkitVersion,review_binding=load_review().binding,policy={k:fusion[k] for k in ['default_enabled','domain_cap_per_molecule','prior','weight','generic_protection']},files_sha256={n:sha(OUT/n) for n in ['templates.jsonl','runtime_instances.jsonl','template_validation.jsonl','applicability_contract.json','representation_rules.json','fusion_contract.json']},raw_dependencies_sha256=dependencies,claim='source-bound structural candidate ranges; old exposed calibration only, new transfer not executed')
    save('template_source_manifest.json',manifest)
    c=dict(version=3,default_enabled=False,manifest=str((OUT/'template_source_manifest.json').relative_to(ROOT)),manifest_sha256=sha(OUT/'template_source_manifest.json'),status='development_calibration_partial_new_transfer_unvalidated')
    if not NO_CONFIG:
        for p in ['configs/glycoside-library-v3.json','flavoretro/assets/configs/glycoside-library-v3.json']:write(T,p,json.dumps(c,ensure_ascii=False,indent=2)+'\n')
    print('templates',len(templates),'new_scopes',3,'support',sum(len(v['checks']) for v in validations),flush=True)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir');parser.add_argument('--no-config',action='store_true');args=parser.parse_args()
    if args.output_dir:
        OUT=(ROOT/args.output_dir).resolve();assert OUT.is_relative_to(ROOT/'outputs/task016-p2')
    NO_CONFIG=args.no_config
    build()
