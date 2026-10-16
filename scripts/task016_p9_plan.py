"""TASK-016-P9: offline inventory and preregistration only; never loads a runtime."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

from rdkit import Chem, rdBase

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from operate import write

TASK = "TASK-016-P9"
OUT = ROOT / "outputs/task016-p9/v1"
FAMILIES = ("C_formation", "sugar_sugar_formation", "O_formation")
RECORD_FILES = (
    "outputs/task016-p1/v2/instances.jsonl",
    "outputs/task016-p2/v2/runtime_instances.jsonl",
    "outputs/task016-p4/v1/runtime_instances.jsonl",
    "outputs/task016-p6/v1/runtime_instances.jsonl",
    "outputs/task016-p6/v1/c_heldout_references.jsonl",
    "outputs/task016-p6/v1/ss_heldout_references.jsonl",
    "outputs/task016-p6/v1/c_runtime_completeness.jsonl",
    "outputs/task016-p6/v1/c_build_supports.jsonl",
)
TEMPLATE_FILES = (
    "outputs/task016-p1/v2/templates.jsonl",
    "outputs/task016-p2/v2/templates.jsonl",
    "outputs/task016-p4/v1/templates.jsonl",
    "outputs/task016-p6/v1/templates.jsonl",
)

def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()

def stable(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

def emit(name, value):
    content = value if isinstance(value, str) else stable(value)
    write(TASK, str((OUT / name).relative_to(ROOT)), content)

def read_inputs():
    manifest = json.loads((OUT / "input_manifest.json").read_text())
    assert len(manifest["files"]) <= manifest["max_files"]
    data = {}
    for entry in manifest["files"]:
        if not entry["exists"]:
            data[entry["path"]] = None
            continue
        path = ROOT / entry["path"]
        assert path.resolve().is_relative_to(ROOT / "outputs")
        assert "data/raw" not in str(path) and "R80" not in str(path)
        raw = path.read_bytes()
        if sha(raw) != entry["sha256"]:
            raise ValueError("input SHA drift: " + entry["path"])
        if manifest["content_read_bytes"] + len(raw) > manifest["max_content_read_bytes"]:
            raise ValueError("input byte budget exhausted")
        if entry["path"].endswith(".jsonl"):
            rows = []
            for number, line in enumerate(raw.decode().splitlines(), 1):
                if not line.strip():
                    continue
                if "permitted_ids" in entry:
                    ids = re.findall(r'"reaction_id"\s*:\s*"([^"]+)"', line)
                    if len(ids) != 1 or ids[0] not in entry["known_audited_ids"]:
                        raise ValueError("unknown row before JSON decode")
                    if ids[0] not in entry["permitted_ids"]:
                        continue
                row = json.loads(line)
                row["_input_pointer"] = entry["path"] + "#L" + str(number)
                rows.append(row)
            data[entry["path"]] = rows
        else:
            data[entry["path"]] = json.loads(raw)
        entry["read_count"] += 1
        manifest["content_read_bytes"] += len(raw)
    emit("input_manifest.json", manifest)
    return data, manifest

class Groups:
    def __init__(self):
        self.parent = {}

    def find(self, node):
        self.parent.setdefault(node, node)
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def join(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[max(a, b)] = min(a, b)

    def components(self):
        groups = defaultdict(list)
        for node in sorted(self.parent):
            groups[self.find(node)].append(node)
        return dict(groups)

def graph_key(smiles):
    # Validate and canonicalize an already encoded graph; never fill missing graphs.
    if not isinstance(smiles, str) or not smiles:
        return None
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return Chem.MolToSmiles(mol, isomericSmiles=True)

def inherited_labels(row):
    case = row.get("annotation_case") or {}
    context = row.get("required_context") or {}
    scope = row.get("p4_scope_center")
    # Explicit producer labels only. No substructure queries or reaction application.
    core = {
        "C_second_encoding": "phloretin_mono_C_glycoside",
        "C_sugar_encoding": "phloretin",
    }.get(case.get("structure_mode"), "not_serialized")
    if row.get("reaction_id") in ("P3R-C05", "P3R-C06"):
        core = "flavonol"
    site = row.get("site", row.get("linkage", row.get("position")))
    if site is None and "sugar_2_encoding" in str(case.get("structure_mode", "")):
        site = "sugar_O2_from_inherited_encoding_label"
    if row.get("reaction_id") in ("P3R-C05", "P3R-C06"):
        site = "C8_from_frozen_scope_metadata"
    if scope:
        site = scope
    return {
        "acceptor_core": core,
        "formed_site_or_linkage": str(site) if site is not None else "not_serialized",
        "sugar_identity": row.get("sugar_type") or "not_serialized",
        "donor_context": context.get("donor_name") or row.get("source_donor") or "not_serialized",
        "catalytic_mode": row.get("catalyst_mode") or context.get("mode") or "not_serialized",
        "inherited_structure_mode": case.get("structure_mode"),
    }

def profile(row, filename, legacy_groups):
    identity = row.get("instance_id") or row.get("reaction_id")
    if not identity:
        raise ValueError("missing object identity: " + filename)
    provenance = row.get("provenance") or row.get("source_binding") or row.get("original_reference") or {}
    source = provenance.get("pmcid")
    original_group = row.get("source_group", row.get("closure_group", row.get("scope_group")))
    normalized_group = original_group
    while isinstance(normalized_group, str) and normalized_group.startswith("inherited:"):
        normalized_group = normalized_group[len("inherited:"):]
    sources = set(legacy_groups.get(normalized_group, []))
    if source:
        sources.add(source)
    if not sources:
        sources.update(re.findall(r"PMC\d+", identity))
    if not sources and isinstance(normalized_group, str):
        sources.update(re.findall(r"PMC\d+", normalized_group))
    target = row.get("target") or row.get("product_smiles")
    acceptor = row.get("acceptor") or row.get("acceptor_smiles")
    refs = row.get("reference_precursors")
    keys = {
        "target": graph_key(target),
        "acceptor": graph_key(acceptor),
        "references": [graph_key(s) for s in refs] if isinstance(refs, list) else None,
    }
    fields_present = bool(target and acceptor and isinstance(refs, list) and len(refs) >= 2)
    donor_graph = graph_key(row.get("donor"))
    graph_fields_parse = bool(fields_present and keys["target"] and keys["acceptor"]
                             and all(keys["references"]))
    reference_contains_acceptor = bool(graph_fields_parse and keys["acceptor"] in keys["references"])
    reference_contains_serialized_donor = (
        donor_graph in keys["references"] if donor_graph and graph_fields_parse else None)
    machine_complete = bool(graph_fields_parse and reference_contains_acceptor
                            and reference_contains_serialized_donor is not False)
    signature_present = bool(row.get("canonical_reaction_signature") or row.get("covalent_signature")
                             or row.get("reference_signature"))
    # Equality checks use existing encoded graphs; missing inherited normalized signature stays unknown.
    inventory_key_available = bool(machine_complete and signature_present)
    target_key = sha(keys["target"]) if inventory_key_available else None
    acceptor_key = sha(keys["acceptor"]) if inventory_key_available else None
    reference_key = sha(".".join(sorted(keys["references"]))) if inventory_key_available else None
    reaction_key = sha(".".join(sorted(keys["references"])) + ">>" + keys["target"]) if inventory_key_available else None
    category = row.get("category", row.get("bond_class"))
    if category not in FAMILIES:
        raise ValueError("unsupported family " + str(category))
    runtime_member = "runtime_instances" in filename
    return {
        "object_id": identity, "reaction_id": row.get("reaction_id"),
        "family": category, "sources": sorted(sources),
        "inherited_source_group": normalized_group,
        "input_pointer": row["_input_pointer"],
        "target_key": target_key, "acceptor_key": acceptor_key,
        "reference_key": reference_key, "reaction_key": reaction_key,
        "existing_normalized_signature_present": signature_present,
        "inventory_key_available": inventory_key_available,
        "reference_contains_acceptor": reference_contains_acceptor,
        "reference_contains_serialized_donor": reference_contains_serialized_donor,
        "graph_fields_parse": graph_fields_parse,
        "key_basis": "existing normalized signature plus canonical equality of existing encoded graphs; not new chemical adjudication",
        "encoded_fields_present": fields_present,
        "machine_parse_complete": machine_complete,
        "inherited_scientific_admission": "final_qualified_runtime_or_final_P6_reference",
        "inherited_runtime_member": runtime_member,
        "inherited_runtime_executable": row.get("runtime_executable"),
        "historical_exposure": True,
        "exposure_basis": "prior qualified delivery used in structure validation/build or historical panel",
        "scientific_re_adjudication": False,
        "labels": inherited_labels(row),
        "local_normalization": "RDKit parse/sanitize and isomeric canonicalization of existing encoded graphs only",
        "donor_key": sha(donor_graph) if donor_graph else None,
    }

def build(data):
    p7 = data["outputs/task016-p7/v1/task_execution_closeout.json"]
    assert p7["execution_status"] == "stopped"
    assert p7["scientific_completion"] is False
    split = data["outputs/task016-p1/v2/development_split_manifest.json"]
    legacy_groups = {g["source_group"]: g["pmcids"] for g in split["groups"]}
    occurrences, selected, errors = [], {}, []
    for filename in RECORD_FILES:
        for row in data[filename]:
            record = profile(row, filename, legacy_groups)
            previous = selected.get(record["object_id"])
            if previous and any(previous[k] != record[k] for k in ("target_key", "acceptor_key", "reference_key")):
                errors.append({"object_id": record["object_id"], "kind": "encoding_conflict",
                               "first": previous["input_pointer"], "second": record["input_pointer"]})
                record["disposition"] = "blocked_encoding_conflict"
            else:
                record["disposition"] = "eligible_encoded_historical" if record["machine_parse_complete"] else "incomplete_existing_encoding"
            occurrences.append(dict(record))
            # Later qualified runtime/P6 representations supersede duplicate delivery copies.
            if previous:
                record["inherited_runtime_member"] |= previous["inherited_runtime_member"]
            selected[record["object_id"]] = record
    if errors:
        raise ValueError("encoding conflict; stop " + str(errors))

    reaudit = data["outputs/task016-p4/v1/p3_reaudit.jsonl"]
    corrected = data["outputs/task016-p4/v1/corrected_reaction_records.jsonl"]
    p6_corrections = {r["reaction_id"]: r for r in data["outputs/task016-p6/v1/ss_reference_reconciliation.jsonl"]}
    represented_ids = {r["reaction_id"] for r in selected.values() if r["reaction_id"]}
    assert "P6-SS22-corrected" in selected
    represented_ids.add("P3R-SS22")  # Explicit P6 corrected-ID supersession, not inferred identity.
    metadata_dispositions = []
    for row in reaudit:
        rid = row["reaction_id"]
        correction = p6_corrections.get(rid)
        if correction and correction["final_status"] == "excluded_primary_and_closure":
            status = "excluded_primary_and_closure_by_P6"
        elif correction and correction["final_status"] == "corrected_identity_but_build_closure":
            status = "old_identity_superseded_P6_no_separate_encoded_export"
        elif not row["countable_as_structure_complete"]:
            status = "deferred_scientific_structure_no_graph_read"
        elif rid in represented_ids:
            status = "represented_by_final_encoded_export"
        else:
            status = "admitted_but_no_machine_graph_in_this_final_export"
        metadata_dispositions.append({
            "object_id": rid, "family": row["bond_class"], "input_pointer": row["_input_pointer"],
            "disposition": status, "p4_scientific_status": row["p4_status"],
            "p6_override": correction["final_status"] if correction else None,
            "target_key": None, "machine_parse_complete": None,
            "effect": None, "historical_exposure": True,
        })

    closure, edges = Groups(), []
    def link(a, b, kind, pointer):
        if not a or not b:
            return
        closure.join(a, b)
        edges.append({"a": a, "b": b, "kind": kind, "pointer": pointer})
    for record in selected.values():
        nodes = ["article:" + s for s in record["sources"]]
        if not nodes:
            nodes = ["unresolved:" + record["object_id"]]
        record["_node"] = nodes[0]
        closure.find(nodes[0])
        for node in nodes[1:]:
            link(nodes[0], node, "inherited_source_group", record["input_pointer"])
    for row in corrected:
        sources = row.get("source_pmcds", [])
        for source in sources[1:]:
            link("article:" + sources[0], "article:" + source,
                 "inherited_multiple_sources_for_same_reaction", row["_input_pointer"])
    for filename in ("outputs/task016-p4/v1/source_group_edges.jsonl",
                     "outputs/task016-p6/v1/ss_source_group_edges.jsonl"):
        for row in data[filename]:
            a, b = row.get("source", row.get("source_a")), row.get("other", row.get("source_b"))
            if a and b:
                link("article:" + a, "article:" + b,
                     row.get("edge_type", row.get("reason")), row["_input_pointer"])
    reaction_sources = defaultdict(list)
    for record in selected.values():
        if record["reaction_key"]:
            reaction_sources[record["reaction_key"]].append(record)
    for records in reaction_sources.values():
        for record in records[1:]:
            link(records[0]["_node"], record["_node"], "same_canonical_encoded_reaction", record["input_pointer"])

    source_components = closure.components()
    split_groups = Groups()
    for component in source_components.values():
        for node in component:
            split_groups.join(component[0], node)
    target_sources = defaultdict(list)
    for record in selected.values():
        if record["target_key"]:
            target_sources[record["target_key"]].append(record)
    split_extra = []
    for target, records in target_sources.items():
        for record in records[1:]:
            split_groups.join(records[0]["_node"], record["_node"])
            split_extra.append({"target_key": target, "a": records[0]["_node"], "b": record["_node"],
                                "kind": "same_product_target_split_guard_not_assay_independence"})
    components = split_groups.components()
    group_ids = {root: "P9G-" + sha("|".join(nodes))[:12] for root, nodes in components.items()}
    for record in selected.values():
        record["source_closure_id"] = "P9C-" + sha("|".join(source_components[closure.find(record["_node"])]))[:12]
        record["split_group_id"] = group_ids[split_groups.find(record["_node"])]
        del record["_node"]
    records = sorted(selected.values(), key=lambda r: r["object_id"])
    record_by_id = {r["object_id"]: r for r in records}

    current_assets = {}
    asset_history = []
    for filename in TEMPLATE_FILES:
        for template in data[filename]:
            supports = template.get("support_instances")
            if not isinstance(supports, list):
                raise ValueError("invalid support schema")
            known = [record_by_id[s] for s in supports if s in record_by_id]
            asset = {
                "template_id": template["template_id"], "family": template["category"],
                "role": template["template_role"], "input_pointer": template["_input_pointer"],
                "support_ids": supports, "unresolved_support_ids": [s for s in supports if s not in record_by_id],
                "support_group_ids": sorted({r["split_group_id"] for r in known}),
                "declared_scope": template.get("scope"),
                "full_asset_sha256": sha(stable({k: v for k, v in template.items() if k != "_input_pointer"})),
            }
            asset_history.append(asset)
            if filename in ("outputs/task016-p2/v2/templates.jsonl", "outputs/task016-p6/v1/templates.jsonl"):
                current_assets[asset["template_id"]] = asset
    assets = sorted(current_assets.values(), key=lambda a: a["template_id"])
    assert len(assets) == 56
    strata = defaultdict(list)
    for record in records:
        labels = record["labels"]
        key = (record["family"], labels["acceptor_core"], labels["formed_site_or_linkage"],
               labels["sugar_identity"], labels["donor_context"], labels["catalytic_mode"])
        strata[key].append(record)
    stratum_rows = []
    for key, members in sorted(strata.items()):
        row = dict(zip(("family", "acceptor_core", "formed_site_or_linkage", "sugar_identity", "donor_context", "catalytic_mode"), key))
        row.update(
            stratum_id="P9S-" + sha("|".join(key))[:12],
            encoded_contexts=len(members), exact_reactions=len({r["reaction_key"] for r in members if r["reaction_key"]}),
            distinct_targets=len({r["target_key"] for r in members if r["target_key"]}),
            distinct_acceptors=len({r["acceptor_key"] for r in members if r["acceptor_key"]}),
            known_source_closure_components=len({r["source_closure_id"] for r in members}),
            split_components=len({r["split_group_id"] for r in members}),
            machine_parse_complete=sum(r["machine_parse_complete"] for r in members),
            inherited_runtime_members=sum(r["inherited_runtime_member"] for r in members),
            inherited_runtime_executable_true=sum(r["inherited_runtime_executable"] is True for r in members),
            inherited_runtime_executable_unknown=sum(r["inherited_runtime_executable"] is None for r in members),
            object_ids=[r["object_id"] for r in members],
            unresolved_label_fields=[f for f, value in row.items() if value == "not_serialized"],
            fresh_targets=0, effects=None,
        )
        stratum_rows.append(row)

    folds, plans = [], []
    for family in FAMILIES[:2]:
        family_records = [r for r in records if r["family"] == family and r["inventory_key_available"]]
        for group in sorted({r["split_group_id"] for r in family_records}):
            test = [r for r in family_records if r["split_group_id"] == group]
            train = [r for r in records if r["split_group_id"] != group and r["inventory_key_available"]]
            train_ids = {r["object_id"] for r in train}
            test_target_keys = {r["target_key"] for r in test}
            assert not test_target_keys.intersection(r["target_key"] for r in train)
            fold_id = family + "/" + group
            actions, rebuildable_scopes = [], []
            for asset in assets:
                surviving = [record_by_id[s] for s in asset["support_ids"] if s in train_ids]
                removed = [s for s in asset["support_ids"] if s in record_by_id and s not in train_ids]
                distinct_acceptors = len({r["acceptor_key"] for r in surviving if r["acceptor_key"]})
                if asset["unresolved_support_ids"]:
                    action = "blocked_unverified_lineage"
                elif asset["role"] == "scope_template":
                    action = "rebuild_from_train_only" if distinct_acceptors >= 2 else "exclude_insufficient_support"
                    if action == "rebuild_from_train_only" and asset["family"] == family:
                        rebuildable_scopes.append(asset["template_id"])
                else:
                    action = "rebuild_from_train_only" if surviving else "exclude_no_train_support"
                actions.append({
                    "template_id": asset["template_id"], "family": asset["family"], "role": asset["role"],
                    "action": action, "surviving_support_ids": [r["object_id"] for r in surviving],
                    "removed_support_ids": removed, "distinct_build_acceptors": distinct_acceptors,
                    "unresolved_support_ids": asset["unresolved_support_ids"],
                    "source_asset_pointer": asset["input_pointer"],
                    "runtime_rebuild_verified": False,
                })
            unverified = [a["template_id"] for a in actions if a["action"] == "blocked_unverified_lineage"]
            status = "unverified_lineage" if unverified else ("data_support_feasible" if rebuildable_scopes else "insufficient_build_support")
            fold = {
                "fold_id": fold_id, "family": family, "held_out_split_group_id": group,
                "test_object_ids": [r["object_id"] for r in test],
                "test_target_keys": sorted(test_target_keys), "registered_target_count": len(test_target_keys),
                "train_object_ids": sorted(train_ids),
                "train_source_group_ids": sorted({r["split_group_id"] for r in train}),
                "test_source_closure_ids": sorted({r["source_closure_id"] for r in test}),
                "known_graph_group_intersection": [],
                "product_target_intersection": [],
                "rebuildable_same_family_scope_ids": rebuildable_scopes,
                "data_feasibility_status": status, "unverified_asset_ids": unverified,
                "runtime_rebuild_verified": False, "execution_authorized": False,
                "all_project_source_assay_closure_verified": False,
                "panel_freeze_release_status": "blocked_pending_full_closure_alias_policy_and_actual_rebuild",
                "selection_used_E_reference_match": False,
                "out_of_scope_test_targets_retained": True,
                "planned_cells": 9 * len(test_target_keys), "observed_cells": 0, "effects": None,
            }
            folds.append(fold)
            plans.append({"fold_id": fold_id, "assets": actions})

    summary = {}
    for family in FAMILIES:
        members = [r for r in records if r["family"] == family]
        fs = [f for f in folds if f["family"] == family]
        meta = [r for r in metadata_dispositions if r["family"] == family]
        summary[family] = {
            "encoded_contexts": len(members),
            "exact_encoded_reactions": len({r["reaction_key"] for r in members if r["reaction_key"]}),
            "distinct_encoded_targets": len({r["target_key"] for r in members if r["target_key"]}),
            "distinct_encoded_acceptors": len({r["acceptor_key"] for r in members if r["acceptor_key"]}),
            "known_source_closure_components": len({r["source_closure_id"] for r in members}),
            "split_components_after_product_guard": len({r["split_group_id"] for r in members}),
            "machine_parse_complete": sum(r["machine_parse_complete"] for r in members),
            "normalized_key_unavailable": sum(not r["inventory_key_available"] for r in members),
            "P4_status_rows": len(meta),
            "P4_status_dispositions": dict(sorted(Counter(r["disposition"] for r in meta).items())),
            "planned_folds": len(fs),
            "data_support_feasible_folds": sum(f["data_feasibility_status"] == "data_support_feasible" for f in fs),
            "unverified_lineage_folds": sum(f["data_feasibility_status"] == "unverified_lineage" for f in fs),
            "planned_cells_for_all_folds": sum(f["planned_cells"] for f in fs),
            "confirmed_independent_fresh_groups": 0, "fresh_targets": 0, "effect": None,
        }
    conflicts = [{
        "kind": "inherited_P5_admission_summary_internal_conflict",
        "path": "outputs/task016-p5/v1/admission_summary.json",
        "description": "counts and explicit new_P5 rows say admitted; note says deferred",
        "resolution": "do not use P5 summary as new admission; P5R-C01/C02 use later hash-bound P6 complete references only",
    }]
    for r in metadata_dispositions:
        if "superseded" in r["disposition"] or "excluded" in r["disposition"]:
            conflicts.append({"kind": "inherited_identity_or_primary_source_override", "object_id": r["object_id"],
                              "final_disposition": r["disposition"], "pointer": r["input_pointer"]})
    preregistration = {
        "version": 1, "status": "registered_plan_only_not_executed",
        "approval_scope": TASK, "new_experiment_execution_authorized": False,
        "evidence_tiers": ["retrospective_development", "independent_transfer_confirmation", "formal_TASK017"],
        "comparisons": {
            "current_system": {"arms": {"A": "generic", "B": "frozen_P6_v6", "E": "future_final_enhanced"},
                               "historical_target_exposure_disclosed": True, "independent_claim_allowed": False,
                               "runtime_hashes": None, "registered_panel_hash": None},
            "source_group_development": {"arms": {"A": "generic", "B_g": "existing_method_rebuilt_on_fold_build",
                                                  "E_g": "enhanced_method_built_on_same_fold_build"},
                                        "fold_ids": [f["fold_id"] for f in folds],
                                        "historical_design_bias_remains": True,
                                        "base_generic_training_overlap": "unknown",
                                        "runtime_hashes": None, "registered_panel_hash": None},
        },
        "primary_denominator": "all source/structure-qualified targets under predeclared domain; no E full-reference-match or A/B-failure selection",
        "conditional_scope_applicable_subset": "diagnostic only; cannot replace primary denominator",
        "seeds": [0, 1, 2], "arms_per_comparison": 3,
        "planned_group_matrix_cells_upper_bound": sum(f["planned_cells"] for f in folds),
        "actual_cells": 0, "same_seed_budget_required": True,
        "reference_matching": "complete isomeric canonical precursor component multiset; keep donor, stereo, salts and multiplicity; registered multiple references retained",
        "normal_absent_reference": 0, "not_executed_error_timeout_scientific_result": None,
        "error_policy": "retain registered panel; report failures and valid pairs plus operational success lower bound separately",
        "reporting_units": ["target", "source_group"], "seeds_are_independent_samples": False,
        "metrics": {k: None for k in ("N_gap", "G", "G_over_N_gap", "net_coverage_vs_A", "net_coverage_vs_B",
                                      "reference_loss", "three_seed_node_transfer", "generic_top3_violations")},
        "trace_layers": ["generated", "truncated", "filtered", "created"],
        "independent_confirmation_floor": {"targets_per_axis": 6, "groups_per_axis": 2, "G_per_axis": 3,
                                          "G_over_N_gap": 0.5, "successful_groups": 2,
                                          "reference_loss": 0, "seeds": [0, 1, 2]},
        "unchanged_P7_protocol": True,
        "pending_execution_bindings": ["model_hashes", "code_hashes", "review_hashes", "stock_keys",
                                       "runtime_and_scope_hashes_per_fold", "panel_hash", "numeric_search_budget"],
        "pending_release": ["full source/assay closure and exposure alias consumption",
                            "actual train-only runtime compilation and build/boundary validation",
                            "precise domain/core labels for under-specified strata",
                            "separately approved bounded execution task"],
    }
    decision = {
        "task": TASK, "planning_complete": True, "development_evaluation_complete": False,
        "c_effect_pass": None, "ss_effect_pass": None, "independent_confirmation_complete": False,
        "pipeline_transition_authorized": False, "P7": "Partial/stopped",
        "axis_decisions": {
            family: {
                "decision": "unresolved_closure_or_lineage" if summary[family]["planned_folds"] else "insufficient_data",
                "local_data_support_feasible_folds": summary[family]["data_support_feasible_folds"],
                "global_closure_verified": False, "runtime_rebuild_verified": False,
                "next_action": "one separately approved bounded asset/closure binding and fold compilation task; no new chemistry source discovery",
                "automatic_execution": False,
            } for family in FAMILIES[:2]
        },
        "scientific_reads_new": 0, "model_runs": 0, "MCTS_cells": 0, "new_epochs": 0,
        "R80_recovery": False, "H5_G7_repaired": False,
        "scope": "bounded already-exposed normalized deliveries; not exhaustive project chemistry inventory",
    }
    groups = {
        "source_closure_components": [
            {"closure_id": "P9C-" + sha("|".join(nodes))[:12], "nodes": nodes}
            for nodes in source_components.values()
        ],
        "split_components": [{"split_group_id": group_ids[root], "nodes": nodes} for root, nodes in components.items()],
        "evidence_edges": sorted(edges, key=stable),
        "product_split_guard_edges": sorted(split_extra, key=stable),
        "same_enzyme_or_donor_alone_used_as_edge": False,
        "independence_scope": "existing named edges within admitted historical corpus only",
        "all_project_source_assay_closure_complete": False,
        "independent_fresh_groups": 0,
    }
    return {
        "record_dispositions.jsonl": "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in occurrences + metadata_dispositions),
        "normalized_inventory.jsonl": "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records),
        "measurability_by_stratum.json": {"families": summary, "strata": stratum_rows,
                                         "encoded_occurrence_rows": len(occurrences),
                                         "unique_encoded_contexts": len(records),
                                         "P4_metadata_status_rows": len(metadata_dispositions),
                                         "counts_not_additive_between_versions": True},
        "group_manifest.json": groups,
        "fold_plan.json": {"folds": folds, "effects": None, "execution_authorized": False},
        "asset_exclusion_plan.json": {"current_v6_assets": assets, "historical_asset_deliveries": asset_history,
                                      "auxiliary_reference_surfaces": {
                                          "runtime_instances": "train IDs only per fold",
                                          "applicability_context_and_donor_maps": "rebuild using train IDs; no test reference-derived entries",
                                          "exact_reaction_or_target_indexes": "rebuild from train IDs; exclude held-out group and same product",
                                          "scope_metadata_and_supports": "fixed algorithm with train-only supports; no test-driven relaxation",
                                          "evaluation_reference_table": "test-only scoring surface; forbidden as build input",
                                          "generic_model_training": "unknown overlap; not asserted independently clean",
                                          "unbound_runtime_config_stock_and_review": "no rebuilt hash binding yet; execution blocked"
                                      },
                                      "folds": plans, "runtime_rebuild_verified": False},
        "inherited_conflicts.json": conflicts,
        "evaluation_preregistration.json": preregistration,
        "decision.json": decision,
    }

def enrich(artifacts):
    """Refine the plan with inherited scope membership, never template applicability."""
    records = [json.loads(line) for line in artifacts["normalized_inventory.jsonl"].splitlines()]
    by_id = {r["object_id"]: r for r in records}
    dispositions = [json.loads(line) for line in artifacts["record_dispositions.jsonl"].splitlines()]
    pointers = defaultdict(list)
    for row in dispositions:
        if "inventory_key_available" in row:
            pointers[row["object_id"]].append(row["input_pointer"])
            final = by_id[row["object_id"]]
            row["deduplication_status"] = ("retained_final_representation" if row["input_pointer"] == final["input_pointer"]
                                           else "duplicate_same_object_same_encoded_keys")
            row["retained_representation_pointer"] = final["input_pointer"]
    for row in records:
        row["delivery_pointers"] = pointers[row["object_id"]]
    artifacts["normalized_inventory.jsonl"] = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
    artifacts["record_dispositions.jsonl"] = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in dispositions)
    assets = artifacts["asset_exclusion_plan.json"]["current_v6_assets"]
    scopes = [a for a in assets if a["role"] == "scope_template"]
    membership = defaultdict(list)
    scope_summary = []
    for asset in scopes:
        supports = [by_id[s] for s in asset["support_ids"] if s in by_id]
        keys = {r["reaction_key"] for r in supports if r["reaction_key"]}
        for r in records:
            if r["reaction_key"] in keys:
                membership[r["object_id"]].append(asset["template_id"])
        scope_summary.append({
            "template_id": asset["template_id"], "family": asset["family"],
            "center_class": (asset["declared_scope"] or {}).get("center_class"),
            "support_ids": asset["support_ids"],
            "distinct_acceptors": len({r["acceptor_key"] for r in supports}),
            "source_closure_components": len({r["source_closure_id"] for r in supports}),
            "split_components": len({r["split_group_id"] for r in supports}),
            "split_group_ids": asset["support_group_ids"],
        })
    plans = {f["fold_id"]: f["assets"] for f in artifacts["asset_exclusion_plan.json"]["folds"]}
    for fold in artifacts["fold_plan.json"]["folds"]:
        actions = {a["template_id"]: a for a in plans[fold["fold_id"]]}
        details = []
        for rid in fold["test_object_ids"]:
            inherited = membership[rid]
            surviving = [sid for sid in inherited if actions[sid]["action"] == "rebuild_from_train_only"]
            status = ("inherited_scope_supported_after_holdout" if surviving else
                      "insufficient_build_support_for_inherited_scope" if inherited else
                      "domain_membership_not_bound_in_existing_scope_supports")
            details.append({"object_id": rid, "target_key": by_id[rid]["target_key"],
                            "inherited_scope_ids": inherited, "surviving_scope_ids": surviving,
                            "status": status, "template_applicability_run": False})
        fold["same_family_scope_availability_only"] = fold["data_feasibility_status"]
        fold["scope_domain_plan"] = details
        fold["established_supported_domain_targets"] = len({d["target_key"] for d in details if d["surviving_scope_ids"]})
        fold["domain_unknown_object_ids"] = [d["object_id"] for d in details if not d["inherited_scope_ids"]]
        fold["data_feasibility_status"] = (
            "data_support_feasible" if fold["established_supported_domain_targets"] else
            "unresolved_domain" if fold["domain_unknown_object_ids"] else "insufficient_build_support")
        fold["main_denominator_unchanged_by_domain_diagnostic"] = True
    for stratum in artifacts["measurability_by_stratum.json"]["strata"]:
        scope_ids = sorted({sid for rid in stratum["object_ids"] for sid in membership[rid]})
        stratum["existing_scope_support_membership_ids"] = scope_ids
        stratum["unbound_scope_domain_object_ids"] = [rid for rid in stratum["object_ids"] if not membership[rid]]
        stratum["build_support_by_fold"] = [
            {"fold_id": f["fold_id"], "template_id": a["template_id"],
             "distinct_build_acceptors": a["distinct_build_acceptors"], "action": a["action"]}
            for f in artifacts["fold_plan.json"]["folds"] if set(f["test_object_ids"]) & set(stratum["object_ids"])
            for a in plans[f["fold_id"]] if a["template_id"] in scope_ids]
        stratum["source_assay_closure_global_status"] = "unverified; counts are local known components"
        stratum["inherited_scope_membership_not_test_applicability"] = True
    for family, summary in artifacts["measurability_by_stratum.json"]["families"].items():
        folds = [f for f in artifacts["fold_plan.json"]["folds"] if f["family"] == family]
        summary["same_family_scope_available_folds"] = summary.pop("data_support_feasible_folds")
        summary["data_support_feasible_folds"] = sum(f["data_feasibility_status"] == "data_support_feasible" for f in folds)
        summary["fold_status_counts"] = dict(sorted(Counter(f["data_feasibility_status"] for f in folds).items()))
        summary["established_supported_domain_targets"] = sum(f["established_supported_domain_targets"] for f in folds)
        summary["domain_unknown_contexts"] = sum(len(f["domain_unknown_object_ids"]) for f in folds)
    artifacts["asset_exclusion_plan.json"]["scope_support_summary"] = scope_summary
    decision = artifacts["decision.json"]
    for family, axis in decision["axis_decisions"].items():
        summary = artifacts["measurability_by_stratum.json"]["families"][family]
        axis["local_data_support_feasible_folds"] = summary["data_support_feasible_folds"]
        axis["known_scope_support_insufficiency"] = "all inherited C/SS scopes have one locally known support split component"
        axis["domain_unknown_contexts"] = summary["domain_unknown_contexts"]
        axis["next_action"] = ("stop group-transfer execution for this bounded corpus; optionally design one separately approved "
                               "current-system descriptive evaluation using frozen historical targets; no new source reading")
    prereg = artifacts["evaluation_preregistration.json"]
    prereg["comparisons"]["source_group_development"]["execution_readiness"] = "blocked: no established domain-supported holdout fold"
    prereg["comparisons"]["source_group_development"]["unknown_domain_policy"] = "unknown is not a negative applicability result; retain targets in main panel"
    prereg["comparisons"]["current_system"]["candidate_target_count_by_axis"] = {
        family: summary["distinct_encoded_targets"] for family, summary in artifacts["measurability_by_stratum.json"]["families"].items()
        if family in FAMILIES[:2]}
    prereg["current_system_matrix_cells_upper_bound"] = 9 * sum(prereg["comparisons"]["current_system"]["candidate_target_count_by_axis"].values())
    prereg["both_comparisons_cells_upper_bound"] = prereg["current_system_matrix_cells_upper_bound"] + prereg["planned_group_matrix_cells_upper_bound"]
    return artifacts

def self_check():
    g = Groups()
    g.join("paperA", "paperB"); g.join("paperB", "paperC")
    assert len(g.components()) == 1
    # Same product through different references must not cross a development split.
    h = Groups()
    examples = [("sourceA", "productX", "route1"), ("sourceB", "productX", "route2"),
                ("sourceC", "productY", "route3")]
    by_target = defaultdict(list)
    for source, target, route in examples:
        h.find(source)
        by_target[target].append(source)
    for sources in by_target.values():
        for source in sources[1:]:
            h.join(sources[0], source)
    assert h.find("sourceA") == h.find("sourceB") != h.find("sourceC")
    assert graph_key("") is None and graph_key(None) is None
    assert graph_key("CO") == graph_key("OC")
    return ["transitive_source_closure", "product_target_split_guard", "missing_graph_not_zero", "equivalent_encoded_graph_key"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    data, manifest = read_inputs()
    artifacts = enrich(build(data))
    if args.verify:
        mismatches = []
        for name, value in artifacts.items():
            content = value if isinstance(value, str) else stable(value)
            if (OUT / name).read_text() != content:
                mismatches.append(name)
        if mismatches:
            raise ValueError("same-input recomputation mismatch: " + str(mismatches))
        result = {"deterministic_artifacts_checked": len(artifacts), "mismatches": [],
                  "synthetic_invariants": self_check(), "input_files": len(manifest["files"]),
                  "content_read_bytes": manifest["content_read_bytes"], "rdkit_version": rdBase.rdkitVersion,
                  "independent_review": False, "scope": "local planning recomputation, not chemistry validation"}
        emit("recomputation.json", result)
        print(stable(result))
    else:
        for name, value in artifacts.items():
            if (OUT / name).exists():
                raise ValueError("main inventory already exists: " + name)
            emit(name, value)
        print(stable(artifacts["measurability_by_stratum.json"]["families"]))
        print("FOLDS", len(artifacts["fold_plan.json"]["folds"]))
        print("ASSET_UNRESOLVED", [
            a["template_id"] for a in artifacts["asset_exclusion_plan.json"]["current_v6_assets"]
            if a["unresolved_support_ids"]])
        print("PLANNING_ONLY: no templates constructed, no model loaded, no search executed.")

if __name__ == "__main__":
    main()
