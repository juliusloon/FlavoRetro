import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from aizynthfinder.context.config import Configuration
from aizynthfinder.chem import TreeMolecule, SmilesBasedRetroReaction
from aizynthfinder.search.mcts.state import MctsState
from flavoretro.ranking import priority, rank_tree, ranked_routes, probability
from flavoretro.search_repaired import SearchTree


def tree(p=0.5, precursors=("CC", "O"), stock=False):
    return {"type":"mol", "smiles":"CCO", "children":[{"type":"reaction",
        "metadata":{"policy_probability":p}, "children":[
            {"type":"mol","smiles":s,"in_stock":stock} for s in precursors]}]}


class RouteRanking(unittest.TestCase):
    def test_equal_legacy_cost_separates_model_support(self):
        low, high = rank_tree(tree(0.01)), rank_tree(tree(0.9))
        self.assertEqual(low["legacy_cost"], high["legacy_cost"])
        self.assertGreater(high["score"],low["score"])

    def test_same_counts_distinguish_unresolved_structural_burden(self):
        low=rank_tree(tree(0.5,("CCCCCCCC",)))
        high=rank_tree(tree(0.5,("C",)))
        self.assertEqual(low["legacy_cost"],high["legacy_cost"])
        self.assertGreater(high["score"],low["score"])

    def test_closed_band_is_above_any_unclosed_route(self):
        closed=rank_tree(tree(0.0,stock=True))
        partial=rank_tree(tree(1.0))
        self.assertGreaterEqual(closed["score"],60)
        self.assertLess(partial["score"],60)
        self.assertGreater(closed["score"],partial["score"])

    def test_zero_missing_and_invalid_probability_remain_distinct(self):
        zero,missing=rank_tree(tree(0.0)),rank_tree(tree(None))
        self.assertEqual(zero["ranking_metrics"]["model_probability_geomean"],0)
        self.assertIsNone(missing["ranking_metrics"]["model_probability_geomean"])
        self.assertEqual(zero["ranking_metrics"]["model_probability_coverage"],1)
        self.assertEqual(missing["ranking_metrics"]["model_probability_coverage"],0)
        for invalid in [True,float('nan'),float('inf'),-0.1,1.1]:self.assertIsNone(probability(invalid))

    def test_hazards_and_stereo_are_penalties_without_safety_claim(self):
        a=priority([("CCO",False)],"CCO",1,1,[0.4])
        b=priority([("CI",False)],"CCO",1,1,[0.4])
        self.assertGreater(b["cost"]["known_hazards"],a["cost"]["known_hazards"])
        self.assertLess(b["score_penalty"],a["score_penalty"])
        self.assertEqual(rank_tree(tree(0.5,("CC(O)F",)))["cost"]["unspecified_leaf_stereo"],1)

    def test_every_candidate_ranked_before_top_k_and_ties_stable(self):
        rows=[dict(route_id=str(i).zfill(3),**rank_tree(tree((i+1)/60))) for i in range(50)]
        chosen=ranked_routes(rows)
        self.assertEqual(len(chosen),50)
        self.assertEqual(chosen[0]["route_id"],"049")
        self.assertEqual(ranked_routes(list(reversed(rows)))[:5],chosen[:5])
        ties=[dict(route_id=x,score=1.234) for x in ['b','a']]
        self.assertEqual([r['route_id'] for r in ranked_routes(ties)],['a','b'])

    def test_repeated_stock_leaves_never_manufacture_coverage(self):
        leaves=[("CCCCCCCC",False),("CC(=O)OC(C)=O",True)]
        short=priority(leaves,"CCCCCCCCCC",3,3,[0.1]*3)
        repeated=priority(leaves+[leaves[-1]]*3,"CCCCCCCCCC",5,5,[0.1]*5)
        self.assertEqual(short['score_components']['stock_coverage'],repeated['score_components']['stock_coverage'])
        self.assertEqual(short['score_components']['precursor_simplicity'],repeated['score_components']['precursor_simplicity'])
        self.assertGreater(short['score'],repeated['score'])
        self.assertEqual(repeated['ranking_metrics']['leaf_count'],5)
        self.assertEqual(repeated['ranking_metrics']['unique_leaf_count'],2)

    def test_tree_ranking_does_not_mutate_historical_payload(self):
        original=tree();before=copy.deepcopy(original);rank_tree(original)
        self.assertEqual(original,before)

    def test_multibranch_depth_and_all_step_probabilities(self):
        value=tree(0.8)
        value['children'][0]['children'][0]=tree(0.2,('C','C'))
        result=rank_tree(value)
        self.assertEqual(result['steps'],2)
        self.assertEqual(result['ranking_metrics']['max_depth'],2)
        self.assertEqual(result['ranking_metrics']['leaf_count'],3)
        self.assertAlmostEqual(result['ranking_metrics']['model_probability_geomean'],0.4)

    def test_real_mcts_backpropagation_uses_continuous_priority(self):
        config=Configuration();config.search.algorithm_config.update(max_nodes=100,research_reward=True)
        search=SearchTree(config,'CCO');root=search.root
        action=SmilesBasedRetroReaction(root.state.mols[0],reactants_str='CC.O',metadata={'policy_probability':0.2})
        root._fill_children_lists([action],[1.0])
        state=MctsState([TreeMolecule(root.state.mols[0],smiles=s) for s in ['CC','O']],config)
        with patch.object(root,'_filter_child_reaction',return_value=False):child=root._create_children_nodes([state],0)[0]
        reward=search.compute_reward(child)
        self.assertAlmostEqual(reward,rank_tree(tree(0.2))['score']/100)
        root._children_visitations[0]=1
        before=root._children_values[0]
        search.backpropagate(child)
        self.assertAlmostEqual(root._children_values[0]-before,reward)
        self.assertGreater(search.profiling['research_reward_evaluations'],0)

    def test_historical_envelope_keeps_bytes_and_original_score(self):
        from flavoretro.web import saved_run
        from flavoretro.resources import sha
        with tempfile.TemporaryDirectory() as directory:
            name='20261023T000000-'+'a'*32
            folder=Path(directory)/'outputs/runs'/name;folder.mkdir(parents=True)
            result={'run_id':name,'status':'ok','routes':[dict(route_id='historical',tree=tree(),score=5)]}
            path=folder/'result.json';path.write_text(json.dumps(result));before=path.read_bytes()
            (folder/'manifest.json').write_text(json.dumps({'run_id':name,'files':{'result.json':sha(path)}}))
            with patch('flavoretro.web.root',return_value=Path(directory)):
                saved=saved_run(name)
            self.assertEqual(saved['result'],result)
            self.assertEqual(path.read_bytes(),before)
            self.assertGreater(saved['research_ranking'][0]['score'],0)


if __name__=='__main__':unittest.main()
