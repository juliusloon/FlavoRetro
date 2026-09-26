"""Immutable, hash-bound SQLite query index; JSON remains the source of truth."""
import argparse
import json
import sqlite3
from pathlib import Path
from .resources import sha, dumps
from .workspace import active_data, root, configure, AssetError

SCHEMA_VERSION = 1

def build():
    folder, manifest, pointer = active_data()
    db = folder / "index.sqlite"
    sidecar = folder / "index.json"
    if db.exists() or sidecar.exists():
        raise ValueError("index exists; retain it and build a new immutable resource version")
    rows = json.loads((folder / "records.json").read_text())
    sources = json.loads((root() / "metadata/sources.json").read_text())["files"]
    connection = sqlite3.connect(db)
    try:
        connection.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE sources(path TEXT PRIMARY KEY, sha256 TEXT NOT NULL, metadata_json TEXT NOT NULL);
            CREATE TABLE records(ordinal INTEGER UNIQUE NOT NULL, id TEXT PRIMARY KEY, kind TEXT NOT NULL,
                source_path TEXT NOT NULL REFERENCES sources(path), source_status TEXT NOT NULL,
                production_eligible INTEGER NOT NULL CHECK(production_eligible IN (0,1)),
                raw_json TEXT NOT NULL, search_text TEXT NOT NULL);
            CREATE INDEX records_kind ON records(kind, ordinal);
            CREATE INDEX records_status ON records(source_status, ordinal);
            CREATE TABLE outcomes(record_id TEXT PRIMARY KEY REFERENCES records(id), value REAL,
                is_missing INTEGER NOT NULL CHECK(is_missing IN (0,1)), raw_json TEXT NOT NULL);
            CREATE TABLE qc(record_id TEXT REFERENCES records(id), issue TEXT NOT NULL, detail_json TEXT NOT NULL);
            CREATE INDEX qc_issue ON qc(issue, record_id);
        """)
        bypath = {s["path"]: s for s in sources}
        for s in sources:
            if sha(root() / s["path"]) != s["sha256"]:
                raise AssetError("source hash drift " + s["path"])
            connection.execute("INSERT INTO sources VALUES(?,?,?)", (s["path"], s["sha256"], dumps(s)))
        for ordinal, row in enumerate(rows):
            if bypath[row["source_path"]]["sha256"] != row["source_sha256"]:
                raise AssetError("record/source hash mismatch")
            body = json.dumps(row, ensure_ascii=False)
            connection.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?)",
                (ordinal,row["id"],row["kind"],row["source_path"],row["source_status"],int(row["production_eligible"]),body,body.casefold()))
            if "outcome" in row:
                outcome = row["outcome"]
                connection.execute("INSERT INTO outcomes VALUES(?,?,?,?)",(row["id"],outcome["value"],int(outcome["is_missing"]),dumps(outcome)))
            checks = list(row.get("issues", []))
            if row.get("name_conflict_recomputed"):
                checks.append("name_conflict")
            if row["kind"] in {"molecule_failures", "molecule_duplicate_names"}:
                checks.append(row["kind"])
            for i, component in enumerate(row.get("components", [])):
                if component.get("structure", {}).get("status") == "parse_failure":
                    checks.append("component_parse_failure:" + str(i))
            for issue in checks:
                connection.execute("INSERT INTO qc VALUES(?,?,?)",(row["id"],str(issue),dumps({"issue":issue})))
        assert not connection.execute("PRAGMA foreign_key_check").fetchall()
        assert connection.execute("SELECT count(*) FROM records").fetchone()[0] == len(rows)
        connection.commit()
    finally:
        connection.close()
    sidecar.write_text(dumps({"schema_version":SCHEMA_VERSION,"resource_version":pointer["version"],
        "resource_manifest_sha256":pointer["manifest_sha256"],"records_sha256":manifest["records_sha256"],
        "database_sha256":sha(db),"records":len(rows),"sources":len(sources),"builder_sha256":sha(__file__)}))
    db.chmod(0o444)
    sidecar.chmod(0o444)
    return json.loads(sidecar.read_text())

def metadata():
    folder, manifest, pointer = active_data()
    try:
        meta = json.loads((folder / "index.json").read_text())
        if (meta["schema_version"] != SCHEMA_VERSION or meta["resource_version"] != pointer["version"]
            or meta["resource_manifest_sha256"] != pointer["manifest_sha256"]
            or meta["records_sha256"] != manifest["records_sha256"]
            or meta["database_sha256"] != sha(folder / "index.sqlite")):
            raise AssetError("database_integrity_failed: stale/corrupt index; rebuild a new immutable resource version")
        return folder, meta
    except (FileNotFoundError, KeyError) as exc:
        raise AssetError("missing_index: python -m flavoretro.database --build --workspace <workspace>") from exc

def query(kind="", q="", offset=0, limit=25, issue="", source_status="", outcome=""):
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("invalid pagination")
    if outcome not in {"", "missing", "zero", "numeric", "unparsed"}:
        raise ValueError("invalid outcome filter")
    folder, meta = metadata()
    conditions, args = [], []
    for key, value in (("kind",kind),("source_status",source_status)):
        if value:
            conditions.append(key + "=?"); args.append(value)
    if q:
        conditions.append("instr(search_text,?)>0"); args.append(q.casefold())
    if issue:
        conditions.append("id IN (SELECT record_id FROM qc WHERE instr(issue,?)>0)"); args.append(issue)
    if outcome:
        predicates = {"missing":"is_missing=1", "zero":"is_missing=0 AND value=0", "numeric":"is_missing=0 AND value IS NOT NULL", "unparsed":"is_missing=0 AND value IS NULL"}
        conditions.append("id IN (SELECT record_id FROM outcomes WHERE " + predicates[outcome] + ")")
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    with sqlite3.connect((folder / "index.sqlite").as_uri() + "?mode=ro", uri=True) as connection:
        connection.execute("PRAGMA query_only=ON")
        total = connection.execute("SELECT count(*) FROM records" + where,args).fetchone()[0]
        found = connection.execute("SELECT raw_json FROM records" + where + " ORDER BY ordinal LIMIT ? OFFSET ?",args+[limit,offset]).fetchall()
    return {"total":total,"records":[json.loads(r[0]) for r in found],"resource_version":meta["resource_version"]}

def records():
    # Inventory consumers still receive lossless records, using the same checked index.
    result = query(limit=100)
    rows = result["records"]
    for offset in range(100,result["total"],100):
        rows.extend(query(offset=offset,limit=100)["records"])
    return rows

def main():
    parser = argparse.ArgumentParser(description="Build/inspect the local immutable SQLite resource index")
    parser.add_argument("--workspace")
    parser.add_argument("--build",action="store_true")
    args = parser.parse_args(); configure(args.workspace)
    print(dumps(build() if args.build else metadata()[1]))

if __name__ == "__main__":
    main()
