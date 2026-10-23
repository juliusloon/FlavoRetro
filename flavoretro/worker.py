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
from .ranking import METHOD as RANKING_METHOD, rank_tree, ranked_routes, molecular_features
from .route_quality import diverse_top, material_subgoal


def extraction_nodes(tree):
    nodes = [node for node in tree.graph() if node is not tree.root]
    frontier = [node for node in nodes if node.state.is_solved or not node.children]
    return nodes, frontier


def route_identity(node):
    value = {k: node.get(k) for k in ("type", "smiles")}
    value["children"] = sorted(
        (route_identity(c) for c in node.get("children", [])),
        key=lambda x: json.dumps(x, sort_keys=True),
    )
    return value



def source_variant(route):
    """Keep only actual generated source witnesses when molecular routes deduplicate."""
    ids = []
    def visit(node):
        evidence = node.get("metadata", {}).get("task022_evidence", {})
        if evidence.get("lab_case"):
            ids.append(evidence["source_reaction_id"])
        for child in node.get("children", []):
            visit(child)
    visit(route)
    return {"source_reaction_ids": sorted(set(ids)), "tree": copy.deepcopy(route)} if ids else None


def merge_source_variants(previous, entry):
    variants = {tuple(v["source_reaction_ids"]): v for v in (previous or {}).get("source_variants", [])}
    variant = source_variant(entry["tree"])
    if variant:
        variants.setdefault(tuple(variant["source_reaction_ids"]), variant)
    return list(variants.values())


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
        source_evidence = node.get("metadata", {}).get("task022_evidence")
        if source_evidence:
            node["review"]["task022"] = source_evidence
        scope_hypothesis = node.get("metadata", {}).get("task022_scope_hypothesis")
        if scope_hypothesis:
            node["review"]["source_class_hypothesis"] = scope_hypothesis
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
        features = molecular_features(node["smiles"])
        info["unspecified_carbon_stereo"] = features[5]
        info["unassigned_hetero_stereo_flags"] = features[2] - features[5]
        node["structure_check"] = info
        node["hazard"] = hazard_reason(node["smiles"]) or "unknown_not_certified_safe"
        if node["closure"] == "partial":
            node["subgoal"] = material_subgoal(node["smiles"])
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
            "algorithm": ("flavoretro.search_repaired.SearchTree"
                          if not request.glycoside_expansion and not request.literature_expansion
                          else "flavoretro.search.SearchTree")
            if request.engine == "optimized"
            else "mcts",
            "algorithm_config": {
                "max_branching": budget["branching"],
                "max_nodes": budget["nodes"],
                "policy_weights": settings["policy_weights"],
                "puct_c_init": settings["puct_c_init"],
                "puct_c_base": settings["puct_c_base"],
                "prune_cycles_in_search": True,
                "research_reward": request.engine == "optimized",
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
    # Generic repair has no second global branch truncation. The branching
    # request still controls each model per expandable molecule.
    if request.engine == "optimized" and not request.glycoside_expansion and not request.literature_expansion:
        effective["search"]["algorithm_config"].pop("max_branching", None)
    if domain_binding is not None:
        domain_module = {"v1": "flavoretro.glycoside_expansion", "v2": "flavoretro.glycoside_library", "v3": "flavoretro.glycoside_library_v3", "v4": "flavoretro.glycoside_library_v4", "v5": "flavoretro.glycoside_library_v5", "v6": "flavoretro.glycoside_library_v6", "v7": "flavoretro.glycoside_library_v7", "v8": "flavoretro.glycoside_library_v8"}[request.glycoside_library_version]
        effective["expansion"]["glycoside"] = {"type": domain_module + ".GlycosideExpansion", "domain_binding": domain_binding}
        effective["filter"]["uspto_filter"].update(type=domain_module + ".DomainAwareQuickFilter", domain_binding=domain_binding)
        effective["search"]["algorithm_config"]["policy_weights"] = {**settings["policy_weights"], "glycoside": 1.0}
    if request.glycoside_library_version in {"v2", "v3", "v4", "v5", "v6", "v7", "v8"}:
        effective["search"]["algorithm_config"]["protect_generic_actions"] = 3
    if __import__("os").environ.get("FLAVORETRO_TASK016_TRACE") == "1":
        effective["search"]["algorithm_config"]["trace_actions"] = True
    return effective


def execute(payload):
    ROOT = root()
    resource_folder, resource_manifest, resource_pointer = active_data()
    request = SearchRequest.model_validate(payload["request"])
    run_id = payload["run_id"]
    evaluation = payload.get('research_evaluation')
    if evaluation is not None:
        from .research_evaluation import validate
        validate(evaluation, request)
    legacy_ranking = evaluation is not None and evaluation['arm'] == 'A'

    settings = config("search.json")
    review = load_review(payload.get("review_binding"))
    domain_binding = None
    if request.glycoside_expansion:
        if request.glycoside_library_version == "v8":
            from .glycoside_library_v8 import load_registry
        elif request.glycoside_library_version == "v3":
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
    from .runtime_extensions import literature_registry, stock_binding, extend_configuration
    literature = literature_registry(payload.get("literature_binding")) if request.literature_expansion else None
    public_stock = stock_binding(request.stock_profile, payload.get("stock_binding")) if request.stock_profile != "reviewed" else None
    from .flavanone_opening import load_binding as load_flavanone_binding
    flavanone = load_flavanone_binding(payload.get("flavanone_binding")) if request.flavanone_opening else None
    action_trace = []
    root_actions = []
    any_tree_solved = False
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
        effective = extend_configuration(effective, request, literature.binding if literature else None, public_stock, domain_binding, flavanone)
        if evaluation is not None:
            effective['search']['algorithm_config']['research_reward'] = evaluation['arm'] == 'C'
        started = time.monotonic()
        finder = AiZynthFinder(configdict=copy.deepcopy(effective))
        from .stock_identity import install as install_stock_identity
        install_stock_identity(finder)
        finder.expansion_policy.select(["uspto", "ringbreaker"] + (["glycoside"] if domain_binding else []) + (["literature"] if literature else []) + (["flavanone_opening"] if flavanone else []))
        finder.filter_policy.select(["reviewed_evidence", "known_hazards", "uspto_filter"])
        finder.stock.select(["public_candidate"] if public_stock else ["candidate"])
        finder.target_smiles = request.smiles
        from aizynthfinder.chem import Molecule
        root_in_stock_before = Molecule(smiles=request.smiles) in finder.stock
        finder.prepare_tree()
        if finder.tree.root.state.is_solved:
            raise ValueError("target exclusion failed")
        elapsed = finder.tree_search()
        load_review(review.binding)
        if domain_binding:
            load_registry(domain_binding)
        if literature:
            literature_registry(literature.binding)
        if public_stock:
            stock_binding(request.stock_profile, public_stock)
        if flavanone:
            load_flavanone_binding(flavanone)
        for child_index, child in enumerate(finder.tree.root.children):
            action = finder.tree.root[child]["action"]
            if action.unqueried:
                raise ValueError("created root action unexpectedly unqueried")
            root_actions.append({"phase": phase_index, "child_index": child_index, "product": action.mol.smiles, "precursors": [m.smiles for m in action.reactants[action.index]], "policy": action.metadata.get("policy_name"), "template_id": action.metadata.get("template_id", str(action.metadata.get("template_code"))), "child_solved": bool(child.state.is_solved), "metadata": action.metadata})
        any_tree_solved = any_tree_solved or any(n.state.is_solved for n in finder.tree.graph())
        if hasattr(finder.tree, "action_trace"):
            action_trace.extend([{**e, "phase": phase_index} for e in finder.tree.action_trace])
        # Prefer actual explored frontier paths. The native state-score selector
        # can return only the unchanged root when no certified stock exists.
        # Preserve actual explored internal paths as partial research candidates.
        # Continuing search must not erase a previously useful source prefix.
        candidates, frontier = extraction_nodes(finder.tree)
        extracted = (node.to_reaction_tree() for node in candidates)
        phases.append(
            dict(
                index=phase_index,
                seed=seed,
                budget=budget,
                effective_config=effective,
                engine_class=f"{type(finder.tree).__module__}.{type(finder.tree).__name__}",
                root_node_class=f"{type(finder.tree.root).__module__}.{type(finder.tree.root).__name__}",
                selected_policies=list(finder.expansion_policy.selection),
                stock_identity_class=type(finder.stock).__module__ + "." + type(finder.stock).__name__,
                stock_identity_profile=dict(finder.stock.identity_profile),
                selected_policy_classes={key: type(finder.expansion_policy[key]).__module__ + "." + type(finder.expansion_policy[key]).__name__ for key in finder.expansion_policy.selection},
                actual_quick_filter_class=type(finder.filter_policy["uspto_filter"]).__module__ + "." + type(finder.filter_policy["uspto_filter"]).__name__,
                **({"flavanone_profiling": finder.expansion_policy["flavanone_opening"].profiling} if flavanone else {}),
                search_stats=finder.search_stats,
                profiling=finder.tree.profiling,
                **({"domain_profiling": finder.expansion_policy["glycoside"].profiling} if domain_binding else {}),
                search_seconds=elapsed,
                wall_seconds=time.monotonic() - started,
                node_count=len(list(finder.tree.graph().nodes)),
                frontier_count=len(frontier),
                extracted_node_count=len(candidates),
                extraction_method="all_generated_prefixes_v1",
                discovery_stock=False,
                root_in_stock_before=root_in_stock_before,
                stock_profile=request.stock_profile,
                **({"literature_profiling": finder.expansion_policy["literature"].profiling} if literature else {}),
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
            metrics = rank_tree(route)
            if legacy_ranking:
                metrics.update(score=metrics['legacy_cost'], score_status='provisional_cost_lower_is_better', ranking_method='legacy-cost-ablation-v1')
            entry = dict(route_id=signature, tree=route, **metrics,
                         native_solved=bool(tree.is_solved), evidence_closed=False,
                         actionable=False, phase=phase_index)
            previous = routes.get(signature)
            variants = merge_source_variants(previous, entry)
            if signature not in routes or ((entry["score"] < routes[signature]["score"]) if legacy_ranking else (entry["score"] > routes[signature]["score"])):
                routes[signature] = entry
            routes[signature]["source_variants"] = variants
    chosen = sorted(routes.values(), key=lambda row:(row["score"],row["route_id"])) if legacy_ranking else ranked_routes(routes.values())
    candidate_ranking = []
    for rank, entry in enumerate(chosen, 1):
        entry["rank"] = rank
        candidate_ranking.append({key: entry[key] for key in
            ("route_id", "rank", "score", "score_status", "ranking_method", "score_components",
             "score_penalty", "ranking_metrics", "route_quality", "steps", "closure", "cost", "legacy_cost", "phase")})
    displayed = chosen[:request.top_k] if legacy_ranking else diverse_top(chosen, request.top_k)
    for entry in displayed:
        _, leaves = annotate(entry["tree"], request.candidate_stock, review)
        for leaf in leaves:
            leaf["stock_profile"] = request.stock_profile
            if public_stock and leaf["closure"] == "surrogate":
                leaf["evidence_basis"] = public_stock["kind"]
                leaf["stock_binding"] = public_stock
    return dict(
        schema_version=1,
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        status="ok",
        execution_source="live_aizynthfinder_mcts",
        request=request.payload(),
        **({"domain_binding": domain_binding} if domain_binding else {}),
        **({"action_trace": action_trace} if __import__("os").environ.get("FLAVORETRO_TASK016_TRACE") == "1" else {}),
        root_actions=root_actions,
        any_tree_solved=any_tree_solved,
        stock_profile=request.stock_profile,
        **({"flavanone_binding": flavanone} if flavanone else {}),
        **({"stock_binding": public_stock} if public_stock else {}),
        **({"literature_binding": literature.binding,
             "development_contexts": [c for c in literature.development_contexts
                 if molecular_features(c["target"])[4] == molecular_features(request.smiles)[4]]} if literature else {}),
        phases=phases,
        candidate_count=len(chosen),
        ranking_method="legacy-cost-ablation-v1" if legacy_ranking else RANKING_METHOD,
        extraction_method="all_generated_prefixes_v1",
        **({"research_evaluation": evaluation} if evaluation is not None else {}),
        candidate_ranking=candidate_ranking,
        routes=displayed,
        diversity={"method": "critical_edges_O_acetyl_stripped_v1", "candidate_families": len({row["route_quality"]["family_id"] for row in chosen}), "displayed_families": len({row["route_quality"]["family_id"] for row in displayed})},
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
