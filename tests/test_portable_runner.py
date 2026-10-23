"""Portable CI policy must never hide undeclared failures or damaged evidence."""
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.test_portable import cases, load_dependencies, portable_suite


class PortableRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def sample(self):
        class Fixture(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise FileNotFoundError("fixture must fail when its bundle exists")

            def test_evidence(self):
                self.fail("original assertion")

        case = Fixture("test_evidence")
        return case, {case.id(): (("outputs/local-bundle",), "local evidence")}

    def run_suite(self, suite):
        return unittest.TextTestRunner(stream=io.StringIO()).run(suite)

    def test_missing_registered_bundle_skips_before_class_fixture_with_same_id(self):
        case, deps = self.sample()
        suite = portable_suite(unittest.TestSuite([case]), deps, self.root)
        self.assertEqual([x.id() for x in cases(suite)], [case.id()])
        result = self.run_suite(suite)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.skipped), 1)
        self.assertIn("outputs/local-bundle", result.skipped[0][1])

    def test_existing_incomplete_bundle_preserves_original_fixture_error(self):
        case, deps = self.sample()
        (self.root / "outputs/local-bundle").mkdir(parents=True)
        suite = portable_suite(unittest.TestSuite([case]), deps, self.root)
        self.assertIs(next(cases(suite)), case)
        result = self.run_suite(suite)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.skipped, [])

    def test_unregistered_file_error_is_not_skipped(self):
        case, _ = self.sample()
        result = self.run_suite(portable_suite(unittest.TestSuite([case]), {}, self.root))
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.skipped, [])

    def test_present_bundle_preserves_assertions_and_nested_suite(self):
        class Assertion(unittest.TestCase):
            def test_assertion(self):
                self.fail("assertion must remain a failure")
        case = Assertion("test_assertion")
        (self.root / "outputs/present").mkdir(parents=True)
        suite = portable_suite(unittest.TestSuite([unittest.TestSuite([case])]),
                               {case.id(): (("outputs/present",), "present")}, self.root)
        result = self.run_suite(suite)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.skipped, [])

    def test_unknown_registration_fails_instead_of_silent_stale_skip(self):
        with self.assertRaisesRegex(ValueError, "not discovered"):
            portable_suite(unittest.TestSuite(), {"test_old.Gone.test_old": (("outputs/old",), "old")}, self.root)

    def manifest(self, tests=None, required=None):
        path = self.root / "local-assets.json"
        path.write_text(json.dumps({"schema_version": 1, "groups": [
            {"tests": tests or ["test_sample.Sample.test_case"],
             "requires": required or ["outputs/local"], "reason": "local evidence"}]}))
        return path

    def test_manifest_rejects_traversal_absolute_and_non_asset_paths(self):
        for rel in ["../outputs/local", "/outputs/local", "outputs/../../secret", "web/app.js"]:
            with self.subTest(rel=rel), self.assertRaises(ValueError):
                load_dependencies(self.manifest(required=[rel]))

    def test_manifest_rejects_duplicate_test_registration(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            load_dependencies(self.manifest(tests=["test_sample.Sample.test_case"] * 2))

    def test_bundle_symlink_cannot_escape_workspace(self):
        case, deps = self.sample()
        (self.root / "outputs").mkdir()
        (self.root / "outputs/local-bundle").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "outside workspace"):
            portable_suite(unittest.TestSuite([case]), deps, self.root)


if __name__ == "__main__":
    unittest.main()
