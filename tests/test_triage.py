import unittest
from copy import deepcopy
from rdkit import Chem
from flavoretro.triage import Screener, load_rules, source_keys, leakage_groups, select_samples

F = "O=c1cc(-c2ccccc2)oc2ccccc12"
O = "O=c1cc(-c2ccc(OC3OC(CO)C(O)C(O)C3O)cc2)oc2ccccc12"
C = "O=c1cc(-c2ccc(C3OC(CO)C(O)C(O)C3O)cc2)oc2ccccc12"


def row(identity, left, right, title="", kind="scifinder_reaction"):
    return {"id": identity, "kind": kind, "source_path": "source", "raw": {"fields": {"RXN:VAR(1):REFERENCE(1):TITLE": title}},
            "components": [{"role": role, "structure": {"canonical_smiles": smiles, "status": "parsed" if Chem.MolFromSmiles(smiles) else "parse_failure"}}
                           for role, values in (("reactant", left), ("product", right)) for smiles in values]}


class TriageContracts(unittest.TestCase):
    def setUp(self):
        self.rules, _ = load_rules()
        self.screen = Screener(self.rules)

    def test_scaffold_queries_are_explicit_candidates(self):
        for key, item in self.rules["scaffolds"].items():
            self.assertIn(key, self.screen.molecule(item["query_smiles"])["scaffolds"])
        self.assertEqual(self.screen.molecule("CCO")["scaffolds"], [])
        self.assertEqual(self.rules["status"], "engineering_frozen_provisional_chemistry")

    def test_aurone_carbonyl_position_control(self):
        self.assertIn("aurone", self.screen.molecule("O=C1C(=Cc2ccccc2)Oc2ccccc21")["scaffolds"])
        self.assertNotIn("aurone", self.screen.molecule("O=C1OC(=Cc2ccccc2)c2ccccc21")["scaffolds"])

    def test_o_and_c_domain_glycosides_separated(self):
        for smiles, family in ((O, "aryl_O_candidate"), (C, "aryl_C_candidate")):
            result = self.screen.reaction(row("a", [F], [smiles]))
            self.assertTrue(result["domain_glycoside_candidate"])
            self.assertIn(family, result["product_domain_sites"])
            self.assertEqual(result["reaction_center_status"], "not_inferred")

    def test_unrelated_glycoside_and_disconnected_mixture_are_controls(self):
        phenol_glycoside = "Oc1ccc(OC2OC(CO)C(O)C(O)C2O)cc1"
        negative = self.screen.reaction(row("a", ["Oc1ccccc1"], [phenol_glycoside]))
        self.assertFalse(negative["domain_structure_candidate"])
        self.assertFalse(negative["domain_glycoside_candidate"])
        mixed = self.screen.reaction(row("b", [F], [F + "." + phenol_glycoside]))
        self.assertTrue(mixed["domain_structure_candidate"])
        self.assertFalse(mixed["domain_glycoside_candidate"])

    def test_failed_component_preserves_valid_side_and_cannot_be_guide_signature(self):
        result = self.screen.reaction(row("bad", ["bad"], [F]))
        self.assertEqual(result["status"], "partial_or_invalid")
        self.assertTrue(result["domain_structure_candidate"])
        self.assertIsNone(result["normalized_reaction"])
        self.assertIsNone(result["guide_signature"])
        self.assertTrue(result["invalid_components"])

    def test_identity_order_salt_map_labels_and_stereo(self):
        a = row("a", ["[CH3:1][OH:2]", "[Na+]"], ["C[C@H](O)F"])
        b = row("b", ["[Na+].OC"], ["C[C@H](O)F"])
        self.assertEqual(self.screen.identity(a), self.screen.identity(b))
        c = row("c", ["CO", "[Na+]"], ["C[C@@H](O)F"])
        self.assertNotEqual(self.screen.identity(a), self.screen.identity(c))
        self.assertNotEqual(self.screen.identity(row("x", ["CCO"], ["CCO"])),
                            self.screen.identity(row("y", ["CCO", "CCO"], ["CCO"])))

    def test_no_change_does_not_become_a_modification_label(self):
        result = self.screen.reaction(row("a", [F], [F]))
        self.assertNotIn("substituent_modification", result["structural_categories"])
        self.assertIn("other_related", result["structural_categories"])

    def test_document_and_exact_reaction_edges_are_transitive(self):
        rows = [row("a", ["CO"], ["CCO"], "A paper"), row("b", ["CC"], ["CCC"], "A paper"),
                row("c", ["CC"], ["CCC"], "A different source"), row("d", ["C"], ["CC"])]
        features = {r["id"]: self.screen.reaction(r) for r in rows}
        groups = leakage_groups(rows, features)
        self.assertEqual(sorted(sorted(g["record_ids"]) for g in groups), [["a", "b", "c"], ["d"]])
        self.assertTrue(all(g["split"] == "development_exposed" for g in groups))
        self.assertEqual(source_keys(rows[-1]), ["unresolved:d"])

    def test_historical_variants_remain_in_one_leakage_group(self):
        a, b = row("a", [F], [O], kind="note_reaction"), row("b", [F], [C], kind="note_reaction")
        a["upstream_sources"], b["upstream_sources"] = ["note-a"], ["note-b"]
        for r in (a, b): r["raw"]["curation"] = {"parent_reaction_id": "LIT_1"}
        groups = leakage_groups([a, b], {r["id"]: self.screen.reaction(r) for r in (a, b)})
        self.assertEqual(len(groups), 1)

    def test_quota_sample_retains_unknown_failures_and_exact_uniqueness(self):
        rules = deepcopy(self.rules)
        rules["sampling_quotas"] = {k: 1 for k in rules["sampling_quotas"]}
        pilot = []
        for index, stratum in enumerate(rules["sampling_quotas"]):
            glyco = stratum.startswith("glycoside")
            valid = stratum != "invalid_or_partial"
            domain = stratum != "low_or_unknown"
            guided = stratum in {"glycoside_guide", "domain_guide"}
            item = {"id": str(index), "guide_supported": guided, "features": {"status": "parsed" if valid else "partial_or_invalid",
                    "domain_glycoside_candidate": glyco, "domain_structure_candidate": domain, "exact_group": str(index)}}
            pilot.extend([item, {**deepcopy(item), "id": "duplicate-" + str(index)}])
        selected, coverage = select_samples(pilot, rules)
        self.assertEqual(len(selected), 6)
        self.assertEqual(len({r["features"]["exact_group"] for _, r in selected}), 6)
        self.assertEqual({k for k, _ in selected}, set(rules["sampling_quotas"]))
        self.assertTrue(all(v["shortfall"] == 0 for v in coverage.values()))
        self.assertEqual(selected, select_samples(pilot[::-1], rules)[0])

    def test_build_rejects_existing_output_without_writing(self):
        import tempfile
        from pathlib import Path
        from flavoretro.triage import build
        with tempfile.TemporaryDirectory() as directory:
            sentinel = Path(directory) / "sentinel"; sentinel.write_text("original")
            with self.assertRaisesRegex(ValueError, "exists"):
                build(directory)
            self.assertEqual(sentinel.read_text(), "original")


if __name__ == "__main__":
    unittest.main()
