# TASK-016-P9：现有数据可测性盘点与开发评价重设计

## 0. 合同元数据与授权

- 任务 ID：**TASK-016-P9**；合同版本：**v0.1**；日期：2026-10-13（Asia/Shanghai）。
- 状态：**Completed（2026-10-13，D0–D4规划交付完成）**。
- 合同编制授权：所有者在本会话指示“好，落实成一个具体的task”。本授权覆盖本合同、索引与当前状态登记；不推定批准本任务执行、P7恢复或新的科学读取。
- 范围与编制决定记录 `agent_delegated`；`human_reviewed=false`。执行批准：所有者本会话“批准执行”，记录 `agent_delegated`；批准绑定见 `outputs/task016-p9/v1/approval.json`，不得借用P7旧approval。
- 人工负责人：项目所有者；拟执行者：Cano。此次不要求增加子代理或恢复旧reader角色。
- 工作区：`/home/ljx/FlavoRetro`；参考分支：`main`；参考HEAD：`993b22f5e8eed5797d27f02c566af1b86a4b7880`。HEAD不代表当前大量未提交交付；执行时另冻实际输入/脚本/合同SHA。
- 起草基线：`operations/task016-p9-draft-20261013/baseline.json`；已有文档字节保存在同目录 `before/`。
- 批准执行后的计划输出：`outputs/task016-p9/v1/`；计划报告：`docs/reports/REPORT-016-P9-development-evaluation-redesign.md`。盘点/规划产物已生成；科学矩阵未执行，见同编号REPORT。
- 本TASK只有一项操作：**基于已有、已准入且已曝光的结构化交付，形成可复算的分轴可测性结论与可交给后续执行任务的评价预登记。**
- 本TASK不构建新模板、不运行评价矩阵、不确认迁移增益；后续实验需要独立、明确的执行合同与批准。

## 1. 事实基础、问题与目标

事实入口按当前效力读取：
[STATE](../../STATE.md) → [P7终止合同](TASK-016-P7-closeout-20261013.md) →
[P7终止审计](../reports/REPORT-016-P7-closeout-20261013.md) →
[P8治理裁定](../reports/REPORT-016-P8-H1-H5-governance-rulings.md)。
P8原报告的继续建议、旧stage快照与恢复许可不能覆盖后来的终止状态。

| 已确认事实 | 本TASK的处理 |
| --- | --- |
| P7为Partial/stopped；C-E02、SS-E02、C-E03为development_epoch_incomplete；更早epochs保持关闭 | 不恢复、不重开、不创建后继epoch |
| fresh targets/group均C0、SS0；新科学A/B/E为0 cell、迁移指标null | 继承事实，不把历史数据盘点计为新增fresh或科学结果 |
| 原TASK-016、P1、P6有来源限定工程、scope与旧回归成果 | 继承可用资产与证据，不整库重写或重复原文审查 |
| 存在错误身份、撤回结构、范围错配、闭包和曝光缺口 | 继承最终裁定；缺失记unknown，不猜补、不自动翻案 |
| 现有结构化资产能否形成有效的回顾性留组实验尚未盘点 | 本TASK回答这一问题；不预先宣称数据足够 |
| H5补充账接入/专利别名解析仍有缺口 | 登记对未来评价的阻断，不在本TASK修复G7 |

目标交付四项：逐对象输入处置与计数、化学范围可测性表、逐折build/test及资产排除计划、分层评价协议与下一步决策。
即使没有可行折，也必须给出文件/字段/对象级原因和明确停止建议；不得为形成正面方案反复补源。

## 2. 三层证据与pipeline映射

| 层次 | 数据及设计 | 允许结论 | 本TASK权限 |
| --- | --- | --- | --- |
| 回顾性开发评价 | 已曝光、已准入数据；按来源闭包留组；每折重建资产 | 方法开发、失败定位、受历史设计影响的开发效果 | 仅盘点与预登记，不运行 |
| 独立迁移确认 | 未用于设计、与build闭包隔离的数据；最终方法冻结后一次确认 | 有来源范围限定的新目标迁移证据 | 仅写未来准入条件，不发现/读取/消费新候选 |
| 正式benchmark | 独立标签、冻结协议及formal_run_ready | TASK-017范围内的正式比较 | 不启动、不放行 |

开发留组不能消除项目历史设计曝光，不能称为blind或fresh。更换agent、移除文件、换fold或换epoch均不能洗掉曝光。
通用模型的训练重叠仍为unknown；只允许声明已检查的领域库/build-test隔离。

**P9完成不等于P7完成或Roadmap P2 development effect通过。**
方法交付、评价执行、C能力增益、SS能力增益、独立确认、formal准入分别记录。
原C/SS双轴科学目标保持；若未来调整pipeline准入或主张范围，必须另行明确批准，不能由P9报告自动改写。

## 3. 范围、输入与保全

### 3.1 允许项（仅在本TASK获批执行后）

1. 读取已有TASK/REPORT/manifest/终止与曝光元数据，定位最终规范化反应交付。
2. 盘点已有、已准入、已明确化学曝光且没有持续内容停止限制的结构化反应；按既存签名、证据指针与裁定形成计数和分组。
3. 对已允许的机器结构做字段完整性及必要的parse/sanitize检查；不改变化学图，不补编码，不据此新增科学准入。已有runtime_complete与本次工程检查分字段记录。
4. 生成新目录中的盘点、留组计划、预登记与验证文件；确有需要可新增一个无网络、无runtime加载副作用的辅助脚本 `scripts/task016_p9_plan.py`。
5. 执行完毕后写同编号REPORT，更新STATE和索引中的P9状态。

### 3.2 输入定位与内容闸门

候选定位根仅限既有 `outputs/task016/v1/`、`outputs/task016-p1/v2/`、
`outputs/task016-p2/v2/`、`outputs/task016-p3/v1/`、
`outputs/task016-p4/v1/`、`outputs/task016-p5/v1/`、
`outputs/task016-p6/v1/`、`outputs/task016-p7/v1/` 与
`outputs/task016-p7/closeout-20261013/`，以及对应合同和报告。
根目录列名不授权整树读取；先用最终交付manifest定位具体文件，形成逐文件allowlist。

优先复用P1/P4/P6最终规范化反应表、来源分组和runtime完整性记录。
P7只引用现存最终设计/准入资产与终止/曝光信息；R80、未终结角色草稿、prospective候选不能成为补读队列。
每个结构化输入在内容读取前具备：
`path/sha256/bytes/producer_version/role/admission_pointer/exposure_pointer/access_policy`。
不能证明内容已准入并已曝光的，保持metadata-only或blocked_input。

混合含未读、未评估或受限内容的文件不得整文件加载来做“盘点”；没有安全的已有最小导出件时，记录输入阻断。
禁止打开PDF/SI/图片/原始数据库响应来补齐字段。Liu2021/R73及其他具名内容停止沿用；只消费其已公布状态元数据。
既有身份/结构否决不重新审判；只有“已曝光而非fresh”这一排除原因，不会自动取消其已有development资格，具体科学准入仍须有最终依据。

### 3.3 禁止项

- 新HTTP、检索、下载、外部API、原文或新候选科学读取、A4–A6重跑、R80恢复。
- 新scope、模板抽取/构建、支持重放、候选生成探针、模型推理、MCTS、训练/调参。
- 修改已有scope、模型、stock17、审核视图、运行配置、运行/epoch/曝光账或历史TASK/REPORT；不修G7/别名入口。
- 变更正式/供应/发布资格，生成human_reviewed，Git提交/推送。
- 写入历史 `/home/ljx/retro_synthesis` 或 `/home/ljx/CondRxnBench`，或依赖其可写缓存。

### 3.4 文件职责（未来执行计划，除本合同外未交付）

| 文件或目录 | 职责 |
| --- | --- |
| `outputs/task016-p9/v1/input_manifest.json` | 精确输入、访问闸门、SHA与版本；缺文件也登记 |
| `record_dispositions.jsonl` | 每条既存对象的来源、最终状态、去重、缺失与纳入/排除原因 |
| `measurability_by_stratum.json`、`measurability.md` | C/SS分范围计数、未知项与可测性 |
| `group_manifest.json`、`fold_plan.json` | 闭包边依据、逐折build/test IDs、隔离与支持门 |
| `asset_exclusion_plan.json` | 各折所有继承库、实例、scope支持的排除/重建要求 |
| `evaluation_preregistration.json`、`evaluation_protocol.md` | 两类比较、冻结分母、指标、失败处理和将来计算量 |
| `decision.json`、`verification.json`、`delivery_manifest.json` | 下一步/停止决策、复算与保护检查、交付SHA |
| 同编号REPORT、STATE与索引 | 事实、限制、状态与未执行事项；不预建虚假结果报告 |

## 4. 执行阶段与阶段门

### D0：冻结授权、输入和保护边界

- 验证新的P9执行批准、合同SHA与P7机器终止状态；旧approval不可借用。
- 保存实际脚本/配置指纹、逐文件输入allowlist、访问策略与限定保护SHA。包含P7终止入口、epoch/run/exposure账、永久曝光投影及相关旧scope/运行绑定。
- 对继承元数据逐对象处理最终裁定与supersession；不能按“旧表行数”或“最后修改时间”代替准入裁定。
- 任何无法安全读取的内容记录阻断，不追读。不存在的新文件不得以空表0行冒充。

D0通过仅放行D1–D4。它不释放P7科学锁。

### D1：按科学对象盘点，形成范围可测性表

按 `family + acceptor_core + formed_site/linkage + sugar_identity + donor_context + catalytic_mode`
分层，优先继承已有、证据明确的范围标签；标签有争议则单列unknown，不通过新化学推断解决。

每个范围至少报告：
- 原始记录/实验上下文数、去重精确反应数、不同产品target数、不同canonical acceptor数；
- 结构完整、完整reference、已有runtime-complete分别多少；本次机器检查与继承科学裁定分开；
- 已确认source/assay闭包组数、闭包未决对象数、已曝光对象数；
- 身份否决、结构撤回、deferred、输入受限、重复、范围标签未决的逐项计数和指针；
- 已有build支持及来源；留出一组后可保留的不同支持受体数。

同一产品的多条件/多来源/多reference不膨胀为多个target；合法多reference按冻结集合保留。
仅在有既存可靠规范化键时去重；键缺失列unknown，不默认为不同，也不手写结构补键。
O作为已有能力参照单列；不得以O的成功或数量抵消C/SS缺口。

### D2：形成按来源闭包留组的可执行规格

- 使用来源文章、真实source/assay/cohort关联及重复反应身份等既存有据闭包边；同一供体或同一酶名称不单独证明相同/独立实验队列。
- 未决边不能按独立组计数；对可能影响分割的未知关系标为阻断。
- 每折整体留出一个闭包组；明确build/test的record、target、source_group IDs及共同对象检查。
- 计划的scope只能从该折build支持构建。继承“至少两个不同canonical acceptor”等已适用的支持门；缺支持则标insufficient_build_support，不手写宽scope兜底。
- 为全部继承库列实例、模板、scope支持和参考信息的来源血缘；无法证明从build侧重建/排除评价闭包的资产标unverified_lineage。
- 冻结算法/支持选择规则在未来各折一致；不得按该折reference或模型结果人工调整scope。
- 输出每折 `data_feasibility_status`、阻断理由、排除映射和预计target数。尚未构建runtime，所以统一 `runtime_rebuild_verified=false`、`execution_authorized=false`；不能把数据可行写成已可运行。

可行折数为0也允许形成有效盘点结论，但必须指出是支持不足、闭包未决、结构缺失还是血缘不可验证。
本任务不把“回顾性留出组”写成“项目从未见过的新来源”。

### D3：冻结两类比较及评价分母

**比较一：当前系统的开发收益。**
A=generic；B=冻结P6 v6；E=拟最终增强版本。使用完整旧库时如实披露其评价来源暴露，只回答已知开发目标上的系统行为。

**比较二：按来源留组的开发迁移。**
A=固定generic；B_g=按该折build侧重建的既有方法；E_g=同build侧构建的增强方法。
方法/参数固定，各折生成独立资产SHA；B_g不能冒称原封不动的P6 v6。
如B_g无法可靠重建，明确该比较尚不可执行，不静默换基线。

两类比较分别预登记，禁止合并其结果或借用完整库成绩支持干净迁移。
generic训练来源未证实的重叠维持unknown。

分母与指标必须同时满足：
1. 主panel先按来源、结构完整性与事前领域条件冻结，不以E能否生成完整reference选样，不只选A/B失败对象。
2. 声明领域内没有被scope覆盖、正常运行但无命中的对象留在主分母；事后scope-applicable子集仅作条件性诊断。
3. 结构/身份不足对象可按事前质量规则排除，但保留逐对象原因与分母流转。
4. 正常执行无参照记观测0；未运行/错误/超时的科学结果记null。错误留在登记panel并单列，不能改写为化学失败。
5. 同时报登记目标总数、正常配对数、失败数与按登记总数计算的操作成功下界；该下界不冒称科学覆盖率。正常配对收益说明子集限制，不静默丢弃错误。
6. 按target及来源组汇总；seed0/1/2为重复运行，不扩增样本/独立组数。
7. 报generated/truncated/filtered/created各层完整reference、相对A/B增益与损失、非reference动作挤出、generic前三保护；新目标迁移必须排除exact build replay。
8. N_gap要求A/B正常且均无完整reference；N_gap=0时G/N_gap为null，不写100%。
9. 真实MCTS证据必须有完整reference action/node及逐cell trace；只有候选列表命中不算node transfer。
10. 预登记model/review/stock17/code/runtime/panel hashes、相同搜索预算与固定种子。未来每个target×3 seeds×3 arms为9 cells；两类矩阵分别核算，失败尝试计账，不为追成绩增加cell。

本TASK生成的所有效果字段统一null或not_executed。上述仅是未来执行规格。

### D4：验证、报告与单一下一步决定

- 同一冻结输入复算计数/分组/留组清单，排除生成时间字段后结果一致；限定保护SHA不变。
- C/SS按范围分别建议 `ready_for_development_execution_design`、`insufficient_data`、
`unresolved_closure_or_lineage` 或 `blocked_input`，附具体对象与最小缺失信息。
- 数据可行时提出一个有界后续开发执行合同规格：输入/折/资产边界、9×target cells计算、成功/失败与停止条件。不自动建立或执行后续任务。
- 不可行时直接交付缺口和停止决定；不默认转入补源、恢复reader或新epoch。
- 若将来考虑独立确认，另需具名干净来源/合法获取路径、每轴≥6 targets/≥2 groups可达性和隔离依据；metadata线索不足以预先宣称完成。
- 最终REPORT明确D0–D4完成程度及全部未执行事项，STATE只登记P9当前状态。

## 5. 独立科学要求与阶段状态不得混用

原P7的科学要求不因P9盘点或开发实验而减免。要声称原定双轴迁移增益，仍须分别证明：
- 合格独立面板≥6 targets/≥2 groups；
- G≥3、G/N_gap≥50%、成功迁移覆盖≥2 groups；
- 相对generic与有效旧方法基线净完整reference覆盖>0、reference loss=0；
- 至少3个不同target跨≥2 groups满足A/B三seed正常无完整参照节点、E三seed均实际创建完整参照节点；
- 最终runtime与旧能力保护通过，且无后验更换面板/规则。

P9提出的全领域主分母与条件子集报告，是新评价协议建议，**不追溯修改P7原有scope-applicable准入规则**。
独立确认最终采用何种面板和基线，须在其新合同中明确批准；不能把不同协议的数字直接算作P7通过。
≥6/≥2是项目开发验收门，并不自动提供广泛泛化或统计显著性的保证。

计划状态字段：
`planning_complete`、`development_evaluation_complete`、
`c_effect_pass`、`ss_effect_pass`、`independent_confirmation_complete`、
`pipeline_transition_authorized`。
P9至多令planning_complete=true；其余执行/确认状态保持false或not_executed，效果pass为null，pipeline_transition_authorized=false。
后续有效实验出现零/负增益可以结束该轮评价，但能力增益门不通过；无合格panel则是不可评价，不能记成零增益。
整体双轴科学目标未通过时继续Partial；不自动启动TASK-017/018。

## 6. 验收标准

- [x] AC01：新的执行授权、合同SHA、输入allowlist、访问闸门与限定保护基线具备；P7仍stopped。
- [x] AC02：每条已读取对象有处置和证据指针；输入不可得/未授权明确列出，没有猜补或重新审原文。
- [x] AC03：C/SS按化学范围给出四层计数、完整性、闭包与缺失；重复不抬高target/group数，unknown不默认为0或独立。
- [x] AC04：逐折build/test IDs、支持门、重复/闭包交叉检查与阻断理由完整；没有可行折时同样可核实。
- [x] AC05：全继承资产的来源血缘及排除/重建计划完整；不能证明者标未通过，不声称已执行runtime隔离。
- [x] AC06：两类比较、历史曝光与generic训练重叠边界清晰，完整v6成绩不冒充留组迁移。
- [x] AC07：主分母不依赖E参照命中或A/B失败；条件子集、错误、null、seed与group汇总规定明确。
- [x] AC08：全部未来效果字段为null/not_executed；没有新增fresh、scope或MCTS结果。
- [x] AC09：原独立科学门、P7终止与P2未验收保持；没有pipeline/formal自动放行。
- [x] AC10：同输入复算一致；限定保护资产无漂移；输入与输出manifest、操作账及预算守恒。
- [x] AC11：报告按轴/范围给出一个明确下一步或停止决定，不生成新的恢复循环。
- [x] AC12：同编号REPORT与STATE/索引一致；清楚区分P9规划完成与科学效果未完成。

P9 Completed只表示上述规划交付全部通过。数据不足但缺口可核实、计划和停止决定完整时可以完成本TASK；
关键输入/裁定无法核对导致规划交付不可靠时记Partial或Blocked并报告，不能靠unknown堆积宣称验收。
本合同已获批准执行；验收结果在最终REPORT逐项登记，合同检查项不冒充已通过。

## 7. 预算、验证与停止

未来批准执行后的独立预算：
- 最多40个经operate记录的本地命令；仅一轮主盘点与一次同输入复算。
- 结构化输入≤120文件、内容读取总量≤200MiB；不扫描全项目原件或重建全局曝光库。
- 最多新增一个盘点辅助脚本；不修改runtime。只有新增解析/分组逻辑存在实质风险时才添加针对性合成验证，不重跑整套科学/安装回归。
- 新HTTP/下载/原文读取/模板构建/模型推理/MCTS/新epoch/Git同步预算全部0。
- 发现错误保留错误版与原因；不得借修错扩大输入、重释旧准入或增加科学动作。

验证使用本任务实际辅助脚本（若确需编写）与直接元数据复算；具体CLI在实现时登记，不能把计划命令写成已运行。
本次合同起草只验证文档链接、状态边界、限定差异与保护SHA，不运行数据盘点或测试矩阵。

立即停止相关处理并保留报告的条件：
1. 需要新科学读取、恢复R80、解除内容锁、修G7或重新化学编码才能继续。
2. 输入包含未读/未准入内容，访问隔离无法保证，或最终裁定冲突无法从现存记录解决。
3. 闭包/资产血缘未知却必须假定独立才能形成折；停止该折，不猜造边。
4. 出现无解释保护SHA漂移、合同/批准绑定错误、并行写入或不可复算差异。
5. 达到命令/输入/字节预算；不自动加额、循环查询或换epoch。
6. 需要改pipeline完成规则、原科学标准、库存、模型或正式准入；仅提出新动议。

## 8. 必须提交的报告与修订记录

获批执行后，无论完成、部分完成或停止，都提交
`docs/reports/REPORT-016-P9-development-evaluation-redesign.md`，登记REPORT索引并更新STATE。
报告必须给出输入范围/排除、逐范围可测性、留组和资产排除、两类预登记、剩余偏差、未执行项、预算/错误与下一步决定。
受限反应明细、结构化本地载荷及原件不入Git；文档只保留必要计数/路径/哈希与证据边界。

方法参考（仅通用技术文档，不是化学证据）：
[分组交叉验证](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data)；
[避免测试数据参与方法选择](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。
这些方法不能逆转已发生的设计曝光。

2026-10-13 v0.1：依所有者指示建立具体TASK，范围限于现有数据可测性盘点和开发评价预登记；
状态Proposed，仅合同编制和索引登记已授权。P7终止、原科学门和后续执行批准边界保持。

2026-10-13 执行登记：所有者“批准执行”；按agent_delegated冻结原v0.1合同SHA与独立批准，进入D0–D4。原范围/预算/停止条件不变。

2026-10-13 执行收口：D0–D4与AC01–AC12规划验收完成，详见[REPORT](../reports/REPORT-016-P9-development-evaluation-redesign.md)。34输入、96去重上下文，C13/SS19不同编码target；已证实同范围支持充足折C0/SS0，停止本库存留组执行。唯一一次同输入复算9产物一致；没有新增科学执行。P7仍Partial/stopped、P2未验收。后续描述性评价规格未自动立项或执行。
