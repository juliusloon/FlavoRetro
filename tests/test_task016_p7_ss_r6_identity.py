"""Contract tests for P7 R6 A3 identity and A6 conservative ID-union screen."""
import json
import unittest
from pathlib import Path

from scripts.operate import ROOT
from scripts.task016_p7_ss_r6_a6_alias_screen import direct_matches
from scripts.task016_p7_ss_r6_a6_alias_screen_v2 import collect_aliases

BASE=ROOT/"outputs/task016-p7/v1/SS/E02/fresh"
A3=BASE/"SS-E02-R6-A3-original-identity-v1/A3_original_identity_results.json"
A6=BASE/"SS-E02-R6-A6-documentary-exposure-screen-v2/A6_full_alias_union_dispositions.json"


class R6PureContracts(unittest.TestCase):
    def test_pmid_only_exposed_always_blocks_direct_alias(self):
        entries=[{"known_exposed":True,"identifier_tokens":["pmid:28725058"],"pointer":"exposure"}]
        self.assertEqual(len(direct_matches(["doi:10.1038/x","pmid:28725058"],entries)),1)

    def test_same_title_without_identity_never_claims_positive_or_clearance(self):
        entries=[{"known_exposed":True,"identifier_tokens":["pmid:111"],"title":"same"}]
        self.assertEqual(direct_matches(["doi:10.1000/example"],entries),[])

    def test_false_history_entries_not_positive(self):
        entries=[{"known_exposed":False,"identifier_tokens":["pmid:111"]}]
        self.assertEqual(direct_matches(["pmid:111"],entries),[])

    def test_original_and_official_conflict_detected(self):
        source={"DOI":"10.1000/example","publication_identity_verified":True,
          "front":{"ids":{"doi":["10.1000/example"],"pmid":["999"]}}}
        official=[{"normalized_identifier_tokens":["doi:10.1000/example","pmid:888"],
                   "record_id":"x","route":"official"}]
        with self.assertRaisesRegex(RuntimeError,"INDEPENDENT_ORIGINAL_ALIAS_MISMATCH"):
            collect_aliases(source,official)


@unittest.skipUnless(A3.exists() and A6.exists(),"P7 R6 local data unavailable")
class R6FrozenOutputContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a3=json.loads(A3.read_text())
        cls.a6=json.loads(A6.read_text())

    def test_two_original_fronts_ten_checks_all_pass(self):
        verified=[x for x in self.a3["results"] if x["publication_identity_verified"]]
        self.assertEqual(len(verified),2)
        for row in verified:
            self.assertEqual(len(row["checks"]),10)
            self.assertTrue(all(row["checks"].values()))
            self.assertFalse(row["abstract_or_chemical_body_read"])

    def test_four_missing_originals_stay_pending(self):
        self.assertEqual(self.a3["counts"],{"processed":6,"passed":2,"rejected":0,"pending":4})
        self.assertEqual(self.a3["fresh_admitted"],0)
        self.assertEqual(self.a6["counts"]["fresh_admitted"],0)

    def test_unverified_name_exposures_never_become_fresh(self):
        self.assertEqual(self.a6["unverified_literal_hypothesis_counts"],
              {"SS_pre_G4":9,"C_pre_G4":16,"C_post_G4":3})
        self.assertTrue(self.a6["source_exposure_nonmatch_does_not_establish_freshness"])
        self.assertTrue(all(x["fresh_admitted"] is False for x in self.a6["sources"]))

    def test_official_PMC_PMID_DOI_union_retained(self):
        a={x["source_id"]:x["official_alias_union"] for x in self.a6["sources"]}
        self.assertEqual(a["PMC5517534"],
           ["article:pmc5517534","doi:10.1038/s41598-017-06453-z","pmid:28725058"])
        self.assertIn("pmid:1124927",a["SS-E02-R3-ID-012"])
        self.assertIn("pmid:160697",a["SS-E02-R3-ID-015"])
        self.assertIn("pmid:9167271",a["SS-E02-R3-ID-017"])

    def test_no_chemical_or_network_promotions(self):
        self.assertEqual(self.a3["new_HTTP"],0)
        self.assertEqual(self.a6["new_HTTP"],0)
        self.assertEqual(self.a6["new_MCTS"],0)
        self.assertTrue(self.a6["not_final_transitive_closure"])
        self.assertTrue(self.a6["no_chemical_source_or_reaction_eligibility_claim"])

if __name__=="__main__":
    unittest.main()
