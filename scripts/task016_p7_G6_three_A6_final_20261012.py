"""A6 final three-workstream disposition: full A4/A5 graph reconciliation, C6 scope static replay,
and definitive SOURCE-DISTINCT BUT REACTION-IDENTICAL-TO-FROZEN-BUILD holdout exclusion.
"""
from pathlib import Path
import json,hashlib,datetime,sys
from rdkit import Chem
from scripts.task016_p7_structure_harness import reconcile
from scripts.task016_p7_closure_harness import canonical,assert_zero_leakage
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,sha_file,ContractError
from flavoretro.glycoside_scope_c_v7 import apply_c_scope
from flavoretro.reviewed_resources import canonical_side
from scripts.operate import ROOT,write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
A4=O/'C_PMC13564134_A4_PubChem_property_full_graph.json'
A5=O/'C_PMC13564134_A5_PubChem_atom_record_full_graph.json'
NAME=O/'A6_isoorientin_name_only_formal_ruling.json'
TEN=O/'source10_Iris_SI_to_main_original_linkage_ruling.json'
FOURTEEN=O/'source14_Pisum_inner_sugar_O2_original_ruling.json'
IN=O/'C_PMC13564134_A0_PubChem_three_complete_graph_inputs.json'
FROZEN=B/'C/E02/build_supports.json';BANK=B/'C/E02/scope_bank.json'
G5=B/'prospective_G6_round_20261011_v1/C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return sha_file(ROOT/p)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,r):
 if (ROOT/p).exists():raise RuntimeError('immutable path '+str(p))
 write(T,str(p),json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
 a,b=rd(A4),rd(A5)
 chem=reconcile(a,b)
 assert chem['status']=='reconciled' and chem['structure_complete'] and chem['reference_precursor_complete']
 name=rd(NAME);ten=rd(TEN);pea=rd(FOURTEEN)
 assert name['decision']=='NAME_ONLY_IS_NOT_STRUCTURE_SITE_REACTION_LEAKAGE'
 assert ten['publication_family_SI_attachment_mapping']=='HIGH_CONFIDENCE_CONFIRMED'
 assert pea['decision']=='DEFERRED_NOT_ESTABLISHED_IN_ORIGINAL_1979_PDF'
 frozen=rd(FROZEN);scope=rd(BANK)
 assert len(frozen)==2 and len(scope)==1
 matches=[]
 for z in frozen:
  target=canonical(z['target']);acc=canonical(z['acceptor']);donor=canonical(z['donor'])
  if target==chem['product_smiles'] and acc==chem['acceptor_smiles'] and donor==chem['donor_smiles']:
   matches.append({'reaction_id':z['reaction_id'],'instance_id':z['instance_id'],
    'source_doi':z['provenance'].get('doi'),
    'build_support_SHA':sha(FROZEN),
    'acceptor_graph_exact_equal':True,'donor_graph_exact_equal':True,'product_graph_exact_equal':True})
 assert len(matches)==1 and matches[0]['reaction_id']=='C-CHRYSIN-LU6'
 # Independent static applicability, no MCTS/ABE; compare exactly the two complete precursors
 t=scope[0]
 rows=apply_c_scope(t,chem['product_smiles'],context=t['required_context'])
 expected=canonical_side(chem['reference_precursors'])
 hit=[x for x in rows if x['precursors']==expected]
 assert len(hit)>=1
 target={'reaction_id':chem['reaction_id'],
    'product_smiles':chem['product_smiles'],'acceptor_smiles':chem['acceptor_smiles'],
    'donor_smiles':chem['donor_smiles'],'reference_precursors':chem['reference_precursors'],
    'site':chem['site'],'doi':'10.1016/j.abiote.2026.100085','pmcid':'PMC13564134'}
 actual_error=None
 try:
  assert_zero_leakage(frozen,[target])
 except ContractError as e:
  actual_error=str(e)
 assert actual_error and 'build/holdout closure leakage' in actual_error
 r={'task':T,'at':now(),'agent_role':'A6','reaction_id':chem['reaction_id'],
  'A4_sha256':sha(A4),'A5_sha256':sha(A5),'input_precontract_sha256':sha(IN),
  'A4_A5_independent_reconciled':True,'actual_reconcile_status':chem['status'],
  'dual_molecular_structure_complete':True,'reference_precursor_complete':True,
  'acceptor_smiles':chem['acceptor_smiles'],'donor_smiles':chem['donor_smiles'],
  'product_smiles':chem['product_smiles'],'bond_atoms':chem['bond_atoms'],'site':chem['site'],
  'anomer_stereo':chem['anomer_stereo'],'source_structure_origin':'PubChem_authoritative_CIDs_5280445_114776_8629',
  'original_article_claim':'PMC13564134 GyCGT1 luteolin -> isoorientin one-step C6',
  'source_identity_A3_verified':True,'graph_source_CIDs':[5280445,114776,8629],
  'A6_name_only_decision':name['decision'],'name_only_exposure_is_not_reason_for_exclusion':True,
  'EXACT_FROZEN_BUILD_REACTION_LEAKAGE':True,'frozen_build_match':matches,
  'holdout_closure_guard_test_actual_raised':actual_error,
  'frozen_C_E02_scope_bank_sha256':sha(BANK),
  'static_only_scope_applicability_complete_reference':True,
  'static_only_outcomes':len(rows),'static_only_exact_reference_matches':len(hit),
  'scope_modified':False,'model_outcomes_read':False,
  'full_G6_chemical_graph_verified':True,'G6_FRESH_REACTION_ADMITTED':False,
  'fresh_eligible':False,'fresh_rejection_reason':'exact three-molecule reaction already present in C-E02 permanent build C-CHRYSIN-LU6 before new 2026 publication was read',
  'prior_named_assay_group_linkage_unknown_not_required_to_reject_exact_build':True,
  'unambiguous_disposition':'REJECTED_FROM_FRESH_AS_EXACT_BUILD_REPLAY',
  'source_can_remain_as_independent_publication_corroboration_for_design':True,
  'fresh_C_increment':0,'fresh_SS_increment':0,
  'G7_panel_freeze_eligible':False,'human_reviewed':False}
 path=O/'C_PMC13564134_A6_dual_structure_and_exact_build_closure_ruling.json';save(path,r)
 stage=O/'C-PMC13564134-G6-corrected/stages'
 freeze_stage_manifest(ROOT/stage,'G6_IDENTITY_STRUCTURE_ADMIT',
   [A4,A5,NAME,TEN,FOURTEEN,IN,path,FROZEN,BANK],G5,
   expected_previous_sha=sha(G5),family='C',epoch_id='C-E02')
 s=stage/'G6_IDENTITY_STRUCTURE_ADMIT.json'
 assert verify_stage_chain(ROOT/s,sha(s))['stage']=='G6_IDENTITY_STRUCTURE_ADMIT'
 event(T,'C_PMC13564134_final_A6_complete_graph_but_exact_build_block',
    C6_graph_reconciled=True,static_complete=True,exact_build='C-CHRYSIN-LU6',fresh=0,
    frozen_G6_amendment_SHA=sha(s))
 print(json.dumps({'full_chemical_structure':True,'complete_precursors':True,
  'frozen_scope_applicable':True,'exact_build_match':matches[0]['reaction_id'],
  'fresh_admitted':0,'G6_corrected_sha':sha(s)},ensure_ascii=False))
if __name__=='__main__':main()
