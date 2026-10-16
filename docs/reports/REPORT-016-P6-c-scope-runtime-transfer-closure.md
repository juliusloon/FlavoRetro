# REPORT-016-P6：C scope 修复、可执行留出与 C/SS 迁移终验

## 对应任务

- 任务：[TASK-016-P6](../tasks/TASK-016-P6-c-scope-runtime-transfer-closure.md)，原合同 SHA `8dac36d0d201192bf8edb4856c9550666e8081b734244bb5fad7555662b4d574`。
- 日期：2026-10-07；执行者：Cano；所有者明确批准执行，批准与阶段决定记 `agent_delegated`，实际人工审核未发生。
- 状态：**Partial，本轮按合同停止条件完成执行收口；C/SS 新底物迁移未验收。**
- 基线：工作区 `/home/ljx/FlavoRetro`，Git HEAD `993b22f5e8eed5797d27f02c566af1b86a4b7880`；继承现有未提交改动，以 G0 哈希快照判定本次差异。
- 事实源：`outputs/task016-p6/v1/`；原件：`data/raw/task016-p6/2026-10-07/`；均本地保留，不进入 Git。
- 结果提交：无；未 commit/push/tag/release，未运行远端 CI。

## 实际结果

P5 的确把精确实例模板当成 scope；P6 已恢复 `derive_template_smarts → scoped_smarts → 范围元数据／守卫 → 全部构建支持重放 → 边界 → 冻结`，第二个构建支持通过。还发现旧 P5 helper 的两种受体各多一个氧，P6 从正确的冻结受体及来源明确的 C8／β-D-Glc 图重新编码，未沿用错误 helper 生成科学对象。

C 旧计数 7 个目标中最终有 **6 个完整可执行目标、4 个闭包组**，面板完整性及隔离通过；化学 Stille 目标 P3R-C12 的完整保护糖基锡前体未编码，保留为 deferred，不计入分母，也未用 UDP-Glc 替换真实化学前体。冻结的 flavonol C8 scope 在这 6 个留出上产生完整参照 **0/6、0 组**，因此触发 **C 停止条件 6：`scope_holdout_domain_mismatch`**。这是正确范围与留出母核／位点不匹配的结果，未定义为模型迁移失败。

SS 旧 4 个计数目标进一步核对后只有 **1 个完整隔离目标、1 个闭包组**：两个来自次级评论并连到已有构建闭包；一个供体／连接标签错误且实际反应连到构建闭包；另一个修正为 Glc 1→6 后保留。两条定向闭环路径仍未解决 ≥6/≥2 门槛，触发 **SS 停止条件 1**。C 与 SS 分轴判定，未以 SS 失败阻止 C 判定。

| 验收轴 | 状态 | 冻结证据 |
| --- | --- | --- |
| P5 错误对账 | Completed | 旧精确 probe 第一支持 raw outcomes=2、第二=0；缺失 scoped_smarts；额外氧错误单独保留 |
| C scope 实现 | Completed | 2 个不同完整受体，2/2 支持；6 个边界控制，0 违反 |
| C 可执行面板 | Completed | 6 目标／4 组，100% 完整，deferred/inferred=0，反应／闭包泄漏=0 |
| C 新底物迁移 | NotExecuted | 冻结 applicability=0/6／0 组，C 停止条件 6；科学指标 null |
| SS 可执行面板 | Partial | 1 目标／1 组；旧标签、次级来源和共享反应闭包完成纠正 |
| SS 新底物迁移 | NotExecuted | SS 停止条件 1；科学指标 null |
| 旧能力回归 | Completed | 最终 v6 上旧 17×3=51 单元；SS4/4、C5/5、O7/7，无新增损失；旧1b仍未创建 |
| 工程交付 | Completed | 正式增量重放4/4；包外 C 构建真实节点2/2；177本地测试、无资产147通过/30跳过；26项终验零失败 |

## 对合同 17 个问题的直接回答

1. **P5-ERR-06 是否独立复现？** 是。旧 helper 与旧 `derive_template_smarts` 路径重跑，精确左侧33原子，第一支持有2个原始结果且参照匹配，第二支持0个结果。旧“C scope 不泛化”判断被 P6 reconciliation 明确 superseded，P1–P5 历史文件未回写。
2. **完整流水线是什么？** `derive_template_smarts` 产生精确实例；在映射后的精确左侧原子顺序上重新绑定糖片段／端基／受体位点，再实际调用冻结 P3 `scoped_smarts`；加 flavonol 母核、C8、完整 UDP-Glc、糖立体与守恒守卫；2/2构建重放与6个边界通过后，先冻结 scope，后读取留出。
3. **两个 SMARTS SHA？** 精确：`6a883c8c728e127c3e8e136ac8110ed11c684f3b5a9c87105ae51a10ae03108b`；scope：`23e7d89c1ddde5e2a8ebb761658af417efa8251da084b3e8d736f9c6d28cbb49`。整个 `c_scope_template.json` 文件 SHA：`a740ed20ac738f20434eecae9a569803d06b7a1a3027e9a87b67597e4db3f662`。SMARTS 内容 SHA 与 JSON 文件 SHA 分开记录。
4. **全部 C 构建支持通过？** 2/2。P3R-C05/C06 均来自 PMC9700910，正确完整受体分别为 kaempferol／quercetin；来源约束编码与实际守卫通过。
5. **第二个支持是否通过？** 是，作为永久 canary；正式 v6 加载、生成、过滤也通过。安装后的 seed0 真实 MCTS 实际创建该完整参照节点。
6. **旧7个 C 计数目标有几个可运行？** 6；4个闭包组。P3R-C03/C04、P4R-C01/C04、P5R-C01/C02进入最终分母；P3R-C12完整化学供体前体未完成，剔出分母并保留。
7. **正确 scope 对几个 holdout 产生参照？** 0/6，0组。目标是 C6 flavone、benzophenone C3 和 gallic-acid C2；冻结 scope 为 flavonol C8。6个可执行完整参照全部做静态 probe，未修改面板／scope。
8. **没有运行 C A/B/E 的确切原因？** C停止条件6：完整参照可产生目标少于3个／2组；原因码 `scope_holdout_domain_mismatch`。支持重放和面板完整性已经通过，故不归为实现失败、面板失败或模型迁移失败。
9. **C A/B/E 多少 cells？** 0。静态 probe 不算 MCTS；51个旧回归与工程构建探针不算新迁移矩阵。
10. **C 科学指标？** `N=6`；`N_gap/G/G_over_N_gap/net_coverage_vs_A/net_coverage_vs_B/reference_loss` 全部 `null`，原因是前置门停止且A/B/E未执行。实际静态匹配数0与未运行指标null严格分开。
11. **真实三-seed C node-transfer 几个？** `null`，未执行。安装构建探针2/2属于 `exact_seed_instance_match=true` 的实例重现，未计迁移成功。
12. **SS 如何从4/6处理？** 未恢复为6。P3R-SS08/09为次级评论对应已有主研究构建闭包而排除；SS12供体应为UDP-apiose、O2β-D-apiose，并因同源apiin完整反应连接构建闭包而排除；SS22应为UDP-Glc、Glc1→6，完成完整图编码后保留。路径A未取得独立两受体O2-Rha构建闭包；路径B未取得足够完整独立留出，最终1/1。未声称来源已经穷尽。
13. **SS A/B/E执行？** 0 cells，停止条件1；全部迁移指标null。
14. **最终 v6 旧17×3回归？** 已执行51次，均正常完成；旧4SS、5C、7O的三种子参照动作均保留，旧1b继续按历史定义单列。以冻结P3结果逐目标比较，新增参照损失0。
15. **哪些结果被 supersede？** G0错误schema读取造成的假漂移；G1孤立糖自由基丢端基手性导致的首版失败；把UDP磷中心当成糖碳手性缺失的首版面板；缺少历史P3/P4无资产跳过声明的首轮隔离测试；标题实体／期刊别名的初始假身份不匹配以及未显式展示出版年卷期对照的初始元数据快照。全部保留并有替代绑定；没有科学A/B/E矩阵被后验重跑或择失败cell重跑。
16. **结论级别？** C scope 实现、来源约束构建实例重现、可执行面板工程与历史能力保持完成；没有 development heldout transfer 结论。C是scope／panel domain mismatch，SS是panel shortage；不是预测失败率估计。
17. **更高科学门？** 新底物候选迁移、三种子新节点迁移、训练集独立性、正式blind/gold benchmark、独立化学／实验可行性、预测条件、真实供应、production、formal_run_ready/release_ready 均未关闭。新增对象 `human_reviewed/actionable/evidence_closed/prediction_conditions_verified=false`。

## 来源、结构及闭包纠正

C产品图来自原文结构图与明确连接／立体信息：PMC6036675 Figure1的C6结构及糖椅式图，PMC11480083 Figure2c的苯甲酮C3图，PMC8841362 Figure2A的maclurin，PMC11053098 Figure1A的两种没食子酸C2图。实际下载、查看8个结构／立体图件，保存图件SHA、位置及编码来源绑定；完整UDP供体与冻结来源受体身份沿用来源链。没有按名称／PubChem替代图／执行者记忆补复杂结构。P3R-C12继续保留受限于完整化学参照编码的缺口。

SS三处关键原文：

- [PMC10602597](https://pmc.ncbi.nlm.nih.gov/articles/PMC10602597/)是关于Yamashita工作的评论；对应[主研究PMC10602602](https://pmc.ncbi.nlm.nih.gov/articles/PMC10602602/)已经在v3构建集合，不计独立主证据。
- [PMC13140228](https://pmc.ncbi.nlm.nih.gov/articles/PMC13140228/)的astragalin反应是apiosylation，有NMR支持；同文还报告与既有主研究相同的完整apigenin7Glc→apiin反应，因此闭包连接到build。保留2025电子刊出／2026印刷出版两个年份，未把年份差异当成新来源。
- [PMC12120870](https://pmc.ncbi.nlm.nih.gov/articles/PMC12120870/)是β-(1,6) oligoglucoside研究，astragalin产物对应标准品，供体为UDP-glucose；原SS22的Rha/O2标签错误。其正确完整结构留在评估侧，不进入runtime。
- 有界补查[PMC4282749](https://pmc.ncbi.nlm.nih.gov/articles/PMC4282749/)的UGT79B6是Glc O2，不是Rha O2；完整kaempferol3Glc参照与既有v3构建反应重合，未据标题恢复SS分母。

8条Europe PMC检索与1条Crossref检索保留580个去重PMCID discovery hints，仅选定继承原始来源及相关酶学标题进行有界审查，另做1篇UGT79B6补查。最终30篇原件的PMCID／标题／DOI／期刊身份已核，出版年份／卷期30/30交叉核对；标题HTML实体及期刊副标题以权威ISSN对齐，原值保留。初始版本已保存出版元数据，显式年卷期对照结果在终验时补齐，无资格或分母变化。元数据核验不等于逐篇化学准入；完整反应身份、结构、反应重复及source/reaction closure另做判定。

治理HTTP账本实际 **128 请求、9,357,618字节、21新全文版本＋9复用版本、8图件请求**，均低于3000请求／4GiB／200版本／360附件。所有请求包括重复元数据请求保留、不冲销。网页工具仅作discovery提示，其内部传输量不可计量，未假称上述HTTP账本覆盖网页工具内部成本；没有来源穷尽结论。

## 改动文件

| 所在目录及职责 | 文件 | 实际改动与用途 |
| --- | --- | --- |
| C范围和门判定 | `flavoretro/glycoside_scope.py` | C8母核／位点／完整糖立体／守恒守卫；运行结构完整性、面板泄漏、分轴preflight及真实节点判定 |
| 独立v6运行版本 | `flavoretro/glycoside_library_v6.py` | 从合格v3建立v6，合格P4 SS O2与P6 C8增量；来源绑定、范围guard、正式生成及过滤 |
| 请求和运行接线 | `cli.py/contracts.py/worker.py/service.py/workspace.py/task016_runs.py` | 新增显式v6版本，保持默认关闭；P6独立哈希批准／用途／总额与分用途账本门 |
| checkout／包配置 | 两份`glycoside-library-v6.json` | 完全一致，绑定v6 manifest；缺载荷或哈希漂移拒绝加载 |
| 分阶段治理脚本 | `scripts/task016_p6_*.py` | G0纠错保护、C exact→scope、结构面板、静态probe、定向来源、SS纠正、v6构建、旧17×3、无资产／安装／独立终验 |
| 永久合同回归 | `tests/test_task016_p6.py` | 26项，包含合同要求22项；23纯fixture合同＋3本地资产合同，第二构建支持canary永久保留 |
| 治理文档 | 本TASK、本REPORT、STATE、ARCHITECTURE及导航 | 按冻结事实标Partial、独立停止理由、null指标、下一步缺口；旧TASK/REPORT不回写 |
| 本地原件／产物 | `data/raw/task016-p6/`、`outputs/task016-p6/v1/` | 元数据／XML／结构图／sha、精确和scope、面板／闭包、预算、逐cell实际trace、metrics／audit／delivery；Git忽略 |
| 本地安装／隔离验证 | `outputs/validation/task016-p6-package/`及两份asset-free快照 | wheel/sdist、仓库外安装与真实构建节点、无资产失败首轮与修正后完整合同测试 |

v6=合格v3（54模板85实例）＋P4 SS O2（1模板2实例）＋P6 C8（1模板2实例）＝**56模板89实例**。v6本轮增量payload只有2模板4构建实例；holdout不进入实例库。C3与Rha1→6被隔离范围在构造层排除。显式opt-in、cap4／prior0.2／weight1／通用前三保护继承前序冻结值。未改模型、PUCT、库存、通用评分或科学门槛。v1—v5旧模块／配置哈希保持；旧v5服务绑定行为未另作范围外修复。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| `operate.py TASK-016-P6 … -m unittest tests.test_task016_p6 -v` | 26通过，合同要求22/22存在；永久ERR06三项保护未删除 |
| `operate.py TASK-016-P6 env … -m unittest discover -s tests -v` | 177通过、0跳过；日志`operations/command-1333.log` |
| `task016_p6_asset_free.py`修正后隔离完整suite | 177发现，147通过，30显式跳过，0失败/错误；20历史P3/P4资产项＋原有10项自然资产跳过；23项P6纯合同全运行 |
| `task016_p6_package.py` | wheel＋sdist不含raw/outputs；仓库外默认结果稳定字段相同；缺载荷fail closed；配置副本一致；安装v6对两C构建目标真实参照节点2/2，均为exact build重现 |
| `task016_p6_regression.py --run` | 51旧E臂真实MCTS，0执行错误；4SS/5C/7O三seed均保持，旧1b历史未创建，新损失0 |
| `task016_p6_verify.py` | 26项检查0失败：exact/scope独立重建、增量payload字节重建、冻结probe重算、完整性／泄漏、源SHA、模型／审核／stock绑定、预算、包与flags |
| 保护完整性 | 继承P5保护3221文件0漂移，P6保护3410文件0漂移；冻结v3 manifest `e17bff4c1b891fe8164e8f62bec21e54527a5662adf466548c5898fdb069da88`未变，stock仍17键，review仍task015-06-v1 |
| `operate.py TASK-016-P6 git diff --check` | 通过；文档最终收口后再执行并绑定最终交付清单 |

独立搜索账本 **62/480**：旧回归51/51，工程11/54，C0/81、SS0/81、重验0/213。实际成功MCTS **56**，实际MCTS失败0；额外6个是三次完整suite中明确mock的服务错误／超时fixture，保守占预算，原始账本保留并另表绑定，不把它们算真实搜索失败。没有借用P5预算。

精确／scope及增量payload从冻结构建支持独立重建一致，probe重算完全一致。`runtime_baseline.json`是初建快照，首次真实矩阵前完成接线修正；最终代码指纹以`experiment_contract.json`和`runtime_baseline_final.json`为准，所有51回归及安装检查使用该最终代码，未发生需要重跑整矩阵的后续运行实现变更。

## 与任务合同的偏差

未取得新底物迁移完成证据；按合同自身停止条件6及SS停止条件1合法停止，未降低目标数、组数或迁移阈值。最终C为允许窗口内6个，而非起点7个；SS不是简单4→6补2个，真实性复核先把错误计数纠正到1个，故保持Partial。v6工程构建和旧回归在科学前置门停止后仍完成，用于消除P5未建成正式runtime的缺口，不抵偿迁移门。科学A/B/E入口未启动，不生成虚构cell。

本轮5个自发现问题全部记录于`self_caught_errors.json`与`supersession_ledger.jsonl`：G0假漂移、G1端基手性、磷中心误判、无资产runner遗漏资产跳过、元数据规范化与出版字段核对缺显式结果。错误probe／面板／验证快照全部保留。G1与面板修正发生在实际留出applicability前；无scope／reference／参数后验调优，无模型矩阵被只挑失败cell重跑。

## 已发现但未修改的问题与遗留风险

当前C冻结scope是flavonol C8，而独立现有留出是其他母核／位点；完整留出数达标不等于对该scope可测。不得把守卫放宽以制造正结果，也不得在看probe后把build实例挪入holdout。SS仍缺独立、完整、适用于冻结范围的原始反应证据。P3R-C12的化学保护糖基锡供体图需要完整来源编码；次级评论与跨论文相同完整反应必须继续闭包合并。

图转写和来源复核是agent_delegated，未经新的所有者化学复核或独立实验；原文支持强度与运行验证分开。30篇身份核验、56次真实MCTS或2/2构建节点重现均不提供训练独立、blind benchmark、预测条件、供应或实验成功率证据。当前局限适用于Linux/Python3.10环境，安装验证不是发布认证。

## 仓库与 CI 状态

所有项目内命令及写入经`operate.py`；现有未提交工作区保留，旧`retro_synthesis`与`CondRxnBench`未写入。v1—v5历史科学载荷、TASK/REPORT与原件保持，操作日志追加；仅本P6合同／报告及当前状态导航更新。未暂存原始或受限数据、未提交／推送／tag／release，未新跑远端CI；Git diff检查不等于远端CI。

## 建议的下一任务

本轮应先审核两个具体科学构造缺口：**C source-qualified scope与独立完整留出能否形成至少3目标／2闭包组的可测关系；SS能否取得适用于冻结范围、完整身份且与构建闭包独立的6目标／2组。** 后续任务继承P6已交付scope、guard、v6、26项合同回归及17×3结果，仅在科学资产实际变化时按合同重验受影响矩阵。不得再次把已完成工程门当作待建任务，也不得自动启动TASK-017或调模型追成绩。后续改变科学scope／面板需新合同授权。
