"""Bind the Partial delivery and verify current governance links without launching searches."""
import sys,json,re,ast,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
from flavoretro.resources import sha
ROOT=Path(__file__).resolve().parents[1];Q=ROOT/'outputs/task016-p2/v2';T='TASK-016-P2'
docs=['STATE.md','ARCHITECTURE.md','docs/README.md','docs/tasks/README.md','docs/reports/README.md','docs/PAPER_ROADMAP.md','docs/WORKBENCH_ROADMAP.md','docs/tasks/TASK-016-P2-c-sugar-transfer-validation.md','docs/reports/REPORT-016-P2-c-sugar-transfer-validation.md']
checks=[];broken=[]
for f in docs:
 p=ROOT/f;text=p.read_text()
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
  if target.startswith(('http:','https:','codex:','app:','#')):continue
  path=target.split('#',1)[0].strip('<>')
  if path and not (p.parent/path).exists():broken.append(dict(document=f,target=target))
checks.append(dict(name='documentation_local_links',passed=not broken,broken=broken))
for f in docs:
 text=(ROOT/f).read_text();assert '016-P2' in text and 'Partial' in text
checks.append(dict(name='current_status_consistent',passed=True))
python_files=[p for p in (ROOT/'scripts').glob('task016_p2_*.py')]+[ROOT/'flavoretro/glycoside_library_v3.py',ROOT/'tests/test_task016_p2_library.py']
for p in python_files:ast.parse(p.read_text(),filename=str(p))
checks.append(dict(name='new_source_syntax',passed=True,files=len(python_files)))
av=['git','diff','--check'];r=subprocess.run(av,cwd=ROOT,text=True,capture_output=True);event(T,'final_git_diff_check',argv=av,returncode=r.returncode,output=r.stdout+r.stderr);checks.append(dict(name='git_diff_check',passed=r.returncode==0,output=r.stdout+r.stderr))
audit=json.loads((Q/'audit.json').read_text());metric=json.loads((Q/'metrics_by_family.json').read_text());checks.append(dict(name='engineering_and_partial_gates',passed=audit['engineering_passed'] and not audit['scientific_acceptance_passed'] and metric['overall_status']=='Partial' and metric['fresh_ABD_matrix_cells']==0))
validation=dict(passed=all(c['passed'] for c in checks),checks=checks,actual_search_attempts=0)
write(T,'outputs/validation/task016-p2-final.json',json.dumps(validation,ensure_ascii=False,sort_keys=True,indent=2)+'\n');assert validation['passed'],validation
baseline=json.loads((ROOT/'outputs/task016-p2/v1/execution-baseline.json').read_text());code=set(baseline['mutable_code_originals'])|{'flavoretro/glycoside_library_v3.py','configs/glycoside-library-v3.json','flavoretro/assets/configs/glycoside-library-v3.json','tests/test_task016_p2_library.py'}
code.update(str(p.relative_to(ROOT)) for p in python_files)
outputs={str(p.relative_to(ROOT)) for p in Q.iterdir() if p.is_file() and p.name!='delivery_manifest.json'}
inputs={'outputs/task016-p2/v1/execution-baseline.json','outputs/task016-p2/v1/acquisition_attempts.jsonl','outputs/task016-p2/v1/acquisition_reservations.jsonl','outputs/task016-p2/v1/run_ledger.jsonl','outputs/task016-p2/v1/external_discovery_receipts.jsonl','outputs/validation/task016-p2-final.json'}
files=set(docs)|code|outputs|inputs
manifest=dict(task=T,overall_status='Partial',engineering_status='Completed',C_transfer_status='Partial',sugar_sugar_transfer_status='Partial',files_sha256={p:sha(ROOT/p) for p in sorted(files)},source_raw_receipts_sha256=sha(ROOT/'outputs/task016-p2/v1/acquisition_attempts.jsonl'),source_reused_and_all_raw_file_dispositions_sha256=sha(Q/'file_dispositions.jsonl'),actual_run_results={o['run_id']:dict(path=o['result_path'],sha256=o['result_sha256']) for o in [json.loads(s) for s in (Q/'mcts_observations.jsonl').read_text().splitlines()]},old_template_manifest_sha256='a98651a5b02873d3df36f46c8a4773867d354859039a5cc84b6f1669f685a2b2',current_template_manifest_sha256=sha(Q/'template_source_manifest.json'),audit_sha256=sha(Q/'audit.json'),scientific_acceptance_passed=False,source_files_not_redistributed=True,git_commit_created=False,formal_run_ready=False,release_ready=False)
write(T,'outputs/task016-p2/v2/delivery_manifest.json',json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
assert all(sha(ROOT/p)==h for p,h in manifest['files_sha256'].items())
event(T,'partial_delivery_finalized',manifest_sha256=sha(Q/'delivery_manifest.json'),files=len(files),new_scope_templates=3,old_SS_repaired=4,fresh_transfer_executed=False,conservative_service_attempts=61,actual_service_attempts=55,source_candidates_remain=True)
print(json.dumps(dict(passed=True,delivery_files=len(files),delivery_manifest_sha256=sha(Q/'delivery_manifest.json'),overall_status='Partial',scientific_acceptance_passed=False),ensure_ascii=False))
