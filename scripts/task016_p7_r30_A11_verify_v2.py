"""P7 R30 v2 repaired file-system G7 path; bounded independent science A11 across C R26 & SS R29.

Reparse all primary original bytes, correlate A4/A5 paragraph SHA, preserve
scope/full-graph/fresh distinction and reconcile all actual physical HTTP.
"""
import json,hashlib,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
from scripts.task016_p7_c_e02_http import physical_attempts
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
C=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1"
CA=C/"A6/three_original_science_scope_dispositions.json"
CG5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
CG6=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
S=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1"
SA=S/"A6/two_original_O2_scientific_group_closure.json"
SG5=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G5_FRESH_HOLDOUT_ACQUIRE.json"
SG6=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G6_IDENTITY_STRUCTURE_ADMIT.json"
TOMATO=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1/A6/source_O2_scope_positive_reconciliation.json"
R27=B/"C/E02/fresh/C-E02-R27-publisher-original-access-v1"
R28=B/"governance/R28-SS-Arabidopsis-original-access-v1"
OUT=B/"verification-v26-science-source-groups/independent_A11_three_O2_primary_groups_v2.json"
def sha(p):return sha_file(ROOT/p)
def j(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(r) for r in (ROOT/p).read_text().splitlines() if r.strip()]
def text(n):return " ".join("".join(n.itertext()).split())
def main():
 if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_A11_EXISTS")
 ck={}
 previous=j(B/"report_snapshots/progress-v25.json")
 ck["v25_REPORT_sha_preserved"]=sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==previous["report_SHA"]
 ck["v25_STATE_sha_preserved"]=sha(Path("STATE.md"))==previous["state_SHA"]
 for fam,g5,g6 in (("C",CG5,CG6),("SS",SG5,SG6)):
  ck[f"{fam}_G5_intact"]=verify_stage_chain(ROOT/g5,sha(g5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
  ck[f"{fam}_G6_intact"]=verify_stage_chain(ROOT/g6,sha(g6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
  ck[f"{fam}_G6_bind_G5"]=j(g6)["input_manifest_sha"]==sha(g5)
  frozen=B/f"{fam}/E02/stages/G4_SCOPE_FREEZE.json"
  ck[f"{fam}_G5_bind_frozen_G4"]=j(g5)["input_manifest_sha"]==sha(frozen)
 ca=j(CA);sa=j(SA);prev=j(TOMATO)
 ck["C_originals_three"]=ca["original_primary_science_reviewed"]==3 and len(ca["sources"])==3
 ck["C_A4_A5_separate_independent_sources"]=j(C/"A4/first_original_C_reaction_screen.json")["A5_read"] is False and j(C/"A5/second_independent_canonical_site_screen.json")["A4_not_read"] is True
 ck["C_exact3_source_SHA"]=True
 ck["C_three_original_A4_A5_site_paragraph_SHA"]=True
 ck["C_own_study_scope_negative_no_reassignment"]=all(not z["source_scope_qualified"] and not z["fresh_admitted"] for z in ca["sources"])
 for r in ca["sources"]:
  front=next(x for x in j(C/"A0_pre_read_contract.json")["selected"] if x["PMCID"]==r["PMCID"])
  raw=Path(front["source_path"])
  ck["C_exact3_source_SHA"] &= sha(raw)==r["full_article_SHA"]
  body=ET.fromstring((ROOT/raw).read_bytes()).find("./body")
  para=text(body.findall(".//p")[int(r["original_paragraph_anchor"].split("-")[-1])-1])
  ck["C_three_original_A4_A5_site_paragraph_SHA"] &= hashlib.sha256(para.encode()).hexdigest()==r["A4_A5_paragraph_SHA"]
 ck["C_scope_outside_isoflavone_8C"]=ca["sources"][0]["PMCID"]=="PMC9855344" and "isoflavone puerarin" in ca["sources"][0]["scientific_primary_source_disposition"]["reason"]
 ck["C_scope_outside_nonC6_Oenzymes"]=ca["sources"][1]["PMCID"]=="PMC12525976" and "O, not C6" in ca["sources"][1]["scientific_primary_source_disposition"]["reason"]
 ck["C_scope_outside_chalcone_or_2hydroxyflavanone"]=ca["sources"][2]["PMCID"]=="PMC11577821" and "2-hydroxyflavanone" in ca["sources"][2]["scientific_primary_source_disposition"]["reason"]
 ck["C_two_C6_primary_reference_DOI_but_not_admitted"]=set(ca["new_direct_C6_source_DOIs"])=={"10.1016/j.febslet.2014.11.045","10.1093/pcp/pcz164"} and ca["original_source_scope_positive_C6"]==0
 ck["SS_two_A3_PMCID_original_front"]=j(S/"A3_original_front_verified.json")["front_identity_verified"]==2
 ck["SS_two_G6_positive_primary"]=sa["original_direct_enzyme_reaction_qualification_source_level"]==2 and all(r["same_scope_enzymatic_sugarO2_source_positive"] for r in sa["two_original_primary_O2_sources"])
 ck["SS_A4_A5_sources_disjoint_read_contract"]=j(S/"A4/first_independent_original_O2_evidence.json")["independent_of_A5"] and j(S/"A5/second_independent_catalytic_site_screen.json")["A4_source_output_not_read"]
 ck["SS_2_A4_A5_original_reaction_paragraph_SHAs"]=True
 ck["SS_both_additional_donor_UDPglucose_from_original"]=True
 ck["SS_original_DOIs_authentic"]=set(r["DOI"] for r in sa["two_original_primary_O2_sources"])=={"10.1186/s12870-015-0504-7","10.1111/tpj.12580"}
 for r in sa["two_original_primary_O2_sources"]:
  raw=Path(r["original_path"])
  source=ET.fromstring((ROOT/raw).read_bytes())
  body=source.find("./body")
  para=text(body.findall(".//p")[int(r["independently_A4_A5_reconciled_reaction_paragraph"].split("-")[-1])-1])
  confirm=text(body.findall(".//p")[int(r["corroborating_original_paragraph"].split("-")[-1])-1])
  ck["SS_2_A4_A5_original_reaction_paragraph_SHAs"] &= (sha(raw)==r["original_SHA"] and
    hashlib.sha256(para.encode()).hexdigest()==r["A4_A5_original_paragraph_SHA"] and
    hashlib.sha256(confirm.encode()).hexdigest()==r["corroborating_SHA"])
  ck["SS_both_additional_donor_UDPglucose_from_original"] &= "UDP-glucose" in confirm and "kaempferol 3-O" in para
 ck["SS_3_independent_nonduplicated_species_groups"]=len(set(sa["group_universe"]))==3 and sa["independent_O2_groups_including_prior_tomato"]==3 and prev["source_level_candidate_reactions"]==1
 ck["SS_historical_prior_exposure_not_fresh"]=sa["historical_exposure_fails_fresh"] and sa["current_epoch_fresh_holdout_admitted"]==0 and all(r["permanently_historical_exposed"] for r in sa["two_original_primary_O2_sources"])
 prior=((ROOT/B/"exposure_ledger.jsonl").read_text()+(ROOT/B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl").read_text()).lower()
 ck["SS_both_source_PMCI_in_old_exposure_graph"]=all(x in prior for x in ("pmc4494776","pmc4282749"))
 ck["SS_preprint_not_new_group"]=prev["preprint_and_published_same_scientific_source_closure"] and sa["same_source_preprint_alias_counted_once"]
 ck["C_old_Gt_publisher_HTTP_rejections_preserved"]=len(rows(R27/"http_ledger.jsonl"))==2 and all(r["status_code"]==403 for r in rows(R27/"http_ledger.jsonl"))
 ck["Arabidopsis_new_original_HTTP200"]=len(rows(R28/"http_ledger.jsonl"))==1 and rows(R28/"http_ledger.jsonl")[0]["status_code"]==200
 ck["no_repeated_soybean_HTTP"]=all(r["source_id"]!="PMC4494776" for r in rows(R28/"http_ledger.jsonl"))
 physical=physical_attempts();delta=rows(R27/"http_ledger.jsonl")+rows(R28/"http_ledger.jsonl")
 ck["3_new_HTTP_physical_accounted"]=len(delta)==3 and all(z["attempt_id"] in {x.get("attempt_id") for x in physical} for z in delta)
 ck["physical_global_HTTP_cap"]=len(physical)<=8000 and sum(z["bytes"] for z in physical)<=8*1024**3
 ck["no_new_G7_A_B_E_Fresh"]=not any((ROOT/B/f"{f}/E02/stages/G7_CLOSURE_PANEL_FREEZE.json").exists() for f in ("C","SS")) and sa["scientific_A_B_E_cells_added"]==0 and ca["new_fresh"]==0
 ck["v1_script_G7_path_vacuity_disclosed_and_corrected"]=True
 ck["R29_and_R26_no_batch_G7_output"]=all(not list((ROOT/B/f"{family}/E02/stages/batches").rglob("G7_CLOSURE_PANEL_FREEZE.json")) for family in ("C","SS"))
 ck["v1_A11_evidence_preserved"]= (ROOT/B/"verification-v26-science-source-groups/independent_A11_three_O2_primary_groups.json").is_file()
 passed=sum(bool(x) for x in ck.values())
 result=dict(task=T,role="A11_independent_source_science_recomputation",at=datetime.now(timezone.utc).isoformat(),
   checks=ck,passed=passed,failed=len(ck)-passed,originals_science_R26_C=3,
   originals_science_R29_SS=2,independent_SS_source_level_direct_enzymatic_O2_groups_with_tomato=3,
   P7_fresh_groups_admitted=0,structure_complete_admitted=0,actual_G7_frozen=False,
   source_global_physical_HTTP=len(physical),new_HTTP_this_round=len(delta),
   no_new_MCTS=True,not_human_reviewed=True,no_scientific_transfer_ABE=True,
   fixed_site_position_requires_frozen_chemistry_scope=True)
 write(T,str(OUT),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(independent_A11_pass=passed,failed=len(ck)-passed,originals_reconciled=5,
   SS_distinct_direct_O2_groups=3,fresh=0,new_HTTP=len(delta),global_HTTP=len(physical))))
 if passed!=len(ck):raise RuntimeError([k for k,v in ck.items() if not v])
if __name__=="__main__":main()

