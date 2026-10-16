"""TASK-016-P7 R7: fail-closed historical exposed-name graph guard tests."""
import json,unittest
from pathlib import Path
from scripts.operate import ROOT
from scripts.task016_p7_r7_exposed_graph_guard import graph,classify_fresh_target
BASE=ROOT/"outputs/task016-p7/v1/governance"
P=BASE/"P7-R7-exposed-graph-candidate-guard-v1/candidate_graph_guard.json"
Q=BASE/"P7-R7-authoritative-exposed-name-resolution-v1/query_execution.jsonl"

class R7PureGuards(unittest.TestCase):
    def test_identical_structure_different_smiles_order_blocks(self):
        fake={"candidate_graph_index":[{"exposed_name":"name","official_PubChem_CID":12,
               "historical_exposure_ids":["prior"],"canonical_RDKit_SMILES":graph("CCO")}]}
        x=classify_fresh_target("OCC",fake)
        self.assertEqual(x["status"],"potential_prior_exposure_block")
        self.assertFalse(x["fresh_eligible"])
        self.assertEqual(x["matched_exposures"][0]["exposure_ids"],["prior"])

    def test_unmatched_is_not_a_fresh_clearance(self):
        fake={"candidate_graph_index":[{"exposed_name":"name","official_PubChem_CID":12,
          "historical_exposure_ids":["prior"],"canonical_RDKit_SMILES":graph("CCO")}]}
        x=classify_fresh_target("CCN",fake)
        self.assertFalse(x["fresh_eligible"])
        self.assertEqual(x["status"],"pending_no_match_not_fresh_cleared")

    def test_missing_and_bad_graph_pending(self):
        fake={"candidate_graph_index":[]}
        for value in ("",None,"C1("):
            with self.subTest(value=value):
                x=classify_fresh_target(value,fake)
                self.assertFalse(x["fresh_eligible"])
                self.assertEqual(x["status"],"pending_invalid_or_missing_input")

    def test_stereochemical_variation_not_auto_equated(self):
        fake={"candidate_graph_index":[{"exposed_name":"name","official_PubChem_CID":12,
          "historical_exposure_ids":["prior"],"canonical_RDKit_SMILES":graph("N[C@@H](C)C(=O)O")}]}
        opposite=classify_fresh_target("N[C@H](C)C(=O)O",fake)
        self.assertEqual(opposite["status"],"pending_no_match_not_fresh_cleared")
        self.assertFalse(opposite["fresh_eligible"])


@unittest.skipUnless(P.is_file() and Q.is_file(),"P7 local R7 data unavailable")
class R7FrozenEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=json.loads(P.read_text())
        cls.q=[json.loads(x) for x in Q.read_text().splitlines() if x.strip()]

    def test_raw_query_count_and_graph_coverage(self):
        self.assertEqual(len(self.q),27)
        self.assertEqual(len(self.g["candidate_graph_index"]),27)
        self.assertEqual(self.g["counts"]["name_exposure_records"],28)
        self.assertEqual(self.g["counts"]["fresh_admitted"],0)
        self.assertEqual(self.g["counts"]["new_HTTP"],0)

    def test_duplicate_name_cross_family_exposure_remains_permanent(self):
        ix=[r for r in self.g["candidate_graph_index"] if r["exposed_name"]=="isorhamnetin"]
        self.assertEqual(len(ix),1)
        self.assertEqual(len(ix[0]["historical_exposure_ids"]),2)
        self.assertEqual(set(x.split(":")[0] for x in ix[0]["family_exposure_tags"]),{"C","SS"})

    def test_each_official_property_is_candidate_only(self):
        self.assertTrue(all(r["candidate_only_not_independently_verified"] for r in self.g["candidate_graph_index"]))
        self.assertTrue(self.g["nonmatches_remain_unresolved"])
        self.assertTrue(self.g["name_to_CID_not_official_synonym_closed"])

    def test_real_normalized_graph_blocks_without_fresh_promotion(self):
        first=self.g["candidate_graph_index"][0]
        x=classify_fresh_target(first["raw_property_SMILES"],self.g)
        self.assertEqual(x["status"],"potential_prior_exposure_block")
        self.assertFalse(x["fresh_eligible"])
        self.assertEqual(x["matched_exposures"][0]["CID"],first["official_PubChem_CID"])

if __name__=="__main__":unittest.main()
