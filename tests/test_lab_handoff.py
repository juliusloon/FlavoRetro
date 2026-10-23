import copy
import unittest
from flavoretro.worker import merge_source_variants
from flavoretro.lab_handoff import packet


def tree(source=None):
    evidence={'source_reaction_id':source,'lab_case':{'source_id':source}} if source else {}
    return {'type':'mol','smiles':'CO','children':[{'type':'reaction','smiles':'X','metadata':{'task022_evidence':evidence},'children':[{'type':'mol','smiles':'C'}]}]}

class SourceWitnessTests(unittest.TestCase):
    def test_graph_dedup_retains_each_actual_generated_source(self):
        previous={'source_variants':merge_source_variants(None,{'tree':tree('Pei')})}
        variants=merge_source_variants(previous,{'tree':tree('Other')})
        self.assertEqual([v['source_reaction_ids'] for v in variants],[['Pei'],['Other']])
        # Repeated actual witnesses are deduplicated; a model-only route adds no source.
        self.assertEqual(len(merge_source_variants({'source_variants':variants},{'tree':tree('Other')})),2)
        self.assertEqual(merge_source_variants(None,{'tree':tree()}),[])

    def test_source_witness_is_snapshot_of_generated_tree(self):
        original=tree('Pei');variants=merge_source_variants(None,{'tree':original})
        original['smiles']='changed'
        self.assertEqual(variants[0]['tree']['smiles'],'CO')

    def test_unverified_or_cached_run_cannot_export_handoff(self):
        for envelope in [{'result':{},'integrity':'unknown'},{'result':{'execution_source':'cached'},'integrity':'verified'}]:
            with self.assertRaisesRegex(ValueError,'verified_live_mcts'):
                packet(envelope,'a','Pei2019')

    def test_source_cannot_be_invented_from_a_matching_graph(self):
        result={'execution_source':'live_aizynthfinder_mcts','routes':[{'route_id':'a','tree':tree()}]}
        with self.assertRaisesRegex(ValueError,'no_generated_source_witness'):
            packet({'integrity':'verified','result':result},'a','Pei2019')
