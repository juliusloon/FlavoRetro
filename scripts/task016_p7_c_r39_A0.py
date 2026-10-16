"""R39 prospective full qualification of one selected original, before any body science."""
import json,re,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import sha,load,lines,put,now
from scripts import task016_p7_full_qualification_harness_v3 as fq
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain,role_manifest
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1"
A3=B/"C/E02/fresh/C-E02-R38-isoorientin-original-custody-v1/A3_original_front_identity.json"
SI=B/"C/E02/fresh/C-E02-R40-advertised-SI-custody-v1"
G4=B/"C/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
POLICY=B/"governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json"
REQ=B/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json"
def main():
 if (ROOT/R).exists():raise RuntimeError("IMMUTABLE")
 a=load(A3);ex=lines(SI/"execution.jsonl")
 assert len(ex)==2 and {x["query_id"] for x in ex}=={"R40-index","R40-SI"}
 original=Path(a["original_raw"]["path"])
 cross=json.loads((ROOT/a["Crossref_raw"]["path"]).read_bytes())["message"]
 expected=next(x["metadata"] for x in lines(B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1/metadata_unique_sources.jsonl") if x["metadata"]["pmcid"]==a["PMCID"])
 checks=dict(DOI=a["DOI"]==expected["doi"]==cross["DOI"].lower(),title=a["original_identity_verified"],journal=a["journal"].casefold()==expected["journalTitle"].casefold()==cross["container-title"][0].casefold(),year=expected["pubYear"] in a["years"] and int(expected["pubYear"]) in [d[0] for k in ["published","published-print","published-online"] for d in cross.get(k,{}).get("date-parts",[])],volume=a["volume"]==expected["journalVolume"]==cross["volume"],issue=a["issue"]==expected["issue"]==cross["issue"],article_number=a["fpage"]==expected["pageInfo"]==cross["article-number"]==cross["page"],publisher="elsevier" in a["Crossref_publisher"].casefold())
 assert all(checks.values()),checks
 raw=[dict(path=str(original),sha256=a["original_raw"]["sha256"])]
 si=next(x for x in ex if x["query_id"]=="R40-SI")
 if si["status"]=="available":
  p=Path(si["raw_pointer"]["path"]);assert sha(p)==si["raw_pointer"]["sha256"] and (ROOT/p).read_bytes().startswith(b"PK")
  raw.append(dict(path=str(p),sha256=si["raw_pointer"]["sha256"]))
 inventory=B/"governance/prior_exposure_inventory_v3/prior_exposure_snapshot_C.json"
 aliases=set(a["official_aliases"]);prior=lines(B/"governance/prior_exposure_inventory_v3/prior_exposure_rows.jsonl")
 assert not any(aliases.intersection(x["closure_tokens"]) for x in prior)
 allmeta=lines(B/"C/E02/fresh/C-E02-R37-recent-C-primary-metadata-v1/metadata_unique_sources.jsonl")
 universe=dict(task=T,scientific_content_read=False,final_structures_provided=False,source_candidates=[dict(source_id=a["PMCID"],official_aliases=a["official_aliases"],raw_status="available",raw_files=raw,prior_scientific_read=False,prior_scientific_read_basis="No known official article/DOI/PMID tokens in full SHA-bound 5199-row prior exposure snapshot; complete graph/alias chemistry remains explicitly unresolved and cannot admit automatically.",full_alias_or_graph_historical_clearance=False,planned_original_routes=["EuropePMC_fullTextXML","PMC_exact_index_advertised_SI"],intake_evidence=[fq.pointer(A3),fq.pointer(SI/"object_index_projection.json"),fq.pointer(SI/"execution.jsonl")])],metadata_only_dispositions=[dict(source_id=x["metadata"].get("doi") or x["metadata"].get("id"),title=x["metadata"]["title"],disposition="not_selected_for_this_bounded_original_round",reason="Source selected prospectively as recent direct isoorientin biosynthesis; all other title hints retained, not chemical rejection or source absence.") for x in allmeta if x["metadata"]["pmcid"]!=a["PMCID"]],selection_reason="One fixed primary original with direct target-biosynthesis title, currently absent known historical source aliases; source and graphs remain unqualified.")
 put(R/"raw_source_universe.json",universe)
 results=dict(task=T,sources=[dict(source_id=a["PMCID"],identity_status="verified",official_aliases=a["official_aliases"],unresolved_conflicts=[],evidence=[fq.pointer(A3),fq.pointer(Path(a["original_raw"]["path"])),fq.pointer(Path(a["Crossref_raw"]["path"]))],field_checks=checks,print_date="Crossref formal issue 2026-12; original/EPMC online 2026-08, same year; future print month retained.")])
 put(R/"A3_source_results.json",results)
 role=role_manifest("A3","C-E02",[R/"raw_source_universe.json",A3,Path(a["original_raw"]["path"]),Path(a["Crossref_raw"]["path"])],[R/"A3_source_results.json"],dict(processed=1,passed=1,rejected=0,pending=0),pointers=[fq.pointer(A3)],read_holdout=False,read_model_outcome=False)
 put(R/"role_A3_manifest.json",role)
 ledger=B/"epoch_ledger.jsonl";data=(ROOT/ledger).read_bytes()
 spec=dict(family="C",epoch_id="C-E02",batch_id="C-E02-R39-prospective-full-qualification",G4=fq.pointer(G4),epoch_state=fq.pointer(B/"epochs/C-E02/epoch_state.v9.json"),epoch_ledger_prefix=dict(path=str(ledger),prefix_bytes=len(data),prefix_sha256=sha(ledger)),scope_manifest=fq.pointer(B/"C/E02/scope_manifest.json"),scope_bank=fq.pointer(B/"C/E02/scope_bank.json"),raw_source_universe=fq.pointer(R/"raw_source_universe.json"),A3_source_results=fq.pointer(R/"A3_source_results.json"),A3_role=fq.pointer(R/"role_A3_manifest.json"),prior_exposure_snapshot=fq.pointer(inventory),late_prior_design_files=[],future_G7_requirement=fq.pointer(REQ),policy=fq.pointer(POLICY),evaluation_events_directory=str(R/"evaluation_read_events"))
 contract=fq.freeze_full_qualification_contract(R/"full_qualification_contract.json",spec)
 validated=fq.validate_full_qualification_contract(contract)
 put(R/"pre_G5_contract_validation.json",dict(task=T,at=now(),source_candidates=validated["source_candidates"],identity_pending=validated["source_identity_pending"],admitted=validated["admitted"],actual_G7_panel_ready=validated["actual_G7_panel_ready"],validator_path="scripts/task016_p7_full_qualification_harness_v3.py",validator_SHA=sha(Path("scripts/task016_p7_full_qualification_harness_v3.py")),actual_C_G4_and_list_scope_bank_used=True))
 inputs=[Path(contract["path"]),R/"raw_source_universe.json",R/"A3_source_results.json",R/"role_A3_manifest.json",R/"pre_G5_contract_validation.json"]+[Path(x["path"]) for x in raw]
 freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",inputs,G4,expected_previous_sha=sha(G4),family="C",epoch_id="C-E02")
 verify_stage_chain(ROOT/G5,sha(G5))
 row=dict(task=T,epoch_id="C-E02",family="C",stage="G5_FRESH_HOLDOUT_ACQUIRE",status="active",event_type="R39_prospective_full_qualification_before_original_science",at=now(),stage_manifest_path=str(G5),stage_manifest_sha256=sha(G5),qualification_contract=contract,source_count=1,source_science_read=False,fresh_admitted=0,approval_type="agent_delegated",human_reviewed=False)
 write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,sort_keys=True)+"\n")
 event(T,"C_R39_G5_before_full_qualification_science",G5_SHA=sha(G5),source_count=1,original_files=len(raw))
 print(json.dumps(dict(G5=sha(G5),source_candidates=1,raw_original_files=len(raw),validated_actual_G4=True,admitted=0)))
if __name__=="__main__":main()
