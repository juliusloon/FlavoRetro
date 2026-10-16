# REPORT-015-06：审核结果如何进入搜索

任务合同：[TASK-015-06](../tasks/TASK-015-06-review-into-search.md)。**Completed（2026-10-05）**。所有者逐项确认D1–D4；按本次用户提供的AGENTS自主审批授权登记整体工程批准 `agent_delegated`。实际人审、代理审核、机器筛选的原始身份分别保留，新增虚构人审0。

## 结果与实际行为

普通CLI/API搜索现在默认读取冻结审核视图，再使用候选库存与生成反应。审核视图实际影响资源准入、严格实例证据关联、逐步/末端/资源展示及导出与运行指纹；模型动作概率、PUCT、路线评分及搜索预算配置原样保持。

- 覆盖3,059条v3原资源的外置审核查询状态；原始records/SQLite/active/release不改。
- 库存按原许可与裁决取交集：49库存中45保留编码候选、4错配隔离；原许可17个键，实际仍17个键。4错配在原v3已禁用，零库存变化符合真实基线，不以此宣称搜索覆盖增益。
- 原文支持9、明确数值产率支持6、结构/分类53开发gold+7排除分别保留。反应索引有1,880个完整结构签名，包含未知/被排除的来源上下文；它不是1,880个可执行模板或独立化学验证。
- 8次冻结开发比较全部成功，4个目标×种子配对的route_id/score/steps/closure/evidence_closed/actionable均相同；真实返回路线中原文支持步骤命中0。9个参考实例查询均严格命中其索引，不能把参考查询结果冒充9个模型生成步骤。
- native共享审核库存准入验证成功；候选库存关闭路径在2次既有live回归及1次包外live中成功。合计12次真实MCTS，达到预登记上限，未扩跑。
- 当前精确供应认证仍0；evidence_closed/actionable/production/formal/release不晋级，未执行独立盲测、TASK-016或Git提交/推送。

## 审核结果如何进入搜索：已有成果的实际接管

| 已有成果 | 实际读取/转换 | 搜索落点 |
| --- | --- | --- |
| P1/P2审核线索与导出材料 | 从P3/P5冻结结论保留已有来源定位、原件哈希、原文与数据库转录差别；本次未重新下载或核读论文/SI | 具体实例证据与原审核溯源，未加载为新策略/库存 |
| P3 53结构/分类开发gold、7排除 | `assemble()`读取P5所绑定的逐卡结构结论及原审核记录；P3 manifest/载荷逐件校验 | 严格结构反应命中后提供结构轴标签；7排除不贡献正面支持，不全局禁用其分子/家族 |
| P4 2,301条处置 | 固定task015-p4-v2，逐record_id读取queue；3黑名单/53不完整/16路径嫌疑撤销该出处的正面支持资格 | `ReviewView.reaction()`保留记录处置；其他独立出处分别判断。没有把机器筛选变成通用化学过滤器 |
| P5 60卡来源/产率、9/6子集 | 完整两侧组分多重集合、方向、立体、同位素、盐及实际outcome严格匹配 | `ReviewedEvidence.apply()`在真实候选过滤链关联metadata；`worker.annotate()`标注最终路线。只关联参考实例，不预测本次条件/产率 |
| P5 508笔记 | 保留242原位置一致、1再定位、7解析失败、258未验证；7解析失败不进入精确签名集合 | 笔记一致性作为独立轴，正面原文支持false；未匹配/未验证均可见 |
| P5 2组/4个FGM名称 | 显式映射FGM-0003/0155到molecule，FGM-0014/0156到molecule_duplicate_names | narirutin别名显示规范名称并保留双方ID；两UDP身份声明隔离，不替换分子图 |
| P5 49库存/2模板身份 | record_id/ref/完整结构校验，按原运行许可与最终决定取交集 | `CandidateStock`真实加载17个允许键；错误对应即使试图将原flag改True仍被审核规则阻止。2本地模板未启用 |
| P5 49供应裁决、22历史上下文 | stock_ref到具体记录关联，当前精确供应false，历史/内部/错配/母体替代分别保留 | 原料卡、资源查询和JSON提供供应轴。候选闭合仍为surrogate，无采购或实验可执行认证 |

计数存在包含/交叉，不能相加作为独立反应或来源量。9/6来自既有P5证据子集，本轮没有生成新的独立科学标签。

## 实现与运行绑定

- [reviewed_resources.py](../../flavoretro/reviewed_resources.py)：冻结输入manifest/载荷校验、显式关联、不可变构建、反应/库存查询、运行版本核验。历史manifest中的code sha保留为当时provenance，新运行另记当前代码hash；不会要求新worker等于旧审核构建时worker。
- [policies.py](../../flavoretro/policies.py)：CandidateStock消费审核交集；ReviewedEvidence按实际reaction.index关联实例，保留原policy_probability与过滤语义。
- [worker.py](../../flavoretro/worker.py)：每个phase前后验证同一审核绑定，动作/叶子传递审核，保持原closure/score及科学字段；原unreviewed_candidate_stock兼容字段保留，具体审核轴在新增review中表达。
- [service.py](../../flavoretro/service.py)：父进程固定绑定、保存review-binding.json并传给子进程；成功/失败manifest及错误结果保存实际或预期绑定，缺资产明确报错。
- [web.py](../../flavoretro/web.py)与[app.js](../../web/app.js)：只读资源原件另附审核层；逐步/末端、历史与下载保留版本。旧运行没有审核字段时明确显示，未回写旧文件。
- 必要样式仅修复新增审核详情的窄屏换行；参考产率、数据库值、方法、不确定度与实例位置语义化展示，完整原值保留于JSON。包副本与源文件一致。

活动审核资源（本地Git忽略）：`outputs/review/task015-06/v1/`。配置入口为`configs/search.json.reviewed_resources`，打包副本一致。只有明确的开发验证环境标记能使用legacy_validation视图，缺资产/错hash不静默回退。

| 指纹 | 值 |
| --- | --- |
| schema / version | 1 / task015-06-v1 |
| manifest SHA-256 | 1e8ea3c461ac3ff88ee4d6bad3385aa832881d65bb682ff7467d64014c15f8ec |
| index SHA-256 | 55f15016571500b00dcd86b9bbf8484c23c0527c33afaa4e6b89d572e86ae06c |
| base resource | v3（原active/records/SQLite不改） |
| default mode | adjudicated |

严格签名清除atom-map标号，使用RDKit2023.09.6的isomeric canonical SMILES，组分排序但不去重/去盐/中和/互变归并。多产物或仅产物/家族/子结构相似不贡献原文支持；未严格匹配仍为候选。条件与产率在source_instance层，不能复制为预测值。

## 验证与实际证据

| 检查 | 结果与产物 |
| --- | --- |
| 全量回归 | 本地全量95项通过（既有82+新增13），包含2次真实live MCTS；后续仅调整两项测试fixture，受影响16项本地复核通过。最终无资产全量89通过、6明确跳过；无新增真实MCTS |
| 新合同重点 | 隔离不能重启、独立同图有效来源保留、原许可交集/库存关闭、错误join、零/立体/同位素/盐/重复组分/方向/多产物、实际outcome、错误schema/hash/中途绑定漂移、未知轴与legacy显式标记 |
| 构建重放 | v1/replay-v1的index/summary/README/manifest共4文件逐字节一致；没有网络重新获取 |
| 输入/原件保护 | 初查181文件0漂移；必要无资产测试fixture修订单独记录原/新hash后，最终180受保护文件0漂移；含123已准入本地源件、v3/index、active/release、原所有者提交、P3/P4/P5、search/triage/topology/evaluation等保护对象。不是全历史目录的新审计 |
| 配置/算法 | 去除新增reviewed_resources配置后与HEAD原search配置一致；search.py原hash不变；固定4配对的稳定路线字段一致 |
| 真实开发核验 | 2目标×2seeds×2视图=8，加native1、回归2、安装live1，共12；0比较失败、0真实原文匹配，正负与零结果保留于runtime/integrity JSON |
| 实例索引核验 | 9原文支持实例各自严格查询成功；6数值产率及>99%、38/38.11、87/86.96、92/91.9±5.2/HPLC原值保持；这是参考查询，不是新生成候选 |
| 浏览器 | 1440×1000、390×844共20组检查通过，JS错误0、四页与展开详情无横向溢出；实际资源API隔离可见，搜索/实例/历史/错误显示使用明确BROWSER TEST ONLY fixture，不构成人审或真实搜索命中 |
| 导出/历史 | 下载result审核绑定与页面一致；历史无字段明确提示；未改历史run文件 |
| 包外安装 | 初始新wheel在隔离target安装后真实MCTS成功，审核绑定正确；缺资产错误manifest保留；最终界面修复后刷新wheel资产，16个运行代码文件与已live验证安装完全一致，最终资产与checkout一致，额外MCTS0 |
| 最终资产检查 | UI修复后3项包资源检查通过，JS语法检查通过；最终wheel只含代码/包资源，不含本地审核载荷 |

主要本地证据：`outputs/validation/task015-06-plan.json`、`task015-06-runtime.json`、`task015-06-integrity.json`（含原基线与测试fixture例外）、`task015-06-browser-v4/report.json`、`task015-06-package/report.json`与`task015-06-package-v2/report.json`。全部保留本地，不提交Git。

最终wheel：`outputs/validation/task015-06-package-v2/dist/flavoretro-0.1.0-py3-none-any.whl`；仅供本地工程验证，不是发布。

### 失败与修复记录

- 首轮构建发现排除卡的structure_gold=null，按缺省轴保留而不伪造空gold；失败日志保留。
- 名称关联首次只覆盖molecule，未覆盖两条molecule_duplicate_names；按原FGM ID、locator和冻结图显式修复，无模糊名称匹配。
- 直接脚本调用误取到旧安装包而缺新模块；新验证脚本显式使用本checkout。包外验证仍以独立安装路径执行，未混用checkout作为安装证据。
- 两次浏览器等待未先等最终资源刷新并打开详情，保留失败日志/partial报告；修复验证时序。
- 无资产全量首次有2项旧worker故障测试提前触发review_assets_error；仅为这两项mock测试提供合成审核绑定，原timeout/engine_error断言与正式加载规则不变。最终89通过、6skip；没有真实MCTS追加。
- v3浏览器实测手机长字段溢出；限定新增审核区域换行并改成语义字段展示，v4全过。v1–v3失败截图与日志保留，不删除。

## 后续与限制

TASK-015-06工程接管已完成；TASK-016尚未启动，可以绑定上述version/manifest/index hash与17库存准入基线，再从G1推进。未来新增模板或资源视图必须生成新版本并记录来源/适用范围，不能覆盖本v1。

真实路线原文命中0是本次预算和目标下的观测，不证明模型绝对不能生成这些步骤。当前供应0、独立标签/盲测不足继续保留；已采纳的审核结论不再交回所有者重复填表。没有Git提交/推送、远端CI、正式评测或公开发布。
