"""R26 C three-original negative scope; R29 SS two original O2 positive groups.

This suite reads immutable raw JATS and checks the science proof and its
explicit prohibition from fresh holdout admission.
"""
import hashlib,json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.operate import ROOT
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
B=ROOT/"outputs/task016-p7/v1"
C=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1"
CG5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
CG6=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
S=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1"
SG5=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G5_FRESH_HOLDOUT_ACQUIRE.json"
SG6=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G6_IDENTITY_STRUCTURE_ADMIT.json"
PAST=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1/A6/source_O2_scope_positive_reconciliation.json"
def j(p):return json.loads(p.read_text())
def t(n):return " ".join("".join(n.itertext()).split())
class P7PrimaryOriginalGroupScience(unittest.TestCase):
 def test_C_G4_G5_G6_real_chain_and_3_sources(self):
  self.assertEqual(verify_stage_chain(CG5,sha_file(CG5))["stage"],"G5_FRESH_HOLDOUT_ACQUIRE")
  self.assertEqual(verify_stage_chain(CG6,sha_file(CG6))["stage"],"G6_IDENTITY_STRUCTURE_ADMIT")
  self.assertEqual(j(C/"A4/first_original_C_reaction_screen.json")["source_count"],3)
  self.assertEqual(j(C/"A5/second_independent_canonical_site_screen.json")["original_source_count"],3)
  self.assertEqual(j(C/"A6/three_original_science_scope_dispositions.json")["original_primary_science_reviewed"],3)

 def test_C_triple_negative_not_false_C6(self):
  a=j(C/"A6/three_original_science_scope_dispositions.json")
  self.assertEqual(a["scope_eligible_C6_reactions_found_in_these_three_originals"],0)
  self.assertEqual(a["new_fresh"],0)
  by={r["PMCID"]:r for r in a["sources"]}
  self.assertEqual(set(by),{"PMC9855344","PMC12525976","PMC11577821"})
  for r in by.values():
   self.assertFalse(r["source_scope_qualified"])
   self.assertEqual(sha_file(ROOT/r["original_path"] if "original_path" in r else ROOT/next(y["source_path"] for y in j(C/"A0_pre_read_contract.json")["selected"] if y["PMCID"]==r["PMCID"])),r["full_article_SHA"])
   self.assertTrue(r["independent_A4_A5_same_source_paragraph"])
  self.assertEqual(a["independent_direct_C6_primary_literature_leads"],2)

 def test_two_SS_originals_identified_and_historical(self):
  a=j(S/"A3_original_front_verified.json")
  self.assertEqual(a["front_identity_verified"],2)
  self.assertEqual({r["PMCID"]:r["DOI"] for r in a["sources"]},{
   "PMC4494776":"10.1186/s12870-015-0504-7",
   "PMC4282749":"10.1111/tpj.12580"})
  for r in a["sources"]:
   self.assertEqual(sha_file(ROOT/r["raw_source_path"]),r["raw_source_SHA"])
   self.assertTrue(r["prior_historical_exposure"])
   root=ET.fromstring((ROOT/r["raw_source_path"]).read_bytes())
   ids=["".join(n.itertext()).strip() for n in root.findall("./front/article-meta/article-id") if n.get("pub-id-type")=="pmcid"]
   self.assertEqual(ids,[r["PMCID"]])

 def test_SS_G5_to_G6_and_double_A4_A5_original_SHA(self):
  self.assertEqual(verify_stage_chain(SG5,sha_file(SG5))["stage"],"G5_FRESH_HOLDOUT_ACQUIRE")
  self.assertEqual(verify_stage_chain(SG6,sha_file(SG6))["stage"],"G6_IDENTITY_STRUCTURE_ADMIT")
  a=j(S/"A6/two_original_O2_scientific_group_closure.json")
  self.assertEqual(a["independent_O2_groups_newly_verified_this_round"],2)
  self.assertEqual(a["independent_O2_groups_including_prior_tomato"],3)
  for r in a["two_original_primary_O2_sources"]:
   raw=ET.fromstring((ROOT/r["original_path"]).read_bytes())
   p=raw.find("./body").findall(".//p")[int(r["independently_A4_A5_reconciled_reaction_paragraph"].split("-")[-1])-1]
   self.assertEqual(hashlib.sha256(t(p).encode()).hexdigest(),r["A4_A5_original_paragraph_SHA"])
   corroboration=raw.find("./body").findall(".//p")[int(r["corroborating_original_paragraph"].split("-")[-1])-1]
   self.assertEqual(hashlib.sha256(t(corroboration).encode()).hexdigest(),r["corroborating_SHA"])
   self.assertTrue(r["same_scope_enzymatic_sugarO2_source_positive"])
   self.assertFalse(r["fresh"])

 def test_SS_3_distinct_species_gene_studies_not_preprint_duplicate(self):
  a=j(S/"A6/two_original_O2_scientific_group_closure.json")
  tomato=j(PAST)
  self.assertEqual(tomato["source_level_candidate_reactions"],1)
  self.assertEqual(len(set(a["group_universe"])),3)
  self.assertEqual({r["PMCID"] for r in a["two_original_primary_O2_sources"]},{"PMC4494776","PMC4282749"})
  self.assertEqual(tomato["related_preprint_PMCID"],"PMC11974848")
  self.assertTrue(tomato["preprint_and_published_same_scientific_source_closure"])
  self.assertNotIn("PMC11974848",str(a["group_universe"]))

 def test_no_fresh_graph_mcts_or_G7_scientific_promotion(self):
  a=j(S/"A6/two_original_O2_scientific_group_closure.json")
  b=j(C/"A6/three_original_science_scope_dispositions.json")
  self.assertTrue(a["historical_exposure_fails_fresh"])
  self.assertEqual(a["complete_reaction_atomgraphs_admitted"],0)
  self.assertEqual(a["current_epoch_fresh_holdout_admitted"],0)
  self.assertEqual(a["scientific_A_B_E_cells_added"],0)
  self.assertEqual(b["new_fresh"],0)
  for fam in ("C","SS"):
   self.assertFalse((B/fam/"E02/stages/G7_CLOSURE_PANEL_FREEZE.json").exists())
if __name__=="__main__":unittest.main()

