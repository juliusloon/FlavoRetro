"""Execute preregistered PubChem original authority graph requests preserving raw bytes and errors."""
import hashlib,json,datetime,time,urllib.request,urllib.error,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
O=B/'G6_three_decisions_20261012_v1'
RAW=Path('data/raw/task016-p7/G6_three_decisions_20261012_PubChem_authority')
PRE=O/'C_PMC13564134_authoritative_graph_query_precontract.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 p=json.loads((ROOT/PRE).read_text());assert len(p['queries'])==6
 if (ROOT/RAW).exists() or (ROOT/O/'C_PubChem_raw_HTTP_receipts.json').exists():raise RuntimeError('already acquired')
 records=[]
 for i,q in enumerate(p['queries'],1):
  start=now();payload=b'';status=None;error=None
  try:
   req=urllib.request.Request(q['url'],headers={'User-Agent':'FlavoRetro-P7-source-structure-audit/1.0','Accept':'application/json'})
   with urllib.request.urlopen(req,timeout=22) as h:
    status=h.status
    payload=h.read(q['max_bytes']+1)
    if len(payload)>q['max_bytes']:error='max_response_bytes_exceeded';payload=payload[:q['max_bytes']]
  except urllib.error.HTTPError as e:status=e.code;error='HTTP_'+str(e.code);payload=e.read(q['max_bytes']+1)[:q['max_bytes']]
  except Exception as e:error=type(e).__name__+':'+str(e)[:150]
  r=RAW/f'{i:02d}_{q["name"].replace("-","_")}_{q["route"][-10:]}.json'
  dest=ROOT/r;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(payload);dest.chmod(0o444)
  event(T,'write_binary',path=str(r),bytes=len(payload),sha256=sha(payload),raw_immutable=True)
  event(T,'source_http',url=q['url'],started_at=start,finished_at=now(),path=str(r),
    sha256=sha(payload),bytes=len(payload),kind='chemical_authority_structure',
    role=q['route'],phase='G6_PMC13564134_full_source_graph',
    status_code=status,error=error,batch_id='P7-G6-20261012-PubChem-6',family='C')
  v={'number':i,'name':q['name'],'route':q['route'],'source_url':q['url'],
     'started_at':start,'ended_at':now(),'status':status,'error':error,
     'bytes':len(payload),'path':str(r),'sha256':sha(payload)}
  if status==200 and not error:
   try:
    obj=json.loads(payload)
    v['CID_property']=(obj.get('PropertyTable') or {}).get('Properties',[{}])[0].get('CID')
    v['CID_record']=(obj.get('PC_Compounds') or [{}])[0].get('id',{}).get('id',{}).get('cid')
    v['parseable_json']=True
   except Exception as e:v['parseable_json']=False;v['parse_error']=str(e)[:70]
  records.append(v)
  time.sleep(0.35)
 out={'task':T,'at':now(),'precontract_sha256':sha((ROOT/PRE).read_bytes()),
  'executed':len(records),'total_bytes':sum(x['bytes'] for x in records),
  'success_HTTP200':sum(x['status']==200 for x in records),'records':records,
  'user_original_PMC_still_immutable':True,'did_not_claim_any_fresh':True}
 filepath=O/'C_PubChem_raw_HTTP_receipts.json'
 write(T,str(filepath),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'HTTP':len(records),'HTTP200':out['success_HTTP200'],'bytes':out['total_bytes'],
  'by_request':[(x['name'],x['status'],x.get('CID_property'),x.get('CID_record'),x['error']) for x in records]},ensure_ascii=False))
if __name__=='__main__':main()
