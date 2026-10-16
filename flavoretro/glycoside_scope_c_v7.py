"""P7 C-scope guard for immutable source-derived core/site specifications."""
from rdkit import Chem
from rdkit.Chem import rdChemReactions
from .reviewed_resources import canonical_side

def c_scope_allowed(template,target,products):
    """Enforce mandatory source core, site, complete donor and conserved acceptor.

    Sugar identity/stereo is also matched by the scoped reaction with chirality;
    this guard independently rejects unspecified transferred carbon stereo.
    """
    spec=template.get("guard_spec")
    if not isinstance(spec,dict) or spec.get("kind")!="source_derived_core_site":return False
    if len(products)!=2:return False
    acceptor,donor=products
    if canonical_side([Chem.MolToSmiles(donor,isomericSmiles=True)])!=template["donor"]:return False
    query=Chem.MolFromSmarts(spec["core_query"])
    if query is None:return False
    site_index=spec["site_query_atom_index"]
    if not isinstance(site_index,int) or not 0<=site_index<query.GetNumAtoms():return False
    if query.GetAtomWithIdx(site_index).GetAtomMapNum()!=spec["site_atom_map"]:return False
    sites={m[site_index] for m in target.GetSubstructMatches(query)}
    expected_acceptor=canonical_side([Chem.MolToSmiles(acceptor,isomericSmiles=True)])
    for site in sites:
        for atom in target.GetAtomWithIdx(site).GetNeighbors():
            ano=atom.GetIdx()
            if atom.GetAtomicNum()!=6 or atom.GetIsAromatic() or atom.GetChiralTag()==Chem.ChiralType.CHI_UNSPECIFIED:continue
            bond=target.GetBondBetweenAtoms(site,ano)
            if bond.GetBondType()!=Chem.BondType.SINGLE:continue
            cut=Chem.FragmentOnBonds(target,[bond.GetIdx()],addDummies=False)
            fragments=Chem.GetMolFrags(cut,asMols=False)
            glycan=next(f for f in fragments if ano in f)
            remaining=next((f for f in fragments if site in f),None)
            if remaining is None or len(glycan)!=spec["required_transferred_atoms"]:continue
            if any(target.GetAtomWithIdx(i).GetAtomicNum()==6 and target.GetAtomWithIdx(i).GetDegree()>=3 and target.GetAtomWithIdx(i).GetChiralTag()==Chem.ChiralType.CHI_UNSPECIFIED for i in glycan):continue
            rw=Chem.RWMol(target)
            for i in sorted(glycan,reverse=True):rw.RemoveAtom(i)
            try:
                remainder=rw.GetMol();Chem.SanitizeMol(remainder)
                if canonical_side([Chem.MolToSmiles(remainder,isomericSmiles=True)])==expected_acceptor:return True
            except (ValueError,RuntimeError):continue
    return False

def apply_c_scope(template,target,context=None):
    if context is not None and context!=template["required_context"]:return []
    mol=Chem.MolFromSmiles(target)
    if mol is None:return []
    rxn=rdChemReactions.ReactionFromSmarts(template["scope_template"])
    rxn.GetSubstructParams().useChirality=True
    results=[]
    for index,products in enumerate(rxn.RunReactants((mol,))):
        try:
            for product in products:Chem.SanitizeMol(product)
            if c_scope_allowed(template,mol,products):
                results.append(dict(outcome_index=index,precursors=canonical_side([Chem.MolToSmiles(p,isomericSmiles=True) for p in products])))
        except (ValueError,RuntimeError):continue
    return results
