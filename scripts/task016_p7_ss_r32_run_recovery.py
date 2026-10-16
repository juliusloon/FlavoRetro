from scripts.task016_p7_ss_r32_ACS_expiry_recovery import *
def main():
 for q in load(O/'file_query_plan.json')['queries']:
  r=get(q,O/'file_query_plan.json')
  append(O/'query_execution.jsonl',dict(query_id=q['query_id'],doi=q['doi'],HTTP=r.get('HTTP',1),status=r['status'],HTTP_status=r.get('status_code'),raw_pointer={k:r.get(k) for k in ['path','sha256','bytes']}))
  if r.get('status_code')!=302:
   print(json.dumps(dict(doi=q['doi'],base_status=r.get('status_code'),terminal='no_advertised_redirect')),flush=True);continue
  loc=r['headers'].get('location')
  u=urllib.parse.urlsplit(loc or '')
  if u.scheme!='https' or u.hostname!='s3-eu-west-1.amazonaws.com':raise RuntimeError('UNEXPECTED_REDIRECT')
  child=dict(q,query_id=q['query_id']+'-exact-advertised-redirect',url=loc,parent_attempt_id=r['attempt_id'])
  plan=O/('redirect_'+q['query_id']+'.json')
  put(plan,dict(task=T,at=now(),queries=[child],planned=1,parent_HTTP_ledger_SHA=sha(O/'http_ledger.jsonl'),automatic_redirect=False))
  rr=get(child,plan)
  append(O/'query_execution.jsonl',dict(query_id=child['query_id'],doi=q['doi'],HTTP=rr.get('HTTP',1),status=rr['status'],HTTP_status=rr.get('status_code'),raw_pointer={k:rr.get(k) for k in ['path','sha256','bytes']}))
  print(json.dumps(dict(doi=q['doi'],base_status=r['status_code'],file_status=rr.get('status_code'),bytes=rr.get('bytes'),error=rr.get('error'))),flush=True)
if __name__=='__main__':main()
