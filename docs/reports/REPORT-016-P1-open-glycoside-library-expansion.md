# REPORT-016-P1：开放黄酮苷反应库批量扩充与适用范围验证

## 结论与验收范围

2026-10-06，TASK-016-P1 **Completed（经agent_delegated批准修订的v0.2合同）**。engineering_status=passed，library_coverage_status=passed，最终51/51验收检查通过。新增**54个**来源明确的精确共价成键反应、**47个**去重可执行模板；5个多受体范围模板在冻结开发留出面板补回**7/12目标，58.3%**，7目标在seed0/1/2均实际创建完整参照动作，A/B参照损失均0。

这是来源约束的反应库和开发候选覆盖交付。全部增益集中在一篇UGT71AP2论文；不是全黄酮苷空间泛化、独立化学验证、正式blind benchmark或可采购闭合路线。模型训练重叠unknown，development_exposed=true，human_reviewed=false，prediction_conditions_verified=false，actionable=false、evidence_closed=0，formal_run_ready/release_ready仍false。

原预算180次未作为完成依据：为来源身份撤回及完整重验，依所有者“允许执行。agent有极高自主权限，human只在最必要的情况下插手。”另记agent_delegated批准，总上限180→240、主验证162→216、工程预留18→24；科学门槛与单次60秒墙钟不变。最终**216/240保守尝试**，主193/216、工程23/24。原合同、原执行基线与每次失败完整保留，不把自主批准写成人审。

## 来源取得、处置与身份质量

通过公开Rhea、Europe PMC/PMC、PubChem及官方Zenodo下载自动取得原件，无所有者人工检索前置。新增586次HTTP尝试、671,194,259字节原件；120文章ID中114可得、6失败/许可或接口待定；578去重文章metadata、889已取得检索行全部有处置。全文/附件解析5940段、22份SI文本；这是实际取得范围，不是穷尽全网或论文所有实验。宽检索未取得页面、未下载附件、失败响应和未知许可分别保留。

Rhea225方向查询行（194/4/12/15）与官方方向映射作为知识/出处入口；EnzymeMap完整processed349,458行、raw324,800行保留，关键词候选2414/2625行及推断/反转标记单列，缺原始逐实验出处的行未直接准入。Zenodo8254726数据许可CC BY4.0与代码MIT分开。ORD继承TASK-015的53文件整库冻结调查；GitHub增量API403、SABIO响应HTML而非SBML，无新ORD/HTE精确实验产出，未用接口可访问数冒充新反应。

93条新实验注释的最终处置为**81准入+12身份待确认=93，差额0**。PMC9149423的12个UDP-Gal上下文原文支持糖基化活性，但未对六受体逐一建立完整3-O-beta-D产物身份，六精确反应和模板在v2撤出；原记录、数据库身份候选与旧载荷保留。最终不借3GT名字、Rhea结构或同族酶推断填补关键实验身份。

其他准入包括FaGT6/7与MrUGT78R/W的O糖基化、SbUGT/UGAT、CgUGT89AK1、UGT78D1；AbCGT/FcCGT的已分离NMR C成键；Pc/Ag/Gu apiosyltransferase、UGT79B31与EpF3R2″XylT糖间成键。来源定位、标准/NMR/作者结构判定及agent编码性质逐实例保存；tentative MS位点、酸脱水后的多步C产物和无法隔离路径不计新单步形成。原文零/明确阴性与缺失分开；Ep论文可疑质量单位原样留在raw_numeric_conflicts.jsonl，未猜补微克或用于预测收率。

原件data/raw/task016-p1/，完整取得与处置outputs/task016-p1/v1/。**当前合格准入/运行载荷为outputs/task016-p1/v2/**；任务内v1只是旧构建版本，与TASK-016的旧策略v1是两个编号轴。

## 反应、来源与模板分母

| 项目 | 硬指标 | 最终结果 |
| --- | --- | --- |
| 新精确成键反应 | ≥40 | **54**；加继承4，共58 |
| 新受体/转移糖型/底层出处组 | ≥10/3/6 | **41/6/11**；新来源14论文，闭包后11组 |
| 新O/C/糖间成键 | C、糖间各≥2 | **33/5/16** |
| 实验上下文/独立物理重复 | 分别登记 | 合格85（81新+4旧）；物理重复未由行数推断，unknown/null |
| build/holdout | 来源/反应闭包隔离 | build73上下文/46反应；holdout12上下文/12反应/12目标 |
| 可执行模板 | 新增≥12 | **51总=46实例+5范围；新增47=42实例+5范围** |
| 范围模板 | ≥4，各≥2受体，≥2糖型 | 5个、3糖型，各2–11受体 |
| 支持实例精确重现/边界 | 100%；每模板≥2，违反0 | **128/128支持、162边界全部通过**；73构建实例实际动作重放通过 |

糖型为glucose、galactose、rhamnose、glucuronate、apiose、xylose。按共价转化去重：条件、酶名、重复出处、离子态和多种子不增加新反应；SMARTS按去map后的规范图、必要供体/上下文和实际作用范围去重，任意ID/重编号不增加模板数。整个库只有3种键形成类别、10种键类别×糖型组合；51模板不能称51独立反应家族。

| 范围（英文合同标识） | 支持上下文 | 不同受体 |
| --- | --- | --- |
| glucose / phenolic_aryl_O | 25 | 8 |
| glucose / flavonol_O3 | 8 | 3 |
| galactose / flavonol_O3 | 2 | 2 |
| rhamnose / flavonol_O3 | 7 | 4 |
| apiose / glucoside_O2 | 13 | 11 |

四个O范围保留来源支持的黄酮母核和OH/OMe装饰、位点/完整UDP糖供体/立体/上下文守卫；葡萄糖O-芳基与黄酮醇O3范围分别处理。apiose范围要求完整β-D-glucosyl O2局部结构和来源支持的flavone/flavanone/isoflavone/chalcone/dihydrochalcone母核，其他母体部分保持，不复制种子的酶活/收率。有限局部迁移是候选适用，不是特定基因、位点选择性或任何新取代基的实验认证。

表示规则acid-oxygen-protonation-v1仅处理单键负酸氧→OH，保留共价结构、立体、同位素、其他电荷、盐/组分和计量；不是无条件中和，也不推断实际优势离子态。旧4实例的严格离子物种重现与v2规范物种重现分别通过，表示增加不计新的化学覆盖。所有模板有相关错误供体/上下文、异头立体等边界；4个OH/OMe范围另有O-O链负对照。

## 分组冻结与开发比较

在首次模板/模型输出之前，按DOI/PMCID/原实验/完整共价反应传递闭包冻结build/holdout；旧v1及TASK-015已暴露精确反应强制build。当前资格修订仅移除12身份不充分的build记录，**holdout字节、原角色、12目标清单、全部5范围模板/支持/权重均未改动**。TASK-015全部16来源文件的出版重叠核对未发现留出三篇论文匹配；这不证明模型训练独立。

A=通用optimized；B=A+旧v1精确实例；C=A+当前v2范围/表示/通用前三动作保护。全部同审核task015-06-v1、17候选库存、模型/通用filter/KnownHazards，quick12秒/20迭代/120节点/12分支/深度2/top_k5。评价整个v2方法，模板扩充、表示与融合规则的单独归因留给后续消融。未给运行注册表或过滤器提供holdout结构/位点白名单和评估参照。

当前108单元证据明确包含**本任务r2既有真实A/B72个控制+资格修订后全新C36次**。A/B活动代码、模型/过滤/库存/请求不变；变更为不加载的v2模块/配置及仅追加预算记录的账本代码，逐项证明保存在retained_A_B_control_proof.json。继承不是新运行，也不是用缓存顶替已要求的新搜索；C全12目标×3seed重新执行，未只选择成功7例。包外最新wheel的C验证并入其中一单元，另1次默认关闭真实搜索逐稳定字段与旧包外结果比较一致。

| 留出产物 | 类别 | A覆盖 | B覆盖 | C覆盖 | C三seed补回 |
| --- | --- | --- | --- | --- | --- |
| PMC11365401 / UGT71AP2 product 1b | O | 0 | 0 | 0 | 0/3 |
| PMC11365401 / UGT71AP2 product 1a | O | 0 | 0 | 1 | 3/3 |
| PMC11365401 / UGT71AP2 product 7a | O | 0 | 0 | 1 | 3/3 |
| PMC11365401 / UGT71AP2 product 2a | O | 0 | 0 | 1 | 3/3 |
| PMC11365401 / UGT71AP2 product 6a | O | 0 | 0 | 1 | 3/3 |
| PMC11365401 / UGT71AP2 product 3a | O | 0 | 0 | 1 | 3/3 |
| PMC11365401 / UGT71AP2 product 4a | O | 0 | 0 | 1 | 3/3 |
| PMC11365401 / UGT71AP2 product 5a | O | 0 | 0 | 1 | 3/3 |
| PMC5856881 / kaempferol 3-O-beta-D-glucosyl-(1->2)-beta-D-galactoside | 糖间 | 0 | 0 | 0 | 0/3 |
| PMC5856881 / kaempferol 3-O-beta-D-glucosyl-(1->2)-beta-D-glucoside | 糖间 | 0 | 0 | 0 | 0/3 |
| PMC9786081 / epimedin B | 糖间 | 0 | 0 | 0 | 0/3 |
| PMC9786081 / sagittatoside B | 糖间 | 0 | 0 | 0 | 0/3 |

单步过滤后A/B/C参照覆盖**0/12、0/12、7/12**；N_gap=12，G=7，补回58.3%，净覆盖+58.3百分点，相对A/B损失0。MCTS36配对中补回21，按独立目标计7，每seed7；所有108实际单元status=ok。7增益均来自PMC11365401的UGT71AP2 2′-O-葡萄糖基化目标；其双O糖苷1b和另四糖间目标仍0，留出C成键为0。

C保留A排名前min(3,已过滤不同前体数)的通用候选，单步和36次C树保护违反0；另有**5个**通用非参照动作被挤出，化学价值unknown，参照零损失不等于这些动作无价值。保留完整raw outcome index、创建slot/node、反应签名和版本来源；转移候选template_source_support=true，exact_seed_instance_match=false，条件/收率/化学验证未确认，不复制支持实例的产率。

| 成本（36次/臂，服务墙钟含加载） | A | B | C |
| --- | --- | --- | --- |
| 平均秒 | 4.05 | 4.35 | 7.36 |
| 平均节点 | 23.31 | 23.31 | 23.81 |
| 平均领域模板尝试 | 0 | 25.33 | 357 |

固定模型资源下这些是本地开发成本，不是性能基准或显著性估计。

## 修订、失败与完整预算

r1新增trace中的NumPy child-slot无法JSON编码：25主尝试中24失败、1成功，全部保留且不用于最终成绩。r2仅转Python int后完整108次重跑。r3最终负对照发现原OH/OMe守卫误接受额外O-O链，收紧至原声明边界，整篇8目标×3seed C复验24次，原边界失败保留。r4按原文身份撤回六Gal反应并重验全36C，科学分母、范围和权重不后验调优。r4结束的报告写入缺少write导入，在36成功搜索/诊断完成后修复并据已存原件重建报告，无额外搜索。最终账本合成fixture分类纳入r2_final_regression，避免漏算2个mock。

**216保守服务尝试=193主（25+108+24+36）+23工程**；全部started/finished配对。状态182ok、34error，其中24为真实r1序列化失败、10为测试合成错误/超时fixture；**实际服务/MCTS尝试206**（含24失败），不把fixture当真实引擎失败或化学失败，仍占保守预算。单次服务最大8.756秒≤60。旧TASK-016账本仍31实际/33保守；跨任务237实际/249保守，旧任务120上限未提高。

预算批准文件哈希固定在task016_runs.py，P1专属账本继续绑定未改的原180基线，新增行另绑定r4批准SHA；旧行180/新行240均保存。任意环境变量不能提高旧120上限，批准SHA漂移失败关闭。

## 验证、载荷与版本绑定

- 本地全量**118/118通过、0skip**，105原回归全部保留；新13项覆盖表示、供体立体、E/Z、范围/O-O拒绝、通用候选保护和预算不可静默抬高。
- 无资产**112通过/6明确skip**（118总）；未声称跳过真实资产项等于源/模型验证。
- 原source-to-instance/template20文件字节重放继承；新资格/模板/动作核心**23/23文件重建字节一致**。全部来源定位/支持与真实结果SHA验证通过，286受保护输入0漂移。
- 最新Linux/Python3.10 wheel包外C搜索、默认关闭稳定字段、缺资产失败关闭通过；包不包含原始/本地数据，双副本配置一致。未执行Git提交/同步、新CI、正式benchmark、供应认证或发布。

核心入口如下，原件和派生载荷仅本地，Git保存代码/合同/报告/操作记录：

| 路径 | 职责 |
| --- | --- |
| outputs/task016-p1/v1/ | 原取得/注释/闭包冻结、r1/r2/r3与全部历史失败 |
| outputs/task016-p1/v2/qualification_manifest.json、unresolved_instances.jsonl | 最新身份撤回、93记录守恒 |
| outputs/task016-p1/v2/instances.jsonl、reaction_groups.jsonl、counting_contract.json | 当前85上下文、58总/54新反应 |
| outputs/task016-p1/v2/development_split_manifest.json、holdout_views.jsonl | 保持原面板的资格版本与隔离 |
| outputs/task016-p1/v2/templates.jsonl、template_source_manifest.json | 51可执行模板、build-only来源与SHA |
| outputs/task016-p1/v2/template_validation.jsonl、build_action_validation.json | 128支持/162边界、73实例动作 |
| outputs/task016-p1/v2/experiment_contract.json、mcts_observations.jsonl、paired_results.jsonl、action_trace.jsonl | 当前108单元的逐版本来源与36配对 |
| outputs/task016-p1/v1/run_ledger.jsonl、v2/budget_revision.json | 全216保守尝试/不可变批准修订 |
| outputs/task016-p1/v2/metrics.json、audit.json、replay.json | 可重算指标、51验收与23文件重放 |
| outputs/validation/task016-p1-package-qualified/ | 最终包外安装/搜索/默认/缺资产证据 |
| outputs/task016-p1/v2/delivery_manifest.json | 最终代码/治理/载荷/运行/原件SHA交付索引 |

| 当前绑定 | SHA-256 |
| --- | --- |
| template_source_manifest.json | a98651a5b02873d3df36f46c8a4773867d354859039a5cc84b6f1669f685a2b2 |
| qualification_manifest.json | 0f04f60b4320c58256fa0d5794704b1c6e0b4336832a9d337850e9d08a885313 |
| development_split_manifest.json | 9e6e61a4417a01e593c1f8693277bc6e2e9cf60f147c1f23a7186eaf3a667249 |
| experiment_contract.json | 697165151fb8633287831edd6dc7b2d51aaba1be5cf2023a81344266343bd00b |
| metrics.json | a7ebdfaec3916db47563c40feaaf908bd01c3c27621c5e268e5555daf27a1210 |
| audit.json | 062f172346f3f5f01340e6712616fa83a6feb63998af217d7c6fdd8dfaecac70 |
| budget_revision.json | 497b5aeca99fa6df1c72d64418b53813d898d8371f5898de14721cce90d6c3cd |

执行/复核入口：

~~~bash
python3 -B scripts/operate.py TASK-016-P1 .venv-foundation/bin/python -B -m scripts.task016_p1_verify_qualified
~~~

该入口只审计现有证据，不启动搜索。构建/来源/实验脚本的已冻结版本默认阻止覆写或重复执行；修改、重建和新的实际矩阵须新版本/明确记账，不用历史结果冒充新搜索。

## 对项目与路线的增益、未满足的更广要求

项目从4个来源精确O模板扩至51个包含C/糖间的可执行模板，并新增了批量开放取得、关键身份不充分时撤回、来源闭包分组、范围/表示边界、build-only注册表和真实动作追踪的完整机制。首次有未参与模板构建的精确目标补回证据，达到本任务数量与开发增益门槛；候选可解释且默认关闭，原审核/模型/17库存保持。

可以进入**TASK-017评测设计与准入核查**，不能直接宣称其正式执行条件已满足。TASK-017须专门解决独立标签与训练重叠、增加独立出处的迁移验证、C/糖间留出覆盖，并依据正式协议核查一手来源/模板与库存投影及所选指标的evidence定义。当前7例同一出处、4SS失败、0C留出、条件/供应/独立化学证据缺失全部保留；不自动启动TASK-017/018，不降低formal/release门槛。本报告完成的是已批准的扩库补充合同，不能据此声称“完美完成整条pipeline”。
