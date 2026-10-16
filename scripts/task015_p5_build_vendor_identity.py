# -*- coding: utf-8 -*-
"""TASK-015-P5 阶段 D1：49 库存 + 2 模板身份审核包 + 22 历史供应商上下文。

输入（只读）：data/derived/v3/records.json。
输出：outputs/evidence/task015-p5-vendor/{identity_packets.jsonl, identity_review.tsv,
suppliers_historical.json, manifest.json}
"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data/derived/v3/records.json"
OUT = ROOT / "outputs/evidence/task015-p5-vendor"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    recs = json.loads(RECORDS.read_text(encoding="utf-8"))
    stocks = sorted([r for r in recs if r["kind"] == "stock"], key=lambda r: (r.get("raw") or {}).get("stock_id") or r["id"])
    templates = sorted([r for r in recs if r["kind"] == "template"], key=lambda r: r["id"])
    suppliers = sorted([r for r in recs if r["kind"] == "supplier"], key=lambda r: r["id"])

    packets = []
    for r in stocks:
        raw = r.get("raw") or {}
        ev = (raw.get("evidence") or [{}])
        pub = next((e for e in ev if e.get("source_type") == "pubchem_identity"), {}) if isinstance(ev, list) else {}
        packets.append({
            "record_id": r["id"], "kind": "stock",
            "ref": raw.get("stock_id"), "name": raw.get("name"),
            "role": raw.get("role"),
            "canonical_smiles": raw.get("smiles"),
            "inchikey": raw.get("inchikey") or (r.get("structure") or {}).get("inchikey"),
            "structure_inchikey": (r.get("structure") or {}).get("inchikey"),
            "promotion_status": raw.get("promotion_status"),
            "promotion_blockers": raw.get("promotion_blockers"),
            "source_layer": raw.get("source_layer"),
            "legacy_metadata": raw.get("legacy_metadata"),
            "identity_evidence": pub,
            "source_status": r.get("source_status"),
            "human_review_status": r.get("human_review_status"),
            "review_status": r.get("review_status"),
            "decision": r.get("decision"),
        })
    for r in templates:
        raw = r.get("raw") or {}
        packets.append({
            "record_id": r["id"], "kind": "template",
            "ref": raw.get("template_id"), "aliases": raw.get("aliases"),
            "reaction_family": raw.get("reaction_family"),
            "template_kind": raw.get("template_kind"),
            "canonical_retro_smarts": raw.get("canonical_retro_smarts"),
            "conditions": raw.get("conditions"),
            "evidence": raw.get("evidence"),
            "deployment_scope": raw.get("deployment_scope"),
            "promotion_status": raw.get("promotion_status"),
            "source_status": r.get("source_status"),
            "human_review_status": r.get("human_review_status"),
            "decision": r.get("decision"),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "identity_packets.jsonl").write_text(
        "".join(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n" for p in packets), encoding="utf-8")

    sup_ctx = []
    for r in suppliers:
        raw = r.get("raw") or {}
        sup_ctx.append({
            "record_id": r["id"], "substance_query": raw.get("substance_query"),
            "cas_rns": raw.get("cas_rns"), "distributor_count": raw.get("distributor_count"),
            "listing_count": raw.get("listing_count"),
            "in_stock_listings": raw.get("in_stock_listings"),
            "evidence_status": raw.get("evidence_status"),
            "source_file": raw.get("source_file"),
            "note": "historical_listing_not_current_supply；仅作 D2 核查的起点线索",
        })
    (OUT / "suppliers_historical.json").write_text(
        json.dumps(sup_ctx, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    with open(OUT / "identity_review.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["kind", "ref", "name_or_alias", "inchikey", "canonical_smiles_or_smarts",
                    "identity_evidence", "promotion_status",
                    "owner_identity_confirmed(yes/rename/reject)", "owner_notes"])
        for p in packets:
            if p["kind"] == "stock":
                pub = p.get("identity_evidence") or {}
                ev = f"PubChem CID {pub.get('source_id', '')} {pub.get('source_url', '')}"
                smi = p.get("canonical_smiles") or ""
                w.writerow(["stock", p.get("ref"), p.get("name"), p.get("inchikey"), smi,
                            ev, p.get("promotion_status"), "", ""])
            else:
                evs = p.get("evidence") or []
                ev = "; ".join(f"DOI {e.get('doi')} manual_review={e.get('manual_primary_source_review')}" for e in evs if isinstance(e, dict))
                w.writerow(["template", p.get("ref"), ";".join(p.get("aliases") or []),
                            "", p.get("canonical_retro_smarts") or "",
                            ev, p.get("promotion_status"), "", ""])

    manifest = {
        "task": "TASK-015-P5-D1",
        "inputs_sha256": {str(RECORDS.relative_to(ROOT)): sha(RECORDS)},
        "outputs_sha256": {f.name: sha(f) for f in sorted(OUT.iterdir()) if f.is_file() and f.name != "manifest.json"},
        "counts": {"stocks": len(stocks), "templates": len(templates), "suppliers_historical": len(sup_ctx)},
        "boundary": "identity packets only; no current_vendor_evidence claim; no human_reviewed filled",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("counts",)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
