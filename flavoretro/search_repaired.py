"""Development candidate: retain model proposals and add PUCT to a UCT floor."""
import math
import numpy as np
from aizynthfinder.search.mcts.node import MctsNode
from aizynthfinder.search.mcts.search import MctsSearchTree
from .ranking import ResearchRewardMixin

METHOD = "full-frontier-uct-floor-puct-v1"

def molecule_history(mol):
    history = []
    while mol is not None:
        history.append((mol.inchi_key, int(mol.transform), mol.mapped_smiles))
        mol = mol.parent
    return tuple(history)

def state_identity(state, blacklist):
    return (tuple(sorted(molecule_history(m) for m in state.mols)), tuple(sorted(blacklist)))

class Node(MctsNode):
    def _fill_children_lists(self, actions, priors):
        # Each action owns a specific TreeMolecule instance. Equal InChIKeys
        # alone do not imply interchangeable expansions (native removes by `is`).
        # Keep model ordering and all proposals; filters remain lazy and unchanged.
        weights = self._algo_config.get("policy_weights", {})
        values = [max(float(p), 1e-12) * weights.get(a.metadata.get("policy_name"), 1.0)
                  for a, p in zip(actions, priors)]
        norm = sum(values) or 1.0
        self.tree.profiling["actions_seen"] += len(actions)
        self.tree.profiling["actions_retained"] += len(actions)
        super()._fill_children_lists(list(actions), [v / norm for v in values])

    def _children_u(self):
        n = np.asarray(self._children_visitations, dtype=float)
        total = max(float(n.sum()), 1.0)
        base = self._algo_config.get("puct_c_base", 19652.0)
        c = self._algo_config.get("puct_c_init", 1.4) + math.log((total + base + 1) / base)
        puct = c * np.asarray(self._children_priors) * math.sqrt(total) / (1.0 + n)
        return super()._children_u() + 0.25 * puct

    def _generated_degeneracy(self, state, child_idx):
        # No cross-parent global pruning: different paths can yield different
        # valid routes. Only merge identical nonterminal siblings, including
        # per-molecule ancestry/depth/mapping and the node cycle-filter context.
        if state.is_terminal or self._degeneracy_check == "none":
            return False
        key = state_identity(state, self.blacklist)
        for child, action in zip(self._children, self._children_actions):
            if child is None or child.is_terminal():
                continue
            if state_identity(child.state, self.blacklist) != key:
                continue
            original = self._children_actions[child_idx]
            if action is not original:
                action.metadata.setdefault("additional_actions", []).append(dict(original.metadata))
            self.tree.profiling["sibling_reuses"] += 1
            return True
        return False

    def _create_children_nodes(self, states, child_idx):
        # Keep raw outcome indices even if preceding outcomes were rejected.
        original = self._children_actions[child_idx]
        nodes = []
        first_slot = True
        for outcome_index, state in enumerate(states):
            if self.tree.created_nodes >= self._algo_config["max_nodes"]:
                self.tree.profiling["stop_reason"] = "node_budget"
                break
            if self._generated_degeneracy(state, child_idx):
                continue
            if first_slot:
                index = child_idx
                self._children_actions[index] = original.copy(index=outcome_index)
                first_slot = False
            else:
                index = self._expand_children_lists(child_idx, outcome_index)
            if self._filter_child_reaction(self._children_actions[index]):
                self._disable_child(index)
                continue
            child = self.__class__(state=state, owner=self.tree, config=self._config, parent=self)
            self._children[index] = child
            self.tree.created_nodes += 1
            nodes.append(child)
        if not nodes:
            self._disable_child(child_idx)
        return nodes

class SearchTree(ResearchRewardMixin, MctsSearchTree):
    def __init__(self, config, root_smiles=None):
        super().__init__(config=config)
        self.created_nodes = 1 if root_smiles else 0
        self.profiling.update(method=METHOD, actions_seen=0, actions_retained=0,
            sibling_reuses=0, global_state_pruning=False, secondary_global_branch_cap=False,
            exploration_floor="native_UCT", puct_bonus_weight=0.25, stop_reason="budget_or_exhaustion")
        if root_smiles:
            self.root = Node.create_root(smiles=root_smiles, tree=self, config=config)

    def one_iteration(self):
        if self.created_nodes >= self.config.search.algorithm_config["max_nodes"]:
            self.profiling["stop_reason"] = "node_budget"
            raise StopIteration
        return super().one_iteration()
