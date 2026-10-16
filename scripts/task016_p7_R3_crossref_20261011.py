"""Owner 13-16 original 4 DOI Crossref authoritative metadata fetch; PDF A3 identity only."""
from pathlib import Path
import datetime,hashlib,json,re,sys,urllib.request,urllib.parse,urllib.error
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
TASK='TASK-016-P7';OUT=Path('outputs/task016-p7/v1/manual_grabbed_R3_A3_20261011')
RAWDIR=Path('data/raw/task016-p7/manual_grabbed_20261011/R3_13_16_crossref')
INPUT=Path('outputs/task016-p7/v1/manual_grabbed_R3_20261011/R3_custody_receipt.json')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(name,v):
 rel=OUT/name
 if (ROOT/rel).exists():raise RuntimeError('IMMUTABLE_EXISTS')
 write(TASK,str(rel),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 return {'path':str(rel),'sha256':sha((ROOT/rel).read_bytes())}
def main():
 if (ROOT/OUT).exists() or (ROOT/RAWDIR).exists():raise RuntimeError('batch exists')
 inv=json.loads((ROOT/INPUT).read_text())
 assert len(inv['rows'])==4 and inv['sha256_matches_all']
 plan={'task':TASK,'at':now(),'source_sha256':sha((ROOT/INPUT).read_bytes()),'intent':'A3 DOI identity metadata only not chemical',
 'prior_first_pages_read_before_R3_contract':True,'already_design_exposed':True,'read_model_metrics':False,
 'source_fresh_admitted':0,'queries':[{'no':r['no'],'doi':r['requested_DOI'],
   'url':'https://api.crossref.org/works/'+urllib.parse.quote(r['requested_DOI'],safe=''),
   'max_calls':1,'timeout_s':14,'max_downloaded_bytes':2500000,
   'local_original_sha256':r['sha256']} for r in inv['rows']]}
 prereg=dump('A3_query_plan_precontract.json',plan)
 result=[]
 for q in plan['queries']:
  raw=b'';status=None;error=None;type_=None;start=now()
  try:
   request=urllib.request.Request(q['url'],headers={'Accept':'application/json','User-Agent':'FlavoRetro-P7-A3-publication-identity/0.1'})
   with urllib.request.urlopen(request,timeout=q['timeout_s']) as f:
    status=f.status;type_=f.headers.get('Content-Type');raw=f.read(q['max_downloaded_bytes']+1)
    if len(raw)>q['max_downloaded_bytes']: raise RuntimeError('max_downloaded_bytes_exceeded')
  except urllib.error.HTTPError as e:
   status=e.code;raw=e.read(q['max_downloaded_bytes']+1);error='HTTP_'+str(e.code)
  except Exception as e:error=type(e).__name__+':'+str(e)[:140]
  ptr=None
  if raw:
   rel=RAWDIR/f"{q['no']}.crossref.raw.json"
   path=ROOT/rel
   if path.exists():raise RuntimeError('raw exists')
   path.parent.mkdir(parents=True,exist_ok=True)
   path.write_bytes(raw)
   event(TASK,'write_binary',path=str(rel),bytes=len(raw),sha256=sha(raw),permission='unknown_external_metadata')
   ptr={'path':str(rel),'sha256':sha(raw)}
  metadata=None
  if status==200:
   try:
    m=json.loads(raw)['message']
    date_parts=((m.get('published-print') or m.get('published-online') or m.get('published') or m.get('issued') or {}).get('date-parts') or [])
    metadata={'DOI':m.get('DOI'),'title':(m.get('title') or [None])[0],
      'journal':(m.get('container-title') or [None])[0],'publisher':m.get('publisher'),
      'year':date_parts[0][0] if date_parts else None,'volume':m.get('volume'),
      'issue':m.get('issue'),'page':m.get('page'),'article_number':m.get('article-number')}
   except Exception as e:error='metadata_parse_'+str(type(e).__name__)
  receipt={'source_no':q['no'],'request_DOI':q['doi'],'url':q['url'],'started_at':start,'finished_at':now(),
    'status_code':status,'error':error,'bytes':len(raw),'raw':ptr,'metadata':metadata,
    'identity_status':'metadata_only_pending_PDF_imprint_reconciliation'}
  result.append(receipt)
  event(TASK,'source_http',url=q['url'],started_at=start,finished_at=receipt['finished_at'],
    path=ptr['path'] if ptr else str(RAWDIR/f"{q['no']}.error_no_raw"),
    sha256=ptr['sha256'] if ptr else None,bytes=len(raw),status_code=status,error=error,
    kind='metadata',role='crossref_A3',phase='owner_R3_manual_identity',
    batch_id='P7-OWNER-R3-A3-20261011',source_no=q['no'])
 out=dump('A3_http_identity_ledger.json',{'task':TASK,'at':now(),'preregistered':prereg,
    'planned':4,'executed':len(result),'HTTP_count':len(result),
    'bytes':sum(x['bytes'] for x in result),'results':result,
    'science_G6_qualified':False,'fresh_C':0,'fresh_SS':0,'MCTS_new':0,
    'permission_to_redistribute_article_PDFs':'not_asserted'})
 print(json.dumps({'planned':4,'executed':len(result),'Crossref_http_200':sum(x['status_code']==200 for x in result),
  'bytes':sum(x['bytes'] for x in result),'ledger':out['path'],'metadata':[(x['source_no'],x['metadata']['title'] if x['metadata'] else None) for x in result]},ensure_ascii=False))
if __name__=='__main__':main()
