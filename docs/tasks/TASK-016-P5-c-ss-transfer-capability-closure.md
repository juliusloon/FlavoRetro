# TASK-016-P5：C/糖间泛化与迁移核心能力闭环

## 合同元数据

- 任务 ID：TASK-016-P5；合同版本：v0.1；起草日期：2026-10-07。
- 状态：**Proposed（拟议）**。本轮仅按所有者“将你的调查结果写成新的 task，这个 task 的核心是把后来暴露出来的 C/糖间泛化和迁移缺口也闭环，证明核心能力”之指示起草合同；**尚未授权执行新的来源采集、结构编码、模板构建、v6 接线或真实 MCTS**。
- 起草授权：human_direct，仅覆盖本合同落盘与任务登记。
- 执行授权：待所有者后续明确批准。执行开始前必须登记批准语句、日期、本合同 SHA-256、实际工作区基线与预算；agent 执行或结构复核不得写成 human_reviewed。
- 人工负责人：项目所有者。
- 执行者：待批准后登记；允许主执行 agent 协调来源、结构、运行与审计子流程，但 build、holdout 与最终指标必须由冻结载荷而非执行者记忆决定。
- 工作区：`/home/ljx/FlavoRetro`；基线分支 `main`；起草时 HEAD=`993b22f5e8eed5797d27f02c566af1b86a4b7880`。
- 起草时工作区：121 个 untracked、23 个 tracked modified，共 144 个 status entries；不得 reset/clean/checkout 覆盖既有 TASK-015/016 与用户改动。
- 前序合同：[TASK-016-P4](TASK-016-P4-p3-admission-correction-and-transfer-completion.md)；前序报告：[REPORT-016-P4](../reports/REPORT-016-P4-p3-admission-correction-and-transfer-completion.md)。P4 历史文件及 `outputs/task016-p4/v1/superseded/` 保持原样。
- 本任务本地科学产物计划根：`outputs/task016-p5/v1/`；新原件计划根：`data/raw/task016-p5/`。二者继续 Git 忽略；代码、合同与测试是否提交/推送不在本批准范围内。
- 所有项目内写入与命令必须经 `scripts/operate.py` 登记；原始/受限来源不得进入 Git。

## 一、任务目标与“证明核心能力”的精确定义

TASK-016 首版已经证明 4 个来源限定 O-糖苷精确实例可以接入搜索；P1/P2/P3/P4 又扩大了模板和来源，但 C 成键与糖—糖成键的**新底物泛化/迁移**一直没有完成可计算验收。P4 修正了 P3 的准入与泄漏错误，却因最终留出不足在 A/B/E 前停止。

本任务不再以“有模板”“支持实例能重放”“旧目标不退化”作为 C/糖间核心能力完成的替代指标。目标是同时完成：

1. 建立至少一个真正合格的 **C build-side 新增/严格扩展范围能力**；
2. 保留或重验收至少一个合格的 **SS build-side 范围能力**；
3. 冻结与 build 来源/反应/精确结构无泄漏的 C、SS 新底物留出面板；
4. 在同一冻结模型、库存、审核视图、搜索参数下执行 A / B / E 三臂；
5. 对 C、SS 两类分别证明：新增范围能力能补回 A 与 B 都没有保留的完整参照，并且该参照在真实 MCTS 中由 E 稳定创建；
6. 重新执行旧能力回归，证明新能力不是以旧能力退化换来的。

本任务允许的最强结论仅为：

> **在 TASK-016-P5 冻结、development-exposed 但与模板构建隔离的新底物留出上，来源支持的 C/SS 范围能力表现出可审计的候选迁移，并在真实 MCTS 中稳定创建完整参照动作；同时旧能力无参照退化。**

该结论**不等于**独立化学准确率、实验可行性、训练独立性、正式 blind benchmark、当前供应认证或 production。即使本任务 Completed，`formal_run_ready`、`release_ready`、`evidence_closed` 与 `actionable` 也不得因此自动翻转。

## 二、起草依据：2026-10-07 独立核查得到的当前事实

本任务以本节事实作为起点，不以 P4 报告中的文字摘要替代冻结产物。

### 2.1 P4 工程纠偏本身成立

现场重新运行：

```bash
.venv-foundation/bin/python -B scripts/task016_p4_verify.py
.venv-foundation/bin/python -B -m unittest discover -s tests -v
```

结果：

- P4 verifier：`overall=Partial`，`failed_checks=[]`；
- 四轴：correction_engineering Completed、corrected_reaction_admission Completed、C_transfer Partial、sugar_sugar_transfer Partial；
- 151/151 本地测试通过；
- 34 条 P3 反应重审后 C=8、SS=16、总=24 structure_complete；
- C3 中间体范围与 SS 1→6 范围被隔离；
- v5 从 P2/v3 54 模板基线重建，仅保留 SS 1→2 范围，运行时合计 55 模板 / 87 实例；
- v5 默认关闭、缺资产或 SHA 漂移失败封闭；
- P3R-SS01/02/03 build/holdout 泄漏已由合同测试抓出，错误面板保留于 `superseded/`。

### 2.2 P4 最终冻结 C 面板不是报告摘要中的 3，而是 1

以下 P4 冻结产物是本任务的权威起点：

| 文件 | SHA-256 | 核查事实 |
| --- | --- | --- |
| `outputs/task016-p4/v1/panel_manifest.json` | `1fe41ed789b180d850949fce02ab9cf2c3c73e9a28f6bc7372d1acdbdb2b6dc2` | C=1（仅 P3R-C12），SS=5 |
| `outputs/task016-p4/v1/c_class_g3_additions.json` | `4ae074302ebaf5717ffc8f0d15aff0d0d760441c31bb5c0b325f048a79d1d42b` | P4R-C01、P4R-C04 被登记为两个 independent_panel_targets 候选 |
| `outputs/task016-p4/v1/metrics_by_family.json` | `871930840a50206d87574ec1d949e285dcbe4ec44ff9d6f8821b6f125e2b6661` | N_family C=1、SS=5；A/B/E=false；全部迁移指标 null |
| `outputs/task016-p4/v1/run_ledger.jsonl` | `04beecc4093941e6ec3c9bafc86b31059d21518b65330567350d87796ed4c53c` | attempts=0 |

`P4R-C01` 与 `P4R-C04` 虽被 P4 G3 判断为可继续考虑的结构完整 C 候选，但没有进入最终 `panel_manifest.json/jsonl`、`split_manifest.json` 或 `heldout_references.jsonl`；P4 新反应记录中两者仍写 `structure_encoding=pending_G3_encoding`。因此不得把它们追认成已经冻结的 holdout。

**P5 的起始留出缺口按最终冻结事实计算：C 1/6，SS 5/6。**  
C01/C04 只属于待重新编码、重新分配的候选池。它们若被用作 C scope build support，就必须退出 holdout；若进入 holdout，就不得参与模板设计、适用范围推断或边界调参。不能同时计两边。

### 2.3 P4 当前没有合格 C build-side 新范围

P4 v5 的唯一新增范围是 `rhamnoside_glucoside_O2`。C `hydroxyflavanone_C3` 因中间体结构证据外推撤出，SS 1→6 因两个来源实际只有一个 distinct canonical acceptor 撤出。

因此 C 的缺口不只是“再补若干 holdout 目标”。要完成 C_transfer，必须同时具备：

- 至少一个来源支持的合格 C 新增/严格扩展 scope；
- 该 scope 的 build support 与 holdout 完全隔离；
- C holdout 最终仍有 ≥6 个完整目标 / ≥2 闭包组。

若把 C01/C04 用于建立 C scope，它们不能再计 C holdout，所以不能用“1+2=3，因此只差3个”作为完整任务规划。

### 2.4 P4 来源总账与报告中的阶段数字不一致

最终 `outputs/task016-p4/v1/source_accounting.json`
SHA-256=`82e544ecfcb0aab354980ecb0e07e0565d33e7330abe9fcbf0cd27c1d37a43c1`，记录：

- HTTP attempts = **45**；
- distinct URLs = 45；
- bytes = **63,180,976**；
- reuse_of_prior_task_files = **74**；
- article_versions = **5**；
- attachments = **9**。

这些数仍显著低于 P4 的 2000 HTTP / 2 GiB 等硬预算，因此“预算未耗尽”成立；但 P4 报告的 23 / 1.13 MB / 40 是阶段口径，不能作为 P5 的起始总账。P5 必须明确区分 discovery-only、new-download 与 whole-task accounting，不再混写。

### 2.5 核心迁移实验至今为 0

P4 没有运行任何 A/B/E cell，真实搜索尝试为 0。C/SS 的 `N_gap`、`G`、`G/N_gap`、真实三-seed node transfer 全部是 `null`，不是 0。

所以当前状态不是“迁移成绩差”，而是**核心迁移能力尚未被实验测量**。

## 三、分轴完成定义

最终 REPORT 必须至少分为以下七轴，禁止只给一个 Overall：

| 轴 | Completed 最低条件 |
| --- | --- |
| p4_reconciliation | P4 冻结事实、报告文字差异和来源口径已在 P5 新载荷中明确交叉表；P4 历史文件不改写 |
| C_scope_capability | 至少 1 个新增/严格扩展 C scope，≥2 个不同 canonical acceptor 的完整 build supports，支持重放 100%，预登记边界违反 0 |
| panel_integrity | C≥6、SS≥6 complete holdout；各≥2闭包组；全局12–18；deferred=0；build/holdout 泄漏=0 |
| C_transfer | C 候选迁移与真实 node transfer 均达到本合同硬门 |
| sugar_sugar_transfer | SS 候选迁移与真实 node transfer 均达到本合同硬门 |
| legacy_regression | 旧 17 目标 ×3 seed 的 E 回归完成且既有参照能力无新增损失 |
| engineering_delivery | v6 默认关闭、绑定/哈希/包外/无资产/重放/预算/保护/测试/报告全部通过 |

**整体 Completed 仅在七轴全部 Completed 时成立。**  
任一核心迁移轴不通过则整体不得 Completed；未执行指标保持 `null`。不能用工程完成、支持重放、旧回归或来源数量抵偿迁移门。

## 四、范围与边界

### 4.1 允许项

- 自动发现、下载、冻结公开且合规的 C-糖基成键与糖—糖成键具体实验来源；
- 复用 P1–P4 已冻结原件，但必须按 SHA 与曝光等级重新登记；
- 对 P4R-C01/C04 及后续候选做完整结构编码、canonical acceptor/reaction/closure 计算；
- 新建 P5 corrected bank、build/holdout split、来源闭包和留出参照；
- 建立一个或多个合格 C 新范围；SS 可复用 P4 已验收的 1→2 范围，也可增加新的合格范围；
- 构建显式默认关闭的 v6；
- 在冻结面板上执行 A/B/E 三臂单步与真实 MCTS；
- 执行旧能力 E 回归；
- 增加完成本合同所需的最小运行接线、测试、审计与治理文档。

### 4.2 禁止项

- 不改 P1/P2/P3/P4 历史 TASK、REPORT、冻结 scientific payload、旧 run ledger 或 `superseded/` 现场；
- 不把 C01/C04 或任何反应同时用作 build support 和 holdout；
- 不因看到 A/B/E 成绩后改变 holdout、reference precursor、closure、scope 或分母；
- 不降低 C/SS 各 6 目标 / 2 组硬门；
- 不用 deferred、名称-only、图未核、关键立体 unknown 或下游终产物证据外推填充面板；
- 不用同一 canonical acceptor 的多个论文、多个酶、多个 assay 复制计数；
- 不调整 PUCT、模型、通用策略权重、库存、KnownHazards 或通用过滤来提高结果；
- 不扩充 17 键候选库存来制造闭合；
- 不训练或微调网络；
- 不把数据库 identity、NMR 下游产品、图回放、来源支持或 agent review 冒充独立化学验证；
- 不执行正式 blind benchmark、TASK-017/018、production/release 晋级；
- 不访问付费/登录受限商业接口，不绕过访问控制；
- 不执行 Git commit/push/tag/release，除非另有明确授权。

## 五、来源与预算合同

### 5.1 来源优先级

优先使用可程序化、可冻结、可回到原件定位的公开来源：

1. Europe PMC / PMC Open Access 正文与附件；
2. DOI 对应的开放 publisher/SI；
3. Rhea/ChEBI 仅用于结构/身份辅助，不能代替具体正向实验；
4. ORD 冻结镜像只读复用与增量核查；
5. Zenodo/作者官方数据仓库/其他合法开放附件；
6. 前序任务已经下载的原始件，只读复用并重新登记 SHA。

标题/摘要只作为发现层，不作为 structure_complete 准入证据。

### 5.2 P5 独立来源硬预算

- HTTP 普通尝试 ≤ **3000**；
- 新下载字节 ≤ **4 GiB**；
- 新 article versions ≤ **200**；
- 新附件 ≤ **360**；
- 并发 ≤4；
- 单 URL 普通网络尝试≤2，恢复链单独登记；
- 单文件≤256 MiB；
- 达到任一上限即停止相应采集并报告真实缺口。

预算是上限而非目标。P1–P4 的网络/运行预算不得借记到 P5，也不得把旧账剩余额度并入 P5。

### 5.3 来源总账必须同时给三套口径

最终至少分别报告：

- discovery/query attempts；
- P5 新下载件数/字节；
- whole-task HTTP / bytes / reused prior files / article versions / attachments。

三者不得用一个数字互相替代。

## 六、执行阶段

## G0：批准、保护与 P4 reconciliation

执行批准后第一步：

1. 冻结实际 Git/代码/配置/环境/审核视图/17库存/模型哈希；
2. 校验本合同列出的 P4 八个关键文件 SHA；
3. 建立 `p4_reconciliation.json`，至少逐项记录：
   - report text claim；
   - frozen artifact fact；
   - authoritative_for_p5；
   - whether_historical_file_rewritten=false；
4. 明确起点：
   - C holdout = 1；
   - SS holdout = 5；
   - C01/C04 = candidate pool，不是 frozen holdout；
   - P4 A/B/E attempts = 0；
   - P4 source whole-task accounting = 45 / 63,180,976 B / reuse 74 / article versions 5 / attachments 9；
5. 建保护基线，禁止执行过程中静默修改 P4/P3 冻结现场。

G0 不运行新 MCTS。

## G1：新来源补充与完整反应准入

目标不是追求记录数量，而是同时满足 build 与 holdout 的独立需求。

每个候选必须保存：

- source/provider/version/DOI/PMCID/record；
- 原件路径、SHA、许可、定位；
- acceptor、donor、product 的完整结构表示；
- 正向成键方向与实际 covalent change；
- 位点与立体；
- enzyme/catalyst/condition context；
- NMR/standard/MS/isolated 等 identity basis；
- `structure_encoding`；
- `canonical_acceptor_signature`；
- `canonical_reaction_signature`；
- `closure_group`；
- exposure grade；
- reviewer_type；
- actionable/evidence_closed/prediction_conditions_verified。

C01/C04 必须重新完成上述字段，不能因 P4 的 `countable_as_structure_complete=true` 自动晋级。

准入状态沿用冻结词汇：

- `structure_complete_admitted`；
- `identity_complete_structure_deferred`；
- `provisional_inferred`；
- `rejected`。

只有第一类可进入 build 或 holdout。

## G2：先冻结 build / holdout，再允许模板构建

在任何 P5 新模板生成和任何 A/B/E 输出出现之前：

1. 构建 source/reaction/exposure closure；
2. 给每条 structure_complete reaction 唯一分配 `build`、`holdout` 或 `unused`；
3. build support 强制 E2/build-only；
4. holdout 与任何 build source/reaction closure 相交则剔除；
5. 同一精确 covalent reaction、多论文复述、多 assay 不重复计；
6. 冻结 `split_manifest.json`、`panel_manifest.json`、`heldout_references.jsonl`、`unselected_records.jsonl`。

### G2-A：C build-side 硬门

至少形成 1 个真正新增或严格扩展的 C scope，并满足：

- ≥2 个不同 `canonical_acceptor_signature`；
- ≥2 个 structure_complete build reactions；
- 供体、受体、位点、立体与必要上下文都有显式边界；
- 不依赖 P4/P3 holdout 精确结构设计；
- 同一反应的多来源不能增加受体数。

若 C01/C04 被选为 build support，则它们不再属于 C holdout。

### G2-B：SS build-side 硬门

P4 `rhamnoside_glucoside_O2` 可作为既有已纠偏范围候选，但执行时仍需重新验证：

- 2 个 distinct canonical acceptors 仍成立；
- 原支持结构与 SHA 未漂移；
- holdout 无 exact support/reaction leakage；
- v6 不暗中重新带回 O6 或 C3 被隔离范围。

可增加新的 SS scope，但不是完成本任务的必要条件。

### G2-C：最终 holdout 面板硬门

- C：**≥6 complete targets、≥2 closure groups**；
- SS：**≥6 complete targets、≥2 closure groups**；
- 全局：**12–18 targets**；
- 每类最多 9；
- deferred / inferred / name-only / graph-only = 0；
- build/holdout reaction overlap = 0；
- build/holdout source closure leak = 0；
- 每个目标一个预冻结完整主 reference precursor multiset；
- 不看 A/B/E 成绩选择目标。

若任一类低于 6，本任务在该类**停止于来源/面板阶段**，迁移指标保持 null；不得先跑再补面板。

## G3：构建显式 v6，并证明 build-side 范围实现正确

v6 定义：

```text
A = optimized generic search, domain library off
B = A + frozen P2/v3 baseline (54 templates)
E = A + TASK-016-P5 v6

v6 = v3
   + explicitly revalidated P4 SS O2 scope
   + P5-qualified C scope(s)
   + optional P5-qualified SS scope(s)
```

v6 **不得**通过“整体继承 v4/v5 然后用状态字段声称失效范围不算”的方式构建；最终 payload 必须只含明确通过 P5 build gate 的增量。

硬要求：

- default_enabled=false；
- v1–v5 旧加载行为与指纹不被改写；
- 缺 payload、manifest、SHA、review binding 时 fail closed；
- runtime_instances 只含 build；
- holdout references 不进 runtime/config/package；
- 新动作保存 template/source/scope/review binding；
- `exact_instance_match`、`template_source_support`、`prediction_conditions_verified` 独立；
- 新目标保持 actionable=false、evidence_closed=false、prediction_conditions_verified=false。

### build implementation 验收

每个可执行 scope：

- 声明 build supports 逆向精确重现率 = **100%**；
- 所有预登记边界 controls 违反数 = **0**；
- 至少包含错误位点/错误糖型/越界受体/错误上下文中的相关控制；
- 支持重放只证明实现与来源表示一致，不计迁移成功。

## G4：冻结 A/B/E 评估合同

在首个 A/B/E cell 前冻结：

- panel manifest SHA；
- heldout references SHA；
- v3/v6 registry SHA；
- task015-06 reviewed-resource manifest/index；
- 17 stock keys；
- 模型与策略配置；
- RDKit/环境；
- 搜索参数；
- seeds；
- action matching 规范；
- run budget；
- 失败/超时处理。

固定搜索参数沿用 P4：

- seed = 0 / 1 / 2；
- quick 单阶段 12 s；
- 20 iterations；
- 120 nodes；
- branching 12；
- depth 2；
- top_k 5；
- candidate_stock=true；
- 单次服务全部 phase 墙钟 ≤60 s；
- 每次独立进程、新 run ID、新 MCTS；
- 禁止缓存结果或 BFS 替代。

如实际接口字段名变化，只允许等价映射并记录，数值不得按成绩优化。

## G5：执行真实 A/B/E + 旧能力回归

### 新面板矩阵

最小 12 目标时：

- 12 targets × 3 seeds × 3 arms = **108 cells**。

最大 18 目标时：

- 18 × 3 × 3 = **162 cells**。

每个 cell 必须保存：

- request/manifest/run ID；
- 生成、融合、截断、过滤动作；
- original outcome index；
- node creation trace；
- wall time/nodes/iterations；
- reference match；
- 失败/超时/未知；
- domain template/scope/source binding。

不得挑 seed、删失败、只重跑失败或成功单元。

### 旧能力回归

v6 改变运行资产后必须重新执行旧 17 目标 ×3 seed 的 E 回归，共 **51 cells**：

- 旧 4 SS、5 C、7 O 参照三 seed 创建保持；
- 旧 1b 按既有规则单列，不把历史缺口写成新退化；
- v3 54 模板指纹保持；
- v4/v5 历史载荷仍可加载；
- 17 stock keys、reviewed resources、模型、PUCT、通用过滤不漂移。

### P5 搜索硬预算

独立 `outputs/task016-p5/v1/run_ledger.jsonl`：

| 用途 | 上限 |
| --- | ---: |
| 新面板首轮 A/B/E | 162 |
| 旧能力首轮 E regression | 51 |
| 首轮最大 | 213 |
| 若实现 bug 污染结果，完整受影响矩阵重验 | 最多再 213 |
| 工程/service/package 真实尝试 | 54 |
| **P5 总硬上限** | **480** |

纯结构编码、模板单步 replay、哈希审计不算 MCTS。任何真实树搜索、失败、超时、工程探针均按合同计账。

## G6：核心迁移硬门

C 与 SS **分别**计算，不能把两类合并后平均过门。

### 6.1 候选迁移

定义：

- `N_family`：冻结 complete holdout 数；
- `N_gap_family`：A、B 都正常但都未过滤保留完整主参照的不同目标数；
- `G_family`：上述 gap 中 E 正常保留完整主参照，且动作来自 P5 build-supported scope、不是 exact seed replay 的不同目标数。

每类必须同时满足：

- `N_family >= 6`；
- `G_family >= 3`；
- `G_family / N_gap_family >= 50%`；
- 成功目标来自 ≥2 个 holdout closure groups；
- E 相对 A **和** B 的净完整参照覆盖均 > 0；
- A/B 已有完整参照在 E 中的损失 = 0；
- `N_gap=0` 时 ratio=null 且迁移门失败，不得写 100%。

### 6.2 真实 MCTS node transfer

每类至少 **3 个不同 holdout targets** 同时满足：

- A seed0/1/2 全部正常；
- B seed0/1/2 全部正常；
- A、B 三 seed 都没有实际创建完整主参照动作；
- E seed0/1/2 全部正常；
- E 三 seed 都实际创建完整主参照动作；
- 成功集合覆盖 ≥2 个 holdout closure groups；
- `exact_seed_instance_match=false`；
- node/action trace 可以从结果文件回算。

“模板能 apply”“候选生成过”“过滤后看见”均不能替代真实 node creation。

### 6.3 允许的核心能力声明

只有 C 与 SS 两类的 6.1 和 6.2 都通过，才允许写：

> C 与糖—糖范围在本冻结开发留出上均显示新底物迁移，并进入真实 MCTS。

若只有一类通过，只能分轴报告一类 Completed、一类 Partial；不得使用“TASK-016 核心泛化能力已证明”这类整体措辞。

## G7：独立终验、报告与状态更新

至少验证：

1. P3/P4 protected inputs 零漂移；
2. P4 reconciliation 可由哈希重算；
3. build/holdout zero leakage；
4. C scope supports/controls 全过；
5. SS scope supports/controls 全过；
6. v6 payload/manifest/config packaged copy 字节一致；
7. v3/v4/v5 旧注册表仍可加载且指纹不变；
8. 运行账本与所有真实 cell 数一致；
9. 每个迁移指标能从逐 cell 结果重算；
10. 旧能力回归逐 seed 完整；
11. 全量本地 tests 通过，数量不得少于起草时已验证的 151 项；新增 P5 合同测试必须包含在总数内；
12. 无资产环境明确跳过受限资产项，不把 skip 当 pass；
13. package/out-of-checkout 加载 v6 的默认关闭与 fail-closed 行为；
14. `git diff --check`；
15. 原始/受限数据未进入 Git；
16. 最终 REPORT、STATE、任务/报告导航与冻结事实一致。

## 七、必须新增的合同测试

至少增加覆盖以下错误模式的自动测试：

- C01/C04 不能在 build 与 holdout 同时出现；
- 任意 build support 不能进入 holdout；
- 同一 canonical reaction 多来源只能计一个目标；
- 同一 canonical acceptor 多上下文不能满足“2 acceptor”；
- deferred/inferred 不进入 N_family；
- holdout exact reaction 不存在于 runtime_instances；
- C3 与 SS O6 被隔离范围不能被 v6 恢复；
- v6 必须显式从合格增量组装，不能整体继承 v4；
- panel SHA 在首个 A/B/E 后不得改变；
- 指标重算必须区分 null 与 0；
- exact support replay 不得计为 transfer；
- node transfer 必须读取真实 node/action trace；
- 来源总账三种口径不能互相覆盖；
- 缺/改 manifest 或 packaged config 漂移必须 fail closed。

## 八、计划产物与职责

| 层 | 计划产物 |
| --- | --- |
| baseline | approval.json、execution_baseline.json、protected_hashes.json |
| reconciliation | p4_reconciliation.json、p4_fact_crosswalk.jsonl |
| sources | query_plan/ledger、acquisition manifests、source_accounting.json |
| admission | reaction_records.jsonl、identity_checks.jsonl、canonical signatures |
| split | exposure_ledger、source_group_edges、split_manifest、panel_manifest、heldout_references、unselected |
| build | scopes.json、runtime_instances、templates、template_source_manifest、support_replay、boundary_results |
| evaluation contract | evaluation_contract.json、registry/review/model/config bindings |
| runs | run_ledger、cell manifests、action/node traces、legacy regression |
| metrics | metrics_by_family、gain/loss/net coverage、cost/accounting |
| engineering | replay、asset-free/package、tests、budget、protection final |
| closeout | audit.json、delivery_manifest.json、REPORT-016-P5、STATE/navigation updates |

具体文件名可调整，但职责不能省略。

## 九、硬验收清单

- [ ] P4 冻结面板事实明确为起点 C=1、SS=5，不再把未冻结 C01/C04 写成现成 holdout。
- [ ] P4 source whole-task accounting 与阶段 discovery 数字已分口径记录。
- [ ] P4/P3 历史载荷零漂移。
- [ ] 至少 1 个 C 新增/严格扩展 scope 由 ≥2 distinct canonical acceptors 支持。
- [ ] SS 至少 1 个合格 scope，经 P5 重新验证后进入 v6。
- [ ] 所有 build support replay 100%，边界违反 0。
- [ ] C holdout ≥6 complete / ≥2 groups。
- [ ] SS holdout ≥6 complete / ≥2 groups。
- [ ] 全局 holdout 12–18，deferred=0，build/holdout leakage=0。
- [ ] v6 默认关闭、fail closed、只含合格增量。
- [ ] A/B/E 三臂按冻结参数全部执行或失败如实保留。
- [ ] C：G≥3、G/N_gap≥50%、成功≥2 groups、对 A/B 净覆盖均>0、参照损失0。
- [ ] SS：同上。
- [ ] C：≥3 targets 在 A/B 三 seed 均不创建而 E 三 seed 均创建真实参照 node，成功≥2 groups。
- [ ] SS：同上。
- [ ] 旧 17×3 E 回归完成且无新增参照退化。
- [ ] P5 真实搜索总账≤480，未借旧预算。
- [ ] 全量测试不少于起草时 151 项且新增 P5 合同测试全过。
- [ ] 包外/无资产/重放/哈希/配置副本/保护终检全部通过。
- [ ] 新目标 actionable=false、evidence_closed=false、prediction_conditions_verified=false。
- [ ] training overlap、independent chemical validation、formal benchmark、vendor/release/production 状态不越级。
- [ ] REPORT/STATE/导航与实际冻结载荷一致。

## 十、停止条件

出现任一情况，停止对应科学轴并保留证据：

1. P3/P4 保护文件出现无法解释漂移；
2. C scope 无法在预算内得到 ≥2 distinct complete acceptor supports；
3. C 或 SS holdout 在完整去泄漏后仍 <6；
4. build 与 holdout 出现无法通过删除污染候选解决的 closure 泄漏；
5. 只有通过降低门槛、换分母、改 reference、调权重/PUCT/库存才能得到正结果；
6. 结构完整性需要依赖常见立体假设、下游终产物外推、数据库替代或未核图形；
7. 来源必须付费、登录或绕过访问限制；
8. 下载或搜索预算达到硬上限；
9. v6 无法默认关闭或无法保持 v3/v4/v5 旧行为；
10. A/B/E 实现 bug 污染结果且剩余预算不足以完整重验受影响矩阵；
11. 运行后发现 panel/split/scientific scope 必须改变——原运行作废并保留，回到 G2 重新冻结，不允许只修失败 cell；
12. C 或 SS 的核心迁移硬门不通过。

触发停止条件不允许通过“找到几个漂亮样例”改变 Completed 定义。最终状态按真实轴写 Partial 或 Blocked。

## 十一、验证命令约定

批准后实际入口可按实现细化，但应保持类似职责：

```bash
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B scripts/task016_p5_g0.py
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B scripts/task016_p5_sources.py
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B scripts/task016_p5_split.py
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B scripts/task016_p5_build.py
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B scripts/task016_p5_runs.py
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B scripts/task016_p5_verify.py
python3 -B scripts/operate.py TASK-016-P5 .venv-foundation/bin/python -B -m unittest discover -s tests -v
python3 -B scripts/operate.py TASK-016-P5 git diff --check
```

脚本名可以变化，但来源、split、build、run、verify 职责必须可独立运行和重算。

## 十二、必须提交的报告

执行无论 Completed、Partial、Blocked 或失败，都必须生成：

`docs/reports/REPORT-016-P5-c-ss-transfer-capability-closure.md`

REPORT 必须显式回答：

1. P4 报告与冻结产物的 C 面板/来源总账差异最终如何解释？
2. C01/C04 最终是 build、holdout 还是 unused？为什么？
3. 新 C scope 的 build supports 是哪些 distinct canonical acceptors？
4. C/SS 最终 holdout 各多少、来自多少 closure groups？
5. A/B/E 实际执行多少 cell，失败/超时多少？
6. C/SS 的 N、N_gap、G、G/N_gap、净覆盖、损失分别是多少？
7. C/SS 各有多少目标满足真实三-seed node transfer？
8. 旧 17×3 能力是否退化？
9. 哪些结果只能支持“冻结开发留出迁移”，哪些科学门仍未关闭？
10. 是否存在任何执行中自发现错误、被 supersede 的中间结果或完整矩阵重跑？

执行收口时最小更新 `STATE.md`、任务/报告导航以及必要的 `ARCHITECTURE.md` 职责。P4 历史文件不追改。

## 十三、修订记录

- 2026-10-07 v0.1：根据所有者要求，将对 TASK-016-P4 的独立调查结果转为后续闭环合同。起草事实包括：P4 工程/151测试成立；最终 frozen panel 实为 C1/SS5；P4R-C01/C04 尚未进入最终 holdout；v5 无 C 新范围；P4 final source accounting 为 45 HTTP / 63,180,976 B / reuse 74 / 5 article versions / 9 attachments；A/B/E 与迁移指标至今未执行。合同据此把“C build-side 范围 + C/SS leakage-free holdout + A/B/E + 真实 node transfer + 旧能力回归”设为不可替代的核心完成链。本轮仅起草，不执行科学/搜索工作。
