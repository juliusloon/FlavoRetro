import math
import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch
import numpy as np
from aizynthfinder.context.config import Configuration
from flavoretro.search import Node, SearchTree

class OptimizationContracts(unittest.TestCase):
    def setUp(self):
        config=Configuration()
        config.search.algorithm_config.update(max_nodes=5,max_branching=2,policy_weights={"a":1.0,"b":0.5})
        self.tree=SearchTree(config, "CCO")
        self.node=self.tree.root

    def action(self,key,policy="a"):
        action = NS(mol=NS(inchi_key="target"),metadata={"template":key,"policy_name":policy},smarts=key,index=0)
        action.copy = lambda index: NS(**{**vars(action), "index":index})
        return action

    def state(self,key,depth):
        return NS(mols=[NS(inchi_key=key)],max_transforms=depth)

    def test_fusion_dedup_and_branch_cap(self):
        actions=[self.action("x"),self.action("x","b"),self.action("y"),self.action("z")]
        self.node._fill_children_lists(actions,[0.4,0.9,0.2,0.1])
        self.assertIs(self.node._children_actions[0],actions[1])
        self.assertEqual(len(self.node._children_actions),2)
        self.assertAlmostEqual(sum(self.node._children_priors),1)
        self.assertEqual(self.tree.profiling["duplicate_actions"],1)
        self.assertEqual(len(self.node._alternatives),1)

    def test_puct_prior_and_visitation_tradeoff(self):
        self.node._children_visitations=[4,1];self.node._children_priors=[0.75,0.25]
        config=self.node._algo_config
        c=config.get("puct_c_init",1.4)+math.log((5+config.get("puct_c_base",19652)+1)/config.get("puct_c_base",19652))
        np.testing.assert_allclose(self.node._children_u(),c*np.array([0.75,0.25])*math.sqrt(5)/np.array([5,2]))

    def test_disabled_action_tries_retained_alternative(self):
        self.node._fill_children_lists([self.action("a"),self.action("b"),self.action("c")],[0.6,0.3,0.1])
        replacement=object()
        with patch("aizynthfinder.search.mcts.node.MctsNode._select_child",side_effect=[None,replacement]):
            self.assertIs(self.node._select_child(0),replacement)
        self.assertEqual(self.node._children_actions[0].metadata["template"],"c")
        self.assertEqual(self.tree.profiling["alternatives_tried"],1)

    def allocate(self,states):
        self.node._fill_children_lists([self.action("outcomes")],[1.0])
        with patch("aizynthfinder.search.mcts.node.MctsNode._create_children_nodes",side_effect=lambda accepted,index:[NS(state=s) for s in accepted]):
            return self.node._create_children_nodes(states,0)

    def test_multi_outcome_obeys_remaining_node_and_branch_slots(self):
        self.tree.created_nodes=4
        nodes=self.allocate([self.state("a",1),self.state("b",1),self.state("c",1)])
        self.assertEqual(len(nodes),1);self.assertEqual(self.tree.created_nodes,5)
        with self.assertRaises(StopIteration): self.tree.one_iteration()

    def test_transposition_rejects_deeper_state(self):
        self.tree.depths[("a",)]=1
        nodes=self.allocate([self.state("a",2),self.state("b",1)])
        self.assertEqual([n.state.mols[0].inchi_key for n in nodes],["b"])
        self.assertEqual(self.tree.profiling["transpositions"],1)

    def test_duplicate_states_within_one_expansion_not_allocated_twice(self):
        nodes=self.allocate([self.state("a",1),self.state("a",1)])
        self.assertEqual(len(nodes),1)

    def test_filtered_outcome_keeps_original_reaction_index(self):
        self.tree.depths[("a",)]=0
        self.node._fill_children_lists([self.action("outcomes")],[1.0])
        def create(states,index):
            self.assertEqual(self.node._children_actions[index].index,1)
            return [NS(state=s) for s in states]
        with patch("aizynthfinder.search.mcts.node.MctsNode._create_children_nodes",side_effect=create):
            self.node._create_children_nodes([self.state("a",1),self.state("b",1)],0)
