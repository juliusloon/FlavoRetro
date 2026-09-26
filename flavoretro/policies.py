"""Conservative candidate stock and known-hazard filters; no safety certification."""

import json
from rdkit import Chem
from aizynthfinder.context.stock.queries import StockQueryMixin
from aizynthfinder.context.policy import FilterStrategy
from aizynthfinder.utils.exceptions import RejectionException
from .resources import sha
from .workspace import active_data


def records():
    from .database import records as indexed_records
    return indexed_records()


class CandidateStock(StockQueryMixin):
    def __init__(self, enabled=False, **kwargs):
        self.keys = {
            r["structure"]["inchikey"]
            for r in (records() if enabled else [])
            if r["kind"] == "stock" and r["runtime_candidate_allowed"]
        }

    def __contains__(self, mol):
        return mol.inchi_key in self.keys

    def __len__(self):
        return len(self.keys)


# Explicit examples from the historical safety contract. Unknown hazards stay unknown.
BANNED = {"CI", "C[Li]", "[Na]", "[K]", "N#C", "[C-]#N"}
METALS = {33, 48, 80, 81, 82}


def hazard_reason(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return "invalid_precursor"
    if any(a.GetAtomicNum() in METALS for a in mol.GetAtoms()):
        return "heavy_metal"
    if Chem.MolToSmiles(mol) in BANNED:
        return "known_severe_or_pyrophoric"
    return None


class KnownHazards(FilterStrategy):
    def apply(self, reaction):
        meta = reaction.metadata
        if (
            meta.get("forward_replay") is False
            or meta.get("forward_replay_status") == "disproved"
        ):
            raise RejectionException("disproved_forward_replay")
        if any(
            meta.get(k) is True
            for k in ("severe_toxicity", "pyrophoric", "heavy_metal")
        ):
            raise RejectionException("known_hazard_metadata")
        temperature = meta.get("temperature_c")
        if isinstance(temperature, (int, float)) and temperature < -50:
            raise RejectionException("extreme_cold")
        for mol in reaction.reactants[reaction.index]:
            reason = hazard_reason(mol.smiles)
            if reason:
                raise RejectionException(reason)
        smarts = getattr(reaction, "smarts", None)
        if smarts and ">>" in smarts:
            from rdkit.Chem import rdChemReactions

            rxn = rdChemReactions.ReactionFromSmarts(smarts)
            if rxn is None:
                raise RejectionException("invalid_template")
            left = [
                a.GetAtomMapNum()
                for m in rxn.GetReactants()
                for a in m.GetAtoms()
                if a.GetAtomMapNum()
            ]
            right = [
                a.GetAtomMapNum()
                for m in rxn.GetProducts()
                for a in m.GetAtoms()
                if a.GetAtomMapNum()
            ]
            if (
                len(set(left)) != len(left)
                or len(set(right)) != len(right)
                or (left and not set(left).issubset(right))
            ):
                raise RejectionException("atom_map_integrity")
