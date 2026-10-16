"""Append-only late-exposure projection; original rows and uncertainty retained."""
import json,re
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts.task016_p7_orchestrate import role_manifest
from scripts.task016_p7_source_alias_closure import closure_tokens
T='TASK-016-P7'; B=Path('outputs/task016-p7/v1')
OUT=B/'governance/late_exposure_temporal_adapter_v1'
INDEX=B/'verification-v34-five-source-prior-alias-precheck-recovery-v2/all_located_exposure_row_files_by_original_lane.v4.json'
def ptr(p):return dict(path=str(p),sha256=sha(p))
def explicit_aliases(row):
 tokens=set(row.get('closure_tokens',[]))
 for key in ('authoritative_DOI','source_DOI','DOI'):
  if row.get(key):tokens.add('doi:'+row[key].lower())
 for key in ('source_identifier','identifier','source_PMCID','PMCID','source_id'):
  val=row.get(key)
  if isinstance(val,str) and re.fullmatch(r'PMC[1-9][0-9]*',val):tokens.add('article:'+val)
  elif isinstance(val,str) and val.startswith('10.'):tokens.add('doi:'+val.lower())
 return sorted(tokens)
def main():
 assert not (ROOT/OUT).exists()
 index=load(INDEX)
 historical=index['latest_historical_manual_aggregate_row_files']+[ptr(B/'C/E02/fresh/C-E02-R68-two-historical-PMC-science-v1/scientific_exposure_reads.jsonl')]
 current=index['recommended_current_aggregate_row_files']
 inputs=[INDEX,Path(__file__).relative_to(ROOT)];counts={};lanes={};graphinputs=[]
 for lane,files in [('prior',historical),('current',current)]:
  projected=[]
  for p in files:
   assert sha(p['path'])==p['sha256'];inputs.append(Path(p['path']))
   original=lines(p['path'])
   counts[p['path']]=len(original)
   for n,row in enumerate(original,1):
    tokens=explicit_aliases(row)
    assert tokens
    out=dict(task=T,literal_record=row,original_row_pointer={**p,'line':n},development_exposed=True,closure_tokens=tokens,exposure_type='late_prior_design' if lane=='prior' else 'current_epoch_evaluation',scientific_content_read=row.get('scientific_content_read'),future_fresh_eligible=False,prior_design=lane=='prior',current_epoch_fresh_eligible=False if lane=='prior' else None,source_alias_closure_complete=False,semantic_unknowns_retained=True,adaptation_approval='agent_delegated',human_reviewed=False,adapted_at=now())
    if lane=='prior':
     if 'manual_grabbed_A3' in p['path']:
      assert row['is_development_exposed'] is True and row['G5_prospective_before_read'] is False and row['fresh_current_epoch_qualified'] is False
      out['classification_basis']='Historical known-source owner intake; no prospective G5 before intake read. Original not_reclassified flag remains in literal_record; this explicit projection excludes it without claiming a preG4 timestamp.'
     elif 'manual_grabbed_R3' in p['path']:
      assert row['exposure_class']=='historical_previously_known_and_current_turn_scientific_summary_read' and row['fresh_candidate_eligible'] is False
      out['classification_basis']='Original historical_previously_known exposure class; first-page read preceded local precontract.'
     else:
      assert row['exposure_type']=='historical_development_exposure' and row['prior_design'] is True
      out['classification_basis']='Original R68 historical type; historical_development_exposure mapped to supported late-prior type without changing temporal meaning.'
    else:
     out['classification_basis']='Own post-G5 current evaluation; no blanket retroactive prior/design exclusion.'
     if 'permanent_graph_exposure' in p['path']:
      assert row['known_reaction_leakage_with_frozen_C_build'] is True
      graph=Path(row['A4_path']);a6=Path(row['A6_path']);assert sha(graph)==row['A4_SHA'] and sha(a6)==row['A6_SHA'];g=load(graph)
      for key in ('acceptor_smiles','donor_smiles','product_smiles','reference_precursors','reaction_id','site'):out[key]=g[key]
      out.update(known_reaction_leakage=True,accepted_as_fresh_holdout=False,build_exact_reaction_id=row['build_exact_reaction_id'],graph_evidence=[ptr(graph),ptr(a6)])
      out['closure_tokens']=sorted(set(tokens)|closure_tokens(out));graphinputs.extend([graph,a6])
     else:
      assert row.get('exposure_type')=='current_epoch_evaluation' or row.get('source_science_read_after_G5_stage') is True
    projected.append(out)
  path=OUT/(lane+'_exposure_rows.jsonl')
  write(T,str(path),''.join(json.dumps(x,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for x in projected));lanes[lane]=ptr(path)
  assert len(projected)==sum(counts[p['path']] for p in files)
 manifest=dict(task=T,approval_type='agent_delegated',human_reviewed=False,at=now(),origin_index=ptr(INDEX),origin_files=historical+current,input_row_counts=counts,prior_exposure=lanes['prior'],current_evaluation=lanes['current'],prior_rows=sum(counts[p['path']] for p in historical),current_rows=sum(counts[p['path']] for p in current),unknown_semantics_remain=True,all_project_exposure_coverage_complete=False,actual_G7_consumption=False,current_evaluation_not_supplied_to_v3_v4_late_prior_field=True,distinct_sources_or_reactions_not_inferred_from_row_counts=True,scientific_new_sources_read=0,HTTP=0,MCTS=0)
 put(OUT/'temporal_adapter_manifest.json',manifest)
 inputs+=graphinputs;outputs=[Path(x['path']) for x in lanes.values()]+[OUT/'temporal_adapter_manifest.json']
 role=role_manifest('A0','C-SS-E02',sorted(set(inputs)),outputs,dict(processed=manifest['prior_rows']+manifest['current_rows'],passed=manifest['prior_rows']+manifest['current_rows'],rejected=0,pending=0),pointers=[ptr(INDEX)],read_holdout=False,read_model_outcome=False)
 role['scope']='Schema/time-lane projection only; unknown alias/source/reaction closure is not cleared.'
 put(OUT/'role_A0_manifest.json',role)
 print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__':main()
