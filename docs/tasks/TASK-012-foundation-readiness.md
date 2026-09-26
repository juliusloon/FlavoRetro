# TASK-012：工程地基补齐与统一验收

## 合同元数据

- 任务 ID：TASK-012
- 状态：In Progress（执行中；所有者已批准全部 G1—G5 范围）
- 起草与核查日期：2026-09-26
- 基线分支：main
- 本地基线提交：5f3240f（TASK-011）；远端 main 核查值：f272c36868ef29db041229e4fc85ae5d38e1240e，落后本地两个提交
- 人工负责人：项目所有者 ljx
- 拟执行者：Cano
- 批准：所有者 ljx 于 2026-09-26 明确回复“同意，开始执行”，批准本合同全部 G1—G5（含恢复 TASK-007-P1 范围内来源定位收口、普通提交/推送至现有私有 origin）。记录为 human_direct 工程授权，非 agent_delegated，非逐记录 human_reviewed 化学审核。
- 本轮已经执行的内容：阅读、只读 GitHub 查询、数据哈希/版本核查、现有测试与短程实时搜索、浏览器验收、在隔离临时目录构建现有包并探测，以及本合同和导航/当前状态的文档写入。核查运行产生新 outputs 和操作日志，不修改已有运行或数据版本。
- 拟议完成判定：数据库、算法运行、独立包、GitHub 同步、前端能力覆盖五项工程门槛同时通过。任一项未通过，结论为 Partial/Blocked，禁止写“地基全部完成”。

## 目标与理由

在进入 WORKBENCH_ROADMAP P2 等下一阶段前，建立可重建、可安装、可追溯、已同步且可从界面检查的工程基线。当前系统能够在本机 checkout 运行，但还不能把本机可运行等同于独立交付完成。

“算法地基完成”在本任务中指真实运行、约束可核验、输入/输出/版本有合同；“数据库地基完成”指记录守恒、查询与溯源一致、版本可重建。这些定义不等于黄酮苷化学有效性、独立供应审核或 production 晋级。科学准入仍由独立任务处理。

## 起草前核查：已确认事实

以下是 2026-09-26 的现场核查，不是本任务未来执行的成果。

| 地基 | 已有能力与现场证据 | 缺口 | 当前判断 |
| --- | --- | --- | --- |
| 数据库/资源 | JSON 版本资源库；3,059 条唯一 ID；123 个来源文件全部 SHA-256 匹配；逐记录来源文件全部存在且哈希匹配；v1/v2 记录载荷各自符合 manifest | 没有 SQL 查询库或统一活动版本配置；多模块硬编码 v1；活动 v1 的 508 条 note_reaction 均为 note_missing；来源清单已扩为 123 条而 v1 绑定旧清单；当前构建器代码哈希与旧 manifest 不同 | 数据保全基本成立，版本治理和独立重建未闭合 |
| 算法 | 32 项现有测试通过；另做 optimized/native × quick/balanced/strict 共 6 次实时短程搜索，均成功、有非零步骤路线；每次独立 run ID；默认无候选库存；工程失败不回退 BFS | native 不具有 optimized 等价节点上限；尚缺独立包路径下的运行验收和部分优化行为合同；糖苷拓扑仍仅诊断/展示，未进扩展/评分 | 现有 MCTS 可用，不能据此声称算法优越或化学有效 |
| Python 项目包 | pyproject.toml、flavoretro 包和 CLI 已有；pip check 通过；隔离源码副本能构建 wheel | .venv 的 include-system-site-packages=true，解释器依赖 retro Conda；wheel 不含 configs/web/STATE，安装副本 SearchRequest.phases() 报 FileNotFoundError；ROOT 绑定包父目录；pip-freeze 含其他机器不可用的 file:///home/conda/... 引用；未做独立新环境安装验收 | 包骨架成立，独立交付不成立 |
| GitHub | 已连接私有仓库 juliusloon/FlavoRetro；gh API 与 git ls-remote 已现场确认；Git 未跟踪 data/outputs/.venv | 远端 main=f272c36，本地 main=5f3240f，115cf67 与 5f3240f 尚未同步；无 .github 工作流，GitHub Actions 运行数为 0；README 的“未连接远端”已过期 | 已连接，未完整同步，自动验收缺失 |
| 前端 | 四页工作台；实时搜索/路线评分/原料/反应卡；资源查询/记录 JSON；文献教学/拓扑/边界文案；现有 Chromium 验收通过 | 无 engine、top_k、depth、branching、nodes 控件；无历史 run 加载与清单核查入口；开发对照与正式 preflight 无完整界面入口；版本、独立安装和同步状态展示不完整 | 主要能力已展示，“所有已有能力覆盖”尚未成立 |

### 数据细节与不能混淆的事实

- 记录构成：note_reaction 508、scifinder_reaction 2,301、molecule 156、molecule_duplicate_names 2、molecule_failures 4、stock 49、template 2、paper 15、supplier 22。4 是失败分组记录数，不表示只有 4 个历史结构解析失败。
- production_eligible=true 为 0；名称冲突 3 条；候选库存准入记录 17 条（不等于 17 个经供应审核的可采购原料）。本轮统计到数值零收率 0 条、明确缺失收率 1,075 条；不能把“本版没有零值”误写为零值被删除，零值保留行为由现有测试确认。
- v1 records SHA-256：e09c2906cf900514f357a58abeae3b040cb4547b189b3c25c724e48c624fe141；v2：448dbbdcd511df0aade80903d33abc34707fdcc2d529d3ecb29dbae94898192e。v1 与 replay-v1 载荷一致。
- v1/v2 的 ID 集合完全相同，恰有 508 条记录变化；变更字段仅 source_status、upstream_sources、upstream_reaction_token_found、upstream_reported_line。v2 中 249 条为 note_located_token_found，259 条为 note_located_token_unmatched。定位到文件、找到 token 均不等于一手化学审核。
- v2 当前来源清单哈希一致，但其历史 code_sha256 与当前 resources.py 不同。这是版本对应问题，不能仅据代码哈希差异断言原始数据损坏，也不能静默改写旧 manifest。
- REPORT-007-P1 以 v1/replay-v1 一致和 v1/v2 计数一致推称“两次重放一致”，同时明确“v2 单独重放事件未记录”。计数一致不能证明 v2 字节级重放；本轮没有重建 v2，也不据该报告判定 v2 重放完成。
- USPTO 模板 42,554 条、ringbreaker 模板 5,282 条，classification 全部为 `0.0 Unrecognized`；已有教学表包含该键。6 次新运行观察到的反应 classification 也全部如此。当前缺口是没有可用的明确家族标签，不能只补数值映射就解决；27 个教学条目不能写成搜索已准确识别 27 个家族。
- 橙皮苷糖间连接呈 other_O_candidate 的已知现象来自 REPORT-011；本轮未做独立化学判定，不擅自修正 family。
- preflight 现场返回 formal_run_ready=false、release_ready=false；正式评测与独立化学标签仍未就绪。

### 本轮验证证据索引

| 核查 | 结果 | 证据 |
| --- | --- | --- |
| 现有完整 unittest | 32 项通过，无跳过；包含两个独立实时 MCTS、节点上限、来源保全、失败记录、拓扑、教学端点 | operations/command-0067.log |
| Chromium 浏览器 | 1440×1000 / 390×844；实时双阶段搜索；15 张文献卡；4 个拓扑关联链接；非法输入 400；JS 错误 0；当前流程无横向溢出 | operations/command-0069.log；outputs/validation/browser-2445ff49/report.json |
| 来源/记录/版本核查 | 123 个来源文件全部匹配；3,059 条唯一 ID；数据版本细节见上文 | operations/command-0070.log、command-0074.log |
| pip check | No broken requirements found；仅验证当前借用环境的依赖一致性 | operations/command-0071.log |
| wheel 探测 | 构建成功；展开副本无搜索配置/前端资源，phases() 失败；不是全新环境安装成功 | operations/command-0072.log；outputs/validation/foundation-package-ojcc9_m_/report.json |
| 6 次引擎/模式核查 | 每阶段 0.5 秒、2 次迭代、nodes=7、branching=2；6 次均真实成功且 steps>0，evidence_closed/actionable 均 false | operations/command-0073.log；outputs/validation/foundation-engines-07efd38f/report.json |
| GitHub 现场查询 | origin 私有；main 仍为 f272c36；Actions 0 次；没有执行 fetch/push | operations/command-0065.log、command-0066.log |
| 模板分类核查 | 两套 gzip 表实际以 Tab 分隔；47,836 条全部 0.0 Unrecognized | operations/command-0076.log；command-0075 的逗号解析统计已明确作废，保留失败诊断历史 |

短程核查没有验证默认完整时间预算、跨平台性能或化学质量。浏览器脚本只覆盖其断言流程，不能证明所有能力都有 UI 或所有异常流程均已通过。

## 拟议方案及需要审核的选择

本合同给出一个完整的工程收口方案；以下选择都尚未实施：

1. 保留不可变 JSON 作为资源事实源，新增 Python 标准库 SQLite 派生查询索引，承接筛选、分页、身份/来源关联和 QC 查询。SQLite 是可重建索引，不成为第二套人工编辑事实源，不引入 PostgreSQL 或新服务。
2. 恢复来源定位收口：以当前冻结构建器生成新不可变 v3 和独立 replay-v3，不覆盖 v1/v2；验证后切换统一活动指针。**批准本 TASK 才表示所有者同意在此范围恢复此前搁置的 TASK-007-P1 事项**；本次核查和起草不撤销原搁置决定。
3. 独立 wheel/sdist 包含原创静态前端及默认配置；数据/模型/STATE/运行输出留在明确指定的工作区。以 FLAVORETRO_WORKSPACE 或统一 --workspace 参数确定工作区，同一上下文贯穿 CLI/API/worker/评估，不再从 site-packages 父目录找运行数据。
4. 完成可展示的已有能力：前端补全现有搜索参数、显式历史运行读取、资源版本与溯源、开发对照入口和前置检查；管理性的重建操作展示状态、说明和命令，不开放浏览器任意文件写入。
5. 增加不携带受限资产的 GitHub CI；所有工程验收通过后，按现有私有 origin 进行普通提交和推送，验证交付提交一致。不开公开仓库，不发布 PyPI，不部署公网。

“批准本 TASK”应覆盖上述五项；若所有者只同意部分，先形成修订版合同，不把部分同意解释为整个合同获批。

## 范围与修改预算

### 允许项（获批后）

| 目录及职责 | 允许文件/新增产物（新增均为计划） | 用途 |
| --- | --- | --- |
| flavoretro：共享包与运行 | resources.py、policies.py、contracts.py、service.py、worker.py、evaluation.py、cli.py、web.py；计划新增 workspace.py、database.py；search.py 仅限合同测试发现的明确工程缺陷修复 | 工作区与统一版本、SQLite 查询、现有搜索和评估入口、保存运行核查；保持当前算法科学语义 |
| 包内原创资源（计划） | flavoretro 内的静态资源目录 | 包含 web 三个文件和三个 configs 的受控默认副本/迁入版本，避免多处漂移 |
| 根级包/环境 | pyproject.toml、.gitignore、README.md、environment/；新独立环境放被忽略目录，保留现有 .venv | 构建入口、可安装包、可重建依赖清单、安装/使用合同；隔离文件不入 Git |
| web/configs | index.html、app.js、style.css、search.json、teaching_guidance.json、literature_teaching_layer.json | UI 能力覆盖；如迁入包内，保留路径兼容或明确更新所有调用方；教学只改 Unknown 状态说明和已有确定映射展示，不编造家族标签 |
| metadata：治理元数据 | 计划新增活动版本指针/索引 schema 元数据；sources.json/note-relocations.json 只在发现明确元数据错误且可溯源时变更 | 统一绑定资产版本、构建器、来源；release.json 可补工程门槛字段，不改候选证据等级 |
| data：本地资产，不入 Git | 新 v3/replay-v3 与 SQLite 索引/清单 | 新不可变构建与回放；data/raw、既有 v1/replay-v1/v2 只读保留 |
| tests/scripts | 现有测试；计划增加包安装/数据库/算法约束/能力覆盖测试及明确命名的核查或重建工具；browser_check.py | 必须针对数据守恒、版本错配、优化行为、包路径与真实 UI，而非只复述实现 |
| .github（计划） | workflows 下的工程 CI | 无私有模型也能运行的测试、包构建与安装检查；全量本地资产验收另行记录 |
| docs 与根级治理 | 本 TASK 批准/进度记录；计划 REPORT-012-foundation-readiness.md、能力覆盖清单、ADR、导航、用户/环境/测试文档、STATE.md、ARCHITECTURE.md | 最终事实、设计理由、目录职责与使用说明；历史 TASK/REPORT 不静默改写 |
| outputs/operations | 每次独立验收目录、操作日志、哈希记录、临时构建目录 | 保留成功和失败证据；本轮 outputs 与既有运行不覆盖 |

任何预算外组件、科学定义变化或替换依赖栈，先修订合同再审批。

### 禁止项与非目标

- 不向 /home/ljx/retro_synthesis、/home/ljx/CondRxnBench 或原 retro Conda 环境写入、安装或运行产生缓存的代码；复制只能从旧库只读读取，并记录来源。
- 不覆写/删除历史资源和失败验收；不自动清理 operations/.staging-task011/（核查前已存在的未跟踪暂存，保留）。
- 不把缺失、冲突、零值、不可解析记录过滤成“干净数据”；不修猜测名称/结构/条件。
- 不接入 WORKBENCH_ROADMAP P2 的糖苷感知扩展/评分，不变更 topology.py 的家族定义，不声称新化学有效性；D3/JSME 等 P4 组件不属于本次验收。
- 不执行正式盲测、不制作独立金标准、不晋级模板或库存、不绕过原人工科学门槛。
- 不把原始或受限数据/模型/SQLite/真实运行 JSON 加入 Git、CI artifact 或发布包。CI 用原创/允许分发的最小 fixture；原来源许可逐项保留。
- 不 force push、不删除远端分支、不变更仓库可见性、不替换 Git 身份、不发布外部包或部署公网。

## 执行顺序与阶段门槛

一个 TASK 对应“统一工程基线就绪”这一交付，内部按 G1—G5 顺序推进；阶段不能用其他阶段的成功替代。获批后可在合同范围内连续执行，触发停止条件除外。

### G1：统一工作区与活动资源版本

- 冻结当前来源、构建器、schema 与输入哈希；核对旧版本与报告差异，以新事实追加解释。
- 用新目录完成 v3 与 replay-v3，两者 records 与同一构建器生成的 manifest 逐字节一致；与 v2 做字段级差异报告。仅更新源码哈希等版本元数据时也明确说明，不修改旧 manifest。
- 统一活动指针贯穿资源查询、库存、状态、目标、worker 资源指纹、评估；缺资产/错配必须报可诊断错误，不能静默回退到旧版。
- 原始值/ID/冲突与总量守恒；若新构建无法满足预期，停止，不为了通过断言删记录。

### G2：资源数据库与算法工程合同

- SQLite 由已验收版本构建，显式 schema_version、外键/唯一键、源记录 ID 和源哈希；记录表与来源/QC/收率查询保留原值或原 JSON 定位。缺失与 0 分开表达，生产准入不默认开启。
- SQLite 查询只读；筛选、分页与 JSON 基线逐 ID 一致；全部记录能溯源。索引损坏/过期必须拒绝使用并给出重建方式。
- 覆盖 PUCT 选择、动作融合/去重、替代动作尝试、转置处理、多产物分配与 max_nodes 上限的实质性合同；native 限制明确标注，不把不同节点预算称为公平算法对比。
- 保持每次新 worker/new MCTS；同一 seed、迭代受限且时间预算不成为截断因素时核结构结果重复性；不承诺所有时间预算下位级确定性。
- preflight 读取真实工程/科学门槛，不因本 TASK 工程通过把 formal_run_ready/release_ready 写 true。

### G3：独立 Python 交付

- 构建 wheel 与 sdist，检查原创资源、依赖和 CLI/Web 入口；统一可写工作区，不在安装目录输出运行或缓存。
- 新建 Python 3.10 独立环境，system-site-packages=false；依赖清单不得引用旧 Conda 私有目录或本机不存在的 file:// 路径。核心依赖固定，工具依赖分组；下载/解析失败如实报告，不借用旧环境掩盖。
- 在仓库外当前目录安装 wheel，验证 import、CLI/help、Web、拓扑、默认配置；无数据时明确显示缺资产及恢复方式，有本地受控资产时运行真实 MCTS。
- 在有资产的独立环境跑完整测试与浏览器；确认实际 import/sys.path、版本、worker 解释器与缓存路径均不依赖旧项目或旧 Conda site-packages。代码独立不等于模型必须开源或自训练。

### G4：前端已有能力全部有去向

先形成能力矩阵，逐项绑定后台/CLI → UI 控件或只读入口 → 边界文案 → 验证证据；不能把未实现的能力写成已支持。

| 能力 | 计划展示/操作 | 必须保留的边界 |
| --- | --- | --- |
| 实时搜索 | SMILES/预设、模式、optimized/native、seed、candidate_stock、top_k、seconds/iterations/depth/branching/nodes；展示有效阶段预算和引擎 | 每次新 MCTS；native 节点预算不等价；非法输入/忙碌/引擎失败可见 |
| 路线与证据 | 现有结构树、逐步卡、评分分解、叶子/闭合、JSON 导出；完整版本/资产/代码指纹和 manifest 查看 | 暂定成本；surrogate/partial；actionable/evidence_closed 真实值 |
| 历史运行 | 运行列表、按 run ID 打开、manifest 与文件完整性状态、结果查看/导出 | 明确 explicit_saved_run，加载不得触发普通搜索或伪装为实时结果 |
| 数据库与 QC | 全部 9 个 kind、查询/分页/明细、来源/QC/冲突/失败/收率、版本/索引状态及重建说明 | 候选保留；历史供应记录不冒充当前可采购；文件定位/token 命中不冒充内容核验 |
| 糖苷拓扑 | 现有目标/叶子标注、键高亮、阴性/未知状态、文献关键词联查 | labelled graph synthons, not reagents；未进搜索，不作有效性结论 |
| 教学/文献 | 现有 27 个条目的独立浏览、15 文献卡和课程、路线教学回退/Unknown 状态 | 0.0 Unrecognized 不能生成确定家族解释；关键词关联不等于文献验证 |
| 开发评估 | 固定原有 3 目标×2 seeds×2 engines 的 12-cell 开发对照启动/进度/结果；与搜索共用并发门控，不开放任意执行参数；正式 preflight 只读展示 | 原始 run/cell 与失败保留；非盲测、节点上限不等价、不能据此宣称性能优势 |
| 项目/安装/Git | 活动版本、包/环境验收、工程门槛、代码提交及已记录同步 SHA、科学阻塞原因、重建与启动说明 | 展示的同步状态有核查时间，不通过界面实时凭空声称 GitHub 已同步；科学晋级不开放自动按钮 |

- 1440×1000 与 390×844 验证全部页面和新增入口；脚本覆盖实际参数提交、历史结果加载、开发对照结果、错误分支，不只检查 DOM 存在。
- 保留受限数据为本地展示，不把资源/运行导出默认上传远端。

### G5：GitHub 同步、文档与总验收

- 增加 CI：无受限资产的单元合同、wheel/sdist 构建、仓库外安装与静态资源/配置验证。需要私有模型的测试单独标记；CI 没跑全量 MCTS 时不得写全量搜索已通过。
- 固定本地带资产验收证据，更新 README 的远端事实、目录职责、安装说明、TASK/REPORT/STATE 与长期设计 ADR。
- 逐文件检查拟提交清单和包/CI artifact 的资产边界；旧未跟踪暂存不纳入本次提交。
- 普通提交并推送到现有私有 origin；以 git ls-remote 与 gh API 确认交付提交等于远端 main，并核对该 SHA 对应 CI 结果。远端有未经本 TASK 纳入的更新时停止同步，不擅自合并或覆盖。
- 明确区分“交付提交已同步”和“操作日志追加后的工作区状态”；最终只读验收仍会追加 operations/events.jsonl，其尾部不能被误写成未同步功能提交或隐瞒为完全干净。
- 输出总验收矩阵：五项工程门槛各自 pass/partial/blocked、证据路径、当前科学门槛。仅当五项全 pass 才能宣告本任务的工程地基就绪。

## 验收标准

- [x] 获所有者明确批准：2026-09-26“同意，开始执行”，范围为整个合同；起草轮核查授权单独保留。
- [ ] 新版本和独立重放逐字节一致；3,059 条 ID/原值守恒，123 个来源无哈希漂移；变化逐字段可解释，0 production 与冲突/失败保留。
- [ ] 统一工作区/活动版本，所有入口同版；索引记录/分页/溯源与 JSON 一致；故意错配或损坏能被检出。
- [ ] 真实 MCTS、优化行为合同、资源/预算/失败合同均通过；native 的非等价限制在 API/界面/评估中可见。
- [ ] 独立环境无旧 site-packages 依赖；wheel/sdist 可从仓库外使用；CLI/API/Web/worker 同一上下文；缺资产错误明确；本地资产真实运行通过。
- [ ] 能力矩阵每行有实际入口与验证证据；参数、历史运行、评估、资源/教学/拓扑、项目状态在桌面和移动端均验证；JS 错误为 0。
- [ ] 27 个教学条目可浏览；未识别模板保持 Unknown/边界文案，不伪造家族分类。
- [ ] 原有测试和新增必要合同通过；全量本地与无资产 CI 的范围分别记录，跳过理由不能充当成功。
- [ ] 数据/模型/真实运行不进 Git/发布包/CI artifact；原始与历史版本不改；来源许可完整。
- [ ] 交付提交等于远端 main，该 SHA 的 CI 通过；本地验收证据齐全，追加日志状态如实记录。
- [ ] REPORT-012 与 STATE/导航/架构/环境文档一致；五项全通过才可称工程地基就绪，科学未闭合项仍明确。

## 验证计划

本段为获批后的计划，不是本轮全部已经执行的命令。新增工具应在对应阶段落地，执行命令以 REPORT 记录的实际 argv 为准。

```bash
# 每条命令均以 scripts/operate.py TASK-012 包装。
# 1. 在新独立环境检查依赖与运行合同（解释器路径由 G3 记录）
<独立环境>/bin/python -B -m pip check
<独立环境>/bin/python -B -m unittest discover -s tests -v
# 2. wheel/sdist 构建、仓库外安装与受控工作区 CLI/API/Web 验证
# 3. 两次全新资源构建及 records/manifest 哈希比较，数据库查询守恒与错配反例
# 4. 浏览器全面能力矩阵与真实搜索/历史读取/12-cell 开发评估验证
# 5. 发布前文件边界、diff 和远端/CI 验证
 git diff --check
 git ls-remote --heads origin
 gh api repos/juliusloon/FlavoRetro/actions/runs
```

## 停止条件

- 未批准：只可继续补充审核材料，不得执行 G1—G5。
- v3 原始值/ID/结构/冲突/总量发生不可解释变化，或来源/模型哈希漂移：停止资源切换，保留产物和诊断。
- 需要猜测教学分类、修正糖苷化学定义、执行正式盲测或晋级证据：停止该事项，另立独立 TASK，不挪用本合同。
- 无法在独立环境解析依赖/恢复合法本地资产：报告 Partial，不借旧可写环境代替成功。
- 实现要求超出修改预算，或者必须改变搜索科学语义：先给出修订与影响，等待所有者批准。
- 远端新增他人提交、身份/权限不符、CI 失败或受限载荷可能进入交付：停止推送，保留本地可审结果。
- 历史测试出现无关失败：记录根因，不借机扩大修改。

## 报告、状态与下一步边界

获批执行后，无论完成、部分完成或阻塞，生成 `docs/reports/REPORT-012-foundation-readiness.md`，记录每阶段实际修改、验证、偏差、失败证据及 Git/CI SHA，并更新 STATE。

本次不提前生成一份声称建设完成的 REPORT-012。核查事实冻结于本 TASK 的“起草前核查”与 operations 记录；当前状态标记为 TASK-012 Proposed。

本任务即使完成，也不自动进入 P2/P4/P5、正式盲测或公开发布；下一阶段另行立 TASK，交所有者审核。

## 批准后执行记录

2026-09-26：所有者批准整个合同，开始执行；上文“起草前核查”与起草时措辞为冻结历史，不作为当前执行状态。

G1—G4 已通过：新 v3/重放、SQLite 守恒、优化合同、独立包及全部前端入口验证；51 项本地全量通过，无资产模拟 45 通过/6 跳过。G5 远端 CI/同步正在收口，详见 REPORT-012；起草轮 Proposed 措辞为历史记录。
