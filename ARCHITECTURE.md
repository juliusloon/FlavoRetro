# 架构与产物登记

本文件登记层次、活动入口、历史版本与证据位置。当前结论看 [STATE.md](STATE.md)，任务时间线看 [PROGRESS.md](PROGRESS.md)，执行依据看 [docs/](docs/README.md)。重构前全文保存在 [原架构快照](outputs/restructure/repo-consolidation-20261015/before-continuation/ARCHITECTURE.md)。

## 分层与写入边界

| 层 | 位置与职责 | 保存规则 |
| --- | --- | --- |
| 治理 | PROJECT / AGENTS 稳定合同；STATE 当前事实；PROGRESS 时间线；TASK 事前授权；REPORT 执行历史；ADR 长期理由 | 原创文档可入 Git；历史合同/报告按当时含义保留 |
| 运行代码 | flavoretro/、pyproject.toml 三个程序入口 | 本轮不改模块字节；新搜索新建 MCTS |
| 配置与前端 | configs/、web/ 编辑源；flavoretro/assets/ 包内副本 | 两份应逐字节一致；本轮不修改 |
| 来源与资源 | metadata/、data/raw/、data/derived/ | 原始字节不可变；data 不入 Git；SQLite 为派生只读索引 |
| 脚本 | scripts/ 常驻入口与历史任务脚本 | 按 [脚本索引](scripts/README.md) 选择；被钉路径原位保留 |
| 证据 | outputs/ 的运行、评价、审核、开发、失败、superseded 产物 | 本地保留、不入 Git；[目录索引](outputs/README.md) |
| 操作 | operations/events.jsonl、基线/原件快照、归档日志 | events 只追加；日志本地保留；[定位规则](operations/README.md) |
| 验证与环境 | tests/、environment/、.github/workflows/engineering.yml | 固定 Linux/Python 3.10 工程检查；本地资产项另标；本轮不改测试 |
| 用户材料 | temp/ RDF、PDF、提取中间件及历史草案 | 不是可随意删除的缓存；不入 Git；[说明](temp/README.md) |

## 活动数据与检索路径

`metadata/active.json → data/derived/v3/manifest.json → records.json / index.sqlite`。

- metadata/sources.json 保存来源、许可与哈希；sources-v1.json 是历史；note-relocations.json 只修定位；foundation.json 登记工程验收；release.json 登记科学候选与发布门。
- v3 有 3,059 候选记录、123 来源；records/manifest 为事实源，SQLite 只派生查询；v1/v2/replay-v1/replay-v3 原样保留。
- 普通搜索默认消费 `outputs/review/task015-06/v1` 的冻结审核视图。库存准入、实例证据、供应与独立化学验证分轴；17 允许库存键、4 错配已禁用；9 原文/6 产率是独立子集。

## 模块职责

| 模块 | 责任 |
| --- | --- |
| workspace.py | 显式可写工作区、包路径、覆盖配置、活动版本/manifest 验证；安装目录不作为工作区 |
| resources.py / database.py | 损失保全解析、不可变版本构建；只读分页/QC/收率/来源查询及索引错配检测 |
| contracts.py / policies.py | 严格请求/预算、候选库存、KnownHazards；未知不认证安全 |
| reviewed_resources.py / review_cards.py | 冻结审核层构建/校验、record/FGM/stock 关联、严格实例证据、运行绑定；离线卡片不覆盖 v3 |
| search.py | PUCT、动作融合/去重、替代动作、转置、预算、通用动作保护与实际节点 trace |
| service.py / worker.py | CLI/API 共享逐次进程及真实 MCTS；模型/配置/代码/审核指纹；逐次保存成功与失败 |
| cli.py / web.py | 搜索/HTTP、资源、拓扑与显式历史核验；前端四页，不开放任意管理写入 |
| triage.py / topology.py | 离线母核/拓扑筛选与泄漏分组；独立 labelled graph synthons 图诊断，不接 MCTS 扩展/评分 |
| evaluation.py | 固定 12-cell 工程开发对照与旧 preflight 兼容门 |
| formal_evaluation.py | TASK-017 的准备/科研准入、冻结、单次矩阵与真实结果复算；准备通过不等于科研运行通过 |
| open_reactions.py / open_glycoside_library.py | 合法来源、方向/结构表示、来源定位与反应库构建支持 |
| glycoside_scope.py / glycoside_scope_c_v7.py / glycoside_scope_ss_v7.py | scope 转换、母核/供体/位点/立体守卫与各版本结构约束 |
| task016_runs.py | 分任务批准、用途预算、尝试与失败总账；不借新目录重置旧预算 |

## 模板版本登记

所有糖苷扩展默认关闭；v2—v7 需显式版本、glycoside_expansion 与 optimized engine。配置同时存在于 configs/ 与包内 assets/configs/，manifest 缺失或 SHA 漂移拒绝加载。旧版本可重放不表示当前科学放行。

| 版本 | 模块 / 配置 | 载荷与解释 |
| --- | --- | --- |
| v1 | glycoside_expansion.py / glycoside-expansion.json | outputs/task016/v1；4 个来源精确 O 成键模板 |
| v2 | glycoside_library.py / glycoside-library-v2.json | outputs/task016-p1/v2；build-only 来源注册表，完整 UDP/立体/母核守卫 |
| v3 | glycoside_library_v3.py / glycoside-library-v3.json | outputs/task016-p2/v2；54 模板，旧实例回归不替代新迁移 |
| v4 | glycoside_library_v4.py / glycoside-library-v4.json | outputs/task016-p3/v1；历史增量，纠偏结论见 P4 |
| v5 | glycoside_library_v5.py / glycoside-library-v5.json | outputs/task016-p4/v1；从合格 v3 重建，55 模板；不继承 v4 整体增量 |
| v6 | glycoside_library_v6.py / glycoside-library-v6.json | outputs/task016-p6/v1；56 模板/89 实例；正确 C8 scope，C3/糖间1→6 排除 |
| v7 | glycoside_library_v7.py / glycoside-library-v7.json | outputs/task016-p7/v1；历史开发版本；P7 Partial/stopped，不重开 epoch |

固定 cap/prior/weight、分支保护、父子 manifest 及实例/模板支持/预测条件分轴的具体值与验收，以对应配置和 REPORT-016 系列为准。

## 证据与工具导航

[outputs/README.md](outputs/README.md) 区分 runs、evaluation、review、triage、coverage、validation、evidence、TASK-016 各阶段与 restructure。TASK-017 的 formal-task017-v1/v2、PDF 对账、历史材料整理与最终代理裁定均是独立产物；当前 `final_agent_historical_adjudication_completed`，preparation_ready=true、research_run_ready=false。历史 32 卡审核不产生正式独立标签，空白 handoff 不回填 gold。

[scripts/README.md](scripts/README.md) 登记常驻工具、TASK-015 来源/卡片链、TASK-016 分组、task017_formal.py 与 task020_futurehealth_rebuild.py。523 个顶层 Python 脚本中，522 个名字被原引用台账记录；task020 工具因既有报告和受控迁移职责保留。历史脚本不可据“可导入”判断可再次执行。两个被冻结的 P7 脚本语法错误保留，详见 [TASK-021报告](docs/reports/REPORT-021-repository-consolidation.md)。

TASK-021 的全仓分类、续作保护、归档映射、验证与历史文档快照位于 [repo-consolidation-20261015](outputs/restructure/repo-consolidation-20261015/README.md)；staging/ 是盘点原件，archived/ 是非活动材料，verification 文件说明核验边界。

## 钉定与外部仓库

manifest/runtime_file_hashes/protected_hashes 中的路径与字节共同决定重放；不得通过移动、合并、修复旧脚本暗改历史保护。新任务应将未经钉定的一次性工具直接放入档案层，活动入口与冻结执行记录分开。日志定位需同时使用事件时间、路径与 SHA，不能仅凭重用编号。

`/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 完整只读，本轮不访问执行；`/home/ljx/FutureHealth` 是独立教学代码仓库，后续 TASK/REPORT/STATE 仍按 [ADR-008](docs/adr/ADR-008-futurehealth-project-split.md) 在 FlavoRetro 登记。M1—M5、P1 内容复制/教师审定不属于本次清理授权。
