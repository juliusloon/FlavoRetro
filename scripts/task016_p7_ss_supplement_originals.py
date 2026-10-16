"""Acquire newly discovered open primary papers; preserve every selection outcome."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,request,save,save_rows,rows,sha,now
from scripts.task016_p7_ss_fresh import historical

def execute():
    ids={'PMC12741331','PMC11527692','PMC6506761','PMC7264309','PMC5479930','PMC4573293','PMC10114341','PMC12046898','PMC7808588'}
    candidates={r['pmcid']:r for r in rows(OUT/'fresh_supplemental_hits.jsonl') if r['pmcid'] in ids and not r['historical_source']}
    plan=[dict(selection_id='SS-FRESH-SUPPLEMENT-SOURCE:'+pmcid,pmcid=pmcid,doi_hint=r['doi'],title_hint=r['title'],registered_at=now(),raw_discovery_response=r['raw_response'],scope_freeze_sha256=sha(OUT/'scope_freeze.json'),reason='Enzyme-specific search post-scope independent original-source review; not outcome-driven') for pmcid,r in sorted(candidates.items())]
    if (OUT/'fresh_supplemental_original_plan.json').exists():raise RuntimeError('ALREADY_REGISTERED')
    save('fresh_supplemental_original_plan.json',dict(selections=plan,scope_frozen=True));out=[];excluded=historical()
    for q in plan:
        pmcid=q['pmcid'];r=dict(q,evidence_eligible=False,read_model_outcomes=False,chemically_read_at=None)
        if pmcid in excluded:r.update(disposition='rejected_historical_source_exposure')
        else:
            meta=request(f'https://pmc-oa-opendata.s3.amazonaws.com/{pmcid}.1/{pmcid}.1.json','metadata','Official original source identity and lawful OA URL',phase='fresh',route='supplemental_PMC_original')
            r['metadata']=meta
            url=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'
            if meta['status_code']==200 and not meta['error']:
                m=json.loads((ROOT/meta['path']).read_text());r['official_identity']=dict(pmcid=m.get('pmcid'),doi=m.get('doi'),title=m.get('title'),citation=m.get('citation'),license=m.get('license_code'));r['media_urls']=m.get('media_urls',[])
                candidate=m.get('xml_url','').replace('s3://pmc-oa-opendata/','https://pmc-oa-opendata.s3.amazonaws.com/')
                if candidate.startswith('https://pmc-oa-opendata.s3.amazonaws.com/'):url=candidate
            x=request(url,'xml','Original post-scope chemical source; no independent eligibility inferred from download',phase='fresh',route='supplemental_PMC_original');r['xml']=x
            r['disposition']='deferred_independent_identity_and_structure' if x['status_code']==200 and not x['error'] else 'deferred_official_original_unavailable'
        out.append(r);save_rows('fresh_supplemental_original_intake.jsonl',out)
    print(dict(selections=len(plan),executed=len(out),downloaded=sum(r.get('xml',{}).get('status_code')==200 for r in out)))
if __name__=='__main__':execute()
