# 当前状态（2026-10-16）

项目处于 **实时研究工作台与来源限定方法已交付，C/糖间独立迁移尚未验证** 的阶段。系统为 research_candidate。任务历史统一查 [PROGRESS.md](PROGRESS.md)，层次与入口查 [ARCHITECTURE.md](ARCHITECTURE.md)，授权与执行事实分别查 [TASK/REPORT索引](docs/README.md)。重构前完整状态保存在 [历史快照](outputs/restructure/repo-consolidation-20261015/before-continuation/STATE.md)。

## 活动资源与运行

- metadata/active.json 指向不可变 data/derived/v3，3,059候选记录/123来源；records.json为事实源，SQLite为派生只读索引；旧版本和重放保留。
- 普通搜索默认消费 outputs/review/task015-06/v1 冻结审核视图（manifest SHA `1e8ea3c461ac3ff88ee4d6bad3385aa832881d65bb682ff7467d64014c15f8ec`）。17允许库存键、4错配已禁用；9原文/6产率是分开保留的证据子集，供应认证0。
- CLI/API/Web共享逐次进程和真实MCTS；普通搜索不读结果缓存、不回退BFS。糖苷扩展默认关闭，v1—v7历史载荷按显式配置/版本与SHA加载，未因整理合并或启用。
- 本机直接使用 /home/ljx/FlavoRetro 和 .venv-foundation/bin/python（CPython3.10.20）。固定依赖见 environment/requirements-linux-py310.lock；当前验证仅覆盖Linux/Python3.10。/Volumes/cano与SSH属于原代理历史访问方式，本机无需挂载。

## 科研与证据门

| 范围 | 当前事实 |
| --- | --- |
| TASK-016方法阶段 | 已结项（ADR-006）；历史有限开发结果按原REPORT解释，C/SS独立迁移未验证 |
| TASK-016-P7 | Partial/stopped；旧epoch incomplete、曝光/unknown保留；fresh C/SS=0、科学cell0、效果null，不自动恢复 |
| TASK-017整体 | Partial；execution_status=final_agent_historical_adjudication_completed |
| 准备/科研运行 | preparation_ready=true、research_run_ready=false；正式科学cell0、C/SS效果null |
| 历史资料代理裁定 | 32卡/34上下文；25纳入（C9/SS16）、4领域排除、3证据不足；agent_delegated、human_reviewed=false；无需ljx逐卡重复审核 |
| 正式独立资格 | 历史卡全部development_exposed、independent_panel_eligible=false；新独立标签/panel/闭包/最终协议未形成，精确正式参考未冻结 |
| 旧兼容与发布门 | legacy formal_run_ready=false、release_ready=false；production0，供应unresolved，independent chemical labels不可用 |

TASK017最终事实见 [最终代理裁定报告](docs/reports/REPORT-017-agent-adjudication-20261015.md) 和本地 [task_execution_closeout.json](outputs/evaluation/task017-agent-adjudication-20261015/task_execution_closeout.json)。已有冻结空白handoff不回填gold；书目不命中已登记PDF不证明新独立来源，不要求重复上传整批48项。准备、科研、供应与发布门按 [ADR-007](docs/adr/ADR-007-research-evaluation-admission.md) 分开。

## 仓库治理与验证

TASK-021整理已完成，**历史验证例外保留**；批准与裁定agent_delegated、human_reviewed=false。[报告](docs/reports/REPORT-021-repository-consolidation.md)、[分类/归档/验证总入口](outputs/restructure/repo-consolidation-20261015/README.md)。

- 24,880起点实质文件逐项分类/保护，523顶层脚本索引，6,364历史日志归档；用户材料与冻结代码/数据/科学账原位保全，原治理全文另存。
- 53项现有合同测试通过；完整585文件语法检查中包和测试通过，两个冻结P7历史脚本错误保留，**全量compileall未通过**。这属于获批治理验收例外，不是新科学结果。
- 565项旧包/脚本正文保护SHA匹配；40项旧缺失旁车专项例外、3份日志无write事件、1份历史并发哈希歧义保留披露。原临时件没有移动前SHA，不宣称全量字节迁移证明。
- 归档草稿25处链接已修，原字节保全；TASK017旧合同2处原有材料链接错误保留，当前docs导航提供正确入口。未重复原代理无结束事件的全量unittest。

## 教学线与待决事项

FutureHealth教学代码在独立仓库 /home/ljx/FutureHealth；M0+P0交付沿用 [TASK020报告](docs/reports/REPORT-020-futurehealth-rebuild-m0-p0.md)，本轮未复查该仓库。后续TASK/REPORT/STATE仍按 [ADR-008](docs/adr/ADR-008-futurehealth-project-split.md) 在FlavoRetro登记。

1. TASK017新独立panel、标签、闭包与最终协议及科研门放行；本次整理不授权新的检索/输入、MCTS或科研矩阵，不重置累计预算。
2. P8/H5遗留G7接入/来源别名缺口：未来面板冻结前仍需解决；P7保持停止。
3. FutureHealth P1 49项内容选入/教师审定和M1—M5：需另行明确授权，当前教师审定/教学真值0。
4. 两个冻结历史脚本语法修复：若将来需要，先确定新的版本/保护策略与批准，不回写旧证据。
5. Git同步：有大量既有未提交交付；本地HEAD `993b22f5e8eed5797d27f02c566af1b86a4b7880`，最近内容提交3361c07。本轮未stage/commit/push、未查远端，HEAD/index保持。

## 不变边界

原始/受限数据、outputs、temp不入Git。retro_synthesis/CondRxnBench只读，本轮与FutureHealth均零触碰；.venv*、工具私有状态、既有暂存不清理。候选、身份、图回放、工程测试、来源裁定、供应与独立化学验证分轴；排除、冲突、缺失、零和失败保留。代码Apache-2.0、原创文档CC BY4.0，源材料依原许可。
