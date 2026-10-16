# REPORT-016-P7 续作附录：R81–R87（2026-10-12，本会话）

授权：所有者本会话明确「审批全部同意，继续推进 task 内容」，批准与阶段决定记 agent_delegated，非 human_reviewed。合同仍为 [TASK-016-P7](../tasks/TASK-016-P7-domain-aligned-transfer-closure.md)（v0.1），全部命令与写入经 `scripts/operate.py` 记账（events.jsonl + command-*.log）。

## 一、R81：Trapero 2012 SS G5 预注册冻结（完成）

- 承接会话前状态：`role_A3_manifest.json` 等三文件为 R80 遗留稿（counts.processed=2），脚本改为 counts=1 后因「文件已存在即跳过」守卫从未生效——这就是连续 `A3 processed denominator` 失败的根因。
- 脚本修复（最小充分）：补 `INTAKE`/`PRECONTRACT` 定义（R78 sealed custody 的 query_execution.jsonl 与 precontract.json）；`assert source_candidates==1`；`source_count=1`；无条件下重生成 universe/A3/role 三文件（旧稿按 supersession 纪律归档至 `superseded/*.pre-r81-counts-fix`，未删除）；**曝光注记如实化**——原稿「exposure-ledger identifier overlap = 0」为错误继承，v4 prior_exposure_inventory 实有 2 行历史设计曝光（#L2548 permanent_scientific_design_source_exposure、#L3209 metadata_or_access_deferred_only）与 Trapero 标识符相交。
- 结果：G5 预注册冻结成功（`G5 manifest SHA 290bbdc18efaabdb30bc63a523a672d361da4e7b29e06c70ee30059cb528293e`），Trapero（PMC3425182, UGT707B1）为唯一 source candidate，content read 前 preregistration 成立。
- **fresh 通道关闭为执行实证**：`fq.open_for_first_scientific_read` 探针按政策 `prior_design_or_historical_exposure_still_excludes` 抛出 `known prior/design or previously read source requires exclusion or explicit recovery contract`——证据 `SS/E02/fresh/SS-E02-R82-.../A0_fresh_lane_closure_probe.json`。用户指示中的 `rm -rf .../superseded/` 实际无对象（R81 无 superseded 目录）；真实的脏状态是三份在位旧稿，已按归档式 supersession 处理并在此声明偏离原因。

## 二、R82：Trapero 设计通道双读者读取与 A6 结构证据裁定（完成并经独立核验）

- 双读者（A4=stdlib HTMLParser/R47 Reader，A5=stdlib regex 块抽取，utf-8 直读 R78 sealed custody HTML）：A4 632 块/81 上下文、A5 207 块/70 上下文；曝光行 4 条（`historical_design`，content_read=true）入 `scientific_exposure_reads.jsonl`。
- **A6 核心判定（SS 轴突破点）**：正文有 sophoroside 1→2 连接的**直接二维 NMR（HMBC）证据**——末位 Glc H1(4.75ppm)×内部 Glc C2(79.53ppm)、Glc C1(102.32ppm)×内部 H2(3.77ppm)、H1(5.10ppm)×苷元 C-3(133.51ppm)；双 Glc 12 碳、β 构型、Table I 全归属、与 Markham 1978 文献值一致。**甲基化分析：无**；**标准品共进样：无**（仅 LC-MS 数据比对 authentic reference materials）；**重组酶体外活性：未证实**（对包括 kaempferol-3-glucoside 在内的全部受试底物无活性，全细胞转化亦阴性）——酶级 2″-O 归属为体内/相关性证据（转基因拟南芥代谢物 fx=K-3GG-7R 的 MSn+温和酸水解、物种共表达）。12 条引文由脚本从落盘文本原样抽取（零转写）。
- 独立核验（saved agent 审阅者，只读）：12/12 引文逐字符一致、SHA 可重算、甲基化/标准品 ABSENT 被独立证实、体外阴性双读者覆盖、位移值两读者一致，`determination_acceptable=true`；报告与核验绑定入批次目录。SS-E02 fresh 保持 0/0（Trapero 永久 design-exposed，不得为 fresh）。

## 三、R83–R87：C-E03 开张（草稿→G4 冻结→fresh 池解锁）

- **R83 设计 intake**：liu2021（JAFC 2021, 10.1021/acs.jafc.1c00602, 69:6578-6587, ACS「Efficient Production of Orientin and Vitexin from Luteolin and Apigenin…」）按所有者批准的 C8 时序开读（intake_manifest fresh_sequencing.C8_cluster）；Crossref 元数据身份（1 次 HTTP）；双读者 pdftotext -layout/-raw；4 条 `late_prior_design` 曝光行。该源自此为 build 语料，永不 fresh。
- **R84 权威结构**：PubChem name→SMILES（apigenin CID 5280443 / luteolin 5280445 / vitexin 5280441 / orientin 5281675）；公式差 Δ=C6H10O5 双通道验证；零手写结构。
- **R85 build supports**：apigenin→vitexin、luteolin→orientin 两个 C_formation 支持（TcCGT1，GenBank MK644229，**体外重组酶动力学实证** Km 0.26/0.9 mM）；**C8 位点计算验证**——A 环 C8 定位器与 vitexin/orientin 糖基碳重合、与 C-E02 冻结的 C6 对照（C-CHRYSIN-LU6）判别成立；8 个边界对照预注册。
- **R86 G4 冻结**：exact→scope 管线复用 C-E02 同款构造（derive_template_smarts + scoped_smarts + guard_spec + pyrone C3-H 谓词）。`scope_audit passed`：1 scope `p7-C-E03:flavone_8_C_glucoside_C8_H`、2 build supports、**replay 2/2**、**8 边界对照 0 违反**。G2（前驱=全局 G1）/G3/G4 阶段链 + scope_manifest 冻结（G4 manifest SHA `bb4b508432bc622b57056371ffe18a1d7136a12aa1f799b740599e0d8eb7654f`）。过程错误如实记录：①R85 将 reference_precursors 存为合并字符串（C-E02 为列表形式），R86 载入规范化并注记；②边界计划 v1 的 BC6/BC7 误设「产物自身不得触发」——retro 模板对支持物产物触发正是 replay 行为，v1 保留为证据，v2 增法式替换为异头差向异构体阴性对照（BC6v2/BC7v2）。
- **R87 fresh 池解锁**：3 件从未读原件（he2019 ANIE 2019、qiu2021 Bioorg Chem 2021、王源杰硕士论文）登记入 C-E03 fresh 队列（每件须各自预注册 G5 full-qualification 合同后方可科学阅读）；台账 G5 行入账，fresh_admitted=0。

## 四、验证与保护

- 全量本地回归 **293/293 OK**（`unittest discover -s tests`，40.0s，operations 最新命令日志）；`git diff --check` 通过。
- 保护完整性：R80 G5 合同（03549307…）与 R80 G5 stage manifest（1f0f4819…）逐字节一致；C-E02 scope_bank 与其 manifest SHA 一致；本会话改动仅落在 `outputs/task016-p7/`、`data/raw/task016-p7` 新 custody、新 `scripts/task016_p7_r8*.py`、本 REPORT 与 STATE 追加段。
- 来源预算：本会话实际 HTTP 均为 metadata/structure-authority 类（R83 Crossref 1、R84 PubChem 4、R85 PubChem 4，其中 1 次 400 失败按纪律留档后以修正 URL 重试成功），远低于 8,000 上限；MCTS 0。

## 五、证据边界（不升格声明）

C-E03 scope 是 design/development 层资产；Trapero 的 1→2 结构证据为设计语料证据，不构成酶级 fresh 迁移证据；SS fresh 仍 0/0，SS 突破的下一手是 R82 判定后为 O2 scope 采集非曝光来源的 fresh 候选。全部新资产 default 关闭语义不变；未触碰模型/PUCT/stock/review 绑定；未 Git commit/push；human_reviewed/独立化学验证/formal/release 门全部保持未关闭。
