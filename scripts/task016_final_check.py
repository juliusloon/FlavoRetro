"""Validate final governance against frozen execution inputs; no network/MCTS."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write, event
root=Path(__file__).resolve().parents[1]; folder=root/'outputs/task016/v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((root/n).read_text())
docs=['docs/tasks/TASK-016-open-glycoside-expansion.md','docs/reports/REPORT-016-open-glycoside-expansion.md','STATE.md','ARCHITECTURE.md','docs/tasks/README.md','docs/reports/README.md','docs/README.md','docs/WORKBENCH_ROADMAP.md','docs/PAPER_ROADMAP.md']
checks={}; errors=[]
for name in docs:
    p=root/name
    for target in re.findall(r'\[[^]\n]*\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith('#'):continue
        target=target.split('#',1)[0]
        if not target:continue
        q=Path(target) if target.startswith('/') else p.parent/target
        if not q.exists():errors.append(dict(document=name,target=target))
checks['markdown_links']=not errors
baseline=read('outputs/task016/v1/execution-baseline.json')
checks['execution_dependencies_unchanged']=all(sha(root/p)==h for p,h in baseline['protected_sha256'].items())
prior=read('operations/task016-v02-revision-baseline.json')
allowed={'flavoretro/worker.py','flavoretro/search.py','flavoretro/service.py','flavoretro/contracts.py','flavoretro/cli.py','flavoretro/workspace.py','docs/reports/README.md','docs/tasks/README.md'}
protected={p:h for p,h in prior['protected'].items() if p not in allowed}
checks['prior_protected_unchanged']=all(sha(root/p)==h for p,h in protected.items())
binding=read('outputs/task016/v1/development_runtime_binding.json')
checks['frozen_runtime_code_unchanged']=all(sha(root/p)==h for p,h in binding['code_sha256'].items())
checks['frozen_models_unchanged']=all(sha(root/p)==h for p,h in binding['model_sha256'].items())
source=read('outputs/task016/v1/source_manifest.json')
checks['raw_immutable']=all(sha(root/r['path'])==r['sha256'] and (root/r['path']).stat().st_mode & 0o222==0 for r in source['files'])
checks['bound_payloads_unchanged']=all(sha(folder/n)==h for n,h in read('outputs/task016/v1/template_source_manifest.json')['files_sha256'].items())
checks['default_off']=read('configs/glycoside-expansion.json')['default_enabled'] is False and read('outputs/task016/v1/default-off-regression.json')['equal']
checks['config_copies_equal']=(root/'configs/glycoside-expansion.json').read_bytes()==(root/'flavoretro/assets/configs/glycoside-expansion.json').read_bytes()
checks['replay_passed']=read('outputs/task016/v1/replay.json')['passed']
checks['source_action_budget_audit_passed']=read('outputs/task016/v1/audit.json')['passed']
checks['task_acceptance_recorded']='- [ ] ' not in (root/docs[0]).read_text() and '- 状态：Completed' in (root/docs[0]).read_text()
report=(root/docs[1]).read_text()
checks['report_payload_hashes']=all(sha(folder/n) in report for n in ['execution-baseline.json','source_manifest.json','instances.jsonl','development_contract.json','development_runtime_binding.json','reference_precursors.jsonl','baseline_observations.jsonl','gap_register.jsonl','templates.jsonl','template_validation.jsonl','template_source_manifest.json','mcts_execution_contract.json','paired_results.jsonl','metrics.json','audit.json','replay.json','candidate_accounting.json'])
diff=subprocess.run(['git','diff','--check'],cwd=root,text=True,capture_output=True)
checks['git_diff_check']=diff.returncode==0
tracked=subprocess.run(['git','ls-files','--','data/raw/task016','outputs/task016','outputs/validation/task016-package'],cwd=root,text=True,capture_output=True,check=True)
checks['new_raw_outputs_untracked']=not tracked.stdout.strip()
paths=[r['path'] for r in source['files']]+[str(p.relative_to(root)) for p in folder.rglob('*') if p.is_file()]
ignored=subprocess.run(['git','check-ignore','--stdin'],input='\n'.join(paths)+'\n',cwd=root,text=True,capture_output=True)
checks['new_raw_outputs_ignored']=set(paths)<=set(ignored.stdout.splitlines())
result=dict(passed=all(checks.values()),checks=checks,link_errors=errors,diff_output=diff.stdout+diff.stderr,protected_files=len(protected),execution_protected_files=len(baseline['protected_sha256']),scope='final documents and frozen inputs; no new experiment or approval',approval_type='agent_delegated')
write('TASK-016','outputs/task016/v1/final-governance-validation.json',json.dumps(result,indent=2)+'\n')
assert result['passed'],result
# The manifest covers the frozen source dependencies, every delivered local payload,
# current runtime/configuration, new scripts/tests and final governance documents.
files=set(paths)|set(docs)|set(binding['code_sha256'])|set(binding['model_sha256'])
files|={str(p.relative_to(root)) for p in (root/'scripts').glob('task016_*.py')}
files|={'tests/test_task016_expansion.py','outputs/validation/task016-package/report.json','outputs/task016/v1/final-governance-validation.json'}
files.discard('outputs/task016/v1/delivery_manifest.json')
manifest=dict(schema_version=1,task='TASK-016',version='task016-delivery-v1',files_sha256={p:sha(root/p) for p in sorted(files)},source_template_manifest_sha256=sha(folder/'template_source_manifest.json'),claim='engineering completion and exact-source candidate coverage; not chemical or release certification')
write('TASK-016','outputs/task016/v1/delivery_manifest.json',json.dumps(manifest,indent=2)+'\n')
event('TASK-016','final_delivery',approval_type='agent_delegated',status='Completed',manifest_sha256=sha(folder/'delivery_manifest.json'),files=len(manifest['files_sha256']))
print(json.dumps(dict(passed=result['passed'],checks=len(checks),delivery_files=len(manifest['files_sha256'])),indent=2))
