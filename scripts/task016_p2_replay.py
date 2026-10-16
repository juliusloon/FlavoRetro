"""Rebuild templates from frozen qualified source inputs, compare bytes without config changes."""
import sys,json,shutil,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
from flavoretro.resources import sha
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'outputs/task016-p2/v2';dest=ROOT/'outputs/task016-p2/replay-v2';assert not dest.exists();dest.mkdir()
for n in ['runtime_instances.jsonl','development_split_manifest.json']:shutil.copy2(src/n,dest/n)
av=[sys.executable,'-B','scripts/task016_p2_build.py','--output-dir',str(dest.relative_to(ROOT)),'--no-config']
event('TASK-016-P2','template_rebuild_command',argv=av,frozen_inputs={n:sha(src/n) for n in ['runtime_instances.jsonl','development_split_manifest.json']},configuration_not_mutated=True)
r=subprocess.run(av,cwd=ROOT,text=True,capture_output=True);write('TASK-016-P2','outputs/task016-p2/v2/replay.log',r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
files=['templates.jsonl','templates.provisional.jsonl','template_validation.jsonl','applicability_contract.json','representation_rules.json','fusion_contract.json','review_binding.json','template_source_manifest.json']
checks=[dict(path=n,original_sha256=sha(src/n),rebuild_sha256=sha(dest/n),byte_identical=(src/n).read_bytes()==(dest/n).read_bytes()) for n in files]
report=dict(passed=all(c['byte_identical'] for c in checks),rebuilt_files=len(checks),checks=checks,method='rerun structural template extraction, source support/boundary validation, deterministic fusion and SHA manifest from frozen qualified runtime; no MCTS; source admission not independently revalidated',actual_search_attempts=0)
write('TASK-016-P2','outputs/task016-p2/v2/replay.json',json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n');print(json.dumps(report));assert report['passed']
