# REPORT-015-P3：60 卡人工复核包交付（阶段 1）

对应 [TASK-015-P3](../tasks/TASK-015-P3-human-review-handoff.md)。所有者选择方案 A 后，Cano 已完成可独立打开的本地审核交接包；本报告仅覆盖阶段 1。实际所有者审核文件尚未回传，后续缺口裁决及 gold 冻结尚未执行，TASK 状态为 AwaitingUserReview。

## 交付

本地入口：`outputs/review/task015-p3/handoff-v2/index.html`，使用说明同目录 `README.md`，可表格查看的逐卡缺口表 `gap_register.tsv`。页面包含全部 60 个固定 ID、原反应结构、TASK-015-P1 代理结论/证据/缺项和 P2 新 RDF 的严格结构、反应号、仅文献线索三种连接；30 条糖苷重点被标记，13 条争议/否决/来源异常列为 P0，另 25 条为 P1、22 条为 P2。优先级仅影响审核顺序，不决定科学标签。

每卡由实际审核者选择「同意代理判断 / 更正 / 暂存疑 / 排除」，分别勾选亲自核对过的结构分类、一手原文实例、条件/收率；勾选原文/收率必须提供具体定位/说明。更正、存疑、排除必须给出理由。浏览器本地保存草稿，可导入、导出带固定 ID、源 SHA、版本、逐卡审核者/时间和修改历史的 JSON。导出统一为 `human_submission_pending_validation`，不写入 `human_reviewed` 或 gold。空白包中的人审字段均为空。

`gap_register.tsv` 按卡号列出代理需要补的材料、用户问题及新 RDF 连接；其中的空白人工列便于表格查漏，但正式交接应使用页面导出的 JSON。页面和载荷含受限数据库衍生材料，保存在 Git 忽略的 `outputs/`；代码、合同和报告不含原始 RDF。不改 TASK-014 冻结样本、P1 代理审核、P2 接收、v3、active 或 MCTS。

## 验证

首版 v1 的自动初次渲染会把页面滚动到卡片，视觉复核发现页首说明不在初屏。保留 v1 作为失败记录，修正后交付 v2；v2 首屏滚动为 0，桌面和手机截图保存在本地验证目录。


生成器 `scripts/build_task015_p3_handoff.py` 校验 TASK-014 原 60 卡空白人审、P1 代理审核 60 ID、P2 交叉表 60 ID 同序，并冻结三份输入的 SHA-256。独立浏览器检查 `scripts/check_task015_p3_handoff.py` 在托管环境通过：60 ID/源及输出哈希、0/60 初始人审、P0/P1 筛选、结构 SVG、保存与刷新恢复、JSON 导出/导入、错源哈希拒绝、1440/390/320 像素无横向溢出、JS 错误 0。合成填写只在 `outputs/validation/task015-p3-handoff-v2/` 中标记 `BROWSER TEST ONLY`，不代表所有者审核。

## 下一阶段门槛

等待所有者按 README 审核并提供导出的 JSON 路径。收到后 Cano 将校验 60 ID/哈希/实际审核者/逐卡字段，依据更正与缺口做来源/结构复核，给每个标签轴明确 verified / uncertain / excluded；合法无法取得的证据保留未核实，不用题名或数据库身份填补。最后交所有者确认闭环，再冻结**开发** gold 的证据合格子集。60 条均为 `development_exposed`，即便完整人审也不会变成未见盲测；正式 benchmark、生产准入及公开发布仍属其他任务。

## 阶段 2：所有者审核回传、P2 代填与校验（2026-09-29）

所有者回传导出 JSON（packet `task015-p3-handoff-v2-203856e17fcd`），已原样存档 `data/inbox/scifinder/task015-user/task015-user-review-20260929.json`（SHA-256 `dec2b71e…8bae1`），未改动任何字段。身份校验：packet ID、60 条 ID/卡号/源 SHA 与交接包逐一绑定一致；三份输入（TASK-014 review、P1 代理审核、P2 交叉表）SHA-256 与 packet 冻结值一致；逐卡修改历史重放落到提交状态一致。

### 人审与代填

38 张（全部 13 P0 + 25 P1）为所有者 `ljx` 亲审提交；22 张空白卡经核对恰为全部 22 张 P2 对照卡，按所有者 2026-09-29 会话指示「P2 对照卡全部同意代理判断」由 Cano 代填，记录为 `agent_delegated`（reviewer `Cano/agent-delegated`），不冒充 human_reviewed。代填前逐卡执行一致性核对：P1 结论均为 retain_candidate(20)/primary_checked(2)、primary_checked 两卡 P1 来源状态确为 primary_instance_verified、TASK-014 机器特征均 parsed、全部组件 SMILES RDKit 复检通过、4 张机器 unknown 卡确为 P1 修正的路线支持步骤。代填仅勾选结构轴（代理复检层级）；来源/收率轴一律未勾选。

### 结论矩阵与更正处置

| P1 结论 × 所有者裁决 | 张数 |
| --- | --- |
| retain_candidate → agree（31 人审 + 22 代填中 20） | 51 |
| retain_candidate → exclude（卡 28） | 1 |
| primary_checked → agree | 9 |
| needs_adjudication → agree / exclude / revise（卡 5） | 3 / 3 / 1 |
| reject_claim → agree（同意否决）/ exclude | 2 / 3 |

P1 的 7 张待裁决卡全部获得所有者裁决；5 张否决声明卡全部确认。60 卡终态：52 agree、1 revise、7 exclude；保留开发候选 53 张（人审 31、代填 22），其中糖苷重点 28 张、P1 一手实例已核 9 张。

更正与排除处置：卡 5（revise）所有者注明为白杨素 + 4-溴丁醇成醚、非糖苷相关——与 P1 糖苷轴判定（无糖）及 TASK-014 旗标（domain_glycoside=False）一致，仅作显式归类记录，无数据冲突。卡 27（exclude）经结构复读为酪氨酸 → 黄酮 C-糖苷多产物，导出把整条生物合成路线压缩为单步「反应」；机器 scaffold_construction+glycosyl_related 旗标在结构层为真、反应级无效，记为路径压缩型假阳性校准点。卡 28/51/52/54/55 按所有者理由排除（无实用价值/内容空/产物无 SMILES/反应不完整），其 P1 来源多为摘要级或不可得。卡 53 原论文已正式撤稿（撤稿注记 DOI 10.1007/s11164-024-05454-8）：对其余 59 卡、635 行新 RDF 记录及 P2 交叉表做精确 token 扫描，撤稿论文 0 命中，无泄漏。

### 标签轴就绪度（gold 冻结依据）

| 轴 | 状态 |
| --- | --- |
| 结构/领域/分类 | 60/60 有结论：30 人审确认 + 1 人审更正 + 7 人审排除 + 22 代填确认（agent 级） |
| 一手来源实例 | 0/60 所有者亲核（38 张人审 source_checked 均未勾选）；9 张为 P1 代理 primary_instance_verified，51 张 not_checked |
| 条件/收率 | 0/60 核对 |

按合同，仅代理审核的轴不得升为 human_reviewed/gold：22 张代填卡与 9 张 P1 代理一手核验均不能冒充人审。人审可冻结的结构轴 gold 候选为 31 张（30 agree + 1 revise，含糖苷重点多数）；来源/收率轴暂无可冻结人审证据。

### 本阶段产物与状态

`outputs/review/task015-p3/ingest-1/`：`delegated-fills.jsonl`（22 条代填及核对证据）、`review-merged.jsonl`（60 卡终审与逐轴 reconciliation）、`summary.json`（矩阵与排除/更正清单）、`manifest.json`（stamp 2026-09-29T08:41:05Z、载荷哈希）。生成器 `scripts/task015_p3_ingest.py` 确定性可重放。未改动：所有者提交原件、交接包、TASK-014 冻结样本、P1/P2 输出、v3、active/MCTS。60 卡保持 development_exposed，0 production。

TASK-015-P3 状态更新为 OwnerClosurePending：60/60 已审（38 人审 + 22 代填），等待所有者确认闭环并裁决 gold 冻结范围（见报告待讨论清单）；确认前不冻结 gold、不启动 TASK-016。

## 阶段 3：所有者闭环决定与 development gold 冻结（2026-09-29）

所有者对本报告阶段 2 待讨论清单作出三项决定，构成合同意义上的闭环确认：

1. **方案 B（53 张全量 gold）**：不要求所有者对 22 张 P2 对照卡逐一亲审；按其指示由 Cano 直接以 agree 代填并入 gold。据此生成 `outputs/review/task015-p3/final/review-final-60.json`（提交 schema、60/60 有结论；38 张为所有者原件、22 张保留 `Cano/agent-delegated` 身份与所有者指示引用），由 `scripts/task015_p3_gold_freeze.py` 从 ingest-1 确定性生成，所有者提交原件未改动。
2. **gold 仅覆盖结构/分类轴；agent 审核计入 gold**：按所有者明示决定执行。22 张代填卡以 agent 溯源计入（`reviewer_types: ["agent"]`，注明"所有者委托代理按 agree 代填；agent 复检层级，非 human_reviewed"），不冒充 human_reviewed。
3. **机器假阳性模式立项修订**：7 张排除卡的模式已登记，新合同 TASK-015-P4（Proposed，待所有者批准执行）。

### gold 冻结产物 `outputs/review/task015-p3/gold-v1/`

- `gold.jsonl`：53 张保留卡（52 agree + 1 revise 卡 5，后者附所有者更正原文）。每卡冻结 P1 代理标签（domain_relevance、transformation_labels、glycoside_assessment 等）与逐卡结构轴溯源：所有者亲核结构 30、人审确认但未亲核结构复选框 1（卡 24）、代填 agent 复检 22；糖苷重点 28。
- `excluded.jsonl`：7 张排除卡及校准模式标签（路径压缩、摘要空内容、撤稿源、产物无结构、导出不完整）。
- `summary.json` / `manifest.json`：轴覆盖、未冻结轴声明（一手来源 0/60 人审亲核、收率 0/60，均不冻结）、边界、输入/载荷哈希、stamp 2026-09-29T09:05:00Z。

更正记录：首版 gold-v1 在生成数分钟内发现汇总字段 `owner_checked_structure` 把代填卡的 agent 复检误计入所有者亲核，当場删除并修正为三个细分字段后重新生成；无任何下游引用，所有者提交原件与 ingest-1 未受影响。

### 边界（不变）

53 张 gold 全部 `development_exposed`，仅用于开发校准，不得改名或用作未见盲测；不构成化学准确率证明；0 production；MCTS/搜索未接入；正式 benchmark、TASK-016（糖苷感知搜索）与公开发布仍需新的所有者批准。TASK-015-P3 状态 Completed。
