"""A4 independent full source molecular graph: PubChem PROPERTY raw name CID stereo records.
Do not read A5 output or PubChem atom/bond RECORD paths. All molecular SMILES verbatim authority.
"""
from pathlib import Path
import json,hashlib,datetime,sys,re
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,Descriptors
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
PRE=O/'C_PMC13564134_A0_PubChem_three_complete_graph_inputs.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 prep=json.loads((ROOT/PRE).read_text())
 assert prep['A4'] and prep['C_E02_G4_sha']=='09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46'
 docs={};forms={}
 for r in prep['structure_requests']:
  if r['route']!='PubChem_PUG_name_to_properties':continue
  fp=Path(r['path']);assert sha(fp)==r['sha256']
  doc=json.loads((ROOT/fp).read_text())['PropertyTable']['Properties'][0]
  assert doc['CID']==prep['authoritative_cids'][r['name']]
  smiles=doc.get('SMILES')
  assert smiles and '@' in smiles if r['name']!='luteolin' else smiles is not None
  mol=Chem.MolFromSmiles(smiles);assert mol
  formula=rdMolDescriptors.CalcMolFormula(mol)
  exact=Descriptors.ExactMolWt(mol)
  assert formula==doc['MolecularFormula'] and abs(exact-float(doc['ExactMass']))<0.00001
  docs[r['name']]=doc
  forms[r['name']]={'source':str(fp),'source_sha256':sha(fp),'CID':doc['CID'],
    'source_isomeric_SMILES':smiles,'canonical_isomeric_graph':Chem.MolToSmiles(mol,isomericSmiles=True),
    'InChIKey':doc['InChIKey'],'InChI':doc['InChI'],'formula':formula,
    'exact_mass':round(exact,8),'IUPACName':doc['IUPACName']}
 assert len(forms)==3
 prod=Chem.MolFromSmiles(docs['isoorientin']['SMILES'])
 lut=Chem.MolFromSmiles(docs['luteolin']['SMILES'])
 # Source IUPAC locant '6' independently verifies the site; RDKit actually finds C(sp2)-C(sp3 glycopyranose).
 assert re.search(r'-6-\[',docs['isoorientin']['IUPACName'])
 assert '2S,3R,4R,5S,6R' in docs['isoorientin']['IUPACName']
 bonds=[]
 for b in prod.GetBonds():
  for ar,sg in ((b.GetBeginAtom(),b.GetEndAtom()),(b.GetEndAtom(),b.GetBeginAtom())):
   if (ar.GetIsAromatic() and sg.GetAtomicNum()==6 and not sg.GetIsAromatic() and
       sg.IsInRingSize(6) and any(n.GetAtomicNum()==8 and n.IsInRingSize(6) for n in sg.GetNeighbors())):
    bonds.append((ar.GetIdx(),sg.GetIdx()))
 assert len(bonds)==1,bonds
 ar,an=bonds[0]
 rw=Chem.RWMol(prod);rw.RemoveBond(ar,an)
 fragments=Chem.GetMolFrags(rw.GetMol(),asMols=True,sanitizeFrags=True)
 parent=[x for x in fragments if Chem.MolToSmiles(x)==Chem.MolToSmiles(lut)]
 assert len(parent)==1 and len(fragments)==2
 assert docs['isoorientin']['MolecularFormula']=='C21H20O11'
 assert docs['UDP-glucose']['MolecularFormula']=='C15H24N2O17P2'
 bd={'acceptor_atom':'PubChemCID5280445:luteolin:ring-C6',
     'donor_atom':'PubChemCID8629:UDP-alpha-D-glucose:sugar-C1',
     'product_atoms':['PubChemCID114776:flavone-ring-C6','PubChemCID114776:glucose-ring-C1']}
 src=next(r for r in prep['structure_requests'] if r['name']=='isoorientin' and r['route'].endswith('properties'))
 row={'task':T,'agent_role':'A4','extraction_id':'A4-PubChem-property-complete-20261012',
  'reaction_id':'PMC13564134-GyCGT1-LUTEOLIN-6C-ISOORIENTIN',
  'input_manifest_sha':sha(PRE),'read_other_extractor_output':False,
  'source_DOI':'10.1016/j.abiote.2026.100085','source_PMCID':'PMC13564134',
  'acceptor_smiles':docs['luteolin']['SMILES'],'donor_smiles':docs['UDP-glucose']['SMILES'],
  'product_smiles':docs['isoorientin']['SMILES'],'bond_atoms':bd,'site':'C6',
  'sugar_identity':'beta-D-glucopyranose',
  'anomer_stereo':'beta-D-glucopyranosyl; PubChem CID114776 (2S,3R,4R,5S,6R)',
  'direction':'acceptor+donor->product','step_count':1,
  'evidence_location':'PMC13564134 Results/Discussion GyCGT1 and one-step isoorientin biosynthesis + PubChem CID114776 IUPAC locant 6 and stereochemical 2S3R4R5S6R; PUG published authority',
  'structure_origin':'authoritative_structure_database_identity_chain',
  'identity_chain':{'original_DOI':'10.1016/j.abiote.2026.100085',
      'original_PMCID':'PMC13564134',
      'source_named_compounds':['luteolin','UDP-glucose','isoorientin'],
      'authoritative_CIDs':prep['authoritative_cids'],
      'source_original_SHA256':prep['source_original_SHA']},
  'structure_evidence_pointer':{'path':str(Path(src['path'])),'sha256':src['sha256']},
  'supplementary_authority_pointers':{k:{'path':v['source'],'sha256':v['source_sha256']} for k,v in forms.items()},
  'reference_precursors':[docs['luteolin']['SMILES'],docs['UDP-glucose']['SMILES']],
  'named_compound_graphs':forms,
  'product_C6_aromatic_index_in_property_SMILES':ar,'product_glucose_C1_index_in_property_SMILES':an,
  'source_product_formula':'C21H20O11','source_product_exact_mass':float(docs['isoorientin']['ExactMass']),
  'chemical_name_IUPAC_site_match':True,
  'cleaved_flavone_fragment_identical_to_authoritative_luteolin':True,
  'full_molecular_graphs_source_authenticated':True,
  'full_source_record_requires_independent_A5':True,
  'read_model_outcome':False,'human_reviewed':False,'fresh_admitted':False}
 p=O/'C_PMC13564134_A4_PubChem_property_full_graph.json'
 if (ROOT/p).exists():raise RuntimeError('immutable')
 write(T,str(p),json.dumps(row,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_A4_PubChem_complete_property_graph',sha256=sha(p),C6_site=ar,glycoC1=an)
 print(json.dumps({'A4_full_graph_source':True,'luteolin_fragment_match':True,'C6_bond_indices':bonds,'IUPAC':docs['isoorientin']['IUPACName']},ensure_ascii=False))
if __name__=='__main__':main()
