"""Execute P7 preregistered 3-route NEW metadata discovery; no science-body reads.
Preserve every response/error bytes plus source_http events; parse title/DOI/PMCID ONLY.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,time,urllib.request,urllib.error,urllib.parse,random
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
O=B/'prospective_G6_round_20261011_v1';Q=O/'G5_metadata_query_plan.json'
RAW=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1')
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def put(path,obj):
 if (ROOT/path).exists():raise RuntimeError('immutable')
 write(T,str(path),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def get(url,no,route,family):
 start=now();status=None;err=None;data=b'';content=None
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'FlavoRetro-P7-G5-traceable-academic-metadata/1.0','Accept':'application/json'})
  with urllib.request.urlopen(req,timeout=18) as r:
   status=r.status;content=r.headers.get('Content-Type');data=r.read(500001)
   if len(data)>500000:err='byte_cap_exceeded';data=data[:500000]
 except urllib.error.HTTPError as e:
  status=e.code;err='HTTP_'+str(e.code);data=e.read(500001)[:500000]
 except Exception as e:err=type(e).__name__+':'+str(e)[:120]
 ptr=RAW/(f'{no:02d}.json')
 p=ROOT/ptr
 if p.exists():raise RuntimeError('raw already exists')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 event(T,'write_binary',path=str(ptr),sha256=sha(data),bytes=len(data),role='prospective_metadata_raw')
 finish=now()
 event(T,'source_http',url=url,started_at=start,finished_at=finish,path=str(ptr),
       sha256=sha(data),bytes=len(data),kind='metadata',role=route,phase='P7_G5_prospective_science_metadata',
       status_code=status,error=err,batch_id='P7-G5-NEW-SOURCE-20261011',family=family)
 return {'no':no,'route':route,'family':family,'url':url,'at_start':start,'at_end':finish,
         'status':status,'error':err,'bytes':len(data),'sha256':sha(data),'raw_file':str(ptr),'content_type':content},data
def parse(meta,payload):
 if meta['status']!=200 or meta['error']:return [],None
 try:res=json.loads(payload)
 except: return [],None
 route=meta['route'];hits=[];seed=None
 if route=='europepmc_fulltext_index':
  for x in res.get('resultList',{}).get('result',[]):
   hits.append({'title':x.get('title'),'DOI':x.get('doi'),'PMCID':x.get('pmcid'),
      'PMID':x.get('id'),'year':x.get('pubYear'),'isOpenAccess':x.get('isOpenAccess'),'source_route':route})
 if route=='crossref_publisher_DOI_bibliography':
  for x in res.get('message',{}).get('items',[]):
   hits.append({'title':(x.get('title') or [''])[0],'DOI':x.get('DOI'),'PMCID':None,
    'year':((x.get('published') or x.get('issued') or {}).get('date-parts') or [[None]])[0][0],
    'source_route':route})
 if route=='openalex_forward_citation_network':
  if isinstance(res,dict) and 'results' not in res:
   seed=res.get('id')
  for x in res.get('results',[]):
   hits.append({'title':x.get('title'),'DOI':(x.get('doi') or '').removeprefix('https://doi.org/'),
    'PMCID':None,'year':x.get('publication_year'),'source_route':route,'openalex_id':x.get('id')})
 return hits,seed
def main():
 plan=json.loads((ROOT/Q).read_text())
 assert len(plan['queries'])==10 and plan['search_routes']==3
 expected={'C','SS'}
 assert set(x['family'] for x in plan['queries'])==expected
 if (ROOT/O/'G5_metadata_executed.json').exists() or (ROOT/RAW).exists():raise RuntimeError('immutable batch')
 records=[];hits=[];seeds={}
 for n,q in enumerate(plan['queries']):
  receipt,body=get(q['url'],n+1,q['route'],q['family'])
  fetched,seed=parse(receipt,body)
  if seed:seeds[q['family']]=seed
  receipt.update({'returned_records':len(fetched),'parseable_seed':seed,
    'abstracts_read':False,'article_body_read':False})
  records.append(receipt)
  for x in fetched:
   x.update({'family':q['family'],'raw_pointer':receipt['raw_file'],
             'source_qualified':False,'fresh_qualified':False,'chemical_graph_read':False})
   hits.append(x)
 # Same scientific route but cite network, not repeating keyword search.
 for n,f in enumerate(['C','SS'],11):
  seed=seeds.get(f)
  if not seed:continue
  url='https://api.openalex.org/works?'+urllib.parse.urlencode(
   {'filter':'cites:'+seed.split('/')[-1],'per-page':20})
  receipt,body=get(url,n,'openalex_forward_citation_network',f)
  fetched,_=parse(receipt,body)
  receipt.update({'returned_records':len(fetched),'seed_id':seed,'abstracts_read':False,'article_body_read':False})
  records.append(receipt)
  for x in fetched:
   x.update({'family':f,'raw_pointer':receipt['raw_file'],
             'source_qualified':False,'fresh_qualified':False,'chemical_graph_read':False,
             'citation_seed':seed})
   hits.append(x)
 dedup={};duplicates=0
 for i,h in enumerate(hits):
  key=(h['family'],(h.get('DOI') or h.get('PMCID') or 'title:'+str(h.get('title'))).lower().strip())
  if key in dedup:
   duplicates+=1
   dedup[key]['routes']=sorted(set(dedup[key]['routes']+[h['source_route']]))
   continue
  h=dict(h);h['routes']=[h['source_route']];h['metadata_identity_pending']=True
  dedup[key]=h
 physical={'task':T,'at':now(),'plan_sha256':sha((ROOT/Q).read_bytes()),'records':records,
   'HTTP_attempts':len(records),'bytes':sum(r['bytes'] for r in records),
   'failure_count':sum(r['status']!=200 or r['error'] for r in records)}
 put(O/'G5_metadata_HTTP_ledger.json',physical)
 state={'task':T,'at':now(),'routes_executed':['europepmc_fulltext_index',
  'crossref_publisher_DOI_bibliography','openalex_forward_citation_network'],
  'route_mechanisms':'search_index_vs_publisher_bibliography_vs_forward_citation_chase',
  'returned':len(hits),'deduplicated':len(dedup),'duplicate_rows':duplicates,
  'metadata_only_candidates':list(dedup.values()),'source_identity_pending':len(dedup),
  'new_closure_groups_verified':0,'new_reaction_admitted':0,'fresh_C':0,'fresh_SS':0,
  'A4_A5_independent_chemistry':False,'this_round_is_not_saturation_proof':True,
  'G5_qualified_originals':0,'G6_qualified':0,'scientific_ABE_cells':0,
  'http_receipt_sha256':sha((ROOT/O/'G5_metadata_HTTP_ledger.json').read_bytes())}
 put(O/'G5_metadata_executed.json',state)
 print(json.dumps({'HTTP':len(records),'HTTP200':sum(r['status']==200 for r in records),
 'failures':physical['failure_count'],'bytes':physical['bytes'],
 'return':len(hits),'unique':len(dedup),
 'by_family':{f:sum(x['family']==f for x in dedup.values()) for f in ['C','SS']},
 'openalex_seed':seeds,'output':str(O/'G5_metadata_executed.json')},ensure_ascii=False))
if __name__=='__main__':main()
