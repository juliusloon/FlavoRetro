import unittest
from unittest.mock import patch
from types import SimpleNamespace as NS
import numpy as np
from aizynthfinder.context.config import Configuration
from aizynthfinder.chem import TreeMolecule, SmilesBasedRetroReaction
from aizynthfinder.search.mcts.node import MctsNode
from aizynthfinder.search.mcts.state import MctsState
from flavoretro.search_repaired import SearchTree, state_identity

class Contracts(unittest.TestCase):
    def setUp(self):
        self.config=Configuration()
        self.config.search.algorithm_config.update(max_nodes=100, max_branching=12,
            policy_weights={"uspto":1.0,"ringbreaker":0.65})
        self.tree=SearchTree(self.config,"CCO");self.node=self.tree.root
    def action(self,mol,prec="C.O",policy="uspto"):
        return SmilesBasedRetroReaction(mol, reactants_str=prec, metadata={"policy_name":policy})
    def test_all_per_molecule_model_proposals_retained_without_query(self):
        mols=[TreeMolecule(None,smiles="CCO"),TreeMolecule(None,smiles="CCO")]
        actions=[self.action(m,policy=p) for m in mols for p in ["uspto","ringbreaker"] for i in range(12)]
        self.node._fill_children_lists(actions,[0.1]*48)
        self.assertEqual(self.node._children_actions,actions)
        self.assertTrue(all(a.unqueried for a in actions))
        self.assertAlmostEqual(sum(self.node._children_priors),1.0)
        self.assertEqual(self.tree.profiling["actions_retained"],48)
    def test_floor_explores_zero_prior_and_puct_still_changes_selection(self):
        self.node._children_visitations=[2,2];self.node._children_priors=[0.9,0.1]
        floor=MctsNode._children_u(self.node);bonus=self.node._children_u()-floor
        self.assertTrue(np.all(bonus>0));self.assertGreater(bonus[0],bonus[1])
        self.node._children_priors=[0,1]
        self.assertEqual(self.node._children_u()[0],floor[0])
    def test_identity_distinguishes_depth_assignment_history_and_cycle_context(self):
        root=TreeMolecule(None,smiles="CCO")
        other=TreeMolecule(None,smiles="CCN")
        a=TreeMolecule(root,smiles="C",transform=1);b=TreeMolecule(root,smiles="O",transform=2)
        c=TreeMolecule(root,smiles="C",transform=2);d=TreeMolecule(root,smiles="O",transform=1)
        s=lambda ms:MctsState(ms,self.config)
        self.assertNotEqual(state_identity(s([a,b]),set()),state_identity(s([c,d]),set()))
        e=TreeMolecule(other,smiles="C",transform=1)
        self.assertNotEqual(state_identity(s([a,b]),set()),state_identity(s([e,b]),set()))
        self.assertNotEqual(state_identity(s([a,b]),{"x"}),state_identity(s([a,b]),{"y"}))
    def test_filtered_outcomes_keep_raw_indices_and_only_global_node_cap(self):
        action=self.action(self.node.state.mols[0]);self.node._fill_children_lists([action],[1])
        self.tree.created_nodes=98
        states=[MctsState([TreeMolecule(action.mol,smiles=s)],self.config) for s in ["C","O","N","CC"]]
        with patch.object(self.node,"_filter_child_reaction",side_effect=lambda r:r.index==0):
            nodes=self.node._create_children_nodes(states,0)
        self.assertEqual(len(nodes),2);self.assertEqual(self.tree.created_nodes,100)
        self.assertEqual([self.node[n]["action"].index for n in nodes],[1,2])
        with self.assertRaises(StopIteration):self.tree.one_iteration()
    def test_solved_route_alternatives_preserved(self):
        action=self.action(self.node.state.mols[0]);self.node._fill_children_lists([action],[1])
        state=MctsState([TreeMolecule(action.mol,smiles="C")],self.config)
        state.is_terminal=True;state.is_solved=True
        with patch.object(self.node,"_filter_child_reaction",return_value=False):
            nodes=self.node._create_children_nodes([state,state],0)
        self.assertEqual(len(nodes),2)

class RuntimeSelection(unittest.TestCase):
    def effective(self, request):
        from flavoretro.worker import effective_configuration
        from flavoretro.workspace import config
        with patch('flavoretro.worker.load_review'):
            return effective_configuration(request,request.phases()[0],config('search.json'),__import__('pathlib').Path('unused_models'),NS(binding={}),{'fixture':True} if request.glycoside_expansion else None)
    def test_generic_actual_path_and_model_budgets(self):
        from flavoretro.contracts import SearchRequest
        r=SearchRequest(smiles='CCO',mode='quick',branching=12,nodes=25000)
        c=self.effective(r)
        self.assertEqual(c['search']['algorithm'],'flavoretro.search_repaired.SearchTree')
        self.assertNotIn('max_branching',c['search']['algorithm_config'])
        self.assertEqual(c['search']['algorithm_config']['max_nodes'],25000)
        self.assertEqual([p['cutoff_number'] for p in c['expansion'].values()],[12,12])
        self.assertEqual(c['search']['algorithm_config']['policy_weights'],{'uspto':1.0,'ringbreaker':0.65})
    def test_knowledge_paths_keep_legacy_and_native_dff_keeps_native(self):
        from flavoretro.contracts import SearchRequest
        for r in [SearchRequest(smiles='CCO',glycoside_expansion=True),SearchRequest(smiles='CCO',glycoside_expansion=True,glycoside_library_version='v8'),SearchRequest(smiles='CCO',literature_expansion=True)]:
            c=self.effective(r)
            self.assertEqual(c['search']['algorithm'],'flavoretro.search.SearchTree')
            self.assertIn('max_branching',c['search']['algorithm_config'])
        for r in [SearchRequest(smiles='CCO',engine='native'),SearchRequest(smiles='CCO',engine='native',flavanone_opening=True)]:
            self.assertEqual(self.effective(r)['search']['algorithm'],'mcts')

if __name__=="__main__":unittest.main()
