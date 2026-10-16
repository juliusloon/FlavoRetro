"""TASK-016-P3 contract tests: explicit v4 increment, default-off, chain
integrity, guard boundaries and old-version behaviour preservation."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _root():
    from flavoretro.workspace import root
    return root()


def _v4_manifest():
    return json.loads(
        (_root() / "outputs/task016-p3/v1/template_source_manifest.json").read_text())


def _cfg(name):
    from flavoretro.workspace import config
    return config(name)


class V4Contract(unittest.TestCase):
    def test_v4_config_default_off(self):
        cfg = _cfg("glycoside-library-v4.json")
        self.assertEqual(cfg["version"], 4)
        self.assertFalse(cfg["default_enabled"])

    def test_v4_package_copy_matches_workspace_config(self):
        from flavoretro.resources import sha
        self.assertEqual(sha(_root() / "configs/glycoside-library-v4.json"),
                         sha(_root() / "flavoretro/assets/configs/glycoside-library-v4.json"))

    def test_v4_registry_chain_and_counts(self):
        from flavoretro.glycoside_library_v4 import load_registry
        r = load_registry()
        self.assertEqual(r.binding["version"], "task016-p3-qualified-v4")
        self.assertEqual(len(r.p3_templates), 3)
        self.assertEqual(len(r.templates), len(r.v3_registry.templates) + 3)
        self.assertEqual(len(r.instances), len(r.v3_registry.instances) + 7)
        self.assertTrue(all(t["template_id"].startswith("p3-scope:") for t in r.p3_templates))

    def test_v3_registry_binding_unchanged(self):
        from flavoretro.glycoside_library_v3 import load_registry
        r = load_registry()
        self.assertEqual(r.binding["version"], "task016-p2-qualified-v3")

    def test_v4_support_replay_and_guard(self):
        from flavoretro.glycoside_library_v4 import apply_template, load_registry
        from flavoretro.reviewed_resources import canonical_side
        r = load_registry()
        for t in r.p3_templates:
            for identifier in t["support_instances"]:
                inst = r.p3_instances[identifier]
                outcomes = apply_template(t, inst["target"])
                self.assertTrue(outcomes, f"no replay for {identifier}")
                self.assertIn(canonical_side(inst["reference_precursors"]),
                              [o["precursors"] for o in outcomes])

    def test_v4_boundaries_zero_violation(self):
        checks = _v4_manifest()["boundaries"]
        self.assertEqual(len(checks), 12)
        self.assertTrue(all(not c["violation"] for c in checks))

    def test_v4_scope_generality_beyond_seed(self):
        """The scoped template must also fire on complete receptors outside the
        seed support instances (proving scope, not exact-instance matching)."""
        from flavoretro.glycoside_library_v4 import apply_template, load_registry
        r = load_registry()
        t = next(x for x in r.p3_templates
                 if x["scope"]["center_class"] == "rhamnoside_glucoside_O6")
        inst = r.p3_instances[t["support_instances"][0]]
        self.assertTrue(apply_template(t, inst["target"]))
        # structurally distinct flavanone glucoside outside every support set
        extra = ("O=C1C[C@@H](c2ccc(O)c(OC)c2)Oc2cc(O[C@@H]3O[C@H](CO[C@@H]4O[C@@H](C)"
                 "[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12")
        self.assertTrue(apply_template(t, extra))

    def test_v4_templates_absent_from_v3_registry(self):
        from flavoretro.glycoside_library_v3 import load_registry
        r = load_registry()
        self.assertFalse(any(t["template_id"].startswith("p3-scope:") for t in r.templates))

    def test_old_v2_templates_byte_identical_in_chain(self):
        """P2's frozen template definitions keep their fingerprints in the chain."""
        from flavoretro.glycoside_library_v4 import load_registry
        old = [json.loads(l)
               for l in (_root() / "outputs/task016-p2/v2/templates.jsonl").read_text().splitlines()]
        r = load_registry()
        by_id = {t["template_id"]: t for t in r.templates}
        for t in old:
            self.assertIn(t["template_id"], by_id)
            self.assertEqual(by_id[t["template_id"]]["smarts"], t["smarts"])

    def test_contract_request_rejects_unknown_version(self):
        from flavoretro.contracts import SearchRequest
        with self.assertRaises(Exception):
            SearchRequest(smiles="O=C1CC(c2ccc(O)cc2)Oc2cc(O)cc(O)c12", seed=0,
                          glycoside_expansion=True, glycoside_library_version="v9")


if __name__ == "__main__":
    unittest.main()
