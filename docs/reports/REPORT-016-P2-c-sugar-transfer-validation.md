# REPORT-016-P2：C成键与糖间成键迁移验证

## 对应任务与结论

- 任务：[TASK-016-P2](../tasks/TASK-016-P2-c-sugar-transfer-validation.md)，合同v0.1，2026-10-06。
- **总体Partial；工程交付Completed，C迁移Partial，糖间迁移Partial。** 两类新面板都未达到各6目标/2来源闭包组；未执行新A/B/D比较，增益、补回率、损失及净覆盖均未评估，以null保留。
- 所有者“批准, 开始执行”是human_direct执行授权。阶段推进、来源取舍、身份撤回、快照与日志修正均为agent_delegated，不写human_reviewed。
- 基线main / 993b22f5e8eed5797d27f02c566af1b86a4b7880及实际工作区SHA；执行基线SHA为795ae452638fbaa42436771b1f9f9209aabcfdfd376aa5da907f9b4aa475f9f2。无本任务提交/推送。
- 当前合格载荷outputs/task016-p2/v2；显式策略版本v3。v1保留来源过程、初版撤回记录、执行批准与唯一运行账本；v1的87条初版编码不能当当前准入。

项目增益是补足了三个有来源支持的候选生成范围，并实际修复此前没有对应领域动作的4个糖间旧目标。它还没有增加已准入新反应或证明新目标独立迁移，不能宣布完成roadmap对P2的全部要求。

## 改动文件

| 目录职责 | 文件 | 实际改动 |
| --- | --- | --- |
| 候选范围与守卫 | flavoretro/glycoside_library_v3.py（新增）；glycoside_library.py | 复用v2表示/模板动作，为v3增加C第二次成键、Glc/Gal糖O2及prenyl化Rha糖O2范围；精确供体、母体糖立体、母核和连接守卫 |
| 请求与独立进程 | contracts.py、cli.py、worker.py、service.py、workspace.py | 显式v3选项、父子SHA绑定与失败关闭；保持默认及旧v1/v2行为 |
| 守恒账本 | flavoretro/task016_runs.py | 固定P2执行批准SHA、路径、验证213/工程27/总240上限；旧TASK016与P1账本不改 |
| 配置 | configs/glycoside-library-v3.json及包内同名副本 | 默认关闭，指向合格v2模板manifest；两个副本SHA一致 |
| 自动采集/构建/验收 | scripts/task016_p2_*.py；tests/test_task016_p2_library.py | API发现、官方全文/SI、准入撤回、支持/边界/映射、真实旧回归、包外安装、无资产、重放、守恒审计；新增6项必要合同测试 |
| 本地原件 | data/raw/task016-p2/2026-10-06 | 209次响应均保留，包括503/500/403、超限部分响应和网络失败；只读快照，不入Git |
| 本地结果 | outputs/task016-p2/v1、v2及replay-v2；outputs/validation/task016-p2-* | 来源及各层处置、85实例/54模板、51个旧回归真实结果、账本、工程证明、全部失败及版本历史；不入Git |
| 治理导航 | TASK、REPORT、STATE、ARCHITECTURE、docs导航和两条roadmap | 当前Partial及剩余验收门，保留旧任务/报告 |

只有7个已有运行模块发生必要修改。open_glycoside_library.py、search.py、通用模型/过滤/PUCT/排序、审核/17库存、旧配置/指针、旧来源/载荷/账本均保持；1,591个受保护文件SHA无漂移。

## 来源、身份与分组

按照nature-academic-search工作流，使用公开Europe PMC、NCBI与Crossref接口以及官方PMC OA下载，复用不可变旧原件；未要求所有者手工检索、未使用受限认证。ORD/HTE不强制配额：继承P1已有ORD来源/角色审核，本轮针对有直接C/糖间证据的开放论文与SI；新批量UGT筛选数据也只按实际身份质量处理。

| 实际量 | 结果 |
| --- | --- |
| 查询合同/路线 | 47；原Europe PMC core路线19查询各503两次后保留失败，转lite/NCBI |
| 查询记录及处置 | 1,590/1,590，差额0；元数据登记键1,382，跨来源别名保留 |
| 文章盘点/取得全文 | 58/55；26个新可用文章版本，28个新全文URL取得尝试，另复用旧原件 |
| 新附件URL/可用附件 | 50/47；部分超32MiB响应、403与失败保留，不算可用原件 |
| 新直接HTTP/原件 | 209/209，差额0，268,558,237字节（约256MiB） |
| 外部发现工具 | 另8个请求单位已登记；工具内部HTTP数不暴露，不宣称精确全量HTTP数 |
| 复用旧文件/源片段 | 131/2,851；每份路径/SHA、许可/版本及记录处置可查 |
| 准入/未决 | 85条继承确认上下文、58个旧共价反应；**新增准入0**；2条初版编码撤回，10条本轮来源/身份未决记录，P1原12未决上下文原封保留 |
| 明确阴性 | 11条源试验定性阴性；数值收率null，不把“未检测”制造为数值0或普遍反应阴性 |
| 未完成发现 | 35篇标题级候选仍未取得/细读；已取得材料亦有未编码图形/未解析格式与身份待确认，盘点不声称穷尽化学空间 |

新下载/直接HTTP与可观测工具单位、登记元数据、新文章/附件均在2GiB/2500/5000/120/240上限内；每URL最多2尝试，最多4并行采集。分页未取得、失败和许可未决逐查询保留。

准入关键裁决：

- [TcCGT来源PMC9700910](https://pmc.ncbi.nlm.nih.gov/articles/PMC9700910/)报告K/Q 8-C-glucoside及NMR，但本轮取得材料尚未将完整糖立体赋值绑定到可执行编码。初版复制既有C糖片段的2条记录被撤回，保留在provisional_withdrawn_instances.jsonl，不进入模板/运行注册表。
- [VtCGTc来源PMC10465961](https://pmc.ncbi.nlm.nih.gov/articles/PMC10465961/)的C-rhamnosyl中间体与脱水后最终产物分开；MS或最终violanthin/isoviolanthin不能补齐完整单步中间体身份。
- [UGT79B6来源PMC4282749](https://pmc.ncbi.nlm.nih.gov/articles/PMC4282749/)与[UGT79B30来源PMC4494776](https://pmc.ncbi.nlm.nih.gov/articles/PMC4494776/)的K-sophoroside与旧反应重叠，整源不能成为新的独立留出组；其他底物活性不自动赋成完整产品结构。
- [Ib3GGT来源PMC6255700](https://pmc.ncbi.nlm.nih.gov/articles/PMC6255700/)、UGT79B1与茶CsFGT1等已识别4个糖间潜在命名目标，但身份/来源闭包尚未全部准入，也未形成6目标面板。
- 补充取得12篇候选并自动抽取21份SI文本；化学C方法的图形结构、HTE的活性/质量命中、phloretin旧反应及多步路径分别保留，未用其凑新反应数。PMC12993211正文将副产物称为naringenin-C-glycoside，SI FigureS5称naringenin-7-O-glycoside，该冲突未自动消解。

全部旧85上下文在P2强制build/calibration，保存原P1角色和SHA；旧12留出及其中4个SS失败不再计新留出。所有当前可执行模板只读这些build实例。合格split的qualification/counts/runtime已撤回两例C8；其继承的初版selection叙述保留为历史，在role_interpretation.json明确覆盖含义，不能按该旧句推断新增准入。

## 范围模板和实际动作

| 新范围 | 来源与完整受体支持 | 允许的候选范围及限制 |
| --- | --- | --- |
| C第二次成键 | FcCGT，phloretin mono-C-Gal与mono-C-Xyl，2受体 | Glc第二次C成键；限定单C母体糖与phloroglucinol dihydrochalcone上下文，不推广为直接flavone C6/C8活性 |
| 糖间Glc O2 | UGT79B31，K3-O-Glc与K3-O-Gal，2受体 | Glc→Glc/Gal O2；仅放宽C4表异构查询，完整母体糖立体守卫仍在，未扩到anthocyanin |
| 糖间Xyl O2 | EpF3R2″XylT，icariin与baohuoside I，2受体 | Xyl→α-L-Rha O2；限定prenyl化、4′-O-methyl flavonol上下文，原7位修饰保留 |

共54模板=46精确+8范围；继承51个模板逐字典不变，新范围3个。分类为O33、C6、糖间15。85实例仍为旧58反应，本轮没有用模板数量冒充新实验/新反应。

134/134声明支持完整前体重放、134/134映射反应动作重放通过；这些不是MCTS或独立化学验证。新模板原12个相关边界及追加6个完整骨架变异挑战全部通过：含错误UDP/催化模式/异头立体、糖内立体、C母体糖异头及改连另一糖羟基，共18项、越界0。远端表示/E-Z的继承回归保留；未知酶活、位点选择性、条件、收率仍未知，不复制源基因/条件/收率给新候选。

v3固定cap4/prior0.2/weight1、分支12、通用前三保护。父子进程绑定合格manifest SHA e17bff4c1b891fe8164e8f62bec21e54527a5662adf466548c5898fdb069da88；默认关闭，缺资产失败关闭。没有按留出或模型输出修改范围/融合参数。

## 按合同验收

| 项目 | 要求 | 实际结论 |
| --- | --- | --- |
| C新留出 | ≥6目标/≥2闭包组 | 合格面板0，未满足；来源候选继续保留 |
| 糖间新留出 | ≥6目标/≥2闭包组 | 合格面板0，未满足；已识别4个潜在命名目标尚不等于完整面板 |
| 新范围 | ≥1C+≥2糖间，每个≥2受体 | 1+2，各2受体，通过 |
| 支持/边界 | 100%，至少4相关边界/新模板，越界0 | 134支持及134映射重放；每新模板6项边界，通过 |
| 双基线新迁移 | 每类≥3、≥50%，收益≥2出处 | 未执行A/B/D，G/N_gap/率/损失/净覆盖null；不能记通过或化学失败 |
| 三seed新补回 | 每类至少3目标 | 未执行，未知 |
| 旧4SS校准 | 4/4，D三seed创建 | 4/4，12次真实D全部正常并创建完整参照 |
| 旧5C/7O回归 | 三seed参照创建保留 | 5/5与7/7；共15+21次真实创建；旧1b仍未补回，非实验阴性 |
| 旧17目标完整矩阵 | 17×3 D=51 | 51/51 live AiZynthFinder MCTS；正常51、错误0，无BFS/缓存替代 |
| 通用保护/挤出 | 保护前三违反0 | D内过滤保护169条检查、违反0；未做本轮配对A/B挤出，其他候选化学价值unknown |
| 默认/旧版本/库存/模型 | 不漂移 | 默认稳定字段与旧基线相同，v1/v2全部源支持重放、审核17库存/模型绑定保持，1,591受保护SHA通过 |
| 工程 | 118旧测试及必要新增；包外/重放 | 124/124本地；无资产117通过/7跳过；当前wheel外部安装、默认/v3真实探针、缺资产失败关闭；8核心重建文件字节一致 |

旧矩阵记录3,138条追踪：领域generated75、截断后75、过滤保留48、实际创建48。48次为旧16目标×三seed参照创建，不能计48个新反应或独立样本。当前实际有收益的是候选能力修复；所有新源迁移指标仍未测。

## 成本、预算与失败历史

独立账本outputs/task016-p2/v1/run_ledger.jsonl共61保守预留/61完成=51验证+10工程，分别低于213/27，总低于240。含6个模拟worker错误fixture（3 timeout、3 engine_error）；以操作时间窗、测试源SHA和日志绑定登记，并非6次真实引擎失败。实际服务尝试55/正常55/错误0。最长服务墙钟8.834秒，低于60秒；旧D中位数7.413秒。旧TASK016账33、P1账216及全部旧失败保持，未移账/删fixture。

两次构建工具错误（部分芳香SMARTS误作SMILES、边界查找不存在的类别）均在真实搜索前修复，历史代码/失败日志保留，不计MCTS。第一轮无资产快照漏带scripts，出现1个import错误；旧快照/失败报告保留，第二轮补脚本与官方ORD protobuf helpers后117通过/7跳过。7跳过为3项本地数据、3项本地模型、1项本地P2源资产，未冒充实际模型验证。

初版full_regression报告误绑定到探索rg日志，审计发现后保留错误版本并更正为实际unittest日志operations/command-1114.log（124测试、11.125秒、OK），没有为此额外重跑。失效原版本、失败响应、未执行主矩阵与空文件语义均可检查。最终导航检查的TASK/REPORT前缀判断也已修正，原失败命令保留，无服务重跑。

## 复核入口与命令

所有命令/写入均经scripts/operate.py TASK-016-P2。当前本地结果入口（均不入Git）：

- outputs/task016-p2/v2/audit.json：40/40工程检查通过；scientific_acceptance_passed=false、overall_status=Partial。
- metrics_by_family.json、stratum_support.json：分母/未执行null、支持层与未覆盖层；legacy_regression.json、action_trace.jsonl：真实节点与原outcome/slot记录。
- source_registry.json、source_yield_inventory.json、file/record/metadata_dispositions与negative_instances：来源差额0、失败/零/未知保留。
- primary_extension_source_review.jsonl、attachment_parse_manifest.jsonl、role_interpretation.json、final_stage_decision.json：新增来源处置与当前角色解释。
- fixture_ledger_annotations.jsonl、costs.json、replay.json、package_validation.json：成本、保守fixture、字节与安装证据；delivery_manifest.json：交付绑定。

~~~bash
python3 -B scripts/operate.py TASK-016-P2 .venv-foundation/bin/python -B scripts/task016_p2_verify.py
python3 -B scripts/operate.py TASK-016-P2 git diff --check
~~~

verify只重算现有证据，不启动MCTS。已执行来源发现/采集/准入、build、actions、boundaries、regression --run、package、asset_free、replay、account_sources命令见操作事件；冻结的原目录不能原地覆盖重建，需要新版本目录。本轮full unittest使用FLAVORETRO_TASK016_PURPOSE=task016_p2_engineering；实际仅接受validation/engineering两个预算用途。

## 偏差、遗留与后续

G2未满足导致主新面板停止；经agent_delegated阶段决定，完成G3/G4来源支持的范围工程及G5旧17目标回归。科学6/2/3/50%门槛保持，整体不Completed。v1初版身份撤回后当前载荷改为v2，没有回写旧版本或P1实例角色。

剩余工作是开放来源的完整单步产物/糖立体解析与闭包核查，建立各类至少6个新目标、至少2出处的新面板，再冻结范围与真实A/B/D运行。35篇未处理标题候选、图形结构、许可/API失败与TcCGT产品冲突分别保留，不能据此说该反应空间没有更多模板。预算余量不是已取得科学证据，也未证明再采集必能达到门槛。

本轮支持TASK-017评测设计/准入核查，但不能批准或满足正式blind运行。development_exposed=true、training_overlap=unknown；新增human_reviewed/独立化学/新活性/预测条件与产率/供应/路线闭合认证均0或未知，formal_run_ready与release_ready保持false。未执行TASK-017/018、提交/推送、部署或发布；未运行新远端CI，当前工程结论来自本地与本机外部安装。
