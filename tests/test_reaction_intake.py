import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from flavoretro import reaction_intake as intake
from flavoretro.resources import sha
from flavoretro.workspace import AssetError


class ReactionIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, FLAVORETRO_WORKSPACE=str(self.root))
        self.env.start(); self.addCleanup(self.env.stop)
        source = self.root / "article.xml"
        source.write_text("<article><body><p>Fixture only: reported yield <bold>0%</bold> under these conditions.</p></body></article>")
        self.record = {"reaction_id": "fixture-1", "source": {"doi": "10.fixture/not-literature", "url": "https://example.org/fixture",
                       "local_path": "article.xml", "sha256": sha(source), "locator": "body/p[1]",
                       "quote": "Fixture only: reported yield 0% under these conditions.", "license": "test_fixture"},
                       "reactants": [{"name": "fixture alcohol", "smiles": "CCO", "identity_source": "test_fixture"}],
                       "products": [{"name": "fixture aldehyde", "smiles": "CC=O", "identity_source": "test_fixture"}],
                       "yield_value": 0, "yield_unit": "%", "yield_status": "reported",
                       "human_reviewed": False, "independent_chemical_validation": False,
                       "exposure": {"source_seen": False, "target_seen": None}}

    def build_snapshot(self, records):
        path = self.root / "input.json"; path.write_text(json.dumps({"records": records}))
        output = self.root / "outputs/task022/intake/v1"
        manifest = intake.build(path, output)
        (self.root / intake.POINTER).write_text(json.dumps({"manifest": str((output / "manifest.json").relative_to(self.root)),
                                                         "manifest_sha256": sha(output / "manifest.json")}))
        return manifest

    def test_zero_preserved_and_no_scientific_promotion(self):
        result = intake.assess(self.record)
        self.assertEqual(result["qc"]["issues"], [])
        self.assertTrue(result["qc"]["quote_located"])
        self.assertTrue(result["qc"]["yield_is_zero"])
        self.assertFalse(result["qc"]["yield_is_missing"])
        self.assertFalse(result["qc"]["independent_chemical_validation"])
        self.assertFalse(result["qc"]["identity_independently_verified"])
        self.assertFalse(result["qc"]["runtime_admitted"])
        self.assertEqual(result["exposure"]["target_seen"], None)

    def test_wrong_quote_and_tampered_source_are_retained(self):
        wrong = copy.deepcopy(self.record); wrong["source"]["quote"] = "An invented reaction claim."
        result = intake.assess(wrong)
        self.assertIn("quote_or_locator_not_verified", result["qc"]["issues"])
        self.assertEqual(result["source"]["quote"], wrong["source"]["quote"])
        (self.root / "article.xml").write_text("changed")
        self.assertIn("source_bytes_missing_or_drift", intake.assess(self.record)["qc"]["issues"])

    def test_incomplete_or_inferred_identity_not_ready(self):
        record = copy.deepcopy(self.record); record["products"][0]["smiles"] = None
        result = intake.assess(record)
        self.assertFalse(result["qc"]["structures_parseable"])
        self.assertEqual(result["qc"]["status"], "retained_with_issues")
        record = copy.deepcopy(self.record); record["products"][0]["structure_origin"] = "handwritten_from_name"
        self.assertIn("products_participant_0_inferred_structure", intake.assess(record)["qc"]["issues"])

    def test_duplicate_rows_and_qualitative_missing_distinction_preserved(self):
        missing = copy.deepcopy(self.record); missing["reaction_id"] = "missing"; missing["yield_value"] = None; missing["yield_status"] = "not_reported"
        trace = copy.deepcopy(missing); trace["reaction_id"] = "trace"; trace["yield_status"] = "trace"
        manifest = self.build_snapshot([self.record, self.record, missing, trace])
        self.assertEqual(manifest["summary"]["total"], 4)
        self.assertEqual(manifest["summary"]["zero_yields"], 2)
        self.assertEqual(manifest["summary"]["missing_yields"], 1)
        result = intake.query()
        self.assertEqual(len(result["records"]), 4)
        self.assertIn("duplicate_reaction_id", result["records"][0]["qc"]["issues"])
        self.assertTrue(result["records"][2]["qc"]["duplicate_reaction_signature"])

    def test_snapshot_and_bound_source_drift_rejected(self):
        self.build_snapshot([self.record])
        self.assertEqual(intake.query(q="FIXTURE", offset=0, limit=1)["total"], 1)
        (self.root / "article.xml").write_text("changed")
        with self.assertRaisesRegex(AssetError, "source drift"):
            intake.query()

    def test_path_escape_and_fabricated_review_are_not_admitted(self):
        record = copy.deepcopy(self.record); record["source"]["local_path"] = "../outside.txt"
        record["human_reviewed"] = True
        result = intake.assess(record)
        self.assertIn("source_binding_unavailable", result["qc"]["issues"])
        self.assertIn("unsupported_evidence_promotion", result["qc"]["issues"])
        self.assertFalse(result["qc"]["human_reviewed"])
        with self.assertRaises(ValueError):
            intake.query(limit=101)

    def test_empty_workspace_has_explicit_empty_state(self):
        self.assertEqual(intake.query()["status"], "not_built")


if __name__ == "__main__":
    unittest.main()
