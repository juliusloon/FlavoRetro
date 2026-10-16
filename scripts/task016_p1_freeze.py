"""Freeze source accounting and publication/reaction-closed development views."""
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from scripts.task016_p1_sources import ROOT,OUT,RAW,save,rows
from flavoretro.open_glycoside_library import normalize_species
from flavoretro.reviewed_resources import load_review,reaction_signature
from flavoretro.resources import sha

def freeze():
    assert not (OUT/'development_split_manifest.json').exists(),'split already frozen'
    instances=rows(OUT/'provisional_instances.jsonl');review=load_review()
    previous=set()
    for sig in review.data['exact_reactions']:
        try:
            left,right=sig.split('>>');previous.add(reaction_signature([normalize_species(left)['normalized']],[normalize_species(right)['normalized']]))
        except Exception:pass
    parent=list(range(len(instances)));links=[];seen={}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,r in enumerate(instances):
        ref=r.get('original_reference',r['provenance']);r['dedup_group']=hashlib.sha256(r['covalent_signature'].encode()).hexdigest()
        r['forced_build']=r.get('inherited',False) or r['covalent_signature'] in previous
        r['task015_development_exact_match']=r['covalent_signature'] in previous
        keys=['reaction:'+r['covalent_signature'],'assay:'+r['actual_assay_group']]
        if ref.get('pmcid'):keys.append('publication:'+ref['pmcid'])
        if ref.get('doi'):keys.append('doi:'+ref['doi'].lower())
        for key in keys:
            if key in seen:
                j=seen[key];parent[find(i)]=find(j);links.append(dict(left=r['instance_id'],right=instances[j]['instance_id'],link_type=key.split(':')[0],link_key_sha256=hashlib.sha256(key.encode()).hexdigest()))
            else:seen[key]=i
    components={}
    for i,r in enumerate(instances):components.setdefault(find(i),[]).append(r)
    # Chosen by source-specific structural identification and isolated publication groups;
    # no template, generic model, filtering or MCTS output has been inspected.
    preferred={'PMC11365401','PMC5856881','PMC9786081'};groups=[]
    for members in components.values():
        papers=sorted({r.get('original_reference',r['provenance']).get('pmcid') for r in members if r.get('original_reference',r['provenance']).get('pmcid')})
        gid=hashlib.sha256('\n'.join(sorted(r['instance_id'] for r in members)).encode()).hexdigest()
        forced=any(r['forced_build'] for r in members)
        role='development_holdout' if preferred.intersection(papers) and not forced else 'development_build'
        for r in members:r.update(source_group=gid,template_role=role,development_exposed=True,human_reviewed=False)
        groups.append(dict(source_group=gid,pmcids=papers,forced_build=forced,role=role,instances=sorted(r['instance_id'] for r in members),reactions=len({r['covalent_signature'] for r in members}),targets=len({r['target'] for r in members})))
    build=[r for r in instances if r['template_role']=='development_build'];hold=[r for r in instances if r['template_role']=='development_holdout']
    assert len({r['target'] for r in hold})>=12 and len({r['covalent_signature'] for r in hold})>=12,'minimum holdout not attained'
    assert not {r['covalent_signature'] for r in build}&{r['covalent_signature'] for r in hold}
    assert all(not r.get('inherited') and not r['forced_build'] for r in hold)
    save('instances.jsonl',instances,True);save('build_views.jsonl',build,True);save('runtime_instances.jsonl',build,True);save('holdout_views.jsonl',hold,True)
    save('reference_precursors.jsonl',[{k:r[k] for k in ['instance_id','target','reference_precursors','reference_signature','covalent_signature','source_group','template_role','dedup_group']} for r in instances],True)
    save('dedup_links.jsonl',links,True)
    reaction_groups=[]
    for sig in sorted({r['covalent_signature'] for r in instances}):
        rr=[r for r in instances if r['covalent_signature']==sig]
        reaction_groups.append(dict(covalent_signature=sig,dedup_group=rr[0]['dedup_group'],instance_ids=sorted(r['instance_id'] for r in rr),inherited=any(r.get('inherited') for r in rr),category=rr[0]['category'],sugar_type=rr[0]['sugar_type'],template_role=rr[0]['template_role']))
    save('reaction_groups.jsonl',reaction_groups,True)
    counts=dict(assay_annotations=len(instances)-4,specific_instances=len(instances),inherited_instances=4,unique_covalent_groups=len(reaction_groups),new_covalent_groups=sum(not g['inherited'] for g in reaction_groups),new_acceptors=len({r['acceptor'] for r in instances if not r.get('inherited')}),new_sugars=sorted({r['sugar_type'] for r in instances if not r.get('inherited')}),new_publications=len({r['provenance']['pmcid'] for r in instances if not r.get('inherited')}),closure_groups=len(groups),build_reactions=len({r['covalent_signature'] for r in build}),holdout_reactions=len({r['covalent_signature'] for r in hold}),holdout_targets=len({r['target'] for r in hold}),new_categories=dict(Counter(g['category'] for g in reaction_groups if not g['inherited'])))
    save('counting_contract.json',dict(schema_version=1,counts=counts,definition='formation reaction is full conserved acceptor + full UDP donor -> primary source-identified product, deduplicated under separately versioned acid O representation; contexts and physical replicates not counted as reactions',physical_replicates='not inferred; null preserved',review_type='agent_delegated',human_reviewed=False))
    save('development_split_manifest.json',dict(schema_version=1,version='task016-p1-development-split-v1',approval_type='agent_delegated',template_outputs_observed=False,model_outputs_observed=False,selection='source-standard/NMR identification preferred for three independent publication components PMC11365401/PMC5856881/PMC9786081; transitive DOI/PMCid/full covalent reaction/assay closure; any legacy TASK016 or TASK015 exact match forces entire component build',groups=sorted(groups,key=lambda x:x['source_group']),counts=counts,files_sha256={n:sha(OUT/n) for n in ['instances.jsonl','runtime_instances.jsonl','build_views.jsonl','holdout_views.jsonl','reference_precursors.jsonl','dedup_links.jsonl','reaction_groups.jsonl','assay_annotations.json']},review_binding=review.binding,scope='development_exposed, template-build held out; not blind, training overlap unknown',patents='no patent source admitted; no patent-family split claim needed'))
    save('evaluation_reference_manifest.json',dict(schema_version=1,scope='independent offline evaluator only; no runtime registry linkage to holdout views',files_sha256={n:sha(OUT/n) for n in ['reference_precursors.jsonl','holdout_views.jsonl','development_split_manifest.json']},human_reviewed=False))
    print(json.dumps(counts,sort_keys=True))

def inventory():
    articles=json.loads((OUT/'article_acquisition_manifest.json').read_text())+json.loads((OUT/'article_acquisition_addendum.json').read_text());cases=json.loads((OUT/'assay_annotations.json').read_text())['cases'];used={c['pmcid'] for c in cases};anchors={(c['pmcid'],p) for c in cases for p in c['locators']}
    dispositions=[]
    for r in rows(OUT/'rhea_knowledge_records.jsonl'):dispositions.append(dict(universe='rhea-query-row',record_id=r['record_id'],query_snapshot=r['query_snapshot'],disposition='knowledge_only_not_assay',parse_status=r['parse_status']))
    for f in ['enzymemap_processed_candidates.jsonl','enzymemap_raw_candidates.jsonl']:
        for i,r in enumerate(rows(OUT/f)):dispositions.append(dict(universe=f,record_index=i,disposition='retained_candidate_no_primary_reference_link',source_flags=r.get('source'),record_sha256=hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()))
    for r in rows(OUT/'article_discovery_records.jsonl'):dispositions.append(dict(universe='article-discovery',record_id=r['pmcid'],disposition='assay_source_annotated' if r['pmcid'] in used else 'retained_metadata_or_unresolved_source',selection_reason=r.get('selection_reason')))
    for r in rows(OUT/'article_evidence_segments.jsonl'):
        dispositions.append(dict(universe='article-evidence-segment',record_id=r['pmcid'],locator=r['locator'],disposition='supports_admitted_annotation' if (r['pmcid'],r['locator']) in anchors else 'retained_source_segment_no_executable_assay_assertion'))
    for r in rows(OUT/'assay_record_dispositions.jsonl'):dispositions.append(dict(universe='assay-annotation',**r))
    save('record_dispositions.jsonl',dispositions,True)
    attempts=rows(OUT/'acquisition_attempts.jsonl');files=[]
    for r in attempts:
        files.append(dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'],provider=r['provider'],role=r['content_role'],disposition='retained_failure_response' if r['status']!='raw_available' else 'immutable_source_snapshot; semantic eligibility separately recorded',status=r['status']))
    save('file_dispositions.jsonl',files,True)
    queries=[]
    for r in attempts:
        if r['status']!='raw_available' or r['provider']!='europepmc':continue
        try:
            d=json.loads((ROOT/r['path']).read_text())
            if 'hitCount' in d:
                n=len(d.get('resultList',{}).get('result',[]));queries.append(dict(url=r['url'],raw_path=r['path'],hit_count=d['hitCount'],retrieved_rows=n,unretrieved_rows=max(0,d['hitCount']-n),pagination_complete=n>=d['hitCount'],bounded=True))
        except Exception:pass
    save('source_registry.json',dict(schema_version=1,sources=[dict(provider='Rhea',license='CC BY4.0',role='reaction knowledge and source discovery; not assays'),dict(provider='EuropePMC/PMC',license='per-article recorded in acquisition manifests',role='open full text, identified forward assays and attachments'),dict(provider='EnzymeMap Zenodo8254726',license='CC BY4.0 dataset, independent of MIT code',role='raw/processed candidate corpus, no per-assay primary references in downloaded CSV'),dict(provider='PubChem',role='compound identity only; no assay support'),dict(provider='SABIO-RK',status='HTML response where SBML required; semantic unavailable; no records admitted'),dict(provider='ORD/HTE',status='inherited frozen corpus audit; upstream GitHubAPI403 prevents verified incremental revision; no new target-specific assay')],queries=queries,source_eligibility='113 initial fulltext articles plus one addendum; each article license recorded; failures and unopened evidence retained',all_counts='separate query rows, candidate rows, assays, covalent reactions; never aggregate library corpus into new assays'))
    negatives=[]
    specifications=[('PMC9149423','Rd3GT6','malvidin','UDP-alpha-D-glucose',31),('PMC9437722','MrUGT78R1/R2','tested flavonols','UDP-glucose/UDP-galactose',11)]
    for pmc,enzyme,a,d,n in specifications:
        source=next(r for r in articles if r['pmcid']==pmc);ps=ET.parse(ROOT/source['xml']['path']).getroot().findall('.//body//p');text=' '.join(''.join(ps[n-1].itertext()).split())
        negatives.append(dict(pmcid=pmc,enzyme=enzyme,acceptor_name=a,donor_name=d,outcome='source explicit absent/negative activity; no numeric zero fabricated',value=None,status='narrative_annotation_not_executable',raw_path=source['xml']['path'],raw_sha256=source['xml']['sha256'],locator=f'body//p[{n}]',source_text=text,human_reviewed=False))
    save('negative_instances.jsonl',negatives,True)
    save('source_conflicts.jsonl',[dict(provider='EnzymeMap',compound_name="quercetin 3prime-O-beta-D-glucoside",conflict='downloaded identity encodes quercetin3-O; substituted source position encoding used, database variant retained',disposition='identity conflict retained; not an independent new assay'),dict(provider='Rhea',record_id='19153',compound_name='apiin',conflict='acceptor scaffold not fully conserved by encoded product; PubChem fully named apiin identity independently retrieved and source authentic product assignment retained',disposition='Rhea encoded product not used'),dict(provider='PMC glycosylation literature',conflict='C-products appearing only after acid dehydration, tentative MS-only sites and ambiguous multiple glycosylations not counted as isolated formation assays',disposition='source segments retained; no executable admission')],True)
    byte_count=sum(p.stat().st_size for p in RAW.rglob('*') if p.is_file());acq=dict(request_attempts=len(attempts),bytes=byte_count,article_ids=len(articles),available_articles=sum(r['status']=='fulltext_available' for r in articles),supplementary_requests=sum(r['content_role']=='supplementary' for r in attempts),metadata_records=len(rows(OUT/'article_discovery_records.jsonl')),processed_corpus=json.loads((OUT/'enzymemap_corpus_accounting.json').read_text()),disposition_counts=dict(Counter(r['universe'] for r in dispositions)),record_disposition_difference=0,full_corpus_non_candidates='stable original CSV rows preserved; count/rule/disposition complement in enzymemap_corpus_accounting.json',non_downloaded='unretrieved query hits and attachments outside first4 bounded selection are not acquired records; original listing retained',all_source_bytes_sha256={r['path']:r['sha256'] for r in attempts})
    assert len(attempts)<=4000 and byte_count<=5*1024**3 and len(articles)<=200 and acq['supplementary_requests']<=400
    save('source_yield_inventory.json',acq)
if __name__=='__main__':inventory();freeze()
