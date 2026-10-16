"""C E02 R26 A0: preregister three original JATS sources and historical exposure before scientific-body read."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
R=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1"
G5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
G4=B/"C/E02/stages/G4_SCOPE_FREEZE.json"
SCOPE=B/"C/E02/scope_manifest.json"
EPOCH=B/"epoch_ledger.jsonl"
EXPOS=B/"exposure_ledger.jsonl"
PRIOR=B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl"
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def put(p,x):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_OUTPUT "+str(p))
 write(T,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/G5).exists():raise RuntimeError("PREREG_ALREADY_EXISTS")
 verified=verify_stage_chain(ROOT/G4,sha(G4))
 assert verified["stage"]=="G4_SCOPE_FREEZE" and verified["epoch_id"]=="C-E02"
 candidates=[x for x in load(A3)["sources"] if x["family"]=="C"]
 assert len(candidates)==3 and all(x["official_PMC_original_front_identity"] for x in candidates)
 assert {x["PMCID"] for x in candidates}=={"PMC9855344","PMC12525976","PMC11577821"}
 ledger=rows(EPOCH)
 assert not any(r.get("epoch_id")=="C-E02" and r.get("status") in ("closed","complete","development_epoch_incomplete","invalidated") for r in ledger)
 assert any(r.get("epoch_id")=="C-E02" and r.get("stage")=="G4_SCOPE_FREEZE" and r.get("stage_manifest_sha256")==sha(G4) for r in ledger)
 texts=[(ROOT/p).read_text().casefold() for p in (EXPOS,PRIOR)]
 ptr=[]
 for x in candidates:
  raw=Path(x["original_source_path"])
  assert sha(raw)==x["original_SHA"]
  sid=x["PMCID"];doi=x["DOI"]
  hits=sum(t.count(sid.casefold())+t.count(doi.casefold()) for t in texts)
  ptr.append(dict(PMCID=sid,DOI=doi,source_path=str(raw),raw_SHA=x["original_SHA"],
   prior_exposure_literals=hits,
   prior_exposure_status="known_exposed_not_fresh" if hits else "unknown_pending_full_alias_and_graph_closure",
   science_original_body_read=False,scientific_eligibility="unknown",eligible_for_holdout=False))
 now=datetime.now(timezone.utc).isoformat()
 paths=[A3,G4,SCOPE,EXPOS,PRIOR,Path("scripts/task016_p7_c_r26_A0.py")]+[Path(x["source_path"]) for x in ptr]
 put(R/"pre_science_exposure_and_identity.json",dict(task=T,epoch_id="C-E02",registered_at=now,
  sources=ptr,full_graph_alias_exposure_reconciliation_not_yet_complete=True,
  known_exposed_count=sum(x["prior_exposure_literals"]>0 for x in ptr),existing_model_outcomes_unread=True,
  prospective_current_epoch_scientific_original_read_after_this_G5=True,
  no_automatic_holdout_or_scientific_qualification=True,human_reviewed=False))
 paths.append(R/"pre_science_exposure_and_identity.json")
 put(R/"A0_pre_read_contract.json",dict(task=T,family="C",epoch_id="C-E02",registered_at=now,
  approval_type="agent_delegated",human_reviewed=False,
  selected=ptr,A3_original_front_SHA=sha(A3),
  actual_source_read="only the 3 listed immutable original JATS body and captions after G5 freeze",
  role_isolation=dict(A4="standalone reader; no A5 output",A5="independent reader; no A4 output",A6="after A4/A5 only"),
  target_scope="C6 direct UDP-glucose flavone C3-H enzymatic single step; no C8/C3-OH/isoflavone/radical or rearrangement",
  no_structure_guessed_from_names=True,chemical_stereo_unverified_by_title=True,
  G4_sha=sha(G4),scope_SHA=sha(SCOPE),new_HTTP=0,new_MCTS=0,
  no_fresh_admission_by_this_contract=True,all_inputs_SHA={str(p):sha(p) for p in paths}))
 paths.append(R/"A0_pre_read_contract.json")
 freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",paths,G4,
    expected_previous_sha=sha(G4),family="C",epoch_id="C-E02")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 ev=dict(task=T,family="C",epoch_id="C-E02",stage="G5_FRESH_HOLDOUT_ACQUIRE",
  event_type="R26_three_C_original_science_prereg_before_body",status="active",
  stage_manifest_path=str(G5),stage_manifest_sha256=sha(G5),
  scope_manifest_path=str(SCOPE),scope_manifest_sha256=sha(SCOPE),
  registered_at=now,source_count=3,scientific_body_read=False,fresh_admitted=0,human_reviewed=False)
 write(T,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(ev,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"C_E02_R26_original_science_G5_registered",G5_SHA=sha(G5),count=3)
 print(json.dumps(dict(C_R26_G5=sha(G5),originals=3,known_exposed=sum(x["prior_exposure_literals"]>0 for x in ptr),pending_alias=sum(x["prior_exposure_literals"]==0 for x in ptr))))
if __name__=="__main__":main()

