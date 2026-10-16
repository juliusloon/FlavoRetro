# TASK-016-P6：C scope 修复、可执行留出与 C/SS 迁移终验

## 合同元数据

- 任务 ID：TASK-016-P6；合同版本：v0.1；起草日期：2026-10-07。
- 状态：**Proposed（拟议）**。本轮仅按所有者“具体起草成一份 task”及“已经恢复在线了，写进文件”的指示落盘合同与导航；**尚未授权执行新的来源采集、结构编码、代码修改、v6 接线、真实 MCTS、Git commit/push**。
- 起草授权：human_direct，仅覆盖本合同落盘与治理登记。
- 执行授权：待所有者后续明确批准。执行开始前必须登记批准语句、日期、本合同 SHA-256、实际工作区基线与预算；agent 执行不得记为 human_reviewed。
- 人工负责人：项目所有者。
- 执行者：待批准后登记。
- 工作区：`/home/ljx/FlavoRetro`。
- 前序合同：[TASK-016-P5](TASK-016-P5-c-ss-transfer-capability-closure.md)。
- 前序报告：[REPORT-016-P5](../reports/REPORT-016-P5-c-ss-transfer-capability-closure.md)。
- 前序纠错标识：`P5-ERR-06`。
- 计划本地科学产物根：`outputs/task016-p6/v1/`；计划新原件根：`data/raw/task016-p6/`。
- 所有项目内命令与写入继续经 `scripts/operate.py` 登记。
- P1–P5 历史 TASK、REPORT、冻结载荷和 superseded 结果保持历史原貌；P6 只能通过新的 reconciliation / supersession 记录说明哪些旧判断不再成立。

## 一、任务目标

TASK-016-P6 的目标不是继续扩大反应数量，而是修复 P5 暴露出的最后一层实验构造问题，并第一次对 C 与糖间（SS）新底物迁移执行有效、可审计的 A/B/E 实验。

P6 必须完成以下闭环：

1. 正式纠正 `P5-ERR-06`：P5 所谓“C scope 对 7 个 holdout 均不可达”的结构层结论无效，因为当时测试的是 `derive_template_smarts` 产生的精确实例模板，而不是经过 `scoped_smarts` 转换后的 scope。
2. 重建并冻结一个真正的 C scope：该 scope 必须首先独立覆盖其全部声明 build supports，并通过预登记边界控制。
3. 将 C frozen panel 从“计数通过”提升为“runtime-executable 通过”：每个进入分母的目标必须具有完整、来源可追溯、可由运行时读取的结构和 reference precursor。
4. C 与 SS 分轴运行：只要 C 自身前置门通过，即使 SS 仍为 4/6，C 也必须独立进入 A/B/E；不得再用 SS 的停止条件阻塞 C。
5. 定向解除 SS 的 build/holdout closure 冲突，使 SS 达到 ≥6 个可执行 holdout。
6. 在冻结 v6 上对 C、SS 分别证明或否定新底物迁移，并执行旧能力回归。
7. 任何失败都必须区分 scope implementation failure、panel/runtime incompleteness、scope/holdout domain mismatch 与 model/search transfer failure；禁止再把工程对象未构造完成误写成模型或化学泛化失败。

## 二、P5 后续复核后的权威起点

### 2.1 P5-ERR-06：撤销的结论

P5 初稿曾给出“合格 C scope 对全部无泄漏 C holdout 不可达，因此 C 迁移结构性不可测”。

后续复核发现当时探针实际只调用：

```text
derive_template_smarts(instance)
```

所得模板保留精确产物的大量原子级字面约束；P3 的完整流水线还包含第二步：

```text
derive_template_smarts(instance)
    ↓
scoped_smarts(...)
```

P5 漏掉了 `scoped_smarts`。

旧探针重跑结果：

| 测试底物 | 旧“scope”探针 fires |
| --- | ---: |
| kaempferol 8-C-glc，第一 build support | 2 |
| quercetin 8-C-glc，第二 build support | 0 |
| isorhamnetin / tamarixetin / myricetin 8-C-glc | 0 |

连声明中的第二个 build support 都无法命中，足以证明该对象不是合格 scope。

因此以下 P5 判断由 P6 明确 supersede：

- “C scope 已正确构建”；
- “C scope 已被结构探针证明不泛化”；
- “C A/B/E 因 scope/holdout 化学结构性不相交而无需执行”。

正确状态为：

> **P5 没有成功建立经过完整 scope 流水线验证的 C scope，因此没有证据判断 C scope 是否能迁移。**

### 2.2 P5 中仍有效的事实

以下事实不因 `P5-ERR-06` 自动失效：

- P4 reconciliation 已完成；
- P4 保护基线未发现未经解释漂移；
- C 冻结计数面板达到 7 targets / 5 closure groups；
- P5 新准入 2 条 structure-complete C reaction；
- SS 当前在去除 build closure leakage 后为 4/6；
- SS 未运行 A/B/E 符合停止条件；
- P5 A/B/E 实际执行次数为 0，搜索尝试 0/480；
- 151 项既有测试当时通过；
- P5 中发现并隔离的错误 PMC 记录、未经来源支持的手写结构等不得恢复资格。

### 2.3 P6 必须重新确认而不能直接继承的事实

以下项目必须由 P6 重新验证：

1. C 的 7 个 holdout 是否全部具有 runtime 可执行的完整 product structure；
2. 每个 C holdout 是否有完整 frozen reference precursor；
3. 两个 C build supports 是否经过真正 `scoped_smarts` 后均能 replay；
4. C scope 的边界是否不会过度泛化；
5. 正确冻结后的 C scope 对多少 holdout 在纯结构层可适用；
6. v6 runtime guard 是否真正支持该 C scope；
7. SS 4/6 是否仍是当前 closure 重算后的真实数量。

## 三、分轴完成定义

P6 最终必须分别报告以下八轴：

| 轴 | Completed 的最低条件 |
| --- | --- |
| p5_err06_reconciliation | 旧探针、漏调用根因、superseded 判断及正确调用链全部可重现 |
| C_scope_implementation | C scope 经完整流水线建立；全部 build supports replay 100%；boundary violations=0 |
| C_runtime_panel | C ≥6 个 complete、runtime-executable holdout，≥2 closure groups，zero leakage |
| C_transfer | C A/B/E 候选迁移与真实三-seed node transfer 均通过硬门 |
| SS_runtime_panel | SS ≥6 个 complete、runtime-executable holdout，≥2 closure groups，zero leakage |
| SS_transfer | SS A/B/E 候选迁移与真实三-seed node transfer 均通过硬门 |
| legacy_regression | 最终 v6 上旧 17 targets ×3 seeds 回归无新增参照损失 |
| engineering_delivery | v6/default-off/fail-closed/package/tests/replay/protection/accounting/report 全部通过 |

**整体 Completed 仅在八轴全部 Completed 时成立。**

必须允许分轴推进：

- SS 面板不足不得阻塞 C；
- C 失败不得阻塞合法的 SS 实验；
- 某轴未满足运行前门槛时，该轴迁移指标保持 `null`；
- 已满足运行前门槛的另一轴必须继续执行，不能因为总体最终仍会是 Partial 而提前停止。

## 四、核心实现原则

### 4.1 exact template 与 scope 必须成为不同的一等对象

P6 必须显式保存：

```text
exact_instance_template
scope_template
scope_transformation
scope_definition
scope_build_supports
scope_boundary_controls
```

不得继续用同一 `template_smarts` 字段让 exact 与 scope 语义混在一起。

至少记录：

- exact template SHA；
- scoped template SHA；
- scope transformation 参数；
- acceptor core；
- donor 约束；
- 反应中心；
- 位点；
- 立体边界；
- 允许/禁止的邻域泛化；
- build support IDs。

### 4.2 build validation 必须先于 holdout probe

固定顺序：

```text
source-qualified build supports
        ↓
derive exact template
        ↓
scope transformation
        ↓
build support replay
        ↓
negative/boundary controls
        ↓
freeze scope + SHA
        ↓
freeze executable holdout panel
        ↓
holdout applicability probe
        ↓
runtime v6
        ↓
A/B/E
```

禁止先看 holdout 结果再修改 `scoped_smarts`、acceptor core 或边界。scope 一旦开始第一次 holdout probe，其定义和 SHA 即冻结。任何后续修改都必须产生新 scope version，并使此前 probe / A/B/E 全部 superseded。

### 4.3 C 与 SS 门槛独立

代码和报告必须分别实现 `C_preflight` 与 `SS_preflight`。不得存在“任一类失败则 stop_all”的逻辑。

要求：

```text
if C_pass:
    run C
else:
    C metrics = null

if SS_pass:
    run SS
else:
    SS metrics = null
```

## 五、G0：P5-ERR-06 reconciliation 与保护基线

P6 执行第一阶段禁止联网、禁止新 MCTS。

必须完成：

1. 冻结实际 Git/代码/配置/环境/模型/reviewed-resource/17 stock keys 状态；
2. 校验 P5 关键载荷 SHA；
3. 复现旧错误探针；
4. 证明旧 probe 输入模板来自 exact `derive_template_smarts`；
5. 找出 P3 中 `scoped_smarts` 的真实调用点、参数和上下文；
6. 生成至少：

```text
outputs/task016-p6/v1/p5_err06_reconciliation.json
outputs/task016-p6/v1/p5_err06_old_probe_replay.json
outputs/task016-p6/v1/p3_scope_pipeline_trace.json
```

其中至少记录：

```text
old_claim
old_template_kind
missing_pipeline_step
build_support_1_result
build_support_2_result
old_verdict_valid=false
superseded_by=P5-ERR-06
```

G0 只证明旧结论无效，不证明新 scope 可用。

## 六、G1：正确构建 C scope

### 6.1 首轮禁止新检索

G1 第一轮只能使用已经冻结、已通过 P5 来源/结构资格的 C build supports。不得因为实现困难先找新文献替代。

### 6.2 恢复完整 pipeline

执行者必须从 P3/P4 实际调用上下文恢复完整流程，而不是单独复制某个函数。

至少验证：

```text
instance
→ derive_template_smarts
→ scoped_smarts
→ scope metadata
→ runtime template
```

若 P3 原调用逻辑包含其他必要步骤，也必须纳入并记录。

### 6.3 build-support 硬门

声明 C scope 必须满足：

- build support 数 ≥2；
- distinct canonical acceptor ≥2；
- 两个 build support 均 structure_complete；
- scope 对每个 build support 均产生正确 reference precursor；
- replay=100%；
- source/reaction/support identity 正确绑定；
- `exact_seed_instance_match` 与 `scope_match` 分开记录。

**第二个 build support 是强制 canary。**

若 build support 1 PASS、build support 2 FAIL，则直接判：

```text
C_scope_implementation = Blocked
```

不得进入 holdout probe，不得得出任何迁移/泛化结论。

### 6.4 boundary controls

首次 holdout probe 前预登记至少包括：

- 错误糖型；
- 错误连接位点；
- 超出允许母核；
- 超出允许取代模式；
- donor 不匹配；
- 非目标 C/O linkage；
- 明确不属于该 scope 的结构近邻。

验收：

```text
expected_positive build supports = 100%
expected_negative boundary controls = 0 violations
```

通过后冻结至少：

```text
c_scope_manifest.json
c_scope_template.json
c_scope_boundary_results.json
```

并记录 SHA。

## 七、G2：C runtime-executable panel

P5 的 `7 targets / 5 groups` 必须重新分成：

```text
counting-qualified
runtime-executable
```

只有 runtime-executable 目标进入 A/B/E 分母。

### 7.1 每个 C holdout 必须具备

- 来源可定位原件；
- product 完整结构；
- canonical product SMILES；
- precursor multiset；
- bond-change / reaction signature；
- 位点与必要立体；
- closure group；
- exposure grade；
- RDKit parse/sanitize；
- 必要的结构/反应质量检查；
- 不依赖 build exact reaction；
- 不依赖猜测得到的手写结构。

如果此前 7 个目标中存在只有名称/证据定位而没有可运行结构的目标：

- 有来源明确结构时，可以在 P6 编码；
- 来源不足时必须剔除；
- 禁止根据名称、常见结构、PubChem 替代结构或执行者记忆直接补齐。

### 7.2 C 面板硬门

最终：

```text
N_C >= 6
closure_groups_C >= 2
deferred = 0
inferred = 0
build/holdout reaction overlap = 0
build/holdout closure leakage = 0
runtime executable = 100%
```

面板冻结后记录 SHA。

## 八、G3：冻结后 C scope applicability probe

只有以下同时成立后才能执行：

```text
C_scope_implementation = Completed
C_runtime_panel = Completed
```

probe 只能读取冻结 scope 与冻结 panel，不得修改二者。

每个 C target 至少记录：

```text
scope_applicable
number_of_candidate_matches
reference_precursor_match
reason_if_not_applicable
```

### 8.1 probe 判读规则

**情形 A：** scope 连第二个 build support 都不能稳定 replay。  
结论：工程实现失败。不得声称 scope 泛化失败。

**情形 B：** build supports 100% 通过，但全部 holdout 均不适用。  
结论：当前冻结 scope 与冻结 holdout 不形成可测迁移关系，原因码写 `scope_holdout_domain_mismatch`，不得写 `model_transfer_failure`。

**情形 C：** build supports 100% 通过，且至少 ≥3 holdout targets / ≥2 closure groups 在结构上可由该 scope 产生完整 reference precursor。  
结论：C transfer experiment 可测，必须进入 A/B/E。

达到情形 C 后不得因为 SS 仍不足而停止 C。

## 九、G4：正式构建 v6 runtime

P5 中未完成的 v6 必须在本任务正式建立。

建议定义：

```text
v6 =
    qualified P2/v3 baseline
    + revalidated P4 SS O2 scope
    + P6-qualified C scope
    + optional P6-qualified SS additions
```

不得整体继承有问题的历史增量再依靠运行时状态字段逻辑禁用。

### 9.1 C 必须有正式 scope guard

完整链必须通过：

```text
source support
→ scope registry
→ v6 manifest
→ runtime loading
→ scope guard
→ candidate generation
→ filtering
→ node creation
```

至少要求：

- default_enabled=false；
- 缺 payload fail closed；
- manifest SHA 漂移 fail closed；
- package config 与 checkout config 一致；
- holdout 不进入 runtime instances；
- exact template / scope template 可区分；
- v1–v5 旧加载行为不被静默改写；
- build 2/2 必须通过正式 runtime 路径 replay，而不仅是 helper function。

## 十、G5：C A/B/E 独立执行

### 10.1 Arm 定义

继续沿用前序冻结语义：

```text
A = optimized generic search，domain library off
B = A + qualified P2/v3 baseline
E = A + TASK-016-P6 v6
```

除明确修复 v6 runtime 外，模型、PUCT、scoring、stock、generic filtering、reviewed-resource view、seeds、budget 均不得按结果调整。

固定 seed：

```text
0
1
2
```

### 10.2 C 运行数量

若 C 最终为 7 targets：

```text
7 × 3 seeds × 3 arms = 63 cells
```

若最终合格 C panel 为 N，则为 `N × 9 cells`，合同允许 C 为 6–9 个目标。

### 10.3 C 候选迁移硬门

定义：

- `N_C`：冻结 complete/runtime-executable holdout 数；
- `N_gap_C`：A 与 B 均正常运行且均未保留完整主 reference 的不同目标数；
- `G_C`：上述 gap 中 E 正常保留完整主 reference，且来源于 P6-qualified C scope、非 exact seed replay 的不同目标数。

C Completed 至少满足：

```text
N_C >= 6
G_C >= 3
G_C / N_gap_C >= 50%
successful closure groups >= 2
net complete-reference coverage vs A > 0
net complete-reference coverage vs B > 0
reference loss = 0
```

`N_gap_C=0` 时 ratio=`null`，不得写 100%。

### 10.4 C 真实 node-transfer 硬门

至少 3 个不同 C holdout target 同时满足：

- A seed0/1/2 均正常；
- B seed0/1/2 均正常；
- A/B 三 seed 均未实际创建完整 reference action；
- E seed0/1/2 均正常；
- E 三 seed 均实际创建完整 reference action/node；
- 成功目标覆盖 ≥2 closure groups；
- `exact_seed_instance_match=false`；
- 可从逐 cell trace 重算。

仅 candidate generation 而没有真实 node creation 不计成功。

## 十一、G6：SS 4/6 定向闭环

SS 不进行无目的大规模扩库。

当前已知核心问题：

> 已验收 O2 build scope 与 `PMC13084081` 共享 closure，使该组多个 SS reaction 被正确排除出 holdout，最终只剩 4/6。

P6 优先测试两条路径。

### 路径 A：更换 build support closure

优先寻找：

```text
same qualified SS O2 scope
+ independent source/reaction closure
+ >=2 distinct canonical acceptors
```

如果能由新的独立 build sources 支持 O2 scope，则重新计算 `PMC13084081` group 是否可合法进入 holdout。不能自动恢复，必须完整重跑 exposure/closure。

### 路径 B：增加新 holdout

若路径 A 不可行，则定向寻找至少 2 个：

- structure_complete；
- runtime-executable；
- leakage-free；
- 与 build closure 独立；
- 适用于已冻结 SS scope 的目标。

### 11.1 来源真实性硬门

鉴于 P5 曾收到错误 PMC 记录，所有新来源在内容分析前必须先机器核：

```text
PMCID
title
DOI
journal
publication metadata
```

必须相互匹配。`HTTP 200` 不构成论文身份确认。

任何 agent/模型给出的 PMCID、DOI、标题组合只能作为 discovery hint，在 publisher / PMC / Crossref 等权威元数据验证前：

```text
evidence_eligible = false
```

### 11.2 结构编码禁止猜测

禁止执行者根据名称自行构造复杂天然产物或甾体 SMILES。只有原始来源、可信结构数据库和明确 identity chain 支持的结构才能进入 `structure_complete`。

## 十二、G7：SS A/B/E

只有以下全部成立时运行：

```text
N_SS >= 6
closure_groups_SS >= 2
runtime_executable = 100%
zero leakage
SS scope build replay = 100%
```

运行方式与 C 相同。

SS 候选迁移门：

```text
G_SS >= 3
G_SS / N_gap_SS >= 50%
successful groups >= 2
net coverage vs A > 0
net coverage vs B > 0
reference loss = 0
```

真实 node-transfer：至少 3 个不同 SS holdout targets 满足 A/B 三 seed 均不创建，而 E 三 seed 均创建完整 reference node，并覆盖 ≥2 closure groups。

## 十三、G8：旧能力回归

只要 v6 因 C capability 已正式变化，并要声明 `C_transfer=Completed`，即必须执行旧能力回归；不能因为 SS 尚未完成而省略。

至少：

```text
17 old targets × 3 seeds × E = 51 cells
```

保持前序约定：旧 4 SS、5 C、7 O；旧 1b 按历史定义单列。

要求：

```text
new reference loss = 0
old successful behavior preserved
v3 fingerprint unchanged
stock keys unchanged
reviewed-resource binding unchanged
```

如果之后 SS scope 又导致 v6 科学资产变化，则最终 v6 必须重新执行受影响的 legacy regression。

## 十四、搜索预算

P6 使用全新独立账本，不借 P5 的 0/480 剩余额度。

| 用途 | 上限 |
| --- | ---: |
| C A/B/E，最多 9 targets | 81 |
| SS A/B/E，最多 9 targets | 81 |
| 首轮 legacy E regression | 51 |
| 首轮科学矩阵最大 | 213 |
| 一次完整受影响矩阵重验 | 213 |
| runtime/package/engineering 真实搜索探针 | 54 |
| **P6 总硬上限** | **480** |

纯 RDKit 结构检查、模板 replay、scope applicability 静态 probe 不计真实 MCTS。

发现实现 bug 后：

- 已执行 cell 必须保留；
- 标记 `superseded_due_to_implementation_bug`；
- 不允许只挑失败 cell 重跑；
- 必须重新跑完整受影响矩阵。

## 十五、必须新增的自动测试

至少包括：

```text
test_exact_template_and_scope_are_distinct_artifacts
test_scope_pipeline_calls_scoped_smarts
test_scope_fires_all_declared_build_supports
test_second_build_support_is_scope_canary
test_scope_negative_controls_do_not_fire
test_scope_hash_frozen_before_holdout_probe
test_holdout_probe_cannot_mutate_scope
test_holdout_target_requires_runtime_complete_structure
test_deferred_target_not_in_runtime_panel
test_build_holdout_zero_reaction_leakage
test_build_holdout_zero_closure_leakage
test_c_and_ss_preflights_are_independent
test_ss_failure_does_not_block_qualified_c_runs
test_exact_seed_replay_not_counted_as_transfer
test_node_transfer_requires_real_node_trace
test_source_identity_requires_metadata_match
test_unverified_agent_citation_not_evidence_eligible
test_inferred_handwritten_structure_not_structure_complete
test_v6_default_off
test_v6_manifest_drift_fails_closed
test_v6_runtime_replays_all_build_supports
test_v3_v4_v5_legacy_loading_unchanged
```

其中以下为 `P5-ERR-06` 的永久回归保护，不得删除：

```text
test_scope_pipeline_calls_scoped_smarts
test_scope_fires_all_declared_build_supports
test_second_build_support_is_scope_canary
```

## 十六、停止条件

### C 轴

出现以下情况停止 C 科学运行：

1. 正确 scope 无法覆盖全部声明 build supports；
2. boundary controls 出现无法解释的误命中；
3. C runtime-executable holdout <6；
4. C closure groups <2；
5. build/holdout 泄漏无法消除；
6. scope 冻结后可产生 reference 的 holdout 少于 3 个或少于 2 closure groups；
7. v6 正式 runtime 无法 replay build supports；
8. 只有修改 holdout、scope 或参数才能获得正结果。

其中 1–2 属于 `scope implementation failure`；3–5 属于 `panel failure`；6 属于 `scope_holdout_domain_mismatch`；只有通过这些门并执行 A/B/E 后失败，才可以叫 `transfer failure`。

### SS 轴

出现以下情况停止 SS 科学运行：

1. runtime-executable holdout <6；
2. closure groups <2；
3. build/holdout leakage；
4. qualified SS scope build replay 不完整；
5. v6 runtime 未形成。

SS 停止不得终止已合格 C 轴。

### 全局

- protected historical payload 无法解释漂移；
- 需要降低门槛；
- 需要改变模型/PUCT/库存/通用评分来提高成绩；
- 达到搜索或来源预算上限；
- 需要绕过付费或登录访问限制；
- 结果出现后必须重新定义 reference；
- 新来源身份验证失败；
- 执行中发现面板污染。

## 十七、硬验收清单

### P5-ERR-06

- [ ] 旧 probe 可重现。
- [ ] 已确认旧 probe 使用 exact instance template。
- [ ] 已确认 P3 完整 pipeline 的 scope transformation。
- [ ] 旧“C scope 不泛化”结论明确 superseded。

### C scope

- [ ] exact template 与 scope template 分离保存。
- [ ] `scoped_smarts` 确实进入正式 build pipeline。
- [ ] C build supports ≥2 distinct canonical acceptors。
- [ ] 全部 build supports replay 100%。
- [ ] 第二个 build support PASS。
- [ ] boundary violations=0。
- [ ] scope 在看 holdout 前冻结 SHA。

### C panel

- [ ] C complete runtime targets ≥6。
- [ ] C closure groups ≥2。
- [ ] 每个目标有 product structure。
- [ ] 每个目标有 frozen reference precursor。
- [ ] deferred/inferred=0。
- [ ] leakage=0。
- [ ] 至少3 targets /2 groups 对冻结 scope 结构可测。

### C runtime / transfer

- [ ] v6 正式 guard 可运行。
- [ ] v6 build replay 100%。
- [ ] C A/B/E 全矩阵实际执行。
- [ ] C `G>=3`。
- [ ] C `G/N_gap>=50%`。
- [ ] C 对 A、B 净覆盖均 >0。
- [ ] C reference loss=0。
- [ ] C 至少3 targets 满足真实三-seed node transfer。
- [ ] 成功覆盖 ≥2 closure groups。

### SS

- [ ] SS holdout ≥6。
- [ ] SS groups ≥2。
- [ ] SS leakage=0。
- [ ] SS build scope replay 100%。
- [ ] SS A/B/E 实际执行。
- [ ] SS `G>=3`。
- [ ] SS `G/N_gap>=50%`。
- [ ] SS 至少3 targets 满足真实三-seed node transfer。

### Regression / delivery

- [ ] 最终 v6 上旧 17×3 回归完成。
- [ ] 旧成功参照无新增损失。
- [ ] 搜索账本≤480。
- [ ] 全量 tests 通过且不少于当前151项。
- [ ] 新 P6 合同测试全部存在。
- [ ] package / no-asset / fail-closed / config-copy 验证通过。
- [ ] protected inputs 零漂移。
- [ ] `git diff --check` 通过。
- [ ] REPORT / STATE / navigation 与冻结事实一致。
- [ ] actionable / evidence_closed / prediction_conditions_verified 不因 P6 自动升格。
- [ ] formal benchmark / training independence / independent chemistry / production 状态保持原边界。

## 十八、推荐执行顺序

```text
G0  P5-ERR-06 replay + protection
 |
G1  reconstruct full C scope pipeline
 |   exact → scoped_smarts → build 2/2 → boundaries
 |
G2  make C panel runtime-complete
 |
G3  freeze C scope + panel, run applicability preflight
 |
 +---- if C measurable ----> G4 build v6
 |                              |
 |                              G5 C A/B/E
 |                              |
 |                              legacy regression if claiming C completion
 |
 +---- independently -----> G6 SS closure repair
                                |
                         if SS >=6
                                |
                             G7 SS A/B/E
                                |
                             G8 final v6 regression
                                |
                         VERIFY / REPORT / STATE
```

**关键规则：不得等待 SS 才执行已经合格的 C。**

## 十九、建议执行入口

实际脚本名可调整，但职责必须分离：

```bash
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_g0.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_c_scope.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_c_panel.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_c_probe.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_build_v6.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_c_runs.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_ss_sources.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_ss_panel.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_ss_runs.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B scripts/task016_p6_verify.py
python3 -B scripts/operate.py TASK-016-P6 .venv-foundation/bin/python -B -m unittest discover -s tests -v
python3 -B scripts/operate.py TASK-016-P6 git diff --check
```

## 二十、计划产物

| 层 | 计划产物 |
| --- | --- |
| protection | `approval.json`, `execution_baseline.json`, `protected_hashes.json` |
| P5 correction | `p5_err06_reconciliation.json`, `old_probe_replay.json`, `scope_pipeline_trace.json` |
| C scope | `c_exact_templates.jsonl`, `c_scope_template.json`, `c_scope_manifest.json`, `c_scope_build_replay.json`, `c_scope_boundary_results.json` |
| C panel | `c_panel_manifest.json`, `c_heldout_references.jsonl`, `c_runtime_completeness.jsonl` |
| C probe | `c_scope_applicability.jsonl`, `c_preflight.json` |
| v6 | `templates.jsonl`, `runtime_instances.jsonl`, `template_source_manifest.json`, config/packaged snapshot |
| SS | source/admission/exposure/split/panel artifacts |
| runs | independent C/SS A/B/E ledgers and cell outputs |
| metrics | `metrics_by_family.json`, gain/loss/net coverage, node-transfer summary |
| regression | legacy 17×3 results |
| closeout | `audit.json`, `delivery_manifest.json`, REPORT, STATE/navigation updates |

## 二十一、必须提交的 REPORT

无论 Completed、Partial、Blocked 或失败，都必须生成：

`docs/reports/REPORT-016-P6-c-scope-runtime-transfer-closure.md`

REPORT 必须直接回答：

1. `P5-ERR-06` 是否被独立复现？
2. P3 完整 scope pipeline 到底是什么？
3. exact instance template 与 scoped template 的 SHA 分别是什么？
4. scoped C template 是否能命中全部 build supports？
5. 第二个 C build support 是否通过？
6. C 的 7 个旧计数目标中最终有多少真正 runtime-executable？
7. 正确冻结的 C scope 对多少 holdout 可产生 reference precursor？
8. 若 C 没有运行 A/B/E，具体是哪一个合同停止条件，而不是笼统写“不可测”？
9. C A/B/E 实际执行多少 cells？
10. C 的 N、N_gap、G、G/N_gap、净覆盖和 reference loss 是多少？
11. C 有多少目标满足真实三-seed node transfer？
12. SS 最终如何从 4/6 处理：更换 build closure、补 holdout，还是仍未解决？
13. SS 是否执行 A/B/E？
14. 最终 v6 是否通过旧 17×3 回归？
15. 是否存在执行过程中被 supersede 的 probe、scope、panel 或矩阵？
16. 最终结论属于 implementation、development transfer，还是仅 evidence/panel completion？
17. 哪些更高科学门仍然没有关闭？

## 二十二、允许的最终科学措辞

若只有 C 通过：

> 在 TASK-016-P6 冻结、与 build 隔离的新底物开发留出上，C-glycosylation scope 显示候选迁移并稳定进入真实 MCTS；SS 尚未完成迁移验收。

若 C 与 SS 都通过：

> 在 TASK-016-P6 冻结、无 build/holdout 泄漏的新底物开发留出上，C-glycosylation 与 sugar–sugar glycosylation 范围能力均表现出跨实例迁移，并在三个固定 seed 的真实 MCTS 中稳定创建完整参照动作，同时既有能力无新增参照退化。

即使两类全部通过，也不得写：

- 已证明真实未知化学预测准确率；
- 已证明训练集独立泛化；
- 已通过正式 blind benchmark；
- 已证明实验可行性；
- 已可用于 production 或 actionable synthesis。

## 二十三、非目标与禁止项

本任务不：

- 训练或微调模型；
- 修改通用 PUCT/scoring 来追成绩；
- 修改库存制造闭合；
- 扩大 formal benchmark；
- 启动 TASK-017/018；
- 做独立湿实验验证；
- 做供应商当前可购认证；
- 升格 production；
- 把 agent review 当 human_reviewed；
- 修改 P1–P5 历史记录来隐藏错误；
- 因为已经迭代到 P6 而降低完成标准；
- 执行 Git commit/push/tag/release，除非所有者另行明确授权。

## 二十四、修订记录

- 2026-10-07 v0.1：根据 P5 后续复核起草。确认 `P5-ERR-06`：P5 C probe 使用了 `derive_template_smarts` 的精确实例模板而漏掉 `scoped_smarts`，连第二个 build support 都无法命中，因此旧“C scope 不泛化/结构性不可测”结论无效。P6 将 C scope 完整构造、build 2/2 canary、runtime-executable holdout、C/SS 分轴 preflight、正式 v6、独立 A/B/E 与真实 node transfer 设为不可替代的完成链；SS 4/6 保持独立 evidence/closure 支线，不再阻塞合法 C 实验。本轮仅起草并落盘合同，未授权执行。
