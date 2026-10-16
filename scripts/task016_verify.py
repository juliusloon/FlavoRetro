"""Independent conservation/provenance/budget audit; retain raw failures and exclusions."""
import csv,hashlib,json,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.resources import sha
from flavoretro.glycoside_expansion import load_registry,apply_template
from flavoretro.reviewed_resources import load_review,canonical_side,reaction_signature
from flavoretro.workspace import root,active_data
from scripts.operate import write
from scripts.task016_evaluate import read_jsonl,metrics

folder=root()/'outputs/task016/v1';registry=load_registry();baseline=json.loads((folder/'execution-baseline.json').read_text());contract=json.loads((folder/'development_contract.json').read_text());source=json.loads((folder/'source_manifest.json').read_text());checks={}
checks['execution_dependencies_unchanged']=all(sha(root()/p)==h for p,h in baseline['protected_sha256'].items())
prior=json.loads((root()/'operations/task016-v02-revision-baseline.json').read_text())
allowed={'flavoretro/worker.py','flavoretro/search.py','flavoretro/service.py','flavoretro/contracts.py','flavoretro/cli.py','flavoretro/workspace.py','docs/reports/README.md','docs/tasks/README.md'}
protected={p:h for p,h in prior['protected'].items() if p not in allowed}
checks['prior_protected_unchanged']=all(sha(root()/p)==h for p,h in protected.items())
checks['raw_snapshot_unchanged']=all(sha(root()/r['path'])==r['sha256'] for r in source['files'])
checks['ord_reuse_hash_verified']=all(sha(root()/r['path'])==r['sha256'] and sha(root()/r['path'])==json.loads((root()/r['path']).parent.joinpath('download.json').read_text())['sha256'] for r in source['ord_reuse']['files'])
checks['raw_budget']=sum(r['bytes'] for r in source['files'])<5*1024**3
knowledge=read_jsonl(folder/'knowledge_records.jsonl');dispositions=read_jsonl(folder/'record_dispositions.jsonl');instances=read_jsonl(folder/'instances.jsonl');validation=read_jsonl(folder/'template_validation.jsonl')
checks['scoped_record_conservation']=len(dispositions)==65+40+10 and len({(r['provider'],r['record_id']) for r in dispositions})==len(dispositions)
checks['source_reconstruction']=all(v['support_passed']==v['support_denominator'] and v['boundary_violations']==0 for v in validation)
checks['all_templates_traceable']=all(t['support_instances'] and all(i in registry.instances for i in t['support_instances']) for t in registry.templates)
checks['source_provenance_complete']=all(all(i['provenance'].get(k) for k in ['doi','pmcid','raw_path','raw_sha256','locator','license','rhea_record_id','rhea_smiles_sha256']) for i in instances)
checks['reference_denominator']=len({i['reference_signature'] for i in instances})==contract['N']==4
checks['review_and_stock_fixed']=load_review().binding==contract['review_binding'] and len(load_review().keys)==17 and active_data()[2]['version']=='v3'
checks['packaged_configuration_equal']=(root()/'configs/glycoside-expansion.json').read_bytes()==(root()/'flavoretro/assets/configs/glycoside-expansion.json').read_bytes()
checks['default_off_regression']=json.loads((folder/'default-off-regression.json').read_text())['equal']
checks['installed_package']=json.loads((root()/'outputs/validation/task016-package/report.json').read_text())['installed_domain']['created_domain_actions']>=1
checks['asset_free']=json.loads((folder/'asset-free-regression-v2.json').read_text())['returncode']==0
# Every downloaded bulk row has a disposition, including rows outside the selected query.
bulk=root()/'data/raw/task016/discovery/2026-10-06/rhea_smiles';selected={r['lr_id'] for r in knowledge if r['parse_status']=='parsed'}
bulk_hash=sha(bulk)
bulk_rows=[dict(provider='Rhea-bulk-SMILES',record_id=line.split('\t',1)[0],line_number=index+1,disposition='scoped_structure_source' if line.split('\t',1)[0] in selected else 'retained_outside_frozen_query',raw_path=str(bulk.relative_to(root())),raw_sha256=bulk_hash) for index,line in enumerate(bulk.read_text().splitlines())]
write('TASK-016',str((folder/'bulk_record_dispositions.jsonl').relative_to(root())),''.join(json.dumps(r,sort_keys=True)+'\n' for r in bulk_rows))
directions=root()/'data/raw/task016/discovery/2026-10-06/rhea_dirs';directions_hash=sha(directions);maps=list(csv.DictReader(directions.open(),delimiter='\t'))
write('TASK-016',str((folder/'direction_record_dispositions.jsonl').relative_to(root())),''.join(json.dumps(dict(provider='Rhea-direction-map',record_id=r['RHEA_ID_MASTER'],record_type='direction_metadata',disposition='retained_direction_mapping',raw_path=str(directions.relative_to(root())),raw_sha256=directions_hash),sort_keys=True)+'\n' for r in maps))
checks['bulk_conservation']=len(bulk_rows)==len(bulk.read_text().splitlines()) and len({r['record_id'] for r in bulk_rows})==len(bulk_rows)
# Ancillary citation lookups and cloud metadata are retained, never extra assay support.
ancillary=[];b=root()/'data/raw/task016/discovery/2026-10-06';pubmed=json.loads((b/'pubmed').read_text())
for r in pubmed['resultList']['result']:ancillary.append(dict(provider='EuropePMC-citation-query',record_id=r['id'],record_type='citation_metadata',disposition='metadata_only',reason='citation relation alone does not establish a checked source assay',raw_path=str((b/'pubmed').relative_to(root())),raw_sha256=sha(b/'pubmed')))
for p in sorted((root()/'data/raw/task016/pmc-s3/2026-10-06/https').glob('*/metadata.attempt-1')):
    r=json.loads(p.read_text());ancillary.append(dict(provider='PMC-cloud',record_id=r['pmcid'],record_type='article_metadata',disposition='licensed_fulltext_available',license=r['license_code'],raw_path=str(p.relative_to(root())),raw_sha256=sha(p)))
ancillary.append(dict(provider='Rhea-SPARQL',record_id='RHEA:61180',record_type='knowledge_metadata',disposition='duplicate_identity_metadata_no_new_assay',raw_path=str((b/'rdf61180').relative_to(root())),raw_sha256=sha(b/'rdf61180')))
write('TASK-016',str((folder/'ancillary_record_dispositions.jsonl').relative_to(root())),''.join(json.dumps(r,sort_keys=True)+'\n' for r in ancillary))
# Actual no-product observations remain categorical absence, not a fabricated 0%.
paper=root()/'data/raw/task016/europepmc/2026-10-06/PMC5818429.xml';xml=ET.parse(paper).getroot();paragraphs=xml.findall('.//body//p');pindex=next(i for i,p in enumerate(paragraphs) if 'No flavonoid O-rutinoside' in ''.join(p.itertext()))
negative=[dict(instance_id='PMC5818429:negative:'+name,provider='EuropePMC',record_type='source_reported_negative_assay',acceptor_name=name,donor_name='UDP-rhamnose',enzyme='CsUGT76F1',raw_path=str(paper.relative_to(root())),raw_sha256=sha(paper),locator=f'body//p[{pindex+1}]',outcome='product_not_detected',yield_value=None,zero_numeric=False,structure_status='not_resolved_no_stereo_guess',positive_template_seed=False) for name in ['hesperetin','naringenin','diosmetin']]
negative.append(dict(instance_id='PMC5818429:negative:monoglycoside-panel',provider='EuropePMC',record_type='source_reported_negative_panel',acceptor_names=['hesperetin-7-O-glucoside','naringenin-7-O-glucoside','diosmetin-7-O-glucoside','quercetin-3-O-glucoside','quercetin-7-O-glucoside','kaempferol-3-O-glucoside','kaempferol-7-O-glucoside'],donor_name='UDP-rhamnose',enzyme='CsUGT76F1',outcome='rutinoside_or_neohesperidose_product_not_detected',yield_value=None,zero_numeric=False,raw_path=str(paper.relative_to(root())),raw_sha256=sha(paper),locator=f'body//p[{pindex+1}]',positive_template_seed=False))
write('TASK-016',str((folder/'negative_instances.jsonl').relative_to(root())),''.join(json.dumps(r,sort_keys=True)+'\n' for r in negative))
assays={(i['provenance']['pmcid'],i['required_context']['enzyme'],i['acceptor'],i['donor'],i['source_conditions']['locator']) for i in instances}
accounting=dict(source_query_records=len(dispositions),ancillary_metadata_records=len(ancillary),bulk_smiles_records=len(bulk_rows),direction_mapping_records=len(maps),positive_product_instances=4,assay_context_groups=len(assays),physical_replicate_count=None,independent_publications=2,exact_reference_groups=4,executable_templates=4,formation_family_count=1,formation_families=['O-glycosylation'],position_class_count=3,positions=['O-3','O-4prime','O-7'],negative_named_assays=3,negative_panels=1,negative_numeric_zeroes=0,source_manifest_counter_clarification={'specific_assays': 'original frozen counter counts 4 product-specific source instances; unique enzyme/acceptor/donor assay contexts are 3, including 1 shared luteolin assay. Neither counter is an independent replicate count.'})
write('TASK-016',str((folder/'source_accounting.json').relative_to(root())),json.dumps(accounting,indent=2)+'\n')
ledger=read_jsonl(folder/'run_ledger.jsonl');ids={r['run_id'] for r in ledger if r.get('run_id')};done=[r for r in ledger if r.get('phase')=='finished' or r.get('sequence')==1];starts={r['run_id'] for r in ledger if r.get('phase')=='started'};ends={r['run_id'] for r in done};checks['ledger_complete']=starts<=ends and len(done)==len(ids)<=120 and all(r['wall_seconds']<=60 for r in done)
observations=read_jsonl(folder/'mcts_observations.jsonl');pairs=read_jsonl(folder/'paired_results.jsonl');checks['frozen_run_universe']=len(observations)==24 and len(pairs)==12 and {(r['target'],r['seed'],r['group']) for r in observations}=={(t,s,g) for t in contract['primary_targets'] for s in [0,1,2] for g in ['A','B']}
traces=[];new_actions=[]
for r in observations:
    result=r['result'];checks['run_files_'+result['run_id']]=all(sha(folder/'paired-runs'/result['run_id']/p)==h for p,h in r['manifest']['files'].items())
    for e in result.get('action_trace',[]):
        entry=dict(run_id=result['run_id'],seed=r['seed'],group=r['group'],**e);traces.append(entry)
        if e['stage']=='mcts_action_created' and e.get('policy')=='glycoside':new_actions.append(entry)
checks['actual_node_trace']=len(new_actions)>=1 and all(e['outcome_index']==e['created_outcome_index'] and e['created_node_count']>=1 and e['metadata']['task016_evidence']['template_source_support'] and e['metadata']['task016_evidence']['exact_instance_match'] and e['metadata']['task016_evidence']['prediction_conditions_verified'] is False for e in new_actions)
checks['created_precursor_signature']=all(e['signature']==reaction_signature(e['precursor_smiles'],[e['target']]) for e in new_actions)
write('TASK-016',str((folder/'action_trace.jsonl').relative_to(root())),''.join(json.dumps(r,sort_keys=True)+'\n' for r in traces))
write('TASK-016',str((folder/'review_binding.json').relative_to(root())),json.dumps(load_review().binding,indent=2)+'\n')
old_metrics=json.loads((folder/'metrics.json').read_text());write('TASK-016',str((folder/'metrics-main-completion.json').relative_to(root())),json.dumps(old_metrics,indent=2)+'\n');final_metrics=metrics(folder,pairs)
final_metrics['run_budget']['actual_live_completed']=sum(r.get('execution_source')=='live_aizynthfinder_mcts' or r.get('sequence')==1 for r in done)
final_metrics['run_budget']['synthetic_service_error_fixtures']=sum(r['status']=='error' and r.get('purpose')=='full_local_regression' for r in done)
final_metrics['source_accounting']=accounting
write('TASK-016',str((folder/'metrics.json').relative_to(root())),json.dumps(final_metrics,indent=2)+'\n')
report=dict(passed=all(checks.values()),checks=checks,protected_files=len(protected),execution_protected_files=len(baseline['protected_sha256']),raw_files=len(source['files']),raw_bytes=sum(r['bytes'] for r in source['files']),source_accounting=accounting,new_created_action_trace_count=len(new_actions),new_action_provenance_completeness=1.0,template_support_reconstruction_rate=1.0,boundary_violations=0,run_budget=final_metrics['run_budget'],notes=['source_manifest specific_assays is a product-instance counter; clarified without rewriting frozen bindings','first empty-cwd asset-free harness failure retained; corrected harness passed','public raw data and all local payloads remain Git-ignored; no old task data written'])
write('TASK-016',str((folder/'audit.json').relative_to(root())),json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2));print('FAILED CHECKS',[k for k,v in checks.items() if not v]);assert report['passed']
