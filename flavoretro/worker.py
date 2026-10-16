"""One fresh process, one request, no result cache or legacy imports."""

import copy, hashlib, json, random, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from aizynthfinder.aizynthfinder import AiZynthFinder
from .contracts import SearchRequest
from .resources import sha, dumps, structure
from .workspace import root, active_data, config_path, config, PACKAGE
from .policies import hazard_reason
from .reviewed_resources import load_review


def route_identity(node):
    value = {k: node.get(k) for k in ("type", "smiles")}
    value["children"] = sorted(
        (route_identity(c) for c in node.get("children", [])),
        key=lambda x: json.dumps(x, sort_keys=True),
    )
    return value


def annotate(node, candidate, review=None, parent_smiles=None):
    children = node.get("children", [])
    steps = int(node.get("type") == "reaction")
    leaves = []
    for child in children:
        n, found = annotate(child, candidate, review, node.get("smiles") if node.get("type") == "mol" else None)
        steps += n
        leaves += found
    if review is not None and node.get("type") == "reaction":
        node["review"] = review.reaction([c["smiles"] for c in children if c.get("type") == "mol"], [parent_smiles] if parent_smiles else [])
        domain_evidence = node.get("metadata", {}).get("task016_evidence")
        if domain_evidence:
            node["review"]["task016"] = domain_evidence
    if node.get("type") == "mol" and not children:
        info = structure(node["smiles"])
        if review is not None:
            node["review"] = review.leaf(node["smiles"])
        node["closure"] = (
            "surrogate" if node.get("in_stock") and candidate else "partial"
        )
        node["evidence_basis"] = (
            "unreviewed_candidate_stock"
            if node["closure"] == "surrogate"
            else "unresolved"
        )
        node["structure_check"] = info
        node["hazard"] = hazard_reason(node["smiles"]) or "unknown_not_certified_safe"
        leaves.append(node)
    return steps, leaves


def effective_configuration(request, budget, settings, raw, review, domain_binding=None):
    expansion = {
        name: {
            "type": "template-based",
            "model": str(raw / model),
            "template": str(raw / template),
            "cutoff_number": budget["branching"],
            "use_rdchiral": True,
        }
        for name, model, template in [
            ("uspto", "uspto_model.onnx", "uspto_templates.csv.gz"),
            (
                "ringbreaker",
                "uspto_ringbreaker_model.onnx",
                "uspto_ringbreaker_templates.csv.gz",
            ),
        ]
    }
    load_review(review.binding)
    effective = {
        "expansion": expansion,
        "filter": {
            "reviewed_evidence": {"type": "flavoretro.policies.ReviewedEvidence", "review_binding": review.binding},
            "known_hazards": {"type": "flavoretro.policies.KnownHazards"},
            "uspto_filter": {
                "type": "quick-filter",
                "model": str(raw / "uspto_filter_model.onnx"),
                "filter_cutoff": 0.05,
            },
        },
        "stock": {
            "candidate": {
                "type": "flavoretro.policies.CandidateStock",
                "enabled": request.candidate_stock,
                "review_binding": review.binding,
            }
        },
        "search": {
            "algorithm": "flavoretro.search.SearchTree"
            if request.engine == "optimized"
            else "mcts",
            "algorithm_config": {
                "max_branching": budget["branching"],
                "max_nodes": budget["nodes"],
                "policy_weights": settings["policy_weights"],
                "puct_c_init": settings["puct_c_init"],
                "puct_c_base": settings["puct_c_base"],
                "prune_cycles_in_search": True,
            },
            "iteration_limit": budget["iterations"],
            "time_limit": budget["seconds"],
            "max_transforms": budget["depth"],
            "return_first": False,
        },
        "post_processing": {
            "min_routes": 1,
            "max_routes": settings["candidate_pool"],
            "all_routes": False,
        },
    }
    if domain_binding is not None:
        domain_module = {"v1": "flavoretro.glycoside_expansion", "v2": "flavoretro.glycoside_library", "v3": "flavoretro.glycoside_library_v3", "v4": "flavoretro.glycoside_library_v4", "v5": "flavoretro.glycoside_library_v5", "v6": "flavoretro.glycoside_library_v6", "v7": "flavoretro.glycoside_library_v7"}[request.glycoside_library_version]
        effective["expansion"]["glycoside"] = {"type": domain_module + ".GlycosideExpansion", "domain_binding": domain_binding}
        effective["filter"]["uspto_filter"].update(type=domain_module + ".DomainAwareQuickFilter", domain_binding=domain_binding)
        effective["search"]["algorithm_config"]["policy_weights"] = {**settings["policy_weights"], "glycoside": 1.0}
    if request.glycoside_library_version in {"v2", "v3", "v4", "v5", "v6", "v7"}:
        effective["search"]["algorithm_config"]["protect_generic_actions"] = 3
    if __import__("os").environ.get("FLAVORETRO_TASK016_TRACE") == "1":
        effective["search"]["algorithm_config"]["trace_actions"] = True
    return effective


def execute(payload):
    ROOT = root()
    resource_folder, resource_manifest, resource_pointer = active_data()
    request = SearchRequest.model_validate(payload["request"])
    run_id = payload["run_id"]
    settings = config("search.json")
    review = load_review(payload.get("review_binding"))
    domain_binding = None
    if request.glycoside_expansion:
        if request.glycoside_library_version == "v3":
            from .glycoside_library_v3 import load_registry
        elif request.glycoside_library_version == "v4":
            from .glycoside_library_v4 import load_registry
        elif request.glycoside_library_version == "v7":
            from .glycoside_library_v7 import load_registry
        elif request.glycoside_library_version == "v6":
            from .glycoside_library_v6 import load_registry
        elif request.glycoside_library_version == "v5":
            from .glycoside_library_v5 import load_registry
        elif request.glycoside_library_version == "v2":
            from .glycoside_library import load_registry
        else:
            from .glycoside_expansion import load_registry
        domain_binding = load_registry(payload.get("domain_binding")).binding
    action_trace = []
    source_manifest = json.loads((ROOT / "metadata/sources.json").read_text())
    assets = {
        x["source_path"]: x
        for x in source_manifest["files"]
        if x["role"] == "external_model"
    }
    for asset in assets.values():
        if sha(ROOT / asset["path"]) != asset["sha256"]:
            raise ValueError("model hash drift")
    raw = ROOT / "data/raw/legacy/data"
    phases = []
    routes = {}
    for phase_index, budget in enumerate(request.phases()):
        seed = (request.seed + phase_index) % 2**32
        random.seed(seed)
        np.random.seed(seed)
        effective = effective_configuration(request, budget, settings, raw, review, domain_binding)
        started = time.monotonic()
        finder = AiZynthFinder(configdict=copy.deepcopy(effective))
        finder.expansion_policy.select(["uspto", "ringbreaker"] + (["glycoside"] if domain_binding else []))
        finder.filter_policy.select(["reviewed_evidence", "known_hazards", "uspto_filter"])
        finder.stock.select(["candidate"])
        finder.target_smiles = request.smiles
        finder.prepare_tree()
        elapsed = finder.tree_search()
        load_review(review.binding)
        if domain_binding:
            load_registry(domain_binding)
        if hasattr(finder.tree, "action_trace"):
            action_trace.extend([{**e, "phase": phase_index} for e in finder.tree.action_trace])
        # Prefer actual explored frontier paths. The native state-score selector
        # can return only the unchanged root when no certified stock exists.
        frontier = [
            node
            for node in finder.tree.graph()
            if node is not finder.tree.root
            and (node.state.is_solved or not node.children)
        ]
        frontier.sort(
            key=lambda n: (
                not n.state.is_solved,
                len(n.state.expandable_mols),
                n.state.max_transforms,
                tuple(sorted(m.smiles for m in n.state.mols)),
            )
        )
        extracted = [
            node.to_reaction_tree() for node in frontier[: settings["candidate_pool"]]
        ]
        phases.append(
            dict(
                index=phase_index,
                seed=seed,
                budget=budget,
                effective_config=effective,
                engine_class=f"{type(finder.tree).__module__}.{type(finder.tree).__name__}",
                search_stats=finder.search_stats,
                profiling=finder.tree.profiling,
                **({"domain_profiling": finder.expansion_policy["glycoside"].profiling} if domain_binding else {}),
                search_seconds=elapsed,
                wall_seconds=time.monotonic() - started,
                node_count=len(list(finder.tree.graph().nodes)),
                discovery_stock=False,
                native_node_cap_equivalent=False
                if request.engine == "native"
                else True,
            )
        )
        for tree in extracted:
            route = tree.to_dict()
            signature = hashlib.sha256(
                json.dumps(route_identity(route), sort_keys=True).encode()
            ).hexdigest()
            steps, leaves = annotate(route, request.candidate_stock, review)
            unresolved = sum(x["closure"] == "partial" for x in leaves)
            hazard = sum(x["hazard"] != "unknown_not_certified_safe" for x in leaves)
            stereo = sum(
                x["structure_check"].get("unspecified_stereo", 0) for x in leaves
            )
            entry = dict(
                route_id=signature,
                tree=route,
                steps=steps,
                closure="surrogate" if leaves and not unresolved else "partial",
                native_solved=bool(tree.is_solved),
                evidence_closed=False,
                actionable=False,
                cost={
                    "steps": steps,
                    "unresolved_materials": unresolved,
                    "known_hazards": hazard,
                    "unspecified_leaf_stereo": stereo,
                },
                score=steps + 2 * unresolved + 5 * hazard + stereo,
                score_status="provisional_cost_lower_is_better",
                phase=phase_index,
            )
            if signature not in routes or entry["score"] < routes[signature]["score"]:
                routes[signature] = entry
    chosen = sorted(routes.values(), key=lambda x: (x["score"], x["route_id"]))
    return dict(
        schema_version=1,
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        status="ok",
        execution_source="live_aizynthfinder_mcts",
        request=request.payload(),
        **({"domain_binding": domain_binding} if domain_binding else {}),
        **({"action_trace": action_trace} if __import__("os").environ.get("FLAVORETRO_TASK016_TRACE") == "1" else {}),
        phases=phases,
        candidate_count=len(chosen),
        routes=chosen[: request.top_k],
        assets={k: v["sha256"] for k, v in assets.items()},
        source_manifest_sha256=sha(ROOT / "metadata/sources.json"),
        resources_sha256=resource_manifest["records_sha256"],
        config_sha256=sha(config_path("search.json")),
        resource_version=resource_pointer["version"],
        review_binding=review.binding,
        resource_manifest_sha256=resource_pointer["manifest_sha256"],
        code={
            str(p.relative_to(PACKAGE.parent)): sha(p)
            for p in sorted(PACKAGE.glob("*.py"))
        },
        release_ready=False,
        limitations=[
            "No independently reviewed production templates or stock",
            "No experimental feasibility certification",
            "No independent forward model; filter rejects only explicit disproved replay",
            "Unknown hazards and conditions remain unknown",
            "Native baseline does not share optimized node ceiling",
        ],
    )


if __name__ == "__main__":
    payload = json.load(sys.stdin)
    result = execute(payload)
    Path(payload["output"]).write_text(dumps(result))
