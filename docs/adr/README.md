# Architecture Decision Records

[ADR-012](ADR-012-source-bound-lab-handoff.md)：实际来源见证与自包含实验开发交接。

最新[ADR011](ADR-011-source-priority-and-prefix-preservation.md)：来源优先级、有限O-乙酰结构分组、真实中间前缀与碳/杂原子标记分轴。

最新[ADR-010](ADR-010-continuous-research-ranking.md)登记连续研究优先级、全前沿排序、重复库存叶纠偏和历史展示投影。

ADR 用于记录会长期影响数据语义、可复现性或研究结论的决定。

ADR 不记录某次 operation 修改了哪些文件，也不替代 TASK、REPORT、STATE 或 Git：

- Git：what changed；
- REPORT：what this operation did；
- STATE：where the project is now；
- ADR：why a durable design is this way。

只有在一个决定会约束未来多个任务、存在真实备选方案且需要保留选择理由时，才创建 ADR。普通重命名、一次性修复和任务执行记录不创建 ADR。

命名格式：`ADR-NNN-short-title.md`（本仓库统一使用 ADR-NNN 前缀；模板文件为 `0000-template.md`）。每份 ADR 至少包含：状态、日期、负责人、背景、决定、备选方案、影响与风险、复审条件。状态可为 `proposed`、`accepted`、`superseded` 或 `rejected`。

## 现有 ADR

| 文件 | 决定 |
| --- | --- |
| [ADR-001-independent-rebuild.md](ADR-001-independent-rebuild.md) | 独立根、三线职责、批准与证据分轴。 |
| [ADR-002-search-evidence.md](ADR-002-search-evidence.md) | 先可解释的实时研究产品，再逐证据晋级。 |
| [ADR-003-repo-orientation.md](ADR-003-repo-orientation.md) | 一次性脚本归档、文档分层、GitHub 清单驱动。 |
| [ADR-004-teaching-layer-and-web-architecture.md](ADR-004-teaching-layer-and-web-architecture.md) | 教学/文献与四页界面。 |
| [ADR-005-foundation-workspace-and-index.md](ADR-005-foundation-workspace-and-index.md) | 独立工作区、不可变版本、派生 SQLite 与包资源。 |
| [ADR-006-method-delivery-and-independent-evaluation.md](ADR-006-method-delivery-and-independent-evaluation.md) | TASK-016按方法及有限开发结项，TASK-017承担正式独立评价；有效负结果与方法增益分开，P7历史终止保持。 |
| [ADR-007-research-evaluation-admission.md](ADR-007-research-evaluation-admission.md) | TASK-017分开评价准备、科研运行与供应/production/发布；任务局部证据真实放行，旧门及G0停止保持历史。 |
| [ADR-008-futurehealth-project-split.md](ADR-008-futurehealth-project-split.md) | 教学代码拆分FutureHealth、P0受控/P1待审；后续TASK/REPORT/STATE仍在FlavoRetro登记。 |

- [ADR-009：完整模型前沿、探索下界与精确库存表示](ADR-009-search-and-stock-identity.md)

[ADR-013](ADR-013-addressable-workbench-navigation.md)：可寻址层级子页、浏览器历史与URL/会话状态分工。

[ADR-014](ADR-014-modular-frontend-project.md)：前端源码分层、公共组件与确定性构建；现有静态运行合同保持。
