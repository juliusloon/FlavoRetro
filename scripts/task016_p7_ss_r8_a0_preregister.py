"""SS-E02 R8: preregister scientific-text screen on two A3-verified originals.
A0 must not read body; freeze G5 before first chemical access. Permanently
expose both source articles conservatively even if downstream screening fails.
"""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,sha_file
from scripts.task016_p7_ss_sources import require_acquisition_phase
TASK="TASK-016-P7"; B=Path("outputs/task016-p7/v1")
R5=B/"SS/E02/fresh/SS-E02-R5-original-acquisition-v1"
R6=B/"SS/E02/fresh/SS-E02-R6-A3-original-identity-v1"
R6A=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v2"
SCOPE=B/"SS/E02/scope_manifest.json"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
OUT=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
EPOCH=B/"epoch_ledger.jsonl"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(t) for t in (ROOT/p).read_text().splitlines() if t.strip()]
def save(p,x):write(TASK,str(p),json.dumps(x,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
def main():
 if (ROOT/OUT).exists() or (ROOT/G5).exists():raise RuntimeError("IMMUTABLE_R8_EXISTS")
 previous=require_acquisition_phase("fresh",epoch_id="SS-E02",
    scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
 stage4=verify_stage_chain(ROOT/G4,sha(G4))
 assert stage4["stage"]=="G4_SCOPE_FREEZE" and stage4["epoch_id"]=="SS-E02"
 original=rows(R5/"original_query_execution.jsonl")
 verified=[r for r in load(R6/"A3_original_identity_results.json")["results"] if r["publication_identity_verified"]]
 assert {r["source_id"] for r in verified}=={"PMC13387883","PMC5517534"}
 screen_sources=[]
 for record in verified:
  candidate=[r for r in original if r["source_id"]==record["source_id"] and r.get("container_validity")=="XML_front_projected_only"]
  if len(candidate)!=1:raise RuntimeError("ORIGINAL_XML_MISSING")
  ptr=candidate[0]["raw_pointer"]
  if sha(Path(ptr["path"]))!=ptr["sha256"]:raise RuntimeError("ORIGINAL_DRIFT")
  if sha(Path(record["source_raw_path"]))!=record["source_raw_sha"]:raise RuntimeError("A3_ORIGINAL_DRIFT")
  assert record["source_raw_path"]==ptr["path"]
  screen_sources.append({"source_id":record["source_id"],"DOI":record["DOI"],
    "A3_verified_bibliography":True,"raw_original":{"path":ptr["path"],"sha256":ptr["sha256"],
      "bytes":ptr["bytes"]},"scientific_read_intent":"source_original_body_only",
    "no_pdf_or_SI_unregistered_chemical_read":True,
    "source_exposure":"permanently_science_exposed_before_first_read",
    "eligible_for_fresh_after_this_screen":False})
 a6=load(R6A/"A6_full_alias_union_dispositions.json")
 if not all(any(r["source_id"]==s["source_id"] and r["source_historical_exposure"]=="unresolved_not_certified_negative"
             for r in a6["sources"]) for s in screen_sources):raise RuntimeError("NO_POSITIVE_CLEARANCE")
 scope=load(SCOPE)
 assert scope["family"]=="SS" and scope["epoch_id"]=="SS-E02"
 stable_inputs=[R5/"role_A2_raw_only_manifest.json",R5/"original_query_execution.jsonl",
                R6/"role_A3_manifest.json",R6/"A3_original_identity_results.json",
                R6A/"A6_full_alias_union_dispositions.json",SCOPE,G4,
                B/"report_snapshots/progress-v19.json"]
 for s in screen_sources:stable_inputs.append(Path(s["raw_original"]["path"]))
 gate_before=dict(G4_SHA=sha(G4),scope_SHA=sha(SCOPE),registered_G5_metadata_before=previous["G5_manifest_sha256"])
 at=datetime.now(timezone.utc).isoformat()
 save(OUT/"pre_read_exposure.json",{
   "task":TASK,"epoch_id":"SS-E02","registered_at":at,
   "source_universe":screen_sources,"source_count":2,
   "status":"permanent_exposure_preregistered_before_new_chemical_original_read",
   "chemical_read_started":False,"no_scientific_content_used_to_choose_sources":True,
   "regardless_of_reaction_or_scope_evidence_these_sources_may_not_be_reused_as_next_epoch_fresh":True,
   "human_reviewed":False})
 stable_inputs.append(OUT/"pre_read_exposure.json")
 plan={"task":TASK,"epoch_id":"SS-E02","family":"SS","registered_at":at,
   "batch_id":"SS-E02-R8-science-screen-v1",
   "planned_sources":screen_sources,"count":2,
   "approval_type":"agent_delegated",
   "G4_scope_prior_to_original_scientific_read":gate_before,
   "read_permission":"only these two verified XML scientific bodies via two independent A4/A5 readers",
   "roles":{"A4":"first source text screen, no access to A5 output",
     "A5":"second independent source text screen, no access to A4 output",
     "A6":"reconcile only after both outputs exist"},
   "pre_registered_permanent_exposure":str(OUT/"pre_read_exposure.json"),
   "must_permanently_exclude_both_from_subsequent_fresh_pools":True,
   "cannot_admit_reactions_via_this_batch":True,
   "scope_bank_unchanged":True,"build_holdout_not_used_to_adjust_scope":True,
   "fresh_eligible":False,"future_G6_admission_requires_separate_qualified_full_reaction_evidence":True,
   "new_HTTP":0,"new_MCTS":0,
   "input_SHA256":{str(p):sha(p) for p in stable_inputs}}
 save(OUT/"A0_science_read_precontract.json",plan)
 stage=freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",
   [*stable_inputs,OUT/"A0_science_read_precontract.json"],G4,
   expected_previous_sha=sha(G4),family="SS",epoch_id="SS-E02")
 ss=sha(G5);assert verify_stage_chain(ROOT/G5,ss)["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 scope_sha=sha(SCOPE); registry=rows(EPOCH)
 if any(r.get("status") in ("development_epoch_incomplete","closed","complete") and r.get("epoch_id")=="SS-E02" for r in registry):
  raise RuntimeError("EPOCH_CLOSED")
 entry={"task":TASK,"epoch_id":"SS-E02","family":"SS","stage":"G5_FRESH_HOLDOUT_ACQUIRE",
    "status":"active","event_type":"scientific_source_screen_G5_preregistered_before_body_read",
    "registered_at":datetime.now(timezone.utc).isoformat(),
    "approval_type":"agent_delegated","human_reviewed":False,
    "metadata_only":False,"full_scientific_round":False,
    "scientific_source_screen_only":True,"permanent_exposure_pre_read":True,
    "new_chemical_source_count":2,"fresh_admitted":0,
    "stage_manifest_path":str(G5),"stage_manifest_sha256":ss,
    "scope_manifest_path":str(SCOPE),"scope_manifest_sha256":scope_sha,
    "precontract_path":str(OUT/"A0_science_read_precontract.json"),
    "precontract_sha256":sha(OUT/"A0_science_read_precontract.json")}
 write(TASK,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(entry,sort_keys=True,ensure_ascii=False)+"\n")
 passed=require_acquisition_phase("fresh",epoch_id="SS-E02",
     scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
 assert passed["G5_manifest_sha256"]==ss and passed["G4_manifest_sha256"]==sha(G4)
 event(TASK,"SS_R8_pre_read_scientific_screen_authorized",source_count=2,stage_sha256=ss,
   both_sources_permanently_exposed_pre_read=True,scientific_qualification_granted=False)
 print(json.dumps({"G5_screen_registered":True,"raw_sources":2,
   "G4_SHA":sha(G4),"G5_SHA":ss,"scope_SHA":scope_sha,"new_HTTP":0,
   "fresh_admitted":0},ensure_ascii=False))
if __name__=="__main__":main()
