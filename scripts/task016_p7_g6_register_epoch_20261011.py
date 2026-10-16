"""Register immutable historical owner G5/G6 stage branch in append-only P7 epoch ledger.
This stage is documentary historical disposition, not a qualified fresh G6 panel.
"""
import datetime,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
R=B/'G6_owner_16_historical_source_review_v2';LEG=B/'epoch_ledger.jsonl'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 raw=(ROOT/LEG).read_text()
 prior=[json.loads(x) for x in raw.splitlines() if x]
 v1=B/'G6_owner_16_historical_source_review_v1'
 if any('owner16_G6' in str(x.get('event_type','')) for x in prior):raise RuntimeError('already registered')
 audit=json.loads((ROOT/R/'A11_original_source_verification.json').read_text())
 assert audit['passed']==177 and audit['failed']==0
 additions=[]
 for fam in ('C','SS'):
  for stage in ('G5_FRESH_HOLDOUT_ACQUIRE','G6_IDENTITY_STRUCTURE_ADMIT'):
   p=R/fam/'stages'/(stage+'.json');sha=sha_file(ROOT/p)
   v=verify_stage_chain(ROOT/p,sha)
   assert v['stage']==stage and v['epoch_id']==fam+'-E02'
   additions.append({'task':T,'at':now(),'epoch_id':fam+'-E02','family':fam,
    'stage':stage,'status':'active',
    'event_type':'owner16_G6_historical_documentary_stage_registered_not_fresh',
    'stage_manifest_path':str(p),'stage_manifest_sha256':sha,
    'source_count':8,'fresh_admitted':0,'G6_full_graph_qualified':0,
    'documentary_G6_closure_batch_finished':stage=='G6_IDENTITY_STRUCTURE_ADMIT',
    'source_exposure_before_batch':True,'holdout_used':False,
    'read_model_outcome':False,'human_reviewed':False,
    'superseded_prior_v1_unregistered':True})
 new=raw+''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in additions)
 if not new.startswith(raw):raise RuntimeError('append-only prefix violation')
 write(T,str(LEG),new)
 event(T,'owner16_G5_G6_epoch_stage_registered',added=4,
  prior_ledger_sha256=None,new_ledger_sha256=sha_file(ROOT/LEG))
 print(json.dumps({'ledger_entries_appended':len(additions),
  'active_historical_G5_G6':4,'fresh_admitted':0,'ledger_sha256':sha_file(ROOT/LEG)},ensure_ascii=False))
if __name__=='__main__':main()
