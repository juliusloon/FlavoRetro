import tempfile,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from rdkit import Chem
from aizynthfinder.chem import Molecule
from aizynthfinder.context.stock import Stock
from aizynthfinder.context.stock.queries import InMemoryInchiKeyQuery
from flavoretro.stock_identity import install
class StockIdentity(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
 def stock(self,smiles):
  p=Path(self.temp.name)/'keys.txt';p.write_text('\n'.join(Chem.MolToInchiKey(Chem.MolFromSmiles(s)) for s in smiles)+'\n')
  raw=Stock();raw.load(InMemoryInchiKeyQuery(str(p)),'fixture');raw.select('fixture')
  finder=NS(stock=raw,config=NS(stock=raw));strict=install(finder)
  self.assertIs(finder.stock,finder.config.stock);self.assertIs(raw['fixture'],strict['fixture']);return strict
 def test_unspecified_stock_does_not_certify_E_or_Z(self):
  s=self.stock(['CC=CC'])
  self.assertIn(Molecule(smiles='CC=CC'),s)
  self.assertNotIn(Molecule(smiles='C/C=C/C'),s);self.assertNotIn(Molecule(smiles='C/C=C\\C'),s)
 def test_full_E_key_and_exclusion_do_not_remove_Z(self):
  s=self.stock(['C/C=C/C','C/C=C\\C'])
  e=Molecule(smiles='C/C=C/C');z=Molecule(smiles='C/C=C\\C')
  self.assertIn(e,s);self.assertIn(z,s);s.exclude(e);self.assertNotIn(e,s);self.assertIn(z,s)
  self.assertEqual(s.availability_list(z),['fixture'])
 def test_tetrahedral_enantiomers_remain_distinct_and_off_stock_unknown(self):
  s=self.stock(['N[C@H](C)O'])
  self.assertIn(Molecule(smiles='N[C@H](C)O'),s);self.assertNotIn(Molecule(smiles='N[C@@H](C)O'),s);self.assertNotIn(Molecule(smiles='CCO'),s)
 def test_existing_criteria_and_selection_preserved(self):
  s=self.stock(['CCCC']);s.set_stop_criteria({'weight':20});self.assertNotIn(Molecule(smiles='CCCC'),s)
  self.assertEqual(s.selection,['fixture']);self.assertEqual(s.stop_criteria['weight'],20)
if __name__=='__main__':unittest.main()
