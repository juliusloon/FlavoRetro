"""Recompute qualified final gates; preserve original version audits and all run failures."""
import hashlib,json,statistics,subprocess,xml.etree.ElementTree as ET
from collections import Counter
from scripts.task016_p1_sources import ROOT,OUT as ORIGINAL,RAW,rows,TASK
from scripts.task016_p1_qualify import QUALIFIED as OUT,save_at
from scripts.task016_p1_verify import template_key
from scripts.task016_p1_revalidate_qualified import verify_binding
from scripts.task016_p1_evaluate import signatures,request
from flavoretro.resources import sha
from flavoretro.glycoside_library import load_registry,apply_template
from flavoretro.glycoside_expansion import load_registry as load_v1,apply_template as apply_v1
from flavoretro.open_glycoside_library import structural_formation,normalize_species
from flavoretro.reviewed_resources import canonical_side,reaction_signature

def verify():
    c=json.loads((OUT/'experiment_contract.json').read_text());verify_binding(c)
    baseline=json.loads((ORIGINAL/'execution-baseline.json').read_text());checks={}
    checks['protected_inputs']=all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in baseline['protected_sha256'].items())
    registry=load_registry();instances=rows(OUT/'instances.jsonl');build=rows(OUT/'runtime_instances.jsonl');hold=rows(OUT/'holdout_views.jsonl');groups=rows(OUT/'reaction_groups.jsonl');templates=registry.templates;validation=rows(OUT/'template_validation.jsonl');split=json.loads((OUT/'development_split_manifest.json').read_text());qualification=json.loads((OUT/'qualification_manifest.json').read_text());counts=json.loads((OUT/'counting_contract.json').read_text())['counts']
    checks['split_hashes']=all(sha(OUT/p)==h for p,h in split['files_sha256'].items())
    checks['qualification_hashes']=all(sha(OUT/p)==h for p,h in qualification['files_sha256'].items())
    checks['holdout_not_reselected']=sha(OUT/'holdout_views.jsonl')==sha(ORIGINAL/'holdout_views.jsonl') and all(r['source_group']==next(q['source_group'] for q in rows(ORIGINAL/'instances.jsonl') if q['instance_id']==r['instance_id']) for r in instances)
    checks['reaction_isolation']=not {r['covalent_signature'] for r in hold}&{r['covalent_signature'] for r in build}
    def publication_keys(rr):return {k for r in rr for k in [r['provenance'].get('pmcid'),r['provenance'].get('doi')] if k}
    checks['publication_isolation']=not publication_keys(hold)&publication_keys(build)
    checks['assay_isolation']=not {r['actual_assay_group'] for r in hold}&{r['actual_assay_group'] for r in build}
    checks['runtime_build_only']=all(r['template_role']=='development_build' for r in registry.instances.values()) and all(i in registry.instances for t in templates for i in t['support_instances'])
    checks['holdout_not_whitelisted']=not {r['target'] for r in hold}&{x for t in templates for x in t['allowed_targets']}
    checks['holdout_not_runtime_source']=all(not any(r['provenance']['raw_path']==p for r in hold) for p in registry_manifest()['raw_dependencies_sha256'])
    checks['task015_publication_isolation']=json.loads((ORIGINAL/'task015_publication_overlap_audit.v2.json').read_text())['passed']
    excluded=set(qualification['excluded_instance_ids']);checks['uncertain_products_not_executable']=not excluded&set(registry.instances) and all(not set(t['support_instances'])&excluded for t in templates) and all(not (r['provenance'].get('pmcid')=='PMC9149423' and r['sugar_type']=='galactose') for r in instances)
    dispositions=rows(OUT/'assay_record_dispositions.jsonl');checks['annotation_conservation']=len(dispositions)==93 and Counter(r['disposition'] for r in dispositions)==Counter({'admitted':81,'retained_unresolved_product_identity':12}) and len(rows(OUT/'unresolved_instances.jsonl'))==12
    checks['source_formation_consistency']=all(structural_formation(r['acceptor'],r['donor'],r['target'])['family']==r['category'] for r in instances)
    provenance=[];xml={}
    for r in instances:
        if r.get('inherited'):continue
        p=r['provenance'];path=p['raw_path'];valid=sha(ROOT/path)==p['raw_sha256']
        if path not in xml:xml[path]=ET.parse(ROOT/path).getroot().findall('.//body//p')
        locators=[]
        for locator in p['locators']:
            n=int(locator['locator'].split('[')[1].split(']')[0]);text=' '.join(''.join(xml[path][n-1].itertext()).split());locators.append(hashlib.sha256(text.encode()).hexdigest()==locator['text_sha256'])
        provenance.append(dict(instance_id=r['instance_id'],passed=valid and bool(locators) and all(locators),source_quality=p['source_quality'],human_reviewed=False))
    save_at(OUT,'source_provenance_validation.json',dict(passed=all(r['passed'] for r in provenance),checks=provenance,scope='raw bytes and cited source paragraphs; agent identity annotation, not independent chemical validation'))
    checks['source_provenance']=all(r['passed'] for r in provenance)
    keys=[template_key(t) for t in templates];checks['canonical_template_dedup']=len(set(keys))==len(keys)
    save_at(OUT,'canonical_template_audit.json',dict(total=len(keys),distinct=len(set(keys)),key_sha256=[hashlib.sha256(k.encode()).hexdigest() for k in keys],definition='canonical map-stripped reaction graphs plus actual scope/necessary donor context; IDs/atom map renumbering omitted'))
    scopes=[t for t in templates if t['template_role']=='scope_template'];scope_support={t['template_id']:len({registry.instances[i]['acceptor'] for i in t['support_instances']}) for t in scopes}
    checks['scope_breadth']=len(scopes)>=4 and all(n>=2 for n in scope_support.values()) and len({t['sugar_type'] for t in scopes})>=2
    original_scopes={t['template_id']:t for t in rows(ORIGINAL/'templates.jsonl') if t['template_role']=='scope_template'};checks['scope_not_fitted']=all(t==original_scopes[t['template_id']] for t in scopes)
    checks['template_support_boundaries']=len(validation)==len(templates) and all(v['passed'] and all(x['passed'] for x in v['checks']) and sum(x['kind'] in ['wrong_context_or_donor','wrong_anomeric_stereo','outside_flavonoid_core','outside_declared_OH_OMe_decorations'] for x in v['checks'])>=2 for v in validation)
    checks['build_actual_action_replay']=json.loads((OUT/'build_action_validation.json').read_text())['passed']
    v1=load_v1();v1checks=[]
    for r in rows(ROOT/'outputs/task016/v1/instances.jsonl'):
        old=next(t for t in v1.templates if r['instance_id'] in t['support_instances']);new=next(q for q in build if q['instance_id']==r['instance_id']);wanted=canonical_side(new['reference_precursors'])
        v1checks.append(dict(instance_id=r['instance_id'],v1_original=canonical_side(r['reference_precursors']) in [o['precursors'] for o in apply_v1(old,r['target'])],v2_normalized=any(wanted in [o['precursors'] for o in apply_template(t,new['target'])] for t in templates if r['instance_id'] in t['support_instances']),original_target=r['target'],normalized_target=new['target'],new_covalent_coverage=False))
    save_at(OUT,'v1_regression.json',dict(passed=all(r['v1_original'] and r['v2_normalized'] for r in v1checks),checks=v1checks,actual_mcts_runs=0));checks['v1_regression']=all(r['v1_original'] and r['v2_normalized'] for r in v1checks)
    checks['default_off']=json.loads((OUT/'default_off_regression.json').read_text())['equal'] and json.loads((OUT/'retained_A_B_control_proof.json').read_text())['passed']
    checks['raw_replay_inherited']=json.loads((ORIGINAL/'replay.json').read_text())['passed'];checks['qualified_byte_replay']=json.loads((OUT/'replay.json').read_text())['passed']
    checks['package_installed']=json.loads((ROOT/'outputs/validation/task016-p1-package-qualified/report.json').read_text())['passed']
    checks['config_copies']=sha(ROOT/'configs/glycoside-library-v2.json')==sha(ROOT/'flavoretro/assets/configs/glycoside-library-v2.json')
    new=[r for r in groups if not r['inherited']];checks['new_reactions']=len(new)>=40;checks['new_templates']=len(templates)-4>=12
    checks['coverage_breadth']=counts['new_acceptors']>=10 and len(counts['new_sugars'])>=3 and counts['new_closed_source_groups']>=6 and counts['new_categories']['C_formation']>=2 and counts['new_categories']['sugar_sugar_formation']>=2
    checks['holdout_denominator']=len({r['target'] for r in hold})>=12 and len({r['covalent_signature'] for r in hold})>=12
    observations=rows(OUT/'mcts_observations.jsonl');pairs=rows(OUT/'paired_results.jsonl');gaps=rows(OUT/'gap_register.jsonl');ledger=rows(ORIGINAL/'run_ledger.jsonl');started=[r for r in ledger if r['phase']=='started'];finished=[r for r in ledger if r['phase']=='finished'];ids={r['run_id'] for r in started}
    mainfiles=[ORIGINAL/'mcts_observations.jsonl',ORIGINAL/'mcts_observations.r2.jsonl',ORIGINAL/'mcts_C_revalidation.r3.jsonl',OUT/'mcts_C_revalidation.jsonl'];mainids={r['run_id'] for path in mainfiles for r in rows(path)};engineering=ids-mainids
    revision=json.loads((OUT/'budget_revision.json').read_text());limits=revision['approved_limits'];checks['budget_accounting']=len(ids)==len(started)==len(finished) and {r['run_id'] for r in finished}==ids and len(ids)<=limits['service_attempts'] and len(mainids)<=limits['main_attempts'] and len(engineering)<=limits['engineering_attempts']
    checks['approved_revision_binding']=all(r['budget_binding']==sha(ORIGINAL/'execution-baseline.json') for r in ledger) and all(r['ceiling']==180 for r in started[:175]) and all(r['ceiling']==240 and r['budget_revision_sha256']==sha(OUT/'budget_revision.json') for r in started[175:])
    checks['wall_limit']=all(r['wall_seconds']<=60 for r in finished)
    checks['matrix_complete']=len(observations)==108 and len({(r['target'],r['seed'],r['arm']) for r in observations})==108 and all(r['status']=='ok' for r in observations)
    checks['whole_C_fresh']=len(rows(OUT/'mcts_C_revalidation.jsonl'))==36 and all(r['origin']=='fresh_qualified_r4_entire_C_panel' for r in observations if r['arm']=='C')
    results={r['run_id']:json.loads((ROOT/r['result_path']).read_text()) for r in observations}
    checks['matrix_actual_mcts']=all(r['execution_source']=='live_aizynthfinder_mcts' for r in results.values());checks['result_hashes']=all(sha(ROOT/r['result_path'])==r['result_sha256'] for r in observations)
    checks['same_requests']=all(results[r['run_id']]['request']==request(r['target'],r['arm'],r['seed']).payload() for r in observations)
    assets=next(iter(results.values()))['assets'];checks['review_models_stock']=all(r['review_binding']==c['review_binding'] and r['assets']==assets for r in results.values())
    checks['node_budget']=all(p['node_count']<=120 and p['budget']=={k:v for k,v in c['budget'].items() if k not in ['mode','engine','top_k']} and p['wall_seconds']<=60 for r in results.values() for p in r['phases'])
    displaced=json.loads((OUT/'candidate_displacement.json').read_text());bytarget={r['target']:r for r in displaced['targets']};protection=[];domain=[]
    for o in observations:
        result=results[o['run_id']]
        if o['arm']!='C':continue
        required=set(bytarget[o['target']]['required_generic_signatures']);available=signatures(result,'after_truncation');protection.append(dict(run_id=o['run_id'],seed=o['seed'],target=o['target'],missing=sorted(required-available),passed=required<=available))
        for e in result.get('action_trace',[]):
            if e['stage']=='mcts_action_created' and e.get('policy')=='glycoside':domain.append(dict(run_id=o['run_id'],seed=o['seed'],**e))
    checks['generic_protection']=displaced['protection_violations']==0 and all(r['passed'] for r in protection)
    save_at(OUT,'mcts_generic_protection.json',dict(passed=checks['generic_protection'],checks=protection))
    def evidence_valid(e):
        evidence=e['metadata']['task016_evidence'];support=evidence['source_instance_ids']
        normalized_sig=reaction_signature(e['precursor_smiles'],[normalize_species(e['target'])['normalized']])
        exact=any(registry.instances[i]['reference_signature']==normalized_sig for i in support)
        return (evidence['template_source_support'] and all(i in registry.instances for i in support) and evidence['exact_seed_instance_match']==exact and not evidence['prediction_conditions_verified'] and evidence['yield_value'] is None and not evidence['actionable'] and not evidence['evidence_closed'] and not evidence['human_reviewed'] and not evidence['independent_chemical_validation'] and not evidence['original_conditions_copied'])
    checks['evidence_axes']=bool(domain) and all(evidence_valid(e) for e in domain);save_at(OUT,'transfer_validation.jsonl',domain,True)
    G=sum(r['gain'] for r in gaps);N_gap=sum(r['known_gap'] for r in gaps);gained={r['target'] for r in gaps if r['gain']};triples={t for t in c['primary_targets'] if all(p['gain'] for p in pairs if p['target']==t)}
    checks['candidate_gain']=G>=6 and len(gained)>=6 and N_gap>0 and G/N_gap>=.5 and sum(r['matches']['C'] for r in gaps)>sum(r['matches']['A'] for r in gaps) and not any(r['loss_A'] or r['loss_B'] for r in gaps)
    checks['mcts_gain']=len(pairs)==36 and len(triples)>=6 and not any(p['loss_A'] or p['loss_B'] for p in pairs)
    attempts=rows(ORIGINAL/'acquisition_attempts.jsonl');actualfiles={str(p.relative_to(ROOT)) for p in RAW.rglob('*') if p.is_file()};checks['raw_hashes']=all((ROOT/r['path']).is_file() and sha(ROOT/r['path'])==r['sha256'] and (ROOT/r['path']).stat().st_size==r['bytes'] for r in attempts)
    checks['raw_conservation']=actualfiles=={r['path'] for r in attempts};acq=json.loads((ORIGINAL/'source_yield_inventory.json').read_text());query=json.loads((ORIGINAL/'source_accounting_addendum.json').read_text());source_bytes=sum((ROOT/p).stat().st_size for p in actualfiles)
    checks['acquisition_budget']=len(attempts)<=4000 and source_bytes<=5*1024**3 and acq['article_ids']<=200 and acq['supplementary_requests']<=400 and acq['metadata_records']<=10000
    checks['source_record_conservation']=acq['record_disposition_difference']==0 and query['query_rows_difference']==0 and checks['annotation_conservation']
    regression=json.loads((OUT/'full_regression.json').read_text());assetfree=json.loads((OUT/'asset_free_regression.json').read_text());checks['full_regression']=regression['returncode']==0 and regression['total_tests']>=118 and regression['skipped']==0;checks['asset_free']=assetfree['returncode']==0 and assetfree['skipped']==6
    tracked=subprocess.run(['git','ls-files','--','data/raw/task016-p1','outputs/task016-p1','outputs/validation/task016-p1-package-qualified'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip();checks['local_data_not_in_git']=not tracked
    costs={}
    for arm in ['A','B','C']:
        rr=[r for r in observations if r['arm']==arm];costs[arm]=dict(mean_wall_seconds=statistics.mean(r['wall_seconds'] for r in rr),median_wall_seconds=statistics.median(r['wall_seconds'] for r in rr),mean_nodes=statistics.mean(sum(p['node_count'] for p in results[r['run_id']]['phases']) for r in rr),mean_template_attempts=statistics.mean(sum(p.get('domain_profiling',{}).get('template_attempts',0) for p in results[r['run_id']]['phases']) for r in rr))
    mocks=[r for r in finished if r['status']=='error' and r['run_id'] in engineering and 'regression' in r['purpose'] and r['manifest'].startswith('/tmp/')]
    metric=dict(schema_version=2,engineering_status='passed' if all(checks[k] for k in ['full_regression','asset_free','package_installed','default_off','v1_regression','protected_inputs','budget_accounting']) else 'partial',library_coverage_status='passed' if all(checks[k] for k in ['new_reactions','new_templates','coverage_breadth','scope_breadth','candidate_gain','mcts_gain','source_provenance']) else 'partial',overall_status='Completed' if all(checks.values()) else 'Partial',library=counts,templates=dict(total=len(templates),exact=len(templates)-len(scopes),scope=len(scopes),new_exact=len(templates)-len(scopes)-4,new_scope=len(scopes),new_total=len(templates)-4,support_replays=sum(x['kind']=='support_replay' for v in validation for x in v['checks']),boundary_checks=sum(x['kind'] in ['wrong_context_or_donor','wrong_anomeric_stereo','outside_flavonoid_core','outside_declared_OH_OMe_decorations'] for v in validation for x in v['checks']),scope_acceptors=scope_support),candidate=dict(N=len(gaps),N_gap=N_gap,gain_reactions=G,gain_targets=len(gained),recovery_rate=G/N_gap if N_gap else None,matches={arm:sum(r['matches'][arm] for r in gaps) for arm in ['A','B','C']},net_percentage_points=100*(sum(r['matches']['C'] for r in gaps)-sum(r['matches']['A'] for r in gaps))/len(gaps),loss_A=sum(r['loss_A'] for r in gaps),loss_B=sum(r['loss_B'] for r in gaps)),actual_mcts=dict(matrix_cells=len(observations),inherited_same_task_A_B=72,fresh_qualified_C=36,paired_cells=len(pairs),all_three_seed_gain_targets=len(triples),gain_targets=sorted(triples),gain_pairs=sum(p['gain'] for p in pairs),loss_A=sum(p['loss_A'] for p in pairs),loss_B=sum(p['loss_B'] for p in pairs),errors=sum(r['status']!='ok' for r in observations),by_seed={str(s):sum(p['gain'] for p in pairs if p['seed']==s) for s in c['seeds']}),run_budget=dict(attempts=len(ids),ceiling=240,original_ceiling=180,approved_revision_sha256=sha(OUT/'budget_revision.json'),finished=len(finished),main_attempts=len(mainids),main_ceiling=216,engineering_attempts=len(engineering),engineering_ceiling=24,max_wall_seconds=max(r['wall_seconds'] for r in finished),status_counts=dict(Counter(r['status'] for r in finished)),synthetic_error_fixtures=len(mocks),actual_service_attempts=len(ids)-len(mocks),old_TASK016_reserved_attempts=33,old_TASK016_actual_attempts=31,cross_task_reserved_attempts=len(ids)+33,cross_task_actual_attempts=len(ids)-len(mocks)+31,history=dict(r1_main=25,r2_main=108,r3_fresh_C=24,r4_fresh_C=36)),costs=costs,protection_violations=sum(bool(r['missing']) for r in protection),generic_other_displaced_actions=sum(len(r['other_displaced']) for r in displaced['targets']),gained_source_groups=len({r['source_group'] for r in hold if r['target'] in gained}),gained_publications=sorted({r['provenance']['pmcid'] for r in hold if r['target'] in gained}),heldout_C_reactions=sum(r['category']=='C_formation' for r in hold),human_reviewed=False,blind=False,training_overlap='unknown',independent_chemical_validation=False,prediction_conditions_verified=False,evidence_closed=0,release_ready=False,scope='source-closed development candidate/action coverage; all gains in one UGT71AP2 paper; no whole-space/chemistry/production claim')
    save_at(OUT,'metrics.json',metric)
    save_at(OUT,'source_accounting.json',dict(request_attempts=len(attempts),raw_bytes=source_bytes,article_ids=acq['article_ids'],available_articles=acq['available_articles'],metadata_records=acq['metadata_records'],query_record_dispositions=len(rows(ORIGINAL/'source_query_record_dispositions.jsonl')),assay_annotations=93,admitted=81,retained_unresolved=12,difference=0,upstream_inventory_sha256=sha(ORIGINAL/'source_yield_inventory.json'),upstream_queries_sha256=sha(ORIGINAL/'source_accounting_addendum.json'),claim='acquired records preserved; pagination gaps and failed/unknown source responses inherited; dataset reaction knowledge not assays'))
    audit=dict(passed=all(checks.values()),checks=checks,protected_files=len(baseline['protected_sha256']),source_attempts=len(attempts),source_bytes=source_bytes,regression=regression,assetfree=assetfree,overall_status=metric['overall_status'],scientific_limitations=['all seven gained targets from one source publication','no heldout C formation test','four sugar-sugar and one double-glycosylation heldout targets unrecovered','development exposed / machine labels / training overlap unknown','novel activity, conditions, yield and procurement unverified; evidence_closed0'],budget_revision_disclosed=True)
    save_at(OUT,'audit.json',audit);print('checks',sum(checks.values()),'/',len(checks),'failed',[k for k,v in checks.items() if not v]);print(json.dumps(metric['run_budget'],indent=2));print('gain',metric['candidate'],metric['actual_mcts']['all_three_seed_gain_targets']);assert audit['passed'],'qualified acceptance gaps retained'

def registry_manifest():return json.loads((OUT/'template_source_manifest.json').read_text())
if __name__=='__main__':verify()
