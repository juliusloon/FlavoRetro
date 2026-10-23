import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from flavoretro.pipeline_presentation import saved_cell, progress
from flavoretro.resources import sha
from flavoretro.workspace import AssetError


class SavedExperimentIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        env=patch.dict(os.environ,FLAVORETRO_WORKSPACE=str(self.root));env.start();self.addCleanup(env.stop)
        self.base=self.root/'outputs/task022'
        self.folder=self.base/'evaluation_audit/fixture/T-0-N';self.folder.mkdir(parents=True)
        self.request={'smiles':'CCO','seed':0}
        self.result={'run_id':'attempt-fixture','request':self.request,'status':'ok','routes':[]}
        (self.folder/'request.json').write_text(json.dumps(self.request))
        (self.folder/'result.json').write_text(json.dumps(self.result))
        self.bind()

    def bind(self):
        manifest={'attempt_id':'attempt-fixture','files':{p.name:sha(p) for p in self.folder.iterdir() if p.name!='manifest.json'}}
        path=self.folder/'manifest.json';path.write_text(json.dumps(manifest))
        rows=[{'event':'reserved','batch':'fixture','cell_id':'T-0-N','purpose':'engineering','attempt_id':'attempt-fixture','request':self.request},
              {'event':'finished','batch':'fixture','cell_id':'T-0-N','attempt_id':'attempt-fixture','status':'completed','artifacts':{str(path.relative_to(self.root)):sha(path)}}]
        (self.base/'run_ledger.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')

    def test_read_is_saved_evidence_not_new_search(self):
        with patch('flavoretro.service.search') as search:
            envelope=saved_cell('fixture','T-0-N')
            self.assertEqual(envelope['execution_source'],'explicit_saved_experiment')
            self.assertEqual(envelope['integrity'],'verified')
            search.assert_not_called()

    def test_result_bytes_and_bound_request_cannot_drift(self):
        self.result['request']={'smiles':'CCC','seed':0}
        (self.folder/'result.json').write_text(json.dumps(self.result))
        with self.assertRaisesRegex(AssetError,'file drift'):
            saved_cell('fixture','T-0-N')
        self.bind()
        with self.assertRaisesRegex(AssetError,'identity mismatch'):
            saved_cell('fixture','T-0-N')

    def test_path_escape_or_uncompleted_cell_cannot_open(self):
        with self.assertRaises(ValueError):saved_cell('../fixture','T-0-N')
        with self.assertRaises(AssetError):saved_cell('fixture','T-0-D')
        (self.base/'run_ledger.jsonl').write_text((self.base/'run_ledger.jsonl').read_text().splitlines()[0]+'\n')
        with self.assertRaisesRegex(AssetError,'uniquely completed'):
            saved_cell('fixture','T-0-N')
        self.assertEqual(progress()['unfinished_attempts'],1)


    def test_failed_attempt_with_result_cannot_be_opened_as_completed(self):
        path=self.base/'run_ledger.jsonl'
        entries=[json.loads(line) for line in path.read_text().splitlines()]
        entries[-1]['status']='failed'
        path.write_text('\n'.join(json.dumps(r) for r in entries)+'\n')
        with self.assertRaisesRegex(AssetError,'uniquely completed'):
            saved_cell('fixture','T-0-N')

    def record_batch(self, name, group, arms):
        protocol={'purpose':'development','claim_boundary':'fixture development boundary',
                  'cells':[{'cell_id':'T-0-'+arm,'arm':arm} for arm in arms],
                  'arms':{arm:arm for arm in arms}}
        frozen=self.base/'batches'/name/'frozen.json';frozen.parent.mkdir(parents=True)
        frozen.write_text(json.dumps({'batch':name,'protocol':protocol}))
        folder=self.base/group/name;folder.mkdir(parents=True)
        (folder/'summary.json').write_text(json.dumps({'axes':{'fixture':{'arms':{arm:{'reference_hits':0} for arm in arms}}},'cells':[]}))
        records=[]
        for arm in arms:
            cid='T-0-'+arm;attempt=name+'-'+arm
            dest=folder/cid;dest.mkdir()
            manifest=dest/'manifest.json';manifest.write_text('{}')
            records.extend([{'event':'reserved','batch':name,'cell_id':cid,'purpose':'development','attempt_id':attempt},
                            {'event':'finished','batch':name,'cell_id':cid,'attempt_id':attempt,'status':'completed','artifacts':{str(manifest.relative_to(self.root)):sha(manifest)}}])
        path=self.base/'run_ledger.jsonl'
        with path.open('a') as handle:
            handle.write('\n'.join(json.dumps(r) for r in records)+'\n')

    def test_new_runner_locations_and_versioned_arms_are_visible(self):
        self.record_batch('domain-fixture','new-source-output',['N','O','D8'])
        self.record_batch('algorithm-fixture','another-output',['N','O2R'])
        experiments={r['batch']:r for r in progress()['experiments']}
        for name,arms in [('domain-fixture',['N','O','D8']),('algorithm-fixture',['N','O2R'])]:
            item=experiments[name]
            self.assertEqual(item['summary_status'],'recorded_snapshot')
            self.assertNotIn('cells',item['summary'])
            self.assertEqual([r['arm'] for r in item['examples']],arms)

    def test_method_failure_disclosure_and_incomplete_pairs(self):
        self.record_batch('legacy-o2','legacy-output',['N','O2'])
        audit=self.base/'evaluation_audit/legacy-o2_independent_audit.json'
        audit.write_text(json.dumps({'limitations':['ignored treatment'], 'method_execution_valid_for_declared_frontier':False}))
        path=self.base/'run_ledger.jsonl'
        entries=[json.loads(line) for line in path.read_text().splitlines()]
        entries[-1]['status']='failed'
        path.write_text('\n'.join(json.dumps(r) for r in entries)+'\n')
        item=next(r for r in progress()['experiments'] if r['batch']=='legacy-o2')
        self.assertEqual(item['examples'],[])
        self.assertEqual(item['failed_cells'],1)
        self.assertFalse(item['method_execution_valid'])
        self.assertEqual(item['audit_limitations'],['ignored treatment'])
        self.assertIsNone(item['audit_axes'])
        audit.write_text(json.dumps({'complete':True,'all_cells_normal':True,'axes':{'fixture':{'arms':{'N':{'median_search_seconds':0.0}}}}}))
        item=next(r for r in progress()['experiments'] if r['batch']=='legacy-o2')
        self.assertEqual(item['audit_axes']['fixture']['arms']['N']['median_search_seconds'],0.0)



    def test_quality_snapshot_keeps_loss_target_pair_visible(self):
        self.record_batch('quality-fixture','quality-output',['N','STOP'])
        analysis=self.base/'quality-fixture_comparison.json'
        analysis.write_text(json.dumps({'batch':'quality-fixture','contrasts':{'STOP':{'summary':{'quality_noninferior_fraction':0.85},'pairs':[{'target_id':'T','seed':0,'arm':'STOP','quality_noninferior':False,'native_solved_score_vector':[1,2],'candidate_solved_score_vector':[1,3]}]}}}))
        item=next(r for r in progress()['experiments'] if r['batch']=='quality-fixture')
        self.assertEqual(item['quality_loss_example']['target_id'],'T')
        self.assertEqual(item['comparisons']['STOP']['quality_noninferior_fraction'],0.85)
        self.assertEqual(item['comparison_snapshot']['sha256'],sha(analysis))
        self.assertEqual([x['arm'] for x in item['examples']],['N','STOP'])


if __name__=='__main__':unittest.main()


class RuntimeAccountingPresentationTests(unittest.TestCase):
    def test_non_viewable_interface_accounting_keeps_counts_without_wrong_cell_links(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, FLAVORETRO_WORKSPACE=d):
            base=Path(d)/"outputs/task022"
            batch=base/"batches/runtime-only";batch.mkdir(parents=True)
            (batch/"frozen.json").write_text(json.dumps({"batch":"runtime-only","protocol":{"purpose":"engineering","claim_boundary":"interfacecheck","cells":[{"arm":"HTTP"}],"saved_experiment_viewable":False}}))
            artifact=base/"runtime_verify/cell/manifest.json";artifact.parent.mkdir(parents=True);artifact.write_text("{}")
            ledger=[{"event":"reserved","batch":"runtime-only","cell_id":"RT-1-HTTP","attempt_id":"a","request":{"smiles":"CCO"}}, {"event":"finished","batch":"runtime-only","cell_id":"RT-1-HTTP","attempt_id":"a","status":"completed","artifacts":{str(artifact.relative_to(Path(d))):sha(artifact)}}]
            (base/"run_ledger.jsonl").write_text(chr(10).join(json.dumps(r) for r in ledger)+chr(10))
            data=progress();self.assertEqual(data["search_attempts"],1);self.assertEqual(data["finished_attempts"],1)
            item=data["experiments"][0];self.assertEqual(item["status"],"completed");self.assertEqual(item["examples"],[]);self.assertEqual(item["arms"],{"HTTP":"HTTP"})
