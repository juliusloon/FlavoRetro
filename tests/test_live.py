import unittest
from flavoretro.resources import ROOT
from flavoretro.service import search
from flavoretro.contracts import SearchRequest


@unittest.skipUnless(
    (ROOT / "data/raw/legacy/data/uspto_model.onnx").exists(), "local models required"
)
class LiveContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        req = SearchRequest(
            smiles="CCOc1ccccc1",
            mode="quick",
            seconds=3.0,
            iterations=5,
            nodes=7,
            branching=2,
        )
        cls.runs = [search(req), search(req)]

    def test_fresh_real_engine(self):
        self.assertNotEqual(self.runs[0]["run_id"], self.runs[1]["run_id"])
        for r in self.runs:
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["execution_source"], "live_aizynthfinder_mcts")
            self.assertEqual(
                r["phases"][0]["engine_class"], "flavoretro.search.SearchTree"
            )

    def test_actual_node_bound_and_partial_paths(self):
        for r in self.runs:
            self.assertLessEqual(r["phases"][0]["node_count"], 7)
            self.assertTrue(r["routes"])
            self.assertTrue(all(route["steps"] > 0 for route in r["routes"]))
            self.assertTrue(all(not route["evidence_closed"] for route in r["routes"]))

    def test_seed_scoped_structural_identity(self):
        self.assertEqual(
            [r["route_id"] for r in self.runs[0]["routes"]],
            [r["route_id"] for r in self.runs[1]["routes"]],
        )
