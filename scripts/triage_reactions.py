"""Audited offline TASK-014 triage; never launches or modifies MCTS."""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.operate import write
from flavoretro.triage import build, dumps
from flavoretro.workspace import configure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rules")
    args = parser.parse_args()
    configure(str(ROOT))
    folder = Path(args.output).resolve()
    if not folder.is_relative_to(ROOT / "outputs/triage"):
        raise ValueError("output must be a new directory below outputs/triage")
    summary = build(folder, writer=lambda path, body: write("TASK-014", str(path.relative_to(ROOT)), body), rules_path=args.rules)
    print(dumps(summary))


if __name__ == "__main__":
    main()
