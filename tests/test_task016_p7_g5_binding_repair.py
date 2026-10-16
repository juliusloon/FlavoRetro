"""SS-E02 G5 append-only frozen-scope binding contract tests.

Local-science-asset-dependent: explicitly skip in asset-free CI.
"""
import json
import unittest
from pathlib import Path

from scripts.operate import ROOT
from scripts.task016_p7_ss_g5_binding_repair_v1 import check

BASE = ROOT / "outputs/task016-p7/v1"
LEDGER = BASE / "epoch_ledger.jsonl"
REPAIR = BASE / "governance/SS_E02_R5_G5_binding_repair_v1/validation.json"


@unittest.skipUnless(LEDGER.exists() and REPAIR.exists(), "P7 local frozen assets unavailable")
class P7SSG5ScopeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
        cls.g4 = [x for x in cls.rows if x.get("epoch_id") == "SS-E02"
                  and x.get("stage") == "G4_SCOPE_FREEZE" and x.get("status") == "active"][-1]
        # R4 metadata batch being tested: later R8 G5 registrations must not
        # change which original omission/correction pair this test audits.
        r4_path = "outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R4-metadata/G5_FRESH_HOLDOUT_ACQUIRE.json"
        cls.g5s = [x for x in cls.rows if x.get("epoch_id") == "SS-E02"
                   and x.get("stage") == "G5_FRESH_HOLDOUT_ACQUIRE"
                   and x.get("status") == "active" and x.get("stage_manifest_path") == r4_path]
        cls.g5 = cls.g5s[-1]

    def test_repaired_registry_uses_unchanged_frozen_manifest(self):
        result = check(self.g4, self.g5, self.g5s)
        self.assertEqual(self.g5["scope_manifest_sha256"], result["scope_sha"])
        self.assertEqual(self.g5["scope_manifest_path"], result["scope_path"])
        self.assertEqual(result["g5_predecessor"], self.g4["stage_manifest_path"])
        self.assertTrue(self.g5["correction_of_omitted_registry_fields"])
        self.assertTrue(self.g5["not_a_new_G5_freeze"])
        self.assertEqual(self.g5["fresh_admitted"], 0)

    def test_original_incomplete_entry_is_not_backdated_or_erased(self):
        old = self.g5s[-2]
        self.assertNotIn("scope_manifest_sha256", old)
        self.assertEqual(old["stage_manifest_path"], self.g5["stage_manifest_path"])
        self.assertEqual(old["stage_manifest_sha256"], self.g5["stage_manifest_sha256"])
        self.assertNotEqual(old["registered_at"], self.g5["registered_at"])

    def test_scope_sha_forgery_fails_closed(self):
        bad = dict(self.g5, scope_manifest_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "G5_WRONG_SCOPE"):
            check(self.g4, bad, self.g5s[:-1] + [bad])

    def test_stage_sha_forgery_fails_closed(self):
        bad = dict(self.g5, stage_manifest_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "STAGE_SHA_DRIFT"):
            check(self.g4, bad, self.g5s[:-1] + [bad])

    def test_cross_epoch_forgery_fails_closed(self):
        bad = dict(self.g5, epoch_id="SS-E03")
        with self.assertRaisesRegex(ValueError, "G5_REGISTRATION_INVALID"):
            check(self.g4, bad, self.g5s[:-1] + [bad])


if __name__ == "__main__":
    unittest.main()
