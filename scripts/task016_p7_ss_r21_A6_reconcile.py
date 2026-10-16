"""SS R21 A6 authoritative source-text reconciliation, real enzymatic O2 proof.

G6 records positive source-level chemistry but intentionally admits zero new
structure-complete / never-exposed fresh holdouts; published/preprint same group.
"""
import hashlib,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import sha_file,freeze_stage_manifest,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G6_IDENTITY_STRUCTURE_ADMIT.json"
A4=R/"A4/source_original_reaction_claims.json"
A5=R/"A5/independent_original_O2_screen.json"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
SCOPE=B/"SS/E02/scope_manifest.json";EPOCH=B/"epoch_ledger.jsonl"
def sha(p):return sha_file(ROOT/p)
def read(p):return json.loads((ROOT/p).read_text())
def txt(n):return " ".join("".join(n.itertext()).split())
def save(p,v):
 if (ROOT/p).exists():raise RuntimeError("R21_A6_ALREADY_EXISTS")
 write(T,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/G6).exists():raise RuntimeError("G6_ALREADY_EXISTS")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 a=read(A4);b=read(A5);id=read(A3);preg=read(R/"A0_G5_original_science_precontract.json")
 assert a["source_count"]==b["source_count"]==2
 assert preg["science_scope"].startswith("only original JATS")
 aa={x["PMCID"]:x for x in a["sources"]};bb={x["PMCID"]:x for x in b["results"]}
 assert set(aa)==set(bb)=={"PMC12611259","PMC11974848"}
 evidence=[];sample=[]
 for sid,anchor in (("PMC12611259","body/p-16"),("PMC11974848","body/p-12")):
  p=aa[sid];q=bb[sid]
  assert p["raw_SHA"]==q["raw_SHA"]==sha(Path(p["raw_path"]))
  aitem=next(x for x in p["original_source_claims"] if x["anchor"]==anchor)
  bitem=next(x for x in q["evidence_anchors"] if x["anchor"]==anchor)
  assert aitem["literal_sha256"]==bitem["SHA256"]
  tree=ET.fromstring((ROOT/p["raw_path"]).read_bytes())
  ps=tree.find("./body").findall(".//p")
  actual=txt(ps[int(anchor.split("-")[-1])-1])
  assert hashlib.sha256(actual.encode()).hexdigest()==bitem["SHA256"]
  low=actual.lower()
  must=["udp-glucose","k-gal","2″","glucosyltransferase","produced"]
  assert all(z in low for z in must),(sid,[z for z in must if z not in low])
  if sid=="PMC12611259":assert "recombinant 79-b" in low and "79-a did not" in low
  else:assert "recombinant slugt79b-b" in low and "slugt79b-a did not" in low
  evidence.append(dict(PMCID=sid,DOI=p["DOI"],source_original_sha=p["raw_SHA"],
    paragraph_anchor=anchor,paragraph_SHA256=bitem["SHA256"],
    A4_identical_paragraph_SHA=aitem["literal_sha256"],A5_identical_paragraph_SHA=bitem["SHA256"],
    independently_agreed=True,
    demonstrated_enzymatic_action="SlUGT79B-B (79-B), recombinant protein; produced K-gal-glu (K2) using K-gal + UDP-glucose; 2-double-prime-O-glucosyltransferase; SlUGT79B-A negative comparison",
    acceptor="kaempferol 3-O-galactoside (K-gal, K1)",
    donor="UDP-glucose",product="kaempferol 3-O-glucosyl(1->2)galactoside (K2)",
    bond_site="existing galactoside sugar residue O2 (2-double-prime)",
    source_claim_disposition="direct_enzymatic_sugar_O2_UDPGlc_original_primary_evidence",
    full_covalent_atom_mapped_reference_not_yet_extracted=True,
    not_human_chemically_verified=True))
  sample.append(dict(PMCID=sid,anchor=anchor,source_SHA=bitem["SHA256"]))
 assert id["front_identified"]==6
 # Reconcile A4 and A5 evidence, not two distinct source groups.
 decision=dict(task=T,epoch_id="SS-E02",family="SS",
   role="A6_independent_source_evidence_and_closure_reconciliation",
   at=datetime.now(timezone.utc).isoformat(),
   cited_source_evidence=evidence,
   representative_primary_published_PMCID="PMC12611259",
   publication_original_verified_A3=True,
   primary_original_DOI="10.1093/plphys/kiaf556",
   related_preprint_PMCID="PMC11974848",
   related_preprint_DOI="10.1101/2025.03.27.645607",
   preprint_and_published_same_scientific_source_closure=True,
   independent_groups_added=0,
   scope_alignment_at_catalysis_level="positive: flavonol-3O-beta-Galp parent sugar O2 receives glucose from UDP-glucose using recombinant SlUGT79B-B",
   source_science_reaction_supported=True,
   source_originals_evidence_supported=2,
   source_level_candidate_reactions=1,
   final_product_stereochemistry_from_explicit_full_graph_confirmed=False,
   independent_dual_complete_molecular_graphs_available=False,
   runtime_complete=False,structure_complete=False,
   full_reference_precursors_complete=False,
   original_graph_from_source_figure_not_independently_transcribed=True,
   historical_development_exposure_or_alias_closure_complete=False,
   web_scientific_excerpt_preexposed_before_R21_G5=True,
   never_count_R21_tomato_as_fresh_without_new_independent_permitted_holdout=True,
   source_qualified_for_bounded_biochemical_O2_mechanism=True,
   P7_G6_complete_structure_reaction_admissions=0,
   P7_G7_qualified_fresh_holdouts=0,
   P7_transfer_ABE_new_cells=0,
   P7_scope_modified=False,read_model_outcomes=False,
   development_scientific_source_reference_not_formal_holdout=True,
   human_reviewed=False,approval_type="agent_delegated",
   no_automated_source_absence_claim=True,
   source_saturation_not_established=True)
 target=R/"A6/source_O2_scope_positive_reconciliation.json"
 save(target,decision)
 inp=[A3,G5,SCOPE,Path("scripts/task016_p7_ss_r21_A0_g5.py"),
      Path("scripts/task016_p7_ss_r21_A4.py"),Path("scripts/task016_p7_ss_r21_A5.py"),
      Path("scripts/task016_p7_ss_r21_A6_reconcile.py"),
      R/"A0_G5_original_science_precontract.json",
      R/"pre_scientific_read_source_exposure.json",
      A4,A5]+[Path(q["raw_path"]) for q in aa.values()]
 freeze_stage_manifest(ROOT/G6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",inp+[target],G5,
    expected_previous_sha=sha(G5),family="SS",epoch_id="SS-E02")
 assert verify_stage_chain(ROOT/G6,sha(G6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
 old=(ROOT/EPOCH).read_text()
 log=dict(task=T,epoch_id="SS-E02",family="SS",stage="G6_IDENTITY_STRUCTURE_ADMIT",
    status="active",event_type="R21_primary_O2_biochemical_source_proof_and_zero_fresh_G6",
    stage_manifest_path=str(G6),stage_manifest_sha256=sha(G6),
    previous_G5_path=str(G5),previous_G5_sha256=sha(G5),
    source_scope_positive=1,same_study_original_versions=2,
    structure_complete=0,fresh_admitted=0,read_model_outcome=False,
    web_preexposure=True,approval_type="agent_delegated",human_reviewed=False)
 write(T,str(EPOCH),old+json.dumps(log,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"SS_R21_source_qualified_direct_sugarO2_enzymatic_mechanism",G6_sha256=sha(G6),source_count=1,fresh=0)
 print(json.dumps(dict(SS_source_scope_positive=1,originals_reconciled=2,A4_A5_identical_original_paragraph_SHA=True,G6=sha(G6),fresh=0)))
if __name__=="__main__":main()

