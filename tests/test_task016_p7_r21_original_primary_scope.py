"""P7 R20/R21 six-real-original and source-positive/O2 fail-closed checks."""
import hashlib,json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.operate import ROOT
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
B=ROOT/"outputs/task016-p7/v1"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
BASE=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G6_IDENTITY_STRUCTURE_ADMIT.json"
def js(p):return json.loads(p.read_text())
class R21PublishedProof(unittest.TestCase):
    def test_6_actual_raw_originals_not_http200_proxies(self):
        six=js(A3)
        self.assertEqual(six["front_identified"],6)
        self.assertEqual(len(six["sources"]),6)
        ids=set()
        for x in six["sources"]:
            raw=ROOT/x["original_source_path"]
            self.assertEqual(sha_file(raw),x["original_SHA"])
            root=ET.fromstring(raw.read_bytes())
            self.assertEqual(root.tag,"article")
            front=root.find("./front")
            self.assertIsNotNone(front)
            self.assertTrue(any("".join(y.itertext()).strip()==x["PMCID"] for y in front.findall(".//article-id")))
            ids.add(x["PMCID"])
        self.assertEqual(len(ids),6)

    def test_DOCTYPE_originals_recovered_from_false_magic(self):
        six=js(A3)["sources"]
        recovered=[x for x in six if x["PMCID"] in ("PMC9855344","PMC12525976")]
        self.assertEqual(len(recovered),2)
        for x in recovered:
            raw=(ROOT/x["original_source_path"]).read_bytes()
            self.assertTrue(raw.lstrip().startswith(b"<!DOCTYPE article"))
            self.assertIsNotNone(ET.fromstring(raw).find("./front"))
        r18=js(B/"governance/R18-eight-PMC-primary-original-access-v1/raw_custody_summary.json")
        self.assertEqual(r18["usable_original_XML"],1)
        self.assertTrue(js(A3)["prior_R18_classification_false_due_to_XML_DOCTYPE"])

    def test_real_frozen_G5_to_G6_not_skipped(self):
        self.assertEqual(verify_stage_chain(G5,sha_file(G5))["stage"],"G5_FRESH_HOLDOUT_ACQUIRE")
        self.assertEqual(verify_stage_chain(G6,sha_file(G6))["stage"],"G6_IDENTITY_STRUCTURE_ADMIT")
        a6=js(BASE/"A6/source_O2_scope_positive_reconciliation.json")
        self.assertEqual(a6["primary_original_DOI"],"10.1093/plphys/kiaf556")
        self.assertEqual(a6["P7_G6_complete_structure_reaction_admissions"],0)
        self.assertEqual(a6["P7_G7_qualified_fresh_holdouts"],0)
        self.assertFalse(a6["structure_complete"])

    def test_direct_sugar_o2_in_original_both_independent_reviews(self):
        a4=js(BASE/"A4/source_original_reaction_claims.json")
        a5=js(BASE/"A5/independent_original_O2_screen.json")
        a6=js(BASE/"A6/source_O2_scope_positive_reconciliation.json")
        self.assertTrue(a6["source_science_reaction_supported"])
        self.assertEqual(a6["source_level_candidate_reactions"],1)
        self.assertTrue(a6["preprint_and_published_same_scientific_source_closure"])
        source=next(x for x in a6["cited_source_evidence"] if x["PMCID"]=="PMC12611259")
        self.assertEqual(source["paragraph_anchor"],"body/p-16")
        sha=source["paragraph_SHA256"]
        a=next(x for x in a4["sources"] if x["PMCID"]=="PMC12611259")
        b=next(x for x in a5["results"] if x["PMCID"]=="PMC12611259")
        self.assertTrue(any(x["literal_sha256"]==sha for x in a["original_source_claims"]))
        self.assertTrue(any(x["SHA256"]==sha and x["has_site_2doubleprime"] and x["has_preglycosylated_acceptor"] and x["has_udp_glc"] for x in b["evidence_anchors"]))
        original=ET.fromstring((ROOT/a["raw_path"]).read_bytes())
        paragraph=original.find("./body").findall(".//p")[15]
        claim=" ".join("".join(paragraph.itertext()).split())
        self.assertEqual(hashlib.sha256(claim.encode()).hexdigest(),sha)
        for required in ("K-gal","UDP-glucose","2″","recombinant 79-B"):
            self.assertIn(required.casefold(),claim.casefold())
if __name__=="__main__":unittest.main()

