# 项目进度总账

定位：本文件是任务时间线与「当前在哪」的唯一总账。单任务的合同与事实分别在 `docs/tasks/`、`docs/reports/`；当前状态在 [STATE.md](STATE.md)；长期理由在 `docs/adr/`；本文件只回答「做过什么、走到哪、下一步是什么」。

## 阶段总览

| 阶段 | 任务 | 状态 | 里程碑 |
| --- | --- | --- | --- |
| 1. 独立重建与工程地基 | TASK-001—013 | Completed | 独立包、v3 数据层、实时 MCTS、四页 Web、可访问性设计 |
| 2. 评测准备与开发标签 | TASK-014—015（含 P1—P5、06） | Completed | 2,301 离线试点、53 结构/分类开发 gold、审核接管搜索；独立人审 gold 0 |
| 3. 糖苷方法与开发扩展 | TASK-016（含 P1—P9） | 阶段结项（ADR-006） | 来源限定模板与 scope 链 v1—v7、开发层保护与回归；C/SS 新目标科学矩阵未完成 |
| 4. 正式独立评价 | TASK-017（v0.1→v0.2） | Partial | preparation_ready=true、research_run_ready=false；科学 cell 0、C/SS 效果 null |
| 5. 教学重建拆分 | TASK-019、TASK-020 | Completed | FutureHealth 独立仓库 /home/ljx/FutureHealth（M0+P0）；本仓保持科研事实源 |
| 6. 仓库治理 | TASK-021 | Completed（历史验证例外保留） | 全仓分类、非证据归档、索引及治理文档重构；两个冻结历史脚本语法错误保留 |

## 时间线

| 编号 | 日期 | 标题 | 状态 | 一句话结果 |
| --- | --- | --- | --- | --- |
| [001](docs/tasks/TASK-001-governance.md) | 2026-09-21 | 治理骨架 | Completed | 独立根、三线职责、operate.py 操作账 |
| [002](docs/tasks/TASK-002-admission.md) | 2026-09-21 | 数据准入 | Completed | 114 文件快照逐字节复制与来源登记 |
| [003](docs/tasks/TASK-003-resources.md) | 2026-09-21 | 资源构建 | Completed | 3,059 条记录、逐记录 QC、重放一致 |
| [004](docs/tasks/TASK-004-runtime.md) | 2026-09-21 | 运行服务 | Completed | 实时 MCTS 与共享服务、25 项测试 |
| [005](docs/tasks/TASK-005-workbench-evaluation.md) | 2026-09-21 | 工作台与比较 | Completed | Web 工作台 + 12-cell 开发对照（TASK-009 补立） |
| [006](docs/tasks/TASK-006-topology.md) | 2026-09-21 | 结构诊断 | Completed | 糖苷拓扑诊断；55 次往返失败修复至 0 |
| [007](docs/tasks/TASK-007-handoff.md) | 2026-09-21 | 最终验收 | Completed | 首版收口；[007-P1](docs/tasks/TASK-007-P1-source-relocation.md) 来源定位 Partial，后由 012 v3 收口 |
| [008](docs/tasks/TASK-008-human-github-handover.md) | 2026-09-21 | 人接管整理 | Completed | GitHub 导向、清理无用旧脚本 |
| [009](docs/tasks/TASK-009-docs-detailing.md) | 2026-09-21 | 文档详细化 | Completed | 治理文档按 CondRxnBench 格式补立 |
| [010](docs/tasks/TASK-010-web-completion.md) | 2026-09-22 | Web 完整化 | Completed | 页面修复、独立收口、文献教学模式接入 |
| [011](docs/tasks/TASK-011-topology-web.md) | 2026-09-25 | 拓扑可视化 | Completed | 有效性判断上 Web（所有者人工批准） |
| [012](docs/tasks/TASK-012-foundation-readiness.md) | 2026-09-26 | 工程地基统一验收 | Completed | G1—G5 全过；独立包/GitHub 同步 4b015cf、CI success |
| [013](docs/tasks/TASK-013-web-ui-design.md) | 2026-09-26 | Web 设计落地 | Completed | WCAG AA 对比度、移动优先、可访问性 |
| [014](docs/tasks/TASK-014-domain-triage.md) | 2026-09-27 | 领域筛选与评测协议 | Completed | 9 母核分类、508 guide、2,301 试点、60 审核样本 |
| [015](docs/tasks/TASK-015-ord-coverage-review-cards.md) | 2026-09-27 | ORD 覆盖与审核卡 | Completed | 镜像冻结 53 Parquet、8,509 候选、60 卡 |
| [015-P1](docs/tasks/TASK-015-P1-agent-review-ord-analysis.md) | 2026-09-27 | 代理审核与深析 | Completed | 60 卡代理审核；非独立人审 |
| [015-P2](docs/tasks/TASK-015-P2-scifinder-inbound.md) | 2026-09-28 | SciFinder RDF 接收 | Completed | 9 个用户 RDF、575 CAS 反应号交叉核对 |
| [015-P3](docs/tasks/TASK-015-P3-human-review-handoff.md) | 2026-09-29 | 人审回传与 gold 冻结 | Completed | 53 结构/分类开发 gold + 7 排除；一手来源轴 0/60 |
| [015-P4](docs/tasks/TASK-015-P4-triage-rule-revision.md) | 2026-09-29 | 筛选规则修订 | Completed | 撤稿黑名单/降级/路径压缩；53 gold 零误降 |
| [015-P5](docs/tasks/TASK-015-P5-p0p1-evidence-closure.md) | 2026-10-05 | 证据收尾 | Completed | 60 卡 53 gold+7 排除定案；库存 4 错配隔离 |
| [015-06](docs/tasks/TASK-015-06-review-into-search.md) | 2026-10-05 | 审核进搜索 | Completed | task015-06-v1 冻结视图接管普通搜索；3,059 资源可查 |
| [016](docs/tasks/TASK-016-open-glycoside-expansion.md) | 2026-10-06 | 开放苷搜索扩展 | Completed | 4 个来源限定 O 成键模板（默认关闭）、4/4 参照、12/12 MCTS 补回 |
| [016-P1](docs/tasks/TASK-016-P1-open-glycoside-library-expansion.md) | 2026-10-06 | 批量扩库 | Completed | 54 新反应/47 模板、7/12 开发补回、预算 240 |
| [016-P2](docs/tasks/TASK-016-P2-c-sugar-transfer-validation.md) | 2026-10-06 | C/糖间迁移验证 | Partial | v3 入口；新面板未形成、迁移未执行 |
| [016-P3](docs/tasks/TASK-016-P3-new-reaction-admission-and-transfer.md) | 2026-10-07 | 新反应准入 | Partial | 34 新反应（C12/SS22）；面板不足迁移 null |
| [016-P4](docs/tasks/TASK-016-P4-p3-admission-correction-and-transfer-completion.md) | 2026-10-07 | 准入纠偏 | Partial | 34/34 重审 C8/SS16；v5 重建；面板仍不足 |
| [016-P5](docs/tasks/TASK-016-P5-c-ss-transfer-capability-closure.md) | 2026-10-07 | 迁移能力闭环 | Partial | 2 条新 C 反应、隔离 3 个虚构来源；P5-ERR-06 撤回旧结论 |
| [016-P6](docs/tasks/TASK-016-P6-c-scope-runtime-transfer-closure.md) | 2026-10-07 | C scope 终验 | Partial | 正确 scope 2/2、v6 56 模板、旧 51 回归零损失；域不匹配停止 |
| [016-P7](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md) | 2026-10-13 | 历史迁移与终止 | **Partial/stopped** | fresh 0、科学 0 cell、metrics=null；epoch 账 82→85 关闭 |
| [016-P8](docs/tasks/TASK-016-P8-evidence-rescue-feasibility.md) | 2026-10-13 | 证据抢救可行性 | Completed（诊断） | H1/H5 治理裁定；G7 接入缺口保留为未来前置 |
| [016-P9](docs/tasks/TASK-016-P9-development-evaluation-redesign.md) | 2026-10-13 | 可测性盘点与重设计 | Completed（规划） | C13/SS19 编码目标；同范围支持充足折 0/0 |
| [017](docs/tasks/TASK-017-independent-c-ss-transfer-benchmark.md) | 2026-10-13/15 | C/SS 正式独立评价 | **Partial** | v0.2 准备就绪、科研门未开；对账/资料整理/最终代理裁定完成；正式标签/面板未生成 |
| [019](docs/tasks/TASK-019-future-health-ai-teaching-feasibility.md) | 2026-10-15 | 教学转化可行性调研 | Completed | conditionally_feasible、not_yet_ready |
| [020](docs/tasks/TASK-020-futurehealth-rebuild.md) | 2026-10-15 | FutureHealth 重建 M0+P0 | Completed | 新仓库 /home/ljx/FutureHealth；23 CORE_REUSE 受控副本；P1 49 项仅登记 |
| [021](docs/tasks/TASK-021-repository-consolidation.md) | 2026-10-15—16 | 仓库全面盘点与精简重构 | Completed（历史验证例外保留） | 24,880文件分类、6,364日志归档、53合同通过；[报告](docs/reports/REPORT-021-repository-consolidation.md)披露全量脚本语法失败2项 |

（TASK-018 未立项：路线图占位，正式消融/论文结果任务未创建。）

## 当前位置（2026-10-16）

- 科研线：v3 数据层与 reviewed_resources 视图承载 3,059 资源；模板链 v2—v7 全部显式默认关闭；TASK-016 方法阶段已结项；C/SS 迁移效果未验证（null），正式测量归 TASK-017，其科研门（research_run_ready）未通过，未产生任何正式盲测/独立标签/production。
- 教学线：已拆分至 FutureHealth 独立仓库（ADR-008），教学代码在 FutureHealth，后续 TASK/REPORT/STATE 仍按 ADR-008 在本库登记；P1 49 项资料待教师/所有者审定，M1—M5未执行。
- 治理线：[TASK-021报告](docs/reports/REPORT-021-repository-consolidation.md)已收口索引/归档/文档重构；活动代码/证据原位保全。两个被冻结历史脚本语法错误与日志/旁车缺证明确保留，原始全量compileall验收未达成。

## 已知待决（均需新的明确授权）

1. TASK-017 科研运行：需独立 panel 资格与科研门核验通过后才能执行（[ADR-007](docs/adr/ADR-007-research-evaluation-admission.md)）。
2. Git 同步：本地HEAD993b22f5，最近内容提交3361c07（2026-09-29）；其后交付仍在工作树，远端同步需所有者授权；本轮未查远端。
3. FutureHealth P1 49 项选入与教师审定（在 FutureHealth 侧执行）。
4. H5 的 G7 接入/专利别名缺口（TASK-016-P8 遗留，未来面板冻结前置）。
