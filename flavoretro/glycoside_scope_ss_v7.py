"""P7 source-qualified sugar O6 scope guards; no scientific assets in code."""
from rdkit import Chem
from .reviewed_resources import canonical_side
from .open_glycoside_library import normalize_species
from . import glycoside_library as v2
from rdkit.Chem import rdChemReactions

# Complete source-parent beta-D-Glcp. The mapped site is the free exocyclic O6.
PARENT_BETA_D_GLC = "*[O:11][C@@H:1]1[O:5][C@H:4]([CH2:6][OH:16])[C@@H:3]([OH])[C@H:2]([OH])[C@H:7]1[OH]"
O6_CENTERS = frozenset({"flavanone_glucoside_O6_rhamnosyl", "flavone_glucoside_O6_rhamnosyl", "flavonol_glucoside_O6_rhamnosyl"})

def source_parent_sites(acceptor):
    query = Chem.MolFromSmarts(PARENT_BETA_D_GLC)
    index = next(a.GetIdx() for a in query.GetAtoms() if a.GetAtomMapNum() == 16)
    return {match[index] for match in acceptor.GetSubstructMatches(query, useChirality=True)}

def scope_center_allowed(template, target, products):
    scope = template.get("scope") or {}
    if scope.get("namespace") != "task016_p7":
        return False
    if scope.get("center_class") not in O6_CENTERS or len(products) != 2:
        return False
    acceptor, donor = products
    donor_smi = canonical_side([Chem.MolToSmiles(donor, isomericSmiles=True)])
    if donor_smi != template["donor"]:
        return False
    if not any(acceptor.HasSubstructMatch(Chem.MolFromSmarts(core), useChirality=True)
               for core in scope["acceptor_cores"]):
        return False
    sites = source_parent_sites(acceptor)
    if not sites:
        return False
    # Atom maps assigned by a reaction are intentionally irrelevant to graph identity.
    a = Chem.Mol(acceptor); t = Chem.Mol(target)
    for mol in (a,t):
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(0)
    # Verify full covalent acceptor conservation and identify exactly one transferred
    # side. This avoids broad ring-carbon matching or substitution of the true donor.
    for match in t.GetSubstructMatches(a, useChirality=True, uniquify=False, maxMatches=100):
        inside = set(match)
        added = set(range(t.GetNumAtoms())) - inside
        links = [bond for bond in t.GetBonds()
                 if (bond.GetBeginAtomIdx() in inside) != (bond.GetEndAtomIdx() in inside)]
        if len(links) != 1 or not added:
            continue
        bond = links[0]
        if bond.GetBondType() != Chem.BondType.SINGLE:
            continue
        anomer = bond.GetBeginAtomIdx() if bond.GetBeginAtomIdx() in added else bond.GetEndAtomIdx()
        site = bond.GetOtherAtomIdx(anomer)
        if site not in {match[i] for i in sites} or t.GetAtomWithIdx(anomer).GetAtomicNum() != 6:
            continue
        if t.GetAtomWithIdx(anomer).GetChiralTag() == Chem.ChiralType.CHI_UNSPECIFIED:
            continue
        # Entire transferred glycan must occur in the complete explicit donor.
        fragment_map = {}
        fragment = Chem.PathToSubmol(t, [b.GetIdx() for b in t.GetBonds()
              if b.GetBeginAtomIdx() in added and b.GetEndAtomIdx() in added], atomMap=fragment_map)
        if anomer not in fragment_map:
            continue
        fragment.GetAtomWithIdx(fragment_map[anomer]).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
        if donor.HasSubstructMatch(fragment, useChirality=True):
            return True
    return False

def apply_template(template,target,context=None):
    if context is not None and context != template["required_context"]:
        return []
    normalized=normalize_species(target)["normalized"]
    if template["template_role"]=="exact_instance_template" and normalized not in template["allowed_targets"]:
        return []
    mol=Chem.MolFromSmiles(normalized)
    rxn=rdChemReactions.ReactionFromSmarts(template["smarts"])
    rxn.GetSubstructParams().useChirality=True
    outputs=[]
    for ix,products in enumerate(rxn.RunReactants([mol])):
        try:
            for product in products:
                Chem.SanitizeMol(product)
            v2.restore_conserved_double_bond_stereo(products,mol)
            if scope_center_allowed(template,mol,products):
                value=canonical_side([Chem.MolToSmiles(p,isomericSmiles=True) for p in products])
                if value: outputs.append({"outcome_index":ix,"precursors":value})
        except (ValueError,RuntimeError):
            continue
    return outputs
