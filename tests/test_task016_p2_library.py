import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from flavoretro.contracts import SearchRequest
from flavoretro.task016_runs import append_run
from flavoretro.workspace import root,AssetError,config
class V3Contracts(unittest.TestCase):
    def test_explicit_v3_requires_domain_optimized(self):
        with self.assertRaises(ValueError):SearchRequest(smiles='CCO',glycoside_library_version='v3')
        with self.assertRaises(ValueError):SearchRequest(smiles='CCO',engine='native',glycoside_expansion=True,glycoside_library_version='v3')
        self.assertEqual(SearchRequest(smiles='CCO',glycoside_expansion=True,glycoside_library_version='v3').payload()['glycoside_library_version'],'v3')
        self.assertNotIn('glycoside_library_version',SearchRequest(smiles='CCO').payload())
    def test_v3_packaged_missing_assets_fail_closed(self):
        from flavoretro.glycoside_library_v3 import load_registry
        with tempfile.TemporaryDirectory() as t,patch.dict(os.environ,{'FLAVORETRO_WORKSPACE':t}):
            self.assertFalse(config('glycoside-library-v3.json')['default_enabled'])
            with self.assertRaises(AssetError):load_registry()
    def test_v3_manifest_drift_rejected(self):
        from flavoretro.glycoside_library_v3 import Registry
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'manifest.json';p.write_text('{}')
            with self.assertRaises(AssetError):Registry(p,'0'*64)
    def test_p2_approval_hash_required(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'outputs/task016-p2/v1/run_ledger.jsonl';p.parent.mkdir(parents=True);p.with_name('execution-baseline.json').write_text('{}')
            with patch('flavoretro.task016_runs.root',return_value=Path(t)),patch.dict(os.environ,{'FLAVORETRO_TASK016_LEDGER':str(p),'FLAVORETRO_TASK016_PURPOSE':'task016_p2_engineering'}):
                with self.assertRaisesRegex(ValueError,'approval hash'):append_run('x','started')
            self.assertFalse(p.exists())
    def test_p2_engineering_quota_cannot_use_validation_capacity(self):
        from flavoretro.resources import sha
        with tempfile.TemporaryDirectory() as t:
            base=Path(t);p=base/'outputs/task016-p2/v1/run_ledger.jsonl';p.parent.mkdir(parents=True);b=p.with_name('execution-baseline.json')
            b.write_text(json.dumps(dict(task='TASK-016-P2',approval_type='human_direct',budgets=dict(total_search_attempts=240,validation_search_attempts=213,engineering_search_attempts=27))))
            binding=sha(b);p.write_text(''.join(json.dumps(dict(run_id=str(i),phase='started',budget_binding=binding,purpose='task016_p2_engineering'))+'\n' for i in range(27)))
            with patch('flavoretro.task016_runs.root',return_value=base),patch('flavoretro.task016_runs.P2_BASELINE_SHA256',binding),patch.dict(os.environ,{'FLAVORETRO_TASK016_LEDGER':str(p),'FLAVORETRO_TASK016_PURPOSE':'task016_p2_engineering','FLAVORETRO_TASK016_MAX_RUNS':'999'}):
                with self.assertRaisesRegex(ValueError,'27-attempt'):append_run('new','started')
                os.environ['FLAVORETRO_TASK016_PURPOSE']='task016_p2_validation';self.assertTrue(append_run('new','started'))
                with self.assertRaises(ValueError):append_run('new','started')
                self.assertTrue(append_run('new','finished'))
                with self.assertRaises(ValueError):append_run('unreserved','finished')
    def test_v3_local_source_scope_contracts(self):
        if not (root()/'outputs/task016-p2/v2/template_source_manifest.json').is_file():self.skipTest('local P2 source assets intentionally absent')
        from flavoretro.glycoside_library_v3 import load_registry
        from flavoretro.glycoside_library import apply_template
        r=load_registry();new=[t for t in r.templates if t['template_id'].startswith('p2-scope:')]
        self.assertEqual(len(new),3)
        for t in new:
            self.assertGreaterEqual(len({r.instances[i]['acceptor'] for i in t['support_instances']}),2)
            for i in t['support_instances']:self.assertTrue(apply_template(t,r.instances[i]['target']))
            self.assertFalse(apply_template(t,'CO'))
