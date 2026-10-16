"""Governed, deterministic helpers for the independently approved P6 contract."""
import hashlib
import json
from pathlib import Path
from scripts.operate import write, event
ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P6"
OUT = ROOT / "outputs/task016-p6/v1"
CONTRACT = "docs/tasks/TASK-016-P6-c-scope-runtime-transfer-closure.md"
def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def content_sha(value):
    return hashlib.sha256(value.encode()).hexdigest()
def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)), json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def save_rows(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)), "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))
def load(name):
    return json.loads((OUT / name).read_text())
