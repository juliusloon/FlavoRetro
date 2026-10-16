"""P7 owner16 G6 bounded source-reaction disposition and explicit zero-full-graph admission.
Scientific scope annotation pertains ONLY to cited example; NEVER reject an entire article as devoid of other chemistry.
The historical originals were exposed before this batch preregistered G5: no fresh holdout is possible.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,sha_file,role_manifest
T='TASK-016-P7'; B=Path('outputs/task016-p7/v1');R=B/'G6_owner_16_historical_source_review_v1'
PR=B/'manual_grabbed_A3_reconciled_20261011/A3_owner_intake_inventory_reconciliation.json'
R3=B/'manual_grabbed_R3_A3_reconciled_20261011/R3_A3_4original_crosscheck_and_G6_documentary_questions.json'
EXP1=B/'manual_grabbed_A3_reconciled_20261011/permanent_manual_science_exposure_v1.jsonl'
EXP2=B/'manual_grabbed_R3_A3_reconciled_20261011/R3_4original_permanent_exposure.jsonl'
LEG=B/'epoch_ledger.jsonl'
# Anchor formulas are NOT structural graphs. They localize a reported reaction statement.
# sample role: source's featured chemistry, not a comprehensive all-reaction inventory.
CHECKS={
'01':('genome-wide association','GWAS_isovitexin_indirect','source_reaction_not_qualified','Mungbean GWAS and isovitexin pathways, not source-complete direct flavone C6 single-step CGT in located claim.'),
'02':('3-O-glycosylation','flavonol_aglycone_3O','scope_mismatch_SS_O2','Tomato SlUGT75C1 converts quercetin and kaempferol aglycones at O3; not sugar inner O2.'),
'03':('quercetin 3-O-rutinoside 7-O-glucoside','rutin_aglycone_O7_O4prime_O3prime','scope_mismatch_SS_O2','Tea CsUGT73AC15 Figure 5 P10-P12 labels show aglycone O7/O4prime/O3prime additions, not inner O2 sugar.'),
'04':('glycosylation of flavonol aglycones','flavonol_aglycone_O3_O7','scope_mismatch_SS_O2','Laportea UGT glycosylation of flavonol aglycones, not specific inner O2.'),
'05':('flavonol 3-O-galactosyltransferase','flavonol_aglycone_3O','scope_mismatch_SS_O2','Apple F3GT enzyme converts aglycone 3-OH, not sugar inner O2.'),
'06':('2-hydroxynaringenin','precursor_2_hydroxy_then_dehydration','scope_mismatch_c6_direct','Desmodium di-C glycocylflavone biosynthesis first uses 2-hydroxynaringenin precursor, later dehydration; not direct frozen flavone C6.'),
'07':('Sc\\(OTf\\)','organic_reaction_not_single_enzymatic_c6','scope_mismatch_c6_direct','RSC multi-step chemical flavone di-C-glycosylation Lewis acid, not direct single enzyme flavone C6.'),
'08':('phloretin','dihydrochalcone_C3prime','scope_mismatch_c6_direct','O-to-C glucosyl bond rearrangement in phloretin to nothofagin C3prime, outside frozen flavone C6.'),
'09':('nothofagin','dihydrochalcone_C3prime','scope_mismatch_c6_direct','Process synthesis of nothofagin glucoside from phloretin, not direct flavone C6.'),
'10':('UGT707B2','SI_only_no_verified_main_attachment_link','source_identity_attachment_pending','UGT707B2 SI spectra; full paper attachment binding and direct C6 reaction not verified.'),
'11':('2-hydroxynaringenin','precursor_2_hydroxy_then_dehydration','scope_mismatch_c6_direct','PNAS two-step di-C CGT acts on 2-hydroxynaringenin then dehydration; not direct flavone C6 enzyme reaction.'),
'12':('2-hydroxyflavanone','precursor_2_hydroxy_then_dehydration','scope_mismatch_c6_direct','Rice cereal CGTs act on 2-hydroxyflavanones before spontaneous dehydration to flavone C6/C8.'),
'13':('reversible','flavonol_3O_reverse_UDP','scope_mismatch_SS_O2','Parsley 3-O UGT reversible reaction: not inner-sugar O2 glycosylation.'),
'14':('triglucoside','flavonol_3O_chain_extension_link_site_unknown','linkage_O2_structure_pending','Pea flavonol 3-O glucoside forms 3-O mono/di/tri glucoside through enzyme extract; no direct inner sugar O2 location structurally verified.'),
'15':('3-O-glucosyltransferase','flavonol_aglycone_3O','scope_mismatch_SS_O2','Petunia flavonol/anthocyanidin O3 glucose addition; not sugar inner O2.'),
'16':('7-hydroxyl','flavonol_aglycone_7O','scope_mismatch_SS_O2','Chrysanthemum flavonol 7-O glucosyltransferase, not inner sugar O2.')
}
# Include non-complete graph failures explicitly rather than hand-writing SMILES.
MISSING=('acceptor_source_atom_mapped_graph','donor_source_atom_mapped_graph','product_source_atom_mapped_graph',
         'bond_atom_identities','confirmed_anomer_stereo','direct_single_step_proof',
         'reference_precursor_full_graph','A4_A5_independent_graph_agreement',
         'source_reaction_closure_verified','scope_runtime_applicability_proven')
def now():return datetime.now(timezone.utc).isoformat()
def put(path,obj):
 if (ROOT/path).exists():raise RuntimeError('immutable output exists '+str(path))
 write(T,str(path),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
 old=json.loads((ROOT/PR).read_text());new=json.loads((ROOT/R3).read_text())
 counts={}
 for fam in ('C','SS'):
  out=R/fam
  g5=out/'stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
  assert verify_stage_chain(ROOT/g5,sha_file(ROOT/g5))['stage']=='G5_FRESH_HOLDOUT_ACQUIRE'
  pre=json.loads((ROOT/out/'A0_G5_manual16_historical_precontract.json').read_text())
  records=[]
  for rec in pre['source_records']:
   no=rec['no'];expr,kind,gate,meaning=CHECKS[no]
   p=ROOT/rec['source_file'];assert sha_file(p)==rec['source_sha256']
   run=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,check=True)
   txt=run.stdout;pages=[x for x in txt.split('\f') if x.strip()]
   located=[]
   for i,page in enumerate(pages):
    match=re.search(expr,page,re.I)
    if match:
     context=' '.join(page[max(0,match.start()-140):match.end()+230].split())[:430]
     located.append({'PDF_page':i+1,'anchor_pattern':expr,
       'source_page_SHA256':hashlib.sha256(page.encode()).hexdigest(),
       'nearby_source_text':context})
   if not located:raise RuntimeError('Source evidence anchor missing '+no+'/'+expr)
   g6='deferred' if no in {'08','10'} else 'rejected_for_current_scope_example'
   record={'task':T,'owner_source_number':no,'family':fam,
     'owner_historical_DOI_or_PMC':rec['v32_identifier'],
     'verified_DOI':rec['DOI'],'source_pdf':rec['source_file'],
     'source_sha256':rec['source_sha256'],'source_A3_publication_identity':rec['A3_pub_identity'],
     'bounded_example_kind':kind,'scope':fam+'-E02',
     'observed_report':meaning,'original_evidence_loci':located[:2],
     'bounded_reaction_scope_gate':gate,'disposition':g6,
     'complete_article_all_reactions_negatively_screened':False,
     'sources_are_historical_prior_scientifically_read':True,
     'fresh_post_scope_eligible':False,'same_article_all_reactions_fresh_excluded':True,
     'A4_chemical_graph_extraction_done':False,'A5_independent_graph_extraction_done':False,
     'graph_reconciliation_passed':False,'source_identity_is_not_structure_eligibility':True,
     'structural_missing_fields':list(MISSING),'G6_fully_qualified_reactions':0,
     'scope_applicable_full_reaction_pass':False,
     'G7_eligibility':False,'scientific_outcome_read':False}
   records.append(record)
  assert len(records)==8
  summary={'task':T,'at':now(),'epoch_id':fam+'-E02','family':fam,
   'stage':'G6_IDENTITY_STRUCTURE_ADMIT','mode':'bounded_owner_historical_originals_source_disposition',
   'G5_precontract_sha256':sha_file(ROOT/out/'A0_G5_manual16_historical_precontract.json'),
   'G5_stage_SHA256':sha_file(ROOT/g5),
   'owner_originals_processed':8,'passed_full_G6':0,
   'deferred':sum(x['disposition']=='deferred' for x in records),
   'rejected_current_example':sum(x['disposition']=='rejected_for_current_scope_example' for x in records),
   'total_conserved':True,'sources':records,
   'no_post_scope_fresh_claim':True,'complete_graph_admitted':0,
   'can_freeze_G7_panel':False,'A4_A5_full_graph_extractions_not_performed':True,
   'all_article_reactions_exhaustively_reviewed':False,
   'requires_future_G5_prospective_novel_source_A3_A4_A5_A6':True,
   'G6_science_status':'historical_owner16_batch_disposition_done_G6_global_open'}
  p=out/'G6_bounded_scientific_dispositions.json'
  put(p,summary)
  role=role_manifest('A6',fam+'-E02',[g5,out/'A0_G5_manual16_historical_precontract.json',PR,R3,EXP1,EXP2],
      [p],{'processed':8,'passed':0,'rejected':summary['rejected_current_example'],'pending':summary['deferred']},
      read_holdout=False,read_model_outcome=False)
  role.update({'role_claim_limit':'bounded source site classification, not full graph two-independent A4/A5',
      'full_graph_admission':0,'permanent_exposure_exclusion':8,'G7_blocked':True})
  rolepath=out/'role_A6_G6_bounded_screen.json'
  put(rolepath,role)
  stage=out/'stages'
  freeze_stage_manifest(ROOT/stage,'G6_IDENTITY_STRUCTURE_ADMIT',
    [p,rolepath,PR,R3,EXP1,EXP2],g5,
    expected_previous_sha=sha_file(ROOT/g5),family=fam,epoch_id=fam+'-E02')
  stagep=stage/'G6_IDENTITY_STRUCTURE_ADMIT.json'
  assert verify_stage_chain(ROOT/stagep,sha_file(ROOT/stagep))['stage']=='G6_IDENTITY_STRUCTURE_ADMIT'
  event(T,'owner16_historical_bounded_G6_science_screen_frozen',family=fam,
      G6_sha256=sha_file(ROOT/stagep),passed=0,pending=summary['deferred'],
      rejected=summary['rejected_current_example'],no_fresh=True)
  counts[fam]={'rows':8,'rejected_bounded':summary['rejected_current_example'],
     'deferred':summary['deferred'],'passed_full_reaction':0,
     'G6_stage_sha256':sha_file(ROOT/stagep)}
 print(json.dumps({'G6_historical_batch_processed':16,'status':'documentary_sample_dispositions_complete_not_GLOBAL_G6',
  'axis':counts,'fresh_C':0,'fresh_SS':0},ensure_ascii=False))
if __name__=='__main__':main()
