"""Corrected v5 runtime: qualified P2/v3 payload plus the P4-revalidated scope only.

v5 is deliberately NOT a subclass of v4. The P4 contract forbids inheriting the
whole v4 increment and then marking two scopes invalid, so v5 is assembled from
the qualified v3 payload plus the single scope that survived the corrected
distinct-acceptor gate (rhamnoside_glucoside_O2).

Two quarantined P3 scopes stay out of this registry by construction:
  C_hydroxyflavanone_C3  no structure-complete intermediate evidence after the
                          G1 re-audit
  rhamnoside_glucoside_O6 one distinct canonical acceptor, below the gate of 2

v4 remains loadable for historical reproduction, but its three P3 scopes carry the
P4 correction status in the registry and none of them enters v5 automatically.
v1/v2/v3/v4 behaviour and fingerprints are unchanged; v5 loads only through an
explicit glycoside_library_version='v5' request and fails closed on a missing
payload or any hash drift.
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
from . import glycoside_library_v4 as v4
from .workspace import root, config, AssetError
from .resources import sha
from .reviewed_resources import canonical_side, reaction_signature, load_review
from .open_glycoside_library import normalize_species

# P4 correction outcome for every P3 scope, carried in the registry so a historical
# v4 run can be read against the corrected judgement without changing v4 itself.
P3_SCOPE_CORRECTION = {
    "C_hydroxyflavanone_C3": {
        "p4_status": "quarantined",
        "reason": "G1 re-audit downgraded P3R-C01 and P3R-C02 to identity_complete_structure_deferred; "
                  "the P3 identification string had transferred NMR/standard evidence of the "
                  "dehydrated flavone products onto the unassigned 2-hydroxyflavanone "
                  "C-glucoside intermediate. No structure-complete intermediate evidence exists.",
        "enters_v5": False,
    },
    "rhamnoside_glucoside_O2": {
        "p4_status": "revalidated",
        "reason": "2 distinct canonical acceptor signatures and 2 structure-complete build "
                  "reactions after canonicalisation; counted into v5.",
        "enters_v5": True,
    },
    "rhamnoside_glucoside_O6": {
        "p4_status": "quarantined",
        "reason": "both P3 supports share one canonical acceptor and reaction_id P3R-SS03, so "
                  "distinct canonical acceptors = 1, below the gate of 2. A second source does "
                  "not create a second receptor.",
        "enters_v5": False,
    },
}

P4_NAMESPACE = "task016_p4"


def p4_scope_center_allowed(t, target, products):
    """Only the revalidated P4 scope may use the v4 context guards.

    The C3 guard is retained in the module but is unreachable from the v5 payload
    because that scope is quarantined; it stays importable so a historical v4 run
    is still reproducible.
    """
    scope = t["scope"]
    center = scope["center_class"]
    acceptor, donor = products
    if canonical_side([Chem.MolToSmiles(donor, isomericSmiles=True)]) != t["donor"]:
        return False
    if not any(target.HasSubstructMatch(Chem.MolFromSmarts(c))
               for c in scope["acceptor_cores"]):
        return False
    for pat in scope["parent_glycan_patterns"]:
        if not acceptor.HasSubstructMatch(Chem.MolFromSmarts(pat), useChirality=True):
            return False
    ts = Chem.MolToSmiles(target, isomericSmiles=True)
    acs = Chem.MolToSmiles(acceptor, isomericSmiles=True)
    ds = Chem.MolToSmiles(donor, isomericSmiles=True)
    if center == "rhamnoside_glucoside_O2":
        return v4._ss_context_ok(acs, ds, ts, "ring")
    if center == "C_hydroxyflavanone_C3":
        return v4._c3_context_ok(acs, ts)
    if center == "rhamnoside_glucoside_O6":
        return v4._ss_context_ok(acs, ds, ts, "exocyclic")
    return False


def scope_center_allowed(t, target, products):
    scope = t.get("scope")
    if scope and scope.get("p4_scope_namespace") == P4_NAMESPACE:
        return p4_scope_center_allowed(t, target, products)
    if scope and scope.get("namespace") == "task016_p3":
        return v4.p3_scope_center_allowed(t, target, products)
    return v2.scope_center_allowed(t, target, products)


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
            raise AssetError("v5 manifest absent or hash drift")
        m = json.loads(path.read_text())
        if m.get("schema_version") != 2 or m["rdkit"] != rdBase.rdkitVersion:
            raise AssetError("v5 schema or environment drift")
        for rel, h in m["files_sha256"].items():
            p = (path.parent / rel).resolve()
            if (not p.is_relative_to(path.parent.resolve())
                    or not p.is_file() or sha(p) != h):
                raise AssetError("v5 build payload drift: " + rel)
        load_review(m["review_binding"])
        self.settings = m["policy"]
        self.p4_templates = [json.loads(l)
                             for l in (path.parent / "templates.jsonl").read_text().splitlines()]
        self.p4_instances = {r["instance_id"]: r for r in
                             [json.loads(l) for l in
                              (path.parent / "runtime_instances.jsonl").read_text().splitlines()]}
        if any(r.get("template_role") != "development_build"
               for r in self.p4_instances.values()):
            raise AssetError("holdout instance in runtime registry")
        for t in self.p4_templates:
            center = (t.get("scope") or {}).get("center_class")
            if P3_SCOPE_CORRECTION.get(center, {}).get("enters_v5") is not True:
                raise AssetError("quarantined P3 scope present in the v5 payload: " + str(center))
        self.v3_registry = v3.load_registry()
        self.templates = self.v3_registry.templates + self.p4_templates
        self.instances = {**self.v3_registry.instances, **self.p4_instances}
        self.by_id = {t["template_id"]: t for t in self.templates}
        if len(self.by_id) != len(self.templates):
            raise AssetError("duplicate v5 template ID")
        self.binding = dict(version=m["version"],
                            manifest=str(path.relative_to(root())),
                            manifest_sha256=expected,
                            chained_v3=self.v3_registry.binding,
                            p3_scope_correction=P3_SCOPE_CORRECTION)
        for t in self.p4_templates:
            if t["validation_status"] != "source_reconstruction_passed":
                raise AssetError("unvalidated v5 template")
            for identifier in t["support_instances"]:
                r = self.p4_instances[identifier]
                if canonical_side(r["reference_precursors"]) not in [
                        o["precursors"] for o in apply_template(t, r["target"])]:
                    raise AssetError("v5 support replay drift")

    def evidence(self, reaction):
        t = self.by_id.get(reaction.metadata.get("template_id"))
        if (t is None
                or reaction.metadata.get("domain_binding") != self.binding
                or reaction.smarts != t["smarts"]
                or reaction.metadata.get("required_context") != t["required_context"]):
            raise RejectionException("v5 provenance invalid")
        actual = canonical_side([m.smiles for m in reaction.reactants[reaction.index]])
        if actual not in [o["precursors"] for o in apply_template(t, reaction.mol.smiles)]:
            raise RejectionException("v5 outcome outside validated scope")
        normalized = normalize_species(reaction.mol.smiles)["normalized"]
        sig = reaction_signature([actual], [normalized])
        matches = [self.instances[i] for i in t["support_instances"]
                   if self.instances[i]["reference_signature"] == sig]
        if (t.get("scope") or {}).get("p4_scope_namespace") == P4_NAMESPACE:
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
                    inherited_template=ns != P4_NAMESPACE)


def load_registry(expected=None):
    s = config("glycoside-library-v5.json")
    r = Registry(root() / s["manifest"], s["manifest_sha256"])
    if expected is not None and r.binding != expected:
        raise AssetError("v5 binding changed during run")
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
            reaction.metadata["filter_path"] = ("known_hazards + validated v5 scope guard; "
                                                "activity unverified")
            reaction.metadata.setdefault("review", {})["task016_p4"] = e
            return
        QuickKerasFilter.apply(self, reaction)
