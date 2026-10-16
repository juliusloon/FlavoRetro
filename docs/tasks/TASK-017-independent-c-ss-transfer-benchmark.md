# TASK-017：冻结独立评价面板与 C/SS 正式迁移检验

## 0. 合同元数据与当前授权

- 任务 ID：**TASK-017**；版本：**v0.2**；日期：2026-10-13（Asia/Shanghai）。
- 状态：**Partial（v0.2已恢复执行；execution_status=materials_preparation_closed_with_gaps）**。真实preparation_ready=true、research_run_ready=false；方法/科研检查/合成验证与metadata准备已完成，真实独立panel/标签及科学矩阵待输入。v0.1的G0_STOPPED保留为历史执行结果。
- 编制与阶段分工授权：所有者本会话明确同意“TASK-016 按已交付的模板、搜索接入及有限开发效果结项；将 C/SS 的正式独立迁移检验明确写入 TASK-017”，并指示“写 Task 17”。
- 起草轮批准为 agent_delegated，human_reviewed=false，仅覆盖合同及阶段分工登记，记录保留于 operations/task017-draft-20261013/scope_decision.json。
- 执行授权：所有者本轮明确指示“开始执行 task 17”；本会话自主审批记录 agent_delegated，human_reviewed=false。既有执行授权继续有效。所有者随后针对准入拆分方案明确指示“修订。”，批准本v0.2合同及治理登记，记录agent_delegated、human_reviewed=false；修订不授予gold代造或供应/production认证权。修订轮未恢复执行；所有者现已明确指示“根据修订后内容，执行task17”，本轮批准与v0.2快照保存于outputs/evaluation/formal-task017-v2/。原批准合同与起始批准见 outputs/evaluation/formal-task017-v1/approved_task.md、approval.json。
- 人工负责人：项目所有者；工程执行者：Cano。独立标签审核负责人ljx（所有者本轮实际指定；原文见v2/reviewer_nomination.json）；尚无真实标签或审核日期，双源流程如使用须另登记实际核验者。
- 基线分支：main；参考HEAD：993b22f5e8eed5797d27f02c566af1b86a4b7880。当前存在未提交交付，执行批准时须另冻实际合同、代码、模型、审核、库存和输入SHA，不能只绑定HEAD。
- 当前实际交付见§13和[执行报告](../reports/REPORT-017-v0.2-execution.md)：科研检查/执行器及37项合成验证、冻结方法、48书目候选/曝光初筛与ljx空白审核包；真实panel/标签未生成。修订决定仍保留于outputs/evaluation/task017-v02-revision-20261013/revision_decision.json，不改写修订历史。
- 本TASK的一项操作：**对已冻结的领域搜索方法开展一次包含C、糖间成键独立面板的正式对照评价，交付可复核的效果结论及其适用边界。**

## 1. 阶段分工与继承事实

阶段分工见 [ADR-006](../adr/ADR-006-method-delivery-and-independent-evaluation.md)；本次科研准入责任修订见 [ADR-007](../adr/ADR-007-research-evaluation-admission.md)，细化ADR-006的正式前置条款，不改变TASK-016结项或P7终止事实。

| 阶段 | 交付与完成口径 | 当前状态 |
| --- | --- | --- |
| TASK-016方法交付 | 开放来源支持的成键模板、受控独立策略接入、来源限定开发覆盖及旧能力保护 | 按所有者本次决定结项；有限成果不外推 |
| TASK-016-P7 | 原合同的C/SS开发迁移尝试及其历史科学门 | Partial/stopped；原始记录与指标保持，不再作为TASK-016方法交付结项前置 |
| TASK-016-P9 | 已曝光数据盘点、留组缺口及评价预登记 | Completed（规划）；未运行科学矩阵 |
| TASK-017 | 独立面板、科研准入、冻结比较及C/SS实际迁移结果 | Partial；v0.2实际准备门true，待ljx独立输入；科研门false，原G0停止保留 |
| TASK-018 | 消融、误差分析、图表与论文整理 | 未启动 |

“独立搜索策略”指与generic并存的受控模块；“独立评价”指方法设计、构建与评价角色隔离。TASK-016结项不赋予历史对象blind资格，也不证明C/SS泛化已成功。

现有证据入口：
[原TASK-016报告](../reports/REPORT-016-open-glycoside-expansion.md)、
[P1报告](../reports/REPORT-016-P1-open-glycoside-library-expansion.md)、
[P6报告](../reports/REPORT-016-P6-c-scope-runtime-transfer-closure.md)、
[P7终止审计](../reports/REPORT-016-P7-closeout-20261013.md)、
[P9盘点](../reports/REPORT-016-P9-development-evaluation-redesign.md)。

既有合格v6为56模板/89运行上下文，默认关闭；P9已有C13/SS19个不同完整编码历史target。这些是构建/开发/回归资产，不构成现成独立面板。6个C/SS scope的支持各集中单组，不能假定已有同范围留组折可运行。通用模型训练重叠仍unknown。

**任务完成与正增益分别判定。** 有效完成的零/负增益评价可标TASK-017 Completed；缺面板、缺准入、未运行或关键数据无效记Partial/Blocked，不能记成零效果或已完成正式评价。不以先证明正迁移作为正式评价的启动条件。

## 2. 科学问题与方法冻结

主要问题：在事前定义的黄酮/黄酮苷C成键与糖间成键范围内，既有领域扩展对真实MCTS完整参考节点覆盖的效果如何？分别报告来源、母核、位点、糖型、供体及催化模式，不能以O增益抵偿C/SS结果。

本轮评价已交付方法，不在test上开发新scope、修改guard、训练或调参。

| 臂 | 固定方法 | 比较用途 |
| --- | --- | --- |
| A | generic；glycoside_expansion=false | 领域扩展的主要基线 |
| B | 合格P2/v2载荷对应的运行版本v3；glycoside_expansion=true | 旧领域方法的次要基线（54模板/85上下文，执行前核验） |
| E | 合格P6运行版本v6；glycoside_expansion=true | 本轮待评价的已交付最终方法（56模板/89上下文，执行前核验） |

主要比较是每轴E−A，次要比较为E−B。B采用v3的理由是衡量P4/P6增量，E不依赖一个尚未构建的未来增强版本。**这与P7/P9中B=P6 v6、E=未来增强版本的设计不同**，属于本新合同的显式选择，不能与旧A/B/E数字合并，也不能据此追认P7通过。

三臂共享模型、优化树、PUCT、审核视图和17键候选库存。源资产SHA、完整实例/模板支持血缘及最终工程保护记录必须核验；版本号或模板数相等不能替代SHA绑定。方法先冻结，独立评价结构/标签后由隔离角色接触；执行角色无权据test调整方法。

## 3. 范围与文件职责

### 3.1 既有执行授权下的v0.2职责

1. 有界核对评价准备条件、数据角色、合法来源计划、隔离和审核责任；不以已有完整panel或标签作为准备启动条件。
2. 在G0登记合法路径及固定查询/来源名册后，开展有界独立面板准备；原始件到达即SHA冻结，只读保留。
3. 工程层解析、规范化、分组、排除重合与生成无预填gold的审核材料；实际独立标签按§4产生。
4. 实现任务范围内的科研准入检查和正式执行器及必要验证，复用真实搜索服务；既有evaluation.preflight保留兼容行为，方法与标签/隔离要求不变。
5. 通过G0–G3后一次执行冻结矩阵，完成逐cell核对、汇总和REPORT，更新STATE。

| 文件/目录 | 职责与当前状态 |
| --- | --- |
| outputs/evaluation/formal-task017-v1/ | v0.1批准合同、真实preflight、依赖/停止决定、空cell账及终验：只读保留，不追加或覆盖 |
| outputs/evaluation/task017-v02-revision-20261013/ | 本次修订批准、前后文档、保护SHA、验证及交付manifest；不是科学结果 |
| outputs/evaluation/formal-task017-v2/ | 后续新批准快照、准备/科研准入、source/exposure manifests、标签、panel/protocol、cell账及结果；当前已创建，实际交付见§13 |
| data/inbox/task017-independent/ | 合法到达的独立原始件；到达即只读冻结，不入Git；空目录或目录缺失不证明科学可达/不可达 |
| flavoretro/formal_evaluation.py | 拟新增preparation与research-run检查、正式冻结/校验/配对汇总模块，复用service.search；已实现并完成合成验证；实际科研准入尚未通过 |
| scripts/task017_formal.py | 拟新增freeze/check/run/verify入口，运行前强制科研准入；不调用旧P7 epoch写入器；已实现并完成合成验证；实际科研准入尚未通过 |
| tests/test_task017_formal.py | 拟新增准入拆分、隔离/固定分母/失败/哈希/真实结果绑定测试；合成fixture不计科学结果；已实现并完成合成验证；实际科研准入尚未通过 |
| flavoretro/evaluation.py | 现有12-cell开发比较与旧preflight保留兼容；旧formal_run_ready不代表v0.2科研放行 |
| metadata/release.json | 保持原状态；本轮局部协议/标签/结果在v2证据中登记，不自动晋级全局科学、供应或production字段 |
| docs/reports/REPORT-017-independent-c-ss-transfer-benchmark.md | v0.1 G0停止报告只读保留；不改写为v0.2结果 |
| docs/reports/REPORT-017-v0.2-admission-revision.md | 本次合同修订报告；后续执行另交版本报告，不覆盖v0.1或本次修订报告 |
| STATE、ARCHITECTURE及索引 | 登记当前版本/实施状态，区分修订完成与评价完成；旧科学账保持历史 |

### 3.2 禁止项

- 恢复R80、重开已关闭epoch、继续Liu2021/R73等具名停止内容；旧prospective许可不作为TASK-017批准。
- 修改旧科学结果、原始来源、曝光时间、P7中央/epoch账或P9交付；换agent/文件/任务编号不能消除已发生曝光。
- 用test或其参考调整scope、模型、参数、支持选择规则；新增模板或重建领域方法须另行开发任务。
- 以人工猜测补复杂结构、将来源定位当结构审核、将候选命中当真实节点、将代理标签冒充独立gold/human_reviewed。
- 绕过v0.2真实科研准入、伪造来源/标签/隔离/供应/production资格；合同批准不替代实际核验，旧preflight为false也不自动证明科研门通过。
- 启动TASK-018、供应/发布晋级、Git提交/推送、对外发送材料或写入历史目录。

## 4. 独立面板与标签规则

### 4.1 有界准备与分步来源登记

G0登记合法入口、固定查询/来源范围、接收顺序、结构/证据字段、预算和审核交接安排。**不要求G0之前已存在独立标签或C/SS各6目标/2组**；最低面板在G2用实际证据验收。metadata-only线索可用于可达性计划，预计名额和未核对线索不计实际target；入口目录不存在不是来源已穷尽或不可达的证据。

默认合法路径仍限所有者合法的新SciFinder导出，或登记的公开出版方/API具体实验来源；没有假定账号、专利API或机构访问权。先冻结固定查询、渠道/范围和排序规则，再执行一次预算内metadata发现；候选ID在得到metadata后、任何原文/结构级读取前冻结。不能要求检索前就知道尚未发现的ID，也不能根据科学运行结果切换来源路线。

方法先冻结，再由已落实的隔离角色接收评价内容。审核计划/责任在G0登记，真实内容接触和gold裁决角色须在相应操作前落实，不编造具名审核人。尚未落实内容/标签角色时，可完成合成fixture与不消费test内容的工程/metadata准备，不能生产gold或宣称盲法成立。

本次修订没有激活新查询或新来源批次。后续按上述路线和原累计预算登记一次有界准备；合法访问、隔离交接或可信来源计划无法落实时停止相关阶段。供应unresolved、production投影0以及尚未产出的panel/标签不单独阻止准备，不再因这些状态触发“上游必须先全部关闭”的循环。

### 4.2 纳入、排除与采样

- 主集合是形成新C糖苷键或糖间键的具体单步实验实例；水解、已有键保留和保护操作另列支持步骤，不补C/SS名额。
- 领域边界继承 [DOMAIN_TRIAGE_V1](../protocols/DOMAIN_TRIAGE_V1.md)，由真实标签确认。非黄酮酚类/其他天然产物不因带糖自动进入本主panel。
- 已有完整product、acceptor、真实donor、位点、关键立体及完整reference precursor；标准化保留盐、立体、同位素、组件重数及原始图，不猜补、不用UDP糖替代真实化学供体。
- 与所有开发/构建材料检查文章/DOI、专利家族、真实source/assay/cohort、父实例和精确反应的传递闭包；与所有臂build共享相同产品亦排除独立test资格，其他合法参考路线不洗掉target重合。
- 从P7原始曝光事件、永久曝光投影、补充账及既有开发清单只读生成TASK-017角色清单；别名未知且会影响分割者阻断准入。H5/G7历史缺口在新清单中逐项核对，不改写旧G7为pass。
- P9的C13/SS19、旧17回归目标及其开发来源只用于方法/工程校准；已曝光对象不能进入本独立主panel。未读对象仍需完成全部准入，不能仅凭unread=true纳入。
- 共享母核不自动等于来源泄漏。Murcko骨架/核心相似性用于分层并披露结构新颖程度；精确产品、反应及真实来源闭包是硬排除。相同母核上的新目标可以回答范围内迁移，不能冒称跨骨架泛化。
- 主panel按事前质量/领域条件和固定来源ID哈希顺序选取，逐条保存排除原因。不能按E完整参考命中、scope适用性或A/B失败选样；领域内scope未覆盖目标仍留在主分母。

计划上限：C12、SS12、O参照6，共最多30个不同target；最低正式双轴panel为C6/SS6，各至少2个经核对的独立来源组。O参照可选，数量与是否包含在第一次结果前冻结，不能抵偿双轴缺额。候选不足按实际短缺报告，不复制上下文凑target。每轴6/2为本项目最低可评价门，不是统计功效或广泛外推保证。

既有 [盲测预注册v1](../protocols/BLIND_BENCHMARK_PREREGISTRATION_V1.md) 仍为未执行的Proposed历史方案。本合同明确细化/调整其provisional规模、聚焦C/SS成键，并将共享Murcko骨架由硬排除改为分层披露；独立标签、精确重合、真实来源闭包与先冻结后评价的原则继承。旧v1查询/导出权限不因本修订自动激活；TASK-017来源批次须按§4.1和原累计预算实际登记。

### 4.3 标签、盲法与审核溯源

独立gold沿用既有规则：由所有者亲核或经登记的文献双源流程产生；Cano/工程agent不产生、修改或预填gold。文献双源须为两条真实、相互独立且支持同一具体反应的证据链，不能用次级转述/同一实验别名充数。

G0登记实际审核者、证据责任和裁决流程；结构工程层与标签层分文件、分权限，标签角色不看模型建议、臂身份、排名、候选输出。工程代录所有者结论保留agent_transcribed和原始指令，不冒充亲核。

审核者可以按冻结方法合法读取test并生成标签；该读取记evaluation_labeling，不因此自动判为开发泄漏。若标签/结构反向影响方法、支持、规则或参数，则相应对象转为development_exposed，按既定规则排除，不能靠换角色恢复盲法。披露实际角色隔离，不能只凭新文件名宣称盲法成立。

一般模型训练重叠保持unknown，ORD/USPTO及已知训练衍生集不作独立来源。可声称的隔离限于已核对的项目构建/开发与评价角色；不自动声称对generic训练从未见过。

## 5. 科研准入与分阶段操作

### 5.1 三种资格各自判定

| 层级 | 必要条件 | 不作为本层前置的条件 |
| --- | --- | --- |
| preparation_ready | 执行授权/版本/预算可追溯；方法及工程资产可冻结；合法有限来源计划、角色与隔离安排；没有具名停止对象被重新启用 | 已有独立gold、已满6/2面板、当前供应approved、非零production投影 |
| research_run_ready | preparation检查通过；实际冻结A/B/E与代码/参数/模型/审核/17库存；C/SS真实最低panel、独立标签、逐项一手参考核验、来源/曝光闭包、协议批准和执行器验证全部通过 | 全库primary_source_review=approved、供应approved、production template/stock非零、release_ready |
| 供应/production/发布资格 | 继续使用相应真实证据和原治理规则；不得由科研评价自动晋级 | 研究矩阵完成或正增益不能替代认证 |

一手证据要求改为本轮方法支持血缘可追溯、评价实例完整结构与反应参考逐项核验，并核对方法/评价隔离；不是要求全部3059资源或通用训练模板先人工晋级production。方法来源未知、通用训练重叠unknown等状态继续披露；影响主panel独立性或参考正确性的unknown仍阻断相应对象。

拟新增任务范围内科研检查，输出profile=task017_research、contract/input SHA、preparation_ready、research_run_ready、blocking_reasons、nonblocking_status及检查明细。必须检查实际文件/结构/标签/来源关系/哈希/授权，不能只读几个approved字段、目录存在或非零计数便放行；未实现或未检查记null，缺失必需证据则false，正式入口仅接受本轮真实research_run_ready=true。

旧evaluation.preflight及其formal_run_ready字段保留原含义、CLI/API兼容行为；v0.1真实false保留。当前release_ready=false不修改；旧门不再是TASK-017 v0.2科研矩阵的放行依据，也不能将新科研true误报为旧门或发布true。旧门、科研门、production资格按profile/范围分别展示和登记。

### G0 授权、保护、准备计划

继承既有执行授权，保存v0.2批准快照与修订决定；新建后续v2工作区，不覆盖v1。核对模型/方法/保护资产，登记有限来源/角色/隔离/交接计划与累计预算。G0允许尚未产出标签或panel；preparation条件失败停止相应准备，不能因供应或production状态替代科学准备判定。

修订轮仅登记合同时preparation_ready=research_run_ready=null；本轮实际检查为true/false，见§13。v0.1记录仍显示release=research_candidate、全局来源/供应unresolved、标签not_available、协议字段缺失、production=0/0；这些不是v0.2已通过的证据。

### G1 方法冻结、准备实现与来源接收

按§2先冻结A/B/E和参数，再按§4.1注册路线接收、SHA冻结、解析并交由真实角色独立审核。科研检查/执行器可先在合成fixture上实现验证，无须等gold已存在；不得用实际test进行实现调试、模板重放或参数试跑。保留全部候选、排除、访问/曝光及失败，不看模型输出填panel，不改已冻结搜索方法。

### G2 Panel、独立标签与协议冻结

冻结不同target、合法完整参考集合、逐项一手定位与标签批准、来源闭包、开发重合、六维分层和选择分母。C/SS每轴至少6目标/2组的门在此验收；任一不足停止双轴正式矩阵并报告Partial，不用另一轴或O补位。来源、标签或结构核验失败保留真实原因，不能写成无增益。

任务局部protocol_review记录实际审查者/权限、具体protocol与合同版本/SHA、批准范围、时间、依据及agent_delegated/human_reviewed溯源。v0.2合同批准可作为准入设计批准依据；最终panel、标签或新增执行细节未冻结/未核验时仍pending，已有执行批准不自动证明这些事实。全部绑定完成后才允许G3。

### G3 执行器核验与科研放行

合成fixture须覆盖：供应unresolved及production=0在研究证据齐全时不阻挡科研门；缺标签/协议/闭包、方法/输入哈希漂移、test回流开发、分母变动则阻断；准备门不依赖已完成panel；旧preflight/CLI/API行为不被改变。fixture只证明检查逻辑，不能产生实际科学资格。

保存真实profile=task017_research的完整检查结果，要求research_run_ready=true，并核验panel/标签/来源闭包/参数/调度/预算/执行代码全绑定。正式run入口再次核验，拒绝过期preflight或漂移输入；不调用旧12-cell比较器冒充正式评价。本轮检查器/执行器已实现并完成合成验证；实际缺独立输入的科研门仍false，不能据工程验证启动矩阵。

P6旧能力保护在资产/代码绑定相同时继承；必要重跑按原预算单列。任一科研运行前置失败，正式矩阵0 cell、指标null。局部科研证据写v2，metadata/release.json及供应/production记录保持；后续全局晋级须另有权限和事实。

### G4 一次冻结对照矩阵

同target×seed0/1/2×A/B/E，随机化臂运行顺序用固定调度seed20261013；每cell新进程、新run ID、不读搜索结果缓存、不回退BFS。运行顺序在结果产生前入ledger。

共同预算：engine=optimized、mode=quick（现有单phase）、candidate_stock=true、top_k=5、seconds=30.0、iterations=100、depth=6、branching=12、nodes=2000。phase列表、实际消费量、领域cap/prior/weight及generic前三保护绑定SHA；三臂只改变§2的领域开关/版本。达到预登记搜索预算是正常结束；外部超时/崩溃/worker错误保持错误状态，不能伪装正常无命中。

SearchRequest只接收target及统一冻结参数；test的供体、酶名、位点和reference只用于隔离评分/分层，不能作为按目标定制的候选生成提示。build侧已冻结的模板上下文保持原有语义。

不同时比较native/optimized，以免将不同节点预算语义当作等价。任何字段/单phase语义不被现有服务支持，在合成实现核验时停止并修订合同，不能等看到test再改变预算。

### G5 核对、统计与结案

对run request/result/manifest/action/node/trace逐cell绑定，核对登记矩阵与账本，固定规则汇总两轴效果、失败与不确定性。输出有效零/负结果，不能追成绩追加cell。符合§7则Completed；未满足正式前置或有效性条件则Partial/Blocked并列缺口。

## 6. 指标与分母预登记

完整reference为保留立体/盐/供体/组件重数的canonical isomeric precursor多重集合；一个target允许多个已冻结合法完整集合，命中任一才算完整。部分前体或只生成候选不计完整created node。

主指标分别按C/SS报告：每个target三seed完整参考created node命中率的E−A平均差；E−B为次指标。按登记target总数、正常配对数和来源组同时报告，保存generated/truncated/filtered/created各层匹配、节点/时间成本、非reference挤出及generic前三保护。

- 正常运行的完整命中记1、正常未命中记0；未运行/错误/外部超时科学结果null。
- 错误保留在登记panel；不得悄悄缩小主分母。存在缺失时，完整panel的科学效应记null；有效配对子集效果可单列并声明覆盖率，同时给登记总数上的操作成功下界。
- seed是同target重复，不增加独立target/group数。来源组有多个target时保留其相关性。
- N_gap为A/B三个seed均正常且均无完整created参考节点的target数；G为其中E三个seed均正常创建完整参考节点的target数。N_gap=0时G/N_gap=null。
- reference gain/loss按臂正常配对逐target/seed保存，并报三seed一致target计数。E错误不能算正常reference loss=0，更不能支持零损失验收。
- 主要分母不依赖scope是否命中；事前声明的core/site/sugar子集只作分层诊断，不能用结果修改主panel。
- 路线partial、surrogate candidate-stock closure、evidence_closed分别报告。17键候选库存命中和完整参考节点不是实验可合成性/证据闭合/供应认证。

每轴独立来源组>=5且主panel完整观测时，按来源组整体重采样2000次，保留组内targets与全部seeds，重算target加权配对效应；固定bootstrap seed20261013，报告每轴97.5% percentile区间并说明两轴多重比较与小样本局限。少于5组只报逐组效应、范围和描述性计数，区间为null，不宣称统计显著或广泛优越性；正式实验的执行事实仍可有效结案。

“正迁移能力”与执行验收分离：本轮可另报告是否达到项目参考门（每轴>=6 targets/>=2 groups、G>=3、G/N_gap>=50%、成功>=2组、至少3个不同target跨>=2组满足A/B三seed无节点而E全创建、相对A/B净参考覆盖>0、reference loss=0及旧能力保护）。该门在本新B/E定义下解释，不能改写P7判决。E−A收益与E−B增量分别保留；有效实验未达门记effect_pass=false，未运行/不可评价记null。

## 7. 完成验收与状态

- [ ] AC01：既有执行授权与v0.2准入修订溯源完整；准备/科研运行阶段分开，合同/资产/输入/累计预算SHA与保护基线齐全，v0.1及旧P7历史保持。
- [ ] AC02：C/SS每轴至少6个结构/标签合格、来源及角色隔离目标，至少2个独立组；每项排除、unknown和多reference可追溯。
- [ ] AC03：独立标签/盲法实际来源和角色清楚；无工程agent预填gold、无历史目标漂白、训练重叠不冒充已排除。
- [ ] AC04：A/B/E固定，主要/次要比较与旧P7/P9基线差异明确，主分母不按输出选择。
- [ ] AC05：真实profile=task017_research且research_run_ready=true，实际panel/独立标签/逐项参考/闭包/协议/运行绑定全部通过；任务局部资格不冒充供应、production、旧formal或发布放行。
- [ ] AC06：一次预登记矩阵全部应运行cell有可验证的正常完整结果，正常预算耗尽与外部超时区分；错误/缺失按规则保留，不能以子集冒充完整完成。
- [ ] AC07：真实reference action/node、各层trace、登记/有效分母、成本及错误守恒，可由冻结结果重新汇总。
- [ ] AC08：C/SS分别报告有效正/零/负结果、不确定性、来源/范围局限、effect_pass与任务状态；不以正增益作为Completed条件。
- [ ] AC09：旧能力检查完成并报告实际损失，保护SHA与独立性终验通过，无后验方法/面板/预算更改；真实能力退化计入效果结论，不伪装成工程失败或删除负结果，未改旧科学账或发布资格。
- [ ] AC10：同编号REPORT、STATE、交付manifest与逐cell账一致；独立重新汇总不重新运行模型。

正式评价Completed须AC01–AC10全部满足。有效的零/负增益可以Completed；错误造成主panel缺失则Partial，能单列正常配对子集但不能宣称完成全部正式矩阵。标签、前置或面板准备完成而没有正式运行，也只能报告相应阶段完成，TASK整体Partial/Blocked。

状态字段分开：method_delivery_complete（继承true）、preparation_ready、panel_ready、research_run_ready、legacy_formal_run_ready、evaluation_complete、c_effect_pass、ss_effect_pass、claim_scope、release_ready。修订轮preparation_ready=research_run_ready=null的历史保持；本轮实际preparation_ready=true、research_run_ready=false、panel_ready=evaluation_complete=false、效果null，legacy_formal_run_ready=false及release_ready=false保持。任务整体仍Partial，工程/metadata准备完成不等于科研评价完成。

## 8. 有界预算与立即停止条件

以下沿用原TASK-017累计硬上限，不因v0.2或新输出目录重置。v0.1 G0和本轮修订消耗均保留；后续G0须合并原budget_accounting与本次operate事件扣除命令预算，其他失败/尝试同样累计。原G0预算快照记local_commands_total=22，快照后操作及本轮需据追加事件核对，不能将22当最终已用量。本轮新增科学及来源运行消耗为0：

| 项目 | 硬上限 |
| --- | ---: |
| 经operate记录的本地执行命令 | 120 |
| 新发现查询 | C6+SS6共12条，执行查询前于G0登记渠道/查询/范围/排序，一轮；不循环换词 |
| 新原件HTTP尝试/字节 | 120次 / 512MiB，失败与重试均计账 |
| 新文章版本/附件 | 24 / 48；超出不自动加额 |
| 结构化输入内容 | 120个文件 / 200MiB，原件下载另账 |
| 正式target | C<=12、SS<=12、O<=6，共<=30 |
| 正式科学cell | N_registered×3seeds×3arms，最多270；每登记cell最多一次尝试 |
| 旧17目标×3seed回归 | 最多51；仅确需时单列，继承有效旧证据不重复运行 |
| 工程运行尝试（含错误fixture） | 最多24，不能作为科学结果 |
| 全部运行尝试合计 | 最多345，未用额度不转为追成绩重试 |

没有合格最低面板或research_run_ready未实际为true时，正式科学额度不能动用；准备/合成fixture无需已有标签或完整panel，但仍受合法访问、方法冻结、角色隔离与预算约束。来源/结构/运行失败完整保留，不退款、不通过换TASK/epoch自动增加预算。零新scope、零训练/调参、零旧epoch恢复、零Git同步。

立即停止相关阶段并报告：①合法访问/结构/独立标签/源身份无法闭合；②闭包或历史曝光未知且必须假定独立才能纳入；③相应阶段的必要证据无效，或启动矩阵时科研门未实际通过（供应/production未认证不是本科研门的失败理由）；④合同/资产/方法/保护SHA漂移；⑤触及预算；⑥test参与方法调整或结果驱动换分母；⑦需要解锁具名停止内容、重新设计方法或追加源路线。

不得把“停止”转为默认无限修复队列。没有面板就是不可评价；有效负结果就是负结果。新增方法、重新试验或正式门改变须另立明确动议，保留原失败。

## 9. 验证与报告要求

未来实现须完成：准备/科研/旧门范围与兼容验证、供应/production非科研阻断测试，以及固定输入/模型/代码/审核/库存哈希校验、合成泄漏/未知/缺文件/错误/组件重数/真实结果绑定测试、逐cell账守恒、仅从已存结果进行的独立重新汇总。若资产和运行逻辑未变，复用已核对的历史工程证据，不重跑整套科学回归。

具体freeze/check/run/verify CLI在实现时登记并与批准合同绑定；本合同不把尚不存在的入口写为已运行命令。每次操作都经 scripts/operate.py TASK-017 记录；不直接执行现有12-cell compare来充当正式矩阵。

v0.1原报告只读保留；本次修订报告为 docs/reports/REPORT-017-v0.2-admission-revision.md，后续实际v0.2执行另交版本REPORT并绑定新v2事实源，不能覆盖历史。报告须有G0–G5状态、输入/独立标签/来源与曝光边界、面板漏斗、三臂SHA与预算、全部cell与失败、C/SS分轴效果及区间适用性、旧能力/科学主张与未完成项。原始/受限结构、标签明细和本地载荷不入Git。

起草轮验证与范围决定保留于 operations/task017-draft-20261013/；该目录不是正式评测结果。v0.1实际G0交付见 outputs/evaluation/formal-task017-v1/ 和原REPORT；本次修订审计见 outputs/evaluation/task017-v02-revision-20261013/，未翻转release、未读取新科学来源。

## 10. 修订记录

2026-10-13 v0.1：依所有者明确决定建立TASK-017合同。TASK-016按已交付方法及有限开发效果结项；C/SS正式独立迁移验证在本合同中承担。P7保持Partial/stopped，原科学门和历史指标保留，不再阻挡TASK-016方法交付结项。合同Proposed，执行尚未批准。

2026-10-13 执行登记：所有者“开始执行 task 17”，自主审批agent_delegated，human_reviewed=false；批准原文SHA为 036c4448f84cda2329b111345e5249688817bca60fe15e185f5498ffda356f09。按v0.1执行G0并触发既定停止条件，未更改科学方法或门槛。

2026-10-13 v0.2：所有者明确指示“修订。”；按§5拆分准备、科研运行和供应/production/发布，原§6指标、§2比较及预算容量不变。当前合同批准、检查待实现、执行未恢复；详见§12。

## 11. v0.1历史执行与停止（只读事实）

**Partial；G0_STOPPED；execution_status=stopped_at_G0。** 已批准、快照并核验现存资产；真实preflight的formal_run_ready=false，来源/供应unresolved、独立标签not_available、协议审核未登记、production template/stock=0/0。独立审核者未实名、两个独立接收入口均不存在，上游无本轮可执行关闭安排，按当时v0.1的§4.1、G0及§8①/③停止。

G1–G4未启动；G5仅提交停止报告。正式科学、模型推理、工程/回归搜索、新查询/HTTP/原文结构读取均0；panel_ready=false、evaluation_complete=false、c_effect_pass=ss_effect_pass=null，全部迁移指标null。当轮按v0.1止步；已有TASK执行授权继续有效。v0.2的新准入设计见§5及§12，不能把本段历史失败当作新版检查结果；来源范围变化仍须明确登记。P7关闭、曝光、TASK-016方法结项及release状态保持。

同编号[REPORT-017](../reports/REPORT-017-independent-c-ss-transfer-benchmark.md)记录阶段、AC01–AC10未完成项、资产继承核验、预算、纠错与继续所需输入；机器决定见outputs/evaluation/formal-task017-v1/stop_decision.json。无独立gold、无新scope、无Git同步，未创建恢复循环。


## 12. v0.2修订轮登记与当时下一步（历史）

2026-10-13，所有者在科研/供应/发布拆分方案后明确指示“修订。”。修订已批准并登记（agent_delegated、human_reviewed=false）；沿用既有TASK-017执行授权，不重复索取执行批准，不据此生成标签或认证供应/production。

本轮只完成合同、ADR、路线图/状态及修订报告。execution_status=not_resumed_after_v0_2_revision；preparation_ready=research_run_ready=null，相关代码、真实检查、独立panel及正式矩阵均未生成。旧evaluation.preflight和release未改，v0.1 G0停止证据及REPORT完整保留，P7继续Partial/stopped。

后续顺序：先依新G0合并预算/冻结方法/登记合法有限来源及审核交接；在合成fixture上实现科研检查与执行器；按G1/G2准备独立面板及真实标签、冻结协议；通过G3实际科研门后才可运行一次G4矩阵。工程或数据准备不足逐阶段报告，不再要求先获得供应/production或先已有gold才能动工。

本次[修订报告](../reports/REPORT-017-v0.2-admission-revision.md)与[ADR-007](../adr/ADR-007-research-evaluation-admission.md)说明具体责任变化；修订决策、前后文档及验证保存在 outputs/evaluation/task017-v02-revision-20261013/，不是科学评测结果。

## 13. v0.2实际执行登记（2026-10-13）

所有者“根据修订后内容，执行task17”授权恢复；agent_delegated、human_reviewed=false。实际审核负责人ljx已实名登记，但未收到真实独立标签。原批准v0.2合同与SHA、方法/保护及累计预算保存于outputs/evaluation/formal-task017-v2/，v1及修订轮原件不改。

实际profile=task017_research，preparation_ready=true（metadata与合成工程范围）、research_run_ready=false，execution_status=awaiting_independent_review_input。科研检查/执行器与37新增合同测试完成，既有16项通过；2次旧错误/超时mock计工程尝试，无真实MCTS。固定12查询得到6成功/6 HTTP503，连同服务检查14 HTTP、29316字节、48书目候选；2条匹配既有prior仍需处置，余46也未证fresh。所有原响应/失败及空白审核包保留，原文/结构/附件接收与新科学读取0。

G0通过准备门；G1方法/工程/metadata完成但原始结构未到；G2真实标签/闭包/最低panel与最终协议待ljx输入；G3仅合成核验、实际放行false；G4未启动；G5仅本轮准备报告。科学cell0，C/SS效果null，旧门/release/P7不变。run已实测在search前拒绝缺证矩阵，不追加发现轮次或启动旧reader/epoch。

[REPORT-017 v0.2执行](../reports/REPORT-017-v0.2-execution.md)与v2/decision.json记录当前单一状态、所有AC缺口、预算和继续所需真实输入；已有执行授权有效。

## 14. 所有者指示的旧资料准备补充（2026-10-13）

TASK-017资料整理补充（2026-10-13）：[报告](docs/reports/REPORT-017-materials-preparation.md)、[材料入口](outputs/evaluation/task017-materials-preparation-20261013/README.md)。48索引全保留：16无效作独立实验原文、14 SI/11语法母桶、18候选；36母标识桶未冒充闭包。登记范围内27未定位正文、1先核prior、1已有文档待确认实验角色、7不索原文；范围/版本线索逐条保留，不要求重复48篇PDF。既有32历史目标/34上下文（C13/SS19）整理成结构/原文卡，23卡材料字段与定位齐备（C7/SS16），9卡保留7供体角色/2定位与酶名对应缺口。全部development_exposed，不进入新独立panel；0实际人审/gold、0独立就绪反应/科学cell，指标null。ljx保留实际核验与结论，本轮无需提前审核。已复核15份既有开发XML，不读取具名停止内容，不改旧科学/epoch账；新查询/HTTP/方法变更/MCTS/Git同步0。原累计结构化输入120/120（29,238,560字节）、发现查询12/12已触及上限，本准备阶段有界收尾，继续新来源摄入须先明确有限额度/范围调整；不因目录更名重置。agent_delegated、human_reviewed=false。

本补充不修改v0.2方法/独立性/验收/预算合同，v1/v2批准快照及历史报告只读保留。资料准备已按当前范围收尾，整体正式评价仍Partial。

## 15. 2026-10-15 定向证据与PDF补件补充

所有者在原额度用尽说明后明确“继续工作，把具体反应的结构与原文证据配齐后，最后给我审核，补PDF”，并选择正文及必要SI。本会话自主批准agent_delegated、human_reviewed=false；批准原文、具名来源清单与旧消耗见outputs/evaluation/task017-evidence-completion-20261015/approval.json。

限定既有32历史目标/34上下文与已列9张缺口，最多15篇具名母文献、30附件；结构/原文角色只作工程整理，真实化学核验和结论由ljx最终作出。无法可靠绑定的反应从就绪队列撤出并保留，不为了凑齐而猜结构或供应体。没有新独立panel来源批次或科学矩阵授权。

本次显式调整原累计硬上限：本地命令120→200；发现/身份查询12→20（新增最多8条具名身份/定位，不作宽泛检索）；结构化输入120→200文件、200→400MiB。HTTP120、原件512MiB、24文章版本/48附件及科学/工程运行上限均不增加。本次不重置旧消耗；旧120文件/12查询及所有失败照计。继续沿用§8其余停止条件；一轮有限补件后收尾，不默认派生新恢复轮次。

新交付outputs/evaluation/task017-evidence-completion-20261015/；20261013资料包、v1/v2批准与报告保留只读。方法/范围/独立性/科学验收不变；历史目标仍非独立test，原P7/Liu2021/R73/R80停止和旧账保持；0模型/MCTS/提交推送/发布。
## 16. 2026-10-15 有限补件交付

本次§15工程准备已收尾：32历史目标/34上下文保留，25主表（C7/SS18）、4范围核对附录、3暂缓；14篇正文PDF与14份必要SI已归档核验（13复用/1新取得）。来源酶/供体/结构纠正均为待审工程提议，原图、原target与历史科学账不覆盖。实际人审/gold/领域结论全空，ljx可按START_HERE核验25条主表。Sasaki2015正文/SI出版方403待补，HIST-24/27暂缓；GuApiGT9a缺具体鉴定，HIST-25暂缓，不索其已有PDF。此前48书目候选未扩搜或宣称全部补齐。

本轮421项工程核验通过；877实质保护文件及旧准备包SHA一致，旧快照另列42缺失AppleDouble侧车，时点unknown，未恢复或删除；无全浏览器交互验证。详见[本轮报告](../reports/REPORT-017-evidence-completion-20261015.md)及outputs/evaluation/task017-evidence-completion-20261015/verification.json。累计额度沿用§15，全部失败和旧消耗见budget_accounting.json。

execution_status=historical_review_packet_delivered_with_three_deferred_cards，TASK整体Partial；preparation_ready=true、panel_ready=evaluation_complete=false、research_run_ready=false，独立fresh目标/gold/科学cell均0，效果null，legacy formal/release仍false。全部为历史开发资料核验；人工审核不能使其成为fresh独立test。G2独立标签/闭包/合格panel和最终协议、G3真实放行、G4矩阵仍未完成；本轮交付不勾选正式AC02–AC09。批准agent_delegated、human_reviewed=false；无方法/MCTS/新epoch/旧停止源解锁/Git同步/发布。旧20261013包、v1/v2批准与报告保持只读。

## 17. 2026-10-15 所有者直接委托最终代理审核

所有者明确“这不需要我审核啊，你直接就能干掉。直接你审核完”；按本会话自主授权批准agent_delegated、human_reviewed=false。取代§15/16对本轮历史32卡由ljx逐条审核的交接安排，直接由Cano作有来源的最终代理裁定；不把代理结论冒充实际人审、独立gold或fresh面板，不改变正式科研验收要求。

限定32历史目标/34上下文，包括25原主表、4范围附录与3暂缓。已有正文、SI、XML及合法HTML为一手证据；某篇PDF归档缺口与科学证据是否充分分别判断，不自动因缺PDF而拒判，也不因HTML可读而臆补鉴定。接受/排除/不足、结构/酶/供体纠正与GT步骤/全体系/盐型边界逐条记录；旧载荷/人工空白模板/历史账保持只读。不会要求所有者重复审核本次代理结论。

一次有限代理审核，累计本地命令上限200→280，旧命令/失败及审核说明读取全部照计；来源文件200/400MiB等既定额度不增加，新查询/新HTTP/新外源输入均0，科学/模型/MCTS/Git/发布0。触及新限额或需要解锁具名停止内容则停止对应项；证据不足记最终不足，不派生无限补件循环。接受项仅历史资料/开发用途；research_run_ready与legacy formal/release保持false。

验收：32卡34上下文逐项裁定与定位；代理更正和未解缺口单列；独立agent复核、保护SHA、同编号报告/STATE与机器摘要一致。批准/输入快照及最终结论见outputs/evaluation/task017-agent-adjudication-20261015/；20261013与本日上一材料交付包保持只读。

## 18. 2026-10-15 最终代理审核结果

§17限定历史代理审核已Completed；所有者不再承担本轮逐条复核。32卡/34上下文最终纳入25（C9/SS16）、领域排除4（HIST14/15/26/30）、证据不足3（HIST12/16/25），实际源文件/图谱和纠正见outputs/evaluation/task017-agent-adjudication-20261015/与[报告](../reports/REPORT-017-agent-adjudication-20261015.md)。所有判决agent_delegated、human_reviewed=false，不生成gold。

HIST02旧图拒绝，hesperetin完整图纠正接受；02/17最终采用Cm1,2RhaT来源绑定，不批准MpRhaT同义。Gu4a/7a的旧标准品声明撤销，连同9a不足。HIST24/27结合合法一手HTML与2018实验可接受，不将缺PDF格式自动当作缺科学证据；PMC5856881现有SI仅引物、FigS1 EPS未核验，接受依据限正文Fig3等已核内容。领域排除与各实例鉴定限制分别保留；所有采用图以新overlay保存，旧目标/评分/模板/账不回写。

三位主审及5卡指定论点独立交叉复核完成，820项交付检查通过，224证据绑定源SHA/90页文本/67段落文本核验。旧上一材料包208文件、20261013资料92文件、785实质保护文件不变，42旧缺失AppleDouble侧车未知时点仍保留披露。未作完整浏览器交互或新湿实验；检查和代理裁定不冒充独立化学验证。

本轮agent_review_complete=true，execution_status=final_agent_historical_adjudication_completed；TASK整体仍Partial、research_run_ready=false，独立fresh/gold/科学cell0，C/SS效果null，精确正式参考0，legacy formal/release=false。接受仅到规范化历史GT步骤，G2新独立标签/闭包/面板/最终协议与G3/G4仍未完成，正式AC02–AC09不勾选。累计命令受280上限，旧消耗失败照计；来源文件/字节及查询/HTTP继承未增，新HTTP/查询/下载/外源/模型/MCTS/运行时/Git/发布0，不派生自动补件或恢复旧停止源。
