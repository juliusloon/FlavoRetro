# 任务合同

`docs/tasks/` 保存每次实质性操作在执行前形成的任务合同。TASK 规定授权范围、验收标准和停止条件；它不是执行结果的记录。

## 目录与文件职责

本目录是项目操作治理的“事前合同”层，与同级的 `docs/reports/`（事后事实报告）相互对应。

| 文件 | 用途 |
| --- | --- |
| [README.md](README.md) | 说明本目录的编号、状态和使用规则。 |
| [TEMPLATE.md](TEMPLATE.md) | 新建任务合同的标准模板。 |
| [TASK-001-governance.md](TASK-001-governance.md) | 独立根与治理骨架的建立合同。 |
| [TASK-002-admission.md](TASK-002-admission.md) | 历史资源快照复制与来源登记合同。 |
| [TASK-003-resources.md](TASK-003-resources.md) | 资源重新解析与结构 QC 合同。 |
| [TASK-004-runtime.md](TASK-004-runtime.md) | 独立实时 MCTS 与共享服务合同。 |
| [TASK-005-workbench-evaluation.md](TASK-005-workbench-evaluation.md) | Web 工作台与开发对照合同。 |
| [TASK-006-topology.md](TASK-006-topology.md) | 糖苷连接结构诊断与历史完整性核对合同。 |
| [TASK-007-handoff.md](TASK-007-handoff.md) | 最终验收与交接物合同。 |
| [TASK-007-P1-source-relocation.md](TASK-007-P1-source-relocation.md) | TASK-007 范围内的笔记来源路径修复补充合同；Partial，指针切换被所有者搁置。 |
| [TASK-008-human-github-handover.md](TASK-008-human-github-handover.md) | 人接管整理与 GitHub/论文导向合同。 |
| [TASK-009-docs-detailing.md](TASK-009-docs-detailing.md) | 治理文档详细化合同。 |
| [TASK-010-web-completion.md](TASK-010-web-completion.md) | Web 工作台完整化、布局修复与项目独立收口合同。 |
| [TASK-011-topology-web.md](TASK-011-topology-web.md) | 糖苷连接拓扑审计接入 Web 界面（有效性判断可视化）合同；所有者人工批准（代行授权已于 2026-09-25 收回）。 |
| [TASK-012-foundation-readiness.md](TASK-012-foundation-readiness.md) | 数据库、算法工程合同、独立 Python 包、GitHub 同步、前端能力覆盖的统一验收合同；含 2026-09-26 现场核查；已获所有者 human_direct 批准，G1—G5 全部通过，Completed；私有交付提交与 CI 已核查。 |
| [TASK-013-web-ui-design.md](TASK-013-web-ui-design.md) | 已完成移动优先、对比度和可访问性呈现层合同。 |
| [TASK-014-domain-triage.md](TASK-014-domain-triage.md) | human_direct 批准；领域总分类、糖苷重点审核、笔记 guide、本地试点及标注/评测协议；Completed。 |
| [TASK-015-ord-coverage-review-cards.md](TASK-015-ord-coverage-review-cards.md) | human_direct 工程授权；ORD 当前镜像覆盖与 60 卡审核准备 Completed；实际 gold 未执行。 |
| [TASK-015-P1-agent-review-ord-analysis.md](TASK-015-P1-agent-review-ord-analysis.md) | 60 卡代理审核与 ORD 深析 Completed；不构成独立人审。 |
| [TASK-015-P2-scifinder-inbound.md](TASK-015-P2-scifinder-inbound.md) | 九个用户 SciFinder RDF 接收、去重、卡片连接和定向化学缺口核对 Completed。 |
| [TASK-015-P3-human-review-handoff.md](TASK-015-P3-human-review-handoff.md) | Completed；已有所有者审核回传，53 条结构/分类开发 gold + 7 排除，代理委托溯源保留。 |
| [TASK-015-P4-triage-rule-revision.md](TASK-015-P4-triage-rule-revision.md) | 人审校准回灌的筛选规则修订 task015-p4-v2；Completed（补登记索引行，合同与报告原已交付）。 |
| [TASK-016-open-glycoside-expansion.md](TASK-016-open-glycoside-expansion.md) | Completed（2026-10-06 v0.2）；开放接口与4个精确来源O成键模板，默认关闭；4/4参照与12/12真实MCTS配对补回，来源/预算/重放验收通过；C/糖间成键及新底物泛化未覆盖。 |
| [TASK-016-P1-open-glycoside-library-expansion.md](TASK-016-P1-open-glycoside-library-expansion.md) | Completed（agent_delegated、r4预算240）；54新反应/47新模板、5范围、7/12留出开发补回，51审计通过；正式评测/独立化学边界保持。 |
| [TASK-016-P2-c-sugar-transfer-validation.md](TASK-016-P2-c-sugar-transfer-validation.md) | Partial（2026-10-06；human_direct执行授权）；工程Completed，新增1C/2糖间范围、旧4SS三seed修复；两类新6目标/2出处面板未形成，新A/B/D未执行，科学阈值保持。 |
| [TASK-016-P3-new-reaction-admission-and-transfer.md](TASK-016-P3-new-reaction-admission-and-transfer.md) | Partial（2026-10-07；agent_delegated 执行授权）；工程与新反应准入 Completed（34 新反应 C12/SS22、3 个显式 v4 范围模板默认关闭、E 臂 51 单元零退化），C/SS 迁移因留出面板不足未执行（null）。 |
| [TASK-016-P4-p3-admission-correction-and-transfer-completion.md](TASK-016-P4-p3-admission-correction-and-transfer-completion.md) | Partial（2026-10-07；human_direct 批准、agent_delegated 阶段决定）；纠偏工程与纠偏后准入 Completed（34/34 重审，C 12→8、SS 22→16、总 24），v5 显式默认关闭且非 v4 继承，C3 与 SS 1→6 两范围结构性撤出；面板 C3/SS5 均低于 ≥6 硬门，A/B/E 未执行（null），搜索尝试 0。 |
| [TASK-016-P5-c-ss-transfer-capability-closure.md](TASK-016-P5-c-ss-transfer-capability-closure.md) | **Partial**（2026-10-07；human_direct 批准、agent_delegated 阶段决定）；P4 reconciliation Completed；C 计数面板 7 目标/5 组、SS 4 目标/3 组；新准入 2 条结构完整 C 反应并隔离 3 个虚构来源。**P5-ERR-06 已撤回旧“C scope 不泛化”结论**：旧探针实际使用 derive_template_smarts 的精确实例模板并漏掉 scoped_smarts，连第二个 build support 都不命中；故 P5 实际未建成 C scope，C 迁移是否可测未回答。7 个 C 目标中 5 个仍缺运行时产品结构，v6 未建成；**A/B/E 0 cell、搜索尝试 0/480**，迁移指标 null。 |
| [TASK-016-P6-c-scope-runtime-transfer-closure.md](TASK-016-P6-c-scope-runtime-transfer-closure.md) | **Partial**（2026-10-07，agent_delegated批准/阶段决定）；正确C scope构建2/2、边界0违反；C完整6目标/4组但applicability0/6→停止条件6 scope_holdout_domain_mismatch；SS纠正后1目标/1组→停止条件1，两轴A/B/E0/指标null。default-off v6 56模板89实例，旧17×3无新增损失、177本地测试/147无资产通过+30跳过，3410保护0漂移，账本62/480。 |
| [TASK-016-P7-domain-aligned-transfer-closure.md](TASK-016-P7-domain-aligned-transfer-closure.md) | **Partial（执行终止，2026-10-13）**；C-E02/SS-E02/C-E03正式development_epoch_incomplete；fresh C0/SS0、科学0 cell、metrics=null，P2未验收。 |
| [TASK-016-P7-closeout-20261013.md](TASK-016-P7-closeout-20261013.md) | Completed（终止行政收口）；P7总体Partial，epoch账82→85；不恢复R80、不修G7、不建新epoch。[报告](../reports/REPORT-016-P7-closeout-20261013.md) |
| [TASK-016-P8-evidence-rescue-feasibility.md](TASK-016-P8-evidence-rescue-feasibility.md) | Completed（诊断性完成）；当前交接纠偏及H1/H5裁定见下行，原交接不作为科学放行。 |
| [TASK-016-P8-H1-H5-governance-rulings.md](TASK-016-P8-H1-H5-governance-rulings.md) | Completed（书面治理与4条真实曝光补记）；当前epochs已由P7-CLOSEOUT正式终止，G7接入仍未完成。[报告](../reports/REPORT-016-P8-H1-H5-governance-rulings.md) |
| [TASK-015-P5-p0p1-evidence-closure.md](TASK-015-P5-p0p1-evidence-closure.md) | Completed（2026-10-05）；所有者采纳代理最终裁决，60 卡/508 笔记/名称/身份/供应全部定案，不再等待人工回填；未翻转 preflight。 |
| [TASK-015-06-review-into-search.md](TASK-015-06-review-into-search.md) | Completed（2026-10-05，agent_delegated）；审核成果已默认进入库存准入、逐步/末端/资源展示和运行指纹；17库存键保持、原配置/排序/评分不变，未启动TASK-016。 |

## 编号与命名

```text
TASK-NNN-short-title.md
REPORT-NNN-short-title.md
```

- 任务 ID 在仓库内唯一且递增。
- TASK 与 REPORT 必须使用相同编号和短标题。
- 同一任务范围内的补充合同使用 `-PN` 后缀（如 `TASK-007-P1-source-relocation.md`），对应报告使用相同编号与短标题。2026-10-05 所有者明确要求本轮使用数字后缀 `15-XX`，故审核结果接入任务命名为 `TASK-015-06`；既有 P1–P5 原编号保持，06 承接 P5，不另建同义 P6。
- 一个 TASK 只定义一项可明确判定“完成”或“未完成”的操作。
- TASK 批准后不得静默改写范围；范围变化必须留下修订说明并重新批准。

## 状态

- `Proposed`：拟议，等待批准，不得执行；
- `Approved`：已批准，可在合同范围内执行；
- `In Progress`：执行中；
- `Completed`：已完成验收，且已有对应 REPORT；
- `Partial`：部分完成，REPORT 必须说明未完成部分；
- `Blocked`：已触发停止条件；
- `Rejected`：未获批准；
- `Reverted`：结果已被后续提交回退。

批准可由 agent 按用户授权代行；此时批准记录必须写 `agent_delegated` 并注明授权依据，禁止写成 `human_reviewed`。agent 代行不等于人工审核。

新任务以 [TEMPLATE.md](TEMPLATE.md) 为模板创建。TASK 只说明“应做什么”；实际结果只写入对应 REPORT 和 Git。

## 阅读约定与常用术语

TASK-001—008 的合同文本在 TASK-009 由速记体扩写为详细格式；扩写只补结构与可核验事实，不改变原范围与结论。编号合同中的背景、验收勾选均保留所属操作当时的含义；当前项目状态以根目录 `STATE.md` 为准。

| 原术语 | 本目录使用的中文含义 |
| --- | --- |
| candidate / production | 候选 / 生产：资源与系统的治理状态；本项目全部资源与系统均为 candidate，无 production。 |
| surrogate closure | 替代闭合：候选库存探索命中的路线终止方式，标记 surrogate / unreviewed_candidate_stock；actionable 始终为 false。 |
| evidence_closed | 证据闭合：路线叶子全部由已确认证据支撑；当前搜索结果中始终为 false（未经独立审核）。 |
| partial | 部分路线：存在未解决叶子的路线；默认无已确认库存时返回 partial 是真实覆盖缺口，不凑路线。 |
| MCTS / PUCT | 蒙特卡洛树搜索 / 其节点选择公式；每次普通搜索都新建 MCTS，不读结果缓存，不回退 BFS。 |
| run / run ID | 一次搜索的独立进程与标识，逐次保存在 `outputs/runs/` 下。 |
| manifest | 清单，绑定输入、版本、行数、哈希等审计信息。 |
| preflight | 正式评测前的合同检查，见 `flavoretro.evaluation`。 |
| replay | 重放：用同一构建器重跑并比较输出逐字节一致。 |
| cell | 目标 × 引擎 × seed 的对照单元（开发对照共 12 cell）。 |
| agent_delegated | agent 按用户授权代行批准，不等于人工审核。 |
| 零收率不等于缺失 | 收率为 0 是测量结果，不得当作数据缺失处理。 |
| research_candidate | `metadata/release.json` 中的系统状态：保留候选、不认证为生产。 |

文件名、命令、字段、状态码、哈希和来源原词保留原文，以便与实现和证据对应。正文采用中文叙述，必要的原文术语附中文说明。
