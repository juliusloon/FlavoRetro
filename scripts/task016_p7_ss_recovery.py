"""One root-authorized explicit recovery chain for a public official SI object."""
import json,sys,urllib.request,urllib.error,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,RAW,rows,save,append,now,require_acquisition_phase
from scripts.task016_p7_orchestrate import sha_file
from scripts.operate import event

def totals(folder):
 return [r for p in folder.rglob('http_ledger.jsonl') if 'superseded' not in p.parts for r in rows(p)]
def head():
 require_acquisition_phase("fresh","SS-E01","SS-E01-bank")
 prior=json.loads((OUT/'fresh_public_SI_large_retry_execution.json').read_text());url=prior['url']
 ss=totals(OUT);glob=totals(ROOT/'outputs/task016-p7/v1');remaining_ss=2*1024**3-sum(r['bytes'] for r in ss);remaining_global=8*1024**3-sum(r['bytes'] for r in glob)
 previous=[r for r in ss if r['url']==url]
 if len(previous)!=2 or any(r['error']!='RuntimeError: OBJECT_TOO_LARGE' for r in previous):raise RuntimeError('EXPECTED_TWO_RETAINED_INCOMPLETE_OBJECTS')
 if (OUT/'public_SI_recovery_chain_plan.json').exists():raise RuntimeError('ONE_RECOVERY_CHAIN_ONLY')
 plan=dict(task_id='TASK-016-P7',family='SS',epoch_id='SS-E01',recovery_chain=True,approval_agent_delegated=True,approved_by='root P7 Orchestrator explicit collaboration authorization',approval_reason='Self-imposed helper object caps are not contract hard byte limits; one preregistered explicit recovery chain after two retained failures, inspect official length and stay within SS2GiB/global8GiB',url=url,prior_failed_objects=[dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'],error=r['error']) for r in previous],registered_at=now(),remaining_ss_bytes=remaining_ss,remaining_global_bytes=remaining_global,chain_operations=['HEAD_official_length','GET_stream_complete_with_actual_remaining_hard_budget'],no_access_control_bypass=True)
 save('public_SI_recovery_chain_plan.json',plan)
 qid=f"SS-Q{len(rows(OUT/'query_plan.jsonl'))+1:05d}";append('query_plan.jsonl',dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),query=url,database=url.split('/')[2],scope_id='SS-E01-bank',family='SS',phase='fresh',reason='Explicit authorized recovery-chain HEAD to inspect official length',max_pages=1,max_objects=0,maximum_bytes=0,route='publisher_public_SI_recovery',registered_at=now(),recovery_chain=True,approval_agent_delegated=True,method='HEAD'))
 started=now();status=None;headers={};error=None
 try:
  req=urllib.request.Request(url,method='HEAD',headers={'User-Agent':'FlavoRetro-TASK016P7/1.0 (public scientific research)'})
  with urllib.request.urlopen(req,timeout=40) as res:status=res.status;headers={k:v for k,v in res.headers.items() if k.lower() in {'content-type','etag','last-modified','content-length'}}
 except Exception as e:error=f'{type(e).__name__}: {e}'
 path=RAW/(hashlib.sha256(url.encode()).hexdigest()+'.recovery-chain.HEAD.metadata')
 if path.exists():raise RuntimeError('RAW_IMMUTABLE_PATH_EXISTS')
 path.write_bytes(b'');h=sha_file(path);event('TASK-016-P7','raw_bytes',path=str(path.relative_to(ROOT)),sha256=h,bytes=0,role='metadata',phase='fresh')
 record=dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),url=url,role='metadata',route='publisher_public_SI_recovery',phase='fresh',started_at=started,finished_at=now(),status_code=status,bytes=0,path=str(path.relative_to(ROOT)),sha256=h,headers=headers,error=error,method='HEAD',recovery_chain=True,approval_agent_delegated=True)
 append('http_ledger.jsonl',record);append('query_execution.jsonl',dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),executed_at=now(),status='terminal',status_code=status,error=error,returned_objects=0,metadata_only=True,admitted=0,deferred=0,rejected=0))
 length=next((v for k,v in headers.items() if k.lower()=='content-length'),None)
 save('public_SI_recovery_HEAD.json',dict(record=record,official_content_length=int(length) if length and length.isdigit() else None,remaining_ss_bytes=remaining_ss,remaining_global_bytes=remaining_global,plan_sha256=sha_file(OUT/'public_SI_recovery_chain_plan.json')))
 print(dict(HEAD_status=status,HEAD_error=error,Content_Length=length,remaining_ss_bytes=remaining_ss,remaining_global_bytes=remaining_global))
def get():
 require_acquisition_phase("fresh","SS-E01","SS-E01-bank")
 head=json.loads((OUT/'public_SI_recovery_HEAD.json').read_text());plan=json.loads((OUT/'public_SI_recovery_chain_plan.json').read_text());url=plan['url']
 if head['record']['error'] or head['record']['status_code']!=200:raise RuntimeError('RECOVERY_HEAD_NOT_AUTHORIZED_OR_AVAILABLE')
 ss=totals(OUT);glob=totals(ROOT/'outputs/task016-p7/v1');remaining=min(2*1024**3-sum(r['bytes'] for r in ss),8*1024**3-sum(r['bytes'] for r in glob))-1024*1024
 length=head['official_content_length']
 if length is not None and length>remaining:raise RuntimeError('OFFICIAL_LENGTH_EXCEEDS_APPROVED_HARD_BYTE_BUDGET')
 if len(ss)>=2500 or len(glob)>=8000 or sum(r['role']=='attachment' for r in ss)>=200:raise RuntimeError('RECOVERY_HARD_HTTP_ATTACHMENT_BUDGET')
 if (OUT/'public_SI_recovery_GET_plan.json').exists():raise RuntimeError('RECOVERY_GET_ALREADY_REGISTERED')
 max_bytes=length if length is not None else remaining
 qid=f"SS-Q{len(rows(OUT/'query_plan.jsonl'))+1:05d}";reg=dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),query=url,database=url.split('/')[2],scope_id='SS-E01-bank',family='SS',phase='fresh',reason='One explicit authorized recovery chain streaming GET under actual remaining byte budget',max_pages=1,max_objects=1,maximum_bytes=max_bytes,route='publisher_public_SI_recovery',registered_at=now(),recovery_chain=True,approval_agent_delegated=True,method='GET',chain_plan_sha256=sha_file(OUT/'public_SI_recovery_chain_plan.json'),official_HEAD_sha256=sha_file(OUT/'public_SI_recovery_HEAD.json'))
 save('public_SI_recovery_GET_plan.json',reg);append('query_plan.jsonl',reg)
 path=RAW/(hashlib.sha256(url.encode()).hexdigest()+'.recovery-chain.GET.attachment')
 if path.exists():raise RuntimeError('RAW_IMMUTABLE_PATH_EXISTS')
 started=now();status=None;headers={};error=None;size=0
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'FlavoRetro-TASK016P7/1.0 (public scientific research)'})
  with urllib.request.urlopen(req,timeout=40) as res,path.open('wb') as stream:
   status=res.status;headers={k:v for k,v in res.headers.items() if k.lower() in {'content-type','etag','last-modified','content-length'}}
   while True:
    chunk=res.read(min(1024*1024,max_bytes-size+1))
    if not chunk:break
    stream.write(chunk);size+=len(chunk)
    if size>max_bytes:raise RuntimeError('APPROVED_RECOVERY_BYTE_CAP_EXCEEDED')
  if length is not None and size!=length:raise RuntimeError('OFFICIAL_CONTENT_LENGTH_MISMATCH')
 except Exception as e:error=f'{type(e).__name__}: {e}'
 if not path.exists():path.write_bytes(b'')
 h=sha_file(path);event('TASK-016-P7','raw_bytes',path=str(path.relative_to(ROOT)),sha256=h,bytes=size,role='attachment',phase='fresh')
 record=dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),url=url,role='attachment',route='publisher_public_SI_recovery',phase='fresh',started_at=started,finished_at=now(),status_code=status,bytes=size,path=str(path.relative_to(ROOT)),sha256=h,headers=headers,error=error,method='GET',recovery_chain=True,approval_agent_delegated=True)
 append('http_ledger.jsonl',record);append('query_execution.jsonl',dict(query_id=qid,ledger_namespace=str(OUT.relative_to(ROOT)),executed_at=now(),status='terminal',status_code=status,error=error,returned_objects=1 if status==200 and error is None else 0,metadata_only=False,admitted=0,deferred=1 if status==200 and error is None else 0,rejected=1 if error else 0))
 save('public_SI_recovery_GET.json',dict(record=record,complete=status==200 and error is None,scope_freeze_sha256=sha_file(OUT/'scope_freeze.json'),chain_plan_sha256=sha_file(OUT/'public_SI_recovery_chain_plan.json'),read_model_outcomes=False,evidence_eligible=False))
 print(dict(GET_status=status,GET_error=error,bytes=size,sha256=h,path=str(path.relative_to(ROOT))))
if __name__=='__main__':
 if sys.argv[1]=='head':head()
 elif sys.argv[1]=='get':get()
 else:raise RuntimeError('head/get only')
