"""Append-only operation journal. All project edits and commands pass this entry."""

import hashlib, json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def event(task, action, **details):
    with (ROOT / "operations/events.jsonl").open("a") as f:
        f.write(
            json.dumps(
                dict(
                    time=datetime.now(timezone.utc).isoformat(),
                    task=task,
                    action=action,
                    **details,
                ),
                ensure_ascii=False,
            )
            + "\n"
        )


def write(task, path, content):
    p = ROOT / path
    if not p.resolve().is_relative_to(ROOT):
        raise ValueError("write outside project")
    old = digest(p) if p.exists() else None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    event(task, "write", path=path, before=old, after=digest(p))


def run(task, cmd):
    event(task, "command_start", argv=cmd, cwd=str(ROOT))
    x = subprocess.run(
        cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    n = len(list((ROOT / "operations").glob("command-*.log"))) + 1
    log = f"operations/command-{n:04d}.log"
    write(task, log, x.stdout)
    event(task, "command_end", argv=cmd, returncode=x.returncode, log=log)
    print(x.stdout)
    return x.returncode


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[2] == "--write" and sys.argv[4] == "--from":
        write(sys.argv[1], sys.argv[3], Path(sys.argv[5]).read_text(encoding="utf-8"))
        sys.exit(0)
    sys.exit(run(sys.argv[1], sys.argv[2:]))
