"""SS R21 A0 official science G5 prereg before original-body reading.

Both published original & related preprint permanently exposed; no 'fresh'
claim even if this source provides a real frozen-scope O2 enzymatic reaction.
"""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
R=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json";SCOPE=B/"SS/E02/scope_manifest.json"
EPOCH=B/"epoch_ledger.jsonl"
def sha(p):return sha_file(ROOT/p)
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def put(p,v):
 if (ROOT/p).exists():raise RuntimeError("R21_IMMUTABLE_ALREADY_EXISTS "+str(p))
 write(T,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/G5).exists():raise RuntimeError("R21_G5_EXISTS")
 v=verify_stage_chain(ROOT/G4,sha(G4))
 assert v["stage"]=="G4_SCOPE_FREEZE" and v["epoch_id"]=="SS-E02"
 a=load(A3)
 chosen=[x for x in a["sources"] if x["PMCID"] in ("PMC12611259","PMC11974848")]
 assert len(chosen)==2 and all(x["official_PMC_original_front_identity"] for x in chosen)
 assert sha(SCOPE)=="c173c0e6aaee7dacfcb9195cbd481577703ecdebcd18aaf506b76b84e74e53b6"
 assert not any(r.get("epoch_id")=="SS-E02" and r.get("status") in ("closed","complete","development_epoch_incomplete") for r in rows(EPOCH))
 prev=[r for r in rows(EPOCH) if r.get("epoch_id")=="SS-E02" and r.get("stage")=="G5_FRESH_HOLDOUT_ACQUIRE" and r.get("status")=="active"]
 assert prev
 paths=[Path(x["original_source_path"]) for x in chosen]
 assert all(sha(p)==x["original_SHA"] for p,x in zip(paths,chosen))
 at=datetime.now(timezone.utc).isoformat()
 ptr=[dict(PMCID=x["PMCID"],DOI=x["DOI"],path=x["original_source_path"],sha256=x["original_SHA"],
  source_scientific_body_read_now=False,public_web_excerpts_exposed_prior_to_this_G5=True,
  same_experimental_source_or_preprint_alias_group="TOMATO-SLUGT79BB-SHIN-2025",
  eligible_for_new_fresh=False,design_or_scientific_review_only=True) for x in chosen]
 inputs=[A3,G4,SCOPE,B/"exposure_ledger.jsonl",
  B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl",
  B/"governance/R18-eight-PMC-primary-original-access-v1/raw_custody_summary.json",
  B/"governance/R19-three-PMC-targeted-original-access-v1/raw_custody_summary.json",*paths]
 for p in inputs:assert (ROOT/p).exists()
 put(R/"pre_scientific_read_source_exposure.json",dict(task=T,epoch_id="SS-E02",at=at,
  exposure_begins="already web-visible to agent during R19 source scouting; registered here BEFORE archived original body is read under P7",
  legal_originals_available=2,source_records=ptr,
  permanent_exposure=True,not_fresh_eligible=True,
  no_web_search_chemical_excerpts_used_as_formal_G6_evidence=True,
  no_human_reviewed_claim=True,applicability_to_O2_source_to_be_checked_independently=True))
 inputs.append(R/"pre_scientific_read_source_exposure.json")
 put(R/"A0_G5_original_science_precontract.json",dict(task=T,family="SS",epoch_id="SS-E02",
   at=at,approval_type="agent_delegated",human_reviewed=False,
   selected_sources=ptr,science_scope="only original JATS bodies and captions from the two exact SHA-bound XML originals",
   stages=dict(A3="front-only done",G5="must freeze before A4/A5",A4="independent reader 1",A5="independent reader 2",A6="post-reader scientific reaction & closure reconciliation"),
   source_alias_group="same preprint/journal source not independent",
   read_model_outcomes=False,modify_frozen_scope=False,
   no_graph_from_name_or_memory=True,
   no_auto_product_SMILES_or_stereo=True,
   source_qualified_not_prejudged=True,scientific_fresh_admitted=0,
   original_A3_SHA=sha(A3),G4_SHA=sha(G4),scope_SHA=sha(SCOPE),
   prior_registered_G5_SHA=prev[-1]["stage_manifest_sha256"],
   inputs_SHA={str(p):sha(p) for p in inputs},new_HTTP=0,new_MCTS=0))
 inputs.append(R/"A0_G5_original_science_precontract.json")
 freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",inputs,G4,
  expected_previous_sha=sha(G4),family="SS",epoch_id="SS-E02")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 rec=dict(task=T,epoch_id="SS-E02",family="SS",stage="G5_FRESH_HOLDOUT_ACQUIRE",
  status="active",event_type="R21_post_web_exposure_original_source_science_preregistered",
  at=at,stage_manifest_path=str(G5),stage_manifest_sha256=sha(G5),
  scope_manifest_path=str(SCOPE),scope_manifest_sha256=sha(SCOPE),
  source_count=2,prior_web_exposure=True,no_fresh_eligible=True,scientific_body_read=False,
  fresh_admitted=0,approval_type="agent_delegated",human_reviewed=False)
 write(T,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(rec,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"SS_E02_R21_G5_tomato_directO2_original_science_preregistered",G5_sha256=sha(G5),source_count=2)
 print(json.dumps(dict(G5_frozen=True,two_originals=2,source_web_exposed=True,fresh=0,G5_SHA=sha(G5))))
if __name__=="__main__":main()

