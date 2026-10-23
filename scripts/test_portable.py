"""Run all engineering tests, reporting absent registered local bundles as skips.

No test exceptions are converted to skips. If a bundle exists, its original
assertions run: incomplete, stale or corrupt contents must still fail.
"""
import json
from pathlib import Path, PurePosixPath
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_dependencies(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("groups"), list):
        raise ValueError("invalid local-asset manifest schema")
    dependencies = {}
    for group in data["groups"]:
        tests, required, reason = (group.get(k) for k in ("tests", "requires", "reason"))
        if not tests or not required or not isinstance(reason, str) or not reason.strip():
            raise ValueError("each dependency group needs tests, bundles and a reason")
        if not isinstance(tests, list) or not isinstance(required, list):
            raise ValueError("tests and requires must be lists")
        for value in required:
            if not isinstance(value, str):
                raise ValueError("bundle path must be a string")
            rel = PurePosixPath(value)
            if rel.is_absolute() or ".." in rel.parts or len(rel.parts) < 2 or rel.parts[0] not in {"data", "outputs"}:
                raise ValueError("bundle must be a relative data/ or outputs/ path")
        for identifier in tests:
            if not isinstance(identifier, str) or len(identifier.split(".")) != 3 or not identifier.split(".")[-1].startswith("test_"):
                raise ValueError("dependency must name an exact discovered test ID")
            if identifier in dependencies:
                raise ValueError("duplicate dependency: " + identifier)
            dependencies[identifier] = (tuple(required), reason)
    return dependencies


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


class MissingLocalBundle(unittest.TestCase):
    def __init__(self, original, reason):
        super().__init__("runTest")
        self.original_id = original.id()
        self.description = str(original)
        self.reason = reason

    def id(self):
        return self.original_id

    def __str__(self):
        return self.description

    def runTest(self):
        self.skipTest(self.reason)


def portable_suite(suite, dependencies, root):
    """Replace only exact registered cases whose local bundle is absent."""
    root = Path(root).resolve()
    identifiers = {case.id() for case in cases(suite)}
    unknown = set(dependencies) - identifiers
    if unknown:
        raise ValueError("registered tests not discovered: " + ", ".join(sorted(unknown)))
    missing = {}
    for identifier, (required, reason) in dependencies.items():
        absent = []
        for rel in required:
            path = (root / rel).resolve()
            if not path.is_relative_to(root):
                raise ValueError("local bundle resolves outside workspace: " + rel)
            if not path.exists():
                absent.append(rel)
        if absent:
            missing[identifier] = "local asset bundle absent: " + ", ".join(absent) + " (" + reason + ")"

    def replace(items):
        result = unittest.TestSuite()
        for item in items:
            if isinstance(item, unittest.TestSuite):
                result.addTest(replace(item))
            elif item.id() in missing:
                result.addTest(MissingLocalBundle(item, missing[item.id()]))
            else:
                result.addTest(item)
        return result

    return replace(suite)


def main():
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    dependencies = load_dependencies(ROOT / "tests/local-assets.json")
    suite = portable_suite(suite, dependencies, ROOT)
    print("Portable suite: exact local-bundle skips are reported; all other tests run.", flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print("Skipped local evidence is not scientific, live-search or browser acceptance.", flush=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
