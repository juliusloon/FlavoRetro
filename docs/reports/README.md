# 执行报告

`docs/reports/` 保存每次操作完成后的事实型执行报告。REPORT 记录实际改动、验证结果、偏差和遗留风险；它不重新定义任务授权范围。

## 目录与文件职责

本目录是项目操作治理的“事后事实”层，通过任务编号与同级的 `docs/tasks/`（事前任务合同）关联。

| 文件 | 用途 |
| --- | --- |
| [README.md](README.md) | 说明本目录的报告规则和各报告文件的职责。 |
| [TEMPLATE.md](TEMPLATE.md) | 新建执行报告的标准模板。 |
| [REPORT-001-governance.md](REPORT-001-governance.md) | 记录治理骨架建立的实际结果。 |
| [REPORT-002-admission.md](REPORT-002-admission.md) | 记录 114 个文件快照逐字节复制与来源清单登记的实际结果。 |
| [REPORT-003-resources.md](REPORT-003-resources.md) | 记录 3,059 条资源构建与两次重放逐字节一致验证的实际结果。 |
| [REPORT-004-runtime.md](REPORT-004-runtime.md) | 记录 MCTS 运行时交付与 25 项测试的验证事实。 |
| [REPORT-005-workbench-evaluation.md](REPORT-005-workbench-evaluation.md) | 记录 Web 工作台与 12 cell 开发对照的实际结果；TASK-009 补立。 |
| [REPORT-006-topology.md](REPORT-006-topology.md) | 记录糖苷连接结构诊断从 55 次往返失败修复到 0 的过程与验证事实。 |
| [REPORT-007-handoff.md](REPORT-007-handoff.md) | 记录最终验收与交接物的实际结果；TASK-009 补立。 |
| [REPORT-007-P1-source-relocation.md](REPORT-007-P1-source-relocation.md) | 记录 v2 来源定位的交付与搁置状态（Partial）；TASK-009 补立。 |
| [REPORT-008-human-github-handover.md](REPORT-008-human-github-handover.md) | 记录人接管整理与初始提交的实际结果。 |
| [REPORT-009-docs-detailing.md](REPORT-009-docs-detailing.md) | 记录治理文档详细化的实际结果。 |
| [REPORT-010-web-completion.md](REPORT-010-web-completion.md) | 记录 Web 工作台完整化、布局修复与项目独立收口的实际结果。 |
| [REPORT-011-topology-web.md](REPORT-011-topology-web.md) | 记录糖苷连接拓扑审计接入 Web 界面（有效性判断可视化）的实际结果。 |
| [REPORT-012-foundation-readiness.md](REPORT-012-foundation-readiness.md) | 记录数据库、算法合同、独立包、前端覆盖、GitHub/CI 的最终验收；Completed，五项工程门槛通过，科学晋级仍未闭合。 |

- 每个 REPORT 必须对应一个编号和短标题相同的 TASK。
- REPORT 记录实际发生的内容，而不是重复任务目标。
- “改动文件”、验证命令、结果、偏差、未处理问题和风险不可省略。
- 不使用“全面提升”“生产就绪”等缺少验收证据的表述。
- REPORT 不替代 `STATE.md`；REPORT 保存历史，STATE 只保存当前事实。

新报告以 [TEMPLATE.md](TEMPLATE.md) 为模板创建。即使任务处于 `Partial`、`Blocked` 或 `Failed` 状态，也必须留下 REPORT。

## 补立约定

REPORT-005、REPORT-007、REPORT-007-P1 为 TASK-009 补立：对应操作发生时未独立成文，后按模板依据 `operations/events.jsonl` 与 `operations/command-*.log` 中的操作记录补写。补立报告只收录可核验事实，无法核实处标注“未记录”。

## 离线复核说明

`operations/command-*.log` 与 `operations/*.json` 被 `.gitignore` 排除，不进入 Git。为使本仓库可独立复核，各报告中的关键命令输出已内联摘录；未摘录的原始记录仅存在于本地操作日志。

## 如何查阅文件说明

各执行报告的“改动文件”表按该操作的实际差异解释目录职责、具体文件用途，以及迁移或删除关系；涉及本地数据生成的报告，还在“实际改动”中说明快照、资源构建产物和验证输出的文件组成。

这些说明用于理解既有改动；报告中的计数、哈希、测试结果和未完成事项仍属于当时的操作记录。当前状态以根目录 `STATE.md` 为准，常用术语见[任务目录阅读约定](../tasks/README.md#阅读约定与常用术语)。
