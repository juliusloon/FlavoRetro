# Architecture Decision Records

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
