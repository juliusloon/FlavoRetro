# ADR-001：独立根、三线职责、批准与证据分轴

- 状态：accepted
- 日期：2026-09-21
- 负责人：Cano（agent_delegated）

## 背景

本项目（FlavoRetro）是旧项目 `/home/ljx/retro_synthesis` 的重建。为使未接触过旧项目的读者可以独立理解本决定，旧项目事实内联如下。来源：旧库 2026-09-20 复盘（快照已复制到 `data/raw/legacy/docs/reports/260920-pre_refactor_project_retrospective.md`）与本仓库 TASK-001 的基线记录。

旧库规模与最终状态：

- 旧库约 5.6 GB（`docs/tasks/TASK-001-governance.md` 记录）；TASK-001 为其建立 SHA-256 基线 `operations/history-before.json`，覆盖 33,146 条路径（`docs/reports/REPORT-001-governance.md`）；复盘静态盘点 `src/ + scripts/ + tests/` 共 131 个 Python 文件。
- 旧库最终自定状态为 `rebuild-foundation / candidate-not-production`：production 模板 0 条晋级、库存 0 条晋级；30 靶标 × 3 seeds × 4 臂 = 360 cell 四臂盲测的合同 runner 已就绪，但正式结果未执行、预注册未批准。

复盘的核心结论：候选、工程通过、化学证据三类事实被反复混淆——parser-ready ≠ runtime-active ≠ chemistry-reviewed；solved 多 ≠ 化学有效；标题命中 ≠ 原文确认；测试全绿 ≠ 研究完成。实证包括：

- 旧 13 靶标 benchmark solved 9/13，而 evidence-closed 0/13。
- 1,053 cell 参数敏感性（13 targets × 3 seeds × 27 configurations）中，reward 优先候选 solved 30/39，而 actionable 0/39。
- virtual 桥与供体沙箱闭合曾被误当可信。
- 多条工作线共享命名，同一名字既指候选又指运行资产，候选被误当生产。

用户硬约束（`PROJECT.md`）：历史 retro_synthesis 完整只读，只复制不移动；原始字节不可变；候选不升格为独立证据；工程批准不冒充人工、实验或供应商确认。本次重建的批准由所有者授权 agent 代行，记为 agent_delegated，不等待人工回复；授权只覆盖本次重建。

## 决定

1. 独立根、只复制不移动。在 `/home/ljx/FlavoRetro` 新根从最小 API 重新实现；需要的旧材料以字节复制进 `data/raw/` 并在 `metadata/sources.json`、`metadata/sources-v1.json` 登记来源，不链接、不挂载回可写历史目录；旧库保持只读，完整性以 `operations/history-before.json` 基线核对。
2. 三线职责、各自独立事实源。化学资源（来源/身份/审核）、搜索产品（共享服务与真实 MCTS）、研究评估（冻结定义/逐次运行/限域结论）三条工作线分离；模板、库存、运行、文献各有独立身份与状态，互不借用对方的状态措辞。
3. 批准与证据分轴。工程审批由 agent 按本次授权完成并记为 agent_delegated，禁止伪装 human_reviewed；化学事实按可核验证据处置，证据不足即记 unresolved，不伪造审核人；任何化学晋级需人工批准加独立证据，agent 不得代行。
4. 交付定义。本次交付定义为运行的研究候选系统；`metadata/release.json` 记 `status=research_candidate`、`decision=retain_candidate_do_not_certify_production`、`decision_authority=agent_delegated`。独立科学有效性按事实报告，不作为必须虚构的完成条件。

## 备选方案

- 原地重构旧库：违反用户硬约束（历史目录完整只读）；且旧命名负担留在原地，无法给出干净的重建起点与准入边界。不采用。
- 整体复制旧仓库再删改：会把隐式依赖（绝对路径、运行时相互引用）与旧结论口径（solved/actionable 混淆的记录）一并带入，违背"从最小 API 重新实现"的要求。不采用。
- 逐文件原地重构：同样触碰只读约束；且逐文件替换会使"新结论 / 旧继承"的边界随时间模糊，事后无法回答某条结论来自哪一次重建，不满足可追溯要求。不采用。

## 影响与风险

- 双库并存的核对成本：任何"旧项目曾做过 X"的表述都要回到旧库或其快照核对。缓解手段：复盘快照已复制到 `data/raw/legacy/`，基线哈希在 `operations/history-before.json`。
- 全部结论需重建证据：旧库的运行成绩（solved 数、计时）不被继承，新系统从 0 production 起步；短期内可展示能力低于旧库表观数字，这是本决定的设计结果而非回归。
- 基线依赖本机：`history-before.json` 记录的是本机旧库 33,146 条路径的哈希；旧库若被迁移、扩容或更换机器，核对方法需重建（核对脚本已归档为 `operations/archive/history_guard-task-001.py`，用法见其文件头，需 before/after 两次快照对比）。
- 授权范围风险：本次 agent_delegated 授权只覆盖本次重建，后续会话恢复明确 TASK 批准流；把本次授权误当长期授权属治理风险。

## 复审条件

- 旧库 `/home/ljx/retro_synthesis` 被归档、迁移或下线时——核对基线与已复制材料的地位需重估。
- 证据晋级流程变更时——例如首批 production 记录经人工批准，或 `metadata/release.json` 任一维度离开当前未决状态。
- 所有者更换治理授权时——agent_delegated 的适用范围或批准流发生变化即触发复审。

文档形态：TASK-009 由速记体扩写，决定内容未变。
