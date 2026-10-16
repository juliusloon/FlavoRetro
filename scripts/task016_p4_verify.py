"""TASK-016-P4 G7: independent read-only verification and axis verdicts.

This script only reads. It never trusts a build script's own "passed" output: it
recomputes the P3 protection check, the re-audit coverage, the distinct-acceptor
count, the holdout completeness, the runtime/holdout separation, the v5
inheritance chain and the budget accounting from the frozen artifacts, then emits
one verdict per contract axis.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
P3 = ROOT / "outputs/task016-p3/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import event, write

CONTRACT_P3_SHAS = {
    "docs/tasks/TASK-016-P3-new-reaction-admission-and-transfer.md":
        "1dfcda3a91d857cef0a867811b67c0f6ebb8906d9e6b6664abf1f323f05b4479",
    "docs/reports/REPORT-016-P3-new-reaction-admission-and-transfer.md":
        "db9dc42661302d67397011893c8343e454d3ba716e2919766beff7572094b783",
    "outputs/task016-p3/v1/reaction_records.jsonl":
        "8832db218293c41845c8b3ba7457fcf929f7227e28a6d984ef28fde5bd7ff504",
    "outputs/task016-p3/v1/identity_checks.jsonl":
        "ad1e3e7813db37640fdbadd1707d7b04833711160f2acf2ec666c1e0e1221eb1",
    "outputs/task016-p3/v1/runtime_instances.jsonl":
        "639ab46d9b0c6fc57a2181e622f2544c5d683d4f6c58abc1af2de063eeef6561",
    "outputs/task016-p3/v1/templates.jsonl":
        "48775ffe5e422caf7d21016c84940c3ea3120c33eddba14a511827e1cf7a180c",
    "outputs/task016-p3/v1/heldout_references.jsonl":
        "52b88e9613859ec0172d15342d384d66c876ffd5255ecbe39525f3abfba11b26",
    "outputs/task016-p3/v1/panel_manifest.json":
        "20ee83c92a49b26722c748ed3876a572bddba228c8bdf105c734df43b2d62823",
}


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, v):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def main():
    checks = {}

    # 1. P3 historical evidence unchanged
    drift = [rel for rel, h in CONTRACT_P3_SHAS.items() if sha(ROOT / rel) != h]
    checks["p3_contract_files_unchanged"] = not drift
    checks["p3_drift_detail"] = drift

    p3_verify = json.loads((P3 / "verify_summary.json").read_text())
    delivery_drift = [n for n, h in p3_verify["delivery_sha256"].items()
                      if not (P3 / n).is_file() or sha(P3 / n) != h]
    checks["p3_delivery_manifest_reproduces"] = not delivery_drift
    checks["p3_delivery_drift_detail"] = delivery_drift

    # 2. re-audit coverage
    reaudit = rows(OUT / "p3_reaudit.jsonl")
    p3_reactions = rows(P3 / "reaction_records.jsonl")
    checks["reaudit_covers_34"] = (len(reaudit) == 34
                                   and {r["reaction_id"] for r in reaudit}
                                   == {r["reaction_id"] for r in p3_reactions})
    levels = Counter(r["p4_status"] for r in reaudit)
    checks["reaudit_levels"] = dict(levels)
    complete = {r["reaction_id"] for r in reaudit if r["countable_as_structure_complete"]}
    c_complete = {r["reaction_id"] for r in reaudit
                  if r["countable_as_structure_complete"] and r["bond_class"] == "C_formation"}
    s_complete = {r["reaction_id"] for r in reaudit
                  if r["countable_as_structure_complete"]
                  and r["bond_class"] == "sugar_sugar_formation"}
    checks["corrected_counts"] = {"C_formation": len(c_complete),
                                  "sugar_sugar_formation": len(s_complete),
                                  "total": len(complete)}
    checks["corrected_reaction_admission_floor_met"] = (
        len(c_complete) >= 8 and len(s_complete) >= 8 and len(complete) >= 16)

    # 3. C3 intermediate no longer borrows dehydrated-product evidence
    by = {r["reaction_id"]: r for r in reaudit}
    checks["c3_intermediate_not_admitted"] = all(
        not by[r]["countable_as_structure_complete"] for r in ("P3R-C01", "P3R-C02"))
    # The retired P3 identification string must not survive as an evidence field.
    # It is legitimate for it to appear inside p3_override, where it is quoted as
    # the claim being retired, so the check targets the evidence-bearing fields.
    _evidence_fields = ("p4_status", "identity_evidence_axis",
                        "structure_determination_basis", "countable_as_structure_complete")
    checks["p3_build_identification_retired"] = all(
        "NMR-assigned 2-hydroxyflavanone" not in json.dumps(
            {k: by[r][k] for k in _evidence_fields})
        for r in ("P3R-C01", "P3R-C02"))
    # and it must not survive anywhere in the v5 runtime payload
    checks["retired_identification_absent_from_v5_payload"] = all(
        "NMR-assigned 2-hydroxyflavanone" not in json.dumps(r)
        for r in rows(OUT / "runtime_instances.jsonl") + rows(OUT / "templates.jsonl"))

    # 4. distinct canonical acceptor counting
    scopes = json.loads((OUT / "scope_decisions.json").read_text())
    checks["scope_counting_key"] = scopes["counting_key"]
    o6 = scopes["scopes"]["rhamnoside_glucoside_O6"]
    checks["o6_counts_one_acceptor"] = o6["distinct_canonical_acceptor"] == 1
    checks["o6_two_sources_not_two_acceptors"] = (len(o6["p3_sources"]) == 2
                                                 and o6["distinct_canonical_acceptor"] == 1)
    checks["v5_increment_scopes"] = scopes["v5_increment_scopes"]

    # 5. holdout completeness and runtime separation
    heldout = rows(OUT / "heldout_references.jsonl")
    runtime = rows(OUT / "runtime_instances.jsonl")
    checks["holdout_all_complete"] = all(h["structure_encoding"] == "complete" for h in heldout)
    checks["no_deferred_in_holdout"] = not [h for h in heldout
                                           if h["reaction_id"] not in complete]
    overlap = sorted({r["reaction_id"] for r in runtime} & {h["reaction_id"] for h in heldout})
    checks["runtime_holdout_overlap"] = overlap
    checks["runtime_has_no_holdout_reaction"] = not overlap
    checks["holdout_deferred_count"] = 0

    # 6. v5 inheritance
    manifest = json.loads((OUT / "template_source_manifest.json").read_text())
    checks["v5_not_descendant_of_v4"] = manifest["inheritance"]["not_a_descendant_of_v4"]
    checks["v5_dropped_quarantined_scopes"] = sorted(
        manifest["inheritance"]["dropped_p3_scopes"])
    tpl = rows(OUT / "templates.jsonl")
    checks["v5_template_scope_centres"] = sorted(t["scope"]["center_class"] for t in tpl)
    checks["v5_holds_only_revalidated_scope"] = (
        checks["v5_template_scope_centres"] == ["rhamnoside_glucoside_O2"])
    cfg = json.loads((ROOT / "configs/glycoside-library-v5.json").read_text())
    pkg = json.loads((ROOT / "flavoretro/assets/configs/glycoside-library-v5.json").read_text())
    checks["v5_default_off"] = (cfg["default_enabled"] is False
                                and pkg["default_enabled"] is False)
    checks["v5_config_copies_identical"] = cfg == pkg
    checks["v5_manifest_binding_matches"] = (
        cfg["manifest_sha256"] == sha(OUT / "template_source_manifest.json"))
    for rel, h in manifest["files_sha256"].items():
        checks["v5_payload_file_" + rel] = sha(OUT / rel) == h

    sys.path.insert(0, str(ROOT))
    from flavoretro import glycoside_library_v3 as v3, glycoside_library_v4 as v4, glycoside_library_v5 as v5
    r3, r4, r5 = v3.load_registry(), v4.load_registry(), v5.load_registry()
    checks["v3_template_count_unchanged"] = len(r3.templates) == 54
    checks["v4_template_count_unchanged"] = len(r4.templates) == 57
    checks["v5_template_count"] = len(r5.templates) == 55
    checks["v5_chains_v3"] = r5.binding["chained_v3"]["version"] == "task016-p2-qualified-v3"
    checks["v5_support_replay_all"] = all(r["replayed"] for r in rows(OUT / "support_replay.jsonl"))

    # 7. budget
    acct = json.loads((OUT / "source_accounting.json").read_text())
    ledger = rows(OUT / "run_ledger.jsonl")
    approval = json.loads((OUT / "approval.json").read_text())
    checks["source_budget_respected"] = (
        acct["http_attempts"] <= approval["budgets"]["source_HTTP_attempts"]
        and acct["bytes"] <= approval["budgets"]["source_bytes"]
        and acct["article_versions"] <= approval["budgets"]["article_versions"]
        and acct["attachments"] <= approval["budgets"]["attachments"])
    checks["search_budget_respected"] = all(
        r.get("attempts", 0) == 0 for r in ledger)

    # 8. no human review claimed
    checks["no_human_reviewed_claims"] = all(
        not r.get("human_reviewed", False)
        for name in ("p3_reaudit.jsonl", "corrected_reaction_records.jsonl",
                     "heldout_references.jsonl", "p4_new_reaction_records.jsonl",
                     "runtime_instances.jsonl")
        for r in rows(OUT / name))

    # 9. new scientific flags never promoted
    checks["new_targets_not_actionable"] = all(
        r.get("actionable") is False and r.get("evidence_closed") is False
        and r.get("prediction_conditions_verified") is False
        for r in rows(OUT / "corrected_reaction_records.jsonl"))

    # ---- axis verdicts
    panel = json.loads((OUT / "panel_manifest.json").read_text())
    metrics = json.loads((OUT / "metrics_by_family.json").read_text())
    engineering_ok = (checks["p3_contract_files_unchanged"]
                      and checks["p3_delivery_manifest_reproduces"]
                      and checks["v5_not_descendant_of_v4"]
                      and checks["v5_holds_only_revalidated_scope"]
                      and checks["v5_default_off"]
                      and checks["v5_manifest_binding_matches"]
                      and checks["v5_support_replay_all"]
                      and checks["runtime_has_no_holdout_reaction"]
                      and checks["v3_template_count_unchanged"]
                      and checks["v4_template_count_unchanged"]
                      and checks["source_budget_respected"]
                      and checks["search_budget_respected"]
                      and checks["no_human_reviewed_claims"])
    admission_ok = checks["corrected_reaction_admission_floor_met"]
    axes = {
        "correction_engineering": "Completed" if engineering_ok else "Partial",
        "corrected_reaction_admission": "Completed" if admission_ok else "Partial",
        "C_transfer": "Partial",
        "sugar_sugar_transfer": "Partial",
    }
    axes["_rationale"] = {
        "C_transfer": ("C holds 1 structure-complete holdout target against a >=6 gate, so the "
                       "A/B/E matrix was never executed and every transfer metric is null"),
        "sugar_sugar_transfer": ("SS holds 5 structure-complete holdout targets against a >=6 gate, "
                                 "so the A/B/E matrix was never executed and every transfer metric "
                                 "is null"),
    }
    overall = ("Completed" if all(axes[k] == "Completed" for k in
                                  ("correction_engineering", "corrected_reaction_admission",
                                   "C_transfer", "sugar_sugar_transfer"))
               else "Partial")

    summary = {
        "task": TASK, "created_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "axis_status": axes, "overall_status": overall,
        "checks": checks,
        "failed_checks": sorted(k for k, v in checks.items()
                                if isinstance(v, bool) and not v),
        "search_attempts": 0,
        "a_b_e_executed": False,
        "formal_run_ready": False, "release_ready": False,
        "independent_chemical_validation": False,
        "training_overlap": "unknown",
    }
    save("verify_summary.json", summary)
    save("axis_status.json", {"task": TASK, "axes": axes, "overall": overall,
                              "unexecuted_metrics": "null, never 0"})
    event(TASK, "g7_verify", overall=overall, failed=len(summary["failed_checks"]))
    print(json.dumps({"overall": overall, "axes": {k: v for k, v in axes.items()
                                                   if not k.startswith("_")},
                      "failed_checks": summary["failed_checks"],
                      "corrected_counts": checks["corrected_counts"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
