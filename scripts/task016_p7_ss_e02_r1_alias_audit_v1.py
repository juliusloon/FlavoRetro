#!/usr/bin/env python3
"""P7 SS-E02 post-G4 metadata-only DOI/PMCID/PMID alias/exposure triage.
Read identifiers and prior exposure markers ONLY, never fresh chemistry, model
outcomes or molecular graph fields. Conservative, no scientific admission.
"""
from __future__ import annotations
import hashlib, json, re, sys
from collections import defaultdict,Counter
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,ContractError
TASK="TASK-016-P7"
B="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R1-metadata/"
O="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R1-alias-audit-v1/"
G="outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R1/G5_FRESH_HOLDOUT_ACQUIRE.json"
SELF="scripts/task016_p7_ss_e02_r1_alias_audit_v1.py"
OLD=[
 "outputs/task016-p7/v1/exposure_ledger.jsonl",
 "outputs/task016-p7/v1/SS/E01_permanent_exposure/v2/permanent_chemical_exposure_ledger.jsonl",
 "outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/Petunia_A6_v1/permanent_11_observed_graph_exposures.jsonl",
 "outputs/task016-p7/v1/SS/E02_design/new_source_actual_exposure_custodian_v3/permanent_exposure_ledger.jsonl",
 "outputs/task016-p7/v1/SS/E02_design/second_acceptor_graph_identity_v1/permanent_observed_graph_and_synonym_exposures.jsonl"]
INPUTS=OLD+[B+"discovery_dispositions.jsonl",B+"query_plan.json",
 B+"round_result.json",B+"metadata_exposure_screen.json",G,SELF]
def sha(p):return sha_file(ROOT/p)
def now():return datetime.now(timezone.utc).isoformat()
def save(path,obj):
 if (ROOT/path).exists():raise ContractError("immutable artifact already exists: "+path)
 write(TASK,path,json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def readjson(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def doi(val):
 if val is None or val=="":return None
 if not isinstance(val,str):raise ContractError("DOI type invalid")
 val=re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)","",val.strip(),flags=re.I)
 val=val.rstrip(".,;)").lower()
 if not re.fullmatch(r"10\.[0-9]{4,9}/[^\s<>]+",val):raise ContractError("malformed DOI")
 return "doi:"+val
def pmcid(val):
 if val is None or val=="":return None
 if not isinstance(val,str):raise ContractError("PMCID type invalid")
 m=re.fullmatch(r"PMC([1-9]\d*)",val.strip(),flags=re.I)
 if not m:raise ContractError("malformed PMCID")
 return "article:PMC"+m.group(1)
def pmid(val):
 if val is None or val=="":return None
 if isinstance(val,bool) or not isinstance(val,(str,int)):raise ContractError("PMID type invalid")
 m=re.fullmatch(r"(?:PMID:\s*)?([1-9]\d*)",str(val).strip(),re.I)
 if not m:raise ContractError("malformed PMID")
 return "pmid:"+m.group(1)
def tokens_from_hint(h):
 res=set()
 for f,fn in (("DOI",doi),("PMCID",pmcid),("PMID",pmid)):
  v=fn(h.get(f))
  if v:res.add(v)
 return res
def tokens_from_exposure(row):
 out=set()
 for t in row.get("closure_tokens",[]):
  if not isinstance(t,str):raise ContractError("invalid old token")
  if t.lower().startswith("doi:"):
   v=doi(t)
   if v:out.add(v)
  elif t.lower().startswith(("article:pmc","pmcid:pmc")):
   v=pmcid(t.split(":",1)[1])
   if v:out.add(v)
  elif t.lower().startswith("pmid:"):
   v=pmid(t.split(":",1)[1])
   if v:out.add(v)
 for f,fn in (("doi",doi),("pmcid",pmcid),("pmid",pmid)):
  v=fn(row.get(f))
  if v:out.add(v)
 for f in ("source_id",):
  value=row.get(f)
  if isinstance(value,str) and re.fullmatch("PMC[1-9][0-9]*",value,re.I):
   out.add(pmcid(value))
 return out
def pre():
 verify_stage_chain(G,sha(G))
 for name in INPUTS:
  if not (ROOT/name).is_file():raise ContractError("missing input "+name)
 assert not (ROOT/(O+"pre_execution_manifest.json")).exists()
 save(O+"pre_execution_manifest.json",dict(task=TASK,epoch_id="SS-E02",
  role="A6 metadata-identity screen only; NOT G6 scientific admission",
  timestamp=now(),source_stage_path=G,stage_sha256=sha(G),
  code_and_inputs_sha256={f:sha(f) for f in INPUTS},
  excluded_operations=["no new HTTP","no source fulltext / reaction graph read",
   "no canonical SMILES read","no G6 qualification","no model outputs",
   "no modification of frozen G4 or original source ledger"],
  cross_database_merge="strict shared normalized DOI/PMCID/PMID only; title never auto-merges",
  prior_exposure_match="explicit token intersection; unresolved aliases deferred",
  source_eligibility_claim=False,human_reviewed=False))
 print("registered alias preflight",len(INPUTS),"SHA bindings")
def run():
 plan=readjson(O+"pre_execution_manifest.json")
 verify_stage_chain(G,sha(G))
 for f,x in plan["code_and_inputs_sha256"].items():
  if sha(f)!=x:raise ContractError("SHA drift: "+f)
 for file in ("identity_clusters.json","exposure_triage.json","role_A6_alias_manifest.json"):
  if (ROOT/(O+file)).exists():raise ContractError("immutable output exists "+file)
 rs=rows(B+"discovery_dispositions.jsonl")
 if len(rs)!=23 or len({r["record_id"] for r in rs})!=23:
  raise ContractError("R1 metadata-count mismatch")
 exposure_index=defaultdict(set)
 exposure_stats={}
 for fname in OLD:
  count=0;exposed=0
  for r in rows(fname):
   count+=1
   if r.get("development_exposed") is not True:continue
   exposed+=1
   for t in tokens_from_exposure(r):
    exposure_index[t].add(fname)
  exposure_stats[fname]=dict(rows=count,development_exposed=exposed)
 # Never read original structure contents; use only metadata hints and historical id tokens.
 groups={i:{i} for i in range(len(rs))}
 parent=list(range(len(rs)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def join(a,b):
  x=root(a);y=root(b)
  if x!=y:parent[max(x,y)]=min(x,y)
 tok_ix={}
 row_tokens=[]
 for i,row in enumerate(rs):
  if row["metadata_only"] is not True or row["evidence_eligible"] is not False:
   raise ContractError("hint falsely classified as evidence")
  tokens=tokens_from_hint(row["source_hint"])
  row_tokens.append(tokens)
  for t in tokens:
   if t in tok_ix:join(i,tok_ix[t])
   else:tok_ix[t]=i
 clusters=defaultdict(list)
 for i in range(len(rs)):clusters[root(i)].append(i)
 out=[];blocked=0;unverified=0
 for n,idxs in enumerate(sorted(clusters.values(),key=lambda x:min(x)),1):
  toks=set().union(*(row_tokens[i] for i in idxs))
  prior={t:sorted(exposure_index[t]) for t in sorted(toks) if t in exposure_index}
  is_known=bool(prior)
  if is_known:blocked+=1
  else:unverified+=1
  labels=[rs[i]["source_hint"].get("title") for i in idxs]
  biblabels=[s for s in labels if isinstance(s,str) and s.strip()]
  title=biblabels[0] if biblabels else None
  priority=("bibliographic_title_relevance_only" if title and
    re.search(r"(flavonol|flavonoid|glycosyltransferase|glucosyltransferase)",title,re.I)
    else "metadata_relevance_unresolved")
  out.append(dict(cluster_id="R1-alias-%02d"%n,query_record_ids=[rs[i]["record_id"] for i in idxs],
   normalized_source_tokens=sorted(toks),record_count=len(idxs),known_design_or_historical_source=is_known,
   matched_prior_tokens=sorted(prior),matched_prior_exposure_ledger_paths=sorted(set().union(*[set(v) for v in prior.values()])) if prior else [],
   bibliographic_title=title,priority_note=priority,scientific_eligibility=False,
   fresh_eligibility=False,identity_reconciled_across_all_databases=False,
   disposition="blocked_from_fresh_by_known_exposure" if is_known else
    "unverified_only_do_not_admit_or_assert_novelty"))
 assert sum(z["record_count"] for z in out)==len(rs)
 assert any("pmid:29214446" in z["normalized_source_tokens"]
  and z["known_design_or_historical_source"] for z in out)
 save(O+"identity_clusters.json",dict(task=TASK,epoch_id="SS-E02",
  grouped_by="exact normalized identifiers only, not title",source_queries=3,
  metadata_rows=len(rs),strict_identifier_groups=len(out),
  independent_distinct_publications=None,clusters=out))
 save(O+"exposure_triage.json",dict(task=TASK,epoch_id="SS-E02",
  timestamp=now(),prior_exposure_inputs=exposure_stats,
  known_exposed_groups=blocked,unknown_identity_or_novelty_groups=unverified,
  metadata_rows=len(rs),new_G6_admitted=0,source_saturation=False,
  warning="lack of matched explicit identifier does not prove novel, scientific, or eligible"))
 save(O+"role_A6_alias_manifest.json",dict(task=TASK,epoch_id="SS-E02",
  role="A6 metadata alias/exposure triage, not independent source-structure review",
  timestamp=now(),G5_R1_stage_sha256=sha(G),pre_execution_sha256=sha(O+"pre_execution_manifest.json"),
  output_file_sha256={O+name:sha(O+name) for name in ("identity_clusters.json","exposure_triage.json")},
  checks=dict(input_sha_no_drift=True,strict_shared_identifier_merge=True,
   known_Petunia_exposure_blocked=True,all_23_rows_accounted=True,
   prohibited_title_merge=True,all_unmatched_still_unverified=True),
  counts=dict(processed=len(out),passed=0,rejected=blocked,pending=unverified),
  cross_db_distinct_papers_verified=None,HTTP=0,MCTS=0,
  read_holdout=False,read_model_outcome=False,read_scientific_fulltext=False,
  read_chemical_graph=False,human_reviewed=False,
  fresh_admitted=0,source_saturation=False,scientific_ABE_cells=0,
  independent_chemical_validation=False))
 print(json.dumps(dict(groups=len(out),known_exposed=blocked,
  unverified=unverified,postfreeze_metadata_rows=23,fresh=0),ensure_ascii=False))
if __name__=="__main__":
 {"pre":pre,"run":run}[sys.argv[1]]()
