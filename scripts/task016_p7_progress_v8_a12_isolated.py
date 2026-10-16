"""Bounded A12 documentary audit in an isolated process; root-authored, not blind chemistry."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from scripts.operate import write
ROOT=Path(__file__).resolve().parents[1]
T="TASK-016-P7"; B=Path("outputs/task016-p7/v1"); O=B/"report_audit/progress-v8-isolated-A12-v1"
inputs={}; checks=[]; facts={}; started=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def bind(p,h=None):
 p=str(p);actual=sha(p)
 if h is not None:assert actual==h,(p,"SHA mismatch")
 inputs[p]=actual;return ROOT/p
def js(p):return json.loads(bind(p).read_text())
def rows(p):return [json.loads(x) for x in bind(p).read_text().splitlines() if x]
def out(p,d):
 assert not (ROOT/p).exists(),str(p)
 write(T,str(p),json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def check(n,fn):
 try:facts[n]=fn();checks.append(dict(name=n,status="passed"))
 except Exception as e:checks.append(dict(name=n,status="failed",error=str(e),error_type=type(e).__name__))
S=js(B/"report_snapshots/progress-v8.json")
report=bind(S["report_pointer"]["path"],S["report_pointer"]["sha256"]).read_text()
state=bind(S["state_pointer"]["path"],S["state_pointer"]["sha256"]).read_text()
bind(Path(__file__).relative_to(ROOT))
def archives():
 for d in S["inputs"].values():bind(d["physical_archive"]["path"],d["sha256"])
 for k in ("prior_report_archive","prior_state_archive"):bind(S[k]["path"],S[k]["sha256"])
 return dict(evidence_archives=len(S["inputs"]),prior_documents=2,report_state_SHA_match=True)
check("v8_physical_archives_and_document_identity",archives)
def stages():
 e=rows(B/"epoch_ledger.jsonl");seen={}
 def visit(p,h=None):
  p=str(p);bind(p,h)
  if p in seen:return seen[p]
  d=js(p);assert d["human_reviewed"] is False and d["approval_type"]=="agent_delegated"
  for f,h in d["files"].items():bind(f,h)
  if d["previous_manifest_path"]:
   q=visit(d["previous_manifest_path"],d["input_manifest_sha"]);assert q["timestamp"]<=d["timestamp"]
  seen[p]=d;return d
 selected=[x for x in e if x.get("epoch_id")=="C-E02" and x.get("batch_id") in ["C-E02-R1","C-E02-R2","C-E02-R3","C-E02-R4"]]
 for x in selected:
  d=visit(x["stage_manifest_path"],x["stage_manifest_sha256"]);assert d["stage"]==x["stage"]
 g=Counter(x["stage"] for x in selected);assert g["G5_FRESH_HOLDOUT_ACQUIRE"]==4 and g["G6_IDENTITY_STRUCTURE_ADMIT"]==3
 assert not any(x.get("epoch_id")=="SS-E02" and x.get("stage") in ["G2_DESIGN_ACQUIRE","G3_SCOPE_BUILD","G4_SCOPE_FREEZE"] for x in e)
 assert not any(x.get("epoch_id")=="C-E02" and str(x.get("stage","")).startswith(("G7_","G8_","G9_")) for x in e)
 return dict(C_G5=4,C_G6=3,SS_E02_G2_G3_G4_absent=True,C_E02_G7_G8_G9_absent=True,recursive_stages=len(seen))
check("registered_stages_and_absent_later_gates",stages)
def r1r2():
 p=B/"C/E02/fresh";a=js(p/"C-E02-R1/query_audit.json");b=js(p/"C-E02-R2/query_audit.json");r=js(p/"C-E02-R2/article_acquisition.json")
 assert (a["planned"],a["executed"],a["returned"],a["discovered"])==(10,10,703,702)
 assert (b["planned"],b["executed"],b["identifier_PMIDs"],b["resolved_PMIDs"])==(5,5,84,84)
 assert len(r)==4 and all(x["xml"] is None and x["evidence_eligible"] is False for x in r)
 a6=js(p/"C-E02-R1/A6_source_reconciliation_v1/A6_source_reconciliation_summary.json")
 return dict(R1_query_counts=[10,10,703,702],R2_query_counts=[5,5,84,84],R2_deferred=4,R2_XML=0,R1_A6=a6)
check("R1_R2_query_and_access_scope",r1r2)
def r3r4():
 p=B/"C/E02/fresh";m=js(p/"C-E02-R3/metadata_discovery_summary.json");r=js(p/"C-E02-R3/raw_original_request_summary.json");c=rows(B/"C/http_ledger.jsonl")
 assert (m["hint_universe"],m["actual_metadata_requests"],r["actual_HTTP"],r["PDF_objects"],r["graphic_objects"],r["HTML_objects"])==(21,36,52,2,1,8)
 counts=Counter(x.get("batch_id") for x in c)
 assert counts["C-E02-R3"]==88 and counts["C-E02-R4"]==6
 q=js(p/"C-E02-R4/raw_file_intake_summary.json");assert q["planned_downloads"]==q["terminal_downloads"]==2 and q["raw_PDFs"]==2
 a=rows(p/"C-E02-R3/A4_fixed_extraction_v1/A4_source_dispositions.jsonl");b=rows(p/"C-E02-R4/A4_fixed_extraction_v1/A4_source_dispositions.jsonl")
 assert len(a)==21 and len(b)==2 and {x["source_id"] for x in b}<={x["source_id"] for x in a}
 return dict(R3_sources=21,R3_metadata_HTTP=36,R3_original_HTTP=52,R4_HTTP=6,R4_sourceIDs_reused=2,R3_raw_PDF=2,R3_graphic=1,R3_HTML=8)
check("R3_R4_sources_HTTP_and_reused_IDs",r3r4)
def cells():
 result={};alias={"purified_CGTa":"CGTa","purified_CGTb":"CGTb","recombinant_FeCGTa":"FeCGTa","recombinant_FeCGTb":"FeCGTb"}
 for batch,n in (("C-E02-R3",68),("C-E02-R4",46)):
  p=B/"C/E02/fresh"/batch
  a=[x for x in rows(p/"A4_fixed_extraction_v1/A4_assay_observations.jsonl") if x["table"]=="Table1"]
  b=rows(p/"A5_fixed_extraction_v1/A5_Table1_complete_assay_cells.jsonl")
  ma={(x["substrate_literal"],alias.get(x["enzyme"],x["enzyme"])):x for x in a};mb={(x["substrate_name_literal"],x["enzyme_literal"]):x for x in b}
  assert len(ma)==len(a)==len(mb)==len(b)==n and set(ma)==set(mb)
  cnt=Counter()
  for k,x in ma.items():
   y=mb[k];st={"numeric_observation_SD_not_reported":"numeric_observation"}.get(x["status"],x["status"])
   st2={"numeric_activity_reported":"numeric_observation"}.get(y["value_status"],y["value_status"])
   assert (st,x["value"],x["sd"],x["literal_value"])==(st2,y["mean"],y["SD"],y["value_literal"])
   assert x["unit"].replace("_"," ")==y.get("units",y.get("unit")).replace("_"," ")
   cnt[st]+=1;cnt["zero_SD"]+=int(y["SD"] is not None and y["SD"]==0);cnt["missing_SD_numeric"]+=int(st=="numeric_observation" and y["SD"] is None);cnt["zero_mean"]+=int(st=="numeric_observation" and y["mean"]==0)
  assert (cnt["numeric_observation"],cnt["not_detected"],cnt["not_tested"],cnt["zero_SD"],cnt["missing_SD_numeric"],cnt["zero_mean"])==((30,24,14,1,0,0) if n==68 else (28,18,0,3,2,0))
  result[batch]=dict(cells=n,counts=dict(cnt))
 return dict(batches=result,total_measurement_cells=114,independent_reactions_inferred=False)
check("114_raw_measurements_status_zero_missingness",cells)
def identities():
 a=rows(B/"C/E02/fresh/C-E02-R3R4-A3/source_publication_identity.v2.jsonl")
 assert len(a)==5 and sum(x["metadata_identity_verified"] is True for x in a)==5 and sum(x["source_identity_verified"] is True for x in a)==4
 s=js(B/"SS/E02_design/A6_source_qualification_v1/A6_source_qualification_summary.v2.json")
 assert s["source_build_supported_contexts"]==2 and s["distinct_eligible_canonical_acceptors"]==1 and s["source_drawn_only_actual_salt_unknown"] is True and s["scope_floor_passed"] is False
 return dict(C_metadata=5,C_original_pass=4,C_original_pending=1,SS_contexts=2,SS_acceptors=1,SS_salt_unknown=True,SS_scope_floor=False)
check("publication_identity_and_SS_scope_floor",identities)
def budget():
 d=js(B/"verification-v12-incremental/budget_prefix_snapshot.json");captured={}
 for p,x in d["physical_prefixes"].items():
  raw=(ROOT/p).read_bytes()[:x["prefix_byte_count"]];assert hashlib.sha256(raw).hexdigest()==x["prefix_sha256"];captured[p]=raw
 attempts={}
 for h in d["http_ledgers"]:
  p=h["path"];raw=captured[p];rr=[json.loads(x) for x in raw.splitlines() if x] if p.endswith(".jsonl") else json.loads(raw)
  for x in rr:
   key=(x["url"],x["started_at"],x["path"])
   if key in attempts:assert all(attempts[key].get(k)==x.get(k) for k in ["sha256","bytes"])
   attempts[key]=x
 for x in [json.loads(l) for l in captured["operations/events.jsonl"].splitlines() if l]:
  if x.get("task")==T and x.get("action")=="source_http":attempts[(x["url"],x["started_at"],x["path"])]=x
 cnt=Counter();families={k:Counter() for k in ["C","SS","root"]}
 for x in attempts.values():
  kind=x.get("kind",x.get("role"));parts=Path(x["path"] or "").parts;f="SS" if "SS" in parts else "C" if "C" in parts else "root";z=families[f]
  z["HTTP"]+=1;z["bytes"]+=x["bytes"];z["article_legacy"]+=int(kind in ["xml","article_version"]);z["article_expanded"]+=int(kind in ["xml","article_version","original_pdf"]);z["attachments"]+=int(kind=="attachment")
 for z in families.values():cnt.update(z)
 assert (cnt["HTTP"],cnt["bytes"],cnt["article_legacy"],cnt["article_expanded"],cnt["attachments"])==(533,1080953785,42,43,90)
 run=rows(B/"run_ledger.jsonl");a={x["run_id"] for x in run if x["phase"]=="started"};b={x["run_id"] for x in run if x["phase"]!="started"};assert a==b and len(a)==107 and len(run)==214
 return dict(as_of=d["capture_finished_at"],total=dict(cnt),families={k:dict(v) for k,v in families.items()},search_started=107,search_terminal=107,article_request_classification_pending=True,available_paper_count_inferred=False)
check("bounded_physical_budget_and_terminal_search_counts",budget)
def scope_of_claims():
 assert S["fresh_C"]==S["fresh_SS"]==S["scientific_ABE_cells"]==0 and S["metrics"] is None and S["goal_completed"] is False and S["human_reviewed"] is False
 assert "In Progress" in report and "development effect 未关闭" in report and "221" in report and "144" in report and "不宣称完整233" in report
 v=js(B/"verification-v12-incremental/independent_verification.v2.json");assert v["check_counts"]==dict(passed=7,pending=7) and v["overall_completed"] is False
 return dict(fresh_C=0,fresh_SS=0,scientific_ABE=0,metrics=None,full233_claim=False,goal_completed=False,A11_v12_completed_bounded_checks=True,report_v8_A11_v12_progress_wording_is_correct_asof_v8=True)
check("engineering_science_and_asof_boundaries",scope_of_claims)
for n in ["source_saturation_and_global_closure","SS_second_acceptor_qualification","C_SS_fresh_panels_and_ABE","current_entire_code_suite","final_independent_chemistry_or_release"]:checks.append(dict(name=n,status="pending",reason="Outside bounded documentary audit or not completed"))
counts=Counter(x["status"] for x in checks)
result=dict(task=T,approval_type="agent_delegated",logical_role="A12 root-authored isolated documentary process",independent_subagent=False,independent_subagent_unavailable_reason="agent thread limit reached",root_already_exposed_to_prior_evidence=True,blind_chemistry=False,human_reviewed=False,independent_chemical_validation=False,started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),snapshot_pointer=dict(path=str(B/"report_snapshots/progress-v8.json"),sha256=sha(B/"report_snapshots/progress-v8.json")),checks=checks,check_counts=dict(counts),facts=facts,input_files_sha256=inputs,executed_subset_passed=counts["failed"]==0,overall_completed=False,new_HTTP=0,new_MCTS=0)
out(O/"bounded_report_validation.json",result)
out(O/"role_A12_isolated_manifest.json",dict(task=T,approval_type="agent_delegated",role=result["logical_role"],human_reviewed=False,independent_subagent=False,input_files_sha256=inputs,output_files_sha256={str(O/"bounded_report_validation.json"):sha(O/"bounded_report_validation.json")},scientific_admission_authority=False))
print(json.dumps(dict(check_counts=dict(counts),output=str(O),overall_completed=False)))
if counts["failed"]:raise SystemExit(1)
