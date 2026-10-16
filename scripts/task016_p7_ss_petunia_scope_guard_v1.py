"""Isolated Petunia SS-O2 proposal guard; deliberately not registered at runtime.

Encoded graph-boundary checks certify neither enzyme activity nor independent
chemistry. All scientific graphs and finite sugar queries come from the external
A7 artifact derived from SHA-bound A6 design supports.
"""
from __future__ import annotations

from functools import partial
from rdkit import Chem
from rdkit.Chem import rdChemReactions

CENTER = "flavonol_3O_betaD_Glcp_or_Galp_O2_betaD_Glcp"
CORE = ("O=[c:4]1[c:3]([O:31])[c:2](-[c:101]2[c:102][c:103][c:104]"
        "[c:105][c:106]2)[o:1][c:109]2[c:8][c:7][c:6][c:5][c:110]12")


def unmap(mol):
    value = Chem.Mol(mol)
    for atom in value.GetAtoms():
        atom.SetAtomMapNum(0)
    Chem.AssignStereochemistry(value, cleanIt=True, force=True)
    return value


def canonical(mol):
    return Chem.MolToSmiles(unmap(mol), isomericSmiles=True)


def side(molecules):
    return ".".join(sorted(canonical(m) for m in molecules))


def query_matches(smarts, mol):
    query = Chem.MolFromSmarts(smarts)
    if query is None:
        return []
    labels = {a.GetAtomMapNum(): a.GetIdx() for a in query.GetAtoms() if a.GetAtomMapNum()}
    return [(set(match), {k: match[v] for k, v in labels.items()})
            for match in mol.GetSubstructMatches(query, useChirality=True,
                                                uniquify=False, maxMatches=100)]


def scope_center_allowed(template, target, products):
    """Complete precursor donor, finite sugars, exact O2 link and conserved core."""
    scope = template.get("scope") or {}
    if (template.get("template_role") != "scope_template"
            or scope.get("namespace") != "task016_p7"
            or scope.get("family") != "SS"
            or scope.get("center_class") != CENTER or len(products) != 2):
        return False
    if scope.get("parent_sugar_domain") != ["beta-D-Glcp", "beta-D-Galp"]:
        return False
    acceptor, donor = [unmap(m) for m in products]
    target = unmap(target)
    if any(len(Chem.GetMolFrags(m)) != 1 for m in (acceptor, donor, target)):
        return False
    if canonical(donor) != template["donor"]:
        return False
    core_matches = query_matches(CORE, acceptor)
    if not core_matches:
        return False
    parent_matches = []
    for entry in scope["parent_queries"]:
        for atoms, labels in query_matches(entry["smarts"], acceptor):
            # Every parent carbon must carry explicit stereochemistry, including
            # C4; the local reaction intentionally does not constrain that one.
            if any(acceptor.GetAtomWithIdx(labels[n]).GetChiralTag()
                   == Chem.ChiralType.CHI_UNSPECIFIED for n in entry["carbon_maps"]):
                continue
            for core_atoms, core_labels in core_matches:
                if (labels[entry["aglycone_owner_map"]] != core_labels[3]
                        or labels[entry["glycosidic_oxygen_map"]] != core_labels[31]):
                    continue
                allowed = atoms | core_atoms
                decorations = set()
                for atom in acceptor.GetAtoms():
                    if atom.GetIdx() in allowed:
                        continue
                    if (atom.GetAtomicNum() == 8 and atom.GetFormalCharge() == 0
                            and atom.GetDegree() == 1 and atom.GetTotalNumHs() == 1
                            and atom.GetBonds()[0].GetBondType() == Chem.BondType.SINGLE
                            and atom.GetNeighbors()[0].GetIdx() in core_atoms
                            and atom.GetNeighbors()[0].GetIsAromatic()):
                        decorations.add(atom.GetIdx())
                if allowed | decorations == set(range(acceptor.GetNumAtoms())):
                    parent_matches.append((labels[entry["O2_map"]], entry["parent"]))
    if not parent_matches:
        return False
    terminal = scope["terminal_query"]
    terminal_matches = query_matches(terminal["smarts"], target)
    for match in target.GetSubstructMatches(acceptor, useChirality=True,
                                           uniquify=False, maxMatches=100):
        inside = set(match)
        added = set(range(target.GetNumAtoms())) - inside
        if len(added) != scope["transferred_atoms"]:
            continue
        links = [b for b in target.GetBonds()
                 if (b.GetBeginAtomIdx() in inside) != (b.GetEndAtomIdx() in inside)]
        if len(links) != 1 or links[0].GetBondType() != Chem.BondType.SINGLE:
            continue
        bond = links[0]
        anomer = bond.GetBeginAtomIdx() if bond.GetBeginAtomIdx() in added else bond.GetEndAtomIdx()
        site = bond.GetOtherAtomIdx(anomer)
        if site not in {match[i] for i, _ in parent_matches}:
            continue
        if any(labels[terminal["anomer_map"]] == anomer
               and labels[terminal["site_map"]] == site
               and {labels[n] for n in terminal["added_maps"]} == added
               for _, labels in terminal_matches):
            return True
    return False


def dispatch_guard(template, target, products):
    """Proposed dispatcher branch; no monkeypatch or production registry mutation."""
    scope = template.get("scope") or {}
    if (scope.get("namespace"), scope.get("family"), scope.get("center_class")) != (
            "task016_p7", "SS", CENTER):
        return False
    return scope_center_allowed(template, target, products)


def raw_outcomes(template, target):
    mol = Chem.MolFromSmiles(target)
    if mol is None:
        return
    reaction = rdChemReactions.ReactionFromSmarts(template["smarts"])
    reaction.GetSubstructParams().useChirality = True
    for index, products in enumerate(reaction.RunReactants((mol,))):
        try:
            for product in products:
                Chem.SanitizeMol(product)
            yield index, mol, products
        except (RuntimeError, ValueError):
            continue


def apply_template(template, target, context=None):
    if context is not None and context != template["required_context"]:
        return []
    outputs = []
    for index, mol, products in raw_outcomes(template, target):
        if dispatch_guard(template, mol, products):
            outputs.append(dict(outcome_index=index, precursors=side(products)))
    return outputs


def make_reaction_class():
    """Provide the actual mapped TemplatedRetroReaction path without importing assets."""
    from aizynthfinder.chem import TemplatedRetroReaction, TreeMolecule

    class PetuniaRetroReaction(TemplatedRetroReaction):
        def _apply_with_rdkit(self):
            template = self.metadata["library_template"]
            parent = unmap(self.mol.mapped_mol)
            reaction = rdChemReactions.ReactionFromSmarts(self.smarts)
            reaction.GetSubstructParams().useChirality = True
            outcomes, raw_indices = [], []
            for raw_index, products in enumerate(reaction.RunReactants((parent,))):
                try:
                    for product in products:
                        Chem.SanitizeMol(product)
                    if not dispatch_guard(template, parent, products):
                        continue
                    callback = partial(self._inherit_atom_mapping,
                                       exclude_nums=set(self.mol.mapping_to_index.keys()))
                    value = tuple(TreeMolecule(parent=self.mol, rd_mol=p, sanitize=True,
                                               mapping_update_callback=callback)
                                  for p in products)
                    outcomes.append(value)
                    raw_indices.append(raw_index)
                except (ValueError, RuntimeError):
                    continue
            self.metadata["raw_outcome_indices"] = raw_indices
            self._reactants = tuple(outcomes)
            return self._reactants

    return PetuniaRetroReaction


def mapped_reference_path(template, target):
    """A8 can call this directly or instantiate the returned reaction class."""
    from aizynthfinder.chem import TreeMolecule
    parent = TreeMolecule(parent=None, smiles=target)
    cls = make_reaction_class()
    reaction = cls(parent, smarts=template["smarts"], use_rdchiral=False,
                   metadata={"library_template": template})
    expected_maps = set(parent.mapping_to_index)
    outputs = []
    for index, reactants in enumerate(reaction.reactants):
        values = [m for m in reactants]
        maps = [a.GetAtomMapNum() for m in values for a in m.mapped_mol.GetAtoms()]
        target_maps = [n for n in maps if n in expected_maps]
        outputs.append(dict(outcome_index=index,
                            raw_outcome_index=reaction.metadata["raw_outcome_indices"][index],
                            precursors=side([m.rd_mol for m in values]),
                            mapped_precursors=[Chem.MolToSmiles(m.mapped_mol, isomericSmiles=True)
                                               for m in values],
                            original_target_maps_preserved=set(target_maps) == expected_maps,
                            original_target_maps_unique=len(target_maps) == len(set(target_maps)),
                            all_output_maps_nonzero=all(maps),
                            all_output_maps_unique=len(maps) == len(set(maps))))
    return outputs
