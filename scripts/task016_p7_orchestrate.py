"""P7 stage/epoch/budget contracts. No chemistry eligibility decisions."""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import write

TASK = "TASK-016-P7"
ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    "G0_BASELINE", "G1_EXPOSURE_LEDGER", "G2_DESIGN_ACQUIRE",
    "G3_SCOPE_BUILD", "G4_SCOPE_FREEZE", "G5_FRESH_HOLDOUT_ACQUIRE",
    "G6_IDENTITY_STRUCTURE_ADMIT", "G7_CLOSURE_PANEL_FREEZE",
    "G8_STATIC_PREFLIGHT", "G9_RUNTIME_FREEZE", "G10_ABE_RUN",
    "G11_LEGACY_REGRESSION", "G12_INDEPENDENT_VERIFY", "G13_REPORT",
)
MCTS_CATEGORIES = ("C_first_matrix", "SS_first_matrix", "legacy_canary", "engineering", "revalidation")
LIMITS = dict(search_attempts=600, C_first_matrix=81, SS_first_matrix=81,
              legacy_canary=90, engineering=60, revalidation=252, HTTP=8000,
              bytes=8*1024**3, article_versions=400, attachments=800,
              concurrency=4, per_url_attempts=2, recovery_extra_attempts=1)


class ContractError(ValueError):
    """Missing, inconsistent or mutable evidence must fail closed."""


def now():
    return datetime.now(timezone.utc).isoformat()


def require_fields(record, fields, *, nullable=()):
    if not isinstance(record, dict):
        raise ContractError("record must be an object")
    missing = [key for key in fields if key not in record]
    empty = [key for key in fields if key in record and record[key] is None and key not in nullable]
    if missing or empty:
        raise ContractError(f"required fields missing={missing} null={empty}")
    return record


def require_int(value, name, *, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ContractError(f"{name} must be an integer >= {minimum}")
    return value


def sha_json(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_json(path, value, *, immutable=False, root=ROOT):
    path = Path(path)
    if not path.is_absolute():
        path = root/path
    if not path.resolve().is_relative_to(root.resolve()):
        raise ContractError("output outside task workspace")
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)+"\n"
    if immutable and path.exists():
        if path.read_text() != text:
            raise ContractError("immutable manifest already exists")
        return sha_file(path)
    write(TASK, str(path.relative_to(ROOT)), text)
    return sha_file(path)


def verify_hashes(files, *, root=ROOT):
    if not isinstance(files, dict) or not files:
        raise ContractError("manifest requires nonempty file SHA bindings")
    for name,expected in files.items():
        path=root/name
        if not path.resolve().is_relative_to(root.resolve()) or not isinstance(expected,str) or len(expected)!=64:
            raise ContractError("manifest file binding malformed/outside workspace")
    drift = [name for name, expected in files.items()
             if not (root/name).is_file() or sha_file(root/name) != expected]
    if drift:
        raise ContractError(f"manifest drift: {drift}")
    return True


def role_manifest(role, epoch_id, inputs, outputs, counts, *, pointers=(), errors=(),
                  unprocessed=(), read_holdout=False, read_model_outcome=False, root=ROOT):
    require_fields(counts, ("processed", "passed", "rejected", "pending"))
    for name in counts:
        require_int(counts[name], name)
    if counts["processed"] != counts["passed"]+counts["rejected"]+counts["pending"]:
        raise ContractError("role disposition counts do not conserve")
    bindings = lambda paths: {str(Path(p).relative_to(root) if Path(p).is_absolute() else p):
                             sha_file(Path(p) if Path(p).is_absolute() else root/p) for p in paths}
    result = dict(task=TASK, epoch_id=epoch_id, agent_role=role, timestamp=now(),
                  input_manifest_sha=bindings(inputs), output_file_sha=bindings(outputs),
                  source_evidence_pointers=list(pointers), counts=counts,
                  errors=list(errors), unprocessed=list(unprocessed),
                  read_holdout=bool(read_holdout), read_model_outcome=bool(read_model_outcome),
                  approval_type="agent_delegated", human_reviewed=False)
    if role in ("A7", "A7 Scope Builder") and (read_holdout or read_model_outcome):
        raise ContractError("scope builder read prohibited inputs")
    return result


class EpochState:
    """C and SS stages advance independently; chemical extraction is irreversible."""

    def __init__(self, family, epoch_number=1, *, historical_exposures=()):
        if family not in ("C", "SS"):
            raise ContractError("unknown family")
        require_int(epoch_number, "epoch_number", minimum=1)
        self.family = family
        self.epoch_number = epoch_number
        self.epoch_id = f"{family}-E{epoch_number:02d}"
        self.stage = "G0_BASELINE"
        self.manifest_sha = None
        self.scope_sha = None
        self.scope_frozen_at = None
        self.extracted = []
        self.permanent_exposures = set(historical_exposures)
        self.status = "active"
        self.stage_records = []

    def transition(self, stage, manifest, *, expected_previous_sha, root=ROOT, validate_files=True):
        if self.status != "active":
            raise ContractError("inactive epoch cannot advance")
        position = STAGES.index(self.stage)
        if stage not in STAGES or STAGES.index(stage) != position+1:
            raise ContractError("stage transition must consume immediate predecessor")
        if expected_previous_sha != self.manifest_sha:
            raise ContractError("predecessor SHA mismatch")
        require_fields(manifest, ("family", "epoch_id", "stage", "input_manifest_sha", "files"), nullable=("input_manifest_sha",))
        if manifest["family"] != self.family or manifest["epoch_id"] != self.epoch_id or manifest["stage"] != stage:
            raise ContractError("stage manifest belongs to different epoch")
        if manifest["input_manifest_sha"] != expected_previous_sha:
            raise ContractError("manifest chain mismatch")
        if not manifest["files"]:
            raise ContractError("stage manifest has no bound outputs")
        if validate_files:
            verify_hashes(manifest["files"],root=root)
            for previous in self.stage_records:
                verify_hashes(previous["files"],root=root)
        self.stage = stage
        self.manifest_sha = sha_json(manifest)
        self.stage_records.append(copy.deepcopy(manifest))
        return self.manifest_sha

    def freeze_scope(self, bank, *, stage_manifest_sha):
        if self.stage != "G4_SCOPE_FREEZE" or stage_manifest_sha != self.manifest_sha:
            raise ContractError("scope freeze requires verified G4 manifest")
        digest = sha_json(bank)
        if self.scope_sha is not None and self.scope_sha != digest:
            raise ContractError("frozen scope mutation requires new epoch")
        self.scope_sha = digest
        self.scope_frozen_at = now()
        return digest

    def record_extraction(self, candidate_id, *, scope_sha, metadata_only=False):
        if metadata_only:
            return dict(candidate_id=candidate_id, exposure="metadata_only")
        if self.status != "active" or self.scope_sha is None or scope_sha != self.scope_sha:
            raise ContractError("fresh extraction must follow immutable scope freeze")
        if STAGES.index(self.stage) < STAGES.index("G5_FRESH_HOLDOUT_ACQUIRE"):
            raise ContractError("chemical extraction before G5 prohibited")
        if candidate_id in self.permanent_exposures:
            raise ContractError("historical exposure cannot become fresh")
        if candidate_id in self.extracted:
            raise ContractError("candidate already extracted")
        self.extracted.append(candidate_id)
        return dict(candidate_id=candidate_id, extracted_at=now(), scope_sha=scope_sha,
                    epoch_id=self.epoch_id, exposure="post_scope_evaluation")

    def invalidate(self, reason):
        if not reason:
            raise ContractError("epoch failure needs explicit reason")
        self.status = "development_epoch_incomplete"
        self.permanent_exposures.update(self.extracted)
        successor = EpochState(self.family, self.epoch_number+1,
                               historical_exposures=self.permanent_exposures)
        return successor

    def as_dict(self):
        return dict(family=self.family, epoch_id=self.epoch_id, stage=self.stage,
                    manifest_sha=self.manifest_sha, scope_sha=self.scope_sha,
                    scope_frozen_at=self.scope_frozen_at, extracted=self.extracted,
                    permanent_exposures=sorted(self.permanent_exposures), status=self.status,
                    stage_records=self.stage_records)


class BudgetLedger:
    """Reservations are append-only and counted even after failed attempts."""

    def __init__(self, entries=(), limits=None):
        self.limits = copy.deepcopy(LIMITS if limits is None else limits)
        self.entries = copy.deepcopy(list(entries))
        for entry in self.entries:
            require_fields(entry, ("category", "amount", "id", "timestamp"))
        self._check()

    def _totals(self):
        totals = {name: 0 for name in self.limits}
        for row in self.entries:
            if row["category"] not in self.limits:
                raise ContractError("unknown budget category")
            require_int(row["amount"], "reservation amount", minimum=1)
            totals[row["category"]] += row["amount"]
        totals["search_attempts"] += sum(totals[name] for name in MCTS_CATEGORIES)
        return totals

    def _check(self):
        totals = self._totals()
        if len({row["id"] for row in self.entries}) != len(self.entries):
            raise ContractError("duplicate budget reservation id")
        for category, limit in self.limits.items():
            if totals[category] > limit:
                raise ContractError(f"budget exhausted: {category}")
        return totals

    def reserve(self, category, amount, reservation_id, **details):
        require_int(amount, "amount", minimum=1)
        trial = self.entries + [dict(category=category, amount=amount, id=reservation_id,
                                     timestamp=now(), **details)]
        validated = BudgetLedger(trial, self.limits)
        self.entries = validated.entries
        return self._check()

    def write_ledger(self, path):
        write(TASK, str(Path(path).relative_to(ROOT) if Path(path).is_absolute() else path),
              "".join(json.dumps(row, ensure_ascii=False, sort_keys=True)+"\n" for row in self.entries))

    def audit(self):
        return dict(limits=self.limits, totals=self._check(), remaining={
            category: limit-self._totals()[category] for category, limit in self.limits.items()})


def freeze_stage_manifest(folder, stage, files, previous_manifest_path=None, *,
                          expected_previous_sha=None, family="global", epoch_id="baseline"):
    """Persist a stage only after verifying the immediately preceding immutable output."""
    folder=Path(folder)
    if not folder.is_absolute():
        folder=ROOT/folder
    if stage not in STAGES:
        raise ContractError("unknown stage")
    if not files:
        raise ContractError("stage output universe empty")
    previous=None
    if stage=="G0_BASELINE":
        if previous_manifest_path is not None or expected_previous_sha is not None:
            raise ContractError("G0 has no predecessor")
    else:
        if previous_manifest_path is None or expected_previous_sha is None:
            raise ContractError("stage requires explicit predecessor file SHA")
        previous_path=Path(previous_manifest_path)
        if not previous_path.is_absolute():
            previous_path=ROOT/previous_path
        if not previous_path.is_file() or sha_file(previous_path)!=expected_previous_sha:
            raise ContractError("predecessor immutable manifest drift")
        previous=json.loads(previous_path.read_text())
        require_fields(previous,("stage","family","epoch_id","files"))
        if STAGES.index(previous["stage"])+1!=STAGES.index(stage):
            raise ContractError("stage skipped immediate predecessor")
        branching = stage=="G2_DESIGN_ACQUIRE" and previous["family"]=="global"
        if not branching and (previous["family"]!=family or previous["epoch_id"]!=epoch_id):
            raise ContractError("stage consumed another family/epoch")
        verify_stage_chain(previous_path,expected_previous_sha)
    bindings={}
    for name in files:
        path=Path(name)
        if not path.is_absolute():
            path=ROOT/path
        if not path.resolve().is_relative_to(ROOT.resolve()) or not path.is_file():
            raise ContractError("stage output missing/outside workspace")
        bindings[str(path.relative_to(ROOT))]=sha_file(path)
    manifest=dict(task=TASK,stage=stage,family=family,epoch_id=epoch_id,timestamp=now(),
                  previous_manifest_path=str(previous_path.relative_to(ROOT)) if previous is not None else None,
                  input_manifest_sha=expected_previous_sha,files=bindings,
                  approval_type="agent_delegated",human_reviewed=False)
    save_json(folder/(stage+".json"),manifest,immutable=True)
    return manifest


def reserve_budget_atomic(path, category, amount, reservation_id, *, limits=None, **details):
    """Serialize independent process reservations against the same immutable journal."""
    import fcntl
    from scripts.operate import event
    path=Path(path)
    if not path.is_absolute():
        path=ROOT/path
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ContractError("budget ledger outside workspace")
    path.parent.mkdir(parents=True,exist_ok=True)
    lock_path=path.with_suffix(path.suffix+".lock")
    existed=lock_path.exists()
    with lock_path.open("a") as lock:
        if not existed:
            event(TASK,"budget_lock_created",path=str(lock_path.relative_to(ROOT)))
        fcntl.flock(lock,fcntl.LOCK_EX)
        entries=[json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []
        ledger=BudgetLedger(entries,limits)
        ledger.reserve(category,amount,reservation_id,**details)
        ledger.write_ledger(path)
        return ledger.audit()


def verify_stage_chain(path, expected_sha, *, root=ROOT, seen=None):
    """Recheck every immutable upstream stage, plus protected historical bytes."""
    path=Path(path)
    if not path.is_absolute():
        path=root/path
    if not path.resolve().is_relative_to(root.resolve()):
        raise ContractError("upstream stage outside workspace")
    if seen is None:
        seen=set()
    resolved=str(path.resolve())
    if resolved in seen:
        raise ContractError("cycle in stage provenance chain")
    seen.add(resolved)
    if not path.is_file() or sha_file(path)!=expected_sha:
        raise ContractError("upstream stage manifest SHA drift")
    manifest=json.loads(path.read_text())
    require_fields(manifest,("task","stage","family","epoch_id","files","previous_manifest_path","input_manifest_sha"),
                   nullable=("previous_manifest_path","input_manifest_sha"))
    if manifest["task"]!=TASK:
        raise ContractError("upstream manifest from another task")
    verify_hashes(manifest["files"],root=root)
    if manifest["stage"]=="G0_BASELINE":
        if manifest["previous_manifest_path"] is not None or manifest["input_manifest_sha"] is not None:
            raise ContractError("G0 cannot have an upstream stage")
        approvals=[root/name for name in manifest["files"] if Path(name).name=="approval.json"]
        if len(approvals)!=1:
            raise ContractError("G0 must root in one immutable owner approval")
        approval=json.loads(approvals[0].read_text())
        if approval.get("task")!=TASK or approval.get("approval_type")!="agent_delegated" or approval.get("human_reviewed") is not False:
            raise ContractError("G0 approval binding invalid")
        for name in manifest["files"]:
            artifact=root/name
            if artifact.name=="protected_hashes.json":
                verify_hashes(json.loads(artifact.read_text()),root=root)
            elif artifact.name=="execution_baseline.json":
                baseline=json.loads(artifact.read_text())
                for original in baseline.get("mutable_originals",{}).values():
                    if sha_file(root/original["snapshot"])!=original["sha256"]:
                        raise ContractError("immutable actual-workspace baseline snapshot drift")
        return manifest
    parent_path=manifest["previous_manifest_path"]
    parent_sha=manifest["input_manifest_sha"]
    if parent_path is None or parent_sha is None:
        raise ContractError("stage upstream chain is unrooted")
    parent=verify_stage_chain(root/parent_path,parent_sha,root=root,seen=seen)
    if STAGES.index(parent["stage"])+1!=STAGES.index(manifest["stage"]):
        raise ContractError("upstream stage sequence drift")
    branch=manifest["stage"]=="G2_DESIGN_ACQUIRE" and parent["family"]=="global"
    if not branch and (parent["family"]!=manifest["family"] or parent["epoch_id"]!=manifest["epoch_id"]):
        raise ContractError("upstream family/epoch drift")
    return manifest
