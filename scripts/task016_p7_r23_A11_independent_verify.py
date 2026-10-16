"""P7 R23 independent A11 bounded reconstruction for 6 original PMC papers & O2.

No automatic chemistry qualification/fresh projection. Checks SHA-frozen
raw/identity, prior exposure, publication/preprint closure, R21 G5/G6 and
both role source anchors directly against original JATS.
"""
import hashlib,xml.etree.ElementTree as ET,json
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
from scripts.task016_p7_c_e02_http import physical_attempts
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R18=B/"governance/R18-eight-PMC-primary-original-access-v1"
R19=B/"governance/R19-three-PMC-targeted-original-access-v1"
R20=B/"governance/R20-six-original-front-identity-v1"
SS=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G6_IDENTITY_STRUCTURE_ADMIT.json"
O=B/"verification-v25-original-science-R18-R21/independent_A11_provenance_science_check.json"
def sha(p):return sha_file(ROOT/p)
def j(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def clean(n):return " ".join("".join(n.itertext()).split())
def main():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE_A11_EXISTS")
 checks={}
 prev=j(B/"report_snapshots/progress-v24.json")
 checks["v24_report_unmodified"]=sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==prev["report_SHA"]
 checks["v24_state_unmodified"]=sha(Path("STATE.md"))==prev["state_SHA"]
 for fam in ("C","SS"):
  g4=B/fam/"E02/stages/G4_SCOPE_FREEZE.json"
  checks[f"{fam}_G4_immutable_stage_chain"]=verify_stage_chain(ROOT/g4,sha(g4))["stage"]=="G4_SCOPE_FREEZE"
 checks["R21_G5_immutable_chain"]=verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 checks["R21_G6_immutable_chain"]=verify_stage_chain(ROOT/G6,sha(G6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
 stage=j(G6);checks["R21_G6_immediate_G5_predecessor"]=stage["input_manifest_sha"]==sha(G5)
 original=j(R20/"A3_six_original_front_identity_v1.json")
 raw18=rows(R18/"http_ledger.jsonl");raw19=rows(R19/"http_ledger.jsonl")
 checks["R18_eight_attempts_actual"]=len(raw18)==8
 checks["R19_three_attempts_actual"]=len(raw19)==3
 checks["physical_success_3_plus_3"]=sum(r["status_code"]==200 for r in raw18)==3 and sum(r["status_code"]==200 for r in raw19)==3
 checks["R18_preserved_5_HTTP500"]=sum(r["status_code"]==500 for r in raw18)==5
 checks["original_universe_exact6"]=len(original["sources"])==6 and len({x["PMCID"] for x in original["sources"]})==6 and original["front_identified"]==6
 checks["raw_SHA_and_bytes_verified"]=all(sha(Path(x["original_source_path"]))==x["original_SHA"] and (ROOT/x["original_source_path"]).stat().st_size==x["original_bytes"] for x in original["sources"])
 checks["exact_original_JATS_PMCID_matches"]=True
 checks["A3_DOI_title_year_exists"]=True
 for x in original["sources"]:
  try:
   tree=ET.fromstring((ROOT/x["original_source_path"]).read_bytes())
   pmcid=[clean(v) for v in tree.findall("./front/article-meta/article-id") if v.get("pub-id-type")=="pmcid"]
   checks["exact_original_JATS_PMCID_matches"] &= tree.tag=="article" and pmcid==[x["PMCID"]]
   checks["A3_DOI_title_year_exists"] &= bool(x["DOI"] and x["article_title"] and x["publication_years"])
  except Exception:checks["exact_original_JATS_PMCID_matches"]=False
 checks["R18_two_DOCTYPE_misclassification_explicitly_corrected"]=sum((ROOT/x["original_source_path"]).read_bytes().lstrip().startswith(b"<!DOCTYPE article") for x in original["sources"])>=2 and j(R18/"raw_custody_summary.json")["usable_original_XML"]==1
 corrected=j(R20/"source_RAW_custody_corrected_v2.json")
 checks["corrected_6_originals_3C3SS"]=corrected["total_acquired_usable_source_originals"]==6 and corrected["by_family"]=={"C":3,"SS":3}
 r4=j(SS/"A4/source_original_reaction_claims.json");r5=j(SS/"A5/independent_original_O2_screen.json")
 r6=j(SS/"A6/source_O2_scope_positive_reconciliation.json")
 checks["A4_and_A5_fixed_two_source_universe"]=set(x["PMCID"] for x in r4["sources"])==set(x["PMCID"] for x in r5["results"])=={"PMC12611259","PMC11974848"}
 checks["each_A4_A5_paragraph_SHA_matches_original"]=True
 for row in r6["cited_source_evidence"]:
  src=next(x for x in original["sources"] if x["PMCID"]==row["PMCID"])
  body=ET.fromstring((ROOT/src["original_source_path"]).read_bytes()).find("./body")
  paragraph=clean(body.findall(".//p")[int(row["paragraph_anchor"].split("-")[-1])-1])
  checks["each_A4_A5_paragraph_SHA_matches_original"] &= hashlib.sha256(paragraph.encode()).hexdigest()==row["paragraph_SHA256"]==row["A4_identical_paragraph_SHA"]==row["A5_identical_paragraph_SHA"]
 checks["direct_original_enzymatic_O2_positive"]=r6["source_science_reaction_supported"] is True and r6["source_qualified_for_bounded_biochemical_O2_mechanism"] is True and r6["source_level_candidate_reactions"]==1
 checks["published_DOI_exact"]=r6["primary_original_DOI"]=="10.1093/plphys/kiaf556"
 checks["preprint_same_study_not_independent"]=r6["related_preprint_DOI"]=="10.1101/2025.03.27.645607" and r6["preprint_and_published_same_scientific_source_closure"] is True and r6["independent_groups_added"]==0
 checks["raw_front_first_and_G5_before_A4_A5"]=j(SS/"A0_G5_original_science_precontract.json")["original_A3_SHA"]==sha(R20/"A3_six_original_front_identity_v1.json") and r6["web_scientific_excerpt_preexposed_before_R21_G5"] is True
 prior=(ROOT/B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl").read_text().casefold()
 checks["PMC12611259_already_present_in_prior_exposure"]=("pmc12611259" in prior)
 checks["unqualified_stereo_graph_remains_false"]=r6["structure_complete"] is False and r6["runtime_complete"] is False and r6["full_reference_precursors_complete"] is False
 checks["fresh_G7_ABE_not_claimed"]=r6["P7_G7_qualified_fresh_holdouts"]==0 and r6["P7_transfer_ABE_new_cells"]==0 and r6["P7_G6_complete_structure_reaction_admissions"]==0
 checks["no_real_G7_stage"]=all(not (ROOT/B/f"{fam}/E02/stages/G7_CLOSURE_PANEL_FREEZE.json").exists() for fam in ("C","SS"))
 physical=physical_attempts()
 ids={r["attempt_id"] for r in raw18+raw19}
 checks["all_11_real_HTTP_in_global_physical_ledger"]=len(ids)==11 and ids.issubset({r.get("attempt_id") for r in physical})
 checks["global_physical_HTTP_budget"]=len(physical)<=8000 and sum(r["bytes"] for r in physical)<=8*1024**3
 checks["R18_R19_sources_counted_not_doublecounted"]=corrected["total_HTTP"]==11 and len(raw18+raw19)==11
 passed=sum(bool(x) for x in checks.values())
 out=dict(task=T,epoch_id="SS-E02",at=datetime.now(timezone.utc).isoformat(),
  audit="A11_bounded_original_source_and_O2_scope_evidence",
  approval_type="agent_delegated",human_reviewed=False,
  checks=checks,passed=passed,failed=len(checks)-passed,
  raw_source_HTTP_delta=11,total_current_physical_HTTP=len(physical),
  new_usable_full_primary_originals=6,originals_by_family={"C":3,"SS":3},
  original_science_A4_A5_sources=2,published_primary_sugar_O2_mechanistic_groups=1,
  full_structure_reaction_admitted=0,fresh_C=0,fresh_SS=0,
  real_ABE_cells=0,G7_frozen=False,
  source_science_not_complete_graph=True,
  no_chemical_or_human_review_claim=True,
  scope_modified=False,model_modified=False,no_MCTS=True)
 write(T,str(O),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(A11_pass=passed,A11_failed=len(checks)-passed,originals=6,C=3,SS=3,source_positive=1,fresh=0,HTTP=len(physical))))
 if len(checks)!=passed:raise RuntimeError([k for k,v in checks.items() if not v])
if __name__=="__main__":main()

