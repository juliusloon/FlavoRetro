"""Explicit default-off P6 runtime: qualified v3 + qualified O2 + frozen C8 scope.

Historical v1-v5 modules are not edited. C evidence has its own namespace and
source support, exact instance match and prediction conditions remain separate.
"""
import json
import time
from pathlib import Path

from rdkit import Chem, rdBase
from rdkit.Chem import rdChemReactions
from aizynthfinder.chem import TemplatedRetroReaction
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException

from . import glycoside_library as v2
from . import glycoside_library_v3 as v3
from . import glycoside_library_v5 as v5
from .glycoside_scope import c_scope_allowed
from .workspace import root, config, AssetError
from .resources import sha
from .reviewed_resources import canonical_side, reaction_signature, load_review
from .open_glycoside_library import normalize_species

P6_NAMESPACE = "task016_p6"
P4_NAMESPACE = "task016_p4"

def scope_center_allowed(t, target, products):
    if (t.get("scope") or {}).get("namespace") == P6_NAMESPACE:
        return c_scope_allowed(t, target, products)
    return v5.scope_center_allowed(t, target, products)


def apply_template(t, target, context=None):
    if context is not None and context != t["required_context"]:
        return []
    normalized = normalize_species(target)["normalized"]
    if t["template_role"] == "exact_instance_template" and normalized not in t["allowed_targets"]:
        return []
    mol = Chem.MolFromSmiles(normalized)
    rxn = rdChemReactions.ReactionFromSmarts(t["smarts"])
    rxn.GetSubstructParams().useChirality = True
    outcomes = []
    for index, products in enumerate(rxn.RunReactants([mol])):
        try:
            for p in products:
                Chem.SanitizeMol(p)
            v2.restore_conserved_double_bond_stereo(products, mol)
            if not scope_center_allowed(t, mol, products):
                continue
            value = canonical_side([Chem.MolToSmiles(p, isomericSmiles=True) for p in products])
            if value:
                outcomes.append(dict(outcome_index=index, precursors=value))
        except (ValueError, RuntimeError):
            continue
    return outcomes


class LibraryRetroReaction(TemplatedRetroReaction):
    def _apply_with_rdkit(self):
        from aizynthfinder.chem import TreeMolecule
        from functools import partial

        rxn = rdChemReactions.ReactionFromSmarts(self.smarts)
        rxn.GetSubstructParams().useChirality = True
        normalized = v2.neutral_mol(self.mol.mapped_mol)
        for atom in normalized.GetAtoms():
            atom.SetAtomMapNum(0)
        t = self.metadata["library_template"]
        outcomes = []
        raw_indices = []
        for raw_index, products in enumerate(rxn.RunReactants([normalized])):
            try:
                for p in products:
                    Chem.SanitizeMol(p)
                v2.restore_conserved_double_bond_stereo(products, normalized)
                if not scope_center_allowed(t, normalized, products):
                    continue
                fn = partial(self._inherit_atom_mapping,
                             exclude_nums=set(self.mol.mapping_to_index.keys()))
                value = tuple(TreeMolecule(parent=self.mol, rd_mol=p, sanitize=True,
                                           mapping_update_callback=fn) for p in products)
                outcomes.append(value)
                raw_indices.append(raw_index)
            except (ValueError, RuntimeError):
                continue
        self.metadata["raw_outcome_indices"] = raw_indices
        self._reactants = tuple(outcomes)
        return self._reactants


class Registry(v3.Registry):
    """Validates the P4 increment and chains the qualified v3 payload."""

    def __init__(self, path, expected):
        path = Path(path)
        if not path.is_file() or sha(path) != expected:
            raise AssetError("v6 manifest absent or hash drift")
        m = json.loads(path.read_text())
        if m.get("schema_version") != 2 or m["rdkit"] != rdBase.rdkitVersion:
            raise AssetError("v6 schema or environment drift")
        for rel, h in m["files_sha256"].items():
            p = (path.parent / rel).resolve()
            if (not p.is_relative_to(path.parent.resolve())
                    or not p.is_file() or sha(p) != h):
                raise AssetError("v6 build payload drift: " + rel)
        load_review(m["review_binding"])
        self.settings = m["policy"]
        self.increment_templates = [json.loads(l)
                             for l in (path.parent / "templates.jsonl").read_text().splitlines()]
        self.increment_instances = {r["instance_id"]: r for r in
                             [json.loads(l) for l in
                              (path.parent / "runtime_instances.jsonl").read_text().splitlines()]}
        if any(r.get("template_role") != "development_build"
               for r in self.increment_instances.values()):
            raise AssetError("holdout instance in runtime registry")
        for t in self.increment_templates:
            center = (t.get("scope") or {}).get("center_class")
            if center not in {"flavonol_8_C_glucoside", "rhamnoside_glucoside_O2"}:
                raise AssetError("quarantined P3 scope present in the v6 payload: " + str(center))
        baseline = (root() / m["qualified_v3"]["manifest"]).resolve()
        if not baseline.is_relative_to(root().resolve()) or not baseline.is_file() or sha(baseline) != m["qualified_v3"]["sha256"]:
            raise AssetError("v6 qualified v3 baseline drift")
        self.v3_registry = v3.load_registry()
        self.templates = self.v3_registry.templates + self.increment_templates
        self.instances = {**self.v3_registry.instances, **self.increment_instances}
        self.by_id = {t["template_id"]: t for t in self.templates}
        if len(self.by_id) != len(self.templates):
            raise AssetError("duplicate v6 template ID")
        self.binding = dict(version=m["version"],
                            manifest=str(path.relative_to(root())),
                            manifest_sha256=expected,
                            chained_v3=self.v3_registry.binding,
                            qualified_increment_centers=sorted({t["scope"]["center_class"] for t in self.increment_templates}))
        for t in self.increment_templates:
            if t["validation_status"] != "source_reconstruction_passed":
                raise AssetError("unvalidated v6 template")
            for identifier in t["support_instances"]:
                r = self.increment_instances[identifier]
                if canonical_side(r["reference_precursors"]) not in [
                        o["precursors"] for o in apply_template(t, r["target"])]:
                    raise AssetError("v6 support replay drift")

    def evidence(self, reaction):
        t = self.by_id.get(reaction.metadata.get("template_id"))
        if (t is None
                or reaction.metadata.get("domain_binding") != self.binding
                or reaction.smarts != t["smarts"]
                or reaction.metadata.get("required_context") != t["required_context"]):
            raise RejectionException("v6 provenance invalid")
        actual = canonical_side([m.smiles for m in reaction.reactants[reaction.index]])
        if actual not in [o["precursors"] for o in apply_template(t, reaction.mol.smiles)]:
            raise RejectionException("v6 outcome outside validated scope")
        normalized = normalize_species(reaction.mol.smiles)["normalized"]
        sig = reaction_signature([actual], [normalized])
        matches = [self.instances[i] for i in t["support_instances"]
                   if self.instances[i]["reference_signature"] == sig]
        if (t.get("scope") or {}).get("namespace") == P6_NAMESPACE:
            ns = P6_NAMESPACE
        elif (t.get("scope") or {}).get("p4_scope_namespace") == P4_NAMESPACE:
            ns = P4_NAMESPACE
        elif (t.get("scope") or {}).get("namespace") == "task016_p3":
            ns = "task016_p3"
        else:
            ns = "task016_p2"
        return dict(namespace=ns,
                    binding=self.binding,
                    template_id=t["template_id"],
                    template_source_support=True,
                    source_instance_ids=t["support_instances"],
                    exact_seed_instance_match=bool(matches),
                    exact_instance_match=bool(matches),
                    prediction_conditions_verified=False,
                    yield_value=None,
                    actionable=False,
                    evidence_closed=False,
                    independent_chemical_validation=False,
                    human_reviewed=False,
                    scope_applicability=t.get("scope", {"mode": "exact_instance"}),
                    transfer_status=("exact_build_source_reconstruction" if matches
                                     else "scope_transfer_candidate_unverified_activity"),
                    required_context=t["required_context"],
                    provenance=[self.instances[i]["provenance"] for i in t["support_instances"]],
                    original_conditions_copied=False,
                    inherited_template=ns != P6_NAMESPACE)


def load_registry(expected=None):
    s = config("glycoside-library-v6.json")
    r = Registry(root() / s["manifest"], s["manifest_sha256"])
    if expected is not None and r.binding != expected:
        raise AssetError("v6 binding changed during run")
    return r


class GlycosideExpansion(ExpansionStrategy):
    def __init__(self, key, config, domain_binding=None, **kwargs):
        ExpansionStrategy.__init__(self, key, config, **kwargs)
        self.registry = load_registry(domain_binding)
        self.profiling = dict(template_attempts=0, generation_seconds=0.,
                              generated_actions=0)

    def get_actions(self, molecules, cache_molecules=None):
        actions = []
        priors = []
        start = time.monotonic()
        for mol in molecules:
            count = 0
            for t in self.registry.templates:
                self.profiling["template_attempts"] += 1
                if not apply_template(t, mol.smiles):
                    continue
                if count >= self.registry.settings["domain_cap_per_molecule"]:
                    break
                a = LibraryRetroReaction(
                    mol, smarts=t["smarts"], use_rdchiral=False,
                    metadata=dict(policy_name=self.key, template_id=t["template_id"],
                                  template=t["smarts"], library_template=t,
                                  domain_binding=self.registry.binding,
                                  required_context=t["required_context"]))
                if not a.reactants:
                    continue
                for index in range(len(a.reactants)):
                    self.registry.evidence(a.copy(index=index))
                actions.append(a)
                priors.append(self.registry.settings["prior"])
                count += 1
        self.profiling["generation_seconds"] += time.monotonic() - start
        self.profiling["generated_actions"] += len(actions)
        return actions, priors


class DomainAwareQuickFilter(QuickKerasFilter):
    def __init__(self, key, config, domain_binding=None, **kwargs):
        QuickKerasFilter.__init__(self, key, config, **kwargs)
        self.registry = load_registry(domain_binding)

    def apply(self, reaction):
        if reaction.metadata.get("policy_name") == "glycoside":
            e = self.registry.evidence(reaction)
            reaction.metadata["task016_evidence"] = e
            reaction.metadata["filter_path"] = ("known_hazards + validated v6 scope guard; "
                                                "activity unverified")
            reaction.metadata.setdefault("review", {})[e["namespace"]] = e
            return
        QuickKerasFilter.apply(self, reaction)
