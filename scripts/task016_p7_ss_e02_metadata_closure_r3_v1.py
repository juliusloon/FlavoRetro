#!/usr/bin/env python3
"""P7 SS-E02 R3 metadata-only identifier closure; never opens scientific raw files."""
from __future__ import annotations
import hashlib,json,re,sys
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
TASK="TASK-016-P7"
BASE="outputs/task016-p7/v1/"
OUT=BASE+"SS/E02/fresh/SS-E02-R3-metadata-closure-v1/"
SELF="scripts/task016_p7_ss_e02_metadata_closure_r3_v1.py"
HINTS=[BASE+"SS/E02/fresh/SS-E02-R1-metadata/discovery_dispositions.jsonl",
       BASE+"SS/E02/fresh/SS-E02-R2-metadata/discovery_dispositions.jsonl"]
REF=BASE+"SS/E02_design/reference_discovery_r2/"
A3=REF+"A3_publication_identity_v1/six_original_publication_identity_checks.json"
ALLOCATION=REF+"prechemical_read_allocation.json"
RAW=REF+"raw_closeout_v1/raw_only_source_intake_manifest.json"
NAMEBASE=BASE+"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/"
NAMELEDGER=NAMEBASE+"permanent_unverified_name_exposures.jsonl"
NAMEMANIFEST=NAMEBASE+"permanent_exposure_manifest.json"
FIVE=["PMC4494776","PMC4762388","PMC9786081","PMC12313340","PMC10940802"]
SINGLE_ID_FIELDS={
 "doi":"doi","DOI":"doi","source_doi":"doi",
 "pmid":"pmid","PMID":"pmid","source_pmid":"pmid",
 "pmcid":"article","PMCID":"article","source_pmcid":"article"}
TOKEN_FIELDS={"closure_tokens","source_tokens","source_alias_tokens","permanent_source_tokens","exact_identifier_tokens"}
POSITIVE_FLAGS={"development_exposed","permanent_design_exposed","permanent_exposed","exposed",
 "permanent_source_and_graph_exposure","conservative_source_design_exposed","actual_original_chemical_review",
 "actual_original_chemistry_read","actual_original_science_read","chemical_original_content_read",
 "chemical_original_body_read","chemical_information_read","SI_chemical_reviewed","metadata_abstract_chemistry_observed"}
CONTAINERS={"sources","records","source_binding","source_support","source_identity","source_publication",
 "metadata_hint","source_hint","original_literals","MED_literals","ids","items","source_exposures",
 "input_pointers","raw_objects","raw_originals","originals","source_originals","source_records"}
BIB={"title","journal","year","volume","issue","pages","pageInfo","article_number","first_page","last_page","publisher","publication_dates"}
def now():return datetime.now(timezone.utc).isoformat()
def sha(name):
 p=ROOT/name;h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(1048576),b""):h.update(c)
 return h.hexdigest()
def load(name):return json.loads((ROOT/name).read_text())
def rows(name):
 return [json.loads(x) for x in (ROOT/name).read_text().splitlines() if x.strip()]
def save(name,obj):
 if (ROOT/name).exists():raise RuntimeError("immutable output exists: "+name)
 write(TASK,name,json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
def save_rows(name,values):
 if (ROOT/name).exists():raise RuntimeError("immutable output exists: "+name)
 write(TASK,name,"".join(json.dumps(x,ensure_ascii=False,sort_keys=True,allow_nan=False)+"\n" for x in values))
def norm(kind,v):
 if v is None or v=="":return None
 if kind=="pmid" and isinstance(v,int) and not isinstance(v,bool):v=str(v)
 if not isinstance(v,str):raise ValueError("invalid "+kind+" type")
 v=v.strip()
 if kind=="doi":
  v=re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)","",v,flags=re.I).lower()
  if re.fullmatch(r"10\.[0-9]{4,9}/[^\s<>]+",v):return "doi:"+v
 if kind=="article" and re.fullmatch(r"PMC[1-9]\d*",v,re.I):return "article:"+v.upper()
 if kind=="pmid" and re.fullmatch(r"(?:PMID:\s*)?[1-9]\d*",v,re.I):return "pmid:"+re.sub(r"^PMID:\s*","",v,flags=re.I)
 raise ValueError("malformed "+kind+" identifier")
def strict_token(v):
 if not isinstance(v,str):return None
 low=v.lower()
 for prefix,kind in (("doi:","doi"),("article:","article"),("pmcid:","article"),("pmid:","pmid")):
  if low.startswith(prefix):
   try:return norm(kind,v.split(":",1)[1])
   except ValueError:return None
 # Other tokens, including all graph/name/reaction tokens, are never output or interpreted.
 return None
def tokens(node,errors,pointer):
 out=set()
 for field,kind in SINGLE_ID_FIELDS.items():
  if field in node and node[field] not in (None,""):
   try:out.add(norm(kind,node[field]))
   except ValueError:errors.append({"pointer":pointer+"/"+field,"error":"invalid_identifier_field"})
 sid=node.get("source_id")
 if isinstance(sid,str) and re.fullmatch(r"PMC[1-9]\d*",sid,re.I):out.add(norm("article",sid))
 for field in TOKEN_FIELDS:
  vs=node.get(field,[])
  if isinstance(vs,list):
   out.update(t for v in vs if (t:=strict_token(v)) is not None)
 return out
def exposure_paths():
 root=ROOT/BASE;out=[]
 for p in sorted(root.rglob("*")):
  if not p.is_file() or p.suffix not in {".json",".jsonl"}:continue
  r=p.relative_to(ROOT).as_posix()
  if any(x in r for x in ("/report_snapshots/","/report_audit/","/report_review/","/verification", "/superseded/","/fresh/SS-E02-R3-metadata-closure-v1/")):continue
  if r==BASE+"exposure_ledger.jsonl":out.append(r);continue
  if not any(r.startswith(BASE+x) for x in ("C/","SS/","epochs/")):continue
  if "expos" not in p.name.lower():continue
  # Source/identifier projections only; timeline records do not add source exposure.
  if "timeline" in p.name or "exposure_triage" in p.name or "metadata_exposure_screen" in p.name:continue
  if p.name=="permanent_exposure_manifest.json" or p.suffix==".jsonl" or any(x in p.name for x in
    ("permanent_design_source_exposure","actual_source_exposure","actual_source_and_graph_exposure",
     "first_scientific_source_read_exposure","permanent_postfreeze_source_exposure","fresh_abstract_chemical_exposure",
     "additional_SS_actual_exposure_pending","actual_first_scientific_read","actual_original_read_design_exposure")):
   out.append(r)
 return sorted(set(out))
def fixed_metadata_paths():
 paths=[A3,ALLOCATION,RAW,NAMELEDGER,NAMEMANIFEST,
  BASE+"SS/E02/stages/G4_SCOPE_FREEZE.json",BASE+"SS/E02/source_identity.json",
  BASE+"SS/E02_design/reference_discovery_r2/raw_closeout_v1/role_A2_raw_only_intake_manifest.json",
  BASE+"SS/E02/fresh/SS-E02-R2-PMC11125054-A3/A3_publication_identity.json"]
 for parent in (BASE+"SS/E02/fresh/SS-E02-R1-metadata/",BASE+"SS/E02/fresh/SS-E02-R2-metadata/"):
  paths.extend(parent+n for n in ("query_plan.json","round_result.json","raw_manifest.json"))
 for name in ("SS-E02-R1","SS-E02-R2-metadata"):
  paths.append(BASE+"SS/E02/stages/batches/"+name+"/G5_FRESH_HOLDOUT_ACQUIRE.json")
 return paths
def pre():
 inputs=sorted(set(HINTS+exposure_paths()+fixed_metadata_paths()+[SELF]))
 for p in inputs:
  if not (ROOT/p).is_file():raise RuntimeError("missing input: "+p)
 manifest={
 "task":TASK,"epoch_id":"SS-E02","agent_role":"A2/A6 metadata-only identifier closure scout",
 "approval_type":"agent_delegated","timestamp":now(),"input_sha256":{p:sha(p) for p in inputs},
 "input_classes":{"metadata_discovery":HINTS,"source_exposure_projection":exposure_paths(),
  "fixed_metadata_front_and_manifests":fixed_metadata_paths()},
 "field_projection":{"identifier_fields":SINGLE_ID_FIELDS,"token_fields_identifier_prefixes_only":sorted(TOKEN_FIELDS),
  "allowed_metadata_containers":sorted(CONTAINERS),"bibliographic_fields":sorted(BIB),
  "exposure_flags":sorted(POSITIVE_FLAGS),"never_interpret_or_output":["molecular graph","SMILES","reaction tokens","structure evidence","abstract/body","figures","model outcomes"]},
 "merge_rule":"Exact normalized DOI/PMCID/PMID sharing only; title is display metadata, never merge or freshness proof. Alias cooccurrence must have at most one value in each identifier namespace.",
 "stops":["input SHA drift","missing required discovery metadata flags","duplicate record IDs","identifier conflict","51-row conservation failure","output already exists","needs HTTP or scientific-content read"],
 "output_contract":["identifier_clusters.json","source_exposure_projection.jsonl","five_precollected_source_check.json",
  "metadata_A3_queue.json","metadata_G5_pending_queue.json","closure_summary.json","role_A2_A6_manifest.json"],
 "five_source_rule":"Keep R2 raw-only unread allocation separate from historical/project exposure; inherited A3 identity is metadata evidence only.",
 "name_hypothesis_rule":"Root 9 preG4 unverified hypotheses are mandatory future name-identity inputs; do not perform source-token matching on null IDs or claim name matching executed.",
 "scope_mutation":False,"new_HTTP":0,"new_MCTS":0,"scientific_qualification":False,"fresh_admission":0,
 "isolation_incident":{"historical_graph_strings_incidentally_visible":True,
  "pointer":"operations/command-4269.log","pointer_status":"confirmed exact diagnostic command log",
  "cause":"initial schema diagnostic printed unfiltered historical closure_tokens first-two-row samples",
  "fresh_scientific_originals_read":False,"graph_interpretation_or_use":False,
  "parent_authorized_repair":"continue with identifier-only whitelist; retain incident; do not claim never saw graphs"}}
 save(OUT+"pre_execution_manifest.json",manifest)
 print(json.dumps({"registered":OUT+"pre_execution_manifest.json","inputs":len(inputs),"exposure_files":len(exposure_paths())}))
def run():
 plan=load(OUT+"pre_execution_manifest.json")
 for p,h in plan["input_sha256"].items():
  if sha(p)!=h:raise RuntimeError("input SHA drift: "+p)
 errors=[];projection=[];aliases=[];exposure_index=defaultdict(list);stats={};unprocessed=[]
 def add_alias(ts,pointer,role):
  if not ts:return
  if any(n>1 for n in Counter(t.split(":",1)[0] for t in ts).values()):
   unprocessed.append({"pointer":pointer,"reason":"multiple IDs in one namespace; no alias merge","identifier_tokens":sorted(ts)})
   return
  aliases.append({"identifier_tokens":sorted(ts),"pointer":pointer,"role":role})
 def walk(v,pointer,inherited=False,force=False):
  if isinstance(v,list):
   for i,x in enumerate(v):walk(x,pointer+"/"+str(i),inherited,force)
   return
  if not isinstance(v,dict):return
  direct_positive=any(v.get(f) is True for f in POSITIVE_FLAGS)
  if v.get("chemically_read_at"):direct_positive=True
  exposed=inherited or direct_positive or force
  ts=tokens(v,errors,pointer)
  if ts:
   item={"pointer":pointer,"identifier_tokens":sorted(ts),"known_exposed":exposed,
    "positive_exposure_flags":sorted(k for k in POSITIVE_FLAGS if v.get(k) is True),
    "exposure_type":v.get("exposure_type") if isinstance(v.get("exposure_type"),str) else None,
    "source_id":v.get("source_id") if isinstance(v.get("source_id"),str) and re.fullmatch(r"PMC[1-9]\d*",v["source_id"],re.I) else None}
   projection.append(item)
   if exposed:
    for t in ts:exposure_index[t].append(pointer)
   add_alias(ts,pointer,"source_exposure_single_publication_metadata")
  elif direct_positive and not any(k in v for k in CONTAINERS):
   unprocessed.append({"pointer":pointer,"reason":"exposed record has no strict source identifier; graph/name tokens deliberately unprocessed"})
  for key in CONTAINERS:
   if key in v and isinstance(v[key],(dict,list)):walk(v[key],pointer+"/"+key,exposed,False)
 for p in plan["input_classes"]["source_exposure_projection"]:
  before=len(projection);d=rows(p) if p.endswith(".jsonl") else load(p)
  # Actual chemical-review log has a source-level timestamp rather than development_exposed.
  force=p.endswith("/fresh_supplemental_chemical_exposure_log.jsonl")
  walk(d,p+"#",False,force)
  stats[p]={"top_level_records":len(d) if isinstance(d,list) else 1,"source_identifier_projection_rows":len(projection)-before}
 hints=[]
 for p,expected in zip(HINTS,[23,28]):
  rs=rows(p)
  if len(rs)!=expected:raise RuntimeError("discovery row conservation mismatch")
  for i,r in enumerate(rs):
   if r.get("metadata_only") is not True or r.get("evidence_eligible") is not False:raise RuntimeError("non-metadata discovery row")
   sh=r.get("source_hint")
   if not isinstance(sh,dict):raise RuntimeError("missing source_hint")
   ts=tokens(sh,errors,p+"#/"+str(i)+"/source_hint")
   add_alias(ts,p+"#/"+str(i)+"/source_hint","postfreeze_discovery")
   hints.append({"record_id":r["record_id"],"input_pointer":p+"#/"+str(i),"tokens":ts,
    "bibliographic_metadata":{k:sh[k] for k in BIB if k in sh},"source_hint_ids":{k:sh[k] for k in SINGLE_ID_FIELDS if k in sh}})
 if len(hints)!=51 or len({r["record_id"] for r in hints})!=51:raise RuntimeError("discovery unique record conservation failure")
 a3=load(A3);a3_records=a3["records"];a3_index={}
 for i,r in enumerate(a3_records):
  original=r["original_literals"];med=r["MED_literals"]
  ids=original["ids"];ts=tokens(ids,errors,A3+"#/records/"+str(i)+"/original_literals/ids")|tokens(med,errors,A3+"#/records/"+str(i)+"/MED_literals")
  ts.add(norm("article",r["source_id"]))
  add_alias(ts,A3+"#/records/"+str(i),"inherited_A3_front_metadata_only")
  a3_index[r["source_id"]]={"tokens":ts,"row":r,"index":i}
 # Union identifier aliases only. No title, graph, name or reaction relation is used.
 parent={}
 def find(x):
  parent.setdefault(x,x)
  if parent[x]!=x:parent[x]=find(parent[x])
  return parent[x]
 def join(x,y):
  a,b=find(x),find(y)
  if a!=b:parent[max(a,b)]=min(a,b)
 for a in aliases:
  ts=a["identifier_tokens"]
  for t in ts:find(t)
  for t in ts[1:]:join(ts[0],t)
 comps=defaultdict(set)
 for t in list(parent):comps[find(t)].add(t)
 grouped=defaultdict(list)
 for h in hints:
  key=find(sorted(h["tokens"])[0]) if h["tokens"] else "unbound:"+h["record_id"]
  grouped[key].append(h)
 clusters=[]
 for i,(key,hs) in enumerate(sorted(grouped.items(),key=lambda kv:min(h["record_id"] for h in kv[1])),1):
  allts=comps[key] if key in comps else set()
  known=sorted(t for t in allts if t in exposure_index)
  ns=Counter(t.split(":",1)[0] for t in allts)
  conflicts=sorted(k for k,n in ns.items() if n>1)
  # Multi-namespace alias conflicts are conservatively unknown and require A3 reconciliation.
  status="known_exposed" if known else "unknown_identity_or_project_exposure"
  a3matches=[sid for sid,a in a3_index.items() if a["tokens"] & allts]
  raw=[]
  for sid in a3matches:
   ptr=a3_index[sid]["row"]["original_pointer"];path=ptr["path"];p=ROOT/path
   raw.append({"source_id":sid,"path":path,"declared_sha256":ptr["sha256"],"local_exists":p.is_file(),
    "local_size_bytes":p.stat().st_size if p.is_file() else None,"contents_not_opened":True,"sha_not_recomputed_by_this_role":True})
  if not raw:raw=[{"availability":"not_established_by_bound_metadata_projection","absence_not_claimed":True}]
  evidence=[{"identifier_token":t,"source_projection_pointers":sorted(set(exposure_index[t]))} for t in known]
  clusters.append({"cluster_id":"SS-E02-R3-ID-%03d"%i,"record_ids":[h["record_id"] for h in hs],"metadata_row_count":len(hs),
   "normalized_source_identifiers":sorted(allts),"discovery_identifier_tokens":sorted(set().union(*(h["tokens"] for h in hs))),
   "bibliographic_metadata_variants":[{"record_id":h["record_id"],**h["bibliographic_metadata"]} for h in hs],
   "source_exposure_status":status,"known_exposure_credentials":evidence,"identifier_namespace_conflicts":conflicts,
   "inherited_A3_identity_source_ids":a3matches,"original_availability":raw,
   "fresh_admitted":False,"scientific_qualification":False,
   "next_gate":"exclude_from_fresh_metadata_queue_preserve_for_design" if known else "A3_identity_alias_and_complete_project_exposure_reconciliation_pending",
   "future_name_identity_gate_required":True})
 five=[]
 rawmanifest=load(RAW);raw_by_id={r["source_id"]:r for r in rawmanifest["sources"]}
 allocation=load(ALLOCATION)
 if allocation["raw_only_unread_source_ids"]!=FIVE:raise RuntimeError("five allocation mismatch")
 for sid in FIVE:
  a=a3_index[sid];r=a["row"];ts=comps[find(sorted(a["tokens"])[0])];known=sorted(t for t in ts if t in exposure_index)
  ptr=r["original_pointer"];p=ROOT/ptr["path"];rm=raw_by_id[sid]
  five.append({"source_id":sid,"normalized_source_identifiers":sorted(ts),
   "bibliographic_front":{k:r["original_literals"].get(k) for k in BIB if k in r["original_literals"]},
   "A3_existing_metadata_only_identity":{"publication_identity_passed":r.get("publication_identity_passed"),
    "checks":r.get("checks"),"chemistry_body_or_graph_read_by_A3":r.get("chemistry_body_or_graph_read"),
    "input_pointer":A3+"#/records/"+str(a["index"]),"original_front_pointer":ptr,"MED_pointer":r["official_MED_pointer"],
    "current_role_independent_reverification":False},
   "raw_allocation":{"declared_unread_in_reference_discovery_r2":True,"scientific_body_read_in_raw_manifest":rm.get("scientific_body_read"),
    "raw_original_acquisition_is_not_chemical_exposure":True,"input_pointer":RAW+"#/sources/"+str(rawmanifest["sources"].index(rm))},
   "original_availability":{"path":ptr["path"],"declared_sha256":ptr["sha256"],"local_exists":p.is_file(),
    "local_size_bytes":p.stat().st_size if p.is_file() else None,"main_PDF_versions":rm.get("original_main_PDF_versions"),
    "XML_versions":rm.get("original_body_XML_versions"),"attachments":rm.get("attachments"),"scientific_bytes_not_opened":True},
   "project_source_exposure_status":"known_exposed" if known else "unknown_identity_or_project_exposure",
   "known_exposure_credentials":[{"identifier_token":t,"projection_pointers":sorted(set(exposure_index[t]))} for t in known],
   "historical_exposure_blocks_fresh":bool(known),"fresh_admitted":False,"scientific_qualification":False,
   "required_next_gate":"preserve_in_design_only" if known else "A3_alias_recheck_plus_explicit_G5_timing_closure_and_name_identity_gate_before_any_science_read"})
 if errors:raise RuntimeError("invalid identifiers; stop before outputs: "+json.dumps(errors))
 a3_queue=[r for r in clusters if r["source_exposure_status"]!="known_exposed"]
 g5_queue=[r for r in five if r["project_source_exposure_status"]!="known_exposed"]
 nknown=sum(c["source_exposure_status"]=="known_exposed" for c in clusters)
 counts={"R1_metadata_rows":23,"R2_metadata_rows":28,"metadata_rows":len(hints),"identifier_clusters":len(clusters),
  "known_exposed_clusters":nknown,"unknown_clusters":len(clusters)-nknown,
  "known_exposed_metadata_rows":sum(c["metadata_row_count"] for c in clusters if c["source_exposure_status"]=="known_exposed"),
  "unknown_metadata_rows":sum(c["metadata_row_count"] for c in clusters if c["source_exposure_status"]!="known_exposed"),
  "precollected_five":len(five),"precollected_known_exposed":sum(r["historical_exposure_blocks_fresh"] for r in five),
  "precollected_unknown":len(g5_queue),"source_projection_rows":len(projection),"exposure_input_files":len(stats),
  "new_HTTP":0,"new_MCTS":0,"fresh_admitted":0,"scientific_ABE_cells":0}
 assert counts["known_exposed_clusters"]+counts["unknown_clusters"]==counts["identifier_clusters"]
 assert counts["known_exposed_metadata_rows"]+counts["unknown_metadata_rows"]==51
 assert counts["precollected_known_exposed"]+counts["precollected_unknown"]==5
 save_rows(OUT+"source_exposure_projection.jsonl",projection)
 save(OUT+"identifier_clusters.json",{"task":TASK,"epoch_id":"SS-E02","counts":counts,"clusters":clusters,"alias_bindings":aliases})
 save(OUT+"five_precollected_source_check.json",{"task":TASK,"scope_unchanged":True,"sources":five,"chemical_read_by_this_role":False})
 save(OUT+"metadata_A3_queue.json",{"task":TASK,"rows":a3_queue,"source_qualified_fresh_count":0,"no_scientific_qualification":True})
 save(OUT+"metadata_G5_pending_queue.json",{"task":TASK,"precollected_unknown_sources":g5_queue,"no_G5_freeze_created":True,
  "required_inputs":[NAMELEDGER,NAMEMANIFEST],"name_identity_matching_executed":False,
  "reason":"Missing source/graph IDs in preG4 hypotheses cannot be checked with an identifier-token helper."})
 save(OUT+"closure_summary.json",{"task":TASK,"timestamp":now(),"counts":counts,"input_stats":stats,
  "conservation_passed":True,"source_saturation":False,"cross_database_publication_count_authoritatively_verified":None,
  "unknown_is_not_fresh":True,"title_merge":False,"science_body_read":False,"model_outcomes_read":False,"scope_modified":False,
  "unprocessed_metadata_exposure_items":unprocessed,"errors":[],"historical_graph_string_incident_disclosed":True})
 files=["source_exposure_projection.jsonl","identifier_clusters.json","five_precollected_source_check.json","metadata_A3_queue.json","metadata_G5_pending_queue.json","closure_summary.json"]
 save(OUT+"role_A2_A6_manifest.json",{"task":TASK,"epoch_id":"SS-E02","agent_role":"A2/A6 metadata-only identifier closure scout",
  "approval_type":"agent_delegated","timestamp":now(),"input_manifest_sha256":sha(OUT+"pre_execution_manifest.json"),
  "input_files_sha256":plan["input_sha256"],"output_file_sha256":{OUT+f:sha(OUT+f) for f in files},
  "counts":{"processed":len(clusters),"passed":0,"rejected":nknown,"pending":len(clusters)-nknown},
  "discovery_row_conservation":counts,"errors":[{"type":"historical_graph_strings_incidentally_visible","basis":"unfiltered historical closure_tokens in one schema diagnostic; no interpretation/use; parent authorized field-whitelist repair"}],
  "unprocessed":unprocessed,"source_evidence_pointers":[A3,RAW,ALLOCATION],
  "read_holdout_scientific_content":False,"read_scientific_body_or_figures":False,"read_model_outcome":False,
  "read_historical_graph_strings_incidentally":True,"read_fresh_chemical_graph":False,
  "graph_interpretation_or_use":False,"metadata_graph_fields_deserialized_but_never_projected_after_repair":True,
  "five_scientific_originals_opened":False,"new_HTTP":0,"new_MCTS":0,"scope_modified":False,
  "new_G5_freeze":False,"new_G6_admission":0,"human_reviewed":False,"independent_chemical_validation":False,
  "future_root_name_identity_gate_input_bound":True,"root_hypothesis_name_matching_executed":False})
 print(json.dumps(counts,ensure_ascii=False))
if __name__=="__main__":{"pre":pre,"run":run}[sys.argv[1]]()
