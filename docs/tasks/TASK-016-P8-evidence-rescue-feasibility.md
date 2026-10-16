# TASK-016-P8：P7 科学可达性诊断与下一 Epoch 决策

## 0. 合同元数据、修订授权与效力

- 任务 ID：**TASK-016-P8**；版本：**v0.2（取代 v0.1 Proposed 文本）**；修订日期：2026-10-12（Asia/Singapore）。
- 状态：**Proposed（仅授权修订合同，未批准科学或工程执行）**。
- 所有者在本会话明确提出：P7 文献已获得原 PDF，相关反应已经核查确实无效；不希望 P8 重跑相同审查，并明确指示“修改 p8”。本次按 **human_direct_task_revision** 登记，仅授权修改事前 TASK、索引和 STATE；**不得由此推定已批准执行 P8 或继续 P7**。
- 人工负责人：FlavoRetro 所有者；未来执行者：经明确批准的 P8 决策主控 + 可选独立核对员（第 7 节）。
- 工作区：`/home/ljx/FlavoRetro`；Git 参考 HEAD `993b22f` 仅是版本参考，实际 P1–P7 多项成果仍在未提交工作区。已有冻结科学资产按现有 SHA 继承，不在 P8 重建全项目 baseline。
- 前置科学合同：[TASK-016-P7](TASK-016-P7-domain-aligned-transfer-closure.md) v0.1；主要事实入口为 [P7 主报告](../reports/REPORT-016-P7-domain-aligned-transfer-closure.md)、[C-E03 预检](../reports/REPORT-016-P7-C-E03-preflight-20261012.md)、[SS/R80 预检](../reports/REPORT-016-P7-SS-R80-recovery-preflight-20261012.md)、[R81–R87](../reports/REPORT-016-P7-continuation-R81-R87-20261012.md)、`STATE.md` 及两个 Roadmap。
- v0.1 原 TASK SHA：`a61c054131b3e1ac4b8d65b7aa578d2b0220b1b647d614d91e48173e63833182`；修订时保留原字节备份及操作记录。文件名 `TASK-016-P8-evidence-rescue-feasibility.md` 保持不变，避免破坏已建立的文档链接；标题和执行范围以本 v0.2 为准。
- 拟在批准执行后产生报告 `docs/reports/REPORT-016-P8-evidence-rescue-feasibility.md`，如需少量机器决策表仅保存 `outputs/task016-p8/v2/`，绝不存原 PDF 或复制 P7 原件。

### 0.1 本次修订的根本改变

**取消 v0.1 的“重建 P1–P7 全量数据库、逐篇审 PDF、重新执行 A3/A4/A5/A6、最多六个端到端资格 pilot、建立统一证据机器流水线”的要求。**

原 PDF 已经核实不满足相应 scope 的反应，P8 必须**直接继承该反应层负结论**，而非把它重新变成待办事项。它的任务是回答：在既有负结论与冻结科学标准下，继续当前 P7 epoch 是否可行？下一步应该有限补证、合法完成已有阶段、宣告 epoch incomplete，还是经新批准设计新的 epoch？

## 1. 事实基础和不可推翻的界限

### 1.1 已有 P7 证据应直接采纳

| 已有事实 | 对 P8 的含义 |
| --- | --- |
| C/SS 合格 fresh 均为 **0**；正式新科学 A/B/E **0 cell**；指标 `null` | 不把历史测试或工程 pass 当作 P7 成功 |
| P7 累计 1,309 次 HTTP / 1,245,786,610 字节 | 不再以 HTTP、PDF、脚本数量当作科学进展 |
| 所有者已经核查相关原 PDF，认为对应反应不符合要求 | **P8 不重新打开、解析、逐篇重审这些 PDF**；在结论表按 `owner_confirmed_exclusion` 标识其所有者确认层级 |
| P7 已记录的 16 个历史/人工来源限定审查：14 条已定位反应不符合冻结 scope、2 条证据待定 | **14 条不重新申请反应资格**；2 条不得擅自变成“已被证明无效”，除非有对应的既存最终裁定或所有者具名确认 |
| 已有 17 source / 36 row 资格清单只包含当时已定位的范围，仍有未评估部分 | 不凭此推断整篇论文的所有反应已穷尽；也不因未评估而自动打开原件 |
| C-E03 C8 工程 G4 冻结，但独立设计双结构前置尚未通过；R87 三 prospective hints 的 prior/closure 未清 | 不开始新的 C-E03 化学首读，也不补造旧前置 |
| SS/R80 旧读取记录存在，但角色终结与 prior 仍有 unknown；237/237 是恢复 metadata 验证 | 不把准备代码/registration 当成完成的科学读取；只列出单项决策所需未闭门 |
| Trapero2012 与 Liu2021 作为设计语料曾暴露；R73/Liu2021 受限内容已停止 | 不能将设计材料重新标 fresh，不能更换 reader 绕开停止 |
| TASK-016 主任务 O 与 P1 的已完成开发成果、P6 范围工程与旧回归 | 按原报告保留，不因 P7 fresh=0 而撤销，亦不冒充 TASK-017 正式盲测 |

**证据层级必须分开**：`existing_report_verified`（P7 报告有直接裁定）；`owner_confirmed_exclusion`（本次所有者确认）；`historical_design_exposed`；`not_yet_assessed`；`unresolved_from_existing_records`。所有者陈述不是伪造的逐篇 A11 原始 terminal，报告与确认不一致则**记录差异而不是偷偷重审或强制改写**。

### 1.2 对“无效”的正确粒度

- **具体反应无效**：已经确定是不同底物、C6/C8 错配、2-hydroxyflavanone→脱水、苷元 O 而非糖间 O2、缺酶催化证据，或属于历史暴露；在相应冻结 scope 下作为本次排除，**不再触发 A4/A5/A6**。
- **论文其他反应尚未核查**：与“已确认这篇论文没有任何可能相关反应”不是同一命题；P8 只继承现有明确范围，不主动创建新的全文排查项目。
- **证据不足或 unknown**：如某个反应确实还缺位点/立体/prior 终结，按既有状态记录 `deferred`；P8 不利用重复阅读去“清零 unknown”。
- **候选科学上可能正确但不 fresh**：仍可为设计/boundary 资产，不得再计入当前或后续已受污染 holdout。
- **技术闸门异常**：如果既存记录显示某个具体候选受治理 bug 而错拒，P8 只判断是否**足以影响下一步决策**，不默认开展程序修复。

## 2. P8 的唯一目标与非目标

**目标**：在不新增 PDF 审查的前提下，基于 P7 已完成核查与冻结验收条件，为 **C 和 SS 两轴分别**输出可复算的已知缺口、当前库存可达性判断、最少新增信息需求和可批准的下一 epoch 决策。

P8 必须最终回答：

1. 现在已知的合格 fresh/独立 closure groups 数，与 P7 原门槛 **C ≥6/≥2、SS ≥6/≥2** 分别差多少？哪部分确实不适用，哪部分只是尚未证明？
2. 已核无效的 PDF/反应为什么不能通过增加审计或更换 Agent 变成 fresh？
3. 有没有**具名且没有已确认不可逆排除原因**的候选，可在不降低科学规则下以一次有限补证继续推进？如果没有，要如实写“现有资料中没有已证实可执行补证路径”。
4. 当前各 C-E02、C-E03、SS-E02（及其他已证存在的冻结 scope/epoch）应 **继续当前 epoch、暂停待补证、按 P7 宣告 incomplete，还是保持 Blocked 并由所有者处理**？
5. 如果需要新的 epoch，如何保证先用有资格的 **design** corpus 建 scope、真实冻结 G4，再开 fresh G5、保持来源/assay/build 和后验模型隔离，避免再损失整批候选？
6. 具体交给 P7 主控的**下一项有限、可批准的行动**是什么；若无法保证终验，必须承认不能保证，而不是无限迭代。

P8 **Completed** 可以是明确的负面科学可达性结论；不以 fresh 从0变1为自身验收。P8 完成 **不等于** P7、Roadmap P2 development effect 或 TASK-017 完成。

### 2.1 明确取消的内容

- 不重新下载、打开、解析、抽取、翻译或双审已经判无效的 PDF/SI。
- 不清查所有 P1–P7 原始账本，不重建全量 source/reaction/target/exposure canonical 数据库。
- 不重新跑 A3/A4/A5/A6、R80 恢复、C-E03 首读、G7/G8 或真实 A/B/E。
- 不新建 C/SS scope、不执行 PUCT/MCTS、模型、库存或模板修改。
- 不为每篇论文、每个缺口增加新脚本、角色、快照、fixture 或通用治理 harness。
- 不要求在 P8 内完成“找到 6 个 fresh”或试探性地消耗潜在新样本。

## 3. P7 原科学标准不得更改

本 TASK **完全沿用** P7 原 v0.1 的 scope-first、epoch、G4→G5→A4/A5→A6→G6/G7/G8/G9/G10 先后门、双独立结构、source/assay/exact/design closure 零泄漏、complete reference precursors、真实静态 scope-applicability 与不存在 exact replay 的条件。

P7 最终仍必须 C/SS 分别具有 **≥6 个 fresh runtime-complete targets、≥2 independent closure groups**；正式 A/B/E 0/1/2 seeds；`G>=3`、`G/N_gap>=50%`（分母为0则 `null`）、≥2 successful groups、双基线净覆盖正值、reference loss=0、≥3 targets/2 groups 的真实三 seed node creation，以及 legacy regression/package/保护验证。**P8 任何建议不得以修改上述硬门为代价。**

两项额外原则：

1. 同一 epoch 合法 G4/G5 后受控科学读取的 evaluation 来源不因“现在已读”自动被排除，但历史 design/build、越序首读、同源 assay 或失败 epoch 的 holdout 不能通过重新登记“漂白”为 fresh。
2. 名称级和 metadata-only 线索既不是结构级泄漏证明，也不是无泄漏证明；`unknown` 不改写为 false/zero。纠正统计假象只有在影响当前决策时才列为必要修复。

## 4. 执行流程：四个有明确产物的决策阶段

### D0 — 接纳既存审查与限定输入（不重审文献）

**输入**：STATE 当前 P7 截面、P7 原 TASK `3/`7–`18`、P7 主报告、C-E03 / SS-R80 preflight、R81–R87、既有逐反应资格清单与已冻结 scope 摘要；所有者确认“原 PDF 已审且相关反应无效”。

主控只以**已有报告、结构化结论与现有 SHA/记录引用**建立 `reviewed_disposition_index.md`（或≤1张小型表）。每一行最少：family、epoch、scope、具名来源/claim（确实有则列）、历史判定、证据指针、所有者确认范围、是否不可逆排除、是否仍 pending、对当前 6/2 分母是否可计、剩余待决议的问题。

**不**重新枚举 P1–P7 全库，不打开 PDF，也不把 owner-confirmed 说成独立 A11 复核。无法定位的所有者确认项标“确认但未能绑定具体 claim”，不能据此给全库计数。

**D0 完成门**：C-E02/C-E03/SS-E02 与具名 R80/Trapero 类别都有“已排除/设计/待证/未评估”明确边界；对不存在的证据不发明细节。

### D1 — 冻结 scope × 家族的差额与可达性（只算已有资料）

按 `family × frozen_epoch × frozen_scope` 生成一个小型 `feasibility_matrix.md`：

| 必填字段 | 算法/口径 |
| --- | --- |
| `confirmed_P7_fresh_targets` | 已经由 P7 原合法科学门验收的数量；P8 草稿候选不能计入 |
| `confirmed_independent_groups` | P7 已验的独立 assay/source closure groups |
| `target_deficit / group_deficit` | `max(0, 6 - confirmed_targets)` 与 `max(0, 2 - confirmed_groups)`；按每轴总量门判定时**对互相独立且允许合并的 scope bank**去重，不把同 target 多 scope 重计 |
| `confirmed_ineligible` | 已明确不符 scope、设计曝光、许可/安全停止、不可逆泄漏的具名反应集合；不再审 |
| `specific_unresolved` | 仅列对下一决策有实际影响的未决事项及其既有证据 |
| `conditional_evaluable` | 有具名来源、具体待补证字段、合法取得路径且未确认不可逆排除的候选；**条件集合不是已验证 fresh** |
| `no_route_proven` | 当前固定库存无证据支持达到6/2；绝不是声称全世界无相应论文 |
| `next_go_no_go` | 有证据的一步行动 / 当前 epoch incomplete 建议 / 等待所有者批准 |

保守下界只能按已核证科学资格计；“可达到的上界”只有具名、现实可补的候选才能列**条件性**上界，无法界定则标 `unknown` 而非杜撰数字。独立来源/组存在 unknown edge 时应给条件区间，不把不同 DOI 自动算独立组。

**D1 完成门**：C/SS 两轴都有数值差额（若 P7 仍为 0/0，则各缺 6 targets/2 groups）、各 scope 及 epoch 的阻断原因和可以/不能推导的可达性结论；没有新的 source/claim 读取。

### D2 — 科学决策：继续、有限补证、结束当前 epoch 或新设计

对 **C 和 SS 独立**按下列优先级决策，不强迫同步：

1. **CONTINUE_EXISTING_EPOCH**：只有现有阶段时序、冻结 scope、未污染且具名候选的必要条件存在**可靠证据**，并且下一步是 P7 原阶段机允许且有价值的动作；P8 只输出建议，不能代替 P7 放行。
2. **ONE_BOUNDED_EVIDENCE_ACTION**：仅存在一项真正可能改变结论的待证字段；给出唯一 claim/source、所缺结构/来源/角色字段、证据可取得性、一次性具体行动、独立核验与失败停止门。**不在 P8 执行补证**。
3. **RECOMMEND_EPOCH_INCOMPLETE**：当前 scope 已由已核无效来源和独立性/适用性缺口证明无法使用现有有界库存形成足够面板，或触发 P7 `18 的真实停止条件；建议 P7 依原合同正式处理此 epoch、追加曝光，且下一 epoch 不复用旧 holdout。P8 自身**不注销或改写 P7 epoch**。
4. **BLOCKED / OWNER_DECISION**：关键安全限制、访问权或先后门事实无法证明；停止相关路径，不凭想象绕过，也不把科学不确定当已经否定整个领域。

如果考虑 **NEW_EPOCH_REQUEST**，另附一页具名新方案，至少说明：可被合法验证的 design support 可能来自哪里、当前哪些来源绝对不可作为 fresh、未来 fresh holdout 从何种**尚未化学阅读的独立来源群**采集、怎样在 G4 前控制评估信息暴露、两轴分离和来源闭包如何检查，以及在 ≥6/≥2 面板落空时如何按 P7 停止。不能声称这个设计必定成功；没有潜在独立群的证据，则只提出“需先进行另获批准的有限 metadata-only 可行性勘察”，不得提前科学阅读候选。

**D2 完成门**：每轴一个主决策 + 最多两个备选；每个决策须有 evidence pointer、当前不可用原因、下一唯一动作、预算/审批范围、成功条件及失败停止条件。

### D3 — 独立审查、交接与结案

由与 D0–D2 提案不同的只读核对员（可以是独立 subagent 或独立简单算术/指针核对过程）核查：
- P7 旧负面反应没有被重新判 fresh，没有把 owner confirmation 冒充 A11；
- 6/2 差额、source/assay group 去重和建议中的必要信息真实来源可追；
- 没有要求同一已否定 PDF 重审，没有复活停止处理的来源；
- 继续/new epoch 的建议不泄漏已见 holdout，不后验调整科学门；
- 没有对 P7 或 Roadmap 的完成状态偷换概念；
- `git diff --check`，仅报告已有 SHA/文件原文且 P8 未碰已冻结科学资产。

交付：`P7_DECISION_HANDOFF.md`（C/SS 分轴一页结论与行动）、`P8_DECISION_AUDIT.md`（分母/指针/禁令），以及事实性的 `docs/reports/REPORT-016-P8-evidence-rescue-feasibility.md`；最后更新 STATE 和任务索引的**真实** P8 状态（Completed / Partial / Blocked）。是否实际恢复 P7、建立新 epoch 仍需独立批准。

**D3 完成门**：所有否定、未决与推荐动作可核验，独立审查无科学规则违背；否则 P8 只能 Partial/Blocked。

## 5. 交接给 P7 的行动合同（必须可执行）

每项 `P7_DECISION_HANDOFF` 最少包含：`family`、`current_epoch`、`frozen_scope_id`、`existing_evidence_pointer`、`decision`、`why_not_existing_fresh`、`single_next_action`、`required_new_information`、`required_approval`、`stop_if`、`impact_on_existing_exposure`、`can_touch_P7_G5/G6/G7`（默认 false）和 `status_of_O_P1_P6_assets`。可以用紧凑 Markdown 表，不强制 JSON/专用脚本。

优先排序：**现有具名、合法、未被确认无效且只欠一个关键判据的路径** → 当前 epoch 有条件可继续 → 当前 epoch incomplete 的正式裁定申请 → 有限新 epoch 设计/metadata-only 可行性合同。严禁“持续搜索直到找到 6 个”这种无终点行动。

若判断某当前 scope **无已证明的现实补证路径**，应直接建议按 P7 合同发出 epoch 停止/缺口报告；不能仅为了维持 In Progress 而制造恢复流程。

## 6. 最小预算与反空转规则

- **外部 HTTP=0；下载 PDF/SI=0；新增科学原文读取=0；A4/A5/A6 重跑=0；新 MCTS=0**。
- **全量 ledger 重建=0；大规模代码改造=0；正式 P7 epoch 写入=0**。
- 最多 **2 个执行角色**（决策主控和独立核对员；若无法提供独立核对则明示限制）；无需召集原 P7 全部 A0–A12。
- 主要输入锁定为第 0 节已列的已有报告/资格表/明确的个别 stage 记录；**至多一轮主分析 + 一轮有新事实的差异修正**。
- 最多处理 **4 项具名的决策关键争议**，而非重核整篇论文；每项都必须先书面证明改变与不改变 P7 选择的条件。若无这样的争议，直接 D2 决策。
- 无需新代码；仅当简单读取/汇总无法复算 6/2 差额时，才允许增加 **至多 1 个短小只读脚本**，不能将其扩展为新 harness。
- 目标为 **≤40 个通过 `scripts/operate.py` 记录的本地命令**（包含必要验证）；达到预算、或连续两次分析没有改变决策依据时停止并报告 Partial/Blocked，而不是继续增加脚本。
- 不允许无授权 Git commit/push、不修改 P7 保护件、不把受限数据/原件放入 Git 或报告；每项写入与执行按 `AGENTS.md` 经 `scripts/operate.py` 审计。

## 7. 角色与审批

- **P8-D 决策主控**：只消费已经形成的报告/判定/索引，生成 D0–D2 差额与决策；禁止直接进行新化学读取或修改 P7 stage。
- **P8-V 独立决策复核**：只核来源指针、计数、决策逻辑、科学门与权限；禁止自己填补不存在的化学证据。允许用真正的独立 subagent，但必须提供输入来源和有界任务说明；双重文字总结不是独立化学确认。

批准应区分两层：
1. 所有者明确批准 **执行本 P8 v0.2** → **仅批准 D0–D3 的上述只读决策工作**。
2. 依据 P8 交接继续 P7、补看原文、运行模型、更改 scope、开启新 epoch 或新文献搜索 → **另需具名、限定的 P7/新 TASK 批准**；P8 不包含这些操作。

## 8. 验收标准

- [ ] 已直接接受已确认无效的原 PDF/反应结论，未再次执行全文审查；既有 14 rejected 与 2 deferred 的证据边界未抹去。
- [ ] C/SS 分轴及各既有冻结 scope 的既知 fresh/closure、到 ≥6/≥2 的差额与当前有效条件集合清晰，没有把条件性可能计为已准入。
- [ ] C-E02、C-E03、SS-E02 和 SS/R80 的分支去留都有明确科学/时序原因与 evidence pointer；没有重做 A4/A5/A6。
- [ ] 每轴主决策属于 CONTINUE / ONE_BOUNDED_EVIDENCE_ACTION / EPOCH_INCOMPLETE / BLOCKED 之一；若提议新 epoch，严格保持 scope-first、无旧 holdout 泄漏且标明无法保证来源充足。
- [ ] 每个下一行动有责任角色、唯一所需信息、预算/授权、完成或停止条件；不存在开放式无穷 source loop。
- [ ] 独立核对 P7 科学门、owner/P7 证据分层、局部反应 vs 全篇文献结论和保护要求。
- [ ] 执行预算与零新增读/HTTP/MCTS/全库清账限制满足，`git diff --check` 通过。
- [ ] `P7_DECISION_HANDOFF.md`、事实性的 `REPORT-016-P8-evidence-rescue-feasibility.md` 与当前 STATE 一致；P8 结案不冒充 P7/TASK-016 development / TASK-017 已关闭。

**P8 Completed 的充分条件是给出可靠的科学可达性判断及可批准的下一步，即使最终 fresh 仍为0。** 任一关键条件未完成，按项目规则标 Partial/Blocked 并如实报告。

## 9. 停止条件与范围外处置

遇到以下任一情况立即停止相应支线：要求重新读取已审无效 PDF；需要把旧曝光来源变成新 fresh；试图更改 P7 冻结 scope/实验门；需要绕过来源访问或安全停止；无证据却要求产出“>=6 已满足”；决定依赖目前无法获得的全新化学细节；存在无法判断的必要 source/assay group 关系且本次限域材料不能解决；达到本任务预算或开始重复空转。

**不能完成 P7 不代表 P8 失败。** P8 需要清楚区分：`existing_frozen_scope_not_demonstrably_feasible`（现有库存不足以证明可达）、`scientifically_falsified_specific_claim`（具体反应不符）、`unknown_global_source_availability`（不能据此证明全球来源不存在）。不得使用笼统“所有相关论文不存在”作结。

### 执行闭环

按 `PROJECT.md → STATE.md → ARCHITECTURE.md → P7 TASK / 当前事实 REPORT → P8 v0.2` 阅读。批准后执行 D0–D3 → 独立复核 → REPORT → STATE。**P7 和 TASK-016 其余开发实验是否重启由所有者根据此决策包另行批准，不由 P8 自动触发。**
