"""Default-off, source-bound enzymatic templates. No chemical feasibility certification."""
import json
import re
import time
from pathlib import Path
from rdkit import Chem, rdBase
from rdkit.Chem import rdFMCS, rdChemReactions
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.chem import TemplatedRetroReaction
from aizynthfinder.utils.exceptions import RejectionException
from .workspace import root, config, AssetError
from .resources import sha
from .reviewed_resources import canonical_side, reaction_signature, load_review
from .topology import audit


def extract_template(instance):
    """Map the conserved acceptor and transferred sugar; retain complete UDP donor."""
    acceptor = Chem.MolFromSmiles(instance["acceptor"])
    donor = Chem.MolFromSmiles(instance["donor"])
    product = Chem.MolFromSmiles(instance["target"])
    if any(m is None for m in (acceptor, donor, product)):
        raise ValueError("invalid participant")
    for atom in product.GetAtoms():
        atom.SetAtomMapNum(atom.GetIdx() + 1)
    mcs = rdFMCS.FindMCS([acceptor, product], timeout=5, ringMatchesRingOnly=True,
                        completeRingsOnly=True, bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms != acceptor.GetNumAtoms():
        raise ValueError("acceptor is not fully conserved; mapping uncertain")
    query = Chem.MolFromSmarts(mcs.smartsString)
    am, pm = acceptor.GetSubstructMatch(query), product.GetSubstructMatch(query)
    for aidx, pidx in zip(am, pm):
        acceptor.GetAtomWithIdx(aidx).SetAtomMapNum(pidx + 1)
    transferred = [i for i in range(product.GetNumAtoms()) if i not in pm]
    sugar = Chem.RWMol()
    positions = {i: sugar.AddAtom(Chem.AtomFromSmarts(f"[#{product.GetAtomWithIdx(i).GetAtomicNum()}:{i+1}]")) for i in transferred}
    for bond in product.GetBonds():
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if a in positions and b in positions:
            sugar.AddBond(positions[a], positions[b], bond.GetBondType())
    query = sugar.GetMol()
    matches = donor.GetSubstructMatches(query, useChirality=False)
    if len(matches) != 1:
        raise ValueError("sugar-to-donor mapping is absent or ambiguous")
    for fidx, didx in enumerate(matches[0]):
        donor.GetAtomWithIdx(didx).SetAtomMapNum(query.GetAtomWithIdx(fidx).GetAtomMapNum())
    links = [b for b in product.GetBonds() if (b.GetBeginAtomIdx() in pm) != (b.GetEndAtomIdx() in pm)]
    if len(links) != 1:
        raise ValueError("not a single sugar attachment")
    sites = [s for s in audit(instance["target"])["sites"] if s["bond_index"] == links[0].GetIdx()]
    if len(sites) != 1 or sites[0]["family"] not in ("aryl_O_candidate", "aryl_C_candidate", "sugar_sugar_O_candidate"):
        raise ValueError("attachment center is not an admitted glycosidic bond")
    left = Chem.MolToSmiles(product, isomericSmiles=True)
    right = Chem.MolToSmiles(acceptor, isomericSmiles=True) + "." + Chem.MolToSmiles(donor, isomericSmiles=True)
    # RDKit otherwise inherits a mapped atom's old charge. Explicit neutral charge
    # is essential when Rhea moves the phenolate site upon glycosylation.
    right = re.sub(r"\[([^\]]*?):(\d+)\]", lambda m: "["+m[1]+("+0" if "+" not in m[1] and "-" not in m[1] else "")+":"+m[2]+"]", right)
    return dict(smarts=left+">>"+right, center=sites[0],
                mapping=dict(tool="RDKit MCS + unique transferred-sugar graph match", rdkit=rdBase.rdkitVersion,
                             status="machine_inferred", transferred_atoms=len(transferred), conserved_acceptor_atoms=len(pm)))


def apply_template(template, target, context=None):
    canonical = canonical_side([target])
    if canonical not in template["allowed_targets"]:
        return []
    if context is not None and context != template["required_context"]:
        return []
    rxn = rdChemReactions.ReactionFromSmarts(template["smarts"])
    if rxn is None:
        raise ValueError("invalid registered template")
    outcomes = []
    for index, molecules in enumerate(rxn.RunReactants([Chem.MolFromSmiles(target)])):
        try:
            for molecule in molecules:
                Chem.SanitizeMol(molecule)
            precursors = canonical_side([Chem.MolToSmiles(m, isomericSmiles=True) for m in molecules])
            if precursors:
                outcomes.append(dict(outcome_index=index, precursors=precursors))
        except Exception as exc:
            outcomes.append(dict(outcome_index=index, status="sanitize_failed", error=str(exc)))
    return outcomes


class Registry:
    def __init__(self, manifest_path, expected_sha256):
        self.path = Path(manifest_path)
        if not self.path.is_file() or sha(self.path) != expected_sha256:
            raise AssetError("task016 manifest absent or hash drift")
        manifest = json.loads(self.path.read_text())
        if manifest.get("schema_version") != 1 or manifest.get("rdkit") != rdBase.rdkitVersion:
            raise AssetError("task016 schema/environment drift")
        self.root = self.path.parent
        for relative, expected in manifest["files_sha256"].items():
            path = (self.root / relative).resolve()
            if not path.is_relative_to(self.root.resolve()) or not path.is_file() or sha(path) != expected:
                raise AssetError("task016 payload absent or hash drift: " + relative)
        for relative, expected in manifest["raw_dependencies_sha256"].items():
            path = (root() / relative).resolve()
            if not path.is_relative_to(root()) or not path.is_file() or sha(path) != expected:
                raise AssetError("task016 source absent or hash drift: " + relative)
        load_review(manifest["review_binding"])
        self.templates = [json.loads(line) for line in (self.root / "templates.jsonl").read_text().splitlines()]
        self.instances = {r["instance_id"]: r for r in [json.loads(l) for l in (self.root / "instances.jsonl").read_text().splitlines()]}
        self.by_id = {t["template_id"]: t for t in self.templates}
        if len(self.by_id) != len(self.templates):
            raise AssetError("duplicate template identifiers")
        self.binding = dict(version=manifest["version"], manifest_sha256=expected_sha256,
                            manifest=str(self.path.relative_to(root())))
        self.settings = manifest["policy"]
        for t in self.templates:
            if t.get("validation_status") != "source_reconstruction_passed" or not t["support_instances"]:
                raise AssetError("unvalidated executable template")
            for identifier in t["support_instances"]:
                instance = self.instances[identifier]
                if canonical_side(instance["reference_precursors"]) not in [o.get("precursors") for o in apply_template(t, instance["target"])]:
                    raise AssetError("registered support reconstruction drift")

    def evidence(self, reaction):
        meta = reaction.metadata
        t = self.by_id.get(meta.get("template_id"))
        if (t is None or meta.get("domain_binding") != self.binding
                or meta.get("required_context") != t["required_context"]
                or canonical_side([reaction.mol.smiles]) not in t["allowed_targets"]
                or getattr(reaction, "smarts", None) != t["smarts"]):
            raise RejectionException("invalid domain provenance or applicability")
        actual = reaction_signature([m.smiles for m in reaction.reactants[reaction.index]], [reaction.mol.smiles])
        known = [self.instances[i] for i in t["support_instances"]]
        matches = [r for r in known if actual == r["reference_signature"]]
        if not matches:
            raise RejectionException("domain outcome outside declared source support")
        return dict(namespace="task016", binding=self.binding, template_id=t["template_id"],
                    template_source_support=True, source_instance_ids=t["support_instances"],
                    exact_instance_match=True, exact_instance_match_scope="frozen required precursors and primary target",
                    full_rhea_equation_match=any(actual == r["strict_source_signature"] for r in matches),
                    prediction_conditions_verified=False, yield_value=None, actionable=False,
                    required_context=t["required_context"], provenance=[r["provenance"] for r in matches],
                    evidence_type="agent_source_annotation_and_machine_reconstruction", independent_chemical_validation=False)


def load_registry(expected=None):
    setting = config("glycoside-expansion.json")
    path = root() / setting["manifest"]
    registry = Registry(path, setting["manifest_sha256"])
    if expected is not None and registry.binding != expected:
        raise AssetError("task016 binding changed during run")
    return registry


class GlycosideExpansion(ExpansionStrategy):
    def __init__(self, key, config, domain_binding=None, **kwargs):
        super().__init__(key, config, **kwargs)
        self.registry = load_registry(domain_binding)
        self.profiling = dict(template_attempts=0, generation_seconds=0.0, generated_actions=0)

    def get_actions(self, molecules, cache_molecules=None):
        start = time.monotonic()
        actions, priors = [], []
        for mol in molecules:
            count = 0
            for template in self.registry.templates:
                self.profiling["template_attempts"] += 1
                if not apply_template(template, mol.smiles):
                    continue
                if count >= self.registry.settings["domain_cap_per_molecule"]:
                    break
                action = TemplatedRetroReaction(mol, smarts=template["smarts"], use_rdchiral=False,
                    metadata=dict(policy_name=self.key, template_id=template["template_id"],
                                  template=template["smarts"], domain_binding=self.registry.binding,
                                  required_context=template["required_context"], prediction_conditions_verified=False))
                for index in range(len(action.reactants)):
                    self.registry.evidence(action.copy(index=index))
                actions.append(action); priors.append(self.registry.settings["prior"]); count += 1
        self.profiling["generation_seconds"] += time.monotonic() - start
        self.profiling["generated_actions"] += len(actions)
        return actions, priors


class DomainAwareQuickFilter(QuickKerasFilter):
    """Generic actions use the unchanged model; source-bound enzymes use the guard."""
    def __init__(self, key, config, domain_binding=None, **kwargs):
        super().__init__(key, config, **kwargs)
        self.registry = load_registry(domain_binding)

    def apply(self, reaction):
        if reaction.metadata.get("policy_name") == "glycoside":
            evidence = self.registry.evidence(reaction)
            reaction.metadata["task016_evidence"] = evidence
            reaction.metadata["filter_path"] = "known_hazards + strict_source_template_guard; USPTO chemical filter not applicable"
            reaction.metadata.setdefault("review", {})["task016"] = evidence
            return
        super().apply(reaction)
