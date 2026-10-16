"""R50: exact cursor-end checks and literal prior-source triage, metadata only."""
import json,urllib.parse,hashlib
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R49-R37-cursor-completion-v1"
O=B/"C/E02/fresh/C-E02-R50-R49-cursor-boundary-v1"
h.C=ROOT/O;h.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R50-R49-cursor-boundary-v1"
def pre():
 assert not (ROOT/O).exists()
 last={x["original_query_id"]:x for x in lines(R/"page_execution.jsonl")}
 chains=load(R/"chain_plan.json")["chains"]
 plan=[dict(query_id=c["original_query_id"],query=c["original_query"],cursor=last[c["original_query_id"]]["returned_next_cursor"],max_pages=1) for c in chains]
 assert len(plan)==3 and all(x["cursor"] for x in plan)
 files=[R/"precontract.json",R/"chain_plan.json",R/"page_execution.jsonl",R/"metadata_pagination_summary.json",R/"title_enzyme_hints.jsonl",B/"governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl",Path(__file__).resolve().relative_to(ROOT),Path("scripts/task016_p7_c_e02_http.py")]
 put(O/"precontract.v2.json",dict(task=T,at=now(),approval_type="agent_delegated",human_reviewed=False,files_sha256={str(p):sha(p) for p in files},max_HTTP=3,chemical_extraction_permitted=False,query_expansion_allowed=False,no_abstract_or_scientific_body_read=True,no_retry=True,no_redirect=True,stop_on_429=True,source_qualification_or_admission_allowed=False,only_terminal_cursor_check=True))
 put(O/"query_plan.json",dict(task=T,queries=plan,max_HTTP=3))
 print(json.dumps(dict(queries=3,max_HTTP=3)))
def run():
 assert not (ROOT/O/"query_execution.jsonl").exists()
 out=[]
 for p in load(O/"query_plan.json")["queries"]:
  endpoint="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=p["query"],format="json",resultType="lite",pageSize=100,cursorMark=p["cursor"]))
  raw=h.acquire(ROOT/O/"precontract.v2.json",endpoint,"metadata","Exactly one terminal cursor check for completed R49 chain; same lite query and no body read.",object_limit=2*1024**2)
  row=dict(query_id=p["query_id"],requested_cursor=p["cursor"],raw_pointer={k:raw[k] for k in ["path","sha256","bytes"]},HTTP_status=raw["status_code"],status=raw["status"],returned=None,cursor_exhaustion_observed=False)
  if raw["status"]=="available":
   obj=load(Path(raw["path"]));rr=obj.get("resultList",{}).get("result",[])
   row.update(hitCount=obj["hitCount"],returned=len(rr),next_cursor=obj.get("nextCursorMark"),cursor_exhaustion_observed=not rr or not obj.get("nextCursorMark") or obj.get("nextCursorMark")==p["cursor"],metadata_rows_retained=rr)
  out.append(row)
  write(T,str(O/"query_execution.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
  if raw["status_code"]==429:break
 print(json.dumps(dict(executed=len(out),empty=sum(x["returned"]==0 for x in out))))
def finish():
 rr=lines(O/"query_execution.jsonl");assert len(rr)==3
 prior=lines(B/"governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl")
 additions=[B/f"{f}/E02/fresh/{f}-E02-R47-Iris-prospective-qualification-v1/scientific_exposure_reads.jsonl" for f in ("C","SS")]
 # R47 exposures were created after inventory v4 and must remain visible here.
 extra=[x for p in additions for x in lines(p)]
 prior_tokens={t for x in prior if x["development_exposed"] for t in x["closure_tokens"]}
 from scripts.task016_p7_source_alias_closure import closure_tokens
 for x in extra:prior_tokens.update(closure_tokens(x))
 hints=lines(R/"title_enzyme_hints.jsonl");triage=[]
 for x in hints:
  hit=sorted(set(x["official_hint_aliases"])&prior_tokens)
  triage.append(dict(metadata=x["metadata"],official_hint_aliases=x["official_hint_aliases"],known_prior_scientific_token_matches=hit,metadata_status="known_prior_token_hit" if hit else "no_known_prior_token_hit_no_clearance",chemical_scope_disposition=None,full_source_graph_alias_clearance=False,source_qualified=False,fresh_eligible=False,not_selected_is_not_chemical_rejection=True))
 write(T,str(O/"title_hint_prior_triage.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in triage))
 files=[R/"metadata_unique_sources.jsonl",R/"title_enzyme_hints.jsonl",O/"query_execution.jsonl",B/"governance/prior_exposure_inventory_v4/prior_exposure_rows.jsonl"]+additions
 put(O/"metadata_boundary_and_triage_summary.json",dict(task=T,agent_role="A1_metadata_only",at=now(),approval_type="agent_delegated",human_reviewed=False,input_files_sha256={str(p):sha(p) for p in files},source_hint_universe=len(hints),prior_snapshot_rows=len(prior),later_R47_exposure_rows=len(extra),known_prior_literal_hits=sum(bool(x["known_prior_scientific_token_matches"]) for x in triage),no_known_prior_token_hits=sum(not x["known_prior_scientific_token_matches"] for x in triage),cursor_checks=len(rr),all_cursor_exhaustion_observed=all(x["cursor_exhaustion_observed"] for x in rr),new_metadata_observations=sum(x["returned"] or 0 for x in rr),source_qualified=0,structure_complete=0,fresh_admitted=0,complete_chemical_qualification_round=False,source_saturation=False,read_scientific_body=False,scope_modified=False,triage_output_SHA=sha(O/"title_hint_prior_triage.jsonl")))
 print(json.dumps(dict(cursor_checks=len(rr),all_empty=all(x["returned"]==0 for x in rr),prior_hits=sum(bool(x["known_prior_scientific_token_matches"]) for x in triage),unmatched=sum(not x["known_prior_scientific_token_matches"] for x in triage))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"finish":finish}[sys.argv[1]]()
