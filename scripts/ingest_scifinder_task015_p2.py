"""Immutable local receipt and conservative crosswalk for TASK-015-P2 RDF exports."""
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from rdkit import RDLogger

from flavoretro.resources import rdf_records, sha
from flavoretro.triage import Screener, load_rules, source_keys
from scripts.operate import event, write

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-015-P2"
SOURCE = ROOT / "temp"
INBOX = ROOT / "data/inbox/scifinder/task015-user/20260928"
OUTPUT = ROOT / "outputs/review/task015-p2/inbound-v1"
OLD = ROOT / "outputs/triage/task014-final/pilot.jsonl"
CARDS = ROOT / "outputs/triage/task014-final/review.jsonl"


def lines(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def compact(value):
    return " ".join(str(value or "").split())


def reaction_number(row):
    return row.get("raw", {}).get("fields", {}).get("RXN:VAR(1):CAS_Reaction_Number")


def source_title(row):
    fields = row.get("raw", {}).get("fields", {})
    return compact(fields.get("RXN:VAR(1):REFERENCE(1):TITLE"))


def identifier(file_sha, number):
    return hashlib.sha256(json.dumps([file_sha, number], ensure_ascii=False).encode()).hexdigest()


def main():
    if OUTPUT.exists() or INBOX.exists():
        raise SystemExit("immutable destination exists; use a new version")
    files = sorted(SOURCE.glob("*.rdf"))
    if len(files) != 9:
        raise SystemExit(f"expected nine RDF files; found {len(files)}")
    old = list(lines(OLD))
    cards = list(lines(CARDS))
    if len(old) != 2301 or len(cards) != 60:
        raise SystemExit("frozen TASK-014 input count drift")
    old_exact = defaultdict(list)
    old_cas = defaultdict(list)
    old_ref = defaultdict(set)
    for item in old:
        row = item["input_record"]
        norm = item["features"].get("normalized_reaction")
        if norm:
            old_exact[norm].append(row["id"])
        cas = reaction_number(row)
        if cas:
            old_cas[cas].append(row["id"])
        for key in item.get("source_group_keys", []):
            old_ref[key].add(row["id"])
    card_ids = {x["id"] for x in cards}
    screener = Screener(load_rules()[0])
    RDLogger.DisableLog("rdApp.warning")
    RDLogger.DisableLog("rdApp.error")
    all_rows = []
    manifest = []
    for path in files:
        source_sha = sha(path)
        destination = INBOX / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        if sha(destination) != source_sha:
            raise SystemExit("copy hash mismatch: " + path.name)
        event(TASK, "freeze_binary_copy", source=str(path.relative_to(ROOT)), destination=str(destination.relative_to(ROOT)), sha256=source_sha)
        n = 0
        for i, raw, components, issues, outcome in rdf_records(destination):
            n += 1
            row = {
                "id": identifier(source_sha, i), "kind": "scifinder_reaction",
                "source_path": str(destination.relative_to(ROOT)), "source_sha256": source_sha,
                "original_path": str(path.relative_to(ROOT)), "locator": f"RFMT/{i + 1}",
                "raw": raw, "components": components, "issues": issues, "outcome": outcome,
                "review_status": "agent_checked_candidate", "human_review_status": "not_performed",
                "production_eligible": False, "split": "development_exposed",
            }
            features = screener.reaction(row)
            norm = features["normalized_reaction"]
            cas = reaction_number(row)
            exact_ids = old_exact.get(norm, []) if norm else []
            cas_ids = old_cas.get(cas, []) if cas else []
            ref_keys = source_keys(row)
            reference_ids = sorted({old_id for key in ref_keys for old_id in old_ref.get(key, [])})
            linked_ids = sorted(card_ids.intersection(set(exact_ids) | set(cas_ids)))
            ref_cards = sorted(card_ids.intersection(reference_ids))
            row.update({
                "features": features,
                "source_group_keys": ref_keys,
                "crosswalk": {
                    "old_exact_ids": sorted(exact_ids),
                    "old_cas_reaction_ids": sorted(cas_ids),
                    "old_reference_ids": reference_ids,
                    "card_exact_or_cas_ids": linked_ids,
                    "card_reference_only_ids": sorted(set(ref_cards) - set(linked_ids)),
                },
                "interpretation": "source/structure candidate; bibliography and export are not primary-source confirmation",
            })
            all_rows.append(row)
        count = path.read_text(encoding="utf-8").count("$RFMT ")
        if n != count:
            raise SystemExit(f"RFMT/parsed mismatch {path.name}: {count}/{n}")
        manifest.append({"name": path.name, "sha256": source_sha, "bytes": path.stat().st_size, "rfmt": count, "parsed": n, "frozen_path": str(destination.relative_to(ROOT))})
    seen_cas = defaultdict(list)
    seen_exact = defaultdict(list)
    seen_block = defaultdict(list)
    for row in all_rows:
        cas = reaction_number(row)
        norm = row["features"]["normalized_reaction"]
        if cas:
            seen_cas[cas].append(row["id"])
        if norm:
            seen_exact[norm].append(row["id"])
        seen_block[row["raw"]["block_sha256"]].append(row["id"])
    for row in all_rows:
        cas = reaction_number(row)
        norm = row["features"]["normalized_reaction"]
        row["inbound_overlap"] = {
            "same_cas_reaction_ids": [x for x in seen_cas.get(cas, []) if x != row["id"]] if cas else [],
            "same_exact_structure_ids": [x for x in seen_exact.get(norm, []) if x != row["id"]] if norm else [],
            "same_raw_block_ids": [x for x in seen_block[row["raw"]["block_sha256"]] if x != row["id"]],
        }
    OUTPUT.mkdir(parents=True)
    write(TASK, str((OUTPUT / "records.jsonl").relative_to(ROOT)), "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in all_rows))
    counts = Counter()
    file_summaries = []
    for file in manifest:
        subset = [x for x in all_rows if x["original_path"] == "temp/" + file["name"]]
        fc = Counter()
        for row in subset:
            feat = row["features"]
            fc["parse_issue_rows"] += bool(row["issues"] or feat["status"] != "parsed")
            fc["domain_candidate"] += feat["domain_structure_candidate"]
            fc["glycoside_candidate"] += feat["domain_glycoside_candidate"]
            fc["product_aryl_C"] += feat["product_domain_sites"].get("aryl_C_candidate", 0) > 0
            fc["product_aryl_O"] += feat["product_domain_sites"].get("aryl_O_candidate", 0) > 0
            fc["apparent_C_increase"] += feat["product_domain_sites"].get("aryl_C_candidate", 0) > feat["reactant_domain_sites"].get("aryl_C_candidate", 0)
            fc["apparent_O_increase"] += feat["product_domain_sites"].get("aryl_O_candidate", 0) > feat["reactant_domain_sites"].get("aryl_O_candidate", 0)
            fc["old_exact_rows"] += bool(row["crosswalk"]["old_exact_ids"])
            fc["old_cas_rows"] += bool(row["crosswalk"]["old_cas_reaction_ids"])
            fc["old_reference_rows"] += bool(row["crosswalk"]["old_reference_ids"])
            fc["card_exact_or_cas_rows"] += bool(row["crosswalk"]["card_exact_or_cas_ids"])
            fc["card_reference_only_rows"] += bool(row["crosswalk"]["card_reference_only_ids"])
            fc["yield_numeric"] += row["outcome"]["status"] == "numeric"
            fc["yield_zero"] += row["outcome"]["value"] == 0
            fc["exp_proc"] += any(k.endswith(":EXP_PROC") for k in row["raw"]["fields"])
        counts.update(fc)
        file_summaries.append({**file, "counts": dict(fc), "distinct_cas_reaction_numbers": len({reaction_number(x) for x in subset if reaction_number(x)}), "distinct_exact_structures": len({x["features"]["normalized_reaction"] for x in subset if x["features"]["normalized_reaction"]})})
    summary = {
        "task": TASK, "scope": "local restricted SciFinder exports; development_exposed only",
        "files": file_summaries, "rows": len(all_rows), "totals": dict(counts),
        "distinct_cas_reaction_numbers": len(seen_cas),
        "distinct_exact_structures": len(seen_exact),
        "distinct_raw_blocks": len(seen_block),
        "duplicate_cas_groups": sum(len(x) > 1 for x in seen_cas.values()),
        "duplicate_exact_groups": sum(len(x) > 1 for x in seen_exact.values()),
        "duplicate_raw_block_groups": sum(len(x) > 1 for x in seen_block.values()),
        "unique_card_exact_or_cas_ids": sorted({card for x in all_rows for card in x["crosswalk"]["card_exact_or_cas_ids"]}),
        "unique_card_reference_only_ids": sorted({card for x in all_rows for card in x["crosswalk"]["card_reference_only_ids"]}),
        "source_note": "Topology counts compare encoded graph sites; they do not establish reaction centers or exact positional labels.",
    }
    write(TASK, str((OUTPUT / "summary.json").relative_to(ROOT)), json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    tsv = OUTPUT / "index.tsv"
    columns = ["file", "rfmt", "cas_reaction_number", "title", "yield_raw", "domain", "glycoside", "reactant_C", "product_C", "reactant_O", "product_O", "old_exact", "old_cas", "card_exact_or_cas", "card_reference_only", "issues", "id"]
    import io
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t")
    writer.writeheader()
    for row in all_rows:
        feat = row["features"]
        writer.writerow({
            "file": Path(row["original_path"]).name, "rfmt": row["locator"],
            "cas_reaction_number": reaction_number(row) or "", "title": source_title(row),
            "yield_raw": "" if row["outcome"]["raw"] is None else row["outcome"]["raw"], "domain": int(feat["domain_structure_candidate"]),
            "glycoside": int(feat["domain_glycoside_candidate"]),
            "reactant_C": feat["reactant_domain_sites"].get("aryl_C_candidate", 0),
            "product_C": feat["product_domain_sites"].get("aryl_C_candidate", 0),
            "reactant_O": feat["reactant_domain_sites"].get("aryl_O_candidate", 0),
            "product_O": feat["product_domain_sites"].get("aryl_O_candidate", 0),
            "old_exact": ",".join(row["crosswalk"]["old_exact_ids"]),
            "old_cas": ",".join(row["crosswalk"]["old_cas_reaction_ids"]),
            "card_exact_or_cas": ",".join(row["crosswalk"]["card_exact_or_cas_ids"]),
            "card_reference_only": ",".join(row["crosswalk"]["card_reference_only_ids"]),
            "issues": len(row["issues"]), "id": row["id"],
        })
    write(TASK, str(tsv.relative_to(ROOT)), stream.getvalue())
    output_manifest = {"input": [{k: v for k, v in f.items() if k != "counts"} for f in manifest], "output": {p.name: sha(p) for p in (OUTPUT / "records.jsonl", OUTPUT / "summary.json", tsv)}}
    write(TASK, str((OUTPUT / "manifest.json").relative_to(ROOT)), json.dumps(output_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "unique_card_reference_only_ids"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
