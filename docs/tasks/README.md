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

## 编号与命名

```text
TASK-NNN-short-title.md
REPORT-NNN-short-title.md
```

- 任务 ID 在仓库内唯一且递增。
- TASK 与 REPORT 必须使用相同编号和短标题。
- 同一任务范围内的补充合同使用 `-PN` 后缀（如 `TASK-007-P1-source-relocation.md`），对应报告使用相同编号与短标题。
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
