# REPORT-017：v0.2科研准入合同修订

- 日期：2026-10-13（Asia/Shanghai）
- 范围：合同与治理记录；修订交付Completed，TASK-017正式评价仍Partial。
- 批准：所有者在具体准入拆分方案后指示“修订。”；agent_delegated，human_reviewed=false。
- 合同：[TASK-017 v0.2](../tasks/TASK-017-independent-c-ss-transfer-benchmark.md)。
- 长期决定：[ADR-007](../adr/ADR-007-research-evaluation-admission.md)；细化ADR-006的正式前置责任。

## 修订解决的问题

v0.1把全局一手来源/供应、非零production投影与研究方法评价统一阻断；又要求任务准备阶段先具备其本应产出的独立标签/面板。修订分开preparation_ready、research_run_ready和供应/production/发布资格，不改变独立评价的真实证据要求。

| 范围 | v0.2合同要求 |
| --- | --- |
| 评价准备 | 执行/版本/预算、方法/工程资产、合法有界来源计划、角色与隔离交接；允许标签和panel待产出 |
| 正式科研运行 | 真实最低panel、独立标签/一手参考、来源与曝光闭包、冻结协议/方法/参数/代码/模型/审核/17库存、执行器验证及预算全部通过 |
| 供应/production/发布 | 保留各自认证和治理规则，不再阻挡本轮方法迁移测量，也不由科研结果自动晋级 |
| 旧preflight | 保留evaluation.preflight及CLI/API原语义和行为，v0.1真实formal_run_ready=false保留 |
| 审核记录 | 绑定实际协议版本/SHA、范围、时间、权限与依据；合同批准不伪造最终panel/标签审核完成 |
| 预算与证据 | 沿用累计上限；v0.1事实源只读，后续实际执行另用v2，不回写历史 |

§2 A/B/E、§4.3独立标签规则、G4矩阵/参数及§6指标/统计已与修订前逐字比较保持一致。C/SS各至少6目标/2组，固定分母、错误null和有效零/负结果可完成评价的规则保持。预算容量不增加；P7的Partial/stopped、曝光和旧epoch不变。

## 当前实际状态

- v0.2合同修订：已批准并登记；既有TASK-017执行授权继续有效。
- execution_status=not_resumed_after_v0_2_revision。
- 科研检查、执行器及其测试：未实现，不能宣称实际准入已通过。
- preparation_ready=null、research_run_ready=null；panel_ready=false、evaluation_complete=false。
- c_effect_pass=ss_effect_pass=null；新科学读取、查询、HTTP、模板构建、标签生产、搜索/模型/MCTS运行均0。
- metadata/release.json及所有运行代码保持，release_ready=false。
- [原G0停止报告](REPORT-017-independent-c-ss-transfer-benchmark.md)和outputs/evaluation/formal-task017-v1/全部只读保留；本修订报告不替代或改写原停止。
- outputs/evaluation/formal-task017-v2/尚未创建；本次审计位于outputs/evaluation/task017-v02-revision-20261013/，不是科学结果。

## 验证与操作预算

保护集合898个现存文件SHA核对无漂移，含原G0事实源/报告、既有方法与配置、release、旧P7/P9及历史协议/ADR。原G0继承保护检查也无漂移。已核对本次变更链接、当前状态、授权边界、未来产物未生成和文档空白格式；本轮仅文档变更，未运行模型或新增工程测试。

本次修订operate命令5次，失败0。按原执行起始游标累计：TASK-017=17次、后续只读核对TASK-017-REVIEW=3次、本轮TASK-017-V02=5次，另继承5次已声明未逐次留痕引导命令；合计30/120（含本次最终核验），不因版本重置。新查询/HTTP/科学/工程搜索额度未动用。精确日志游标和保护/交付SHA见本地verification、budget_carry_forward及delivery_manifest。

原批准合同、审批历史、真实检查失败和本轮修订批准分别可追溯；未把agent_delegated冒充human_reviewed，未执行Git暂存/提交/推送或对外发布。

## 后续顺序

在既有执行授权下依v0.2新G0合并预算、冻结实际方法与保护边界，登记合法来源和真实角色交接；先用合成fixture实现科研检查/正式执行器，按G1/G2准备独立panel与真实标签/协议。G3必须获得任务范围内真实research_run_ready=true，才可启动一次G4矩阵。

此处未预判最低面板可以取得或方法会有正增益。缺真实审核角色、结构/参考或独立性证据仍按阶段停止；任务修订Completed不等于TASK-017评价Completed。
