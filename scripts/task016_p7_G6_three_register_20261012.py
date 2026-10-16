"""Append corrected G6 stage receipt plus permanent source/structure exposure; no fresh holdout."""
from pathlib import Path
import json,datetime,sys
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1';E=B/'epoch_ledger.jsonl'
def sha(p):return sha_file(ROOT/p)
def main():
 audit=json.loads((ROOT/O/'A11_three_workstreams_independent_raw_verification.json').read_text())
 assert audit['failed']==0 and audit['passed']==305
 stage=O/'C-PMC13564134-G6-corrected/stages/G6_IDENTITY_STRUCTURE_ADMIT.json'
 verify_stage_chain(ROOT/stage,sha(stage))
 target=O/'C_PMC13564134_A6_dual_structure_and_exact_build_closure_ruling.json'
 exposure=O/'C_PMC13564134_permanent_graph_exposure.jsonl'
 if (ROOT/exposure).exists():raise RuntimeError('immutable exposure')
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 row={'task':T,'at':now,'role':'A6_exposure_registrar',
  'source_DOI':'10.1016/j.abiote.2026.100085','source_PMCID':'PMC13564134',
  'source_exposure_type':'source_read_for_G6_in_current_epoch_full_A4_A5_structure_transcribed',
  'build_exact_reaction_id':'C-CHRYSIN-LU6','development_exposed':True,
  'accepted_as_fresh_holdout':False,'known_reaction_leakage_with_frozen_C_build':True,
  'A4_path':str(O/'C_PMC13564134_A4_PubChem_property_full_graph.json'),
  'A4_SHA':sha(O/'C_PMC13564134_A4_PubChem_property_full_graph.json'),
  'A5_path':str(O/'C_PMC13564134_A5_PubChem_atom_record_full_graph.json'),
  'A5_SHA':sha(O/'C_PMC13564134_A5_PubChem_atom_record_full_graph.json'),
  'A6_path':str(target),'A6_SHA':sha(target),
  'source_graph_authority_CIDs':[5280445,114776,8629],
  'G7_writer_must_merge_this_exposure_before_freeze':True,
  'human_reviewed':False}
 write(T,str(exposure),json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
 orig=(ROOT/E).read_text();old=[json.loads(l) for l in orig.splitlines() if l.strip()]
 if any(x.get('event_type')=='G6_PMC13564134_A4_A5_full_graph_exact_frozen_build_v2' for x in old):
  raise RuntimeError('epoch already exists')
 add={'task':T,'at':now,'family':'C','epoch_id':'C-E02',
  'event_type':'G6_PMC13564134_A4_A5_full_graph_exact_frozen_build_v2',
  'stage':'G6_IDENTITY_STRUCTURE_ADMIT','status':'active',
  'stage_manifest_path':str(stage),'stage_manifest_sha256':sha(stage),
  'corrects_previous_block_reason':'prior original text-only G6 branch superseded by authoritative PubChem full graph; exact build leakage now independently established',
  'stage_is_not_P7_G6_global_completed':True,
  'source_article_PMC':'PMC13564134','chemical_structure_complete':True,
  'reference_precursors_complete':True,'static_frozen_scope_applicability':True,
  'reaction_identity_is_already_C_E02_build':'C-CHRYSIN-LU6',
  'fresh_admitted':0,'science_cells':0,'read_model_outcome':False,
  'exposure_supplement_SHA':sha(exposure),'human_reviewed':False}
 write(T,str(E),orig+json.dumps(add,ensure_ascii=False,sort_keys=True)+'\n')
 event(T,'P7_G6_three_rulings_stage_registered',sha256=sha(stage),epoch_SHA=sha(E),
       exact_build=True,fresh=0)
 print(json.dumps({'epoch_rows_appended':1,'permanent_graph_exposure_written':True,
  'stage_sha256':sha(stage),'ledger_sha256':sha(E)}))
if __name__=='__main__':main()
