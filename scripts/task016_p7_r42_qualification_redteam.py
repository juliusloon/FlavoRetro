"""Actual R39 v3 contract + science round red-team, with isolated nonadmitting counterfactuals."""
import copy,json,hashlib
from pathlib import Path
from unittest.mock import patch
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import load,put,sha,now,lines
from scripts import task016_p7_full_qualification_harness_v3 as fq
from scripts.task016_p7_orchestrate import ContractError
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1"
O=B/"verification-v28-C-R39-full-qualification/counterfactuals"
G5=B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
checks=[]
def check(n,ok,detail=None):
 checks.append(dict(check=n,passed=bool(ok),detail=detail))
def deny(n,call,fragment):
 try:
  value=call()
 except ContractError as exc:
  check(n,fragment in str(exc),str(exc));return
 check(n,False,"Unexpectedly accepted: "+str(value)[:160])
def main():
 assert not (ROOT/O).exists()
 cp=fq.pointer(R/"full_qualification_contract.json");g5=fq.pointer(G5);spec=load(Path(cp["path"]));rp=fq.pointer(R/"full_round_manifest.json")
 valid=fq.validate_full_science_round(cp,g5,rp)
 check("actual_deferred_round_complete_without_admission",valid["round_execution_complete"] and valid["fresh_admitted"]==0 and not valid["qualified_for_final_G7_review"])
 def contract_bad(name,edit,fragment):
  s=copy.deepcopy(spec);edit(s);deny(name,lambda:fq._validate_spec(s,ROOT),fragment)
 contract_bad("actual_validator_binding_missing",lambda s:s["implementation_files_sha256"].pop("scripts/task016_p7_full_qualification_harness_v3.py"),"actual qualification validator implementation")
 contract_bad("physical_vs_canonical_scope_digest_conflict",lambda s:s.update(scope_bank_json_sha256="0"*64),"physical and canonical scope digest drift")
 contract_bad("source_universe_changed_after_freeze",lambda s:s.update(source_candidate_ids=[]),"selected-source universe drift")
 # Exercise all terminal epoch variants using isolated registry copies; actual registry untouched.
 ledger=(ROOT/spec["epoch_ledger_prefix"]["path"]).read_bytes()
 for event in ("epoch_incomplete_decision","epoch_invalidation","epoch_invalidated","epoch_closed","epoch_complete"):
  rel=O/("registry-"+event+".jsonl")
  data=ledger+json.dumps(dict(task=T,family="C",epoch_id="C-E02",event_type=event,status="counterfactual",not_a_real_epoch_event=True)).encode()+b"\n"
  write(T,str(rel),data.decode())
  s=copy.deepcopy(spec);s["epoch_ledger_prefix"]=dict(path=str(rel),prefix_bytes=len(data),prefix_sha256=sha(rel))
  deny("terminal_event_"+event,lambda s=s:fq._state_epoch_open(s,ROOT),"closed epoch")
 deny("reader_replay_requires_explicit_recovery",lambda:fq.open_for_first_scientific_read(cp,g5,"PMC13564134","A4","A4-counterfactual-no-open"),"reader already registered")
 checked=fq.validate_full_qualification_contract(cp)
 old=copy.deepcopy(checked["meta"]["prior"])
 old.append(dict(development_exposed=True,exposure_type="historical_design",closure_tokens=["article:PMC13564134"]))
 with patch.object(fq,"_exposure_rows",return_value=old):
  deny("known_prior_source_alias_blocks_read_before_payload",lambda:fq.open_for_first_scientific_read(cp,g5,"PMC13564134","A4","A4-counterfactual-prior-no-open"),"known prior/design source")
 with patch.object(fq,"evaluation_events",return_value=[]):
  deny("completed_science_requires_actual_G5_read_receipts",lambda:fq.validate_full_science_round(cp,g5,rp),"scientific read lacks prospective G5 receipt")
 def variant(name,role,edit,role_edit=None):
  result=copy.deepcopy(load(R/role/"round_result.json"));edit(result)
  rel=O/name/(role+"_result.json")
  put(rel,dict(result,counterfactual_only=True,never_admit=True))
  roleobj=copy.deepcopy(load(R/role/"role_manifest.json"))
  key="output_file_sha" if "output_file_sha" in roleobj else "output_file_sha256"
  roleobj[key].pop(str(R/role/"round_result.json"))
  roleobj[key][str(rel)]=sha(rel)
  if role_edit:role_edit(roleobj)
  rr=O/name/(role+"_role.json");put(rr,roleobj)
  obj=copy.deepcopy(load(Path(rp["path"])));obj[role+"_result"]=fq.pointer(rel);obj[role+"_role"]=fq.pointer(rr)
  dest=O/name/"round_manifest.json";put(dest,obj);return fq.pointer(dest)
 v=variant("omitted_original_route","A4",lambda x:x["source_dispositions"][0].update(original_routes_executed=["EuropePMC_fullTextXML"]))
 deny("omitted_original_SI_route_is_not_complete",lambda:fq.validate_full_science_round(cp,g5,v),"original access route plan")
 v=variant("available_but_unread","A4",lambda x:x["source_dispositions"][0].update(scientific_body_read=False))
 vv=fq.validate_full_science_round(cp,g5,v)
 check("available_unread_original_keeps_round_incomplete",not vv["round_execution_complete"] and any("available_original_not_scientifically_processed" in x for x in vv["unprocessed"]) and vv["fresh_admitted"]==0,vv["unprocessed"])
 v=variant("omitted_reaction","A6",lambda x:x.update(reaction_dispositions=[]))
 deny("A6_must_dispose_complete_reaction_union",lambda:fq.validate_full_science_round(cp,g5,v),"A6 must dispose complete")
 def fakequal(x):
  x["source_dispositions"][0]["disposition"]="qualified";x["reaction_dispositions"][0]["disposition"]="qualified"
 v=variant("qualified_without_molecular_graphs","A6",fakequal)
 deny("qualification_without_both_full_graphs_fails",lambda:fq.validate_full_science_round(cp,g5,v),"qualified full structure records absent")
 def peer(x):x["read_other_extractor_output"]=True
 v=variant("peer_output_read","A4",lambda x:None,peer)
 deny("peer_output_read_invalidates_independent_extractor",lambda:fq.validate_full_science_round(cp,g5,v),"extractor read peer final output")
 check("actual_scientific_event_universe_unchanged",len(fq.evaluation_events(cp))==4)
 result=dict(task=T,agent_role="A8",approval_type="agent_delegated",human_reviewed=False,at=now(),counterfactual_artifacts_never_admit=True,actual_contract=cp,actual_round=rp,checks=checks,passed=sum(x["passed"] for x in checks),failed=sum(not x["passed"] for x in checks),scope_modified=False,new_HTTP=0,new_MCTS=0,actual_fresh_admitted=0,qualified_candidate_path_live_exercised=False,tests_limit="Actual deferred branch and specified fail-closed gates exercised; no claim that a live qualified candidate or final G7 panel has passed.")
 put(O/"red_team_results.json",result)
 print(json.dumps(dict(passed=result["passed"],failed=result["failed"],new_science_opens=0)))
 if result["failed"]:raise RuntimeError("RED_TEAM_FAILURE")
if __name__=="__main__":main()
