import copy, os, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from pydantic import ValidationError
from aizynthfinder.utils.exceptions import RejectionException
from flavoretro.contracts import SearchRequest
from flavoretro.runtime_extensions import stock_binding, extend_configuration, SourceAndDomainFilter
from flavoretro.resources import sha
from flavoretro.workspace import AssetError

class RuntimeOptionContracts(unittest.TestCase):
    def test_defaults_preserve_old_payload(self):
        r=SearchRequest(smiles='CCO')
        self.assertFalse(r.literature_expansion)
        self.assertEqual(r.stock_profile,'reviewed')
        self.assertNotIn('literature_expansion',r.payload())
        self.assertNotIn('stock_profile',r.payload())

    def test_explicit_opt_in_and_engine_required(self):
        for kw in [dict(stock_profile='zinc'),dict(stock_profile='../stock',candidate_stock=True),dict(literature_expansion=True,engine='native'),dict(glycoside_library_version='v8')]:
            with self.assertRaises(ValidationError):SearchRequest(smiles='CCO',**kw)
        r=SearchRequest(smiles='CCO',glycoside_expansion=True,glycoside_library_version='v8',literature_expansion=True,candidate_stock=True,stock_profile='zinc')
        self.assertEqual(SearchRequest.model_validate(r.payload()),r)

    def test_stock_bytes_and_binding_checked(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ,FLAVORETRO_WORKSPACE=d):
            p=Path(d)/'stock';p.write_bytes(b'fixture only')
            config={'stock':{'zinc':{'path':'stock','sha256':sha(p),'current_supplier_verified':False}}}
            with patch('flavoretro.runtime_extensions.config',return_value=config):
                b=stock_binding('zinc')
                self.assertEqual(stock_binding('zinc',b),b)
                with self.assertRaises(AssetError):stock_binding('zinc',{**b,'sha256':'0'*64})
                p.write_bytes(b'changed')
                with self.assertRaises(AssetError):stock_binding('zinc')

    def test_stock_cannot_escape_workspace(self):
        with patch('flavoretro.runtime_extensions.config',return_value={'stock':{'zinc':{'path':'../external','sha256':'0'*64,'current_supplier_verified':False}}}):
            with self.assertRaises(AssetError):stock_binding('zinc')

    def test_domain_source_and_generic_filters_remain_separate(self):
        policy=object.__new__(SourceAndDomainFilter)
        policy.literature=NS(evidence=lambda r: {'source':True})
        policy.domain=NS(evidence=lambda r: {'namespace':'v8','domain':True})
        for name,key in [('literature','task022_evidence'),('glycoside','task016_evidence')]:
            r=NS(metadata={'policy_name':name})
            with patch('flavoretro.runtime_extensions.QuickKerasFilter.apply') as generic:
                policy.apply(r);generic.assert_not_called();self.assertIn(key,r.metadata)
        with patch('flavoretro.runtime_extensions.QuickKerasFilter.apply') as generic:
            r=NS(metadata={'policy_name':'uspto'});policy.apply(r);generic.assert_called_once_with(r)
        def reject(r):raise RejectionException('source mismatch')
        policy.literature=NS(evidence=reject)
        with self.assertRaises(RejectionException):policy.apply(NS(metadata={'policy_name':'literature'}))

    def test_extension_preserves_hazard_filters_and_domain_weight(self):
        effective={'search':{'algorithm_config':{'policy_weights':{'uspto':1,'glycoside':1}}},'expansion':{'glycoside':{}},'filter':{'known_hazards':{'type':'unchanged'},'uspto_filter':{'model':'unchanged'}}}
        r=SearchRequest(smiles='CCO',literature_expansion=True)
        result=extend_configuration(copy.deepcopy(effective),r,{'test':'binding'},domain={'test':'domain'})
        self.assertEqual(result['filter']['known_hazards'],effective['filter']['known_hazards'])
        self.assertEqual(result['search']['algorithm_config']['policy_weights'],{'uspto':1,'glycoside':1,'literature':1})
        self.assertTrue(result['search']['exclude_target_from_stock'])

if __name__=='__main__':unittest.main()
