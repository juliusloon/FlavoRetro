"""Immutable, axis-specific review views. Review evidence never certifies a route."""
import argparse
import json
import os
from collections import Counter
from pathlib import Path
from rdkit import Chem, rdBase
from .resources import dumps, sha
from .workspace import root, active_data, config, configure, AssetError

SCHEMA = 1
PINS = {
    "outputs/review/task015-p3/gold-v1/manifest.json": "91ba607d1ec65047f495a322c0d25a6b7e5def154894b0ec8fe7a312087c712b",
    "outputs/triage/task015-p4-v2/manifest.json": "1f27b28c55d807f127591620a1680e2ae208e28c70ecea7c23033e8dca8cb993",
    "outputs/evidence/task015-p5-final-v1/manifest.json": "9f3e7ac254b54241d8409fc7e2edc01d5754e68b3e7e3e14b3a69f9826331a88",
}
BLOCKED = {"blocked_source_blacklist", "incomplete_record", "pathway_suspect"}
_CACHE = {}


def local_path(name):
    p = (root() / name).resolve()
    if not p.is_relative_to(root()):
        raise AssetError("review_path_outside_workspace")
    return p


def jsonl(p):
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def canonical_side(smiles):
    pieces = []
    for value in smiles:
        mol = Chem.MolFromSmiles(value)
        if mol is None or any(a.GetAtomicNum() == 0 for a in mol.GetAtoms()):
            return None
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(0)
        pieces.extend(Chem.MolToSmiles(mol, isomericSmiles=True).split("."))
    return ".".join(sorted(pieces)) or None


def reaction_signature(reactants, products):
    left, right = canonical_side(reactants), canonical_side(products)
    return left + ">>" + right if left and right else None


def row_signature(row):
    sides = {"reactant": [], "product": []}
    for c in row.get("components", []):
        if c.get("role") not in sides or c.get("structure", {}).get("status") != "parsed":
            return None
        sides[c["role"]].append(c["structure"]["canonical_smiles"])
    return reaction_signature(sides["reactant"], sides["product"])


def bind_inputs():
    paths = {}
    for name, expected in PINS.items():
        p = local_path(name)
        if sha(p) != expected:
            raise AssetError("review_input_manifest_drift: " + name)
        paths[name] = expected
        m = json.loads(p.read_text())
        payloads = m.get("payload_sha256", m.get("outputs_sha256", {}))
        for filename, digest in payloads.items():
            q = local_path(filename) if "/" in filename else p.parent / filename
            if sha(q) != digest:
                raise AssetError("review_input_payload_drift: " + str(q))
            paths[str(q.relative_to(root()))] = digest
    return paths


def assemble(rows, axes, notes, identities, vendors, names, pilot):
    byid = {r["id"]: r for r in rows}
    if len(byid) != len(rows):
        raise AssetError("duplicate_resource_ids")
    reviews = {rid: {"record_id": rid, "status": "no_specific_review", "axes": {},
                        "positive_source_support": False, "split": "development_exposed",
                        "source_ref": {"path": r["source_path"], "sha256": r["source_sha256"], "locator": r["locator"]}}
               for rid, r in byid.items()}
    for p in pilot:
        rid = p["id"]
        if rid not in byid or p["input_record"]["source_sha256"] != byid[rid]["source_sha256"]:
            raise AssetError("triage_crosswalk_mismatch")
        reviews[rid]["axes"]["record_disposition"] = p["queue"]
    for a in axes:
        rid = a["id"]
        if rid not in byid or a["source_sha256"] != byid[rid]["source_sha256"]:
            raise AssetError("card_crosswalk_mismatch")
        review = reviews[rid]
        review["card_number"] = a["card_number"]
        review["reviewer_type"] = a["reviewer_type"]
        review["decision_authority"] = a["decision_authority"]
        review["owner_adopted_conclusions"] = a["owner_adopted_conclusions"]
        review["structure_review_provenance"] = (a.get("structure_gold") or {}).get("structure_axis_provenance")
        review["previous_owner_review"] = a.get("previous_owner_review")
        review["axes"].update(structure_classification=a["structure_decision"],
                              primary_source=a["source_final_status"], yield_status=a["yield_final"]["final_status"])
        review["source_instance_evidence"] = a["source_evidence"]
        review["source_instance_yield"] = a["yield_final"]
        review["structure_labels"] = (a.get("structure_gold") or {}).get("labels", {})
        review["positive_source_support"] = bool(a["primary_source_supported"] and
            a["structure_decision"] != "excluded" and review["axes"].get("record_disposition") not in BLOCKED)
    for n in notes:
        rid = n["id"]
        if rid not in byid or byid[rid]["kind"] != "note_reaction":
            raise AssetError("note_crosswalk_mismatch")
        reviews[rid]["axes"]["note_locator"] = n["final_decision"]
        reviews[rid]["reviewer_type"] = n["reviewer_type"]
        reviews[rid]["note_is_primary_experimental_evidence"] = False
    stock_refs = {r["raw"]["stock_id"]: r["id"] for r in rows if r["kind"] == "stock"}
    for i in identities:
        rid = i["record_id"]
        if rid not in byid or byid[rid]["kind"] != i["kind"]:
            raise AssetError("identity_crosswalk_mismatch")
        row = byid[rid]
        ref = row["raw"].get("stock_id", row["raw"].get("template_id"))
        if ref != i["ref"] or (i["kind"] == "stock" and row["structure"]["inchikey"] != i["computed_inchikey"]):
            raise AssetError("identity_structure_mismatch")
        reviews[rid]["axes"]["identity"] = i["final_decision"]
        reviews[rid]["identity_reason"] = i["reason"]
        reviews[rid]["reviewer_type"] = i["reviewer_type"]
        reviews[rid]["decision_authority"] = i["decision_authority"]
    for v in vendors:
        rid = stock_refs.get(v["stock_ref"])
        if rid is None:
            raise AssetError("vendor_crosswalk_mismatch")
        reviews[rid]["axes"]["current_vendor"] = v["final_decision"]
        reviews[rid]["current_exact_supply_verified"] = v["current_exact_supply_verified"]
        reviews[rid]["vendor_reason"] = v["reason"]
    fgm = {r["raw"]["molecule_id"]: r["id"] for r in rows if r["kind"] in {"molecule", "molecule_duplicate_names"}}
    for group in names:
        for fid in group["record_ids"]:
            rid = fgm.get(fid)
            if rid is None:
                raise AssetError("name_crosswalk_mismatch")
            reviews[rid]["fgm_id"] = fid
            reviews[rid]["axes"]["identity"] = group["final_decision"]
            reviews[rid]["identity_reason"] = group["reason"]
            reviews[rid]["canonical_display_name"] = group["details"].get("canonical_name")
    stock, exact = {}, {}
    for rid, row in byid.items():
        review = reviews[rid]
        if review["axes"]:
            review["status"] = "reviewed_axes_only"
        if row["kind"] == "stock":
            quarantined = review["axes"].get("identity", "").startswith("quarantine")
            allowed = bool(row.get("runtime_candidate_allowed") and not quarantined)
            review["original_runtime_candidate_allowed"] = row.get("runtime_candidate_allowed", False)
            review["effective_runtime_candidate_allowed"] = allowed
            key = row["structure"]["inchikey"]
            stock.setdefault(key, []).append({"record_id": rid, "name": row["raw"]["name"],
                "canonical_smiles": row["structure"]["canonical_smiles"], "allowed": allowed,
                "original_allowed": row.get("runtime_candidate_allowed", False), "review": review})
        signature = row_signature(row) if row.get("components") else None
        if review["axes"].get("note_locator", "").startswith("exclude_exact_reaction"):
            signature = None
        review["exact_signature_status"] = "available" if signature else "not_applicable_or_unparseable"
        if signature:
            exact.setdefault(signature, []).append(rid)
    summary = {"records": len(rows), "cards": len(axes), "notes": len(notes),
        "identity_records": len(identities), "vendor_records": len(vendors), "name_groups": len(names),
        "triage_records": len(pilot), "structure_gold": sum(a["structure_decision"] == "development_gold" for a in axes),
        "excluded_cards": sum(a["structure_decision"] == "excluded" for a in axes),
        "primary_supported_cards": sum(a["primary_source_supported"] for a in axes),
        "numeric_supported_cards": sum(a["numeric_yield_supported"] for a in axes),
        "original_stock_keys": sum(any(x["original_allowed"] for x in group) for group in stock.values()),
        "eligible_stock_keys": sum(any(x["allowed"] for x in group) for group in stock.values()),
        "quarantined_stock_records": sum(i["final_decision"].startswith("quarantine") for i in identities if i["kind"] == "stock"),
        "current_exact_supply_supported": sum(v["current_exact_supply_verified"] for v in vendors),
        "exact_reaction_groups": len(exact), "source_positive_indexed_records": sum(reviews[rid]["positive_source_support"] for ids in exact.values() for rid in ids),
        "triage_dispositions": dict(Counter(p["queue"] for p in pilot)), "note_dispositions": dict(Counter(n["final_decision"] for n in notes)),
        "new_human_reviews": 0, "production_records": 0, "blind_records": 0}
    return {"records": reviews, "stock": stock, "exact_reactions": exact, "summary": summary}


def build(destination):
    if rdBase.rdkitVersion != "2023.09.6":
        raise AssetError("review_builder_rdkit_version_mismatch")
    dest = local_path(destination)
    if dest.exists():
        raise AssetError("review_destination_exists: retain immutable version")
    inputs = bind_inputs()
    folder, m, pointer = active_data()
    if pointer["version"] != "v3":
        raise AssetError("review_builder_requires_frozen_v3")
    rows = json.loads((folder / "records.json").read_text())
    p5 = root() / "outputs/evidence/task015-p5-final-v1"
    data = assemble(rows, jsonl(p5 / "axes-final-60.jsonl"), jsonl(p5 / "notes-final-508.jsonl"),
        jsonl(p5 / "identity-final-51.jsonl"), jsonl(p5 / "vendor-final-49.jsonl"),
        json.loads((p5 / "name-decisions.json").read_text()), jsonl(root() / "outputs/triage/task015-p4-v2/pilot.jsonl"))
    expected = {"records": 3059, "cards": 60, "notes": 508, "identity_records": 51,
        "vendor_records": 49, "name_groups": 2, "triage_records": 2301, "structure_gold": 53,
        "excluded_cards": 7, "primary_supported_cards": 9, "numeric_supported_cards": 6,
        "original_stock_keys": 17, "eligible_stock_keys": 17, "quarantined_stock_records": 4,
        "current_exact_supply_supported": 0}
    if any(data["summary"][k] != value for k, value in expected.items()):
        raise AssetError("review_count_universe_mismatch: " + dumps(data["summary"]))
    dest.mkdir(parents=True)
    (dest / "index.json").write_text(dumps(data))
    (dest / "summary.json").write_text(dumps(data["summary"]))
    (dest / "README.md").write_text("# 审核搜索视图 v1\n外置、分轴、development_exposed；原件保留。17候选库存键，0当前精确供应认证；索引匹配不认证新预测或路线。\n")
    manifest = {"schema_version": SCHEMA, "version": "task015-06-v1", "rdkit_version": rdBase.rdkitVersion,
        "base_resource_version": pointer["version"], "base_manifest_sha256": pointer["manifest_sha256"],
        "records_sha256": m["records_sha256"], "sources_sha256": m["sources_sha256"],
        "inputs_sha256": inputs, "builder_sha256": sha(__file__),
        "payload_sha256": {p.name: sha(p) for p in dest.iterdir()}, "summary": data["summary"]}
    (dest / "manifest.json").write_text(dumps(manifest))
    for p in dest.iterdir():
        p.chmod(0o444)
    return manifest


class ReviewView:
    def __init__(self, data, binding):
        self.data, self.binding = data, binding
        self.legacy = binding.get("mode") == "legacy_validation"
        self.keys = {key for key, group in data["stock"].items()
                     if any(x["original_allowed"] if self.legacy else x["allowed"] for x in group)}

    def record(self, rid):
        return {**self.data["records"].get(rid, {"record_id": rid, "status": "no_specific_review", "axes": {}}),
                "review_version": self.binding["version"]}

    def reaction(self, reactants, products):
        signature = reaction_signature(reactants, products)
        ids = self.data["exact_reactions"].get(signature, []) if signature else []
        return {"status": "legacy_validation" if self.legacy else ("exact_match" if ids else "unmatched"),
                "review_version": self.binding["version"], "record_ids": ids if not self.legacy else [],
                "evidence": [self.record(rid) for rid in ids] if not self.legacy else [],
                "source_instance_supported": bool(not self.legacy and any(self.data["records"][rid]["positive_source_support"] for rid in ids)),
                "prediction_conditions_verified": False, "actionable": False}

    def leaf(self, smiles):
        mol = Chem.MolFromSmiles(smiles)
        key = Chem.MolToInchiKey(mol) if mol else None
        canonical = canonical_side([smiles])
        group = [x for x in self.data["stock"].get(key, []) if canonical_side([x["canonical_smiles"]]) == canonical]
        return {"review_version": self.binding["version"], "status": "legacy_validation" if self.legacy else ("stock_records_matched" if group else "no_stock_match"),
                "stock_records": group if not self.legacy else [], "current_exact_supply_verified": False,
                "evidence_closed": False, "actionable": False}


def load_review(expected=None):
    try:
        settings = config("search.json").get("reviewed_resources", {})
        path = local_path(settings["manifest"])
        digest = sha(path)
        if digest != settings["manifest_sha256"]:
            raise AssetError("review_manifest_integrity_failed")
        m = json.loads(path.read_text())
        if type(m["schema_version"]) is not int or m["schema_version"] != SCHEMA or m["rdkit_version"] != rdBase.rdkitVersion:
            raise AssetError("review_schema_or_rdkit_mismatch")
        _, base, pointer = active_data()
        if (m["base_resource_version"] != pointer["version"] or m["base_manifest_sha256"] != pointer["manifest_sha256"]
            or m["records_sha256"] != base["records_sha256"] or m["sources_sha256"] != base["sources_sha256"]):
            raise AssetError("review_base_resource_mismatch")
        for filename, value in m["payload_sha256"].items():
            p = local_path(str(path.parent.relative_to(root()) / filename))
            if sha(p) != value:
                raise AssetError("review_payload_integrity_failed")
        for name, value in m["inputs_sha256"].items():
            if sha(local_path(name)) != value:
                raise AssetError("review_frozen_input_drift: " + name)
        mode = "legacy_validation" if os.environ.get("FLAVORETRO_REVIEW_VALIDATION_LEGACY") == "1" else "adjudicated"
        binding = {"schema_version": SCHEMA, "version": m["version"], "manifest_sha256": digest,
            "index_sha256": m["payload_sha256"]["index.json"], "mode": mode, "summary": m["summary"]}
        if expected is not None and binding != expected:
            raise AssetError("review_binding_changed_during_run")
        cache_key = (str(path), digest, binding["index_sha256"], mode)
        if cache_key not in _CACHE:
            _CACHE[cache_key] = ReviewView(json.loads((path.parent / "index.json").read_text()), binding)
        return _CACHE[cache_key]
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
        raise AssetError("missing_or_invalid_review_assets: restore frozen review bundle and config") from exc


def reviewed_query(result):
    if not result["records"]:
        return result
    review = load_review()
    return {**result, "review_binding": review.binding,
            "records": [{**r, "review": review.record(r["id"])} for r in result["records"]]}


def main():
    parser = argparse.ArgumentParser(description="Build immutable TASK-015-06 review view")
    parser.add_argument("--workspace")
    parser.add_argument("--build", required=True)
    args = parser.parse_args()
    configure(args.workspace)
    print(dumps(build(args.build)["summary"]))


if __name__ == "__main__":
    main()
