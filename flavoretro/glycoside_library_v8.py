"""Default-off corrected source library; graph replay is not chemical validation.

The flat payload removes quarantined historical supports. Historical v6 bytes
and results stay unchanged. New rhamnosides have exact templates only.
"""
import json
from pathlib import Path

from rdkit import rdBase
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter

from . import glycoside_library_v6 as v6
from .workspace import root, config, AssetError
from .resources import sha
from .reviewed_resources import canonical_side, reaction_signature, load_review
from .open_glycoside_library import normalize_species

NAMESPACE = "task022_glycoside_v8"
VERSION = "task022-glycoside-v8-corrected"
QUARANTINED_INSTANCES = frozenset({
    "PMC10589286:GuApiGT:aae2c63f73eef2968fcc",
    "PMC10589286:GuApiGT:a82d1be431bc0259d186",
    "PMC10589286:GuApiGT:ea94a5a029b2e15eb6bc",
    "PMC13084081:MpRhaT:a7c23dd18652d36e64e23c53",
    "PMC13084081:MpRhaT:f2cab8d5e86df915f06735ed",
})
QUARANTINED_TEMPLATES = frozenset({
    "p1-exact:649f782d70c24c328be0", "p1-exact:85ecc3b8deba014fccc2",
    "p1-exact:411a053a7ea74877029a", "p3-scope:9766b2bf1515f4c519ec",
})
POLICY = dict(default_enabled=False, domain_cap_per_molecule=4,
              generic_protection=3, prior=0.2, weight=1.0)
apply_template = v6.apply_template
LibraryRetroReaction = v6.LibraryRetroReaction


def _verify_files(base, entries, message):
    base = base.resolve()
    for rel, digest in entries.items():
        p = (base / rel).resolve()
        if not p.is_relative_to(base) or not p.is_file() or sha(p) != digest:
            raise AssetError(message + str(rel))


class Registry(v6.Registry):
    """Validate all flattened supports without reinstating historical entries."""

    def __init__(self, path, expected):
        path = Path(path).resolve()
        if not path.is_relative_to(root().resolve()):
            raise AssetError("v8 manifest outside workspace")
        if not path.is_file() or sha(path) != expected:
            raise AssetError("v8 manifest absent or hash drift")
        m = json.loads(path.read_text())
        if (m.get("schema_version") != 3 or m.get("version") != VERSION
                or m.get("rdkit") != rdBase.rdkitVersion):
            raise AssetError("v8 schema or environment drift")
        if m.get("policy") != POLICY:
            raise AssetError("v8 fixed policy drift")
        if not {"templates.jsonl", "runtime_instances.jsonl", "quarantine.json"}.issubset(m["files_sha256"]):
            raise AssetError("v8 payload binding incomplete")
        _verify_files(path.parent, m["files_sha256"], "v8 build payload drift: ")
        _verify_files(root(), m["raw_dependencies_sha256"], "v8 source drift: ")
        _verify_files(root(), m["ancestor_files_sha256"], "v8 ancestor drift: ")
        load_review(m["review_binding"])
        self.settings = m["policy"]
        self.templates = [json.loads(line) for line in
                          (path.parent / "templates.jsonl").read_text().splitlines()]
        rows = [json.loads(line) for line in
                (path.parent / "runtime_instances.jsonl").read_text().splitlines()]
        self.instances = {r["instance_id"]: r for r in rows}
        self.by_id = {t["template_id"]: t for t in self.templates}
        if len(self.instances) != len(rows) or len(self.by_id) != len(self.templates):
            raise AssetError("duplicate v8 identifier")
        if QUARANTINED_INSTANCES.intersection(self.instances) or QUARANTINED_TEMPLATES.intersection(self.by_id):
            raise AssetError("quarantined historical evidence in v8 runtime")
        if m.get("counts") != dict(templates=len(self.templates), instances=len(self.instances)):
            raise AssetError("v8 declared counts drift")
        for r in rows:
            if r.get("template_role") != "development_build":
                raise AssetError("holdout instance in v8 runtime")
            target = normalize_species(r["target"])["normalized"]
            if r["reference_signature"] != reaction_signature([canonical_side(r["reference_precursors"])], [target]):
                raise AssetError("v8 instance reaction identity drift")
            for source in r.get("source_bindings", []):
                if m["raw_dependencies_sha256"].get(source["path"]) != source["sha256"]:
                    raise AssetError("v8 corrected source binding incomplete")
        for t in self.templates:
            support = t["support_instances"]
            if (t.get("validation_status") != "source_reconstruction_passed"
                    or not support or len(set(support)) != len(support)
                    or not set(support).issubset(self.instances)):
                raise AssetError("v8 invalid template support")
            if t["template_role"] == "scope_template":
                if len({canonical_side([self.instances[i]["acceptor"]]) for i in support}) < 2:
                    raise AssetError("v8 scope has fewer than two distinct acceptors")
            elif t["template_role"] == "exact_instance_template":
                targets = {normalize_species(self.instances[i]["target"])["normalized"] for i in support}
                if set(t["allowed_targets"]) != targets:
                    raise AssetError("v8 exact target drift")
            else:
                raise AssetError("v8 template role invalid")
            for identifier in support:
                r = self.instances[identifier]
                if canonical_side(r["reference_precursors"]) not in [
                        o["precursors"] for o in apply_template(t, r["target"])]:
                    raise AssetError("v8 support replay drift: " + identifier)
        self.binding = dict(version=VERSION, manifest=str(path.relative_to(root())),
                            manifest_sha256=expected, namespace=NAMESPACE,
                            corrected_source_library=True)

    def evidence(self, reaction):
        e = super().evidence(reaction)
        t = self.by_id[e["template_id"]]
        e["historical_template_namespace"] = e["namespace"]
        e["namespace"] = NAMESPACE
        e["inherited_template"] = not t["template_id"].startswith("v8-exact:")
        e["source_correction"] = t.get("correction")
        e["source_library_version"] = VERSION
        e["normalized_gt_reference_only"] = True
        e["exact_formal_reference_ready"] = False
        return e


def load_registry(expected=None):
    if expected is None:
        s = config("glycoside-library-v8.json")
    else:
        # A frozen worker can bind this isolated version before the shared
        # configuration whitelist is updated. It cannot select external files.
        if (not isinstance(expected, dict)
                or not isinstance(expected.get("manifest"), str)
                or not isinstance(expected.get("manifest_sha256"), str)):
            raise AssetError("v8 frozen binding incomplete")
        s = expected
    rel = Path(s["manifest"])
    path = (root() / rel).resolve()
    if rel.is_absolute() or not path.is_relative_to(root().resolve()):
        raise AssetError("v8 manifest outside workspace")
    r = Registry(path, s["manifest_sha256"])
    if expected is not None and r.binding != expected:
        raise AssetError("v8 binding changed during run")
    return r


class GlycosideExpansion(v6.GlycosideExpansion):
    def __init__(self, key, config, domain_binding=None, **kwargs):
        ExpansionStrategy.__init__(self, key, config, **kwargs)
        self.registry = load_registry(domain_binding)
        self.profiling = dict(template_attempts=0, generation_seconds=0., generated_actions=0)


class DomainAwareQuickFilter(QuickKerasFilter):
    def __init__(self, key, config, domain_binding=None, **kwargs):
        QuickKerasFilter.__init__(self, key, config, **kwargs)
        self.registry = load_registry(domain_binding)

    def apply(self, reaction):
        if reaction.metadata.get("policy_name") == "glycoside":
            e = self.registry.evidence(reaction)
            reaction.metadata["task016_evidence"] = e
            reaction.metadata["filter_path"] = "known_hazards + validated v8 source guard; activity unverified"
            reaction.metadata.setdefault("review", {})[NAMESPACE] = e
            return
        QuickKerasFilter.apply(self, reaction)
