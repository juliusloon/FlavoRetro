"""P7 SS-R8 A6: reconcile independently screened original science before any G6.
Two articles previously permanently exposure-preregistered. This source screen
does not generate reaction SMILES, independent graph checks or new fresh targets.
"""
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,freeze_stage_manifest
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R8=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
OUT=R8/"A6"
LEDGER=B/"epoch_ledger.jsonl"
SCOPE=B/"SS/E02/scope_manifest.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def local(e):return e.tag.rsplit("}",1)[-1]
def paratext(source_path,index):
 root=ET.parse(ROOT/source_path).getroot()
 body=next(x for x in root.iter() if local(x)=="body")
 p=[x for x in body.iter() if local(x)=="p"]
 if not 1<=index<=len(p):raise RuntimeError("INVALID_ORIGINAL_PARAGRAPH")
 return " ".join("".join(p[index-1].itertext()).split())
def evidence(path,idx,required):
 s=paratext(path,idx)
 for needle in required:
  if needle.casefold() not in s.casefold():raise RuntimeError("MISSING_EXACT_SOURCE_ANCHOR "+str((idx,needle)))
 return {"original_path":str(path),"original_SHA":sha(path),"paragraph_ordinal":idx,
  "paragraph_sha256":hashlib.sha256(s.encode()).hexdigest(),
  "observed_literal_features":required,"excerpt":s[:160],
  "pointer":str(path)+"#body/p-"+str(idx)}
def main():
 if (ROOT/OUT).exists() or (ROOT/G6).exists():raise RuntimeError("R8_A6_ALREADY_WRITTEN")
 a4=load(R8/"A4/source_body_screen.json")
 a5=load(R8/"A5/independent_body_scope_screen.json")
 plan=load(R8/"A0_science_read_precontract.json")
 exposure=load(R8/"pre_read_exposure.json")
 assert a4["counts"]["processed"]==a5["counts"]["processed"]==2
 assert {x["source_id"] for x in a4["sources"]}=={x["source_id"] for x in a5["sources"]}=={
   "PMC13387883","PMC5517534"}
 assert exposure["source_count"]==2
 verify_stage_chain(ROOT/G5,sha(G5))
 index={s["source_id"]:Path(s["raw_original"]["path"]) for s in plan["planned_sources"]}
 for row in plan["planned_sources"]:
  raw=Path(row["raw_original"]["path"])
  if sha(raw)!=row["raw_original"]["sha256"]:raise RuntimeError("SOURCE_RAW_SHA_DRIFT")
  assert any(x["source_id"]==row["source_id"] and x["source_exposed"] and not x["fresh_eligible"] for x in a4["sources"])
  assert any(x["source_id"]==row["source_id"] and x["source_permanently_exposed"] and not x["fresh_eligible"] for x in a5["sources"])
 pre={"task":TASK,"agent_role":"A6","timestamp":datetime.now(timezone.utc).isoformat(),
      "G5_sha":sha(G5),"scope_sha":sha(SCOPE),
      "A4_SHA":sha(R8/"A4/source_body_screen.json"),
      "A5_SHA":sha(R8/"A5/independent_body_scope_screen.json"),
      "source_count":2,"source_exposure_preregistered_sha":sha(R8/"pre_read_exposure.json"),
      "only_reconciliation_after_A4_and_A5_complete":True,
      "not_a_completed_dual_structural_graph_extraction":True}
 write(TASK,str(OUT/"pre_execution.json"),json.dumps(pre,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 tea=index["PMC5517534"];carn=index["PMC13387883"]
 tea_anchors=[
 evidence(tea,14,["flavonoid monoglycosides","3-O-glucoside","7-O","3,7"]),
 evidence(tea,18,["kaempferol 3-O-glucoside","7-hydroxy","kaempferol-di-glucoside"]),
 evidence(tea,17,["7-hydroxy","3-hydroxy"])]
 carn_anchors=[
 evidence(carn,35,["transgenic tobacco","kaempferol 3","sophoroside"]),
 evidence(carn,36,["transgenic carnation","3","sophorobiose","UDP sugars"]),
 evidence(carn,46,["previous study","sophoroside","rutinoside"])]
 data=[
 {"source_id":"PMC5517534","original_DOI":"10.1038/s41598-017-06453-z",
  "A4_A5_looked_at_same_original_SHA":True,
  "reconciled_claim":"The enzyme is reported to use monoglycosides as acceptors and convert 3-O-glucosides into 3,7-di-O glycosides; the added sugar is reported at flavonoid 7-hydroxy, not O2 of a sugar residue.",
  "A4_A5_keyword_motif_hits_are_not_reaction_evidence":True,
  "evidence_pointers":tea_anchors,
  "scope_disposition":"demonstrated_different_7_O_aglycone_site_not_frozen_SS_E02_O2",
  "exact_frozen_scope_site_O2_supported":False,
  "full_reaction_stereo_donor_structure_qualified":False,"eligible_for_SS_E02_panel":False,
  "possible_other_future_design_role":"exposed_design_only"},
 {"source_id":"PMC13387883","original_DOI":"10.1111/pbi.70674",
  "A4_A5_looked_at_same_original_SHA":True,
  "reconciled_claim":"Transgenic accumulation of sophoroside/rutinoside-containing metabolites was reported together with a proposed 3-O flavonol glycosylation role; this does not identify a source-qualified isolated enzyme reaction adding sugar at an existing glycoside's O2.",
  "A4_A5_keyword_motif_hits_are_not_reaction_evidence":True,
  "evidence_pointers":carn_anchors,
  "scope_disposition":"insufficient_direct_sugar_O2_reaction_in_screened_original",
  "exact_frozen_scope_site_O2_supported":False,
  "full_reaction_stereo_donor_structure_qualified":False,"eligible_for_SS_E02_panel":False,
  "possible_other_future_design_role":"exposed_design_only"}]
 result={"task":TASK,"role":"A6_reconciliation_and_closure","epoch_id":"SS-E02",
  "timestamp":datetime.now(timezone.utc).isoformat(),
  "input_pre_execution_SHA":sha(OUT/"pre_execution.json"),
  "sources":data,
  "counts":{"processed":2,"passed_scientific":0,
    "rejected_for_current_scope":1,"deferred_no_direct_O2_reaction":1,
    "fresh_admitted":0,"new_closure_groups":0,"new_MCTS":0},
  "dual_readers_independently_scanned_original_science":True,
  "dual_complete_chemical_structure_extraction":False,
  "no_graph_structure_or_stereo_inferred":True,
  "no_new_G7_or_runtime":True,
  "no_claim_of_total_scientific_absence_in_any_article":True,
  "read_original_body":True,"human_reviewed":False,"source_permanent_exposure":True,
  "no_fresh_reuse_in_same_or_next_epoch":True}
 write(TASK,str(OUT/"source_scope_reconciliation.json"),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 freeze_stage_manifest(ROOT/G6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",
   [R8/"A0_science_read_precontract.json",R8/"pre_read_exposure.json",
    R8/"A4/source_body_screen.json",R8/"A5/independent_body_scope_screen.json",
    OUT/"source_scope_reconciliation.json",OUT/"pre_execution.json"],
   G5,expected_previous_sha=sha(G5),family="SS",epoch_id="SS-E02")
 verify_stage_chain(ROOT/G6,sha(G6))
 entry={"task":TASK,"event_type":"SS_R8_G6_screened_zero_scientific_admission",
   "epoch_id":"SS-E02","family":"SS","stage":"G6_IDENTITY_STRUCTURE_ADMIT",
   "status":"active","registered_at":datetime.now(timezone.utc).isoformat(),
   "stage_manifest_path":str(G6),"stage_manifest_sha256":sha(G6),
   "source_scientific_screen_only":True,"full_dual_graph_chemical_admission":False,
   "fresh_admitted":0,"source_count":2,"scope_manifest_sha256":sha(SCOPE),
   "approval_type":"agent_delegated","human_reviewed":False,
   "both_sources_permanently_exposed_before_original_read":True}
 write(TASK,str(LEDGER),(ROOT/LEDGER).read_text()+json.dumps(entry,sort_keys=True,ensure_ascii=False)+"\n")
 event(TASK,"SS_R8_G6_screen_zero_reaction_qualified",sources=2,new_fresh=0,
   tea_7_O_site_not_sugar_O2=True,carnation_direct_sugar_O2_unproven=True)
 print(json.dumps({"role":"A6","original_sources":2,"scope_ineligible":2,
   "G6_stage_sha":sha(G6),"new_scientific_fresh":0,"new_MCTS":0},ensure_ascii=False))
if __name__=="__main__":main()
