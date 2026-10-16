#!/usr/bin/env python3
"""TASK-016-P3 G1 closure: consolidate the inherited-queue evidence review.

1. Validate and merge temp/p3-extract/inh-batch{1..5}.json (35 inherited
   pending_source_only_title_candidate articles) into
   outputs/task016-p3/v1/inherited_queue_review.jsonl.
2. Rewrite outputs/task016-p3/v1/metadata_dispositions.jsonl: every acquired
   article gets a final review_status with pointers (extracted groups vs
   inherited review batches); no record stays "awaiting review" without a
   next step.
3. Build outputs/task016-p3/v1/inherited_queue_crosswalk.jsonl binding every
   P2 inherited record (35 title candidates, 10 unresolved, 2 provisional
   withdrawals, 12 primary/extension reviews) to its P3 disposition and
   evidence pointer.  P2 records themselves are read-only.
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / "temp/p3-extract"
V1 = ROOT / "outputs/task016-p3/v1"
P2V2 = ROOT / "outputs/task016-p2/v2"

CANDIDATE_FIELDS = [
    "pmcid", "disposition", "context", "class", "enzyme_or_catalyst",
    "acceptor_name", "acceptor_compound_number", "donor_name", "product_name",
    "product_compound_number", "new_bond", "sugar_stereo_evidence",
    "evidence_locators", "evidence_quotes", "conditions_summary",
    "yield_reported", "identity_complete", "missing_elements",
]
SOURCE_P2 = "outputs/task016-p2/v2"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    return 2


def main():
    # 1. merge inherited batches
    records = []
    batch_files = {}
    for i in (1, 2, 3, 4, 5):
        p = TEMP / f"inh-batch{i}.json"
        if not p.exists():
            return fail(f"missing {p}")
        data = json.loads(p.read_text())
        if not isinstance(data, list) or not data:
            return fail(f"{p} is not a non-empty JSON array")
        batch_files[f"batch{i}"] = p.name
        for rec in data:
            if rec.get("disposition") == "candidate":
                missing = [f for f in CANDIDATE_FIELDS if f not in rec]
                if missing:
                    return fail(f"{p} candidate missing fields {missing}")
                if not rec.get("evidence_quotes"):
                    return fail(f"{p} candidate without evidence_quotes")
            elif rec.get("disposition") == "no_candidate":
                if not rec.get("notes"):
                    return fail(f"{p} no_candidate without notes")
            else:
                return fail(f"{p} unknown disposition {rec.get('disposition')!r}")
            out = dict(rec)
            out["review_batch"] = f"inh-batch{i}"
            out["review_source_file"] = str(p.relative_to(ROOT))
            records.append(out)

    pmcids = sorted({r["pmcid"] for r in records})
    p2 = [json.loads(l) for l in (P2V2 / "metadata_dispositions.jsonl").open() if l.strip()]
    p2_pend = {r["pmcid"] for r in p2 if r.get("disposition") == "pending_source_only_title_candidate_not_acquired"}
    uncovered = p2_pend - set(pmcids)
    extra = set(pmcids) - p2_pend
    if uncovered:
        return fail(f"inherited articles without review: {sorted(uncovered)}")
    if extra:
        return fail(f"reviewed articles outside inherited set: {sorted(extra)}")

    review_path = V1 / "inherited_queue_review.jsonl"
    with review_path.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    # 2. refresh per-article dispositions
    disp_path = V1 / "metadata_dispositions.jsonl"
    dispositions = [json.loads(l) for l in disp_path.open() if l.strip()]
    group_of = {}
    for g in "ABCDEFGH":
        for rec in json.loads((TEMP / f"group-{g}.json").read_text()):
            group_of.setdefault(rec["pmcid"], set()).add(g)
    inh_counts = Counter()
    for rec in records:
        inh_counts[rec["pmcid"]] += 1 if rec["disposition"] == "candidate" else 0
    inh_nocand = Counter()
    for rec in records:
        if rec["disposition"] != "candidate":
            inh_nocand[rec["pmcid"]] += 1

    out_disp = []
    for d in dispositions:
        pmcid = d["pmcid"]
        if pmcid in p2_pend:
            d = dict(d)
            d["review_status"] = "reviewed_inherited_queue"
            d["review_result"] = (
                f"{inh_counts[pmcid]} candidate record(s), "
                f"{inh_nocand[pmcid]} no_candidate record(s)"
            )
            d["review_evidence"] = "outputs/task016-p3/v1/inherited_queue_review.jsonl"
            d["next_step"] = (
                "candidate records enter G2 single-step admission dedup; "
                "no_candidate records carry scope-exclusion reasoning"
            )
        elif pmcid in group_of:
            d = dict(d)
            d["review_status"] = "extracted_group_evidence"
            d["review_result"] = f"groups {','.join(sorted(group_of[pmcid]))} extraction records"
            d["review_evidence"] = (
                "temp/p3-extract/group-*.json -> outputs/task016-p3/v1/candidate_reactions.jsonl"
            )
            d["next_step"] = "candidate records enter G2 single-step admission dedup"
        else:
            d = dict(d)
            d["review_status"] = "acquired_not_extracted_review_required"
        out_disp.append(d)
    tmp = disp_path.with_suffix(".jsonl.tmp")
    with tmp.open("w") as f:
        for d in out_disp:
            f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(disp_path)

    # 3. crosswalk of every P2 inherited record to its P3 disposition
    cand_by_pmc = {}
    for rec in records:
        if rec["disposition"] == "candidate":
            cand_by_pmc.setdefault(rec["pmcid"], []).append(rec)

    cross = []
    for r in p2:
        if r.get("disposition") != "pending_source_only_title_candidate_not_acquired":
            continue
        pmcid = r["pmcid"]
        cands = cand_by_pmc.get(pmcid, [])
        cross.append({
            "p2_record_type": "pending_source_only_title_candidate_not_acquired",
            "pmcid": pmcid,
            "p2_metadata_key": r.get("metadata_key"),
            "title": r.get("title"),
            "p3_disposition": (
                "reviewed_candidates_found" if cands else "reviewed_no_candidate"
            ),
            "p3_candidate_uids": [
                f"INH-{pmcid}-{i:03d}" for i, _ in enumerate(cands)
            ],
            "p3_evidence": "outputs/task016-p3/v1/inherited_queue_review.jsonl",
        })
    for name, rtype in (
        ("unresolved_instances.jsonl", "unresolved_instance"),
        ("provisional_withdrawn_instances.jsonl", "provisional_withdrawn_instance"),
        ("primary_extension_source_review.jsonl", "primary_extension_source_review"),
    ):
        p = P2V2 / name
        for r in [json.loads(l) for l in p.open() if l.strip()]:
            pmcid = r.get("pmcid")
            grps = sorted(group_of.get(pmcid, set()))
            cross.append({
                "p2_record_type": rtype,
                "pmcid": pmcid,
                "p2_reason": r.get("reason") or r.get("source_disposition") or r.get("admission_status"),
                "p3_disposition": (
                    f"re_extracted_in_groups_{','.join(grps)}" if grps
                    else "not_re_extracted_in_p3"
                ),
                "p3_evidence": (
                    "temp/p3-extract/group-*.json -> outputs/task016-p3/v1/candidate_reactions.jsonl"
                    if grps else "outputs/task016-p3/v1/metadata_dispositions.jsonl"
                ),
                "p2_original_file": f"{SOURCE_P2}/{name}",
            })

    cross_path = V1 / "inherited_queue_crosswalk.jsonl"
    with cross_path.open("w") as f:
        for c in cross:
            f.write(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n")

    cands = [r for r in records if r["disposition"] == "candidate"]
    print(f"inherited review records: {len(records)} "
          f"(candidates {len(cands)}, no_candidate {len(records) - len(cands)})")
    print("candidate class:", dict(Counter(r.get("class") for r in cands)))
    print("candidate identity_complete:",
          dict(Counter(str(r.get("identity_complete")) for r in cands)))
    print(f"wrote {review_path}")
    print(f"refreshed {len(out_disp)} dispositions in {disp_path}")
    print(f"wrote {len(cross)} crosswalk records to {cross_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
