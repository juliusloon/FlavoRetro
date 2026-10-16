# TASK-016-P7：领域对齐的新底物迁移闭环与 Roadmap P2 终验

## 合同元数据

- 任务 ID：TASK-016-P7；合同版本：v0.1；起草日期：2026-10-07。
- 状态：**Proposed（拟议，未授权执行）**。
- 起草授权：所有者本会话明确要求“根据这些问题建立新的 task，解决这里所有的问题，真正实现 roadmap 里 TASK 16 的效果，并设计多 subagent / loop / harness、明确验收标准和边界”。该指令授权本合同落盘与治理登记，**不等同于执行授权**。
- 执行批准：待所有者另行明确批准；批准后按实际授权类型记录，禁止写成 human_reviewed。
- 人工负责人：项目所有者。
- 执行者：待批准后登记；建议主控 Cano + 多角色 subagent/harness。
- 工作区：`/home/ljx/FlavoRetro`。
- Git 定位基线：`993b22f5e8eed5797d27f02c566af1b86a4b7880`；当前工作区包含 TASK-015/016 系列大量未提交成果，执行基线不得只用 HEAD，必须以文件 SHA manifest 冻结实际工作区。
- 前序合同：[TASK-016-P6](TASK-016-P6-c-scope-runtime-transfer-closure.md)。
- 前序报告：[REPORT-016-P6](../reports/REPORT-016-P6-c-scope-runtime-transfer-closure.md)。
- 计划本地科学产物根：`outputs/task016-p7/`；计划新原件根：`data/raw/task016-p7/`。
- 所有项目内命令与最终写入继续经 `scripts/operate.py` 登记。
- P1–P6 的 TASK、REPORT、冻结载荷、错误版本与 supersession 记录保持历史原貌；P7 不回写历史来“修正”旧结论。

## 一、任务目标：真正完成 Roadmap P2 的开发层效果

Roadmap 的 P2 / D2 目标不是“增加模板数量”，而是：

> 把经过验证的黄酮苷领域知识转成受控的搜索候选能力，并在冻结协议下证明它能改变真实 MCTS 的搜索行为，同时保留证据边界和既有能力。

TASK-016 主任务与 P1 已经证明来源限定的 O-糖苷实例补回；P2–P6 则暴露并逐步清理了 C 成键与糖间成键的来源、结构、scope、holdout、泄漏和 runtime 问题。P7 的唯一总体目标是：

**对 C-glycosylation 与 sugar–sugar glycosylation 两轴，建立 source-qualified、scope-aligned、无 build/holdout 泄漏的新底物开发留出，在冻结 scope 与冻结运行合同下完成真实 A/B/E MCTS，达到预注册迁移硬门，并证明最终领域策略没有造成既有参考能力退化。**

只有以下全部成立，P7 才可写 **Completed / Roadmap P2 development effect closed**：

1. C 与 SS 各有合格 scope bank；
2. C 与 SS 各有 `>=6` 个 runtime-executable、与 scope 同域的 post-scope holdout，且 `>=2` 个独立 closure groups；
3. 两轴都实际执行完整 A/B/E 三 seed 矩阵；
4. 两轴都达到候选迁移、真实 node transfer、净覆盖和零 reference loss 硬门；
5. 最终 runtime、旧能力回归、package/no-asset/fail-closed、来源审计与保护完整性全部通过；
6. 没有通过改变 holdout、scope、模型、PUCT、库存、评分或门槛来追成绩。

**只完成工程、只补面板、只完成其中一轴、或只观察到候选生成而没有真实 MCTS node creation，整体均不得标 Completed。**

## 二、P6 之后的权威问题清单

P7 必须把以下问题全部作为输入，不得再次遗漏：

1. **C scope/holdout domain mismatch**：P6 的正确 `flavonol_8_C_glucoside` scope 对 6 个完整旧 holdout 为 0/6，因为这些 holdout 实际属于 flavone C6、benzophenone C3、gallic-acid C2 等不同母核/位点。
2. **SS 独立完整留出不足**：P6 真正可用的 SS holdout 仅 1 target / 1 closure group；旧计数中存在次级评论、共享 build closure、供体/连接标签错误。
3. **历史 development exposure 过深**：P2–P6 的旧 panel、probe、来源和结构已经多次被观察，不能继续把它们当成新的迁移证据。
4. **P4 泄漏事故**：build support 曾进入 holdout，必须永久防止。
5. **P5 scope 实现事故**：exact instance template 曾被误当 scope，必须永久防止。
6. **P5 来源真实性事故**：subagent 曾返回与声称内容不符的 PMC ID；HTTP 200 不能成为证据资格。
7. **P5 手写复杂结构事故**：名称不能替代结构，执行者记忆/手写 SMILES 不能进入 structure_complete。
8. **P5 查询循环漏执行**：计划查询必须由 harness 对计划数/执行数/结果数做差额守恒。
9. **P5 canonical acceptor 空集合静默失败**：所有关键计数字段必须 schema-validated，不允许缺字段默认为 0。
10. **P6 正确工程资产已经存在**：v6、C scope guard、build replay、旧 17×3 回归、P6 合同测试均不得无理由重写。
11. **训练独立性仍 unknown**、formal benchmark 未执行、独立化学验证未发生；P7 只能形成更强的 development transfer 证据，不能冒充 TASK-017。

## 三、关键实验设计改变：scope-first、fresh-holdout、epoch 化

P7 不再继续“拿现有 holdout 去找一个能命中的 scope”。这会造成后验设计。

每个家族 C / SS 都采用独立的 **scope-first epoch**：

```text
Design corpus（可使用 P1–P6 暴露数据）
        ↓
build supports / scope definition
        ↓
replay + boundary controls
        ↓
FREEZE scope SHA
        ↓
之后才允许化学抽取 fresh evaluation candidates
        ↓
identity / structure / closure / runtime completeness
        ↓
post-scope holdout freeze
        ↓
static applicability preflight（不可改 scope）
        ↓
A/B/E
```

### 3.1 旧数据的角色

- P1–P6 中已经看过结构、反应、panel、probe 或 runtime 结果的对象，一律记入 `historical_development_exposure`。
- 它们可以进入 P7 的 design corpus、scope build support、boundary design 或诊断材料。
- **不得作为 P7 的新底物迁移成功分母。**

### 3.2 fresh holdout 的定义

一个 P7 evaluation reaction 只有同时满足以下条件才可进入迁移分母：

- scope 已经先冻结；
- 该反应没有用于该 scope 或任何 P7 scope 的构建、规则设计、边界调节；
- 与 build reaction/source closure 零交叉；
- 在进入 scope freeze 前，没有被项目用于化学结构/位点级的 scope 设计；仅 metadata-only discovery hint 可以保留，但必须在 exposure ledger 中说明；
- product、acceptor、donor、成键位置、关键立体、reference precursor 全部 runtime-complete；
- 结构来源可追溯且不依赖执行者手写猜测；
- 未进入 exact template runtime instances；
- 在冻结 panel 前未运行 A/B/E 或其他模型结果筛选。

### 3.3 epoch 失败如何处理

如果某个 scope epoch 冻结后发现 fresh holdout 数不足、closure 不足或 applicability 不足：

1. 本 epoch 判为 `development_epoch_incomplete`；
2. 所有已被化学抽取/检查的候选永久加入 exposure ledger；
3. 它们**不得在下一 epoch 继续充当 holdout**；
4. 可以把这些对象转为 design corpus；
5. 生成新的 scope version / SHA；
6. 必须再采集一批 scope 冻结后才抽取的 fresh holdout。

禁止在同一 epoch 看完 holdout 后直接修改 scope 再用同一批 holdout 重新验收。

## 四、多 subagent 职责分离

执行时至少使用以下逻辑角色。可以是独立 subagent、独立进程或等价隔离 harness，但产物职责必须分开，不能只靠聊天叙述。

| 角色 | 职责 | 明确禁止 |
| --- | --- | --- |
| A0 Orchestrator / Ledger | 阶段机、预算、文件 SHA、epoch 状态、失败保留 | 不直接判定化学证据资格 |
| A1 C Source Scout | C scope/build 与 fresh holdout 发现 | 不自行把来源标 evidence_eligible |
| A2 SS Source Scout | SS scope/build 与 fresh holdout 发现 | 同上 |
| A3 Source Identity Verifier | PMCID/DOI/title/journal/year/volume/pages/出版方一致性 | 不依据 scout 描述直接通过 |
| A4 Structure Extractor-1 | 独立抽取 reactant/product/site/stereo/evidence pointer | 不看 A5 最终结构 |
| A5 Structure Extractor-2 | 第二次独立抽取与编码 | 不看 A4 最终结构 |
| A6 Reconciliation & Closure Auditor | 对 A4/A5 差异裁定；构建 exposure/source/reaction closure 图 | 不构建 scope、不选模型赢家 |
| A7 Scope Builder | 只从 design/build corpus 建 exact→scope、guard、边界 | 不读取 A/B/E 输出；scope freeze 后不可原地改 |
| A8 Red-team Preflight | 检查泄漏、过度泛化、负控、schema、holdout 新鲜度 | 不修改 scope 或 panel 来“修过” |
| A9 Runtime Engineer | 将合格 scope bank 接入新 runtime 版本 | 不更改模型/PUCT/scoring/stock |
| A10 Experiment Runner | 只消费冻结 experiment contract 执行 A/B/E | 无权改来源、结构、scope、panel、参数 |
| A11 Independent Verifier | 从原始 cells 重算指标、预算、reference loss、node trace | 不采用 runner 汇总值作为唯一事实 |
| A12 Report Auditor | 对 REPORT/STATE/roadmap 用词做证据边界复核 | 不升格 human_reviewed / independent chemistry |

### 4.1 subagent 输出要求

每个角色必须输出机器可检查的 JSON/JSONL/manifest，至少包含：

- `agent_role`；
- 输入 manifest SHA；
- 输出文件 SHA；
- source/evidence pointers；
- 处理数量、通过/拒绝/待定差额；
- 错误与未处理列表；
- 是否读取过 holdout / model outcome；
- 时间戳与 task/epoch ID。

**任何 subagent 的自然语言断言本身不构成来源证据。**

## 五、P7 状态机与 harness

P7 主控必须实现显式阶段锁；建议入口 `scripts/task016_p7_orchestrate.py`，状态至少为：

```text
G0_BASELINE
G1_EXPOSURE_LEDGER
G2_DESIGN_ACQUIRE
G3_SCOPE_BUILD
G4_SCOPE_FREEZE
G5_FRESH_HOLDOUT_ACQUIRE
G6_IDENTITY_STRUCTURE_ADMIT
G7_CLOSURE_PANEL_FREEZE
G8_STATIC_PREFLIGHT
G9_RUNTIME_FREEZE
G10_ABE_RUN
G11_LEGACY_REGRESSION
G12_INDEPENDENT_VERIFY
G13_REPORT
```

任何下游阶段只能读取前一阶段 immutable manifest。阶段间输入 SHA 不匹配必须 fail closed。

### 5.1 必须新增的 harness

至少交付：

- `task016_p7_orchestrate.py`：状态机、epoch、预算与阶段锁；
- `task016_p7_source_harness.py`：查询计划/执行守恒、来源下载与 disposition；
- `task016_p7_identity_harness.py`：出版身份核验；
- `task016_p7_structure_harness.py`：双抽取、结构一致性、reference precursor 完整性；
- `task016_p7_closure_harness.py`：历史 exposure、source/reaction closure、零泄漏；
- `task016_p7_scope_harness.py`：exact→scope、build replay、boundary、冻结；
- `task016_p7_panel_harness.py`：fresh holdout、runtime completeness、scope applicability；
- `task016_p7_experiment_harness.py`：A/B/E cell contract、账本、trace；
- `task016_p7_verify.py`：独立重算最终验收，不启动新科学搜索。

脚本名可以调整，但职责不得合并到一个不可审计的大脚本中。

## 六、来源发现与循环策略

### 6.1 Design acquisition loop

C 与 SS 分开循环。设计语料可以使用：

- P1–P6 已暴露合格来源；
- P6 未完成但可继续核验的来源线索；
- 新公开 API / PMC / publisher / Crossref / Rhea / PubChem / ORD / 合法可程序化开放来源；
- citation chase、作者/酶名/产物名/连接位点反向检索。

Design loop 的目的不是凑 holdout，而是建立**有真实来源支持的 scope bank**。

### 6.2 Fresh holdout acquisition loop

只有 scope bank freeze 后才启动。

每一轮搜索必须先写 `query_plan.json` 再执行，至少记录：

- 预注册 query；
- 预期数据库/API；
- scope_id / family；
- 查询原因；
- 最大页数/对象数；
- 执行状态；
- 返回条数；
- 去重条数；
- 待核身份条数；
- admitted/deferred/rejected 数；
- 新 closure group 数。

至少使用 3 类不同 discovery route，不能只换关键词重复同一路线。

### 6.3 饱和判定

不得因“一轮没找到”就宣布来源不足。只有满足以下之一才可停止来源循环：

1. C 与 SS 都已达到可执行实验面板；
2. 达到来源硬预算；
3. 至少 3 种 discovery route 已执行，且连续 2 个完整 round 对该家族都没有新增任何 `structure_complete + runtime_executable + leakage_free + scope_applicable` closure group；
4. 合法来源受许可/访问限制阻断，继续需要绕过登录、付费或访问控制。

如果因 2–4 停止但面板不足，任务必须 Partial/Blocked，不得降低门槛。

### 6.4 来源预算

独立于 P1–P6 计账，初始硬上限：

| 项 | 上限 |
| --- | ---: |
| 可观测 HTTP 请求 | 8,000 |
| 新下载字节 | 8 GiB |
| article versions | 400 |
| attachments / supplementary objects | 800 |
| 单 URL 尝试 | 最多 2 次；明确恢复链可另记 1 次 |
| 并发采集 | 最多 4 |

内部不可观测的外部搜索工具传输不能伪装进 HTTP 精确账本。

## 七、来源真实性与结构准入硬门

### 7.1 来源身份

在任何内容进入 evidence-eligible 前，A3 必须核：

```text
PMCID / PMID（如有）
DOI
title
journal
publication year / volume / pages or article number
publisher / PMC authoritative metadata
```

允许字段缺失，但已有字段必须相互一致；冲突必须显式 unresolved。

`HTTP 200`、搜索摘要、subagent 叙述、文件名均不能单独证明来源身份。

### 7.2 原件

- 原件保存不可变 bytes + SHA；
- 许可与再分发状态逐件登记；
- 失败响应保留；
- metadata-only 不能升级为 reaction evidence；
- source identity 与 chemical claim evidence 分开登记。

### 7.3 双结构抽取

所有进入 build 或 holdout 的反应必须由 A4/A5 独立抽取：

- acceptor；
- donor；
- product；
- 成键原子与位点；
- sugar identity；
- anomer/stereo（来源未定则不得猜）；
- reaction direction；
- 单步/多步；
- evidence location（段落/表/图/SI 页）；
- structure origin。

二者 canonicalized graph / atom identity / stereo 不一致时进入 reconciliation，不得自动取任一方。

### 7.4 禁止手写猜复杂结构

复杂天然产物、糖链、保护基、立体中心不得依据名称、记忆或“看起来合理”手写成 structure_complete。

允许的结构来源：

- 原文机器可读结构；
- 官方 supplementary machine-readable structure；
- 权威结构数据库且 identity chain 明确；
- 原文图形结构经双独立转写 + graph/formula/mass/命名一致性核对。

无法可靠编码则标 deferred，不得进入 runtime panel。

## 八、Exposure / closure / split 规则

P7 必须生成项目级 `exposure_ledger.jsonl`，覆盖 TASK-016 主任务至 P6 的：

- build supports；
- exact template supports；
- scope supports；
- boundary examples；
- panel targets；
- probe targets；
- A/B/D/E 运行 targets；
- 被人工/agent 化学结构级检查过的来源。

至少构建以下闭包边：

- exact covalent reaction signature；
- same acceptor+donor+site/product signature；
- same experimental cohort / source assay；
- same source article when reactions共享结构设计信息；
- historical design exposure；
- explicit template/scope support relation。

P7 transfer holdout 与 build/design corpus 必须：

```text
reaction leakage = 0
source/assay closure leakage = 0
exact runtime instance leakage = 0
scope design leakage = 0
```

A6 独立冻结 split；A7 无权改 split。

## 九、Scope bank 构建规则

P7 不假定只存在一个 C8 scope 或一个 SS O2 scope。允许建立多个来源合格 scope，但每个 scope 必须独立满足：

1. 至少 2 个不同 canonical acceptor build supports；
2. build supports 100% exact replay；
3. exact instance template 与 scoped template 分离保存；
4. 明确 acceptor core、donor、位点、stereo 和允许泛化边界；
5. 至少 6 个预登记 boundary controls；
6. boundary violations = 0；
7. runtime guard 能在正式路径重放所有 build supports；
8. scope SHA 在任何 fresh holdout 化学抽取与 applicability 之前冻结。

C scope 可以覆盖例如 flavonol C8、flavone C6、benzophenone C3、gallic-acid C2 等不同 strata，但**每个 stratum 必须由自身来源 build supports 建立，不能因为旧 holdout 存在而直接手写 scope**。

SS scope 同理，1→2、1→6、O2 等不同连接/受体上下文必须分 scope，不得用一个过宽规则合并。

### 9.1 scope 版本与 epoch

命名建议：

```text
C-E01-scope-bank-v1
C-E02-scope-bank-v2
SS-E01-scope-bank-v1
...
```

一旦 scope freeze 后需要修改：

- 当前 epoch 的 holdout 全部永久 exposed；
- 当前 epoch 后续结果 superseded；
- 新开 epoch；
- 新 holdout 必须重新采集。

## 十、Fresh panel 最低门与缓冲目标

为了避免再次“刚好 6 个，复核掉 1 个就全盘停止”，执行目标分两层：

### 10.1 运营缓冲目标

进入正式 panel freeze 前，优先争取每类：

```text
>=8 runtime-complete targets
>=3 closure groups
```

### 10.2 不可降低的 Completion floor

若来源客观不足，允许按以下最低线冻结，但不得更低：

```text
C:  >=6 targets, >=2 closure groups
SS: >=6 targets, >=2 closure groups
```

每个进入分母的 target 必须：

- runtime_complete=true；
- source_identity_verified=true；
- structure_complete=true；
- reference_precursor_complete=true；
- leakage=false；
- exact_seed_instance_match=false；
- 至少适用于一个已冻结 scope；
- `scope_applicability=true` 必须在不改 scope 的静态 preflight 中产生完整 reference precursor。

**P6 的“完整但 0/6 scope-applicable”情况在 P7 不再允许进入实验 panel。**

## 十一、冻结运行时：v7

若存在至少一个 P7 合格 scope，则建立显式、默认关闭的新版本，建议：

```text
v7 =
    frozen P6 v6 baseline
    + P7-qualified C scopes
    + P7-qualified SS scopes
```

要求：

- `default_enabled=false`；
- 缺 payload fail closed；
- manifest/SHA 漂移 fail closed；
- checkout config 与 packaged config 字节一致；
- P7 holdout 不进入 runtime instances；
- exact / scope artifact 明确区分；
- P1–P6 的历史加载行为不静默改变；
- 模型、PUCT、通用 scoring、stock17、reviewed-resource binding 不改；
- generic top candidate 保护逻辑不按 P7 成绩调参。

## 十二、正式 development A/B/E

### 12.1 Arm

冻结：

```text
A = optimized generic search，所有 TASK-016 domain library off
B = frozen P6 v6
E = P7 v7
```

这样同时回答：

- 相对纯 generic 是否有增益；
- 相对当前最强 TASK-016/P6 基线是否有增益。

### 12.2 固定种子

```text
0, 1, 2
```

### 12.3 运行数量

每类 panel N 为 6–9 时：

```text
N × 3 seeds × 3 arms
```

两类最小 108 cells，最大 162 cells。

进入正式矩阵前必须冻结：

- panel manifest；
- scope bank SHA；
- runtime manifest SHA；
- code SHA；
- model hashes；
- review/resource binding；
- stock keys；
- all search parameters；
- budget；
- metrics definition。

## 十三、迁移指标与完成硬门

对每个 family 独立定义：

- `N`：冻结 P7 fresh、runtime-complete、scope-applicable holdout 数；
- `N_gap`：A 与 B 均正常完成且均未保留完整主 reference 的不同 target 数；
- `G`：`N_gap` 中 E 正常保留完整主 reference，且动作来自 P7-qualified scope、非 exact replay 的不同 target 数。

### 13.1 候选迁移

C 和 SS **分别**必须满足：

```text
N >= 6
closure_groups >= 2
G >= 3
G / N_gap >= 50%   （N_gap=0 时为 null，不能写 100%）
successful_transfer_groups >= 2
net complete-reference coverage vs A > 0
net complete-reference coverage vs B > 0
reference_loss = 0
```

### 13.2 真实 node transfer

每类至少 3 个不同 target、覆盖至少 2 个 closure groups，同时满足：

- A seed0/1/2 全部正常；
- B seed0/1/2 全部正常；
- A/B 三 seed 都没有创建完整 reference action/node；
- E seed0/1/2 全部正常；
- E 三 seed 全部实际创建完整 reference action/node；
- action 来源于 P7 scope；
- `exact_seed_instance_match=false`；
- 逐 cell trace 可重算。

只在 candidate list 出现而没有进入真实树节点，不计成功。

### 13.3 候选挤出与副作用

必须报告：

- generated / truncated / filtered / created 各层动作数；
- generic top-3 protection 违反数，要求 0；
- E 相比 A/B 新增与减少的独立动作；
- 被挤出的非 reference 动作逐项可追溯；
- 不把未知非 reference 动作价值擅自解释为收益或损失。

## 十四、旧能力与 O 轴保护

P7 不重新证明 O 化学泛化，但最终 v7 必须保护已有 TASK-016 能力。

至少执行：

1. P6 冻结旧 17 targets × 3 seed × E = 51 个真实回归 cell；
2. TASK-016 主任务的 4 个 O exact canary；
3. P1 冻结的历史成功迁移 canary manifest（按冻结 ID 重放，不按报告文字手工重造）。

要求：

```text
new reference loss = 0
historical successful behavior preserved
v3/v6 decisive fingerprints unchanged
stock keys unchanged
reviewed-resource binding unchanged
```

如果 C/SS scope 在首次回归后又有科学资产变化，受影响的完整回归必须重新执行，旧运行保留并标 superseded。

## 十五、运行预算

P7 使用全新独立账本。

| 用途 | 上限 |
| --- | ---: |
| C A/B/E（最多 9 targets） | 81 |
| SS A/B/E（最多 9 targets） | 81 |
| 初次正式两轴矩阵 | 162 |
| 最终 legacy / historical canary | 90 |
| runtime/package/engineering 真实探针 | 60 |
| 一次完整受影响矩阵重验 | 252 |
| **P7 总硬上限** | **600** |

纯结构检查、source parsing、template replay、scope applicability 静态 probe 不计真实 MCTS。

### 15.1 实现 bug 后的重跑纪律

如果冻结矩阵执行后发现实现 bug：

- 所有已执行 cell 保留；
- 标记 `superseded_due_to_implementation_bug`；
- 不允许只重跑失败 cell；
- 必须重跑完整受影响矩阵；
- 预算不足则任务 Partial，不得提高上限而不重新批准。

## 十六、必须新增的永久自动测试

在 P6 永久回归基础上，至少新增：

```text
test_p7_historical_exposure_cannot_enter_fresh_holdout
test_p7_scope_frozen_before_fresh_holdout_extraction
test_p7_epoch_mutation_invalidates_prior_holdout
test_p7_prior_epoch_holdout_becomes_exposed
test_p7_query_plan_and_execution_counts_conserve
test_p7_missing_schema_field_cannot_default_to_zero
test_p7_agent_source_hint_is_not_evidence
test_p7_source_metadata_identity_must_match
test_p7_dual_structure_extractors_must_reconcile
test_p7_handwritten_complex_structure_rejected
test_p7_build_and_holdout_have_zero_reaction_leakage
test_p7_build_and_holdout_have_zero_source_closure_leakage
test_p7_holdout_not_in_runtime_instances
test_p7_scope_bank_replays_all_build_supports
test_p7_scope_has_minimum_boundary_controls
test_p7_scope_applicability_required_for_panel
test_p7_c_and_ss_epochs_are_independent
test_p7_family_failure_does_not_block_other_family
test_p7_runner_cannot_modify_frozen_contract
test_p7_exact_replay_not_counted_as_transfer
test_p7_node_transfer_requires_real_tree_trace
test_p7_metrics_recomputed_from_raw_cells
test_p7_v7_default_off
test_p7_v7_manifest_drift_fails_closed
test_p7_v6_behavior_unchanged
test_p7_generic_top3_protection
```

P6 的以下保护继续永久存在：

```text
test_scope_pipeline_calls_scoped_smarts
test_scope_fires_all_declared_build_supports
test_second_build_support_is_scope_canary
```

## 十七、独立验证 harness 必须检查的守恒量

最终 `task016_p7_verify.py` 至少检查：

- query plan = executed + explicitly skipped；
- discovered = admitted + deferred + rejected + metadata_only；
- downloaded bytes/files 与 raw manifest 一致；
- source identity eligible 数与 verifier 输出一致；
- structure extraction 双轨差额全部关闭；
- build/holdout graph 零泄漏；
- scope build replay 100%；
- boundary violations 0；
- panel N/group/applicability 与 manifest 一致；
- runtime templates/instances 与 config/manifest SHA 一致；
- A/B/E cells 计划数 = started = terminal states；
- real MCTS 与 synthetic fixture 分开；
- metrics 能从 raw cells 独立重算；
- run budget 未超；
- historical protected files 无无法解释漂移；
- raw/restricted assets 不进 Git/package；
- REPORT 数字与最终 manifests 一致。

## 十八、停止条件

### 18.1 某 family 的 epoch 停止

- scope build support replay <100%；
- boundary 有无法解释误命中；
- fresh panel <6 targets 或 <2 groups；
- panel 中存在 leakage；
- runtime completeness <100%；
- scope applicability <6 或 <2 groups；
- 需要看 A/B/E 结果后才能调整 scope/panel；
- 来源饱和条件已满足但仍无法形成 panel。

该 family 可以进入下一 epoch；旧 holdout 变为 exposed。另一 family 不受阻塞。

### 18.2 全局立即停止并报告

- protected historical payload 出现无法解释漂移；
- 需要降低科学门槛；
- 需要改变模型/PUCT/scoring/stock 来制造增益；
- 需要把 historical/exposed target 当 fresh holdout；
- 需要伪造/猜测结构或来源；
- 来源身份无法验证却必须依赖它才能达标；
- 超过来源或搜索硬预算；
- 需要绕过登录、付费、验证码或访问控制；
- 结果出现后重新定义 reference 成功条件；
- subagent/harness 的阶段隔离无法保证；
- 发现面板污染且预算不足以开启全新 epoch。

## 十九、总体验收清单

### Governance / provenance

- [ ] 实际工作区 baseline + protected SHA 冻结。
- [ ] P1–P6 historical exposure ledger 完整。
- [ ] subagent 角色与输入/输出 manifest 可审计。
- [ ] 所有 query 有 plan/execution 守恒。
- [ ] 所有 evidence-eligible 来源通过 authoritative metadata identity。
- [ ] build/holdout 结构均双抽取或有等价独立核对。
- [ ] 复杂结构无手写猜测准入。

### C

- [ ] C scope bank 全部 build replay 100%。
- [ ] 每个 C scope boundary controls >=6 且 0 违反。
- [ ] C fresh holdout >=6 targets / >=2 groups。
- [ ] C holdout 100% runtime-complete。
- [ ] C holdout 100% scope-applicable。
- [ ] C reaction/source/design leakage=0。
- [ ] C A/B/E 全矩阵实际执行。
- [ ] C G>=3。
- [ ] C G/N_gap>=50%。
- [ ] C successful groups>=2。
- [ ] C net coverage vs A >0 且 vs B >0。
- [ ] C reference loss=0。
- [ ] C 至少3 targets /2 groups 满足真实三-seed node transfer。

### SS

- [ ] SS scope bank 全部 build replay 100%。
- [ ] 每个 SS scope boundary controls >=6 且 0 违反。
- [ ] SS fresh holdout >=6 targets / >=2 groups。
- [ ] SS holdout 100% runtime-complete。
- [ ] SS holdout 100% scope-applicable。
- [ ] SS reaction/source/design leakage=0。
- [ ] SS A/B/E 全矩阵实际执行。
- [ ] SS G>=3。
- [ ] SS G/N_gap>=50%。
- [ ] SS successful groups>=2。
- [ ] SS net coverage vs A >0 且 vs B >0。
- [ ] SS reference loss=0。
- [ ] SS 至少3 targets /2 groups 满足真实三-seed node transfer。

### Runtime / regression / delivery

- [ ] v7 default-off / missing asset fail-closed / SHA drift fail-closed。
- [ ] holdout 不进入 runtime instances。
- [ ] A/B/E runner 无权修改冻结合同。
- [ ] 最终旧17×3真实回归无新增 reference loss。
- [ ] TASK-016/P1 历史 canary 保持。
- [ ] 全量本地测试通过。
- [ ] 无资产 suite 仅明确资产项 skip，其他 0 failure/error。
- [ ] wheel/sdist 不含 raw/outputs/restricted payload。
- [ ] 仓库外安装能执行 default、v6、v7 的合法路径及缺资产失败路径。
- [ ] P7 搜索总账 <=600。
- [ ] protected files 0 unexplained drift。
- [ ] `git diff --check` 通过。
- [ ] REPORT / STATE / docs navigation / roadmap 与最终事实一致。
- [ ] actionable/evidence_closed/prediction_conditions_verified 不因本任务自动升格。
- [ ] formal_run_ready/release_ready 不因 development transfer 自动变 true。

### 总体完成门

- [ ] **C_transfer=Completed 且 SS_transfer=Completed。**
- [ ] **engineering_delivery=Completed。**
- [ ] **legacy_regression=Completed。**
- [ ] **independent verification=Completed。**
- [ ] **Roadmap P2 development effect 可据冻结事实标记完成。**

任何一项未满足，整体不得写 Completed。

## 二十、推荐执行循环

```text
G0 baseline / exposure ledger / protection
 |
 +--> C design loop -----------------------------+
 |     acquire -> verify -> dual extract          |
 |     -> closure -> build supports               |
 |     -> scope build/boundary -> FREEZE          |
 |                                                |
 |     fresh holdout acquisition AFTER freeze     |
 |     -> verify -> dual extract -> closure        |
 |     -> panel -> applicability                  |
 |          |                                     |
 |          +-- insufficient --> expose epoch ----+--> next C epoch
 |          |
 |          +-- pass --> freeze C experiment contract
 |
 +--> SS design loop ----------------------------+
       same independent epoch logic
       -> pass --> freeze SS experiment contract

C ready? run C A/B/E immediately
SS ready? run SS A/B/E immediately
(one family never blocks the other)

        ↓
freeze final v7
        ↓
legacy + historical canary regression
        ↓
independent metric recomputation
        ↓
package / no-asset / protected SHA / budget audit
        ↓
REPORT / STATE / roadmap closeout
```

## 二十一、计划文件与产物

| 层 | 计划产物 |
| --- | --- |
| governance | `approval.json`, `execution_baseline.json`, `protected_hashes.json`, `exposure_ledger.jsonl` |
| orchestrator | `epoch_ledger.jsonl`, `stage_manifest.json`, `budget.json` |
| discovery | per-family `query_plan.jsonl`, `query_execution.jsonl`, `source_dispositions.jsonl` |
| source identity | `source_identity_verification.jsonl`, raw file manifest |
| structure | extractor-A/B JSONL, reconciliation, runtime-completeness |
| closure | `closure_edges.jsonl`, `split_manifest.json`, leakage audit |
| scopes | per-epoch exact/scope templates, scope manifest, build replay, boundaries |
| panels | per-epoch fresh panel, heldout references, applicability, preflight |
| runtime | `glycoside-library-v7.json`, runtime template/instance/source manifests |
| runs | C/SS independent experiment contracts, run ledgers, raw cell traces |
| metrics | raw-derived family metrics, node-transfer summary, candidate accounting |
| regression | old17×3 + historical TASK-016/P1 canary results |
| verification | replay, no-asset, package, independent audit, delivery manifest |
| docs | REPORT-016-P7、STATE、ARCHITECTURE/导航/roadmap必要更新 |

建议代码范围：

- 新增 `flavoretro/glycoside_library_v7.py` 或等价最小模块；
- 复用 `glycoside_scope.py`，只有被新合同测试证明需要时才做最小修改；
- 新增 `configs/glycoside-library-v7.json` 与包副本；
- 新增 `scripts/task016_p7_*.py` harness；
- 新增 `tests/test_task016_p7.py`；
- contracts/cli/worker/service/workspace/task016_runs 仅做 v7 显式接线与预算治理所需最小修改；
- 不改 web，除非执行阶段另获明确授权。

## 二十二、必须提交的 REPORT

无论 Completed、Partial、Blocked 或 Failed，都必须生成：

`docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md`

REPORT 必须直接回答：

1. P7 一共运行了几个 C epoch、几个 SS epoch？每个为何通过/失效？
2. P1–P6 哪些对象被列为 historical development exposure？
3. 最终 C/SS scope bank 各有多少 scope、每个有哪些 build supports 与边界？
4. fresh holdout 是否都在 scope freeze 后才完成化学抽取？
5. 是否有旧 epoch holdout 被下一 epoch 重用为 holdout？
6. 来源身份验证失败/错误引用多少，如何隔离？
7. 双结构抽取分歧多少，哪些 deferred？
8. 最终 C panel 的 N/groups/applicability/leakage 是多少？
9. 最终 SS panel 的 N/groups/applicability/leakage 是多少？
10. A/B/E 实际各执行多少 cells、多少真实 MCTS、多少 fixture？
11. C 的 N_gap、G、G/N_gap、net coverage、reference loss、node-transfer 成功数是多少？
12. SS 的同组指标是多少？
13. 成功是否覆盖至少2 closure groups？
14. E 是否挤出 generic 动作？top-3保护是否0违反？
15. 是否有任何 scope/panel 在看到 A/B/E 后改变？
16. 实现 bug 后是否完整重跑受影响矩阵？
17. 最终 v7 是否通过旧17×3及历史 TASK-016/P1 canary？
18. 最终 source/search budget 实际使用多少？
19. Roadmap P2 的 development effect 是否可以标记完成？依据是什么？
20. 哪些更高科学门仍保持未关闭？

## 二十三、允许的最终结论

只有全部总体验收通过，允许写：

> 在 TASK-016-P7 预先冻结的来源合格 scope 与随后建立、无 build/design 泄漏的开发留出上，C-glycosylation 与 sugar–sugar glycosylation 领域策略均相对 generic 与 P6 v6 基线产生可审计的新增参考候选，并在三个固定 seed 的真实 MCTS 中稳定创建完整参考动作；既有 TASK-016 能力无新增参考损失。因此 WORKBENCH_ROADMAP 的 P2“黄酮苷领域搜索扩展”在 development evidence 层完成。

即使 P7 完全通过，也**不得**写：

- 已证明真实未知化学预测准确率；
- 已证明训练集独立泛化；
- 已完成正式 blind benchmark；
- 已产生 independent chemical labels；
- 已证明实验可行性或产率；
- 已完成供应商可购认证；
- 已 production-ready / release-ready；
- agent 双审等于 human_reviewed。

这些属于 TASK-017 或更高科学准入。

## 二十四、非目标与禁止项

本任务不：

- 训练或微调神经模型；
- 修改通用 PUCT、scoring 或库存来追 P7 成绩；
- 用 exact instance template 冒充 scope；
- 用旧 P1–P6 panel 冒充 fresh P7 transfer holdout；
- 看 holdout 或 A/B/E 后在同一 epoch 调 scope；
- 根据名称/记忆手写复杂结构进入准入；
- 把 subagent 返回的 DOI/PMCID 当作权威来源；
- 绕过付费、登录、验证码或访问控制；
- 做湿实验；
- 做当前供应商认证；
- 启动 TASK-017/018；
- 修改历史 TASK/REPORT 隐藏失败；
- 删除 superseded/failed 产物来让结果“干净”；
- 因任务已经迭代到 P7 而降低 6 targets / 2 groups / 3 transfer / 50% 等硬门；
- Git commit/push/tag/release，除非所有者另行明确授权。

## 二十五、批准前检查

执行批准前，主控必须先向所有者明确：

- 本任务是 **development transfer closure**，不是正式 blind；
- 预计需要多轮公开来源采集与多个 subagent；
- 搜索硬上限 600，来源硬预算见第六节；
- 如果公开来源不足，结果仍可能是 Partial，但不能通过降低门槛改成 Completed；
- 当前工作区大量未提交文件会以 SHA manifest 保护，不要求先清理或提交。

## 二十六、修订记录

- 2026-10-07 v0.1：按所有者本会话要求起草。相对 P6 的核心改变是：不再复用反复观察的旧 holdout 继续追 scope，而采用“scope-first → freeze → fresh-holdout → epoch”的开发实验设计；新增职责隔离 subagent、双结构抽取、来源身份 verifier、project-wide exposure/closure harness、独立 metric recomputation 与 A/B/E runner 权限隔离。总体 Completed 必须同时关闭 C 与 SS transfer，并把 WORKBENCH_ROADMAP P2 的 development effect 真正闭环；TASK-017 formal blind 仍保持独立。
