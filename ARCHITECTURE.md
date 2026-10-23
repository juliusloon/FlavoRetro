# 架构与产物登记

本文件登记层次、活动入口、历史版本与证据位置。当前结论看 [STATE.md](STATE.md)，任务时间线看 [PROGRESS.md](PROGRESS.md)，执行依据看 [docs/](docs/README.md)。重构前全文保存在 [原架构快照](outputs/restructure/repo-consolidation-20261015/before-continuation/ARCHITECTURE.md)。

## 分层与写入边界

| 层 | 位置与职责 | 保存规则 |
| --- | --- | --- |
| 治理 | PROJECT / AGENTS 稳定合同；STATE 当前事实；PROGRESS 时间线；TASK 事前授权；REPORT 执行历史；ADR 长期理由 | 原创文档可入 Git；历史合同/报告按当时含义保留 |
| 运行代码 | flavoretro/、pyproject.toml 三个程序入口 | 按活动 TASK 最小修改；冻结历史字节不回写；新搜索新建 MCTS |
| 配置与前端 | configs/配置源；web/src、styles与清单为前端源，构建为web三运行资产；flavoretro/assets/包内副本 | 配置与运行资产镜像逐字节一致；前端源由build/check约束，修改按活动TASK记录 |
| 来源与资源 | metadata/、data/raw/、data/derived/ | 原始字节不可变；data 不入 Git；SQLite 为派生只读索引 |
| 脚本 | scripts/ 常驻入口与历史任务脚本 | 按 [脚本索引](scripts/README.md) 选择；被钉路径原位保留 |
| 证据 | outputs/ 的运行、评价、审核、开发、失败、superseded 产物 | 本地保留、不入 Git；[目录索引](outputs/README.md) |
| 操作 | operations/events.jsonl、基线/原件快照、归档日志 | events 只追加；日志本地保留；[定位规则](operations/README.md) |
| 验证与环境 | tests/、environment/、.github/workflows/engineering.yml | 固定 Linux/Python 3.10 工程检查；本地资产项另标；按活动变更验证 |
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
| ranking.py | research-priority-v4：唯一叶结构/库存、模型/简洁/来源支持、碳立体及保护调整扣分；optimized回传与全部实际前缀排序共用，非成功概率 |
| search.py / search_repaired.py | 旧来源知识树保持；generic默认新树保全模型候选，以NativeUCT下界＋0.25PUCT选择，按深度/历史安全兄弟重用与25000节点硬限 |
| service.py / worker.py | CLI/API 共享逐次进程及真实 MCTS；模型/配置/代码/审核指纹；逐次保存成功与失败 |
| cli.py / web.py | 搜索/HTTP、资源、拓扑与显式历史核验；前端五个主入口与层级子页，不开放任意管理写入 |
| triage.py / topology.py | 离线母核/拓扑筛选与泄漏分组；独立 labelled graph synthons 图诊断，不接 MCTS 扩展/评分 |
| route_quality.py | 有限O-乙酰结构分组、真实祖先重访诊断、来源步骤覆盖、明确未解决子目标；不认证化学 |
| research_evaluation.py | 私有冻结A/B/C协议、输入与代码/数据漂移拒绝，不向公开SearchRequest添加控制字段 |
| evaluation.py | 固定 12-cell 工程开发对照与旧 preflight 兼容门 |
| formal_evaluation.py | TASK-017 的准备/科研准入、冻结、单次矩阵与真实结果复算；准备通过不等于科研运行通过 |
| open_reactions.py / open_glycoside_library.py | 合法来源、方向/结构表示、来源定位与反应库构建支持 |
| glycoside_scope.py / glycoside_scope_c_v7.py / glycoside_scope_ss_v7.py | scope 转换、母核/供体/位点/立体守卫与各版本结构约束 |
| reaction_intake.py / literature_policy.py / biochemical_stock.py | TASK-022 来源准入、精确文献动作与候选库存；不产生独立化学标签或当前供应认证 |
| runtime_extensions.py / pipeline_presentation.py | 显式 v8/literature/ZINC 绑定；从冻结协议和运行账定位批次摘要及配对，打开保存单元核验 SHA，不启动新搜索 |
| task016_runs.py | 分任务批准、用途预算、尝试与失败总账；不借新目录重置旧预算 |

## 模板版本登记

所有糖苷扩展默认关闭；v2—v8 需显式版本、glycoside_expansion 与 optimized engine。配置同时存在于 configs/ 与包内 assets/configs/，manifest 缺失或 SHA 漂移拒绝加载。旧版本可重放不表示当前科学放行。

| 版本 | 模块 / 配置 | 载荷与解释 |
| --- | --- | --- |
| v1 | glycoside_expansion.py / glycoside-expansion.json | outputs/task016/v1；4 个来源精确 O 成键模板 |
| v2 | glycoside_library.py / glycoside-library-v2.json | outputs/task016-p1/v2；build-only 来源注册表，完整 UDP/立体/母核守卫 |
| v3 | glycoside_library_v3.py / glycoside-library-v3.json | outputs/task016-p2/v2；54 模板，旧实例回归不替代新迁移 |
| v4 | glycoside_library_v4.py / glycoside-library-v4.json | outputs/task016-p3/v1；历史增量，纠偏结论见 P4 |
| v5 | glycoside_library_v5.py / glycoside-library-v5.json | outputs/task016-p4/v1；从合格 v3 重建，55 模板；不继承 v4 整体增量 |
| v6 | glycoside_library_v6.py / glycoside-library-v6.json | outputs/task016-p6/v1；56 模板/89 实例；正确 C8 scope，C3/糖间1→6 排除 |
| v7 | glycoside_library_v7.py / glycoside-library-v7.json | outputs/task016-p7/v1；历史开发版本；P7 Partial/stopped，不重开 epoch |
| v8 | glycoside_library_v8.py / glycoside-library-v8.json | outputs/task022/glycoside-v8；54 模板/86 实例；来源及 O2″ 糖链图纠偏，旧错误支持保留隔离；开发/来源重建证据 |

固定 cap/prior/weight、分支保护、父子 manifest 及实例/模板支持/预测条件分轴的具体值与验收，以对应配置和 REPORT-016 系列为准。

## 证据与工具导航

[outputs/README.md](outputs/README.md) 区分 runs、evaluation、review、triage、coverage、validation、evidence、TASK-016 各阶段与 restructure。TASK-017 的 formal-task017-v1/v2、PDF 对账、历史材料整理与最终代理裁定均是独立产物；当前 `final_agent_historical_adjudication_completed`，preparation_ready=true、research_run_ready=false。历史 32 卡审核不产生正式独立标签，空白 handoff 不回填 gold。

[scripts/README.md](scripts/README.md) 登记常驻工具、TASK-015 来源/卡片链、TASK-016 分组、task017_formal.py 与 task020_futurehealth_rebuild.py。523 个顶层 Python 脚本中，522 个名字被原引用台账记录；task020 工具因既有报告和受控迁移职责保留。历史脚本不可据“可导入”判断可再次执行。两个被冻结的 P7 脚本语法错误保留，详见 [TASK-021报告](docs/reports/REPORT-021-repository-consolidation.md)。

TASK-021 的全仓分类、续作保护、归档映射、验证与历史文档快照位于 [repo-consolidation-20261015](outputs/restructure/repo-consolidation-20261015/README.md)；staging/ 是盘点原件，archived/ 是非活动材料，verification 文件说明核验边界。

## 钉定与外部仓库

manifest/runtime_file_hashes/protected_hashes 中的路径与字节共同决定重放；不得通过移动、合并、修复旧脚本暗改历史保护。新任务应将未经钉定的一次性工具直接放入档案层，活动入口与冻结执行记录分开。日志定位需同时使用事件时间、路径与 SHA，不能仅凭重用编号。

`/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 完整只读，本轮不访问执行；`/home/ljx/FutureHealth` 是独立教学代码仓库，后续 TASK/REPORT/STATE 仍按 [ADR-008](docs/adr/ADR-008-futurehealth-project-split.md) 在 FlavoRetro 登记。M1—M5、P1 内容复制/教师审定不属于本次清理授权。


## TASK-022 续作定位

`scripts/task022_loop.py` 管理原累计 3600 搜索预算；`outputs/task022/current.json` 是当前恢复指针。冻结协议和旧代码结果不因后续纠偏而覆盖。`outputs/task022/resume-20261021/` 保存恢复审批、方法纠偏、验证和操作例外；`evaluation_audit/audit_resumed.py` 只离线核验与重算，不运行搜索。

旧 `algorithm-v2-dev` 的 O2 标签实际调用普通 optimized：worker 未读取处理标记。真正扩大候选前沿的方法使用独立 `algorithm_frontier_runner.py` / `source_evaluation/worker_frontier.py`，结果须同时记录变体与实际候选数。`v8_newsource_runner_current.py` / `v8_evaluation/worker_current.py` 对全部三臂显式排除目标，并按当前字节冻结引用方法的完整依赖。方法纠偏不追认旧批次为合规新方法。

最终本地代码闭包补验使用 `v8_newsource_runner_complete.py` 和 `v8-newsource-current-v2`：271项资产覆盖全部当前package Python、所选worker、配置/环境定义与既有数据。`local_code_coverage.json` 区分引用旧方法清单覆盖和当前导入闭包；旧current-v1漏两个普通臂导入模块的事实保留，不追认完整闭包。


## TASK-022 goal方法与展示定位

`outputs/task022/goal_20261021/`保留NFAST工程/开发/180新来源及完整审计；前瞻效率失败，不晋升。`readout_development_20261021/`保留7次同树全前沿诊断（0增益）及停止的候选。`runtime_draft_20261021/`包含实际只读展示接入审批、历史原字节/SHA映射、41反应/12来源与教学激活、24测试和浏览器验证；未应用NFAST搜索运行时草稿。旧批次直接依赖路径在展示变更后有意变化，须保留原审计与preimages，不能暗重跑追认。

`outputs/task022/flavanone_scope_20261021/`为新的源类别图假设：native MCTS加FF-OPEN-E-v1，限定单核中性2arylflavanone，保留原子/非C2手性并独立反向闭环；新增规则独有图守卫，其余模型/危害/审核/库存不变。`policy.py/worker.py/runner.py/audit.py`、291资产开发批与298资产final-method分别冻结；工程6、开发54成功仅为已曝光证据。新来源须同一固定协议、至少12目标/4DOI且不同已知连接身份，尚未完成。`current.json`记录goal下一步；正式TASK017与供应/教师/化学门不因此改变。

DFF前瞻入口为flavanone_scope_20261021/prospective_runner.py；source_admission_audit.py独立检查源身份、原子保全/明确MOM脱保护与先验曝光。prospective_sources内13卡/5物理组、26身份解析、85条筛选和原始材料合并冻结613项；goal-flavanone-prospective-source-v1为130次真实调用，运行中不改任何被钉资产。current.json只保留当前检查点，旧混合字段快照另存checkpoint_before_prospective_v1.json。

## DFF实际接入与后续优化覆盖修复

flavoretro/flavanone_opening.py及两份flavanone-opening.json提供绑定的FF-OPEN-E-v1；SearchRequest/CLI/API/Web显式native opt-in，默认关闭。source130效果见flavanone_scope_20261021/*comparison/representation/geometry/quality/additional_audit，全部原始结果在接入前审计。intake/current指v5、teaching/current指v6；54记录/17来源、32论文/18lesson，FV6数值冲突另有overlay，不回写冻结来源卡。evaluation_audit/goal-flavanone-prospective-source-v1_independent_audit.json仅将完整绑定结果转为旧表格schema；runtime_only协议禁止科研单元链接，普通实际run ID由outputs/runs读取。所有后续代码/展示原件和SHA映射见runtime_dff_draft及presentation_130各修订目录。

optimized_coverage_repair_20261021/diagnosis-v1.json和plan-v1.json登记仍未完成的普通optimized覆盖修复；源类别DFF成功不能替代该目标。保留PUCT引导，前瞻固定探索下界/完整模型候选/安全状态身份等候选，先在新目录实现和单位检查，后冻3工程＋42开发＋最多2运行时；当前尚未执行。native+DFF与已验来源扩展保留，完整goal active。

## 当前严格搜索与库存身份（2026-10-22）

stock_identity.py为所有当前Finder安装共同CanonicalStock：按显示结构正常解析后使用完整InChIKey，含E/Z、手性和精确目标排除；原库存/query/selection/criteria不变。finder.stock与config.stock同一对象，phase记录实际类/profile；库存仍候选，不认证供应。generic optimized走search_repaired.py，糖苷/文献保留旧search.py，native+DFF仍原生树加固定规则。运行时原字节与历史SHA映射、66测试见optimized_coverage_repair_20261021/strict_stock_v2/runtime_draft。旧v1表示失败overlay保留，strict-v2 42已独立全叶审计通过。

final_dff_regression/plan-v3及628资产批goal-dff-canonical-current-regression-v3已130/130正常并独立核验：当前13目标曝光回归效果门全过、效率20%未过；不覆盖旧130前瞻身份。运行时387资产的3真实接口通过；后续2JS保存方法提示修订有前像，提交/序列化与后端不变，最终18只读浏览器流程/导出通过。全1449清单5793文件SHA一致、没有未终态任务，current.json与strict_stock_v2/COMPLETED.md为完成指针；不再恢复旧handle。完整目标验收见final_verification_v2与full_goal_completion_audit_v1，后续任务另立批准。

## TASK-023 教学导航与交互

web/与flavoretro/assets/web/双份同步。前端LEARNING_TOPICS按固定来源ID提供O/C/糖链/母核编辑导航，复用/api/teaching原理；/api/literature-teaching仍提供同一32篇/18例，浏览器筛选不改后端反应分类、模板与运行数据。文献加载完成后执行锚点聚焦，课程与来源互链；嵌套条件以dl键值结构完整展示。角色定义见docs/ROLE_REVIEWERS.md，前像与角色QA见outputs/task023/；本轮无搜索语义或独立科学门变更。

## TASK-025 视口工作台与分页展示

原生JS保留共享搜索/证据接口。header下方#main固定剩余视口，桌面路线aside/results各自overflow与overscroll隔离；资源采用独立筛选栏、58:42记录/JSON详情，手机切换面板并转移焦点。pagination()统一驱动上下控件，资源limit显式送入/api/records，教学各栏目保持独立offset/limit且只渲染当前切片；六步仍按原v1记录索引导出全量。

web/和包内assets/web/现在有原三文件加teaching-examples.json与4个teaching-example-*.svg，8文件镜像。web.py静态白名单显式增加这五个GET资产，JSON/SVG MIME独立；无任意路径开放。配图来自已有精确来源实例的RDKit重绘，完整结构/DOI/定位/许可/SHA保存在JSON。新增示例不接搜索、不变更模板与课程准入。修改前字节及来源/QA见outputs/task025/，常见图登记docs/TEACHING_EXAMPLES.md。

## TASK-026 当前排序与研究界面

ranking.py为当前评分事实源；worker提取全部实际前沿、结构去重、评分后才取top_k，candidate_ranking保留全部候选排名。research_reward配置仅用于优化树，原UCT/PUCT和native回传语义保留。web.saved_run额外提供历史展示投影，原result/manifest不改。前端显式科学字段白名单，不再渲染原始JSON、耗时或工程面板；横向路线在局部滚动。方法与限制见ADR010，芦丁自检见REPORT026。新TASK027仅为Proposed；TASK022历史方法的验收不代表当前评分方法性能。

## TASK-027 当前方法与来源准入

当前v4及all_generated_prefixes_v1保留实际创建的非根路径，包括内部前缀；原frontier统计和新增extracted_node_count分开。源码route_quality.py仅处理有限O-乙酰结构组与子目标，不把组数作为机理数；ranking.py分开碳立体与杂原子标记，不填P配置。原整数成本作为legacy_cost保留。

runtime-candidates两份配置的显式literature绑定指向outputs/task027/literature/v2：旧10+新三条精确命名来源转换；无泛化scope、库存新增0。源码/包内前端一致，来源按钮为显式启用，摘要与全文范围/原料子目标分开呈现。旧18个v3 cell、P4/P5三例分别保存，旧68/72资产精确快照支持审查；不对旧路径直接套当前方法追认。原协议不覆写，实际批准/版本见TASK027各阶段记录、REPORT027及ADR011。TASK028仅Proposed。

## TASK-029 跨项目实验开发交接

`flavoretro/literature_policy.py`保留精确来源动作与非动作的development_contexts；`worker.py.source_variants`只存实际生成过的同图来源树。`flavoretro/lab_handoff.py`从校验后的只读运行导出v1包，`web.py /api/lab-handoff`只读提供；web及包内镜像呈现三篇角色、候选与导出/进入入口。当前15条来源动作与1条工程菌上下文的唯一登记是`outputs/task029/literature/v3/manifest.json`（本地ignored），configs指针与包内镜像绑定同一SHA。既有13条和历史运行不改。`scripts/task029_build_sources.py`是一次性本地构建器，显式输入已授权Lab来源根；运行服务不依赖该路径。`outputs/task029`保存本轮基线、真实运行、准入与验收；原始来源不入Git。协议理由见ADR-012。

## TASK-031 路线探索参数与操作区

`#search-form`采用纵向flex：`.search-form-scroll`独立滚动、`.search-form-actions`固定占据面板底部空间，不覆盖参数；手机上下布局允许参数末端向结果页滚动衔接。随机种子与库存范围仅移入高级设置，请求字段/默认值不变。反应原理随路线默认加载，旧localStorage开关不再读取；原有逐步详情仍可展开。web与包内三文件镜像同步，验证见REPORT-031。

## TASK-032 搜索历史与顶部分页

历史页上方comparison-panel、下方history-saved；history-records沿用records-panel/record-table-wrap边框与滚动，history-table和resource-table共享主要视觉规则。资源只渲染records-pager-top，历史只渲染runs-pager-top；教学其他分页不属本任务。loadRuns将runLimit传给原只读/api/runs，默认25、10/25/50/100可选，total缩减时回收有效页；A/B菜单与保存运行核验语义保持。网页源与包内对应片段同步，证据见REPORT-032/outputs/task032。

## TASK-034 高级设置预算默认值

HTML内search-budget-defaults为当前search.json的非执行JSON快照；初始化后使用/api/status.profiles.profiles刷新。syncBudgetDefaults显示所选预算末阶段值和分阶段标签，budgetOverrides仅记录用户编辑/历史显式覆盖；提交不把可见但未编辑的默认值转换为统一覆盖。模式切换保留自定义、重置移除覆盖，历史无值项显示对应模式默认。web与包内两文件镜像同步；后端与默认phase不改，见REPORT-034。

## TASK-033 文献教学层级与展示状态

教学页三个同级section为topic-explorer、teaching-catalog与literature-tools。EXAMPLE_LESSONS解释既有四个来源绑定结构，PRINCIPLE_GUIDES逐分类提供实例/家族通式或明确证据不足说明；均是展示文字，不修改后端分类或准入。conceptGeneration、catalogGeneration独立防止过期异步渲染；activeConcept只控制示例，literature-topic只控制论文/案例，工具范围由updateLiteratureContext展示。27原理选择器配合原pagination，默认1条；原结构JSON/SVG和32/18/54资料保留。三份前端镜像同步，验收见REPORT-033与outputs/task033。

## TASK-035 当前历史页面板布局

.history-workspace按DOM顺序承载history-saved和history-comparison；桌面grid为1.85fr/1fr（约65:35），各自滚动，低于1100px为历史在上/对照在下。删除comparison-title与指定说明，用aria-label命名对照region；A/B、分页、真实读取及导出JS原字节保留。此布局取代TASK032的上下排布，原报告仍是历史记录。见REPORT-035/outputs/task035。

## TASK-036 教学顶部区域导航

teaching-sections为三个tabpanel提供顶部互斥导航；activeTeachingSection默认examples，showTeachingSection只调整可见性、ARIA和滚动，switchTeachingSection按需渲染当前区域。switchLiteratureView自动揭示tools，保留既有来源/案例/示例筛选跨区入口；内部activeConcept、catalog分页、文献筛选与学习记录独立保留。新加载默认首项，当前页往返保留选择。导航样式显式限定以避免主导航配色继承，来源标题留96px滚动空间；两份前端逐字节一致，详见REPORT-036。

## TASK-037 常见类型双面板

example-heading将topic-title与learning-topic-options放在同排，按钮组靠右；renderLearningTopics共用example-layout，左example-narrative只放标题/引言/三步解释，右example-visual放原方程式/结构SVG/图注。桌面minmax(280px,1fr)/minmax(0,2fr)，小于1100px堆叠；手机两列按钮及图内横滑。重复example-identities渲染和样式已移除，出处/边界与筛选动作仍在布局后，原例文与SVG/JSON内容不改。三份前端镜像一致；详见REPORT-037。

## TASK-038 示例左栏上下文

example-layout的首列改由example-left承载；example-narrative、example-source、example-boundary和筛选button-row依次为其同级子元素。出处/核对文字直接排在讲解卡片外，整行布局align-items:start使右图保持自然高度。指定筛选提示已删除，筛选处理、来源内容与原结构图保持。两份前端镜像一致，详见REPORT-038。

## TASK-039 原理区固定单条展示

principle-heading将同字号h2/label和principle-select并排，selectedPrinciple取代teachingPages.catalog，loadTeachingCatalog只渲染单条。原理上下分页DOM与调用移除；principleArticle复用example-layout/left/narrative/visual左讲解右图式，来源和参考位于左列。顶部三分区及其他文献工具分页保持。当前行为取代TASK033原理分页，详情见REPORT-039/outputs/task039。

## TASK-040 教学标题行导航

literature-heading将literature-heading-copy（标题/说明）和原teaching-sections导航放入同一flex行；导航margin-left:auto，桌面同排、窄屏自然换行并靠右。固定范围改为组合标题栏，原按钮互斥/键盘JS不改；来源锚点按视口留96/160/240px避让。相关HTML/CSS镜像一致，见REPORT-040。

## TASK-041 可寻址子页面与浏览器历史

`web/app.js`的集中导航控制器将五个主入口、教学分区/工具、资源记录、保存运行/路线映射到`#/`层级路径；同一静态壳保持当前服务与包资产白名单，不需要HTTP回退或重启。`captureRoute/readRoute/restoreLocation`负责地址序列化与恢复，pushState记录真实访问、replaceState规范化，popstate/hashchange恢复内容、滚动和选中状态。运行/资源继续使用现有GET，导航代次及对照代次拒绝过期响应；来源链接只产生目标子页的一次导航。

主导航及教学导航用真实a链接保留ARIA、方向键和原生新标签能力。`#page-breadcrumb`提供当前位置与上级入口；可分享筛选/分页/A/B/item存在URL，搜索草稿与budgetOverrides仅存会话，`#search-advanced`提供稳定保存节点。旧?run入口迁移兼容；不改变搜索/数据/来源内容或原始导出。三份前端及包内镜像同步；长期理由见ADR-013，验收见REPORT-041与outputs/task041。本节更新此前“仅当前页往返保留状态”的导航合同。

## TASK-042 移除面包屑展示

按用户要求移除#page-breadcrumb/.page-location及其生成/样式；updatePageLocation只维护页面标题和导航链接。隐藏的navigation-message独立保留，仅读取中/错误时显示，无常驻占位。TASK041的层级URL、浏览器历史与所有状态恢复继续使用原逻辑；本节取代前节关于面包屑上级入口的当前界面描述。见REPORT-042。

## TASK-043 教学固定栏与主header衔接

#literature.page在既有媒体查询之后以padding-top:0消除滚动容器顶部内边距，使.literature-heading的sticky top:0直接贴主header底部；原左右/底部间距及不透明背景不改。仅CSS与包内镜像修改，无HTML/JS变更；首屏/滚动/来源定位与导航恢复验收见REPORT-043及outputs/task043。

## TASK-045 文献工具精简与分页对齐

literature-tools从四个选项起始，移除重复标题/说明和small第三行；案例页的context清空并hidden，不留占位，其他工具范围说明保留。四工具只使用顶部分页；文献/案例/新增证据默认25及10/25/50/100，与历史共用pagination，六步练习保持1/2/3/6。captureRoute/restoreLocation及openLiteratureAnchor统一新的25默认，显式10条来源跨页保留size；示例筛选聚焦papers-title。三文件镜像一致，其他来源/数据/搜索语义保持。文献精简初始TASK044因与另一聊天同号改为TASK045，详见REPORT045及outputs/task045，不覆盖并行标题栏背景修改。

## TASK-044 保留教学原高度并补齐背景

本节取代TASK043的当前实现：移除padding-top:0覆盖，恢复原页面顶部内边距（桌面20px、手机16px）。sticky .literature-heading::before在bottom:100%向上延伸var(--space-6)=24px同色不透明背景，超出部分由#literature滚动容器裁切，pointer-events:none。原标题栏几何/正文/其他页面不变；只改CSS及镜像，45处整段截图像素和跨页面起点比较验证覆盖及高度统一。详见背景合同/REPORT-044，独立证据outputs/task044/backdrop/。

## TASK-046 文献工具固定列表与阅读区

文献工具保留四个子页。#literature[data-section="tools"]在桌面采用剩余视口flex，tool-view内的.tool-split约34:66，TOOL_PANELS统一案例/论文/证据列表与reader，左右各自滚动；小于768px短列表在上、完整阅读在下。关键词/类型或检查状态处于同位置，新增证据也支持即时输入和清空；四入口用途手机隐藏以节省高度。顶部分页、旧默认25及六步1/2/3/6地址保持。

toolSelections和navigationItem同步真实选中与item URL，非首项保留到新筛选时补写地址；selectToolItem不滚外层。关联来源通过showInlineSource在同reader读取并返回，内联卡不复用主卡ID；外部openLiteratureAnchor仍使用旧深链。scrollPositions登记新增列表/reader；浏览器返回前进恢复阅读位置，键盘导航不被详情抢焦点。读取失败在可见reader显示role=alert。嵌套条件用同一科学字段白名单分组，原教学常量、内容与六步schema不变；STEP导航重绘后保留焦点。见REPORT046和outputs/task046。本节取代旧文献工具长卡片、跨栏目内部来源跳转的当前界面描述，不改科学准入与搜索。

## TASK-047 当前前端开发结构

web/src/shell.html与pages/的9个HTML片段构成六个页面区域（五个业务入口＋独立组件参考）；页面JS、core和shared按职责拆分。core/pages.js的PageRegistry提供register/load，core/router.js保留URL/history及全部旧状态恢复。components/ui.js闭包提供FlavoUI，ui.d.ts是调用契约；公共分页与真实列表/控件使用同一组件，mount使静态和新增DOM使用同一UI类。

styles/tokens.css、components.css及页面层明确视觉与分栏合同，保留教学原高度/背景。routes.json和frontend.json为路由/依赖顺序事实源，scripts/frontend.py用标准库build/check/watch/routes/create-page；check验证页面、DOM ID和六份生成资产，已接入CI配置。根级app.js/style.css/index.html及包镜像均为生成物，禁止手改；运行HTTP/安装包仍只消费原资产白名单。JS是显式顺序的经典脚本构建片段，既有全局名称为兼容边界，新页面状态在生命周期闭包内。

开发操作入口web/README.md，规范docs/frontend/，可运行参考`/#/components`不占主导航；scripts/check_frontend.py为只读浏览器回归。无面包屑，无搜索/科学身份变化。ADR014解释长期理由，REPORT047及outputs/task047给出验收。本节更新早期“web三个文件直接编辑/无构建”的开发规则，旧报告按历史保留。
