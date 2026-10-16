"""Verify claimed source identity against independently acquired authoritative metadata."""
from __future__ import annotations

import html
import re
import unicodedata
import xml.etree.ElementTree as ET

from scripts.task016_p7_orchestrate import ContractError, ROOT, require_fields, sha_file, sha_json

IDENTITY_FIELDS = ("pmcid","pmid","doi","title","journal","year","volume","pages","article_number","publisher")
AUTHORITIES = {"PMC JATS", "PMC authoritative metadata", "publisher metadata", "Crossref", "Europe PMC"}


def normalize(value):
    if value is None or value=="":
        return None
    value = re.sub("<[^>]+>","",html.unescape(str(value)))
    return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",value)).strip().casefold()


def normalize_field(value, field):
    normalized = normalize(value)
    if field == "title" and normalized is not None:
        normalized = "".join("-" if unicodedata.category(character)=="Pd" else character for character in normalized)
    if field == "title" and normalized is not None and normalized.endswith("."):
        normalized = normalized[:-1].rstrip()
    return normalized


def verify_identity(claim, authoritative_records, *, root=ROOT, validate_files=True):
    if not isinstance(claim, dict):
        raise ContractError("source claim must be object")
    if not authoritative_records:
        raise ContractError("source hint/HTTP status is not identity evidence")
    field_values = {field: [] for field in IDENTITY_FIELDS}
    pointers = []
    for row in authoritative_records:
        require_fields(row, ("provider","authoritative","metadata","evidence_pointer"))
        if row["provider"] not in AUTHORITIES or row["authoritative"] is not True:
            raise ContractError("identity authority not approved")
        pointer = row["evidence_pointer"]
        require_fields(pointer,("path","sha256"))
        if validate_files and (not (root/pointer["path"]).is_file() or
                               sha_file(root/pointer["path"])!=pointer["sha256"]):
            raise ContractError("authoritative metadata SHA mismatch")
        pointers.append(pointer)
        metadata = row["metadata"]
        if not isinstance(metadata,dict):
            raise ContractError("metadata must be object")
        for field in IDENTITY_FIELDS:
            if normalize(metadata.get(field)) is not None:
                field_values[field].append((row["provider"],metadata[field]))
    if not field_values["title"] or not field_values["journal"] or not field_values["year"]:
        raise ContractError("identity lacks authoritative title/journal/year")
    if not any(field_values[field] for field in ("pmcid","pmid","doi")):
        raise ContractError("identity lacks authoritative identifier")
    checks = {}
    conflicts = []
    missing = []
    for field, values in field_values.items():
        raw_claim = claim.get(field)
        observations = [dict(provider=provider,value=value) for provider,value in values]
        known = {normalize_field(value,field) for _,value in values}
        if normalize(raw_claim) is not None:
            known.add(normalize_field(raw_claim,field))
        if len(known)>1:
            conflicts.append(field)
        if not values:
            missing.append(field)
        checks[field] = dict(claim=raw_claim,authoritative_values=observations,
                             comparison_rule="normalize html/unicode/whitespace/case; Unicode Pd hyphens equal ASCII hyphen; strip one terminal period" if field=="title" else "normalize html/unicode/whitespace/case; preserve punctuation",
                             status="conflict" if len(known)>1 else "missing" if not values else "consistent")
    verified = not conflicts
    return dict(source_identity_verified=verified,evidence_eligible=verified,
                chemical_claim_evidence_eligible=False,status="verified" if verified else "unresolved",
                conflict_fields=conflicts,missing_fields=missing,field_checks=checks,
                authoritative_evidence_pointers=pointers,input_sha=sha_json(
                    dict(claim=claim,authoritative_records=authoritative_records)),
                human_reviewed=False,agent_role="A3 Source Identity Verifier")


def parse_jats(path, pointer):
    root = ET.parse(path).getroot()
    def text_at(expression):
        node=root.find(expression)
        return "".join(node.itertext()).strip() if node is not None else None
    metadata={}
    for node in root.findall(".//article-meta/article-id"):
        field={"pmc":"pmcid","pmcid":"pmcid","pmid":"pmid","doi":"doi"}.get(node.get("pub-id-type"))
        if field:
            value="".join(node.itertext()).strip()
            metadata[field]=("PMC"+value if field=="pmcid" and not value.upper().startswith("PMC") else value)
    metadata.update(title=text_at(".//article-meta/title-group/article-title"),
                    journal=text_at(".//journal-meta/journal-title-group/journal-title"),
                    year=text_at(".//article-meta/pub-date/year"),
                    volume=text_at(".//article-meta/volume"),
                    publisher=text_at(".//journal-meta/publisher/publisher-name"),
                    article_number=text_at(".//article-meta/elocation-id"))
    start=text_at(".//article-meta/fpage")
    end=text_at(".//article-meta/lpage")
    metadata["pages"]=start+("-"+end if end and end!=start else "") if start else None
    return dict(provider="PMC JATS",authoritative=True,metadata=metadata,evidence_pointer=pointer)
