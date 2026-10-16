"""Independent A11 original-document/G5->G6 source disposition audit; no chemical graph approval."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file,ContractError
from scripts.task016_p7_structure_harness import _validated
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
V1=B/'G6_owner_16_historical_source_review_v1'
V2=B/'G6_owner_16_historical_source_review_v2'
OUT=V2/'A11_original_source_verification.json'
def rd(p):return json.loads((ROOT/p).read_text())
def lines(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
checks=[]
def ck(cond,label):
 if not cond:raise RuntimeError('G6_A11_VERIFY_FAIL: '+label)
 checks.append(label)
def main():
 if (ROOT/OUT).exists():raise RuntimeError('immutable_existing')
 ck((ROOT/V1).exists(),'prior_v1_preserved')
 all_=[]
 for fam in ('C','SS'):
  x=V2/fam
  g5=x/'stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
  g6=x/'stages/G6_IDENTITY_STRUCTURE_ADMIT.json'
  v5=verify_stage_chain(ROOT/g5,sha_file(ROOT/g5))
  v6=verify_stage_chain(ROOT/g6,sha_file(ROOT/g6))
  ck(v5['stage']=='G5_FRESH_HOLDOUT_ACQUIRE','G5 predecessor '+fam)
  ck(v6['stage']=='G6_IDENTITY_STRUCTURE_ADMIT','G6 frozen source disposition '+fam)
  ck(v6['input_manifest_sha']==sha_file(ROOT/g5),'G6 binds immutable G5 '+fam)
  a=rd(x/'G6_bounded_scientific_dispositions.json')
  role=rd(x/'role_A6_G6_bounded_screen.json')
  ck(a['total_conserved'] is True and a['owner_originals_processed']==8,'conserved 8 '+fam)
  ck(len(a['sources'])==8,'eight reactions records '+fam)
  ck(a['passed_full_G6']==0 and a['complete_graph_admitted']==0,'no claimed G6 graph '+fam)
  ck(a['rejected_current_example']==7 and a['deferred']==1,'7 reject example 1 defer '+fam)
  ck(role['counts']=={'processed':8,'passed':0,'rejected':7,'pending':1},'A6 role schema '+fam)
  ck(role['read_model_outcome'] is False and role['read_holdout'] is False,'A6 model split '+fam)
  for p,digest in role['input_manifest_sha'].items():ck(sha_file(ROOT/p)==digest,'A6 input SHA '+fam+':'+Path(p).name)
  for p,digest in role['output_file_sha'].items():ck(sha_file(ROOT/p)==digest,'A6 output SHA '+fam+':'+Path(p).name)
  for r in a['sources']:
   num=r['owner_source_number'];p=ROOT/r['source_pdf']
   ck(sha_file(p)==r['source_sha256'],'raw sha '+num)
   data=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,text=True,check=True).stdout
   pages=[x for x in data.split('\f') if x.strip()]
   for a0 in r['original_evidence_loci']:
    page=pages[a0['PDF_page']-1]
    ck(hashlib.sha256(page.encode()).hexdigest()==a0['source_page_SHA256'],'page hash '+num)
    ck(re.search(a0['anchor_pattern'],page,re.I) is not None,'source anchor '+num)
   ck(r['fresh_post_scope_eligible'] is False and r['G7_eligibility'] is False,'not fresh/holdout '+num)
   ck(r['A4_chemical_graph_extraction_done'] is False and r['A5_independent_graph_extraction_done'] is False,'no forged dual graph '+num)
   ck(len(r['structural_missing_fields'])>=9,'missing all graph fields '+num)
   ck(r['complete_article_all_reactions_negatively_screened'] is False,'bounded single report not whole article '+num)
   all_.append(r)
 ck(len(all_)==16,'sixteen source records')
 ck(len({x['owner_source_number'] for x in all_})==16,'no duplicate owner IDs')
 ck(all(x['disposition']=='rejected_for_current_scope_example' for x in all_ if x['owner_source_number'] in {'08','09','13','15','16'}),'source original sample scope boundaries')
 by={x['owner_source_number']:x for x in all_}
 ck(by['14']['disposition']=='deferred' and by['14']['bounded_reaction_scope_gate']=='linkage_O2_structure_pending',
    '14 uncertain O2 not falsely rejected')
 ck(by['10']['disposition']=='deferred' and by['10']['source_A3_publication_identity']=='SI_link_pending',
    '10 incomplete SI chain not falsely admitted')
 v1_ss=rd(V1/'SS/G6_bounded_scientific_dispositions.json')
 v1_c=rd(V1/'C/G6_bounded_scientific_dispositions.json')
 ck(next(x for x in v1_ss['sources'] if x['owner_source_number']=='14')['disposition']=='rejected_for_current_scope_example',
    'v1 14 source classification error preserved')
 ck(next(x for x in v1_c['sources'] if x['owner_source_number']=='08')['disposition']=='deferred',
    'v1 08 source classification error preserved')
 for fam,expected in [('C','09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46'),
                       ('SS','a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f')]:
  ck(sha_file(ROOT/B/fam/'E02/stages/G4_SCOPE_FREEZE.json')==expected,'G4 frozen '+fam)
 # Demonstrate full-graph harness cannot accept name-only/documentary source observation.
 try:
  _validated({'reaction_id':'owner14','anomer_stereo':'unknown','structure_origin':'handwritten'})
 except ContractError:
  checks.append('full_graph_harness_rejects_name_only_incomplete')
 else:raise RuntimeError('G6_FAIL_OPEN')
 result={'task':T,'agent_role':'A11','human_reviewed':False,
 'scope':'source-original textual anchors and contract data, NOT independent A4/A5 molecule reconstruction',
 'passed':len(checks),'failed':0,'check_names':checks,
 'v1_preserved':True,'v2_corrected':True,'G5_G6_frozen_C':sha_file(ROOT/V2/'C/stages/G6_IDENTITY_STRUCTURE_ADMIT.json'),
 'G5_G6_frozen_SS':sha_file(ROOT/V2/'SS/stages/G6_IDENTITY_STRUCTURE_ADMIT.json'),
 'sources_covered':16,'bounded_rejected':14,'deferred':2,'full_reactions_admitted':0,
 'fresh_C':0,'fresh_SS':0,'science_ABE_cells':0,'metrics':None,
 'G6_global_completed':False,'G7_panel':False,
 'read_model_outcome':False,'errors':[]}
 write(T,str(OUT),json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 event(T,'owner16_independent_G6_bounded_A11_completed',passed=len(checks),failed=0)
 print(json.dumps({'A11_pass':len(checks),'A11_fail':0,'sixteen_scope_dispositions':{'bounded_rejected':14,'deferred':2,'G6_fresh':0},
  'report':str(OUT)},ensure_ascii=False))
if __name__=='__main__':main()
