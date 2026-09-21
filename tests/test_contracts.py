import json, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError
from flavoretro.contracts import SearchRequest
from flavoretro.resources import outcome, structure, ROOT, sha
from flavoretro.policies import CandidateStock, KnownHazards, hazard_reason, records
from flavoretro.service import search
from flavoretro.worker import route_identity
from aizynthfinder.context.config import Configuration
from aizynthfinder.utils.exceptions import RejectionException


class DataContracts(unittest.TestCase):
    def test_zero_is_not_missing(self):
        for token in [0, "0", "0.0", "0%"]:
            value = outcome(token)
            self.assertEqual(value["value"], 0)
            self.assertFalse(value["is_missing"])
        for token in [None, "", "NA"]:
            self.assertTrue(outcome(token)["is_missing"])

    def test_out_of_range_is_not_clipped(self):
        self.assertEqual(outcome("-2")["value"], -2)
        self.assertEqual(outcome("120")["value"], 120)
        self.assertFalse(outcome("trace")["is_missing"])
        self.assertIsNone(outcome("trace")["value"])

    def test_salt_and_stereochemistry_preserved(self):
        self.assertIn(".", structure("CC(=O)[O-].[Na+]")["canonical_smiles"])
        self.assertNotEqual(
            structure("C[C@H](O)Cl")["inchikey"], structure("C[C@@H](O)Cl")["inchikey"]
        )

    def test_invalid_retained(self):
        self.assertEqual(structure("not-a-molecule")["status"], "parse_failure")

    @unittest.skipUnless(
        (ROOT / "data/derived/v1/records.json").exists(), "local raw assets required"
    )
    def test_real_conservation_and_conflicts(self):
        rows = records()
        self.assertEqual(len(rows), 3059)
        self.assertEqual(sum(r.get("name_conflict_recomputed", False) for r in rows), 3)
        self.assertTrue(
            all(
                not r["production_eligible"]
                and r["human_review_status"] == "not_performed"
                for r in rows
            )
        )
        self.assertEqual(sum(r["kind"] == "scifinder_reaction" for r in rows), 2301)

    @unittest.skipUnless(
        (ROOT / "data/derived/replay-v1").exists(), "local replay required"
    )
    def test_replay(self):
        for file in ["records.json", "manifest.json"]:
            self.assertEqual(
                sha(ROOT / "data/derived/v1" / file),
                sha(ROOT / "data/derived/replay-v1" / file),
            )

    def test_no_candidate_stock_by_default(self):
        self.assertEqual(len(CandidateStock()), 0)

    def test_conflicts_virtuals_excluded(self):
        stock = CandidateStock(enabled=True)
        for r in records():
            if r["kind"] == "stock" and (
                r.get("name_conflict_recomputed")
                or r["raw"]["source_layer"] == "virtual_bridge"
            ):
                self.assertNotIn(r["structure"]["inchikey"], stock.keys)


class RuntimeContracts(unittest.TestCase):
    def test_invalid_smiles(self):
        for s in ["", "*", "INVALID"]:
            with self.assertRaises(ValidationError):
                SearchRequest(smiles=s)

    def test_limits_and_nonfinite(self):
        for kwargs in [
            {"nodes": 25001},
            {"depth": 11},
            {"branching": 25},
            {"seconds": float("nan")},
            {"iterations": 0},
            {"seed": -1},
            {"top_k": 0},
            {"candidate_stock": "false"},
        ]:
            with self.assertRaises(ValidationError):
                SearchRequest(smiles="CCO", **kwargs)

    def test_profile_phases_and_overrides(self):
        req = SearchRequest(smiles="CCO")
        self.assertEqual(len(req.phases()), 2)
        self.assertEqual(req.phases()[1]["depth"], 8)
        req = SearchRequest(smiles="CCO", seconds=0.5)
        self.assertTrue(all(p["seconds"] == 0.5 for p in req.phases()))

    def test_route_identity_ignores_scores_not_connectivity(self):
        a = {"type": "mol", "smiles": "CCO", "score": 1, "children": []}
        b = {**a, "score": 2}
        self.assertEqual(route_identity(a), route_identity(b))
        self.assertNotEqual(route_identity(a), route_identity({**a, "smiles": "COC"}))

    def test_known_hazards_and_unknown(self):
        self.assertEqual(hazard_reason("[Hg]"), "heavy_metal")
        self.assertIsNotNone(hazard_reason("CI"))
        self.assertIsNone(hazard_reason("CCO"))

    def test_negative_replay_and_temperature(self):
        policy = KnownHazards("test", Configuration())
        for meta in [
            {"forward_replay": False},
            {"temperature_c": -78},
            {"pyrophoric": True},
        ]:
            fake = type("Reaction", (), {"metadata": meta})()
            with self.assertRaises(RejectionException):
                policy.apply(fake)

    def test_timeout_recorded_no_fallback(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch(
                "flavoretro.service.subprocess.run",
                side_effect=subprocess.TimeoutExpired("worker", 1),
            ),
        ):
            result = search(SearchRequest(smiles="CCO", mode="quick"), folder)
            self.assertEqual(result["error"]["code"], "timeout")
            self.assertEqual(result["routes"], [])
            files = list(Path(folder).glob("*/manifest.json"))
            self.assertEqual(len(files), 1)

    def test_engine_failure_recorded(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch(
                "flavoretro.service.subprocess.run",
                return_value=type("Process", (), {"returncode": 1})(),
            ),
        ):
            result = search(SearchRequest(smiles="CCO", mode="quick"), folder)
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error"]["code"], "engine_error")


if __name__ == "__main__":
    unittest.main()
