"""AiZynthFinder node overlay: PUCT, policy fusion, bounded alternatives."""

import math
import numpy as np
from aizynthfinder.search.mcts.node import MctsNode
from aizynthfinder.search.mcts.search import MctsSearchTree


class Node(MctsNode):
    def _fill_children_lists(self, actions, priors):
        weights = self._algo_config.get("policy_weights", {})
        unique = {}
        for action, prior in zip(actions, priors):
            meta = action.metadata
            policy = meta.get("policy_name", "unknown")
            key = (
                action.mol.inchi_key,
                str(meta.get("template") or meta.get("template_code") or action.smarts),
            )
            value = max(float(prior), 1e-12) * weights.get(policy, 1.0)
            if key not in unique or value > unique[key][0]:
                unique[key] = (value, action)
        ranked = sorted(unique.items(), key=lambda x: (-x[1][0], x[0]))
        cap = self._algo_config["max_branching"]
        selected = ranked[:cap]
        self._alternatives = [x[1] for x in ranked[cap:]]
        norm = sum(x[1][0] for x in selected) or 1.0
        self._norm = norm
        self.tree.profiling["actions_seen"] += len(actions)
        self.tree.profiling["duplicate_actions"] += len(actions) - len(unique)
        super()._fill_children_lists(
            [x[1][1] for x in selected], [x[1][0] / norm for x in selected]
        )

    def _children_u(self):
        n = np.asarray(self._children_visitations, dtype=float)
        total = max(float(n.sum()), 1)
        c = self._algo_config.get("puct_c_init", 1.4) + math.log(
            (total + self._algo_config.get("puct_c_base", 19652) + 1)
            / self._algo_config.get("puct_c_base", 19652)
        )
        return c * np.asarray(self._children_priors) * math.sqrt(total) / (1 + n)

    def _select_child(self, index):
        child = super()._select_child(index)
        while child is None and getattr(self, "_alternatives", []):
            value, action = self._alternatives.pop(0)
            self._children_actions[index] = action
            self._children_priors[index] = value / self._norm
            self._children_values[index] = value / self._norm
            self._children_visitations[index] = 1
            self._children[index] = None
            self.tree.profiling["alternatives_tried"] += 1
            child = super()._select_child(index)
        return child

    def _create_children_nodes(self, states, child_idx):
        # Keep original reaction outcome indices even when earlier states are pruned.
        original = self._children_actions[child_idx]
        nodes = []
        first = True
        for outcome_index, state in enumerate(states):
            signature = tuple(sorted(m.inchi_key for m in state.mols))
            depth = int(state.max_transforms)
            if self.tree.depths.get(signature, 10**9) <= depth:
                self.tree.profiling["transpositions"] += 1
                continue
            remaining = self._algo_config["max_nodes"] - self.tree.created_nodes
            active = sum(x is not None for x in self._children)
            if remaining <= 0 or active >= self._algo_config["max_branching"]:
                break
            if first:
                index = child_idx
                self._children_actions[index] = original.copy(index=outcome_index)
                first = False
            else:
                index = self._expand_children_lists(child_idx, outcome_index)
            allocated = super()._create_children_nodes([state], index)
            for node in allocated:
                key = tuple(sorted(m.inchi_key for m in node.state.mols))
                self.tree.depths[key] = int(node.state.max_transforms)
            self.tree.created_nodes += len(allocated)
            nodes.extend(allocated)
        if not nodes:
            self._disable_child(child_idx)
        return nodes


class SearchTree(MctsSearchTree):
    def __init__(self, config, root_smiles=None):
        super().__init__(config=config, root_smiles=root_smiles)
        self.depths = {}
        self.created_nodes = 1
        self.profiling.update(
            actions_seen=0,
            duplicate_actions=0,
            alternatives_tried=0,
            transpositions=0,
            stop_reason="budget_or_exhaustion",
        )
        if root_smiles:
            self.root = Node.create_root(smiles=root_smiles, tree=self, config=config)
            self.depths[tuple(sorted(m.inchi_key for m in self.root.state.mols))] = 0

    def one_iteration(self):
        if self.created_nodes >= self.config.search.algorithm_config["max_nodes"]:
            self.profiling["stop_reason"] = "node_budget"
            raise StopIteration
        return super().one_iteration()
