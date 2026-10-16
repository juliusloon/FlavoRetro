#!/usr/bin/env python3
"""TASK-016-P3: rebuild the reaction-level candidate merge from the eight group
extraction files.  The earlier PMCID-level collapse (temp/p3-extract/merged-candidates.json,
25 stubs) is superseded by this deterministic rebuild: every candidate and
no_candidate record is kept verbatim with full evidence fields plus a stable
candidate_uid.  Read-only on the group files; writes only P3 outputs."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = "ABCDEFGH"
OUT_DIR = ROOT / "outputs/task016-p3/v1"
TEMP_DIR = ROOT / "temp/p3-extract"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    records = []
    group_files = {}
    for g in GROUPS:
        src = TEMP_DIR / f"group-{g}.json"
        if not src.exists():
            print(f"ERROR: missing {src}", file=sys.stderr)
            return 2
        group_files[g] = sha256_file(src)
        data = json.loads(src.read_text())
        for idx, rec in enumerate(data):
            if rec.get("pmcid") is None:
                print(f"ERROR: group {g} record {idx} missing pmcid", file=sys.stderr)
                return 2
            out = dict(rec)
            out["group"] = g
            out["candidate_uid"] = f"P3CAND-{g}-{rec['pmcid']}-{idx:03d}"
            out["source_group_file"] = f"temp/p3-extract/group-{g}.json"
            out["source_group_file_sha256"] = group_files[g]
            records.append(out)

    out_path = OUT_DIR / "candidate_reactions.jsonl"
    with out_path.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    cands = [r for r in records if r.get("disposition") == "candidate"]
    nocands = [r for r in records if r.get("disposition") != "candidate"]
    cls = Counter(r.get("class") for r in cands)
    ident = Counter(str(r.get("identity_complete")) for r in cands)
    ev = Counter(r.get("sugar_stereo_evidence") or "none" for r in cands)
    grp = Counter(r["group"] for r in cands)
    pmcids = sorted({r["pmcid"] for r in records})

    summary = {
        "generated_by": "scripts/task016_p3_merge.py",
        "group_file_sha256": group_files,
        "total_records": len(records),
        "candidates": len(cands),
        "no_candidate_records": len(nocands),
        "unique_pmcids": len(pmcids),
        "candidate_class_distribution": dict(cls),
        "candidate_identity_complete_distribution": dict(ident),
        "candidate_evidence_distribution": dict(ev),
        "candidate_group_distribution": dict(grp),
        "note": (
            "reaction-level extraction candidates from eight P3 discovery groups; "
            "supersedes the PMCID-level collapse in temp/p3-extract/merged-candidates.json "
            "and outputs/task016-p3/merged_summary.json (kept only as superseded working "
            "files). Extraction counts are admission targets inputs, not admitted reactions."
        ),
    }
    (OUT_DIR / "candidate_extraction_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    )

    print(f"records={len(records)} candidates={len(cands)} no_candidate={len(nocands)} "
          f"unique_pmcids={len(pmcids)}")
    print(f"class={dict(cls)}")
    print(f"identity={dict(ident)}")
    print(f"wrote {out_path}")
    print(f"wrote {OUT_DIR / 'candidate_extraction_summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
