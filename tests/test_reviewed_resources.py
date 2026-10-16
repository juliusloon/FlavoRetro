import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rdkit import rdBase
from flavoretro.resources import structure, sha, dumps
from flavoretro.reviewed_resources import assemble, reaction_signature, ReviewView, load_review
from flavoretro.workspace import AssetError
from flavoretro.worker import annotate


def resource(rid, smiles="CCO", allowed=True, name="test"):
    return {"id": rid, "kind": "stock", "raw": {"stock_id": "STK-" + rid, "name": name},
            "structure": structure(smiles), "runtime_candidate_allowed": allowed,
            "source_path": "fixture.json", "source_sha256": "a" * 64, "locator": rid}


def identity(row, decision):
    return {"record_id": row["id"], "kind": row["kind"], "ref": row["raw"]["stock_id"],
            "computed_inchikey": row["structure"]["inchikey"], "final_decision": decision,
            "reason": "fixture", "reviewer_type": "agent", "decision_authority": "agent_delegated"}


def view(rows, identities=(), axes=(), pilot=()):
    data = assemble(rows, axes, [], identities, [], [], pilot)
    return ReviewView(data, {"version": "fixture-v1", "mode": "adjudicated"})


class ReviewMatching(unittest.TestCase):
    def test_map_numbers_ignored_components_and_direction_preserved(self):
        self.assertEqual(reaction_signature(["[CH3:1][OH:2]", "CC"], ["COC"]),
                         reaction_signature(["CC", "CO"], ["COC"]))
        self.assertNotEqual(reaction_signature(["CO", "CO"], ["COC"]), reaction_signature(["CO"], ["COC"]))
        self.assertNotEqual(reaction_signature(["CO"], ["COC"]), reaction_signature(["COC"], ["CO"]))

    def test_stereo_isotope_salt_and_products_are_not_erased(self):
        for a,b in [("C[C@H](O)Cl", "C[C@@H](O)Cl"), ("[13CH3]O", "CO"), ("CC(=O)[O-].[Na+]", "CC(=O)O")]:
            self.assertNotEqual(reaction_signature([a], ["CCO"]), reaction_signature([b], ["CCO"]))
        self.assertNotEqual(reaction_signature(["CO"], ["CCO", "O"]), reaction_signature(["CO"], ["CCO"]))
        self.assertIsNone(reaction_signature(["*"], ["CCO"]))

    def test_quarantine_cannot_be_reenabled_by_original_flag(self):
        row=resource("bad")
        v=view([row], [identity(row,"quarantine_name_structure_mismatch")])
        self.assertEqual(v.keys,set())
        self.assertFalse(v.record("bad")["effective_runtime_candidate_allowed"])

    def test_independent_same_graph_source_survives(self):
        bad, good=resource("bad"), resource("good")
        v=view([bad,good],[identity(bad,"quarantine_name_structure_mismatch"),identity(good,"retain_encoded_candidate")])
        self.assertEqual(v.keys,{good["structure"]["inchikey"]})
        self.assertEqual(len(v.leaf("OCC")["stock_records"]),2)
        self.assertFalse(v.leaf("OCC")["current_exact_supply_verified"])

    def test_review_never_expands_original_permission(self):
        row=resource("disabled",allowed=False)
        self.assertEqual(view([row],[identity(row,"retain_encoded_candidate")]).keys,set())
        from flavoretro.policies import CandidateStock
        with patch("flavoretro.reviewed_resources.load_review") as loader:
            self.assertEqual(CandidateStock(enabled=False).keys,set())
            loader.assert_not_called()

    def test_identity_and_vendor_join_fail_closed(self):
        row=resource("a"); bad=identity(row,"retain_encoded_candidate");bad["computed_inchikey"]="wrong"
        with self.assertRaises(AssetError):view([row],[bad])
        with self.assertRaises(AssetError):assemble([row],[],[],[],[{"stock_ref":"unknown"}],[],[])

    def test_exact_instance_support_is_axis_specific_and_source_specific(self):
        r=resource("reaction");r.update(kind="scifinder_reaction",components=[{"role":"reactant","structure":structure("CO")},{"role":"product","structure":structure("CCO")}])
        card={"id":r["id"],"source_sha256":r["source_sha256"],"card_number":1,"reviewer_type":"agent","decision_authority":"agent_delegated","owner_adopted_conclusions":True,"structure_decision":"development_gold","structure_gold":None,"source_final_status":"primary_instance_verified","yield_final":{"final_status":"numeric","primary_value":0,"raw_reported":"0"},"source_evidence":{"status":"primary_instance_verified"},"primary_source_supported":True,"numeric_yield_supported":True}
        v=view([r],axes=[card])
        exact=v.reaction(["CO"],["CCO"])
        self.assertTrue(exact["source_instance_supported"])
        self.assertFalse(exact["prediction_conditions_verified"])
        self.assertFalse(exact["actionable"])
        self.assertEqual(exact["evidence"][0]["source_instance_yield"]["primary_value"],0)
        self.assertFalse(v.reaction(["CO"],["CCO","O"])["source_instance_supported"])
        pilot={"id":r["id"],"input_record":r,"queue":"blocked_source_blacklist"}
        self.assertFalse(view([r],axes=[card],pilot=[pilot]).reaction(["CO"],["CCO"])["source_instance_supported"])
        card["source_sha256"]="wrong"
        with self.assertRaises(AssetError):view([r],axes=[card])

    def test_annotation_preserves_route_closure_and_has_review(self):
        row=resource("a");v=view([row])
        node={"type":"mol","smiles":"CCO","in_stock":True,"children":[]}
        _, leaves=annotate(node,True,v)
        self.assertEqual(leaves[0]["closure"],"surrogate")
        self.assertFalse(leaves[0]["review"]["evidence_closed"])
        self.assertIn("review_version",leaves[0]["review"])


    def test_policy_uses_selected_outcome_and_preserves_prior(self):
        from aizynthfinder.context.config import Configuration
        from flavoretro.policies import ReviewedEvidence
        r=resource("reaction");r.update(kind="scifinder_reaction",components=[{"role":"reactant","structure":structure("CO")},{"role":"product","structure":structure("CCO")}])
        v=view([r])
        with patch("flavoretro.reviewed_resources.load_review",return_value=v):
            policy=ReviewedEvidence("review",Configuration())
        mol=lambda smiles:type("Molecule",(),{"smiles":smiles})()
        fake=type("Reaction",(),{"mol":mol("CCO"),"reactants":[(mol("CC"),),(mol("CO"),)],"index":1,"metadata":{"policy_probability":0.2}})()
        policy.apply(fake)
        self.assertEqual(fake.metadata["review"]["status"],"exact_match")
        self.assertEqual(fake.metadata["policy_probability"],0.2)
        fake.index=0;policy.apply(fake)
        self.assertEqual(fake.metadata["review"]["status"],"unmatched")


class ReviewIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.env=patch.dict(os.environ,FLAVORETRO_WORKSPACE=self.tmp.name);self.env.start();self.addCleanup(self.env.stop)
        self.envlegacy=patch.dict(os.environ,{"FLAVORETRO_REVIEW_VALIDATION_LEGACY":"0"});self.envlegacy.start();self.addCleanup(self.envlegacy.stop)
        self.folder=self.root/'review';self.folder.mkdir()
        data=assemble([resource("a")],[],[],[],[],[],[])
        (self.folder/'index.json').write_text(dumps(data))
        self.manifest={"schema_version":1,"version":"fixture-v1","rdkit_version":rdBase.rdkitVersion,"base_resource_version":"fixture","base_manifest_sha256":"base","records_sha256":"records","sources_sha256":"sources","inputs_sha256":{},"payload_sha256":{"index.json":sha(self.folder/'index.json')},"summary":data['summary']}
        self.save()
        self.base=patch('flavoretro.reviewed_resources.active_data',return_value=(self.root,{"records_sha256":"records","sources_sha256":"sources"},{"version":"fixture","manifest_sha256":"base"}));self.base.start();self.addCleanup(self.base.stop)

    def save(self):
        (self.folder/'manifest.json').write_text(dumps(self.manifest))
        p=self.root/'configs';p.mkdir(exist_ok=True)
        (p/'search.json').write_text(dumps({'reviewed_resources':{'manifest':'review/manifest.json','manifest_sha256':sha(self.folder/'manifest.json')}}))

    def test_pinned_binding_and_mutated_payload(self):
        binding=load_review().binding
        self.assertEqual(load_review(binding).binding,binding)
        (self.folder/'index.json').write_text('{}')
        with self.assertRaises(AssetError):load_review(binding)

    def test_wrong_manifest_schema_missing_and_workspace_escape(self):
        self.manifest['schema_version']=True;self.save()
        with self.assertRaises(AssetError):load_review()
        self.manifest['schema_version']=1;self.save()
        configpath=self.root/'configs/search.json'
        configpath.write_text(dumps({'reviewed_resources':{'manifest':'../outside.json','manifest_sha256':'bad'}}))
        with self.assertRaises(AssetError):load_review()
        configpath.write_text('{}')
        with self.assertRaises(AssetError):load_review()

    def test_mid_run_binding_drift_and_frozen_source_drift(self):
        expected=load_review().binding
        self.manifest['version']='fixture-v2';self.save()
        with self.assertRaises(AssetError):load_review(expected)
        p=self.root/'source.json';p.write_text('original')
        self.manifest['inputs_sha256']={'source.json':sha(p)};self.save()
        load_review()
        p.write_text('modified')
        with self.assertRaises(AssetError):load_review()

    def test_legacy_comparison_explicitly_marked(self):
        normal=load_review().binding
        with patch.dict(os.environ,FLAVORETRO_REVIEW_VALIDATION_LEGACY='1'):
            legacy=load_review()
            self.assertEqual(legacy.binding['mode'],'legacy_validation')
            with self.assertRaises(AssetError):load_review(normal)
            self.assertFalse(legacy.reaction(['CO'],['CCO'])['source_instance_supported'])


if __name__=='__main__':unittest.main()
