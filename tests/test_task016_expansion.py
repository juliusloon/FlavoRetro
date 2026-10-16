"""Synthetic contracts only; these fixtures are not chemical validation."""
import copy,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch,Mock
from rdkit import Chem
from aizynthfinder.context.config import Configuration
from aizynthfinder.chem import TreeMolecule,TemplatedRetroReaction
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException
from flavoretro.glycoside_expansion import extract_template,apply_template,Registry,DomainAwareQuickFilter
from flavoretro.reviewed_resources import canonical_side,reaction_signature
from flavoretro.contracts import SearchRequest
from flavoretro.workspace import AssetError
from flavoretro.search import SearchTree


class DomainContracts(unittest.TestCase):
    def setUp(self):
        self.instance=dict(instance_id='synthetic-only',acceptor='Oc1ccccc1',donor='OP(=O)(O)O[C@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O',target='c1ccc(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)cc1',provenance={'scope':'synthetic test only'})
        self.instance['reference_precursors']=[self.instance['acceptor'],self.instance['donor']]
        self.instance['reference_signature']=reaction_signature(self.instance['reference_precursors'],[self.instance['target']])
        self.instance['strict_source_signature']=reaction_signature(self.instance['reference_precursors'],[self.instance['target'],'[H+]'])
        self.template=dict(template_id='synthetic-template',support_instances=['synthetic-only'],allowed_targets=[canonical_side([self.instance['target']])],required_context={'enzyme':'synthetic-only'},**extract_template(self.instance))
        self.registry=object.__new__(Registry);self.registry.by_id={'synthetic-template':self.template};self.registry.instances={'synthetic-only':self.instance};self.registry.binding={'version':'synthetic'}

    def reaction(self):
        return TemplatedRetroReaction(TreeMolecule(smiles=self.instance['target'],parent=None),smarts=self.template['smarts'],use_rdchiral=False,metadata={'template_id':'synthetic-template','policy_name':'glycoside','domain_binding':self.registry.binding,'required_context':self.template['required_context']})

    def test_full_donor_and_stereo_reconstruction(self):
        outcomes=apply_template(self.template,self.instance['target'])
        self.assertIn(canonical_side(self.instance['reference_precursors']),[o['precursors'] for o in outcomes])
        self.assertIn('P',outcomes[0]['precursors'])
        self.assertEqual(self.template['mapping']['transferred_atoms'],11)

    def test_sugar_epimer_rejected_by_declared_boundary(self):
        mol=Chem.MolFromSmiles(self.instance['target']);mol.GetAtomWithIdx(self.template['center']['anomeric_candidate']).InvertChirality()
        self.assertEqual(apply_template(self.template,Chem.MolToSmiles(mol,isomericSmiles=True)),[])

    def test_wrong_enzyme_context_rejected(self):
        self.assertEqual(apply_template(self.template,self.instance['target'],{'enzyme':'different'}),[])

    def test_source_support_does_not_verify_conditions_or_full_equation(self):
        evidence=self.registry.evidence(self.reaction())
        self.assertTrue(evidence['template_source_support']);self.assertTrue(evidence['exact_instance_match'])
        self.assertFalse(evidence['full_rhea_equation_match']);self.assertFalse(evidence['prediction_conditions_verified'])
        self.assertIsNone(evidence['yield_value']);self.assertFalse(evidence['actionable'])

    def test_forged_binding_and_smarts_are_rejected(self):
        for field,value in [('domain_binding',{'version':'wrong'}),('required_context',{'enzyme':'wrong'})]:
            reaction=self.reaction();reaction.metadata[field]=value
            with self.assertRaises(RejectionException):self.registry.evidence(reaction)
        reaction=self.reaction();reaction.smarts='[C:1]>>[C:1]'
        with self.assertRaises(RejectionException):self.registry.evidence(reaction)

    def test_precursor_edit_cannot_claim_source_match(self):
        reaction=self.reaction();reaction._reactants=((TreeMolecule(parent=reaction.mol,smiles='O'),),)
        with self.assertRaises(RejectionException):self.registry.evidence(reaction)

    def test_generic_filter_keeps_original_model_path(self):
        policy=object.__new__(DomainAwareQuickFilter);policy.registry=Mock()
        reaction=NS(metadata={'policy_name':'uspto','template_id':'synthetic-template'})
        with patch.object(QuickKerasFilter,'apply') as original:
            policy.apply(reaction);original.assert_called_once_with(reaction)
        policy.registry.evidence.assert_not_called()

    def test_missing_or_tampered_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'manifest.json'
            with self.assertRaises(AssetError):Registry(path,'0'*64)
            path.write_text('{}')
            with self.assertRaises(AssetError):Registry(path,'0'*64)

    def test_option_off_preserves_old_request_shape(self):
        request=SearchRequest(smiles='CCO');self.assertFalse(request.glycoside_expansion)
        self.assertNotIn('glycoside_expansion',request.payload())
        self.assertTrue(SearchRequest(smiles='CCO',glycoside_expansion=True).payload()['glycoside_expansion'])

    def test_created_trace_credits_only_surviving_original_outcome(self):
        config=Configuration();config.search.algorithm_config.update(max_nodes=5,max_branching=2,trace_actions=True)
        tree=SearchTree(config,'CCO');node=tree.root
        action=NS(mol=NS(inchi_key='root',smiles='CCO'),metadata={'template':'synthetic','policy_name':'test'},smarts='synthetic',index=0,reactants=((NS(smiles='C'),),(NS(smiles='CO'),)))
        action.copy=lambda index:NS(**{**vars(action),'index':index})
        states=[NS(mols=[NS(inchi_key='pruned')],max_transforms=1),NS(mols=[NS(inchi_key='surviving')],max_transforms=1)]
        tree.depths[('pruned',)]=0;node._fill_children_lists([action],[1.0])
        with patch('aizynthfinder.search.mcts.node.MctsNode._create_children_nodes',side_effect=lambda values,index:[NS(state=s) for s in values]):node._create_children_nodes(states,0)
        events=[e for e in tree.action_trace if e['stage']=='mcts_action_created']
        self.assertEqual([e['outcome_index'] for e in events],[1])
        self.assertEqual(events[0]['signature'],reaction_signature(['CO'],['CCO']))


if __name__=='__main__':unittest.main()
