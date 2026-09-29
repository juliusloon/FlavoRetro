"""TASK-015-P4 contracts: v2 dispositions never fake coverage and never demote gold."""
import unittest
from copy import deepcopy
from rdkit import Chem, RDLogger
from flavoretro.triage import (
    Screener, load_rules, source_blacklist_hits, pathway_compression_suspect, v2_disposition)

RDLogger.DisableLog("rdApp.*")
F = "O=c1cc(-c2ccccc2)oc2ccccc12"
GLY = "O=c1cc(-c2ccc(O)cc2)oc2c([C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)cc(O)c12"
GLY2 = "O=c1cc(-c2ccc(O)cc2)oc2cc(O)c([C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)c12"
TYR = "N[C@@H](Cc1ccc(O)cc1)C(=O)O"


def cite_row(text):
    return {"id": "x", "kind": "scifinder_reaction", "raw": {"fields": {"RXN:VAR(1):REFERENCE(1):CITATION": text}},
            "components": []}


def comp_row(reactants, products, parse_fail=False):
    comps = [{"role": "reactant", "structure": {"status": "parsed", "canonical_smiles": s}} for s in reactants]
    comps += [{"role": "product", "structure": {"status": "parse_failure" if parse_fail else "parsed",
                                                "canonical_smiles": s if not parse_fail else ""}} for s in products]
    return {"id": "x", "kind": "scifinder_reaction", "raw": {"fields": {}}, "components": comps}


class V2RuleLoading(unittest.TestCase):
    def test_v1_and_v2_both_load(self):
        v1, _ = load_rules("configs/domain_triage.json")
        v2, _ = load_rules("configs/domain_triage-v2.json")
        self.assertEqual(v1["protocol_version"], "task014-v1")
        self.assertEqual(v2["protocol_version"], "task015-p4-v2")

    def test_unknown_version_rejected(self):
        bad = deepcopy(load_rules("configs/domain_triage-v2.json")[0])
        bad["protocol_version"] = "task999-v9"
        import json, tempfile, os
        from pathlib import Path
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(json.dumps(bad)); tmp = fh.name
        try:
            with self.assertRaises(ValueError):
                load_rules(tmp)
        finally:
            os.unlink(tmp)

    def test_v2_requires_calibration_fields(self):
        bad = deepcopy(load_rules("configs/domain_triage-v2.json")[0])
        del bad["source_blacklist"]
        import json, tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(json.dumps(bad)); tmp = fh.name
        try:
            with self.assertRaisesRegex(ValueError, "source_blacklist"):
                load_rules(tmp)
        finally:
            os.unlink(tmp)

    def test_blacklist_entry_needs_verifiable_identity(self):
        bad = deepcopy(load_rules("configs/domain_triage-v2.json")[0])
        bad["source_blacklist"] = [{"journal": "Some Journal"}]
        import json, tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(json.dumps(bad)); tmp = fh.name
        try:
            with self.assertRaisesRegex(ValueError, "verifiable identity"):
                load_rules(tmp)
        finally:
            os.unlink(tmp)


class BlacklistMatching(unittest.TestCase):
    def setUp(self):
        self.v2 = load_rules("configs/domain_triage-v2.json")[0]
        self.v1 = load_rules("configs/domain_triage.json")[0]

    def cases(self):
        return [("Research on Chemical Intermediates (2024), 50(7), 3079-3108", True),
                ("Research on Chemical Intermediates (2020), 46(1), 1-9", False),
                ("Some Journal (2019), 3, 22. DOI: 10.1007/s11164-024-05300-x", True),
                ("Research on Chemical Intermediates (2024), 50(8), 3079-3108", False),
                ("Res. Chem. Intermed. 2024, 50, 3079-3108.", True),
                ("Res. Chem. Intermed. 2019, 29, 3079-3108.", False),
                ("Nature (2024), 50(7), 3079-3108", False)]

    def test_match_semantics(self):
        for text, want in self.cases():
            got = bool(source_blacklist_hits(cite_row(text), self.v2))
            self.assertEqual(got, want, text)

    def test_v1_rules_have_no_blacklist(self):
        self.assertEqual(source_blacklist_hits(cite_row("Research on Chemical Intermediates (2024), 50(7), 3079-3108"), self.v1), [])


class PathwayCompression(unittest.TestCase):
    def setUp(self):
        self.v2 = load_rules("configs/domain_triage-v2.json")[0]
        self.screen = Screener(self.v2)

    def features(self, row):
        return self.screen.reaction(row)

    def test_tyrosine_to_two_glycosides_is_suspect(self):
        row = comp_row([TYR], [GLY, GLY2])
        self.assertTrue(pathway_compression_suspect(row, self.features(row), self.screen, self.v2))

    def test_single_product_not_suspect(self):
        row = comp_row([TYR], [GLY])
        self.assertFalse(pathway_compression_suspect(row, self.features(row), self.screen, self.v2))

    def test_domain_reactant_not_suspect(self):
        row = comp_row([F], [GLY, GLY2])
        self.assertFalse(pathway_compression_suspect(row, self.features(row), self.screen, self.v2))

    def test_partial_record_never_flagged(self):
        row = comp_row([TYR], [GLY, GLY2], parse_fail=True)
        self.assertFalse(pathway_compression_suspect(row, self.features(row), self.screen, self.v2))

    def test_duplicate_product_molecules_count_once(self):
        row = comp_row([TYR], [GLY, GLY])
        self.assertFalse(pathway_compression_suspect(row, self.features(row), self.screen, self.v2))


class DispositionPrecedence(unittest.TestCase):
    def setUp(self):
        self.v2 = load_rules("configs/domain_triage-v2.json")[0]
        self.screen = Screener(self.v2)

    def test_blocklist_beats_incomplete(self):
        row = cite_row("Research on Chemical Intermediates (2024), 50(7), 3079-3108")
        row["components"] = comp_row([], [GLY], parse_fail=True)["components"]
        features = {"status": "partial_or_invalid"}
        d = v2_disposition(row, features, self.screen, self.v2)
        self.assertEqual(d["queue"], "blocked_source_blacklist")

    def test_incomplete_beats_pathway(self):
        row = comp_row([TYR], [GLY, GLY2], parse_fail=True)
        features = self.screen.reaction(row)
        d = v2_disposition(row, features, self.screen, self.v2)
        self.assertEqual(d["queue"], "incomplete_record")

    def test_clean_record_has_no_override(self):
        row = comp_row([F], [GLY])
        features = self.screen.reaction(row)
        self.assertIsNone(v2_disposition(row, features, self.screen, self.v2))

    def test_v1_rules_return_none(self):
        v1 = load_rules("configs/domain_triage.json")[0]
        row = comp_row([TYR], [GLY, GLY2])
        self.assertIsNone(v2_disposition(row, self.screen.reaction(row), self.screen, v1))


if __name__ == "__main__":
    unittest.main()
