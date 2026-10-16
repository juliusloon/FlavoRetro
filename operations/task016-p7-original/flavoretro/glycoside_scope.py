"""P6 structural guards, panel completeness and independent scientific preflights.

These checks certify encoded objects and declared graph scope only. They do not
certify enzyme activity, experimental conditions or independent chemistry.
"""
from rdkit import Chem
from rdkit.Chem import rdFMCS, rdChemReactions
from .reviewed_resources import canonical_side, reaction_signature
FLAVONOL = "O=c1c(O)c(-c2ccccc2)oc2ccccc12"

def c8_sites(mol):
    """Locate A-ring C8 through the pyrone oxygen and its fused neighbour."""
    sites = set()
    rings = mol.GetRingInfo().AtomRings()
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() != 8 or not atom.IsInRing() or atom.GetDegree() != 2:
            continue
        for fusion in atom.GetNeighbors():
            if fusion.GetAtomicNum() != 6 or not fusion.GetIsAromatic():
                continue
            if sum(fusion.GetIdx() in ring for ring in rings) < 2:
                continue
            for n in fusion.GetNeighbors():
                if n.GetAtomicNum() == 6 and n.GetIsAromatic() and sum(n.GetIdx() in ring for ring in rings) == 1:
                    sites.add(n.GetIdx())
    return sites

def c_scope_allowed(t, target, products):
    if len(products) != 2:
        return False
    acceptor, donor = products
    if canonical_side([Chem.MolToSmiles(donor, isomericSmiles=True)]) != t["donor"]:
        return False
    if not acceptor.HasSubstructMatch(Chem.MolFromSmarts(FLAVONOL)):
        return False
    mcs = rdFMCS.FindMCS([acceptor,target], timeout=5, ringMatchesRingOnly=True,
                         completeRingsOnly=True, bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms != acceptor.GetNumAtoms():
        return False
    query = Chem.MolFromSmarts(mcs.smartsString)
    for conserved in target.GetSubstructMatches(query, useChirality=True):
        inside = set(conserved)
        added = set(range(target.GetNumAtoms())) - inside
        if len(added) != 11:
            continue
        links = [b for b in target.GetBonds() if (b.GetBeginAtomIdx() in inside) != (b.GetEndAtomIdx() in inside)]
        if len(links) != 1:
            continue
        link = links[0]
        site = link.GetBeginAtomIdx() if link.GetBeginAtomIdx() in inside else link.GetEndAtomIdx()
        ano = link.GetOtherAtomIdx(site)
        if site not in c8_sites(target) or target.GetAtomWithIdx(ano).GetAtomicNum() != 6:
            continue
        if target.GetAtomWithIdx(ano).GetChiralTag() == Chem.ChiralType.CHI_UNSPECIFIED:
            continue
        return True
    return False

def apply_c_scope(t, target, context=None):
    if context is not None and context != t["required_context"]:
        return []
    mol = Chem.MolFromSmiles(target)
    if mol is None:
        return []
    rxn = rdChemReactions.ReactionFromSmarts(t["scope_template"])
    rxn.GetSubstructParams().useChirality = True
    results = []
    for index, products in enumerate(rxn.RunReactants((mol,))):
        try:
            for p in products:
                Chem.SanitizeMol(p)
            if c_scope_allowed(t, mol, products):
                results.append(dict(outcome_index=index, precursors=canonical_side([Chem.MolToSmiles(p,isomericSmiles=True) for p in products])))
        except (RuntimeError, ValueError):
            continue
    return results

def runtime_complete(record):
    if not record.get("structure_complete") or record.get("inferred") or record.get("deferred"):
        return False
    if record.get("structure_origin") in ("handwritten_from_name", "model_memory", None):
        return False
    for field in ("product_smiles", "reference_precursors", "canonical_reaction_signature", "closure_group", "source_binding"):
        if not record.get(field):
            return False
    if not record["source_binding"].get("metadata_verified"):
        return False
    values = [record["product_smiles"]] + record["reference_precursors"]
    for s in values:
        mol = Chem.MolFromSmiles(s)
        if mol is None or any(a.GetNumRadicalElectrons() for a in mol.GetAtoms()):
            return False
        if any(a.GetChiralTag() == Chem.ChiralType.CHI_UNSPECIFIED for a in mol.GetAtoms() if a.GetAtomicNum() == 6 and a.GetIdx() in dict(Chem.FindMolChiralCenters(mol, includeUnassigned=True))):
            return False
    return record["canonical_reaction_signature"] == reaction_signature([canonical_side(record["reference_precursors"])], [canonical_side([record["product_smiles"]])])

def panel_preflight(records, build_signatures, build_closures):
    complete = [r for r in records if runtime_complete(r)]
    signatures = [r["canonical_reaction_signature"] for r in complete]
    leakage = sorted(set(signatures) & set(build_signatures))
    closure_leakage = sorted({r["closure_group"] for r in complete} & set(build_closures))
    groups = {r["closure_group"] for r in complete}
    passed = 6 <= len(complete) <= 9 and len(groups) >= 2 and not leakage and not closure_leakage and len(set(signatures)) == len(signatures)
    return dict(passed=passed, targets=len(complete), closure_groups=len(groups),
                reaction_leakage=leakage, closure_leakage=closure_leakage,
                duplicate_reactions=len(signatures)-len(set(signatures)), runtime_executable_percent=100 if complete else None)

def independently_runnable(preflights):
    return [family for family,p in preflights.items() if p.get("passed")]

def source_identity_eligible(claim, verified):
    fields = ("pmcid", "title", "doi", "journal")
    return all(claim.get(f) and claim[f] == verified.get(f) for f in fields) and bool(verified.get("publication_metadata_verified"))

def transfer_trace_eligible(cells):
    if len(cells) != 9 or {(c.get("arm"),c.get("seed")) for c in cells} != {(a,s) for a in ("A","B","E") for s in (0,1,2)}:
        return False
    for c in cells:
        if c.get("status") != "ok":
            return False
        if c["arm"] == "E":
            if c.get("exact_seed_instance_match") is not False or not c.get("reference_node_created") or not any(e.get("stage") == "mcts_action_created" and e.get("signature") == c.get("reference_signature") and e.get("signature") and e.get("created_node_count", 0) > 0 and isinstance(e.get("created_node_index"), int) for e in c.get("node_trace", [])):
                return False
        elif c.get("reference_node_created"):
            return False
    return True
