"""Immutable permanent development exposure supplement for owner PDFs.
Never mutate the frozen P1-P6 historical exposure ledger or stage manifests.
"""
import json,sys,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';D=Path('outputs/task016-p7/v1')
V=D/'manual_grabbed_A3_reconciled_20261011/A3_owner_intake_inventory_reconciliation.json'
P=D/'manual_grabbed_A3_reconciled_20261011/permanent_manual_science_exposure_v1.jsonl'
Q=D/'manual_grabbed_A3_reconciled_20261011/permanent_exposure_receipt_v1.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 if (ROOT/P).exists() or (ROOT/Q).exists():raise RuntimeError('append immutable batch version')
 v=json.loads((ROOT/V).read_text())
 arr=[x for x in v['owner_16_items'] if x['owner_provided_original']]
 if len(arr)!=12:raise RuntimeError('expected twelve provenance rows')
 b=[]
 at=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for x in arr:
  no=x['owner_number']
  b.append({'task':T,'event_type':'owner_supplied_original_manual_documentary_scientific_read',
     'registered_at':at,'owner_number':no,'source_identifier':x['inventory_identifier'],
     'authoritative_DOI':x['metadata_DOI'],'source_original_SHA':x['file_sha'],'source_original_file':x['file'],
     'family':x['inventory_family'],'source_id_aliases_not_fully_closed':True,
     'prior_design_or_historical_exposure':'not_reclassified_by_this_supplement',
     'P7_epoch':'C-E02' if x['inventory_family']=='C' else 'SS-E02',
     'is_development_exposed':True,'fresh_current_epoch_qualified':False,
     'future_epoch_fresh_reuse_allowed':False,'source_qualification':'documentary_scope_only',
     'scientific_content_read':True,'scientific_content_read_started_before_this_exposure_supplement':True,
     'read_holdout_for_model_metrics':False,'read_model_outcome':False,'human_reviewed':False,
     'G5_prospective_before_read':False,'full_A4_A5_structure':False,
     'G6_full_reaction_qualified':False,
     'G7_writer_consumption':'not_yet_bound_must_be_required_by_future_G7',
     'binding_A3_result_SHA':sha(V)})
 write(T,str(P),'\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in b)+'\n')
 receipt={'task':T,'at':at,'fixed_denominator':12,'permanent_development_exposure_added':12,
 'source_exposure_sha256':sha(P),'binding_A3_result_SHA':sha(V),
 'do_not_append_to_original_exposure_ledger_immutability':True,
 'future_G7_exposure_gate_integration':'pending_required_before_final_panel',
 'fresh_admitted':0,'scientific_ABE_cells':0}
 write(T,str(Q),json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'owner_manual_science_exposure_supplement_frozen',path=str(P),sha256=sha(P),source_count=12)
 print(json.dumps({'exposure_rows':12,'exposure_sha256':sha(P),'G7_gate_integration':'pending'},ensure_ascii=False))
if __name__=='__main__':main()
