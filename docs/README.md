# FlavoRetro 文档导航

按 [PROJECT.md](../PROJECT.md) → [STATE.md](../STATE.md) → [ARCHITECTURE.md](../ARCHITECTURE.md) → 当前 TASK 阅读。任务时间线与阶段位置统一在 [PROGRESS.md](../PROGRESS.md)，单次事实保存在 REPORT，长期理由保存在 ADR。

## 当前项目位置

实时研究工作台与来源限定模板工程已交付。TASK-016 方法阶段结项，P7 保持 **Partial/stopped**；C/糖间独立迁移未验证。TASK-017 整体 **Partial**，preparation_ready=true、research_run_ready=false、正式科学 cell 0、C/SS 效果 null、legacy formal/release=false。

历史资料最终代理裁定已完成：32 卡 25 纳入/4 领域排除/3 证据不足，agent_delegated、human_reviewed=false；不再要求 ljx 逐卡重复审核。正式独立 panel、标签、闭包与最终协议仍缺。现有空白审核包不能冒充 gold。当前细节以 [STATE](../STATE.md) 和 [最终裁定报告](reports/REPORT-017-agent-adjudication-20261015.md) 为准。

## 按用途查阅

| 入口 | 内容 |
| --- | --- |
| [任务合同索引](tasks/README.md) / [执行报告索引](reports/README.md) | 全部 TASK 与 REPORT，包括阶段补充和历史失败 |
| [长期决定索引](adr/README.md) | ADR-001—008；方法/评价分工、科研准入、FutureHealth 拆分 |
| [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md) / [USER_GUIDE.md](USER_GUIDE.md) | 接管与使用；历史验证数字按所属阶段解释 |
| [WORKBENCH_ROADMAP.md](WORKBENCH_ROADMAP.md) / [PAPER_ROADMAP.md](PAPER_ROADMAP.md) | 已登记路线与后续准入；不单独构成执行批准 |
| [FOUNDATION_CAPABILITIES.md](FOUNDATION_CAPABILITIES.md) / [TEST_CONTRACTS.md](TEST_CONTRACTS.md) | 功能入口、工程验收与测试合同 |
| [独立环境](../environment/README.md) | Linux/Python 3.10 固定依赖、安装及本地资产恢复 |
| [协议索引](protocols/README.md) | 领域筛选、标注、开发评价与来源接入协议 |
| [脚本索引](../scripts/README.md) / [证据索引](../outputs/README.md) / [操作账定位](../operations/README.md) | 常驻入口、被冻结历史脚本、证据版本及日志归档 |
| [TASK-021整理台账](../outputs/restructure/repo-consolidation-20261015/README.md) | 全仓分类、归档映射、验证例外、原治理文档快照 |

## 研究评价材料入口

| 内容 | 事实与边界 |
| --- | --- |
| [TASK-015-P3](tasks/TASK-015-P3-human-review-handoff.md) / [P5最终报告](reports/REPORT-015-P5-p0p1-evidence-closure.md) | 53 条结构/分类开发 gold + 7 排除；一手来源/独立化学轴仍分开 |
| [审核进入搜索](reports/REPORT-015-06-review-into-search.md) | task015-06-v1 冻结审核视图接管普通搜索；17 库存键、供应认证 0 |
| [TASK-016](tasks/TASK-016-open-glycoside-expansion.md) / [方法结项 ADR-006](adr/ADR-006-method-delivery-and-independent-evaluation.md) | 来源限定方法与有限开发效果；P2—P7各阶段 Partial 不被改写 |
| [P7终止审计](reports/REPORT-016-P7-closeout-20261013.md) / [P8治理裁定](reports/REPORT-016-P8-H1-H5-governance-rulings.md) | 旧 epoch incomplete、曝光和 unknown 保留；G7 接入仍未完成 |
| [TASK-017合同](tasks/TASK-017-independent-c-ss-transfer-benchmark.md) / [v0.2执行](reports/REPORT-017-v0.2-execution.md) / [ADR-007](adr/ADR-007-research-evaluation-admission.md) | 检查与执行器已实现；准备门通过、科研门未通过；原 v1 G0停止报告保留 |
| [PDF对账](../outputs/evaluation/task017-pdf-reconciliation-20261013/README.md) / [资料整理报告](reports/REPORT-017-materials-preparation.md) / [材料入口](../outputs/evaluation/task017-materials-preparation-20261013/README.md) | 登记材料先对账；48书目不是48篇已确认独立论文；无需重复补交整批PDF |
| [补证报告](reports/REPORT-017-evidence-completion-20261015.md) / [最终代理裁定](reports/REPORT-017-agent-adjudication-20261015.md) | 历史审核已完成且保持 development_exposed；未形成新独立面板 |

TASK-017旧合同第288行的材料链接存在原有相对路径错误；上表提供正确入口，冻结合同字节保留。历史 P7 草稿在 [报告档案](reports/archive/README.md)，不作为当前结论。

## 教学线与授权

[TASK-019报告](reports/REPORT-019-future-health-ai-teaching-feasibility.md) 给出 conditionally_feasible/not_yet_ready；[TASK-020报告](reports/REPORT-020-futurehealth-rebuild-m0-p0.md) 完成 FutureHealth M0+P0：23 受控副本、P1 49 项仅登记。教学代码在独立仓库，后续治理仍在本库登记（[ADR-008](adr/ADR-008-futurehealth-project-split.md)）。本轮整理不授权教学后续阶段、科研运行或 Git 同步。

新合同/报告分别用 [TASK模板](tasks/TEMPLATE.md)、[REPORT模板](reports/TEMPLATE.md)；长期决定用 [ADR模板](adr/0000-template.md)。所有写入和命令通过 scripts/operate.py 记录。原始/受限数据及 outputs/temp 不入 Git，候选、图回放、工程验证、供应和独立化学证据各自保留身份。
