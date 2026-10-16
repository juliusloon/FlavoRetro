"""A6 G6 reconciliation and historical target-name closure for new official PMC13564134.
Never substitute source-text agreement for independent atom-graph reconciliation.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,freeze_stage_manifest
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
FILES={
 'A3':O/'C_PMC13564134_A3_original_front_and_exposure.json',
 'A4':O/'C_PMC13564134_A4_independent_source_read.json',
 'A5':O/'C_PMC13564134_A5_independent_source_read.json',
 'A0':O/'C_PMC13564134_A0_dual_science_read_precontract.json'}
G5=O/'C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
OUT=O/'C_PMC13564134_A6_source_name_closure_and_graph_gaps.json'
def read(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/OUT).exists():raise RuntimeError('immutable')
 verify_stage_chain(ROOT/G5,sha_file(ROOT/G5))
 a3=read(FILES['A3']);a=read(FILES['A4']);b=read(FILES['A5']);p=read(FILES['A0'])
 assert a3['identity_verified'] and a3['official_DOI']==b['source_DOI']==a['source_DOI']
 assert a['agent_role']=='A4' and b['agent_role']=='A5' and a['extraction_id']!=b['extraction_id']
 assert a['read_other_extractor_output'] is False and b['read_other_extractor_output'] is False
 assert a['source_sha256']==b['source_sha256']==p['source_SHA']
 assert a['input_manifest_sha']==b['input_manifest_sha']==sha_file(ROOT/FILES['A0'])
 # Name exposure from original old history exact raw rows; do NOT conflate unmatched DOI with source novelty.
 history=B/'governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl'
 cited=[]; doi_alias=[]
 for lineno,line in enumerate((ROOT/history).read_text().splitlines(),1):
  x=json.loads(line);tokens=[v.lower() for v in x.get('closure_tokens',[])]
  if 'partial-target-name:isoorientin' in tokens:
   cited.append({'line':lineno,'record_type':x.get('exposure_type'),
     'original_file':x.get('origin_file'),
     'source_tokens':sorted(t for t in tokens if t.startswith('doi:'))[:3]})
  if any(t=='doi:10.1016/j.abiote.2026.100085' for t in tokens):doi_alias.append(lineno)
 assert cited and not doi_alias
 missing=sorted(set(a['missing']+b['outstanding']))
 out={'task':T,'at':datetime.now(timezone.utc).isoformat(),'epoch':'C-E02',
  'agent_role':'A6','human_reviewed':False,'approval':'agent_delegated',
  'A3_verified_DOI':a3['official_DOI'],'A4_output_SHA':sha_file(ROOT/FILES['A4']),
  'A5_output_SHA':sha_file(ROOT/FILES['A5']),'source_original_SHA':p['source_SHA'],
  'A4_A5_independent_processes_read_same_SHA':True,'A4_A5_qualitative_claim_agreement':True,
  'A4_A5_full_molecule_graph_reconciliation':False,
  'structure_complete':False,'reference_precursor_complete':False,
  'source_diagram_atom_bond_original_transcribed':False,
  'reported_candidate':['luteolin','UDP-glucose','isoorientin','C6','GyCGT1'],
  'documented_direct_flavone_C6_step':True,
  'source_article_DOI_exact_in_prior_exposure':False,
  'source_alias_and_same_assay_closure_complete':False,
  'named_target_isoorientin_prior_exposure_rows':cited[:32],
  'prior_named_target_row_count':len(cited),'prior_name_exposure_detected':True,
  'exact_product_graph_match_or_mismatch':'unverifiable_no_source_bound_graphs',
  'reconciliation_unresolved_fields':missing,
  'G6_scope_claim':'direct_C6_source_step_observed_but_graph_and_name_closure_block',
  'source_qualification':'A3_identity_only_full_reaction_deferred',
  'fresh_admitted':False,'full_G6_reaction_admitted':0,'fresh_C':0,'fresh_SS':0,
  'G7_panel_allowed':False,'G8_preflight_allowed':False,'no_model_outcomes_read':True,
  'metadata_only_saturation_proven':False,
  'do_not_label_publication_unique_as_reaction_leakage_free':True}
 write(T,str(OUT),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 stage=O/'C-PMC13564134/stages'
 freeze_stage_manifest(ROOT/stage,'G6_IDENTITY_STRUCTURE_ADMIT',
   [*FILES.values(),OUT,history],G5,
   expected_previous_sha=sha_file(ROOT/G5),family='C',epoch_id='C-E02')
 v=stage/'G6_IDENTITY_STRUCTURE_ADMIT.json'
 assert verify_stage_chain(ROOT/v,sha_file(ROOT/v))['stage']=='G6_IDENTITY_STRUCTURE_ADMIT'
 event(T,'P7_C_new_original_G6_A6_closed_ineligible',doi=a3['official_DOI'],
   A4_A5_processes=2,structure_complete=False,fresh=0,
   prior_target_name_exposure_count=len(cited),G6_SHA=sha_file(ROOT/v))
 print(json.dumps({'new_original_A3':True,'direct_C6_source_claim':True,
  'independent_text_extractors':2,'full_graphs':False,
  'prior_target_name_exposure':len(cited),'fresh_admitted':0,
  'G6_stage_sha256':sha_file(ROOT/v)},ensure_ascii=False))
if __name__=='__main__':main()
