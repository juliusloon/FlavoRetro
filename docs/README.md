# FlavoRetro 文档导航

机器契约（agent 先读）：[PROJECT.md](../PROJECT.md) → [STATE.md](../STATE.md) → [ARCHITECTURE.md](../ARCHITECTURE.md) → 当前 TASK。

## 人接管与论文

| 文件 | 用途 |
|---|---|
| [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md) | 人接管指南：读序、常用命令、验证完整性、决策权边界 |
| [PAPER_ROADMAP.md](PAPER_ROADMAP.md) | 最终论文路线：阻断性缺口、阶段计划、发布检查清单 |
| [USER_GUIDE.md](USER_GUIDE.md) | 工作台使用说明（搜索、资源、API、重放诊断） |
| [TEST_CONTRACTS.md](TEST_CONTRACTS.md) | 测试合同与历史测试继承映射 |

## 任务合同（事前）与报告（事后）

| 阶段 | TASK | REPORT |
|---|---|---|
| 治理 | [TASK-001](tasks/TASK-001-governance.md) | [REPORT-001](reports/REPORT-001-governance.md) |
| 数据准入 | [TASK-002](tasks/TASK-002-admission.md) | [REPORT-002](reports/REPORT-002-admission.md) |
| 资源构建 | [TASK-003](tasks/TASK-003-resources.md) | [REPORT-003](reports/REPORT-003-resources.md) |
| 运行服务 | [TASK-004](tasks/TASK-004-runtime.md) | [REPORT-004](reports/REPORT-004-runtime.md) |
| 工作台与比较 | [TASK-005](tasks/TASK-005-workbench-evaluation.md) | REPORT-004 末节 + 运行输出 |
| 历史完整性 | [TASK-006](tasks/TASK-006-topology.md)* | [REPORT-006](reports/REPORT-006-topology.md) |
| 最终验收 | [TASK-007](tasks/TASK-007-handoff.md) | 见 REPORT-008 汇总 |
| 人接管整理 | [TASK-008](tasks/TASK-008-human-github-handover.md) | [REPORT-008](reports/REPORT-008-human-github-handover.md) |

\* TASK-006 文件名为 topology，内容同时覆盖历史目录完整性冻结核对。

## 长期决定

- [ADR-001](adr/ADR-001-independent-rebuild.md)：独立根、三线职责、批准与证据分轴
- [ADR-002](adr/ADR-002-search-evidence.md)：先可解释的实时研究产品，再逐证据晋级
- [ADR-003](adr/ADR-003-repo-orientation.md)：一次性脚本归档、文档分层、GitHub 发布前清单

## 活动脚本

| 脚本 | 用途 |
|---|---|
| [scripts/operate.py](../scripts/operate.py) | 追加式操作日志；所有写入与命令经此记录 |
| [scripts/smoke.py](../scripts/smoke.py) | 实时搜索冒烟（3 次新 MCTS，写 outputs/validation/live-smoke.json） |
| [scripts/browser_check.py](../scripts/browser_check.py) | 浏览器工程验收（需 Playwright Chromium） |

一次性脚本已归档至 [operations/archive/](../operations/archive/README.md)，不再是活动工具。
