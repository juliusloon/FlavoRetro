"""TASK-016-P7 owner batch formal G5 documentary source freeze (NOT fresh admission).
All 16 historical originals have already been read/reviewed; no retroactive prospective read claims.
"""
from pathlib import Path
import datetime,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file,freeze_stage_manifest
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');R=B/'G6_owner_16_historical_source_review_v2'
G1=B/'manual_grabbed_A3_reconciled_20261011/A3_owner_intake_inventory_reconciliation.json'
G2=B/'manual_grabbed_R3_A3_reconciled_20261011/R3_A3_4original_crosscheck_and_G6_documentary_questions.json'
X1=B/'manual_grabbed_A3_reconciled_20261011/permanent_manual_science_exposure_v1.jsonl'
X2=B/'manual_grabbed_R3_A3_reconciled_20261011/R3_4original_permanent_exposure.jsonl'
H=B/'verification-v32-pending-original-source-inventory/named_pending_original_inventory.json'
LEG=B/'epoch_ledger.jsonl'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def put(path,data):
 if (ROOT/path).exists(): raise RuntimeError('immutability '+str(path))
 write(T,str(path),json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def main():
 if (ROOT/R).exists():raise RuntimeError('Batch version already exists')
 old=json.loads((ROOT/G1).read_text()); new=json.loads((ROOT/G2).read_text()); inv=json.loads((ROOT/H).read_text())
 assert len(old['owner_16_items'])==16 and len(new['R3_13_16'])==4
 files=[]; map16=[]
 for n in range(1,17):
  no=f'{n:02d}'; oldr=next(x for x in old['owner_16_items'] if x['owner_number']==no)
  row=next((x for x in new['R3_13_16'] if x['number']==no),None) if n>=13 else None
  path=row['file'] if row else oldr['file']
  digest=row['file_sha256'] if row else oldr['file_sha']
  assert sha_file(ROOT/path)==digest
  idx=next(x for x in inv['items'] if x['source_identifier']==oldr['inventory_identifier'])
  assert idx['family']==(row['inventory_family'] if row else oldr['inventory_family'])
  map16.append({'no':no,'family':idx['family'],'v32_identifier':idx['source_identifier'],
    'DOI':row['metadata_DOI'] if row else oldr['metadata_DOI'],
    'source_file':path,'source_sha256':digest,
    'access':'owner_original_available','prior_or_development_exposure':True,
    'prospective_holdout_admitted':False,'A3_pub_identity':'cross_checked' if no!='10' else 'SI_link_pending'})
  files.append(path)
  event(T,'G5_owner_historical_source_binding_rechecked',number=no,original_SHA=digest,family=idx['family'])
 assert len(map16)==16 and len({x['source_sha256'] for x in map16})==16
 for fam in ('C','SS'):
  g4=B/fam/'E02/stages/G4_SCOPE_FREEZE.json'
  verify_stage_chain(ROOT/g4,sha_file(ROOT/g4))
  local=[x for x in map16 if x['family']==fam]
  assert len(local)==8
  out=R/fam
  prior=rows(LEG)
  assert any(x.get('family')==fam for x in prior)
  receipt={'task':T,'at':now(),'agent_role':'A0','family':fam,'epoch_id':fam+'-E02',
    'intent':'historical_owner_originals_G5_documentary_review_only',
    'first_scientific_read_occurred_prior_to_this_G5':True,
    'originals_prospective_fresh':False,'legal_owner_received_originals':8,
    'originals_preserved_by_SHA':True,'G4_stage_sha256':sha_file(ROOT/g4),
    'source_count':8,'source_records':local,'excluded_from_heldout_denominator':8,
    'no_mcts_or_holdout_outcomes_read':True,'scientific_G6_has_not_passed':True,
    'prior_metadata_A3_binding':{str(p):sha_file(ROOT/p) for p in [G1,G2,H,X1,X2]},
    'G5_expected_role':'historical/design intake, not post-scope fresh holdout'};
  p=out/'A0_G5_manual16_historical_precontract.json'
  put(p,receipt)
  files=[p,G1,G2,H,X1,X2,*[x['source_file'] for x in local]]
  stage=out/'stages'
  freeze_stage_manifest(ROOT/stage,'G5_FRESH_HOLDOUT_ACQUIRE',files,g4,
    expected_previous_sha=sha_file(ROOT/g4),family=fam,epoch_id=fam+'-E02')
  s=stage/'G5_FRESH_HOLDOUT_ACQUIRE.json'
  assert verify_stage_chain(ROOT/s,sha_file(ROOT/s))['stage']=='G5_FRESH_HOLDOUT_ACQUIRE'
  event(T,'G5_historical_owner16_precontract_stage_frozen',family=fam,
      G5_sha256=sha_file(ROOT/s),sources=8,fresh_admitted=0)
 print(json.dumps({'historical_bound_originals':16,'families':{'C':8,'SS':8},
  'G5_hist_stage_C':str(R/'C/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'),
  'G5_hist_stage_SS':str(R/'SS/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'),'fresh':0},ensure_ascii=False))
if __name__=='__main__':main()
