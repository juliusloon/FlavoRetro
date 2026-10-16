#!/usr/bin/env python3
"""Source G5 metadata-only branch closeout; no chemistry qualification or G6."""
from __future__ import annotations
import json,sys
from collections import Counter
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p7_orchestrate import (
 sha_file,verify_stage_chain,freeze_stage_manifest,save_json,ContractError)
from scripts.task016_p7_source_harness import validate_query_accounting,validate_acquisition
TASK="TASK-016-P7"
G4="outputs/task016-p7/v1/SS/E02/stages/G4_SCOPE_FREEZE.json"
DIR="outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R1-metadata/"
BATCH="outputs/task016-p7/v1/SS/E02/stages/batches/SS-E02-R1/"
def sha(p):return sha_file(ROOT/p)
def jsonread(p):return json.loads((ROOT/p).read_text())
def lines(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def need(c,m):
 if not c:raise ContractError(m)
def now():return datetime.now(timezone.utc).isoformat()
def prep():
 verify_stage_chain(G4,sha(G4))
 plan=jsonread(DIR+"query_plan.json")
 reg=jsonread(DIR+"preregistered_execution_boundary.json")
 need(reg["query_plan_sha256"]==sha(DIR+"query_plan.json"),"plan drift")
 need(reg["G4_sha256"]==sha(G4),"scope G4 drift")
 executions=lines(DIR+"query_execution.jsonl")
 hints=lines(DIR+"discovery_dispositions.jsonl")
 attempts=lines(DIR+"physical_attempts.jsonl")
 raw=jsonread(DIR+"raw_manifest.json")
 count=validate_query_accounting(plan,executions,hints)
 need(count["planned"]==count["executed"]==3 and count["discovered"]==23,
  "cannot match actual physical R1 plan without rereading")
 need(all(h["disposition"]=="metadata_only" and not h["evidence_eligible"]
   for h in hints),"metadata hints elevated to sources")
 need(len(attempts)==3 and len(raw["objects"])==3 and all(r["http_status"]==200 for r in attempts),
  "physical HTTP cannot silently be rewritten")
 return plan,reg,executions,hints,attempts,raw,count
def close():
 plan,reg,executions,hints,attempts,raw,count=prep()
 towrite=(DIR+"normalized_acquisition_attempts.jsonl",
          DIR+"normalized_acquisition_manifest.json",
          DIR+"metadata_exposure_screen.json",
          DIR+"R1_source_guard_validation.json")
 for p in towrite+(BATCH+"G5_FRESH_HOLDOUT_ACQUIRE.json",):
  need(not (ROOT/p).exists(),"immutable closeout exists: "+p)
 normalized=[]
 objects=[]
 raw_by_query={r["query_id"]:r for r in raw["objects"]}
 for r in attempts:
  aid=r["query_id"]
  nr=dict(attempt_id=aid,url=r["url"],bytes=r["bytes"],status=r["http_status"],
   started_at=r["started_at"],path=r["path"],sha256=r["sha256"],
   recovery_chain=False,license=None,redistribution=False)
  normalized.append(nr)
  source=raw_by_query[aid]
  need(source["sha256"]==r["sha256"] and source["bytes"]==r["bytes"]
    and source["path"]==r["path"],"raw metadata object mismatch")
  objects.append(dict(attempt_id=aid,path=source["path"],sha256=source["sha256"],
    bytes=source["bytes"],kind="metadata"))
 physical=dict(objects=objects,http_requests=len(attempts),
  bytes=sum(x["bytes"] for x in attempts),article_versions=0,attachments=0)
 source_check=validate_acquisition(normalized,physical,root=ROOT)
 need(source_check["conserved"] and source_check["http_requests"]==3
  and source_check["bytes"]==59055,"physical HTTP conservation invalid")
 from scripts.operate import write
 write(TASK,DIR+"normalized_acquisition_attempts.jsonl",
  "".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in normalized))
 save_json(DIR+"normalized_acquisition_manifest.json",physical,immutable=True)
 pmid_design=sum(h["source_hint"].get("PMID")=="29214446"
  for h in hints)
 exact_design_doi=sum((h["source_hint"].get("DOI") or "").lower()
   =="10.1007/s00425-017-2822-5" for h in hints)
 screen=dict(task=TASK,epoch_id="SS-E02",
  status="metadata_only_screening_not_G6",
  timestamp=now(),query_hints_total=len(hints),
  independently_unique_publications=None,
  known_exposed_design_PubMed_29214446_hints=pmid_design,
  known_exposed_design_Petunia_DOI_hints=exact_design_doi,
  all_hints_evidence_eligible=False,
  cross_database_aliases_not_resolved=True,
  other_hints_not_automatically_fresh=True,
  no_fulltext_or_reaction_graph_read=True,
  incomplete_G5_scientific_round=True,
  no_source_saturation_claim=True)
 save_json(DIR+"metadata_exposure_screen.json",screen,immutable=True)
 guard=dict(task=TASK,epoch_id="SS-E02",status="G5_metadata_only_branch_terminal",
  timestamp=now(),query_validation=count,
  physical_acquisition_validation=source_check,
  scope_sha256=sha("outputs/task016-p7/v1/SS/E02/scope_manifest.json"),
  G4_stage_sha256=sha(G4),actual_HTTP=3,
  new_metadata_only_hints=len(hints),new_chemical_qualification=0,
  new_runtime_executable_fresh=0,new_closure_groups=0,
  no_G6_admission=True,not_complete_scientific_round=True,
  source_saturation=False,scientific_ABE_cells=0,metrics=None,
  human_reviewed=False,independent_chemical_validation=False)
 save_json(DIR+"R1_source_guard_validation.json",guard,immutable=True)
 inputs=[DIR+name for name in (
  "query_plan.json","preregistered_execution_boundary.json",
  "query_execution.jsonl","discovery_dispositions.jsonl",
  "physical_attempts.jsonl","raw_manifest.json","round_result.json",
  "normalized_acquisition_attempts.jsonl","normalized_acquisition_manifest.json",
  "metadata_exposure_screen.json","R1_source_guard_validation.json")]
 inputs += [r["path"] for r in objects]
 inputs+=["scripts/task016_p7_ss_e02_metadata_r1_chatgpt_v1.py",
          "scripts/task016_p7_ss_e02_metadata_g5_closeout_chatgpt_v1.py"]
 result=freeze_stage_manifest(BATCH,"G5_FRESH_HOLDOUT_ACQUIRE",inputs,
  previous_manifest_path=G4,expected_previous_sha=sha(G4),
  family="SS",epoch_id="SS-E02")
 verify_stage_chain(BATCH+"G5_FRESH_HOLDOUT_ACQUIRE.json",
                    sha(BATCH+"G5_FRESH_HOLDOUT_ACQUIRE.json"))
 print(json.dumps(dict(stage=result["stage"],family="SS",epoch="SS-E02",
  branches=1,metadata_hints=len(hints),HTTP=3,bytes=source_check["bytes"],
  new_fresh=0,no_scientific_round_closed=True,verified=True),ensure_ascii=False))
if __name__=="__main__":close()
