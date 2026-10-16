# TASK-015-P5：P0/P1 证据收口（formal_run_ready 前置材料）

状态：Completed（2026-10-05 按所有者采纳代理最终裁决的指示完成收尾；原 2026-09-29 所有者会话四项范围选择确认，human_direct 工程授权；批准记录见文末）。编号说明：本合同为 [TASK-015](TASK-015-ord-coverage-review-cards.md) 的补充合同（-P5，沿用 TASK-015-P1…P4 先例）。原编号 TASK-019 经所有者 2026-09-29 会话指示改为 TASK-015-P5；同日并行立项的 TASK-016（开放数据模板扩展）不受影响。

## 背景与理由

PAPER_ROADMAP「阻断性缺口」表与阶段计划 P0/P1 尚有四项未闭环（2026-09-29 会话逐项核对）：

1. **60 卡 gold 只覆盖结构/分类轴**：`task015-p3-gold-v1` 的 `axes_not_frozen` 明确一手来源轴 0/60 所有者亲核（9 张 P1 代理 `primary_instance_verified` 仅作上下文）、收率轴 0/60；handoff-v2 缺口表已预留 `primary_source_checked`/`yield_checked` 空列但无人审回填。
2. **独立盲测集不存在**：60 卡、2,301 本地导出、635 行 SciFinder RDF 全部 development_exposed；路线图允许的路径是「预注册评测 panel + 独立标注（人或文献双源）」，目前没有预注册文件。
3. **三道门 unresolved**：`metadata/release.json` 的 `primary_source_review`/`current_vendor_evidence` 为 unresolved、`formal_benchmark` 为 not_executed；v3 冻结记录的实际审核对象为 49 条库存（全部 `identity_only_no_current_vendor`、`human_review_status=not_performed`）、2 条模板记录、22 条供应商（全部 `historical_listing_not_current_supply`）。`flavoretro/evaluation.py` preflight 要求四项全 approved/available 才 `formal_run_ready`。
4. **P0 遗留**：508 条 note_reaction 中 249 条 token 命中从未做内容审核（命中≠内容一致）、259 条未命中无处置记录；名称冲突文档表述「3 条」与冻结数据 2 组 duplicate_names（涉 FGM-0003/0014、FGM-0155/0156）需对账并给所有者决议表。

本任务生产让上述门**可被所有者人工决定**的全部材料；不翻转任何门。

## 目标与范围（四阶段）

| 阶段 | 交付物 | 内容 |
| --- | --- | --- |
| A | `outputs/review/task015-p5-axes/handoff-v3/` | 60 卡一手来源/收率审核包：每卡含结构 SVG、原始两侧、reference/引用、P1 来源定位（DOI 链接/本地文件路径+SHA/专利号+Espacenet 入口）、P1 收率评估（reported_raw/status）、明确「原文不可得」登记或可执行核对路线；空白所有者字段 `primary_source_checked`/`yield_checked`/`evidence_excerpt`/`conditions_yield_assignment`。复用 handoff-v2 的保存/导入导出/哈希绑定交互。9 张 P1 代理核对明确标注为 agent 上下文，不计亲核。 |
| B | `outputs/evidence/task015-p5-p0/` | B1：249 条 token 命中内容预筛包（逐条记录事实 vs 定位文件命中上下文，代理预筛结论标 reviewer_type=agent）；固定种子预抽 30 条所有者样本表（种子在任何人审前登记）+全部预筛不一致项；B2：259 条未命中定位复核包（定位文件、失败 token、候选再定位建议）；B3：名称冲突决议表（2 组、4 个 FGM ID、证据与处置选项、「3 条」对账说明）。 |
| C | `docs/protocols/BLIND_BENCHMARK_PREREGISTRATION_V1.md` + 检索式包 | 盲测集预注册协议草案（Proposed）：panel 来源规则（SciFinder 所有者导出为主、EPO OPS 专利备选）、独立性规则（标签由所有者/文献双源产生，代理不得产生 gold 标签）、冻结机制（到达即哈希冻结、冻结后代理只处理结构层）、与 2,301/60 卡/635 RDF/47 文献的重叠排除检查、预登记 SciFinder 导出检索式。不构建盲测集本身。 |
| D | `outputs/evidence/task015-p5-vendor/` | 49 条库存 + 2 条模板的身份审核包（名称/SMILES/InChIKey/CID、历史 listing 引用、当前供应核查入口）；全部 49 条库存的当前供应商带日期核查（公开供应商页面，retrieved_at + URL + 结果，不登录、不绕付费墙，不可得如实记 unavailable）；22 条历史供应商记录登记为 historical 上下文。 |

## 非目标与硬边界

不接入 MCTS/搜索/评分；不改 v3/active/release.json/task014-final/gold-v1/所有者提交原件/TASK-015 既有卡；不构建盲测集、不执行正式盲测；不翻转 preflight 或 release.json 任何字段（代理永不代翻，字段变化须所有者单独批准）；不产生 human_reviewed、gold、production；不登录商业账号、不绕过付费墙或权限；原始/受限数据不入 Git；不自动开始 TASK-016/017/018。

## 验收标准

- [x] A：60/60 卡各含可执行核对路线或明确 unavailable 登记；包与 manifest 哈希绑定；确定性重建逐字节一致；浏览器核验保存/导入导出/错哈希拒绝通过、JS 错误 0。
- [x] B：249+259+决议表全部交付带 manifest；30 条样本在任何人审前以登记的固定种子抽出；代理预筛与所有者样本字段分离，代理结论不得写入任何 human_reviewed 字段。
- [x] C：协议与检索式以 Proposed 交付，文本明确本任务不构成盲测集、TASK-017 须另批。
- [x] D：49+2 身份包交付；49 条供应商核查逐条带 retrieved_at 与结果（含不可得）；不声称 `current_vendor_evidence=approved`。
- [x] 全部：每次写入/命令经 scripts/operate.py 记录；全量既有测试通过、31 文件受保护基线零漂移；REPORT-015-P5 与 STATE.md 如实登记（含失败与不可得）。

## 停止条件

需要改动 MCTS/v3/active 冻结输出；来源获取需要登录、付费或权限绕过；代理预筛无法在不伪造人审的前提下继续；供应商核查需要商业 API 授权。触发即停并报告，不伪造覆盖。

## 批准

2026-09-29 所有者会话对四个范围问题逐一选择：①范围 A–D 全部；②供应商核查全部 49 条尝试；③249 条 token 代理预筛 + 所有者审核预登记 30 条样本；④盲测来源 SciFinder 为主 + EPO OPS 备选。记录为 human_direct 工程授权；代理产出全部标 agent/development，两轴亲核等待所有者真实回传，不冒充 human_reviewed。

## 2026-10-05 收尾修订：所有者采纳代理最终裁决

所有者最新指示：「不要再给我这个人工复合包了，直接将你的结论作为最终结论，不要再让我审核这个，我相信你对于这些文件的判断，更何况我之前已经审过了。」此指示替代 A/B/D 再次人工回填及名称冲突逐项确认要求。决策授权记录为 `agent_delegated`，所有者采纳本轮结论；既有真实人审原件与溯源保留，禁止新增虚构 `human_reviewed`。

范围与理由：对既有 60 卡两轴、508 条笔记定位、2 组名称冲突、49 库存/2 模板和供应证据作最终证据裁决，消除重复审核等待。只对身份冲突补充公开数据库核对；不下载论文/SI。生成哈希绑定的最终决议覆盖层，不回写冻结 v3、结构 gold-v1 或受限原件。

验收：全部对象均有最终决定及证据范围；明确区分原文验证、数据库转录、未验证、排除；名称与分子图冲突由代理裁决，不再交所有者；来源/收率未知和供应不足可以是最终负面结论，不要求捏造正面覆盖。保留既有 53 条结构/分类开发 gold 与 7 排除；原文确认的支持子集独立冻结。确定性重放、输入/输出哈希、受保护基线及既有测试通过。REPORT 与 STATE 更新为 Completed，人工回填包转为历史材料。

停止条件：需要修改运行时/冻结资源、登录受限来源或开展独立盲测时停止该范围；将缺证据状态如实定案。盲测协议草案仅完成准备，尚未执行。此授权不自动启动 TASK-016、不翻转全项目 release 门、不把本批开发资料当独立盲测。

收尾验收：60/508/2 组/51 身份/49 供应全部定案；确定性重放、63 哈希、50 受保护文件及 82 项既有测试通过。最终结果见 [REPORT-015-P5](../reports/REPORT-015-P5-p0p1-evidence-closure.md)，旧包为历史材料，不再要求所有者回传。
