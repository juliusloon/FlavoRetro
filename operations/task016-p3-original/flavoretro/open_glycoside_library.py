"""Versioned source species representation and single-step structural admission.

These checks establish structural consistency; assay support is supplied separately.
"""
from rdkit import Chem
from rdkit.Chem import rdFMCS
from flavoretro.reviewed_resources import canonical_side,reaction_signature
REPRESENTATION_VERSION='acid-oxygen-protonation-v1'
def normalize_species(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:raise ValueError('invalid source SMILES')
    changes=[]
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
        # Acid/base representations only; never remove salts or alter covalent bonds.
        if atom.GetAtomicNum()==8 and atom.GetFormalCharge()==-1 and atom.GetDegree()==1:
            bond=atom.GetBonds()[0];neighbor=atom.GetNeighbors()[0]
            acidic=(neighbor.GetAtomicNum()==15 or neighbor.GetIsAromatic() or
                     (neighbor.GetAtomicNum()==6 and any(b.GetBondType()==Chem.BondType.DOUBLE and b.GetOtherAtom(neighbor).GetAtomicNum()==8 for b in neighbor.GetBonds())))
            if acidic and bond.GetBondType()==Chem.BondType.SINGLE:
                changes.append(dict(atom_index=atom.GetIdx(),element='O',formal_charge_before=-1,formal_charge_after=0,explicit_h_before=atom.GetNumExplicitHs(),explicit_h_after=1,acid_neighbor_element=neighbor.GetSymbol()))
                atom.SetFormalCharge(0);atom.SetNumExplicitHs(1);atom.SetNoImplicit(True)
    Chem.SanitizeMol(mol)
    return dict(original=canonical_side([smiles]),normalized=Chem.MolToSmiles(mol,isomericSmiles=True),changes=changes,rule_version=REPRESENTATION_VERSION,interpretation='representational parent; physical predominant species/pKa not inferred')
def covalent_signature(acceptor,donor,target):
    return reaction_signature([normalize_species(acceptor)['normalized'],normalize_species(donor)['normalized']],[normalize_species(target)['normalized']])
def structural_formation(acceptor,donor,target):
    a,d,p=[Chem.MolFromSmiles(s) for s in [acceptor,donor,target]]
    if any(m is None for m in [a,d,p]):raise ValueError('invalid participants')
    if len(Chem.GetMolFrags(a))!=1 or len(Chem.GetMolFrags(d))!=1 or len(Chem.GetMolFrags(p))!=1:raise ValueError('multi-component participant unresolved')
    common=rdFMCS.FindMCS([a,p],timeout=3,ringMatchesRingOnly=True,completeRingsOnly=True,bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if common.canceled or common.numAtoms!=a.GetNumAtoms() or not p.HasSubstructMatch(a,useChirality=True):raise ValueError('acceptor not fully conserved including stereochemistry in one step')
    q=Chem.MolFromSmarts(common.smartsString);found=[]
    for conserved in p.GetSubstructMatches(q,maxMatches=128):
        inside=set(conserved);added=set(range(p.GetNumAtoms()))-inside
        links=[b for b in p.GetBonds() if (b.GetBeginAtomIdx() in inside)!=(b.GetEndAtomIdx() in inside)]
        if len(links)!=1 or not added:continue
        b=links[0];anomeric=b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in added else b.GetEndAtomIdx();site=b.GetOtherAtomIdx(anomeric)
        if p.GetAtomWithIdx(anomeric).GetAtomicNum()!=6:continue
        fragment_map={}
        glycan=Chem.PathToSubmol(p,[b.GetIdx() for b in p.GetBonds() if b.GetBeginAtomIdx() in added and b.GetEndAtomIdx() in added],atomMap=fragment_map)
        # The anomeric configuration can invert during UDP transfer; other sugar stereocenters cannot.
        glycan.GetAtomWithIdx(fragment_map[anomeric]).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
        if not d.HasSubstructMatch(glycan,useChirality=True):continue
        siteatom=p.GetAtomWithIdx(site)
        if siteatom.GetAtomicNum()==6 and siteatom.GetIsAromatic():family='C_formation'
        elif siteatom.GetAtomicNum()==8:
            other=[x for x in siteatom.GetNeighbors() if x.GetIdx()!=anomeric]
            if len(other)!=1:continue
            family='O_formation' if other[0].GetIsAromatic() else 'sugar_sugar_formation' if other[0].IsInRing() and other[0].GetAtomicNum()==6 else 'unresolved_O_formation'
        else:continue
        found.append(dict(family=family,product_atom_indices=dict(acceptor_site=site,anomeric=anomeric,added=sorted(added)),bond_type=str(b.GetBondType()),acceptor_atoms=a.GetNumAtoms(),added_atoms=len(added),direction='forward formation',validation='structural consistency only; source assay remains a separate axis'))
    if not found:raise ValueError('no single conserved glycosidic formation center')
    signatures={x['family'] for x in found}
    if len(signatures)!=1:raise ValueError('ambiguous center family')
    found.sort(key=lambda x:(x['product_atom_indices']['acceptor_site'],x['product_atom_indices']['anomeric']))
    return {**found[0],'equivalent_match_count':len(found)}
