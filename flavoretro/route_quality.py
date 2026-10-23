"""Structural route diagnostics. These labels do not establish chemical feasibility."""
from functools import lru_cache
import hashlib,json
from rdkit import Chem

_ACETYL=Chem.MolFromSmarts('[O;X2:1]-[C;X3:2](=[O;X1:3])-[CH3:4]')

@lru_cache(maxsize=16384)
def canonical(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:raise ValueError('invalid route molecule')
    for atom in mol.GetAtoms():atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol,isomericSmiles=True)

@lru_cache(maxsize=16384)
def acetate_skeleton(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:raise ValueError('invalid route molecule')
    # Strip only a bounded O-acetyl motif. Never strip sugar, methyl ether,
    # anomeric halide, benzyl or other groups using a guessed general rule.
    remove=set();count=0
    for oxygen,carbon,oxo,methyl in mol.GetSubstructMatches(_ACETYL):
        if mol.GetAtomWithIdx(oxygen).IsInRing() or mol.GetAtomWithIdx(carbon).IsInRing():continue
        if mol.GetAtomWithIdx(oxygen).GetDegree()!=2:continue
        other=next(a for a in mol.GetAtomWithIdx(oxygen).GetNeighbors() if a.GetIdx()!=carbon)
        if other.GetAtomicNum()!=6 or any(b.GetBondType()==Chem.BondType.DOUBLE and b.GetOtherAtom(other).GetAtomicNum()==8 for b in other.GetBonds()):continue
        remove.update([carbon,oxo,methyl]);count+=1
    edit=Chem.RWMol(mol)
    for index in sorted(remove,reverse=True):edit.RemoveAtom(index)
    value=edit.GetMol();Chem.SanitizeMol(value)
    for atom in value.GetAtoms():atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(value,isomericSmiles=True),count


def protection_only(product,precursors):
    core,p=acetate_skeleton(product)
    return any(acetate_skeleton(s)[0]==core and acetate_skeleton(s)[1]!=p for s in precursors)


def source_supported(metadata):
    source=metadata.get('task022_evidence') or {}
    return bool((source.get('source_reconstruction') and source.get('exact_source_instance_match')) or metadata.get('review',{}).get('source_instance_supported'))


def diagnostics(tree):
    critical=[];protection=source=steps=revisits=0
    def walk(node,parent=None,ancestors=()):
        nonlocal protection,source,steps,revisits
        if node.get('type')=='mol':
            key=canonical(node['smiles']);revisits+=int(key in ancestors)
            ancestors=ancestors+(key,)
        if node.get('type')=='reaction':
            steps+=1;metadata=node.get('metadata',{})
            source+=int(source_supported(metadata) or bool(node.get('review',{}).get('source_instance_supported')))
            prec=[child['smiles'] for child in node.get('children',[]) if child.get('type')=='mol']
            if parent and protection_only(parent,prec):protection+=1
            elif parent:critical.append((acetate_skeleton(parent)[0],tuple(sorted(acetate_skeleton(s)[0] for s in prec))))
        for child in node.get('children',[]):walk(child,node.get('smiles') if node.get('type')=='mol' else parent,ancestors)
    walk(tree)
    family=hashlib.sha256(json.dumps(sorted(critical),sort_keys=True).encode()).hexdigest()
    return {'family_id':family,'protection_only_steps':protection,'source_supported_steps':source,
            'source_step_coverage':source/max(steps,1),'exact_ancestor_revisits':revisits,
            'family_method':'critical_edges_O_acetyl_stripped_v1','chemical_validation':False}


def diverse_top(routes,k):
    ordered=sorted(routes,key=lambda r:(-r['score'],r['route_id']))
    selected=[];seen=set()
    for row in ordered:
        family=row.get('route_quality',{}).get('family_id',row['route_id'])
        if family in seen:continue
        selected.append(row);seen.add(family)
        if len(selected)>=k:return selected
    chosen={row['route_id'] for row in selected}
    selected.extend(row for row in ordered if row['route_id'] not in chosen)
    return sorted(selected[:k],key=lambda r:(-r['score'],r['route_id']))


def material_subgoal(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:return {'kind':'structure_repair','next_step':'先修复结构身份。'}
    if sum(a.GetAtomicNum()==15 for a in mol.GetAtoms())>=2:
        return {'kind':'activated_nucleotide_sugar','next_step':'核查该完整活化糖供体的制备或再生路线、盐型与当前供应；保持异头构型，不以游离糖替代。','current_supply':'unverified'}
    if any(a.GetAtomicNum()==35 for a in mol.GetAtoms()) and any(len(r)==6 for r in mol.GetRingInfo().AtomRings()):
        return {'kind':'glycosyl_halide','next_step':'继续规划该糖基卤化物，核查保护状态、异头构型及制备来源。','current_supply':'unverified'}
    return {'kind':'unresolved_precursor','next_step':'对该精确前体继续逆合成，并核查来源与当前供应。','current_supply':'unverified'}
