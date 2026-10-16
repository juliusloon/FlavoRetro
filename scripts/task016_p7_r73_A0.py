"""Freeze both R73 qualification contracts before any five-source science read."""
import json
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now
from scripts.task016_p7_orchestrate import role_manifest,freeze_stage_manifest,verify_stage_chain
from scripts import task016_p7_full_qualification_harness_v4 as fq
T='TASK-016-P7'; B=Path('outputs/task016-p7/v1')
A3DIR=B/'C/E02/fresh/C-E02-R71-five-JATS-front-identity-v1/recovery-v2/publisher-review-v3'
A3=A3DIR/'five_source_identity_dispositions.v3.json'; A3ROLE=A3DIR/'role_A3_manifest.v3.json'
PRE=B/'verification-v34-five-source-prior-alias-precheck-recovery-v2'
ADAPT=B/'governance/late_exposure_temporal_adapter_v1'
POLICY=B/'governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json'
UNKNOWN=B/'governance/unknown_prior_science_intake_v1/agent_delegated_prospective_decision.json'
REQ=B/'governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json'
ROUTES=['R70_official_advertised_PMC_S3_JATS_original_local_processing']
def base(f):return B/f'{f}/E02/fresh/{f}-E02-R73-five-originals-full-qualification-v1'
def stage(f):return B/f'{f}/E02/stages/batches/{f}-E02-R73-five-originals-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json'
def main(a11_review,a6_review):
 assert not any((ROOT/base(f)).exists() for f in ('C','SS'))
 # Review paths are mandatory immutable inputs, never inferred from chat.
 for p,role in [(a11_review,'A11'),(a6_review,'A6')]:
  review=load(p);assert review.get('agent_role')==role and review.get('safe_to_proceed_to_conditional_scientific_processing') is True and review.get('errors')==[]
 identity=load(A3);assert identity['processed']==identity['passed']==5 and identity['pending']==identity['rejected']==0 and identity['errors']==[]
 prior=load(PRE/'five_source_fixed_identity_metadata.v3.json'); assert len(prior['sources'])==5
 meta={x['source_id']:x for x in prior['sources']}
 adapter=load(ADAPT/'temporal_adapter_manifest.json'); assert adapter['prior_rows']==28 and adapter['current_rows']==24
 contracts={};raws=[]
 for family in ('C','SS'):
  r=base(family);g4=B/f'{family}/E02/stages/G4_SCOPE_FREEZE.json'
  sources=[];results=[]
  for row in identity['sources']:
   sid=row['source_id']; m=meta[sid]; raw={k:row['JATS_raw_pointer'][k] for k in ('path','sha256')};raws.append(Path(raw['path']))
   aliases=m['official_aliases'];assert 'article:'+row['PMCID'] in aliases and 'doi:'+row['DOI'].lower() in aliases
   precheck=[fq.pointer(PRE/'five_source_dispositions.v3.json'),fq.pointer(PRE/'prior_scientific_read_false_assessment.v4.json'),fq.pointer(PRE/'role_A6_manifest.v4.json')]
   sources.append(dict(source_id=sid,official_aliases=aliases,raw_status='available',raw_files=[raw],prior_scientific_read=None,prior_read_status='unknown',prior_uncertainty_blocks_qualification=True,prior_read_precheck_evidence=precheck,prior_scientific_read_recorded=False,prior_recorded_scope='Only bounded recorded project metadata: no known match is not proof of unread history.',planned_original_routes=ROUTES,source_metadata_title=m['full_titles'],full_alias_or_graph_historical_clearance=False,SIs_not_yet_in_this_raw_universe=True,SI_required_for_any_reaction_must_be_acquired_in_separate_preregistered_raw_route=True))
   results.append(dict(source_id=sid,identity_status='verified',official_aliases=aliases,unresolved_conflicts=[],evidence=[fq.pointer(A3),fq.pointer(A3ROLE),raw,m['authority_metadata']],publisher_literals_preserved=True,publisher_relation_not_legal_entity_equality=True))
  put(r/'raw_source_universe.json',dict(task=T,scientific_content_read=False,final_structures_provided=False,source_candidates=sources,metadata_only_dispositions=[],source_count=5,shared_source_count_across_C_SS=5,independence_group_count_not_doubled=True,prior_read_uncertainty_retained=True))
  put(r/'A3_source_results.json',dict(task=T,sources=results))
  role=role_manifest('A3',family+'-E02',[r/'raw_source_universe.json',A3,A3ROLE,PRE/'five_source_fixed_identity_metadata.v3.json',*sorted(set(raws))],[r/'A3_source_results.json'],dict(processed=5,passed=5,rejected=0,pending=0),pointers=[fq.pointer(A3),fq.pointer(A3ROLE)],read_holdout=False,read_model_outcome=False)
  role['scope']='Schema projection of independently verified A3 source identity; no new scientific eligibility or prior-read clearance.'
  put(r/'role_A3_manifest.json',role)
  ledger=B/'epoch_ledger.jsonl';data=(ROOT/ledger).read_bytes();epoch=B/'epochs'/(family+'-E02')/('epoch_state.v9.json' if family=='C' else 'epoch_state.v6.json')
  spec=dict(family=family,epoch_id=family+'-E02',batch_id=family+'-E02-R73-five-originals-full-qualification',G4=fq.pointer(g4),epoch_state=fq.pointer(epoch),epoch_ledger_prefix=dict(path=str(ledger),prefix_bytes=len(data),prefix_sha256=sha(ledger)),scope_manifest=fq.pointer(B/f'{family}/E02/scope_manifest.json'),scope_bank=fq.pointer(B/f'{family}/E02/scope_bank.json'),raw_source_universe=fq.pointer(r/'raw_source_universe.json'),A3_source_results=fq.pointer(r/'A3_source_results.json'),A3_role=fq.pointer(r/'role_A3_manifest.json'),prior_exposure_snapshot=fq.pointer(B/f'governance/prior_exposure_inventory_v4/prior_exposure_snapshot_{family}.json'),late_prior_design_files=[adapter['prior_exposure']],prior_current_evaluation_ledger=adapter['current_evaluation'],current_exposure_temporal_adapter=fq.pointer(ADAPT/'temporal_adapter_manifest.json'),future_G7_requirement=fq.pointer(REQ),policy=fq.pointer(POLICY),unknown_prior_intake_policy=fq.pointer(UNKNOWN),independent_intake_review=fq.pointer(a11_review),independent_exposure_projection_review=fq.pointer(a6_review),evaluation_events_directory=str(r/'evaluation_read_events'))
  cp=fq.freeze_full_qualification_contract(r/'full_qualification_contract.json',spec);v=fq.validate_full_qualification_contract(cp);assert v['source_candidates']==5 and v['admitted']==0
  contracts[family]=cp
  put(r/'pre_G5_contract_validation.json',dict(task=T,at=now(),family=family,source_candidates=5,A3_identity_passed=5,prior_scientific_read_unknown=5,science_admitted=0,actual_G4_scope_bank_and_v4_validated=True,unknown_cannot_be_qualified=True,HTTP=0,MCTS=0))
 for family in ('C','SS'):
  r=base(family);g4=B/f'{family}/E02/stages/G4_SCOPE_FREEZE.json';g5=stage(family)
  paths=[r/x for x in ('full_qualification_contract.json','raw_source_universe.json','A3_source_results.json','role_A3_manifest.json','pre_G5_contract_validation.json')]+sorted(set(raws))+[Path(__file__).relative_to(ROOT),a11_review,a6_review,ADAPT/'prior_exposure_rows.jsonl',ADAPT/'current_exposure_rows.jsonl',ADAPT/'temporal_adapter_manifest.json',UNKNOWN]
  freeze_stage_manifest(ROOT/g5.parent,'G5_FRESH_HOLDOUT_ACQUIRE',paths,g4,expected_previous_sha=sha(g4),family=family,epoch_id=family+'-E02')
  verify_stage_chain(g5,sha(g5))
  row=dict(task=T,epoch_id=family+'-E02',family=family,stage='G5_FRESH_HOLDOUT_ACQUIRE',status='active',event_type='R73_both_axes_preregistered_before_five_original_science',at=now(),stage_manifest_path=str(g5),stage_manifest_sha256=sha(g5),qualification_contract=contracts[family],source_count=5,prior_read_unknown=5,source_science_read=False,fresh_admitted=0,approval_type='agent_delegated',human_reviewed=False)
  ledger=B/'epoch_ledger.jsonl';write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,sort_keys=True)+'\n')
 shared=B/'governance/R73-five-originals-cross-axis-read-binding-v1/both_G5_ready_before_first_read.json'
 put(shared,dict(task=T,at=now(),approval_type='agent_delegated',human_reviewed=False,contracts=contracts,G5={f:fq.pointer(stage(f)) for f in ('C','SS')},shared_sources=identity['sources'] and list(meta),shared_source_original_files=[fq.pointer(x) for x in sorted(set(raws))],first_scientific_read_not_yet_started=all(not fq.evaluation_events(contracts[f]) for f in ('C','SS')),source_count=5,source_independence_groups_not_yet_established=True,prior_read_unknown=5,fresh_admitted=0,source_saturation=False))
 event(T,'R73_both_G5_before_five_original_science',shared_binding_SHA=sha(shared),source_count=5,fresh_admitted=0)
 print(json.dumps(dict(G5={f:sha(stage(f)) for f in ('C','SS')},science_reads=0,fresh_admitted=0)))
if __name__=='__main__':
 import sys
 main(Path(sys.argv[1]),Path(sys.argv[2]))
