"""Registered enzyme-specific post-scope supplemental source discovery."""
import json,sys,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,request,save,save_rows,sha,now
from scripts.task016_p7_ss_fresh import historical

def execute():
    queries=['TITLE_ABS:rhamnosyltransferase AND (flavonoid OR flavonol OR flavone OR flavanone) AND OPEN_ACCESS:Y','(UGT79D OR UGT79A OR UGT91) AND OPEN_ACCESS:Y']
    plan=[dict(query_id='SS-FRESH-SUPPLEMENT:'+str(ix+1),query=q,url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',pageSize=100,resultType='core')),registered_at=now(),route='EuropePMC_enzyme_specific_supplement',max_pages=1,maximum_results=100,scope_freeze_sha256=sha(OUT/'scope_freeze.json')) for ix,q in enumerate(queries)]
    if (OUT/'fresh_supplemental_query_plan.jsonl').exists():raise RuntimeError('SUPPLEMENT_ALREADY_REGISTERED')
    save_rows('fresh_supplemental_query_plan.jsonl',plan);out=[];hits=[];seen=historical()
    for q in plan:
        res=request(q['url'],'metadata','Enzyme-specific official discovery after broad metadata-only sources yielded few open primary originals',phase='fresh',route=q['route'])
        c=[]
        if res['status_code']==200 and not res['error']:c=json.loads((ROOT/res['path']).read_text()).get('resultList',{}).get('result',[])
        out.append(dict(query_id=q['query_id'],returned=len(c),error=res['error'],http=res,executed_at=now()))
        for r in c:
            hits.append(dict(query_id=q['query_id'],pmcid=r.get('pmcid'),pmid=r.get('pmid'),doi=r.get('doi'),title=r.get('title'),historical_source=r.get('pmcid') in seen,metadata_only=True,evidence_eligible=False,raw_response=res['path']))
        save_rows('fresh_supplemental_query_execution.jsonl',out);save_rows('fresh_supplemental_hits.jsonl',hits)
    print(dict(queries=len(out),hits=len(hits),historical=sum(r['historical_source'] for r in hits)))
if __name__=='__main__':execute()
