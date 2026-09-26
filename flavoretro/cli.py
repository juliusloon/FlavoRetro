import argparse, json, sys
from .contracts import SearchRequest
from .service import search


def main():
    parser = argparse.ArgumentParser(description="FlavoRetro live MCTS research CLI")
    parser.add_argument("--smiles", required=True)
    parser.add_argument("--mode", default="balanced")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--engine", default="optimized")
    parser.add_argument("--candidate-stock", action="store_true")
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--iterations", type=int)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--workspace")
    for name in ("depth", "branching", "nodes"):
        parser.add_argument("--" + name, type=int)
    args = vars(parser.parse_args())
    from .workspace import configure
    configure(args.pop("workspace"))
    try:
        result = search(
            SearchRequest(**{k: v for k, v in args.items() if v is not None})
        )
        code = 0 if result["status"] == "ok" else 1
    except ValueError as exc:
        result = {
            "status": "error",
            "error": {"code": "invalid_request", "message": str(exc)},
        }
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
