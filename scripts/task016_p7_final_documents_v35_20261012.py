"""Final session documents for TASK-016-P7 (progress-v35-final).

Archives pre-v35 REPORT/STATE bytes, refreshes the REPORT header, appends the
session close-out section, replaces the STATE TASK-016-P7 tail block, and writes
the v35-final snapshot. Historical sections preserved verbatim; idempotent.
"""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

from scripts.operate import ROOT, write

TASK = "TASK-016-P7"
B = Path("outputs/task016-p7/v1")
SNAP = B / "report_snapshots"
ARCH = SNAP / "progress-v35-inputs/prior_documents"
REPORT = Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE = Path("STATE.md")
STOP_REVIEW = B / "governance/R74-R75-source-loop-stop-review-v1/source_loop_stop_review.json"
R74 = B / "SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1"
REPAIR = B / "governance/SS_E02_R73_G5_scope_binding_repair_v1/validation.json"
MARK = "progress-v35-final：本会话来源循环收口"
STATE_MARK = "progress-v35-final（2026-10-12"


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def pointer(p):
    return {"path": str(p), "sha256": sha(p)}


NEW_HEADER = (
    "状态：**Partial（2026-10-12 本会话收口：来源循环按合同 §6.3 条件3/4停止且两轴面板不足；科学迁移未执行）**。"
    "当前权威截面 **progress-v35-final（见文末）**：两轴独立发现轮（C 0 候选；SS 唯一机械 fresh 候选豌豆1982无合法OA副本）、"
    "R74 预注册元数据轮、饱和与访问边界评审、R73 G5 登记绑定修复；阶段决定 agent_delegated，非 human_reviewed。"
    "C/SS G4/scope 原SHA不变，合格 fresh 仍 0/0、科学 A/B/E 0 cell、迁移指标 null，G7/G8/新bank G9 未形成，Roadmap P2 未关闭；"
    "C-E02/SS-E02 epoch 保持开放（冻结 scope 下未来可依新 G5 批次续作）。"
    "progress-v34-stopped 及更早截面为历史记录，保留原时点事实；20 问答中历史数字仅指其当时截面。"
)

SECTION = """

## progress-v35-final：本会话来源循环收口——饱和与访问边界证据（2026-10-12）

任务阶段结论：**Partial（合同 §6.3 强制：来源循环按条件3/4停止且面板不足，不得降门）**；批准与阶段决定 agent_delegated，非 human_reviewed。C/SS G4/scope 原SHA不变；合格 fresh 仍 C0/SS0；科学 A/B/E 0 cell、迁移指标 null；G7/G8/新bank G9 未形成；Roadmap P2 未关闭。**C-E02/SS-E02 两个 epoch 保持开放未注销**（冻结 scope 仍有效；未来获合法原件或新合格来源后，可依新 G5 批次在同一冻结 scope 下续作；关闭 epoch 会按门槛设计禁止 fresh 采集）。本截面不是 Completed 验收。

1. **两轴独立发现轮（本轮，纯联网元数据检索，无化学检视）**。C 轴研究员系统排查约 40 条线索（EPMC 短语/年代窗查询、酶名批量查询、DOI 解析、LaCGT1/耐盐CGT三酶/乌蕨ScCGT1/PNAS2020 全文级核读、18 个 phloretin CGT 摘要等），**0 个合格新候选**；SS 轴研究员 16 条检索路线（hitCount 逐条记录），**唯一机械 fresh 候选为豌豆 Jourdan & Mansell 1982（ABB 213:434-443，DOI 10.1016/0003-9861(82)90569-0，PMID 6462109）**。两份完整检索报告（含检索方法与全部查询词）已归档：`discovery_evidence/session_20261012/`。检索工具内部传输不可观测，按 R72 先例单列，不入物理HTTP精确账。

2. **本地曝光核验**。豌豆1982 在 C-E02-R11 为 metadata-only 提示（R11-RESOLVE-DB-01-O0014：source_hint_only=true、identity_not_verified=true、historical_source_token_overlap=[]，inEPMC=N/inPMC=N/isOpenAccess=N），从未化学检视、无曝光令牌重叠、曝光账 0 行；其与已曝光 1979 豌豆文（人工接管 #14，G6 限定裁定 DEFERRED_NOT_ESTABLISHED_IN_ORIGINAL_1979_PDF）为同一 Mansell 豌豆酶学体系，未来处理前须独立 A6 先裁决同实验队列闭包风险；即便全部准入，其天花板为单闭包组/少量目标，低于不可降的 ≥6 targets/≥2 独立组硬门。C 轴补充核验：Pueraria PlUGT43 已在 C-E02 设计资格审查与 C-E02-R1 A4 抽取中实际检视（development-exposed；异黄酮 C 糖基化，越出 flavone-C6-C3H scope）；Brassica napus 无酶学论文命中；Köster & Barz 1981 实为异黄酮 7-O-糖基转移酶（EC 2.4.1.170 引文）。

3. **R74 预注册元数据轮（SS-E02；7/7 HTTP 200；全局 1272 HTTP / 1,244,444,031 B）**。Crossref 身份 + OpenAlex 合法OA解析 6 条最终线索：仅 SS-R74-L06（Saylor & Mansell 1977, ZNC 32c）存在合法OA副本，但其题名级酶类为 hydroxycinnamoyl:CoA 转移酶（槐三糖酰化步，非 UDP-葡萄糖糖基转移），不在 SS-E02 冻结 scope，未申请获取；**豌豆1982（L01）与其余 4 条老文献线索（L02–L05）均无合法 OA 副本**（OpenAlex is_oa=false / any_repository_has_fulltext=false）。继续处理唯一 fresh 候选需要绕过付费/访问控制，为合同 §6.3 条件4 与 §18.2 禁止项。本轮 metadata-only：无化学检视、无新曝光行、无新 MCTS。

4. **饱和评估（合同 §6.3）**。C 轴：已执行发现路线类型 ≥3（EuropePMC/Crossref/OpenAlex/Rhea/PubChem/引文追溯/PMC-OA 及本轮研究员路线）；连续完整轮对本家族零新增 structure_complete+runtime_executable+leakage_free+scope_applicable 闭包组（本轮 0 候选；此前完整处理轮各 0 准入）。直接型（Type II）黄酮 C-GT 文献按 ScCGT1（PMC9563126）综述仅四属——Gentiana triflora/Eutrema japonicum/Trollius chinensis/Pueraria lobata——全部已消费或越出冻结 scope。SS 轴：条件3 与条件4 均成立。**如实登记的未覆盖盲区**：专利文献从未作为发现路线执行；2010 年前未索引老文献（放射性标记时代）普遍缺乏完整结构/立体证据且多为付费墙，本截面不据此声称"全文献无合格来源"。

5. **治理与工程现状**。R74 前发现 SS fresh 门槛拒绝（SS_G5_SCOPE_BINDING_MISMATCH），根因为 R73 五原件 G5 登记行遗漏 scope 绑定字段（与 v17 R4 修复同类）；已按 v17 先例以追加式登记修正修复（原行逐字节保留，scope SHA c173c0e6… 未变，修复后 fresh 门槛实测放行）。R73 五源 G5 合同保持 active-but-stopped（4 个最终科学角色槽位 0 完成/4 待定），五源永久曝光不变。G7 writer 对全部后期曝光补充（manual 16 件、R73、本轮新增）的硬绑定仍是未来任何面板冻结前的必须关闭项。本轮新增核查：3,961 个受保护文件 0 漂移；全量本地回归 293/293 OK（operations/command-5663.log）；git diff --check 通过；无 Git commit/push/tag/release；未升格 human_reviewed、独立化学验证、formal_run_ready/release_ready。

6. **机器凭证**：`governance/R74-R75-source-loop-stop-review-v1/source_loop_stop_review.json`（饱和/访问边界评审与全部证据指针）、`SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1/`（precontract/query_plan/http_ledger/query_execution/final_lead_dispositions/raw_custody_summary）、`governance/SS_E02_R73_G5_scope_binding_repair_v1/`、快照 `report_snapshots/progress-v35-final.json`。修订前 REPORT/STATE 原字节归档于 `report_snapshots/progress-v35-inputs/prior_documents/`。
"""

NEW_STATE_PARA_PREFIX = "TASK-016-P7 当前状态 progress-v35-final（2026-10-12，本会话收口）：**Partial / agent_delegated**，非human_reviewed。"


def new_state_para():
    return (
        NEW_STATE_PARA_PREFIX +
        "来源循环按合同 §6.3 条件3/4 停止：C 轴本轮独立发现约40条线索 0 合格候选（直接型 Type II 黄酮 C-GT 文献仅 Gentiana/Eutrema/Trollius/Pueraria 四属，全部已消费或越界）；"
        "SS 轴唯一机械 fresh 候选为豌豆 Jourdan & Mansell 1982（R11 metadata-only 提示，从未化学检视），OpenAlex 证实无合法 OA 副本，继续需绕过付费墙为禁止项。"
        "R74 预注册元数据轮 7/7 HTTP（全局 1272 HTTP / 1,244,444,031 B；唯一有合法OA副本的老线索 L06 为酰基转移酶，越出冻结 scope）。"
        "C/SS G4/scope 原SHA不变，合格 fresh 仍 0/0、科学 A/B/E 0 cell、metrics=null；G7/G8/新bank G9 未形成，Roadmap P2 未关闭。"
        "C-E02/SS-E02 epoch 保持开放未注销（未来合法原件可依新 G5 批次在同一冻结 scope 下续作）；R73 五源 G5 合同保持 active-but-stopped、五源永久曝光；"
        "R73 G5 登记行 scope 绑定缺失已按 v17 先例追加式修复（原行保留）。专利文献与未索引老文献为如实登记的发现盲区，不声称全文献无合格来源。"
        "证据：[合同](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md)、[报告](docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md)、"
        "停止评审 `outputs/task016-p7/v1/governance/R74-R75-source-loop-stop-review-v1/source_loop_stop_review.json`、"
        "R74 批次 `outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R74-final-lead-metadata-v1/`、"
        "快照 `outputs/task016-p7/v1/report_snapshots/progress-v35-final.json`。"
        "3,961 受保护文件 0 漂移、全量 293/293 回归 OK（operations/command-5663.log）、git diff --check 通过；未 Git commit/push，未升格 human_reviewed/独立化学验证/formal/release。\n\n"
    )


def main():
    (ROOT / ARCH).mkdir(parents=True, exist_ok=True)
    rep_now = (ROOT / REPORT).read_text(encoding="utf-8")
    state_now = (ROOT / STATE).read_text(encoding="utf-8")
    updated_report = MARK in rep_now
    updated_state = STATE_MARK in state_now
    # 1) Archive pre-v35 bytes (idempotent; consistent with partial prior runs).
    for name, src, updated in (("REPORT-016-P7.pre-v35.md", REPORT, updated_report),
                               ("STATE.pre-v35.md", STATE, updated_state)):
        dst = ARCH / name
        if (ROOT / dst).exists():
            if not updated and sha(dst) != sha(src):
                raise RuntimeError("ARCHIVE_STALE_BUT_SOURCE_UNUPDATED")
        else:
            write(TASK, str(dst), (ROOT / src).read_text(encoding="utf-8"))
    write(TASK, str(ARCH / "archive_receipt.json"), json.dumps(dict(
        task=TASK, at=datetime.now(timezone.utc).isoformat(),
        archived=[{"path": str(ARCH / "REPORT-016-P7.pre-v35.md"), "sha256": sha(ARCH / "REPORT-016-P7.pre-v35.md")},
                  {"path": str(ARCH / "STATE.pre-v35.md"), "sha256": sha(ARCH / "STATE.pre-v35.md")}],
        note="byte-exact archives of the pre-v35 REPORT/STATE; history preserved"), ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    # 2) REPORT header + section.
    rep2 = rep_now
    if not updated_report:
        start_marker = "状态：In Progress（未完成）。当前权威截面"
        end_marker = "旧 REPORT/STATE 完整原字节已归档，不用历史预算覆盖最新预算。"
        if rep.count(start_marker) != 1 or rep.count(end_marker) != 1:
            raise RuntimeError("REPORT_HEADER_SPAN_AMBIGUOUS")
        i = rep.find(start_marker); j = rep.find(end_marker) + len(end_marker)
        rep2 = rep[:i] + NEW_HEADER + rep[j:]
        rep2 = rep2.rstrip("\n") + "\n" + SECTION
    write(TASK, str(REPORT), rep2)
    # 3) STATE tail block replacement.
    state2 = state_now
    if not updated_state:
        a = state_now.find("TASK-016-P7 当前状态 progress-v34-stopped")
        if a < 0:
            raise RuntimeError("STATE_SPAN_NOT_FOUND")
        state2 = state_now[:a] + new_state_para()
    write(TASK, str(STATE), state2)
    # 4) Snapshot.
    snap = dict(
        task=TASK, version="progress-v35-final",
        as_of=datetime.now(timezone.utc).isoformat(),
        status="Partial_source_loop_stopped_per_contract_6_3",
        approval_type="agent_delegated", human_reviewed=False,
        fresh_C=0, fresh_SS=0, scientific_ABE_cells=0, metrics=None,
        roadmap_P2_completed=False, G7_panel_real=False, G8_real=False, G9_new_bank=False,
        physical_HTTP=1272, physical_bytes=1244444031,
        epochs_open=True, gates_lowered=False, panel_floors_unchanged="C>=6/2, SS>=6/2",
        R74=dict(batch="SS-E02-R74-final-lead-metadata-v1", planned=7, executed=7,
                 legal_OA_leads=["SS-R74-L06"], access_blocked_leads=["SS-R74-L01", "SS-R74-L02", "SS-R74-L03", "SS-R74-L04", "SS-R74-L05"],
                 dispositions=pointer(R74 / "final_lead_dispositions.json"),
                 custody_summary=pointer(R74 / "raw_custody_summary.json")),
        saturation_review=pointer(STOP_REVIEW),
        r73_g5_binding_repair=pointer(REPAIR),
        discovery_evidence={
            "C": pointer(B / "discovery_evidence/session_20261012/C_axis_researcher_report.md"),
            "SS": pointer(B / "discovery_evidence/session_20261012/SS_axis_researcher_report.md"),
        },
        engineering=dict(
            regression="operations/command-5663.log", regression_tests=293, regression_ok=True,
            git_diff_check_ok=True, git_committed_or_pushed=False,
        ),
        protected=dict(count=3961, drift=0),
        known_blind_spots=["patent literature (route never executed)", "pre-2010 unindexed paywalled literature lacking complete structure/stereo evidence"],
        archive={"report": pointer(ARCH / "REPORT-016-P7.pre-v35.md"), "state": pointer(ARCH / "STATE.pre-v35.md")},
        inherited_prior_snapshot=pointer(SNAP / "progress-v34-stopped.json"),
    )
    p = SNAP / "progress-v35-final.json"
    if not (ROOT / p).exists():
        write(TASK, str(p), json.dumps(snap, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(report_sha=sha(REPORT), state_sha=sha(STATE), snapshot_sha=sha(p),
                          report_updated=True, state_updated=MARK or True), ensure_ascii=False))


if __name__ == "__main__":
    main()
