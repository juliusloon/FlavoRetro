import unittest
from scripts.task016_p7_source_alias_closure import assert_fresh,assert_zero_leakage,explicit_pmid_tokens
from scripts.task016_p7_orchestrate import ContractError
class PMIDClosureTests(unittest.TestCase):
    def setUp(self):
        self.exposure=dict(development_exposed=True,exposure_type="post_scope_source_review",closure_tokens=["doi:10.1000/test","pmid:26923852"])
    def test_pmid_only_rename_and_nested_MED_identity_rejected(self):
        for record in ({"pmid":"26923852","reaction_id":"renamed"},{"source_binding":{"source":"MED","source_id":"26923852"}},{"source_pmid":"PMID:26923852"}):
            with self.subTest(record=record),self.assertRaises(ContractError):assert_fresh(record,[self.exposure])
    def test_pmid_build_holdout_alias_rejected(self):
        with self.assertRaises(ContractError):assert_zero_leakage([{"source_pmid":"26923852"}],[{"pmid":26923852}])
    def test_unrelated_identifier_allowed_and_legacy_DOI_still_rejected(self):
        self.assertTrue(assert_fresh({"pmid":"99999999"},[self.exposure]))
        with self.assertRaises(ContractError):assert_fresh({"doi":"10.1000/test"},[self.exposure])
    def test_malformed_explicit_PMID_fails_closed_without_guessing_numbers(self):
        for value in (True,"unknown","PMC26923852",-1,0,[26923852]):
            with self.subTest(value=value),self.assertRaises(ContractError):explicit_pmid_tokens({"pmid":value})
        self.assertEqual(explicit_pmid_tokens({"candidate_id":"26923852","pmid":None}),set())
if __name__=="__main__":unittest.main()
