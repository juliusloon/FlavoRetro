"""Corrected source-library boundary checks; no MCTS or chemical validation."""
import copy
import json
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from rdkit import Chem
from aizynthfinder.chem import TreeMolecule
from aizynthfinder.context.config import Configuration
from aizynthfinder.utils.exceptions import RejectionException
from flavoretro import glycoside_library_v8 as v8
from flavoretro import glycoside_library_v6 as v6
from flavoretro.resources import sha
from flavoretro.reviewed_resources import canonical_side
from flavoretro.workspace import root, AssetError
from scripts import operate

OUT = root() / "outputs/task022/glycoside-v8"
MANIFEST = OUT / "template_source_manifest.json"
ASSETS = MANIFEST.is_file()


def extension_positions(smiles):
    """Number glycan carbons from the aryl O-linked C1, independent of names."""
    mol = Chem.MolFromSmiles(smiles)
    rings = [set(r) for r in mol.GetRingInfo().AtomRings() if len(r) == 6
             and sum(mol.GetAtomWithIdx(i).GetAtomicNum() == 8 for i in r) == 1
             and all(mol.GetAtomWithIdx(i).GetAtomicNum() in (6, 8)
                     and not mol.GetAtomWithIdx(i).GetIsAromatic() for i in r)]
    positions = []
    for ring in rings:
        oxygen = next(i for i in ring if mol.GetAtomWithIdx(i).GetAtomicNum() == 8)
        for c1 in mol.GetAtomWithIdx(oxygen).GetNeighbors():
            if c1.GetIdx() not in ring or not any(n.GetAtomicNum() == 8 and n.GetIdx() not in ring
                    and any(a.GetIsAromatic() for a in n.GetNeighbors()) for n in c1.GetNeighbors()):
                continue
            path = [c1.GetIdx()]; previous = oxygen
            for _ in range(4):
                nxt = next(n.GetIdx() for n in mol.GetAtomWithIdx(path[-1]).GetNeighbors()
                           if n.GetIdx() in ring and n.GetIdx() != previous and n.GetIdx() != oxygen)
                previous = path[-1]; path.append(nxt)
            for position, atom in enumerate(path, 1):
                for bridge in mol.GetAtomWithIdx(atom).GetNeighbors():
                    if bridge.GetAtomicNum() == 8 and bridge.GetIdx() not in ring and any(
                            n.GetIdx() != atom and any(n.GetIdx() in other for other in rings if other != ring)
                            for n in bridge.GetNeighbors()):
                        positions.append(position)
    return positions


@unittest.skipUnless(ASSETS, "local corrected v8 source payload required")
class CorrectedLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = json.loads((root() / "configs/glycoside-library-v8.json").read_text())
        cls.registry = v8.Registry(MANIFEST, cls.settings["manifest_sha256"])
        cls.corrected = [t for t in cls.registry.templates if t["template_id"].startswith("v8-exact:")]
        cls.quarantine = json.loads((OUT / "quarantine.json").read_text())

    def test_config_is_default_off_and_packaged_bytes_match(self):
        self.assertFalse(self.settings["default_enabled"])
        self.assertEqual({k:self.settings[k] for k in v8.POLICY}, v8.POLICY)
        self.assertEqual((root() / "configs/glycoside-library-v8.json").read_bytes(),
                         (root() / "flavoretro/assets/configs/glycoside-library-v8.json").read_bytes())

    def test_quarantined_records_are_preserved_but_not_runtime_support(self):
        self.assertEqual(set(r["instance_id"] for r in self.quarantine["instances"]), v8.QUARANTINED_INSTANCES)
        self.assertFalse(v8.QUARANTINED_INSTANCES.intersection(self.registry.instances))
        self.assertFalse(v8.QUARANTINED_TEMPLATES.intersection(self.registry.by_id))
        self.assertFalse(v8.QUARANTINED_INSTANCES.intersection(i for t in self.registry.templates for i in t["support_instances"]))
        self.assertEqual((len(self.registry.templates), len(self.registry.instances)), (54, 86))

    def test_all_132_source_support_pairs_replay(self):
        checks = 0
        for t in self.registry.templates:
            for i in t["support_instances"]:
                r = self.registry.instances[i]
                self.assertIn(canonical_side(r["reference_precursors"]), [o["precursors"] for o in v8.apply_template(t, r["target"])])
                checks += 1
        self.assertEqual(checks, 132)

    def test_gu_scope_has_ten_supports_and_eight_distinct_acceptors(self):
        t = self.registry.by_id["p1-scope:ab57f3c00a24cc6fe5ea"]
        self.assertEqual(len(t["support_instances"]), 10)
        self.assertEqual(len({canonical_side([self.registry.instances[i]["acceptor"]]) for i in t["support_instances"]}), 8)
        for scope in self.registry.templates:
            if scope["template_role"] == "scope_template":
                self.assertGreaterEqual(len({canonical_side([self.registry.instances[i]["acceptor"]]) for i in scope["support_instances"]}), 2)

    def test_new_exact_graphs_are_o2_and_old_graphs_are_o3(self):
        old = {r["instance_id"]:r for r in self.quarantine["instances"]}
        self.assertEqual(len(self.corrected), 2)
        for t in self.corrected:
            r = self.registry.instances[t["support_instances"][0]]
            self.assertEqual(extension_positions(r["target"]), [2])
            previous = old[r["correction"]["supersedes_instance_id"]]
            self.assertEqual(extension_positions(previous["target"]), [3])
            self.assertFalse(v8.apply_template(t, previous["target"]))
        self.assertFalse(any(t.get("scope", {}).get("center_class") == "rhamnoside_glucoside_O2" for t in self.registry.templates))

    def test_exact_templates_do_not_cross_match(self):
        for t in self.corrected:
            other = next(x for x in self.corrected if x is not t)
            self.assertFalse(v8.apply_template(t, other["allowed_targets"][0]))

    def test_context_stereochemistry_and_non_glycoside_controls(self):
        for t in self.corrected:
            r = self.registry.instances[t["support_instances"][0]]
            self.assertFalse(v8.apply_template(t, r["target"], dict(mode="chemical")))
            self.assertFalse(v8.apply_template(t, r["target"], dict(mode="enzymatic", donor_name="UDP-glucose")))
            self.assertFalse(v8.apply_template(t, r["acceptor"]))
            self.assertFalse(v8.apply_template(t, "O=C1CC(c2ccccc2)Oc2ccccc21"))
            mol = Chem.MolFromSmiles(r["target"])
            center = next(a for a in mol.GetAtoms() if a.GetChiralTag() != Chem.ChiralType.CHI_UNSPECIFIED)
            center.InvertChirality()
            self.assertFalse(v8.apply_template(t, Chem.MolToSmiles(mol, True)))
            center.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
            self.assertFalse(v8.apply_template(t, Chem.MolToSmiles(mol, True)))

    def test_corrected_evidence_has_source_boundary_and_conversion(self):
        for t in self.corrected:
            r = self.registry.instances[t["support_instances"][0]]
            self.assertFalse(r["correction"]["enzyme_alias"])
            self.assertEqual(r["actual_assay_group"], "PMC13084081:Cm1,2RhaT")
            self.assertFalse(r["source_conversion"]["isolated_yield"])
            self.assertFalse(r["human_reviewed"])
            self.assertFalse(r["independent_chemical_validation"])
            self.assertFalse(r["exact_formal_reference_ready"])
            for source in r["source_bindings"]:
                self.assertEqual(sha(root() / source["path"]), source["sha256"])

    def test_real_action_evidence_and_metadata_tamper(self):
        t = self.corrected[0]
        strategy = v8.GlycosideExpansion("glycoside", Configuration(), domain_binding=self.registry.binding)
        actions, priors = strategy.get_actions([TreeMolecule(parent=None, smiles=t["allowed_targets"][0])])
        action = next(a for a in actions if a.metadata["template_id"] == t["template_id"])
        evidence = self.registry.evidence(action)
        self.assertEqual(evidence["namespace"], v8.NAMESPACE)
        self.assertTrue(evidence["exact_seed_instance_match"])
        self.assertFalse(evidence["prediction_conditions_verified"])
        self.assertTrue(evidence["normalized_gt_reference_only"])
        self.assertTrue(all(p == 0.2 for p in priors))
        self.assertLessEqual(len(actions), 4)
        action.metadata["required_context"] = dict(mode="chemical")
        with self.assertRaises(RejectionException):
            self.registry.evidence(action)

    def test_manifest_hash_drift_fails_closed(self):
        with self.assertRaisesRegex(AssetError, "manifest"):
            v8.Registry(MANIFEST, "wrong")

    def test_payload_and_source_hash_drift_fail_closed(self):
        manifest = json.loads(MANIFEST.read_text())
        for target, error in ((OUT / "templates.jsonl", "payload"),
                              (root() / next(iter(manifest["raw_dependencies_sha256"])), "source")):
            with patch.object(v8, "sha", side_effect=lambda p: "wrong" if Path(p) == target.resolve() else sha(p)):
                with self.assertRaisesRegex(AssetError, error):
                    v8.Registry(MANIFEST, self.settings["manifest_sha256"])

    @contextmanager
    def mutated_payload(self, mutate):
        manifest = json.loads(MANIFEST.read_text())
        templates = copy.deepcopy(self.registry.templates)
        rows = copy.deepcopy(list(self.registry.instances.values()))
        mutate(templates, rows, manifest)
        with tempfile.TemporaryDirectory(prefix="test-v8-", dir=OUT) as directory:
            base = Path(directory)
            for filename in manifest["files_sha256"]:
                data = (OUT / filename).read_text()
                if filename == "templates.jsonl":
                    data = "".join(json.dumps(t) + "\n" for t in templates)
                elif filename == "runtime_instances.jsonl":
                    data = "".join(json.dumps(r) + "\n" for r in rows)
                operate.write("TASK-022", str((base / filename).relative_to(root())), data)
                manifest["files_sha256"][filename] = sha(base / filename)
            manifest["counts"] = dict(templates=len(templates), instances=len(rows))
            mp = base / "template_source_manifest.json"
            operate.write("TASK-022", str(mp.relative_to(root())), json.dumps(manifest))
            yield mp, sha(mp)

    def test_rebound_quarantined_support_is_rejected(self):
        def mutate(templates, rows, manifest):
            rows.append(copy.deepcopy(self.quarantine["instances"][0]))
        with self.mutated_payload(mutate) as args:
            with self.assertRaisesRegex(AssetError, "quarantined"):
                v8.Registry(*args)

    def test_single_acceptor_scope_is_rejected(self):
        def mutate(templates, rows, manifest):
            t = next(t for t in templates if t["template_role"] == "scope_template")
            t["support_instances"] = t["support_instances"][:1]
        with self.mutated_payload(mutate) as args:
            with self.assertRaisesRegex(AssetError, "two distinct"):
                v8.Registry(*args)

    def test_unbound_exact_target_and_holdout_support_are_rejected(self):
        def target_mutation(templates, rows, manifest):
            next(t for t in templates if t["template_role"] == "exact_instance_template")["allowed_targets"].append("CCO")
        def holdout_mutation(templates, rows, manifest):
            rows[0]["template_role"] = "holdout"
        for mutate, error in ((target_mutation, "exact target"), (holdout_mutation, "holdout")):
            with self.mutated_payload(mutate) as args:
                with self.assertRaisesRegex(AssetError, error):
                    v8.Registry(*args)

    def test_load_registry_with_frozen_binding_needs_no_shared_config(self):
        with patch.object(v8, "config", side_effect=AssertionError("shared config consulted")):
            self.assertEqual(v8.load_registry(self.registry.binding).binding, self.registry.binding)
            with self.assertRaisesRegex(AssetError, "binding changed"):
                v8.load_registry(dict(self.registry.binding, version="wrong"))

    def test_frozen_binding_cannot_escape_workspace_or_omit_hash(self):
        for value in (dict(self.registry.binding, manifest="../outside.json"),
                      dict(self.registry.binding, manifest=str(MANIFEST)),
                      {"version": "wrong"}):
            with self.assertRaises(AssetError):
                v8.load_registry(value)
        with self.assertRaisesRegex(AssetError, "hash drift"):
            v8.load_registry(dict(self.registry.binding, manifest_sha256="wrong"))

    def test_default_loader_uses_shared_config(self):
        with patch.object(v8, "config", return_value=self.settings) as config:
            self.assertEqual(v8.load_registry().binding, self.registry.binding)
        config.assert_called_once_with("glycoside-library-v8.json")

    def test_legacy_v6_payload_stays_unchanged(self):
        legacy = v6.load_registry()
        self.assertEqual((len(legacy.templates), len(legacy.instances)), (56, 89))
        self.assertEqual(json.loads((OUT / "protected_before.json").read_text()),
                         json.loads((OUT / "protected_after.json").read_text()))
        for path, digest in json.loads((OUT / "protected_before.json").read_text()).items():
            if path.startswith("outputs/task016") or "glycoside-library-v6" in path or path.endswith("glycoside_library_v6.py"):
                self.assertEqual(sha(root() / path), digest)


if __name__ == "__main__":
    unittest.main()
