"""Independent P7 verification from physical files; never runs searches.

A passed subset is not task completion. Missing scientific gates stay pending.
All results preserve their raw file bindings and the old failed evaluations.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from rdkit import Chem, rdBase

from scripts.task016_p7_orchestrate import (
    ContractError, ROOT, TASK, now, role_manifest, save_json, sha_file, sha_json,
)


def rows(path):
    values = []
    for line_number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ContractError(f"non-object ledger row: {path}:{line_number}")
            values.append(value)
    return values


def require(condition, message):
    if not condition:
        raise ContractError(message)


def molecular_graph(value):
    require(isinstance(value, str) and bool(value), "empty molecular graph")
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(value)
    require(mol is not None, "invalid molecular graph")
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def reaction_signature(precursors, target):
    # Preserve all raw target charges. Emitted precursor normalization is an
    # explicit historical library rule applied before calling this function.
    side = sorted(molecular_graph(component)
                  for value in precursors for component in value.split("."))
    require(bool(side), "empty precursor side")
    return ".".join(side) + ">>" + molecular_graph(target)


class PhysicalAudit:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        self.inputs = {}
        self.checks = []
        self.historical_substitutions = {}
        self.historical_revision_evidence = None

    def path(self, value):
        p = Path(value)
        p = p if p.is_absolute() else self.root / p
        require(p.resolve().is_relative_to(self.root), "input outside workspace")
        return p

    def _historical_closure_revision(self):
        """One explicit historical source revision, checked against real early bytes."""
        if self.historical_revision_evidence is not None:
            return self.historical_revision_evidence
        old_sha = "7a4d5a46136fca41bf1ed599799d78055e3d71acc098ad64c2d67936b0584b3f"
        new_sha = "1712f7bf914a0c63e0131efa27df80b67e3f308dc860eb638c012209b7bf3a08"
        folder = Path("outputs/task016-p7/v1/code_revision_history/null_reaction_closure_fix_v1")
        correction = self.json(folder / "code_revision_provenance.correction.v2.json",
                               "b5000523ae66b19506afbf6a0e1c0b09471a99d64009abab2f7d65bab950d98d")
        provenance = self.json(correction["corrects_path"], correction["corrects_sha256"])
        require(provenance.get("original_archive_existed_before_edit") is False and
                correction["corrected_project_global_fact"]["original_archive_existed_before_edit"] is True and
                correction["original_provenance_inaccurate_field_preserved_not_overwritten"] is True,
                "historical inaccurate provenance or explicit correction was lost")
        preferred = correction["preferred_original_before_edit_archive"]
        early = self.bind(preferred["path"], old_sha)
        reconstructed = self.bind(folder / "closure_harness.before.reconstituted.py", old_sha)
        after = self.bind(folder / "closure_harness.after.py", new_sha)
        require(early.read_bytes() == reconstructed.read_bytes(),
                "late reconstructed historical bytes differ from actual early archive")
        before_text = early.read_text()
        old_expression = 'row.get("reaction_id",row.get("target_id",str(i)))'
        new_expression = 'row.get("reaction_id") or row.get("target_id") or row.get("exposure_id") or str(i)'
        require(before_text.count(old_expression) == 1 and
                before_text.replace(old_expression, new_expression) == after.read_text(),
                "closure revision contains changes beyond the documented null-ID fix")
        operation_bytes = self.path("operations/events.jsonl").read_bytes()
        operation_lines = operation_bytes.splitlines()
        proofs = []
        for pointer, event_key, line_key in [
            (preferred, "original_operate_write_event", "original_operate_write_event_line"),
            (correction, "actual_helper_edit_operate_event", "actual_helper_edit_operate_event_line"),
        ]:
            index = pointer[line_key]
            require(0 < index <= len(operation_lines), "historical operate proof line missing")
            actual_event = json.loads(operation_lines[index - 1])
            require(all(actual_event.get(k) == v for k, v in pointer[event_key].items()),
                    "actual operate event differs from historical correction")
            proofs.append(dict(line_number=index, actual_event=actual_event))
        require(proofs[0]["actual_event"]["time"] < proofs[1]["actual_event"]["time"] <
                correction["created_at"], "historical archive/edit/correction ordering differs")
        original_v9 = self.json("outputs/task016-p7/v1/verification-v9/independent_verification.json",
                                "ec7f182de1e2fc19d5e311a0e1935bd064c06918559ab5410b2ed13f0395bf50")
        require(any("physical SHA mismatch: scripts/task016_p7_closure_harness.py" ==
                    e.get("error") for e in original_v9["errors"]),
                "original v9 physical SHA failure is not preserved")
        self.historical_revision_evidence = dict(
            original_path="scripts/task016_p7_closure_harness.py", before_sha256=old_sha,
            current_sha256=new_sha, preferred_original_archive=preferred["path"],
            preferred_original_archive_sha256=old_sha,
            actual_operation_proofs=proofs,
            operation_bytes_sha256=__import__("hashlib").sha256(operation_bytes).hexdigest(),
            late_reconstitution_path=str(folder / "closure_harness.before.reconstituted.py"),
            original_inaccurate_field_preserved=True, explicit_correction_verified=True,
            actual_early_archive_existed_before_edit=True, v9_failure_preserved=True,
            current_scientific_stage_not_repaired=True)
        return self.historical_revision_evidence

    def bind(self, value, expected=None):
        p = self.path(value)
        require(p.is_file(), f"physical file missing: {value}")
        actual = sha_file(p)
        rel = str(p.relative_to(self.root))
        prior = self.inputs.get(rel)
        require(prior is None or prior == actual, f"input changed during verification: {value}")
        self.inputs[rel] = actual
        if expected is not None and actual != expected:
            known = (rel == "scripts/task016_p7_closure_harness.py" and
                     expected == "7a4d5a46136fca41bf1ed599799d78055e3d71acc098ad64c2d67936b0584b3f" and
                     actual == "1712f7bf914a0c63e0131efa27df80b67e3f308dc860eb638c012209b7bf3a08")
            require(known, f"physical SHA mismatch: {value}")
            evidence = self._historical_closure_revision()
            self.historical_substitutions[rel + ":" + expected] = dict(
                original_path=rel, expected_historical_sha256=expected,
                current_path_sha256=actual,
                actual_historical_bytes_path=evidence["preferred_original_archive"],
                historical_sha256=expected, current_path_SHA_does_not_equal_historical=True,
                explicit_actual_early_archive_mapping=True)
            return self.path(evidence["preferred_original_archive"])
        return p

    def json(self, value, expected=None):
        return json.loads(self.bind(value, expected).read_text())

    def rows(self, value, expected=None):
        return rows(self.bind(value, expected))

    def mapping(self, mapping, relative_to=None):
        require(isinstance(mapping, dict) and bool(mapping), "empty SHA mapping")
        for path, expected in mapping.items():
            p = (Path(relative_to) / path) if relative_to is not None else path
            self.bind(p, expected)

    def record(self, name, passed, **details):
        check = dict(name=name, status="passed" if passed else "failed",
                     passed=bool(passed), **details)
        self.checks.append(check)
        return check

    def pending(self, name, reason, **details):
        check = dict(name=name, status="pending", passed=False, reason=reason, **details)
        self.checks.append(check)
        return check


def created_actions(raw):
    phases = {p["index"]: p for p in raw.get("phases", [])}
    require(bool(phases), "real MCTS has no physical phases")
    require(all(p.get("engine_class") == "flavoretro.search.SearchTree"
                for p in phases.values()), "unexpected physical engine")
    result = []
    for index, entry in enumerate(raw.get("action_trace", [])):
        if entry.get("stage") != "mcts_action_created":
            continue
        require(isinstance(entry.get("created_node_count"), int)
                and entry["created_node_count"] > 0, "creation has no actual child")
        phase = phases.get(entry.get("phase"))
        require(phase is not None, "creation phase is missing")
        child = entry.get("created_node_index")
        require(isinstance(child, int) and 0 < child < phase["node_count"],
                "creation child index exceeds physical tree node count")
        actual = reaction_signature(entry["precursor_smiles"], entry["target"])
        require(entry.get("signature") == actual,
                "action signature differs from complete physical precursor/target graphs")
        result.append(dict(trace_index=index, phase=entry["phase"],
                           child_index=child, signature=actual,
                           policy=entry.get("policy"), template_id=entry.get("template_id"),
                           source_instance_ids=entry.get("metadata", {}).get(
                               "task016_evidence", {}).get("source_instance_ids", []),
                           exact_seed_instance_match=entry.get("metadata", {}).get(
                               "task016_evidence", {}).get("exact_seed_instance_match") is True))
    return result


def audit_regression(audit, base="outputs/task016-p7/v1/regression"):
    """Recompute old17, frozen P1 IDs and all four corrected charged canaries."""
    from flavoretro.open_glycoside_library import normalize_species
    from flavoretro.reviewed_resources import load_review
    from flavoretro.glycoside_library_v7 import load_registry
    from flavoretro.workspace import active_data

    base = Path(base)
    contract = audit.json(base / "contract.json")
    recovery_base = base / "canary_recovery_v2"
    recovery = audit.json(recovery_base / "contract.json")
    for c in [contract, recovery]:
        audit.mapping(c["files_sha256"])
        audit.mapping(c["models_sha256"])
    audit.mapping(recovery["production_code_sha256"])
    require(recovery["parameters"] == contract["parameters"],
            "revalidation parameters changed")
    require(recovery["domain_binding"] == contract["domain_binding"] ==
            load_registry().binding, "runtime registry binding changed")
    review = load_review()
    require(recovery["review_binding"] == contract["review_binding"] ==
            review.binding, "review binding changed")
    require(recovery["stock_keys"] == contract["stock_keys"] == sorted(review.keys),
            "frozen candidate stock keys changed")

    old_contract = audit.json("outputs/task016-p6/v1/experiment_contract.json")
    require(contract["references"] == old_contract["references"],
            "legacy reference universe changed")
    require(len(contract["references"]) == 17, "legacy reference count differs from17")
    p1_metrics = audit.json("outputs/task016-p1/v2/metrics.json")
    p1_source = audit.rows("outputs/task016-p1/v2/holdout_views.jsonl")
    gains = set(p1_metrics["actual_mcts"]["gain_targets"])
    p1_expected = [r for r in p1_source if r["target"] in gains]
    require(len(p1_expected) == 7, "P1 historical successful ID universe differs from7")
    require({r["instance_id"] for r in p1_expected} ==
            {r["instance_id"] for r in contract["P1_success_canaries"]},
            "P1 successful frozen source IDs changed")
    for old in p1_expected:
        projected = next(r for r in contract["P1_success_canaries"]
                         if r["instance_id"] == old["instance_id"])
        require(projected["target"] == old["target"] and
                projected["reference_precursors"] == old["reference_precursors"] and
                projected["reference_signatures"] == [old["reference_signature"]],
                "P1 historical reference projection changed")

    task_source = audit.rows("outputs/task016/v1/instances.jsonl")
    require(len(task_source) == 4, "original TASK016 source ID universe differs from4")
    by_id = {r["instance_id"]: r for r in task_source}
    require(len(by_id) == 4 and set(by_id) ==
            {r["instance_id"] for r in recovery["references"]} ==
            {r["instance_id"] for r in contract["TASK016_exact_canaries"]},
            "exact canary source IDs changed")
    corrected = {}
    for reference in recovery["references"]:
        original = by_id[reference["instance_id"]]
        require({k: v for k, v in reference.items() if k != "expected_trace_signature"} ==
                original, "corrected canary original source record changed")
        precursors = [normalize_species(p)["normalized"]
                      for p in original["reference_precursors"]]
        correct = reaction_signature(precursors, original["target"])
        require(correct == reference["expected_trace_signature"],
                "corrected trace signature does not preserve raw source target charge")
        corrected[reference["instance_id"]] = correct

    unique = {r["target"] for r in contract["references"] +
              contract["TASK016_exact_canaries"] + contract["P1_success_canaries"]}
    expected_matrix = {(t, seed) for t in unique for seed in [0, 1, 2]}
    require(len(expected_matrix) == 63 and
            {(r["target"], r["seed"]) for r in contract["matrix"]} == expected_matrix
            and len(contract["matrix"]) == 63, "original historical matrix not complete63")
    expected_recovery = {(r["instance_id"], seed)
                         for r in task_source for seed in [0, 1, 2]}
    require({(r["instance_id"], r["seed"]) for r in recovery["matrix"]} ==
            expected_recovery and len(recovery["matrix"]) == 12,
            "all affected4x3 revalidation cells were not frozen")
    sources = audit.json("metadata/sources.json")
    expected_assets = {r["source_path"]: r["sha256"]
                       for r in sources["files"] if r["role"] == "external_model"}
    active_folder, active_manifest, active_pointer = active_data()
    audit.bind("metadata/active.json")
    audit.bind(active_folder / "manifest.json", active_pointer["manifest_sha256"])
    source_sha = audit.inputs["metadata/sources.json"]
    config_sha = sha_file(audit.bind("configs/search.json"))
    raw_by_cell = {}
    recovery_by_cell = {}
    run_ids = set()
    physical = []

    for folder, c, cells, key_names in [
        (base, contract, raw_by_cell, ("target", "seed")),
        (recovery_base, recovery, recovery_by_cell, ("instance_id", "seed")),
    ]:
        observations = audit.rows(folder / "observations.jsonl")
        require(len(observations) == len(c["matrix"]), "raw observation matrix incomplete")
        for observation in observations:
            key = tuple(observation[k] for k in key_names)
            require(key not in cells, "duplicate historical raw cell")
            rid = observation["run_id"]
            require(rid not in run_ids, "same physical run reused across cells")
            run_ids.add(rid)
            raw = audit.json(observation["result_path"], observation["result_sha256"])
            manifest = audit.json(observation["manifest_path"], observation["manifest_sha256"])
            run_folder = audit.path(observation["result_path"]).parent
            audit.mapping(manifest["files"], relative_to=run_folder)
            request = audit.json(run_folder / "request.json")
            require(raw["run_id"] == manifest["run_id"] == rid,
                    "historical raw run identity differs")
            require(raw["status"] == manifest["status"] == observation["status"] == "ok",
                    "historical physical run failed")
            require(raw["execution_source"] == "live_aizynthfinder_mcts" and
                    observation.get("synthetic_fixture") is False,
                    "historical fixture is not genuine MCTS")
            require(request == raw["request"], "physical request and result request differ")
            require(request["smiles"] == observation["target"] and
                    request["seed"] == observation["seed"] and
                    request["candidate_stock"] is True and
                    request["glycoside_expansion"] is True and
                    request["glycoside_library_version"] == "v7",
                    "actual search target, seed, library or stock changed")
            require(all(request[k] == v for k, v in c["parameters"].items()),
                    "actual request parameters differ from frozen contract")
            require(raw["assets"] == expected_assets, "physical source model assets differ")
            require(raw["source_manifest_sha256"] == source_sha and
                    raw["config_sha256"] == config_sha and
                    raw["resource_manifest_sha256"] == active_pointer["manifest_sha256"] and
                    raw["resources_sha256"] == active_manifest["records_sha256"],
                    "physical source/resources/config binding differs")
            require(raw["domain_binding"] == manifest["domain_binding"] ==
                    c["domain_binding"] and
                    raw["review_binding"] == manifest["review_binding"] ==
                    c["review_binding"], "physical registry or review binding differs")
            require(all(raw["code"].get(p) == h for p, h in c.get(
                "production_code_sha256", c["files_sha256"]).items()
                if p.startswith("flavoretro/")), "physical production code differs")
            for phase in raw["phases"]:
                require(phase["seed"] == observation["seed"] and
                        phase["budget"] == {k: c["parameters"][k] for k in
                                            ["seconds", "iterations", "depth", "branching", "nodes"]},
                        "physical engine seed/budget differs")
                algorithm = phase["effective_config"]["search"]["algorithm_config"]
                require(algorithm["protect_generic_actions"] == 3 and
                        algorithm["policy_weights"] == {"glycoside": 1.0, "ringbreaker": .65,
                                                         "uspto": 1.0},
                        "production policy or generic protection changed")
            actions = created_actions(raw)
            cells[key] = dict(observation=observation, actions=actions)
            physical.append(dict(run_id=rid, folder=str(folder),
                                 result_path=observation["result_path"],
                                 result_sha256=observation["result_sha256"],
                                 actual_created_actions=len(actions),
                                 distinct_created_signatures=len({e["signature"] for e in actions}),
                                 seed=observation["seed"]))
    require(set(raw_by_cell) == expected_matrix and
            set(recovery_by_cell) == expected_recovery, "physical matrix cell universe mismatch")

    def reference_checks(references, cell_rows, recovery_mode=False):
        result = []
        for reference in references:
            seed_rows = []
            for seed in [0, 1, 2]:
                key = (reference["instance_id"], seed) if recovery_mode else (reference["target"], seed)
                actual = cell_rows[key]
                expected = ([corrected[reference["instance_id"]]] if recovery_mode
                            else reference["reference_signatures"])
                matched = [entry for entry in actual["actions"] if entry["signature"] in expected]
                created = set(expected) <= {entry["signature"] for entry in matched}
                exact = (any(entry["exact_seed_instance_match"] and
                             reference["instance_id"] in entry["source_instance_ids"]
                             for entry in matched) if recovery_mode else None)
                seed_rows.append(dict(seed=seed, run_id=actual["observation"]["run_id"],
                                      complete_reference_created=created,
                                      exact_original_source_ID_match=exact,
                                      raw_creation_pointers=matched))
            result.append(dict(instance_id=reference.get("instance_id"),
                               target=reference["target"], by_seed=seed_rows,
                               all_three_seed_created=all(r["complete_reference_created"] and
                                                          (r["exact_original_source_ID_match"]
                                                           is not False) for r in seed_rows)))
        return result

    legacy = reference_checks(contract["references"], raw_by_cell)
    p1 = reference_checks(contract["P1_success_canaries"], raw_by_cell)
    old_exact = reference_checks(contract["TASK016_exact_canaries"], raw_by_cell)
    corrected_old_refs = [dict(r, reference_signatures=[corrected[r["instance_id"]]])
                          for r in contract["TASK016_exact_canaries"]]
    actual_original_exact = reference_checks(corrected_old_refs, raw_by_cell)
    recovered = reference_checks(recovery["references"], recovery_by_cell, True)
    prior = audit.json("outputs/task016-p6/v1/e_regression.json")
    previous = {r["target"]: r for r in prior["checks"]}
    require(set(previous) == {r["target"] for r in legacy}, "old17 comparison universe changed")
    losses = [r["target"] for r in legacy if previous[r["target"]]["all_three_seed_created"]
              and not r["all_three_seed_created"]]
    old_validation = audit.json(base / "validation.json")
    require(old_validation["passed"] is False, "old failed evaluation was not preserved")
    passed = not losses and all(r["all_three_seed_created"] for r in p1 + recovered)
    result = dict(passed=passed, actual_original_MCTS=63, actual_revalidation_MCTS=12,
                  unique_physical_runs=len(run_ids), synthetic_fixture=0,
                  old17_checks=legacy, P1_frozen_success_checks=p1,
                  original_TASK016_wrong_evaluator_checks=old_exact,
                  original_TASK016_corrected_physical_trace_checks=actual_original_exact,
                  recovery_TASK016_complete4x3_checks=recovered,
                  new_reference_loss=losses, physical_runs=physical,
                  old_failed_evaluation_preserved=True,
                  correction_cause="Old evaluator normalized charged original targets; physical trace target retains raw original target charge. Precursor normalization remains the pre-existing rule.",
                  source_original_ID_universe_preserved=True,
                  scientific_transfer_claim=False)
    audit.record("independent_75_historical_physical_runs", passed,
                 unique_physical_runs=len(run_ids), old17_new_reference_loss=len(losses),
                 P1_canaries_retained=sum(r["all_three_seed_created"] for r in p1),
                 corrected_exact_canaries_retained=sum(r["all_three_seed_created"]
                                                       for r in recovered))
    return result


def audit_search_budget(audit, base):
    """All reservations count, including failed and mislabelled engineering runs."""
    ledger = audit.rows(Path(base) / "run_ledger.jsonl")
    starts, terminals = {}, {}
    for row in ledger:
        rid = row.get("run_id")
        require(isinstance(rid, str) and rid, "reservation has no run ID")
        destination = starts if row.get("phase") == "started" else terminals
        require(rid not in destination, "duplicate reservation or terminal")
        destination[rid] = row
    limits = {"p7_C_validation": 81, "p7_SS_validation": 81,
              "p7_legacy_canary": 90, "p7_engineering": 60,
              "p7_revalidation": 252}
    require(all(r.get("purpose") in limits for r in starts.values()),
            "unknown search budget category")
    require(set(terminals) <= set(starts), "unreserved terminal search")
    counts = Counter(r["purpose"] for r in starts.values())
    require(len(starts) <= 600 and all(counts[k] <= v for k, v in limits.items()),
            "approved hard search budget exceeded")
    decisions = []
    for rid, end in terminals.items():
        start = starts[rid]
        require(start["purpose"] == end["purpose"], "terminal category differs")
        manifest = Path(end["manifest"])
        if end.get("execution_source") == "live_aizynthfinder_mcts":
            raw = audit.json(manifest.with_name("result.json"))
            physical_manifest = audit.json(manifest)
            audit.mapping(physical_manifest["files"], relative_to=manifest.parent)
            require(raw["run_id"] == physical_manifest["run_id"] == rid and
                    raw["execution_source"] == "live_aizynthfinder_mcts" and
                    bool(raw.get("phases")) and all(
                        p["engine_class"] == "flavoretro.search.SearchTree"
                        for p in raw["phases"]), "real search physical provenance absent")
            classification = "real_MCTS"
        elif (start.get("synthetic_fixture") is True and
              end.get("synthetic_fixture") is True and
              start["purpose"] == "p7_engineering" and
              manifest.is_absolute() and manifest.is_relative_to("/tmp")):
            classification = "synthetic_fixture"
        else:
            classification = "failed_real_attempt_or_unproven"
        decisions.append(dict(run_id=rid, purpose=start["purpose"],
                              classification=classification,
                              start_fixture_flag=start.get("synthetic_fixture"),
                              terminal_fixture_flag=end.get("synthetic_fixture"),
                              original_flags_preserved=True))
    classes = Counter(r["classification"] for r in decisions)
    result = dict(reserved=len(starts), terminal=len(terminals),
                  pending_ids=sorted(set(starts) - set(terminals)),
                  categories=dict(counts), limits=limits, total_limit=600,
                  effective_classes=dict(classes), decisions=decisions,
                  all_reservations_counted=True,
                  classification_from_physical_result_not_suite_flag=True)
    audit.record("search_hard_budget", True, reserved=len(starts),
                 real_MCTS=classes["real_MCTS"], fixture=classes["synthetic_fixture"],
                 pending=len(result["pending_ids"]))
    if result["pending_ids"]:
        audit.pending("search_terminal_conservation",
                      "Reserved searches have no terminal ledger record.",
                      run_ids=result["pending_ids"])
    else:
        audit.record("search_terminal_conservation", True)
    return result


def audit_source_budget(audit, base):
    """De-duplicate header snapshots, while keeping each real retry attempt."""
    import hashlib

    base = Path(base)
    candidates = sorted(p for p in audit.path(base).rglob("*")
                        if p.is_file() and p.suffix in (".json", ".jsonl")
                        and (p.name == "http_ledger.jsonl" or "http_attempt" in p.name))
    attempts, snapshots, rows_seen = {}, [], 0
    for path in candidates:
        records = audit.rows(path) if path.suffix == ".jsonl" else audit.json(path)
        require(isinstance(records, list), "HTTP ledger is not a row list")
        for row in records:
            require(all(k in row for k in ("url", "started_at", "path", "sha256", "bytes")),
                    "HTTP attempt missing physical accounting fields")
            require(isinstance(row["bytes"], int) and row["bytes"] >= 0,
                    "invalid HTTP physical bytes")
            identity = (row["url"], row["started_at"], row["path"])
            rows_seen += 1
            if identity in attempts:
                previous = attempts[identity]
                require(all(previous[k] == row[k] for k in ("url", "started_at",
                                                           "path", "sha256", "bytes")),
                        "same HTTP identity has conflicting physical data")
                snapshots.append(dict(path=str(path.relative_to(audit.root)),
                                      url=row["url"], started_at=row["started_at"],
                                      raw_path=row["path"]))
            else:
                attempts[identity] = row
    # Actual source_http operation events independently expose C requests.
    operation_path = audit.path("operations/events.jsonl")
    operation_bytes = operation_path.read_bytes()
    operation_sha = hashlib.sha256(operation_bytes).hexdigest()
    operation_records = [json.loads(line) for line in operation_bytes.splitlines() if line]
    operation_requests = [r for r in operation_records
                          if r.get("task") == TASK and r.get("action") == "source_http"]
    missing_events = []
    for row in operation_requests:
        identity = (row["url"], row["started_at"], row["path"])
        if identity not in attempts:
            attempts[identity] = row
            missing_events.append(dict(attempt_id=row.get("attempt_id"),
                                       raw_path=row["path"], evidence="source_http operation"))
    attempt_rows = list(attempts.values())
    raw_paths = set()
    family = {"C": Counter(), "SS": Counter(), "root": Counter()}
    for row in attempt_rows:
        if row["path"] is not None:
            raw = audit.bind(row["path"], row["sha256"])
            require(raw.stat().st_size == row["bytes"], "HTTP recorded physical size differs")
            raw_paths.add(str(raw.relative_to(audit.root)))
        parts = Path(row["path"] or "").parts
        which = ("SS" if "SS" in parts else "C" if "C" in parts else "root")
        family[which]["HTTP"] += 1
        family[which]["bytes"] += row["bytes"]
        kind = row.get("kind", row.get("role"))
        family[which]["article_versions"] += int(kind in ("article_version", "xml"))
        family[which]["attachments"] += int(kind == "attachment")
        family[which]["failed"] += int(bool(row.get("error")) or
                                      row.get("status_code") != 200)
    unledgered_root = []
    for raw in audit.path("data/raw/task016-p7/root").glob("*"):
        if raw.is_file() and str(raw.relative_to(audit.root)) not in raw_paths:
            audit.bind(raw)
            unledgered_root.append(str(raw.relative_to(audit.root)))
    require(not unledgered_root, "root raw source acquisition missing HTTP accounting")
    total = Counter()
    for value in family.values():
        total.update(value)
    require(total["HTTP"] <= 8000 and total["bytes"] <= 8 * 1024**3 and
            total["article_versions"] <= 400 and total["attachments"] <= 800,
            "global source hard budget exceeded")
    for name in ("C", "SS"):
        require(family[name]["HTTP"] <= 2500 and family[name]["bytes"] <= 2 * 1024**3
                and family[name]["article_versions"] <= 120 and
                family[name]["attachments"] <= 200,
                f"{name} family hard source budget exceeded")
    # Actual HTTP plans must be registered before their matching requests.
    query_checks = []
    c_plan_path = base / "C/acquisition_plan.jsonl"
    c_plan = audit.rows(c_plan_path)
    c_requests = [r for r in attempt_rows if "C" in Path(r.get("path") or "").parts
                  and isinstance(r.get("attempt_id"), str)]
    require(Counter(r["attempt_id"] for r in c_plan) ==
            Counter(r["attempt_id"] for r in c_requests),
            "C preregistered HTTP plan != unique executed attempts")
    c_request_keys = Counter((r["attempt_id"], r["url"], r["started_at"]) for r in c_requests)
    c_plan_keys = Counter((r["attempt_id"], r["url"], r["registered_at"]) for r in c_plan)
    require(c_request_keys == c_plan_keys, "C actual composite preregistration identity mismatch")
    collision_ids = [k for k,v in Counter(r["attempt_id"] for r in c_requests).items() if v > 1]
    c_collisions = [dict(attempt_id=k, actual_requests=[dict(url=r["url"], started_at=r["started_at"],
                                                            path=r["path"], sha256=r["sha256"])
                                                       for r in c_requests if r["attempt_id"] == k])
                    for k in collision_ids]
    resolution_verified = False
    if c_collisions:
        resolution_path = base / "C/E01/http_audit/request_id_collision_v1/request_id_alias_resolution.json"
        if audit.path(resolution_path).is_file():
            resolution = audit.json(resolution_path)
            audit.mapping(resolution["immutable_snapshot_files_sha256"])
            frozen_plan = audit.rows(resolution_path.parent / "acquisition_plan.snapshot.jsonl")
            frozen_http = audit.rows(resolution_path.parent / "http_ledger.snapshot.jsonl")
            require(resolution.get("original_request_id_conservation_passed") is False and
                    resolution.get("original_request_id_uniqueness_passed") is False and
                    resolution.get("retroactive_plan_pass_claimed") is False and
                    resolution.get("human_reviewed") is False,
                    "alias resolution erases original ID failure")
            expected_collisions = {(r["attempt_id"], r["url"], r["started_at"], r["path"])
                                   for r in c_requests if r["attempt_id"] in collision_ids}
            actual_aliases, alias_ids = set(), set()
            for alias in resolution["aliases"]:
                ledger_row = frozen_http[alias["original_ledger_line"] - 1]
                plan_row = frozen_plan[alias["original_plan_line"] - 1]
                require(sha_json(ledger_row) == alias["original_ledger_row_sha256"] and
                        sha_json(plan_row) == alias["original_plan_row_sha256"],
                        "collision alias original row SHA differs")
                require((ledger_row["attempt_id"], ledger_row["url"], ledger_row["started_at"]) ==
                        (plan_row["attempt_id"], plan_row["url"], plan_row["registered_at"]) ==
                        (alias["original_request_id"], alias["url"], alias["started_at"]) and
                        alias["registered_at"] == plan_row["registered_at"] and
                        alias["raw_path"] == ledger_row["path"] and
                        alias["raw_sha256"] == ledger_row["sha256"] and
                        alias["bytes"] == ledger_row["bytes"] and
                        alias["HTTP_status"] == ledger_row["status_code"] and
                        alias["budget_HTTP_count"] == 1,
                        "collision alias does not preserve physical event")
                key = (alias["original_request_id"], alias["url"], alias["started_at"],
                       alias["raw_path"])
                require(key not in actual_aliases and alias["physical_event_alias"] not in alias_ids,
                        "collision aliases merge two actual events")
                actual_aliases.add(key)
                alias_ids.add(alias["physical_event_alias"])
                audit.bind(alias["raw_path"], alias["raw_sha256"])
            require(actual_aliases == expected_collisions, "collision alias event universe differs")
            resolution_verified = True
            audit.record("C_HTTP_original_ID_collision_preserved", True,
                         original_ID_conservation=False, original_ID_uniqueness=False,
                         collisions=c_collisions, original_rows_preserved=True)
            audit.record("C_HTTP_collision_physical_alias_resolution", True,
                         physical_events=len(actual_aliases), budget_HTTP_count=len(actual_aliases),
                         resolution_path=str(resolution_path))
        else:
            audit.record("C_HTTP_unique_registered_request_IDs", False,
                         collisions=c_collisions, all_real_attempts_counted=True,
                         original_rows_preserved=True)
    else:
        audit.record("C_HTTP_unique_registered_request_IDs", True)
    query_checks.append(dict(namespace="C/acquisition_plan", planned=len(c_plan),
                             executed=len(c_requests), passed=True))
    for folder in [base / "SS", base / "SS/pubchem_design", base / "SS/pubchem_supports2"]:
        plan = audit.rows(folder / "query_plan.jsonl")
        executed = audit.rows(folder / "query_execution.jsonl")
        require(Counter(r["query_id"] for r in plan) ==
                Counter(r["query_id"] for r in executed),
                "SS preregistered query plan != executed + skipped")
        http = [r for r in attempt_rows if r.get("ledger_namespace") == str(folder)]
        planned = {r["query_id"]: r for r in plan}
        for row in http:
            require(row["query_id"] in planned and
                    planned[row["query_id"]]["registered_at"] <= row["started_at"],
                    "SS HTTP lacks earlier query registration")
        query_checks.append(dict(namespace=str(folder), planned=len(plan),
                                 executed=len(executed), physical_HTTP=len(http), passed=True))
    result = dict(unique_HTTP_attempts=len(attempt_rows), raw_ledger_rows=rows_seen,
                  excluded_duplicate_header_snapshots=snapshots,
                  independently_checked_C_operation_requests=len(operation_requests),
                  operations_snapshot_sha256=operation_sha,
                  operations_snapshot_bytes=len(operation_bytes),
                  operation_http_records=operation_requests,
                  operation_only_requests=missing_events,
                  root_unledgered_raw_files=unledgered_root,
                  C_original_request_ID_collisions=c_collisions,
                  C_original_ID_conservation=not bool(c_collisions),
                  C_physical_alias_resolution_verified=resolution_verified,
                  families={k: dict(v) for k, v in family.items()}, total=dict(total),
                  raw_SHA_and_bytes_verified=True,
                  actual_plan_execution_checks=query_checks,
                  discovery_disposition_accounting_not_inferred_from_HTTP=True)
    audit.record("source_physical_budget_and_HTTP_preregistration", True,
                 unique_HTTP_attempts=len(attempt_rows), total_bytes=total["bytes"],
                 root_requests=family["root"]["HTTP"],
                 snapshot_duplicates=len(snapshots))
    # Discovery query rows need their own denominator and dispositions; HTTP
    # equality alone never establishes source chemical completeness.
    audit.pending("all_discovery_disposition_conservation",
                  "HTTP plans checked; all source discovery/qualification disposition universes still require their explicit family accounting.")
    return result


def audit_ss_effective_exposure_resolution(audit, original, wrapper):
    """Consume a separately preserved correction, never rewrite the original decision."""
    from scripts.task016_p7_closure_harness import assert_fresh, source_tokens

    path = Path("outputs/task016-p7/v1/epochs/SS-E01/closure_resolution_v1/"
                "effective_permanent_exposure_manifest.json")
    if not audit.path(path).is_file():
        return original, None
    manifest = audit.json(path)
    require(manifest.get("task") == TASK and manifest.get("family") == "SS"
            and manifest.get("epoch_id") == "SS-E01" and manifest.get("human_reviewed") is False
            and manifest.get("approval_type") == "agent_delegated"
            and manifest.get("scope_or_scientific_outcome_changed") is False
            and manifest.get("new_holdout_qualified") == 0,
            "SS effective exposure correction governance differs")
    audit.mapping(manifest["files_sha256"])
    decision_pointer = manifest["original_closed_epoch_decision_pointer"]
    decision = audit.json(decision_pointer["path"], decision_pointer["sha256"])
    require(decision.get("status") == "development_epoch_incomplete"
            and decision.get("epoch_id") == "SS-E01"
            and manifest["created_at"] > decision["actual_decision_at"],
            "SS exposure resolution reopens or backdates the epoch")
    original_wrapper_pointer = manifest["original_permanent_exposure_wrapper"]
    physical_wrapper = audit.json(original_wrapper_pointer["path"],
                                  original_wrapper_pointer["sha256"])
    require(physical_wrapper == wrapper
            and decision["permanent_exposure_manifest"] == original_wrapper_pointer,
            "SS effective wrapper does not bind the original decision")
    original_pointer = manifest["original_permanent_exposure_ledger"]
    original_bound = audit.rows(original_pointer["path"], original_pointer["sha256"])
    require(original_bound == original, "SS correction original ledger differs")
    resolution_pointer = manifest["resolution_pointer"]
    resolution = audit.json(resolution_pointer["path"], resolution_pointer["sha256"])
    require(resolution.get("task") == TASK and resolution.get("human_reviewed") is False
            and resolution.get("family") == "SS" and resolution.get("epoch_id") == "SS-E01"
            and resolution.get("changed_chemical_rows") == 1
            and resolution.get("scientific_qualified") == 0
            and resolution.get("source_graphs_or_reaction_graphs_guessed") == 0
            and resolution.get("source_evidence_qualification_granted") is False,
            "SS alias correction silently qualifies or fabricates chemistry")
    require(resolution["original_ledger_pointer"]["path"] == original_pointer["path"]
            and resolution["original_ledger_pointer"]["sha256"] == original_pointer["sha256"]
            and resolution["original_ledger_pointer"]["line"] == 117,
            "SS alias correction original line/SHA differs")
    effective_pointer = manifest["effective_permanent_exposure_ledger"]
    require(resolution["effective_ledger_pointer"] == effective_pointer,
            "SS resolution and effective wrapper ledger differ")
    effective = audit.rows(effective_pointer["path"], effective_pointer["sha256"])
    require(len(original) == len(effective) == manifest["rows"] == 119,
            "SS effective exposure loses original rows")
    target = original[116]
    require(target["exposure_id"] == "SS-E01:historical-design-reread:E02-D05"
            and target["closure_tokens"] == [],
            "SS alias correction original empty row differs")
    support = target["source_support"][0]
    require(resolution["original_source_support"] == support,
            "SS alias correction is not source-supported")
    audit.bind(support["raw_path"], support["raw_sha256"])
    token = resolution["added_closure_token"]
    require(source_tokens({"source_id": support["source_id"]}) == {token}
            and token == "doi:" + resolution["explicit_source_DOI"].lower(),
            "SS explicit source DOI parser disagrees with registered correction")
    require(effective[116].get("target_graph") is None
            and effective[116].get("reaction_signature") is None,
            "SS source-only correction guessed target/reaction graphs")
    schema_corrections = []
    for index, (before, after) in enumerate(zip(original, effective), 1):
        require(before["exposure_id"] == after["exposure_id"],
                "SS effective exposure changes ID/order")
        expected = dict(before)
        if "exposure_type" not in before:
            expected["exposure_type"] = wrapper["exposure_type"]
            schema_corrections.append(index)
        if index == 117:
            expected["closure_tokens"] = [token]
            pointer = after.get("closure_resolution_pointer")
            require(isinstance(pointer, dict)
                    and pointer.get("path") == resolution_pointer["path"]
                    and pointer.get("source_original_ledger_line") == index
                    and decision["actual_decision_at"] < pointer["resolved_at"] <= manifest["created_at"],
                    "SS effective row correction pointer/time differs")
            expected["closure_resolution_pointer"] = pointer
        require(expected == after, "SS effective exposure changes unapproved row fields")
    require(schema_corrections == list(range(113, 120)),
            "SS exposure type normalization edits unknown rows")
    aliases = resolution["alias_rejection_validation"]
    require(len(aliases) == 5, "SS correction alias probe denominator differs")
    probe_records = []
    for record in aliases:
        candidate = record["candidate_source_alias"]
        try:
            # Isolate corrected117 so another existing source row cannot mask
            # an ineffective correction or DOI parser regression.
            assert_fresh(candidate, [effective[116]])
        except ContractError as exc:
            require("intersects holdout" in str(exc) and token in str(exc),
                    "SS alias probe failed for another contract reason")
            probe_records.append(dict(candidate=candidate, actual_rejection=str(exc)))
        else:
            raise ContractError("SS corrected original source alias became fresh")
    parser = resolution["source_parser_code_pointer"]
    audit.bind(parser["path"], parser["sha256"])
    return effective, dict(effective_manifest_path=str(path),
                           effective_manifest_sha256=sha_file(audit.path(path)),
                           original_empty_line117_preserved=True,
                           physical_source_binding_verified=True,
                           corrected_chemical_rows=1, normalized_exposure_type_rows=7,
                           missing_human_and_eligibility_fields_unchanged=True,
                           isolated_actual_alias_rejection_probes=probe_records,
                           unique_alias_probes=len({sha_json(r["candidate_source_alias"]) for r in aliases}),
                           scientific_source_qualification_granted=False)


def audit_ss_permanent_exposure(audit, package, wrapper):
    """Verify the SS export schema without turning missing historical flags into false."""
    from scripts.task016_p7_closure_harness import assert_fresh, canonical

    require(package.get("task_id") == TASK and package.get("approval") == "agent_delegated"
            and wrapper.get("human_reviewed") is False,
            "SS exposure export/wrapper governance differs")
    require(package.get("A5_final_outputs_decoded") is False
            and package.get("scope_modified") is False
            and package.get("scientific_model_runs") == 0,
            "SS exposure export claims prohibited reads/changes")
    audit.mapping(package["input_file_sha256"])
    outputs = package["output_bindings"]
    require(isinstance(outputs, list) and len(outputs) == 9,
            "SS export output inventory schema differs")
    by_name = {}
    for pointer in outputs:
        audit.bind(pointer["path"], pointer["sha256"])
        name = Path(pointer["path"]).name
        require(name not in by_name, "duplicate SS exposure output")
        by_name[name] = pointer

    def export_rows(name):
        pointer = by_name[name]
        return audit.rows(pointer["path"], pointer["sha256"])

    groups = {
        "candidate": export_rows("candidate_chemical_exposure_28.jsonl"),
        "source": export_rows("source_chemical_exposure_15.jsonl"),
        "auxiliary": export_rows("auxiliary_actual_chemical_observations.jsonl"),
        "historical": export_rows("historical_design_rereads.jsonl"),
    }
    permanent = export_rows("permanent_chemical_exposure_ledger.jsonl")
    expected_counts = {"candidate": 28, "source": 15, "auxiliary": 69, "historical": 7}
    require({k: len(v) for k, v in groups.items()} == expected_counts,
            "SS exposure group denominator differs")
    combined = [row for values in groups.values() for row in values]
    require(Counter(sha_json(r) for r in permanent) ==
            Counter(sha_json(r) for r in combined) and len(permanent) == 119,
            "SS permanent ledger does not conserve all original rows")
    ids = [r["exposure_id"] for r in permanent]
    require(len(set(ids)) == len(ids), "duplicate SS permanent exposure ID")
    permanent, correction = audit_ss_effective_exposure_resolution(audit, permanent, wrapper)
    require(all(r.get("development_exposed") is True
                and r.get("eligible_for_fresh_holdout") is False
                and isinstance(r.get("closure_tokens"), list)
                and bool(r["closure_tokens"]) for r in permanent),
            "SS exposure row can enter future fresh or lacks closure tokens")
    # These seven historical/source rows predate the standard role schema.
    # Missing is recorded as unknown. It is never interpreted as human review.
    missing = {field: sum(field not in r for r in permanent)
               for field in ["evidence_eligible", "human_reviewed", "family", "source_tokens"]}
    require(missing == {"evidence_eligible": 7, "human_reviewed": 7,
                        "family": 7, "source_tokens": 7},
            "SS retained historical schema absence denominator differs")
    require(all(r["human_reviewed"] is False for r in permanent if "human_reviewed" in r),
            "SS exposure explicitly claims human review")
    require(sum(r.get("qualified_reaction_reference") is True for r in permanent) == 0,
            "SS exposure export silently qualifies source reactions")
    require(Counter(r["disposition"] for r in groups["candidate"]) ==
            Counter({"rejected": 18, "deferred": 10}),
            "SS original 28 candidate dispositions differ")
    require(len({r["source_id"] for r in groups["source"]}) == 15,
            "SS source-ID universe does not conserve 15 sources")
    for row in permanent:
        if row.get("donor_actual_assay_evidence_present") is False:
            require(row.get("reaction_signature") is None
                    and not any(t.startswith(("reaction:", "acceptor-donor-site:"))
                                for t in row["closure_tokens"]),
                    "identity-only SS donor created a full reaction closure")
        for pointer in row.get("origins", []):
            audit.bind(pointer["path"], pointer["sha256"])

    inventory = export_rows("raw_and_review_artifact_inventory.jsonl")
    require(len(inventory) == 150, "SS physical inventory denominator differs")
    for pointer in inventory:
        path = audit.bind(pointer["path"], pointer["sha256"])
        require(path.stat().st_size == pointer["bytes"],
                "SS inventory byte count differs")
    partial_pointer = by_name["unresolved_partial_identity_index.json"]
    partial = audit.json(partial_pointer["path"], partial_pointer["sha256"])
    tokens = partial["tokens"]
    require(isinstance(tokens, dict) and len(tokens) == 78,
            "SS unresolved partial identity index denominator differs")
    require(all(isinstance(token, str) and token and isinstance(refs, list)
                and refs and set(refs).issubset(ids) for token, refs in tokens.items()),
            "SS partial identity points outside preserved exposure rows")
    row_tokens = {t for r in permanent for t in r.get("unresolved_partial_identity_tokens", [])}
    require(row_tokens.issubset(tokens), "SS partial row identity missing from index")
    products = {canonical(r["product_smiles"]) for r in permanent
                if isinstance(r.get("product_smiles"), str) and r["product_smiles"]}
    require(len(products) == 9, "SS known product target denominator differs")
    blocked = []
    for i, product in enumerate(sorted(products)):
        renamed = {"source_id": "A11-new-source", "reaction_id": "A11-new-reaction-" + str(i),
                   "product_smiles": product}
        try:
            assert_fresh(renamed, permanent)
        except ContractError:
            blocked.append(product)
        else:
            raise ContractError("SS known product became fresh after renaming source/reaction")
    require(wrapper["chemical_rows"] == len(permanent)
            and wrapper["evidence_eligible_field_absent_rows"] == missing["evidence_eligible"]
            and wrapper["unresolved_partial_identity_tokens"] == len(tokens)
            and wrapper["known_targets_blocked_after_source_and_reaction_rename"] == len(blocked),
            "SS wrapper actual inventory counts differ")
    return dict(permanent_rows=len(permanent), group_counts=expected_counts,
                actual_source_ids=15, original_candidate_dispositions={"rejected": 18, "deferred": 10},
                physical_inventory_files=len(inventory), unresolved_partial_tokens=len(tokens),
                known_products_blocked_after_source_and_reaction_rename=len(blocked),
                missing_historical_fields_preserved_unknown=missing,
                original_package_missing_human_reviewed_field="human_reviewed" not in package,
                wrapper_machine_governance_only=True, scientific_qualification_granted=False,
                append_only_closure_correction=correction)


def audit_protection_and_stages(audit, base):
    import datetime
    from scripts.task016_p7_orchestrate import STAGES

    base = Path(base)
    approval = audit.json(base / "approval.json")
    require(approval["task"] == TASK and approval["approval_type"] == "agent_delegated"
            and approval["human_reviewed"] is False, "delegated approval invalid")
    baseline = audit.json(base / "execution_baseline.json")
    original_contract = baseline["mutable_originals"][approval["contract"]]
    require(original_contract["sha256"] == approval["approved_contract_sha256"],
            "approved original contract SHA differs")
    audit.bind(original_contract["snapshot"], approval["approved_contract_sha256"])
    audit.bind(approval["contract"])  # Working TASK may append explicit execution status.
    protected = audit.json(base / "protected_hashes.json")
    audit.mapping(protected)
    require(len(protected) == 3961, "G0 protected universe changed")
    baseline = audit.json(base / "execution_baseline.json")
    for item in baseline.get("mutable_originals", {}).values():
        audit.bind(item["snapshot"], item["sha256"])
    audit.record("approval_and3961_protected_physical_SHA", True,
                 protected_files=len(protected))
    cached = {}

    def verify(path, expected=None, seen=()):
        path = audit.bind(path, expected)
        key = str(path)
        require(key not in seen, "cycle in immutable stage chain")
        if key in cached:
            return cached[key]
        manifest = audit.json(path)
        require(all(k in manifest for k in ("task", "stage", "family", "epoch_id",
                                            "files", "previous_manifest_path",
                                            "input_manifest_sha")), "stage schema incomplete")
        require(manifest["task"] == TASK and manifest["stage"] in STAGES,
                "unknown stage or task")
        audit.mapping(manifest["files"])
        if manifest["stage"] == "G0_BASELINE":
            require(manifest["previous_manifest_path"] is None and
                    manifest["input_manifest_sha"] is None and
                    str(base / "approval.json") in manifest["files"],
                    "G0 is not rooted in actual delegated approval")
        else:
            require(manifest["previous_manifest_path"] is not None and
                    manifest["input_manifest_sha"] is not None, "unrooted downstream stage")
            parent = verify(manifest["previous_manifest_path"],
                            manifest["input_manifest_sha"], seen + (key,))
            require(STAGES.index(parent["stage"]) + 1 == STAGES.index(manifest["stage"]),
                    "stage sequence not adjacent")
            branch = manifest["stage"] == "G2_DESIGN_ACQUIRE" and parent["family"] == "global"
            require(branch or (parent["family"] == manifest["family"] and
                               parent["epoch_id"] == manifest["epoch_id"]),
                    "independent family/epoch stage chain crossed")
            if "timestamp" in parent and "timestamp" in manifest:
                require(datetime.datetime.fromisoformat(parent["timestamp"]) <=
                        datetime.datetime.fromisoformat(manifest["timestamp"]),
                        "downstream stage recorded before upstream freeze")
        cached[key] = manifest
        return manifest

    stages = []
    archived_stage_copies = []
    for path in sorted(audit.path(base).rglob("G*.json")):
        if "stages" not in path.parts:
            continue
        manifest = verify(path)
        if "report_snapshots" in path.parts:
            parts = path.relative_to(audit.path(base / "report_snapshots")).parts
            require("outputs" in parts, "archived stage lacks original output-path mapping")
            original = "/".join(parts[parts.index("outputs"):])
            audit.bind(original, sha_file(path))
            archived_stage_copies.append(dict(path=str(path.relative_to(audit.root)),
                                              original_path=original, sha256=sha_file(path)))
            continue
        stages.append(dict(path=str(path.relative_to(audit.root)), sha256=sha_file(path),
                           stage=manifest["stage"], family=manifest["family"],
                           epoch_id=manifest["epoch_id"], file_count=len(manifest["files"])))
    epoch_path = base / "epoch_ledger.jsonl"
    epochs = audit.rows(epoch_path)
    if not epochs:
        audit.pending("independent_epoch_ledger",
                      "Epoch ledger is physically empty; directory naming is not an epoch transition history.")
    else:
        registered, decisions = set(), []
        for row in epochs:
            event = row.get("event_type")
            if event == "verified_existing_stage_registration":
                require(row.get("registration_delay_explicit") is True and
                        row.get("registration_is_not_backdated_transition") is True,
                        "epoch registry silently invents historical transitions")
                physical = verify(row["stage_manifest_path"], row["stage_manifest_sha256"])
                require(row["manifest_created_at"] == physical["timestamp"] and
                        row["registered_at"] >= row["manifest_created_at"] and
                        row["family"] == physical["family"] and row["epoch_id"] == physical["epoch_id"],
                        "epoch actual stage registration identity/time differs")
                registered.add(row["stage_manifest_path"])
            elif event == "epoch_incomplete_decision":
                decision = audit.json(row["decision_manifest_path"], row["decision_manifest_sha256"])
                require(decision["task"] == TASK and
                        decision["family"] == row["family"] in {"C", "SS"} and
                        decision["epoch_id"] == row["epoch_id"] and
                        decision["status"] == row["status"] == "development_epoch_incomplete" and
                        decision["actual_decision_at"] == row["actual_decision_at"] and
                        decision.get("human_reviewed") is False and
                        decision.get("scientific_completion") is False,
                        "incomplete epoch decision identity/claim differs")
                for stage_name in ["G4", "G5"]:
                    pointer = decision["prior_stages"][stage_name]
                    physical = verify(pointer["path"], pointer["sha256"])
                    require(physical["stage"].startswith(stage_name + "_") and
                            physical["family"] == row["family"] and
                            physical["epoch_id"] == row["epoch_id"] and
                            physical["timestamp"] <= row["actual_decision_at"],
                            "incomplete decision original stage/time differs")
                exposure_pointer = decision["permanent_exposure_manifest"]
                exposure = audit.json(exposure_pointer["path"], exposure_pointer["sha256"])
                require(exposure.get("task") == TASK and exposure.get("human_reviewed") is False,
                        "permanent exposure package lacks explicit machine governance")
                maps = []
                for name in ["files", "files_sha256", "files_SHA", "input_files_sha256",
                             "output_files_sha256", "raw_evidence_files_SHA",
                             "bound_immutable_input_files_SHA",
                             "output_and_preserved_v1_v2_files_SHA",
                             "design_input_package_files_SHA", "frozen_artifacts_SHA"]:
                    if name in exposure:
                        audit.mapping(exposure[name])
                        maps.append(name)
                pointers = []
                for name, pointer in exposure.items():
                    if isinstance(pointer, dict) and isinstance(pointer.get("path"), str) and "sha256" in pointer:
                        audit.bind(pointer["path"], pointer["sha256"])
                        pointers.append(name)
                require(maps and pointers, "permanent exposure package lacks file SHA/inventory pointers")
                nested_manifest_path = exposure.get("source_package_manifest_path")
                nested_manifest_sha = exposure.get("source_package_manifest_sha256")
                if nested_manifest_path is not None:
                    require(nested_manifest_sha is not None, "nested exposure manifest SHA absent")
                    nested = audit.json(nested_manifest_path, nested_manifest_sha)
                    if row["family"] == "SS":
                        require(nested.get("task_id") == TASK and
                                nested.get("approval") == "agent_delegated",
                                "SS nested export schema/task differs")
                        exposure_details = audit_ss_permanent_exposure(audit, nested, exposure)
                        maps.extend(["nested:input_file_sha256", "nested:output_bindings"])
                        audit.record("SS_permanent_exposure_independent119_rows", True,
                                     **exposure_details)
                    else:
                        require(nested.get("task") == TASK and nested.get("human_reviewed") is False,
                                "nested exposure package machine governance missing")
                    for field in ["bound_immutable_input_files_SHA", "raw_evidence_files_SHA",
                                  "output_and_preserved_v1_v2_files_SHA",
                                  "design_input_package_files_SHA", "frozen_artifacts_SHA",
                                  "files_sha256", "input_files_sha256", "output_files_sha256"]:
                        if field in nested:
                            audit.mapping(nested[field])
                            maps.append("nested:" + field)
                    require(any(x.startswith("nested:") for x in maps),
                            "nested exposure package physical raw/file inventory absent")
                    for field, pointer in nested.items():
                        if isinstance(pointer, dict) and isinstance(pointer.get("path"), str) and "sha256" in pointer:
                            audit.bind(pointer["path"], pointer["sha256"])
                            pointers.append("nested:" + field)
                    # This is metadata inventory validation only. Hash pointers
                    # to A4 chemistry are never decoded by the verifier.
                    if row["family"] == "C":
                        source_rows = audit.rows(nested["source_exposure_pointer"]["path"],
                                                 nested["source_exposure_pointer"]["sha256"])
                        object_rows = audit.rows(nested["chemical_objects_and_fixtures_pointer"]["path"],
                                                 nested["chemical_objects_and_fixtures_pointer"]["sha256"])
                        block_rows = audit.rows(nested["permanent_source_blocklist_pointer"]["path"],
                                                nested["permanent_source_blocklist_pointer"]["sha256"])
                        require(len(source_rows) == nested["counts"]["actual_chemically_inspected_source_ids"]
                                and len(object_rows) == nested["counts"]["all_object_records"],
                                "C exposure source/object inventory denominator differs")
                        require(all(r.get("future_fresh_eligible") is False and
                                    r.get("permanent_design_exposed") is True for r in source_rows + object_rows)
                                and all(r.get("fresh_eligible") is False for r in block_rows)
                                and {r["source_id"] for r in source_rows} == {r["source_id"] for r in block_rows},
                                "C permanently inspected source/object permits future fresh admission")
                        require(len({t for r in source_rows for t in r["closure_tokens"]}) ==
                                nested["counts"]["unique_normalized_source_closures"],
                                "C normalized permanent source closure denominator differs")

                successor = decision["successor"]
                require(successor.get("status") == "E02_requested_only" and
                        successor.get("frozen") is False,
                        "incomplete decision silently initializes/freezes successor")
                require(not any(x["family"] == row["family"] and x["epoch_id"] == row["epoch_id"]
                                for x in decisions), "duplicate final epoch decision")
                decisions.append(dict(family=row["family"], epoch_id=row["epoch_id"],
                                      actual_decision_at=row["actual_decision_at"],
                                      decision_manifest_path=row["decision_manifest_path"],
                                      decision_manifest_sha256=row["decision_manifest_sha256"],
                                      status="development_epoch_incomplete",
                                      original_G4_G5_recursive_SHA_verified=True,
                                      exposure_package_mapping_fields=maps,
                                      exposure_inventory_pointers=pointers,
                                      successor_frozen=False, scientific_completion=False))
            else:
                raise ContractError("unknown epoch event type: " + str(event))
        audit.record("epoch_existing_stage_registration_limited_evidence", True,
                     actual_registered_rows=sum(x.get("event_type") == "verified_existing_stage_registration"
                                                for x in epochs),
                     no_backdated_transitions=True)
        if decisions:
            audit.record("actual_incomplete_epoch_decision_bindings", True, decisions=decisions,
                         scientific_closure_promoted=False)
        unregistered = [r["path"] for r in stages if r["family"] != "global"
                        and r["path"] not in registered]
        if unregistered:
            audit.pending("new_stage_epoch_registration", "Immutable stages have not yet been appended to delayed epoch registry.",
                          paths=unregistered)
        audit.pending("scientific_epoch_closure", "Delayed existing-stage registrations do not establish G6-G10 completion or a scientific state transition.")
    audit.record("registered_stage_full_recursive_SHA", True, registered_stages=len(stages))
    return dict(protected_files=len(protected), registered_stages=stages,
                epoch_rows=epochs, incomplete_decisions=decisions if epochs else [],
                archived_stage_copies_not_new_registry_events=archived_stage_copies,
                immutable_stage_files_verified=True,
                all_task_stages_complete=False)


def audit_roles(audit, base):
    import re
    base = Path(base)
    candidates = []
    for path in sorted(audit.path(base).rglob("*manifest*.json")):
        if any(k in path.parts for k in ("runs", "superseded", "verification")):
            continue
        data = json.loads(path.read_text())
        logical_role_name = re.match(r"(?:role_|[Aa][0-9]+_)", path.name) is not None
        if isinstance(data, dict) and "agent_role" in data and logical_role_name:
            candidates.append((path, data))
    latest = {}
    for path, data in candidates:
        key = (str(path.parent), re.sub(r"(?:_v|\.v)[0-9]+(?=\.json$)", "", path.name))
        match = re.search(r"(?:_v|\.v)([0-9]+)(?=\.json$)", path.name)
        version = int(match.group(1)) if match else 0
        if key not in latest or latest[key][0] < version:
            latest[key] = (version, path, data)
    records, needs = [], []
    for _, path, data in latest.values():
        audit.bind(path)
        counts = data.get("counts")
        standard = isinstance(counts, dict) and all(
            k in counts for k in ("processed", "passed", "rejected", "pending"))
        if not standard:
            needs.append(dict(path=str(path.relative_to(audit.root)),
                              reason="nonstandard or absent disposition counts",
                              original_counts=counts, agent_role=data["agent_role"]))
            continue
        require(all(isinstance(counts[k], int) and not isinstance(counts[k], bool)
                    and counts[k] >= 0 for k in ("processed", "passed", "rejected", "pending")),
                "negative or noninteger logical role counts")
        require(counts["processed"] == counts["passed"] + counts["rejected"] + counts["pending"],
                "logical role disposition universe not conserved")
        require(data.get("human_reviewed") is not True, "machine role claims human review")
        if data.get("human_reviewed") is not False:
            needs.append(dict(path=str(path.relative_to(audit.root)),
                              reason="missing explicit human_reviewed=false",
                              agent_role=data["agent_role"]))
        input_map = data.get("input_manifest_sha", data.get("input_manifest_sha256", data.get("input_files_sha256")))
        output_map = data.get("output_file_sha", data.get("output_files_sha256"))
        if not isinstance(input_map, dict) or not isinstance(output_map, dict):
            needs.append(dict(path=str(path.relative_to(audit.root)),
                              reason="role physical SHA input/output mappings absent",
                              agent_role=data["agent_role"]))
            continue
        # Hash final graph files for provenance only; never decode another
        # extractor's chemistry in this A5-derived verifier context.
        mismatch = []
        for side in [input_map, output_map]:
            for p, expected in side.items():
                try:
                    audit.bind(p, expected)
                except ContractError as exc:
                    mismatch.append(str(exc))
        if mismatch:
            needs.append(dict(path=str(path.relative_to(audit.root)),
                              reason="retained/active role binding needs explicit supersession resolution",
                              errors=mismatch, agent_role=data["agent_role"]))
        records.append(dict(path=str(path.relative_to(audit.root)),
                            role=data["agent_role"], counts=counts,
                            disposition_conserved=True, current_bindings_passed=not mismatch,
                            read_holdout=data.get("read_holdout"),
                            read_model_outcome=data.get("read_model_outcome")))
    audit.record("standard_role_disposition_count_conservation", True,
                 standard_roles_checked=len(records), nonstandard=len(needs))
    if needs:
        audit.pending("current_role_provenance_full_universe",
                      "Explicit retained/superseded version and nonstandard role schemas need closure.",
                      roles=needs)
    return dict(role_manifest_files=len(candidates), latest_version_records=records,
                versions_selection_rule="highest explicit _vN or .vN within same parent/name; lower versions retained",
                unresolved_role_manifests=needs,
                reads_other_extractor_chemical_graphs=False,
                all_current_roles_audited=not needs)


def audit_runtime(audit, base):
    from aizynthfinder.chem import TreeMolecule
    from flavoretro.glycoside_library_v7 import (
        Registry, LibraryRetroReaction, apply_template,
    )
    from flavoretro.reviewed_resources import canonical_side

    base = Path(base)
    manifest_path = base / "runtime/template_source_manifest.json"
    manifest = audit.json(manifest_path)
    projection = audit.json(base / "runtime/runtime_projection.json")
    registry = Registry(audit.path(manifest_path), sha_file(audit.path(manifest_path)))
    c_scope = audit.json(base / "C/E01/scope_manifest.json")
    ss_scope = audit.json(base / "SS/scope_freeze.json")
    for scope, folder in [(c_scope, base / "C/E01"), (ss_scope, base / "SS")]:
        for path, expected in scope["files_sha256"].items():
            candidate = Path(path) if len(Path(path).parts) > 1 else folder / path
            audit.bind(candidate, expected)
    c_original = audit.json(base / "C/E01/scope_bank.json")
    c_instances = audit.json(base / "C/E01/build_supports.json")
    ss_original = audit.rows(base / "SS/scope_templates_formal.jsonl")
    ss_instances = audit.rows(base / "SS/runtime_instances.jsonl")
    expected_templates = {t["template_id"]: t for t in c_original + ss_original}
    require(set(expected_templates) == {t["template_id"] for t in registry.increment_templates},
            "runtime scope template universe differs from original freezes")
    c_ids = {t["template_id"] for t in c_original}
    c_projection = next(p for p in projection["projections"] if p["family"] == "C")
    for template in registry.increment_templates:
        original = expected_templates[template["template_id"]]
        differences = {k for k in set(template) | set(original)
                       if template.get(k) != original.get(k)}
        permitted = (set(c_projection["template_fields_added_or_normalized"])
                     if template["template_id"] in c_ids else {"source_qualification"})
        require(differences <= permitted, "runtime projection changed scientific template/guard")
        qualification = template.get("source_qualification")
        if qualification:
            audit.bind(qualification["verification_path"], qualification["verification_sha256"])
            require(qualification["human_reviewed"] is False,
                    "runtime projection claims human chemistry review")
    expected_instances = {r["instance_id"]: r for r in c_instances + ss_instances}
    require(set(expected_instances) == set(registry.increment_instances),
            "runtime build support universe differs")
    for iid, projected in registry.increment_instances.items():
        original = expected_instances[iid]
        differences = {k for k in set(projected) | set(original)
                       if projected.get(k) != original.get(k)}
        permitted = (set(c_projection["instance_fields_added"])
                     if iid in {r["instance_id"] for r in c_instances} else set())
        require(differences <= permitted, "runtime projection changed original build chemical graph")
    require(registry.templates[:len(registry.v6_registry.templates)] == registry.v6_registry.templates,
            "inherited v6 scientific template data changed")
    require(all(registry.instances[i] == r for i, r in registry.v6_registry.instances.items()),
            "inherited v6 scientific instance data changed")
    require(len(registry.increment_templates) == 6 and
            len(registry.increment_instances) == 12, "P7 scope/build increment counts differ")

    def mapped(template, target):
        reaction = LibraryRetroReaction(
            TreeMolecule(parent=None, smiles=target), smarts=template["smarts"],
            use_rdchiral=False,
            metadata=dict(policy_name="glycoside", template_id=template["template_id"],
                          library_template=template, required_context=template["required_context"],
                          domain_binding=registry.binding))
        return reaction, [canonical_side([m.smiles for m in group])
                          for group in reaction.reactants]

    build = []
    for template in registry.increment_templates:
        for iid in template["support_instances"]:
            row = registry.increment_instances[iid]
            expected = canonical_side(row["reference_precursors"])
            static = [x["precursors"] for x in apply_template(template, row["target"])]
            reaction, actual = mapped(template, row["target"])
            require(expected in static and expected in actual, "physical build replay failed")
            index = actual.index(expected)
            evidence = registry.evidence(reaction.copy(index=index))
            require(evidence["exact_seed_instance_match"] is True and
                    all(evidence[k] is False for k in
                        ["actionable", "evidence_closed", "prediction_conditions_verified",
                         "independent_chemical_validation", "human_reviewed"]),
                    "build replay promoted to scientific/activity claim")
            build.append(dict(template_id=template["template_id"], instance_id=iid,
                              complete_reference=expected, static_passed=True,
                              production_mapped_passed=True, evidence=evidence))
    controls = []
    for folder, plan_file in [(base / "C/E01", "boundary_plan.json"),
                               (base / "SS", "scope_boundary_plan.json")]:
        plan = audit.json(folder / plan_file)
        for control in plan["controls"]:
            tid = control.get("template_id", control.get("scope_id"))
            template = registry.by_id[tid]
            static = apply_template(template, control["target"])
            _, actual = mapped(template, control["target"])
            violated = bool(static or actual)
            require(not violated, "registered runtime negative control admitted")
            controls.append(dict(template_id=tid,
                                 control=control.get("control_id", control["control"]),
                                 static_outcomes=static, production_mapped_outcomes=actual,
                                 violated=violated))
    require(len(build) == 12 and len(controls) == 40,
            "runtime build/registered negative universe incomplete")
    semantic = audit.json(base / "C/E01/stages/batches/WASABI_PUBLIC_SI/A5_frozen_core_semantic_boundary.json")
    # Independently re-run direct A5 original-figure graph encodings.
    semantic_actual = []
    for row in semantic["source_confirmed_cases"]:
        results = {t["template_id"]: apply_template(t, row["target_smiles"])
                   for t in registry.increment_templates if t["scope"]["family"] == "C"}
        semantic_actual.append(dict(product_name=row["product_name"],
                                    target_smiles=row["target_smiles"], actual=results))
    semantic_closed = semantic.get("semantic_boundary_closed") is True
    if not semantic_closed:
        audit.pending("C_frozen_core_semantic_boundary",
                      "Source-confirmed flavonol6C graphs are accepted by flavone6C query; no pre-registered C3-H negative failure is invented.",
                      postfreeze_probe_results=semantic_actual)
    audit.record("physical_v7_projection12build40registered_controls", True,
                 templates=len(registry.templates), instances=len(registry.instances),
                 increment_build_replays=12, registered_controls=40)
    return dict(registered_runtime_replay_passed=True,
                templates=len(registry.templates), instances=len(registry.instances),
                increment_templates=6, increment_instances=12,
                build_replay=build, registered_controls=controls,
                original_scientific_data_preserved=True,
                semantic_boundary_closed=semantic_closed,
                full_scientific_scope_acceptance=semantic_closed,
                semantic_source_probes=semantic_actual, real_MCTS_run_by_verifier=0)


def audit_package_and_noasset(audit, base):
    import re
    import zipfile
    import tarfile

    base = Path(base)
    revision = next((name for name in ("engineering-v4", "engineering-v3", "engineering-v2")
                     if audit.path(base / name / "asset_free_regression.json").is_file()), None)
    require(revision is not None, "physical no-asset suite result absent")
    report = audit.json(base / revision / "asset_free_regression.json")
    log = audit.bind(base / revision / "asset_free_regression.log", report["log_sha256"])
    text = log.read_text()
    match = re.search(r"Ran (\d+) tests", text)
    require(match is not None and int(match.group(1)) == report["total_tests"],
            "no-asset physical test denominator differs")
    require(report["exit_code"] == 0 and report["errors"] == report["failures"] == 0 and
            report["passed"] + report["skipped"] == report["total_tests"] and
            re.search(r"\bOK\b", text) is not None, "no-asset physical suite failed")
    skip_plan = audit.json(base / revision / "asset_free_skip_plan.json",
                           report["explicit_skip_plan_sha256"])
    if revision == "engineering-v4":
        require(report.get("explicit_skip_plan_path") == str(base / revision / "asset_free_skip_plan.json"),
                "actual no-asset child skip-plan path does not bind this revision")
    snapshot = audit.path(report["snapshot"])
    snapshot_source_drift = []
    for archived in audit.path(snapshot / "tests").rglob("*.py"):
        audit.bind(archived)
        current = audit.bind("tests" / archived.relative_to(snapshot / "tests"))
        if archived.read_bytes() != current.read_bytes():
            snapshot_source_drift.append(str(current.relative_to(audit.root)))
    if snapshot_source_drift:
        audit.pending("current_code_asset_free_suite",
                      "Preserved successful snapshot predates current test changes; final current-source asset-free run is pending.",
                      preserved_tests=report["total_tests"], changed_test_files=snapshot_source_drift)
    prior_failure = audit.json(base / "engineering/asset_free_regression.json")
    prior_log = audit.bind(base / "engineering/asset_free_regression.log",
                          prior_failure["log_sha256"])
    require(prior_failure["exit_code"] != 0 and "ERROR" in prior_log.read_text(),
            "old asset-free failure was not retained")
    package = audit.json(base / "package-v2/validation.json")
    wheel = audit.bind(package["wheel"], package["wheel_sha256"])
    sdist = audit.bind(package["sdist"], package["sdist_sha256"])
    with zipfile.ZipFile(wheel) as archive:
        wheel_files = archive.namelist()
    with tarfile.open(sdist) as archive:
        sdist_files = archive.getnames()
    forbidden = [p for p in wheel_files + sdist_files
                 if any(part in {"outputs", "operations", "raw", "models", ".venv-foundation"}
                        for part in Path(p).parts)]
    require(not forbidden, "source/model/output payload was packaged")
    from flavoretro.workspace import PACKAGE
    configs = audit.path("configs")
    config_comparisons = []
    for name in ["search.json", "glycoside-library-v6.json", "glycoside-library-v7.json"]:
        canonical_path = audit.bind(configs / name)
        packaged_config = audit.bind(Path(PACKAGE) / "assets" / "configs" / name)
        require(canonical_path.read_bytes() == packaged_config.read_bytes(),
                "repository packaged config copies differ")
        config_comparisons.append(name)
    # Installed probe physical provenance is checked by the global run ledger.
    probe_ids = [r["run_id"] for r in package["probes"]]
    require(len(probe_ids) == 4 and len(set(probe_ids)) == 4,
            "installed package probe universe incomplete")
    stable = audit.json(base / "package-v2/default_off_regression.json")
    previous = audit.json(stable["previous_path"], stable["previous_result_sha256"])
    current = next(r for r in audit.rows(base / "run_ledger.jsonl")
                   if r.get("phase") != "started" and r["run_id"] == stable["current_run_id"])
    after = audit.json(Path(current["manifest"]).with_name("result.json"),
                       stable["current_result_sha256"])
    excluded = set(stable["excluded_fields"])
    def stable(value):
        if isinstance(value, dict):
            return {k: stable(v) for k, v in value.items() if k not in excluded}
        if isinstance(value, list):
            return [stable(v) for v in value]
        return value
    require(stable(previous) == stable(after),
            "default-off physical stable field regression differs")
    missing_log = audit.bind("outputs/validation/task016-p7-package-v2/missing-assets.log")
    missing_probe = json.loads(missing_log.read_text())
    require(missing_probe.get("missing_assets_fail_closed") is True and
            missing_probe.get("default_off") is True,
            "installed package missing-asset/default-off raw probe failed")
    full_revision = next((name for name in ("engineering-current-v2", "engineering-current")
                          if audit.path(base / name / "full_suite.json").is_file()), None)
    if full_revision is not None:
        full = audit.json(base / full_revision / "full_suite.json")
        full_log = audit.bind(base / full_revision / "full_suite.log", full["log_sha256"])
        full_match = re.search(r"Ran (\d+) tests", full_log.read_text())
        is_new_schema = full_revision == "engineering-current-v2"
        full_passed = full["passed_tests"] if is_new_schema else full["passed"]
        full_success = full["passed"] if is_new_schema else full["successful"]
        require(full_success is True and full["failures"] == full["errors"] == 0 and
                full_passed + full["skipped"] == full["total_tests"] and
                full_match is not None and int(full_match.group(1)) == full["total_tests"] and
                (not is_new_schema or full["exit_code"] == 0),
                "physical current full test suite failed")
        source_bindings = full["source_SHA_bindings"] if is_new_schema else full["source_file_sha256"]
        full_test_drift = []
        for p, expected in source_bindings.items():
            if p.startswith("tests/") and sha_file(audit.path(p)) != expected:
                # Preserve the actual historical full suite; source drift does
                # not turn a previous denominator into current verification.
                archived_revision = "engineering-v3" if not is_new_schema else revision
                historical_noasset = audit.json(base / archived_revision / "asset_free_regression.json")
                archived = audit.path(historical_noasset["snapshot"]) / p
                audit.bind(archived, expected)
                full_test_drift.append(p)
            elif p.startswith(("tests/", "flavoretro/", "configs/")):
                audit.bind(p, expected)
        audit.record("physical_preserved_full_test_suite" if full_test_drift
                     else "physical_current_full_test_suite", True, tests=full["total_tests"],
                     tests_passed=full_passed, tests_skipped=full["skipped"],
                     current_source_universe_unchanged=not full_test_drift,
                     actual_result_namespace=full_revision)
        if full_test_drift:
            audit.pending("current_changed_full_test_universe",
                          "Historical full suite passed; current changed tests await appropriate full run.",
                          preserved_tests=full["total_tests"], changed_test_files=full_test_drift)
        if is_new_schema:
            # The old219 suite is retained as historical evidence, never
            # overwritten or silently promoted to the newer denominator.
            old_full = audit.json(base / "engineering-current/full_suite.json")
            audit.bind(base / "engineering-current/full_suite.log", old_full["log_sha256"])
    else:
        audit.pending("current_full_test_suite", "Current full suite result absent.")
    audit.record("physical_package_default_off_and_noasset", True,
                 noasset_tests=report["total_tests"], noasset_passed=report["passed"],
                 noasset_skipped=report["skipped"], probes=4)
    return dict(noasset_physical_log_verified=True, test_denominator=report["total_tests"],
                passed_tests=report["passed"], explicit_skipped=report["skipped"],
                previous_failed_run_preserved=True,
                wheel_payload_verified=True, sdist_payload_verified=True,
                config_copies_compared=config_comparisons,
                installed_probe_ids=probe_ids, default_off_physical_comparison_passed=True,
                missing_assets_installed_probe_independently_verified=True,
                noasset_revision=revision,
                release_claim=False)


def audit_fresh_acquisition_timing(audit, base):
    """Check actual later SS batch bindings without opening A4 graph outputs."""
    import hashlib

    base = Path(base)
    notice_path = base / "SS/G5_revision_v2_engineering_binding_notice.json"
    if not audit.path(notice_path).is_file():
        audit.pending("SS_later_fresh_batch_timing", "Later batch timing bindings absent.")
        return dict(completed=False, scientific_preregistration_verified=False)
    notice = audit.json(notice_path)
    original = audit.json(notice["original_G5_path"], notice["original_G5_sha256"])
    revision = audit.json(notice["new_G5_path"], notice["new_G5_sha256"])
    audit.mapping(original["files"])
    audit.mapping(revision["files"])
    batches = audit.rows(notice["source_batch_timing_path"], notice["source_batch_timing_sha256"])
    require(original["stage"] == revision["stage"] == "G5_FRESH_HOLDOUT_ACQUIRE" and
            revision["timestamp"] == notice["new_G5_timestamp"] and
            notice.get("reviewed_candidates_late_binding_exposed") is True and
            notice.get("formal_G6_absent") is True,
            "later batch revision invents a passed scientific phase")
    operation_bytes = audit.path("operations/events.jsonl").read_bytes()
    events = [json.loads(line) for line in operation_bytes.splitlines() if line]
    results, bound_operations = [], []
    seen_ids = set()
    for batch in batches:
        bid = batch["batch_id"]
        require(bid not in seen_ids, "duplicate fresh batch timing ID")
        seen_ids.add(bid)
        audit.mapping(batch["raw_inputs_sha256"])
        require(batch.get("first_actual_chemical_review_at") is None,
                "unrecorded first review timestamp was silently backfilled")
        manifest_path = batch.get("raw_only_manifest_path")
        review_path = batch.get("documented_review_artifact_path")
        prior_bound = None
        if manifest_path:
            raw_only = audit.json(manifest_path, batch["raw_only_manifest_sha256"])
            require(not raw_only.get("contains_final_graphs", False),
                    "raw-only timing input contains final graphs")
            require(revision["files"].get(manifest_path) == batch["raw_only_manifest_sha256"],
                    "revision G5 does not bind exact later raw-only manifest")
            prior_bound = original["files"].get(manifest_path) == batch["raw_only_manifest_sha256"]
            require(prior_bound == batch["original_G5_bound_this_batch"],
                    "original G5 raw-only coverage claim differs")
        writes = [r for r in events if r.get("task") == TASK and r.get("action") == "write"
                  and r.get("path") == review_path] if review_path else []
        review_bound = min(r["time"] for r in writes) if writes else None
        recorded = batch.get("documented_chemical_review_completed_no_later_than")
        if review_path:
            audit.bind(review_path)  # SHA only; no A4 chemistry decoded.
            require(review_bound == recorded,
                    "review-completed bound differs from original operate write event")
            require(review_bound is not None and review_bound < revision["timestamp"] and
                    prior_bound is False and batch["late_binding_after_chemical_exposure"] is True
                    and batch["permanent_chemical_exposure"] is True,
                    "late chemical exposure was erased or promoted to preregistration")
            bound_operations.extend(r for r in writes if r["time"] == review_bound)
        elif recorded is not None:
            raise ContractError("review bound has no physical artifact pointer")
        results.append(dict(batch_id=bid, original_G5_binds_raw_manifest=prior_bound,
                            review_completed_no_later_than=review_bound,
                            exact_first_review_at=None,
                            revision_G5_at=revision["timestamp"],
                            late_binding_verified=bool(review_bound),
                            current_raw_only_SHA_binding_verified=bool(manifest_path),
                            scientific_timing_eligibility=False,
                            no_A4_final_graphs_decoded=True))
    audit.record("SS_later_G5_current_physical_bindings", True,
                 batch_rows=len(results), late_reviewed_batches=sum(
                     r["late_binding_verified"] for r in results),
                 retrospective_scientific_pass_claimed=False)
    audit.pending("SS_fresh_batch_scientific_preregistration",
                  "Later raw-only batches were chemically reviewed before formal G5 binding; initial exact review time remains unrecorded.",
                  batches=results)
    return dict(current_revision_physical_bindings_verified=True,
                scientific_preregistration_verified=False, batch_checks=results,
                operation_review_write_records=bound_operations,
                operations_snapshot_sha256=hashlib.sha256(operation_bytes).hexdigest(),
                no_other_extractor_graphs_read=True)


def audit_e02_governance(audit, base):
    """Read governance/count metadata; never decode the other extraction track."""
    base = Path(base)
    history = audit._historical_closure_revision()
    audit.bind(history["original_path"], history["current_sha256"])
    audit.record("explicit_early_archive_closure_revision_mapping", True, **history)
    cbase = base / "C/E02"
    stage_shas = {
        "G2_DESIGN_ACQUIRE": "83fd36a2bda5277265017446f7edc628b798a4aaf6aba98f76bcfa06e1d4d213",
        "G3_SCOPE_BUILD": "07d62d116c8cb226dc0e7fd3e0a55d69a4b05ea70a85837177ad1a39b84fdeb7",
        "G4_SCOPE_FREEZE": "09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46",
    }
    stages = {name: audit.json(cbase / "stages" / (name + ".json"), digest)
              for name, digest in stage_shas.items()}
    for name, stage in stages.items():
        require(stage["family"] == "C" and stage["epoch_id"] == "C-E02" and stage["stage"] == name,
                "C E02 stage identity differs")
        audit.mapping(stage["files"])
    require(stages["G4_SCOPE_FREEZE"]["input_manifest_sha"] == stage_shas["G3_SCOPE_BUILD"] and
            stages["G3_SCOPE_BUILD"]["input_manifest_sha"] == stage_shas["G2_DESIGN_ACQUIRE"],
            "C E02 own stage predecessor binding differs")
    metadata_roles = {}
    for relative in [
        "root_A6_source_admission/v1/role_A6_source_admission_manifest.json",
        "A8_source_scope_preflight/v1/role_A8_manifest.json",
        "role_A0_epoch_initialization_manifest.json", "role_A0_G3_G4_freeze_manifest.json",
    ]:
        path = cbase / relative
        data = audit.json(path)
        require(data["human_reviewed"] is False and data["approval_type"] == "agent_delegated",
                "C E02 role claims human review")
        audit.mapping(data["input_manifest_sha"])
        audit.mapping(data["output_file_sha"])
        metadata_roles[str(path)] = dict(sha256=sha_file(audit.path(path)),
                                        agent_role=data["agent_role"], counts=data["counts"])
    a8 = audit.json(cbase / "A8_source_scope_preflight/v1/A8_source_scope_validation.json")
    require(a8["passed"] is True and a8["validation"]["scopes"] == 1 and
            a8["full_reference_supports"] == a8["distinct_canonical_acceptors"] == 2 and
            a8["context_aware_control_refusals"] == 10 and
            a8["mapped_chemical_control_refusals"] == 8 and
            a8["new_scientific_MCTS"] == a8["fresh_candidates"] == 0 and
            a8["overall_scientific_completed"] is False,
            "C E02 bounded source-only A8 claims differ")
    audit.mapping(a8["input_files_sha256"])
    audit.record("C_E02_G2_G3_G4_physical_governance_bindings", True,
                 stage_files_sha256=stage_shas, role_metadata=metadata_roles,
                 existing_A8_metadata_counts=dict(scopes=1, supports=2,
                     context_API_refusals=10, mapped_chemical_refusals=8),
                 no_new_independent_chemical_replay_in_this_A11=True)

    hyp_path = cbase / "pre_freeze_hypothesis_exposure/v1/permanent_exposure_manifest.json"
    hyp = audit.json(hyp_path, "dfdc8f24deeba64c2e16ed6869c41cb0e25b2bbddd88ed947a2a65f1d99d8fd8")
    audit.mapping(hyp["input_files_sha256"]); audit.mapping(hyp["output_files_sha256"])
    hrows = audit.rows(cbase / "pre_freeze_hypothesis_exposure/v1/permanent_name_hypothesis_exposure.jsonl")
    require(len(hrows) == hyp["records"] == 16 and len({r["exposure_id"] for r in hrows}) == 16,
            "C late hypothesis exposure universe differs")
    require(hyp["created_at"] > stages["G4_SCOPE_FREEZE"]["timestamp"] and
            hyp["actual_G4_timestamp"] == stages["G4_SCOPE_FREEZE"]["timestamp"] and
            hyp["G4_sha256"] == stage_shas["G4_SCOPE_FREEZE"] and
            hyp["future_G5_must_bind_this_supplement"] is True and
            hyp["scope_bank_or_guard_modified"] is False,
            "C hypothesis supplement silently backdates or changes frozen scope")
    require(all(r["permanent_design_exposed"] is True and r["future_fresh_eligible"] is False and
                r["registration_is_late"] is True and r["registration_is_not_backdated"] is True and
                r["actual_registered_at"] == hyp["created_at"] and r["human_reviewed"] is False and
                r["source_scientific_qualified"] is False and
                all(r[k] is None for k in ["canonical_acceptor_graph", "canonical_product_graph",
                                           "donor_graph", "source_id"]) for r in hrows),
            "C name-only hypotheses became qualified/fresh or acquired invented graphs")
    fresh_stages = list(audit.path(cbase / "stages").rglob("G5*.json"))
    require(not fresh_stages, "C E02 fresh G5 appeared during pre-G5 audit")
    audit.record("C_E02_late16_name_hypotheses_permanent_notfresh", True,
                 records=16, full_graphs=0, identity_pending=16,
                 actual_registration=hyp["created_at"], G4_frozen_before_registration=True,
                 G5_present=False, future_G5_must_bind_supplement=True,
                 no_names_promoted_to_source_facts=True,
                 original_not_metadata_only_field=hyp["not_metadata_only"])
    audit.pending("C_E02_name_hypothesis_identity_closure",
                  "Sixteen exposed names have no adjudicated source/full-graph identity. Future G5 must bind this late supplement and resolve identities; no full-graph laundering probe is claimed.")

    ssbase = base / "SS/E02_design"
    manifest = audit.json(ssbase / "root_A6_graph_reconciliation/v1/permanent_design_exposure_manifest.json",
                          "809e503dac075970d0ec8e7553743366c52165812549b516369ef5fbaa83d2b2")
    audit.mapping(manifest["input_files_sha256"]); audit.mapping(manifest["output_files_sha256"])
    raw = audit.rows(ssbase / "root_A6_graph_reconciliation/v1/permanent_design_exposure_ledger.jsonl")
    require(len(raw) == manifest["exposure_rows"] == 19 and
            len({r["exposure_id"] for r in raw}) == 19 and
            sum(r.get("reaction_id") is None for r in raw) == 8 and
            manifest["source_scientific_qualified"] == 0,
            "SS design exposure count/nullable-source schema differs")
    require(all(r["development_exposed"] is True and r["eligible_for_fresh_holdout"] is False and
                r["human_reviewed"] is False and r["source_scientific_qualified"] is False for r in raw),
            "SS exposed design object became fresh/qualified")
    # Tokens are handled as opaque bytes here, never interpreted as molecular graphs.
    # This validates the exported edge partition; it is not an independent graph re-extraction.
    parent = list(range(len(raw)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    owners = {}
    for i, row in enumerate(raw):
        tokens = row["closure_tokens"]
        require(isinstance(tokens, list) and tokens, "SS exposure lacks opaque closure edges")
        for token in tokens:
            require(isinstance(token, str) and token, "invalid opaque closure token")
            if token.startswith("target:"):
                continue
            token_digest = sha_json(token)
            if token_digest in owners:
                parent[find(i)] = find(owners[token_digest])
            else:
                owners[token_digest] = i
    grouped = {}
    for i, row in enumerate(raw):
        grouped.setdefault(find(i), []).append(row.get("reaction_id") or row["exposure_id"])
    groups = {"closure:" + sha_json(sorted(v))[:20]: sorted(v) for v in grouped.values()}
    declared = audit.json(ssbase / "root_A6_graph_reconciliation/v1/permanent_design_closure_groups.json")
    require(groups == declared and len(groups) == manifest["closure_groups"] == 2,
            "SS opaque closure edge partition/membership differs")
    from scripts.task016_p7_closure_harness import assert_fresh
    probes = []
    for row in raw:
        source_only = {k: row[k] for k in ["development_exposed", "exposure_type"]}
        source_only["closure_tokens"] = [t for t in row["closure_tokens"]
                                         if t.startswith(("article:", "doi:"))]
        require(bool(source_only["closure_tokens"]), "SS design source lacks actual source alias edges")
        candidate = dict(source_id=row["doi"], reaction_id="A11-renamed-source-reaction")
        try:
            assert_fresh(candidate, [source_only])
        except ContractError as exc:
            require("intersects holdout" in str(exc), "SS source-only probe failed merely on schema")
        else:
            raise ContractError("SS exposed design source can be laundered via DOI alias")
        probes.append(dict(exposure_id=row["exposure_id"], renamed_DOI_source_rejected=True))
    audit.record("SS_E02_design19_permanent_governance_and_opaque_closure", True,
                 rows=19, original_assay_contexts=11, whole_source_rows=4,
                 CAS_database_objects=4, nullable_or_absent_reaction_IDs=8,
                 original_reaction_ID_field_missing_rows=4,
                 original_reaction_ID_explicit_null_rows=4,
                 opaque_edge_groups=2, isolated_actual_DOI_rejection_probes=probes,
                 molecular_edge_derivation_not_independently_recomputed=True,
                 no_source_scientific_qualification=True)

    role_paths = {
        "A4_v5": ssbase / "A4_fixed_extraction_v5/role_A4_fixed_extraction_manifest.json",
        "A5_v4": ssbase / "harness_A5_extraction/v4/role_A5_manifest.json",
        "assay_universe_v3": ssbase / "A4_assay_universe_v3/role_A4_source_assay_universe_manifest.json",
    }
    ss_roles = {}
    for name, path in role_paths.items():
        data = audit.json(path)
        require(data["human_reviewed"] is False and data["approval_type"] == "agent_delegated",
                "SS current role claims human review")
        for field in ["input_files_sha256", "output_files_sha256", "input_manifest_sha", "output_file_sha"]:
            if isinstance(data.get(field), dict):
                audit.mapping(data[field])
        ss_roles[name] = dict(path=str(path), sha256=sha_file(audit.path(path)),
                              agent_role=data["agent_role"])
    a4 = audit.json(role_paths["A4_v5"])
    a5 = audit.json(role_paths["A5_v4"])
    require(a4["focus_source_assay_count"] == 11 and
            a4["complete_reference_graph_contexts"] == 9 and
            a4["deferred_product_graph_contexts"] == 2 and
            a4["scientifically_qualified_reactions"] == 0 and
            a5["counts"] == dict(processed=11, passed=10, rejected=0, pending=1),
            "SS two current track metadata counts silently equated")
    universe = audit.json(role_paths["assay_universe_v3"])
    assays = audit.rows(ssbase / "A4_assay_universe_v3/source_assay_universe.jsonl")
    actual_locations = Counter(r["source_id"] + ":" + r["source_location"] for r in assays)
    require(len(assays) == universe["actual_enumerated_source_assay_rows"] == 821 and
            len({r["assay_id"] for r in assays}) == 821 and
            actual_locations == Counter(universe["source_location_row_counts"]) and
            all(r["development_exposed"] is True and r["evidence_eligible"] is False and
                r["structure_complete"] is False and r["reference_precursor_complete"] is False and
                r["product_smiles"] is None for r in assays) and
            universe["qualified_reactions"] == 0 and
            universe["full_every_experiment_universe_complete"] is False,
            "SS assay universe lost row conservation or became complete source reaction refs")
    audit.record("SS_current_A4v5_A5v4_and821_assay_metadata_bindings", True,
                 roles=ss_roles, A4_complete_candidates=9, A4_deferred_candidates=2,
                 A5_complete_candidates=10, A5_deferred_candidates=1,
                 assay_universe_rows=821, source_location_row_counts=dict(actual_locations),
                 scientific_qualified=0, no_A4_final_graph_file_decoded=True,
                 full_every_experiment_universe_complete=False)
    return dict(C_E02_G4_sha256=stage_shas["G4_SCOPE_FREEZE"],
                C_E02_G5_present=False, C_late_name_exposures=16,
                SS_design_exposure_rows=19, SS_assay_rows=821,
                current_SS_roles=ss_roles, source_only_governance_audit=True,
                independent_chemical_validation=False, scientific_completion=False)

def audit_scientific_gates(audit, base):
    from scripts.task016_p7_experiment_harness import (
        validate_runner_inputs, load_raw_cells, recompute_metrics,
    )
    from scripts.task016_p7_closure_harness import assert_zero_leakage, closure_groups
    from flavoretro.glycoside_library_v7 import load_registry
    from flavoretro.reviewed_resources import canonical_side

    base = Path(base)
    registry = load_registry()
    exposure = audit.rows(base / "exposure_ledger.jsonl")
    families = {}
    for family, folder in [("C", base / "C/E01"), ("SS", base / "SS")]:
        frozen_path = folder / "experiment/frozen_contract.json"
        if not audit.path(frozen_path).is_file():
            families[family] = dict(completed=False, reason="No qualified panel/frozen scientific contract",
                                    G9_frozen_contract_present=False, fresh_transfer_claim=False)
            audit.pending(f"{family}_scientific_transfer_matrix",
                          "Qualified fresh source panel, leakage/floor, G9 contract and full live A/B/E matrix are absent.")
            continue
        frozen = audit.json(frozen_path)
        contract = frozen["contract"]
        validate_runner_inputs(frozen, contract)
        for field in ["scope_bank_sha", "runtime_manifest_sha", "code_sha", "model_hashes"]:
            audit.mapping(contract[field])
        panel = contract["panels"][family]
        references = audit.rows(panel["path"], panel["sha256"])
        preflight = audit.json(panel["preflight_path"], panel["preflight_sha256"])
        require(preflight.get("passed") is True and preflight.get("agent_role") == "A8",
                "scientific panel has no passed independent A8 preflight")
        require(6 <= len(references) <= 9 and len(closure_groups(references)) >= 2,
                "scientific panel source closure floor failed")
        assert_zero_leakage(list(registry.increment_instances.values()), references,
                            exposure, list(registry.instances.values()))
        for reference in references:
            require(all(reference.get(k) is True for k in
                        ["runtime_complete", "source_identity_verified", "structure_complete",
                         "reference_precursor_complete", "scope_applicability"]) and
                    reference.get("leakage") is False and
                    reference.get("exact_seed_instance_match") is False,
                    "scientific reference eligibility flags fail closed")
            require(canonical_side(reference["reference_precursors"]) ==
                    canonical_side([reference["acceptor_smiles"], reference["donor_smiles"]]),
                    "scientific full precursor conservation failed")
        observation_path = folder / "experiment/observations.jsonl"
        if not audit.path(observation_path).is_file():
            families[family] = dict(completed=False, reason="Frozen matrix has no full raw observations")
            audit.pending(f"{family}_full_raw_matrix", "No complete physical A/B/E matrix.")
            continue
        observations = audit.rows(observation_path)
        for row in observations:
            audit.bind(row["result_path"], row["result_sha256"])
        cells = load_raw_cells(observations, root=audit.root)
        metrics = recompute_metrics(frozen, cells, references)
        family_metrics = metrics["metrics_by_family"][family]
        families[family] = dict(completed=family_metrics["completion_passed"],
                                independently_recomputed_metrics=family_metrics,
                                actual_raw_accounting=metrics["accounting"])
        audit.record(f"{family}_raw_scientific_metrics", family_metrics["completion_passed"])
    completed = set(families) == {"C", "SS"} and all(r["completed"] for r in families.values())
    return dict(families=families, completed=completed,
                metrics_from_physical_raw_only=True, source_failure_not_relaxed=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="outputs/task016-p7/v1/verification")
    parser.add_argument("--regression-only", action="store_true")
    args = parser.parse_args()
    audit = PhysicalAudit()
    base = Path("outputs/task016-p7/v1")
    sections = {}
    errors = []
    jobs = [("regression", lambda: audit_regression(audit))]
    if not args.regression_only:
        jobs += [
            ("protected_and_stages", lambda: audit_protection_and_stages(audit, base)),
            ("search_budget", lambda: audit_search_budget(audit, base)),
            ("source_budget", lambda: audit_source_budget(audit, base)),
            ("roles", lambda: audit_roles(audit, base)),
            ("runtime", lambda: audit_runtime(audit, base)),
            ("package_noasset", lambda: audit_package_and_noasset(audit, base)),
            ("fresh_timing", lambda: audit_fresh_acquisition_timing(audit, base)),
            ("e02_governance", lambda: audit_e02_governance(audit, base)),
            ("scientific", lambda: audit_scientific_gates(audit, base)),
        ]
    for name, function in jobs:
        try:
            sections[name] = function()
        except Exception as exc:
            error = dict(section=name, type=type(exc).__name__, error=str(exc))
            errors.append(error)
            sections[name] = dict(passed=False, error=error, independently_completed=False)
            audit.record(name + "_physical_audit", False, error=error)
    if args.regression_only:
        audit.pending("scientific_family_closure",
                      "Historical capability retention cannot complete P7 scientific eligibility/leakage/floors/transfer matrices.")
    out = ROOT / args.out
    operation_snapshot = sections.get("source_budget", {}).pop("operation_http_records", None)
    additional_outputs = []
    if operation_snapshot is not None:
        snapshot_path = out / "source_operation_requests_snapshot.json"
        save_json(snapshot_path, dict(task=TASK, timestamp=now(),
                                     source_operation_records=operation_snapshot,
                                     source_full_operations_snapshot_sha256=sections[
                                         "source_budget"]["operations_snapshot_sha256"],
                                     snapshot_scope="TASK016P7 source_http operations only; root requests additionally bound by physical root ledgers"),
                  immutable=True)
        sections["source_budget"]["frozen_source_operations_snapshot_path"] = str(
            snapshot_path.relative_to(ROOT))
        sections["source_budget"]["frozen_source_operations_snapshot_sha256"] = sha_file(
            snapshot_path)
        additional_outputs.append(snapshot_path)
    review_operations = sections.get("fresh_timing", {}).pop("operation_review_write_records", None)
    if review_operations is not None:
        timing_path = out / "source_review_write_operations_snapshot.json"
        save_json(timing_path, dict(task=TASK, timestamp=now(),
                                   operations_records=review_operations,
                                   source_operations_SHA=sections["fresh_timing"]["operations_snapshot_sha256"],
                                   purpose="Physical review-write bounds only; no first-review timestamp inference"),
                  immutable=True)
        sections["fresh_timing"]["review_operations_snapshot_path"] = str(timing_path.relative_to(ROOT))
        sections["fresh_timing"]["review_operations_snapshot_sha256"] = sha_file(timing_path)
        additional_outputs.append(timing_path)
    statuses = Counter(c["status"] for c in audit.checks)
    scientific_complete = sections.get("scientific", {}).get("completed") is True
    overall = (scientific_complete and not statuses["failed"] and not statuses["pending"]
               and not args.regression_only)
    report = dict(task=TASK, agent_role="A11", timestamp=now(),
                  verification_scope=("historical physical regression subset" if
                                      args.regression_only else "physical independent P7 audit with explicit incomplete gates"),
                  sections=sections, checks=audit.checks, errors=errors,
                  input_files_sha256=audit.inputs, check_counts=dict(statuses),
                  historical_file_substitutions=list(audit.historical_substitutions.values()),
                  historical_revision_evidence=audit.historical_revision_evidence,
                  role_isolation_disclosure={'own_SS_A5_v4_fixed_before_this_audit': True, 'read_SS_A4_final_graph_files': False, 'read_root_SS_A6_exposure_ledger_graph_tokens': True, 'this_audit_does_not_claim_blind_reextraction': True, 'exposure_file': 'outputs/task016-p7/v1/SS/E02_design/root_A6_graph_reconciliation/v1/permanent_design_exposure_ledger.jsonl', 'exposure_file_sha256': '1831038d3fdd56b73d8c76673381087236a38ad51f43f62738baa6844931006b', 'exposure_fields': ['closure_tokens'], 'exposure_command_started_at': '2026-10-09T01:29:16.745892+00:00', 'exposure_command_finished_at': '2026-10-09T01:29:16.773751+00:00', 'exposure_operate_command_start_line': 19636, 'exposure_raw_command_log': 'operations/command-2778.log', 'own_A5_v4_output_sha256': 'eebdd8f9fed0785a889b41965819a032387c39190e9fd9c82e5d9a7b99e4e17b', 'no_A5_or_scientific_assets_changed': True},
                  engineering_test_coverage_boundary={'completed_suite_tests': 221, 'full_suite_bound_files': 144, 'new_A7_builder_and_later_fresh_entry_not_promoted_to_this_suite_coverage': True, 'no_new_suite_or_MCTS_rerun_in_this_audit': True},
                  executed_subsets_passed=statuses["failed"] == 0,
                  all_required_checks_passed=overall, overall_completed=overall,
                  scientific_transfer_verified=scientific_complete,
                  unprocessed_checks=[c["name"] for c in audit.checks if c["status"] == "pending"],
                  no_new_MCTS_runs=True, approval_type="agent_delegated", human_reviewed=False,
                  independent_chemical_validation=False, release_ready=False)
    name = "independent_regression_validation.json" if args.regression_only else "independent_verification.json"
    report_path = out / name
    save_json(report_path, report, immutable=True)
    counts = dict(processed=len(audit.checks), passed=statuses["passed"],
                  rejected=statuses["failed"], pending=statuses["pending"])
    role = role_manifest("A11", "GLOBAL", list(audit.inputs),
                         [report_path] + additional_outputs, counts,
                         errors=errors,
                         unprocessed=report["unprocessed_checks"],
                         read_holdout=not args.regression_only,
                         read_model_outcome=True)
    role.update(read_fresh_A4_final_graphs=False,
                read_P7_transfer_model_outcomes=scientific_complete,
                actual_historical_physical_runs=sections.get("regression", {}).get(
                    "unique_physical_runs"),
                overall_completed=overall, isolation_disclosure=report["role_isolation_disclosure"],
                engineering_test_coverage_boundary=report["engineering_test_coverage_boundary"])
    manifest_name = "role_A11_regression_manifest.json" if args.regression_only else "role_A11_independent_manifest.json"
    manifest_path = out / manifest_name
    save_json(manifest_path, role, immutable=True)
    print(json.dumps(dict(report=str(report_path.relative_to(ROOT)),
                          report_sha256=sha_file(report_path),
                          manifest=str(manifest_path.relative_to(ROOT)),
                          manifest_sha256=sha_file(manifest_path),
                          check_counts=dict(statuses), overall_completed=overall), ensure_ascii=False))


if __name__ == "__main__":
    main()
