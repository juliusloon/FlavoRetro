"""Encode fully named source compounds; not a source of invented assays."""
from rdkit import Chem
from flavoretro.open_glycoside_library import structural_formation
from flavoretro.topology import audit
CORE='O=[c:4]1[cH:3][c:2](-[c:101]2[cH:102][cH:103][cH:104][cH:105][cH:106]2)[o:1][c:109]2[cH:8][cH:7][cH:6][cH:5][c:110]12'
def named_flavone(hydroxyls,methoxys=()):
    rw=Chem.RWMol(Chem.MolFromSmiles(CORE));positions={a.GetAtomMapNum():a.GetIdx() for a in rw.GetAtoms()}
    for pos in [*hydroxyls,*methoxys]:
        a=rw.GetAtomWithIdx(positions[pos]);a.SetNumExplicitHs(0)
        o=rw.AddAtom(Chem.Atom('O'));rw.AddBond(a.GetIdx(),o,Chem.BondType.SINGLE)
        if pos in methoxys:
            c=rw.AddAtom(Chem.Atom('C'));rw.AddBond(o,c,Chem.BondType.SINGLE)
    m=rw.GetMol();Chem.SanitizeMol(m)
    for a in m.GetAtoms():a.SetAtomMapNum(0)
    return Chem.MolToSmiles(m,isomericSmiles=True)
def position_oxygen(smiles,pos):
    mol=Chem.MolFromSmiles(smiles);q=Chem.MolFromSmarts(CORE.replace('cH','c'))
    matches=mol.GetSubstructMatches(q,uniquify=False)
    if not matches:raise ValueError('named flavone core not present')
    pi=next(a.GetIdx() for a in q.GetAtoms() if a.GetAtomMapNum()==pos)
    oxygens=set()
    for match in matches:
        oxygens.update(a.GetIdx() for a in mol.GetAtomWithIdx(match[pi]).GetNeighbors() if a.GetAtomicNum()==8 and a.GetDegree()==1)
    if not oxygens:raise ValueError('position oxygen not resolved')
    if len(oxygens)>1:
        signatures=set()
        for idx in oxygens:
            labelled=Chem.Mol(mol);labelled.GetAtomWithIdx(idx).SetIsotope(999)
            signatures.add(Chem.MolToSmiles(labelled,isomericSmiles=True))
        if len(signatures)!=1:raise ValueError('position oxygen not uniquely resolved')
    return min(oxygens)
def glycan_stub(acceptor,donor,product):
    result=structural_formation(acceptor,donor,product);center=result['product_atom_indices'];keep=set(center['added'])|{center['acceptor_site']}
    rw=Chem.RWMol(Chem.MolFromSmiles(product));stub=rw.GetAtomWithIdx(center['acceptor_site']);stub.SetAtomicNum(0);stub.SetIsAromatic(False);stub.SetFormalCharge(0);stub.SetNumExplicitHs(0);stub.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    for idx in reversed(range(rw.GetNumAtoms())):
        if idx not in keep:rw.RemoveAtom(idx)
    mol=rw.GetMol();Chem.SanitizeMol(mol)
    return Chem.MolToSmiles(mol,isomericSmiles=True)
def attach_stub(acceptor,stub,site):
    a=Chem.MolFromSmiles(acceptor);g=Chem.MolFromSmiles(stub)
    outcomes=Chem.ReplaceSubstructs(g,Chem.MolFromSmarts('[#0]'),a,replacementConnectionPoint=site,replaceAll=True)
    if len(outcomes)!=1:raise ValueError('attachment ambiguous')
    p=outcomes[0];Chem.SanitizeMol(p);return Chem.MolToSmiles(p,isomericSmiles=True)
def glucoside_2_oxygen(smiles):
    mol=Chem.MolFromSmiles(smiles);sites=[s for s in audit(smiles)['sites'] if s['family']=='aryl_O_candidate' and s['sugar_ring_size']==6]
    if len(sites)!=1:raise ValueError('multiple/absent aryl glucosides')
    ano=sites[0]['anomeric_candidate'];ring=next(r for r in mol.GetRingInfo().AtomRings() if ano in r and len(r)==6 and sum(mol.GetAtomWithIdx(i).GetAtomicNum()==8 for i in r)==1)
    c2=next(a for a in mol.GetAtomWithIdx(ano).GetNeighbors() if a.GetAtomicNum()==6 and a.GetIdx() in ring)
    oxy=[a.GetIdx() for a in c2.GetNeighbors() if a.GetAtomicNum()==8 and a.GetIdx() not in ring and a.GetDegree()==1]
    if len(oxy)!=1:raise ValueError('sugar 2 hydroxyl not uniquely resolved')
    return oxy[0]
def convert_C_glucose(product,to):
    mol=Chem.MolFromSmiles(product);site=next(s for s in audit(product)['sites'] if s['family']=='aryl_C_candidate');c1=site['anomeric_candidate']
    ring=next(r for r in mol.GetRingInfo().AtomRings() if c1 in r and len(r)==6 and sum(mol.GetAtomWithIdx(i).GetAtomicNum()==8 for i in r)==1)
    path=[c1]
    while len(path)<5:
        ns=[a.GetIdx() for a in mol.GetAtomWithIdx(path[-1]).GetNeighbors() if a.GetIdx() in ring and a.GetAtomicNum()==6 and a.GetIdx() not in path]
        if len(ns)!=1:raise ValueError('sugar ring numbering ambiguous')
        path.append(ns[0])
    rw=Chem.RWMol(mol)
    if to=='galactose':rw.GetAtomWithIdx(path[3]).InvertChirality()
    elif to=='xylose':
        c5=rw.GetAtomWithIdx(path[4]);c6=next(a for a in c5.GetNeighbors() if a.GetIdx() not in ring and a.GetAtomicNum()==6);o6=next(a for a in c6.GetNeighbors() if a.GetAtomicNum()==8)
        c5.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED);c5.SetNumExplicitHs(2)
        for idx in sorted([c6.GetIdx(),o6.GetIdx()],reverse=True):rw.RemoveAtom(idx)
    else:raise ValueError('unsupported sugar change')
    m=rw.GetMol();Chem.SanitizeMol(m);return Chem.MolToSmiles(m,isomericSmiles=True)
