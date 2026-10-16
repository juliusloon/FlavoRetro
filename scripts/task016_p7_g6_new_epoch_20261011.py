"""Register genuinely obtained new C original G5/G6 stages append-only, with explicitly 0 admitted.
Current article science-reading exposure supplement separate; no G7 writer consumption claimed.
"""
import json,datetime
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
D=B/'prospective_G6_round_20261011_v1';E=B/'epoch_ledger.jsonl'
def main():
 orig=(ROOT/E).read_text()
 rows=[json.loads(x) for x in orig.splitlines() if x]
 if any(r.get('event_type')=='C-PMC13564134-new-original-partial-G6' for r in rows):
  raise RuntimeError('already registered')
 added=[]
 for stage in ['G5_FRESH_HOLDOUT_ACQUIRE','G6_IDENTITY_STRUCTURE_ADMIT']:
  p=D/'C-PMC13564134/stages'/f'{stage}.json'
  digest=sha_file(ROOT/p)
  v=verify_stage_chain(ROOT/p,digest)
  assert v['stage']==stage and v['epoch_id']=='C-E02'
  added.append({'task':T,'family':'C','epoch_id':'C-E02','stage':stage,
   'status':'active','event_type':'C-PMC13564134-new-original-partial-G6',
   'stage_manifest_path':str(p),'stage_manifest_sha256':digest,
   'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'source_DOI':'10.1016/j.abiote.2026.100085','source_PMCID':'PMC13564134',
   'source_original_acquired':True,'source_A3_verified':True,'A4_A5_independent_textual_read':True,
   'dual_complete_structural_graphs':False,'name_closure_leakage_free':False,
   'full_G6_scientific_admission':0,'fresh_admitted':0,'read_model_outcome':False,
   'human_reviewed':False})
 write(T,str(E),orig+''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in added))
 event(T,'C_PM13564134_P7_epoch_two_stages_append_only',rows=2,
   epoch_ledger_sha256=sha_file(ROOT/E),fresh=0)
 print(json.dumps({'G5_G6_new_original_epoch_stage_rows':2,
  'source_original_PMC':'PMC13564134','fresh_admitted':0,'epoch_sha':sha_file(ROOT/E)}))
if __name__=='__main__':main()
