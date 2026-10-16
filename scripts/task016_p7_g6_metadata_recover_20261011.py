"""Offline recovery of the completed 10 preregistered G5 HTTP requests.
Execution failed AFTER HTTP on purely Python None-sum; do NOT repeat URLs or erase HTTP 429.
This rebuilds metadata-only outputs from original raw bytes and logged exact requests.
"""
import json,hashlib,sys,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from scripts.operate import write,event
from scripts import task016_p7_g6_metadata_execute_20261011 as mod
T='TASK-016-P7';O=Path('outputs/task016-p7/v1/prospective_G6_round_20261011_v1')
RAW=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 plan=json.loads((ROOT/O/'G5_metadata_query_plan.json').read_text())
 if (ROOT/O/'G5_metadata_executed.json').exists():raise RuntimeError('already finalized')
 calls=[]
 for l in (ROOT/'operations/events.jsonl').read_text().splitlines():
  try:e=json.loads(l)
  except:continue
  if e.get('action')=='source_http' and e.get('batch_id')=='P7-G5-NEW-SOURCE-20261011':
   calls.append(e)
 if len(calls)!=10:raise RuntimeError(f'expected 10 actual calls, got {len(calls)}')
 records=[];hits=[];seed={}
 for n,(e,q) in enumerate(zip(calls,plan['queries']),1):
  if e['url']!=q['url']:raise RuntimeError('request order URL drift '+str(n))
  path=RAW/f'{n:02d}.json'
  if e['sha256']!=sha(path) or e['bytes']!=(ROOT/path).stat().st_size:raise RuntimeError('raw drift')
  receipt={'no':n,'route':q['route'],'family':q['family'],'url':e['url'],
   'at_start':e['started_at'],'at_end':e['finished_at'],'status':e['status_code'],
   'error':e['error'],'bytes':e['bytes'],'sha256':e['sha256'],'raw_file':str(path)}
  found,seedid=mod.parse(receipt,(ROOT/path).read_bytes())
  if seedid:seed[q['family']]=seedid
  receipt.update({'returned_records':len(found),'parseable_seed':seedid,'abstracts_read':False,'article_body_read':False})
  records.append(receipt)
  for x in found:
   x.update({'family':q['family'],'raw_pointer':str(path),'source_qualified':False,
             'fresh_qualified':False,'chemical_graph_read':False})
   hits.append(x)
 dedup={};dups=0
 for x in hits:
  k=(x['family'],(x.get('DOI') or x.get('PMCID') or 'title:'+str(x.get('title'))).casefold())
  if k in dedup:
   dups+=1;dedup[k]['routes']=sorted(set(dedup[k]['routes']+[x['source_route']]))
   continue
  x=dict(x);x['routes']=[x['source_route']];x['metadata_identity_pending']=True;dedup[k]=x
 physical={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'plan_sha256':sha(O/'G5_metadata_query_plan.json'),'reconstruction_from_exact_source_http_events':True,
   'original_execution_failed_after_10_HTTP_before_writing_result':True,
   'no_HTTP_retries_in_recovery':True,'records':records,
   'HTTP_attempts':len(records),'bytes':sum(r['bytes'] for r in records),
   'failure_count':sum(bool(r['status']!=200 or r['error']) for r in records)}
 p=O/'G5_metadata_HTTP_ledger.json'
 if (ROOT/p).exists():raise RuntimeError('immutable')
 write(T,str(p),json.dumps(physical,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 out={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'routes_attempted':['europepmc_fulltext_index','crossref_publisher_DOI_bibliography',
                       'openalex_forward_citation_network'],
   'route_openalex':'HTTP429 both seed resolves; forward citation not executed; no 3 route saturation claim',
   'HTTP_failed':2,'returned':len(hits),'deduplicated':len(dedup),'duplicate_rows':dups,
   'metadata_only_candidates':list(dedup.values()),'source_identity_pending':len(dedup),
   'new_closure_groups_verified':0,'fresh_C':0,'fresh_SS':0,
   'A4_A5_independent_chemistry':False,'this_round_is_not_saturation_proof':True,
   'G5_qualified_originals':0,'G6_qualified':0,'scientific_ABE_cells':0,
   'http_receipt_sha256':sha(p)}
 target=O/'G5_metadata_executed.json'
 write(T,str(target),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 print(json.dumps({'HTTP_exact':len(records),'HTTP_200':8,'HTTP_429':2,
   'bytes':physical['bytes'],'returned':len(hits),'unique':len(dedup),
   'byfamily':{f:sum(v['family']==f for v in dedup.values()) for f in ['C','SS']},
   'out':str(target)},ensure_ascii=False))
if __name__=='__main__':main()
