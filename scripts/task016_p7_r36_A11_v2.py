"""R36 independent audit of actual custody, stage restoration and scientific boundaries."""
import json,hashlib,collections,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import load,lines,sha,put,now
from scripts.task016_p7_orchestrate import verify_stage_chain
from scripts.task016_p7_c_e02_http import physical_attempts
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"verification-v27-ACS-SI-and-restoration-v2"
R=B/"SS/E02/fresh/SS-E02-R34-three-ACS-SI-science-v1"
R31=B/"SS/E02/fresh/SS-E02-R31-ACS-public-SI-custody-v1"
R32=B/"SS/E02/fresh/SS-E02-R32-ACS-SI-expiry-recovery-v1"
R35=B/"governance/R35-frozen-input-exact-restoration-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=G5.parent/"G6_IDENTITY_STRUCTURE_ADMIT.json"
checks=[]
def check(name,ok,evidence=None):
 checks.append(dict(check=name,passed=bool(ok),evidence=evidence))
def main():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 inputs=[R/"pre_science_exposure_contract.json",R/"A3/original_SI_front_identity.json",R/"A4/independent_original_text_extraction.json",R/"A5/independent_original_text_extraction.json",R/"A6/scientific_SI_dispositions.json",R/"scientific_exposure_reads.jsonl",R32/"raw_custody_summary.json",R31/"raw_custody_summary.json",R35/"precontract.json",R35/"restoration_receipt.json",B/"report_snapshots/progress-v27-physical-budget.json"]
 for p in [G5,G6]:
  verify_stage_chain(ROOT/p,sha(p));check("new_stage_chain_"+p.name,True)
 contract=load(R/"pre_science_exposure_contract.json");source=contract["source_universe"]
 check("universe_fixed_at_three",len(source)==3)
 a3=load(R/"A3/original_SI_front_identity.json");a6=load(R/"A6/scientific_SI_dispositions.json")
 check("A3_actual_SI_title_match_3",all(x["exact_normalized_title_present"] and x["original_SI_identity_verified"] for x in a3["records"]))
 check("A6_caption_crosschecks",len(a6["caption_crosschecks"])==7 and all(x["both_independent_parsers_match"] for x in a6["caption_crosschecks"]))
 check("A6_disposition_conservation",a6["counts"]==dict(processed=3,passed=0,rejected=0,pending=3))
 for s in source:
  raw=Path(s["original_path"]);data=(ROOT/raw).read_bytes()
  check(s["DOI"]+"_PDF_raw_SHA_size_MD5",data.startswith(b"%PDF-") and sha(raw)==s["original_SHA"] and len(data)==s["original_bytes"] and hashlib.md5(data).hexdigest()==s["official_file_MD5"])
  check(s["DOI"]+"_publisher_exact_resource_DOI",s["official_resource_DOI"]==s["DOI"] and s["license"]["name"]=="CC BY-NC 4.0")
  inputs.append(raw)
  versions=[]
  for role in ("A4","A5"):
   r=next(x for x in load(R/role/"independent_original_text_extraction.json")["records"] if x["source_id"]==s["DOI"])
   p=Path(r["pages_path"]);assert sha(p)==r["pages_SHA"]
   pages=load(p)["pages"];inputs.append(p);versions.append(pages)
   check(s["DOI"]+"_"+role+"_bound_independent_pages",r["original_SHA"]==s["original_SHA"] and r["peer_final_read"] is False and all(hashlib.sha256(x["text"].encode()).hexdigest()==x["text_SHA"] for x in pages))
  check(s["DOI"]+"_two_parser_page_count",len(versions[0])==len(versions[1])==next(x["page_count"] for x in a3["records"] if x["source_id"]==s["DOI"]))
  disp=next(x for x in a6["records"] if x["source_id"]==s["DOI"])
  check(s["DOI"]+"_no_graph_stereo_fresh_invention",all(disp[k] is None for k in ["product_graph","acceptor_graph","donor_graph","stereo","reference_precursors"]) and disp["structure_complete"] is False and disp["fresh_admitted"] is False and disp["whole_paper_SS_O2_absence_claim"] is False)
 receipts=lines(R/"scientific_exposure_reads.jsonl")
 check("all_nine_A3_A4_A5_first_read_receipts",len(receipts)==9 and collections.Counter(r["agent_role"] for r in receipts)==dict(A3=3,A4=3,A5=3))
 check("G5_before_all_actual_reads",all(r["at"]>load(G5)["timestamp"] and r["G5_SHA"]==sha(G5) for r in receipts))
 rr31=lines(R31/"http_ledger.jsonl");rr32=lines(R32/"http_ledger.jsonl")
 check("R31_query_conservation",len(rr31)==12 and len(lines(R31/"query_execution.jsonl"))==12)
 check("R32_query_conservation",len(rr32)==6 and len(lines(R32/"query_execution.jsonl"))==6)
 check("no_silent_redirect_requests",sum(r["status_code"]==302 for r in rr31)==3 and sum(r["status_code"]==302 for r in rr32)==3)
 for r in rr31+rr32:
  p=Path(r["path"]);check(r["query_id"]+"_raw_custody",sha(p)==r["sha256"] and (ROOT/p).stat().st_size==r["bytes"])
 old403=[r for r in rr31 if r["status_code"]==403]
 check("three_expiry_failures_actual_XML_preserved",len(old403)==3 and all(ET.fromstring((ROOT/r["path"]).read_bytes()).findtext("Message")=="Request has expired" for r in old403))
 check("three_public_SIs_recovered",sum(r["status_code"]==200 for r in rr32)==3)
 fix=load(R35/"precontract.json");receipt=load(R35/"restoration_receipt.json")
 for r in fix["records"]:
  check(Path(r["path"]).name+"_exact_old_SHA_restored",sha(Path(r["path"]))==r["original_frozen_SHA"])
  check(Path(r["path"]).name+"_complete_before_bytes_preserved",sha(Path(r["full_archive_path"]))==r["full_archive_SHA"])
 check("physical_accounting_conserved_during_restoration",receipt["global_HTTP_before"]==receipt["global_HTTP_after"]==1105 and receipt["global_bytes_before"]==receipt["global_bytes_after"])
 check("old_R11_role_bytes_preserved",sha(Path(fix["old_role_path"]))==fix["old_role_SHA"])
 for p,h in fix["protected_frozen_manifests_SHA"].items():
  check(Path(p).name+"_old_R12_manifest_no_mutation",sha(Path(p))==h)
  verify_stage_chain(ROOT/p,h)
 current={}
 for r in lines(B/"epoch_ledger.jsonl"):
  if r.get("epoch_id") in ("C-E02","SS-E02") and r.get("status")=="active" and r.get("stage") in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT"):
   current[r["stage_manifest_path"]]=r["stage_manifest_sha256"]
 for p,h in current.items():verify_stage_chain(ROOT/p,h)
 check("all_registered_active_current_G5_G6_chains",len(current)==17,dict(count=len(current)))
 snap=load(B/"report_snapshots/progress-v27-physical-budget.json");actual=physical_attempts()
 check("physical_HTTP_independent_recount",len(actual)==snap["totals"]["HTTP"]==1105)
 check("physical_bytes_independent_recount",sum(r["bytes"] for r in actual)==snap["totals"]["bytes"]==1231963333)
 for fam,expected in [("C","09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46"),("SS","a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f")]:
  check(fam+"_G4_still_frozen",sha(B/f"{fam}/E02/stages/G4_SCOPE_FREEZE.json")==expected)
  check(fam+"_real_G7_absent",not list((ROOT/B/f"{fam}/E02/stages").rglob("G7_CLOSURE_PANEL_FREEZE.json")))
 run=lines(B/"run_ledger.jsonl")
 check("no_new_MCTS_rows",len(run)==214 and sha(B/"run_ledger.jsonl")==load(B/"report_snapshots/progress-v22-physical-budget.json")["physical_prefixes"][str(B/"run_ledger.jsonl")]["prefix_sha256"],"Exact entire run-ledger SHA unchanged from actual 04:01UTC snapshot; v1 incorrectly assumed nonexistent status field.")
 check("three_deferred_not_full_qualification_or_saturation",a6["qualified_new_closure_groups"]==a6["complete_graphs"]==a6["fresh_admitted"]==0 and a6["source_saturation"] is False and a6["complete_full_qualification_round"] is False)
 result=dict(supersedes_verifier="verification-v27-ACS-SI-and-restoration/independent_A11_public_SI_custody_and_restoration.json",correction_reason="v1 queried nonexistent run-ledger status key; v2 verifies exact full ledger SHA against before-work snapshot, not inferred counts",task=T,agent_role="A11",epoch_id="SS-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,input_manifest_sha={str(p):sha(p) for p in dict.fromkeys(inputs)},checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),counts=dict(processed=len(checks),passed=sum(x["passed"] for x in checks),rejected=sum(not x["passed"] for x in checks),pending=0),errors=[x for x in checks if not x["passed"]],unprocessed=[],read_holdout=True,read_model_outcome=False,chemical_independent_validation=False,scope_modified=False,science_ABE_cells=0,fresh_C=0,fresh_SS=0)
 put(O/"independent_A11_public_SI_custody_and_restoration.json",result)
 print(json.dumps(dict(passed=result["passed"],failed=result["failed"],registered_stage_chains=len(current))))
 if result["failed"]:raise RuntimeError("A11_FAILED")
if __name__=="__main__":main()
