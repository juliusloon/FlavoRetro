"""Rebuild from frozen raw inputs in memory; never replace bound v1 files."""
import hashlib, json, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.operate import write
from flavoretro.workspace import root

builder = root() / "scripts/task016_build.py"
source = builder.read_text()
guard = "assert not (out/'development_contract.json').exists(), 'immutable panel already frozen'"
assert source.count(guard) == 1
# Only the creation guard is removed. Every builder write is intercepted below;
# normalization, source reads, mapping, context and validation remain unchanged.
source = source.replace(guard, "assert (out/'development_contract.json').exists(), 'frozen panel required'")
captured = {}
def capture(task, path, content):
    assert task == "TASK-016" and path not in captured
    captured[path] = content.encode()
with patch("scripts.operate.write", capture):
    exec(compile(source, str(builder), "exec"), {"__file__": str(builder), "__name__": "__task016_replay__"})
checks = {path: {"equal": payload == (root()/path).read_bytes(),
                 "replayed_sha256": hashlib.sha256(payload).hexdigest(),
                 "original_sha256": hashlib.sha256((root()/path).read_bytes()).hexdigest()}
          for path, payload in captured.items()}
required = {"instances.jsonl", "templates.jsonl", "reference_precursors.jsonl", "template_validation.jsonl"}
assert required <= {Path(p).name for p in checks}
report = dict(passed=all(r["equal"] for r in checks.values()), files=len(checks), checks=checks,
              scope="same frozen raw snapshot, same runtime; byte-identical core rebuild, no network or MCTS; bound v1 files not overwritten")
write("TASK-016", "outputs/task016/v1/replay.json", json.dumps(report, indent=2)+"\n")
print(json.dumps(dict(passed=report["passed"], files=report["files"])))
assert report["passed"]
