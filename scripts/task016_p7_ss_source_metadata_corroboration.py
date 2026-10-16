"""A3 bounded metadata corroboration for SS sources with unavailable main text."""
import json
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,verify_hashes,role_manifest
from scripts.task016_p7_ss_new_source_identity_v3 import n
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
B=ROOT/'outputs/task016-p7/v1/SS/E02_design/new_source_discovery_v1';O=ROOT/'outputs/task016-p7/v1/SS/E02_design/new_source_A3_metadata_corroboration_v1'
def main():
    ip=B/'common_raw_only_source_input_v1.json';d=json.loads(ip.read_text());verify_hashes(d['raw_input_files_sha256']);result=[];inventory=[];inputs=[ip,ROOT/'scripts/task016_p7_ss_new_source_identity_v3.py',ROOT/'scripts/task016_p7_ss_source_metadata_corroboration.py']
    for s in d['sources']:
        med=[];cross=[]
        for r in s['raw_inputs']:
            if r['HTTP_status']!=200:continue
            p=ROOT/r['path']
            try:z=json.loads(p.read_text())
            except (ValueError,UnicodeDecodeError):continue
            med += [(m,p) for m in z.get('resultList',{}).get('result',[]) if str(m.get('pmid') or m.get('id'))==s['pmid']]
            x=z.get('message',{})
            if isinstance(x,dict):cross += [(c,p) for c in [x]+x.get('items',[]) if c.get('DOI','').lower()==s['doi'].lower()]
        assert med,s['source_id']
        inventory.append(dict(source_id=s['source_id'],doi=s['doi'],MED_route_occurrences=len(med),Crossref_route_occurrences=len(cross),MED_pointers=[pointer(p) for _,p in med],Crossref_pointers=[pointer(p) for _,p in cross],raw_original_fulltext_versions=len(s['valid_fulltext_originals']),route_occurrences_not_unique_sources=True,chemical_qualification_granted=False))
        if s['valid_fulltext_originals'] or not cross:continue
        m,mp=med[0];c,cp=cross[0];inputs += [mp,cp]
        ma=m['authorList']['author'];ca=c.get('author',[]);assert len(ma)==len(ca)>0
        names=[dict(order=i+1,MED=dict(given=a.get('firstName'),family=a.get('lastName')),Crossref=dict(given=z.get('given'),family=z.get('family')),given_equal=n(a.get('firstName'))==n(z.get('given')),family_equal=n(a.get('lastName'))==n(z.get('family'))) for i,(a,z) in enumerate(zip(ma,ca))]
        assert all(x['given_equal'] and x['family_equal'] for x in names)
        ji=m['journalInfo'];mj=ji['journal'];cj=c.get('container-title',[]);crissn=c.get('ISSN',[]);missn=[mj.get('issn'),mj.get('essn')];sameISSN=bool(set(crissn)&set(missn))
        journal_equal=any(n(mj['title'])==n(x) for x in cj);explicit_alias=(sameISSN and ((mj['title']=='Molecular genetics and genomics : MGG' and cj==['Molecular Genetics and Genomics']) or (mj['title']=='Plant & cell physiology' and cj==['Plant and Cell Physiology'])))
        dates={k:c[k] for k in ['published','published-online','published-print'] if k in c};years={str(v) for a in dates.values() for parts in a.get('date-parts',[]) for v in parts[:1]}
        page=c.get('page') or c.get('article-number')
        checks=dict(doi=m['doi'].lower()==c['DOI'].lower()==s['doi'].lower(),PMID=m['pmid']==s['pmid'],title=n(m['title'])==n(c.get('title',[''])[0]),journal=journal_equal or explicit_alias,year=str(m['pubYear']) in years,volume=ji.get('volume')==c.get('volume'),issue=ji.get('issue')==c.get('issue'),pages_or_article_number=m.get('pageInfo')==page,ordered_authors=all(x['given_equal'] and x['family_equal'] for x in names))
        assert all(checks.values()),(s['source_id'],checks)
        result.append(dict(source_id=s['source_id'],doi=s['doi'],MED_pointer=pointer(mp),Crossref_pointer=pointer(cp),checks=checks,ordered_authors=names,journal_literals=dict(MED=mj['title'],Crossref=cj,MED_ISSN=missn,Crossref_ISSN=crissn,same_ISSN=sameISSN,explicit_qualified_or_ampersand_alias=explicit_alias),title_literals=dict(MED=m['title'],Crossref=c.get('title')),publication_dates=dict(MED_pubYear=m['pubYear'],MED_dateOfPublication=ji.get('dateOfPublication'),MED_firstPublicationDate=m.get('firstPublicationDate'),Crossref=dates),bibliographic_literals=dict(MED_volume=ji.get('volume'),Crossref_volume=c.get('volume'),MED_issue=ji.get('issue'),Crossref_issue=c.get('issue'),MED_pageInfo=m.get('pageInfo'),Crossref_page=c.get('page'),Crossref_article_number=c.get('article-number'),Crossref_publisher=c.get('publisher'),MED_publisher_not_invented=True),metadata_corroborated=True,primary_main_text_available=False,chemical_qualification_granted=False,human_reviewed=False))
    assert len(result)==3 and len(inventory)==12
    out=[]
    for name,data in [('three_metadata_publication_identity_checks.json',result),('twelve_source_metadata_route_inventory.json',inventory),('A3_metadata_corroboration_summary.json',dict(task=TASK,at=now(),metadata_sources_processed=12,additional_dual_route_metadata_corroborated=3,previous_full_XML_PDF_identity_sources=3,remaining_without_Crossref_in_this_raw_input=6,new_primary_originals=0,new_chemical_qualifications=0,new_HTTP=0,new_MCTS=0,missing_main_text_not_filled_from_metadata=True))]:
        p=O/name;immutable_json(p,data);out.append(p)
    role=role_manifest('A3 root metadata corroboration','SS-E02',inputs,out,dict(processed=12,passed=3,pending=6,previous_original_pass=3),read_holdout=False,read_model_outcome=False,unprocessed=['Six sources without a second Crossref record in this packet','Unavailable primary main texts and all chemical qualification gates'])
    role.update(root_authored=True,independent_chemical_validation=False,new_HTTP=0,new_MCTS=0,metadata_pass_not_reaction_pass=True)
    p=O/'role_A3_manifest.json';immutable_json(p,role);print(json.dumps(dict(role=pointer(p),additional_metadata_pass=3,chemical_qualifications=0)))
if __name__=='__main__':main()
