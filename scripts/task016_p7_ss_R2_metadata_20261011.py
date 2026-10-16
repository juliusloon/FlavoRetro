"""A second *new* SS-O2-specific bibliographic metadata query round.
Two legitimate endpoints Crossref and EuropePMC; this is NOT a full three-route
saturation certificate and must not be counted as chemistry or holdout targets.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,urllib.parse,urllib.request,urllib.error,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_SS_targeted_metadata_R2_20261011'
RAWDIR=Path('data/raw/task016-p7/prospective_G6_SS_targeted_metadata_R2_20261011')
Q=[
 ('EuropePMC','TITLE_ABS:(flavonol AND sophoroside AND glycosyltransferase)'),
 ('EuropePMC','TITLE_ABS:(flavonol AND "2-O-glucosyltransferase")'),
 ('EuropePMC','TITLE_ABS:(flavonol AND "2-glucosyltransferase")'),
 ('EuropePMC','TITLE_ABS:(flavonol AND "sugar-sugar" AND glycosyltransferase)'),
 ('Crossref','flavonol glycoside 2-O-glucosyltransferase 2024 biosynthesis'),
 ('Crossref','flavonol sophoroside UDP-glycosyltransferase flavonoid 2023 2025')]
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def jput(p,x):
 if (ROOT/p).exists():raise RuntimeError('immutable file exists')
 write(T,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
 if (ROOT/O).exists() or (ROOT/RAWDIR).exists():raise RuntimeError('already')
 qs=[]
 for route,q in Q:
  uri=('https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':q,'format':'json','pageSize':20})
    if route=='EuropePMC' else 'https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':15,'select':'DOI,title,container-title,published,type'}))
  qs.append({'route':route,'query':q,'url':uri,'max_requests':1,'science_read':False,'max_return':20})
 plan={'task':T,'at':now(),'source':'SS-E02','frozen_G4_sha':sha((ROOT/B/'SS/E02/stages/G4_SCOPE_FREEZE.json').read_bytes()),
   'prior_metadata_round_sha':sha((ROOT/B/'prospective_G6_round_20261011_v1/G5_metadata_executed.json').read_bytes()),
   'source_meta_only':True,'allowed_new_HTTP':6,'read_science_body':False,
   'no_name_based_graph_inference':True,'do_not_count_as_complete_discovery_round':True,
   'searches':qs,'scope_family':'SS','G6_not_yet_qualified':True}
 pre=O/'query_plan.json';jput(pre,plan)
 event(T,'SS_R2_metadata_query_pre_frozen',sha256=sha((ROOT/pre).read_bytes()),queries=6)
 raw=[];hits=[]
 for i,q in enumerate(qs,1):
  payload=b'';code=None;error=None;start=now()
  try:
   req=urllib.request.Request(q['url'],headers={'User-Agent':'FlavoRetro-P7-G5-SS-origin-research/0.1','Accept':'application/json'})
   with urllib.request.urlopen(req,timeout=17) as f:code=f.status;payload=f.read(500000)
  except urllib.error.HTTPError as e:
   code=e.code;payload=e.read(500000);error='HTTP_'+str(e.code)
  except Exception as e:error=type(e).__name__+':'+str(e)[:170]
  ptr=RAWDIR/f'{i:02d}.json';p=ROOT/ptr
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(payload)
  event(T,'write_binary',path=str(ptr),sha256=sha(payload),bytes=len(payload),role='SS_R2_source_metadata')
  event(T,'source_http',url=q['url'],started_at=start,finished_at=now(),path=str(ptr),sha256=sha(payload),
     bytes=len(payload),kind='metadata',role=q['route'],phase='SS-E02_G5_R2',
     status_code=code,error=error,batch_id='P7-SS-R2-20261011',family='SS')
  count=0
  if code==200:
   try:
    data=json.loads(payload)
    rows=(data.get('resultList',{}).get('result',[]) if q['route']=='EuropePMC' else data.get('message',{}).get('items',[]))
    for x in rows:
     doc={'DOI':x.get('doi') if q['route']=='EuropePMC' else x.get('DOI'),
      'PMCID':x.get('pmcid') if q['route']=='EuropePMC' else None,
      'title':x.get('title') if q['route']=='EuropePMC' else (x.get('title') or [None])[0],
      'year':x.get('pubYear') if q['route']=='EuropePMC' else ((x.get('published') or {}).get('date-parts') or [[None]])[0][0],
      'source_route':q['route'],'raw_path':str(ptr),
      'chemical_content_read':False,'source_identity_qualified':False}
     hits.append(doc);count+=1
   except Exception as e:error='parse:'+type(e).__name__
  raw.append({'no':i,'route':q['route'],'status':code,'error':error,'bytes':len(payload),
       'sha256':sha(payload),'pointer':str(ptr),'result_count':count})
 # Keep original provider order and source pointer, do not give chemical qualification.
 unique={}
 for x in hits:
  k=(x['DOI'] or x['PMCID'] or x['title'] or '').lower()
  if k and k not in unique:unique[k]=x
 result={'task':T,'at':now(),'result_kind':'SS_O2_BIBLIOGRAPHY_ONLY',
  'preregistered_plan_sha256':sha((ROOT/pre).read_bytes()),'HTTP_attempts':len(raw),
  'downloaded_bytes':sum(x['bytes'] for x in raw),'raw_receipts':raw,
  'returned':len(hits),'unique':len(unique),'candidates':list(unique.values()),
  'fresh_reaction_complete':0,'A4_A5_complete':0,'new_closure_group_complete':0,
  'saturation_claim':False,'G6_complete':False}
 output=O/'R2_search_results.json';jput(output,result)
 print(json.dumps({'HTTP':len(raw),'200':sum(x['status']==200 for x in raw),
 'results':len(hits),'unique':len(unique),
 'metadata_titles':[{'doi':x['DOI'],'title':(x['title'] or '')[:110]} for x in list(unique.values())[:16]],
 'result':str(output)},ensure_ascii=False))
if __name__=='__main__':main()
