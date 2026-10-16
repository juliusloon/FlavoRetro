"""A5 independent full source graph: PubChem PC_Compound raw atom/bond table and 'SMILES Absolute'.
Never read A4 output/property files; reconstruct 3 graphs and source-stable original PUG AIDs.
"""
import hashlib,json,sys,re
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors,Descriptors
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
PRE=O/'C_PMC13564134_A0_PubChem_three_complete_graph_inputs.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def lookup_prop(obj,label,name):
 vals=[p['value'].get('sval') for p in obj['props'] if p.get('urn',{}).get('label')==label and (p.get('urn',{}).get('name') or '')==name]
 assert len(vals)==1,(label,name,len(vals))
 return vals[0]
def record_to_rdkit(comp):
 atoms=comp['atoms'];bonds=comp['bonds'];rw=Chem.RWMol();aid_map={}
 for aid,el in zip(atoms['aid'],atoms['element']):
  if el==1:continue
  a=Chem.Atom(int(el));a.SetIntProp('official_pubchem_aid',int(aid))
  aid_map[int(aid)]=rw.AddAtom(a)
 for u,v,order in zip(bonds['aid1'],bonds['aid2'],bonds['order']):
  if u not in aid_map or v not in aid_map:continue
  rw.AddBond(aid_map[int(u)],aid_map[int(v)],
     {1:Chem.BondType.SINGLE,2:Chem.BondType.DOUBLE,3:Chem.BondType.TRIPLE}[order])
 mol=rw.GetMol();Chem.SanitizeMol(mol)
 return mol
def main():
 pre=json.loads((ROOT/PRE).read_text())
 data={};payloads={};recordmol={}
 for r in pre['structure_requests']:
  if r['route']!='PubChem_PUG_name_to_molecule_record':continue
  p=Path(r['path']);assert sha(p)==r['sha256']
  x=json.loads((ROOT/p).read_text())['PC_Compounds'][0]
  assert x['id']['id']['cid']==pre['authoritative_cids'][r['name']]
  absolute=lookup_prop(x,'SMILES','Absolute')
  ipn=lookup_prop(x,'IUPAC Name','Preferred')
  formula=lookup_prop(x,'Molecular Formula','')
  m=Chem.MolFromSmiles(absolute)
  assert m and rdMolDescriptors.CalcMolFormula(m)==formula
  mr=record_to_rdkit(x)
  assert rdMolDescriptors.CalcMolFormula(mr)==formula
  assert Chem.MolToSmiles(m,isomericSmiles=False)==Chem.MolToSmiles(mr,isomericSmiles=False)
  data[r['name']]={'path':str(p),'raw_sha256':sha(p),'CID':x['id']['id']['cid'],
   'official_Absolute_SMILES':absolute,'canon_isomeric_SMILES':Chem.MolToSmiles(m,isomericSmiles=True),
   'formula':formula,'exact_mass':round(Descriptors.ExactMolWt(m),8),
   'original_PUG_IUPAC':ipn,'official_record_atom_ids':len(x['atoms']['aid']),
   'official_record_bonds':len(x['bonds']['aid1']),'source_tetrahedral_stereocenters':len(x.get('stereo',[]))}
  payloads[r['name']]=x;recordmol[r['name']]=mr
 assert len(data)==3
 # SOURCE ATOM ID: product original PubChem atom-bond table has unique C(sp2)-C(sp3 ring glucopyranosyl) bridge
 product=recordmol['isoorientin']
 candidates=[]
 for b in product.GetBonds():
  for ar,sg in ((b.GetBeginAtom(),b.GetEndAtom()),(b.GetEndAtom(),b.GetBeginAtom())):
   if (ar.GetIsAromatic() and sg.GetAtomicNum()==6 and not sg.GetIsAromatic() and
       sg.IsInRingSize(6) and any(n.GetAtomicNum()==8 and n.IsInRingSize(6) for n in sg.GetNeighbors())):
    candidates.append({'aromatic_aid':ar.GetIntProp('official_pubchem_aid'),
      'glyco_c1_aid':sg.GetIntProp('official_pubchem_aid'),'indices':(ar.GetIdx(),sg.GetIdx())})
 assert len(candidates)==1,candidates
 c=candidates[0]
 rd=Chem.RWMol(product);rd.RemoveBond(*c['indices'])
 frags=Chem.GetMolFrags(rd.GetMol(),asMols=True,sanitizeFrags=True)
 lut=recordmol['luteolin']
 assert len(frags)==2 and any(Chem.MolToSmiles(f,isomericSmiles=False)==Chem.MolToSmiles(lut,isomericSmiles=False) for f in frags)
 # donor source atom mapping using six-membered sugar ring: C1 has exocyclic O attached to phosphorus
 m=recordmol['UDP-glucose'];g1=[]
 for ring in m.GetRingInfo().AtomRings():
  if len(ring)!=6:continue
  atoms=[m.GetAtomWithIdx(i) for i in ring]
  if sum(a.GetAtomicNum()==8 for a in atoms)!=1:continue
  for a in atoms:
   if a.GetAtomicNum()!=6:continue
   for o in a.GetNeighbors():
    if o.GetAtomicNum()!=8 or o.GetIdx() in ring:continue
    if any(n.GetAtomicNum()==15 for n in o.GetNeighbors()):
     g1.append({'glucose_C1_aid':a.GetIntProp('official_pubchem_aid'),
       'phosphate_ester_O_aid':o.GetIntProp('official_pubchem_aid')})
 assert len(g1)==1,g1
 assert re.search(r'-6-\[',data['isoorientin']['original_PUG_IUPAC'])
 assert '2S,3R,4R,5S,6R' in data['isoorientin']['original_PUG_IUPAC']
 official={'product':c,'donor':g1[0]}
 bd={'acceptor_atom':'PubChemCID5280445:luteolin:ring-C6',
     'donor_atom':'PubChemCID8629:UDP-alpha-D-glucose:sugar-C1',
     'product_atoms':['PubChemCID114776:flavone-ring-C6','PubChemCID114776:glucose-ring-C1']}
 row={'task':T,'agent_role':'A5','extraction_id':'A5-PubChem-atomic-bond-record-20261012',
  'reaction_id':'PMC13564134-GyCGT1-LUTEOLIN-6C-ISOORIENTIN',
  'input_manifest_sha':sha(PRE),'read_other_extractor_output':False,
  'source_DOI':'10.1016/j.abiote.2026.100085','source_PMCID':'PMC13564134',
  'acceptor_smiles':data['luteolin']['official_Absolute_SMILES'],
  'donor_smiles':data['UDP-glucose']['official_Absolute_SMILES'],
  'product_smiles':data['isoorientin']['official_Absolute_SMILES'],
  'bond_atoms':bd,'site':'C6','sugar_identity':'beta-D-glucopyranose',
  'anomer_stereo':'beta-D-glucopyranosyl; PubChem CID114776 (2S,3R,4R,5S,6R)',
  'direction':'acceptor+donor->product','step_count':1,
  'evidence_location':'PMC13564134 original enzyme paragraph + PubChem CID114776 PC_Compound original bond aid pair, CID8629 original C1-O-P bond, absolute stereo SMILES/IUPAC',
  'structure_origin':'authoritative_structure_database_identity_chain',
  'identity_chain':{'original_DOI':'10.1016/j.abiote.2026.100085',
     'original_PMCID':'PMC13564134','source_named_compounds':['luteolin','UDP-glucose','isoorientin'],
     'authoritative_CIDs':pre['authoritative_cids'],
     'source_original_SHA256':pre['source_original_SHA']},
  'structure_evidence_pointer':{'path':data['isoorientin']['path'],'sha256':data['isoorientin']['raw_sha256']},
  'supplementary_authority_pointers':{k:{'path':v['path'],'sha256':v['raw_sha256']} for k,v in data.items()},
  'reference_precursors':[data['luteolin']['official_Absolute_SMILES'],data['UDP-glucose']['official_Absolute_SMILES']],
  'named_compound_graphs':data,'source_PubChem_record_native_atom_id_evidence':official,
  'original_atom_table_non_stereo_topology_derived_independently':True,
  'original_record_absolute_SMILES_stereo_source_verifiable':True,
  'source_product_formula':data['isoorientin']['formula'],
  'source_product_exact_mass':data['isoorientin']['exact_mass'],
  'read_model_outcome':False,'human_reviewed':False,'fresh_admitted':False}
 dest=O/'C_PMC13564134_A5_PubChem_atom_record_full_graph.json'
 if (ROOT/dest).exists():raise RuntimeError('immutable')
 write(T,str(dest),json.dumps(row,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'C_PMC13564134_A5_original_PC_Compound_atom_site_verified',record_sha=sha(dest),
   product_aromatic_aid=c['aromatic_aid'],product_C1_aid=c['glyco_c1_aid'],donor_C1_aid=g1[0]['glucose_C1_aid'])
 print(json.dumps({'A5_full_graph_source':True,'native_bond_PubChem_atom_ids':official,
   'product_formula':data['isoorientin']['formula']},ensure_ascii=False))
if __name__=='__main__':main()
