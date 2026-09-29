"""Offline domain triage. Candidate observations never enter MCTS or certify chemistry."""
import hashlib
import csv
import io
import json
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from rdkit import Chem, rdBase
from .topology import audit
from .workspace import PACKAGE, active_data, root
from .resources import sha


def dumps(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest(value):
    return hashlib.sha256(dumps(value).encode()).hexdigest()


def load_rules(path=None):
    explicit = path is not None
    path = Path(path) if explicit else root() / "configs/domain_triage.json"
    if explicit and not path.is_file():
        raise ValueError("requested triage rules are missing")
    if not path.is_file():
        path = PACKAGE / "assets/configs/domain_triage.json"
    rules = json.loads(path.read_text())
    known = {(1, "task014-v1"), (2, "task015-p4-v2")}
    if (rules.get("schema_version"), rules.get("protocol_version")) not in known:
        raise ValueError("unsupported triage rules version")
    if rules["schema_version"] >= 2:
        for key in ("dispositions", "source_blacklist"):
            if key not in rules:
                raise ValueError("v2 rules require " + key)
        if rules["dispositions"]["precedence"] != ["blocked_source", "incomplete_record", "pathway_suspect"]:
            raise ValueError("unsupported v2 disposition precedence")
        for entry in rules["source_blacklist"]:
            if not entry.get("journal") or not entry.get("retraction_note_doi"):
                raise ValueError("blacklist entry lacks verifiable identity")
    if sum(rules["sampling_quotas"].values()) != rules["limits"]["sample_records"]:
        raise ValueError("sampling quotas must reconcile")
    for item in rules["scaffolds"].values():
        if Chem.MolFromSmiles(item["query_smiles"]) is None:
            raise ValueError("invalid scaffold query")
    return rules, path


class Screener:
    def __init__(self, rules):
        self.rules = rules
        self.patterns = {k: Chem.MolFromSmiles(v["query_smiles"]) for k, v in rules["scaffolds"].items()}

    @lru_cache(maxsize=None)
    def molecule(self, smiles):
        mol = Chem.MolFromSmiles(smiles) if smiles else None
        if mol is None:
            return {"status": "parse_failure", "canonical": None, "scaffolds": [], "sites": {},
                    "domain_sites": {}, "wildcard": False, "unspecified_stereo": None,
                    "map_atoms": 0, "atom_count": 0}
        wildcard = any(a.GetAtomicNum() == 0 for a in mol.GetAtoms())
        # Map labels are arbitrary correspondence IDs; identity retains stereo/isotopes/charge.
        map_atoms = sum(a.GetAtomMapNum() > 0 for a in mol.GetAtoms())
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(0)
        scaffolds, sites, domain_sites = set(), Counter(), Counter()
        for fragment in Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True):
            found = {k for k, query in self.patterns.items() if fragment.HasSubstructMatch(query, useChirality=False)}
            scaffolds.update(found)
            topology = audit(Chem.MolToSmiles(fragment, isomericSmiles=True))
            counts = Counter(site["family"] for site in topology["sites"])
            sites.update(counts)
            if found:
                domain_sites.update(counts)
        return {"status": "generic_candidate" if wildcard else "parsed",
                "canonical": Chem.MolToSmiles(mol, isomericSmiles=True), "scaffolds": sorted(scaffolds),
                "sites": dict(sorted(sites.items())), "domain_sites": dict(sorted(domain_sites.items())),
                "wildcard": wildcard, "map_atoms": map_atoms, "atom_count": mol.GetNumAtoms(),
                "unspecified_stereo": sum(tag == "?" for _, tag in Chem.FindMolChiralCenters(mol, includeUnassigned=True))}

    def identity(self, row):
        sides = {"reactant": [], "product": []}
        for component in row.get("components", []):
            structure = component.get("structure", {})
            role = component.get("role")
            descriptor = self.molecule(structure.get("canonical_smiles"))
            if role not in sides or structure.get("status") != "parsed" or descriptor["status"] != "parsed":
                return None
            sides[role].extend(descriptor["canonical"].split("."))
        if not all(sides.values()):
            return None
        return ">>".join(".".join(sorted(sides[role])) for role in ("reactant", "product"))

    def reaction(self, row):
        sides = {"reactant": [], "product": []}
        invalid = []
        for number, component in enumerate(row.get("components", [])):
            role = component.get("role")
            if role not in sides:
                invalid.append({"component": number, "reason": "unknown_role"})
                continue
            structure = component.get("structure", {})
            descriptor = self.molecule(structure.get("canonical_smiles"))
            sides[role].append(descriptor)
            if descriptor["status"] != "parsed" or structure.get("status") != "parsed":
                invalid.append({"component": number, "reason": descriptor["status"] if descriptor["status"] != "parsed" else "upstream_parse_failure"})
        for role, components in sides.items():
            if not components:
                invalid.append({"component": None, "reason": "missing_" + role})
        features = {}
        for role, components in sides.items():
            features[role + "_scaffolds"] = sorted({s for c in components for s in c["scaffolds"]})
            for field in ("sites", "domain_sites"):
                counts = Counter()
                for c in components:
                    counts.update(c[field])
                features[role + "_" + field] = dict(sorted(counts.items()))
        domain = bool(features["reactant_scaffolds"] or features["product_scaffolds"])
        domain_glycoside = any(features[role + "_domain_sites"].get(family, 0)
                              for role in sides for family in ("aryl_O_candidate", "aryl_C_candidate", "sugar_sugar_O_candidate", "other_O_candidate"))
        appearance = bool(features["product_scaffolds"] and not features["reactant_scaffolds"])
        categories = set()
        if domain:
            if appearance:
                categories.add("scaffold_construction")
            elif features["reactant_scaffolds"] and features["product_scaffolds"]:
                if features["reactant_scaffolds"] != features["product_scaffolds"]:
                    categories.add("scaffold_interconversion")
                else:
                    categories.add("substituent_modification")
            else:
                categories.add("other_related")
            if domain_glycoside:
                categories.add("glycosyl_related")
        if not categories:
            categories.add("out_of_scope_or_unknown")
        normalized = None
        if not invalid:
            normalized = self.identity(row)
            if normalized.split(">>")[0] == normalized.split(">>")[1]:
                categories.discard("substituent_modification")
                categories.add("other_related")
        signature = {k: v for k, v in features.items() if k.endswith("scaffolds")}
        signature.update({role + "_glycoside_families": sorted(features[role + "_domain_sites"])
                          for role in sides})
        score = (self.rules["scores"]["domain_structure"] * domain
                 + self.rules["scores"]["domain_glycoside"] * domain_glycoside
                 + self.rules["scores"]["scaffold_appearance"] * appearance)
        return {**features, "domain_structure_candidate": domain, "domain_glycoside_candidate": domain_glycoside,
                "structural_categories": sorted(categories), "invalid_components": invalid,
                "status": "partial_or_invalid" if invalid else "parsed",
                "normalized_reaction": normalized,
                "exact_group": digest(normalized) if normalized else "invalid:" + row["id"],
                "guide_signature": digest(signature) if domain and not invalid else None,
                "baseline_score": score, "reaction_center_status": "not_inferred",
                "mapping_status": "upstream_maps_present_unverified" if any(c["map_atoms"] for cs in sides.values() for c in cs) else "not_available",
                "unspecified_stereo": sum(c["unspecified_stereo"] or 0 for cs in sides.values() for c in cs)}


def citation_texts(row):
    """(doi_text, token_text): DOI matching keeps hyphens; token matching normalizes dashes."""
    fields = row["raw"].get("fields", {}) if isinstance(row.get("raw"), dict) else {}
    text = " ".join(str(value) for key, value in fields.items() if "CITATION" in key)
    doi_text = re.sub(r"\s+", " ", text).casefold()
    token_text = re.sub(r"[\s\u2010\u2011\u2012\u2013\u2014-]+", " ", doi_text)
    return doi_text, token_text


def source_blacklist_hits(row, rules):
    """Queue-level block for verifiably retracted sources. Bibliographic only."""
    if rules.get("schema_version", 1) < 2:
        return []
    doi_text, token_text = citation_texts(row)
    hits = []
    for entry in rules["source_blacklist"]:
        doi_hit = any(doi.casefold() in doi_text for doi in (entry.get("original_doi"), entry.get("retraction_note_doi")) if doi)
        names = [entry["journal"], *entry.get("aliases", [])]
        pages = entry.get("pages")
        year = str(entry["year"]) if entry.get("year") else None
        name_hit = any(
            re.sub(r"[\s\u2010\u2011\u2012\u2013\u2014-]+", " ", name).casefold() in token_text
            for name in names if name)
        pages_hit = bool(pages) and re.sub(r"[\s\u2010\u2011\u2012\u2013\u2014-]+", " ", str(pages)).casefold() in token_text
        bounded_hit = all(re.search(r"\b" + re.escape(str(token)) + r"\b", token_text)
                          for token in ([entry.get("volume"), year]) if token)
        issue = entry.get("issue")
        if issue:
            # An issue number only discriminates when the citation carries one; omitting it passes.
            groups = [group for group in re.findall(r"\((\d+)\)", token_text) if group != year]
            bounded_hit = bounded_hit and ((not groups) or (str(issue) in groups))
        token_hit = name_hit and pages_hit and bounded_hit
        if doi_hit or token_hit:
            hits.append(entry)
    return hits


def pathway_compression_suspect(row, features, screener, rules):
    """Multi-product domain output over a non-domain reactant smells like a compressed pathway."""
    if rules.get("schema_version", 1) < 2 or features["status"] != "parsed":
        return False
    if features["reactant_scaffolds"]:
        return False
    if not features["product_scaffolds"]:
        return False
    minimum = rules["dispositions"]["pathway_suspect"]["min_distinct_domain_product_molecules"]
    carrying = 0
    seen = set()
    for component in row.get("components", []):
        if component.get("role") != "product" or component.get("structure", {}).get("status") != "parsed":
            continue
        for smiles in (component["structure"].get("canonical_smiles") or "").split("."):
            if not smiles or smiles in seen:
                continue
            seen.add(smiles)
            if screener.molecule(smiles)["scaffolds"]:
                carrying += 1
    return carrying >= minimum


def v2_disposition(row, features, screener, rules):
    """Owner-calibrated queue overrides. Never deletes records; precedence is contractual."""
    if rules.get("schema_version", 1) < 2:
        return None
    blocked = source_blacklist_hits(row, rules)
    if blocked:
        return {"queue": "blocked_source_blacklist", "flag": "blocked_source",
                "blacklist_entries": [e["retraction_note_doi"] for e in blocked]}
    if features["status"] != "parsed":
        return {"queue": "incomplete_record", "flag": "incomplete_record", "blacklist_entries": []}
    if pathway_compression_suspect(row, features, screener, rules):
        return {"queue": "pathway_suspect", "flag": "pathway_suspect", "blacklist_entries": []}
    return None


def source_keys(row):
    """Conservative grouping hints. Bibliographic identity is not source verification."""
    if row["kind"] == "note_reaction":
        paths = row.get("upstream_sources", [])
        return (["note_file:" + path for path in paths] or ["unresolved:" + row["id"]])
    fields = row["raw"].get("fields", {})
    citations = " ".join(str(value) for key, value in fields.items() if "REFERENCE" in key and key.endswith(":CITATION"))
    titles = [str(value).strip().casefold() for key, value in fields.items() if "REFERENCE" in key and key.endswith(":TITLE") and str(value).strip()]
    keys = ["doi:" + doi.rstrip(".,;)").casefold() for doi in re.findall(r"10\.\d{4,9}/[^\s<>]+", citations, re.I)]
    keys += ["patent:" + re.sub(r"\s+", "", match).upper() for match in re.findall(r"\b(?:WO|US|EP|CN|JP|KR)\s*\d{6,12}(?:\s*[A-C]\d?)?\b", citations, re.I)]
    keys += ["title:" + re.sub(r"\W+", "", title) for title in titles]
    if not keys and citations.strip():
        keys = ["citation:" + re.sub(r"\s+", " ", citations.strip().casefold())]
    return sorted(set(keys)) or ["unresolved:" + row["id"]]


def context_candidates(row, rules):
    raw = row["raw"]
    if row["kind"] == "note_reaction":
        text = " ".join([str(raw.get("name", "")), str(raw.get("conditions", {}).get("condition_text", ""))])
    else:
        text = " ".join(str(value) for key, value in raw.get("fields", {}).items()
                        if key.endswith(":NOTES") or ("REFERENCE" in key and key.endswith(":TITLE")))
    hits = {category: [term for term in terms if term.casefold() in text.casefold()]
            for category, terms in rules["context_terms"].items()}
    return {category: terms for category, terms in hits.items() if terms}


def leakage_groups(rows, features):
    parents = {row["id"]: row["id"] for row in rows}
    def find(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key
    seen = {}
    for row in rows:
        keys = source_keys(row) + ["exact:" + features[row["id"]]["exact_group"]]
        if row["kind"] == "note_reaction":
            parent = row["raw"].get("curation", {}).get("parent_reaction_id")
            if parent:
                keys.append("variant_parent:" + row["source_path"] + ":" + parent)
        for key in keys:
            if key in seen:
                left, right = find(row["id"]), find(seen[key])
                parents[max(left, right)] = min(left, right)
            else:
                seen[key] = row["id"]
    grouped = defaultdict(list)
    for row in rows:
        grouped[find(row["id"])].append(row["id"])
    return [{"group_id": digest(sorted(ids)), "record_ids": sorted(ids), "split": "development_exposed",
             "primary_document_identity_review": "not_performed", "patent_family_resolution": "not_performed"}
            for ids in sorted(grouped.values(), key=lambda members: min(members))]


def select_samples(pilot, rules):
    strata = defaultdict(list)
    for row in pilot:
        features = row["features"]
        if features["status"] != "parsed":
            key = "invalid_or_partial"
        elif features["domain_glycoside_candidate"]:
            key = "glycoside_guide" if row["guide_supported"] else "glycoside_outside_guide"
        elif features["domain_structure_candidate"]:
            key = "domain_guide" if row["guide_supported"] else "domain_outside_guide"
        else:
            key = "low_or_unknown"
        strata[key].append(row)
    chosen, seen = [], set()
    coverage = {}
    for stratum, quota in rules["sampling_quotas"].items():
        ordered = sorted(strata[stratum], key=lambda row: digest(["task014-review-v1", row["id"]]))
        picked = 0
        for row in ordered:
            if picked >= quota:
                break
            exact = row["features"]["exact_group"]
            if exact in seen:
                continue
            chosen.append((stratum, row)); seen.add(exact); picked += 1
        coverage[stratum] = {"available_records": len(ordered), "quota": quota, "selected": picked,
                             "shortfall": quota - picked}
    return chosen, coverage


def build(folder, writer=None, rules_path=None):
    """New immutable output only. The operation CLI supplies an audited writer."""
    folder = Path(folder).resolve()
    if folder.exists():
        raise ValueError("triage output exists; choose a new directory")
    rules, rule_path = load_rules(rules_path)
    resource_folder, resource_manifest, pointer = active_data()
    rows = json.loads((resource_folder / "records.json").read_text())
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate record identity")
    source_manifest = json.loads((root() / "metadata/sources.json").read_text())
    for source in source_manifest["files"]:
        if sha(root() / source["path"]) != source["sha256"]:
            raise ValueError("source hash drift: " + source["path"])
    notes = sorted((row for row in rows if row["kind"] == "note_reaction"), key=lambda row: row["id"])
    reactions = sorted((row for row in rows if row["kind"] == "scifinder_reaction"), key=lambda row: row["id"])
    if len(notes) != 508 or len(reactions) != 2301:
        raise ValueError("TASK-014 frozen input population changed")
    screener = Screener(rules)
    selected = notes + reactions
    bypath = {source["path"]: source for source in source_manifest["files"]}
    for row in selected:
        if row["source_path"] not in bypath or row["source_sha256"] != bypath[row["source_path"]]["sha256"]:
            raise ValueError("record/source binding mismatch: " + row["id"])
    features, exact_cache, computations = {}, {}, 0
    for row in selected:
        # Exact standardized reaction identity reuses classification, independently of component order.
        normalized = screener.identity(row)
        cache_key = normalized if normalized else "invalid:" + row["id"]
        if cache_key not in exact_cache:
            exact_cache[cache_key] = screener.reaction(row); computations += 1
        value = dict(exact_cache[cache_key])
        descriptors = [screener.molecule(c.get("structure", {}).get("canonical_smiles")) for c in row.get("components", [])]
        value["mapping_status"] = "upstream_maps_present_unverified" if any(c["map_atoms"] for c in descriptors) else "not_available"
        features[row["id"]] = value
    guide, signatures, exact_guides = [], defaultdict(list), defaultdict(list)
    note_texts = {}
    for row in notes:
        raw = row["raw"]
        f = features[row["id"]]
        locations = []
        token = raw.get("raw_reaction_smiles")
        for path in row.get("upstream_sources", []):
            if path not in note_texts:
                note_texts[path] = (root() / path).read_text().splitlines()
            lines = [index + 1 for index, line in enumerate(note_texts[path]) if token and token in line]
            locations.append({"path": path, "sha256": sha(root() / path), "reported_line": row.get("upstream_reported_line"), "matched_token_lines": lines})
        found = any(location["matched_token_lines"] for location in locations)
        if found != row.get("upstream_reaction_token_found", False):
            raise ValueError("note token check drift: " + row["id"])
        curation = raw.get("curation", {})
        historical_variant = bool(curation.get("manual_review_applied") or curation.get("variant_label") or curation.get("parent_reaction_id"))
        risks = []
        if not found: risks.append("note_token_unmatched")
        if historical_variant: risks.append("historical_rewrite_or_variant_not_independently_verified")
        if f["status"] != "parsed": risks.append("component_parse_or_generic_failure")
        if f["unspecified_stereo"]: risks.append("unspecified_stereochemistry")
        if raw.get("flags", {}).get("has_generic_group") or raw.get("generic_groups"): risks.append("historical_generic_groups")
        if raw.get("flags", {}).get("aizynthfinder_ready"): risks.append("legacy_ready_is_not_admission")
        conditions = raw.get("conditions", {})
        if conditions.get("yields") and row["outcome"]["is_missing"]: risks.append("context_yield_unassigned")
        eligible = bool(f["guide_signature"])
        use = "pattern_only" if eligible else "context_only"
        if eligible and found and not historical_variant: use = "pattern_and_note_example_candidate"
        item = {"id": row["id"], "input_record": row, "features": f, "locations": locations,
                "guide_use": use, "risks": risks, "legacy_classification": raw.get("classification"),
                "legacy_category_candidate": rules["legacy_classification_candidates"].get(raw.get("classification"), "other_related"),
                "context_category_candidates": context_candidates(row, rules), "production_eligible": False,
                "source_review_status": "not_performed", "human_review_status": "not_performed",
                "split": "development_exposed", "reaction_fact_status": "extraction_candidate"}
        guide.append(item)
        if eligible: signatures[f["guide_signature"]].append(row["id"])
        if use == "pattern_and_note_example_candidate": exact_guides[f["exact_group"]].append(row["id"])
    groups = leakage_groups(selected, features)
    group_for = {record_id: group["group_id"] for group in groups for record_id in group["record_ids"]}
    pilot, duplicates = [], defaultdict(list)
    for row in reactions:
        f = features[row["id"]]
        pattern_ids = sorted(signatures.get(f["guide_signature"], []))
        exact_ids = sorted(exact_guides.get(f["exact_group"], []))
        supported = bool(pattern_ids or exact_ids)
        queue_before = "guide_supported" if f["domain_structure_candidate"] and supported else "outside_guide_structure" if f["domain_structure_candidate"] else "low_or_unknown"
        disposition = v2_disposition(row, f, screener, rules)
        queue = disposition["queue"] if disposition else queue_before
        score = f["baseline_score"] + rules["scores"]["guide_signature"] * bool(pattern_ids) + rules["scores"]["guide_exact"] * bool(exact_ids)
        item = {"id": row["id"], "input_record": row, "features": f, "queue": queue,
                "guide_supported": supported, "guide_score": score,
                "guide_match": {"signature_count": len(pattern_ids), "signature_example_ids": pattern_ids[:rules["limits"]["guide_examples_per_match"]],
                                "exact_count": len(exact_ids), "exact_example_ids": exact_ids[:rules["limits"]["guide_examples_per_match"]],
                                "meaning": "coarse domain pattern, not chemical evidence"},
                "context_category_candidates": context_candidates(row, rules), "source_group_keys": source_keys(row),
                "leakage_group": group_for[row["id"]], "split": "development_exposed",
                "primary_source_status": "not_performed", "human_review_status": "not_performed",
                "production_eligible": False}
        if rules.get("schema_version", 1) >= 2:
            # v1 payloads stay byte-identical; calibration fields exist only under v2 rules.
            item["v1_queue"] = queue_before
            item["v2_disposition"] = disposition
        pilot.append(item); duplicates[f["exact_group"]].append(row["id"])
    chosen, coverage = select_samples(pilot, rules)
    review = []
    for stratum, item in chosen:
        review.append({"id": item["id"], "stratum": stratum, "selection": "development_calibration_not_probability_sample",
                       "leakage_group": item["leakage_group"], "split": "development_exposed", "input_record": item["input_record"],
                       "machine_suggestion": {"features": item["features"], "guide_match": item["guide_match"], "queue": item["queue"]},
                       "annotation": {"reviewer_id": None, "reviewed_at": None, "domain_relevance": None, "transformation_labels": None,
                                      "glycoside_connection": None, "specific_experimental_instance": None, "primary_source_locator": None,
                                      "primary_source_sha256": None, "evidence_excerpt": None, "reactant_product_confirmed": None,
                                      "conditions_yield_assignment": None, "stereo_status": None, "decision": None, "disagreement": None},
                       "human_review_status": "not_performed", "production_eligible": False})
    duplicate_rows = [{"exact_group": key, "record_ids": sorted(ids), "count": len(ids)} for key, ids in sorted(duplicates.items())]
    baseline_order = [row["id"] for row in sorted(pilot, key=lambda row: (-row["features"]["baseline_score"], row["id"]))]
    guide_order = [row["id"] for row in sorted(pilot, key=lambda row: (-row["guide_score"], row["id"]))]
    summary = {"scope": "offline development triage; not a chemical accuracy estimate or formal benchmark",
               "guide_records": len(guide), "pilot_records": len(pilot), "exact_reaction_groups": len(duplicates),
               "duplicate_records_beyond_first": len(pilot) - len(duplicates), "component_descriptor_computations": screener.molecule.cache_info().misses,
               "unique_reaction_classifications": computations, "queues": dict(sorted(Counter(row["queue"] for row in pilot).items())),
               "pilot_status": dict(sorted(Counter(row["features"]["status"] for row in pilot).items())),
               "structural_categories_multilabel": dict(sorted(Counter(c for row in pilot for c in row["features"]["structural_categories"]).items())),
               "guide_use": dict(sorted(Counter(row["guide_use"] for row in guide).items())),
               "guide_risks_multilabel": dict(sorted(Counter(risk for row in guide for risk in row["risks"]).items())),
               "pilot_domain_records": sum(row["features"]["domain_structure_candidate"] for row in pilot),
               "pilot_domain_glycoside_records": sum(row["features"]["domain_glycoside_candidate"] for row in pilot),
               "rank_changed_records": sum(a != b for a, b in zip(baseline_order, guide_order)),
               "top60_overlap": len(set(baseline_order[:60]) & set(guide_order[:60])),
               "top60_baseline_glycosides": sum(row["features"]["domain_glycoside_candidate"] for row in pilot if row["id"] in set(baseline_order[:60])),
               "top60_guide_glycosides": sum(row["features"]["domain_glycoside_candidate"] for row in pilot if row["id"] in set(guide_order[:60])),
               "review_samples": len(review), "sampling_coverage": coverage, "leakage_groups": len(groups),
               "blind_records": 0, "human_reviewed_records": 0, "production_records": 0,
               "precision": None, "recall": None, "accuracy": None,
               "limitations": ["Inputs are historical query-selected exports, not an unbiased chemical population",
                               "No atom mapping or reaction-center inference; topology signatures are candidates only",
                               "Guide signatures are coarse scaffold/topology co-occurrence; not mechanistic matching",
                               "All inputs were exposed during development; cannot be reused as independent blind labels",
                               "Stratified quota samples are not a probability sample and cannot estimate whole-population accuracy"]
                               + (["Owner-review-calibrated dispositions are screening behavior learned from 60 development-exposed cards; they are not validated chemical filters"]
                                  if rules.get("schema_version", 1) >= 2 else [])}
    files = {"guide.jsonl": "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in guide),
             "pilot.jsonl": "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in pilot),
             "duplicates.json": dumps(duplicate_rows), "leakage-groups.json": dumps(groups),
             "review.jsonl": "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in review),
             "queues.json": dumps({"baseline_order": baseline_order, "guide_order": guide_order,
                                  "by_queue": {q: [r["id"] for r in pilot if r["queue"] == q]
                                               for q in sorted({r["queue"] for r in pilot})}}),
             "summary.json": dumps(summary), "rules.json": dumps(rules)}
    review_buffer = io.StringIO(newline="")
    columns = ["id", "stratum", "leakage_group", "split", "machine_queue", "machine_categories",
               "reactants", "products", "source_path", "source_locator", "reference_citation", "reference_title"]
    annotation_columns = list(review[0]["annotation"]) if review else []
    table = csv.DictWriter(review_buffer, fieldnames=columns + annotation_columns, delimiter="\t", lineterminator="\n")
    table.writeheader()
    for item in review:
        record = item["input_record"]
        fields = record["raw"].get("fields", {})
        payload = {"id": item["id"], "stratum": item["stratum"], "leakage_group": item["leakage_group"],
                   "split": item["split"], "machine_queue": item["machine_suggestion"]["queue"],
                   "machine_categories": ";".join(item["machine_suggestion"]["features"]["structural_categories"]),
                   "source_path": record["source_path"], "source_locator": record["locator"],
                   "reference_citation": " ".join(str(v) for k, v in fields.items() if "REFERENCE" in k and k.endswith(":CITATION")),
                   "reference_title": " ".join(str(v) for k, v in fields.items() if "REFERENCE" in k and k.endswith(":TITLE"))}
        for role, column in (("reactant", "reactants"), ("product", "products")):
            payload[column] = ".".join(c.get("structure", {}).get("canonical_smiles") or "[UNPARSED]"
                                      for c in record.get("components", []) if c["role"] == role)
        table.writerow(payload)
    files["review.tsv"] = review_buffer.getvalue()
    files["README.md"] = """# TASK-014 本地离线试点

全部载荷仅在本地保留，不入 Git。本目录冻结后只读；填写审核记录请另建版本化的审核目录，不编辑此处。

- guide.jsonl：508 条笔记原记录、定位行号、风险及 guide 用途。
- pilot.jsonl：2,301 条原记录、结构描述、优先级与 guide 匹配线索。
- queues.json：两策略全部排序和三队列；低分与失败仍保留。
- duplicates.json：精确标准化反应的全部来源成员；不同条件/收率未合并。
- leakage-groups.json：防泄漏连接组；全部为 development_exposed，文献/专利家族身份未审核。
- review.jsonl、review.tsv：60 条固定配额开发审核样本；人工标签 null/空白，machine_ 前缀列仅为候选建议。TSV 是本地导出，若用表格软件导入，应把字段设为文本，不能把 null/空白改为零。
- summary.json：机器观察、抽样覆盖及局限；precision/recall/accuracy 为 null。
- rules.json：本次使用的规则快照；manifest.json 绑定输入、代码、规则和所有输出哈希。
- audit.ipynb：独立统计核查；从项目根目录执行，可调整 folder 核查重放输出。

review 包用于开发校准，不能直接冒充独立盲标包；后续盲标须隐藏机器建议。本任务未核验一手来源、未产生独立 gold、未接入搜索、未改变科学准入。
"""
    # A standard-library companion notebook independently recomputes conservation/counts.
    cell = """import json\nfrom pathlib import Path\nfrom collections import Counter\nworkspace = Path.cwd()  # Run from the repository root, or set this path explicitly.\nfolder = workspace / RUN_FOLDER\nguide = [json.loads(line) for line in (folder / 'guide.jsonl').read_text().splitlines()]\npilot = [json.loads(line) for line in (folder / 'pilot.jsonl').read_text().splitlines()]\nsummary = json.loads((folder / 'summary.json').read_text())\nraw = json.loads((workspace / 'data/derived/v3/records.json').read_text())\nassert {r['id']: r for r in raw if r['kind'] == 'note_reaction'} == {r['id']: r['input_record'] for r in guide}\nassert {r['id']: r for r in raw if r['kind'] == 'scifinder_reaction'} == {r['id']: r['input_record'] for r in pilot}\nassert dict(Counter(r['queue'] for r in pilot)) == summary['queues']\nassert len({r['features']['exact_group'] for r in pilot}) == summary['exact_reaction_groups']\nassert all(r['split'] == 'development_exposed' and not r['production_eligible'] for r in guide + pilot)\nprint({'guide': len(guide), 'pilot': len(pilot), 'queues': summary['queues'], 'blind_records': 0})\n"""
    # Keep the notebook path-independent so replay is byte-identical.
    cell = cell.replace("RUN_FOLDER", "Path('outputs/triage/task014-final')  # Set to the output being audited")
    notebook = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
                "cells": [{"id": "scope", "cell_type": "markdown", "metadata": {}, "source": ["# TASK-014 独立统计核查\n", "从项目根目录运行；核查记录保全和机器统计，不确认化学标签。重放时调整 folder。\n"]},
                          {"id": "audit", "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": cell.splitlines(keepends=True)}]}
    files["audit.ipynb"] = dumps(notebook)
    manifest = {"schema_version": 1, "protocol_version": rules["protocol_version"], "resource_version": pointer["version"],
                "records_sha256": resource_manifest["records_sha256"], "source_manifest_sha256": sha(root() / "metadata/sources.json"),
                "rules_sha256": sha(rule_path), "triage_code_sha256": sha(__file__), "topology_code_sha256": sha(PACKAGE / "topology.py"),
                "rdkit_version": rdBase.rdkitVersion, "payload_sha256": {name: hashlib.sha256(body.encode()).hexdigest() for name, body in files.items()},
                "scope": summary["scope"], "approval_type": "human_direct_task_execution_not_chemical_review"}
    files["manifest.json"] = dumps(manifest)
    folder.mkdir(parents=True)
    for name, body in files.items():
        path = folder / name
        if writer:
            writer(path, body)
        else:
            path.write_text(body, encoding="utf-8")
        path.chmod(0o444)
    return summary
