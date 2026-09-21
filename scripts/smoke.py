import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from flavoretro.contracts import SearchRequest
from flavoretro.service import search
from flavoretro.resources import ROOT, dumps

results = []
for mode, candidate in [("quick", False), ("quick", False), ("balanced", True)]:
    r = search(
        SearchRequest(
            smiles="CCOc1ccccc1",
            mode=mode,
            seconds=2.0,
            iterations=5,
            candidate_stock=candidate,
        )
    )
    results.append(r)
    assert r["status"] == "ok", r
    assert all(x["engine_class"] == "flavoretro.search.SearchTree" for x in r["phases"])
    assert all(not x["actionable"] and not x["evidence_closed"] for x in r["routes"])
assert len({r["run_id"] for r in results}) == 3
assert len(results[-1]["phases"]) == 2
out = ROOT / "outputs/validation"
out.mkdir(parents=True, exist_ok=True)
(out / "live-smoke.json").write_text(
    dumps(
        [
            {
                "run_id": r["run_id"],
                "routes": len(r["routes"]),
                "phases": len(r["phases"]),
                "nodes": [p["node_count"] for p in r["phases"]],
            }
            for r in results
        ]
    )
)
print((out / "live-smoke.json").read_text())
