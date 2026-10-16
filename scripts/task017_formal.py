"""TASK-017 freeze/check/run/verify; no legacy comparison dispatch."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.formal_evaluation import check_bundle,freeze_bundle,run_bundle,verify_results

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action",choices=("check","freeze","run","verify"))
    parser.add_argument("--folder",type=Path,default=Path("outputs/evaluation/formal-task017-v2"))
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    try:
        action={"check":check_bundle,"freeze":freeze_bundle,
                "run":run_bundle,"verify":verify_results}[args.action]
        result=action(args.folder)
        text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
        if args.output:
            from scripts.operate import write
            write("TASK-017",str(args.output),text)
        print(text)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({"status":"blocked","error":str(exc)},ensure_ascii=False))
        return 2
    return 0
if __name__=="__main__":
    raise SystemExit(main())
