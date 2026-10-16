"""Append-only correction for the SS-E02 R4 G5 registry/scope binding.

No stage, scope, frozen script or historical registry record is rewritten.
The R5 raw-only acquisition precontract references the existing SS sources
module by SHA; repairing the registry instead preserves that binding.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import ROOT, write
from scripts.task016_p7_orchestrate import verify_stage_chain

TASK = "TASK-016-P7"
LEDGER = Path("outputs/task016-p7/v1/epoch_ledger.jsonl")
OUT = Path("outputs/task016-p7/v1/governance/SS_E02_R5_G5_binding_repair_v1")


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def check(g4, g5, rows):
    if g4.get("epoch_id") != "SS-E02" or g4.get("family") != "SS" or g4.get("status") != "active":
        raise ValueError("G4_REGISTRATION_INVALID")
    if g5.get("epoch_id") != "SS-E02" or g5.get("family") != "SS" or g5.get("status") != "active":
        raise ValueError("G5_REGISTRATION_INVALID")
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
    if g5.get("scope_manifest_sha256") not in (None, scope_sha):
        raise ValueError("G5_WRONG_SCOPE")
    if g5.get("scope_manifest_path") not in (None, scope_path):
        raise ValueError("G5_WRONG_SCOPE_PATH")
    if not rows or rows[-1] != g5:
        raise ValueError("NOT_LATEST_G5_REGISTRATION")
    return {"g4_sha": g4["stage_manifest_sha256"],
            "g5_sha": g5["stage_manifest_sha256"],
            "scope_sha": scope_sha, "scope_path": scope_path,
            "g5_predecessor": stage5["previous_manifest_path"]}


def main():
    rows = [json.loads(t) for t in (ROOT / LEDGER).read_text().splitlines() if t.strip()]
    g4s = [r for r in rows if r.get("epoch_id") == "SS-E02" and r.get("stage") == "G4_SCOPE_FREEZE" and r.get("status") == "active"]
    g5s = [r for r in rows if r.get("epoch_id") == "SS-E02" and r.get("stage") == "G5_FRESH_HOLDOUT_ACQUIRE" and r.get("status") == "active"]
    if not g4s or not g5s:
        raise ValueError("FROZEN_STAGES_MISSING")
    g4, g5 = g4s[-1], g5s[-1]
    if "scope_manifest_sha256" in g5:
        raise ValueError("REGISTRY_ALREADY_SCOPE_BOUND_NO_REPAIR")
    checks = check(g4, g5, g5s)
    old = (ROOT / LEDGER).read_text()
    prior_sha = hashlib.sha256(old.encode()).hexdigest()
    created = datetime.now(timezone.utc).isoformat()
    correction = dict(g5, event_type="verified_G5_scope_binding_correction", registered_at=created,
                      scope_manifest_path=checks["scope_path"],
                      scope_manifest_sha256=checks["scope_sha"],
                      original_registration_at=g5["registered_at"],
                      correction_of_omitted_registry_fields=True, original_registration_preserved=True,
                      not_a_new_G5_freeze=True, stage_is_metadata_only=True,
                      scientific_body_read=False, fresh_admitted=0, human_reviewed=False)
    if (ROOT / OUT).exists():
        raise ValueError("REPAIR_OUTPUT_ALREADY_EXISTS")
    note = {
        "task": TASK, "timestamp": created, "approval": "agent_delegated_execution_of_approved_TASK_016_P7",
        "reason": "SS_G5_SCOPE_BINDING_MISMATCH at command-4480; R4 metadata stage omitted frozen scope binding from registry",
        "original_g5_registry": g5, "validated": checks, "ledger_prior_sha256": prior_sha,
        "no_frozen_stage_or_scope_changed": True, "no_HTTP": True, "no_science_admission": True,
        "no_earlier_registry_gap_retroactively_closed": True,
        "P7_R5_input_script_sha_unchanged": True,
    }
    write(TASK, str(OUT / "preflight.json"), json.dumps(note, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    write(TASK, str(LEDGER), old + json.dumps(correction, ensure_ascii=False, sort_keys=True) + "\n")
    from scripts.task016_p7_ss_sources import require_acquisition_phase
    outcome = require_acquisition_phase("fresh", epoch_id="SS-E02",
        scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
    if outcome["G5_manifest_sha256"] != checks["g5_sha"] or outcome["G4_manifest_sha256"] != checks["g4_sha"]:
        raise ValueError("POSTGATE_WRONG_STAGES")
    end = {"preflight_sha256": digest(OUT / "preflight.json"),
           "ledger_after_sha256": digest(LEDGER),
           "correction": correction, "gate": outcome,
           "new_HTTP": 0, "new_MCTS": 0, "fresh_admitted": 0, "G5_scientific_eligibility": False}
    write(TASK, str(OUT / "validation.json"), json.dumps(end, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": "pass", "G4_SHA": checks["g4_sha"],
                      "G5_SHA": checks["g5_sha"], "scope_SHA": checks["scope_sha"],
                      "original_registry_row_preserved": True,
                      "original_command_4480_preserved": True, "fresh": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
