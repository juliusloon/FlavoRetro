# TASK-016-P8：P7 存量证据救援、资格流水线纠偏与双轴可达性审计

## 0. 合同元数据与授权

- 任务 ID：**TASK-016-P8**；版本：**v0.1 / Proposed**；起草日期：2026-10-12（Asia/Singapore）。
- **创建授权**：所有者在本会话要求创建详细、可划分、可通过 subagents 执行的 P8；授权仅覆盖本合同起草、落盘、索引及 STATE 登记，记作 **human_direct_task_drafting**。**不推定已批准实际运行 P8 科学读取、P7 恢复、代码修复或 MCTS**。执行前必须另获明确批准，记录真实主体，不能冒充 human_reviewed。
- 人工负责人：FlavoRetro 所有者；未来执行主控：批准后的 P8-O；具体角色见第 7 节。
- 工作区：`/home/ljx/FlavoRetro`；Git HEAD 参考 `993b22f`，但 P1–P7 大量未提交内容必须在 G0 以**实际 SHA 文件清单**冻结，HEAD 不是全部事实。
- 前置科学合同：[TASK-016-P7](TASK-016-P7-domain-aligned-transfer-closure.md) v0.1，其成功硬门全部保持；上游 [TASK-016](TASK-016-open-glycoside-expansion.md) 与 P1–P6 的历史结果不回写。
- 输入报告：[P7 主报告](../reports/REPORT-016-P7-domain-aligned-transfer-closure.md)、[C-E03 预检](../reports/REPORT-016-P7-C-E03-preflight-20261012.md)、[SS/R80 恢复预检](../reports/REPORT-016-P7-SS-R80-recovery-preflight-20261012.md)、[R81–R87](../reports/REPORT-016-P7-continuation-R81-R87-20261012.md)、STATE.md、docs/WORKBENCH_ROADMAP.md。
- 计划输出：`outputs/task016-p8/v1/`（本地、禁止加入 Git）；计划结案报告：`docs/reports/REPORT-016-P8-evidence-rescue-feasibility.md`（执行后按实生成）。
- 起草时 **P8=Proposed / P7=In Progress**；P8 不自动暂停或完成 P7。建议 P8 获批后由所有者授权 P7 临时停止**新来源扩张**并保留原冻结科学任务。

## 1. 问题定义：为什么大量文献没有变成 fresh

### 1.1 起点事实（2026-10-12；不是 P8 的实验结果）

| 指标或对象 | 截面事实与界限 |
| --- | --- |
| C / SS 合格 fresh | **0 / 0**；正式科学 A/B/E **0 cell**，迁移指标 **null** |
| P7 物理账 | **1,309 HTTP / 1,245,786,610 bytes**；HTTP 不等于独立论文或反应 |
| C-E03 | C8 scope/G4 工程已冻结，SHA `bb4b508432bc622b57056371ffe18a1d7136a12aa1f799b740599e0d8eb7654f`；但 R83 双 reader 是文本 harvest，非双完整图；A11 228 pass / 9 fail / 2 pending；三份 prospect A6 全 pending，首个 fresh 科学读取被锁 |
| SS/R80 | 早期原件打开存在证据，但 A4/A5/A6 终结 role 缺失，prior unknown=2；v2 恢复 metadata 检查 237/237 仅验证适配器，不证明科学资格 |
| 已暴露设计文献 | Trapero 2012 的 HMBC 可作 SS 糖链结构设计证据，但不可追认为 fresh；Liu 2021 为 C8 design，不是 fresh |
| 停止内容 | R73 五源及 Liu2021 后续内容处理遭拒/停止，不能换角色、换 reader 规避 |
| 旧工程测试 | 293/293 是历史回归，214 行旧 MCTS 账不等于新的 P7 迁移矩阵 |

G0 必须再次核对真实文件、版本、原 SHA、修改时点。发现后续进展应保留新旧截面，不回写旧事实。

### 1.2 待检验的四类故障（不得预判全部已证实）

1. **科学域/样本密度不足**：冻结 C6、C8、SS O2 scope 对应的一步反应、明确糖位点/立体、reference precursor 和独立 groups 本来就少；论文相关不等于反应适用。
2. **资格假阴性与三值逻辑错误**：metadata/名称级 exposure 被误当图级泄漏；unknown 误作 false 或 0；多版 exposure ledger 相同行重复计为独立事实；source/cohort 闭包错误。
3. **流程交接断裂**：A4/A5 仅文本无结构；role/round terminal 缺失；先读后登记；前置门缺口在 G4 后发现；reconciliation 被错误当作独立抽取；恢复适配器未产生科学终结。
4. **管理与工程空转**：版本、脚本、fixture、审计和快照不断扩大，但候选无有效状态变化。新任务必须以科学不确定性实际消减计量，不用 HTTP、测试数和新文件数冒充进展。

“Agent 上下文一定不足”只是假设，除非有具名故障和证据链，不能写成已证实根因。

## 2. 任务唯一目标与完成边界

**P8 成功 = 建立存量可信事实源，定位具体阻塞或假阴性，验证一条有限、可复核的准入链路，并把 P7 下一步所需的最小行动与可达性界限交付；不保证凭空找到 fresh。**

最终必须能明确回答：

1. 存量 P1–P7 来源、文章版本、证据事件、反应和 target 的**全部已发现数据**如何唯一映射？哪些仅 metadata，哪些被抽取、哪些从未处理？
2. C 和 SS 各被 source / structure / exposure / scope / runtime / role / access / policy 中哪一项阻断，逐条给出可复核原始指针与状态？
3. 哪些可能被治理逻辑错误拒绝，哪些是真正违反科学合同，哪些仍不可判断？
4. 是否存在一个对象能依合同完成 A3→独立 A4/A5→A6→G6→G8 静态闭环？若不能，其第一个不可越门是什么？
5. 每个已冻结 scope 已证合格的候选下界、**仅有条件的潜在上界**及独立 closure groups，是否存在达到每轴 >=6 / >=2 的现实补证路径？
6. 对 P7 是建议继续当前 epoch、限量补证、epoch incomplete 后另开批准、还是必须 Blocked？每条动作指向哪个证据和哪个合同门？
7. TASK-016 已完成的 O/P1 工程/真实 MCTS 开发成果、C/SS 尚未证明的领域泛化及 TASK-017 正式盲测边界如何保持？

**P8 可以 fresh 仍为 0/0 而 Completed**，前提是上述均形成有证据的裁定与可执行 handoff；P8 Completed 绝不表示 P7 / Roadmap P2 / TASK-017 Completed。

## 3. 绝对禁止降低的科学和操作约束

- P7 `3、`7–`18 的 scope-before-fresh、双独立**分子结构**提取、source/assay/reaction/design closure 零泄漏、runtime complete、static scope applicability、C/SS 各 >=6 个目标 / >=2 独立组，以及 G>=3、G/N_gap>=50%（N_gap=0 为 null）、至少2成功组、双基线正向覆盖、reference loss=0、seed0/1/2 真实 MCTS node transfer、legacy 17×3 等**原封不动**。
- P8 不改模型、PUCT、scoring、stock17、已有 P7 scope guard/G4 SHA、runtime 真实路径、review binding、历史报告及已冻结 P7 阶段；**不执行 MCTS**。
- 同一个 epoch 中，合法在 G4/G5 后受控首读的 evaluation 来源**不因现已阅读而自动失去本 epoch 身份**；但先于必要 G5 的科学设计曝光、build 支持、同源 assay 闭包及前失败 epoch 的 holdout，不能被漂白为新 epoch fresh。
- metadata-only / 名称级 token 不是自动完整反应泄漏，也不是自动无泄漏。`unknown` 不得变成 0 / false，null 不得当 success/failure；所有时间证据来自真实既存日志，**不得倒签 G5**。
- 复杂结构不靠名称、记忆、人工猜 SMILES 升格；权威结构 ID 仍需要原件身份与连接位点证据。两个 reader 同意文字叙述**不等于**两套完整图独立一致。
- 安全拒绝/停止的内容不得改 prompt、换 reader、换 subagent 重试；不得绕过登录/付费/验证码。原始/受限物不进 Git、wheel/sdist 或公开报告。
- 所有 P8 的 candidate eligibility 仅为 `recommended_P7_action`；正式 P7 G5/G6/G7 只由原状态机、原授权、独立验证放行，P8 不给自己签发权限。
- P8 不撤销 TASK-016/P1 已完成 O/历史开发能力；不把 P7 development claim 升格 TASK-017 formal blind、human_reviewed、独立化学/湿实验、evidence_closed、actionable 或 release。

## 4. 变更范围

| 对象 | 允许 | 禁止 |
| --- | --- | --- |
| 新 P8 TASK / docs/tasks/README / STATE | 事前合同、索引、Proposed 状态 | 改写 P7 科学阈值或历史结果 |
| `outputs/task016-p8/v1/` | 离线索引、候选总账、负门试验、差异审计、handoff manifest | 存放未获授权的正文副本、伪 firstread |
| `scripts/task016_p8_*.py`、`tests/test_task016_p8*.py` | 有确凿重复性需求时最多少量小脚本 | 每论文、每失败新造 harness / 修改 MCTS |
| P7 `outputs/task016-p7`、`data/raw/task016-p7`、历史全来源 | **只读、按 SHA 关联** | 原地修改/重新签署/清理失败、将源新拷贝冒充 fresh |
| P7 代码、冻结 scope、阶段、runner | 默认只读；输出单独 patch proposal | 未获 P7 专项授权合入补丁或继续受阻科学读 |
| 路线图/ARCHITECTURE/core runtime | 仅读，最终报告可提出变更 | P8 任务创建时改变科研结论 |

批准 P8 的离线 G0–G3 **不自动批准**后续任何新的科学原文打开、P7 同批恢复调用或 P7 程序改造；这些必须有具体源、角色、epoch 和失败回退的补充授权。


## 5. 清账对象、机器 schema、三值判定（G1/G2 的实际实现合同）

### 5.1 三层身份，严禁跨层错误去重

**Source work**：规范化 DOI、PMCID、PMID、正式题名、出版年、别名；冲突标 `unresolved_identity`，不能简单因题名相似合并。
**Source version / object**：正文/PDF/JATS/SI/表格/原件 SHA、作者/出版版本关系；同篇不同格式不是独立来源，HTTP response 和文件数不是论文数。
**Scientific reaction / assay claim**：acceptor、donor、product、真实一步成键 atom/site/stereo/sugar、enzyme/context、source assay/cohort、reference precursors；结构未完整时给 `provisional_claim_id`，不虚构 reaction graph ID。
**Evaluation target**：P7 epoch_id + scope_id + product graph + reference precursor set；biological endpoint 名称不是完整反应图。
**Closure group**：由 A6 以 shared article / source assay / same cohort / chemically shared design / exact reaction 等证据连通分量算出，不能因为 DOI 不同就默许独立。
**Evidence pointer**：已有文件相对路径 + sha256 + 页/图/表/段落或 JSONL 原行 + 审核时间、角色、是否已发生化学阅读；无效行号必须标错误。

### 5.2 机器准入表（JSONL 强制字段；允许 null 但禁止默认零）

```json
{
  "schema":"task016-p8-candidate-v1",
  "candidate_id":"C-or-SS::stable-provisional-id",
  "family":"C",
  "source_work_key":null,
  "source_object_sha256":null,
  "source_rows":[],
  "assay_cohort_key":null,
  "p7_epoch_id":null,
  "scope_id":null,
  "reaction_graph_key":null,
  "identity_state":"unknown",
  "scientific_prior_read_state":"unknown",
  "g4_g5_firstread_order":"unknown",
  "exposure_class":"unknown",
  "structure":{"acceptor":null,"donor":null,"product":null,"donor_sugar":null,"site":null,"stereo":null,"reference_precursors":null},
  "a4_structure_result":"not_executed",
  "a5_structure_result":"not_executed",
  "a6_closure_result":"not_executed",
  "scope_static_applicability":"not_evaluated",
  "runtime_completeness":"not_evaluated",
  "p8_decision":"unassessed",
  "blocker_codes":[],
  "evidence_pointers":[],
  "next_one_action":null,
  "requires_owner_approval":false
}
```

- 表示三值时采用 `true / false / unknown`，时间/文件不存在采用 `null`；状态字段不得用混合的 0、空字符串、字符串 “false”。
- 至少区分 `unassessed`、`deferred_with_specific_missing_field`、`rejected_this_reaction`、`historical_design_only`、`policy_stop`、`governance_false_negative_suspected`、`stage_incomplete`、`P7_handoff_candidate`；禁止根据局部反应排除整篇文章。
- 一条 source 可有多个 claims，一条 claim 可引用多篇 source，source DOI 不等于反应唯一键。
- 附加独立文件保存 `raw_to_canonical_links.jsonl`、`identity_conflicts.jsonl`、`source_alias_edges.jsonl`、`assay_closure_edges.jsonl`、`exposure_events_effective.jsonl`、`candidate_status_transitions.jsonl`。每行绑定原始 ID、来源 SHA、规则版本与裁定理由。
- 按 P7 `3.2 评估每一次 scope freeze 与实际第一次**语义科学读取**、metadata 读取、byte-open 的真实时序，分开保存 `open_receipt_present` 与 `semantic_structure_review_completed`；后者不能由前者推断。
- 重复账本处理：distinct 指按来源**事件身份**及真实原行证据定义，另报总 ledger row instances 与多版本重复投影；禁止使用“同名词出现36次=36独立科学曝光”的推断。

### 5.3 每一候选必须可解释的 blocker code

定义有限词表：`SOURCE_IDENTITY_CONFLICT`、`RAW_OBJECT_UNAVAILABLE`、`SOURCE_LINKAGE_UNKNOWN`、`HISTORICAL_DESIGN_EXPOSURE`、`PRE_G5_CHEMICAL_EXPOSURE`、`SOURCE_ASSAY_CLOSURE_UNKNOWN`、`STRUCTURE_ACCEPTOR_MISSING`、`DONOR_MISSING`、`PRODUCT_GRAPH_MISSING`、`ATOM_SITE_MISSING`、`STEREO_MISSING`、`REFERENCE_PRECURSOR_MISSING`、`SCOPE_MISMATCH`、`SCOPE_G4_PREREQUISITE_MISSING`、`READER_INDEPENDENCE_MISSING`、`ROLE_TERMINAL_MISSING`、`RUNTIME_INCOMPLETE`、`LEGAL_ACCESS_BLOCKED`、`CONTENT_POLICY_STOP`、`EPOCH_INVALIDATED` 和 `NOT_YET_ASSESSED`。未知原因只能暂标 `UNCLASSIFIED_PENDING`，最终必须绑定责任人和具体调查/停止理由。

### 5.4 计数守恒与不可跳过的负门

- 原始导入行 = 已映射行 + 明确不适用行 + 解析失败保留行；不能静默丢行。
- `source_objects >= source_works`；HTTP/response 数不能作为 source_works 数。
- 每一已定位科学 claim 恰属一个终端/当前状态；`admitted + deferred + rejected + blocked + unassessed = located unique claims`；P8 handoff 不计 P7 admitted。
- 原始曝光事件行 = effective unique keys + duplicate-version projections + unresolved；同一真实事件不得计算为多次独立读。
- `reader states` 必须区分 authorized-not-started、started-not-terminal、terminal-success、terminal-failed、not-authorized、unknown；代码存在不是实际执行。
- 每个 role 的 input SHA、output SHA、原始证据指针、counts、error/unprocessed、read footprint 均不可缺；生成的自然语言分析本身不是 A4/A5 独立结构证据。
- 所有守恒差额必须在 `unresolved_reconciliation.jsonl` 有唯一 entry，不能为了使式子相等而补零、覆盖源行或编造 terminal。

## 6. 问题驱动的“损耗漏斗”与科学可达性计算

### 6.1 每个 family × scope 的候选漏斗

固定阶段：metadata hint → 合法原件可用 → source A3 verified → 定位具体反应 → true in-scope → independent A4/A5 full structure → A6 no leakage + prior-clearance → complete reference/runtime → frozen-scope static applicability → **P7 原合同才可计 admitted**。

每个阶段报告：
- 上一阶段不同 source/claim/target 数、转入数、拒绝数、待核数、未执行数；
- 每一拒绝/待核主因及具体缺字段（可另有多个次要 blocker）；
- 按 **source work / assay closure / reaction / target** 四个粒度分别去重；
- 净通过候选 ID，不能仅显示百分比；
- 不能依赖现有旧汇总复制，要从 raw-to-canonical lineage 独立计算。

### 6.2 conservative lower bound / conditional upper bound（不是成功预测）

- `L_targets`：全部当前**已严格核证**、适用于冻结 scope、结构和 reference 完整且可经 P7 重验证的候选数；当前历史已报告 0，P8 不得从审核建议直接把它升成 P7 final count。
- `U_evaluable_targets`：仅那些具名、有 source work/原件线索、允许处理、**明确列出仍待补证字段**且不存在已确认不可逆阻断的候选上界；一个未知旧读取/assay closure 未解决的项是条件数，不是“已 fresh”；无原文访问路径的线索不进入现实可达上界。
- `L_groups` / `U_groups`：按已证 source/assay/cohort 连通关系计算；未知关联须给“可能合并”的敏感性区间，不能默认每来源一组。
- `p7_floor_deficit_targets = max(0,6-L_targets)`；`p7_floor_deficit_groups = max(0,2-L_groups)`；同时报告 `U_targets<6`、`U_groups<2` 的本地证据边界，**绝不由此声称全世界不可完成**。
- 按 P7 G7/G8 实际准入结果区别 `can_run_gate_now`、`conditional_route_after_specific_work` 和 `no_route_proven_in_current_inventory`；不得把 P8 候选预测直接写成 G7 已冻结。
- 两轴分开判定；一轴有希望不等于另一轴完成；优先记录 exact 是否匹配 P7 已存在 v7 实例，防止重复重放冒充迁移。

### 6.3 四种最终可操作判定

1. `READY_TO_RESUME_P7_GATE`：具体候选和 manifest 已具 P7 原阶段机所需输入，仍待 P7 本身独立检查；不能无证据标 ready。
2. `BOUNDED_REMEDIATION_PATH`：缺口有限且授权/合法证据可补；每项给负责人、输入、预期输出、消耗和一次性停止条件。
3. `EPOCH_INCOMPLETE_RECOMMENDED`：冻结 scope 在当前有界、合法、已审核库存中缺口无法补足，建议按 P7 `3.3/`18 宣告对应 epoch incomplete，已曝光候选转 design，**新 epoch 必须新批准及全新 post-freeze holdout**。
4. `BLOCKED_OR_INDETERMINATE`：时序、policy、可达源、独立 reader 或证据身份无法闭合；不得自行跳过。可转人工处理或报告 Partial/Blocked。

P8 报告必须允许 **C=类别1/2/3/4、SS=另一类别**；不能为凑统一完成结论强迫双轴相同。


## 7. Subagent 组织：按数据所有权拆分，而非“轮流看同一篇论文”

可以调用真实 subagent，也可以使用互相独立、受控读集的进程/harness。不得把同一主控连续写两份文本称为两名独立化学 reader。推荐 **一个主控 + 六类角色**，最多同时 3 个执行子进程；科学双读者必须遵守 P7 A4/A5 的实际独立性。

| 角色 | 唯一职责、必须交付的独立文件 | 禁止与隔离 |
| --- | --- | --- |
| **P8-O（Orchestrator）** | 锁定 G0 manifest；维护任务配额与阶段令牌；签发受控只读工作包；整合 `decision_register.jsonl` | 不判断分子位点、不直接给候选 fresh=pass；不篡改下属产物 |
| **P8-I（Inventory & Provenance）** | 对 P1–P7 来源/原件/ledger/receipt 去重与 lineage；`source_object_index.jsonl`、`raw_to_canonical_links.jsonl` | 不读未授权的全新正文/图，不为缺证对象编写反应图 |
| **P8-X（Exposure & Temporal）** | 重算 effective prior/read/role epoch 时序和 source/assay/alias graph；`exposure_events_effective.jsonl`、`gate_timeline.jsonl` | 不看 A/B/E outcome，不修改旧 exposure；不将 unknown 清零 |
| **P8-C（C chemical triage）** | 仅消费 G1/G2 允许的现有证据，C-E02/E03 逐条 source→claim→structure/scope 差额；`C_triage.jsonl` | 不建立新的 scope；不对未授权 fresh 首读正文 |
| **P8-S（SS chemical triage）** | 同上，SS-E02、R80 与相关历史支持的具名反应；`SS_triage.jsonl` | 不把结构糖链关系推为重组酶体外因果证明 |
| **P8-V（Independent Auditor）** | 与主控实现分离，重读输入 SHA、逐行核分母、检查至少12个负门；`verification.json`、`counterexamples.jsonl` | 不引用 P8-O summary 当事实，不擅改数据或通过 blocked |
| **P8-R（Scientific Reporter）** | 对人类可读报告/STATE 用词和数据指针做独立检查；`report_audit.json` 与最终 REPORT | 不把 P8 inferred 记作 P7 verified，不能写 human_reviewed |

**重要补充**：P8-C/S 不是 P7 A4/A5 的替身。若 G4 pilot 需要新的化学读取，必须请求原 P7 合同的 A3/A4/A5/A6 合格角色、唯一源范围授权、独立输出和独立 verifier；P8 仅做调度与诊断，不另造不兼容的第三级真值。

### 7.1 每个 subagent 任务包

P8-O 事先发 `role_assignment.json`：task_id、stage、role、固定输入 paths+sha256、允许读的物理内容集合、**禁止内容的绝对路径/类型**、最大处理 ID 数、预期字段、允许的写目录、阶段门、最大操作量、期限/结束条件。角色返回 `role_result.json`：实际输入 SHA、实际输出 SHA、processed/pass/reject/defer/unassessed/unprocessed、第一条失败、代码 SHA、读内容事件（无则显式 false）、无法继续原因。

A4/A5 独立性至少需要：二者原始 source SHA 相同、分别进程/执行上下文、前者完成前双方不可读取对方结构产物、两份独立 terminal role 与 evidence pointers。只有文本 harvest 必须保持 `structure_complete=false`；A6 在双 terminal 之前不可写 `reconciled=true` 作为结构通过。

### 7.2 实施与并发顺序

`P8-O -> (P8-I ∥ P8-X) -> P8-V reconciliation -> (P8-C ∥ P8-S) -> P8-V -> [有授权则 P7 A4/A5/A6 科学 pilot] -> P8-V -> P8-R`。

- 同一候选最多 **1 主审 + 1 复审**；同一阻塞不允许无新增数据反复换 agent 跑。一次复审仍无法达成则 `unresolved` / `owner_decision`。
- 若某子 agent 中断，保留 terminal `agent_failed_or_incomplete`；不拿启动事件冒充执行完成。替代 agent 要新 role assignment、明确继承仅 metadata/允许原始输入，并继续独立负门。
- Agent 间通信只交换**带 SHA 的清单和结论**，不交换未授权正文，也不依赖易失聊天上下文来保管科学事实。
- 跨轮次恢复先读 P8 G0、阶段 state、待办 ID、未处理计数，再执行一个固定包；不得通读数百快照当作“恢复”。

## 8. 严格有界的阶段计划（每关可单独停止）

### G0 — Freeze & Inventory Boundary（先建工作基线，不打开新科学内容）

**输入**：本 TASK 获批版本、STATE、P7 主报告与 Oct12 两份预检、R81–R87、P7 P1–P6 可达原 ledger、关键 scope、已存在测试、Git status、`operations/events.jsonl`。

动作：逐项 SHA 冻结文件指针与物理存在性；记录 P7 现有 G4、G5、epoch、reader、role、protected hashes、已停止来源、权限边界、当前 P7 可能仍在写的文件；保证 P7 与 P8 不会同时改同一账本。对**已知无法取得**的 raw source 仅记录 inaccessible，不重复下载。

交付：`G0/input_manifest.json`、`G0/contract_registry.json`、`G0/freeze_state.json`、`G0/read_permission_matrix.json`、`G0/baseline_conflicts.jsonl`。单一 `current_snapshot_id` 决定以哪份 STATE/report 为入口，保留较早截面。对 293 test、214 MCTS、82 epoch 等数字标 `historical_not_rerun`。

**G0 gate**：全部声明输入都有 SHA、状态和可读/不可读标记；0 个未经声明的新增科学读取；任何核心冻结 scope 文件 drift 则停止 P8、通知所有者，不自行修复。

### G1 — Unified Source/Reaction/Exposure Census（全量离线源清账）

**输入**：G0 指定的已存在 metadata/index、历史 P1–P7 source/query ledger、P7 exposure/epoch、各阶段 G5/G6、已存在 17源/36 行反应清单、R80/C-E03 记录；不预设只存在这些来源。

P8-I 读取**账本的元数据与既有结构化结果**，不打开新文章正文；以稳定 ID 统一 raw-object/source-work/reaction-claim/target/closure 关系，保存包括没审过的来源与其他卷次。所有原行/异常、未解析 pointer 和旧错误报告必须可导航到原文件。

交付：`G1/source_object_index.jsonl`、`G1/source_work_index.jsonl`、`G1/claim_registry.jsonl`、`G1/target_registry.jsonl`、`G1/import_coverage.json`、`G1/raw_to_canonical_links.jsonl`、`G1/identity_conflicts.jsonl`。

**G1 gate**：已声明的每个 ledger/file prefix 均有 imported/count/failed/missing；重复多版本不多算；检测 2026-10-11 17-source/36-row 局部清单不能偷换成全库；所有异常有证据指针。没有必要重新运行无关工程 suite。

### G2 — Exposure / Stage / Prior / Role Root-Cause Audit（救真正的治理假阴性）

P8-X 在固定有效 prior/present ledgers 上重算：
1. `isoorientin` 36 行实例/12 distinct/0 完整结构字段的来源版本差异，检查此前无效行号及“名称即结构泄漏”假设；
2. R73 被停止五源的真实 first-read 事件、role terminal 空缺、永久曝光状态；不能从不存在的 role 推断内容已通过；
3. SS/R80 两来源 `prior_scientific_read=unknown` 的物理前置、8 旧事件、恢复 v1 拒绝负门、v2 metadata 成功与 A4 registration/permit 的**真实当前时序**；
4. C-E03 R83 文本 harvest 与完整 A4/A5 structure 不一致，R86 G4 工程通过不覆盖科学前置，三 fresh hints 未得 A6 clearance；
5. 论文/反应/site 范围错配、旧 E01/旧 holdout 与 epoch contamination；来源 identity-only、source alias、assay cohort 的负门；
6. 读后补录、错误 DOI、publication/SI linkage、unknown 被写成 false、role 仅代码存在、错误 candidate denominator 等已知模式；
7. 阶段锁是否在候选预审之前真实调用，是否存在 `fail-open` 或错误的 `fail-closed`。

交付：`G2/gate_timeline.jsonl`、`G2/effective_exposure_ledger.jsonl`、`G2/counterexamples.jsonl`、`G2/root_cause_register.jsonl`、`G2/disputed_prior_decisions.jsonl`、`G2/patch_proposals/`（仅有重现和最小 diff 建议，不自动修改 P7）。

**G2 gate**：每个具名缺陷至少有原始输入、旧输出、独立重算、最小正/负反例、修复建议或严格保留 unknown；不得因为预期“fresh 从0增加”而人为选择裁定。

### G3 — Family-Specific Dossier Funnel（让已有论文实际产出可行动信息）

P8-C 与 P8-S 分轴独立，只消费 G1/G2 已有合规内容/证据和必要 metadata。首先按照“科学相关度×证据完备性×未曝光潜力×真实 scope 静态匹配可能性×获取可行性”固定候选优先级；排序**不得读取 A/B/E 搜索结果**或改 scope。

**C 指定起点**：
- C-E02 direct flavone C6：PMC13564134 与历史 2-hydroxyflavanone→脱水案例分开；明确 gyCGT1 的实测/叙述与完整 reference 缺口，isoorientin 名称曝光按 G2 结果处理；
- C-E03 C8：Liu2021/R83 design 独立结构前置（不读取已停止内容）、R84 PubChem 图/身份链、R85 TcCGT1 两 build supports、R86 frozen G4、R87 三 hint（he2019/qiu2021/王源杰2018）；
- 不将 C8 候选塞入 C6 scope；如果 scope 缺失科学前置，不让新的 G5 实验制造更多曝光。

**SS 指定起点**：
- SS-E02 / R80 豌豆 1982 与 Morita2005 的 2-source × 2-reader 缺终结状态和 prior unknown2；只在已获授权范围内使用已有证据；
- Trapero2012/R82 1→2 的 HMBC 是结构设计证据，不等于酶级体外催化或 fresh；
- Shute/Jourdan/Mansell 1979 的多葡糖苷例缺内层 O2 原子证明；rutin 3/7-O 跨位点例不属于糖残基 O2；
- 既有 SS 正面文献同 PMID/PMCID/assay closure，不能把 DOI 别名当新 group。

交付：`G3/C_dossiers.jsonl`、`G3/SS_dossiers.jsonl`、`G3/funnel_by_scope.json`、`G3/priority_queue.jsonl`、`G3/source_reaction_vs_article_dispositions.jsonl`。每张 dossier 必填：具体成键主张、来源锚点、是否可接 P7、证据已具字段/缺字段、两个 reader 真正终结状态、主要 blocker、**下一唯一动作**、下次尝试必要新增输入。

**G3 gate**：两轴每个起点均有明确 disposition；不存在用 `unassessed` 报“论文不含反应”的情况；存在至少一张 end-to-end pilot 工单，或有证据证明无合法可读候选并登记 owner_decision。不能无限扩张优先队列。


### G4 — Bounded End-to-End Qualification Pilot（证明管线工作，或定位首个硬阻断）

**本关不是正式 P7 G5/G6/G7，也不是承诺必定取得 1 个 fresh。** P8-O 只能消费 G3 优先队列、阶段就绪凭证和所有者授权。先选每轴**至多3个不同 claim/组的候选**，总量 ≤6；每个对象最多 1 次规范执行 + 1 次基于具体新证据的纠错复核，不无限换源、换 reader、换合同。

**工作包种类必须互斥：**

- **T1：metadata/ledger-only 复算**：未取得新科学读取许可时，能用既有 evidence pointer 完成 source identity、prior/exposure/alias 与角色授权/终结时序核验；报告 expected vs actual gate，绝不生成新科学图。
- **T2：既有已合法曝光 design 证据补齐**：只能在现有已获准、未被安全停止的材料及允许读集内，补明确所需 structure/assay 权威证据；这类结果属于 development support，**不自动 fresh**。
- **T3：同 epoch 已合法 G4/G5 预先冻结的 evaluation continuation**：必须先校验 prior/read 顺序、source/assay closure、P7 原 scope SHA、真实 reader permit、独立 A4/A5 terminal 和 A6 阶段资格；例 SS/R80 如需恢复，完全遵循既有 v2 限定，不由 P8 重新签发“许可”，不把 A4 的 registration pass 当实际科学执行，也不擅自动用 A5。
- **T4：新的 prospective 首读**：**不在 P8 默认执行权限内**。须另获所有者逐源逐 epoch 许可，并依 P7 原合同完成独立设计前置和 G5-before-read；若不可满足则输出“新任务/新 epoch 申请”，不在 P8 趁机展开新的采集循环。
- **T5：受安全/访问限制的 source**：立即 `policy_stop`，不构造替代 reader/提示/解析器/下载方式绕开限制；仅以已存在且允许核查的身份/metadata 结论关案。

**试点单体 protocol（每个候选记录 1 行 machine trace）：**

1. 记录 frozen scope SHA、source object SHA、真实历史 prior 与当前 epoch ID，证实法定读取权限与安全边界；
2. A3 来源身份或引用既有已独立通过身份，分辨本文 vs SI、文本描述 vs 反应原图；
3. 对需要且经逐源授权的科学结构阶段，调用 **P7 原 A4/A5 两个独立 reader**：各自完整 acceptor/donor/product/site/stereo/sugar、证据页图、reference precursors、graph canonicalization，不可拿文本 harvest 顶替；
4. P7 A6 从有效 exposure ledger + exact reaction + assay/source alias + scope support 重算 prior closure；unknown 保留，冲突独立裁定；
5. P8 仅做 **G8 dry-run**：在不读取模型结果/不创建 MCTS 的条件下，静态验证 scope 对完整 reference precursors 可适用，以及 target 不属于 exact build/runtime instance；
6. 最后输出 `P8_candidate_handoff_ready` 或确定的 `blocked_at_stage`；P7 的 G6/G7 真正晋级还需其原冻结 writer/independent verifier 自行复核。

交付：`G4/pilot_contracts/*.json`、`G4/pilot_execution.jsonl`、`G4/pilot_gate_trace.jsonl`、`G4/reader_independence_audit.json`、`G4/pilot_dispositions.jsonl`、`G4/stop_disclosures.jsonl`。每个 pilot 需要记录首个失败门（first-blocking-gate）、消耗、是否实际处理源内容、未处理字段、是否消耗未来 fresh 资格。

**G4 gate**：全部被授权 pilot 均有真实 terminal（passed / blocked / deferred / policy-stop），缺失/无权执行也有机读终止理由。若 0 个可被合法执行，必须给出两轴各自已查证的阻断清单，不伪造 pipeline success；不能无限寻找下一篇。

### G5 — Scientific Feasibility & Decision Gate（真正回答能否恢复 P7）

对各 C/SS 的每个已冻结 scope 建：
- `observed_lower_bound`：仅实际 A3、完整双图、A6 无泄漏、reference/runtime/static scope 均已证而形成的本任务建议数；**不宣称 P7 admitted**；
- `conditional_upper_bound`：具名来源/反应和可获得的必要证据集合，按所有必需假设逐条标注；不存在可合法取得的必要原文时上界应收缩；
- 按 worst/best-case closure edge 两种情形分别计算组数；
- 受限/设计曝光/不合 scope 已排除对象及理由；
- 可补证是否能触及 P7 6/2 的 minimum floor，不能则明确“**就当前有界库存无证明路径**”；此结论不是全球论文不存在、也不是 P7 自动停止；
- 下一个唯一最有价值动作（missing evidence → authorized actor → immutable output → go/no-go）；**不允许建议“无限继续搜文献”**。

交付：`G5/feasibility_C.json`、`G5/feasibility_SS.json`、`G5/decision_matrix.json`、`G5/prioritized_remediation_backlog.jsonl`、`G5/owner_decision_required.jsonl`。决策结论只能取 `READY_TO_RESUME_P7_GATE`、`BOUNDED_REMEDIATION_PATH`、`EPOCH_INCOMPLETE_RECOMMENDED`、`BLOCKED_OR_INDETERMINATE`（两轴独立）。

**G5 gate**：所有上下界均可从逐候选 ledger 重算；缺省为 unknown，不能因为论文多就推断分母够 6；每条“继续”建议都有确定边界、证据和终止条件。

### G6 — Minimal Repair Proposal & Transfer Package（修最少的真 bug）

只对 G2/G4 已**复现且造成实际错拒/错放/角色损坏**的缺陷提出最小改动。推荐顺序：
1. metadata vs scientific_read 与三值规范化；
2. 源/assay 别名闭包与跨版本 exposure distinct 去重；
3. role terminal、input SHA、reader 独立完成才进入 reconciliation；
4. stage-lock 对 stale/missing G4/G5、读前许可、exact instance 排除 fail closed；
5. 静态 precursor/applicability 缺字段时不默认 false 或成功。

每个 patch proposal 有 `bug_id`、受影响真实 candidate ID、reproducer input SHA、旧/新期望、最小 patch diff、正负测试、受保护文件 SHA、回滚计划、是否影响 P7 冻结成果、所需额外批准。**除 P8 自身索引/测试工具外，不合入 P7 修复；原失败版本保留。** 不因测试数通过重写 G4 或借新 scope 达成指标。

**P7 handoff package** 最少含：
- 唯一事实源与原行映射、全部 freeze SHA，旧未知/冲突/访问停止不可省；
- C 和 SS 分开的候选可执行队列及明确 exclusion/defer/historical；
- 逐条 `stage_to_resume`（例如 G3 design proof、G5 prereg、A4、A5、A6、G6、G7、G8），实际许可和前置条件；
- P7 应继续执行的**原合同入口**及验签方案，不编造“P8 自动放行”API；
- 对 P7 `3.3` 的 epoch incomplete 建议，如需变更 scope 给出**新 epoch 提案**，不让现有 holdout 循环使用；
- 遗留 O/P1/P6 真实能力保护清单、未来 A/B/E 必须做的真实 node/legacy regression、TASK-017 separate-gate 提醒。

交付：`G6/P7_HANDOFF_MANIFEST.json`、`G6/P7_RESUME_PLAYBOOK.md`、`G6/P7_PATCH_PROPOSALS.md`、`G6/stop_or_resume_decision.json`。交接文件必须被 P8-V 从 G0–G5 原始产物**独立复算**，非主控直接拼接结论。

### G7 — Independent Verification, Report & State（在证据正确的地方停）

P8-V 独立重读 G0 已冻结原件哈希、G1–G6 所有有效行与各 role terminal，核对：
- input/file/source/claim/event/target/count 与 source/assay closure 连通分量守恒；
- exact/name-only exposure 与 prior unknown 的负控；
- A4/A5 独立完整结构、G4/G5 首读时序、stop policy、scope applicability、P7 权限与实验边界；
- stage counts、状态净变化、budget/no-new-HTTP/no-MCTS；
- REPORT/STATE 和 P7_Handoff 的**每个核心数值**可由证据重算；
- P7/G4、模型/stock、旧保护件零无法解释漂移；`git diff --check` 及无受限数据混入 Git/package。

P8-R 生成中文 `docs/reports/REPORT-016-P8-evidence-rescue-feasibility.md`，明确结论/剩余 unknown/无法推进的源、成本、已经纠正与**没有纠正**的错误、对 P7 的一次性下一步。更新 STATE 只保留 P8 当前终态以及 P7 实际状态，docs/tasks/README 索引保持；若需要更改路线图，**另附修改建议由所有者批准**，不抢先宣告 Roadmap 已完成。

**G7 gate**：全部上述验证通过、P8-V 与 P8-R terminal 可追溯才允许 P8=Completed；否则 Partial/Blocked 并真实报告。

## 9. 预算、队列上限、反空转 watchdog

| 资源 | 硬边界（超过须停并重新取得批准） |
| --- | --- |
| G0–G3 外部 HTTP、新论文下载、新科学首读 | **0 / 0 / 0**；只能消费现有合法 metadata 与已经批准/完成的审查结果 |
| P8 默认全程新 HTTP / 新原件 | **0**；要补合法来源独立开补证/新 epoch 授权，不能默默计 P7 原额度 |
| P8 全程真实 MCTS cell | **0**，不消费 P7 600 上限、不更改任何历史 runner |
| deep-dossier priority queue | 最多 **24 份**（C ≤12、SS ≤12）；超过仅列 deferred backlog，不继续分析 |
| G4 end-to-end pilot | ≤**6 条不同 claim**（C ≤3、SS ≤3）；最多一轮规范执行 + 一轮有新证据的受控复审 |
| P8 新的可执行 Python helper | ≤**6 个**（索引/差额/静态门/独立验证等共用程序），禁止 per-source 脚本爆炸 |
| P8 新单元测试 | 优先一个 `tests/test_task016_p8_contract.py` 内的参数化 guard fixtures，不为每轮新建文件 |
| 同时运行的 subagent/独立进程 | ≤**3**；科学 A4/A5 必须保持读集隔离 |
| subagent 工作包 | ≤**14 个主包**；重试必须有新证据 SHA + 预批准，不重复无变化任务 |
| 审核迭代 | G1/G2 统一 baseline + 1 次差异复审；G3/G4 每候选仅一次新证据复核 |
| G0–G7 local operate 执行命令 | 计划 ≤**120 个**（审计只读计入）；达到 120 必须停止或重新授权 |
| Git 变更 | 默认合同/索引/报告/新 P8 helper；绝不默认 commit/push、改 P7 protected |

Watchdog 在每个阶段必须统计 `candidates_changed_state`、`unknown_resolved`、`confirmed_false_negatives`、`new_valid_handoff`、`new_irreversible_blocks`、`commands`、`new_helpers`。**连续两个授权工作包在相同固定输入 SHA 下全部为 zero_change 且无新的明确阻断**，立即停止相应支线，记 `nonproductive_loop` 并形成决策，不允许以“又跑了 200 个测试”重置计数。所有者可重新批准带新输入的具体补证，但不能暗改预算。


## 10. 最小实现建议（避免再新增数百个脚本）

优先以 P7 既有 source/identity/closure/scope/panel harness 的**只读接口**重算；仅在实际缺口需要时新增：
1. `task016_p8_inventory.py`：指定输入 manifest，统一 metadata rows、原始行 pointer、唯一 work/claim/target key；不得再抓网页。
2. `task016_p8_exposure_audit.py`：三值 prior/read events、跨版本去重、角色 terminal、G4/G5 序列、闭包图。
3. `task016_p8_funnel.py`：按 C/SS/scope 计算漏斗、显式 blocker、上下界、状态差额。
4. `task016_p8_pilot_dryrun.py`：只读 pilot 阶段契约和 P7 既有静态 validator，禁止调用 MCTS/HTTP/open new source。
5. `task016_p8_independent_verify.py`：从原始输入独立重算，不调用前述脚本的汇总函数，重点测试负门。
6. `task016_p8_handoff.py`（仅确需时）：生成带 SHA 的 P7 handoff，而不是另造 P7 状态机。

所有脚本都应为相同 manifest 重跑得到相同**规范化 payload**（带时间的审计事件单独存，不掺入可复算数据哈希）。不得对 P1–P7 历史目录写入缓存；Python 解析、日志和临时文件仅存 P8 自己目录。每次项目写入/命令必须通过 `scripts/operate.py TASK-016-P8 ...` 记账，保留失败 stdout/exit code，禁用“如果文件存在就悄悄跳过”作为有效阶段完成证明。

### 10.1 必备正/负门回归（不少于以下场景）

| 测试 | 必须断言 |
| --- | --- |
| historical design source 重新作为 fresh | 拒绝，原因可定位 |
| G5 后同 epoch 合法首次读 | 不能仅因 current exposure 自动拒绝，仍需 A6 完整证明 |
| G5 前发生真实结构阅读 | 不能追溯准入 |
| prior `unknown` / source alias unknown | 不转 false / leak-free |
| 同一 12 distinct × 3 版本行 | 计为12 distinct、36 ledger instances，仍不能推断结构曝光 |
| metadata-only partial name match | 既不能自动 true leakage，也不能自动 false |
| source identity 仅 HTTP 200 / 文件名 | 不通过 A3 |
| article 与 SI 关系 unknown | 不自动绑定 |
| 拒绝的单条反应 vs 未核整篇 | 不升级为 article-level exclusion |
| 2 个 reader 都只抽文本 | 不能通过 P7 dual-structure |
| A4 reader 启动未终结 / A5 只有准备脚本 | 不能当作 terminal/已执行 |
| A0 synthetic reconciliation=true | 不替代双 reader 图 |
| 旧 R80 event 数差额 / zero-hardcode | 保留真实 8 event 与 prior unknown2 |
| C8 scope 对 C6 target / SS aglycone-O 对 inner-sugar-O | static out-of-domain 真实拒绝 |
| no product graph / donor / stereochemistry | 不写 runtime_complete=true |
| source/assay group 共用设计闭包 | group 不虚增 |
| G4 SHA 与 reader input SHA 漂移 | fail closed |
| stopped content 换 reader 重试 | 明确禁止，非可尝试的 workaround |
| empty queue、missing key、malformed JSONL、非幂等 hash | 明确报错/unknown、永不默认成功 |
| synthetic testcase 出现“node transfer” | 不冒充真实 P7 A/B/E |

所有 fixture **必须用合成/允许公开的最小值**；禁止在 Git 单测中拷贝原始文献、受限结构或未获权限的 PDF。历史回归仅在 P8 代码真正触及共享接口时按影响域执行；若未触碰共享代码可运行有界 P8 tests + SHA/diff，完整 suite 是否重跑必须明示。

## 11. 里程碑检查点、审批与分流策略

| 检查点 | 可用的最小事实 | 所有者/主控下一步 |
| --- | --- | --- |
| **M0 = G0 pass** | 真实源快照、权限、保护清单冻结 | 准许离线 G1；同时阻止 P7 在未纳入快照的情况下并发改变科学账本 |
| **M1 = G1/G2 pass** | 源/反应全量覆盖表、假阴性与角色/先后门缺陷 | 若 G2 显示前置崩溃，先限域修 stage gate，不继续搜 |
| **M2 = G3 pass** | 每轴明确至多12项优先级候选与其唯一阻断 | 决定是否另行授权某个 G4 科学 pilot；不自动授权 |
| **M3 = G4 terminal** | 至多3+3个真实 pilot 结果，或无可许可候选的严格说明 | 可证资格向 P7 原 validator 交接；否则进入 G5 判定 |
| **M4 = G5/G6 pass** | C/SS 可达性、有限补证账单、P7 handoff / epoch 决议建议 | 所有者决定恢复 P7、另开有限补证、新 epoch 或停止 |
| **M5 = G7 pass** | 独立审核＋REPORT＋STATE 当前事实 | 关闭 P8；P7 是否重启**另依据原科学合同** |

**验收分流示例**（不是结果承诺）：
- 若 G2 证实因 prior 代码错拒造成候选被挡，输出被影响 candidate ID + 最小 patch + 完整负门测试；P7 只有在真正重新验证 G6/G7 后才能计入。
- 若候选结构证据一直缺 site/stereo/reference，输出具体论文页/SI/权威图 ID 的**有界补证需求**；如受阻不能继续，则宣布当前候选 deferred，不消耗新 epoch holdout。
- 若 C-E03 的独立设计结构前置无法合法补齐，当前冻结工程 scope 保留、科学资格锁保持；不利用 R87 的三篇未知 prospect 倒逼 scope 前置。
- 若 SS/R80 有真实、获批的 A4/A5/A6 终结结果，独立核入 P7 原合同；如仅 metadata 237/237，则 P8 不得写 SS 已录取。
- 若即使上界的具名候选都不足各自6/2，则对当前库存建议 scope-epoch incomplete/补证或新研究设计，不再无界扩张脚本和搜索；**不可修改 P7 科学分母来制造 Completed**。

## 12. 必须验收的交付清单（P8 Completed gate）

### 数据事实源
- [ ] G0 实际未提交工作区与 P7 protect SHA 固定，既有停止源权限清晰。
- [ ] G1 全部声明输入账本/原件索引覆盖有分母守恒、可回溯原行；输入失效和 source/assay 冲突未被隐瞒。
- [ ] 来源、反应、目标、事件、版本、组五类身份没有错误混计；17/36 局部清单不冒充全量。
- [ ] distinct/name-only/true-structure exposure、prior unknown、G4/G5/首读顺序分别三值呈现。
- [ ] 每个已定位对象有唯一当前 disposition、blocker、最小下一动作或可审计终结理由。

### 可执行资格诊断
- [ ] C-E02 / C-E03 / SS-E02 和 R80 的指定缺陷均有具名、证据指针可复算的裁定。
- [ ] 已有的 P7 source/structure/reader/stage 错误中，至少明确区分真实科学阻断与治理 bug；不能混写“无任何反应”。
- [ ] G4 所有获批准 pilot 都有 terminal 结果；如果无合法 pilot，则有独立复核的 first-blocking-gate 清单。
- [ ] P8 没有伪造 G5 首读、没有洗白 design 来源、没有换 reader 绕过停止、没有用文本 harvest 冒充完整化学图。
- [ ] 每轴已冻结 scope 的上下界及 >=6/2 可达性均可独立重算；“当前库存无证明路径”和“全世界不可行”严格区分。

### P7 可用的交接
- [ ] `P7_HANDOFF_MANIFEST.json` 和 `P7_RESUME_PLAYBOOK.md` 绑定每条候选、原 SHA、阶段、角色、缺口、权限与明确 go/no-go。
- [ ] 每项 patch proposal 有可复现缺陷、真实受影响对象、正反测试、回滚及需授权范围；无擅自改 P7 core 或 scope。
- [ ] C/SS 分轴终态为四种之一，包含具体的最小后续行动与终止条件；所有者决策点明显可见。
- [ ] P8 对 TASK-016/O/P1/P6 的保护，以及未来 P7 G7/G8/G9/G10/legacy/node 和 TASK-017 独立盲测门，全部清楚列示。

### 程序、预算与证据边界
- [ ] G0–G3 HTTP=0、新科学首读=0；P8 正式 MCTS=0；脚本、worker、pilot、review 数未超过第9节。
- [ ] P8 独立 verifier 从原始证据核对计数、负门、哈希、净状态变化、权限和输出，不仅测试“文件存在”。
- [ ] `git diff --check` 通过；原始/受限数据无 Git/打包泄漏；共享受保护文件无无法解释 drift。
- [ ] 用 `REPORT-016-P8-evidence-rescue-feasibility.md` 记录真实执行、负结果、未决、权限与 Git 状态；STATE、task 索引仅准确反映当前阶段。
- [ ] P8 结案没有将 fresh 0 伪装成成功、没有将治理 pass 称科学 pass、没有将 P7/P2/TASK-017 自动标 Completed。

**一项不通过则 P8 只能 Partial 或 Blocked。** 若某个 family 无法恢复但以上诊断与独立交接完成，P8 可 Completed，P7 仍按原合同独立状态结案或继续。

## 13. 立即停止、报告及恢复纪律

任何以下情况立即停受影响支线并封存证据：scope/G4/protected SHA 无法解释漂移；来源身份虚构/无法证明；无法保障独立 A4/A5；prior/assay unknown 被隐式清空；读取与许可顺序倒置；读受限/安全停止内容；出现 P7 MCTS 调用；原始文献进入 repo；需要更改科学门/模型/stock；超过配额；同固定输入重复无产出；出现文件名/行号指针不可解析且被当 pass；subagent 发生未授权内容访问；输出声称 human_reviewed/independent chemistry 而没有实证。

任何修复只能**新版本、append-only、保留原失败结果与 SHA**。不能删掉 superseded 记录、修补出虚构 G5 pre-read 或通过盲目脚本恢复让 unknown 消失。安全/访问阻塞允许以 Blocked 终结，不鼓励寻求绕过方案。

## 14. 必须提交的报告与批准接口

1. 起草完成只登记 `P8 Proposed`；所有者后续批准需明确是仅 G0–G3 离线执行，还是另签发具体 G4 试点授权。仅收到“开始 P8”默认**仅 G0–G3 离线执行**，不得新读尚未获许可的 prospect。
2. 未来 REPORT 与 TASK 同短标题：`REPORT-016-P8-evidence-rescue-feasibility.md`；报告必须有“科学合格候选/治理修复/原件访问/角色恢复/真实 A/B/E”分别的分母表，每个为空也明确写 0 或 null 的准确语义。
3. P7 恢复条件以 **该轴** 的 P7 阶段机真实输入为准，不能用 P8 报告直接重设 scope 或调用 G10。恢复审批必须绑定 P7 scope+epoch+候选、源/read 许可、前置 verifier。
4. 若需要新的大规模采集、scope epoch 或 P7 修复，**提出独立限定合同和预算**，由所有者另批；P8 不吸纳新的无限探索。
5. 以 `PROJECT.md → STATE.md → ARCHITECTURE.md → TASK-016-P7 → 本 TASK` 的阅读顺序进入执行，所有命令/写入通过 `scripts/operate.py`；最后 REPORT→STATE，Git 是否提交/推送另获明确指示。

**总原则**：不以降低科学标准换取 fresh 计数；不以增加治理工作代替科学产出；用可核验的候选状态变化、明确阻断与有限下一步，让 TASK-016 的 C/SS 研究从无界循环回到有终点的科学决策。
