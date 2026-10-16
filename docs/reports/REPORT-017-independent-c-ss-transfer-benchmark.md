# REPORT-017：C/SS 正式独立迁移评价 G0 执行与停止报告

- 对应合同：[TASK-017](../tasks/TASK-017-independent-c-ss-transfer-benchmark.md)，批准版本 v0.1；2026-10-13（Asia/Shanghai）。
- 整体状态：**Partial；execution_status=stopped_at_G0**。G0 有界核验已完成，G0 门未通过；正式评价未完成。
- 所有者执行指令：“开始执行 task 17”。本会话自主审批记录 **agent_delegated，human_reviewed=false**；已有执行批准有效，不需要重复批准同一执行范围。
- 原批准合同 SHA256：036c4448f84cda2329b111345e5249688817bca60fe15e185f5498ffda356f09；原文与批准保存在本地 approved_task.md、approval.json。
- 本地事实源：outputs/evaluation/formal-task017-v1/。本报告是实际 G0 核验及停止报告，不是正式效果报告。

## 本轮结论

真实运行现有 flavoretro.evaluation.preflight 后，**formal_run_ready=false，release_ready=false**。一手来源、供应、独立标签、科学协议审核及 production 资源投影均未满足现有门。没有可登记的本轮上游关闭安排，也没有实际独立标签审核者和已接收的独立来源批次。

按合同 §4.1、G0、§8 停止条件①/③停止正式路径，未继续读新科学原文/结构、检索或生成标签，未实现 G3 执行器或运行科学矩阵。此次 TASK 执行授权已经落实；其不能替代独立标签、供应或 production 的真实证据。

**本轮效果不可评价。** C/SS 的 N_gap、G、G/N_gap、E−A、E−B、reference loss、三 seed 迁移与 bootstrap 区间全部 null；正式科学 cell、模型推理及 MCTS 尝试均为 0。这不是有效零效果、迁移失败或全球来源穷尽。

## 阶段及实际交付

| 阶段 | 本轮状态 | 证据 |
| --- | --- | --- |
| G0 执行授权与保护 | 批准/保护/真实前置核验完成；gate_pass=false | approval、execution_baseline、protected_hashes、preflight 及 provenance |
| G0 责任/来源可达性 | 未就绪；无具名独立审核者，无可验证的双轴 6/2 路径 | roles、dependency_matrix、source_access_plan |
| G1 方法冻结/来源接收 | not_started；只有现存资产完整性绑定，未完成评价方法冻结 | asset_bindings |
| G2 panel/独立标签/协议 | not_started；未登记任何合格 target/reference | stop_decision、cell_ledger |
| G3 执行器/正式放行 | not_started；formal_evaluation.py、task017_formal.py 及其测试未实现 | 停止发生在其前置阶段 |
| G4 一次矩阵 | not_started；registered_cells=attempts=0 | cell_ledger |
| G5 效果核对与结案 | 仅完成停止报告及当前状态登记；正式汇总未发生 | 本报告、STATE、verification、delivery_manifest |

本地同时交付 input_manifest、inherited_integrity、isolation_status、audit_corrections、budget_accounting 与文档变更差异。所有原始/受限数据及本地载荷保持 Git 忽略；没有提交或推送。只修改本任务文档与当前导航，不修改方法、运行代码、配置、release 或旧科学账。

## 正式依赖的实际核验

执行命令通过 scripts/operate.py 留痕：env PYTHONDONTWRITEBYTECODE=1 .venv-foundation/bin/python -B -m flavoretro.evaluation。原输出、命令日志 SHA 和 command_end 事件绑定到 preflight_provenance.json；没有 mock 或改写 preflight。

| 依赖 | 实际 | 要求/责任边界 |
| --- | --- | --- |
| 工程资源 | assets_verified=true；v3 共 3,059 记录 | 工程可用，不替代科学资格 |
| primary_source_review | unresolved | 有权限上游须提供真实审核及证据 |
| current_vendor_evidence | unresolved | 有权限上游须提供真实当前供应证据；本任务不代认证 |
| independent_chemical_labels | not_available | 待实名负责人按所有者亲核或真实独立双源流程产生 |
| evaluation_protocol_review | 字段缺失；preflight 解释为 unresolved | TASK 执行已获批准；科学协议实审凭据尚未登记，不能只改字段 |
| production template/stock | 0 / 0 | 必须有非零独立 source-reviewed 投影；晋级不在本任务认证权限内 |

两个合同入口 data/inbox/task017-independent/、data/inbox/scifinder/task017-blind/ 均不存在，未创建空目录假装已经接收。没有已冻结的公开出版方/API来源批次或候选 ID；未假定账号、专利 API 或合法机构访问已经可用。

上游依赖已足以触发 G0 停止，因此新发现查询为 0，12 条查询名册尚未激活，未把旧预注册查询或 P7 恢复许可复用为本轮科学读取许可。C/SS 合格独立目标和组均为 0，分别仍缺至少 6 目标/2 组；这些是本轮已准入数量，不是对世界可用文献的计数。

独立审核者/双源核验者实名均为 null；Cano 只担任工程执行者，没有预填 gold，也没有启动新代理读取 test。H5/G7 及专利别名闭包未修复，曝光未清除；没有把旧对象重新标为 fresh 或 blind。

## 现存方法与保护绑定

| 臂/资产 | G0 实际核验 | 边界 |
| --- | --- | --- |
| A | 固定 generic 定义；当前代码/配置 SHA 留档 | 未在新 test 上运行 |
| B | P2/v2 manifest SHA e17bff4c1b891fe8164e8f62bec21e54527a5662adf466548c5898fdb069da88；54 模板/85 上下文 | v3 的来源绑定开发方法 |
| E | P6 manifest SHA 210ed717dffaa7f6bcdac45ecfd21fe9bb9c6ab81eeb2aa0ef799a92a6bff874；独立增量 2/4，继承 B 后 56/89 | 核验父 SHA 与 ID 无重合；未新增或重建方法 |
| 模型/通用模板 | metadata 中 5 个 external_model 资产 SHA 全部匹配（3 ONNX、2 模板表） | 只做完整性核对，未模型推理 |
| 审核/库存 | task015-06-v1 manifest 及其 payload SHA 匹配；17 候选库存键 | 不认证供应或 production |

绑定来源、SHA、计数和配置政策保存在 asset_bindings.json。JSONL 只抽取 ID/计数检查继承，不进行化学编码或 gold 裁决。v3 原依赖字节哈希也已核验；原件只校验完整性，不阅读或解释新的科学内容。

本轮保护基线 778 个现存文件；P9 继承的 667 个限定不可变文件 SHA 检查无漂移。保护包括现存代码/配置、活动资源、绑定载荷、具名 P7 关闭/epoch/曝光/运行账，以及 P9 和 TASK-017 起草交付。最终再次核验结果见 verification.json；这是限定保护范围，不宣称全部历史原始件均复核。

P7 保持 Partial/stopped，旧 epoch、曝光和原指标未改；TASK-016 方法及有限开发阶段 Completed 保持。训练重叠继续 unknown。未重跑旧 17×3 科学回归，也未把历史工程证据当作本轮完整 AC09 验收。

## 验收、预算与偏差

| 验收 | 本轮结果 |
| --- | --- |
| AC01 | 执行批准、合同原文、现存资产/保护/上限绑定完成；独立评价输入及完整正式绑定未发生 |
| AC02–03 | 不满足：无双轴最低独立面板及真实独立标签/审核角色 |
| AC04 | 臂与比较定义继承合同，G1/G2 正式冻结未完成 |
| AC05 | 不满足：真实 formal_run_ready=false |
| AC06–07 | 未执行；无正式逐 cell 结果或效果汇总 |
| AC08 | 已如实报告停止、null 及主张边界；尚无有效效果结论 |
| AC09 | 本轮限定保护无漂移；正式旧能力检查及独立性终验未完成 |
| AC10 | 已交付本次停止范围的报告/STATE/manifest/空账核对；不代表整个科学验收完成 |

因此 AC01–AC10 未全部满足，TASK 整体不能记 Completed。registered_count=attempted_count=0，不将预算容量 270 当成已经登记的分母。

原批准上限保持：命令 120、查询 12、HTTP 120/512MiB、24 文章/48 附件、结构化输入 120 文件/200MiB、正式 cell 270、旧回归 51、工程运行 24、全部运行 345。来源、科学、回归和工程搜索消耗均为 0。G0 登记的 37 份既存输入共 3,926,592 字节，完整性扫描与规范/代码/日志阅读单独说明，不冒充新科学数据读取；未对科学内容做新解析。最终操作游标、命令数及预算核对见 budget_accounting.json。

记录一项本轮自发现错误 TASK017-G0-ERR01：初版将 E 的增量文件计数误要求为完整 56/89，断言失败。保留失败日志和初版脚本，依据既存 v6 合成实现修正为父 v3 54/85 加增量 2/4，并核验 ID 无重合。未改变方法、面板、门槛或科学结论。两次探索命令的缺路径返回码也保留在操作账，不作为成功检查。操作入口加载前 5 次只读引导命令未逐次留痕，已在 approval/budget 据实登记并计入 120 上限，不回填虚假运行日志。

仅新增文档和本地治理产物，没有新增运行代码，因此未重跑整套工程测试或科学回归。实际验证为原有 preflight、资产 SHA/继承检查、停止状态及文档/账本/忽略规则一致性检查。

## 继续所需的具体输入

1. 有权限的上游提供一手来源、当前供应及非零 production template/stock 投影的真实证据与具名关闭安排；本 TASK 不代认证，也不自动创建上游任务。
2. 登记实际独立标签负责人及裁决流程，给出合法固定来源批次与 C/SS 每轴至少 6 目标/2 组的可核对可达性；按冻结顺序接收，不靠旧对象漂白。
3. 实际完成科学协议审核及隔离/别名闭包核验，再以原门重跑 G0。已有 TASK-017 执行批准继续有效；若改变来源路线、方法、范围或门槛，须明确修订合同。

没有上述证据时，本轮保持一个有效状态 G0_STOPPED，不派生 reader/epoch 恢复循环；后续 TASK-018 未启动。
