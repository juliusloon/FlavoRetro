# REPORT-016-P9：现有数据可测性盘点与开发评价重设计

## 对应任务与结果

- 任务：[TASK-016-P9](../tasks/TASK-016-P9-development-evaluation-redesign.md)。
- 状态：**Completed（规划交付完成，2026-10-13）**；D0–D4完成。
- 授权：所有者本会话“批准执行”；批准记录agent_delegated，human_reviewed=false。
- 原批准合同SHA：74c23372e1eac57ad19a941cab50d16345145801c4ec3964921a91ed1daf9ebe；原文及批准见本地outputs/task016-p9/v1/approved_task.md、approval.json。
- 基线：outputs/task016-p9/v1/execution_baseline.json；分支main，HEAD 993b22f5e8eed5797d27f02c566af1b86a4b7880；无新提交。

**现有数据可支持历史目标的描述性开发评价，但本轮没有证实可执行的同范围来源留组折。** 主要瓶颈是范围支持集中在单组，而非简单“反应总条数不足”。P9已完成盘点与预登记，不表示TASK-016科学目标完成。

P7保持Partial/stopped；P2 development effect未验收。独立确认、TASK-017/018和正式/供应/发布资格未放行。没有新增fresh、没有新科学结果，也不声称全球来源穷尽或迁移失败。

## 改动文件与职责

| 文件/目录 | 实际交付 |
| --- | --- |
| scripts/task016_p9_plan.py | 一个离线盘点辅助脚本；只用标准库和RDKit读取allowlist，不加载运行时、模型或网络 |
| outputs/task016-p9/v1/ | 本地批准/输入/保护基线、逐对象处置、去重盘点、27个范围、分组、12折计划、56资产逐折动作、预登记、决定、复算与交付清单 |
| 本报告及TASK-016-P9 | 当前执行结果、验收与修订历史 |
| STATE、任务/报告/文档索引、两份Roadmap | 仅登记P9的当前完成状态和限制 |

本地结构化载荷、旧版审查产物和化学明细不入Git。ARCHITECTURE及原有代码/配置/历史科学治理文件未修改。原有大量未提交交付不被本轮覆盖。

## 输入闸门与继承裁定

精确allowlist为34个既存文件；读取累计8,798,293 bytes（含最终输入SHA校验），包含本轮重复读取/复算，不按文件唯一大小掩盖预算。内容预算200MiB、文件上限120；命令执行总数及审计游标见verification.json，未超过40。

优先采用P1/P2最终合格机器载荷与P4/P6纠偏及支持记录。P4混合表只按既有34个最终重审ID定位、对其中24个已准入ID解码；10个deferred行保持不解码，未知ID立即停止。表整体字节读取已计预算；未打开原文、图片或PDF。

P3旧混合表、P5新反应表和P7 prospective/角色内容均未作为补读队列。P5汇总计数与说明存在矛盾；本轮保留矛盾，不以该汇总新增准入。P5两个C完整对象仅采用后续P6已冻结编码。

SS08/09继承P6一手/闭包排除，SS12旧身份被纠正但与build闭包重合，SS22采用P6纠正的1→6完整引用。未重新审原文或翻转科学裁定。Liu2021/R73内容停止、R80停止、H5/G7缺口继续有效。

## 盘点结论

| 轴 | 去重上下文 | 精确编码反应 | 不同产品target | 不同canonical受体 | 本地已知闭包/分割组 | 机器检查完整 | 既有runtime成员 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C | 13 | 13 | 13 | 11 | 7/7 | 13 | 7 |
| SS | 21 | 19 | 19 | 18 | 5/5 | 21 | 20 |
| O参照 | 62 | 37 | 37 | 23 | 8/8 | 62 | 62 |

191条结构交付出现记录去重为96个上下文，另处置P4的34条最终重审状态。出现记录逐行标明保留/重复及最终代表指针；不同版本不相加。仅以既有规范化签名及已编码图做相等性归一，不补图或引入新的化学准入。

机器检查不等于runtime验证。显式runtime_executable=true仅继承C6个对象；C其余7、SS21、O62个未声明，保持unknown。已有runtime成员与该显式字段分开。完整reference检查包含现存acceptor和显式donor一致性，不施加模板或生成候选。

P4状态仍有C4、SS10条已准入但未机器编码；新增target数unknown，不能直接加14。其ID/证据指针和C4/SS6 deferred、纠偏/排除均保留在record_dispositions.jsonl。所有96个上下文的全项目source/assay闭包尚未核验完整；表内7/5/8只表示本地已知连通分量，不能当作已确认独立组。

六维分层共27个范围，缺失core/site/sugar/donor/mode逐对象标not_serialized。完整表及每折剩余支持见measurability.md与measurability_by_stratum.json；没有依靠新化学推断补标签。O单列，不抵消C/SS缺口。

## 留组计划与可测性判断

先继承有据来源/重复反应闭包，再以相同产品加分割保护；产品保护不冒充同一assay证据，同一酶或供体名称不单独建边。

当前v6有56个资产：46个精确模板、10个scope。每折均提供全部56个资产的train保留支持、held-out排除、不同支持受体数和重建/排除动作；附属实例、donor/context映射、target/reaction索引及test参考表也列出隔离职责。模板支持ID在本地均可追溯，不代表完整运行绑定已核验。

**6个C/SS scope各自只有1个支持分组。** 留出其支持组后，对应scope剩余支持受体为0，未满足至少2个不同canonical acceptor的门。未使用不相关的同族scope来证明测试范围可行。

| 轴 | 候选折 | 已知scope支持不足 | 含范围未绑定对象 | 可证实同范围支持充足的折 |
| --- | ---: | ---: | ---: | ---: |
| C | 7 | 2 | 5 | 0 |
| SS | 5 | 3 | 2 | 0 |

C9、SS2个上下文没有既有scope支持成员关系，其中一个SS上下文与既知对象共享产品。unknown不等于适用性阴性；scope成员与相等反应键只提供继承范围依据，本轮没有运行SMARTS。主panel对象全部保留，范围子集只作诊断。

已知图的train/test组及产品交集均为空；全项目闭包、别名消费和实际train-only runtime重建仍未完成。所有折runtime_rebuild_verified=false、execution_authorized=false。不能把12个候选折或本地无交集写成12个可执行独立实验。

## 评价协议与单一后续决定

完整规格见本地evaluation_preregistration.json、evaluation_protocol.md及protocol_bindings.json：

1. 当前系统：A=generic、B=真实冻结P6 v6、E=后续合同冻结的最终增强版本，只评价历史开发目标。
2. 留组开发：A=generic、B_g/E_g均从同折train按固定方法重建；当前停止，不静默换B_g为完整v6。
3. 主分母事前按来源/结构/领域冻结，不按E命中或A/B失败筛样。正常无参考记0；未执行/错误/超时科学结果null；登记分母不丢错误。
4. 逐target/来源组报告；seed0/1/2不充当独立样本。完整reference以供体/立体/盐/组件重数保留的前体集合匹配；created完整节点及trace用于node transfer，候选命中不替代。
5. N_gap、G、净覆盖、损失、错误配对子集及操作成功下界在协议中明确；N_gap=0的比例为null。model/review/stock/code/runtime/panel及精确数值搜索预算仍待后续冻结。

决定为：**停止本库存的来源留组迁移执行；不补源，不恢复reader或epoch。** 两轴机器决定unresolved_closure_or_lineage，同时标明已知支持不足和范围未知。

如另行批准一个后续合同，优先做一次有界“当前系统历史目标开发评价”：仅C13+SS19完整编码target、3arms×3seeds，C/SS矩阵最多288 cells，失败尝试计账；执行前冻结全部资产、panel和数值预算，旧能力保护另列预算。零/负结果可结束该轮评价，不追加目标追成绩。来源留组的另288 cells仅是理论容量，未放行。

本轮没有注册或执行该后续TASK。上述描述性评价即使完成也不承担独立迁移证明；原每轴≥6 targets/≥2独立组、G≥3、G/N_gap≥50%、成功≥2组、三seed真实节点、净收益>0和reference loss=0等要求保持。若要改变pipeline完成规则，必须另立明确合同，不能由P9自动替换。

## 验证与合同偏差

主盘点一次，同冻结输入复算一次；9份核心产物逐字节一致，RDKit2023.09.6。针对新增分组/解析逻辑验证传递闭包、不同路线同产品分割、缺失不为0及等价编码键四个合成不变量；不是独立化学审核，没有重跑旧科学矩阵。

计划审查发现初版“任何同族scope存续即可行”的判据过粗。初版完整保留在review_before/，plan_review.json记录原因；仅从已生成结果补充继承同范围支持成员检查，再用唯一一次原输入复算验证最终版。没有二次主盘点、输入扩张、scope重建或预算扩张。

668个限定保护SHA检查无漂移；批准原文SHA、34个输入SHA、协议绑定、状态一致性、Git忽略与交付清单最终结果见verification.json及delivery_manifest.json。操作审计由scripts/operate.py写入现存operations/events.jsonl，仅从本轮游标计数。

| 验收 | 结果及证据 |
| --- | --- |
| AC01–02 | 通过；approval/approved_task/input_manifest、逐记录处置及访问闸门 |
| AC03 | 通过；96个上下文、27范围、四层计数、缺失及本地/全局闭包区分 |
| AC04–05 | 通过；12折逐ID计划、56资产逐折动作、同范围支持及运行未验证标记 |
| AC06–07 | 通过；两类比较、固定分母/错误/seed/group和训练重叠边界 |
| AC08–09 | 通过；科学效果全部null、科学执行0，P7/P2/正式门保持 |
| AC10 | 通过；9产物一致、668保护无漂移、输入/输出SHA和预算核对 |
| AC11–12 | 通过；停止留组执行并给一个有界后续规格，REPORT/STATE/索引一致 |

合同范围未扩展。规划完成条件不要求伪造可行折；数据不足已落实到具体scope、对象和支持缺口。后续效果、独立确认及pipeline转换保持未完成。

## 仓库、CI与未执行项

未提交、未推送，未调用外部服务；未启动CI、训练、模板构建、模型推理、MCTS或新epoch。仅新增一个盘点辅助脚本，旧代码/配置未改，不需重跑整套安装/科学回归。保护与忽略检查是本地治理验证。

planning_complete=true；development_evaluation_complete=false；c_effect_pass=ss_effect_pass=null；independent_confirmation_complete=false；pipeline_transition_authorized=false。新科学读取/HTTP/下载/模型/MCTS/新epoch均0，H5/G7未修复，R80未恢复。
