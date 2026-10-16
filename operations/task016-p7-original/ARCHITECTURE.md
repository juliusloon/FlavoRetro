# 当前责任与产物登记

本表登记活动事实源与文件职责。TASK 保存事前合同，REPORT 保存执行历史，STATE 保存当前事实，ADR 保存长期理由；新的产物先核本表。

| 入口/目录 | 责任与主要文件 | 状态 |
| --- | --- | --- |
| PROJECT.md / AGENTS.md | 稳定目标、硬约束与批准流程；每项任务独立授权，TASK-014/015 为 human_direct 工程执行批准，TASK-015 预算内细化为 agent_delegated | active |
| STATE.md | 当前版本、阶段验收与待办，不替代历史报告 | active |
| pyproject.toml | Python 3.10 范围、固定核心依赖、验证工具、三项程序入口、默认资源打包 | active |
| environment/ | README 独立安装/资产恢复；requirements-linux-py310.lock 新解析锁；pip-freeze.txt 历史借用环境快照 | active |
| docs/ | 导航、用户/接管/测试文档、工作台/论文路线、FOUNDATION_CAPABILITIES.md 能力与边界矩阵；protocols/ 保存领域/标注/评测 v1 与接入调查 | active |
| docs/tasks、reports、adr | TASK-001…014；REPORT-001…014（含 007-P1）；ADR-001…005；编号目录说明与模板 | active |
| metadata/ | sources.json 来源/许可/哈希清单；sources-v1.json 历史留档；note-relocations.json 文件定位；active.json 活动版本/manifest 绑定；foundation.json 工程阶段事实；release.json 科学候选状态 | active |
| data/raw/ | 合法本地只读副本/模型，字节不可变，不入 Git | local immutable |
| data/derived/ | 活动 v3：records.json 事实源、manifest.json 构建/来源/记录哈希、index.sqlite 派生查询库、index.json 索引 schema/哈希；replay-v3 独立字节重放；v1/replay-v1/v2 原样保留 | local immutable |
| flavoretro/workspace.py | 显式工作区、包路径、默认/覆盖配置、活动版本验证；避免安装目录被当成可写工作区 | active |
| flavoretro/resources.py | 损失保全的源解析与新不可变版本构建，零/缺失/冲突/失败保持原值 | active |
| flavoretro/database.py | SQLite 索引构建、只读查询/分页/QC/收率/源状态、索引错配检测；JSON 仍是唯一事实源 | active |
| flavoretro/contracts.py、policies.py | 严格输入/预算；候选库存与明确已知危害过滤，未知不认证安全 | active |
| flavoretro/reviewed_resources.py | P3/P4/P5冻结输入、record/FGM/stock显式关联、库存准入交集、严格反应实例查询、运行绑定/完整性；外置视图不覆盖v3 | active offline builder + runtime reader |
| flavoretro/search.py | PUCT、动作融合/去重、替代动作、转置与预算；多产物保持原 index，不改变糖苷家族定义 | active |
| flavoretro/service.py、worker.py | CLI/API 共享的逐次进程与真正 MCTS；工作区/版本/模型/配置/代码指纹；运行结果、失败与 manifest | active |
| flavoretro/cli.py、web.py | 搜索 CLI 和本机 HTTP；静态前端、资源、拓扑、显式历史全文件核查、同进程搜索/开发对照门控 | active |
| flavoretro/triage.py | 只读版本绑定、笔记 guide、标准化精确去重复用、母核/拓扑候选排序、审核样本与泄漏分组；不进 MCTS | active offline |
| flavoretro/evaluation.py | 固定 12-cell 工程开发对照与真实门槛 preflight；不是正式执行器，不是盲测 | active |
| flavoretro/topology.py | 保持原独立图诊断语义；labelled graph synthons, not reagents；不进 MCTS 扩展/评分 | active |
| web/、configs/ | 前端三个编辑源、三个运行配置与独立离线 domain_triage.json；前端四页完整能力入口，不开放任意管理写入 | active source |
| flavoretro/assets/ | web/configs 的包交付副本；测试逐文件字节比较，独立安装读取，不依赖 checkout | active packaged snapshots |
| tests/ | 输入/保全、真实运行、优化行为、拓扑、SQLite、安装与 HTTP 合同；需本地资产的项明确标记 | active |
| scripts/ | operate.py 操作日志；browser_check.py 四页/历史/12-cell 浏览器验收；package_check.py 包外安装/真实搜索；artifact_check.py wheel/sdist 载荷边界；triage_reactions.py 审计离线筛选入口；smoke.py 历史冒烟入口 | active |
| .github/workflows/engineering.yml | 固定 Linux/Python 3.10 无受限资产 CI，构建/安装/合同；CI 命令也经 operate.py；不上传本地载荷 | active |
| outputs/runs/ | 每次独立 request/result/worker.log/manifest，错误也保留；历史只显式读取 | local evidence |
| outputs/evaluation/ | 独立开发对照 contract/cell/summary；HTTP job 进度原子保存，外进程未完成记录不声称仍运行 | local evidence |
| outputs/triage/ | task014-final 的 guide/pilot/queues/duplicates/leakage/review JSONL/TSV、规则/统计/manifest/README/audit.ipynb；task014-replay 独立字节重放，task014-v1 首轮保留 | local immutable development |
| outputs/validation/ | 每次独立浏览器/包/构建目录、TASK-012 阶段 JSON；task012-sync.json 是带时间的实际远端/CI 核查快照 | local evidence |
| operations/ | events.jsonl 追加式操作事件入 Git；命令日志/基线 JSON/本轮暂存不入 Git；最终只读核查可产生未提交追加尾部 | audit |
| operations/archive/ | 一次性脚本/旧构建器；不作为活动 runtime | archived |

科学门槛由 release 元数据和 preflight 显式保留；工程阶段通过不自动改变 primary source/vendor/independent labels/production/formal benchmark 状态。

TASK-015 离线补充：flavoretro/review_cards.py 与 scripts/build_review_cards.py 生成本地审核卡；fetch_ord.py / scan_ord.py / survey_ord_mirror.py / summarize_ord_coverage.py 负责冻结公开镜像、原件校验、逐行候选与严格重合；setup_ord_schema.py 和 environment/task015-ord-schema.json 只隔离官方生成 protobuf 模块。来源身份导航由 review_references.py / refine_review_references.py 生成；check_review_cards.py / audit_ord_coverage.py 核工程结果。data/raw/ord/task015 为原件，outputs/coverage 为机器结果，outputs/review/task015-v2 为最终卡片，data/inbox/scifinder/task015-user 为未来用户原件接收目录，均不入 Git。不接 runtime/v3，不生成 human_reviewed / gold；具体字段与职责见 REPORT-015、ORD_COVERAGE_V1、SCIFINDER_TARGETED_IMPORT_V1。

TASK-015-P1：scripts/analyze_ord_review.py在冻结扫描结果上重算来源/重合/糖拓扑诊断；scripts/assemble_agent_reviews.py合并三个代理审核批次并生成只读页及JSONL/TSV。最新本地结果outputs/review/task015-p1/final-v2，ORD补充outputs/coverage/task015-p1；身份human_delegated_agent_review，不接活动v3或runtime。

TASK-015-P3：scripts/build_task015_p3_handoff.py 从冻结 60 卡、代理审核和 P2 新 RDF 交叉表生成本地人审界面/缺口表/版本及哈希 packet；scripts/check_task015_p3_handoff.py 使用隔离浏览器测试保存、导入导出与哈希拒绝。outputs/review/task015-p3/handoff-v2 仅本地受限衍生审核包，人工提交待独立验证，不回写原卡/v3/运行时。

TASK-016（2026-10-06 v0.2 Completed）：[合同](docs/tasks/TASK-016-open-glycoside-expansion.md) / [报告](docs/reports/REPORT-016-open-glycoside-expansion.md)。open_reactions.py处理官方取得/方向映射/正文定位；glycoside_expansion.py校验冻结来源、抽取精确物种模板并提供独立领域expansion与酶促过滤守卫；task016_runs.py提供显式运行总账。contracts/cli/worker/service/workspace接入glycoside_expansion=false及--glycoside-expansion、父子绑定与必要配置入口；search.py在显式诊断时追溯真实outcome/节点。configs/glycoside-expansion.json与包内副本相同，外置manifest SHA a47523992eb006c3ffe22c204e492e7a8470786d8bbec6613c7d57e49f087471；缺资产/哈希漂移失败。4个O成键模板仅接受来源登记的精确结构/离子态，固定cap=4、prior=0.2、weight=1；默认关闭，通用过滤保持。酶促动作使用来源/模板/上下文/实际outcome守卫及KnownHazards，明确不将USPTO化学filter用作酶可行性分数。独立TASK-016命名空间保留模板支持/当前实例匹配/预测条件三轴，旧审核注释不覆盖新来源；G4–G5同样绑定task015-06-v1与17库存。原件data/raw/task016/和载荷outputs/task016/v1/本地Git忽略；24主MCTS及重放/包外验证通过。来源精确重现不表示预测条件确认、新底物泛化、evidence_closed或生产晋级。

TASK-015-06（2026-10-05 Completed）：[审核结果如何进入搜索](docs/tasks/TASK-015-06-review-into-search.md) / [报告](docs/reports/REPORT-015-06-review-into-search.md)。flavoretro/reviewed_resources.py构建/校验外置冻结视图outputs/review/task015-06/v1，通过policies的CandidateStock与ReviewedEvidence、worker/service和现有Web资源/逐步/末端/导出传递分轴审核结论和运行指纹。配置入口configs/search.json.reviewed_resources及打包副本默认adjudicated，manifest SHA 1e8ea3c461ac3ff88ee4d6bad3385aa832881d65bb682ff7467d64014c15f8ec。17候选库存键保持，4错配原已禁用，2本地模板未启用；9原文/6产率独立子集，不认证预测或采购。原v3/SQLite/active/release不改；TASK-016 G4–G5绑定该稳定视图。

TASK-016-P1（2026-10-06 v0.2 Completed）：[合同](docs/tasks/TASK-016-P1-open-glycoside-library-expansion.md) / [报告](docs/reports/REPORT-016-P1-open-glycoside-library-expansion.md)。open_glycoside_library.py定义保留原结构的acid-O表示和单糖形成一致性；glycoside_library.py提供build-only来源注册表、实例/范围模板、完整UDP供体/立体/母核/位点守卫、映射/E-Z保全和证据分轴。contracts/cli/worker/service支持显式glycoside_library_version=v2，默认关闭且v1请求形状保持；search.py实施固定分支内前三已过滤通用动作保护与完整实际节点trace。configs/glycoside-library-v2.json及包副本指向outputs/task016-p1/v2/template_source_manifest.json，缺资产/哈希漂移失败。

scripts/task016_p1_sources/discover/articles/curate/encode/freeze/build.py完成有界公开采集、来源编码、反应去重、冻结闭包分组与多受体范围抽取；qualify.py在新版本撤回身份不充分实例，不更换留出面板/作用范围；evaluate/revalidate_r3/revalidate_qualified.py保存各版本真实开发矩阵、明确继承同任务未变A/B控制；verify_qualified.py是最终只读审计入口。运行注册表仅build73上下文/51模板，holdout12参照由独立评估器读取。task016_runs.py保留旧120上限，对固定P1账本校验原基线和SHA固定的r4 agent_delegated预算240，不允许任意环境提高预算。

当前data/raw/task016-p1/原件、outputs/task016-p1/v1原获取/冻结/r1-r3历史、v2合格载荷及outputs/validation/task016-p1-package-qualified安装证据本地Git忽略。新54反应/47模板、7/12开发补回、118回归/23文件重放与51审计通过；93新注释中12待确认完整保留，预算216/240及所有失败登记。这里只确认来源重现/结构声明范围/开发实际动作，不证明新酶活、条件、供应、独立标签或正式评测，完整限制见REPORT。

TASK-016-P4（2026-10-07 Partial）：[合同](docs/tasks/TASK-016-P4-p3-admission-correction-and-transfer-completion.md) / [报告](docs/reports/REPORT-016-P4-p3-admission-correction-and-transfer-completion.md)。glycoside_library_v5.py 为显式默认关闭纠偏运行版本，**从合格 P2/v3 重建而非继承 v4**：v5 = v3(54 模板) + 仅经纠偏重验收的 SS 1→2 范围（2 个不同 canonical 受体）= 55 模板/87 实例，支持重放 2/2；被隔离的 C 羟基黄烷酮 C3（无中间体完整结构证据）与 SS 鼠李糖 1→6（两来源实为同一 canonical 受体，distinct=1<2）在 payload 构造层即排除，模块内 P3_SCOPE_CORRECTION 记录三范围纠偏结论供历史 v4 运行对照读取。configs/glycoside-library-v5.json 与包副本相同，缺资产/哈希漂移失败封闭；contracts/worker/cli/workspace 增加 v5 接线，v1—v4 行为与 54/57 模板指纹不变。scripts/task016_p4_{g0,audit,scopes,sources,new_sources,panel,build,runs,verify}.py 分层承载准入重审/范围计数/定向补源/面板冻结/构建/预算/终验，判据表显式可重算。outputs/task016-p4/v1 为本轮事实源，superseded/ 保留被取代的错误面板作为证据。本轮 C 与 SS 面板均低于 ≥6 硬门，A/B/E 未执行、迁移指标 null，搜索尝试 0；独立化学验证、训练重叠、formal/release 门均未改变。

TASK-016-P2（2026-10-06 Partial）：[合同](docs/tasks/TASK-016-P2-c-sugar-transfer-validation.md)、[报告](docs/reports/REPORT-016-P2-c-sugar-transfer-validation.md)。新增glycoside_library_v3.py及显式默认关闭v3入口；合格载荷outputs/task016-p2/v2，v1保留来源/撤回历史/批准和独立账本。54模板（46精确、8范围）中3新范围分别为phloretin mono-C-Gal/Xyl第二次Glc成键、flavonol Glc/Gal糖O2-Glc、prenyl化4′-O-methyl flavonol Rha糖O2-Xyl；完整供体、母体糖立体/连接、母核守卫，候选活性/条件未知。85继承实例全部build/calibration，51旧模板保持。旧4SS/5C/7O三seed真实创建；新两类面板不足，新A/B/D未执行，不能声明新迁移。cap4/prior0.2/weight1、分支12、通用前三保护复用；父子SHA绑定/缺资产失败关闭。P2预算213验证+27工程=240，已61保守/55实际；默认/v1/v2、审核17库存、模型/PUCT与旧账不漂移。

TASK-016-P6（2026-10-07 Partial）：[合同](docs/tasks/TASK-016-P6-c-scope-runtime-transfer-closure.md) / [报告](docs/reports/REPORT-016-P6-c-scope-runtime-transfer-closure.md)。glycoside_scope.py定义P3精确→scope构造后C8/flavonol/完整糖立体守卫、runtime完整性、分轴preflight与真实节点判据；glycoside_library_v6.py从合格P2/v3重建+P4 SS O2+P6 C8，共56模板89实例，增量2模板4构建实例、无holdout，C3与Rha1→6结构性排除。configs及包副本glycoside-library-v6.json一致，显式v6/默认关闭/缺payload及SHA漂移拒绝加载，task016_runs绑定新批准与独立480总额及81/81/51/213/54用途上限；旧模块/配置未改。scripts/task016_p6_*.py承载纠错保护、正确scope、来源完整图编码、静态可测性、SS身份/闭包、正式runtime、旧17×3、无资产/安装/独立终验；tests/test_task016_p6.py含22必需/26实际合同测试。outputs/task016-p6/v1为本轮事实源，superseded及supersession_ledger保存错误证据；raw、payload与安装快照本地Git忽略。C6目标4组但scope完整参照0/6→停止条件6 domain mismatch，SS1目标1组→停止条件1，科学矩阵0、迁移null；构建4/4、安装C节点2/2为exact重现，旧51回归无新增损失；工程完成不替代新底物迁移或更高科学门。
