"""Open-source snapshots and strict structures; database records are not experiments."""
import csv
import hashlib
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from datetime import datetime, timezone
from rdkit import Chem
from .reviewed_resources import canonical_side, reaction_signature


def freeze_download(url, folder, name, *, limit=25 * 1024**2, attempts=2):
    """Bounded public GET; preserve each failure, never overwrite a snapshot."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    history = []
    for attempt in range(1, attempts + 1):
        path = folder / f"{name}.attempt-{attempt}"
        if path.exists():
            raise ValueError("snapshot already exists")
        status, error, data = None, None, b""
        try:
            with urlopen(Request(url, headers={"User-Agent": "FlavoRetro-TASK016/0.1"}), timeout=25) as response:
                status = response.status
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError("per-file acquisition budget exceeded")
        except HTTPError as exc:
            status, error = exc.code, str(exc)
            data = exc.read(limit)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        path.write_bytes(data)
        row = dict(url=url, path=str(path), status_code=status, error=error,
                   bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                   acquired_at=datetime.now(timezone.utc).isoformat(), attempt=attempt,
                   status="raw_available" if status == 200 and not error else "unavailable")
        history.append(row)
        if row["status"] == "raw_available" or status in (400, 401, 403, 404):
            break
        if attempt < attempts:
            time.sleep(1)
    return history


def concrete_side(raw):
    values = canonical_side(raw.split("."))
    if not values:
        raise ValueError("invalid or generic reaction participants")
    return values.split(".")


def rhea_rows(query_file, directions_file, smiles_file):
    directions = {r[key]: r for r in csv.DictReader(Path(directions_file).open(), delimiter="\t")
                  for key in ("RHEA_ID_MASTER", "RHEA_ID_LR", "RHEA_ID_RL", "RHEA_ID_BI")}
    smiles = dict(line.split("\t", 1) for line in Path(smiles_file).read_text().splitlines())
    for raw in csv.DictReader(Path(query_file).open(), delimiter="\t"):
        identifier = raw["Reaction identifier"].split(":")[1]
        row = dict(provider="Rhea", record_id="RHEA:" + identifier, raw=raw,
                   record_type="curated_reaction_knowledge", review_type="machine_parsed",
                   license="CC-BY-4.0", conditions=None, yield_value=None,
                   conditions_status="not_reported_in_database", yield_status="not_reported_in_database",
                   catalyst_mode="enzymatic", direction_evidence="Rhea official LR mapping, not an experimental observation")
        try:
            mapping = directions[identifier]
            row.update(master_id=mapping["RHEA_ID_MASTER"], lr_id=mapping["RHEA_ID_LR"])
            row["raw_reaction_smiles"] = smiles[row["lr_id"]]
            left, right = row["raw_reaction_smiles"].split(">>")
            row.update(reactants=concrete_side(left), products=concrete_side(right), parse_status="parsed")
            row["strict_source_signature"] = reaction_signature(row["reactants"], row["products"])
        except Exception as exc:
            row.update(parse_status="parse_failed", error=f"{type(exc).__name__}: {exc}")
        yield row


def paragraphs(xml_root):
    """Locators remain deterministic for the frozen JATS bytes."""
    for index, element in enumerate(xml_root.findall(".//body//p")):
        yield {"locator": f"body//p[{index + 1}]", "text": "".join(element.itertext())}
