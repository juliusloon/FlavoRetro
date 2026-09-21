import unittest
from rdkit import Chem
from flavoretro.topology import audit

O = "Oc1ccc(OC2OC(CO)C(O)C(O)C2O)cc1"
C = "Oc1ccc(C2OC(CO)C(O)C(O)C2O)cc1"


class TopologyContracts(unittest.TestCase):
    def test_ordinary_ether_is_negative(self):
        self.assertEqual(audit("COc1ccccc1")["sites"], [])

    def test_o_c_separated(self):
        self.assertEqual([s["family"] for s in audit(O)["sites"]], ["aryl_O_candidate"])
        self.assertEqual([s["family"] for s in audit(C)["sites"]], ["aryl_C_candidate"])

    def test_roundtrip_and_reordering(self):
        mol = Chem.MolFromSmiles(O)
        reference = sorted(s["family"] for s in audit(O)["sites"])
        for seed in range(10):
            order = (
                list(range(mol.GetNumAtoms()))[seed:]
                + list(range(mol.GetNumAtoms()))[:seed]
            )
            result = audit(
                Chem.MolToSmiles(Chem.RenumberAtoms(mol, order), canonical=False)
            )
            self.assertEqual(sorted(s["family"] for s in result["sites"]), reference)
            self.assertTrue(all(s["graph_roundtrip"] for s in result["sites"]))

    def test_absolute_stereo_survives_neighbor_reordering(self):
        result = audit("COc1ccc(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)cc1")
        self.assertTrue(result["sites"])
        self.assertTrue(all(s["graph_roundtrip"] for s in result["sites"]))

    def test_free_sugar_not_glycosidic_connection(self):
        self.assertEqual(audit("OC1OC(CO)C(O)C(O)C1O")["sites"], [])

    def test_invalid_not_silently_deleted(self):
        self.assertEqual(audit("bad")["status"], "parse_failure")
