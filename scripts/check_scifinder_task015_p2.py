"""Recount TASK-015-P2 receipt and build a non-promoting 60-card crosswalk."""
import csv
import io
import json
from collections import defaultdict
from pathlib import Path

from flavoretro.resources import sha
from scripts.operate import write

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-015-P2"
OUT = ROOT / "outputs/review/task015-p2/inbound-v1"


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    manifest = json.loads((OUT / "manifest.json").read_text())
    summary = json.loads((OUT / "summary.json").read_text())
    records = rows(OUT / "records.jsonl")
    cards = rows(ROOT / "outputs/triage/task014-final/review.jsonl")
    reviews = {x["id"]: x for x in rows(ROOT / "outputs/review/task015-p1/final-v2/review.jsonl")}
    assert len(cards) == len(reviews) == 60
    assert len(records) == summary["rows"] == 635
    assert len({x["id"] for x in records}) == 635
    assert sum(x["rfmt"] for x in manifest["input"]) == 635
    for file in manifest["input"]:
        assert sha(ROOT / "temp" / file["name"]) == file["sha256"]
        assert sha(ROOT / file["frozen_path"]) == file["sha256"]
        local = [x for x in records if x["source_sha256"] == file["sha256"]]
        assert len(local) == file["rfmt"]
        assert {x["locator"] for x in local} == {f"RFMT/{i}" for i in range(1, file["rfmt"] + 1)}
    for name, expected in manifest["output"].items():
        assert sha(OUT / name) == expected
    assert all(x["human_review_status"] == "not_performed" and not x["production_eligible"] and x["split"] == "development_exposed" for x in records)
    by_card = defaultdict(lambda: {"same_cas": [], "exact_structure": [], "reference_only": []})
    for row in records:
        cross = row["crosswalk"]
        for card_id in cross["card_exact_or_cas_ids"]:
            if card_id in cross["old_cas_reaction_ids"]:
                by_card[card_id]["same_cas"].append(row)
            if card_id in cross["old_exact_ids"]:
                by_card[card_id]["exact_structure"].append(row)
        for card_id in cross["card_reference_only_ids"]:
            by_card[card_id]["reference_only"].append(row)
    columns = ["card_number", "card_id", "prior_decision", "same_cas_rows", "same_cas_locators", "exact_structure_rows", "exact_structure_locators", "reference_only_rows", "reference_only_locators", "new_export_procedure_rows", "evidence_interpretation"]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t")
    writer.writeheader()
    counts = {"same_cas_cards": 0, "exact_structure_cards": 0, "reference_only_cards": 0, "export_procedure_card_rows": 0}
    for card in cards:
        card_id = card["id"]
        match = by_card[card_id]
        same, exact, reference = match["same_cas"], match["exact_structure"], match["reference_only"]
        counts["same_cas_cards"] += bool(same)
        counts["exact_structure_cards"] += bool(exact)
        counts["reference_only_cards"] += bool(reference)
        unique = {x["id"]: x for x in same + exact + reference}
        proc = sum(any(k.endswith(":EXP_PROC") for k in x["raw"]["fields"]) for x in unique.values())
        counts["export_procedure_card_rows"] += proc
        def locators(items):
            return "; ".join(sorted({Path(x["original_path"]).name + " " + x["locator"] for x in items}))
        writer.writerow({
            "card_number": reviews[card_id]["card_number"], "card_id": card_id,
            "prior_decision": reviews[card_id]["decision"],
            "same_cas_rows": len(same), "same_cas_locators": locators(same),
            "exact_structure_rows": len(exact), "exact_structure_locators": locators(exact),
            "reference_only_rows": len(reference), "reference_only_locators": locators(reference),
            "new_export_procedure_rows": proc,
            "evidence_interpretation": "same CAS/export structure are database-layer; reference-only is a paper lead, not this card's experiment",
        })
    crosswalk = OUT / "card_crosswalk.tsv"
    if crosswalk.exists():
        assert crosswalk.read_bytes().decode("utf-8") == stream.getvalue(), "card crosswalk drift"
    else:
        write(TASK, str(crosswalk.relative_to(ROOT)), stream.getvalue())
    validation = {"status": "passed", "checks": ["9 source/copy hashes", "635 locators and unique row IDs", "output manifest hashes", "60 card IDs", "candidate-only statuses"], "card_crosswalk_sha256": sha(crosswalk), "card_counts": counts, "source_hashes": {x["name"]: x["sha256"] for x in manifest["input"]}}
    target = OUT / "validation.json"
    if target.exists():
        assert json.loads(target.read_text()) == validation, "validation drift"
    else:
        write(TASK, str(target.relative_to(ROOT)), json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
