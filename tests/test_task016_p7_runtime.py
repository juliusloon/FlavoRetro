"""Production P7 runtime guards; local source-dependent tests skip without payloads."""
import copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from flavoretro.workspace import root,config,AssetError
from flavoretro.contracts import SearchRequest
from flavoretro.resources import sha

P7_ASSETS=(root()/"outputs/task016-p7/v1/runtime/template_source_manifest.json").is_file()

class P7RuntimeContracts(unittest.TestCase):
    def test_p7_v7_default_off(self):
        self.assertNotIn("glycoside_library_version",SearchRequest(smiles="CCO").payload())
        with self.assertRaises(ValueError):SearchRequest(smiles="CCO",glycoside_library_version="v7")
        if (root()/"configs/glycoside-library-v7.json").is_file():
            self.assertIs(config("glycoside-library-v7.json")["default_enabled"],False)
            self.assertEqual((root()/"configs/glycoside-library-v7.json").read_bytes(),(root()/"flavoretro/assets/configs/glycoside-library-v7.json").read_bytes())

    def test_p7_v7_manifest_drift_fails_closed(self):
        from flavoretro.glycoside_library_v7 import Registry
        with tempfile.TemporaryDirectory() as tmp:
            manifest=Path(tmp)/"manifest.json";manifest.write_text("{}")
            with self.assertRaisesRegex(AssetError,"manifest absent or hash drift"):Registry(manifest,"f"*64)
        with self.assertRaises(AssetError):Registry(Path("/nonexistent/P7/manifest.json"),"0"*64)

    @unittest.skipUnless(P7_ASSETS,"P7 qualified local scope payload required")
    def test_p7_frozen_guard_drift_fails_closed(self):
        from flavoretro import glycoside_library_v7 as v7
        guard=root()/"flavoretro/glycoside_scope_c_v7.py"
        original=sha
        with patch.object(v7,"sha",side_effect=lambda path:"f"*64 if Path(path).resolve()==guard.resolve() else original(path)):
            with self.assertRaisesRegex(AssetError,"frozen scope asset drift"):v7.load_registry()

    @unittest.skipUnless(P7_ASSETS,"P7 qualified local scope payload required")
    def test_p7_v6_behavior_unchanged(self):
        from flavoretro import glycoside_library_v6 as v6,glycoside_library_v7 as v7
        baseline=v6.load_registry();current=v7.load_registry()
        self.assertEqual(current.binding["chained_v6"],baseline.binding)
        self.assertEqual(current.templates[:len(baseline.templates)],baseline.templates)
        self.assertEqual(current.settings,baseline.settings)
        for t in baseline.templates:
            for iid in t["support_instances"]:
                target=baseline.instances[iid]["target"]
                self.assertEqual(v6.apply_template(t,target),v7.apply_template(t,target),iid)

    @unittest.skipUnless(P7_ASSETS,"P7 qualified local scope payload required")
    def test_p7_qualified_increment_replays_actual_mapped_reactions(self):
        from aizynthfinder.chem import TreeMolecule
        from flavoretro.glycoside_library_v7 import load_registry,LibraryRetroReaction
        from flavoretro.reviewed_resources import canonical_side
        registry=load_registry()
        for t in registry.increment_templates:
            for iid in t["support_instances"]:
                r=registry.increment_instances[iid]
                action=LibraryRetroReaction(TreeMolecule(parent=None,smiles=r["target"]),smarts=t["smarts"],use_rdchiral=False,metadata=dict(template_id=t["template_id"],library_template=t,domain_binding=registry.binding,required_context=t["required_context"],policy_name="glycoside"))
                expected=canonical_side(r["reference_precursors"])
                matches=[i for i,o in enumerate(action.reactants) if canonical_side([p.smiles for p in o])==expected]
                self.assertTrue(matches,iid)
                for i in matches:
                    e=registry.evidence(action.copy(index=i))
                    self.assertTrue(e["exact_seed_instance_match"])
                    self.assertEqual(e["namespace"],"task016_p7")
                    for flag in ["human_reviewed","independent_chemical_validation","prediction_conditions_verified","actionable","evidence_closed"]:self.assertIs(e[flag],False)

    def test_p7_charged_canary_reference_matches_production_trace(self):
        from types import SimpleNamespace
        from flavoretro.search import Node
        from flavoretro.reviewed_resources import reaction_signature, canonical_side
        from flavoretro.open_glycoside_library import normalize_species
        from scripts.task016_p7_canary_recovery import trace_reference
        # Isolated trace fixture for the actual charged-target evaluation bug;
        # no search, source admission, or tree-transfer evidence is created.
        target = canonical_side(["[O-]c1ccccc1"])
        record = dict(target=target, reference_precursors=["CCO", "O"])
        action = SimpleNamespace(mol=SimpleNamespace(smiles=target),
                                 reactants=[tuple(SimpleNamespace(smiles=s) for s in ["CCO", "O"])],
                                 metadata=dict(policy_name="fixture", template_id="trace-contract"))
        node = SimpleNamespace(tree=SimpleNamespace(action_trace=[], trace_target=target))
        Node.trace_action(node, action, "generated")
        self.assertEqual(len(node.tree.action_trace), 1)
        self.assertEqual(trace_reference(record), node.tree.action_trace[0]["signature"])
        neutral_target = normalize_species(target)["normalized"]
        self.assertNotEqual(reaction_signature(record["reference_precursors"], [neutral_target]),
                            node.tree.action_trace[0]["signature"])

    def test_p7_run_ledger_rejects_duplicate_or_unreserved_completion(self):
        from flavoretro.task016_runs import append_run
        approval=root()/"outputs/task016-p7/v1/approval.json"
        if not approval.exists():self.skipTest("P7 approved local baseline required")
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);ledger=base/"outputs/task016-p7/v1/run_ledger.jsonl";ledger.parent.mkdir(parents=True)
            ledger.with_name("approval.json").write_bytes(approval.read_bytes())
            with patch("flavoretro.task016_runs.root",return_value=base),patch.dict(os.environ,FLAVORETRO_TASK016_LEDGER=str(ledger),FLAVORETRO_TASK016_PURPOSE="p7_engineering"):
                with self.assertRaises(ValueError):append_run("unreserved","finished")
                append_run("fixture-reservation","started",synthetic_fixture=True)
                append_run("fixture-reservation","finished",synthetic_fixture=True)
                with self.assertRaises(ValueError):append_run("fixture-reservation","finished")
                with self.assertRaises(ValueError):append_run("fixture-reservation","started")
                self.assertEqual(len(ledger.read_text().splitlines()),2)

if __name__=="__main__":unittest.main()
