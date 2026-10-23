"""Versioned research heuristics; scores are priorities, never success probabilities."""
from functools import lru_cache
import math
from rdkit import Chem
from .policies import hazard_reason

METHOD = "research-priority-v4"
WEIGHTS = {"stock_coverage": 0.28, "precursor_simplicity": 0.20,
           "model_support": 0.20, "route_economy": 0.12, "source_support": 0.20}


@lru_cache(maxsize=16384)
def molecular_features(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Cannot rank an unparseable structure")
    heavy = mol.GetNumHeavyAtoms()
    centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    # Transparent structural burden proxy, not an independently trained SA model.
    complexity = heavy * (1 + 0.08 * mol.GetRingInfo().NumRings() + 0.04 * len(centers))
    unspecified = sum(label == "?" for _, label in centers)
    carbon_unspecified = sum(label == "?" and mol.GetAtomWithIdx(index).GetAtomicNum() == 6 for index, label in centers)
    return heavy, complexity, unspecified, bool(hazard_reason(smiles)), Chem.MolToSmiles(mol, isomericSmiles=True), carbon_unspecified


def probability(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) and 0 <= number <= 1 else None


def priority(leaves, target, steps, depth, probabilities, source_count=0, protection_steps=0):
    features = [(molecular_features(smiles), bool(stock)) for smiles, stock in leaves]
    target_burden = max(molecular_features(target)[1], 1.0)
    # Preparing the same structure repeatedly is no additional search progress.
    # Preserve real multiplicities in route/cost/economy, not in coverage/burden.
    unique = list({f[4]: (f, stock) for f, stock in features}.values())
    total_heavy = sum(f[0] for f, _ in unique) or 1
    unresolved = [(f, stock) for f, stock in features if not stock]
    coverage = sum(f[0] for f, stock in unique if stock) / total_heavy
    burden = sum(f[1] for f, stock in unique if not stock) / target_burden
    known = [p for p in probabilities if p is not None]
    # Missing evidence contributes no support. A real zero remains a real zero.
    model = (math.exp(sum(math.log(p) for p in known) / len(known))
             if known and all(p > 0 for p in known) else 0.0)
    model *= len(known) / max(len(probabilities), 1)
    economy = 1 / (1 + 0.15 * steps + 0.10 * depth + 0.05 * max(0, len(leaves) - 1))
    components = {"stock_coverage": coverage, "precursor_simplicity": math.exp(-burden),
                  "model_support": model, "route_economy": economy,
                  "source_support": source_count / max(steps, 1)}
    hazards = sum(f[3] for f, _ in features)
    stereo = sum(f[2] for f, _ in features)
    carbon_stereo = sum(f[5] for f, _ in features)
    penalty = math.exp(-0.25 * hazards - 0.08 * carbon_stereo - 0.08 * protection_steps)
    quality = sum(WEIGHTS[key] * value for key, value in components.items()) * penalty
    closed = bool(features) and not unresolved
    score = 60 + 40 * quality if closed else 60 * quality
    return {"score": score, "score_status": "research_priority_higher_is_better",
            "ranking_method": METHOD, "score_components": components,
            "score_weights": WEIGHTS, "score_penalty": penalty,
            "ranking_metrics": {"unresolved_complexity_ratio": burden,
                "model_probability_geomean": (0.0 if any(p == 0 for p in known) else
                    math.exp(sum(math.log(p) for p in known) / len(known))) if known else None,
                "model_probability_coverage": len(known) / max(len(probabilities), 1),
                "max_depth": depth, "leaf_count": len(leaves), "unique_leaf_count": len(unique)},
            "steps": steps, "closure": "surrogate" if closed else "partial",
            "cost": {"steps": steps, "unresolved_materials": len(unresolved),
                     "known_hazards": hazards, "unspecified_leaf_stereo": stereo, "unspecified_leaf_carbon_stereo": carbon_stereo,
                     "unassigned_hetero_stereo_flags": stereo - carbon_stereo},
            "legacy_cost": steps + 2 * len(unresolved) + 5 * hazards + stereo}


def rank_tree(tree):
    leaves, probabilities = [], []
    steps = depth = 0
    def visit(node, level):
        nonlocal steps, depth
        if node.get("type") == "reaction":
            steps += 1
            probabilities.append(probability(node.get("metadata", {}).get("policy_probability")))
            level += 1
            depth = max(depth, level)
        children = node.get("children", [])
        if node.get("type") == "mol" and not children:
            leaves.append((node["smiles"], node.get("in_stock", False)))
        for child in children:
            visit(child, level)
    visit(tree, 0)
    from .route_quality import diagnostics
    quality = diagnostics(tree)
    result = priority(leaves, tree["smiles"], steps, depth, probabilities,
                      quality['source_supported_steps'], quality['protection_only_steps'])
    result['route_quality'] = quality
    return result


def ranked_routes(routes):
    """Stable true ties; never add arbitrary jitter to the numeric score."""
    return sorted(routes, key=lambda route: (-route["score"], route["route_id"]))


class ResearchRewardMixin:
    def compute_reward(self, node):
        if not self.config.search.algorithm_config.get("research_reward", False):
            return super().compute_reward(node)
        actions = []
        current = node
        while current.parent is not None:
            actions.append(current.parent[current]["action"])
            current = current.parent
        from .route_quality import protection_only, source_supported
        metrics = priority(
            [(mol.smiles, stock) for mol, stock in zip(node.state.mols, node.state.in_stock_list)],
            self.root.state.mols[0].smiles, len(actions), node.state.max_transforms,
            [probability(action.metadata.get("policy_probability")) for action in actions],
            sum(source_supported(action.metadata) for action in actions),
            sum(protection_only(action.mol.smiles, [m.smiles for m in action.reactants[action.index]]) for action in actions))
        self.profiling["research_reward_evaluations"] = self.profiling.get("research_reward_evaluations", 0) + 1
        # Same bounded priority guides real backpropagation. UCT/PUCT selection stays intact.
        return metrics["score"] / 100.0
