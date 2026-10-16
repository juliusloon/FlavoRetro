"""Owner manual PDF A3 cross-reference, raw-only immutable DOI metadata intake.
This is publication-identity verification, NOT reaction G6, graph or fresh admission.
"""
import hashlib,json,re,sys,datetime,urllib.request,urllib.error,urllib.parse,time,html,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7'; ROOTOUT=Path('outputs/task016-p7/v1/manual_grabbed_A3_20261011')
RAWDIR=Path('data/raw/task016-p7/manual_grabbed_20261011/crossref_a3')
M=Path('outputs/task016-p7/v1/manual_grabbed_intake_20261011/custody_manifest.json')
DOIS={'01':'10.1111/tpj.70932','02':'10.1021/acs.jafc.5c06227','03':'10.1021/acs.jafc.4c03824',
'04':'10.1021/acs.jafc.4c00488','05':'10.1111/tpj.16898','06':'10.1039/c5ob01926e',
'07':'10.1039/c0ob00011f','08':'10.1039/c4cc00536h','09':'10.1002/bit.26491',
'10':'10.1002/cbic.70486','11':'10.1073/pnas.202012745','12':'10.1074/jbc.M109.009258'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def put(rel,bs):
 p=ROOT/rel
 if p.exists():raise RuntimeError('IMMUTABLE_DESTINATION_EXISTS '+str(p))
 p.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(bs,str):write(T,str(rel),bs)
 else:
  p.write_bytes(bs);event(T,'write_binary',path=str(rel),before=None,after=sha(bs),bytes=len(bs),source='public Crossref metadata')
 return {'path':str(rel),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
def jput(rel,obj):return put(rel,json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def run():
 inv=json.loads((ROOT/M).read_text())
 outdir=ROOT/ROOTOUT
 if outdir.exists() or (ROOT/RAWDIR).exists():raise RuntimeError('IMMUTABLE_BATCH_EXISTS')
 sources={}
 for no,doi in DOIS.items():
  rows=[x for x in inv['source_files'] if x['number']==no and x['role']==('supporting_pdf' if no=='10' else 'main_article_pdf')]
  if len(rows)!=1:raise RuntimeError('missing/ambiguous '+no)
  sources[no]=rows[0]
 plan={'task':T,'at':now(),'agent_role':'A3_publication_identity',
 'approval_type':'owner_supplied_originals_in_P7','purpose':'official_crossref_DOI_identity_only_not_new_chemical_science',
 'input_manifest':{'path':str(M),'sha256':sha((ROOT/M).read_bytes())},
 'G4_current_sha':inv['G4_current_sha'],'source_state':'all_01_12_development_exposed_not_fresh',
 'scientific_body_read_now':False,'read_model_outcome':False,
 'no_auto_link_to_new_holdout':True,'HTTP_max':12,'retries':0,'timeout_seconds':14,
 'metadata_provider':'https://api.crossref.org/works/{DOI}','query_plan':[
 {'source_no':n,'doi':doi,'endpoint':'https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''),
  'max_calls':1,'raw_input_sha':sources[n]['sha256']} for n,doi in DOIS.items()]}
 p=jput(ROOTOUT/'precontract.json',plan)
 ledger=[];result=[]
 for q in plan['query_plan']:
  n=q['source_no'];uri=q['endpoint'];beg=now();raw=b'';status=None;err=None;media=None
  try:
   req=urllib.request.Request(uri,headers={'User-Agent':'FlavoRetro-A3-P7-academic-provenance-check/0.1','Accept':'application/json'})
   with urllib.request.urlopen(req,timeout=14) as resp:
    status=resp.status;media=resp.headers.get('Content-Type');raw=resp.read(2500001)
    if len(raw)>2500000:raise RuntimeError('per_request_raw_cap_exceeded')
  except urllib.error.HTTPError as e:
   status=e.code;raw=e.read(2500001);err='HTTPError_'+str(e.code)
  except Exception as e:err=type(e).__name__+':'+str(e)[:200]
  physical={'source_no':n,'doi':q['doi'],'url':uri,'at_start':beg,'at_end':now(),'status':status,
            'bytes':len(raw),'error':err,'raw_sha256':sha(raw) if raw else None}
  if raw:physical['raw']=put(RAWDIR/f'{n}.crossref.raw.json',raw)
  ledger.append(physical)
  parsed=None
  if status==200 and raw:
   try:
    m=json.loads(raw)['message']
    dates=(m.get('published-print') or m.get('published-online') or m.get('published') or m.get('issued') or {}).get('date-parts') or []
    parsed={'DOI':m.get('DOI'),'title':m.get('title',[None])[0] if m.get('title') else None,
     'journal':m.get('container-title',[None])[0] if m.get('container-title') else None,
     'year':dates[0][0] if dates else None,'volume':m.get('volume'),'issue':m.get('issue'),
     'page':m.get('page'),'article_number':m.get('article-number'),'publisher':m.get('publisher'),
     'type':m.get('type'),'PMCID':None,'PMID':None,'raw_crossref':physical['raw']}
   except Exception as e:err='parse:'+type(e).__name__
  result.append({'source_no':n,'expected_DOI':q['doi'],'manual_original_sha256':sources[n]['sha256'],
     'metadata':parsed,'identity_metadata_acquired':bool(parsed),'parse_issue':err,
     'publication_identity_full_A3_decision':'pending_front_imprint_comparison',
     'source_chemistry':'not_adjudicated','fresh_eligible':False})
  event(T,'A3_external_metadata_request',source_no=n,endpoint=uri,status=status,bytes=len(raw),raw_sha=sha(raw) if raw else None)
 # All 12 planned requests are complete/failed exactly once; append total ledger, no external unverifiable calls.
 led=jput(ROOTOUT/'physical_HTTP_ledger.json',{'task':T,'at':now(),'planned':12,'attempted':len(ledger),
    'bytes':sum(x['bytes'] for x in ledger),'HTTP':len(ledger),'raw_metadata_only':True,
    'local_owner_PDF_count':12,'records':ledger})
 res=jput(ROOTOUT/'A3_raw_authoritative_metadata.json',{'task':T,'at':now(),'plan':p,'ledger':led,'sources':result,
   'metadata_identity_not_chemistry':True,'all_heldout_fresh_false':True})
 print(json.dumps({'planned':12,'attempted':len(ledger),'http_200':sum(x['status']==200 for x in ledger),
  'raw_bytes':sum(x['bytes'] for x in ledger),'metadata_usable':sum(x['metadata'] is not None for x in result),
  'ledger':str(led['path']),'results':str(res['path'])},ensure_ascii=False))
if __name__=='__main__':run()
