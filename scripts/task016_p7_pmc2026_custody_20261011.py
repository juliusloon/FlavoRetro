"""Custody only: legal PMC original JATS bytes, G5 stage immutability before any science read."""
from pathlib import Path
import json,hashlib,datetime,sys,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,sha_file
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
PLAN=O/'C_PMC13564134_G5_original_acquisition_precontract.json'
RAW=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
LED=O/'C_PMC13564134_original_HTTP_custody.json'
G5=O/'C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 plan=json.loads((ROOT/PLAN).read_text())
 if (ROOT/RAW).exists() or (ROOT/LED).exists() or (ROOT/G5).exists():raise RuntimeError('immutable original already acquired')
 start=now();response=b'';status=None;err=None
 try:
  req=urllib.request.Request(plan['official_PMC_fullTextXML_URL'],headers={'User-Agent':'FlavoRetro-P7-G5-scientific-original-custody/1.0','Accept':'application/xml'})
  with urllib.request.urlopen(req,timeout=21) as res:
   status=res.status;response=res.read(5000001)
   if len(response)>5000000:err='raw_byte_limit_exceeded';response=response[:5000000]
 except urllib.error.HTTPError as e:
  status=e.code;response=e.read(5000001)[:5000000];err='HTTP_'+str(e.code)
 except Exception as e:err=type(e).__name__+':'+str(e)[:220]
 (ROOT/RAW).parent.mkdir(parents=True,exist_ok=True)
 (ROOT/RAW).write_bytes(response);(ROOT/RAW).chmod(0o444)
 event(T,'write_binary',path=str(RAW),sha256=sha(response),bytes=len(response),source='official PMC original, not chemical content yet')
 event(T,'source_http',url=plan['official_PMC_fullTextXML_URL'],started_at=start,finished_at=now(),
  path=str(RAW),sha256=sha(response),bytes=len(response),kind='article_version',role='official_PMC_JATS',
  phase='C-E02_prospective_G5',status_code=status,error=err,batch_id='P7-C-PMC13564134',family='C')
 rec={'task':T,'at':now(),'source_DOI':plan['source_DOI'],'PMCID':plan['source_PMCID'],
   'HTTP_status':status,'error':err,'bytes':len(response),'original_source_path':str(RAW),
   'raw_sha256':sha(response),'raw_content_not_yet_read':True,'fresh_admission':False,
   'source_identity_validation_pending':True,'G5_scientific_read_boundary_to_be_frozen':status==200 and err is None}
 write(T,str(LED),json.dumps(rec,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
 if status!=200 or err:
  print(json.dumps({'G5_original_available':False,'HTTP_status':status,'error':err,'bytes':len(response)}))
  return
 g4=B/'C/E02/stages/G4_SCOPE_FREEZE.json'
 freeze_stage_manifest(ROOT/G5.parent,'G5_FRESH_HOLDOUT_ACQUIRE',
  [PLAN,LED,RAW,O/'G5_metadata_query_plan.json',O/'G5_metadata_executed.json',
   B/'C/E02/scope_manifest.json'],g4,
  expected_previous_sha=sha_file(ROOT/g4),family='C',epoch_id='C-E02')
 assert verify_stage_chain(ROOT/G5,sha_file(ROOT/G5))['stage']=='G5_FRESH_HOLDOUT_ACQUIRE'
 event(T,'PMC13564134_original_G5_frozen_before_science_read',G5_sha256=sha_file(ROOT/G5),original_sha=sha(response))
 print(json.dumps({'G5_original_available':True,'status':status,'bytes':len(response),
  'original_sha256':sha(response),'G5_SHA':sha_file(ROOT/G5)},ensure_ascii=False))
if __name__=='__main__':main()
