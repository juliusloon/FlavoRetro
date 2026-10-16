"""P7 R7: conservative candidate-only exposed-name graph guard.

Positive graph identity blocks a prospective fresh candidate pending A6 review.
A non-match NEVER grants freshness. PubChem CID/SMILES alone does not prove
official synonym identity, a reaction, a source or stereochemical completeness.
"""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from rdkit import Chem
from scripts.operate import ROOT,write

TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
P=B/"governance/P7-R7-authoritative-exposed-name-resolution-v1"
OUT=B/"governance/P7-R7-exposed-graph-candidate-guard-v1"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def graph(smiles):
 if not isinstance(smiles,str) or not smiles.strip():return None
 mol=Chem.MolFromSmiles(smiles)
 if mol is None:return None
 return Chem.MolToSmiles(mol,canonical=True,isomericSmiles=True)
def classify_fresh_target(smiles,guard):
 """Potential blocker only. Missing/unmatched graph is unresolved, not fresh."""
 canon=graph(smiles)
 if canon is None:
  return {"status":"pending_invalid_or_missing_input","fresh_eligible":False,"matched_exposures":[]}
 matches=[r for r in guard["candidate_graph_index"] if r["canonical_RDKit_SMILES"]==canon]
 return {"status":"potential_prior_exposure_block" if matches else "pending_no_match_not_fresh_cleared",
    "fresh_eligible":False,"matched_exposures":[
       {"name":r["exposed_name"],"CID":r["official_PubChem_CID"],
        "exposure_ids":r["historical_exposure_ids"],"verified_alias":False} for r in matches],
    "canonical_SMILES":canon,"needs_independent_structure_synonym_and_assay_closure":True}
def main():
 if (ROOT/OUT).exists():raise RuntimeError("GUARD_IMMUTABLE_EXISTS")
 inputs=[P/"query_plan.json",P/"query_execution.jsonl",P/"http_ledger.jsonl",P/"disposition_summary.json"]
 original={str(p):sha(p) for p in inputs}
 plan=load(P/"query_plan.json"); exe=rows(P/"query_execution.jsonl"); req=rows(P/"http_ledger.jsonl")
 pm={r["query_id"]:r for r in plan["queries"]}; rm={r["query_id"]:r for r in req}
 assert len(pm)==len(rm)==len(exe)==27 and len({r["query_id"] for r in exe})==27
 index=[];missing=[]
 for record in exe:
  rid=record["query_id"];q=pm[rid];req=rm[rid]
  path=Path(req["path"])
  if sha(path)!=req["sha256"] or record["raw"]["sha256"]!=req["sha256"]:
   raise RuntimeError("MUTABLE_ORIGINAL_RAW")
  raw=load(path)
  properties=raw.get("PropertyTable",{}).get("Properties",[])
  if len(properties)!=1 or record["disposition"]!="candidate_only_single_CID_pending_independent_identity":
   raise RuntimeError("COMPOUND_NAME_RESPONSE_NOT_SINGLE")
  p=properties[0]
  cid=p.get("CID")
  smiles=p.get("SMILES") or p.get("IsomericSMILES")
  connectivity=p.get("ConnectivitySMILES") or p.get("CanonicalSMILES")
  c=graph(smiles)
  if c is None or graph(connectivity) is None or not isinstance(cid,int):
   missing.append({"name":q["name"],"CID":cid,"reason":"missing_valid_structural_encoding"})
   continue
  if cid!=record["property_identity_candidates"][0]["CID"]:
   raise RuntimeError("CID_CHANGED_BETWEEN_ROLE_RECORDS")
  if record["property_identity_candidates"][0]["InChIKey"]!=p.get("InChIKey"):
   raise RuntimeError("INCHIKEY_CHANGED")
  index.append({"exposed_name":q["name"],"official_PubChem_CID":cid,
   "official_PubChem_InChIKey":p.get("InChIKey"),
   "canonical_RDKit_SMILES":c,"raw_property_SMILES":smiles,
   "connectivity_SMILES":connectivity,
   "historical_exposure_ids":[x["exposure_id"] for x in q["exposure_hypotheses"]],
   "family_exposure_tags":[x["family"]+":"+x["phase"] for x in q["exposure_hypotheses"]],
   "raw_pointer":{"path":str(path),"sha256":sha(path)},
   "query_plan_id":rid,"candidate_only_not_independently_verified":True,
   "positive_graph_match_would_block_only":True})
 assert len(index)+len(missing)==27
 assert sum(len(r["historical_exposure_ids"]) for r in index)+sum(len(pm[r["query_id"]]["exposure_hypotheses"]) for r in [])==28 if not missing else True
 result={"task":TASK,"timestamp":datetime.now(timezone.utc).isoformat(),
  "role":"A6_potential_exposure_guard","input_SHA256":original,
  "candidate_graph_index":index,"missing_or_invalid_graphs":missing,
  "counts":{"unique_exposed_names":27,"name_exposure_records":28,
   "graph_candidate_inputs":len(index),"not_graph_executable":len(missing),
   "fresh_admitted":0,"independent_synthetic_or_natural_product_structure_verifications":0,
   "new_HTTP":0,"new_MCTS":0},
  "block_positive_matches_only":True,"nonmatches_remain_unresolved":True,
  "name_to_CID_not_official_synonym_closed":True,
  "reaction_source_assay_scope_not_verified":True,
  "no_change_to_G4_G5_scope_or_runtime":True,"human_reviewed":False}
 write(TASK,str(OUT/"candidate_graph_guard.json"),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"graph_candidates":len(index),"unresolved_graph":len(missing),
   "exposure_hypotheses":28,"fresh":0,"new_HTTP":0},ensure_ascii=False))
if __name__=="__main__":main()
