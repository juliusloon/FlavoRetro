"""TASK-016-P3 G0: takeover verification, execution approval registration, protection baseline.

Registers the owner execution instruction, the approved contract SHA and budgets,
verifies the inherited P2 protected set has zero drift, snapshots mutable code
touchpoints, and freezes the P3 protection baseline. No source acquisition, no
code mutation, no search in this stage.
"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P3"
OUT = ROOT / "outputs/task016-p3/v1"
SNAP = ROOT / "operations/task016-p3-original"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)), json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def main():
    contract_rel = "docs/tasks/TASK-016-P3-new-reaction-admission-and-transfer.md"
    contract_sha = sha(ROOT / contract_rel)
    p2_base_rel = "outputs/task016-p2/v1/execution-baseline.json"
    p2_baseline = json.loads((ROOT / p2_base_rel).read_text())
    p2_protected = p2_baseline["protected_sha256"]

    drift = [rel for rel, h in p2_protected.items() if not (ROOT / rel).is_file() or sha(ROOT / rel) != h]

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    git_status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=ROOT).stdout

    mutable = sorted(p2_baseline["mutable_code_originals"].keys())
    originals = {}
    for rel in mutable:
        src = ROOT / rel
        snap = SNAP / rel
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, snap)
        originals[rel] = {"sha256": sha(src), "snapshot_path": str(snap.relative_to(ROOT))}
        event(TASK, "protect_snapshot", path=rel, snapshot=str(snap.relative_to(ROOT)), sha256=originals[rel]["sha256"])

    protected = dict(p2_protected)
    additions = [
        "flavoretro/glycoside_library_v3.py",
        "configs/glycoside-library-v3.json",
        "flavoretro/assets/configs/glycoside-library-v3.json",
        "tests/test_task016_p2_library.py",
    ]
    additions += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "scripts").glob("task016_p2_*.py"))
    for folder in [
        "outputs/task016/v1", "outputs/task016-p1/v1", "outputs/task016-p1/v2",
        "outputs/task016-p2/v1", "outputs/task016-p2/v2",
        "outputs/review/task015-06/v1", "outputs/review/task015-p3/gold-v1",
        "outputs/triage/task014-final",
    ]:
        d = ROOT / folder
        if d.is_dir():
            additions += sorted(str(p.relative_to(ROOT)) for p in d.rglob("*") if p.is_file())
    additions.append(contract_rel)
    doc_mutable = {
        "STATE.md", "ARCHITECTURE.md", "docs/PAPER_ROADMAP.md", "docs/WORKBENCH_ROADMAP.md",
        "docs/README.md", "docs/tasks/README.md", "docs/reports/README.md",
        "docs/reports/REPORT-016-P3-new-reaction-admission-and-transfer.md",
    }
    added = 0
    for rel in additions:
        if rel in protected or rel in mutable or rel in doc_mutable:
            continue
        f = ROOT / rel
        if f.is_file():
            protected[rel] = sha(f)
            added += 1
    protected = {k: v for k, v in protected.items() if k not in mutable and k not in doc_mutable}

    budgets = {
        "source_bytes": 4 * 1024 ** 3,
        "source_HTTP_attempts": 4000,
        "metadata_records": 8000,
        "article_versions": 150,
        "attachments": 300,
        "per_file_bytes": 256 * 1024 ** 2,
        "per_url_attempts": 2,
        "concurrency": 4,
        "validation_search_attempts": 426,
        "engineering_search_attempts": 54,
        "total_search_attempts": 480,
        "service_wall_seconds": 60,
    }
    old_ledgers = {
        "outputs/task016/v1/run_ledger.jsonl": sha(ROOT / "outputs/task016/v1/run_ledger.jsonl"),
        "outputs/task016-p1/v1/run_ledger.jsonl": sha(ROOT / "outputs/task016-p1/v1/run_ledger.jsonl"),
        "outputs/task016-p2/v1/run_ledger.jsonl": sha(ROOT / "outputs/task016-p2/v1/run_ledger.jsonl"),
    }
    key_contract_shas = {rel: sha(ROOT / rel) for rel in [
        "outputs/task016-p2/v2/delivery_manifest.json",
        "outputs/task016-p2/v2/template_source_manifest.json",
        "outputs/task016-p2/v2/development_split_manifest.json",
        "outputs/task016-p2/v2/runtime_instances.jsonl",
        "outputs/task016-p2/v2/templates.jsonl",
        "outputs/review/task015-06/v1/manifest.json",
        "configs/glycoside-library-v3.json",
    ]}

    approval = {
        "task": TASK,
        "created_at": stamp(),
        "approval_quote": "同意开始执行（所有者本会话执行指令；要求参考 nature-academic-search 等 skill）",
        "approval_type": "human_direct",
        "stage_decisions": "agent_delegated",
        "delegation_basis": "AGENTS.md 委托：本次用户授予 Cano 自主审批权，批准记录写 agent_delegated，禁止伪装 human_reviewed",
        "approved_contract_sha256": contract_sha,
        "contract": contract_rel,
        "contract_version": "v0.1",
        "git_head": git_head,
        "git_status": git_status,
        "baseline_note": "HEAD仅作定位；当前文件哈希是实际基线；存在前序未提交交付，禁止重置、清理或仅按HEAD恢复",
        "budgets": budgets,
        "old_ledgers_sha256": old_ledgers,
        "key_payload_sha256": key_contract_shas,
        "skill_reference": "nature-academic-search v2.0.0 workflow=multi-source-search（G1 文献发现/获取路由）",
        "new_reaction_floor": {"C_formation": 8, "sugar_sugar_formation": 8, "total": 16},
        "scientific_gates": "每类≥6新留出目标、≥2闭包组、G≥3、G/N_gap≥50%、成功≥2组、三seed真实创建；继承P2 6/2/3/50%门槛",
        "formal_run_ready": False,
        "release_ready": False,
        "no_git_sync": True,
        "p2_baseline_sha256": sha(ROOT / p2_base_rel),
    }
    baseline_manifest = {
        "task": TASK,
        "created_at": stamp(),
        "approval_sha256": None,
        "p2_baseline_sha256": sha(ROOT / p2_base_rel),
        "p2_protected_files": len(p2_protected),
        "p2_protected_drift": drift,
        "added_protected_files": added,
        "protected_sha256": protected,
        "mutable_code_originals": originals,
        "allowed_doc_mutations": sorted(doc_mutable),
        "budgets": budgets,
        "git_head": git_head,
        "checkpoints": ["G0"],
    }
    save("approval.json", approval)
    baseline_manifest["approval_sha256"] = sha(OUT / "approval.json")
    save("baseline_manifest.json", baseline_manifest)
    event(TASK, "g0_baseline", protected_files=len(protected), drift=len(drift), mutable=len(originals), contract_sha256=contract_sha)
    print(json.dumps({
        "protected_files": len(protected),
        "p2_drift": drift,
        "mutable_originals": len(originals),
        "contract_sha256": contract_sha,
        "approval": str((OUT / "approval.json").relative_to(ROOT)),
        "baseline": str((OUT / "baseline_manifest.json").relative_to(ROOT)),
    }, indent=1))


if __name__ == "__main__":
    main()
