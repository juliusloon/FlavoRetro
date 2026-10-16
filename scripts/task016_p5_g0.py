"""TASK-016-P5 G0: takeover verification, execution approval, protection baseline, P4 reconciliation.

No source acquisition, no structure encoding, no template write and no MCTS in this
stage. The stage exists because the P5 contract opens from the *frozen* P4 artifacts,
not from the P4 report prose: the report text claims C=3/SS=5 and 23 HTTP / 1.13 MB /
40 reuse, while the frozen payload says C=1/SS=5 and 45 HTTP / 63,180,976 B /
reuse 74 / 5 article versions / 9 attachments. Both readings are recorded; the
frozen artifact is authoritative for P5 and the historical P4 file is not rewritten.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
SNAP = ROOT / "operations/task016-p5-original"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

CONTRACT = "docs/tasks/TASK-016-P5-c-ss-transfer-capability-closure.md"
CONTRACT_SHA = "baf3fbb076f1c68e893a257f9915d78c5985d95115f6bbba956665f005444266"
P4_REPORT = "docs/reports/REPORT-016-P4-p3-admission-correction-and-transfer-completion.md"
P4_TASK = "docs/tasks/TASK-016-P4-p3-admission-correction-and-transfer-completion.md"

# SHA-256 recorded in the P5 contract, section 2.2 plus the two additional P4
# artifacts the same section relies on for split and build provenance.
CONTRACT_P4_SHAS = {
    "outputs/task016-p4/v1/panel_manifest.json":
        "1fe41ed789b180d850949fce02ab9cf2c3c73e9a28f6bc7372d1acdbdb2b6dc2",
    "outputs/task016-p4/v1/c_class_g3_additions.json":
        "4ae074302ebaf5717ffc8f0d15aff0d0d760441c31bb5c0b325f048a79d1d42b",
    "outputs/task016-p4/v1/metrics_by_family.json":
        "871930840a50206d87574ec1d949e285dcbe4ec44ff9d6f8821b6f125e2b6661",
    "outputs/task016-p4/v1/run_ledger.jsonl":
        "04beecc4093941e6ec3c9bafc86b31059d21518b65330567350d87796ed4c53c",
    "outputs/task016-p4/v1/source_accounting.json":
        "82e544ecfcb0aab354980ecb0e07e0565d33e7330abe9fcbf0cd27c1d37a43c1",
    # additional P4 provenance the same reconciliation quotes
    "outputs/task016-p4/v1/split_manifest.json":
        "ee43247d9b5c508e05750a941a92b1c5573b20fd2ebfa91d2861d48f2e08b414",
    "outputs/task016-p4/v1/template_source_manifest.json":
        "b73cb3db4fa6ef2fbab64a9dfb4c04af038d4d661826c25f4755376727915346",
    "outputs/task016-p4/v1/corrected_reaction_records.jsonl":
        "e2e9564f63107cb4a229c1fc4efa654e9c7295bac548b5aa7d547528c10da6ab",
}

# P5 may add code; it may not rewrite the v1..v5 chain or the P1..P4 payloads.
MUTABLE_CODE = [
    "flavoretro/cli.py",
    "flavoretro/contracts.py",
    "flavoretro/search.py",
    "flavoretro/service.py",
    "flavoretro/task016_runs.py",
    "flavoretro/worker.py",
    "flavoretro/workspace.py",
]

DOC_MUTABLE = [
    "STATE.md",
    "ARCHITECTURE.md",
    "docs/README.md",
    "docs/tasks/README.md",
    "docs/reports/README.md",
    "docs/reports/REPORT-016-P5-c-ss-transfer-capability-closure.md",
]

# Inherited protection: everything P4 froze, re-verified rather than re-declared.
INHERIT_BASELINE = "outputs/task016-p4/v1/baseline_manifest.json"


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


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def rows(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def main():
    # 1. contract integrity: the approved text must be the text on disk
    contract_actual = sha(ROOT / CONTRACT)
    contract_mismatch = None
    if contract_actual != CONTRACT_SHA:
        contract_mismatch = {"expected": CONTRACT_SHA, "actual": contract_actual}

    # 2. every P4 artifact the P5 reconciliation quotes must be byte-identical
    p4_sha_check, p4_sha_mismatch = {}, {}
    for rel, expected in CONTRACT_P4_SHAS.items():
        actual = sha(ROOT / rel) if (ROOT / rel).is_file() else None
        p4_sha_check[rel] = actual
        if actual != expected:
            p4_sha_mismatch[rel] = {"expected": expected, "actual": actual}

    # 3. the inherited P4 protection set must show zero drift
    p4_baseline = json.loads((ROOT / INHERIT_BASELINE).read_text())
    inherited = p4_baseline["protected_sha256"]
    p4_drift = sorted(rel for rel, h in inherited.items()
                      if not (ROOT / rel).is_file() or sha(ROOT / rel) != h)

    # 4. the P4 delivery manifest must still reproduce
    p4_verify_rel = "outputs/task016-p4/v1/verify_summary.json"
    p4_delivery_drift = []
    if (ROOT / p4_verify_rel).is_file():
        p4_verify = json.loads((ROOT / p4_verify_rel).read_text())
        for name, h in p4_verify.get("delivery_sha256", {}).items():
            f = ROOT / "outputs/task016-p4/v1" / name
            if not f.is_file() or sha(f) != h:
                p4_delivery_drift.append(name)

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip()
    git_status = subprocess.run(["git", "status", "--short"], capture_output=True,
                                text=True, cwd=ROOT).stdout

    # 5. snapshot the code P5 is allowed to touch
    originals = {}
    for rel in MUTABLE_CODE:
        src = ROOT / rel
        if not src.is_file():
            continue
        snap = SNAP / rel
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, snap)
        originals[rel] = {"sha256": sha(src), "snapshot_path": str(snap.relative_to(ROOT))}
        event(TASK, "protect_snapshot", path=rel,
              snapshot=str(snap.relative_to(ROOT)), sha256=originals[rel]["sha256"])

    protected = {k: v for k, v in inherited.items()
                 if k not in MUTABLE_CODE and k not in DOC_MUTABLE}
    additions = [
        CONTRACT, P4_REPORT, P4_TASK, INHERIT_BASELINE, p4_verify_rel,
        "flavoretro/glycoside_library_v3.py",
        "flavoretro/glycoside_library_v4.py",
        "flavoretro/glycoside_library_v5.py",
        "configs/glycoside-library-v3.json",
        "configs/glycoside-library-v4.json",
        "configs/glycoside-library-v5.json",
        "flavoretro/assets/configs/glycoside-library-v3.json",
        "flavoretro/assets/configs/glycoside-library-v4.json",
        "flavoretro/assets/configs/glycoside-library-v5.json",
        "outputs/review/task015-06/v1/manifest.json",
    ]
    additions += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "scripts").glob("task016_p4_*.py"))
    for folder in ["outputs/task016-p4/v1", "outputs/task016-p3/v1", "outputs/task016-p2/v2"]:
        d = ROOT / folder
        if d.is_dir():
            additions += sorted(str(p.relative_to(ROOT)) for p in d.rglob("*")
                                if p.is_file() and not p.name.startswith("._"))
    added = 0
    for rel in additions:
        if rel in protected or rel in MUTABLE_CODE or rel in DOC_MUTABLE:
            continue
        f = ROOT / rel
        if f.is_file():
            protected[rel] = sha(f)
            added += 1

    budgets = {
        "source_HTTP_attempts": 3000,
        "source_bytes": 4 * 1024 ** 3,
        "article_versions": 200,
        "attachments": 360,
        "metadata_records": 5000,
        "per_file_bytes": 256 * 1024 ** 2,
        "per_url_attempts": 2,
        "concurrency": 4,
        "panel_first_round_search_attempts": 162,
        "legacy_first_round_search_attempts": 51,
        "matrix_revalidation_search_attempts": 213,
        "engineering_search_attempts": 54,
        "total_search_attempts": 480,
        "service_wall_seconds": 60,
    }
    old_ledgers = {rel: sha(ROOT / rel) for rel in [
        "outputs/task016/v1/run_ledger.jsonl",
        "outputs/task016-p1/v1/run_ledger.jsonl",
        "outputs/task016-p2/v1/run_ledger.jsonl",
        "outputs/task016-p3/v1/run_ledger.jsonl",
        "outputs/task016-p4/v1/run_ledger.jsonl",
    ] if (ROOT / rel).is_file()}

    # ------------------------------------------------------------ reconciliation
    panel = json.loads((ROOT / "outputs/task016-p4/v1/panel_manifest.json").read_text())
    metrics = json.loads((ROOT / "outputs/task016-p4/v1/metrics_by_family.json").read_text())
    accounting = json.loads((ROOT / "outputs/task016-p4/v1/source_accounting.json").read_text())
    split = json.loads((ROOT / "outputs/task016-p4/v1/split_manifest.json").read_text())
    g3 = json.loads((ROOT / "outputs/task016-p4/v1/c_class_g3_additions.json").read_text())
    ledger = rows(ROOT / "outputs/task016-p4/v1/run_ledger.jsonl")

    crosswalk = [
        dict(item="C_holdout_target_count",
             report_text_claim="C_transfer 行写「面板 1 目标（C12 + P4R-C01 + P4R-C04 = 3，仍 < 6）」，"
                               "同一句内部既写 1 又写 3，且把 C01/C04 算进面板",
             frozen_artifact_fact=f"panel_manifest.json panel.C_formation.targets = "
                                  f"{panel['panel']['C_formation']['targets']}，"
                                  f"targets_count = {panel['panel']['C_formation']['targets_count']}",
             authoritative_for_p5="frozen_artifact",
             p5_starting_value=1,
             why="P4R-C01/C04 只登记在 c_class_g3_additions.json 的 "
                 "independent_panel_targets，未进入 panel_manifest.json/jsonl、"
                 "split_manifest.json 或 heldout_references.jsonl，"
                 "且 p4_new_reaction_records 中仍为 structure_encoding=pending_G3_encoding",
             historical_file_rewritten=False),
        dict(item="C01_C04_status",
             report_text_claim="报告把 P4R-C01/C04 当作已产生的 C 面板目标",
             frozen_artifact_fact=f"c_class_g3_additions.json independent_panel_targets = "
                                  f"{g3['independent_panel_targets']}；两者均不在 "
                                  f"heldout_references.jsonl 的 {split['holdout_reactions']} 中",
             authoritative_for_p5="frozen_artifact",
             p5_starting_value="candidate_pool_not_frozen_holdout",
             why="P5 只能把它们当候选：用作 build support 则退出 holdout，"
                 "用作 holdout 则不得参与模板设计，两边不能同时计",
             historical_file_rewritten=False),
        dict(item="SS_holdout_target_count",
             report_text_claim="报告摘要写 C3/SS5",
             frozen_artifact_fact=f"panel_manifest.json panel.sugar_sugar_formation.targets_count = "
                                  f"{panel['panel']['sugar_sugar_formation']['targets_count']}",
             authoritative_for_p5="frozen_artifact",
             p5_starting_value=5,
             why="SS 口径一致，C 口径不一致",
             historical_file_rewritten=False),
        dict(item="v5_has_no_qualified_C_scope",
             report_text_claim="报告承认 P4 未取得合格 C 新范围",
             frozen_artifact_fact="v5 payload 只有 1 个 scope 模板 "
                                  "rhamnoside_glucoside_O2；"
                                  "metrics_by_family.engineering_preflight.quarantined_scopes_excluded "
                                  "记录 C_hydroxyflavanone_C3 与 rhamnoside_glucoside_O6 被隔离",
             authoritative_for_p5="frozen_artifact",
             p5_starting_value="no_qualified_C_build_scope",
             why="C_transfer 必须先补 build-side 范围，不能只补 holdout",
             historical_file_rewritten=False),
        dict(item="source_whole_task_accounting",
             report_text_claim="报告正文写「HTTP 23/2000、字节 1.13 MB/2 GiB、"
                               "文章 1/100、附件 0/180、复用既有原始件 40 个」",
             frozen_artifact_fact=f"source_accounting.json: http_attempts = "
                                  f"{accounting['http_attempts']}，bytes = {accounting['bytes']}，"
                                  f"article_versions = {accounting['article_versions']}，"
                                  f"attachments = {accounting['attachments']}，"
                                  f"reuse_of_prior_task_files = "
                                  f"{accounting['reuse_of_prior_task_files']}",
             authoritative_for_p5="frozen_artifact",
             p5_starting_value=dict(
                 http_attempts=accounting["http_attempts"],
                 bytes=accounting["bytes"],
                 article_versions=accounting["article_versions"],
                 attachments=accounting["attachments"],
                 reuse_of_prior_task_files=accounting["reuse_of_prior_task_files"]),
             why="23 / 1.13 MB / 40 是 discovery 阶段口径，不能当 whole-task 总账；"
                 "P5 必须把 discovery、new-download、whole-task 三套口径分开报告",
             historical_file_rewritten=False),
        dict(item="A_B_E_and_transfer_metrics",
             report_text_claim="报告写 A/B/E 未执行",
             frozen_artifact_fact=f"run_ledger.jsonl 共 {len(ledger)} 行，"
                                  f"其中 reservation attempts = "
                                  f"{[r.get('attempts') for r in ledger]}；"
                                  f"metrics_by_family.metrics_by_family.C.N_gap_family = "
                                  f"{metrics['metrics_by_family']['C']['N_gap_family']}，"
                                  f"SS.N_gap_family = "
                                  f"{metrics['metrics_by_family']['SS']['N_gap_family']}",
             authoritative_for_p5="frozen_artifact",
             p5_starting_value="attempts=0; all transfer metrics null",
             why="null 不等于 0：核心迁移能力至今未被实验测量过",
             historical_file_rewritten=False),
    ]
    save_jsonl("p4_fact_crosswalk.jsonl", crosswalk)

    reconciliation = {
        "task": TASK,
        "created_at": stamp(),
        "purpose": "P5 opens from frozen P4 artifacts, not from P4 report prose",
        "authoritative_rule": "the frozen payload under outputs/task016-p4/v1 wins over any "
                              "P4 report sentence; the P4 report, P4 TASK and every P4 frozen "
                              "artifact are left byte-identical",
        "contract_sha256_expected": CONTRACT_SHA,
        "contract_sha256_actual": contract_actual,
        "contract_sha_mismatch": contract_mismatch,
        "p4_artifact_sha_check": p4_sha_check,
        "p4_artifact_sha_mismatch": p4_sha_mismatch,
        "inherited_p4_protected_files": len(inherited),
        "inherited_p4_drift": p4_drift,
        "p4_delivery_manifest_drift": p4_delivery_drift,
        "historical_files_rewritten": False,
        "p5_starting_facts": {
            "C_holdout_targets": panel["panel"]["C_formation"]["targets_count"],
            "C_holdout_closure_groups": panel["panel"]["C_formation"]["groups_count"],
            "SS_holdout_targets": panel["panel"]["sugar_sugar_formation"]["targets_count"],
            "SS_holdout_closure_groups": panel["panel"]["sugar_sugar_formation"]["groups_count"],
            "C01_C04": "candidate pool; not frozen holdout; if used as build support they "
                       "leave the C holdout entirely",
            "p4_A_B_E_attempts": 0,
            "p4_C_transfer_metrics": "all null",
            "p4_source_whole_task_accounting": {
                "http_attempts": accounting["http_attempts"],
                "bytes": accounting["bytes"],
                "reuse_of_prior_task_files": accounting["reuse_of_prior_task_files"],
                "article_versions": accounting["article_versions"],
                "attachments": accounting["attachments"],
            },
            "p4_source_report_prose_accounting": {
                "http": 23, "megabytes": "1.13", "reused_files": 40,
                "note": "discovery-stage figures quoted in the P4 report; not the whole-task ledger",
            },
            "p5_gap": "C 1/6 and SS 5/6 on the frozen holdout; v5 holds no qualified C build scope",
        },
        "crosswalk_file": "p4_fact_crosswalk.jsonl",
        "crosswalk_items": len(crosswalk),
    }
    save("p4_reconciliation.json", reconciliation)

    approval = {
        "task": TASK,
        "created_at": stamp(),
        "approval_quote": "挂载读取, ssh cano 后操作, 执行 "
                          "docs/tasks/TASK-016-P5-c-ss-transfer-capability-closure.md. "
                          "你可以开 subagents, 可以调用 literature-search / "
                          "scienceclaw-investigate, 执行任务直到最终完成 task 要求.",
        "approval_type": "human_direct",
        "stage_decisions": "agent_delegated",
        "delegation_basis": "AGENTS.md 委托：阶段与撤回决定由 agent 代行；"
                            "批准本身是所有者本轮人工直接指令",
        "approved_contract_sha256": contract_actual,
        "contract": CONTRACT,
        "contract_version": "v0.1",
        "git_head": git_head,
        "git_status_short_lines": len(git_status.splitlines()),
        "baseline_note": "HEAD 仅作定位；现场文件 SHA 是实际基线；存在 TASK-015/016 前序未提交交付，"
                         "禁止 reset/clean/checkout --/按 HEAD 恢复",
        "execution_note": "本机 ~/FlavoRetro 不存在；实际工作区为 /Volumes/cano/FlavoRetro"
                          "（WebDAV 挂载）↔ ssh cano:/home/ljx/FlavoRetro；所有执行在 cano 上完成",
        "budgets": budgets,
        "budget_isolation": "P5 不借 P1–P4 旧账；独立账本 outputs/task016-p5/v1/run_ledger.jsonl",
        "old_ledgers_sha256": old_ledgers,
        "axis_status_policy": "七轴分判：p4_reconciliation / C_scope_capability / panel_integrity / "
                              "C_transfer / sugar_sugar_transfer / legacy_regression / "
                              "engineering_delivery；未执行指标写 null 不写 0",
        "panel_gates": "C≥6 complete targets/≥2 closure groups；SS≥6/≥2；全局 12–18；"
                       "deferred=0；build/holdout leakage=0",
        "transfer_gates": "每类 G≥3、G/N_gap≥50%、成功≥2 组、对 A 和 B 净覆盖均>0、"
                          "参照损失 0；且≥3 个目标在 A/B 三 seed 均不创建而 E 三 seed 均真实创建",
        "strongest_allowed_claim": "在 TASK-016-P5 冻结、development-exposed 但与模板构建隔离的"
                                   "新底物留出上，来源支持的 C/SS 范围能力表现出可审计的候选迁移，"
                                   "并在真实 MCTS 中稳定创建完整参照动作；旧能力无参照退化",
        "explicitly_not_claimed": ["independent_chemical_validation", "formal_run_ready",
                                  "release_ready", "evidence_closed", "actionable",
                                  "training_independence", "vendor_supply", "production"],
        "formal_run_ready": False,
        "release_ready": False,
        "human_reviewed_claimed": False,
        "no_git_sync": True,
        "stop_conditions_acknowledged": True,
    }
    save("approval.json", approval)

    baseline_manifest = {
        "task": TASK,
        "created_at": stamp(),
        "approval_sha256": sha(OUT / "approval.json"),
        "inherited_p4_baseline_sha256": sha(ROOT / INHERIT_BASELINE),
        "inherited_p4_protected_files": len(inherited),
        "inherited_p4_drift": p4_drift,
        "p4_artifact_sha_mismatch": p4_sha_mismatch,
        "p4_delivery_manifest_drift": p4_delivery_drift,
        "added_protected_files": added,
        "protected_sha256": protected,
        "mutable_code_originals": originals,
        "allowed_doc_mutations": sorted(DOC_MUTABLE),
        "budgets": budgets,
        "old_ledgers_sha256": old_ledgers,
        "git_head": git_head,
        "p5_output_namespace": "outputs/task016-p5/v1",
        "p5_raw_namespace": "data/raw/task016-p5",
        "checkpoints": ["G0"],
    }
    save("execution_baseline.json", baseline_manifest)

    save("protected_hashes.json", {
        "task": TASK, "created_at": stamp(),
        "count": len(protected),
        "contract_p4_sha_check": p4_sha_check,
        "contract_p4_sha_mismatch": p4_sha_mismatch,
        "mutable_code_originals": originals,
    })

    event(TASK, "g0_baseline",
          protected_files=len(protected),
          p4_drift=len(p4_drift),
          p4_sha_mismatch=len(p4_sha_mismatch),
          p4_delivery_drift=len(p4_delivery_drift),
          mutable=len(originals),
          contract_sha256=contract_actual,
          crosswalk_items=len(crosswalk))
    print(json.dumps({
        "contract_sha256": contract_actual,
        "contract_sha_mismatch": contract_mismatch,
        "p4_artifact_sha_mismatch": p4_sha_mismatch,
        "inherited_p4_drift": p4_drift,
        "p4_delivery_manifest_drift": p4_delivery_drift,
        "protected_files": len(protected),
        "mutable_originals": len(originals),
        "crosswalk_items": len(crosswalk),
        "p5_starting_facts": reconciliation["p5_starting_facts"],
        "git_head": git_head,
    }, ensure_ascii=False, indent=1))
    if contract_mismatch or p4_sha_mismatch or p4_drift or p4_delivery_drift:
        print("STOP: contract or protected P4 evidence drift; do not write P5 assets")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())