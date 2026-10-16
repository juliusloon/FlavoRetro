"""P7 SS-R8 frozen screen/phase barrier: no scientific overpromotion."""
import json,unittest,hashlib
from pathlib import Path
from datetime import datetime
from scripts.operate import ROOT
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file

B=ROOT/"outputs/task016-p7/v1"
R=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
def load(p):return json.loads(Path(p).read_text())

@unittest.skipUnless(G6.exists(),"SS R8 original science outputs not installed")
class P7SSR8FrozenContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a0=load(R/"A0_science_read_precontract.json")
  cls.exp=load(R/"pre_read_exposure.json")
  cls.a4=load(R/"A4/source_body_screen.json")
  cls.a5=load(R/"A5/independent_body_scope_screen.json")
  cls.a6=load(R/"A6/source_scope_reconciliation.json")

 def test_G4_G5_G6_chain_and_FROZEN_scope(self):
  self.assertEqual(verify_stage_chain(G4,sha_file(G4))["stage"],"G4_SCOPE_FREEZE")
  self.assertEqual(verify_stage_chain(G5,sha_file(G5))["stage"],"G5_FRESH_HOLDOUT_ACQUIRE")
  self.assertEqual(verify_stage_chain(G6,sha_file(G6))["stage"],"G6_IDENTITY_STRUCTURE_ADMIT")
  self.assertEqual(load(G5)["input_manifest_sha"],sha_file(G4))
  self.assertEqual(load(G6)["input_manifest_sha"],sha_file(G5))

 def test_sources_permanently_exposed_before_science_read(self):
  self.assertEqual(self.exp["source_count"],2)
  events=[json.loads(s) for s in (ROOT/"operations/events.jsonl").read_text().splitlines() if s.strip()]
  first=[x["time"] for x in events if x.get("action") in ("SS_R8_A4_original_science_read_start","SS_R8_A5_original_science_read_start")]
  self.assertEqual(len(first),4)
  self.assertTrue(all(datetime.fromisoformat(self.exp["registered_at"])<datetime.fromisoformat(t) for t in first))
  self.assertTrue(self.exp["regardless_of_reaction_or_scope_evidence_these_sources_may_not_be_reused_as_next_epoch_fresh"])

 def test_original_immutable_SHA(self):
  self.assertEqual(len(self.a0["planned_sources"]),2)
  for x in self.a0["planned_sources"]:
   p=ROOT/x["raw_original"]["path"]
   self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),x["raw_original"]["sha256"])

 def test_A4_A5_separate_source_universe_no_guess(self):
  self.assertEqual({x["source_id"] for x in self.a4["sources"]},
                   {x["source_id"] for x in self.a5["sources"]})
  self.assertTrue(all(not x["complete_reaction_structure_extracted"] for x in self.a4["sources"]))
  self.assertTrue(all(not x["reaction_structure_qualified"] for x in self.a5["sources"]))
  self.assertFalse(self.a5["read_other_extractor"])
  self.assertFalse(self.a4["read_model_outcome"])

 def test_tea_mono_glycoside_7_O_not_sugar_O2(self):
  s=next(x for x in self.a6["sources"] if x["source_id"]=="PMC5517534")
  self.assertEqual(s["scope_disposition"],"demonstrated_different_7_O_aglycone_site_not_frozen_SS_E02_O2")
  self.assertFalse(s["eligible_for_SS_E02_panel"])
  self.assertTrue(any("7-hydroxy" in " ".join(e["observed_literal_features"]) for e in s["evidence_pointers"]))

 def test_carnation_accumulation_not_isolated_O2_reaction(self):
  s=next(x for x in self.a6["sources"] if x["source_id"]=="PMC13387883")
  self.assertEqual(s["scope_disposition"],"insufficient_direct_sugar_O2_reaction_in_screened_original")
  self.assertFalse(s["exact_frozen_scope_site_O2_supported"])
  self.assertTrue(any("sophoroside" in " ".join(e["observed_literal_features"]) for e in s["evidence_pointers"]))

 def test_scientific_admission_not_claimed(self):
  self.assertEqual(self.a6["counts"],{"processed":2,"passed_scientific":0,
     "rejected_for_current_scope":1,"deferred_no_direct_O2_reaction":1,"fresh_admitted":0,
     "new_closure_groups":0,"new_MCTS":0})
  self.assertFalse(self.a6["dual_complete_chemical_structure_extraction"])
  self.assertTrue(self.a6["no_claim_of_total_scientific_absence_in_any_article"])

 def test_registry_science_G5_and_G6_are_honest(self):
  entries=[json.loads(s) for s in (B/"epoch_ledger.jsonl").read_text().splitlines() if s.strip()]
  r5=[r for r in entries if r.get("stage_manifest_path")==str(G5.relative_to(ROOT))]
  r6=[r for r in entries if r.get("stage_manifest_path")==str(G6.relative_to(ROOT))]
  self.assertEqual(len(r5),len(r6))
  self.assertEqual(len(r5),1)
  self.assertTrue(r5[0]["permanent_exposure_pre_read"])
  self.assertEqual(r6[0]["fresh_admitted"],0)
  self.assertFalse(r6[0]["full_dual_graph_chemical_admission"])

if __name__=="__main__":unittest.main()
