# REPORT-016：开放数据驱动的黄酮苷反应模板与搜索扩展

日期：2026-10-06。对应 [TASK-016 v0.2](../tasks/TASK-016-open-glycoside-expansion.md)。状态：**Completed（G1—G5 工程验收；来源实例限定的开发覆盖）**。任务范围由所有者 human_direct 批准并指示“开始执行。”；采集、解析与预算细化为 agent_delegated，没有新增 human_reviewed、独立化学 gold 或 production。

当前通用策略在冻结设置下没有提出本批 4 个完整的糖基化参照前体。新增 4 个开放来源支持的 O-糖苷成键模板，显式启用后，过滤后覆盖从 **0/4 到 4/4**；4 个目标 × 3 个 seed 的 **12/12 配对**在 B 组实际创建了参照 MCTS 动作，A 组均未创建。领域策略默认关闭。结果证明本批来源实例的计算重现和搜索接入，尚无新底物泛化或总体化学准确率结论。

## 1. 交付范围与运行基线

执行基线为 outputs/task016/v1/execution-baseline.json，保留当前 HEAD 993b22f5e8eed5797d27f02c566af1b86a4b7880、既有未提交改动及实际代码/环境指纹；HEAD 不能代替当前执行代码。Python 3.10.20、RDKit 2023.09.6；未升级运行环境。模型、解析、过滤、库存、审核与运行代码在观察成绩前冻结，见 development_runtime_binding.json。

A/B 均为 optimized MCTS，使用 task015-06-v1 adjudicated 视图和同一 17 键候选库存。TASK-015 的 P3/P4/P5、审核 manifest/index 五个绑定不变；旧构建时代码指纹保留。当前 v3、active/release、历史工作区和既有裁决未改写。

领域配置入口 configs/glycoside-expansion.json 及包内副本字节一致，default_enabled=false；请求字段 glycoside_expansion、CLI --glycoside-expansion 显式启用。父子进程校验新增来源 manifest、全部载荷/原件哈希、RDKit 版本和审核绑定；缺失或漂移明确失败。恢复本地模型、TASK-015 审核包和 TASK-016 原件/载荷后才具备运行条件；wheel 不携带这些数据。本轮没有新增 Web 启用控件或改版。

## 2. G1：自动取得来源与完整处置

全部资料通过公开 API 或官方可程序化下载取得，没有人工检索前置依赖。采用 nature-academic-search 与 nature-downloader 的开放检索/取得工作流；学术连接器在本环境不可调用，使用官方接口和 Python 下载入口。[技能检索说明](/home/ljx/.agents/skills/nature-academic-search/SKILL.md) 的本机实际位置为 /home/ljx/.agents/skills/nature-academic-search/SKILL.md；下载技能为 /home/ljx/.agents/skills/nature-downloader/SKILL.md。

| 来源与实际取得范围 | 处置与边界 |
| --- | --- |
| Rhea 冻结查询 65 条；官方方向映射 18,611 行；反应 SMILES 36,552 行 | 查询记录全部处置；批量行分别保留查询内结构来源或查询外知识，方向元数据另计。数据库知识不是具体实验。[官方 REST](https://www.rhea-db.org/help/rest-api)、[许可 CC-BY-4.0](https://www.rhea-db.org/help/license-disclaimer) |
| Europe PMC 冻结发现页 40 条；4 个直接 XML | 只有 2 篇进入本批正向实例集合；其余保留 metadata_only 或知识线索。全文和许可按件登记。[官方接口](https://europepmc.org/RestfulWebService) |
| PMC 官方开放云：2 个 XML、2 个附件 | 1 个 XML 为已有文章的另一取得版本，不增加独立来源。按官方 metadata 核许可/撤稿状态，4 个 XML/附件对象通过 MD5。[官方云入口](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/) |
| ORD 官方镜像 | revision 93475c46949f9218e1dfb6624096025135db2add 未变，复用 53 个冻结 Parquet，逐件核对 download.json 哈希；新增下载 0 字节。继承 TASK-015 已完成调查，没有宣称本轮重新扫描整个 ORD。[官方仓库](https://github.com/open-reaction-database/ord-data) |
| Zenodo 冻结结果 10 条 | 本批没有确认相关 HTE 表，全部 metadata_only；不是全网 HTE 无此类反应的结论。[官方接口](https://developers.zenodo.org/) |

新增原件 **49 件、23,996,931 字节**，低于 5 GiB 上限；24 件 raw_available，25 件 HTTP 失败响应原样保留。原件只读、Git 忽略，哈希未漂移。公开下载状态、文件角色和逐件许可见 file_dispositions.jsonl / source_catalog.json；全文/XML/PDF 不进入 Git。直接取得文章中存在 CC-BY-NC-ND 许可，但本批可执行实例的两篇种子文章均为 CC-BY，其他版本许可独立保留。

冻结查询的 115 条记录处置：61 retained_knowledge、48 metadata_only、4 linked_structure、2 source_assay_linked，差额 0。10 条附加引用/云 metadata、36,552 个 SMILES 行、18,611 个方向映射行分别对账，与查询或论文重叠不计为新实验。

具体正向产物实例 **4**，独立论文 **2**，酶/受体/供体实验上下文 **3**；两个 luteolin 产物属于同一个来源实验上下文。物理重复实验数没有抽取，保持 null。原冻结 source_manifest 的 specific_assays=4 字段实际统计产物实例；不重写已经绑定的文件，以 source_accounting.json 和本报告澄清。4 个模板只有 **1 个成键家族、3 个位点类别**，不能称 4 个独立反应家族。

## 3. G2—G3：参照、模板与来源限制

| 来源实例 | 来源酶与产物指定 | 结构证据与位点 |
| --- | --- | --- |
| PMC5818429:CsUGT76F1:O_3:61181 | quercetin 3-O-β-D-glucoside | 来源图 5D / LC-MS、参照标准；O-3 |
| PMC5818429:CsUGT76F1:O_3:69660 | kaempferol 3-O-β-D-glucoside | 来源图 5E / LC-MS、参照标准；O-3 |
| PMC5897352:OcUGT1:O_4prime:69668 | luteolin 4′-O-β-D-glucoside（1b） | 来源 NMR 指定；O-4′ |
| PMC5897352:OcUGT1:O_7:19578 | luteolin 7-O-β-D-glucoside（1c） | 来源 NMR 指定；O-7 |

酶身份、UDP-glucose 供体、产物指定和正向转化依据分别来自 [CsUGT76F1 原文](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2018.00166/full) 和 [OcUGT1 原文](https://www.nature.com/articles/s41598-018-24277-3)。机器解析保存 XML 段落定位与文本哈希；OcUGT1 附件保存 PDF 原件、官方 MD5 和 pdftotext -layout 输出。Rhea/ChEBI 提供结构表示，论文名称到具体结构的关联由 agent_delegated 注释，未经独立人工化学确认。

kaempferol 3-O 和 luteolin 4′-O 对应 Rhea 条目为水解：这里只复用化合物结构，成键方向/供体/酶来自上述独立的正向来源实验；没有机械倒转水解作为正向证据。

在看模型结果前按来源质量及固定实例 ID 冻结全部 4 个准入实例，N=4、N_support=0；未按基础模型失败挑样本。前体参照同时保留**完整受体与完整 UDP-α-D-glucose**，没有用游离糖或断键碎片替代实际供体。酶、缓冲液、溶剂作为催化/条件上下文保留；UDP/H+ 为副产物，不列为输入。比对 atom-map 清除后的 isomeric canonical SMILES 组分多重集合，保留盐、立体、同位素和重复组分。required_precursor 匹配与完整 Rhea 方程匹配分别报告。

RDKit MCS/糖图匹配建立映射与实际新成键中心；topology 只辅助定位，不单独证明可行性。模板支持实例 **4/4 精确重现**；每条模板有糖端差向异构和错误酶上下文两项声明边界对照，**8/8 拒绝，违反数 0**。边界对照是软件作用范围检查，没有把未知邻近底物当作已证明的化学负例。

v1 模板保留完整产物骨架，**仅接受已登记来源的精确结构/离子态**。Rhea 中这些结构含特定酚盐离子态；中性形式和其他底物不在适用范围。没有暗中标准化离子态以扩大命中。初始模板探针曾因电荷继承导致前体不一致，已在 SMARTS 中显式保留中性 +0 电荷后通过；失败日志/探针保留。

来源负结果另存 negative_instances.jsonl：3 个命名底物的未检出结果及 1 个面板负结果，not_detected 保持类别，产率 null；本批没有可据此填写的数值 0% 产率。正向实例也未抽取产品专属数值产率，不从动力学、活性、图中总量或培养滴度推断。

## 4. G4：独立策略与证据链

- flavoretro/open_reactions.py 处理公开取得、方向映射与正文定位；glycoside_expansion.py 负责受限模板、冻结注册表和独立 expansion/filter；task016_runs.py 负责范围内运行总账。
- contracts/cli/worker/service/workspace 仅增加显式开关、配置入口、来源绑定、总墙钟限制及结果传递；search.py 在显式诊断模式记录生成/截断/过滤/真实创建的原始 outcome index 和节点。默认行为与普通请求形状保留。
- 领域 cap=4/分子、prior=0.2、weight=1.0 在覆盖结果前固定，复用现有融合与分支预算；没有按成绩反复调参或重训模型。
- 通用动作继续原 USPTO quick-filter；酶促领域动作经已登记模板/精确目标/上下文/真实 outcome 的严格守卫、KnownHazards 和既有审核注释。明确记录 USPTO 化学 quick-filter 对该来源限定酶促动作不适用，不把其分数解释为酶可行性；未知普通动作没有获得全局放行。
- 新来源独立 task016 命名空间保存 template_source_support、exact_instance_match、prediction_conditions_verified 三轴。最后一项始终 false；来源支持不会复制为预测条件/产率/供应认证。TASK-015 的 unmatched 注释不覆盖新增来源，actionable=false、independent_chemical_validation=false。

默认关闭前后，同一普通目标/seed 的稳定输出字段一致；run ID、创建时间、代码指纹与计时等易变字段单列，见 default-off-regression.json。领域运行中原审核资产、17 键库存和旧 v3 没有扩大。

## 5. G5：冻结开发对照与指标

主矩阵：**4 个目标 × seed 0/1/2 × A/B = 24 次真实 MCTS**，12 配对。每次 quick 单阶段 12 秒、20 迭代、120 节点、12 分支、深度 2；全部 phase 总墙钟硬上限 60 秒。模型候选 cutoff=12/通用策略，融合分支上限 12；“未观察到”只针对该设置，不是模型绝对不能提出。

| 指标 | 实际结果与分母 |
| --- | --- |
| 过滤后精确参照覆盖 C_A / C_B | 0/4 → 4/4 |
| 可判定缺口 N_gap、补回 G / N_gap | 4；4/4 |
| 参照覆盖净变化、参照损失 | +100 个百分点；0 |
| 基础未知/错误、增强单步错误 | 0/4；0/4 |
| 实际 MCTS 补回配对 | 12/12，4 个不同目标 |
| seed=0 / 1 / 2 | 各 4/4 补回，损失各 0 |
| 新领域真实创建动作 | 12 条根动作，有实际节点及 outcome index；来源完整率 100% |
| 24 次主运行失败/超时 | 0 / 0 |
| B−A 平均墙钟 / 节点差 | +0.4151 秒 / +1.4167 节点 |
| evidence_closed / actionable | 0；false，路线为 partial/surrogate |
| 支持步骤 N_support / M_support | 0 / 0，未估计支持步骤覆盖 |

O 成键分母 4，C 成键和糖—糖成键分母均 0；后两类覆盖率为未估计，不填 0% 或 100%。训练重叠 unknown，全部实例 development_exposed，没有盲测、独立化学准确率或供应可执行路线结论。

候选集合也发生变化：过滤后按“同一目标 + 完整前体签名”去重，B 比 A **新增 4 个动作、减少 8 个其他动作**；这些减少发生在融合截断阶段，生成阶段原通用动作都仍在。参照覆盖损失 0 并不意味着保留了所有通用候选。当前新增权重会占用固定分支预算，其他候选的价值未经化学确认，见 candidate_accounting.json。

| 目标顺序（与上表实例一致） | 生成阶段独立动作 A/B | 截断后 A/B | 过滤后 A/B | 过滤后新增/减少 |
| --- | --- | --- | --- | --- |
| quercetin 3-O | 21/22 | 9/7 | 9/7 | 1/3 |
| kaempferol 3-O | 23/24 | 7/8 | 5/6 | 1/0 |
| luteolin 4′-O | 22/23 | 14/11 | 14/11 | 1/4 |
| luteolin 7-O | 26/27 | 10/10 | 10/10 | 1/1 |

这里是独立动作签名数；一个模板可产生多个 outcome，不能与原始模板/trace 行数混用。单步生成、过滤、墙钟的 B−A 平均分别为 +0.00694、+0.00089、+0.17802 秒，属于本机小样本工程计时。

总账 conservatively 预留 **33/120** 次服务尝试并全部结束：**31 次实际成功 MCTS**（24 主对照、前后默认 2、领域探针 1、已有回归 2、包外验证 2），另外 2 次为合成的服务错误/超时测试 fixture，无实际树搜索。主运行与实际 MCTS 没有失败；fixture 错误不计为化学失败。最大墙钟 **5.21965 秒 < 60 秒**。缺资产在树搜索前失败的检查及纯单步诊断/重建不算实际 MCTS。逐次 ID、purpose、状态、预算和原始结果见 run_ledger.jsonl / mcts_observations.jsonl / paired_results.jsonl；没有挑 seed、删失败或重复凑目标数。

## 6. 验证与保留的失败

| 验证 | 结果与证据 |
| --- | --- |
| 全量本地测试 | 105/105 通过（既有 95 + 新增 10）；operations/command-0788.log |
| 无本地资产环境 | 105 项发现，99 通过、6 个明确跳过；asset-free-regression-v2.json/.log |
| 同原件重建 | 11 个核心实例/模板/配置文件逐字节一致；replay.json；不重新抓取网络，不覆盖已绑定 v1 文件 |
| 安装包与包外运行 | Linux/Python 3.10 wheel 隔离构建和安装，仓库 cwd 外通用/领域真实搜索成功，领域动作创建 1；缺资产明确失败；outputs/validation/task016-package/report.json。未做 sdist 或发布 |
| 来源/预算/实际动作审计 | audit.json 全部检查通过；174 个既有保护文件、35 个执行保护依赖零漂移，49 原件与 53 ORD 文件哈希一致；来源/模板/实际动作追溯 100% |
| 最终治理验收 | final-governance-validation.json：文档链接、git diff --check、冻结输入/代码绑定及数据 Git 边界；按最终产物记录 |

首次无资产 harness 在临时 cwd 中运行，使既有测试中显式 repo-relative triage 配置无法找到，留下 15 errors/6 skips。修正 harness 为“空外部 workspace + 保留仓库 cwd”，应用代码未因此修改；原失败日志和 asset-free-first-attempt.json 保留。审计首跑因每行重复哈希大文件而停止，保留 -15 日志，缓存一次哈希后通过；不消耗 MCTS 次数。下载失败、初次 S3 scheme 解析失败和模板电荷探针失败均保留。

## 7. 缺口与下一步边界

本批 **C 成键可执行模板=0、糖—糖成键可执行模板=0、HTE 准入表=0**。取得的 C-糖苷论文是全细胞多步合成，保留为 pathway evidence，不伪造孤立单步模板或把培养滴度当产率。Montbretin 糖间延伸论文在本次 Europe PMC 取得失败，官方云冻结查询也没有可取对象，保留 unavailable；这不等于论文或整个公开来源不存在。

当前第一版优先实现可审计、来源限定的 O 成键动作。进一步扩展需明确处理**中性/离子态等价规则、新底物适用证据、C/糖间成键来源以及固定预算内通用候选取舍**，再冻结新版分母；不能从本轮 4/4 自动推断转移能力。本任务没有启动 TASK-017/018、正式盲测、供应准入或发布，也没有提交/推送 Git；已有未提交改动保留。科学门仍为 research_candidate，formal_run_ready/release_ready=false。

## 8. 可核查产物与重放入口

最终本地载荷根：outputs/task016/v1/；原件根：data/raw/task016/。各来源失败与记录处置、负结果、参考、生成/过滤/实际创建日志、逐次运行、成本与计数均在这些目录。delivery_manifest.json 给出全部最终载荷及代码/脚本/文档 SHA-256；下列关键文件可逐件核验。

| 文件（相对本地载荷根） | SHA-256 |
| --- | --- |
| execution-baseline.json | d333ca6b2d43c14d4a1401a042b11e028d105b99512d89d49fee37f245fb7e57 |
| source_manifest.json | 0b5c32d0371029fa9cb9d244f0813af7b6472308c4a2854a3849741901e67edf |
| instances.jsonl | 19c89c564d11f63c0eaa4917e49b064fcfbe79e3de1750482aa41c80c3cf2fd1 |
| development_contract.json | 1d5186f3a08ecd3c196f12a83af3654b05d3ce9309c7c540e392cb2d5eee2454 |
| development_runtime_binding.json | 9f50271c7847676dbd419f4dc3d0597a659946776d4814fcbee76e8260ae25b0 |
| reference_precursors.jsonl | e7818994186e50e06565b7adbb9772a07509113a02ae4dba633925844e06c9f1 |
| baseline_observations.jsonl | c2b1aaad5cffa57cc9c9c473f1af710c43988bf9aaaca825eb4b3fd590f3d31f |
| gap_register.jsonl | 924169630b9d53a050754d74c1ae5f3640c1acef51cde6613c9340bab1f2f168 |
| templates.jsonl | a86e0b43d195198f08086cc4fc05870181b9434855f5f9c4c956a8b0deebcbaa |
| template_validation.jsonl | 48c5c13de2ad615f062a2a38ca0d0cd4dc6c1cf61ae570021dfdf2eca5f3cf4f |
| template_source_manifest.json | a47523992eb006c3ffe22c204e492e7a8470786d8bbec6613c7d57e49f087471 |
| mcts_execution_contract.json | 6e422c28d338ce2ec76aeba2e14ab84a619bbc0cf85b781e178405f547f66857 |
| paired_results.jsonl | 93e5ee5ec3137e6d833f6197252a994c77b038c82fdf68941a7935dd44f34d6e |
| metrics.json | c19ba2d3d036041dd915140e7b9f362e2f59021f3f97ffd62d4ec4356eb6a63f |
| audit.json | fb1bafbe38fbb5dd705064680d7edf0bc5507c84e935979754b262b6c52db757 |
| replay.json | 28bab3797a553f1e9ff143a710a8ed1fcd34789c2369098a3823f15e9a804abb |
| candidate_accounting.json | 973e88d826ccd4160a77e066e27f254bdfc8ffa75c6b9f54a3b696e8c15e5df5 |

源码入口：scripts/task016_acquire.py、task016_pmc_cloud.py、task016_build.py、task016_diagnose.py、task016_evaluate.py、task016_replay.py、task016_asset_free_check.py、task016_package_check.py、task016_verify.py。所有项目命令/写入和实现细化经 scripts/operate.py 记入 operations/events.jsonl 与 command-*.log。构建和主矩阵脚本对冻结文件采用不覆盖守卫；本轮不重复跑实验。

不消耗 MCTS 预算的同原件重建命令：

~~~bash
python3 -B scripts/operate.py TASK-016 .venv-foundation/bin/python -B scripts/task016_replay.py
~~~

后续经授权运行 CLI 时，在登记的精确目标与本地资产就绪前提下使用 --glycoside-expansion；不启用则保持原默认搜索。新的开发矩阵必须用新版本目录，记录总账与实验合同，不覆盖本次 24 次观测。
