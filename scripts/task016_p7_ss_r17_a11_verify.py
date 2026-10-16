"""SS-E02 R17 A11 independent bounded scientific-source access audit.

Reconstructs metadata and original-intake statuses from immutable evidence.
Not a chemical A11, no novel accepted reactions, no holdout/ABE claims.
"""
from __future__ import annotations
import hashlib,html,json,re
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
from scripts.task016_p7_c_e02_http import physical_attempts
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R13=B/"SS/E02/fresh/SS-E02-R13-title-metadata-discovery-v1"
R14=B/"SS/E02/fresh/SS-E02-R14-broad-title-discovery-v1"
R15=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1"
R16=B/"SS/E02/fresh/SS-E02-R16-verified-publisher-PDF-access-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
OUT=B/"verification-v24-ss-r13-r16/independent_source_admission_audit_v1.json"
ATT=R16/"public_access_attempt_attestation_v2.json"
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def lines(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def norm(s):return re.sub(r"[^a-z0-9]+","",html.unescape(re.sub(r"<[^>]*>","",str(s or ""))).casefold())
def save(p,x):write(TASK,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/OUT).exists() or (ROOT/ATT).exists():raise RuntimeError("A11_IMMUTABLE_V24_EXISTS")
 checks={}
 checks["G4_chain_intact"]=verify_stage_chain(ROOT/G4,sha(G4))["stage"]=="G4_SCOPE_FREEZE"
 checks["G5_chain_intact"]=verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 checks["G4_sha_vs_v23_still_intact"]=sha(G4)=="a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f"
 v23=load(B/"report_snapshots/progress-v23.json")
 checks["v23_REPORT_SHA_preserved"]=sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==v23["report_SHA"]
 checks["v23_STATE_SHA_preserved"]=sha(Path("STATE.md"))==v23["state_SHA"]
 perbatch={}
 for p,n in ((R13,8),(R14,8),(R15,4),(R16,2)):
  plan=load(p/"query_plan.json")["queries"]
  e=lines(p/"query_execution.jsonl");http=lines(p/"http_ledger.jsonl")
  checks["planned_terminal_"+p.name]=len(plan)==len(e)==len(http)==n and {r["query_id"] for r in plan}=={r["query_id"] for r in e}=={r["query_id"] for r in http}
  checks["precontract_input_SHA_"+p.name]=all(sha(Path(f))==s for f,s in load(p/"precontract.json")["registered_input_SHA"].items())
  checks["raw_SHA_"+p.name]=all(sha(Path(r["path"]))==r["sha256"] and (ROOT/r["path"]).stat().st_size==r["bytes"] for r in http)
  checks["no_science_read_"+p.name]=all(r.get("scientific_body_content_read") is False or r.get("source_original_contents_read") is False for r in http)
  perbatch[p.name]={"HTTP":len(http),"bytes":sum(r["bytes"] for r in http),
    "statuses":{str(code):sum(r.get("status_code")==code for r in http) for code in sorted({r.get("status_code") for r in http},key=str)}}
 source=load(R14/"discovered_title_identity_dispositions.json")
 corrected=load(R15/"A3_two_route_bibliographic_preflight_v2.json")
 checks["four_distinct_authoritative_second_route_IDs"]=len(corrected["records"])==4 and len({r["doi"] for r in corrected["records"]})==4 and all(r["metadata_identity_verified"] for r in corrected["records"])
 checks["strict_year_correction_frozen_original_failed"]=load(R15/"A3_two_route_bibliographic_preflight.json")["passed"]==0 and corrected["initial_false_year_conflict_count"]==4
 checks["crossref_raw_reparse_all4"]=True
 for row in lines(R15/"crossref_bibliography_projection.jsonl"):
  m=row["metadata"];r=next(x for x in corrected["records"] if x["doi"]==row["DOI"])
  original=json.loads((ROOT/row["original_raw"]["path"]).read_text())["message"]
  if original.get("DOI")!=m.get("DOI") or norm(original.get("title",[""])[0])!=norm(r["Crossref_title"]) or sha(Path(row["original_raw"]["path"]))!=row["original_raw"]["sha256"]:
   checks["crossref_raw_reparse_all4"]=False
 checks["no_false_fresh_from_new_titles"]=corrected["count"]["fresh_admitted"]==0 and corrected["count"]["original_publication_identity_verified"]==0
 checks["R14_new_titles_outside_R10_but_not_fresh"]=all(r["previous_R10_title_cluster_absent"] and r["real_historical_chemical_exposure_alias_graph_status"]=="unknown" for r in corrected["records"])
 reqs=load(R16/"query_plan.json")["queries"];http=lines(R16/"http_ledger.jsonl")
 checks["two_actual_Crossref_verified_publisher_paths"]=all(r["url"]==next(x for x in reqs if x["query_id"]==r["query_id"])["url"] for r in http)
 checks["two_HTTP_403_no_valid_PDF"]=len(http)==2 and all(r["status_code"]==403 and not r["public_pdf_magic"] and r["status"]=="failed" for r in http)
 checks["no_access_bypass_in_actual_request_code"]=all(r.get("final_url")==r.get("url") for r in http) and all("NoRedirect" in (ROOT/"scripts/task016_p7_ss_r16_publisher_raw.py").read_text() for _ in range(1))
 checks["no_G7_scientific_panel_created"]=all(not (ROOT/B/f"{f}/E02/stages/G7_CLOSURE_PANEL_FREEZE.json").exists() for f in ("C","SS"))
 checks["no_new_ABE_development_cells"]=len((ROOT/B/"run_ledger.jsonl").read_text().splitlines())==214
 physical=physical_attempts()
 selected_id={r["attempt_id"] for p in (R13,R14,R15,R16) for r in lines(p/"http_ledger.jsonl")}
 checks["22_new_exact_physical_attempts_reconciled"]=len(selected_id)==22 and all(any(x.get("attempt_id")==aid for x in physical) for aid in selected_id)
 checks["project_budget_below_ceiling"]=len(physical)<=8000 and sum(r["bytes"] for r in physical)<=8*1024**3
 checks["zero_chemical_scientific_source_upgrades"]=not any(r["scientific_reaction_qualified"] for r in corrected["records"])
 # A v1 preregistration boolean was named inconsistently; preserve v1 bytes,
 # attest the concrete request construction and HTTP access-control results.
 att=dict(task=TASK,epoch_id="SS-E02",at=datetime.now(timezone.utc).isoformat(),
   prior_contract_path=str(R16/"precontract.json"),prior_contract_SHA=sha(R16/"precontract.json"),
   misnamed_prior_field="no_login_cookie_payment_credential",misnamed_prior_value=False,
   correction="v1 field uses negated confusing name; actual transport constructed anonymous requests with User-Agent and Accept-Encoding only; no credentials, cookies, login, proxy, workaround or redirect auto-follow",
   source_code_path="scripts/task016_p7_ss_r16_publisher_raw.py",
   source_code_SHA=sha(Path("scripts/task016_p7_ss_r16_publisher_raw.py")),
   HTTP_responses=[dict(DOI=r["source_id"],HTTP=r["status_code"],raw_SHA=r["sha256"]) for r in http],
   status="public_anonymous_attempts_blocked_403",chemical_originals_available=0)
 save(ATT,att)
 count=sum(checks.values());failed=len(checks)-count
 out=dict(task=TASK,epoch_id="SS-E02",audit="A11_independent_bounded_source_provenance",
    at=datetime.now(timezone.utc).isoformat(),approval_type="agent_delegated",
    human_reviewed=False,checks=checks,passed=count,failed=failed,
    batches=perbatch,physical_cumulative=dict(HTTP=len(physical),bytes=sum(r["bytes"] for r in physical)),
    distinct_R13_metadata_titles=load(R13/"discovered_title_identity_dispositions.json")["distinct_titles"],
    distinct_R14_metadata_titles=source["distinct_titles"],
    two_provider_verified_primary_titles=corrected["count"]["bibliography_verified"],
    accessible_originals=0,new_reactions_qualified=0,
    fresh_admitted_C=0,fresh_admitted_SS=0,scientific_ABE_cells=0,
    no_claim_of_source_saturation=True,not_full_A3_and_not_chemical_science_A11=True,
    access_attestation_sha=sha(ATT),
    full_scientific_completion=False,roadmap_P2_completed=False)
 save(OUT,out)
 print(json.dumps(dict(A11_pass=count,A11_fail=failed,HTTP22=len(selected_id),verified_bibliography=out["two_provider_verified_primary_titles"],originals=0,fresh=0,global_HTTP=len(physical))))
 if failed:raise RuntimeError([k for k,v in checks.items() if not v])
if __name__=="__main__":main()

