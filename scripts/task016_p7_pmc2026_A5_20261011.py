"""A5 independent source-text extraction via stdlib XML iteration (not lxml, no A4 read).
Tracks source claim atom/regio and exact unknown graph fields, no name-derived SMILES.
"""
import hashlib,json,datetime,sys
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
SRC=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
PRE=O/'C_PMC13564134_A0_dual_science_read_precontract.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def clean(el):return ' '.join(''.join(el.itertext()).split())
def main():
 contract=json.loads((ROOT/PRE).read_text());assert contract['A5']['read_A4_output'] is False
 assert sha(SRC)==contract['source_SHA']
 root=ET.parse(ROOT/SRC).getroot()
 nodes=[]
 for sec in root.iter('sec'):
  title=sec.find('title')
  secname=clean(title) if title is not None else 'no-section-title'
  if secname not in ('Results','Discussion','De novo isoorientin biosynthesis'):continue
  for el in list(sec):
   if el.tag not in ('p','fig'):continue
   node=el.find('caption') if el.tag=='fig' else el
   if node is None:continue
   s=clean(node)
   if ('isoorientin' in s.lower() and
        any(w in s.lower() for w in ('glycosyltransferase','gycgt1','udp-glucose','one-step'))):
    nodes.append({'section':secname,'element_tag':el.tag,'element_id':el.get('id'),
      'source_text':s[:1050], 'paragraph_SHA256':hashlib.sha256(s.encode()).hexdigest(),
      'source_file_sha256':sha(SRC)})
 assert len(nodes)>=2,'no independent evidence for C6 enzyme step'
 out={'task':T,'agent_role':'A5','epoch_id':'C-E02','timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'source_DOI':'10.1016/j.abiote.2026.100085','source_PMCI':'PMC13564134',
 'extraction_id':'A5-elementtree-independent-jats-20261011',
 'input_manifest_sha':sha(PRE),'source_sha256':sha(SRC),
 'read_other_extractor_output':False,'read_model_outcome':False,'human_reviewed':False,
 'acceptor':'luteolin','donor':'UDP-glucose','product':'isoorientin',
 'reaction_site':'flavone C6 C-C glucose bond','reported_enzyme':'GyCGT1',
 'glucose_donor':'UDP-Glc','reported_single_step':True,
 'cited_source_original_elements':nodes[:8],
 'acceptor_smiles':None,'donor_smiles':None,'product_smiles':None,
 'formed_bond_source_atom_ids':None,'anomer_configuration_verified':False,
 'product_stereo_verified':False,'reference_precursor_full_molecular_graphs':None,
 'structure_origin':'text_extraction_only_not_eligible_source_graph_origin',
 'source_graph_formula_mass_reconciliation_done':False,
 'structure_complete':False,'full_G6_eligibility':False,'fresh_admitted':False,
 'outstanding':['original or official supplementary atom graph','independent source atom-map assignments',
                'acceptor/donor/product stereochemical consistency','chemical formula and mass source crosscheck',
                'historical exact named target and assay closure'] }
 dst=O/'C_PMC13564134_A5_independent_source_read.json'
 if (ROOT/dst).exists():raise RuntimeError('immutable')
 write(T,str(dst),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_A5_partial_extraction',source_sha=sha(SRC),evidence_count=len(nodes),full_graph=False)
 print(json.dumps({'A5_evidence':len(nodes),'complete_graph':False,'file':str(dst)},ensure_ascii=False))
if __name__=='__main__':main()
