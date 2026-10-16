"""Official ACS figshare file retrieval based only on exact resource DOI."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import scripts.task016_p7_ss_sources as s
BASE=s.OUT;s.OUT=BASE/'fresh_narcissoside2025_original'
rr=s.rows(s.OUT/'original_execution.jsonl');search=next(r for r in rr if r['route']=='official_ACS_figshare_public_SI_discovery')
items=json.loads((ROOT/search['path']).read_text());doi='10.1021/acs.jafc.4c12187'
plan=[]
for item in items:
 if item.get('resource_doi')!=doi or not item['url_public_html'].startswith('https://acs.figshare.com/'):raise RuntimeError('SI_RESOURCE_IDENTITY_MISMATCH')
 plan.append(dict(article_id=item['id'],url=item['url_public_api'],resource_doi=item['resource_doi'],si_doi=item['doi'],registered_at=s.now()))
if (s.OUT/'SI_metadata_plan.json').exists():raise RuntimeError('IMMUTABLE_PLAN_EXISTS')
s.save('SI_metadata_plan.json',dict(search_input_path=search['path'],search_input_sha256=search['sha256'],selections=plan));out=[]
for q in plan:
 m=s.request(q['url'],'metadata','Exact-resource-DOI ACS figshare public SI metadata',phase='fresh',route='ACS_figshare_official_SI_metadata');rec=dict(selection=q,metadata=m,files=[])
 if m['status_code']==200 and not m['error']:
  data=json.loads((ROOT/m['path']).read_text())
  if data.get('resource_doi')!=doi:raise RuntimeError('SI_RESOURCE_IDENTITY_MISMATCH')
  files=data.get('files',[])
  rec['SI_identity']=dict(resource_doi=data.get('resource_doi'),doi=data.get('doi'),title=data.get('title'),description=data.get('description'),license=data.get('license'),published_date=data.get('published_date'))
  s.save('SI_files_plan_'+str(q['article_id'])+'.json',dict(metadata_input_path=m['path'],metadata_input_sha256=m['sha256'],registered_at=s.now(),files=files))
  for f in files:
   if not f['download_url'].startswith('https://'):raise RuntimeError('INVALID_OFFICIAL_FILE_URL')
   a=s.request(f['download_url'],'attachment','Official SI file linked by exact DOI ACS figshare metadata; candidate chemistry not independently eligible',phase='fresh',route='ACS_figshare_official_SI_file')
   rec['files'].append(dict(original_name=f['name'],official_size=f.get('size'),official_md5=f.get('supplied_md5') or f.get('computed_md5'),http=a))
 out.append(rec);s.save_rows('SI_execution.jsonl',out)
print(json.dumps([{'id':r['selection']['article_id'],'files':[{'name':f['original_name'],'status':f['http']['status_code'],'bytes':f['http']['bytes']} for f in r['files']]} for r in out],ensure_ascii=False))
