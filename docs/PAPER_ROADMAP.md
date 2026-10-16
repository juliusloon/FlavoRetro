# 论文路线（PAPER ROADMAP）

当前系统状态：`metadata/release.json` 标记为 `research_candidate`，六个外部验证维度全部 unresolved / not_executed / not_performed。本路线把"最终论文"拆成可执行阶段；**任何阶段都不得用工程测试冒充化学验证**。下一阶段的任务主线与优先级见下文「下一阶段主线」一节。

## 科研评价与供应/发布证据分工（2026-10-13 v0.2）

所有者明确批准TASK-017准入修订，见[ADR-007](adr/ADR-007-research-evaluation-admission.md)。科研评价与供应/production/发布分别验收；不存在必须先认证供应才能开始方法实验的统一前置。

| 证据或资格 | 当前事实 | 责任与关闭条件 |
| --- | --- | --- |
| 方法/工程资产 | TASK-016已交付候选研究方法，production为0 | 科研评价绑定实际代码/模型/模板支持血缘/审核/库存SHA；不要求全库先晋级production |
| 评价准备 | v0.2合同已批准；preparation检查尚未实现/运行 | 执行授权、冻结方法、合法有限来源路线、角色隔离/交接和累计预算；允许panel/gold仍待产出 |
| 独立标签与参考 | 全局not_available；TASK-017未产出独立panel | 在TASK-017准备阶段落实真实审核角色，逐项核验完整实验结构/参考与一手出处、来源/曝光隔离；C/SS各至少6目标/2组 |
| 正式科研评价 | not_executed；research_run_ready=null（未实现/未核验） | 局部协议及panel冻结，全部真实科研检查通过后一次矩阵；完成与正增益分开 |
| 全库来源/production资格 | primary_source_review=unresolved；production template/stock=0/0 | 继续逐条真实审核/晋级或否决；不由科研评价自动认证 |
| 当前供应商证据 | current_vendor_evidence=unresolved | 继续真实可日期供应/价格核查，约束采购、可执行性与供应主张；不是方法迁移评价前置 |
| 结构诊断真值 | topology只有开发自检 | 独立标注子集支撑precision/recall主张，不由搜索reference覆盖替代 |
| 发布就绪 | release_ready=false | 保持原治理范围；实验完成不自动发布或认证 |

旧evaluation.preflight及formal_run_ready语义/CLI/API保持，v0.1真实false完整保留。TASK-017 v0.2拟以任务范围research_run_ready放行科研矩阵，必须验证真实来源、独立标签、闭包、协议、资产与预算；不是把旧字段改成true。科研检查/执行器当前待实现，合同修订不代表放行。原“先补齐来源/供应/标签前三行，formal执行器才允许动工”的统一阻断由本次责任分工取代；供应/production证据本身不删除。

## 下一阶段主线：从"工程正确"到"科学可评价"（TASK-014—018）

本节由所有者于 2026-09-26 提出并指示写入本路线，用于确定后续 TASK 的思路、范围与先后顺序。它是**方向性计划，不是已批准的 TASK 合同**：每一阶段动工前仍须按[tasks/README.md](tasks/README.md)记录明确批准；历史P2/P5人工批准要求在本次TASK-016-P1中由所有者明确高自主授权覆盖，记录agent_delegated，其他任务不得推定已批准。

### 现状判断

项目已不缺水工程骨架，缺的是把现有工程能力转化为**可验证的科研贡献**。已具备：独立 Python 环境、v3 资源与 SQLite 只读索引、真实实时 MCTS、CLI/API/Web、CI、仓库外安装与较完整的浏览器工程验收。但 `metadata/release.json` 仍是 `research_candidate`，一手来源审核、当前供应商证据、独立化学标签、正式 benchmark 四项均未闭环。

因此后续瓶颈不是"再加页面或 API"，而是**独立 gold set 与冻结评测协议**。在它到位之前，现有 12-cell 开发比较只能说明工程行为，不能支撑算法优越性。

### 后续发展空间（按价值排序）

**D1 最高优先级——从"工程正确"升级到"科学可评价"。** 瓶颈不在功能数量，而在缺少独立 gold set：需要人工核对一批黄酮/黄酮苷反应（底物身份、断键位置、反应类别、原料可获得性），并冻结标签规范，之后才能执行真正的盲测。目前正式 benchmark 仍为 `not_executed`、独立化学标签 `not_available`，所以 12-cell 开发比较只说明工程行为，不能支撑算法优越性。

**D2 最有项目特色——P2 糖苷感知搜索。** 糖苷拓扑能力已相当扎实（识别候选糖苷连接、Web 高亮、关联文献），但它完全独立于 MCTS 的 expansion 与 scoring：系统"看得懂某些糖苷结构"，却不会用这种知识改变搜索决策。有研究价值的下一步，是把**经过验证**的糖苷信息转成受控的 action prior、candidate reranking、branch filtering 或 route scoring，再与普通 MCTS 在冻结协议下对照。该方向已列为工作台路线 P2，但须先冻结定义与评测协议。

**D3 明显能力缺口——反应家族识别。** 当前 47,836 个模型模板全部为 `0.0 Unrecognized`；工作台已有 27 个教学条目，但搜索产生的模板不能可靠落入这些类别（TASK-010 已指出旧教学层的命名家族与当前 USPTO/ringbreaker 数值 classification 不匹配）。可发展为独立的"反应语义层"：模板 → 结构变换 → reaction family，每条映射带来源、置信等级与人工复核状态。做扎实后，它既是界面改进，也是 P2 搜索约束与结果解释的基础。

**D4 搜索算法优化——排在科学评测体系之后。** PUCT、动作融合、去重、替代动作、转置与预算合同已经存在（TASK-012 修复了同次扩展重复状态与多产物 outcome index 两个真实缺陷），但 native 与 optimized 仍无严格等价的节点预算，早期搜索参数仍是 provisional、未经系统调优。后续可做预算归一基准（budget-normalized benchmark）、参数消融、PUCT 权重研究、template-policy 融合实验与不同转置策略比较，很可能成为论文的算法实验章节——但前提仍是先有可信评测集。

**D5 证据层——从"可追溯"到"可审核"。** v3 已解决工程追溯（3,059 条记录、123 个来源、SQLite 查询；508 条文献记录中 249 条命中原文 token、259 条只定位文件），但"文件定位/token 命中"不等于内容审核。值得增加审核工作流，如 `unreviewed → source_located → primary_checked → structure_checked → reaction_checked`，记录审核人、证据片段、日期与冲突，使项目从 evidence-aware 走向 evidence-auditable。

**D6 工作台——从研究展示工具升级为研究决策工具。** 四页入口、历史运行、资源 QC、教学、拓扑与 12-cell 开发比较均已存在，TASK-013 又把移动端、键盘操作、对比度与无障碍做到较完整。下一层不应只是继续美化，而应增加路线横向比较、候选步骤人工接受/拒绝、证据差异视图、route annotation、实验备注与可复现"研究会话"等真正辅助决策的交互。注意当前浏览器验收都是工程验收，没有真人可用性结论。

**D7 产品化与平台化——当前基本未展开。** HTTP 服务本质仍是本机开发服务器，同一服务进程门控，没有分布式调度、公开部署、任务恢复与真人使用测试；平台只验证过 Linux x86_64 / Python 3.10。若未来要支持实验室多人使用，可再做持久 job queue、任务恢复、权限与 workspace 隔离、共享运行库、服务器部署与 macOS/Windows 支持。这些工作对当前科研价值的边际收益低于独立标签与正式 benchmark。

以上 D1—D7 是本路线的价值排序编号。D2、D3 提到的"P2/P3"指 [WORKBENCH_ROADMAP.md](WORKBENCH_ROADMAP.md) 的工作台阶段编号，与本文件「阶段计划」的 P0—P3 不是同一套编号，引用时须注明。

### 主线任务序列（TASK-014—018）

按"最可能把 FlavoRetro 推向论文级成果"的顺序：

| TASK | 主题 | 对应方向 | 前置 | 批准要求 |
|---|---|---|---|---|
| [TASK-014](tasks/TASK-014-domain-triage.md) | 领域反应筛选与科学评测协议（含本地试点） | D1、D5 | 已完成规范和本地试点 | 已获 human_direct 批准；Completed |
| [TASK-015](tasks/TASK-015-ord-coverage-review-cards.md) | 已完成 ORD、53 条结构/分类开发 gold 与证据最终裁决；独立盲测另行准备 | D1 | TASK-014 标签规范与 gold-v1 已冻结；P5 来源/产率按证据子集定案 | 已有人审与代理委托 gold 授权；P5 最终裁决获采纳，保留审核溯源 |
| [TASK-015-06](tasks/TASK-015-06-review-into-search.md) | 已完成审核结果搜索接管：冻结视图、库存准入与逐步/末端/运行追溯 | D1、D2 | P3/P4/P5稳定成果与严格关联已实际接管；不是新生成覆盖或独立化学认证 | 2026-10-05 agent_delegated，Completed；D1–D4所有者确认 |
| [TASK-016](tasks/TASK-016-open-glycoside-expansion.md) | 开放数据驱动的成键模板、受控独立搜索策略与有限开发验证 | D2 | 继承已交付来源/模板/MCTS及审核/17库存 | **Completed（方法与有限开发阶段，2026-10-13所有者确认结项）**；原v0.2与P1成果保留，C/SS正式独立迁移由TASK-017承担 |
| [TASK-016-P1](tasks/TASK-016-P1-open-glycoside-library-expansion.md) | 批量扩充真实成键反应/模板与作用范围，验证新实例覆盖 | D2 | 复用首版地基，规模/范围/留出增益共同验收；保持审核/17库存 | 2026-10-06 Completed；54新反应/47新模板、5范围、7/12开发补回；正式评测另行准入 |
| [TASK-016-P2](tasks/TASK-016-P2-c-sugar-transfer-validation.md) | 补C与糖间新精确目标迁移 | D2 | 两类各6新目标/2出处、双基线至少3且50%补回/三seed；旧4SS仅校准 | 2026-10-06 Partial；工程新1C/2糖间范围、旧4SS修复；新面板不足，新A/B/D未执行，科学门保持 |
| [TASK-016-P7](tasks/TASK-016-P7-domain-aligned-transfer-closure.md) | 历史C/SS双轴开发迁移尝试及其终止记录 | D2 | 原scope-first/fresh合同与永久曝光保留 | **Partial/stopped（2026-10-13）**；fresh C0/SS0、科学0 cell、metrics=null；[终止审计](reports/REPORT-016-P7-closeout-20261013.md)。原科学门未通过，不再阻挡TASK-016方法阶段结项 |
| [TASK-016-P9](tasks/TASK-016-P9-development-evaluation-redesign.md) | 现有数据可测性、留组缺口与评价预登记 | D1、D2 | 既有已准入/已曝光资产；P7终止保持 | **Completed（规划交付）**；C13/SS19历史编码目标，同范围支持充足折0/0；[报告](reports/REPORT-016-P9-development-evaluation-redesign.md)。未产生新效果，后续正式验证归TASK-017 |
| [TASK-017](tasks/TASK-017-independent-c-ss-transfer-benchmark.md) | 冻结独立面板并开展C/SS科研迁移检验 | D1、D4 | ADR-007准备/科研分层；真实独立标签/来源闭包及冻结方法协议 | **Partial / awaiting_independent_review_input**；v0.2准备true/科研false，48书目候选与ljx审核包；科学0 cell。[执行报告](reports/REPORT-017-v0.2-execution.md) |
| TASK-018 | 消融、误差分析与论文结果整理 | D4、D6 | TASK-017 的冻结运行 | 所有者人工批准 |

2026-10-13 当前阶段分工（所有者本会话明确同意）：TASK-016按已交付方法和有限开发效果结项；C/SS正式独立迁移检验由[TASK-017](tasks/TASK-017-independent-c-ss-transfer-benchmark.md)承担。P7的Partial/stopped与原科学门保持；原“P7作为P2终验”不再是方法阶段结项前置。见[ADR-006](adr/ADR-006-method-delivery-and-independent-evaluation.md)。合同起草决定保留；TASK-017本轮执行已批准但G0停止，正式运行未放行。 现按[ADR-007](adr/ADR-007-research-evaluation-admission.md)登记v0.2准入责任变化；本句前述G0停止为v0.1历史，未将新版科研门判true。

2026-09-29 范围明确：[TASK-016](tasks/TASK-016-open-glycoside-expansion.md) 以公开 API/官方批量下载自主获取反应为前置，化学合成与酶催化均可纳入；从具体实例构建受限模板并检查基础模型缺口，再以独立策略接入 MCTS。首版不以调分代替候选生成，不依赖人工检索，不接管 TASK-015 修补；仅做开发对照，正式盲测与生产晋级另行治理。本合同的新批准取代本路线较早关于 TASK-016 尚未授权的描述，其他阶段未自动获批。

### 并行线、论证链与启动前收口

- **并行低风险线**：反应家族映射（D3，工作台路线 P3）可在 TASK-014/015 期间作为低风险工程线推进，先建规范与来源；仍不得把教学材料冒充"已识别家族"。
- **论证链**：结构领域知识 → 可审计标签 → 搜索方法 → 冻结评测 → 可复现实验 → 限域科学结论。下一阶段的主线因此不再是"多做功能"，而是形成完整论证链。
- **启动前先收口**：TASK-013 已完成并通过验收，但合同未授权提交/推送，UI 改动仍待所有者决定是否入库；在开工上述主线前，先收敛工作区状态更稳妥。

## 阶段计划

- **P0 证据整理（无新实验）**：来源定位已由 TASK-012 获批恢复并切换 v3（249 条 token 命中、259 条文件定位但 token 未命中）；剩余 token/原文内容审核仍需科学任务；产率字段覆盖率统计；2 组/4 ID 名称冲突已由 TASK-015-P5 裁决。产出：数据审核附录素材。
- **P1 人工审核与标注**：template/stock 逐条人工审核（多名审核人 + 分歧记录）；糖苷连接诊断标注 50—100 分子子集。产出：`production_eligible` 首批记录、诊断真值表。
- **P2 预注册正式评测**：定义目标 panel、对照基线、指标（闭合率需 evidence 定义、成本分布、多样性）；冻结合同后跑正式盲测（开发对照的 12 cell 规模远不够）。产出：`outputs/evaluation/formal-*` 与统计报告。
- **P3 论文产物**：图表全部从 `outputs/` 已存运行重绘（禁止手改数值）；附录含 sources 清单、哈希、运行 ID；代码打版本标签并公开仓库。

与下一阶段主线的对应：P0/P1 → TASK-014、TASK-015；P2 → TASK-017；P3 → TASK-018；工作台路线 P2（糖苷感知搜索）→ TASK-016。

## 可直接复用的工程素材（论文方法部分）

- 每次搜索独立进程、独立 run ID、结果哈希入 manifest（可追溯性）。
- 原生/优化树同资产、同时间/迭代预算的开发对照运行器（节点上限不等价）（`flavoretro/evaluation.py`）。
- 证据分级输出（partial / surrogate / evidence_closed，默认全 false）。
- 资源准入：逐记录 SHA-256、解析失败保留、零收率≠缺失。
- 结构诊断：立体化学感知的图往返回归测试（`tests/test_topology.py`）。

## GitHub 发布检查清单（所有者执行）

- [x] 选择代码许可证（已确定：代码 Apache-2.0、项目原创文档 CC BY 4.0，同 CondRxnBench，2026-09-21）
- [ ] 确认仓库无受限数据：`data/`、`outputs/` 在 .gitignore；`metadata/` 只含哈希与清单
- [ ] 替换 repo-local git 身份为所有者 GitHub 身份
- [ ] README 补充仓库地址与引用方式（建议届时加 CITATION.cff）
- [ ] 环境可复现声明：pyproject 固定版本 + pip-freeze + 模型资产获取说明
- [ ] 打版本标签（如 v0.1.0-research-candidate）

TASK-012 只同步现有私有仓库并保留已有 repo-local Git 身份，不替代本页的公开发表身份、引用、许可或科学检查清单。Linux/Python 3.10 独立安装已验证，锁清单改用 environment/requirements-linux-py310.lock；其他平台、标签和公开发布仍需单独批准。

## 2026-09-27 TASK-014 收口

TASK-014 已按所有者本会话批准完成“先建立黄酮总分类、糖苷为重点审核子集”：领域/guide/标注与评测规范见 [protocols/](protocols/README.md)，实际结果见 [REPORT-014](reports/REPORT-014-domain-triage.md)。508 条笔记 guide 和 2,301 条本地导出全部保留；60 条开发审核样本包含 30 条糖苷重点。所有输入均 development_exposed，不能直接作为未见盲测。

TASK-015 后续需建立独立审核的开发 gold，并明确独立保留来源；外部 ORD 子集接入另立有来源/许可/训练重叠检查的任务。TASK-017 除 gold 外仍依赖一手来源、供应证据及已审核 template/stock 投影；本次协议完成不使 preflight 自动通过。TASK-015—018 未自动授权，原序列保持。

## 2026-09-27 TASK-015 收口

所有者授权的实际合同为 ORD 覆盖与卡片准备，53 当前镜像源和 60 卡已完成，见 REPORT-015 与 protocols/ORD_COVERAGE_V1.md。既有路线的人工 gold 目标仍未达成：应先初筛 30 糖苷重点、补 4 条定向来源材料，并用新来源/标签接管合同明确审核者和分歧处理。这个工程 TASK 完成不满足 TASK-016/017 的化学前提；上游 train/test 数据不成为本项目盲测。

## 2026-10-05 TASK-015 最终裁决

TASK-015-P3 已有真实所有者回传与明确 gold 冻结决定；TASK-015-P5 现按所有者“直接将你的结论作为最终结论，不要再让我审核”完成，无重复人工审核待办。此前“人工 gold 未达成/等待独立审核”的表述仅为当时历史记录，当前为 53 条结构/分类 development gold、7 排除，来源正面子集 9 条、明确原文数值产率子集 6 条。所有对象的未知/冲突/不可得均已定案标记，不把缺证据当作正面认证。

详见 [REPORT-015-P5](reports/REPORT-015-P5-p0p1-evidence-closure.md)。P5最终覆盖层已由TASK-015-06外置审核视图接入搜索资源；当前供应证据和独立盲测仍不足；正式 benchmark 门不变。TASK-016 继续按已批准合同推进，无需再次审核本批卡片。

2026-10-05：[TASK-015-06](tasks/TASK-015-06-review-into-search.md) 已Completed，审核结果进入普通搜索资源和证据查询。后续TASK-016的G4–G5绑定task015-06-v1及manifest/index哈希，固定17候选库存基线；本轮未启动TASK-016。8次开发对照稳定字段一致、来源实际命中0；当前精确供应/独立盲测门仍未关闭。

2026-10-06：TASK-016 v0.2 已按所有者明确同意修订；成键候选为主指标，支持步骤另表，A/B 均读取同一 adjudicated 审核与 17 库存。定义冻结 N/N_gap/M、前体匹配、模板实例重现、动作追溯、补回/损失/未知/失败和运行成本；是否覆盖提升由真实 G 与净变化判断，不由模板或数据行数判断。G1—G5 尚未执行。

2026-10-06 执行结项：[REPORT-016](reports/REPORT-016-open-glycoside-expansion.md) 完成公开采集到真实MCTS的G1—G5。4个产物实例来自2论文/3实验上下文，只有O成键1家族、3位点类；过滤后0/4→4/4，seed0/1/2各4/4实际补回，来源精确结构/离子态范围之外没有泛化证据。固定预算过滤后另减少8个非参照候选；31实际MCTS、105本地测试、重放/安装/来源审计通过。全部development_exposed，C/糖间成键和HTE准入仍为0、训练重叠unknown，不构成盲测benchmark或化学准确率，formal/release门不变。

2026-10-06 扩库补充完成：[TASK-016-P1](tasks/TASK-016-P1-open-glycoside-library-expansion.md)/[REPORT-016-P1](reports/REPORT-016-P1-open-glycoside-library-expansion.md)完成约定规模/范围/开发增益；新增54反应、47模板，5多受体范围，12目标补回7且三seed创建。撤回12身份不充分上下文、保留所有失败，预算自主批准修订180→240、最终216次。该开发证据达到本任务门槛；增益全部来自UGT71AP2一个出处，C/糖间迁移及训练独立性不足，不能作为正式论文泛化结论。下一步TASK-017设计与准入核查须明确独立标签/训练重叠及正式来源/模板/库存/evidence口径，development_holdout不晋升为blind/gold，不自动执行TASK-017/018或认证供应/production。

2026-10-06 当前方向：[TASK-016-P2](tasks/TASK-016-P2-c-sugar-transfer-validation.md)已按所有者批准执行，本轮[REPORT](reports/REPORT-016-P2-c-sugar-transfer-validation.md)为Partial。工程交付默认关闭v3、3新范围与旧4SS修复；新增准入0，两类6新目标/2闭包出处门未满足，双基线新增益/三seed新迁移未评估。工程40检查/124测试通过不构成独立化学或正式评测证据。继续补完整来源身份/闭包与新面板；TASK-017可进行设计/准入核查，本轮不执行正式blind。TASK-016/P1 Completed保持，TASK-017/018仍各自准入与批准。

2026-10-13 终止裁定：[TASK-016-P7](tasks/TASK-016-P7-domain-aligned-transfer-closure.md) **Partial，执行终止，科学验收未完成**；C-E02/SS-E02/C-E03已按原§3.3/§18.1正式development_epoch_incomplete，C-E01/SS-E01维持关闭。[终止审计](reports/REPORT-016-P7-closeout-20261013.md)。fresh C0/SS0、科学A/B/E0 cell、metrics=null；P2 development effect未验收，原科学门不变。已有O/P1/P6工程成果与曝光保留，不恢复R80、不以G7修复作为退出前置；本轮不建新epoch。后续研究须另行批准并先证明干净评价来源的可达性与隔离方案；TASK-017正式盲测未执行。

2026-10-13 阶段职责修订：依所有者“我同意，写 Task 17”登记上述当前分工。此前P7终止裁定中的“P2 development effect未验收”保留为原严格C/SS目标的历史事实；当前TASK-016方法及有限开发阶段已结项，未解决的正式迁移验证由TASK-017新合同承担。未改旧TASK/REPORT、epochs、曝光或scientific metrics，release/formal门不变。

2026-10-13 TASK-017 v0.2准入修订：所有者指示“修订。”。准备评价不要求已完成panel/gold；科研矩阵须真实来源参考、独立标签、来源/曝光闭包、冻结协议/方法和科研准入通过。供应及production保留为相应资格门，不能阻止候选方法测量。历史段落的统一formal门按当时合同解释，当前以本分工为准；原G0及P7记录不回写，runtime/release未改。本轮只有合同修订，无科学运行。
