"""Freeze TASK-015-P3 development gold (structure/classification axis, 53 cards).

Owner closure decisions, 2026-09-29 session:
  1. Plan B: full 53-card gold; the 22 P2 control cards stand as agree via delegated fill.
  2. Gold covers the structure/classification axis only; agent-reviewed provenance is
     gold-eligible by owner decision (recorded honestly, never as human_reviewed).
Deterministic replay with the same --stamp. Inputs are hash-verified and never mutated.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

INGEST = ROOT / "outputs/review/task015-p3/ingest-1"
GOLD_VERSION = "task015-p3-gold-v1"
CLOSURE_NOTE = (
    "所有者 2026-09-29 闭环决定：①53 张全量 gold（22 张 P2 对照卡按其指示以代理代填 agree 计入）；"
    "②gold 仅覆盖结构/分类轴，agent 审核的轴按所有者决定计入 gold（保留 agent 溯源，不冒充 human_reviewed）。"
)

EXCLUSION_PATTERNS = {
    27: "path_compression_multistep_exported_as_single_reaction",
    28: "no_usable_reaction_content_abstract_only",
    51: "no_usable_reaction_content",
    52: "no_usable_reaction_content_no_primary_fulltext",
    53: "retracted_source",
    54: "product_structure_unavailable",
    55: "incomplete_reaction_export_product_only",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def dumps_line(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stamp", required=True, help="ISO UTC timestamp frozen into the artifacts")
    args = parser.parse_args()
    datetime.strptime(args.stamp, "%Y-%m-%dT%H:%M:%SZ")

    manifest = json.loads((INGEST / "manifest.json").read_text())
    for name, digest in manifest["payload_sha256"].items():
        if sha256(INGEST / name) != digest:
            raise ValueError("ingest payload drift: " + name)
    summary = json.loads((INGEST / "summary.json").read_text())
    merged = [json.loads(line) for line in (INGEST / "review-merged.jsonl").read_text().splitlines()]
    fills = {f["card_number"]: f for f in (json.loads(line) for line in
             (INGEST / "delegated-fills.jsonl").read_text().splitlines())}
    p1 = {r["id"]: r for r in (json.loads(line) for line in
          (ROOT / "outputs/review/task015-p1/final-v2/review.jsonl").read_text().splitlines())}
    if len(merged) != 60 or len(fills) != 22:
        raise ValueError("unexpected ingest population")
    if sha256(ROOT / summary["user_submission"]) != summary["user_submission_sha256"]:
        raise ValueError("owner submission drift")

    # Final merged review JSON in the submission schema: 38 owner reviews untouched,
    # 22 delegated fills carried over with agent identity preserved (never ljx).
    final_records = []
    for row in merged:
        review = dict(row["review"])
        if row["final_review_status"] == "agent_delegated_reviewed":
            if review["reviewer_id"] != "Cano/agent-delegated":
                raise ValueError("delegated identity drift on card " + str(row["card_number"]))
        final_records.append({"id": row["id"], "card_number": row["card_number"],
                              "source_sha256": row["source_sha256"], "review": review})
    final = {
        "schema_version": 1, "packet_id": summary["packet_id"],
        "split": "development_exposed", "status": "final_merged_owner_and_delegated",
        "reviewer_id": "mixed:38×ljx(human)+22×Cano/agent-delegated(agent)",
        "provenance_note": CLOSURE_NOTE + " 本文件由 freeze 脚本从 ingest-1 确定性生成，所有者提交原件未改动。",
        "records": final_records,
    }

    gold, excluded = [], []
    for row in merged:
        verdict = row["review"]["verdict"]
        base = {
            "id": row["id"], "card_number": row["card_number"], "priority": row["priority"],
            "glycoside_focus": row["glycoside_focus"], "verdict": verdict,
            "p1_decision": row["p1_decision"], "p1_source_status": row["p1_source_status"],
            "review": row["review"], "final_review_status": row["final_review_status"],
            "split": "development_exposed", "production_eligible": False,
            "gold_version": GOLD_VERSION, "gold_scope": "structure_classification_axis_only",
        }
        if verdict in ("agree", "revise"):
            agent = p1[row["id"]]
            base["labels"] = {
                "domain_relevance": agent["domain_relevance"],
                "transformation_labels": agent["transformation_labels"],
                "transformation_description_zh": agent["transformation_description_zh"],
                "glycoside_assessment": agent["glycoside_assessment"],
            }
            human = row["final_review_status"] == "human_reviewed"
            base["structure_axis_provenance"] = {
                "owner_checked_structure": bool(row["review"].get("structure_checked")),
                "reviewer_types": ["human", "agent"] if human else ["agent"],
                "note": ("所有者亲核结构轴并确认/更正代理标签" if human and row["review"].get("structure_checked")
                         else "所有者裁决采纳代理结构标签（未亲核结构复选框）" if human
                         else "所有者委托代理按 agree 代填；agent 复检层级，非 human_reviewed"),
            }
            if verdict == "revise":
                base["owner_correction_zh"] = row["review"].get("correction", "")
            gold.append(base)
        else:
            base["exclusion"] = {
                "reason_zh": row["review"].get("correction", ""),
                "calibration_pattern": EXCLUSION_PATTERNS[row["card_number"]],
            }
            excluded.append(base)
    if len(gold) != 53 or len(excluded) != 7:
        raise ValueError("gold/excluded partition mismatch")

    human_gold = [g for g in gold if g["final_review_status"] == "human_reviewed"]
    delegated_gold = [g for g in gold if g["final_review_status"] == "agent_delegated_reviewed"]
    gold_summary = {
        "gold_version": GOLD_VERSION, "stamp": args.stamp, "closure_note": CLOSURE_NOTE,
        "packet_id": summary["packet_id"],
        "user_submission": summary["user_submission"],
        "user_submission_sha256": summary["user_submission_sha256"],
        "ingest_payload_sha256": manifest["payload_sha256"],
        "axis": {"structure_classification": {"records": 53,
                 "human_reviewed": len(human_gold), "agent_delegated": len(delegated_gold),
                 "human_owner_checked_structure": sum(
                     g["final_review_status"] == "human_reviewed" and g["review"].get("structure_checked") for g in gold),
                 "human_confirmed_without_structure_recheck": sum(
                     g["final_review_status"] == "human_reviewed" and not g["review"].get("structure_checked") for g in gold),
                 "agent_rechecked_structure_delegated": sum(
                     g["final_review_status"] == "agent_delegated_reviewed" and g["review"].get("structure_checked") for g in gold),
                 "revise_records": sum(g["verdict"] == "revise" for g in gold),
                 "glycoside_focus": sum(g["glycoside_focus"] for g in gold)}},
        "axes_not_frozen": {
            "primary_source": "0/60 所有者亲核；9 张 P1 代理 primary_instance_verified 仅作上下文，不冻结为 gold 轴",
            "conditions_yield": "0/60 核对，不冻结"},
        "excluded": [{"card_number": e["card_number"], "calibration_pattern": e["exclusion"]["calibration_pattern"]}
                     for e in excluded],
        "boundaries": [
            "全部 60 卡 development_exposed；此 gold 只用于开发校准，不得改名或用作未见盲测",
            "22 张代填卡保留 agent 溯源（reviewer Cano/agent-delegated + 所有者指示引用），不声称 human_reviewed",
            "0 production；MCTS/搜索未接入；正式 benchmark、公开发布不在本任务范围"],
        "scope": "development gold for structure/classification axis only; not a chemical accuracy certificate",
    }

    out_final = ROOT / "outputs/review/task015-p3/final"
    out_gold = ROOT / "outputs/review/task015-p3/gold-v1"
    for folder in (out_final, out_gold):
        if folder.exists():
            raise ValueError("output exists: " + str(folder))
    out_final.mkdir(parents=True)
    out_gold.mkdir(parents=True)
    final_body = dumps(final)
    files = {
        out_final / "review-final-60.json": final_body,
        out_gold / "gold.jsonl": "".join(dumps_line(g) for g in gold),
        out_gold / "excluded.jsonl": "".join(dumps_line(e) for e in excluded),
        out_gold / "summary.json": dumps(gold_summary),
    }
    files[out_gold / "manifest.json"] = dumps({
        "schema_version": 1, "gold_version": GOLD_VERSION, "stamp": args.stamp,
        "freeze_code_sha256": sha256(Path(__file__)),
        "final_json_sha256": hashlib.sha256(final_body.encode()).hexdigest(),
        "owner_decision": "2026-09-29 session: plan B full 53 gold; structure axis only; agent provenance counts",
        "payload_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(b.encode()).hexdigest() for p, b in files.items()},
    })
    for path, body in files.items():
        path.write_text(body, encoding="utf-8")
        path.chmod(0o444)
    print(dumps(gold_summary))


if __name__ == "__main__":
    main()
