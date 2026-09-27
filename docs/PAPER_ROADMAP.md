# 论文路线（PAPER ROADMAP）

当前系统状态：`metadata/release.json` 标记为 `research_candidate`，六个外部验证维度全部 unresolved / not_executed / not_performed。本路线把"最终论文"拆成可执行阶段；**任何阶段都不得用工程测试冒充化学验证**。下一阶段的任务主线与优先级见下文「下一阶段主线」一节。

## 阻断性缺口（写论文前必须关闭）

| 缺口 | 现状 | 关闭条件 |
|---|---|---|
| 模板/库存独立来源审核 | `primary_source_review: unresolved` | 有署名的人工化学审核记录，逐条 template/stock 晋级或否决 |
| 当前供应商证据 | `current_vendor_evidence: unresolved` | 可日期的供应/价格核查，与历史 listing 分开 |
| 独立化学标签 | `independent_chemical_labels: not_available` | 预注册评测 panel + 独立标注（人或文献双源） |
| 正式盲测 | `formal_benchmark: not_executed` | 冻结合同后一次性执行（evaluation.preflight 的 `formal_run_ready` 变为 true 才允许启动） |
| 结构诊断真值 | topology 只有开发自检 | 糖苷连接候选的人工标注子集，报告 precision/recall |

`evaluation.py` 的 preflight 是这道门的代码化形式：**先补齐前三行，formal 执行器才允许动工。**

## 下一阶段主线：从"工程正确"到"科学可评价"（TASK-014—018）

本节由所有者于 2026-09-26 提出并指示写入本路线，用于确定后续 TASK 的思路、范围与先后顺序。它是**方向性计划，不是已批准的 TASK 合同**：每一阶段动工前仍须按 [tasks/README.md](tasks/README.md) 的批准规则取得所有者**人工**批准，P2/P5 不接受 `agent_delegated`。

### 现状判断

项目已不缺水工程骨架，缺的是把现有工程能力转化为**可验证的科研贡献**。已具备：独立 Python 环境、v3 资源与 SQLite 只读索引、真实实时 MCTS、CLI/API/Web、CI、仓库外安装与较完整的浏览器工程验收。但 `metadata/release.json` 仍是 `research_candidate`，一手来源审核、当前供应商证据、独立化学标签、正式 benchmark 四项均未闭环。

因此后续瓶颈不是"再加页面或 API"，而是**独立 gold set 与冻结评测协议**。在它到位之前，现有 12-cell 开发比较只能说明工程行为，不能支撑算法优越性。

### 后续发展空间（按价值排序）

**D1 最高优先级——从"工程正确"升级到"科学可评价"。** 瓶颈不在功能数量，而在缺少独立 gold set：需要人工核对一批黄酮/黄酮苷反应（底物身份、断键位置、反应类别、原料可获得性），并冻结标签规范，之后才能执行真正的盲测。目前正式 benchmark 仍为 `not_executed`、独立化学标签 `not_available`，所以 12-cell 开发比较只说明工程行为，不能支撑算法优越性。

**D2 最有项目特色——P2 糖苷感知搜索。** 糖苷拓扑能力已相当扎实（识别候选糖苷连接、Web 高亮、关联文献），但它完全独立于 MCTS 的 expansion 与 scoring：系统"看得懂某些糖苷结构"，却不会用这种知识改变搜索决策。有研究价值的下一步，是把**经过验证**的糖苷信息转成受控的 action prior、candidate reranking、branch filtering 或 route scoring，再与普通 MCTS 在冻结协议下对照。该方向已列为工作台路线 P2，但须先冻结定义与评测协议。

**D3 明显能力缺口——反应家族识别。** 当前 47,836 个模型模板全部为 `0.0 Unrecognized`；工作台已有 27 个教学条目，但搜索产生的模板不能可靠落入这些类别（TASK-010 已指出旧教学层的命名家族与当前 USPTO/ringbreaker 数值 classification 不匹配）。可发展为独立的"反应语义层"：模板 → 结构变换 → reaction family，每条映射带来源、置信等级与人工复核状态。做扎实后，它既是界面改进，也是 P2 搜索约束与结果解释的基础。

**D4 搜索算法优化——排在科学评测体系之后。** PUCT、动作融合、去重、替代动作、转置与预算合同已经存在（TASK-012 修复了同次扩展重复状态与多产物 outcome index 两个真实缺陷），但 native 与 optimized 仍无严格等价的节点预算，早期搜索参数仍是 provisional、未经系统调优。后续可做预算归一基准（budget-normalized benchmark）、参数消融、PUCT 权重研究、template-policy 融合实验与不同转置策略比较，很可能成为论文的算法实验章节——但前提仍是先有可信评测集。

**D5 证据层——从"可追溯"到"可审核"。** v3 已解决工程追溯（3,059 条记录、123 个来源、SQLite 查询；508 条文献记录中 249 条命中原文 token、259 条只定位文件），但"文件定位/token 命中"不等于内容审核。值得增加审核工作流，如 `unreviewed → source_located → primary_checked → structure_checked → reaction_checked`，记录审核人、证据片段、日期与冲突，使项目从 evidence-aware 走向 evidence-auditable。

**D6 工作台——从研究展示工具升级为研究决策工具。** 四页入口、历史运行、资源 QC、教学、拓扑与 12-cell 开发比较均已存在，TASK-013 又把移动端、键盘操作、对比度与无障碍做到较完整。下一层不应只是继续美化，而应增加路线横向比较、候选步骤人工接受/拒绝、证据差异视图、route annotation、实验备注与可复现"研究会话"等真正辅助决策的交互。注意当前浏览器验收都是工程验收，没有真人可用性结论。

**D7 产品化与平台化——当前基本未展开。** HTTP 服务本质仍是本机开发服务器，同一服务进程门控，没有分布式调度、公开部署、任务恢复与真人使用测试；平台只验证过 Linux x86_64 / Python 3.10。若未来要支持实验室多人使用，可再做持久 job queue、任务恢复、权限与 workspace 隔离、共享运行库、服务器部署与 macOS/Windows 支持。这些工作对当前科研价值的边际收益低于独立标签与正式 benchmark。

以上 D1—D7 是本路线的价值排序编号。D2、D3 提到的"P2/P3"指 [WORKBENCH_ROADMAP.md](WORKBENCH_ROADMAP.md) 的工作台阶段编号，与本文件「阶段计划」的 P0—P3 不是同一套编号，引用时须注明。

### 主线任务序列（TASK-014—018）

按"最可能把 FlavoRetro 推向论文级成果"的顺序：

| TASK | 主题 | 对应方向 | 前置 | 批准要求 |
|---|---|---|---|---|
| [TASK-014](tasks/TASK-014-domain-triage.md) | 领域反应筛选与科学评测协议（含本地试点） | D1、D5 | 已完成规范和本地试点 | 已获 human_direct 批准；Completed |
| [TASK-015](tasks/TASK-015-ord-coverage-review-cards.md) | 已完成 ORD 覆盖与审核准备；人工 gold 仍待独立审核阶段 | D1 | TASK-014 的标签规范冻结；具体来源与人工实例确认仍待完成 | human_direct 工程授权；未自动授权科学标签/gold |
| TASK-016 | P2 糖苷感知搜索（受控接入 MCTS expansion/scoring） | D2 | TASK-014 的评测协议 + 经确认的糖苷信息 | 所有者人工批准；P2 不接受 `agent_delegated` |
| TASK-017 | 冻结 blind benchmark 并正式执行 | D1、D4 | TASK-015 的 gold set + `formal_run_ready` | 所有者人工批准 |
| TASK-018 | 消融、误差分析与论文结果整理 | D4、D6 | TASK-017 的冻结运行 | 所有者人工批准 |

### 并行线、论证链与启动前收口

- **并行低风险线**：反应家族映射（D3，工作台路线 P3）可在 TASK-014/015 期间作为低风险工程线推进，先建规范与来源；仍不得把教学材料冒充"已识别家族"。
- **论证链**：结构领域知识 → 可审计标签 → 搜索方法 → 冻结评测 → 可复现实验 → 限域科学结论。下一阶段的主线因此不再是"多做功能"，而是形成完整论证链。
- **启动前先收口**：TASK-013 已完成并通过验收，但合同未授权提交/推送，UI 改动仍待所有者决定是否入库；在开工上述主线前，先收敛工作区状态更稳妥。

## 阶段计划

- **P0 证据整理（无新实验）**：来源定位已由 TASK-012 获批恢复并切换 v3（249 条 token 命中、259 条文件定位但 token 未命中）；剩余 token/原文内容审核仍需科学任务；产率字段覆盖率统计；3 个名称冲突库存条目的处置决定。产出：数据审核附录素材。
- **P1 人工审核与标注**：template/stock 逐条人工审核（多名审核人 + 分歧记录）；糖苷连接诊断标注 50—100 分子子集。产出：`production_eligible` 首批记录、诊断真值表。
- **P2 预注册正式评测**：定义目标 panel、对照基线、指标（闭合率需 evidence 定义、成本分布、多样性）；冻结合同后跑正式盲测（开发对照的 12 cell 规模远不够）。产出：`outputs/evaluation/formal-*` 与统计报告。
- **P3 论文产物**：图表全部从 `outputs/` 已存运行重绘（禁止手改数值）；附录含 sources 清单、哈希、运行 ID；代码打版本标签并公开仓库。

与下一阶段主线的对应：P0/P1 → TASK-014、TASK-015；P2 → TASK-017；P3 → TASK-018；工作台路线 P2（糖苷感知搜索）→ TASK-016。

## 可直接复用的工程素材（论文方法部分）

- 每次搜索独立进程、独立 run ID、结果哈希入 manifest（可追溯性）。
- 原生/优化树同资产、同时间/迭代预算的开发对照运行器（节点上限不等价）（`flavoretro/evaluation.py`）。
- 证据分级输出（partial / surrogate / evidence_closed，默认全 false）。
- 资源准入：逐记录 SHA-256、解析失败保留、零收率≠缺失。
- 结构诊断：立体化学感知的图往返回归测试（`tests/test_topology.py`）。

## GitHub 发布检查清单（所有者执行）

- [x] 选择代码许可证（已确定：代码 Apache-2.0、项目原创文档 CC BY 4.0，同 CondRxnBench，2026-09-21）
- [ ] 确认仓库无受限数据：`data/`、`outputs/` 在 .gitignore；`metadata/` 只含哈希与清单
- [ ] 替换 repo-local git 身份为所有者 GitHub 身份
- [ ] README 补充仓库地址与引用方式（建议届时加 CITATION.cff）
- [ ] 环境可复现声明：pyproject 固定版本 + pip-freeze + 模型资产获取说明
- [ ] 打版本标签（如 v0.1.0-research-candidate）

TASK-012 只同步现有私有仓库并保留已有 repo-local Git 身份，不替代本页的公开发表身份、引用、许可或科学检查清单。Linux/Python 3.10 独立安装已验证，锁清单改用 environment/requirements-linux-py310.lock；其他平台、标签和公开发布仍需单独批准。

## 2026-09-27 TASK-014 收口

TASK-014 已按所有者本会话批准完成“先建立黄酮总分类、糖苷为重点审核子集”：领域/guide/标注与评测规范见 [protocols/](protocols/README.md)，实际结果见 [REPORT-014](reports/REPORT-014-domain-triage.md)。508 条笔记 guide 和 2,301 条本地导出全部保留；60 条开发审核样本包含 30 条糖苷重点。所有输入均 development_exposed，不能直接作为未见盲测。

TASK-015 后续需建立独立审核的开发 gold，并明确独立保留来源；外部 ORD 子集接入另立有来源/许可/训练重叠检查的任务。TASK-017 除 gold 外仍依赖一手来源、供应证据及已审核 template/stock 投影；本次协议完成不使 preflight 自动通过。TASK-015—018 未自动授权，原序列保持。

## 2026-09-27 TASK-015 收口

所有者授权的实际合同为 ORD 覆盖与卡片准备，53 当前镜像源和 60 卡已完成，见 REPORT-015 与 protocols/ORD_COVERAGE_V1.md。既有路线的人工 gold 目标仍未达成：应先初筛 30 糖苷重点、补 4 条定向来源材料，并用新来源/标签接管合同明确审核者和分歧处理。这个工程 TASK 完成不满足 TASK-016/017 的化学前提；上游 train/test 数据不成为本项目盲测。
