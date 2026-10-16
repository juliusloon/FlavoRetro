"""Historical provisional v1 freeze; both new C8 encodings withdrawn in qualified v2.
Never treat this preserved v1 proposal as current admission; existing v1 is immutable.
"""
import sys,json,copy,hashlib,re,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,save,rows
from flavoretro.resources import sha
from flavoretro.open_glycoside_library import structural_formation,covalent_signature,normalize_species
from flavoretro.reviewed_resources import reaction_signature
# Identity resolution/encoding helpers only. Import does not invoke curation or write P1 data.
from scripts.task016_p1_curate import resolve,DONORS,GLC_STUB
from scripts.task016_p1_encode import CORE,attach_stub
from rdkit import Chem
articles={r['pmcid']:r for n in ['article_acquisition_manifest.json','article_acquisition_addendum.json'] for r in json.loads((OUT/n).read_text()) if r['status']=='fulltext_available'}
segments=rows(OUT/'article_evidence_segments.jsonl')
def provenance(pmc,locators,identity):
    article=articles[pmc]
    anchors=[]
    for locator in locators:
        s=next(r for r in segments if r['pmcid']==pmc and r['locator']==locator)
        anchors.append(dict(locator=locator,text_sha256=s['text_sha256']))
    root=ET.parse(ROOT/article['xml']['path']).getroot();doi=root.find(".//article-id[@pub-id-type='doi']")
    return dict(pmcid=pmc,doi=doi.text if doi is not None else None,raw_path=article['xml']['path'],raw_sha256=article['xml']['sha256'],license=article.get('license'),article_version=article.get('article_version'),locators=anchors,identification=identity,source_quality='specific_forward_assay_source_assignment')
def c8(smiles):
    m=Chem.MolFromSmiles(smiles);q=Chem.MolFromSmarts(CORE.replace('cH','c'));idx=next(a.GetIdx() for a in q.GetAtoms() if a.GetAtomMapNum()==8)
    matches=m.GetSubstructMatches(q,uniquify=False);sites={v[idx] for v in matches};assert len(sites)==1
    # C-glycan stereochemistry copied from independently encoded source beta-D-C-glucoside.
    from scripts.task016_p1_curate import C_STUB
    return attach_stub(smiles,C_STUB,next(iter(sites)))
def encode(pmc,enzyme,a,p,locators,identity,sugar,case):
    d,dp=DONORS[sugar];f=structural_formation(a,d,p);prov=provenance(pmc,locators,identity)
    iid=pmc+':'+enzyme+':p2:'+hashlib.sha256((a+'>'+d+'>'+p).encode()).hexdigest()[:20]
    return dict(instance_id=iid,record_type='specific_forward_assay_source_annotation',review_type='agent_delegated',human_reviewed=False,independent_chemical_validation=False,development_exposed=True,training_overlap='unknown',source_quality='specific_forward_assay_source_assignment',original_reference=prov,provenance=prov,actual_assay_group=pmc+':'+enzyme+':'+a+':'+sugar,physical_replicates=None,acceptor=a,donor=d,target=p,reference_precursors=sorted([a,d]),reference_signature=reaction_signature([a,d],[p]),covalent_signature=covalent_signature(a,d,p),formation=f,category=f['family'],sugar_type=sugar,catalyst_mode='enzymatic',required_context=dict(mode='enzymatic',enzyme=enzyme,donor_name=case['donor_name'],donor_delivery='source UDP donor regeneration context; not a prediction'),source_yield=dict(value=None,status='no normalized isolated-yield assertion; raw measurements retained'),source_conditions=dict(status='source context retained; no predicted conditions'),prediction_conditions_verified=False,actionable=False,annotation_case=case,inherited=False,original_structures=[dict(provider='source author structure/NMR name machine encoding',case=case,role='chemical identity encoding, not new assay')],normalization={'version':'acid-oxygen-protonation-v1','donor':dp})
def freeze():
    assert not (OUT/'development_split_manifest.json').exists(),'split frozen'
    inherited=rows(ROOT/'outputs/task016-p1/v2/instances.jsonl')
    allrows=[];roles=[]
    for old in inherited:
        r=copy.deepcopy(old);roles.append(dict(instance_id=r['instance_id'],original_role=r['template_role'],original_source_group=r.get('source_group'),original_path='outputs/task016-p1/v2/instances.jsonl',original_SHA=sha(ROOT/'outputs/task016-p1/v2/instances.jsonl'),P2_role='development_build',reason='previous TASK016/P1 exposure, including four SS failures'))
        r.update(inherited=True,template_role='development_build',P2_role='development_build',original_P1_role=old['template_role'],source_group='inherited:'+old.get('source_group',old['provenance'].get('pmcid','unknown')),forced_build=True)
        allrows.append(r)
    # Two NMR-characterized direct 8-C-beta-D-glucosides provide a separate supported core.
    new=[]
    for name,loc in [('kaempferol',[19,20,21,22,25]),('quercetin',[19,20,23,24,25])]:
        a,_=resolve(name);a=normalize_species(a)['normalized'];p=c8(a)
        new.append(encode('PMC9700910','TcCGT',a,p,[f'body//p[{i}]' for i in loc],'isolated author-assigned 8-C-glucoside, LC/MS and 1H/13C NMR; source C-glycan stereochemistry bound to full sugar donor and structural name; encoding agent-delegated','glucose',dict(acceptor_name=name,target_name=name+' 8-C-beta-D-glucoside',position=8,donor_name='UDP-alpha-D-glucose',structure_mode='source C8 name encoding',source_sugar_assignment='source beta-D-glucosyl fragment, no inferred wet experiment')))
    # Candidate examples that do not form a qualifying 6-target panel remain unresolved / prospective.
    unresolved=[dict(pmcid='PMC10465961',category='C_formation',reason='2-hydroxynaringenin C-rhamnosyl intermediate3 only MS; acid-dehydrated violanthin/isoviolanthin cannot establish complete single-step intermediate stereo',locators=['body//p[21]'],disposition='retained_unresolved_single_step_identity'),dict(pmcid='PMC7060329',category='C_formation',reason='phloretin/nothofagin exact overlap forces source build; final vitexin/orientin follow intermediate/dehydration pathway; MS-only C-Ara assignment not complete executable identity',disposition='retained_candidate_or_overlap'),dict(pmcid='PMC6255700',category='sugar_sugar_formation',potential_distinct_targets=2,reason='cyanidin/peonidin3-O-sophoroside named assays; full source identity/standard and isolated donor/product stereo admission still pending; no 6-target panel',disposition='prospective_not_runtime'),dict(pmcid='PMC3507004',category='sugar_sugar_formation',potential_distinct_targets=1,reason='cyanidin sambubioside standard validated; other substrate activities do not identify each complete product; no 6-target panel',disposition='prospective_not_runtime'),dict(pmcid='PMC12313340',category='sugar_sugar_formation',potential_distinct_targets=1,reason='source NMR Q-g-r-g is glucose(1→3)rhamnose on rutin; not glucose(1→2)glucose, target identity encoding not yet admitted; no 6-target panel',disposition='prospective_not_runtime'),dict(pmcid='PMC4494776',category='sugar_sugar_formation',reason='K-sophoroside exact old overlap forces entire publication component build; Q/Gal substrate activity not sufficient to fabricate individual full product identity',disposition='old_reaction_overlap_or_unresolved_product'),dict(pmcid='PMC4282749',category='sugar_sugar_formation',reason='K/Q sophoroside standard/NMR confirmed; K reaction overlaps prior P1 so entire source component forced build',disposition='old_reaction_overlap'),dict(pmcid='PMC12993211',category='C_formation',reason='direct TcCGT engineering source refers original TcCGT/known C8 products; precise source closure and complete individual product identity need curation; not counted as held-out',disposition='retained_candidate_not_runtime')]
    for r in new:r.update(template_role='development_build',P2_role='development_build',source_group='new:C8:PMC9700910',forced_build=False)
    allrows.extend(new)
    # No qualifying new holdout panel. Stop primary transfer searches at G2, retain useful build engineering.
    save('instances.jsonl',sorted(allrows,key=lambda r:r['instance_id']),True);save('runtime_instances.jsonl',sorted(allrows,key=lambda r:r['instance_id']),True);save('build_views.jsonl',sorted(allrows,key=lambda r:r['instance_id']),True);save('holdout_views.jsonl',[],True)
    save('unresolved_instances.jsonl',unresolved,True);save('legacy_roles.jsonl',roles,True)
    save('reference_precursors.jsonl',[{k:r[k] for k in ['instance_id','target','reference_precursors','reference_signature','covalent_signature','source_group','template_role']} for r in allrows],True)
    groups=[]
    for sig in sorted({r['covalent_signature'] for r in allrows}):
        rr=[r for r in allrows if r['covalent_signature']==sig]
        groups.append(dict(covalent_signature=sig,category=rr[0]['category'],sugar_type=rr[0]['sugar_type'],instance_ids=sorted(r['instance_id'] for r in rr),P2_role='development_build',inherited=any(r['inherited'] for r in rr)))
    save('reaction_groups.jsonl',groups,True)
    closure_links=[]
    for r in allrows:
        for q in allrows:
            if r['instance_id']>=q['instance_id']:continue
            if r['covalent_signature']==q['covalent_signature'] or r['provenance'].get('pmcid')==q['provenance'].get('pmcid'):closure_links.append(dict(left=r['instance_id'],right=q['instance_id'],keys=['publication'] if r['provenance'].get('pmcid')==q['provenance'].get('pmcid') else ['exact_reaction'],role='build'))
    save('dedup_links.jsonl',closure_links,True)
    counts=dict(specific_instances=len(allrows),inherited_instances=len(inherited),new_instances=len(new),unique_covalent_reactions=len(groups),new_covalent_reactions=sum(not r['inherited'] for r in groups),categories=dict(Counter(r['category'] for r in groups)),holdout_targets={'C_formation':0,'sugar_sugar_formation':0},holdout_source_groups={'C_formation':0,'sugar_sugar_formation':0},SS_prospective_upper_bound=4)
    save('counting_contract.json',dict(counts=counts,zeros_are_explicit=True,physical_replicates='not inferred',definition='full acceptor+UDP donor to author-assigned single-step product; machine encoding and source identity remain separate from independent chemistry',review_type='agent_delegated'))
    save('development_split_manifest.json',dict(task='TASK-016-P2',version='P2-build-calibration-v1',approval_type='agent_delegated',source_only_selection=True,model_outputs_observed=False,template_outputs_observed=False,holdout_qualified={'C_formation':False,'sugar_sugar_formation':False},transfer_status='not_executed_below_G2_minimum',selection='all inherited instances forced build; 2 new NMR-assigned C8 build instances for scope support; prospectives retained separately; no old failed target promoted to holdout',closure='DOI/PMC/experiment/full covalent reaction/upstream assay links; all admitted rows build; no split-isolation claim with zero holdout',source_candidates_unfinished=unresolved,files_sha256={n:sha(OUT/n) for n in ['instances.jsonl','runtime_instances.jsonl','build_views.jsonl','holdout_views.jsonl','legacy_roles.jsonl','reference_precursors.jsonl','unresolved_instances.jsonl','reaction_groups.jsonl','dedup_links.jsonl']},human_reviewed=False,development_exposed=True,training_overlap='unknown',counts=counts))
    save('evaluation_reference_manifest.json',dict(role='independent evaluator only; no new holdout runtime linkage',files_sha256={n:sha(OUT/n) for n in ['reference_precursors.jsonl','holdout_views.jsonl','development_split_manifest.json']}))
    save('source_feasibility.json',dict(G1_status='partial',G2_status='below_minimum_stop_primary_transfer',engineering_can_continue='source supported scope construction and 17 old regression targets; no fresh A/B/D transfer matrix',C={'fully_admitted_new_targets':2,'new_holdout_targets':0,'minimum':6,'notes':'new C8 build support is useful; complete source-closed held-out panel unavailable in curated candidate universe'},SS={'prospective_max_without_activity_inference':4,'qualified_new_holdout_targets':0,'minimum':6,'notes':'old K/Q overlaps cannot count as new sources; individual substrate activity not sufficient for full product identity'},scientific_thresholds_unchanged=True))
    print(json.dumps(counts,ensure_ascii=False),flush=True)
if __name__=='__main__':freeze()
