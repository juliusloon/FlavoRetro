import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from rdkit import Chem
from flavoretro.contracts import SearchRequest
from flavoretro.open_glycoside_library import normalize_species,structural_formation
from flavoretro.glycoside_library import neutral_mol
from flavoretro.task016_runs import append_run

class LibraryContracts(unittest.TestCase):
    def test_legacy_request_shape(self):
        r=SearchRequest(smiles='CCO');self.assertNotIn('glycoside_library_version',r.payload());self.assertNotIn('glycoside_expansion',r.payload())
        self.assertNotIn('glycoside_library_version',SearchRequest(smiles='CCO',glycoside_expansion=True).payload())
    def test_v2_requires_explicit_optimized_opt_in(self):
        for args in [dict(glycoside_library_version='v2'),dict(glycoside_library_version='v2',glycoside_expansion=True,engine='native')]:
            with self.assertRaises(ValueError):SearchRequest(smiles='CCO',**args)
        self.assertEqual(SearchRequest(smiles='CCO',glycoside_expansion=True,glycoside_library_version='v2').payload()['glycoside_library_version'],'v2')
    def test_normalization_keeps_isotope_salt_and_other_charge(self):
        s='[13CH3]Oc1ccc([O-])cc1.[Na+].C[N+](C)(C)C';r=normalize_species(s)
        self.assertEqual(len(r['changes']),1);self.assertIn('[13CH3]',r['normalized']);self.assertIn('[Na+]',r['normalized']);self.assertIn('[N+]',r['normalized']);self.assertNotEqual(r['original'],r['normalized']);self.assertGreater(len(r['original']),1)
    def test_normalization_does_not_change_alkoxide(self):
        r=normalize_species('CC[O-]');self.assertEqual(r['normalized'],'CC[O-]');self.assertEqual(r['changes'],[])
    def test_mapped_normalization_preserves_atom_order(self):
        m=Chem.MolFromSmiles('[O-:19][c:20]1[cH:21][cH:22][cH:23][cH:24][cH:25]1');n=neutral_mol(m)
        self.assertEqual([a.GetAtomMapNum() for a in m.GetAtoms()],[a.GetAtomMapNum() for a in n.GetAtoms()]);self.assertEqual(n.GetAtomWithIdx(0).GetFormalCharge(),0)
    def test_nonanomeric_donor_stereo_is_required(self):
        a='Oc1ccccc1';g='OC[C@H]1O[C@@H](Oc2ccccc2)[C@H](O)[C@@H](O)[C@@H]1O';donor='OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@@H]1O'
        self.assertEqual(structural_formation(a,donor,g)['family'],'O_formation')
        m=Chem.MolFromSmiles(donor);centers=Chem.FindMolChiralCenters(m,includeUnassigned=False);m.GetAtomWithIdx(centers[-1][0]).InvertChirality()
        with self.assertRaises(ValueError):structural_formation(a,Chem.MolToSmiles(m,isomericSmiles=True),g)
    def test_components_are_not_silently_removed(self):
        with self.assertRaises(ValueError):structural_formation('Oc1ccccc1.[Na+]','C','COc1ccccc1')
    def test_remote_EZ_survives_partial_template_on_mapped_parent(self):
        from aizynthfinder.chem import TreeMolecule
        from rdkit.Chem import rdChemReactions
        from flavoretro.glycoside_library import restore_conserved_double_bond_stereo
        parent=TreeMolecule(parent=None,smiles='Oc1ccc(/C=C/c2ccccc2)cc1');mol=neutral_mol(parent.mapped_mol)
        rxn=rdChemReactions.ReactionFromSmarts('[c:1][OH:2]>>[c:1][OH:2]');products=rxn.RunReactants([mol])[0]
        for p in products:Chem.SanitizeMol(p)
        restore_conserved_double_bond_stereo(products,mol)
        from flavoretro.reviewed_resources import canonical_side
        self.assertEqual(canonical_side([Chem.MolToSmiles(products[0],isomericSmiles=True)]),canonical_side([parent.smiles]))

    def test_scope_rejects_oxygen_chain_beyond_declared_OH_OMe(self):
        from scripts.task016_p1_encode import named_flavone,attach_stub,position_oxygen
        from flavoretro.glycoside_library import scope_center_allowed,FLAVONE
        donor='OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@@H]1O'
        stub='*[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O'
        parent=named_flavone([5,7,104],[8]);target=attach_stub(parent,stub,position_oxygen(parent,7))
        template=dict(donor=donor,category='O_formation',scope=dict(center_class='phenolic_aryl_O',acceptor_cores=[FLAVONE]))
        self.assertTrue(scope_center_allowed(template,Chem.MolFromSmiles(target),[Chem.MolFromSmiles(parent),Chem.MolFromSmiles(donor)]))
        bad=Chem.RWMol(Chem.MolFromSmiles(parent));site=position_oxygen(parent,5);o=bad.AddAtom(Chem.Atom('O'));bad.AddBond(site,o,Chem.BondType.SINGLE);Chem.SanitizeMol(bad);acceptor=Chem.MolToSmiles(bad,isomericSmiles=True);product=attach_stub(acceptor,stub,position_oxygen(acceptor,7))
        self.assertFalse(scope_center_allowed(template,Chem.MolFromSmiles(product),[Chem.MolFromSmiles(acceptor),Chem.MolFromSmiles(donor)]))

    def test_old_ledger_ceiling_cannot_be_raised_by_environment(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/'outputs/task016/test.jsonl';p.parent.mkdir(parents=True);p.write_text(''.join(json.dumps(dict(run_id=str(i),phase='started'))+'\n' for i in range(120)))
            with patch('flavoretro.task016_runs.root',return_value=root),patch.dict(os.environ,{'FLAVORETRO_TASK016_LEDGER':str(p),'FLAVORETRO_TASK016_MAX_RUNS':'999'}):
                with self.assertRaises(ValueError):append_run('new','started')
    def test_p1_budget_revision_requires_exact_approved_hash(self):
        from flavoretro.resources import sha
        with tempfile.TemporaryDirectory() as t:
            workspace=Path(t);p=workspace/'outputs/task016-p1/v1/run_ledger.jsonl';p.parent.mkdir(parents=True)
            baseline=p.with_name('execution-baseline.json');baseline.write_text(json.dumps(dict(task='TASK-016-P1',approval_type='agent_delegated',limits=dict(service_attempts=180))))
            revised=workspace/'outputs/task016-p1/v2/budget_revision.json';revised.parent.mkdir();revised.write_text('{}')
            with patch('flavoretro.task016_runs.root',return_value=workspace),patch.dict(os.environ,{'FLAVORETRO_TASK016_LEDGER':str(p)}):
                with self.assertRaisesRegex(ValueError,'revision hash drift'):append_run('new','started')
            self.assertFalse(p.exists())

    def test_p1_new_revision_preserves_original_ledger_binding_and_ceiling(self):
        from flavoretro.resources import sha
        with tempfile.TemporaryDirectory() as t:
            workspace=Path(t);p=workspace/'outputs/task016-p1/v1/run_ledger.jsonl';p.parent.mkdir(parents=True)
            baseline=p.with_name('execution-baseline.json');baseline.write_text(json.dumps(dict(task='TASK-016-P1',approval_type='agent_delegated',limits=dict(service_attempts=180))))
            binding=sha(baseline);p.write_text(''.join(json.dumps(dict(run_id=str(i),phase='started',budget_binding=binding,ceiling=180))+'\n' for i in range(180)))
            revised=workspace/'outputs/task016-p1/v2/budget_revision.json';revised.parent.mkdir();revised.write_text(json.dumps(dict(task='TASK-016-P1',approval_type='agent_delegated',original_baseline_sha256=binding,approved_limits=dict(service_attempts=240))))
            with patch('flavoretro.task016_runs.root',return_value=workspace),patch('flavoretro.task016_runs.P1_BUDGET_REVISION_SHA256',sha(revised)),patch.dict(os.environ,{'FLAVORETRO_TASK016_LEDGER':str(p)}):
                self.assertTrue(append_run('new','started'))
                last=json.loads(p.read_text().splitlines()[-1]);self.assertEqual(last['budget_binding'],binding);self.assertEqual(last['ceiling'],240);self.assertEqual(last['budget_revision_sha256'],sha(revised))
                with self.assertRaises(ValueError):append_run('new','started')

    def test_generic_protection_uses_accepted_distinct_precursors(self):
        from types import SimpleNamespace
        from flavoretro.search import Node
        from aizynthfinder.search.mcts.node import MctsNode
        class Action:
            def __init__(self,key,smiles,policy,rejected=False):self.metadata=dict(policy_name=policy,template=key);self.smarts=key;self.mol=SimpleNamespace(inchi_key='target',smiles='CC');self.reactants=[tuple(SimpleNamespace(smiles=x) for x in smiles)];self.rejected=rejected
            def copy(self,index=0):return self
        actions=[Action('bad',['O'],'uspto',True),Action('g1',['CCO'],'uspto'),Action('duplicate',['CCO'],'ringbreaker'),Action('g2',['CCN'],'uspto'),Action('g3',['CCC'],'ringbreaker'),Action('domain',['CCCl'],'glycoside')]
        node=Node.__new__(Node);node._config=SimpleNamespace(search=SimpleNamespace(algorithm_config=dict(max_branching=6,protect_generic_actions=3,use_prior=True,policy_weights={})));node.tree=SimpleNamespace(profiling=dict(actions_seen=0,duplicate_actions=0))
        with patch.object(MctsNode,'_filter_child_reaction',lambda _,action:action.rejected):node._fill_children_lists(actions,[.19,.18,.17,.16,.15,.9])
        keys=[a.smarts for a in node._children_actions];self.assertEqual(keys[:3],['g1','g2','g3']);self.assertEqual(len(keys),6)
if __name__=='__main__':unittest.main()
