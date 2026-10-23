"""AiZynthFinder node overlay: PUCT, policy fusion, bounded alternatives."""

import math
import numpy as np
from aizynthfinder.search.mcts.node import MctsNode
from aizynthfinder.search.mcts.search import MctsSearchTree
from .ranking import ResearchRewardMixin


class Node(MctsNode):
    def trace_action(self, action, stage, **extra):
        if getattr(self.tree, "action_trace", None) is None or action.mol.smiles != self.tree.trace_target:
            return
        from .reviewed_resources import reaction_signature
        import copy
        try:
            for outcome_index, outcome in enumerate(action.reactants):
                if (stage.startswith("filtered_") or stage == "generic_protection_checked") and outcome_index != extra.get("tested_outcome_index"):
                    continue
                if stage == "mcts_action_created" and outcome_index != extra.get("created_outcome_index"):
                    continue
                self.tree.action_trace.append(dict(stage=stage, target=action.mol.smiles, outcome_index=outcome_index, precursor_smiles=[m.smiles for m in outcome], signature=reaction_signature([m.smiles for m in outcome], [action.mol.smiles]), policy=action.metadata.get("policy_name"), template_id=action.metadata.get("template_id", str(action.metadata.get("template_code"))), metadata=copy.deepcopy(action.metadata), **extra))
        except Exception as exc:
            self.tree.action_trace.append(dict(stage=stage, target=action.mol.smiles, status="generation_error", error=str(exc), **extra))

    def expand(self):
        if not self._algo_config.get("trace_actions"):
            return super().expand()
        import time
        start = time.monotonic()
        try:
            return super().expand()
        finally:
            self.tree.profiling["expansion_seconds"] += time.monotonic() - start

    def _filter_child_reaction(self, reaction):
        import time
        start = time.monotonic()
        rejected = super()._filter_child_reaction(reaction)
        if self._algo_config.get("trace_actions"):
            self.tree.profiling["filter_seconds"] += time.monotonic() - start
            self.trace_action(reaction.copy(index=reaction.index), "filtered_rejected" if rejected else "filtered_accepted", tested_outcome_index=reaction.index)
        return rejected

    def _fill_children_lists(self, actions, priors):
        if self._algo_config.get("trace_actions"):
            for action, prior in zip(actions, priors):
                self.trace_action(action, "generated", prior=float(prior))
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
        protection = self._algo_config.get("protect_generic_actions", 0)
        if protection:
            from .reviewed_resources import reaction_signature
            generic = [item for item in ranked if item[1][1].metadata.get("policy_name") != "glycoside"][:cap]
            protected = []; signatures = set()
            for item in generic:
                action = item[1][1]
                for outcome_index, outcome in enumerate(action.reactants):
                    variant = action.copy(index=outcome_index)
                    rejected = super()._filter_child_reaction(variant)
                    self.trace_action(variant, "generic_protection_checked", tested_outcome_index=outcome_index, rejected=rejected)
                    signature = reaction_signature([m.smiles for m in outcome], [action.mol.smiles])
                    if not rejected and signature not in signatures:
                        signatures.add(signature)
                        if item not in protected:protected.append(item)
                    if len(signatures) >= protection:break
                if len(signatures) >= protection:break
            protected_keys = {item[0] for item in protected}
            selected = (protected + [item for item in ranked if item[0] not in protected_keys])[:cap]
        selected_keys = {item[0] for item in selected}
        self._alternatives = [item[1] for item in ranked if item[0] not in selected_keys]
        if self._algo_config.get("trace_actions"):
            for _, (value, action) in selected:
                self.trace_action(action, "after_truncation", weighted_prior=float(value))
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
            if allocated and self._algo_config.get("trace_actions"):
                self.trace_action(self._children_actions[index], "mcts_action_created", created_outcome_index=outcome_index, created_node_count=len(allocated), created_child_slot=int(index), created_node_index=int(self.tree.created_nodes), raw_outcome_index=self._children_actions[index].metadata.get("raw_outcome_indices", list(range(len(original.reactants))))[outcome_index])
            self.tree.created_nodes += len(allocated)
            nodes.extend(allocated)
        if not nodes:
            self._disable_child(child_idx)
        return nodes


class SearchTree(ResearchRewardMixin, MctsSearchTree):
    def __init__(self, config, root_smiles=None):
        super().__init__(config=config, root_smiles=root_smiles)
        self.depths = {}
        self.created_nodes = 1
        if self.config.search.algorithm_config.get("trace_actions"):
            self.action_trace = []
            self.trace_target = root_smiles
            self.profiling.update(expansion_seconds=0.0, filter_seconds=0.0)
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
