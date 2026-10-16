"""TASK-016-P7 SS-E02 R12 A6: source-specific, SHA-anchored reconciliation.
This is a bounded original-text scientific source screen, NOT dual graph admission.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,xml.etree.ElementTree as ET
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,freeze_stage_manifest
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R12-original-science-review-v3"
G5=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G6_IDENTITY_STRUCTURE_ADMIT.json"
SCOPE=B/"SS/E02/scope_manifest.json";EPOCH=B/"epoch_ledger.jsonl"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def save(p,x):write(TASK,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def local(e):return e.tag.rsplit("}",1)[-1]
def evidence(path,ordinal,requirements):
    root=ET.parse(ROOT/path).getroot()
    body=next(x for x in root.iter() if local(x)=="body")
    ps=[x for x in body.iter() if local(x)=="p"]
    if not 0<ordinal<=len(ps):raise RuntimeError("MISSING_PARAGRAPH")
    s=" ".join("".join(ps[ordinal-1].itertext()).split())
    if any(k.casefold() not in s.casefold() for k in requirements):raise RuntimeError("ANCHOR_TEXT_DRIFT "+str(ordinal))
    return dict(source=str(path),original_sha256=sha(path),
       location=f"{path}#body/p-{ordinal}",paragraph_ordinal=ordinal,
       text_sha256=hashlib.sha256(s.encode()).hexdigest(),
       literal_features=requirements,excerpt=s[:155])
def main():
 if (ROOT/(R/"A6")).exists() or (ROOT/G6).exists():raise RuntimeError("R12_A6_EXISTS")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 p=read(R/"A0_science_read_precontract.json")
 e=read(R/"pre_read_exposure.json")
 a3=read(R/"A3_front_identity.json")
 a4=read(R/"A4/source_body_screen.json");a5=read(R/"A5/independent_body_scope_screen.json")
 assert len(p["planned_sources"])==len(e["source_universe"])==2
 expected={"PMC5444469","PMC6813240"}
 assert {x["source_id"] for x in a4["sources"]}=={x["source_id"] for x in a5["sources"]}==expected
 assert {x["source_id"] for x in a3["results"]}==expected
 assert e["permanently_exposed_before_new_scientific_read"] is True
 assert sha(SCOPE)==p["G4_scope_prior_to_original_scientific_read"]["scope_SHA"]
 look={x["source_id"]:Path(x["raw_original"]["path"]) for x in p["planned_sources"]}
 for v in p["planned_sources"]:
  original=Path(v["raw_original"]["path"])
  if sha(original)!=v["raw_original"]["sha256"]:raise RuntimeError("RAW_INPUT_DRIFT")
  assert any(s["source_id"]==v["source_id"] and s["source_exposed"] and s["fresh_eligible"] is False for s in a4["sources"])
  assert any(s["source_id"]==v["source_id"] and s["source_permanently_exposed"] and s["fresh_eligible"] is False for s in a5["sources"])
 frozen=[R/"A0_science_read_precontract.json",R/"A3_front_identity.json",R/"pre_read_exposure.json",
  R/"A4/source_body_screen.json",R/"A5/independent_body_scope_screen.json",G5,SCOPE]
 out=R/"A6"
 save(out/"pre_execution.json",dict(task=TASK,role="A6",time=datetime.now(timezone.utc).isoformat(),
   input_SHA256={str(x):sha(x) for x in frozen},pre_registered_science_exposure=True,
   two_independent_original_text_readers=True,not_graph_structure_qualified=True,human_reviewed=False))
 lotus=look["PMC5444469"];freesia=look["PMC6813240"]
 records=[
  dict(source_id="PMC5444469",doi="10.1093/jxb/erw420",article_subject="Lotus japonicus UGT72 family",
    exact_frozen_O2_reaction_supported=False,
    disposition="out_of_frozen_scope_primary_3O_aglycone_glucosylation_secondary_metabolite_accumulation_not_direct_O2",
    scientific_observation="Recombinant UGT72AD1/UGT72Z2 assays identified 3-O monoglucosides from flavonol aglycones. Rhamnosyl(1-to-2) glucoside appears among transgenic metabolite accumulation, not as a demonstrated UDPGlc-mediated direct sugar-O2 extension of a flavonol 3-O glucoside substrate.",
    anchors=[evidence(lotus,40,["kaempferol","quercetin","flavonol 3-O-monoglucosides"]),
             evidence(lotus,58,["rhamnosyl","levels of F3 increased"]),
             evidence(lotus,65,["flavonol aglycones","3-O-glucosides"]),
             evidence(lotus,69,["enhanced levels","UDP-rhamnose"])],
    complete_reference_chemical_graph=False,current_epoch_fresh_qualified=False,
    permanent_exposure=True,possible_future_design_use="exposed_design_only"),
  dict(source_id="PMC6813240",doi="10.3389/fpls.2019.01330",article_subject="Freesia hybrida flavonoid 3-O GTs",
    exact_frozen_O2_reaction_supported=False,
    disposition="out_of_frozen_scope_flavonol_aglycone_3O_initial_glucosylation_not_sugar_residue_O2",
    scientific_observation="Source assays use UDP-glucose with flavonol/anthocyanidin aglycones and describe product 3-O-glucoside; no demonstrated direct transfer to the O2 of an existing flavonol 3-O glycoside in these cited reactions.",
    anchors=[evidence(freesia,4,["3-position of flavonoid","first enzymes"]),
             evidence(freesia,23,["flavonol aglycones","cyanidin 3-O-glucoside"]),
             evidence(freesia,26,["could glucosylate a series of aglycones"])],
    complete_reference_chemical_graph=False,current_epoch_fresh_qualified=False,
    permanent_exposure=True,possible_future_design_use="exposed_design_only")
 ]
 summary=dict(task=TASK,role="A6_reconciliation",epoch_id="SS-E02",
     timestamp=datetime.now(timezone.utc).isoformat(),source_count=2,sources=records,
     counts=dict(processed=2,original_publication_identity_verified=2,
         distinct_scientific_originals_screened=2,outside_current_O2_scope=2,
         current_O2_source_qualified=0,full_dual_graph_qualified=0,fresh_admitted=0,
         new_closure_groups=0,scientific_ABE_cells=0,new_HTTP=0,new_MCTS=0),
     limitations=["screened cited reactions only; no assertion that all other article chemistry is absent",
       "no complete reactant/product/donor/stereo graph; bounded source screen not a full qualification round",
       "same-epoch fresh status remains unverified; next epoch reuse blocked by permanent exposure"],
     read_original_scientific_body=True,read_model_outcome=False,
     no_scope_bank_change=True,human_reviewed=False)
 save(out/"source_scope_reconciliation.json",summary)
 freeze_stage_manifest(ROOT/G6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",
     [*frozen,out/"pre_execution.json",out/"source_scope_reconciliation.json"],
     G5,expected_previous_sha=sha(G5),family="SS",epoch_id="SS-E02")
 assert verify_stage_chain(ROOT/G6,sha(G6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
 reg=dict(task=TASK,event_type="SS_R12_G6_two_originals_screened_zero_qualification",
    epoch_id="SS-E02",family="SS",stage="G6_IDENTITY_STRUCTURE_ADMIT",status="active",
    registered_at=datetime.now(timezone.utc).isoformat(),
    stage_manifest_path=str(G6),stage_manifest_sha256=sha(G6),
    scope_manifest_sha256=sha(SCOPE),screened_sources=2,
    science_screen_only=True,complete_dual_graph=False,
    full_scientific_round=False,permanent_exposure=True,
    fresh_admitted=0,new_closure_groups=0,human_reviewed=False,
    approval_type="agent_delegated")
 write(TASK,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(reg,ensure_ascii=False,sort_keys=True)+"\n")
 event(TASK,"SS_R12_G6_screen_closed",originals=2,qualified=0,reason="different aglycone 3O reaction vs frozen sugar O2",G6_SHA=sha(G6))
 print(json.dumps(dict(A3_verified=2,A4_A5_screened=2,A6_scope_ineligible=2,fresh=0,G6_SHA=sha(G6))))
if __name__=="__main__":main()

