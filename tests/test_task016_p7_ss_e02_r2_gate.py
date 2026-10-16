"""P7 SS-E02 R2: post-freeze identity/exposure/source-scope gates remain fail-closed."""
import json
import unittest
from pathlib import Path

from scripts.task016_p7_orchestrate import ContractError,sha_file,verify_stage_chain
from scripts.task016_p7_source_alias_closure import assert_fresh

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/"outputs/task016-p7/v1/SS/E02"
DOC=ROOT/"outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R2-PMC11125054-"

def load(p):return json.loads(Path(p).read_text())

class P7SSE02SourceR2GateTests(unittest.TestCase):
    def test_frozen_scope_chain_still_unchanged(self):
        frozen=load(B/"scope_manifest.json")
        self.assertFalse(frozen["holdout_extraction_started"])
        self.assertEqual(sha_file(B/"scope_bank.json"),frozen["scope_bank_sha256"])
        p=B/"stages/G4_SCOPE_FREEZE.json"
        self.assertEqual(verify_stage_chain(p,sha_file(p))["stage"],"G4_SCOPE_FREEZE")

    def test_all_R2_stage_branches_replay(self):
        for name in ("SS-E02-R2-metadata/G5_FRESH_HOLDOUT_ACQUIRE.json",
                     "SS-E02-R2-PMC11125054/G5_FRESH_HOLDOUT_ACQUIRE.json",
                     "SS-E02-R2-PMC11125054/G6_IDENTITY_STRUCTURE_ADMIT.json"):
            with self.subTest(name=name):
                p=B/"stages/batches"/name
                self.assertEqual(verify_stage_chain(p,sha_file(p))["stage"],p.stem)

    def test_original_identity_verified_without_chemical_admission(self):
        x=load(Path(str(DOC)+"A3/A3_publication_identity.json"))
        self.assertEqual(x["passed"],x["total"])
        self.assertTrue(x["publication_identity_verified"])
        self.assertFalse(x["source_eligible_for_G6"])

    def test_source_assay_out_of_ss_scope(self):
        a5=load(Path(str(DOC)+"A5/A5_independent_source_assay_screen.json"))
        a6=load(Path(str(DOC)+"A6_scope_disposition/A6_source_scope_disposition.json"))
        self.assertEqual(a5["passed"],5)
        self.assertTrue(a5["assay_acceptors_are_source_named_aglycones"])
        self.assertEqual(a6["disposition"],"rejected_for_frozen_SS_E02_O2_assay")
        self.assertFalse(a6["scope_applicable_to_reported_assay"])
        self.assertEqual(a6["G6_new_structure_admitted"],0)

    def test_postfreeze_chemical_source_permanently_exposed_all_aliases(self):
        exposure=load(Path(str(DOC)+"science-screen/permanent_postfreeze_source_exposure.json"))
        self.assertTrue(exposure["development_exposed"])
        for record in ({"pmcid":"PMC11125054"},{"pmid":"38794460"},{"doi":"10.3390/plants13101390"}):
            with self.subTest(record=record),self.assertRaises(ContractError):
                assert_fresh(record,[exposure])
        self.assertTrue(assert_fresh({"pmid":"99999999"},[exposure]))

if __name__=="__main__":
    unittest.main()
