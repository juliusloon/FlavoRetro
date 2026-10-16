"""Query-plan/disposition conservation and immutable raw acquisition accounting."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from scripts.task016_p7_orchestrate import ContractError, ROOT, require_fields, require_int, sha_file

QUERY_FIELDS = ("query_id", "query", "route", "database", "family", "scope_id", "reason", "max_pages", "max_objects")
EXEC_FIELDS = ("query_id", "status", "returned_count", "deduplicated_count", "pending_identity_count",
               "admitted", "deferred", "rejected", "metadata_only", "new_closure_groups")
DISPOSITIONS = ("admitted", "deferred", "rejected", "metadata_only")


def validate_query_accounting(plan, executions, discoveries):
    require_fields(plan, ("task", "epoch_id", "queries", "preregistered_at"))
    queries = plan["queries"]
    expected = []
    for row in queries:
        require_fields(row, QUERY_FIELDS)
        if row["family"] not in ("C", "SS") or not row["query"].strip() or not row["reason"].strip():
            raise ContractError("invalid query identity/family/reason")
        for key in ("max_pages", "max_objects"):
            require_int(row[key], key, minimum=1)
        expected.append(row["query_id"])
    if len(set(expected)) != len(expected):
        raise ContractError("duplicate preregistered query")
    if Counter(expected) != Counter(row.get("query_id") for row in executions):
        raise ContractError("query plan != executed + explicitly skipped")
    by_query = {}
    for row in executions:
        require_fields(row, EXEC_FIELDS)
        if row["status"] not in ("executed", "skipped"):
            raise ContractError("unterminated query")
        for key in EXEC_FIELDS[2:]:
            require_int(row[key], key)
        if row["status"] == "skipped":
            require_fields(row, ("skip_reason",))
            if not row["skip_reason"] or any(row[key] for key in EXEC_FIELDS[2:]):
                raise ContractError("skipped query needs reason and zero result counts")
        if row["deduplicated_count"] > row["returned_count"]:
            raise ContractError("deduplicated exceeds returned")
        if sum(row[key] for key in DISPOSITIONS) != row["deduplicated_count"]:
            raise ContractError("discovered != admitted + deferred + rejected + metadata_only")
        if row["pending_identity_count"] > row["deferred"]+row["metadata_only"]:
            raise ContractError("pending identity cannot be admitted")
        by_query[row["query_id"]] = row
    seen = set()
    counts = Counter()
    per_disposition = Counter()
    for row in discoveries:
        require_fields(row, ("record_id", "query_id", "disposition", "source_hint", "metadata_only"))
        key = (row["query_id"], row["record_id"])
        if key in seen or row["query_id"] not in by_query:
            raise ContractError("duplicate/undeclared discovery")
        seen.add(key)
        if row["disposition"] not in DISPOSITIONS:
            raise ContractError("discovery disposition missing")
        if row["disposition"] == "metadata_only" and row["metadata_only"] is not True:
            raise ContractError("metadata_only disposition inconsistent")
        if row.get("evidence_eligible") and not row.get("identity_verification_sha"):
            raise ContractError("agent/scout hint cannot become evidence")
        counts[row["query_id"]] += 1
        per_disposition[(row["query_id"], row["disposition"])] += 1
    for query_id,row in by_query.items():
        if counts[query_id] != row["deduplicated_count"]:
            raise ContractError("query result row count mismatch")
        for disposition in DISPOSITIONS:
            if per_disposition[(query_id, disposition)] != row[disposition]:
                raise ContractError("query disposition count mismatch")
    return dict(planned=len(queries), executed=sum(row["status"]=="executed" for row in executions),
                skipped=sum(row["status"]=="skipped" for row in executions),
                returned=sum(row["returned_count"] for row in executions),
                discovered=len(discoveries),
                routes=sorted({row["route"] for row in queries}),
                conserved=True)


def validate_acquisition(attempts, raw_manifest, *, root=ROOT):
    require_fields(raw_manifest, ("objects", "bytes", "http_requests", "article_versions", "attachments"))
    for key in ("bytes", "http_requests", "article_versions", "attachments"):
        require_int(raw_manifest[key], key)
    if len(attempts) != raw_manifest["http_requests"]:
        raise ContractError("HTTP count mismatch")
    ids = set()
    per_url = Counter()
    observed_bytes = 0
    for row in attempts:
        require_fields(row, ("attempt_id", "url", "bytes", "status", "recovery_chain", "path",
                             "sha256", "license", "redistribution", "started_at"), nullable=("path","sha256","license"))
        if row["attempt_id"] in ids:
            raise ContractError("duplicate acquisition attempt")
        ids.add(row["attempt_id"])
        require_int(row["bytes"], "download bytes")
        per_url[row["url"]] += 1
        if per_url[row["url"]] > (3 if row["recovery_chain"] else 2):
            raise ContractError("URL attempt cap exceeded")
        if row["recovery_chain"] is True and not row.get("recovery_reason"):
            raise ContractError("third URL attempt needs recovery reason")
        if row["bytes"] or row["path"] is not None:
            if row["path"] is None or row["sha256"] is None:
                raise ContractError("downloaded/failed response requires immutable bytes and SHA")
            path = root/row["path"]
            if not path.is_file() or path.stat().st_size != row["bytes"] or sha_file(path) != row["sha256"]:
                raise ContractError("raw bytes/SHA mismatch")
        observed_bytes += row["bytes"]
    objects = raw_manifest["objects"]
    if Counter(row["attempt_id"] for row in objects) != Counter(row["attempt_id"] for row in attempts
                                                               if row["path"] is not None):
        raise ContractError("raw file manifest != attempts with bytes")
    for row in objects:
        require_fields(row, ("attempt_id", "path", "sha256", "bytes", "kind"))
        attempt = next(item for item in attempts if item["attempt_id"]==row["attempt_id"])
        if any(row[key] != attempt[key] for key in ("path","sha256","bytes")):
            raise ContractError("raw manifest binds different attempt")
    if observed_bytes != raw_manifest["bytes"]:
        raise ContractError("downloaded byte count mismatch")
    article_versions = sum(row["kind"]=="article_version" for row in objects)
    attachments = sum(row["kind"]=="attachment" for row in objects)
    if article_versions != raw_manifest["article_versions"] or attachments != raw_manifest["attachments"]:
        raise ContractError("article/attachment accounting mismatch")
    if len(attempts)>8000 or observed_bytes>8*1024**3 or article_versions>400 or attachments>800:
        raise ContractError("source budget exceeded")
    return dict(http_requests=len(attempts),bytes=observed_bytes,files=len(objects),
                article_versions=article_versions,attachments=attachments,conserved=True)


def saturated(rounds):
    """A family may stop only after three routes and two fully terminal empty rounds."""
    if len(rounds)<2:
        return False
    for row in rounds:
        require_fields(row,("family","round_id","complete","routes","new_qualified_closure_groups"))
        require_int(row["new_qualified_closure_groups"],"new qualified groups")
    families = {row["family"] for row in rounds}
    if len(families)!=1:
        raise ContractError("saturation is family independent")
    routes = set().union(*(set(row["routes"]) for row in rounds))
    return len(routes)>=3 and all(row["complete"] is True and row["new_qualified_closure_groups"]==0
                                  for row in rounds[-2:])
