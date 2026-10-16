"""R49 bounded completion of R37's three already-declared cursor chains, lite only."""
import json,math,urllib.parse,hashlib,re
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,gate,now,can
from scripts import task016_p7_c_e02_http as h
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
OLD=B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1"
O=B/"C/E02/fresh/C-E02-R49-R37-cursor-completion-v1"
h.C=ROOT/O;h.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R49-R37-cursor-completion-v1"
def append(p,x):write(T,str(p),((ROOT/p).read_text() if (ROOT/p).exists() else "")+json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n")
def pre():
 assert not (ROOT/O).exists()
 old=lines(OLD/"query_execution.jsonl");plans=load(OLD/"query_plan.json")["queries"]
 chains=[]
 for row in old:
  if not row.get("next_page_unprocessed"):continue
  assert sha(row["raw_path"])==row["raw_SHA"]
  raw=load(Path(row["raw_path"]));mark=raw.get("nextCursorMark");assert isinstance(mark,str) and mark
  q=next(x for x in plans if x["query_id"]==row["query_id"])
  chains.append(dict(original_query_id=row["query_id"],original_query=q["query"],initial_hit_count=row["hitCount"],first_page_count=row["returned"],first_page_raw=dict(path=row["raw_path"],sha256=row["raw_SHA"]),initial_cursor=mark,max_additional_pages=math.ceil(row["hitCount"]/100)-1,page_size=100))
 assert len(chains)==3 and sum(x["max_additional_pages"] for x in chains)==59
 ga=gate("C")
 inputs=[OLD/"query_execution.jsonl",OLD/"query_plan.json",OLD/"metadata_unique_sources.jsonl",B/"report_snapshots/progress-v29.json",B/"C/E02/stages/G4_SCOPE_FREEZE.json",Path(__file__).resolve().relative_to(ROOT),Path("scripts/task016_p7_c_e02_http.py")]
 inputs += [Path(x["first_page_raw"]["path"]) for x in chains]
 put(O/"precontract.json",dict(task=T,epoch_id="C-E02",family="C",batch_id=O.name,at=now(),approval_type="agent_delegated",human_reviewed=False,G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(p):sha(p) for p in inputs},chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,max_HTTP=59,only_initial_count_bound_cursor_pages=True,no_abstract_or_scientific_body_read=True,metadata_fields=load(OLD/"precontract.json")["metadata_fields"],no_retry=True,no_redirect=True,stop_on_429=True,query_expansion_allowed=False,no_source_saturation_claim=True,one_discovery_route_not_three=True,source_qualification_or_admission_allowed=False,scope_modified=False))
 put(O/"chain_plan.json",dict(task=T,at=now(),chains=chains,max_HTTP=59,unprocessed_original_chains=3))
 print(json.dumps(dict(chains=3,max_HTTP=59,initial_hits_total=sum(x["initial_hit_count"] for x in chains),planned_new_max_objects=5900)))
def url(query,cursor):
 return "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=query,format="json",resultType="lite",pageSize=100,cursorMark=cursor))
def run():
 plan=load(O/"chain_plan.json");fields=load(O/"precontract.json")["metadata_fields"];halt=False
 for chain in plan["chains"]:
  records=[x for x in lines(O/"page_execution.jsonl") if x["original_query_id"]==chain["original_query_id"]]
  cursor=chain["initial_cursor"]
  if records:
   assert [x["additional_page"] for x in records]==list(range(1,len(records)+1))
   for row in records:
    assert row["requested_cursor"]==cursor
    if row["terminal_reason"]!="next_page_available":cursor=None;break
    cursor=row["returned_next_cursor"]
  for number in range(len(records)+1,chain["max_additional_pages"]+1):
   if halt or cursor is None:break
   endpoint=url(chain["original_query"],cursor)
   prior=h.physical_attempts()
   if sum(can(x["url"])==can(endpoint) for x in prior)>=2:
    append(O/"chain_stop_events.jsonl",dict(original_query_id=chain["original_query_id"],at=now(),reason="prior_exact_URL_cap",remaining_after=number-1));break
   raw=h.acquire(ROOT/O/"precontract.json",endpoint,"metadata","Only predeclared R37 cursor continuation, lite bibliography; no new query expansion or chemical content.",object_limit=2*1024**2)
   row=dict(original_query_id=chain["original_query_id"],additional_page=number,requested_cursor=cursor,requested_cursor_SHA=hashlib.sha256(cursor.encode()).hexdigest(),HTTP_status=raw["status_code"],status=raw["status"],raw_pointer={k:raw[k] for k in ["path","sha256","bytes"]},results=[],returned=0,returned_next_cursor=None,terminal_reason="access_pending")
   if raw["status_code"]==429:halt=True;row["terminal_reason"]="host_throttle";cursor=None
   elif raw["status"]=="available":
    response=load(Path(raw["path"]));results=response.get("resultList",{}).get("result",[]);assert isinstance(results,list) and len(results)<=100
    nxt=response.get("nextCursorMark")
    row.update(hitCount=response["hitCount"],returned=len(results),results=[{k:x.get(k) for k in fields} for x in results],returned_next_cursor=nxt)
    exhausted=not results or not nxt or nxt==cursor
    row["terminal_reason"]="cursor_exhausted" if exhausted else "next_page_available"
    cursor=None if exhausted else nxt
   else:cursor=None
   append(O/"page_execution.jsonl",row)
   print(json.dumps(dict(query=chain["original_query_id"],additional_page=number,HTTP_status=row["HTTP_status"],returned=row["returned"],terminal_reason=row["terminal_reason"])),flush=True)
def finish():
 plan=load(O/"chain_plan.json");records=lines(O/"page_execution.jsonl")
 summary=[];total_seen=[]
 for chain in plan["chains"]:
  rr=[x for x in records if x["original_query_id"]==chain["original_query_id"]];assert [x["additional_page"] for x in rr]==list(range(1,len(rr)+1))
  cursor=chain["initial_cursor"]
  for r in rr:
   assert r["requested_cursor"]==cursor and sha(r["raw_pointer"]["path"])==r["raw_pointer"]["sha256"]
   cursor=r["returned_next_cursor"]
   total_seen+=r["results"]
  returned=chain["first_page_count"]+sum(x["returned"] for x in rr)
  initial_count_covered=returned>=chain["initial_hit_count"]
  exhausted=bool(rr) and rr[-1]["terminal_reason"]=="cursor_exhausted"
  summary.append(dict(original_query_id=chain["original_query_id"],initial_hit_count=chain["initial_hit_count"],additional_pages=len(rr),returned_including_first=returned,initial_count_covered=initial_count_covered,cursor_exhaustion_observed=exhausted,remaining_cursor_unprocessed=bool(rr and rr[-1]["returned_next_cursor"] and rr[-1]["terminal_reason"]=="next_page_available"),bounded_plan_terminal=len(rr)==chain["max_additional_pages"] or exhausted,dynamic_hit_counts=sorted(set(x.get("hitCount") for x in rr if x.get("hitCount") is not None))))
 old=lines(OLD/"metadata_unique_sources.jsonl")
 def key(x):return "doi:"+x["doi"].casefold() if x.get("doi") else str(x.get("source"))+"-"+str(x.get("id"))
 existing={key(x["metadata"]) for x in old};index={}
 for page in records:
  for m in page["results"]:
   k=key(m);alias={"doi:"+m["doi"].casefold()} if m.get("doi") else set()
   if m.get("pmcid"):alias.add("article:"+m["pmcid"].upper())
   if m.get("pmid"):alias.add("pmid:"+m["pmid"])
   if m.get("source")=="MED" and m.get("id"):alias.add("pmid:"+m["id"])
   index.setdefault(k,dict(metadata=m,official_hint_aliases=sorted(alias),observed_pages=[],present_in_original_R37=k in existing,scientific_qualification=None,fresh_eligibility=None))
   index[k]["observed_pages"].append(dict(query_id=page["original_query_id"],additional_page=page["additional_page"]))
 out=O/"metadata_unique_sources.jsonl"
 write(T,str(out),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in index.values()))
 # Candidate projection is title-only; no source is chemically rejected from a title.
 hints=[]
 for row in index.values():
  title=row["metadata"]["title"] or ""
  if re.search(r"glycosyltransferase|glucosyltransferase|C.glycos|C.glucos|isovitexin|isoscoparin|isoorientin",title,re.I):
   hints.append(dict(row,title_only_selection=True,chemical_scope_decision=None))
 write(T,str(O/"title_enzyme_hints.jsonl"),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in hints))
 value=dict(task=T,agent_role="A1_metadata_only",at=now(),approval_type="agent_delegated",human_reviewed=False,chains=summary,HTTP=len(records),observations=len(total_seen),unique_metadata=len(index),unique_new_to_R37=sum(not x["present_in_original_R37"] for x in index.values()),title_only_enzyme_hints=len(hints),all_bounded_plans_terminal=all(x["bounded_plan_terminal"] for x in summary),scientific_admitted=0,fresh_admitted=0,complete_full_qualification_round=False,source_saturation=False,scope_modified=False,metadata_output_SHA=sha(out))
 put(O/"metadata_pagination_summary.json",value)
 print(json.dumps({k:value[k] for k in ["HTTP","observations","unique_metadata","unique_new_to_R37","title_only_enzyme_hints","all_bounded_plans_terminal"]}))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"finish":finish}[sys.argv[1]]()
