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
| 审核结果如何进入搜索 | [TASK-015-06](tasks/TASK-015-06-review-into-search.md) | [REPORT-015-06](reports/REPORT-015-06-review-into-search.md) | Completed；默认审核资源、严格实例关联、界面/导出/运行追溯 |
| 开放数据与黄酮苷搜索扩展 | [TASK-016](tasks/TASK-016-open-glycoside-expansion.md) | [REPORT-016](reports/REPORT-016-open-glycoside-expansion.md) | Completed；4个来源限定O成键模板默认关闭，4/4参照、12/12真实MCTS补回；C/糖间及泛化未覆盖 |
| 黄酮苷反应库批量扩充 | [TASK-016-P1](tasks/TASK-016-P1-open-glycoside-library-expansion.md) | [REPORT-016-P1](reports/REPORT-016-P1-open-glycoside-library-expansion.md) | Completed；54新反应/47新模板、5范围，7/12开发补回；正式评测另行准入 |
| C/糖间成键迁移验证 | [TASK-016-P2](tasks/TASK-016-P2-c-sugar-transfer-validation.md) | [REPORT-016-P2](reports/REPORT-016-P2-c-sugar-transfer-validation.md) | Partial；1C+2糖间新范围、旧4SS三seed修复；新两类6目标/2出处面板未满足，新A/B/D未执行 |
| C scope修复与分轴终验 | [TASK-016-P6](tasks/TASK-016-P6-c-scope-runtime-transfer-closure.md) | [REPORT-016-P6](reports/REPORT-016-P6-c-scope-runtime-transfer-closure.md) | Partial；正确scope2/2、可执行C6/4、v6与旧51回归完成；C域不匹配/SS1/1，迁移null；177测试、3410保护0漂移 |
| TASK-016 Roadmap P2 终验 | [TASK-016-P7](tasks/TASK-016-P7-domain-aligned-transfer-closure.md) | — | Proposed；scope-first/fresh-holdout epoch，多subagent职责隔离；须同时关闭C与SS真实迁移后才可Completed |

TASK-015既有裁决及搜索接管已完成。[TASK-016](tasks/TASK-016-open-glycoside-expansion.md)保留4精确O首版；[TASK-016-P1](tasks/TASK-016-P1-open-glycoside-library-expansion.md) Completed，54新反应/47新模板、7/12开发补回。[TASK-016-P2](tasks/TASK-016-P2-c-sugar-transfer-validation.md)本轮Partial，见[报告](reports/REPORT-016-P2-c-sugar-transfer-validation.md)：默认关闭v3共54模板，新增1C/2糖间范围、旧4SS三seed修复；新增准入反应0，新迁移面板不足，未运行新A/B/D。工程124测试、重建/包外安装/保护审计通过不抵偿科学门。当前缺口以[TASK-016-P6报告](reports/REPORT-016-P6-c-scope-runtime-transfer-closure.md)的C范围/独立留出域对齐与SS原始反应闭包为准；TASK-017仍未授权，正式/独立化学/供应门保持。

[TASK-016-P7](tasks/TASK-016-P7-domain-aligned-transfer-closure.md) 已按所有者本会话要求建立为 Proposed：不复用反复观察的旧 holdout，而采用 scope 先冻结、随后 fresh holdout、失败 epoch 永久暴露并换新 holdout 的机制；只有 C/SS 双轴都通过真实 A/B/E 与三 seed node-transfer，才允许把工作台 Roadmap P2 的 development effect 标记完成。当前尚未授权执行。

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

[TASK-015-P1](tasks/TASK-015-P1-agent-review-ord-analysis.md) / [REPORT-015-P1](reports/REPORT-015-P1-agent-review-ord-analysis.md)：Completed，60条委托代理审核、ORD深入分析、[SciFinder直接检索词](protocols/SCIFINDER_SEARCH_TASK015_P1.md)。结果入口outputs/review/task015-p1/final-v2/index.html；不构成独立人审/gold。

[TASK-015-P2](tasks/TASK-015-P2-scifinder-inbound.md) / [REPORT-015-P2](reports/REPORT-015-P2-scifinder-inbound.md)：已接收并核对九个 SciFinder RDF、635 条导出行；本地明细见 outputs/review/task015-p2/inbound-v1。OsCGT 来源已覆盖，精确 5-O 指定供体及 3-O-ribofuranoside 目标仍缺；不构成独立 gold。

[TASK-015-P3 人审交接](tasks/TASK-015-P3-human-review-handoff.md) / [阶段报告](reports/REPORT-015-P3-human-review-handoff.md)：60 卡可填写离线包已交付，本地入口 outputs/review/task015-p3/handoff-v2/index.html；等待所有者审核回传，再逐轴补证并条件冻结开发 gold。

2026-10-05：[TASK-015-06](tasks/TASK-015-06-review-into-search.md) 已完成。P3/P4/P5既有成果已进入冻结审核视图、17候选库存准入交集、动作/末端/资源/运行证据；95项回归、无资产检查、重放/安装/浏览器通过，真实开发路线来源命中0，供应认证0。后续TASK-016绑定实际审核版本；本轮未启动。
