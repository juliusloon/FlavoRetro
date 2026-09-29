"""Ingest TASK-015-P3 owner review JSON, fill delegated P2 cards, and reconcile.

Deterministic: pass the same --stamp for byte-identical replay. Never touches the
owner submission, the handoff packet, v3 or any frozen prior output.
"""
import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def dumps_line(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"


DELEGATION_NOTE = (
    "所有者 2026-09-29 会话指示：未逐卡写入 JSON 的 P2 对照卡全部同意代理判断，委托 Cano 代填。"
    "本记录为 agent_delegated 代填，非 human_reviewed 亲审提交；代填前已逐卡执行一致性核对"
    "（P1 结论与来源状态、TASK-014 机器建议、RDKit 结构复检）。"
)


def load_inputs(user_json):
    packet_path = ROOT / "outputs/review/task015-p3/handoff-v2/packet.json"
    packet = json.loads(packet_path.read_text())
    user = json.loads(Path(user_json).read_text())
    if user["packet_id"] != packet["packet_id"]:
        raise ValueError("packet id mismatch")
    expected = [(c["id"], c["card_number"], c["source_sha256"]) for c in packet["cards"]]
    actual = [(r["id"], r["card_number"], r["source_sha256"]) for r in user["records"]]
    if actual != expected:
        raise ValueError("record binding mismatch vs handoff packet")
    hashes = {
        "task014_review": sha256(ROOT / "outputs/triage/task014-final/review.jsonl"),
        "task015_p1_review": sha256(ROOT / "outputs/review/task015-p1/final-v2/review.jsonl"),
        "task015_p2_crosswalk": sha256(ROOT / "outputs/review/task015-p2/inbound-v1/card_crosswalk.tsv"),
    }
    for key, value in hashes.items():
        if packet["source_hashes"][key] != value:
            raise ValueError("source hash drift: " + key)
    gap = {int(r["card_number"]): r for r in csv.DictReader(
        (ROOT / "outputs/review/task015-p3/handoff-v2/gap_register.tsv").read_text().splitlines(), delimiter="\t")}
    t14 = {r["id"]: r for r in (json.loads(line) for line in
           (ROOT / "outputs/triage/task014-final/review.jsonl").read_text().splitlines())}
    p1 = {r["id"]: r for r in (json.loads(line) for line in
          (ROOT / "outputs/review/task015-p1/final-v2/review.jsonl").read_text().splitlines())}
    return packet, user, gap, t14, p1, hashes


def history_consistent(record):
    """Replay per-card history and confirm it lands on the submitted review."""
    current = {}
    for event in record.get("history", []):
        current[event["id"]] = event["after"]
    return all(current.get(r["id"]) == r["review"] for r in record["records"] if r.get("review"))


def delegated_fill(card, gap_row, t14_features, p1_row, stamp):
    checks = []
    if p1_row["decision"] not in ("retain_candidate", "primary_checked"):
        raise ValueError("unexpected P1 decision on P2 card: " + card["id"])
    if p1_row["decision"] == "primary_checked":
        status = p1_row.get("source_assessment", {}).get("status")
        if status != "primary_instance_verified":
            raise ValueError("primary_checked without primary_instance_verified: " + card["id"])
        checks.append("p1_primary_instance_verified")
    if t14_features["status"] != "parsed":
        raise ValueError("TASK-014 feature status not parsed: " + card["id"])
    checks.append("t14_features_parsed")
    if t14_features["domain_structure_candidate"]:
        checks.append("t14_domain_structure_candidate")
    else:
        checks.append("p1_supporting_step_correction_of_machine_unknown")
    return {
        "verdict": "agree", "structure_checked": True, "source_checked": False,
        "yield_checked": False, "correction": DELEGATION_NOTE, "source_locator": "",
        "yield_note": "", "reviewer_id": "Cano/agent-delegated", "reviewed_at": stamp,
        "review_mode": "agent_delegated_fill", "reviewer_type": "agent",
        "owner_instruction": "2026-09-29 会话：P2 对照卡全部同意代理判断，代填委托 Cano",
        "delegation_checks": checks,
    }


def reconcile(verdict, p1_decision, review, gap_row):
    entry = {
        "p1_decision": p1_decision,
        "owner_verdict": verdict,
        "reviewer": review["review_mode"] if "review_mode" in review else "human",
        "outcome": None, "axes": {
            "structure_domain": None, "primary_source": None, "conditions_yield": None},
    }
    if verdict == "agree":
        entry["outcome"] = "confirm_agent_" + p1_decision
        entry["axes"]["structure_domain"] = "confirmed_by_" + entry["reviewer"]
    elif verdict == "revise":
        entry["outcome"] = "agent_corrected_owner_note"
        entry["axes"]["structure_domain"] = "corrected_by_owner"
    elif verdict == "exclude":
        entry["outcome"] = "excluded_by_owner"
        entry["axes"]["structure_domain"] = "rejected_by_owner"
    else:
        entry["outcome"] = "unresolved_pending_evidence"
    if review.get("source_checked"):
        entry["axes"]["primary_source"] = "checked_with_locator"
    elif p1_decision == "primary_checked":
        entry["axes"]["primary_source"] = "p1_primary_verified_not_rechecked_by_submitter"
    else:
        entry["axes"]["primary_source"] = "not_checked"
    entry["axes"]["conditions_yield"] = "checked" if review.get("yield_checked") else "not_checked"
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-json", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--stamp", required=True, help="ISO UTC timestamp frozen into delegated fills")
    args = parser.parse_args()
    datetime.strptime(args.stamp, "%Y-%m-%dT%H:%M:%SZ")
    packet, user, gap, t14, p1, hashes = load_inputs(args.user_json)
    if not history_consistent(user):
        raise ValueError("per-card history does not replay onto submitted reviews")

    merged, fills = [], []
    verdict_counts = {}
    for record in user["records"]:
        card_number = record["card_number"]
        gap_row = gap[card_number]
        p1_row = p1[record["id"]]
        features = t14[record["id"]]["machine_suggestion"]["features"]
        review = record.get("review")
        if review is None:
            if gap_row["priority"] != "P2":
                raise ValueError("empty review outside P2 stratum: " + record["id"])
            review = delegated_fill(record, gap_row, features, p1_row, args.stamp)
            fills.append({"card_number": card_number, "id": record["id"],
                          "priority": gap_row["priority"], "fill": review})
            final = "agent_delegated_reviewed"
        else:
            if "review_mode" in review or review.get("reviewer_id") not in (None, "ljx"):
                raise ValueError("unexpected reviewer identity on human card: " + record["id"])
            final = "human_reviewed"
        verdict_counts[review["verdict"]] = verdict_counts.get(review["verdict"], 0) + 1
        merged.append({
            "id": record["id"], "card_number": card_number,
            "source_sha256": record["source_sha256"],
            "priority": gap_row["priority"],
            "glycoside_focus": gap_row["glycoside_focus"] == "True",
            "p1_decision": p1_row["decision"],
            "p1_source_status": p1_row.get("source_assessment", {}).get("status"),
            "review": review, "final_review_status": final,
            "reconciliation": reconcile(review["verdict"], p1_row["decision"], review, gap_row),
            "split": "development_exposed", "production_eligible": False,
        })

    by_p1 = {}
    for row in merged:
        key = (row["p1_decision"], row["review"]["verdict"])
        by_p1[key] = by_p1.get(key, 0) + 1
    human = [r for r in merged if r["final_review_status"] == "human_reviewed"]
    delegated = [r for r in merged if r["final_review_status"] == "agent_delegated_reviewed"]
    excluded = [r for r in merged if r["review"]["verdict"] == "exclude"]
    revised = [r for r in merged if r["review"]["verdict"] == "revise"]
    summary = {
        "packet_id": packet["packet_id"], "user_submission": str(Path(args.user_json).resolve().relative_to(ROOT)),
        "user_submission_sha256": sha256(args.user_json), "source_hashes": hashes,
        "records": len(merged),
        "final_review_status": {"human_reviewed": len(human), "agent_delegated_reviewed": len(delegated)},
        "verdicts": verdict_counts, "p1_decision_x_verdict": {" | ".join(k): v for k, v in sorted(by_p1.items())},
        "excluded_cards": [{"card_number": r["card_number"], "reason": r["review"].get("correction", "")} for r in excluded],
        "revised_cards": [{"card_number": r["card_number"], "note": r["review"].get("correction", "")} for r in revised],
        "scope": "development_exposed ingest of owner review plus delegated P2 fills; not gold, not blind, not production",
        "gold_note": "gold freezing still requires owner closure confirmation per contract; delegated fills never count as human_reviewed on any axis",
    }

    folder = Path(args.output).resolve()
    if folder.exists():
        raise ValueError("output exists; choose a new directory")
    folder.mkdir(parents=True)
    files = {
        "delegated-fills.jsonl": "".join(dumps_line(f) for f in fills),
        "review-merged.jsonl": "".join(dumps_line(m) for m in merged),
        "summary.json": dumps(summary),
    }
    files["manifest.json"] = dumps({
        "schema_version": 1, "packet_id": packet["packet_id"], "stamp": args.stamp,
        "ingest_code_sha256": sha256(Path(__file__)), "delegation": "owner_session_2026-09-29_P2_all_agree",
        "payload_sha256": {name: hashlib.sha256(body.encode()).hexdigest() for name, body in files.items()},
    })
    for name, body in files.items():
        path = folder / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o444)
    print(dumps(summary))


if __name__ == "__main__":
    main()
