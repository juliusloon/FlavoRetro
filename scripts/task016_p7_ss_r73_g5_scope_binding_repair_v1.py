"""Append-only correction: bind the R73 SS G5 registry row to the frozen scope.

The R73 five-originals G5 registration (R73_both_axes_preregistered_before_five_
original_science) omitted scope_manifest_sha256 from its ledger row, so the SS
fresh-acquisition phase gate rejects with SS_G5_SCOPE_BINDING_MISMATCH. This is
the same registry-omission class repaired for R4 in v17. No stage, scope, frozen
script or historical registry record is rewritten; a correction row is appended
with the real current time and the original row is preserved verbatim.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import ROOT, write
from scripts.task016_p7_orchestrate import verify_stage_chain

TASK = "TASK-016-P7"
LEDGER = Path("outputs/task016-p7/v1/epoch_ledger.jsonl")
OUT = Path("outputs/task016-p7/v1/governance/SS_E02_R73_G5_scope_binding_repair_v1")


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    rows = [json.loads(t) for t in (ROOT / LEDGER).read_text().splitlines() if t.strip()]
    g4s = [r for r in rows if r.get("epoch_id") == "SS-E02" and r.get("stage") == "G4_SCOPE_FREEZE" and r.get("status") == "active"]
    g5s = [r for r in rows if r.get("epoch_id") == "SS-E02" and r.get("stage") == "G5_FRESH_HOLDOUT_ACQUIRE" and r.get("status") == "active"]
    if not g4s or not g5s:
        raise ValueError("FROZEN_STAGES_MISSING")
    g4, g5 = g4s[-1], g5s[-1]
    if g5.get("event_type") != "R73_both_axes_preregistered_before_five_original_science" or "R73" not in str(g5.get("stage_manifest_path")):
        raise ValueError("LATEST_G5_IS_NOT_R73")
    if g5.get("scope_manifest_sha256") is not None:
        raise ValueError("REGISTRY_ALREADY_SCOPE_BOUND_NO_REPAIR")
    for stage, entry in (("G4_SCOPE_FREEZE", g4), ("G5_FRESH_HOLDOUT_ACQUIRE", g5)):
        p = entry["stage_manifest_path"]
        if digest(p) != entry["stage_manifest_sha256"]:
            raise ValueError("STAGE_SHA_DRIFT")
        verified = verify_stage_chain(ROOT / p, entry["stage_manifest_sha256"])
        if verified["stage"] != stage or verified["epoch_id"] != "SS-E02":
            raise ValueError("STAGE_CHAIN_INVALID")
    stage5 = json.loads((ROOT / g5["stage_manifest_path"]).read_text())
    if stage5.get("previous_manifest_path") != g4["stage_manifest_path"]:
        raise ValueError("G5_PREDECESSOR_MISMATCH")
    if stage5.get("input_manifest_sha") != g4["stage_manifest_sha256"]:
        raise ValueError("G5_G4_SHA_MISMATCH")
    scope_path = g4["scope_manifest_path"]
    scope_sha = g4["scope_manifest_sha256"]
    if digest(scope_path) != scope_sha:
        raise ValueError("SCOPE_SHA_DRIFT")
    scope = json.loads((ROOT / scope_path).read_text())
    if scope.get("epoch_id") != "SS-E02" or scope.get("family") != "SS":
        raise ValueError("SCOPE_EPOCH_MISMATCH")
    if g5s[-1] is not g5:
        raise ValueError("NOT_LATEST_G5_REGISTRATION")
    old = (ROOT / LEDGER).read_text()
    prior_sha = hashlib.sha256(old.encode()).hexdigest()
    created = datetime.now(timezone.utc).isoformat()
    correction = dict(g5, event_type="verified_G5_scope_binding_correction_R73", registered_at=created,
                      scope_manifest_path=scope_path, scope_manifest_sha256=scope_sha,
                      original_registration_at=g5.get("at") or g5.get("registered_at"),
                      correction_of_omitted_registry_fields=True, original_registration_preserved=True,
                      not_a_new_G5_freeze=True, r73_content_processing_stopped=True,
                      five_source_fresh_eligibility_still_lost=True,
                      scientific_body_read=False, fresh_admitted=0, human_reviewed=False,
                      approval_type="agent_delegated")
    if (ROOT / OUT).exists():
        raise ValueError("REPAIR_OUTPUT_ALREADY_EXISTS")
    note = {
        "task": TASK, "timestamp": created, "approval": "agent_delegated_execution_of_approved_TASK_016_P7",
        "reason": "SS_G5_SCOPE_BINDING_MISMATCH at R74 prereg; R73 five-originals G5 registry row omitted frozen scope binding fields",
        "original_g5_registry": g5, "validated_scope_sha": scope_sha, "validated_scope_path": scope_path,
        "ledger_prior_sha256": prior_sha,
        "no_frozen_stage_or_scope_changed": True, "no_HTTP": True, "no_science_admission": True,
        "no_earlier_registry_gap_retroactively_closed": True,
        "r73_stop_status_unchanged": True,
    }
    write(TASK, str(OUT / "preflight.json"), json.dumps(note, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    write(TASK, str(LEDGER), old + json.dumps(correction, ensure_ascii=False, sort_keys=True) + "\n")
    from scripts.task016_p7_ss_sources import require_acquisition_phase
    outcome = require_acquisition_phase("fresh", epoch_id="SS-E02",
        scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
    if outcome["G5_manifest_sha256"] != g5["stage_manifest_sha256"] or outcome["G4_manifest_sha256"] != g4["stage_manifest_sha256"]:
        raise ValueError("POSTGATE_WRONG_STAGES")
    end = {"preflight_sha256": digest(OUT / "preflight.json"),
           "ledger_after_sha256": digest(LEDGER),
           "correction": correction, "gate": outcome,
           "new_HTTP": 0, "new_MCTS": 0, "fresh_admitted": 0, "G5_scientific_eligibility": False}
    write(TASK, str(OUT / "validation.json"), json.dumps(end, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": "pass", "G4_SHA": g4["stage_manifest_sha256"],
                      "G5_SHA": g5["stage_manifest_sha256"], "scope_SHA": scope_sha,
                      "original_registry_row_preserved": True, "fresh": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
