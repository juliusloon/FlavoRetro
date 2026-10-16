# TASK-016-P2：C成键与糖间成键迁移验证

## 合同元数据

- 任务 ID：TASK-016-P2；作为TASK-016的第二个补充合同，保留已完成的TASK-016与TASK-016-P1历史。
- 状态：**Partial（2026-10-06；工程Completed，C迁移/糖间迁移Partial；合格新面板不足，未执行新A/B/D）**。
- 合同版本：v0.1。
- 基线分支/HEAD：main / 993b22f5e8eed5797d27f02c566af1b86a4b7880。工作区已有未提交实现，实际SHA基线优先于HEAD。
- 负责人：项目所有者；执行者：Cano。
- 方向/起草授权：human_direct；所有者“我觉得你说的有道理, 请开始写 TASK-016”，承接“进一步扩充C/糖间迁移验证”的讨论。本条明确授权合同起草；未把“开始写”记录成采集、模板修改或MCTS执行批准。
- 执行批准：2026-10-06，human_direct；所有者“批准, 开始执行”，批准本合同G1—G5及固定预算。Cano按既有高自主权限推进阶段与范围内修订；代理决定记录agent_delegated，来源审核不标human_reviewed。实际基线见outputs/task016-p2/v1/execution-baseline.json。
- 起草基线：operations/task016-p2-draft-baseline.json；起草校验：outputs/validation/task016-p2-draft.json。
- 修改预算：有界公开来源盘点/解析、C与糖间范围模板、隔离的显式v3、开发分组与真实动作比较、回归/审计及治理文档。实现阶段只做满足本合同所需的最小变更。
- 后续关系：优先于TASK-017正式运行；本任务不自动批准TASK-017/018，不生成正式blind/gold或供应/production证据。

## 目标与完成含义

将现有C成键、糖间成键从精确实例或单一糖型支持，推进到**来源约束的范围模板和新精确目标迁移证据**。两类分别达到来源分组、候选增益、真实MCTS及边界门槛；O糖基化成绩不能抵偿任一类短缺。

所验证的是完整单步前体候选是否被生成、过滤保留并实际创建节点。来源实例/NMR/作者结构判定、机器编码、模板适用、未知新酶活、预测条件、收率和路线闭合分别登记。新增模板/接口可访问/旧失败目标命中本身不足以完成本任务。

下文6/2/3/50%为所有者已批准的硬验收线。G1先核实可得性，再冻结可执行输入与面板；不能依据来源不足或模型成绩降低这些指标。任一类未达标，总体Partial，保留已完成的另一类成果。

## 继承事实与缺口

[REPORT-016-P1](../reports/REPORT-016-P1-open-glycoside-library-expansion.md)交付54新反应（O33/C5/糖间16）、47新模板（总51，5范围），冻结12目标补回7且三seed实际创建；全部增益来自UGT71AP2一个出处。118本地测试、51验收检查、23文件重放通过。P1预算已批准180→240，保守216（206实际尝试）；全部旧失败、10合成fixture和历史上限保留。本任务新账本独立，不挪用P1剩余预算。

起草前只读缺口审计outputs/planning/task016-p2-transfer-gap-audit.json确认：

| 类别 | 当前真实支持 | 尚缺证据/原因 |
| --- | --- | --- |
| C成键 | 5精确实例模板，来自AbCGT/FcCGT的phloretin及mono-C糖苷受体 | scope_template=0、C holdout=0；没有新精确目标迁移验证 |
| 糖间成键 | 12个apiose精确模板+1个apiose→β-D-glucosyl O2范围模板 | 上轮4留出目标需glucose或xylose；12次C臂真实搜索全树domain generated_actions=0，未生成对应候选 |
| O成键 | 7/12总体留出增益全部来自O糖基化 | 保留作为回归；不计本任务C/糖间迁移增益 |

四个旧糖间案例：kaempferol 3-O-glucosyl-(1→2)-galactoside、kaempferol 3-O-glucosyl-(1→2)-glucoside、epimedin B、sagittatoside B。它们已经被查看、编码、运行；本任务只能作为build/calibration或regression，不能改名计入新留出。

### 冻结继承绑定

| 输入 | SHA-256 |
| --- | --- |
| delivery_manifest.json | 3555a738436c9a93707fc894613abaf01496313e75344adcf32d2ccbd3ad907f |
| template_source_manifest.json | a98651a5b02873d3df36f46c8a4773867d354859039a5cc84b6f1669f685a2b2 |
| development_split_manifest.json | 9e6e61a4417a01e593c1f8693277bc6e2e9cf60f147c1f23a7186eaf3a667249 |
| instances.jsonl | 0982dc1f160efc9ecd556d07160461d2610b7138e4117ab82ba30daf970263bd |
| templates.jsonl | f6da1ddd0a4934e03e9d2347db0fa55728d0c6781dd00b087d9aec378e6f64fb |
| metrics.json | a7ebdfaec3916db47563c40feaaf908bd01c3c27621c5e268e5555daf27a1210 |
| audit.json | 062f172346f3f5f01340e6712616fa83a6feb63998af217d7c6fdd8dfaecac70 |
| task015-06审核manifest | 1e8ea3c461ac3ff88ee4d6bad3385aa832881d65bb682ff7467d64014c15f8ec |
| task015-06审核index | 55f15016571500b00dcd86b9bbf8484c23c0527c33afaa4e6b89d572e86ae06c |

上表P1交付文件位于outputs/task016-p1/v2；审核manifest/index位于outputs/review/task015-06/v1。执行前核原件、全部旧TASK/REPORT/载荷/账本、旧v1/v2配置、审核/17库存、模型和活动资源SHA。P1 delivery中的STATE/共享导航是交付时快照，可在本任务治理层继续更新；不回写旧delivery消除差异，旧代码/来源/运行证据保留其版本身份。

## 范围与非目标

### 允许项

- 优先复用已取得且许可合规的不可变原件，通过公开API/作者官方下载补足C与糖间来源；按实际证据选择化学或酶催化，不设强制配额，无所有者人工检索前置。
- 修正来源发现规则的漏检：先去HTML标签，再识别C-glycosyl/C-glucosyl/C-rhamnosyl、glucosyl/galactosyl/xylosyl/rhamnosyl/apiosyl及糖链延长/连接位点同义词；完整候选与筛除理由保留。
- 新版本批量身份准入、反应中心/单步方向验证、去重、来源闭包分组、边界/表示/实际动作重放；新增有多受体支持的C及糖间范围模板。
- 新增显式glycoside_library_version=v3及包内配置副本，build-only载荷独立；共享模块仅为该版本必要适配而改动，须证明旧行为不退化。
- 固定A/B/D开发比较、独立账本、旧案例回归、字节重建、包外安装、来源/指标/成本审计及中文REPORT/STATE/路线更新。

### 禁止项与非目标

- 不改旧TASK/REPORT、原件、P1冻结分组/观测/载荷或旧v1/v2配置/指针；不得把待确认12上下文静默重新准入。
- 不重训模型，不改通用filter/KnownHazards、PUCT/路线评分、库存49编码/17准入键、审核裁决、active/v3资源或release；不以扩库存提高闭合成绩。
- 不用新留出结构/位点/供体建立白名单、抽取/扩宽模板、调prior或筛选成功面板；不将同反应异构编码/离子态/重复条件变成新迁移样本。
- 不把多步最终产物、图回放、酶名称/同源性推断或数据库身份替代实际单步实验；不认证新反应酶活、产率、供应、化学正确性或独立gold。
- 不写历史/home/ljx/retro_synthesis及/home/ljx/CondRxnBench，不加入原始/受限数据到Git；不提交/推送、部署/发布或正式评测。

### 目录职责与计划产物

| 目录/入口 | 用途与拟改动 |
| --- | --- |
| data/raw/task016-p2/ | 新合法原件与失败响应，不可变/本地不入Git；已有原件以路径/SHA复用 |
| outputs/task016-p2/v1/、v2/ | v1来源过程/批准/独立账本及撤回初版；v2合格build-only载荷/当前工程与Partial审计，实质修订保留旧版本 |
| flavoretro/open_glycoside_library.py、glycoside_library.py及必要新模块 | C/糖间单步、糖型/位点/母核/上下文范围守卫；复用现有表示/映射/E-Z保全 |
| contracts/cli/worker/service/workspace及必要ledger适配 | 显式v3入口、父子SHA绑定、独立固定预算；默认及旧请求形状保持 |
| configs/glycoside-library-v3.json及包内副本（计划） | default_enabled=false；指向新任务build-only manifest，不覆盖v2 |
| scripts/task016_p2_*.py、tests/必要合同测试（计划） | 有界来源/构建/冻结/评估/重放/验证；118原回归保持 |
| docs/tasks/reports、STATE/ARCHITECTURE/导航/路线 | 本合同、执行REPORT及当前状态；如实保留Partial/失败/预算修订 |

当前合格载荷为outputs/task016-p2/v2，策略v3是运行版本；v1的87条初版编码包含后来撤回的两条C8记录，不作当前准入。预算与来源原始账本仍固定v1。

## G1：开放来源可得性与质量盘点

1. 冻结执行基线、查询合同、来源范围/许可、预算与阶段门。先核已取得全文/SI/元数据，继承P1失败响应及未知状态，避免同版本重复下载。
2. C方向优先寻找有完整结构支持的实际C键形成单步，区分直接芳基C糖基化、2-hydroxyflavanone等中间体成键与后续脱水。最终C-flavone不能直接代替未被鉴定的糖基化中间体；中间体共价/立体未知则保留候选、不准入可执行反应。
3. 糖间方向优先补glucose/xylose供体对应受体糖与连接中心，分别编码Glc/Gal/Rha母体糖、1→2/1→6等连接和异头立体。Rha或其他连接扩展按实际来源选择，不用更换供体字符串生成未报道实验。
4. 对同位素/盐/质子化表示、催化模式、完整供体/受体、必要酶/辅助供体/再生系统、原始产率/未知重复、来源质量与关键身份歧义分别处置。
5. 每类输出build支持可得性、潜在新留出目标数、来源闭包组数、未知/排除和未取得清单。接口失败有限重试；某类不足可继续独立来源/另一类，不放松质量或分母凑数。

起草已核对的入口仅是候选：

- [GmF3G2″Gt/UGT79B30研究](https://pmc.ncbi.nlm.nih.gov/articles/PMC4494776/)，DOI10.1186/s12870-015-0504-7，提供糖间(1→2)glucosyltransferase来源入口；与旧K反应的精确重叠须闭包核验，不能因不同论文成为新留出。
- [VtCGTc研究](https://pmc.ncbi.nlm.nih.gov/articles/PMC10465961/)，DOI10.1016/j.apsb.2023.05.011，旧盘点仅metadata；须核清实际C-rhamnosyl化中间体与脱水/最终产物区别，尚未准入本任务。

入口不是已下载/已编码/已有迁移结果。数据库与开放接口用于发现和身份；具体来源定位、标准/NMR/作者完整结构赋值必须独立成立。unknown许可不自动可再分发，原文零/阴性不等于缺失。

## G2：准入、去重、开发角色与新留出冻结

- 继承P1严格/acid-oxygen-protonation-v1双签名规则，完整共价结构/立体/同位素/组分/计量保持；original与normalized及实际改变原子并存。
- 按DOI/PMCID/版本/原实验/专利家族（若有）/精确共价反应及明确上游实验转载关系做传递闭包。同反应在新论文重报仍与旧组相连，不能拆出处/换酶ID制造独立迁移。
- TASK-015、TASK-016、P1已用于构建/来源实例开发/模型诊断的反应和出处全部强制build/calibration/regression；身份重叠未知者保留并按保守角色处置。原件只作本任务新覆盖层输入，旧原角色/分组不回写。
- 上轮4SS失败可以成为v3构建校准支持，但其原角色/版本/已暴露身份必须保存；原7O增益、1b未补回和5C精确实例作为旧回归。它们不计新留出或新迁移成绩。
- 未用于本任务及旧任务模板构建/成绩开发的精确反应，才进入新development_holdout；全部仍development_exposed=true、training_overlap=unknown、human_reviewed=false，不称blind。
- 在新模板/模型输出前冻结全部合格实例、闭包组、主参照完整前体、质量选择规则与panel。每类至少6不同目标/6精确参照，至少2不同闭包出处组；全局至少12不同目标。多种子、多产物路线和重复来源不增加独立样本。
- 超过预算面板时按预登记质量等级和稳定组/反应ID，先满足两类各6，再按类别轮流扩至各最多9、全局最多18；每目标冻结一个主成键参照，其他有效参照完整另存。选择只依据来源质量/闭包/稳定排序，不看A/B/D成绩；所有未选记录及理由保留。
- 运行注册表只含build和模板支持；新holdout/参照由独立评估器读取。模板中心、过滤范围和prior冻结后不能用holdout精确结构补缺。build与holdout的论文/实验/精确反应闭包隔离须通过SHA和逐记录审计。

若任一类不足6目标或2出处组，该类迁移门未满足；允许完成另一类的预冻结验证，总体Partial。不得把旧失败案例或模糊结构填入短缺。

## G3：来源支持的C/糖间范围与边界

新增至少**1个C范围模板、2个糖间范围模板**；每个至少2不同完整受体支持，不靠酶名/条件/重复实验增加支持数。糖间新增范围应补足glucose和xylose两种当前缺失供体的明确受体糖/连接中心；保留已有apiose范围。两个模板是否属于不同供体/连接/受体条件按规范中心和真实作用范围去重，ID/atom-map变化不计数量。

C范围声明母核/反应位点、供体糖型/立体、mono/di-C受体条件、催化模式和必要上下文；对中间体反应保持真实结构/必要立体，不能借脱水“纠正”回放。糖间范围声明完整受体糖及可接受修饰、连接氧/位点、供体和异头立体，不将β-Glc、β-Gal、α-Rha或1→2/1→6混为一体。

每个新/继承可执行模板对全部声明支持实例完整前体精确重现100%；新模板至少4个相关边界，包括错误供体、必要立体、声明范围外的位点/受体糖或母核、错误催化上下文，违反数0。若某项不适用，在固定边界合同中说明并用另一相关边界替代，不能事后删失败。负对照只能依据明确范围；原文未报告不等于实验阴性。

对每个候选保存template_source_support、exact_seed_instance_match、scope_applicability、transfer_status、prediction_conditions_verified及原始来源。新精确目标的迁移必须由scope_template产生且exact_seed_instance_match=false；精确实例白名单重现仅列校准。种子条件/基因、实例认证和产率不复制给新目标，yield_value=null、actionable/evidence_closed不自动晋级。

支持精确实例、表示变体、实际映射反应动作和远端E/Z分别验证；任何支持失败保留在原分母并阻止模板准入。模板匹配不确定、源物种关键表示未知或守卫越界则停该模板，修复后新版本重验。

## G4：显式v3、固定比较与证据追踪

策略v3默认关闭，v1/v2分别可加载，默认请求仍原形状；新配置与包副本SHA一致，父子进程绑定且缺资产/漂移失败关闭。复用表示规则、cap4/prior0.2/weight1、固定分支12内保留A前三不同已过滤通用动作；不调PUCT/模型/通用filter/库存/审核。必须在看成绩之前冻结新范围、模板去重、模板顺序/截断/融合合同及支持SHA。

新比较使用**A/B/D**，避免字母C与C成键类别混淆：

| 臂 | 本任务实际策略 |
| --- | --- |
| A | 当前通用optimized，领域扩展关闭 |
| B | A+冻结的P1 v2；模板manifest及配置保持原SHA |
| D | A+新v3；包含受保护的继承能力与build-only新C/糖间范围 |

新主面板A/B/D全部在本任务真实运行、相同目标/seed/审核17库存/模型/通用过滤/参数；历史A/B/C成绩只作背景，不能替代本轮新比较。新请求每次独立MCTS，不读结果缓存，不回退BFS。完整追踪生成、截断、过滤、实际创建、原outcome index/slot/node及来源/版本，差异逐项登记。

候选可得性和真实节点创建分别报告。D保留A前min(3,A不同已过滤动作数)违反0；其他挤出数量和化学价值unknown单列。每类D相对A、B的冻结参照损失均0，保留旧O迁移、旧C支持和apiose能力，不用增加O成绩抵偿C/糖间失败。

## G5：按类别验收迁移增益与真实MCTS

定义family为C_formation或sugar_sugar_formation。只对冻结主面板、每目标主精确成键参照计算下列量：

- N_family：全部冻结不同目标/精确参照（每类≥6），包括运行错误/超时/未知，不能事后缩小。
- N_gap_family：单步诊断A和B均正常完成、均未过滤保留完整参照的目标数；来源/结构未知和执行错误不算“模型不会”，仍留在N并单列。
- G_family：上述缺口中D正常过滤保留完整参照，且由新/受保护的build来源范围模板迁移产生的不同目标数。要求**G_family≥3且G_family/N_gap_family≥50%**；N_gap=0时率null，增益门未满足。
- 同时输出D相对A、B各自的缺口/补回/损失/净覆盖；两类各净覆盖为正，损失0。各类成功补回还须来自至少**2个不同留出来源闭包组**，避免再将全部收益集中一篇论文。
- 上述每类至少3目标须在seed0/1/2中A/B正常且均未创建完整参照动作，D正常实际创建该参照动作；全部三seed成立才计实际迁移目标。生成/过滤日志不能代替创建记录，错误、超时、重试全部保留。
- 准入反应、实验上下文、模板/变换、distinct donor/acceptor/core/link/source、生成/过滤/节点、每seed/跨seed分别计数。按糖型/受体糖/位点/母核/直接或中间体C反应分层，明确哪些层只有支持、哪些有留出和成功；不能用总体结果宣称每层迁移。

所有成绩是来源闭包隔离的开发证据，不推断训练独立、酶/反应可行性或统计显著性。按独立目标/反应/出处报告，不把三seed当三个独立化学样本。

## 硬验收表与总体判定

| 验收项 | C成键 | 糖间成键/共同门槛 |
| --- | --- | --- |
| 新留出分母 | ≥6不同目标/参照，≥2闭包出处组 | 同左；全局≥12不同目标 |
| 新范围 | ≥1，有≥2不同受体支持 | ≥2，补glucose/xylose供体对应范围，各≥2不同受体 |
| 来源身份/单步准入 | 完整C形成单步，脱水/路径单列 | 完整受体糖/供体/连接/异头立体；关键歧义不准入 |
| 候选新增迁移 | ≥3且≥50%双基线缺口；正净覆盖 | 同左；O成绩不抵偿 |
| 收益出处多样性 | 成功补回来自≥2闭包出处组 | 同左 |
| 三seed真实补回 | ≥3目标A/B均正常未创建、D均创建 | 同左 |
| 参照/通用保护 | 对A/B损失0；保护前三违反0 | 同左；其他挤出与价值unknown单列 |
| 支持/边界 | 声明支持100%，新模板≥4边界/模板、违反0 | 同左；全部来源/实际动作可追溯 |
| 已暴露旧SS修复 | 不计新C/糖间迁移 | 4/4旧SS完整参照重现并在D三seed创建，另列校准/回归 |
| 旧实例/行为 | 旧5C支持和7O三seed创建不退化 | 旧12目标+5C回归；默认关闭/v1/v2/审核库存不漂移 |
| 工程/数据保全 | 118既有本地回归及必要新测试；无资产skip明确 | 来源/记录差额0，核心重建字节一致，包外安装/默认/缺资产通过 |
| 预算/报告 | 新任务总≤240保守服务尝试、每次墙钟≤60秒 | 独立账本/失败全保留；REPORT/STATE/版本/分层指标可重算 |

工程、C迁移、糖间迁移分别登记engineering_status、C_transfer_status、sugar_sugar_transfer_status。所有共同门及两类硬指标都通过，且有REPORT/最终审计，才能总体Completed。任一类不足总体Partial；另一类结果和来源短缺/误差分析完整交付，不降低原指标、不扩大表示规则或调整留出。

## 执行预算与阶段停止条件

### 来源预算

新增下载≤2GiB；HTTP总尝试≤2500（失败/重试计入）、metadata去重发现≤5000、开放全文≤120文章版本、附件≤240件；最多4工作进程、每请求最多2尝试，尊重官方限流。继承原件列路径/SHA与读取范围，原已取得数量不重复算新增；取得失败、未知许可、分页未取得和未解析补充材料均有处置。

### 搜索预算

- 主面板计划12–18目标×seed0/1/2×A/B/D=108–162次；严格quick单阶段12秒/20迭代/120节点/12分支/深度2/top_k5，服务全部phase墙钟≤60秒。
- 旧回归固定P1全部12目标（7已补回O、4SS未补回、1b未补回）+5C支持目标=17目标，D三seed，计划51次；输入去重若减少实际目标，原17参照从属关系全部保留，不产生未登记新目标。旧4SS改用校准后命中不计新留出；1b原未补回不是实验阴性，后续命中单列。
- 主/旧回归验证尝试共享硬上限**213**（162+51），含失败/超时/重试/版本重验；工程/安装/完整回归/合成service fixture等另最多**27**，新任务全部保守服务尝试总硬上限**240**。计划次数不等于可无限重试；不足时按Partial保留未执行单元。
- 所有会调用tree_search的安装/测试/诊断均计本任务；无tree_search的单步/源实例重放计数0但保存证据。可把包外安装验证并入预登记主矩阵单元，不能漏记该实际尝试。
- 独立outputs/task016-p2/v1/run_ledger.jsonl与不可变批准预算/原基线SHA绑定；使用固定路径/哈希校验，不允许任意环境变量增加上限。旧TASK-016120、P1批准240及其33/216历史账不改，不移账/转任务规避预算。
- 冻结参数/prior/范围后如发现代码错误或越界，停验收、保留全部失败及旧合同；在预留中修复并按明确受影响完整面板新版本重验。预算内是否可完成须先核账。确需增预算/调科学指标/改变任务性质，先追加明确批准修订和理由，不能先超额后补账；不能因自主权限静默改门槛。

### 阶段门与停止条件

1. G1许可/可得性/关键身份不足：停止对应来源或实例准入，继续独立来源至预定上限；不得请求所有者手工检索作为默认补救。
2. G2留出不足：该类保持Partial/未执行，不借旧失败或同反应新论文填足；另一类可按其预冻结合格面板独立验证。
3. G2/G3存在来源闭包泄漏、holdout进入抽取/白名单/守卫、支持重现失败/边界越界：停止接入/成绩验收，保存失败，修复后新版本重验。
4. 活动/审核/库存/模型/旧载荷SHA漂移或账本不守恒：停止真实搜索与验收，定位原因；不得修改旧证据使校验消失。
5. 达任一硬预算：保存账本/未执行项并报告；不得删失败、隐藏fixture、用缓存/旧运行顶替本轮新搜索。
6. 涉及受限认证/不可获取原件、扩旧裁决/库存、写历史目录、训练、正式评测/供应/发布/Git同步等范围外行动时停止该部分，只在最必要事项请求所有者介入。既有自主执行偏好不转化为范围外批准。

## 阶段产物与执行验证（计划）

| 阶段 | outputs/task016-p2/v1/计划核心产物 |
| --- | --- |
| G1 | execution-baseline.json、query_contract.json、source_registry.json、acquisition_attempts.jsonl、source_yield_inventory.json、file/record_dispositions.jsonl、source_feasibility.json |
| G2 | instances.jsonl、unresolved_instances.jsonl、negative_instances.jsonl、reaction_groups.jsonl、counting_contract.json、dedup_links.jsonl、legacy_roles.jsonl、development_split_manifest.json、build/holdout_views.jsonl、reference_precursors.jsonl、runtime_instances.jsonl、evaluation_reference_manifest.json |
| G3 | templates.jsonl、template_groups.jsonl、applicability_contract.json、representation_rules.json、template_validation.jsonl、build_action_validation.json、template_source_manifest.json |
| G4 | review_binding.json、fusion_contract.json、default_off_regression.json、v1_v2_regression.json、experiment_contract.json、single_step_A_B_D.jsonl、gap_register.jsonl、candidate_displacement.json |
| G5 | run_ledger.jsonl、mcts_observations.jsonl、paired_results.jsonl、action_trace.jsonl、legacy_regression.json、metrics_by_family.json、stratum_support.json、costs.json、audit.json、replay.json、delivery_manifest.json |

起草轮只核文档链接、范围/分母/预算一致性、git diff --check及受保护输入SHA，不采集新原件、修改运行代码或启动MCTS。执行前须登记批准和实际基线，才运行所需构建/验证；以下为执行轮合同，不是本轮已运行声明：

~~~bash
python3 -B scripts/operate.py TASK-016-P2 env FLAVORETRO_TASK016_LEDGER=/home/ljx/FlavoRetro/outputs/task016-p2/v1/run_ledger.jsonl FLAVORETRO_TASK016_PURPOSE=task016_p2_engineering .venv-foundation/bin/python -B -m unittest discover -s tests -v
python3 -B scripts/operate.py TASK-016-P2 git diff --check
~~~

执行轮还须有真实来源/支持/边界/节点证据、核心字节重建、包外当前v3/默认关闭与缺资产检查。118原回归保留，新测试只针对实际合同/隔离/边界，资产skip不冒充实际源/模型验证。所有命令/写入经scripts/operate.py TASK-016-P2。

## 验收清单

- [x] 执行批准与实际基线/固定预算已登记，来源通过开放接口自动取得/复用，许可/失败/分页/记录与原件守恒。
- [ ] 两类各≥6新留出目标/参照与≥2闭包出处组，全局≥12目标；旧已暴露实例强制build/regression，面板/参照在模板/成绩前冻结。
- [x] ≥1C+≥2糖间范围模板，各≥2不同受体支持；补glucose/xylose中心，全部支持100%、相关边界违反0，严格/表示/实际动作分轴。
- [ ] 两类分别≥3目标、≥50%双基线缺口补回，成功各来自≥2出处组；对A/B参照损失0、通用前三保护违反0。
- [ ] 两类分别≥3目标三seed实际参照动作补回；新A/B/D真实矩阵完整，错误/超时/重试不算化学缺口。
- [x] 4旧SS校准重现与D三seed创建；旧O/C/apiose/默认/v1/v2与审核/17库存保持；118既有回归及必要新验证通过。
- [x] 来源/模板/实际节点可追溯，核心字节重建/包外安装/缺资产检查通过；新总≤240、墙钟≤60秒及旧账历史不改。
- [x] REPORT按engineering/C_transfer/sugar_sugar_transfer分别给Completed/Partial、分层失败/未知与边界；STATE/架构/路线/导航/交付SHA更新，正式/独立化学门保持。

## 必须提交的报告与后续判定

执行完成、部分完成或失败均提交**REPORT-016-P2-c-sugar-transfer-validation.md**，逐项列实际值、冻结分母、source闭包、原始身份/方向/立体、模板/范围/支持、A/B/D生成/过滤/节点、两类/各层补回及损失/挤出、全部运行/失败/成本/预算、旧回归/重建/安装/保护哈希与未完成项。说明已补齐哪些迁移层，哪些仍只有来源重现，是否足够推进TASK-017设计与准入核查；不据此自动执行正式benchmark或把开发留出变独立gold。

## 决策与历史

- 2026-10-06：所有者要求进一步扩充C/糖间迁移验证；只读审计确认C精确5/范围0/留出0，旧4SS×3seed没有领域动作，补足对应范围与新来源验证为主要方向。
- 2026-10-06：所有者“我觉得你说的有道理, 请开始写 TASK-016”，授权本合同起草。采用TASK-016-P2补充编号，既有TASK-016/P1 Completed不回退。6/2/3/50%方向已采纳，本文将新增收益出处多样性、范围支持、双基线和预算等执行细节明确为Proposed；本轮不标工程批准或human_reviewed。
- 2026-10-06：所有者“批准, 开始执行”，human_direct批准v0.1的G1—G5、两类独立硬指标及新240次预算。原Proposed起草决定保留，本条登记工程执行授权；从G1开始，科学阈值不因来源不足自动下调。

## 本轮执行结果与保留门槛（2026-10-06）

[REPORT-016-P2](../reports/REPORT-016-P2-c-sugar-transfer-validation.md)与outputs/task016-p2/v2/audit.json为本轮事实入口：40/40工程检查通过，整体Partial；当前54模板（46精确/8范围），新增1C+2糖间范围，各2完整受体；134声明支持/134映射动作与18新范围边界通过。85继承上下文/58旧反应保留，新增准入0，2条C8编码撤回，P1原12未决上下文不改。

旧17目标×三seed的51次D真实MCTS正常：旧4SS/5C/7O均全seed创建参照，旧1b仍未补回；旧4SS为来源暴露后的build校准修复，不计新留出或独立迁移。C/糖间新面板均为合格0目标/0闭包组，没有执行新A/B/D；N_gap/G/补回率/损失/净覆盖为null，科学6/2/3/50%门槛保持。源盘点58文章/55可得全文，209新直接HTTP与8工具请求单位、268,558,237字节；35标题候选及未编码/身份冲突仍待处理，不宣称穷尽来源。

124本地测试通过；无资产117通过/7资产跳过，第一轮快照遗漏scripts的失败保留；当前包外安装/默认/缺资产通过，8核心文件重建字节一致。1,591受保护SHA不漂移。独立账本61保守预留/61完成=51验证+10工程，含6模拟错误fixture；55实际服务尝试均正常，最长8.834秒。旧账33/216不改。正式/独立化学/供应/release门保持。

- 2026-10-06（agent_delegated）：G2新面板不足，停止新迁移矩阵，继续来源支持范围与旧17目标回归；来源扩展12篇后仍不准入合格新面板，按合同Partial交付，未降低科学阈值或扩大预算。
- 2026-10-06（agent_delegated）：初版C8复制糖片段没有取得完整源立体绑定，撤回两例并用合格v2覆盖；v1历史、旧P1角色/配置/账本保持。v2 split继承的初版selection句以role_interpretation.json及qualification/实际85条runtime解释，不据旧句增加准入。
- 2026-10-06（agent_delegated）：修复构建工具、无资产快照和full_regression日志指针，失败/错误版本保留；本合同测试命令用途明确为engineering，实际账本只接受validation/engineering，原批准SHA与预算不改。
- 2026-10-06：REPORT/STATE/架构/路线/导航更新；未满足项保持未勾选，不批准或执行TASK-017/018。
