"""Additional full-scaffold guard challenges; mutations are engineering controls, not experiments."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from rdkit import Chem
from scripts.operate import write
from flavoretro.glycoside_library_v3 import load_registry
from flavoretro.glycoside_library import apply_template
from flavoretro.open_glycoside_library import structural_formation
ROOT=Path(__file__).resolve().parents[1];registry=load_registry();checks=[]
for t in registry.templates:
 if not t['template_id'].startswith('p2-scope:'):continue
 r=registry.instances[t['support_instances'][0]];m=Chem.MolFromSmiles(r['target']);f=structural_formation(r['acceptor'],r['donor'],r['target']);idx=f['product_atom_indices'];added=set(idx['added'])
 # Changing a non-anomeric stereocenter preserves a sugar and bond but violates full donor identity.
 pos=next(a.GetIdx() for a in m.GetAtoms() if a.GetIdx() in added and a.GetIdx()!=idx['anomeric'] and a.GetChiralTag()!=Chem.ChiralType.CHI_UNSPECIFIED)
 other=Chem.Mol(m);other.GetAtomWithIdx(pos).InvertChirality();sm=Chem.MolToSmiles(other,isomericSmiles=True)
 checks.append(dict(template_id=t['template_id'],kind='wrong_inner_donor_sugar_stereo',target=sm,passed=not apply_template(t,sm)))
 if t['category']=='C_formation':
  pos=next(a.GetIdx() for a in m.GetAtoms() if a.GetIdx() not in added and a.GetChiralTag()!=Chem.ChiralType.CHI_UNSPECIFIED and any(n.GetIsAromatic() for n in a.GetNeighbors()))
  other=Chem.Mol(m);other.GetAtomWithIdx(pos).InvertChirality();sm=Chem.MolToSmiles(other,isomericSmiles=True);kind='wrong_first_C_parent_anomer'
 else:
  # Move the new bond to a different free OH on the same fully retained parent sugar.
  oxygen=next(a.GetIdx() for a in m.GetAtoms() if a.GetAtomicNum()==8 and a.GetDegree()==1 and a.GetIdx() not in added and a.GetIdx()!=idx['acceptor_site'] and a.GetNeighbors()[0].GetAtomicNum()==6 and not a.GetNeighbors()[0].GetIsAromatic())
  other=Chem.RWMol(m);other.RemoveBond(idx['anomeric'],idx['acceptor_site']);other.AddBond(idx['anomeric'],oxygen,Chem.BondType.SINGLE);Chem.SanitizeMol(other);sm=Chem.MolToSmiles(other,isomericSmiles=True);kind='different_parent_sugar_linkage_OH'
 checks.append(dict(template_id=t['template_id'],kind=kind,target=sm,passed=not apply_template(t,sm)))
report=dict(passed=all(c['passed'] for c in checks),checks=checks,additional_checks=len(checks),original_checks=12,total_new_template_boundaries=12+len(checks),actual_search_attempts=0,scope='full source-scaffold chemical-graph mutations exercise declared guards; no source-negative or wet experiment claim')
write('TASK-016-P2','outputs/task016-p2/v2/scope_boundary_validation.json',json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'}));assert report['passed'],checks
