"""A4 independent source-text extraction from official JATS using lxml section paths.
No previous A5 or A6 output reads; graph fields explicitly unresolved.
"""
from pathlib import Path
import hashlib,json,datetime,sys
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
SRC=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
PRE=O/'C_PMC13564134_A0_dual_science_read_precontract.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 contract=json.loads((ROOT/PRE).read_text());assert contract['A4']['read_A5_output'] is False
 assert sha(SRC)==contract['source_SHA']
 tree=etree.parse(str(ROOT/SRC),etree.XMLParser(resolve_entities=False,no_network=True))
 found=[]
 for section in tree.xpath('.//body//sec'):
  tit=section.xpath('./title')
  name=' '.join(''.join(tit[0].itertext()).split()) if tit else ''
  if name not in ('Discussion','De novo isoorientin biosynthesis'):continue
  for ix,p in enumerate(section.xpath('./p')):
   s=' '.join(''.join(p.itertext()).split())
   if any(key in s.lower() for key in ('gycgt1','glycosyltransferase for one-step','glycosylation to isoorientin')):
    found.append({'section':name,'paragraph_index_in_section':ix+1,
      'paragraph_text':s[:1200],'paragraph_sha':hashlib.sha256(s.encode()).hexdigest(),
      'original_sha':sha(SRC)})
 assert found and any('one-step' in x['paragraph_text'] for x in found)
 out={'task':T,'agent_role':'A4','epoch':'C-E02',
 'source_DOI':'10.1016/j.abiote.2026.100085','source_PMCID':'PMC13564134',
 'input_manifest_sha':sha(PRE),'source_sha256':sha(SRC),
 'extraction_id':'A4-lxml-results-discussion-20261011','read_other_extractor_output':False,
 'read_model_outcome':False,'human_reviewed':False,
 'candidate_claim':{'acceptor':'luteolin/flavone aglycone','donor':'UDP-glucose',
   'product':'isoorientin (luteolin 6-C-glucoside)','site':'flavone C6',
   'sugar_identity':'glucose','direction':'acceptor+UDP-Glc->C-glucoside+UDP',
   'reported_step_count':1,'enzyme':'GyCGT1','original_evidence_location':found},
 'acceptor_smiles':None,'donor_smiles':None,'product_smiles':None,
 'bond_atoms':None,'anomer_stereo':None,'reference_precursors':None,
 'allowed_structural_origin':None,
 'full_graph_source_not_present_in_selected_source_text':True,
 'source_formula_mass_stereo_original_check':False,
 'complete_reaction_structure_extracted':False,
 'fresh_admitted':False,'read_other_extractor':False,
 'missing':['source-approved acceptor graph','source-approved donor graph','source-approved product graph',
    'source atom map/bond identities','sugar anomer and stereochemistry','full reference precursors'] }
 dst=O/'C_PMC13564134_A4_independent_source_read.json'
 if (ROOT/dst).exists():raise RuntimeError('immutable')
 write(T,str(dst),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_A4_partial_extraction',source_sha=sha(SRC),evidence_count=len(found),full_graph=False)
 print(json.dumps({'A4_evidence':len(found),'complete_graph':False,'file':str(dst)},ensure_ascii=False))
if __name__=='__main__':main()
