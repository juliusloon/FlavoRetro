# TASK-014 独立标注与科学评测协议 v1

本协议为 TASK-015—018 的接管依据，方案执行已由所有者在 TASK-014 以 human_direct 批准。它冻结字段、单位、分工及防泄漏约束；并未产生人工标签，也未批准正式 benchmark。TASK-015 须在自己的合同中确定审核者、最终数量、入选来源和日程；TASK-017 才冻结完整盲测合同。

## 人机分工

机器负责结构化、批量去重、领域线索、来源定位和审核排序。人负责定义领域边界、核对具体实例、处理方向/位点/立体/产率归属等高影响歧义、核查一手来源，并对筛选误收/漏检作校准。agent 提供候选与定位材料，不以工程授权填写 human_reviewed。

源事实核验、领域相关性、结构正确性、模板准入、供应证据是不同轴；不得使用一个 approved 状态覆盖所有轴。建议以追加审核记录实现，不重写 v3。

## 标注单位与必需字段

记录主键为 input_record.id；保留 source_path/source_sha256/locator、具体来源实例与原始 reactant/product。通式、Markush、机器枚举和多产物反应必须显式标记，不能按枚举数计“独立实验实例”。

| 字段轴 | 允许标签/信息 | 规则 |
| --- | --- | --- |
| domain_relevance | relevant / supporting_step / out_of_scope / uncertain | unknown 和真实负例分开；保护操作可为 supporting_step |
| transformation_labels | 总分类 ID 的列表；uncertain | 多标签、记录证据；不得从 legacy classification 自动继承 |
| glycoside_connection | O / C / sugar_sugar / other / none / uncertain；位点/糖身份 | 分别记录底物与产物；区别拓扑存在和该步键变化 |
| specific_experimental_instance | true / false / uncertain | 指定 scheme/example/table 行号；通式不等于实例 |
| reactant_product_confirmed | true / false / uncertain | 方向、参与物完整性、取代模式、多产物、映射/反应中心分别核对 |
| conditions_yield_assignment | assigned / absent / ambiguous / not_checked | 收率 0 为真实数值；缺失/未报告/未归属不能混为一谈 |
| stereo_status | confirmed / unspecified_in_source / conflicting / not_checked | 不补猜绝对构型或异构体比例 |
| primary_source_locator | DOI/专利号 + SI/正文 + 页码/图表/实例 | 引文字符串和来源文件定位并非审核通过 |
| evidence_excerpt、primary_source_sha256 | 合法证据定位与本地来源哈希 | 本地受限内容不上 Git；无法取原文须保留 unavailable |
| reviewer_id、reviewed_at | 实际审核者与 ISO 日期 | 机器产生文件的日期不是人工审核日期 |
| decision、disagreement | retain_candidate / reject_claim / primary_checked / needs_adjudication | 人的分歧追加保存；否决也不删除原始候选 |

审核包 review.jsonl 的 annotation 字段初始全 null，human_review_status=not_performed，production_eligible=false。机器建议在独立命名的 machine_suggestion 下，仅用于开发校准。正式独立标注包须隐藏 machine_suggestion、分数、队列和自动分类，防止锚定偏差；本轮包不冒充盲标界面。

## 首轮审核设计

本轮导出至多 60 条开发样本，以精确反应组去重后抽选代表来源：

| 互斥抽样层 | 计划名额 |
| --- | ---: |
| 已有 guide 模式支持的领域糖苷候选 | 15 |
| guide 未覆盖的领域糖苷候选 | 15 |
| guide 未覆盖的其他领域候选 | 10 |
| guide 支持的其他领域候选 | 10 |
| 低优先级/当前未知对照 | 5 |
| 解析不完整/失败/泛化对照 | 5 |

先把不完整行归入最后一层，避免重复算名额。各层用固定哈希顺序选取，记录可用数、名额、实际数和短缺，不以重复记录或推测标签补齐。至少 30 条糖苷重点样本的可实现性由实际数据验证。首轮任务可由一人进行开发校准；用于独立 gold 的记录建议两名审核者分别标注，再由第三人/所有者裁决分歧，身份与角色在 TASK-015 实名登记。

这是固定配额的校准样本，非概率抽样。不能用 60 条的简单平均准确率代表 2,301 条或整个化学空间。后续若估计总体准确率，须另设计各层内概率抽样、保存 inclusion_probability 并使用相应加权估计；或者完整审核冻结评测集合。

## 数据角色与隔离

当前 508 条 guide 和 2,301 条试点记录全部为 development_exposed；本任务没有创建任何 blind/test 记录。未来人审可以形成可信开发 gold，但不能因为换一个审核者就把已参与规则开发的数据变成未见盲测。

预留盲测必须来自事先留出的独立来源/具体实例，且在调规则、选参数或查看运行成绩前冻结。不允许把失败样本事后移出分母。每次数据角色变化须有版本、理由、批准和哈希。

防泄漏检查按连通分组执行：同一论文/DOI、专利及家族、同一笔记文件、同一通式父记录及变体、精确标准化反应，共享任一键的记录不能跨开发和盲测；关联是传递的，不能只逐对检查。当前 leakage-groups.json 用可用 DOI/专利号/规范化标题及引用线索、笔记文件和父 ID、精确结构组保守分组，所有组均为 development_exposed。

标题/引用归一只是分组线索；文献身份和专利家族尚未人工解析。缺一手身份或 unresolved 分组键的记录不得自动进入盲测。未来对同一骨架/近邻反应的独立性，须明确是 interpolation 还是 scaffold-held-out，不笼统称为“完全独立”。

本项目使用 USPTO/ringbreaker 模型；新引入的 USPTO/专利数据可能与模型训练数据重叠。没有模型训练清单或可核查分割时必须标记 training_overlap_unknown，不能声称训练集独立，且不能用新下载日期证明化学实例是新数据。

## 分开评价三类问题

### A. 领域筛选

比较结构基线和 guide 辅助排序；同一输入、标准化/去重策略和固定 top-K。事前指定 K（建议 20/60/100）以及以“精确反应组”还是“来源记录”为分母。当前运行保存来源记录排序；后续 group-level 指标须选择每组最高排名的代表，防止重复导出抬高命中数。

有独立完整相关性标签后才能计算 precision@K、reviewed relevance rate；recall 需要独立定义且足够完整的相关反应分母。只审核 top-K 不能估计全局 recall。guide 外发现数、队列大小、重复率、解析状态、审核耗时是流程指标，不是化学正确率。类别 precision/recall 需固定多标签规则及 uncertain 的分母处理，不能把 uncertain 算负例。

### B. 糖苷拓扑

在独立确认的分子/连接子集中，以实际键、O/C 类别及位点为单位分别报告 precision/recall；图往返成功不是真阳性。该协议区分“连接存在”和“该反应生成/断裂连接”，后者需要核验反应中心与具体实例。

### C. MCTS 搜索

TASK-016 受控接入后，再以 target × engine/policy × seed 作为运行单元。当前 native/optimized 没有严格等价节点上限；未来冻结时间预算、迭代预算及各自节点实际用量，不能用节点上限名称相同宣称等价。

同一目标/seed 的引擎对照为配对数据，路线条数和 seed 重复不是独立目标样本。协议须预注册主要指标、次要指标、目标 panel、seed 数、预算、资产/代码/配置哈希、失败/超时分母、置信区间方法及比较规则；不在看完结果后挑最优 seed。

闭合率分别统计 partial、surrogate candidate-stock closure 与 evidence_closed。只有逐步骤/末端证据满足定义才可报告证据闭合；当前 candidate 命中不是可合成证明。可另列 explored depth、不同路线数和运行成本，但不得替代独立化学评价。

冻结结果后，按目标分层/聚类重采样估计不确定性，保留 seed 内相关性；分类样本量不足时只报告观察与区间，不作泛化/优越性结论。最终 power/样本量与统计方法由实际 TASK-015 gold 分布及 TASK-017 合同确定，本任务不伪造功效分析。

## 正式准入依赖

现有 evaluation.preflight 要求 primary_source_review=approved、current_vendor_evidence=approved、independent_chemical_labels=available、evaluation_protocol_review=approved，以及非零、独立审核的 production template/stock 投影。TASK-014 不修改上述元数据，formal_run_ready/release_ready 继续 false。

TASK-015 负责独立标签和对应来源审核；供应核验、模板/库存准入须在明确人工授权的资源任务中完成，不因有 gold 自动通过。TASK-016 仅在定义/协议和糖苷信息满足要求后受控接入。TASK-017 在全部 preflight 条件满足并由所有者批准后才允许冻结/执行正式 benchmark；当前只定义方法，不启动正式执行器。

## 版本与停止规则

规则修改必须在开发集进行，形成 v2 并保留 v1；盲测启动后不能反向调整指标/入选标准。泄漏、原始结构漂移、来源身份未解、人工分歧未裁决、许可不足或正式门槛未闭合均须记录并停止相关准入；不通过改写状态或删除失败关闭缺口。
