"""Freeze bounded official full-text/SI sources; metadata never counts as an experiment."""
import json, sys, hashlib, xml.etree.ElementTree as ET, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.operate import write, event
from flavoretro.open_reactions import freeze_download

root = Path(__file__).resolve().parents[1]
base = root / "data/raw/task016/europepmc/2026-10-06/retry"
manifest = []
for pmcid in ["PMC6139687", "PMC6036675"]:
    rows = freeze_download(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", base, pmcid)
    for row in rows:
        row.update(provider="EuropePMC", record_id=pmcid, content_role="fullTextXML")
        if row["status"] == "raw_available":
            try:
                xml = ET.parse(row["path"]).getroot()
                license_el = xml.find(".//license")
                row.update(parse_status="parsed", license="".join(license_el.itertext()) if license_el is not None else None)
            except ET.ParseError as exc:
                row.update(parse_status="parse_failed", error=str(exc))
        event("TASK-016", "open_download", **row)
        manifest.append(row)
for pmcid in ["PMC6139687", "PMC5818429", "PMC5897352"]:
    rows = freeze_download(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles", base, pmcid + "-si")
    for row in rows:
        row.update(provider="EuropePMC", record_id=pmcid, content_role="supplementaryFiles")
        if row["status"] == "raw_available":
            try:
                with zipfile.ZipFile(row["path"]) as z:
                    row["members"] = [{"name": i.filename, "bytes": i.file_size} for i in z.infolist()]
                row["parse_status"] = "archive_verified"
            except zipfile.BadZipFile:
                row.update(parse_status="parse_failed", error="response is not a ZIP archive")
        event("TASK-016", "open_download", **row)
        manifest.append(row)
write("TASK-016", "outputs/task016/v1/acquisition_attempts.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print(json.dumps([{k: r.get(k) for k in ["record_id", "content_role", "status_code", "status", "parse_status", "bytes", "members"]} for r in manifest], ensure_ascii=False, indent=2))
