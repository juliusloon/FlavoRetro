# REPORT-017：v0.2 执行、科研准备与独立审核交接

- 日期：2026-10-13（Asia/Shanghai）；对应 [TASK-017 v0.2](../tasks/TASK-017-independent-c-ss-transfer-benchmark.md)。
- 所有者指令：“根据修订后内容，执行task17”；执行批准 agent_delegated，human_reviewed=false。原批准合同 SHA：13a9463c476d548ba9bbec135f17a6c659bd6e52cd6b436c9bf674b4592d7868。
- 独立标签审核负责人：**ljx**，由所有者本会话回答“ljx”实际指定；原文保存在 reviewer_nomination.json，工程代录保留溯源。指定角色尚未产生独立标签。
- 整体 **Partial；execution_status=awaiting_independent_review_input；有效状态 AWAITING_INDEPENDENT_INPUT**。
- 事实源：outputs/evaluation/formal-task017-v2/；v0.1 G0及v0.2修订交付与报告只读保留。

## 本轮实际结果

真实任务内科研检查为 **profile=task017_research、preparation_ready=true、research_run_ready=false**。准备门允许 metadata/合成工程工作；科研门仍缺实际panel、独立标签、逐项一手参考与来源闭包、最终协议/调度冻结。全局来源/供应unresolved、production=0未阻止准备；旧formal_run_ready=false与release_ready=false保持。

本轮完成已交付方法冻结、科研准入/冻结/执行/复算入口及必要合成验证、一轮固定metadata发现、历史曝光元数据初筛和ljx无预填gold交接包。**正式科学cell=0，实际模型推理/MCTS=0，C/SS效果及迁移指标null**。真实run入口在调用search之前拒绝了缺证矩阵，拒绝与日志SHA留档。

当前缺的是ljx提供的合法结构/逐项原始反应依据及真实独立审核，和这些材料对应的闭包/协议冻结；已有执行授权继续有效，不重复索取批准。未启动新的reader/epoch循环，不追加检索轮次，不声称全球来源穷尽。

## 阶段及交付

| 阶段 | 实际状态 |
| --- | --- |
| G0 | v0.2批准快照、累计预算、保护与方法/来源/角色计划已登记；真实preparation门通过 |
| G1 | A/B/E及参数先于新metadata冻结；科研代码/合成验证和metadata接收完成；原文/结构内容尚未接收 |
| G2 | 实际panel/独立标签/逐项参考、来源与曝光闭包、最终协议待真实输入；未冻结科学分母 |
| G3 | 执行器合成核验完成；实际research门false，正式放行未发生 |
| G4 | 未启动，未注册或尝试任何科学cell |
| G5 | 仅本轮准备/缺口报告与状态登记；未产生科学结果汇总 |

| 文件 | 实际职责 |
| --- | --- |
| flavoretro/formal_evaluation.py | 准备/科研分层检查；实际文件、SHA、结构/组件重数/立体、独立审核原件、source闭包与开发重合、最终协议及执行证明关系检查；冻结、单次矩阵、真实结果解析和配对汇总 |
| scripts/task017_formal.py | freeze/check/run/verify CLI；run重新核验科研门，不调旧12-cell compare |
| tests/test_task017_formal.py | 37个合成合同测试；不生成真实gold或科学证据 |
| v2本地事实源 | approval、method、plan、metadata原响应/失败、候选/初筛、审核提名、空白审核包、测试证明、真实research_check、run拒绝、预算/输入/保护/终验 |
| handoff/README.md | ljx的48条来源队列、prior处置限制、所需结构/证据字段与无标签模板 |

代码没有修改搜索算法、已冻结方法、原配置、旧evaluation.preflight/CLI/API、release或P7/P9科学账。新模块由既有包发现机制收录；当前只在本地固定Linux/Python环境验证，未新跑安装/CI或Git同步。

## 检索与曝光边界

使用 nature-academic-search 技能的检索/去重工作流；专用academic MCP工具未挂载，按合同采用公开Europe PMC/Crossref书目API。先登记C6+SS6共12条固定查询、渠道、范围、每条最多8结果、按规范化DOI/来源ID哈希排序；方法在发现前已冻结。

结果：**12查询，6个200成功响应、6个503失败响应；连同2个服务检查共14 HTTP尝试，29,316字节metadata，去重48条书目候选。** 服务检查中另有1个404，全部原响应/失败保留。失败不退款、不换词、不启动第二轮。没有摘要/全文/图片/结构/附件接收或解释；新原始文章/附件为0。预计候选和标题中的检索轴都不计真实target/化学标签。

历史初筛只读既存治理metadata：104条永久曝光投影、1789条中央曝光事件、5204条prior v4记录及4条真实曝光补记。对限定身份字段做DOI/PMCID token比对，48条中2条命中既存prior记录；prior命中不自动等同肯定科学曝光，逐项处置仍待完成。其余46条未命中也不证明fresh。全项目来源/家族/assay闭包、别名和具体反应/同产品排除尚未完成，**合格独立目标C0/SS0、组0/0**。

交接包只包含题名/DOI、原始查询出处、prior状态与空白decisions；没有给ljx模型建议、臂排名、搜索候选或预填gold。旧R80、Liu2021/R73和epoch锁保持；未读取这些具名科学内容。

## 方法、检查与运行约束

A=generic，B=既有v3（54模板/85上下文），E=既有v6（继承B加2模板/4上下文，组成56/89）。模型/审核/17候选库存及方法代码/配置SHA沿既存资产重新绑定；参数为合同固定的optimized/quick单phase、30s、100 iterations、depth6、branch12、nodes2000、top_k5、seed0/1/2。未训练、调参、构建新scope或以test改变方法。

checker分别输出preparation_ready/research_run_ready、实际输入SHA、逐项错误、非阻断资源状态和旧门。实际缺失文件明确记false，未用目录存在、非零计数或approved字段替代文件/结构/审核原件关系。protocol review须与实际协议/panel/labels SHA及审核者原件对应；label决策须与真实审核原件中的结构/参考对应。source closure按实际图边传递分组，核对开发库存原件、精确产品/反应、未知和曝光。

run入口要求真实科研门true，并拒绝旧TASK016账环境、已尝试矩阵及重复cell；每cell先预留再调用共享service新进程。冻结输入/方法/验证代码漂移拒绝运行。结果解析验证request/result/manifest/资源/模型/代码绑定，仅完整参考多重集合的真实created节点计命中；候选/截断/过滤trace与成本完整保留。错误、外部超时与未运行保留null和登记分母；来源组bootstrap仅在合同条件满足时执行。

本轮只验证合成逻辑与实际缺证拒绝。尚未以真实独立panel完成正常矩阵，不能声称整个G3/G4端到端科学验收通过。旧能力证据是否可继承仍须绑定实际最终科学输入/代码，必要的旧17×3回归尚未执行。

## 验证与预算

- 新37项合同测试全部通过；实际结构化测试报告及代码SHA见 implementation_validation.json、synthetic_validation.json。
- 既有16项输入/运行合同全部通过；其中2次mock worker错误/超时按工程尝试计账，实际MCTS为0。不是科学负结果。
- 原有旧门的兼容字段/行为与准备/科研分离已核验；缺标签、协议、闭包、SHA漂移、test回流、分母变化、组件重数及候选冒充节点均覆盖。
- 本轮保护基线 827 个限定文件；最终直接SHA检查见verification.json，包含v1/修订原件、已冻结方法、release及旧治理账。不宣称全量历史原始件重验。
- 累计上限继承：120命令、12查询、120 HTTP/512MiB、24文章/48附件、120结构化文件/200MiB、270科学/51旧回归/24工程/345总尝试；不因v2重置。
- 实际来源消耗12查询/14 HTTP/29,316字节metadata，文章/附件/科学均0；工程错误fixture2，总尝试2。保守登记累计 83 文件、26,375,809 字节，治理阅读/完整性扫描及非累计OS读取界限见input_manifest。最终命令游标/累计数见budget_accounting.json。

记录一项本轮工程审计纠错：保存测试runner时的日志定位误匹配当前准备命令，首次执行只更新预算；错误脚本和日志保留，纠正选择条件后实际重新运行37项测试并绑定最终代码。没有伪称首次runner完成了测试，也没有科学结果受影响。终验还抓出ARCHITECTURE旧状态未被首轮替换，已修正并保留失败核验。探索缺路径、HTTP503/404及真实run拒绝返回码均据实保留；拒绝不计科学搜索尝试。

## AC与继续条件

| 验收 | 本轮判定 |
| --- | --- |
| AC01 | 授权、累计预算、方法/输入/保护及旧历史保全完成；最终科研输入绑定仍待G2 |
| AC02–03 | 真实最低panel/独立gold/全项目闭包未完成；仅审核负责人及隔离交接已落实 |
| AC04 | 臂、方法和参数已冻结；科学panel与主分母尚未生成 |
| AC05 | 不满足：实际research_run_ready=false |
| AC06–07 | 未执行真实科学矩阵；仅执行器/解析/缺失规则合成验证通过 |
| AC08 | 按实报告null、未执行和来源局限；科学效果待测 |
| AC09 | 本轮保护SHA核验；正式旧能力/独立性验收尚未完成 |
| AC10 | 本轮准备范围报告/STATE/manifest/空cell账一致；整个科研评价尚未完成 |

下一步是ljx依据handoff固定来源队列提供合法完整结构、逐项一手定位和实际独立审核结论；完成prior/闭包排除后形成C/SS各至少6目标/2组，核验旧能力及最终协议，再冻结一次矩阵。原执行授权有效，改变方法/来源路线/预算/门槛仍须明确合同修订。当前没有实际输入可继续生产gold或科学运行，因此保持一个待真实输入状态，不派生自动恢复队列。
