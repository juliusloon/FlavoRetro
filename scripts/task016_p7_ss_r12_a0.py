"""P7 SS-R12 A0: prerequisite-bound science screen; freeze exposure/G5 before body."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,freeze_stage_manifest
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R12-original-science-review-v3"
R11=B/"SS/E02/fresh/SS-E02-R11-original-acquisition-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
SCOPE=B/"SS/E02/scope_manifest.json"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
EPOCH=B/"epoch_ledger.jsonl"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(s) for s in (ROOT/p).read_text().splitlines() if s.strip()]
def save(p,x):write(TASK,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/G5).exists() or (ROOT/R/"A0_science_read_precontract.json").exists():raise RuntimeError("IMMUTABLE_R12_G5_EXISTS")
 stage=verify_stage_chain(ROOT/G4,sha(G4))
 assert stage["stage"]=="G4_SCOPE_FREEZE" and stage["epoch_id"]=="SS-E02"
 a3=read(R/"A3_front_identity.json")
 src=a3["results"]
 assert len(src)==2 and all(x["status"]=="original_publication_identity_verified_front_only" for x in src)
 assert {x["source_id"] for x in src}=={"PMC5444469","PMC6813240"}
 if any(x.get("status") in ("development_epoch_incomplete","closed","complete") and x.get("epoch_id")=="SS-E02" for x in rows(EPOCH)):
  raise RuntimeError("CLOSED_EPOCH")
 parent=rows(EPOCH)
 prior=[x for x in parent if x.get("stage")=="G5_FRESH_HOLDOUT_ACQUIRE" and x.get("epoch_id")=="SS-E02" and x.get("status")=="active"]
 assert prior,"No prior registered G5"
 assert all(x["source_reaction_qualified"] is False and x["fresh_admitted"]==0 for x in src)
 scope=read(SCOPE);assert scope["family"]=="SS" and scope["epoch_id"]=="SS-E02"
 source_universe=[]
 for a in src:
  p=Path(a["original"]["path"])
  if sha(p)!=a["original"]["sha256"]:raise RuntimeError("RAW_DRIFT")
  source_universe.append(dict(source_id=a["source_id"],DOI=a["doi"],
      A3_front_publication_identity=True,
      raw_original=dict(path=str(p),sha256=sha(p),bytes=a["original"]["bytes"]),
      scientific_read_intent="source original XML body only, independent A4/A5",
      source_exposure="permanently_science_exposed_before_first_read",
      chemical_reaction_qualified=False,eligible_for_fresh_after_current_epoch=False))
 now=datetime.now(timezone.utc).isoformat()
 immutable_inputs=[R/"A3_pre_execution.json",R/"A3_front_identity.json",
                   R11/"http_ledger.jsonl",R11/"raw_execution.jsonl",
                   B/"governance/prior_exposure_inventory_v1/inventory_provenance.json",
                   B/"SS/E02/stages/G4_SCOPE_FREEZE.json",SCOPE]
 immutable_inputs += [Path(x["raw_original"]["path"]) for x in source_universe]
 save(R/"pre_read_exposure.json",dict(task=TASK,epoch_id="SS-E02",family="SS",
   registered_at=now,source_count=2,source_universe=source_universe,
   permanently_exposed_before_new_scientific_read=True,previous_scientific_body_read=False,
   historic_exposure_alias_graph_not_cleared=True,
   no_chemical_source_qualification=True,not_reusable_in_future_epoch=True,
   human_reviewed=False))
 immutable_inputs.append(R/"pre_read_exposure.json")
 plan=dict(task=TASK,epoch_id="SS-E02",family="SS",batch_id="SS-E02-R12-original-science-review-v3",
    registered_at=now,approval_type="agent_delegated",human_reviewed=False,
    count=2,planned_sources=source_universe,
    read_permission="only these two original XML scientific bodies via independent A4 and A5",
    roles=dict(A4="standalone first body reader; no A5 output",A5="standalone independent body reader; no A4 output",A6="reconcile only after both"),
    pre_registered_permanent_exposure=str(R/"pre_read_exposure.json"),
    must_permanently_exclude_both_from_subsequent_fresh_pools=True,
    full_qualified_graph_requires_separate_dual_structure_G6=True,
    no_automatic_reaction_admission=True,no_current_fresh_claim=True,
    scope_bank_unchanged=True,build_holdout_not_used_to_adjust_scope=True,
    G4_scope_prior_to_original_scientific_read=dict(G4_SHA=sha(G4),scope_SHA=sha(SCOPE),previous_G5=prior[-1]["stage_manifest_sha256"]),
    input_SHA256={str(p):sha(p) for p in immutable_inputs},new_HTTP=0,new_MCTS=0)
 save(R/"A0_science_read_precontract.json",plan)
 freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",
   [*immutable_inputs,R/"A0_science_read_precontract.json"],G4,
   expected_previous_sha=sha(G4),family="SS",epoch_id="SS-E02")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 rec=dict(task=TASK,epoch_id="SS-E02",family="SS",stage="G5_FRESH_HOLDOUT_ACQUIRE",
   status="active",event_type="SS_R12_original_science_G5_preregistered_before_read",
   registered_at=datetime.now(timezone.utc).isoformat(),
   stage_manifest_path=str(G5),stage_manifest_sha256=sha(G5),
   scope_manifest_path=str(SCOPE),scope_manifest_sha256=sha(SCOPE),
   source_count=2,publication_identity_verified=2,science_read=False,
   fresh_admitted=0,scientific_source_screen_only=True,full_scientific_round=False,
   permanent_exposure_pre_read=True,approval_type="agent_delegated",human_reviewed=False)
 write(TASK,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(rec,ensure_ascii=False,sort_keys=True)+"\n")
 from scripts.task016_p7_ss_sources import require_acquisition_phase
 gate=require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
 assert gate["G5_manifest_sha256"]==sha(G5)
 event(TASK,"SS_R12_g5_preread_authorized",original_count=2,G5_SHA=sha(G5),exposure_sha=sha(R/"pre_read_exposure.json"))
 print(json.dumps(dict(G5_pass=True,originals=2,new_fresh=0,sha=sha(G5))))
if __name__=="__main__":main()

