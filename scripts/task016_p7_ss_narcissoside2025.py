"""Actual public primary/SI routes for a new E01 isorhamnetin candidate."""
import sys,json,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import scripts.task016_p7_ss_sources as s
BASE=s.OUT;s.OUT=BASE/'fresh_narcissoside2025_original';s.OUT.mkdir(exist_ok=True)
doi='10.1021/acs.jafc.4c12187'
plan=[dict(url='https://pubs.acs.org/doi/'+doi,role='publisher_html',route='public_ACS_DOI_primary',method='GET'),dict(url='https://api.openalex.org/works/https://doi.org/'+doi,role='metadata',route='public_repository_locator_OpenAlex',method='GET'),dict(url='https://api.semanticscholar.org/graph/v1/paper/DOI:'+doi+'?fields=title,externalIds,openAccessPdf,url',role='metadata',route='public_repository_locator_SemanticScholar',method='GET'),dict(url='https://api.figshare.com/v2/articles/search',role='metadata',route='official_ACS_figshare_public_SI_discovery',method='POST',body={'resource_doi':doi})]
if (s.OUT/'original_plan.json').exists():raise RuntimeError('IMMUTABLE_BATCH_EXISTS')
s.save('original_plan.json',dict(doi=doi,registered_at=s.now(),epoch_id='SS-E01',scope_freeze_sha256=s.sha(BASE/'scope_freeze.json'),discovery_input=str(BASE/'fresh_substrate_source_batch2/hits.jsonl'),discovery_input_sha256=s.sha(BASE/'fresh_substrate_source_batch2/hits.jsonl'),routes=plan,reason='New functional isorhamnetin/narcissoside source metadata; legal primary originals and public SI sought without assuming noPMC is terminal'))
out=[]
for q in plan:
 r=s.request(q['url'],q['role'],'New E01 source public primary/repository/SI path; no login/access-control bypass',phase='fresh',route=q['route'],http_method=q['method'],request_body=json.dumps(q['body']).encode() if q.get('body') else None)
 out.append(r);s.save_rows('original_execution.jsonl',out)
print(json.dumps([{'route':r['route'],'status':r['status_code'],'bytes':r['bytes'],'error':r['error']} for r in out],ensure_ascii=False))
