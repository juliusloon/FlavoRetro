# FlavoRetro 文档导航

机器契约（agent 先读）：[PROJECT.md](../PROJECT.md) → [STATE.md](../STATE.md) → [ARCHITECTURE.md](../ARCHITECTURE.md) → 当前 TASK。

人类研究员接手：先读 [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md)，再按需要读任务合同与报告。全部治理文档遵循 CondRxnBench 详细格式；读者无需访问旧项目 `/home/ljx/retro_synthesis`。

## 人接管与方向

| 文件 | 用途 |
|---|---|
| [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md) | 人接管指南：读序、常用命令、验证完整性、决策权边界 |
| [WORKBENCH_ROADMAP.md](WORKBENCH_ROADMAP.md) | 工作台路线：现状、P1—P5 阶段方向与准入规则 |
| [PAPER_ROADMAP.md](PAPER_ROADMAP.md) | 最终论文路线：阻断性缺口、下一阶段主线（TASK-014—018，含 D1—D7 方向价值排序）、阶段计划、发布检查清单 |
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
| 来源定位补充 | [TASK-007-P1](tasks/TASK-007-P1-source-relocation.md) | [REPORT-007-P1](reports/REPORT-007-P1-source-relocation.md) | 历史 Partial；后由 TASK-012 获批恢复并以新 v3 收口 |
| 人接管整理 | [TASK-008](tasks/TASK-008-human-github-handover.md) | [REPORT-008](reports/REPORT-008-human-github-handover.md) | Completed |
| 文档详细化 | [TASK-009](tasks/TASK-009-docs-detailing.md) | [REPORT-009](reports/REPORT-009-docs-detailing.md) | Completed |
| Web 完整化与独立收口 | [TASK-010](tasks/TASK-010-web-completion.md) | [REPORT-010](reports/REPORT-010-web-completion.md) | Completed |
| 有效性判断可视化 | [TASK-011](tasks/TASK-011-topology-web.md) | [REPORT-011](reports/REPORT-011-topology-web.md) | Completed |
| 工程地基统一验收 | [TASK-012](tasks/TASK-012-foundation-readiness.md) | [REPORT-012](reports/REPORT-012-foundation-readiness.md) | Completed；五项工程门槛通过，科学门槛仍未闭合 |
| Web 设计落地 | [TASK-013](tasks/TASK-013-web-ui-design.md) | [REPORT-013](reports/REPORT-013-web-ui-design.md) | Completed；呈现层交付，未提交 |
| 领域筛选与评测协议 | [TASK-014](tasks/TASK-014-domain-triage.md) | [REPORT-014](reports/REPORT-014-domain-triage.md) | Completed；开发试点与协议，独立化学审核未执行 |

TASK-014 已完成领域筛选与评测规范；TASK-015 已获批并完成 ORD 覆盖与审核准备，实际独立人工 gold 未执行。TASK-016—018 仍为方向计划，未自动授权。见 [protocols/](protocols/README.md) 与 [PAPER_ROADMAP.md](PAPER_ROADMAP.md)。

\* TASK-006 文件名为 topology，内容同时覆盖历史目录完整性冻结核对。REPORT-005、REPORT-007、REPORT-007-P1 为 TASK-009 补立，事实来源为 `operations/events.jsonl` 与 `operations/command-*.log`（本机日志，不入 Git）。

[工程能力与界面覆盖](FOUNDATION_CAPABILITIES.md) 给出每项功能的入口、验证及证据边界；[独立环境](../environment/README.md) 给出安装与本地资产恢复。

## 长期决定

- [ADR-001](adr/ADR-001-independent-rebuild.md)：独立根、三线职责、批准与证据分轴
- [ADR-002](adr/ADR-002-search-evidence.md)：先可解释的实时研究产品，再逐证据晋级
- [ADR-003](adr/ADR-003-repo-orientation.md)：一次性脚本归档、文档分层、GitHub 发布前清单
- [ADR-004](adr/ADR-004-teaching-layer-and-web-architecture.md)：教学与文献层迁入 configs/、Web 四页信息架构

- [ADR-005](adr/ADR-005-foundation-workspace-and-index.md)：可写工作区、不可变 JSON/SQLite 索引、受控包资源与独立安装

## 活动脚本

| 脚本 | 用途 |
|---|---|
| [scripts/operate.py](../scripts/operate.py) | 追加式操作日志；所有写入与命令经此记录（`run` 记命令，`--write/--from` 记文件写入前后哈希） |
| [scripts/smoke.py](../scripts/smoke.py) | 实时搜索冒烟（3 次新 MCTS，写 outputs/validation/live-smoke.json） |
| [scripts/browser_check.py](../scripts/browser_check.py) | 浏览器工程验收（需 Playwright Chromium） |

[package_check.py](../scripts/package_check.py) 验证仓库外安装和实时搜索；[artifact_check.py](../scripts/artifact_check.py) 核包资源与本地载荷排除。

一次性脚本已归档至 [operations/archive/](../operations/archive/README.md)，不再是活动工具。

[领域/标注/评测协议](protocols/README.md) 定义 TASK-014 的总分类与 TASK-015 接管规则；[triage_reactions.py](../scripts/triage_reactions.py) 是只读输入、新目录输出的离线筛选入口。

[ORD 实际覆盖](protocols/ORD_COVERAGE_V1.md) 给出当前镜像全量扫描与来源边界；[定向 SciFinder 材料/审核指南](protocols/SCIFINDER_TARGETED_IMPORT_V1.md) 给出 60 卡入口、4 条首批材料和原件接收格式。
