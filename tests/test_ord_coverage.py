"""Isolated ORD adapter contracts; optional vendored protobufs are local only."""
import importlib.util,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'outputs/validation/task015-dependencies'))
try:
 from scripts import scan_ord as scan
 from ord_schema.proto import reaction_pb2 as pb
except ImportError:
 scan=None

@unittest.skipIf(scan is None,'ORD schema snapshot unavailable; run isolated TASK-015 setup')
class ORDContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):scan.initialize()
 def reaction(self,smiles,idx='fixture'):
  rx=pb.Reaction(reaction_id=idx);rx.identifiers.add(type=pb.ReactionIdentifier.REACTION_SMILES,value=smiles);return rx
 def batch(self,rx):return scan.process((0,0,[{'reaction_id':rx.reaction_id,'reaction':rx.SerializeToString()}]))
 def test_zero_yield_has_presence_and_missing_is_not_zero(self):
  rx=self.reaction('O=c1cc(-c2ccccc2)oc2ccccc12>>O=c1cc(-c2ccccc2)oc2ccccc12')
  p=rx.outcomes.add().products.add();p.measurements.add(type=pb.ProductMeasurement.YIELD).percentage.value=0
  p.measurements.add(type=pb.ProductMeasurement.YIELD).percentage.SetInParent()
  result=self.batch(rx);m=result['candidates'][0]['yield_measurements']
  self.assertEqual([x['value'] for x in m],[0.0,None]);self.assertEqual(result['stats']['candidate_with_zero_yield'],1)
 def test_malformed_and_partial_are_preserved(self):
  rx=self.reaction('CCC>>');self.assertEqual(self.batch(rx)['stats']['unknown'],1)
  rx=self.reaction('O=c1cc(-c2ccccc2)oc2ccccc12>>');result=self.batch(rx)
  self.assertEqual(result['stats']['candidate'],1);self.assertTrue(result['candidates'][0]['issues']['missing_reaction_side'])
  bad=scan.process((0,7,[{'reaction_id':'bad','reaction':b'\xff'}]));self.assertEqual(bad['stats']['protobuf_parse_failure'],1);self.assertEqual(bad['unknown'][0]['row'],7)
 def test_agents_excluded_and_explicit_fallback_role_bound(self):
  rx=self.reaction('CC>O=c1cc(-c2ccccc2)oc2ccccc12>CCC');self.assertEqual(self.batch(rx)['stats']['outside_queries'],1)
  rx=pb.Reaction(reaction_id='fallback');c=rx.inputs['input'].components.add(reaction_role=pb.ReactionRole.REACTANT);c.identifiers.add(type=pb.CompoundIdentifier.SMILES,value='O=c1cc(-c2ccccc2)oc2ccccc12');c=rx.outcomes.add().products.add();c.identifiers.add(type=pb.CompoundIdentifier.SMILES,value='CC')
  result=self.batch(rx);self.assertEqual(result['stats']['candidate'],1);self.assertEqual(result['candidates'][0]['representation'],'explicit_components')
 def test_disconnected_sugar_not_domain_glycoside(self):
  s='O=c1cc(-c2ccccc2)oc2ccccc12.Oc1ccc(OC2OC(CO)C(O)C(O)C2O)cc1'
  result=self.batch(self.reaction(s+'>>'+s));self.assertFalse(result['candidates'][0]['features']['domain_glycoside_candidate'])
 def test_mapping_labels_removed_stereo_is_retained(self):
  rx=self.reaction('[CH3:7]Oc1ccc(-c2cc(=O)c3ccccc3o2)cc1>>COc1ccc(-c2cc(=O)c3ccccc3o2)cc1')
  result=self.batch(rx);r=result['candidates'][0];self.assertNotIn(':7',r['features']['normalized_reaction']);self.assertIn(':7',r['raw_reaction_smiles']);self.assertEqual(r['human_review_status'],'not_performed');self.assertFalse(r['production_eligible'])

if __name__=='__main__':unittest.main()
