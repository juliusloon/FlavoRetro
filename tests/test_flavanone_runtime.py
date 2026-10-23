"""Runtime contract/binding/filter/service checks. Never starts a search worker."""
import copy,importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from flavoretro.workspace import AssetError
from pydantic import ValidationError
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from flavoretro import contracts as contract
from flavoretro import flavanone_opening as ff
from flavoretro import runtime_extensions as extension
from flavoretro import service
from flavoretro.contracts import SearchRequest as OldRequest
class Contracts(unittest.TestCase):
 def test_default_payload_unchanged_and_explicit_native_optin(self):
  expected=dict(smiles='CCO',mode='balanced',engine='optimized',seed=0,candidate_stock=False,top_k=5,seconds=None,iterations=None,depth=None,branching=None,nodes=None)
  self.assertEqual(contract.SearchRequest(smiles='CCO').payload(),expected)
  self.assertEqual(contract.SearchRequest(smiles='CCO',engine='native').payload(),{**expected,'engine':'native'})
  r=contract.SearchRequest(smiles='CCO',engine='native',flavanone_opening=True)
  self.assertTrue(r.payload()['flavanone_opening']);self.assertFalse(r.candidate_stock)
  self.assertEqual(contract.SearchRequest.model_validate(r.payload()),r)
 def test_hybrid_or_silent_switch_is_rejected(self):
  for kw in [dict(flavanone_opening=True),dict(engine='native',flavanone_opening=True,glycoside_expansion=True),dict(engine='native',flavanone_opening='true')]:
   with self.assertRaises(ValidationError):contract.SearchRequest(smiles='CCO',**kw)
class BindingAndFilters(unittest.TestCase):
 def setUp(self):
  self.path=ROOT/'configs/flavanone-opening.json';self.settings=json.loads(self.path.read_text())
  self.config=patch('flavoretro.workspace.config',side_effect=lambda name:self.settings if name=='flavanone-opening.json' else (_ for _ in ()).throw(ValueError('unexpected config '+name)));self.config.start();self.addCleanup(self.config.stop)
  from flavoretro.workspace import config_path as original_config_path
  self.config_path=patch('flavoretro.workspace.config_path',side_effect=lambda name:self.path if name=='flavanone-opening.json' else original_config_path(name));self.config_path.start();self.addCleanup(self.config_path.stop)
 def test_binding_rejects_code_and_evidence_drift(self):
  good=ff.load_binding();self.assertEqual(ff.load_binding(good),good)
  with self.assertRaises(AssetError):ff.load_binding({**good,'prior':0.5})
  for k,v in [('prior',0.5),('policy_sha256','0'*64),('exact_target_registry',True),('independent_chemical_validation',True)]:
   saved=self.settings[k];self.settings[k]=v
   with self.assertRaises(AssetError):ff.load_binding()
   self.settings[k]=saved
 def test_config_preserves_native_models_stock_and_other_filters(self):
  effective=dict(expansion={'uspto':{'model':'same'},'ringbreaker':{'model':'same2'}},filter={'uspto_filter':{'type':'quick-filter','model':'samefilter','filter_cutoff':.05},'known_hazards':{'type':'samehazards'},'reviewed_evidence':{'type':'samereview'}},stock={'candidate':{'same':'stock'}},search={'algorithm':'mcts','algorithm_config':{'policy_weights':{'uspto':1,'ringbreaker':1}}})
  old=copy.deepcopy(effective);request=contract.SearchRequest(smiles='CCO',engine='native',flavanone_opening=True)
  out=extension.extend_configuration(effective,request,flavanone=ff.load_binding())
  for key in ['known_hazards','reviewed_evidence']:self.assertEqual(out['filter'][key],old['filter'][key])
  self.assertEqual(out['stock'],old['stock']);self.assertEqual(out['search']['algorithm'],'mcts');self.assertEqual(out['search']['algorithm_config'],old['search']['algorithm_config'])
  self.assertEqual(out['expansion']['uspto'],old['expansion']['uspto']);self.assertEqual(out['expansion']['ringbreaker'],old['expansion']['ringbreaker']);self.assertEqual(out['filter']['uspto_filter']['model'],'samefilter')
  self.assertEqual(out['expansion']['flavanone_opening']['type'],'flavoretro.flavanone_opening.FlavanoneOpening')
  with self.assertRaises(AssetError):extension.extend_configuration(copy.deepcopy(old),OldRequest(smiles='CCO'),flavanone=ff.load_binding())
 def test_model_filter_bypass_only_for_verified_added_rule(self):
  with patch.object(QuickKerasFilter,'__init__',return_value=None) as init,patch.object(QuickKerasFilter,'apply',return_value='generic_model') as generic:
   strategy=ff.GraphRuleQuickFilter('uspto_filter',NS(),model='samefilter',scope_binding=ff.load_binding())
   self.assertNotIn('scope_binding',init.call_args.kwargs)
   self.assertEqual(strategy.apply(NS(metadata={'policy_name':'uspto'})),'generic_model');generic.assert_called_once()
   product='O=C1CC(c2ccccc2)Oc2ccccc21';precursor=ff.precursors(product)[0]
   reaction=NS(metadata=dict(policy_name='flavanone_opening',template_id=ff.RULE_ID),mol=NS(smiles=product),reactants=[[NS(smiles=precursor)]],index=0)
   strategy.apply(reaction);self.assertEqual(generic.call_count,1);ev=reaction.metadata['task022_scope_hypothesis']
   self.assertFalse(ev['exact_source_instance_match']);self.assertFalse(ev['independent_chemical_validation'])
   bad=NS(metadata=dict(policy_name='flavanone_opening',template_id=ff.RULE_ID),mol=NS(smiles=product),reactants=[[NS(smiles='CCO')]],index=0)
   from aizynthfinder.utils.exceptions import RejectionException
   with self.assertRaises(RejectionException):strategy.apply(bad)
 def test_service_persists_same_binding_with_mock_worker(self):
  request=contract.SearchRequest(smiles='CCO',engine='native',flavanone_opening=True,seconds=1.0,iterations=1)
  captured=[]
  def worker(argv,**kw):
   env=json.loads(kw['input']);captured.append(env)
   Path(env['output']).write_text(json.dumps(dict(status='ok',run_id=env['run_id'],request=env['request'],execution_source='test_fixture_not_real_mcts',routes=[],flavanone_binding=env['flavanone_binding'])))
   return NS(returncode=0)
  with tempfile.TemporaryDirectory() as temp,patch.object(service,'workspace_root',return_value=Path(temp)),patch.object(service,'load_review',return_value=NS(binding={'fixture':True})),patch('flavoretro.task016_runs.append_run',return_value=False),patch.object(service.subprocess,'run',side_effect=worker):
   result=service.search(request);folder=Path(temp)/'outputs/runs'/result['run_id'];manifest=json.loads((folder/'manifest.json').read_text());binding=json.loads((folder/'flavanone-binding.json').read_text())
   self.assertEqual(manifest['flavanone_binding'],binding);self.assertEqual(binding,captured[0]['flavanone_binding']);self.assertEqual(result['flavanone_binding'],binding);self.assertTrue(captured[0]['request']['flavanone_opening']);self.assertEqual(len(captured),1)
class ActualRegisteredAssets(unittest.TestCase):
 def test_actual_config_registry_and_code_binding_load_without_mocks(self):
  binding=ff.load_binding()
  self.assertEqual(binding['rule_id'],'FF-OPEN-E-v1')
  self.assertEqual(binding['prior'],0.25)
  self.assertFalse(binding['exact_target_registry'])
  self.assertFalse(binding['independent_chemical_validation'])
  self.assertEqual(ff.load_binding(binding),binding)

if __name__=='__main__':unittest.main(verbosity=2)
