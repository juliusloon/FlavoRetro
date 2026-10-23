"""Exact literature reaction retrieval as an opt-in MCTS expansion policy.

This is source reconstruction, not a learnt or generalizable reaction template.
Every action is restricted to one exact source product; conditions remain source
context, never predicted conditions. All data stay in a local immutable manifest.
"""
from pathlib import Path
import json
import time
from rdkit import Chem
from aizynthfinder.chem import SmilesBasedRetroReaction
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException
from .resources import sha
from .workspace import root, AssetError
from .reaction_intake import local_path, canonical_side


def canonical(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or not mol.GetNumAtoms():
        raise ValueError("invalid exact literature structure")
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, isomericSmiles=True)


class Registry:
    def __init__(self, manifest, manifest_sha256):
        path = local_path(manifest)
        if not path.is_file() or sha(path) != manifest_sha256:
            raise AssetError("literature manifest absent or drift")
        self.manifest = json.loads(path.read_text())
        if self.manifest.get("kind") != "exact_source_reaction_registry" or self.manifest.get("human_reviewed") is not False:
            raise AssetError("invalid source registry role")
        for rel, expected in self.manifest["assets"].items():
            asset = local_path(rel)
            if not asset.is_file() or sha(asset) != expected:
                raise AssetError("literature source asset drift: " + rel)
        record_path = local_path(self.manifest["records"])
        if sha(record_path) != self.manifest["records_sha256"]:
            raise AssetError("literature records drift")
        self.records = json.loads(record_path.read_text())
        self.by_id = {r["reaction_id"]: r for r in self.records}
        if len(self.by_id) != len(self.records):
            raise AssetError("duplicate source reaction identifier")
        self.by_target = {}
        for row in self.records:
            if not row.get("exact_reconstruction_approved") or row.get("scope_transfer_evidence") is not False:
                raise AssetError("unapproved source reconstruction")
            if len(row["products"]) != 1:
                raise AssetError("exact retrieval requires one defined main product")
            target, problems = canonical_side(row["products"])
            precursors, precursor_problems = canonical_side(row["reactants"])
            if not target or not precursors or problems or precursor_problems:
                raise AssetError("invalid source participants")
            if target != row["target"] or precursors != row["precursors"]:
                raise AssetError("source registry graph mismatch")
            self.by_target.setdefault(target, []).append(row)
        self.development_contexts = []
        context_path = self.manifest.get("development_contexts")
        if context_path:
            if context_path not in self.manifest["assets"]:
                raise AssetError("unbound development context")
            self.development_contexts = json.loads(local_path(context_path).read_text())
            if any(c.get("mcts_action") is not False or c.get("human_reviewed") is not False for c in self.development_contexts):
                raise AssetError("invalid development context role")
        self.binding = {"version": self.manifest["version"], "manifest": str(path.relative_to(root())),
                        "manifest_sha256": manifest_sha256, "kind": "exact_source_reconstruction"}

    def evidence(self, reaction):
        row = self.by_id.get(reaction.metadata.get("source_reaction_id"))
        if row is None or reaction.metadata.get("literature_binding") != self.binding:
            raise RejectionException("literature provenance mismatch")
        actual = ".".join(sorted(canonical(m.smiles) for m in reaction.reactants[reaction.index]))
        if canonical(reaction.mol.smiles) != row["target"] or actual != row["precursors"]:
            raise RejectionException("outside exact source reaction")
        return {"source_reaction_id": row["reaction_id"], "source": row["source"],
                **({"lab_case": row["lab_case"]} if row.get("lab_case") else {}),
                "binding": self.binding, "source_reconstruction": True,
                "exact_source_instance_match": True, "scope_transfer_evidence": False,
                "source_reactants": row["reactants"], "source_products": row["products"],
                "source_conditions": row.get("conditions"), "source_catalyst": row.get("catalyst"),
                "source_yield_value": row.get("yield_value"), "source_yield_unit": row.get("yield_unit"),
                "source_yield_status": row.get("yield_status"),
                "source_yield_reported_text": row.get("yield_reported_text"),
                "source_product_mass_g_range": row.get("product_mass_g_range"),
                "source_reagents_stock_checked": False,
                "conditions_prediction_verified": False, "human_reviewed": False,
                "independent_chemical_validation": False, "evidence_closed": False,
                "actionable": False, "review_cautions": row.get("review_cautions", [])}


class LiteratureExpansion(ExpansionStrategy):
    def __init__(self, key, config, literature_binding, **kwargs):
        super().__init__(key, config, **kwargs)
        self.registry = Registry(literature_binding["manifest"], literature_binding["manifest_sha256"])
        if self.registry.binding != literature_binding:
            raise AssetError("literature binding mismatch")
        self.profiling = {"lookups": 0, "generated_actions": 0, "generation_seconds": 0.0}

    def get_actions(self, molecules, cache_molecules=None):
        start = time.monotonic()
        actions, priors = [], []
        for mol in molecules:
            self.profiling["lookups"] += 1
            for row in self.registry.by_target.get(canonical(mol.smiles), []):
                metadata = {"policy_name": self.key, "template_code": row["reaction_id"],
                            "source_reaction_id": row["reaction_id"], "template_id": row["reaction_id"],
                            "literature_binding": self.registry.binding,
                            "source_record_type": "exact_source_reconstruction",
                            "classification": "source_recorded_" + row.get("category", "reaction")}
                action = SmilesBasedRetroReaction(mol, reactants_str=row["precursors"], metadata=metadata)
                if not action.reactants:
                    continue
                action.metadata["task022_evidence"] = self.registry.evidence(action)
                actions.append(action)
                priors.append(self.registry.manifest["policy"]["prior"])
                self.profiling["generated_actions"] += 1
        self.profiling["generation_seconds"] += time.monotonic() - start
        return actions, priors


class SourceAwareQuickFilter(QuickKerasFilter):
    def __init__(self, key, config, literature_binding, **kwargs):
        super().__init__(key, config, **kwargs)
        self.registry = Registry(literature_binding["manifest"], literature_binding["manifest_sha256"])

    def apply(self, reaction):
        if reaction.metadata.get("policy_name") == "literature":
            evidence = self.registry.evidence(reaction)
            reaction.metadata["task022_evidence"] = evidence
            reaction.metadata["filter_path"] = "known hazards + exact source record; no independent chemistry claim"
            reaction.metadata.setdefault("review", {})["task022"] = evidence
            return
        return super().apply(reaction)
