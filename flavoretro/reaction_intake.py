"""Loss-preserving intake of newly located literature reactions.

A verifiable excerpt and parsable structure are separate checks. Neither proves
experimental reproducibility, name-to-structure identity, or template transfer.
This layer never changes the active v3 database, stock, or runtime libraries.
"""
from __future__ import annotations
from collections import Counter
import copy
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from rdkit import Chem
from .resources import sha, dumps
from .workspace import root, AssetError

POINTER = "outputs/task022/intake/current.json"
BOUNDARY = "原文定位、数据库结构和代理审核分别记录；非独立化学验证，未自动接入搜索或库存。"


def local_path(value, workspace=None):
    workspace = Path(workspace or root()).resolve()
    p = Path(value)
    p = (workspace / p).resolve() if not p.is_absolute() else p.resolve()
    if not p.is_relative_to(workspace):
        raise ValueError("evidence path outside workspace")
    return p


def normalized_text(value):
    return re.sub(r"\s+", " ", value).strip()


def document_text(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".xml", ".nxml"}:
        return " ".join(ET.fromstring(text).itertext())
    return text


def canonical_side(participants):
    values, issues = [], []
    if not isinstance(participants, list) or not participants:
        return None, ["participants_missing"]
    for index, participant in enumerate(participants):
        if not isinstance(participant, dict):
            issues.append(f"participant_{index}_invalid")
            continue
        raw = participant.get("smiles")
        mol = Chem.MolFromSmiles(raw) if isinstance(raw, str) and raw else None
        if mol is None or not mol.GetNumAtoms() or any(a.GetAtomicNum() == 0 or a.GetNumRadicalElectrons() for a in mol.GetAtoms()):
            issues.append(f"participant_{index}_structure_missing_or_invalid")
            continue
        if not participant.get("identity_source"):
            issues.append(f"participant_{index}_identity_source_missing")
        if participant.get("inferred") or participant.get("structure_origin") in {"model_memory", "handwritten_from_name"}:
            issues.append(f"participant_{index}_inferred_structure")
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(0)
        values.append(Chem.MolToSmiles(mol, isomericSmiles=True))
    return ".".join(sorted(values)) if len(values) == len(participants) else None, issues


def assess(record, workspace=None):
    row = copy.deepcopy(record)
    issues = []
    source = row.get("source") or {}
    source_ok = quote_ok = False
    if not row.get("reaction_id"):
        issues.append("reaction_id_missing")
    if not isinstance(source, dict):
        source = {}
        issues.append("source_invalid")
    if not (source.get("doi") or source.get("accession")) or not source.get("url"):
        issues.append("source_identifier_or_url_missing")
    try:
        path = local_path(source["local_path"], workspace)
        source_ok = path.is_file() and sha(path) == source["sha256"]
        if not source_ok:
            issues.append("source_bytes_missing_or_drift")
        else:
            # Binary source (e.g. PDF) may bind a separately frozen extraction.
            text_path = path
            if source.get("text_path"):
                text_path = local_path(source["text_path"], workspace)
                if sha(text_path) != source.get("text_sha256"):
                    raise ValueError("extracted text hash drift")
            quote = source.get("quote")
            quote_ok = bool(quote and source.get("locator") and normalized_text(quote) in normalized_text(document_text(text_path)))
            if not quote_ok:
                issues.append("quote_or_locator_not_verified")
    except (OSError, ValueError, KeyError, UnicodeError, ET.ParseError, TypeError):
        issues.append("source_binding_unavailable")
    left, left_issues = canonical_side(row.get("reactants"))
    right, right_issues = canonical_side(row.get("products"))
    issues.extend("reactants_" + x for x in left_issues)
    issues.extend("products_" + x for x in right_issues)
    if left and right and left == right:
        issues.append("unchanged_reaction")
    value = row.get("yield_value")
    if value is not None:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            issues.append("yield_invalid_numeric")
        elif value < 0 or (row.get("yield_unit") in {"%", "percent"} and value > 100):
            issues.append("yield_out_of_range")
        if not row.get("yield_unit"):
            issues.append("yield_unit_missing")
    if row.get("human_reviewed") is True or row.get("independent_chemical_validation") is True:
        issues.append("unsupported_evidence_promotion")
    # Preserve the submitted fields even when they conflict; computed decisions
    # live in qc, avoiding silent replacement of source claims.
    row["qc"] = {
        "source_bytes_verified": source_ok,
        "quote_located": quote_ok,
        "structures_parseable": bool(left and right),
        "identity_sources_supplied": bool(row.get("reactants") and row.get("products")) and all(isinstance(p, dict) and p.get("identity_source") for p in row.get("reactants", []) + row.get("products", [])),
        "identity_independently_verified": False,
        "reaction_signature": left + ">>" + right if left and right else None,
        "issues": sorted(set(issues)),
        "status": "source_bound_structure_candidate" if not issues else "retained_with_issues",
        "yield_is_missing": value is None and row.get("yield_status") not in {"trace", "qualitative", "reported_unparsed"},
        "yield_is_zero": value == 0 if value is not None and not isinstance(value, bool) else False,
        "runtime_admitted": False,
        "independent_chemical_validation": False,
        "human_reviewed": False,
        "boundary": BOUNDARY,
    }
    return row


def build(input_path, output_dir, workspace=None):
    """Build a new immutable snapshot, preserving every submitted record."""
    workspace = Path(workspace or root()).resolve()
    input_path = local_path(input_path, workspace)
    output_dir = local_path(output_dir, workspace)
    if output_dir.exists():
        raise ValueError("intake snapshot already exists")
    payload = json.loads(input_path.read_text())
    inputs = payload["records"]
    if not isinstance(inputs, list):
        raise ValueError("records must be a list")
    records = [assess(item, workspace) for item in inputs]
    ids = Counter(row.get("reaction_id") for row in records)
    signatures = Counter(row["qc"]["reaction_signature"] for row in records if row["qc"]["reaction_signature"])
    for row in records:
        row["qc"]["duplicate_reaction_signature"] = bool(signatures[row["qc"]["reaction_signature"]] > 1)
        if ids[row.get("reaction_id")] > 1:
            row["qc"]["issues"].append("duplicate_reaction_id")
            row["qc"]["status"] = "retained_with_issues"
    summary = {"total": len(records), "by_status": dict(Counter(r["qc"]["status"] for r in records)),
               "sources": len({identifier for r in records if (identifier := ((r.get("source") or {}).get("doi") or (r.get("source") or {}).get("accession")))}),
               "zero_yields": sum(r["qc"]["yield_is_zero"] for r in records),
               "missing_yields": sum(r["qc"]["yield_is_missing"] for r in records),
               "runtime_admitted": 0, "independent_chemical_validated": 0}
    source_assets = {}
    for row in records:
        source = row.get("source") or {}
        for path_key, hash_key in (("local_path", "sha256"), ("text_path", "text_sha256")):
            try:
                path = local_path(source[path_key], workspace)
                if path.is_file() and sha(path) == source.get(hash_key):
                    source_assets[str(path.relative_to(workspace))] = source[hash_key]
            except (ValueError, KeyError, OSError, TypeError):
                pass  # A retained QC issue is not a successfully bound asset.
    output_dir.mkdir(parents=True)
    (output_dir / "records.json").write_text(dumps(records))
    manifest = {"schema": 1, "input_path": str(input_path.relative_to(workspace)), "input_sha256": sha(input_path),
                "records_sha256": sha(output_dir / "records.json"), "summary": summary, "source_assets": source_assets,
                "boundary": BOUNDARY}
    (output_dir / "manifest.json").write_text(dumps(manifest))
    return manifest


def query(q="", status="", offset=0, limit=25):
    if offset < 0 or not 1 <= limit <= 100 or len(q) > 500:
        raise ValueError("invalid reaction evidence pagination/query")
    pointer = root() / POINTER
    if not pointer.exists():
        return {"status": "not_built", "total": 0, "records": [], "summary": {"total": 0}, "boundary": BOUNDARY}
    binding = json.loads(pointer.read_text())
    path = local_path(binding["manifest"])
    if sha(path) != binding["manifest_sha256"]:
        raise AssetError("reaction intake manifest drift")
    manifest = json.loads(path.read_text())
    for rel, expected in manifest.get("source_assets", {}).items():
        source_path = local_path(rel)
        if not source_path.is_file() or sha(source_path) != expected:
            raise AssetError("reaction intake source drift: " + rel)
    record_path = path.parent / "records.json"
    if sha(record_path) != manifest["records_sha256"]:
        raise AssetError("reaction intake records drift")
    records = json.loads(record_path.read_text())
    selected = [r for r in records if (not status or r["qc"]["status"] == status)
                and (not q or q.casefold() in json.dumps(r, ensure_ascii=False).casefold())]
    return {"status": "available", "total": len(selected), "records": selected[offset:offset + limit],
            "summary": manifest["summary"], "manifest_sha256": binding["manifest_sha256"], "boundary": BOUNDARY}
