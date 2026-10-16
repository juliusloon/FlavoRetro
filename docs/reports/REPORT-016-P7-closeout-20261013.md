# REPORT-016-P7-CLOSEOUT：P7 终止审计与当前 epochs 正式收口

日期：2026-10-13（Asia/Shanghai）。批准与裁定：**agent_delegated**，human_reviewed=false。
合同：[TASK-016-P7-CLOSEOUT](../tasks/TASK-016-P7-closeout-20261013.md)；原科学合同：[TASK-016-P7](../tasks/TASK-016-P7-domain-aligned-transfer-closure.md)。

**P7 已停止执行，总体结案状态为 Partial；科学验收未完成。C-E02、SS-E02、C-E03 已正式记为 development_epoch_incomplete。**
C-E01/SS-E01 维持原已关闭状态。本轮不创建后继 epoch、不恢复 R80、不修 G7，也不开展新科学读取。

## 1. 正式停止决定

| epoch | 本次正式状态 | 直接停止依据与边界 |
| --- | --- | --- |
| C-E02 | development_epoch_incomplete | confirmed fresh=0，低于 ≥6 targets/≥2 groups；当前有界库存和已完成发现路线没有形成可验证面板路径。不是全球文献或化学空间穷尽 |
| SS-E02 | development_epoch_incomplete | confirmed fresh=0；条件组上界4不等于4个合格组，也不能提供6个合格target。R80角色完整恢复不作为停止前置 |
| C-E03 | development_epoch_incomplete | confirmed fresh=0；H1未满足§7.3，A11 F1/F2 blocking、F3/F6 pending。现有A0锁件不允许fresh首读，缺少已证且获准的合法前置闭合路径；依所有者本次授权结束持续等待 |

三个决定直接依据 P7 §3.3 与 §18.1 的面板最低门。C-E03 的 G4 工程scope继续保留，**不宣称scope无效、不宣称未来任何合法方案都不可能，也不把没有科学验证解释成模型迁移失败**。

终止登记仅向原 epoch_ledger.jsonl **追加3行（82→85）**；旧82行字节前缀完整保留。各决定在：
- outputs/task016-p7/v1/epochs/C-E02/incomplete_decision.json
- outputs/task016-p7/v1/epochs/SS-E02/incomplete_decision.json
- outputs/task016-p7/v1/epochs/C-E03/incomplete_decision.json

每个 epoch 另有 terminal_state_20261013.json。旧 active stage/epoch_state 快照保留历史性质，不能覆盖更晚的正式终止事件。
项目级机器入口为 **outputs/task016-p7/v1/task_execution_closeout.json**：task_status=Partial、execution_status=stopped、scientific_completion=false、current_epoch_scientific_execution_authorized=false。

## 2. 为什么本轮可以结束恢复循环

P8 已经完成诊断；H1 书面裁定未使 C-E03 科学前置成立。既存 scientific_processing_lock 的 release_condition 是尚未实现的条件陈述，不是已完成的科学产物或已获准的执行方案。A0 既存处置明确 candidate_content_reads_authorized=false。所有者本次“请落实”授权正式停止，所以不再维持 C-E03 为无限期等待状态。

R80 的 prior unknown、pending、未终结role/round保留真实状态。pea1982 的 not_blocked 裁定不被撤销，也不被提升为完整独立性证明。本轮撤销旧 prospective 恢复许可对已关闭 epochs 的**后续执行效力**，原批准和当时发生的读取仍是历史证据，不回写、不伪造完成。

H5 的曝光补记保留；**G7未消费补充账、专利别名解析缺口仍存在**。这些是未来冻结任何面板前需要解决的阻断，但不构成退出当前 epochs 的前置。本轮没有以行政结案把治理缺口改成pass，也不新增一个为保持P7运行而必须完成的修复任务。

## 3. 曝光与未读候选的保全

原中央曝光账、既有prior账和原始阅读事件均不回写。终止时消费现存明确索引/阅读事件元数据，并生成：
- permanent_exposure_closeout.jsonl：**104条既有肯定读取事件的永久不可fresh投影**。
- exposure_preservation_manifest.json：**96个具名元数据文件**的SHA、保留账指针、未确认事件分文件计数与范围限制。

**104是事件投影行，不是不同来源、反应或合格target数**，包括不同reader、重复/重叠账的记录。只有原记录明确 scientific_content_read=true 或 scientific_bytes_opened=true 的事件进入本次确认读取投影；开始/登记行、metadata-only和未确认内容不由本轮升格为新读取。

有 **17条**既有肯定读取记录没有可直接复用的closure_tokens。本轮保留其原证据指针与未知别名，不猜造闭包；这是后续面板准入需要处理的残余限制，不阻止本次终止。原有exposed标记与既有names登记均保留。

he2019、qiu2021、Shi2026、EfCGT1及三件SS旧文献保留原未读/未证明状态；没有因epoch终止自动判污染。王源杰2018的公开摘要及三专利沿用前轮真实曝光补记，不能通过新epoch漂白已读内容。
本轮**没有重建全项目曝光库或验证全项目source/assay闭包完成**；覆盖声明严格限于继承的明确账与本次具名事件集合，all_project_exposure_coverage_complete=false。

## 4. 科学结果与已有工程成果

| 项目 | 最终保留事实 |
| --- | --- |
| 合格fresh targets | C=0，SS=0 |
| 已确认独立fresh groups | C=0，SS=0 |
| 缺额 | 每轴6 targets/2 groups |
| 正式新科学A/B/E | 0 cell |
| N_gap、G、G/N_gap、净覆盖、reference loss、三seed node transfer | null（未运行，不能记0） |
| 既有scope/G4与旧运行 | 保留；epoch终止不撤销工程证据 |
| P7总体 | **Partial，执行终止，科学未验收** |
| Roadmap P2 development effect | 未验收，不标完成 |
| TASK-017/018与formal/release | 未执行/未升格 |

C-E03 两个build replay与8边界检查仍是原工程结果；O/P1/P6的历史交付保留。未获科学评价数据不等于已测得迁移增益为零。

## 5. 未来工作的准入边界

本轮不新建任务执行科学发现，不生成 C-E04 或 SS-E03，也不延续当前epochs的旧读取许可。
将来只有另获独立任务批准，并在科学读取前说明以下事实，才值得重新投入：
1. 干净评价来源群的具名/可核实发现依据与合法取得路径；
2. 支持 ≥6 targets/≥2 independent groups 的可达性依据与不确定性；
3. design/build/evaluation 的时间顺序、来源/assay隔离与历史曝光处理；
4. 一次有界执行的预算、失败停止门，以及 G7 全量补充账/别名接入的验证方案。

只有metadata线索时如实标候选，不能预先宣称来源足够或评价必成。旧失败epoch已读对象可成为design材料，不能重新成为fresh。

## 6. 操作、验证与限制

- 所有执行/写入经scripts/operate.py登记；本轮第一条只读bootstrap未经operate的事实已专门披露，不冒充原始命令当时已被登记。
- 新HTTP/下载/原文读取/A4–A6重跑/R80恢复/MCTS/代码修复/新scope/新epoch/Git同步均0。读取范围为已有合同、报告、阶段/曝光/访问元数据；未打开PDF/SI或受限科学原文。
- 旧报告/STATE/合同状态原文已存于closeout-20261013/before/。当前入口改为终止状态，旧科学条款和证据历史保留。
- 本轮是主控行政裁定与直接一致性验证，没有新独立科学审核。批准后命令预算20；最终计数与SHA/前缀/状态验证见verification.json。
- CLOSEOUT-ERR-01：初版覆盖清单把26667条继承的未确认/登记项逐行展开，过度冗余；改为分文件计数，初版保留于superseded/。读取事实、确认投影、unknown和科学分母均未改。
- 仍有独立结构、prior/assay、别名与G7入口缺口；全部随Partial结案保留，不伪造科学完成，也不把它们变成本轮无限恢复队列。
