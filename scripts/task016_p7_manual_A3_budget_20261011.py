"""Reconcile real manual A3 Crossref physical requests into P7 shared source_http accounting.
Original request timestamps and raw bytes remain unchanged. R2 start time was not logged;
therefore started_at stays null and is NOT invented from the preregistration timestamp.
"""
import json,sys,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';D=Path('outputs/task016-p7/v1')
L=D/'manual_grabbed_A3_20261011/physical_HTTP_ledger.json'
R=D/'manual_grabbed_A3_R2_20261011/A3_corrected_11.json'
P=D/'manual_grabbed_A3_R2_20261011/precontract.json'
O=D/'manual_grabbed_A3_reconciled_20261011'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def main():
 legacy=read(L)['records'];fix=read(R);plan=read(P)
 if len(legacy)!=12 or fix['HTTP']!=1:raise RuntimeError('bad event count')
 previous=[]
 for line in (ROOT/'operations/events.jsonl').read_text().splitlines():
  try:x=json.loads(line)
  except:continue
  if x.get('action')=='source_http' and x.get('batch_id')=='P7-OWNER-A3-20261011':previous.append(x)
 if previous:raise RuntimeError('manual A3 source_http budget already recorded; no duplicate')
 recs=[]
 for x in legacy:
  raw=x['raw']
  if sha(raw['path'])!=raw['sha256']:raise RuntimeError('raw drift')
  rec={'url':x['url'],'started_at':x['at_start'],'finished_at':x['at_end'],
   'path':raw['path'],'sha256':raw['sha256'],'bytes':x['bytes'],
   'kind':'metadata','role':'crossref_A3','phase':'owner_manual_identity','status_code':x['status'],
   'error':x['error'],'family': 'root','batch_id':'P7-OWNER-A3-20261011',
   'source_no':x['source_no'],'log_entry_is_later_than_actual_HTTP':True}
  recs.append(rec)
 raw=fix['raw_pointer']
 if sha(raw['path'])!=raw['sha256']:raise RuntimeError('r2 raw drift')
 recs.append({'url':plan['query'],'started_at':None,'finished_at':fix['at'],
   'path':raw['path'],'sha256':raw['sha256'],'bytes':fix['bytes'],'kind':'metadata',
   'role':'crossref_A3','phase':'owner_manual_identity','status_code':fix['status'],
   'error':fix['error'],'family':'root','batch_id':'P7-OWNER-A3-20261011','source_no':'11',
   'started_at_not_captured_in_original_execution':True,'preregistered_at':plan['at'],
   'log_entry_is_later_than_actual_HTTP':True})
 if len(recs)!=13 or sum(r['bytes'] for r in recs)!=154257:raise RuntimeError('budget conservation')
 for r in recs: event(T,'source_http',**r)
 o={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'batch_id':'P7-OWNER-A3-20261011',
   'source_original_HTTP_accounted':True,'new_HTTP_records':13,'new_bytes':sum(r['bytes'] for r in recs),
   'last_R2_unknown_started_at_explicit':True,'v1_HTTP404_preserved':True,'inputs_sha':{str(k):sha(k) for k in [L,R,P]},
   'family':'root','source_chemistry_qualified':False,'fresh_C':0,'fresh_SS':0}
 out=O/'physical_source_http_reconciliation_receipt.json'
 if (ROOT/out).exists():raise RuntimeError('receipt already exists')
 write(T,str(out),json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'events_appended':len(recs),'bytes':o['new_bytes'],'receipt':str(out),'started_at_null_R2':True}))
if __name__=='__main__':main()
