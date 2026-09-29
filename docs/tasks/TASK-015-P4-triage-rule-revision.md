# TASK-015-P4：筛选规则修订（人审校准回灌）

状态：Completed（2026-09-29 当日完成，见 REPORT-015-P4；执行时状态记录保留于下文）。原记录：Approved → In Progress（2026-09-29 所有者在本会话明确回复「批准. 执行前, 还有需要确定的吗? …」，记录为 human_direct 工程执行授权。执行中工程决定：新增处置桶不静默删记录、版本 task015-p4-v2、黑名单入 configs/、回归检查从严（gold 卡不入任何新拦截/嫌疑桶）。

## 背景与理由

TASK-015-P3 的 60 卡人审（38 所有者亲审 + 22 所有者委托代填，gold task015-p3-gold-v1）暴露 TASK-014 筛选规则 v1 的机器假阳性模式，7 张排除卡给出明确校准标签：

| 卡 | 模式 | 标签 |
| --- | --- | --- |
| 27 | 多步生物合成路径被导出压缩为单步"反应"（酪氨酸 → 黄酮 C-糖苷多产物） | path_compression_multistep_exported_as_single_reaction |
| 28/51/52 | 仅摘要级证据、无可 usable 反应内容仍保留候选 | no_usable_reaction_content(_abstract_only/_no_primary_fulltext) |
| 53 | 来源论文正式撤稿仍进入候选 | retracted_source |
| 54 | 产物无 SMILES/结构不可用 | product_structure_unavailable |
| 55 | 导出不完整（STEPS=Product only） | incomplete_reaction_export_product_only |

其中 54/55 已由 v1 的 partial_or_invalid 处理，需验证覆盖；27/28/51/52/53 需要新规则或新输入。当前瓶颈：人审已给出开发校准点，但机器筛选行为尚未回灌这些结论，同类假阳性会在后续队列继续出现。

## 目标与范围

| 项 | 内容 |
| --- | --- |
| 规则 v2 | configs/domain_triage.json 升级为新 protocol_version（v2 与 v1 并存可加载），路径压缩检测、撤稿来源黑名单（数据文件，初始含已核实的撤稿论文 DOI 10.1007/s11164-024-05454-8 关联对）、摘要空内容降权/分箱规则，全部版本化并显式 provisional |
| 代码 | flavoretro/triage.py 最小扩展以支持 v2 字段；不改 v1 行为 |
| 重跑 | 同一冻结 2,301 输入重跑试点至新目录（outputs/triage/task015-p4-v2），与 task014-final 对比队列变化 |
| 回灌验证 | 以 60 卡人审结论为校准集：v2 应对 7 张排除卡降级/拦截，且不得把 53 张 gold 保留卡错误降为 low_or_unknown（回归检查） |
| 报告 | REPORT-015-P4：规则变化、队列前后对比、回归结果、局限 |

## 非目标与硬边界

不接入 MCTS/搜索/评分；不改 task014-final、gold-v1、所有者提交原件、v3、active；不声称化学准确率或方法优越性（60 卡开发样本上的过滤率变化不外推总体）；不产生新的独立盲测；原始/受限数据不入 Git。撤稿黑名单仅收录可核实的公开撤稿记录，逐条注明来源与日期。

## 验收标准

- [ ] v2 规则版本化、可加载、v1 行为不回归；每条新规则有明确的判定输入与 provisional 声明。
- [ ] 同输入重跑与对比完成；7 张排除卡的处置变化逐卡登记；53 张 gold 保留卡零误降级。
- [ ] 新增合同测试 + 既有全量测试通过；两次独立构建逐字节一致。
- [ ] REPORT/STATE 如实登记；不自动启动 TASK-016。

## 停止条件

规则修订需改动 MCTS 语义、需触碰冻结输出、或校准集出现无法用规则表达的人审判断时，停止并报告；不伪造规则覆盖。

## 批准

2026-09-29 所有者会话回复「批准」，human_direct 工程执行授权；机器筛选与校准回灌记 agent_delegated，不伪装 human_reviewed。
