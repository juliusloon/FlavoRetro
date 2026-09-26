"""New, bounded development comparisons; never historical acceptance replay."""

import argparse, json, uuid
from datetime import datetime, timezone
from pathlib import Path
from .contracts import SearchRequest
from .service import search
from .resources import dumps, sha
from .workspace import root, active_data, config_path
from .policies import records


def preflight():
    from .workspace import AssetError
    from .database import metadata as index_metadata
    reasons = []
    engineering = {}
    try:
        _, manifest, pointer = active_data()
        engineering = {"resource_version":pointer["version"],"records":sum(manifest["counts"].values()),
            "database":index_metadata()[1],"assets_verified":True}
    except (AssetError, ValueError) as exc:
        engineering = {"assets_verified":False,"error":str(exc)}
        reasons.append(str(exc))
    release_path = root() / "metadata/release.json"
    release = json.loads(release_path.read_text()) if release_path.is_file() else {}
    required = {"primary_source_review":"approved", "current_vendor_evidence":"approved",
        "independent_chemical_labels":"available", "evaluation_protocol_review":"approved"}
    scientific = {k:{"actual":release.get(k,"unresolved"),"required":v,"pass":release.get(k)==v} for k,v in required.items()}
    for key, gate in scientific.items():
        if not gate["pass"]:
            reasons.append(key + ": " + str(gate["actual"]))
    rows = records() if engineering.get("assets_verified") else []
    projections = {kind:sum(r["production_eligible"] and r["kind"]==kind for r in rows) for kind in ("template","stock")}
    if not all(projections.values()):
        reasons.append("No independently source-reviewed production template/stock projection")
    engineering["production_projection_counts"] = projections
    return {"formal_run_ready":not reasons,"release_ready":False,"engineering":engineering,
        "scientific":scientific,"reasons":reasons,"scope":"preflight only; development comparisons are not formal blind evaluation"}


def compare(folder=None, progress=None):
    ROOT = root()
    resource_folder, resource_manifest, _ = active_data()
    rows = records()
    targets = [
        r
        for r in rows
        if r["kind"] == "molecule"
        and r["raw"]["query_name"].lower() in ("hesperidin", "hesperetin", "quercetin")
    ]
    assert len(targets) == 3
    supplied = folder is not None
    folder = Path(folder) if supplied else ROOT / "outputs/evaluation" / ("development-" + uuid.uuid4().hex)
    folder.mkdir(parents=True, exist_ok=supplied)
    if (folder / "contract.json").exists():
        raise ValueError("evaluation exists; immutable new job required")
    contract = {
        "scope": "development_engine_comparison_not_blind",
        "targets": [r["id"] for r in targets],
        "seeds": [0, 1],
        "engines": ["native", "optimized"],
        "candidate_stock": True,
        "seconds": 2.0,
        "iterations": 10,
        "depth": 4,
        "same_node_ceiling": False,
        "resource_sha256": resource_manifest["records_sha256"],
        "config_sha256": sha(config_path("search.json")),
    }
    (folder / "contract.json").write_text(dumps(contract))
    cells = []
    for r in targets:
        for seed in contract["seeds"]:
            for engine in contract["engines"]:
                result = search(
                    SearchRequest(
                        smiles=r["raw"]["smiles"],
                        mode="quick",
                        seed=seed,
                        engine=engine,
                        candidate_stock=True,
                        seconds=2.0,
                        iterations=10,
                        depth=4,
                    )
                )
                cell = {
                    "target": r["raw"]["query_name"],
                    "seed": seed,
                    "engine": engine,
                    "run_id": result["run_id"],
                    "status": result["status"],
                    "routes": len(result["routes"]),
                    "evidence_closed": sum(
                        x["evidence_closed"] for x in result["routes"]
                    ),
                    "native_solved": sum(x["native_solved"] for x in result["routes"]),
                    "search_seconds": sum(
                        x["search_seconds"] for x in result.get("phases", [])
                    ),
                }
                cells.append(cell)
                if progress:
                    progress(cells.copy())
                (
                    folder / (r["id"] + "-" + str(seed) + "-" + engine + ".json")
                ).write_text(dumps(cell))
    report = {
        "contract_sha256": sha(folder / "contract.json"),
        "expected_cells": 12,
        "completed_cells": len(cells),
        "failures": sum(x["status"] != "ok" for x in cells),
        "cells": cells,
        "claim": "Engineering development observation only; no chemical superiority conclusion",
    }
    (folder / "summary.json").write_text(dumps(report))
    for p in folder.iterdir():
        p.chmod(0o444)
    return str(folder), report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--workspace")
    args = parser.parse_args()
    from .workspace import configure
    configure(args.workspace)
    if args.development:
        folder, result = compare()
        print(dumps({"folder": folder, **result}))
    else:
        print(dumps(preflight()))
