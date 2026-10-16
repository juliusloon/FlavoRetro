"""Freeze the existing exposure inventory before prospective source science reads."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_closure_harness import source_tokens,closure_tokens as legacy_tokens,canonical
TASK="TASK-016-P7";B=ROOT/"outputs/task016-p7/v1";D=B/"governance/prior_exposure_inventory_v2"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def put(p,obj):write(TASK,rel(p),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if D.exists():raise RuntimeError("inventory namespace already exists")
 ts=datetime.now(timezone.utc).isoformat()
 files=[]
 for p in sorted(B.rglob("*.jsonl")):
  dirs=p.relative_to(B).parts[:-1]
  if any(x=="fixtures" or x=="report_snapshots" or x.startswith("verification-") or x.startswith("prior_exposure_inventory_") for x in dirs):continue
  if "expos" in p.name.lower() or "hypothes" in p.name.lower():files.append(p)
 excluded=[p for p in files if p.name=="source_exposure_projection.jsonl"]
 normative=[p for p in files if p not in excluded]
 assert B/"exposure_ledger.jsonl" in normative
 origins={rel(p):sha(p) for p in files}
 rows=[];issues=[];counts={}
 def nodes(obj):
  if isinstance(obj,dict):
   yield obj
   for v in obj.values():yield from nodes(v)
  elif isinstance(obj,list):
   for v in obj:yield from nodes(v)
 for p in normative:
  records=[json.loads(line) for line in p.read_text().splitlines() if line.strip()]
  counts[rel(p)]=len(records)
  for i,record in enumerate(records,1):
   tokens=set();unknown=[]
   for node in nodes(record):
    try:tokens.update(legacy_tokens(node))
    except Exception as exc:
     tokens.update(source_tokens(node));unknown.append(type(exc).__name__+":legacy_closure_semantics")
    for field in ("pmid","source_pmid"):
     value=node.get(field)
     if isinstance(value,int) and not isinstance(value,bool) and value>0:tokens.add("pmid:"+str(value))
     elif isinstance(value,str) and value.strip().isdigit() and int(value.strip())>0:tokens.add("pmid:"+value.strip())
     elif value is not None:unknown.append("explicit_"+field+"_not_normalized")
    for field in ("target_graph","product_graph","canonical_smiles","canonical_isomeric_smiles","isomeric_smiles"):
     value=node.get(field)
     if isinstance(value,str):
      try:tokens.add("target:"+canonical(value))
      except Exception:unknown.append(field+"_not_a_confirmed_molecular_graph")
   is_metadata=(record.get("development_exposed") is False and record.get("exposure_type")=="metadata_only")
   # Unknown provenance remains conservative; no source/graph freshness follows.
   row={"origin_file":rel(p),"origin_file_sha256":origins[rel(p)],"origin_jsonl_line":i,
        "development_exposed":not is_metadata,"exposure_type":"metadata_only" if is_metadata else "historical_design",
        "scientific_content_read":False if is_metadata else None,
        "classification_basis":"explicit_original_metadata_only" if is_metadata else "existing_exposure_event_conservative_prior_exclusion",
        "original_exposure_type":record.get("exposure_type"),"closure_tokens":sorted(tokens),
        "semantic_unknowns":sorted(set(unknown)),
        "actual_identity_automatically_verified":False,
        "original_record_retained_in_SHA_bound_origin":True}
   if unknown:issues.append({"origin_file":rel(p),"origin_jsonl_line":i,"issues":sorted(set(unknown))})
   rows.append(row)
 assert rows
 data=D/"prior_exposure_rows.jsonl"
 write(TASK,rel(data),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows))
 inventory={"task":TASK,"timestamp":ts,"approval_type":"agent_delegated","human_reviewed":False,
  "origin_files_sha256":origins,"normative_exposure_files":[rel(p) for p in normative],
  "derived_projections_excluded_from_duplicate_event_rows":[{"path":rel(p),"sha256":sha(p),"reason":"derived alias/source exposure projection; original normative events separately retained"} for p in excluded],
  "source_row_counts":counts,"row_count":len(rows),"semantic_unknown_rows":issues,
  "semantic_clearance_established":False,"candidate_freshness_automatically_established":False,
  "inventory_status":"all_selected_existing_exposure_jsonl_files_read_and_SHA_bound",
  "scope_bank_modified":False,"new_HTTP":0,"new_MCTS":0}
 put(D/"inventory_provenance.json",inventory)
 data_sha=sha(data)
 for family in ("C","SS"):
  epoch=family+"-E02"
  role=D/("role_A0_inventory_"+family+".json")
  put(role,{"task":TASK,"agent_role":"A0","epoch_id":epoch,"timestamp":ts,"approval_type":"agent_delegated","human_reviewed":False,
   "input_manifest_sha":origins,"output_file_sha":{rel(data):data_sha,rel(D/"inventory_provenance.json"):sha(D/"inventory_provenance.json")},
   "source_evidence_pointers":[{"path":rel(D/"inventory_provenance.json"),"sha256":sha(D/"inventory_provenance.json")}],
   "counts":{"processed":len(rows),"passed":len(rows),"rejected":0,"pending":0},
   "count_unit":"inventory rows retained, not chemical identity decisions",
   "errors":[],"unprocessed":[],"semantic_unknown_rows_retained":len(issues),
   "read_holdout":False,"read_model_outcome":False,"read_new_source_scientific_body":False,
   "chemical_identity_verified":0,"candidate_admitted":0})
  manifest={"task":TASK,"epoch_id":epoch,"family":family,"created_at":ts,
    "coverage_status":"inventory_complete_unknown_semantics_retained",
    "coverage_scope":"existing normative P7 exposure event ledgers; inherited P1-P6 inventory plus later P7 events; derived projections not new exposure events",
    "origin_files_sha256":origins,"exposure_files_sha256":{rel(data):data_sha},"row_count":len(rows),
    "coverage_role":{"path":rel(role),"sha256":sha(role)},
    "semantic_unknowns_retained":len(issues),"chemical_identity_clearance":False,
    "source_prior_read_absence_not_proven_from_negative_token_match":True,
    "future_candidate_still_requires_A6_all_prior_graph_alias_and_named_reviews":True}
  put(D/("prior_exposure_snapshot_"+family+".json"),manifest)
 print(json.dumps({"origin_files":len(files),"normative_files":len(normative),"rows":len(rows),"semantic_unknown_rows":len(issues),"metadata_only_rows":sum(not r["development_exposed"] for r in rows),"new_HTTP":0,"new_MCTS":0},ensure_ascii=False))
if __name__=="__main__":main()
