"""P7 R7 independent physical/source/graph audit; no model or new HTTP."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from collections import Counter
from rdkit import Chem
from scripts.operate import ROOT,write
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
NAME=B/"governance/P7-R7-authoritative-exposed-name-resolution-v1"
GUARD=B/"governance/P7-R7-exposed-graph-candidate-guard-v1/candidate_graph_guard.json"
OLD=B/"report_snapshots/progress-v18.json"
OUT=B/"verification-v19-exposed-name-resolution"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def load(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_AUDIT_EXISTS")
 audit_input=[NAME/"query_plan.json",NAME/"query_execution.jsonl",NAME/"http_ledger.jsonl",
  NAME/"request_preregistration.jsonl",NAME/"disposition_summary.json",GUARD,OLD,
  Path("scripts/task016_p7_r7_exposed_name_identity.py"),
  Path("scripts/task016_p7_r7_exposed_graph_guard.py")]
 frozen={str(p):sha(p) for p in audit_input}
 plan=load(NAME/"query_plan.json");execute=rows(NAME/"query_execution.jsonl")
 req=rows(NAME/"http_ledger.jsonl");preregister=rows(NAME/"request_preregistration.jsonl")
 summary=load(NAME/"disposition_summary.json");guard=load(GUARD);old=load(OLD)
 tests={};errors=[]
 def check(k,ok):
  tests[k]=bool(ok)
  if not ok:errors.append(k)
 check("prior_v18_REPORT_SHA",sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==old["current_REPORT_sha"])
 check("prior_v18_STATE_SHA",sha(Path("STATE.md"))==old["current_STATE_sha"])
 check("v18_evidence_SHA_unchanged",all(sha(Path(p))==digest for p,digest in old["input_and_evidence_SHA"].items()))
 check("R7_prior_exposure_input_SHA",all(sha(Path(p))==digest for p,digest in plan["inputs_SHA256"].items()))
 planned={q["query_id"]:q for q in plan["queries"]}
 check("query_IDs_conserve",len(planned)==len(execute)==len(req)==len(preregister)==27 and
    set(planned)=={r["query_id"] for r in execute}=={r["query_id"] for r in req}=={r["query_id"] for r in preregister})
 check("hypotheses_28_unique_names_27",sum(len(x["exposure_hypotheses"]) for x in planned.values())==28 and len(set(x["name"] for x in planned.values()))==27)
 check("no_prior_unexposed_names",all(q["research_fresh_candidate"] is False for q in planned.values()))
 req_by={r["query_id"]:r for r in req}
 exe_by={r["query_id"]:r for r in execute}
 sum_bytes=0;valid=0;casefold_graph={}
 for i,q in planned.items():
  r=req_by[i];x=exe_by[i];path=Path(r["path"])
  good=sha(path)==r["sha256"] and (ROOT/path).stat().st_size==r["bytes"] and x["raw"]["sha256"]==r["sha256"]
  if not good:errors.append("BAD_SHA:"+i)
  sum_bytes+=r["bytes"]
  raw=load(path);properties=raw.get("PropertyTable",{}).get("Properties",[])
  c=x["property_identity_candidates"]
  if len(properties)!=1 or len(c)!=1 or properties[0].get("CID")!=c[0].get("CID") or properties[0].get("InChIKey")!=c[0].get("InChIKey"):
   errors.append("RAW_PROJECTION_MISMATCH:"+i)
  else:
   valid+=1
  if r["url"]!=q["url"] or r["kind"]!="metadata" or r["status_code"]!=200:
   errors.append("UNREGISTERED_HTTP_OR_FAILED:"+i)
  smi=properties[0].get("SMILES")
  if smi:
   mol=Chem.MolFromSmiles(smi)
   if mol is None:errors.append("INVALID_PROVIDER_STRUCTURE:"+i)
   else:casefold_graph[q["name"]]=Chem.MolToSmiles(mol,isomericSmiles=True,canonical=True)
 check("all_27_raw_sha_size",not any(x.startswith("BAD_SHA") for x in errors))
 check("all_27_raw_property_projection",valid==27)
 check("all_27_HTTP_200_registered",not any(x.startswith("UNREGISTERED_HTTP") for x in errors))
 check("27_provider_SMILES_valid",len(casefold_graph)==27)
 index=guard["candidate_graph_index"]
 check("27_guard_candidates_all_match_raw",len(index)==27 and all(casefold_graph.get(x["exposed_name"])==x["canonical_RDKit_SMILES"] for x in index))
 check("duplicate_name_exposure_survives",len([x for x in index if x["exposed_name"]=="isorhamnetin"])==1 and
       len([x for x in index if x["exposed_name"]=="isorhamnetin"][0]["historical_exposure_ids"])==2)
 check("no_promotion_fresh_or_science",summary["counts"]["new_scientific_holdout"]==0 and
       guard["counts"]["fresh_admitted"]==0 and guard["nonmatches_remain_unresolved"] is True)
 check("bytes_and_HTTP_conserve",len(req)==summary["counts"]["physical_HTTP"] and sum_bytes==summary["counts"]["raw_bytes"] and sum_bytes==7932)
 check("hard_budget_limit_after",summary["current_global_physical_budget"]["HTTP"]<=8000 and
       summary["current_global_physical_budget"]["bytes"]<8*1024**3)
 check("reported_prefix_matches_delta",summary["current_global_physical_budget"]["HTTP"]==plan["budget_before"]["HTTP"]+27 and
       summary["current_global_physical_budget"]["bytes"]==plan["budget_before"]["bytes"]+sum_bytes)
 outcome={"task":TASK,"agent_role":"A11","timestamp":datetime.now(timezone.utc).isoformat(),
  "input_SHA256":frozen,"checks":tests,"passed":sum(tests.values()),"failed":len(errors),
  "errors":errors,"bytes":sum_bytes,"physical_HTTP":len(req),
  "unique_exposed_names":27,"exposure_hypothesis_records":28,
  "provider_CID_identity_candidate_only":27,"independent_name_synonym_validation_completed":0,
  "qualified_fresh":0,"scientific_ABE_cells":0,"MCTS_added":0,
  "scientific_metrics":None,
  "not_a_chemistry_or_scientific_eligibility_certificate":True,"human_reviewed":False,
  "global_after":summary["current_global_physical_budget"]}
 write(TASK,str(OUT/"independent_R7_verification.json"),json.dumps(outcome,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"pass" if not errors else "failed","checks":len(tests),
   "passed":outcome["passed"],"errors":len(errors),"HTTP":len(req),
   "bytes":sum_bytes,"fresh":0},ensure_ascii=False))
 if errors:raise RuntimeError("R7_INDEPENDENT_AUDIT_FAILED")
if __name__=="__main__":main()
