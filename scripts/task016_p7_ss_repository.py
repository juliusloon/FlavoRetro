"""Public repository locator fallback for primary originals without PMC."""
import json,sys,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,ROOT,request,save_rows,save,now,sha

def execute():
    dois=['10.1111/tpj.12030','10.1080/09168451.2018.1491286','10.1007/s11103-013-0133-1','10.1007/s00253-015-6982-6','10.1007/s00425-025-04742-w']
    plan=[]
    for i,doi in enumerate(dois):
        for route,url in [('OpenAlex_OA_locator','https://api.openalex.org/works/https://doi.org/'+doi),('SemanticScholar_OA_locator','https://api.semanticscholar.org/graph/v1/paper/DOI:'+doi+'?'+urllib.parse.urlencode({'fields':'title,year,externalIds,openAccessPdf,url'}))]:
            plan.append(dict(query_id='SS-REPOSITORY-LOCATOR:'+str(i)+':'+route,doi_hint=doi,url=url,route=route,registered_at=now(),maximum_results=1,scope_freeze_sha256=sha(OUT/'scope_freeze.json'),reason='Public lawful OA repository locator after official no-PMC/public publisher path did not expose original fulltext; no access-control circumvention'))
    if (OUT/'fresh_repository_locator_plan.jsonl').exists():raise RuntimeError('PLAN_EXISTS')
    save_rows('fresh_repository_locator_plan.jsonl',plan);out=[]
    for q in plan:
        res=request(q['url'],'metadata',q['reason'],phase='fresh',route=q['route']);links=[];identity={}
        if res['status_code']==200 and not res['error']:
            data=json.loads((ROOT/res['path']).read_text());identity=dict(title=data.get('title'),year=data.get('publication_year',data.get('year')),doi=data.get('doi'),ids=data.get('ids',data.get('externalIds')))
            if q['route']=='OpenAlex_OA_locator':
                locations=data.get('locations',[])
                best=data.get('best_oa_location')
                if best:locations.append(best)
                for loc in locations:
                    if loc.get('is_oa') and loc.get('pdf_url'):links.append(dict(url=loc['pdf_url'],source=loc.get('source'),license=loc.get('license'),version=loc.get('version'),locator_reports_oa=True))
            else:
                loc=data.get('openAccessPdf') or {}
                if loc.get('url'):links.append(dict(url=loc['url'],license=loc.get('license'),status=loc.get('status'),locator_reports_oa=True))
        dedup={l['url']:l for l in links}
        out.append(dict(q,response=res,locator_identity=identity,lawful_OA_candidate_links=list(dedup.values()),evidence_eligible=False,read_model_outcomes=False))
        save_rows('fresh_repository_locator_execution.jsonl',out)
    print([(r['doi_hint'],r['route'],r['response']['status_code'],len(r['lawful_OA_candidate_links'])) for r in out])
if __name__=='__main__':execute()
