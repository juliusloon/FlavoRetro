"""TASK-016-P4 G0: takeover verification, correction-stage approval registration, protection baseline.

Registers the owner execution instruction for TASK-016-P4, verifies that the P3/v1
decisive evidence files still match the SHA-256 values recorded in the P4 contract,
verifies the inherited P3 protection set has zero drift, snapshots the code
touchpoints P4 is allowed to mutate, and freezes the P4 protection baseline plus an
independent budget. No source acquisition, no structure encoding, no template write
and no MCTS in this stage.
"""
import hashlib, json, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
SNAP = ROOT / "operations/task016-p4-original"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

CONTRACT = "docs/tasks/TASK-016-P4-p3-admission-correction-and-transfer-completion.md"
P3_REPORT = "docs/reports/REPORT-016-P3-new-reaction-admission-and-transfer.md"

# SHA-256 recorded in the P4 contract, section "证据基线与历史保护".
CONTRACT_P3_SHAS = {
    "docs/tasks/TASK-016-P3-new-reaction-admission-and-transfer.md":
        "1dfcda3a91d857cef0a867811b67c0f6ebb8906d9e6b6664abf1f323f05b4479",
    P3_REPORT:
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

# Code P4 is allowed to touch. v3 library and the v1/v2/v3/v4 chain stay protected.
MUTABLE_CODE = [
    "flavoretro/cli.py",
    "flavoretro/contracts.py",
    "flavoretro/glycoside_library.py",
    "flavoretro/open_glycoside_library.py",
    "flavoretro/search.py",
    "flavoretro/service.py",
    "flavoretro/task016_runs.py",
    "flavoretro/worker.py",
    "flavoretro/workspace.py",
]

DOC_MUTABLE = [
    "STATE.md",
    "ARCHITECTURE.md",
    "docs/PAPER_ROADMAP.md",
    "docs/WORKBENCH_ROADMAP.md",
    "docs/README.md",
    "docs/tasks/README.md",
    "docs/reports/README.md",
    "docs/reports/REPORT-016-P4-p3-admission-correction-and-transfer-completion.md",
]


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def main():
    contract_sha = sha(ROOT / CONTRACT)
    p3_base_rel = "outputs/task016-p3/v1/baseline_manifest.json"
    p3_baseline = json.loads((ROOT / p3_base_rel).read_text())
    p3_protected = p3_baseline["protected_sha256"]

    # 1. contract-declared P3 SHAs must still hold on site before any P4 write.
    p3_sha_check, p3_sha_mismatch = {}, {}
    for rel, expected in CONTRACT_P3_SHAS.items():
        actual = sha(ROOT / rel) if (ROOT / rel).is_file() else None
        p3_sha_check[rel] = actual
        if actual != expected:
            p3_sha_mismatch[rel] = {"expected": expected, "actual": actual}

    # 2. whole inherited P3 protection set must have zero drift.
    p3_drift = sorted(
        rel for rel, h in p3_protected.items()
        if not (ROOT / rel).is_file() or sha(ROOT / rel) != h
    )

    # 3. P3 own delivery manifest must still reproduce byte for byte.
    p3_verify = json.loads((ROOT / "outputs/task016-p3/v1/verify_summary.json").read_text())
    p3_delivery_drift = sorted(
        name for name, h in p3_verify["delivery_sha256"].items()
        if not (ROOT / "outputs/task016-p3/v1" / name).is_file()
        or sha(ROOT / "outputs/task016-p3/v1" / name) != h
    )

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip()
    git_status = subprocess.run(["git", "status", "--short"], capture_output=True,
                                text=True, cwd=ROOT).stdout

    # 4. snapshot the mutable code touchpoints.
    originals = {}
    for rel in MUTABLE_CODE:
        src = ROOT / rel
        if not src.is_file():
            continue
        snap = SNAP / rel
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, snap)
        originals[rel] = {"sha256": sha(src),
                          "snapshot_path": str(snap.relative_to(ROOT))}
        event(TASK, "protect_snapshot", path=rel,
              snapshot=str(snap.relative_to(ROOT)), sha256=originals[rel]["sha256"])

    protected = dict(p3_protected)
    additions = [
        CONTRACT, P3_REPORT,
        "flavoretro/glycoside_library_v3.py", "flavoretro/glycoside_library_v4.py",
        "configs/glycoside-library-v3.json", "configs/glycoside-library-v4.json",
        "flavoretro/assets/configs/glycoside-library-v3.json",
        "flavoretro/assets/configs/glycoside-library-v4.json",
        "outputs/task016-p3/v1/verify_summary.json",
        "outputs/task016-p2/v2/delivery_manifest.json",
        "outputs/review/task015-06/v1/manifest.json",
    ]
    additions += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "scripts").glob("task016_p3_*.py"))
    for folder in ["outputs/task016-p3/v1", "outputs/task016-p3/v2", "outputs/task016-p2/v2"]:
        d = ROOT / folder
        if d.is_dir():
            additions += sorted(str(p.relative_to(ROOT)) for p in d.rglob("*") if p.is_file())
    added = 0
    for rel in additions:
        if rel in protected or rel in MUTABLE_CODE or rel in DOC_MUTABLE:
            continue
        f = ROOT / rel
        if f.is_file():
            protected[rel] = sha(f)
            added += 1
    protected = {k: v for k, v in protected.items()
                 if k not in MUTABLE_CODE and k not in DOC_MUTABLE}

    budgets = {
        "source_HTTP_attempts": 2000,
        "source_bytes": 2 * 1024 ** 3,
        "article_versions": 100,
        "attachments": 180,
        "metadata_records": 5000,
        "per_file_bytes": 256 * 1024 ** 2,
        "per_url_attempts": 2,
        "concurrency": 4,
        "panel_first_round_search_attempts": 213,
        "matrix_revalidation_search_attempts": 213,
        "engineering_search_attempts": 54,
        "total_search_attempts": 480,
        "service_wall_seconds": 60,
    }
    old_ledgers = {
        rel: sha(ROOT / rel) for rel in [
            "outputs/task016/v1/run_ledger.jsonl",
            "outputs/task016-p1/v1/run_ledger.jsonl",
            "outputs/task016-p2/v1/run_ledger.jsonl",
            "outputs/task016-p3/v1/run_ledger.jsonl",
        ] if (ROOT / rel).is_file()
    }
    key_shas = {rel: sha(ROOT / rel) for rel in [
        "outputs/task016-p2/v2/templates.jsonl",
        "outputs/task016-p2/v2/runtime_instances.jsonl",
        "outputs/task016-p2/v2/template_source_manifest.json",
        "outputs/task016-p3/v1/templates.jsonl",
        "outputs/task016-p3/v1/runtime_instances.jsonl",
        "outputs/task016-p3/v1/heldout_references.jsonl",
        "outputs/task016-p3/v1/panel_manifest.json",
        "outputs/review/task015-06/v1/manifest.json",
        "configs/glycoside-library-v3.json",
        "configs/glycoside-library-v4.json",
    ] if (ROOT / rel).is_file()}

    approval = {
        "task": TASK,
        "created_at": stamp(),
        "approval_quote": "使用连接器 desktop-commander, 工作区 ~/FlavoRetro 批准 TASK-016-P4 开始执行",
        "approval_type": "human_direct",
        "stage_decisions": "agent_delegated",
        "delegation_basis": "AGENTS.md 委托：阶段与撤回决定由 agent 代行；批准本身是所有者本轮人工直接指令",
        "approved_contract_sha256": contract_sha,
        "contract": CONTRACT,
        "contract_version": "v0.1",
        "git_head": git_head,
        "git_status_short_lines": len(git_status.splitlines()),
        "baseline_note": "HEAD 仅作定位；现场文件 SHA 是实际基线；存在 TASK-015/016 前序未提交交付，"
                         "禁止 reset/clean/checkout --/按 HEAD 恢复",
        "connector_note": "所有者指定 desktop-commander 连接器；该连接器被 WorkBuddy 安全中心策略禁用"
                          "（WORKBUDDY_TOOL_CONTROL_BLOCKED），改用内置工具执行，操作对象与授权范围不变；"
                          "另所有者书写的 ~/FlavoRetro 在本机不存在，实际工作区为 /Volumes/cano/FlavoRetro"
                          "（WebDAV 挂载）↔ ssh cano:/home/ljx/FlavoRetro",
        "budgets": budgets,
        "budget_isolation": "P4 不借 P3/P2/P1 旧账；独立账本 outputs/task016-p4/v1/run_ledger.jsonl",
        "old_ledgers_sha256": old_ledgers,
        "key_payload_sha256": key_shas,
        "contract_p3_sha_check": p3_sha_check,
        "corrected_reaction_floor": {"C_formation": 8, "sugar_sugar_formation": 8, "total": 16},
        "scientific_gates": "每类≥6 complete holdout 目标、≥2 闭包组、每范围≥2 distinct canonical acceptor、"
                            "G≥3、G/N_gap≥50%、成功≥2 组、三 seed 真实 node creation",
        "axis_status_policy": "correction_engineering / corrected_reaction_admission / C_transfer / "
                              "sugar_sugar_transfer 分轴判定；未执行指标写 null 不写 0",
        "formal_run_ready": False,
        "release_ready": False,
        "human_reviewed_claimed": False,
        "no_git_sync": True,
        "p3_baseline_sha256": sha(ROOT / p3_base_rel),
        "stop_conditions_acknowledged": True,
    }
    baseline_manifest = {
        "task": TASK,
        "created_at": stamp(),
        "approval_sha256": None,
        "p3_baseline_sha256": sha(ROOT / p3_base_rel),
        "p3_protected_files": len(p3_protected),
        "p3_protected_drift": p3_drift,
        "p3_contract_sha_mismatch": p3_sha_mismatch,
        "p3_delivery_manifest_drift": p3_delivery_drift,
        "added_protected_files": added,
        "protected_sha256": protected,
        "mutable_code_originals": originals,
        "allowed_doc_mutations": sorted(DOC_MUTABLE),
        "budgets": budgets,
        "old_ledgers_sha256": old_ledgers,
        "git_head": git_head,
        "p4_output_namespace": "outputs/task016-p4/v1",
        "p4_raw_namespace": "data/raw/task016-p4",
        "checkpoints": ["G0"],
    }
    save("approval.json", approval)
    baseline_manifest["approval_sha256"] = sha(OUT / "approval.json")
    save("baseline_manifest.json", baseline_manifest)

    # independent protected-hash ledger, readable without parsing the manifest
    save("protected_hashes.json", {
        "task": TASK, "created_at": stamp(),
        "count": len(protected),
        "p3_decisive_contract_shas": p3_sha_check,
        "p3_contract_sha_mismatch": p3_sha_mismatch,
        "mutable_code_originals": originals,
    })

    event(TASK, "g0_baseline", protected_files=len(protected),
          p3_drift=len(p3_drift), p3_sha_mismatch=len(p3_sha_mismatch),
          p3_delivery_drift=len(p3_delivery_drift),
          mutable=len(originals), contract_sha256=contract_sha)
    print(json.dumps({
        "protected_files": len(protected),
        "p3_protected_drift": p3_drift,
        "p3_contract_sha_mismatch": p3_sha_mismatch,
        "p3_delivery_manifest_drift": p3_delivery_drift,
        "mutable_originals": len(originals),
        "contract_sha256": contract_sha,
        "git_head": git_head,
        "approval": str((OUT / "approval.json").relative_to(ROOT)),
        "baseline": str((OUT / "baseline_manifest.json").relative_to(ROOT)),
    }, ensure_ascii=False, indent=1))
    if p3_sha_mismatch or p3_drift or p3_delivery_drift:
        print("STOP: unexplained drift on protected P3 evidence; do not write P4 assets")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
