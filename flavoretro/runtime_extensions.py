"""Explicit runtime bindings for local literature and historical stock assets."""
import importlib
from pathlib import Path
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from .workspace import config, root, AssetError
from .resources import sha
from .literature_policy import Registry

DOMAIN_MODULES = {"v1": "glycoside_expansion", "v2": "glycoside_library", **{f"v{i}": f"glycoside_library_v{i}" for i in range(3, 9)}}


def literature_registry(expected=None):
    settings = expected if expected is not None else config("runtime-candidates.json")["literature"]
    registry = Registry(settings["manifest"], settings["manifest_sha256"])
    if expected is not None and registry.binding != expected:
        raise AssetError("literature binding changed during run")
    return registry


def stock_binding(profile, expected=None):
    if profile != "zinc":
        raise AssetError("unsupported public stock profile")
    settings = config("runtime-candidates.json")["stock"][profile]
    binding = {"profile": profile, **settings}
    if expected is not None and binding != expected:
        raise AssetError("stock configuration changed during run")
    rel = Path(binding["path"])
    path = (root() / rel).resolve()
    if rel.is_absolute() or not path.is_relative_to(root().resolve()):
        raise AssetError("stock path outside workspace")
    if not path.is_file() or sha(path) != binding["sha256"]:
        raise AssetError("stock asset absent or drift")
    if binding.get("current_supplier_verified") is not False:
        raise AssetError("unsupported supplier evidence promotion")
    return binding


def extend_configuration(effective, request, literature=None, stock=None, domain=None, flavanone=None):
    effective["search"]["exclude_target_from_stock"] = True
    if literature is not None:
        effective["expansion"]["literature"] = {"type": "flavoretro.literature_policy.LiteratureExpansion", "literature_binding": literature}
        effective["filter"]["uspto_filter"].update(type="flavoretro.runtime_extensions.SourceAndDomainFilter", literature_binding=literature, domain_binding=domain, domain_version=request.glycoside_library_version)
        weights = effective["search"]["algorithm_config"]["policy_weights"]
        effective["search"]["algorithm_config"]["policy_weights"] = {**weights, "literature": 1.0}
    if flavanone is not None:
        if request.engine != "native" or domain is not None or literature is not None:
            raise AssetError("flavanone policy requires unmodified native engine and separate source classes")
        from .flavanone_opening import load_binding
        binding = load_binding(flavanone)
        effective["expansion"]["flavanone_opening"] = {"type": "flavoretro.flavanone_opening.FlavanoneOpening", "scope_binding": binding}
        effective["filter"]["uspto_filter"].update(type="flavoretro.flavanone_opening.GraphRuleQuickFilter", scope_binding=binding)
    if stock is not None:
        effective["stock"] = {"public_candidate": {"type": "inchiset", "path": str(root() / stock["path"])}}
    return effective


class SourceAndDomainFilter(QuickKerasFilter):
    """Exact literature and domain guards stay separate; generic actions use model."""
    def __init__(self, key, config, literature_binding, domain_binding=None, domain_version="v1", **kwargs):
        super().__init__(key, config, **kwargs)
        self.literature = literature_registry(literature_binding)
        self.domain = None
        if domain_binding is not None:
            if domain_version not in DOMAIN_MODULES:
                raise AssetError("unknown domain version")
            module = importlib.import_module("flavoretro." + DOMAIN_MODULES[domain_version])
            self.domain = module.load_registry(domain_binding)

    def apply(self, reaction):
        policy = reaction.metadata.get("policy_name")
        if policy == "literature":
            evidence = self.literature.evidence(reaction)
            reaction.metadata["task022_evidence"] = evidence
            reaction.metadata.setdefault("review", {})["task022"] = evidence
            reaction.metadata["filter_path"] = "known hazards + exact source record; no independent chemistry claim"
        elif policy == "glycoside" and self.domain is not None:
            evidence = self.domain.evidence(reaction)
            reaction.metadata["task016_evidence"] = evidence
            reaction.metadata.setdefault("review", {})[evidence.get("namespace", "domain")] = evidence
            reaction.metadata["filter_path"] = "known hazards + bound domain source guard; activity unverified"
        else:
            super().apply(reaction)
