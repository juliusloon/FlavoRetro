import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from flavoretro.contracts import SearchRequest
from flavoretro.workspace import root,AssetError,config

OUT = Path("outputs/task016-p4/v1")


def rows(p):
    p = root() / p
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


class V5Contracts(unittest.TestCase):
    def test_explicit_v5_requires_domain_optimized(self):
        with self.assertRaises(ValueError):
            SearchRequest(smiles="CCO", glycoside_library_version="v5")
        with self.assertRaises(ValueError):
            SearchRequest(smiles="CCO", engine="native", glycoside_expansion=True,
                          glycoside_library_version="v5")
        self.assertEqual(
            SearchRequest(smiles="CCO", glycoside_expansion=True,
                          glycoside_library_version="v5").payload()["glycoside_library_version"],
            "v5")

    def test_v5_default_off(self):
        self.assertFalse(config("glycoside-library-v5.json")["default_enabled"])
        self.assertNotIn("glycoside_library_version",
                         SearchRequest(smiles="CCO").payload())

    def test_v5_packaged_missing_assets_fail_closed(self):
        from flavoretro.glycoside_library_v5 import load_registry
        with tempfile.TemporaryDirectory() as t, patch.dict(os.environ, {"FLAVORETRO_WORKSPACE": t}):
            with self.assertRaises(AssetError):
                load_registry()

    def test_v5_manifest_drift_rejected(self):
        from flavoretro.glycoside_library_v5 import Registry
        p = root() / "outputs/task016-p4/v1/template_source_manifest.json"
        with self.assertRaises(AssetError):
            Registry(p, "0" * 64)

    def test_v5_inherits_v3_plus_only_revalidated_scope(self):
        from flavoretro import glycoside_library_v5 as v5
        r = v5.load_registry()
        self.assertEqual(r.binding["version"], "task016_p4_v5")
        self.assertEqual(r.binding["chained_v3"]["version"], "task016-p2-qualified-v3")
        self.assertEqual(len(r.v3_registry.templates), 54)
        self.assertEqual(len(r.templates), 55)
        centres = [t["scope"]["center_class"] for t in r.p4_templates]
        self.assertEqual(centres, ["rhamnoside_glucoside_O2"])

    def test_v5_is_not_a_descendant_of_v4(self):
        """v5 must rebuild from v3, not inherit v4 and then mark two scopes invalid."""
        from flavoretro import glycoside_library_v5 as v5
        m = json.loads((root() / "outputs/task016-p4/v1/template_source_manifest.json").read_text())
        self.assertTrue(m["inheritance"]["not_a_descendant_of_v4"])
        r = v5.load_registry()
        for t in r.p4_templates:
            self.assertEqual(t["scope"].get("namespace"), "task016_p3")
            self.assertEqual(t["scope"]["center_class"], "rhamnoside_glucoside_O2")

    def test_quarantined_scopes_absent_from_v5(self):
        from flavoretro import glycoside_library_v5 as v5
        r = v5.load_registry()
        present = {t["scope"]["center_class"] for t in r.p4_templates}
        for centre in ("C_hydroxyflavanone_C3", "rhamnoside_glucoside_O6"):
            self.assertNotIn(centre, present)
            self.assertFalse(v5.P3_SCOPE_CORRECTION[centre]["enters_v5"])
        self.assertTrue(v5.P3_SCOPE_CORRECTION["rhamnoside_glucoside_O2"]["enters_v5"])

    def test_v3_and_v4_still_loadable(self):
        from flavoretro import glycoside_library_v3 as v3, glycoside_library_v4 as v4
        self.assertEqual(len(v3.load_registry().templates), 54)
        self.assertEqual(len(v4.load_registry().templates), 57)

    def test_runtime_holds_no_holdout_instance(self):
        m = json.loads((root() / "outputs/task016-p4/v1/template_source_manifest.json").read_text())
        self.assertFalse(m["holdout_in_runtime"])
        for r in rows("outputs/task016-p4/v1/runtime_instances.jsonl"):
            self.assertEqual(r["template_role"], "development_build")
            self.assertNotIn(r["reaction_id"], {p["reaction_id"] for p in
                                                rows("outputs/task016-p4/v1/heldout_references.jsonl")})


class P4CorrectionLedger(unittest.TestCase):
    def test_reaudit_covers_all_34(self):
        r = rows("outputs/task016-p4/v1/p3_reaudit.jsonl")
        self.assertEqual(len(r), 34)
        self.assertEqual({x["reaction_id"] for x in r},
                         {x["reaction_id"] for x in rows("outputs/task016-p3/v1/reaction_records.jsonl")})

    def test_reaudit_levels_are_from_the_frozen_vocabulary(self):
        allowed = {"structure_complete_admitted", "identity_complete_structure_deferred",
                   "provisional_inferred", "rejected"}
        for x in rows("outputs/task016-p4/v1/p3_reaudit.jsonl"):
            self.assertIn(x["p4_status"], allowed)

    def test_no_agent_review_is_claimed_as_human(self):
        for name in ("p3_reaudit.jsonl", "corrected_reaction_records.jsonl",
                     "heldout_references.jsonl", "p4_new_reaction_records.jsonl"):
            for x in rows("outputs/task016-p4/v1/" + name):
                self.assertFalse(x.get("human_reviewed", False))

    def test_scope_counting_uses_canonical_acceptor(self):
        s = json.loads((root() / "outputs/task016-p4/v1/scope_decisions.json").read_text())
        self.assertEqual(s["counting_key"], "canonical_acceptor_signature")
        self.assertEqual(s["v5_increment_scopes"], ["rhamnoside_glucoside_O2"])
        self.assertEqual(sorted(s["quarantined_scopes"]),
                         ["C_hydroxyflavanone_C3", "rhamnoside_glucoside_O6"])

    def test_o6_scope_is_one_distinct_acceptor_not_two(self):
        s = json.loads((root() / "outputs/task016-p4/v1/scope_decisions.json").read_text())
        o6 = s["scopes"]["rhamnoside_glucoside_O6"]
        self.assertEqual(o6["p3_support_contexts"], 2)
        self.assertEqual(len(o6["p3_sources"]), 2)
        self.assertEqual(o6["distinct_canonical_acceptor"], 1)
        self.assertFalse(o6["gates"]["min_distinct_canonical_acceptor"]["pass"])

    def test_deferred_never_enters_the_holdout_denominator(self):
        m = json.loads((root() / "outputs/task016-p4/v1/panel_manifest.json").read_text())
        self.assertEqual(m["deferred_counted_in_denominator"], 0)
        for cls in m["gates"].values():
            self.assertEqual(cls["deferred_in_denominator"], 0)
        complete = {x["reaction_id"] for x in rows("outputs/task016-p4/v1/p3_reaudit.jsonl")
                    if x["countable_as_structure_complete"]}
        for h in rows("outputs/task016-p4/v1/heldout_references.jsonl"):
            self.assertEqual(h["structure_encoding"], "complete")
            if h["reaction_id"].startswith("P3R-"):
                self.assertIn(h["reaction_id"], complete)

    def test_c3_intermediate_no_longer_borrows_dehydrated_product_nmr(self):
        by = {x["reaction_id"]: x for x in rows("outputs/task016-p4/v1/p3_reaudit.jsonl")}
        for rid in ("P3R-C01", "P3R-C02"):
            self.assertEqual(by[rid]["p4_status"], "identity_complete_structure_deferred")
            self.assertFalse(by[rid]["countable_as_structure_complete"])
            self.assertIn("T4", by[rid]["failed_tests"])

    def test_p3_evidence_files_are_not_rewritten(self):
        import hashlib
        expected = {
            "outputs/task016-p3/v1/reaction_records.jsonl":
                "8832db218293c41845c8b3ba7457fcf929f7227e28a6d984ef28fde5bd7ff504",
            "outputs/task016-p3/v1/heldout_references.jsonl":
                "52b88e9613859ec0172d15342d384d66c876ffd5255ecbe39525f3abfba11b26",
            "outputs/task016-p3/v1/templates.jsonl":
                "48775ffe5e422caf7d21016c84940c3ea3120c33eddba14a511827e1cf7a180c",
        }
        for rel, want in expected.items():
            got = hashlib.sha256((root() / rel).read_bytes()).hexdigest()
            self.assertEqual(got, want, rel)


if __name__ == "__main__":
    unittest.main()
