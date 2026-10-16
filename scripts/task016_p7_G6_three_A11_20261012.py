"""A11 independent raw source rederivation of three P7 G6 decisions.
Validates actual PubChem bytes, true three-graph exact build leakage, unchanged G4,
source10 authoritative PMC SI page linkage, source14 source-only insufficient O2.
"""
from pathlib import Path
import json,hashlib,re,subprocess,sys
from lxml import html
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
from scripts.task016_p7_closure_harness import canonical
from scripts.task016_p7_structure_harness import reconcile
from flavoretro.glycoside_scope_c_v7 import apply_c_scope
from flavoretro.reviewed_resources import canonical_side
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
AUD=O/'A11_three_workstreams_independent_raw_verification.json'
def sha(p):return sha_file(ROOT/p)
def rd(p):return json.loads((ROOT/p).read_text())
checks=[]
def ck(x,s):
 if not x:raise RuntimeError('A11 G6 INDEPENDENT FAILURE: '+s)
 checks.append(s)
def main():
 if (ROOT/AUD).exists():raise RuntimeError('immutable')
 plan=rd(O/'three_workstreams_precontract.json')
 for key,p in plan['inputs'].items():
  ck(sha(Path(p['path']))==p['sha256'],'inputSHA_'+key)
 a6n=rd(O/'A6_isoorientin_name_only_formal_ruling.json')
 org={}
 for fn in ['A6_prior_exposure','A6_prior_exposure_v2','A6_prior_exposure_effective']:
  p=Path(plan['inputs'][fn]['path'])
  vals=[(n,json.loads(l)) for n,l in enumerate((ROOT/p).read_text().splitlines(),1) if 'partial-target-name:isoorientin' in l]
  ck(len(vals)==12,'12 name instances '+fn)
  for num,v in vals:
   org.setdefault(v['exposure_id'],[]).append((str(p),num))
   for fld in ['acceptor_smiles','donor_smiles','product_smiles','target_graph','reaction_signature','site','site_claim']:
    ck(v.get(fld) is None,'no_struct_site_'+fn+':'+str(num)+':'+fld)
 ck(len(org)==12 and all(len(a)==3 for a in org.values()),'12 historical analytes 3 versions')
 ck(a6n['name_token_automatic_fresh_rejection'] is False,'metadata name only not automatic block')
 ck(a6n['fresh_admitted'] if 'fresh_admitted' in a6n else not a6n['name_token_automatic_fresh_admission'],'no first-step automatic admission')
 r10=rd(O/'source10_Iris_SI_to_main_original_linkage_ruling.json')
 p=Path(plan['inputs']['Iris_official_PMC_HTML']['path'])
 page=html.fromstring((ROOT/p).read_text())
 ck(page.xpath('//meta[@name="citation_doi"]/@content')==['10.1002/cbic.70486'],'official Iris main DOI')
 ck(any('CBIC-27-e70486-s001.pdf' in h for h in page.xpath('//a/@href')),'actual official SI link')
 ck(r10['owner_SI_exact_binary_equality_to_official_download'].startswith('NOT_PROVEN'),'do not fake SI bit identity')
 si=Path(plan['inputs']['Iris_owner_SI']['path'])
 si_text=subprocess.run(['pdftotext','-layout',str(ROOT/si),'-'],capture_output=True,text=True,check=True).stdout
 ck('UGT707B2' in si_text and 'Iris tectorum' in si_text,'owner SI title content')
 ck('Fig. S6' in si_text and 'Table S3' in si_text,'owner SI figs and table')
 r14=rd(O/'source14_Pisum_inner_sugar_O2_original_ruling.json')
 pea=Path(plan['inputs']['Pea_original_PDF']['path'])
 text=subprocess.run(['pdftotext','-layout',str(ROOT/pea),'-'],capture_output=True,text=True,check=True).stdout
 ck('glucosylation' in text.lower() and 'kaempferol' in text.lower(),'original 1979 enzyme data')
 ck(r14['site_inner_sugar_O2_source_confirmed'] is False,'no O2 invented')
 ck(r14['decision']=='DEFERRED_NOT_ESTABLISHED_IN_ORIGINAL_1979_PDF','C14 deferred')
 q=rd(O/'C_PubChem_raw_HTTP_receipts.json')
 ck(len(q['records'])==6 and all(x['status']==200 for x in q['records']),'6 official PubChem 200')
 source={}
 for x in q['records']:
  p=Path(x['path'])
  ck(sha(p)==x['sha256'],'PubChem original unchanged '+str(x['number']))
  payload=rd(p)
  rec=payload['PropertyTable']['Properties'][0] if x['route'].endswith('properties') else payload['PC_Compounds'][0]
  cid=rec.get('CID') or rec['id']['id']['cid']
  ck(cid=={'luteolin':5280445,'isoorientin':114776,'UDP-glucose':8629}[x['name']],
     'source identity CID '+str(x['number']))
  if x['route'].endswith('properties'):
   m=Chem.MolFromSmiles(rec['SMILES'])
   ck(m is not None and rdMolDescriptors.CalcMolFormula(m)==rec['MolecularFormula'],
      'source property full graph and formula '+x['name'])
   source[x['name']]=rec['SMILES']
 main=rd(O/'C_PMC13564134_A6_dual_structure_and_exact_build_closure_ruling.json')
 a4=rd(O/'C_PMC13564134_A4_PubChem_property_full_graph.json')
 a5=rd(O/'C_PMC13564134_A5_PubChem_atom_record_full_graph.json')
 dual=reconcile(a4,a5)
 ck(dual['structure_complete'] and dual['reference_precursor_complete'] and dual['status']=='reconciled',
     'actual code formal two-extractor source graph reconciliation')
 for name,key in [('luteolin','acceptor_smiles'),('isoorientin','product_smiles'),('UDP-glucose','donor_smiles')]:
  ck(canonical(source[name])==canonical(dual[key]),'authority official source matches extractor graph '+name)
 build=rd(B/'C/E02/build_supports.json')
 exact=[x for x in build if canonical(x['target'])==dual['product_smiles'] and canonical(x['acceptor'])==dual['acceptor_smiles'] and canonical(x['donor'])==dual['donor_smiles']]
 ck(len(exact)==1 and exact[0]['reaction_id']=='C-CHRYSIN-LU6','actual old frozen C build three graph exact leakage')
 ck(main['EXACT_FROZEN_BUILD_REACTION_LEAKAGE'] is True,'A6 did not reverse exact build result')
 t=rd(B/'C/E02/scope_bank.json')[0]
 hit=apply_c_scope(t,dual['product_smiles'],context=t['required_context'])
 ck(any(x['precursors']==canonical_side(dual['reference_precursors']) for x in hit),
    'static original frozen scope returns complete ref precursor')
 stage=O/'C-PMC13564134-G6-corrected/stages/G6_IDENTITY_STRUCTURE_ADMIT.json'
 ck(verify_stage_chain(ROOT/stage,sha(stage))['stage']=='G6_IDENTITY_STRUCTURE_ADMIT','G5 G6 prior SHA chain')
 for name,expected in [('C','09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46'),('SS','a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f')]:
  ck(sha(B/name/'E02/stages/G4_SCOPE_FREEZE.json')==expected,'G4 original SHA '+name)
 ck(main['G6_FRESH_REACTION_ADMITTED'] is False and not main['fresh_eligible'],'never accept exact build as fresh')
 out={'task':T,'role':'A11','at':'2026-10-12','checks_total':len(checks),'passed':len(checks),'failed':0,
  'checks':checks,'source_metadata_distinct_name_exposures':12,'source10_official_SI_page_link_confirmed':True,
  'source10_exact_bytes_unverified':True,'source14_O2_not_proven':True,
  'authoritative_structure_3_CIDs_reconciled':True,'original_source_PMC13564134':True,
  'frozen_scope_static_works':True,'EXACT_BUILD_REACTION_MATCH':'C-CHRYSIN-LU6',
  'fresh_C':0,'fresh_SS':0,'ABE_cells':0,'full_global_G6_completed':False,
  'no_model_read':True,'human_reviewed':False}
 write(T,str(AUD),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'P7_G6_three_workstreams_A11_raw_independent',passed=len(checks),failed=0,fresh=0)
 print(json.dumps({'A11_pass':len(checks),'failed':0,'C_structure_complete':True,
  'C_exact_build':'C-CHRYSIN-LU6','fresh_C':0,'fresh_SS':0},ensure_ascii=False))
if __name__=='__main__':main()
