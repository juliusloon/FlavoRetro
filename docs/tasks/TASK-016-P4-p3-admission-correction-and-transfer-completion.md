# TASK-016-P4：P3准入纠偏与C/糖间迁移验收补全

## 合同元数据

- 任务 ID：TASK-016-P4；合同版本：v0.1；起草日期：2026-10-07。
- 状态：**Proposed（拟议）**。本轮仅根据所有者与 ChatGPT 对 TASK-016-P3 的联合复核起草并落盘合同；**尚未授权执行本合同中的来源采集、结构编码、模板修改、运行库切换或 MCTS**。
- 起草授权：所有者 2026-10-07 指示“把我们的讨论内容修建为一个新的 task 文件，明确写清其要求、分工、架构、验收标准、边界”，记为 human_direct，仅覆盖本合同起草。
- 执行授权：待所有者后续明确批准。批准后记录批准语句、日期、本合同 SHA-256 与预算；代理执行不得记为 human_reviewed。
- 人工负责人：项目所有者。
- 执行者：待批准后登记；可由一个主执行 agent 完成，但必须按本文规定隔离“准入/构建/评估/终验”职责与数据视图。
- 工作区：`/home/ljx/FlavoRetro`；基线分支 `main`；起草时 HEAD=`993b22f5e8eed5797d27f02c566af1b86a4b7880`。
- 工作区状态：起草时存在 TASK-015/016 系列与前序工作的大量未提交交付；**不得 reset、clean、checkout --、按 HEAD 恢复或覆盖用户/其他任务改动**。HEAD 只作定位，执行前以现场文件 SHA 重新冻结实际基线。
- 前序合同：[TASK-016-P3](TASK-016-P3-new-reaction-admission-and-transfer.md)；前序报告：[REPORT-016-P3](../reports/REPORT-016-P3-new-reaction-admission-and-transfer.md)。P3 历史文件保持原样，不静默改写历史结论。
- 本任务性质：**纠偏 + 补全**。不是降低 P3 门槛，也不是把 P3 的 `Partial` 文案改成 `Completed`；只有重新满足硬门后，P4 才能声明相应轴完成。
- 所有命令与项目内写入必须经 `scripts/operate.py` 登记；原始/受限来源、运行结果和本地科学载荷继续不进入 Git。

## 目标与完成定义

TASK-016-P3 已取得实际来源增量、候选反应整理、显式 v4 工程接入和旧能力回归，但复核发现其“新反应准入 Completed”和部分“新增范围”判断高于合同证据实际支持程度。本任务的目标是：

1. **逐条重审 P3 的 34 个“新反应”及其支持上下文**，把“命名/路径身份已知”与“完整可计算单步结构已准入”分开，形成可重算的纠偏准入层；
2. **撤销或降级证据不足的范围支持**，尤其处理 C3 2-hydroxyflavanone 中间体的结构外推和 SS 1→6 同一受体重复计数问题；
3. 在不污染 holdout 的前提下，**补足 C 与糖间（SS）两类的结构完整 build 支持和结构完整留出面板**；
4. 从可信的 P2/v3 基线重新构建一个显式、默认关闭的纠偏运行版本；**不得把整个 P3/v4 直接当可信科学基线继续继承**；
5. 面板和运行资产通过预检后，执行 P3 原本未完成的真实 A/B/E 三臂对照，证明或否定“当前模型不会提出、而新增范围能力能补回”的迁移；
6. 保持旧能力、旧资产、证据边界和科学准入状态，不把工程可运行性冒充独立化学验证。

### 分轴完成定义

本任务最终必须分别判定以下四轴：

| 轴 | Completed 的最低条件 |
| --- | --- |
| correction_engineering | P3 资产冻结、纠偏载荷独立、显式新版本默认关闭、字节重放/包外/无资产/旧版本回归/保护终检通过 |
| corrected_reaction_admission | 经纠偏后仍有 C≥8、SS≥8、总≥16 个 **structure_complete_admitted** 的不同完整单步；重复来源/同反应上下文不重复计数 |
| C_transfer | C 类结构完整 holdout ≥6目标/≥2闭包组，合格 C 范围能力通过支持/边界，A/B/E 候选与真实迁移硬门通过 |
| sugar_sugar_transfer | SS 类结构完整 holdout ≥6目标/≥2闭包组，合格 SS 范围能力通过支持/边界，A/B/E 候选与真实迁移硬门通过 |

**整体 Completed 仅在四轴全部 Completed 时成立。** 任一科学轴不足则整体 Partial；未执行指标写 `null`，不得写成 0。工程通过不能抵偿准入或迁移失败。

## 背景：本任务要纠正的已确认问题

本节只记录本轮复核已经从 P3 合同、报告、源码和载荷中直接确认的问题，不新增未经证实的化学判断。

### 1. “34 个全部完整准入”与实际结构状态不一致

P3 报告称 34 个新共价反应“全部具备完整单步身份”，但评估侧 `heldout_references.jsonl` 同时明确：

- `P3R-C12`：`structure_encoding=deferred`；
- `P3R-SS23`：`structure_encoding=deferred`；
- `P3R-SS22`：`structure_encoding=complete`。

因此“名称/连接身份可描述”不能等同于“完整结构可计算准入”。按 P3 合同要求，留出参照需有完整单步前体；deferred 记录不能计入可运行迁移面板。

### 2. C3 范围把终产物证据外推给未完整赋值中间体

P3 候选记录对相关 2-hydroxyflavanone C-glucoside 中间体本身明确保留了诸如：

- “intermediate itself not assigned (MS-only)”；
- “only matched by calculated m/z / no authentic reference”；
- 结构证据依赖脱水后 vitexin/isovitexin 或 orientin/isoorientin 的标准品/NMR/LC-MS。

但 `scripts/task016_p3_build.py` 的 `C_SUPPORTS` 又将对应完整中间体 SMILES 硬编码，并把 identification 写成“source NMR-assigned 2-hydroxyflavanone C-glycoside”等措辞。该写法把**脱水后终产物的 NMR/标准品证据错误转嫁给未完整赋值中间体**。

因此当前 `C_hydroxyflavanone_C3` 不能作为已验收的新范围能力继续使用，除非本任务找到并绑定中间体本身的完整结构证据或等价、可审计的同一物种身份链。

### 3. SS 1→6 范围的“两条支持”并非两个不同受体

P3 `SS-rhamnoside-O6` 的两个 runtime support：

- 来自两个来源/酶上下文；
- 但 `reaction_id` 同为 `P3R-SS03`；
- acceptor、target、reference signature 均相同。

P3 合同要求每个新增范围由“≥2 个不同完整受体源实例”支持。**两个出处不能把同一个 canonical acceptor / 同一个共价反应计成两个不同受体。** 因此当前 1→6 范围按合同只能视为 1 个不同受体支持，未过范围硬门。

### 4. 名义留出面板不等于可计算留出面板

P3 名义冻结面板为 C 1、SS 2，但其中两个结构 deferred。按“可真实执行 A/B/E 的完整主参照”计：

- C 当前结构完整留出：**0**；
- SS 当前结构完整留出：**1**（P3R-SS22）。

因此后续缺口不能继续按“C 还差5、SS还差4”计算；执行本任务时必须从完整可计算参照重新计数。

### 5. 核心新目标迁移验收未执行

P3 因面板不足未执行 A/B/E 新面板矩阵，C/SS 候选迁移和真实节点迁移均为 `null`。51 次 E 臂旧目标回归只证明旧能力保持，不能证明新增范围补回模型新缺口。

## 证据基线与历史保护

起草时已核对以下 P3 文件 SHA-256，执行前必须现场重新确认；若不一致，先解释差异，不得覆盖：

| 文件 | 起草时 SHA-256 |
| --- | --- |
| `docs/tasks/TASK-016-P3-new-reaction-admission-and-transfer.md` | `1dfcda3a91d857cef0a867811b67c0f6ebb8906d9e6b6664abf1f323f05b4479` |
| `docs/reports/REPORT-016-P3-new-reaction-admission-and-transfer.md` | `db9dc42661302d67397011893c8343e454d3ba716e2919766beff7572094b783` |
| `outputs/task016-p3/v1/reaction_records.jsonl` | `8832db218293c41845c8b3ba7457fcf929f7227e28a6d984ef28fde5bd7ff504` |
| `outputs/task016-p3/v1/identity_checks.jsonl` | `ad1e3e7813db37640fdbadd1707d7b04833711160f2acf2ec666c1e0e1221eb1` |
| `outputs/task016-p3/v1/runtime_instances.jsonl` | `639ab46d9b0c6fc57a2181e622f2544c5d683d4f6c58abc1af2de063eeef6561` |
| `outputs/task016-p3/v1/templates.jsonl` | `48775ffe5e422caf7d21016c84940c3ea3120c33eddba14a511827e1cf7a180c` |
| `outputs/task016-p3/v1/heldout_references.jsonl` | `52b88e9613859ec0172d15342d384d66c876ffd5255ecbe39525f3abfba11b26` |
| `outputs/task016-p3/v1/panel_manifest.json` | `20ee83c92a49b26722c748ed3876a572bddba228c8bdf105c734df43b2d62823` |

P3/v1 为**历史证据与错误现场**，必须保持不可变。P4 不直接改写 P3 的 reaction_records、runtime_instances、templates、panel、heldout、run ledger 或 REPORT；所有纠偏写入独立命名空间。

## 架构与职责分层

### 总体架构

P4 使用“冻结历史 → 纠偏准入 → build-only 构建 → holdout-only 评估 → 独立终验”的单向数据流：

```text
P3/v1 immutable evidence
        |
        v
P4 correction/admission ledger
   |                     |
   | build partition     | holdout partition
   v                     v
P4 build-only scopes     evaluator-only references
   |                     |
   +----------+----------+
              v
       frozen P4 split
              |
              v
   explicit corrected v5 runtime
              |
              v
       A / B / E matrix
              |
              v
       independent audit/report
```

### 关键版本原则

- P2/v3（54 模板）仍是**可信比较基线 B**。
- P3/v4 保留为历史实现与候选能力证据，但**不能整体作为 P4 的可信科学父版本**。
- 若 P4 需要运行增量，建立显式默认关闭的 **v5**：
  - v5 = P2/v3 + 仅经 P4 重新验收通过的 P3/P4 增量；
  - 不得“v4 全继承后再标记两条无效”；
  - v1/v2/v3/v4 文件、指纹和旧行为全部保留。
- 若最终没有任何 C 或 SS 合格范围，允许不生成对应科学增量，但不得为了形成 v5 而保留不合格模板。

### 计划文件与目录职责

| 路径 | 职责与边界 |
| --- | --- |
| `docs/tasks/TASK-016-P4-p3-admission-correction-and-transfer-completion.md` | 本合同；批准后不得静默降门槛 |
| `docs/reports/REPORT-016-P4-p3-admission-correction-and-transfer-completion.md` | 最终事实；必须逐轴报告 Completed/Partial/Blocked |
| `outputs/task016-p3/v1/` | 历史只读证据，不修改 |
| `data/raw/task016-p4/` | 新取得原件/附件/图形裁剪，只读、本地、Git忽略 |
| `outputs/task016-p4/v1/` | P4 纠偏事实源：准入、身份、闭包、split、模板、面板、账本、指标、终验 |
| `scripts/task016_p4_audit.py`（计划） | 34 条 P3 反应及其上下文的确定性 re-admission audit |
| `scripts/task016_p4_sources.py`（计划） | 定向补证/补源与预算登记；不做无界大扫库 |
| `scripts/task016_p4_build.py`（计划） | 只从 structure-complete build 记录构建合格范围与 v5 增量 |
| `scripts/task016_p4_panel.py`（计划） | 闭包、split、完整 holdout 面板冻结；拒绝 deferred 计入 |
| `scripts/task016_p4_runs.py` 或 `flavoretro/task016_runs.py` P4 分支 | 独立搜索预算、原子预留、运行账本 |
| `scripts/task016_p4_verify.py`（计划） | 结构/支持/边界/泄漏/预算/旧能力/字节重放/保护终检 |
| `flavoretro/glycoside_library_v5.py`（如需） | 显式纠偏运行版本；只继承 v3 + P4 合格增量 |
| `configs/glycoside-library-v5.json` 及包副本（如需） | v5 唯一显式配置、载荷/来源/指纹绑定 |
| `tests/` | 只增加必要的纠偏合同、默认关闭、不同受体计数、holdout泄漏与旧版本不变性测试 |
| `STATE.md`、导航、`ARCHITECTURE.md` | 仅在执行完成后按实际事实最小更新；不改写历史报告 |

具体脚本名可调整，但职责层必须保留；不得把准入、build、holdout 和运行结果混成一个不可审计文件。

## 分工与隔离要求

本任务允许同一个执行 agent 完成全部技术工作，但必须保留以下**逻辑角色隔离**，并在产物中能证明每个角色拿到的数据不同。

### 所有者

- 批准或拒绝本合同；
- 仅在需要改变科学门槛、预算、访问付费/登录资源、改变项目范围或做新的人工化学裁决时重新介入；
- 不承担常规论文下载、SMILES手填、逐条运行或错误修复；
- 未亲自审核的结构不得记 `human_reviewed=true`。

### 准入/来源工作流

负责：

- 重审 P3 的 34 个新反应及 82 条已准入上下文；
- 补充必要原件、SI、图形和身份链；
- 生成 corrected admission ledger；
- 先完成身份和闭包，再分 build/holdout。

禁止：

- 看到 A/B/E 成绩后再改变身份、split 或主参照；
- 用数据库全结构、常见立体、脱水终产物或同源酶常识填补源材料缺失事实。

### 构建工作流

输入仅限冻结后的 **build partition**。负责：

- 选择结构完整 build 支持；
- 构建/修复范围模板；
- 运行支持重放和边界测试；
- 生成 v5 build-only 载荷。

禁止：

- 读取 holdout 精确 target/precursor 结构来扩宽 SMARTS、调 prior、加白名单或选择范围；
- 将同一 canonical acceptor 的不同论文/酶上下文重复计为两个不同受体。

### 评估工作流

在模板与 split 均冻结后读取 evaluator-only holdout。负责：

- A/B/E 请求计划；
- 完整参照匹配；
- candidate / filter / node creation 证据；
- family-level metrics。

禁止：

- 将 holdout 内容回流构建；
- 用历史 P1/P2/P3 成绩代替 P4 新矩阵；
- 用成功单元筛选面板。

### 终验工作流

只读核查：

- P3/v1 未漂移；
- corrected admission 与源证据一致；
- distinct acceptor 计数无重复膨胀；
- holdout 全部 complete；
- runtime 不含 holdout；
- v5 只继承 v3 + 合格增量；
- 指标分母和账本完整；
- 测试/包外/无资产/旧能力回归真实执行。

终验可以由同一主 agent 的独立脚本完成，但不得使用“构建脚本自己输出 passed”作为唯一证据。

## G0：批准、现场基线与保护快照

批准后，任何来源获取、结构编码、模板写入或 MCTS 前必须：

1. 读取 PROJECT.md → STATE.md → ARCHITECTURE.md → P2/P3 TASK/REPORT → 本合同；
2. 登记执行授权、本合同 SHA、工作区 HEAD、dirty 清单与 P3/P2 关键文件 SHA；
3. 冻结：
   - P2/v3 54 模板、runtime、配置和交付清单；
   - P3/v1 全部决定性文件；
   - task015-06 reviewed resources；
   - 17 库存键、模型、搜索配置、旧账本；
4. 新建 P4 独立预算与输出目录；不得借用 P3 未耗尽的 429 次搜索余额，也不得修改 P3 ledger；
5. 写出 `baseline_manifest.json` 与 `approval.json`；
6. 如现场 SHA 与本合同起草时记录不符，先查来源；未解释前停止对相关资产写入。

## G1：P3 34 个新反应的逐条 re-admission audit

### 四级状态

P4 必须对 P3 所有 34 个新 reaction_id 及其支持上下文重新判定，且只能使用以下状态之一：

1. `structure_complete_admitted`
   - 完整受体、实际供体、主要产物均有可解析结构；
   - 新键原子、糖型、必要立体、保护状态和上下文明确；
   - 结构编码可直接追溯源材料中的结构图/明确命名+完整赋值/同一物种可审计身份链；
   - 不是从后续脱水、脱保护、氧化、重排后的终产物反推唯一中间体结构。

2. `identity_complete_structure_deferred`
   - 单步反应和连接身份可描述；
   - 但一个或多个关键物种缺完整结构编码；
   - 可保留为来源知识，**不计完整准入、不进 build、不进可计算 holdout**。

3. `provisional_inferred`
   - 当前结构需要机器推断、常见立体假设、数据库替代或终产物反推；
   - 仅作为候选，不计准入。

4. `rejected`
   - 反应不是目标单步、身份矛盾、重复旧反应、证据不足或被更强证据否决；
   - 保留原因和原记录，不删除历史。

禁止继续使用 P3 中“`identity_complete=true` 但 `missing_elements` 仍写关键结构未赋值”的混合语义作为完整准入依据。

### 每个 structure_complete_admitted 记录的最低字段

每个可计数反应必须有：

- stable reaction_id；
- source SHA、DOI/PMCID/附件 SHA、页/段/图/化合物编号；
- experiment/assay/condition ID；
- context type（enzymatic / chemical 等）；
- 完整 reactants、主要 product；
- canonical isomeric SMILES 或等价可重算结构表示；
- actual donor、acceptor、sugar identity；
- new bond atoms / linkage / anomeric or required stereochemistry；
- aglycone/core、parent glycan、保护状态；
- raw conditions、yield 原值及缺失状态；
- encoding method；
- identity evidence axis；
- reviewer_type；
- admission status；
- canonical reaction signature；
- canonical acceptor signature；
- source closure group；
- development exposure 状态。

### C3 特别纠偏

对 P3R-C01/C02 及任何用于 `C_hydroxyflavanone_C3` 的支持：

- 终产物 vitexin/isovitexin/orientin/isoorientin 的 NMR、标准品或 LC-MS **不能自动认证前一步 2-hydroxyflavanone-C-glucoside 中间体的完整结构**；
- 若原文只给中间体 MS / calculated m/z，默认降为 `identity_complete_structure_deferred` 或 `provisional_inferred`；
- 只有中间体本身的明确结构图、完整赋值、可核同一编号 SI，或其他不跨反应步骤的可审计身份链，才可升级为 `structure_complete_admitted`；
- P3 build 脚本中的 “source NMR-assigned 2-hydroxyflavanone C-glycoside” 不得继续作为证据字段。

### 纠偏计数

重审后重新计算：

- C structure_complete 新反应数；
- SS structure_complete 新反应数；
- 总数；
- build 候选数；
- holdout-eligible 数；
- deferred / inferred / rejected 数。

要把 corrected count 与 P3 原称 C12/SS22 并列展示，不能覆盖历史数字。

**corrected_reaction_admission Completed 仍要求 C≥8、SS≥8、总≥16。** 若重审后不足，允许在 G2/G3 中补证或补新来源；预算结束仍不足则该轴 Partial。

## G2：范围能力纠偏

### 计数键必须冻结

“不同完整受体”以 `canonical_acceptor_signature` 去重，不以 PMCID、DOI、酶名、实验次数或上下文计数。

同一个：

- acceptor 结构；
- target 结构；
- covalent reaction signature；

即使被两篇论文、两个酶或多个 assay 重复确认，也只能作为**一个受体/一个共价反应**计范围支持；可增加来源上下文数，但不能增加 distinct acceptor 数。

### 当前三个 P3 范围的处理要求

1. `C_hydroxyflavanone_C3`
   - 当前状态：**not accepted pending correction**；
   - 必须先解决中间体完整结构证据；
   - 如不能解决，从 P4 合格 runtime 增量中排除；
   - 若找到新的、结构完整且不同受体的 C 类 build 支持，也可构建新的 C 范围，不要求保住原模板名。

2. `rhamnoside_glucoside_O2`
   - 不预设通过；
   - 重新核对两个支持是否确为不同 canonical acceptor、完整结构、同一声明范围；
   - 通过后可作为 P4 合格增量候选。

3. `rhamnoside_glucoside_O6`
   - 当前两个 P3 support 先按 **1 个不同受体**计；
   - 必须补到 ≥2 个不同 structure-complete canonical acceptor；
   - 仅新增第二篇出处但反应/受体相同不算；
   - 若补不到则该范围不进入 P4 合格增量。

### 每个合格范围的硬门

每个 P4 接受的新增/严格扩展范围必须：

- 至少 2 个不同 `canonical_acceptor_signature`；
- 至少 2 个 structure_complete_admitted build reactions；
- 全部 support 100% 重放主参照；
- 不依赖 holdout 精确结构；
- 每范围至少 4 条预登记相关边界；
- 边界违反 0；
- 新键/远端结构/立体/供体/parent glycan/母核上下文检查完整；
- exact support、scope support、prediction conditions 分轴；
- `human_reviewed=false` 除非所有者实际逐条审核。

每类 C、SS 至少要有 1 项满足以上条件的真正新增或严格扩展范围，才允许该类进入迁移验收。

## G3：定向补证与补源

本任务不是再次无界扫描开放文献。优先级依次为：

1. 修复 P3 已知结构缺口（尤其已有 SI/figure 但未编码的材料）；
2. 为 C 类找到可结构完整准入、可形成 build 或 holdout 的不同反应；
3. 为 SS 1→6 或其他 SS 范围补真正不同的完整受体；
4. 补足 C/SS 结构完整 holdout；
5. 只有上述不足时才做新的定向发现。

### 已知优先线索

至少重新处置：

- P3 明确保留的未编码图形：PMC11502824 / PMC12790375 / PMC13421352；
- P3 126 条 retained_pending_identity；
- P3R-C12（PMC13035923）结构图/SI；
- P3R-SS23（PMC6899944）acylated mini-MbA 结构；
- 所有可能提供第二个不同 SS 1→6 acceptor 的已取得资料；
- C3 中间体的原始图/SI/化合物编号，而不是继续依赖终产物。

### 来源准入规则

- 作者结构图、化合物编号+完整赋值、可定位 SI 可作为编码依据；
- OCSR/OCR 只能给候选，必须逐关键键/立体复核；
- 数据库可辅助同一物种身份链，但不能代替实验原文；
- 名称 + MS、质量增量、酶名、终产物、同源酶常识均不能单独补齐完整结构；
- 不要求用户手工搜论文、手填 SMILES 或人工下载；
- 登录/付费/许可受限时登记不可得，不绕过访问控制。

### P4 独立来源预算

P4 不借 P3 来源预算。批准后默认硬上限：

- 新直接 HTTP 请求 ≤ **2,000**；
- 新下载字节累计 ≤ **2 GiB**；
- 新文章版本 ≤ **100**；
- 新附件 ≤ **180**；
- 新 metadata 键 ≤ **5,000**；
- 并发 ≤4；
- 单 URL 最多2次普通网络尝试；恢复链单独登记；
- 单文件 ≤256 MiB，未知 Content-Length 流式截断；
- 达任一上限即停止相应采集并报告缺口，不为“耗尽预算”下载无关材料。

如执行者在 G0 认为该预算与现场剩余缺口明显不匹配，只能在**首个新下载前**提出修订并重新批准，不能事后扩容。

## G4：来源闭包、split 与可计算留出面板冻结

### split 原则

在任何 P4 新模板构建和 A/B/E 成绩出现之前：

1. 冻结 corrected reaction bank；
2. 构建 source/reaction/exposure closure；
3. 冻结 build / holdout；
4. 冻结每个 holdout 的主单步完整参照；
5. 写 `split_manifest.json`、`source_group_edges.jsonl`、`exposure_ledger.jsonl`、`panel_manifest.json`、`heldout_references.jsonl`；
6. 记录所有未选目标和理由。

同 DOI/PMC/SI、同原始实验、专利家族、同完整共价反应、明确重复使用实验必须闭包。已用于模板设计或结构范围推断的组件强制 build/calibration。

### 留出计数硬规则

只有满足以下全部条件的目标才计入面板：

- `structure_encoding=complete`；
- target 完整可解析；
- 主 reference precursors 完整可解析；
- reaction signature 明确；
- 来源闭包与 build 无泄漏；
- 没有在前序模板设计中暴露其精确结构/位点/供体范围；
- 一个化学目标只计一次，多 seed/多 assay/多论文复述不增加目标。

**任何 `deferred`、名称-only、图未核、关键立体 unknown 的记录可以保留，但不得计入 N_family。**

### 面板硬门

- C：≥6 个不同完整目标、≥2 个闭包组；
- SS：≥6 个不同完整目标、≥2 个闭包组；
- 全局 12–18 个目标；
- 每类最多9；
- 不看 A/B/E 成绩选目标；
- 每目标一个预冻结主参照。

起草时按可计算口径，P3 遗留基线视为 C=0、SS=1；执行时必须重新审计后更新，不能沿用名义 C1/SS2 直接扣差额。

若一类面板不足，允许另一类继续到预冻结工程验证，但整体不得 Completed；不足类 A/B/E 未执行指标写 null。

## G5：纠偏运行版本 v5

如 G1–G4 形成合格增量，则构建显式默认关闭的 v5。

### v5 继承关系

```text
A = optimized generic search, domain library off
B = A + frozen P2/v3 (54 templates, original build payload)
E = A + corrected P4/v5
v5 = P2/v3 + only P4-revalidated build increments
```

**v5 不得写成 v4 的直接可信继承。** v4 继续可加载用于历史重现，但其三个 P3 范围按 P4 纠偏结果分别标记，不自动进入 E。

### 运行资产要求

- 默认关闭；
- v1/v2/v3/v4 行为与指纹不变；
- 缺 P4 payload / SHA mismatch 必须 fail closed；
- runtime_instances 只含 build；
- heldout 精确参照不进入 runtime/config/package；
- cap/prior/weight、PUCT、模型、库存、通用过滤与 P3 原对照保持；
- 不用调参提高 holdout 成绩；
- action trace 保存生成→融合→过滤→node creation 全链；
- exact support 和范围迁移明确区分；
- 新目标始终 `actionable=false`、`evidence_closed=false`、`prediction_conditions_verified=false`，除非另有独立证据任务改变。

## G6：真实 A/B/E 迁移验收

只有 G4 面板和 G5 v5 通过 preflight 后才能执行。

### 固定参数

沿用 P3 冻结协议：

- seed：0 / 1 / 2；
- quick 单阶段 12 s；
- 20 iterations；
- 120 nodes；
- branching 12；
- depth 2；
- top_k 5；
- candidate_stock=true；
- 单次服务全部 phase 墙钟 ≤60 s；
- 模型、task015-06 审核视图、17 库存键、通用过滤一致；
- 每次独立进程、新 run ID、新 MCTS；
- 禁止缓存结果或 BFS 替代。

如现场实现已经使这些参数名改变，只能做等价字段映射并记录；不得改数值优化结果。

### 候选迁移指标

每类独立计算：

- `N_family`：冻结的完整不同目标数；
- `N_gap_family`：A、B 均正常，但均未过滤保留完整主参照的目标；
- `G_family`：上述 gap 中，E 正常保留完整主参照，且来自 P4 build-supported scope、不是 exact seed white-list replay 的不同目标。

硬门：

- C：G≥3；
- SS：G≥3；
- 各自 `G/N_gap ≥ 50%`；
- 成功来自≥2个不同留出闭包组；
- E 相对 A、B 均正净覆盖；
- 完整主参照损失=0；
- N_gap=0 时比率为 null 且迁移门不通过，不能写100%。

### 真实节点迁移指标

每类至少3个成功目标同时满足：

- A seed0/1/2 全部正常；
- B seed0/1/2 全部正常；
- A/B 三 seed 均未实际创建完整主参照动作；
- E seed0/1/2 全部正常；
- E 三 seed 均实际创建完整主参照动作；
- 成功目标覆盖≥2个闭包组；
- `exact_seed_instance_match=false`；
- node/action trace 可核对。

“模板生成”“过滤保留”“候选列表出现”均不能替代 node creation。

### 旧能力回归

v5 发生运行资产变化后，必须重新执行旧17目标×3 seed 的 E 回归（51 单元）：

- 旧4SS、5C、7O参照全 seed 创建保持；
- 旧1b 继续单列，不把历史未补回当新退化；
- P2/v3 54 模板指纹保持；
- 默认/v1/v2/v3/v4 可加载行为保持；
- 17库存键、reviewed resources、模型、PUCT、通用过滤不漂移。

## 搜索预算

P4 使用独立账本 `outputs/task016-p4/v1/run_ledger.jsonl`，不修改 P3/P2/P1 旧账。

| 用途 | 计划/硬上限 |
| --- | --- |
| 新面板首轮 A/B/E | 12–18目标 ×3 seed ×3臂 = 108–162 |
| v5 旧能力首轮 E 回归 | 17×3 = 51 |
| 首轮最大验证计划 | 213 |
| 受实现缺陷影响后的完整矩阵重验容量 | 最多再213 |
| 工程/service/包外真实尝试 | 54 |
| **P4 全任务保守硬上限** | **480** |

规则：

- 首个 `tree_search` 前必须绑定 P4 approval SHA 和预算；
- 每次尝试前原子预留，失败/超时也占预算；
- mock/合成错误 fixture 标注非真实但计工程保守尝试；
- 纯结构解析、模板单步 replay 不算 MCTS；
- 不借 P3 剩余额度；
- 修实现错误后，若错误影响矩阵结论，必须按预先定义的受影响完整矩阵重跑，不能只重成功或失败单元；
- 若修复改变来源身份、模板科学语义或 split，原 holdout 视为受污染，回到 G1/G4 重新冻结，不能直接继续跑。

## G7：验证、报告和当前状态更新

### 必须产物

`outputs/task016-p4/v1/` 至少应包含以下职责：

| 层 | 最低产物 |
| --- | --- |
| 授权/保护 | approval、baseline_manifest、protected hashes |
| P3纠偏 | p3_reaudit、corrected_reaction_records、identity_checks、status_crosswalk |
| 来源 | query plan/ledger、raw manifest、attachment parse、source accounting |
| 去重/闭包 | old/new map、canonical reaction/acceptor signatures、source edges、exposure ledger |
| split | split manifest、panel manifest、heldout references、unselected records |
| build | runtime_instances、templates、template_source_manifest、support replay、boundaries |
| 运行 | request manifest、run ledger、cell status、action/node trace |
| 指标 | metrics_by_family、gain/loss/net coverage、legacy regression |
| 工程 | byte replay、tests、asset-free/package checks、budget audit、protection final |
| 收口 | audit、delivery_manifest、REPORT |

文件名可不同，但职责不得缺失。

### 纠偏报告必须显式回答

1. P3 原34条经重审后，C/SS 各有多少 `structure_complete_admitted`、deferred、inferred、rejected？
2. P3 三个范围中哪些被保留、降级、撤出？每个范围有几个 **distinct canonical acceptor**？
3. 当前真正可计算 holdout C/SS 各多少、来自多少闭包组？
4. A/B/E 实际执行了多少 cell，失败/超时多少？
5. C/SS 各自 N_family、N_gap、G、G/N_gap、真实三seed节点迁移数是多少？
6. 旧能力是否退化？
7. 哪些 P3 报告陈述被 P4 的当前事实 supersede，但历史文件为何保留不改？
8. 哪些科学门仍未关闭？

### 报告状态

最终 REPORT 必须分轴：

- correction_engineering；
- corrected_reaction_admission；
- C_transfer；
- sugar_sugar_transfer。

不能只写一个 Overall。

## 硬验收清单

| 硬门 | C | SS / 共同要求 |
| --- | --- | --- |
| P3逐条纠偏 | 12个原C反应全部有四级状态 | 22个原SS反应全部有四级状态；34/34零遗漏 |
| 完整新反应准入 | ≥8 structure_complete 不同单步 | ≥8；总≥16；重复来源/上下文不重复计 |
| build受体 | 每个接受范围≥2不同 canonical acceptor | 同左；同一反应不同论文不重复计 |
| 范围增量 | ≥1真正新增/严格扩展且支持/边界全过 | ≥1；不合格P3范围不得偷偷继承 |
| holdout | ≥6 complete不同目标/≥2闭包组 | 同左；deferred=0；全局12–18 |
| 来源泄漏 | 0 | 0；runtime中holdout exact references=0 |
| 候选迁移 | G≥3 且 G/N_gap≥50%，成功≥2组 | 同左；对A/B净覆盖>0，参照损失0 |
| 真实迁移 | ≥3目标A/B三seed均不创建、E三seed均创建 | 同左；成功≥2组、真实node证据 |
| 旧能力 | 旧5C/7O三seed保持 | 旧4SS、apiose/既有支持保持；旧1b单列 |
| 工程 | v5默认关闭、v3/v4旧行为不漂移 | 字节重放、测试、包外、无资产、预算、保护全部通过 |
| 科学边界 | actionable/evidence_closed/prediction conditions 不越级 | training overlap、independent validation、formal/release 不越级 |

附加勾选：

- [ ] P3/v1 历史决定性文件 SHA 全部不变。
- [ ] C3 中间体没有再使用“终产物 NMR=中间体 NMR”的证据转移。
- [ ] SS 1→6 没有把同一 canonical acceptor 的两个来源计成两个受体。
- [ ] `structure_encoding=deferred` 没有进入 holdout 分母。
- [ ] v5 没有整体继承不合格 v4 科学增量。
- [ ] 所有支持实例可回到原件 SHA 和定位。
- [ ] 所有 MCTS 使用 P4 独立账本，预算未借旧任务。
- [ ] 最终 REPORT/STATE/导航与实际结果一致。

## 非目标与禁止项

本任务明确不做：

- 不训练/微调神经网络；
- 不调整 PUCT、通用评分、模型权重、库存或 KnownHazards 以提高迁移成绩；
- 不扩大候选库存来制造路线闭合；
- 不做正式 blind benchmark、TASK-017/018；
- 不把 agent 结构复核记为 human_reviewed；
- 不把 NMR/标准品的下游终产物身份跨步骤转移给未赋值中间体；
- 不把数据库 identity、质量增量、酶名或图回放当独立化学验证；
- 不修改 `metadata/release.json` 把系统升格 production；
- 不做供应商当前在售认证；
- 不做 UI 改版；
- 不公开受限原始文件；
- 不执行 Git commit/push/tag/release，除非所有者另行明确授权；
- 不修改 P1/P2/P3 历史 TASK/REPORT/ledger/冻结载荷来“修正历史”。

## 停止条件

出现以下任一情况，停止对应科学验收并保留证据：

1. P3/P2 受保护文件出现无法解释的漂移；
2. structure_complete 需要依赖未证实的常见立体、数据库替代或跨步骤终产物反推；
3. build 与 holdout 来源/反应闭包泄漏；
4. 模板必须读取 holdout 精确结构才能形成声明范围；
5. 某范围支持少于2个 distinct canonical acceptor；
6. C 或 SS holdout 低于6个 complete 目标；
7. 运行版本无法做到默认关闭或无法保持 v3/v4 旧行为；
8. 搜索/下载预算到顶；
9. 必须付费、登录或绕过访问限制才能继续；
10. 修复需要改变冻结科学指标、搜索参数、库存或模型；
11. A/B/E 实现缺陷污染整个矩阵且剩余预算不足以完整重验。

触发停止条件后可继续做不受影响的另一类/工程审计，但必须把受影响轴记 Partial 或 Blocked，不能通过缩小分母、换面板或改定义补过。

## 建议执行顺序

批准后按以下顺序推进，禁止跳过 G1/G4 直接跑 MCTS：

```text
G0  approval + baseline/protection
G1  re-audit all 34 P3 reactions
G2  correct scope support counting / quarantine invalid scopes
G3  targeted evidence completion + bounded new sources
G4  freeze complete build/holdout split and panel
G5  build corrected explicit v5 from v3 + validated increments
G6  run fresh A/B/E + legacy regression
G7  independent verify + REPORT + STATE/navigation update
```

建议提供等价可执行入口，例如：

```bash
python3 -B scripts/operate.py TASK-016-P4 .venv-foundation/bin/python -B scripts/task016_p4_audit.py
python3 -B scripts/operate.py TASK-016-P4 .venv-foundation/bin/python -B scripts/task016_p4_sources.py
python3 -B scripts/operate.py TASK-016-P4 .venv-foundation/bin/python -B scripts/task016_p4_panel.py
python3 -B scripts/operate.py TASK-016-P4 .venv-foundation/bin/python -B scripts/task016_p4_build.py
python3 -B scripts/operate.py TASK-016-P4 .venv-foundation/bin/python -B scripts/task016_p4_runs.py
python3 -B scripts/operate.py TASK-016-P4 .venv-foundation/bin/python -B scripts/task016_p4_verify.py
```

脚本不存在时由执行者在批准范围内实现；命名可调整，但每个职责必须能独立重算与审计。

## 必须提交的报告

无论 Completed、Partial、Blocked 或 Rejected，都必须生成：

`docs/reports/REPORT-016-P4-p3-admission-correction-and-transfer-completion.md`

并在执行收口时最小更新 `STATE.md`、任务/报告导航与必要的 `ARCHITECTURE.md` 当前职责。P3 历史报告保留，不追改；P4 报告负责说明哪些 P3 的当前接受判断已被 supersede。

## 修订记录

- 2026-10-07 v0.1：根据所有者与 ChatGPT 对 TASK-016-P3 的联合复核起草。明确四项纠偏事实：C3 中间体证据外推、SS 1→6 不同受体计数不足、名义留出中两个结构 deferred、A/B/E 未执行；保留 P3 原科学门槛并新增 distinct canonical acceptor / complete holdout / v3→v5 纠偏继承规则。本轮仅起草合同，未执行其科学或运行内容。
