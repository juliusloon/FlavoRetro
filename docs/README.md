# FlavoRetro 文档导航

机器契约（agent 先读）：[PROJECT.md](../PROJECT.md) → [STATE.md](../STATE.md) → [ARCHITECTURE.md](../ARCHITECTURE.md) → 当前 TASK。

人类研究员接手：先读 [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md)，再按需要读任务合同与报告。全部治理文档遵循 CondRxnBench 详细格式；读者无需访问旧项目 `/home/ljx/retro_synthesis`。

## 人接管与论文

| 文件 | 用途 |
|---|---|
| [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md) | 人接管指南：读序、常用命令、验证完整性、决策权边界 |
| [PAPER_ROADMAP.md](PAPER_ROADMAP.md) | 最终论文路线：阻断性缺口、阶段计划、发布检查清单 |
| [USER_GUIDE.md](USER_GUIDE.md) | 工作台使用说明（搜索、资源、API、重放诊断） |
| [TEST_CONTRACTS.md](TEST_CONTRACTS.md) | 测试合同与历史测试继承映射 |

## 目录规则与模板

| 目录 | 规则（README） | 模板 |
|---|---|---|
| 事前合同 `docs/tasks/` | [tasks/README.md](tasks/README.md)：编号、状态、批准记录规则、术语表 | [tasks/TEMPLATE.md](tasks/TEMPLATE.md) |
| 事后报告 `docs/reports/` | [reports/README.md](reports/README.md)：补立约定、事实纪律 | [reports/TEMPLATE.md](reports/TEMPLATE.md) |
| 长期决定 `docs/adr/` | [adr/README.md](adr/README.md)：何时建 ADR、职责分轴 | [adr/0000-template.md](adr/0000-template.md) |

## 任务合同（事前）与报告（事后）

每个 TASK 必有同编号同短标题的 REPORT；`docs/` 相对链接均可解析。TASK-001—008 文本于 TASK-009 由速记体扩写为详细格式（事实与结论未变，见 [tasks/README.md](tasks/README.md) 阅读约定）。

| 阶段 | TASK | REPORT | 状态 |
|---|---|---|---|
| 治理骨架 | [TASK-001](tasks/TASK-001-governance.md) | [REPORT-001](reports/REPORT-001-governance.md) | Completed |
| 数据准入 | [TASK-002](tasks/TASK-002-admission.md) | [REPORT-002](reports/REPORT-002-admission.md) | Completed |
| 资源构建 | [TASK-003](tasks/TASK-003-resources.md) | [REPORT-003](reports/REPORT-003-resources.md) | Completed |
| 运行服务 | [TASK-004](tasks/TASK-004-runtime.md) | [REPORT-004](reports/REPORT-004-runtime.md) | Completed |
| 工作台与比较 | [TASK-005](tasks/TASK-005-workbench-evaluation.md) | [REPORT-005](reports/REPORT-005-workbench-evaluation.md) | Completed |
| 结构诊断与历史完整性* | [TASK-006](tasks/TASK-006-topology.md) | [REPORT-006](reports/REPORT-006-topology.md) | Completed |
| 最终验收 | [TASK-007](tasks/TASK-007-handoff.md) | [REPORT-007](reports/REPORT-007-handoff.md) | Completed |
| 来源定位补充 | [TASK-007-P1](tasks/TASK-007-P1-source-relocation.md) | [REPORT-007-P1](reports/REPORT-007-P1-source-relocation.md) | Partial（指针切换被所有者搁置） |
| 人接管整理 | [TASK-008](tasks/TASK-008-human-github-handover.md) | [REPORT-008](reports/REPORT-008-human-github-handover.md) | Completed |
| 文档详细化 | [TASK-009](tasks/TASK-009-docs-detailing.md) | [REPORT-009](reports/REPORT-009-docs-detailing.md) | 见文件 |

\* TASK-006 文件名为 topology，内容同时覆盖历史目录完整性冻结核对。REPORT-005、REPORT-007、REPORT-007-P1 为 TASK-009 补立，事实来源为 `operations/events.jsonl` 与 `operations/command-*.log`（本机日志，不入 Git）。

## 长期决定

- [ADR-001](adr/ADR-001-independent-rebuild.md)：独立根、三线职责、批准与证据分轴
- [ADR-002](adr/ADR-002-search-evidence.md)：先可解释的实时研究产品，再逐证据晋级
- [ADR-003](adr/ADR-003-repo-orientation.md)：一次性脚本归档、文档分层、GitHub 发布前清单

## 活动脚本

| 脚本 | 用途 |
|---|---|
| [scripts/operate.py](../scripts/operate.py) | 追加式操作日志；所有写入与命令经此记录（`run` 记命令，`--write/--from` 记文件写入前后哈希） |
| [scripts/smoke.py](../scripts/smoke.py) | 实时搜索冒烟（3 次新 MCTS，写 outputs/validation/live-smoke.json） |
| [scripts/browser_check.py](../scripts/browser_check.py) | 浏览器工程验收（需 Playwright Chromium） |

一次性脚本已归档至 [operations/archive/](../operations/archive/README.md)，不再是活动工具。
