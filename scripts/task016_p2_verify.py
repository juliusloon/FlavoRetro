"""Recompute engineering gates; failed scientific transfer prerequisites remain Partial."""
import sys,json,hashlib,statistics,subprocess,re
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
from flavoretro.resources import sha
from flavoretro.glycoside_library_v3 import load_registry
from flavoretro.glycoside_library import apply_template
from flavoretro.open_glycoside_library import structural_formation,normalize_species
from flavoretro.reviewed_resources import canonical_side,reaction_signature,load_review
from scripts.task016_p2_regression import verify as verify_experiment
from scripts.task016_p1_verify import template_key
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'outputs/task016-p2/v1';Q=ROOT/'outputs/task016-p2/v2'
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def read(n):return json.loads((Q/n).read_text())
def save(n,v,jl=False):write('TASK-016-P2',str((Q/n).relative_to(ROOT)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in v) if jl else json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def verify():
 baseline=json.loads((R/'execution-baseline.json').read_text());checks={};checks['fixed_approval']=sha(R/'execution-baseline.json')=='795ae452638fbaa42436771b1f9f9209aabcfdfd376aa5da907f9b4aa475f9f2' and baseline['approval_type']=='human_direct'
 drift=[p for p,h in baseline['protected_sha256'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h];checks['protected_inputs']=not drift
 c=read('experiment_contract.json');verify_experiment(c);checks['experiment_bindings']=True
 registry=load_registry();instances=rows(Q/'runtime_instances.jsonl');hold=rows(Q/'holdout_views.jsonl');templates=registry.templates;old=rows(ROOT/'outputs/task016-p1/v2/templates.jsonl');by=registry.instances;new=[t for t in templates if t['template_id'].startswith('p2-scope:')]
 split=read('development_split_manifest.json');checks['split_hashes']=all(sha(Q/p)==h for p,h in split['files_sha256'].items());checks['build_only']=len(instances)==85 and len(hold)==0 and all(r['template_role']=='development_build' for r in instances) and all(i in by for t in templates for i in t['support_instances'])
 checks['legacy_roles_preserved']=len(rows(Q/'legacy_roles.jsonl'))==85 and all(r['original_P1_role']==next(x['template_role'] for x in rows(ROOT/'outputs/task016-p1/v2/instances.jsonl') if x['instance_id']==r['instance_id']) for r in instances)
 checks['old_templates_equal']=all(next(t for t in templates if t['template_id']==o['template_id'])==o for o in old)
 keys=[template_key(t) for t in templates];checks['template_semantic_dedup']=len(keys)==len(set(keys))
 save('template_groups.jsonl',[dict(template_id=t['template_id'],category=t['category'],role=t['template_role'],canonical_semantic_key_sha256=hashlib.sha256(k.encode()).hexdigest(),definition='map-stripped canonical reaction graphs plus declared scope and necessary context') for t,k in zip(templates,keys)],True)
 checks['new_scope_support']=len(new)==3 and Counter(t['category'] for t in new)==Counter({'C_formation':1,'sugar_sugar_formation':2}) and all(len({by[i]['acceptor'] for i in t['support_instances']})>=2 for t in new)
 tv=rows(Q/'template_validation.jsonl');supports=[ch for v in tv for ch in v['checks'] if ch['kind']=='support_replay'];bounds=[ch for v in tv for ch in v['checks'] if ch['kind']!='support_replay']
 checks['support_replay']=len(supports)==134 and len(tv)==54 and all(v['passed'] and all(ch['passed'] for ch in v['checks']) for v in tv)
 checks['new_scope_boundaries']=len(bounds)==12 and all(sum(ch['kind']!='support_replay' for ch in v['checks'])>=4 for v in tv if v['template_id'].startswith('p2-scope:')) and read('scope_boundary_validation.json')['passed']
 checks['mapped_source_actions']=read('build_action_validation.json')['passed'] and read('build_action_validation.json')['source_replays']==134
 checks['source_formation']=all(structural_formation(r['acceptor'],r['donor'],r['target'])['family']==r['category'] for r in instances)
 withdrawn={r['instance_id'] for r in rows(Q/'provisional_withdrawn_instances.jsonl')};checks['withdrawn_not_runtime']=len(withdrawn)==2 and not withdrawn&set(by)
 checks['old_unresolved_untouched']=len(rows(ROOT/'outputs/task016-p1/v2/unresolved_instances.jsonl'))==12
 checks['config_copies_default_off']=sha(ROOT/'configs/glycoside-library-v3.json')==sha(ROOT/'flavoretro/assets/configs/glycoside-library-v3.json') and not json.loads((ROOT/'configs/glycoside-library-v3.json').read_text())['default_enabled']
 checks['default_off']=read('default_off_regression.json')['equal'];checks['v1_v2']=read('v1_v2_regression.json')['v1_supports_passed'] and read('v1_v2_regression.json')['v2_supports_passed'];checks['installed_package']=read('package_validation.json')['passed'];checks['missing_assets']=read('package_validation.json')['missing_assets_fail_closed'];checks['core_byte_rebuild']=read('replay.json')['passed'] and read('replay.json')['rebuilt_files']==8
 full=read('full_regression.json');checks['full_tests']=full['exit_code']==0 and full['tests']==124 and full['passed']==124 and sha(ROOT/full['operation_log'])==full['operation_log_sha256'] and 'Ran 124 tests' in (Q/'full_regression.log').read_text()
 af=read('asset_free_regression.json');checks['asset_free_tests']=af['exit_code']==0 and af['passed']==117 and af['skipped']==7
 obs=rows(Q/'mcts_observations.jsonl');results={o['run_id']:json.loads((ROOT/o['result_path']).read_text()) for o in obs};checks['old_matrix_complete']=len(obs)==51 and len({(r['target'],r['seed'],r['arm']) for r in obs})==51 and all(o['status']=='ok' and o['arm']=='D' and sha(ROOT/o['result_path'])==o['result_sha256'] for o in obs)
 checks['real_engine']=all(r['execution_source']=='live_aizynthfinder_mcts' for r in results.values())
 first=next(iter(results.values()));checks['review_stock_models_stable']=load_review().binding==c['review_binding'] and sorted(load_review().keys)==c['stock_keys'] and len(c['stock_keys'])==17 and all(r['review_binding']==c['review_binding'] and r['assets']==first['assets'] for r in results.values())
 checks['same_fixed_requests']=all(r['request']==dict(smiles=o['target'],seed=o['seed'],candidate_stock=True,glycoside_expansion=True,glycoside_library_version='v3',**c['budget']) for o in obs for r in [results[o['run_id']]])
 checks['fixed_phase_budget']=all(p['budget']=={k:v for k,v in c['budget'].items() if k not in ['mode','engine','top_k']} and p['node_count']<=120 and p['wall_seconds']<=60 for r in results.values() for p in r['phases'])
 legacy=read('legacy_regression.json');checks['old_SS_repaired']=legacy['old_SS_all_three_seed_created']==4;checks['old_C_retained']=legacy['old_C_all_three_seed_created']==5;checks['old_O_retained']=legacy['old_O_all_three_seed_created']==7
 trace=rows(Q/'action_trace.jsonl');protection=[];displacement=[];domain=[e for e in trace if e['stage']=='mcts_action_created' and e.get('policy')=='glycoside']
 for o in obs:
  ev=results[o['run_id']]['action_trace'];groups=defaultdict(list)
  for e in ev:groups[e['target']].append(e)
  for target,es in groups.items():
   required={e['signature'] for e in es if e['stage']=='generic_protection_checked' and not e.get('rejected') and e.get('signature')}
   retained={e['signature'] for e in es if e['stage']=='after_truncation' and e.get('signature')}
   protection.append(dict(run_id=o['run_id'],seed=o['seed'],target=target,required=sorted(required),missing=sorted(required-retained),passed=required<=retained))
   generated={e['signature'] for e in es if e['stage']=='generated' and e.get('policy')!='glycoside' and e.get('signature')}
   displacement.append(dict(run_id=o['run_id'],seed=o['seed'],target=target,generated_generic_not_retained=sorted(generated-retained),claim='includes ordinary generic truncation, not a measured D-versus-A displacement; no fresh A run'))
 checks['generic_protection']=bool(protection) and all(p['passed'] for p in protection)
 save('mcts_generic_protection.json',dict(passed=checks['generic_protection'],checks=protection,violations=sum(not p['passed'] for p in protection),scope='within-D filtered top-three checks; not a fresh paired A/B coverage experiment'))
 save('candidate_displacement.json',dict(paired_A_B_D_displacement=None,paired_measurement_status='not_executed_below_G2',generic_protection_violations=sum(not p['passed'] for p in protection),D_generic_truncation_records=displacement,chemical_value_of_other_displaced_candidates='unknown'))
 def valid_evidence(e):
  v=e['metadata']['task016_evidence'];support=v['source_instance_ids'];sig=reaction_signature(e['precursor_smiles'],[normalize_species(e['target'])['normalized']]);exact=any(by[i]['reference_signature']==sig for i in support)
  return v['template_source_support'] and all(i in by for i in support) and v['exact_seed_instance_match']==exact and all(not v[k] for k in ['prediction_conditions_verified','actionable','evidence_closed','human_reviewed','independent_chemical_validation','original_conditions_copied']) and v['yield_value'] is None
 checks['action_evidence_axes']=bool(domain) and all(valid_evidence(e) for e in domain)
 save('transfer_validation.jsonl',domain,True)
 ledger=rows(R/'run_ledger.jsonl');started=[r for r in ledger if r['phase']=='started'];finished=[r for r in ledger if r['phase']=='finished'];ids={r['run_id'] for r in started};eng=[r for r in started if r['purpose']=='task016_p2_engineering'];val=[r for r in started if r['purpose']=='task016_p2_validation']
 checks['budget_conservation']=len(ids)==len(started)==len(finished) and {r['run_id'] for r in finished}==ids and len(started)<=240 and len(eng)<=27 and len(val)<=213 and {r['run_id'] for r in val}==set(results)
 checks['budget_binding']=all(r['budget_binding']==sha(R/'execution-baseline.json') and r['ceiling']==240 for r in ledger)
 checks['service_wall_limit']=all(r['wall_seconds']<=60 for r in finished)
 events=rows(ROOT/'operations/events.jsonl');windows=[]
 for end in events:
  av=end.get('argv',[])
  if end.get('task')=='TASK-016-P2' and end.get('action')=='command_end' and ('unittest' in av or 'scripts/task016_p2_asset_free.py' in av):
   start=next(e for e in reversed(events[:events.index(end)]) if e.get('task')=='TASK-016-P2' and e.get('action')=='command_start' and e.get('argv')==av)
   windows.append((start['time'],end['time'],end['log'],end.get('returncode')))
 fixtures=[]
 for fin in finished:
  st=next(r for r in started if r['run_id']==fin['run_id'])
  if fin['status']=='error' and st['purpose']=='task016_p2_engineering' and st['request']['smiles']=='CCO':
   w=next(w for w in windows if w[0]<=st['at']<=w[1])
   fixtures.append(dict(run_id=fin['run_id'],classification='synthetic mocked worker failure fixture',operation_log=w[2],operation_returncode=w[3],error_code=fin['error']['code'],conservative_reserved=True,actual_worker_MCTS=False,proof='test_timeout_recorded_no_fallback and test_engine_failure_recorded use mocked subprocess; request/time bound to recorded full or asset-free suite',test_source_sha256=sha(ROOT/'tests/test_contracts.py')))
 checks['fixture_accounting']=len(fixtures)==6 and Counter(f['error_code'] for f in fixtures)==Counter({'timeout':3,'engine_error':3})
 save('fixture_ledger_annotations.jsonl',fixtures,True)
 budget=dict(conservative_reserved_attempts=len(started),finished=len(finished),validation_attempts=len(val),engineering_attempts=len(eng),synthetic_error_fixtures=len(fixtures),actual_service_attempts=len(started)-len(fixtures),actual_ok=sum(r['status']=='ok' for r in finished),actual_errors=sum(r['status']!='ok' for r in finished)-len(fixtures),ceilings=dict(total=240,validation=213,engineering=27),max_wall_seconds=max(r['wall_seconds'] for r in finished),actual_max_wall_seconds=max(r['wall_seconds'] for r in finished if r['run_id'] not in {f['run_id'] for f in fixtures}),old_TASK016_reserved=33,old_P1_reserved=216,old_ledgers_unchanged=checks['protected_inputs'])
 source=read('source_yield_inventory.json');checks['source_files_conserved']=source['raw_file_difference']==0 and source['pending_reservations']==0 and source['record_disposition_difference']==0 and source['query_rows']==len(rows(Q/'source_query_record_dispositions.jsonl')) and all(r['hash_verified'] and sha(ROOT/r['path'])==r['sha256'] for r in rows(Q/'file_dispositions.jsonl'))
 checks['tracked_source_budget']=source['new_HTTP_attempts']+source['external_tool_request_units']<=2500 and source['new_raw_bytes']<=2*1024**3 and source['metadata_records']<=5000 and source['new_attempted_article_versions']<=120 and source['new_attachment_attempted_files']<=240
 tracked=subprocess.run(['git','ls-files','--','data/raw/task016-p2','outputs/task016-p2','outputs/validation/task016-p2-package','outputs/validation/task016-p2-asset-free-r2'],cwd=ROOT,text=True,capture_output=True);event('TASK-016-P2','git_source_boundary_check',argv=tracked.args,returncode=tracked.returncode);checks['source_not_tracked']=tracked.returncode==0 and not tracked.stdout.strip()
 thresholds=dict(fresh_targets=6,closed_source_groups=2,gained_targets=3,common_gap_recovery_fraction=.5,successful_source_groups=2,seeds=[0,1,2])
 family={k:dict(status='Partial',transfer_status='not_executed_below_G2',N_family=0,N_gap=None,G_family=None,recovery_rate=None,actual_transfer_targets=None,source_groups=0,successful_source_groups=None,loss_A=None,loss_B=None,net_coverage_A=None,net_coverage_B=None,thresholds=thresholds,qualified_panel=False) for k in ['C_formation','sugar_sugar_formation']}
 save('metrics_by_family.json',dict(overall_status='Partial',engineering_status='Completed' if all(checks.values()) else 'Partial',C_transfer_status='Partial',sugar_sugar_transfer_status='Partial',families=family,fresh_ABD_matrix_cells=0,old_regression=dict(runs=51,targets=17,old_SS=4,old_SS_created_all_seeds=4,old_C_created_all_seeds=5,old_O_created_all_seeds=7,old_1b_created_all_seeds=False,not_new_transfer=True),templates=dict(total=54,exact=46,scopes=8,new_C_scopes=1,new_SS_scopes=2),build_instances=85,covalent_reactions=58,new_confirmed_reactions=0,support_replays=134,new_scope_boundary_checks=18,run_budget=budget,development_exposed=True,training_overlap='unknown',human_reviewed=False,independent_chemical_validation=False,conditions_verified=False,evidence_closed=0,formal_run_ready=False,release_ready=False))
 strata=[dict(template_id=t['template_id'],category=t['category'],sugar_type=t['sugar_type'],center=t['scope']['center_class'],acceptors=len({by[i]['acceptor'] for i in t['support_instances']}),support_instances=t['support_instances'],source_pmcs=sorted({by[i]['provenance'].get('pmcid') for i in t['support_instances']}),evidence='source/build scope support only',fresh_holdout=0,fresh_transfer=None) for t in new]
 save('stratum_support.json',dict(strata=strata,uncovered_or_unvalidated=['direct flavone/flavonol C6/C8 transfer','C-rhamnosyl intermediate identity and dehydration separation','new C scope targets beyond exposed phloretin supports','new Glc/Gal/Rha sugar-chain transfer targets','1-to-6,1-to-3 and anthocyanin chain generalization'],O_gains_not_used_to_compensate=True))
 save('counting_contract.json',dict(confirmed_instances=85,unique_covalent_reactions=58,new_confirmed_reactions=0,withdrawn_encoding=2,runtime_role='build_calibration_only',physical_replicates='not inferred',categories=dict(Counter(r['category'] for r in rows(Q/'reaction_groups.jsonl'))),source_unresolved_records=10,inherited_unresolved_contexts=12,zero_not_missing=True))
 for n in ['single_step_A_B_D.jsonl','gap_register.jsonl','paired_results.jsonl']:save(n,[],True)
 save('evaluation_reference_manifest.json',dict(fresh_status='not_executed_below_G2',fresh_references=[],legacy_references=c['references'],experiment_sha256=sha(Q/'experiment_contract.json'),empty_files_are_unexecuted_not_zero_gain=True))
 save('costs.json',dict(run_budget=budget,source_budget=source,total_finished_service_wall_seconds=sum(r['wall_seconds'] for r in finished),median_old_D_service_wall_seconds=statistics.median(o['wall_seconds'] for o in obs),sum_old_D_search_seconds=sum(p['search_seconds'] for r in results.values() for p in r['phases']),domain_actions_by_stage=dict(Counter(e['stage'] for e in trace if e.get('policy')=='glycoside')),all_action_trace_records=len(trace),bounded_source_exhaustive=False))
 report=dict(engineering_passed=all(checks.values()),overall_status='Partial',scientific_acceptance_passed=False,checks=checks,failed_engineering_checks=[k for k,v in checks.items() if not v],protected_files=len(baseline['protected_sha256']),protected_drift=drift,scientific_gates=dict(C_fresh_panel=False,SS_fresh_panel=False,C_dual_baseline_gain=None,SS_dual_baseline_gain=None,C_three_seed_transfer=None,SS_three_seed_transfer=None),source_HTTP_boundary='209 direct HTTP attempts plus 8 external tool request units tracked; internal web-provider HTTP count unavailable',limitations=['no qualified fresh six-target/two-source panel in either family','no fresh A/B/D matrix or gain/loss estimates','old four SS fixes are exposed build/calibration, not independent transfer','source candidates and 35 title-only article candidates remain pending; intake is not exhaustive','two C8 provisional encodings withdrawn for unbound complete sugar stereo','one source TcCGT byproduct C-versus-7-O conflict retained','synthetic errors and failed first asset-free harness preserved','development exposure and unknown model training overlap; no chemistry/activity/conditions/yield/supply/blind/release claim'])
 save('audit.json',report);print(json.dumps(dict(engineering_passed=report['engineering_passed'],checks_passed=sum(checks.values()),checks_total=len(checks),failed=report['failed_engineering_checks'],overall_status='Partial',run_budget=budget),ensure_ascii=False,indent=2));assert report['engineering_passed'],report['failed_engineering_checks']
if __name__=='__main__':verify()
