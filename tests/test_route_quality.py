import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from rdkit import Chem
from flavoretro.route_quality import acetate_skeleton,protection_only,diagnostics,diverse_top,material_subgoal,source_supported
from flavoretro.ranking import rank_tree,priority
from flavoretro.contracts import SearchRequest
from flavoretro.research_evaluation import validate
from flavoretro.workspace import AssetError
from flavoretro.resources import sha


def mol(s,children=None,stock=False):return {'type':'mol','smiles':s,'in_stock':stock,**({'children':children} if children else {})}
def reaction(children,source=False):return {'type':'reaction','metadata':{'policy_probability':None,'task022_evidence':{'source_reconstruction':source,'exact_source_instance_match':source}},'children':children}


class RouteQuality(unittest.TestCase):
    def test_acetate_strip_retains_phenol_and_never_strips_ether(self):
        self.assertEqual(acetate_skeleton('CC(=O)Oc1ccccc1'),('Oc1ccccc1',1))
        self.assertEqual(acetate_skeleton('COc1ccccc1')[1],0)
        self.assertEqual(acetate_skeleton('CC(=O)OC(C)=O')[1],0)
        self.assertNotEqual(acetate_skeleton('COc1ccccc1')[0],'Oc1ccccc1')
    def test_acetyl_order_is_one_structural_family(self):
        direct=mol('Oc1ccccc1',[reaction([mol('c1ccccc1'),mol('O')])])
        protected=mol('Oc1ccccc1',[reaction([mol('CC(=O)Oc1ccccc1',[reaction([mol('c1ccccc1'),mol('O')])])])])
        a,b=diagnostics(direct),diagnostics(protected)
        self.assertEqual(a['family_id'],b['family_id'])
        self.assertEqual(b['protection_only_steps'],1)
        self.assertGreater(rank_tree(direct)['score'],rank_tree(protected)['score'])
        self.assertFalse(protection_only('COc1ccccc1',['Oc1ccccc1']))
    def test_supported_source_adds_separate_evidence_without_filling_probability(self):
        unknown=mol('CCO',[reaction([mol('CC'),mol('O')])]);source=copy.deepcopy(unknown);source['children'][0]['metadata']['task022_evidence']={'source_reconstruction':True,'exact_source_instance_match':True}
        a,b=rank_tree(unknown),rank_tree(source)
        self.assertGreater(b['score'],a['score'])
        self.assertIsNone(b['ranking_metrics']['model_probability_geomean'])
        self.assertEqual(b['score_components']['source_support'],1)
    def test_longer_same_leaf_route_scores_worse_even_with_more_known_steps(self):
        leaves=[('CCO',True),('CCCCCC',False)]
        a=priority(leaves,'CCCCCCCC',2,2,[0.2]*2)
        b=priority(leaves,'CCCCCCCC',4,4,[0.2]*4,protection_steps=2)
        self.assertGreater(a['score'],b['score'])
    def test_exact_ancestor_cycle_is_flagged(self):
        tree=mol('CCO',[reaction([mol('CC',[reaction([mol('CCO')])])])])
        self.assertEqual(diagnostics(tree)['exact_ancestor_revisits'],1)
    def test_diverse_selection_preserves_score_order_and_all_candidates(self):
        rows=[{'route_id':'a','score':10,'route_quality':{'family_id':'same'}},{'route_id':'b','score':9,'route_quality':{'family_id':'same'}},{'route_id':'c','score':8,'route_quality':{'family_id':'different'}}]
        before=copy.deepcopy(rows);chosen=diverse_top(rows,2)
        self.assertEqual([r['route_id'] for r in chosen],['a','c']);self.assertEqual(rows,before)
        self.assertEqual(len(diverse_top(rows,3)),3)
    def test_donor_subgoal_retains_activation_and_supply_gap(self):
        self.assertEqual(material_subgoal('OP(=O)(O)OP(=O)(O)O')['kind'],'activated_nucleotide_sugar')
        self.assertEqual(material_subgoal('CCO')['current_supply'],'unverified')
    def test_udp_heteroatom_flags_do_not_become_missing_carbon_stereo(self):
        donor='C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)[C@H](O)[C@@H]2O)[C@H](O)[C@H](O)[C@H]1O'
        result=priority([(donor,False)],donor,1,1,[0.1])
        self.assertEqual(result['cost']['unspecified_leaf_carbon_stereo'],0)
        self.assertEqual(result['cost']['unassigned_hetero_stereo_flags'],2)
        self.assertEqual(result['cost']['unspecified_leaf_stereo'],2)
        self.assertEqual(result['score_penalty'],1)
        carbon=priority([('CC(O)F',False)],'CC(O)F',1,1,[0.1])
        self.assertEqual(carbon['cost']['unspecified_leaf_carbon_stereo'],1)
        self.assertLess(carbon['score_penalty'],1)

    def test_no_source_upgrade_from_support_flag_alone(self):
        self.assertFalse(source_supported({'task022_evidence':{'source_reconstruction':True}}))
    def test_internal_created_prefix_is_preserved_with_frontier(self):
        from types import SimpleNamespace as NS
        from flavoretro.worker import extraction_nodes
        root=NS(state=NS(is_solved=False),children=[1])
        internal=NS(state=NS(is_solved=False),children=[2])
        leaf=NS(state=NS(is_solved=False),children=[])
        nodes,frontier=extraction_nodes(NS(root=root,graph=lambda:[root,internal,leaf]))
        self.assertEqual(nodes,[internal,leaf]);self.assertEqual(frontier,[leaf])

    def test_ordinary_request_cannot_select_private_ablation(self):
        with self.assertRaises(ValueError):SearchRequest(smiles='CCO',research_evaluation={'arm':'A'})
    def test_frozen_binding_checks_request_and_source_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);base=root/'outputs/task027';base.mkdir(parents=True)
            asset=root/'asset';asset.write_text('fixed');request=SearchRequest(smiles='CCO')
            protocol={'kind':'task027_frozen_ablation_v1','approval':'agent_delegated','human_reviewed':False,'assets':{'asset':sha(asset)},'cells':[{'cell_id':'one','arm':'A','request':request.payload()}]}
            path=base/'protocol.json';path.write_text(json.dumps(protocol));binding={'protocol':'outputs/task027/protocol.json','protocol_sha256':sha(path),'cell_id':'one','arm':'A'}
            with patch('flavoretro.research_evaluation.root',return_value=root):
                self.assertEqual(validate(binding,request)['arm'],'A')
                with self.assertRaises(AssetError):validate({**binding,'arm':'C'},request)
                asset.write_text('changed')
                with self.assertRaises(AssetError):validate(binding,request)


class SourceAdmission(unittest.TestCase):
    def test_local_exact_registry_has_three_new_actions_and_originals(self):
        from flavoretro.runtime_extensions import literature_registry
        registry=literature_registry();new=[r for r in registry.records if r['reaction_id'].startswith('T027:')]
        self.assertEqual(len(new),3)
        for r in new:self.assertFalse(r['scope_transfer_evidence']);self.assertIsNone(r['yield_value'])
        rutin=next(row for row in new if row['reaction_id'].startswith('T027:rutin:'))
        self.assertEqual(rutin['source']['evidence_scope'],'primary_abstract');self.assertIsNone(rutin['conditions'])
    def test_source_panel_and_inventory_are_distinct(self):
        panel=json.loads(Path('outputs/task027/panel.json').read_text());admission=json.loads(Path('outputs/task027/p1-admission.json').read_text())
        self.assertEqual(len(panel),3);self.assertEqual(admission['inventory_admissions'],0)
        self.assertTrue(all(not row['independent_panel'] for row in panel))
    def test_named_transfer_conserves_elements_with_UDP_byproduct(self):
        from collections import Counter
        from flavoretro.runtime_extensions import literature_registry
        def elements(smiles):
            mol=Chem.AddHs(Chem.MolFromSmiles(smiles));return Counter(atom.GetSymbol() for atom in mol.GetAtoms())
        udp=Counter({'C':9,'H':14,'N':2,'O':12,'P':2})
        for row in literature_registry().records:
            if not row['reaction_id'].startswith('T027:'):continue
            reactants=Counter()
            for r in row['reactants']:reactants.update(elements(r['smiles']))
            products=elements(row['products'][0]['smiles']);products.update(udp)
            self.assertEqual(reactants,products)

if __name__=='__main__':unittest.main()
