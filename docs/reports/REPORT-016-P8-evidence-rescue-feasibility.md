# REPORT-016-P8：P7 科学可达性诊断与下一 Epoch 决策

- 任务：**TASK-016-P8**（合同 **v0.2**，SHA `2cab3f4d394aedaa40118b9428b845555ee7d1caadeb64e520c3d29880bcf395`；v0.1 原字节 SHA `a61c0541…` 归档于 `operations/task016-p8-original/`）。
- 结论：**Completed（负面科学可达性结论）**。合同 §8 末句明写"P8 Completed 的充分条件是给出可靠的科学可达性判断及可批准的下一步，**即使最终 fresh 仍为 0**"。本轮满足该条件：两轴差额、可达性、四类结论分层与六项可批准行动均已给出并经独立复核。
- 授权：所有者本会话"我已批准，开始执行TASK-016-P8"＝合同 §7 **第 1 层**（仅批准 D0–D3 只读决策工作），记 `human_direct`；阶段决定 `agent_delegated`。**非 `human_reviewed`，无独立化学验证。**
- 执行角色：**2 个**（P8-D 决策主控 = root；P8-V 独立决策复核 = 1 个独立只读子代理）。所有者本会话允许创建智能体团队，但合同 §6 的 2 角色上限更严，**P8 按合同执行、未组建多代理团队**。
- **本报告不改变任何 P7 数值**：fresh **C 0 / SS 0**、科学 A/B/E **0 cell**、迁移指标 **`null`**（未运行，不记为 0）、`can_freeze_G7_panel=false`、`G6_global_complete=false`、G7/G8/新 bank G9/G10 未形成、物理账 **1309 HTTP / 1,245,786,610 B 不变**、MCTS 账 **214 行 SHA 不变**、未 Git commit/push。**TASK-016-P7 与 Roadmap P2 仍 In Progress；P8 结案不自动升格 TASK-016、P7 或 TASK-017 正式盲测。**
- 交付物：`outputs/task016-p8/v2/` 下 `approval.json`、`reviewed_disposition_index.md`（D0）、`feasibility_matrix.md`（D1）、`d2_decisions.md`（D2）、`P7_DECISION_HANDOFF.md`、`P8_DECISION_AUDIT.md`，及 `superseded/*.pre-p8v-correction-v1`（v1 原字节，未删改）。本文件为事实性报告。

## 一、本轮做了什么、没做什么

**做了**：只读消费 P7 既有报告（主报告 618 行含 20 问答与 v17–v39 全部增量、C-E03 预检、SS/R80 恢复预检、R81–R87 续作附录）、既有冻结产物（逐反应资格账本 17 source/36 row、三个 G4 stage、R87 fresh 队列、R80 A6 草稿、R74/R76 饱和评审、intake 清单、A11/A6 审计件）与合同文本，产出 D0 处置索引（65 行逐来源 + 5 个 epoch 边界 + 4 项具名争议）、D1 差额与可达性矩阵（5 个 epoch × 8 个必填字段 + 轴级汇总 + 两条结构性引理）、D2 分轴决策（每轴 1 主决策 + 2 备选 + NEW_EPOCH 附页）、D3 独立复核与交接。

**没做**（合同 §2.1 / §6 全部禁令，实测值见 `P8_DECISION_AUDIT.md` 第四节）：外部 HTTP **0**、PDF/SI 下载 **0**、新增科学原文读取 **0**、A4/A5/A6 重跑 **0**、新 MCTS **0**、全量 ledger 重建 **0**、大规模代码改造 **0**（`scripts/`、`flavoretro/`、`tests/`、`configs/` 零改动）、正式 P7 epoch 写入 **0**、新建项目脚本 **0**、修改 P7 保护件 **0**（P8-V 独立遍历 `outputs/task016-p7/` **5,705** 个文件，mtime 晚于本轮起点者 **0 个**；三个 G4 stage SHA 逐字符相符；`git diff --check` 退出码 0）。**未重新打开、解析或逐篇重审任何已判无效的 PDF。**

## 二、合同 §2 六个必答问题的回答

**1｜现在已知的合格 fresh / 独立 closure groups 数，与 P7 原门槛 C ≥6/≥2、SS ≥6/≥2 分别差多少？哪部分确实不适用，哪部分只是尚未证明？**

两轴均为 **0 fresh targets / 0 independent closure groups**，差额各 **6 targets / 2 groups**。

*确实不适用*（规则性不可逆排除，非证据不足）：C-E01 与 SS-E01 两个 epoch 全部（已停止/已注销）；C-E02 的 owner16 C 侧 7 条限定例、`PMC13564134`（`REJECTED_FROM_FRESH_AS_EXACT_BUILD_REPLAY`：全图与静态适用性均通过，却精确命中 build 反应 C-CHRYSIN-LU6）、`PMC9855344`/`PMC12525976`/`PMC11577821`、Gentiana GtUF6CGT1 与 UGT84A57（2/2 HTTP403 + 历史曝光）、PlUGT43、R73 五源；SS-E02 的 **3 个 direct 糖残基 O2 源级正证据组**（番茄 SlUGT79B-B `PMC12611259`、大豆 Fg3 `PMC4494776`、拟南芥 UGT79B6 `PMC4282749`）与 Trapero 2012 `PMC3425182`、`PMC11974848`（同 closure 非第二组）、owner16 SS 侧 7 条限定例、Morita 2005（`OUT_OF_SCOPE_ACCEPTOR_CLASS`）、kamsteeg1979（6″-O-Rha 越域）、`PMC5517534`/`PMC5444469`/`PMC6813240`、buckwheat2018、Nemophila GT、Saylor & Mansell 1977、R73 五源。

*只是尚未证明*（`unknown`/`not_yet_assessed`，**未改写为 false/zero**）：C-E03 四件具名候选（he2019、qiu2021、Shi 2026 `PMC12993211`、EfCGT1 `PMC12310836`）的 prior 与 liu2021 闭包；王源杰2018 与 EkCGT1 `10.1021/acs.jafc.5c09887` 的面板内容；SS 侧 kho1978/heinsbroek1979/sutter1973 的 scope 对齐；owner16 C-10（Iris SI）与 SS-14（豌豆 1979）两条 deferred；28 条永久命名曝光的结构级排除（真实审查 **0**）；88+35 条残余 metadata 宇宙；17 来源各自的残余 `not_yet_assessed` 行（`article_reaction_universe_exhausted` 17/17 均 `false`、`article_level_exclusion_rows=0`）。

**2｜已核无效的 PDF/反应为什么不能通过增加审计或更换 Agent 变成 fresh？**

因为排除依据是**规则性**的而非**证据质量性**的。P7 §3.1–3.2 规定：P1–P6 及本 epoch 内已被化学结构/位点级检视、或曾用于 scope 设计/规则设计/边界调节的对象，一律记 `historical_development_exposure`，**不得作为新底物迁移成功分母**；§3.3 第 2–3 条规定 epoch 内已被化学抽取/检查的候选永久入 exposure ledger 且**不得在下一 epoch 继续充当 holdout**。增加审计只能提高**判定的可靠性**，不能改变**阅读已发生**这一事实；更换 Agent 更被 §18.2 直接禁止（"需要把 historical/exposed target 当 fresh holdout"、"subagent/harness 的阶段隔离无法保证"）。

这不是推定而是**执行实证**：R81 的 `fq.open_for_first_scientific_read` 探针对 Trapero 按政策 `prior_design_or_historical_exposure_still_excludes` **实际抛出拒绝**（`SS/E02/fresh/SS-E02-R82-…/A0_fresh_lane_closure_probe.json`）。反向同样成立：被排除**不等于**该论文全部化学内容被否定——17/17 来源的 `article_reaction_universe_exhausted=false`、`article_level_exclusion_rows=0`，R8 对 `PMC13387883` 亦明记"不是对整篇论文所有化学内容的否定"。

**3｜有没有具名且无已确认不可逆排除原因、可在不降低科学规则下以一次有限补证继续推进的候选？**

**C 轴：有。** C-E03 的 he2019（`10.1002/anie.201905505`，在库 4,090,558 B，`unread=true`）、qiu2021（`10.1016/j.bioorg.2021.104926`，在库 1,458,830 B，`unread=true`）、Shi 2026（`PMC12993211`，CC-BY，R77 密封未读）、EfCGT1 2025（`PMC12310836`，gold OA，R79 密封未读）——四件具名、合法在库、从未内容阅读、无已确认不可逆排除原因。其补证**不是"再去读一篇论文"**，而是先由 root/A0 书面裁决 **DSP-4**（design 侧 §7.3 前置能否以既有 R84 PubChem 权威结构闭合），该裁决**不需要任何新化学证据、不需要新 HTTP**。

**SS 轴：没有。** pea 1982 的缺口已在**同一原文内**被全文扫描否证（无 2-O/1→2 连接、无甲基化/全甲基化/高碘酸氧化/酶水解结构测定），**无具名待补证字段可在不新增科学阅读下闭合**；kho1978/heinsbroek1979/sutter1973 经 DSP-3 书面证明**即使全部准入也不改变 SS 决策**（`targets ≥6` 无具名可信路径）。故如实写：**SS 侧现有资料中没有已证实可执行、且能改变结论的补证路径。**

**4｜C-E02、C-E03、SS-E02（及其他已证存在的冻结 scope/epoch）各自应如何处置？**

| epoch | 处置 | 依据 |
| --- | --- | --- |
| C-E01 | **不重开** | 已按 §18.1 正式停止；20 已读来源/19 闭包/56 对象永久曝光 |
| C-E02 | **RECOMMEND_EPOCH_INCOMPLETE** | §18.1"fresh panel <6 targets 或 <2 groups"+"来源饱和条件已满足但仍无法形成 panel"；§6.3 条件 3+4 成立（v35 判定、v36 三条新路线复核维持）；剩余两件候选各为单一来源（引理 A），且王源杰2018 主要途径即 C-E02 build 反应（引理 B） |
| **C-E03** | **CONTINUE_EXISTING_EPOCH（有条件）与 BLOCKED/OWNER_DECISION 并列待裁** | scope 有效未被判无效（replay 2/2、8 边界 0 违反、`scope_invalidated_by_A11=false`）、阶段时序成立、四件具名未读候选在库；但 A11 F1/F2 为 **blocking**、F3/F6 为 **pending**、A6 三源 prior 与 liu2021 闭包 **`unknown`**，且 intake `role` 标签为 `C8_design_deferred`/`C6_design_deferred` 与 R87 的 `prospective_fresh_*` 冲突。**故该主决策不能自足成立**，由 ROOT-Q-C1 决定取哪一支 |
| SS-E01 | **不重开** | 已实际注销；P4 已证 1→6 仅 1 个 canonical acceptor，未过 §9 第 1 条 |
| **SS-E02** | **RECOMMEND_EPOCH_INCOMPLETE**（先收尾 R80，后裁定） | §18.1 同款 + §6.3 条件 3+4 成立；`groups ∈ [0,4]` 虽可达 ≥2，但 **`targets ≥6` 无具名可信路径**（这才是绑定约束） |

**P8 自身不注销、不改写任何 P7 epoch。**

**5｜如果需要新的 epoch，如何保证 scope-first、真实 G4、fresh G5、来源/assay/build 与后验模型隔离？**

见 `P7_DECISION_HANDOFF.md` H6 与 `d2_decisions.md` 第三节附页。要点：严格 §3 时序（design corpus → build supports → replay + boundary → **FREEZE scope SHA** → 之后才允许化学抽取 fresh）；把 **per-target G5 首读批准做成硬门而非事后补记**（这正是 C-E03 F6 的缺陷）；把"unread 证明"改为**与完整 live 曝光账交叉核对**出具，而非沿用早于 design read 的 intake 标志；**新增要求**：同一酶跨论文跨年代是否构成 `same experimental cohort / source assay`，必须由独立 A6 出具**书面判据**（把 P7 既有先例"共用 donor 不作为单独泄漏依据"明确扩展到"共用酶"），不得由 root 事后叙述；G7 writer 必须已硬绑定**全部**曝光补充登记（manual 16 件、manual 11 件、R73、DSP-1 专利补记、28 名称审查结果）后方可冻结面板；两轴分离；≥6/≥2 落空时直接按 §18.1 判 `development_epoch_incomplete`，不降门、不复用旧 holdout、不以 metadata 数/处理轮次数/工程检查数替代留出闭包数。

**SS 侧诚实结论**：当前**没有**潜在独立群的证据（3 个 direct-O2 正证据组全部已曝光；v35 记"UGT79B 家族全库扫描无新表征成员"；SS 专利线两轮阴性；R76 三条新路线 0 个 scope 对齐候选），故**只能**提出"需先进行另获批准的有限 **metadata-only** 可行性勘察"，**不得**提前科学阅读候选，**不得**声称该设计必定成功。
**C 侧诚实结论**：本轮**不**提出 C-E04。已执行的 C8 发现路线（EuropePMC/Crossref/OpenAlex/Rhea/PubChem/引文追溯/PMC-OA/NCBI esearch 全字段/NCBI MeSH 交叉/NCBI elink/EPMC 预印本/专利/学位论文）已把可命名的 C8 文献群收敛到 TcCGT1 簇 + ThCGT + EfCGT1 + 四属直接型 CGT，未读者仅剩 Shi 2026 与 EfCGT1。**若二者亦被消费，C-E04 没有已知的独立 fresh 来源群。**

**6｜交给 P7 主控的下一项有限、可批准的行动是什么？能否保证终验？**

按优先级（`P7_DECISION_HANDOFF.md` H1–H6）：
- **H1（最高优先）**：root/A0 就 **DSP-4 + ROOT-Q-C1 + intake `role` 标签冲突**出具**一份书面裁决**。0 HTTP / 0 新科学阅读 / 0 MCTS。
- **H2**：在 A0 已签发的**仅限原 R80 同批**恢复许可内，补齐 R80 的**终结 A4/A5/A6 role 与 round manifest**（既有批次的文档终结，不新增候选、不重开首读），随后按 §18.1 发出 SS-E02 缺口报告。
- **H3**：按 §18.1 发出 C-E02 缺口报告，owner16 C-10 保持 deferred 并单列。
- **H4**：C-E01/SS-E01 不重开，无行动请求。
- **H5（治理阻断）**：root/A0 裁定 **DSP-1** 并**补记曝光账**——两份免费专利（`CN113186214A` 子代理已读至实施例、`CN121065126A` 主控已读全文）与 `CN111808902B` 实施例 1 的反应级阅读，在 progress-v37 §1 有叙述、§6 却记"无新曝光行"，而两个专利号在**任何曝光账中 0 命中**（P8-D 与 P8-V 分别独立核验）。**这是 G7 writer 的 `named_exposure_gate_v4.validate_final_panel(enforce_floor=True)` 硬绑定必须消费的曝光补充之一；缺行状态下冻结任何面板都会使防泄漏门形同虚设。**
- **H6**：SS-E03 仅限 metadata-only 可行性勘察，**明确不推荐现在批准执行**。

**不能保证终验，本报告明确承认这一点。** C-E03 即使 DSP-4 裁决为是，仍需 DSP-2 判独立组、intake 标签冲突裁定、四件候选各自过 G5→A3→A4/A5→A6→§7.4 完整结构→§10.2 全部八项条件，才**可能**形成 ≥6/≥2 面板；SS-E02 的 R80 收尾能否在不重开首读下完成，既存产物中**无先例可判**（故 H2 预设"两次尝试失败即转 Partial"的退出路径）。**P8 不以"持续搜索直到找到 6 个"作为行动**（合同 §5 严禁项已写入 H1/H2/H3/H6 的 `stop_if`）。

## 三、两条决定全部结论的结构性引理

**引理 A（单来源不可能闭合任一轴）**：§10.2 的 floor 是 `≥6 targets` **且** `≥2 closure groups`，§8 把 `same experimental cohort / source assay` 与 `same source article` 列为闭包边。故任何单一来源最多贡献 1 组，一个轴要达 floor 必须有**至少 2 个互相独立、未被排除、scope 对齐的来源**，且每个都通过 §7.3/§7.4 完整结构与 §10.2 八项条件。

**引理 B（exact build replay 会吞掉"看起来最像"的候选）**：`PMC13564134` 已通过 A3 身份、A4/A5 完整全图（`structure_complete=true`、`reference_precursor_complete=true`）、C6–C1 键与 (2S,3R,4R,5S,6R) 糖立体核对，并在冻结 C-E02 scope 下静态还原出完整前体（2 个有效结果），**仍被判 `REJECTED_FROM_FRESH_AS_EXACT_BUILD_REPLAY`**。故**候选的科学质量不是瓶颈，独立性才是**。这直接给出王源杰2018（主要途径 luteolin→isoorientin 即 C-E02 build 反应）的先验风险。

## 四、三层结论分离（合同 §9；禁止笼统"所有相关论文不存在"）

| 结论类型 | C 轴 | SS 轴 |
| --- | --- | --- |
| `existing_frozen_scope_not_demonstrably_feasible`（现有库存不足以证明可达） | **C-E01、C-E02 成立**；**C-E03 明确不成立**（阻断在程序/证据层，不在来源可得性层） | **SS-E01、SS-E02 成立** |
| `scientifically_falsified_specific_claim`（具体反应不符） | owner16 C 侧 7 条限定例（2-羟基前体后脱水、有机多步化学、二氢查尔酮 C3′、GWAS 间接）；`PMC9855344`/`PMC12525976`/`PMC11577821` 的具体反应层；`PMC13564134` 的**独立性**（非其化学正确性——其化学结构核对是通过的） | Morita 2005 受体类越域；owner16 SS 侧 7 条限定例（苷元 O3/O7/O4′/O3′、3-O 可逆 UDP 转移）；kamsteeg1979 的 6″-O-Rha；`PMC5517534` 母核 7-O；Nemophila 苷元 O；Saylor & Mansell 1977 的 hydroxycinnamoyl:CoA 转移酶 |
| `unknown_global_source_availability`（**保留**，不得当作已否证） | 专利路线直到 v37 才执行；2010 年前未索引老文献为如实登记盲区；88 条 C 轴残余 metadata 从未化学评估 | SS 专利线两轮阴性**不等于**穷尽；2010 年前老文献盲区；35 条 SS 轴残余 metadata 从未化学评估；UGT79B 家族扫描阴性不证明无其他家族 |

**必须同时说明的正面事实（避免把负面结论读成"该化学不存在"）**：SS-E02 的冻结 scope 化学**是真实且有源级正证据的**——3 个不同发表原始研究的 direct 糖残基 O2 + UDP-glucose 重组酶证据，加 Trapero 2012 的 1→2 直接 HMBC 结构证据（末位 Glc H1 4.75 ppm × 内 Glc C2 79.53 ppm 等，双 Glc 12 碳、β 构型、Table I 全归属、与 Markham 1978 一致）。它们不可用**仅因规则性曝光排除**，不因其证据薄弱。Trapero 另有一项**独立的科学限制**须与曝光排除分开记：**重组酶体外活性未证实**（对含 kaempferol-3-glucoside 的全部受试底物无活性，全细胞转化亦阴性）、甲基化分析无、标准品共进样无，故其酶级 2″-O 归属为**体内/相关性证据**。

## 五、工程完成 / 来源限制 / 具体化学确认三层（项目纪律）

- **工程完成**：D0–D3 四阶段全部产出并经独立复核；P8-V 六项判定全 pass；8 项差异中 7 项已在 v2 修正、1 项经 P8-D 复核判为 P8-V 误报（`disposition_summary.json` 实测**不含** `title_relevant` 键）并如实记录；预算远低于上限（本轮执行阶段 `operate.py` 记录操作 ≤16 / 上限 40）；`git diff --check` 通过；P7 保护件 0 漂移（5,705 文件独立遍历）。
- **来源限制**：本轮 HTTP=0、下载=0、新科学原文读取=0，故**所有 `unknown` 保持 `unknown`**——DSP-1 的最终曝光层级、DSP-2 的 TcCGT1 同队列判定、各条件性候选的 `targets` 数、王源杰2018 期刊版是否在全库、R80 收尾能否不重开首读，**五项均未闭合，P8 未代为填补**。`data/raw/` 原件内容与 `outputs/task016-p7/` 全库检索受合同 §2.1 约束，未执行。
- **具体化学确认**：**本轮未发生任何独立化学验证**。P8-V 的复核属指针/计数/逻辑/门禁/权限层，**不是独立化学确认**（合同 §7："双重文字总结不是独立化学确认"）。P8 全部结论属"对既有裁定的整合与算术"，**不构成新的化学证据**，不升格 `human_reviewed`、`independent chemical validation`、`actionable`、`evidence_closed`、`prediction_conditions_verified`、`formal_run_ready`、`release_ready`。

## 六、本轮自身错误（如实登记；无一靠降门槛或换分母修复）

| ID | 错误 | 代价 | 处置 |
| --- | --- | --- | --- |
| P8-ERR-01 | D0 v1 交叉引用错号（S-24 应为 S-22） | 可追溯性缺陷，无科学代价 | v2 已改，v1 归档 |
| P8-ERR-02 | **D0/D1 v1 漏引既存 A6 `not_blocked` 裁定**（`A6_exposure_projection_review.json`，`at=2026-10-12T07:05:16+00:00`），把 P8 自己的保守合并当定论 | SS-E02 组数上界被低估 1（`[0,3]`→`[0,4]`）；**SS 主决策不变**（绑定约束是 targets 门） | v2 已改并显式标注"P8 推断 vs 既有裁定方向相反"；按合同 §6 的 4 项上限**不新开 DSP-5** |
| P8-ERR-03 | **D0 v1 未披露 intake `role` 与 R87 队列 `role` 的冲突**（`C8_design_deferred`/`C6_design_deferred` vs `prospective_fresh_*`） | C 轴主决策的证据基础被高估；若不披露会让 CONTINUE 看起来比实际更成立 | v2 新增 D0"第四之一"节全表披露 11 件；D2/H1 明写"主决策不能自足成立"并设 ROOT-Q-C1 与 `stop_if` ③ |
| P8-ERR-04 | D2 v1 字段名混用（`future_epoch_reuse_allowed` 用于 C-E03/R83 侧） | 指针精度缺陷 | v2 改为 `current_epoch_fresh_eligible`/`future_fresh_eligible` 并加注 |
| P8-ERR-05 | D1 v1 把 qiu2021 并入 TcCGT1 簇下界，与 D0"不推断其酶身份"自相矛盾 | 下界成因表述不一致 | v2 已改（上界单列、下界并入并写明原因） |
| P8-LIM-01 | Edit 工具在 SMB 挂载 `rename` 失败（`EINVAL`），改用 `temp/p8-drafts/` 下两个一次性草稿替换助手 | 引入 2 个非项目脚本（Git-ignored，不入交付，不读 P7 产物、不写 `outputs/` 或 `scripts/`） | 已在审计件第四节披露；不占用合同允许的"1 个只读脚本"额度（它既非只读也非项目脚本） |
| P8-LIM-02 | P8-V 的一处误报（差异 #8） | 若照改会引入一个不存在的"矛盾标注" | P8-D 实测键列表后**不按其修改文件**，并在审计件 3.2 #8 如实记录为误报 |

## 七、验收标准逐条对照（合同 §8）

| 验收项 | 状态 | 依据 |
| --- | --- | --- |
| 已直接接受已确认无效的原 PDF/反应结论，未再次执行全文审查；既有 14 rejected 与 2 deferred 的证据边界未抹去 | **满足** | 本轮 0 PDF 打开；D0 第一节把所有者确认严格绑定到 14 条 rejected，C-10 与 SS-14 明确排除在确认范围外并保持 deferred；P8-V 判定 #1 pass |
| C/SS 分轴及各既有冻结 scope 的既知 fresh/closure、到 ≥6/≥2 的差额与当前有效条件集合清晰，没有把条件性可能计为已准入 | **满足** | D1 五个 epoch × 8 字段 + 轴级汇总；全部 `confirmed_*` = 0，全部 `conditional_evaluable` 的"可计入 6/2"列为**否** |
| C-E02、C-E03、SS-E02 和 SS/R80 的分支去留都有明确科学/时序原因与 evidence pointer；没有重做 A4/A5/A6 | **满足** | 第二节问题 4 表 + H1–H6 逐项 pointer；A4/A5/A6 重跑 = 0 |
| 每轴主决策属 CONTINUE / ONE_BOUNDED_EVIDENCE_ACTION / EPOCH_INCOMPLETE / BLOCKED 之一；若提议新 epoch，严格保持 scope-first、无旧 holdout 泄漏且标明无法保证来源充足 | **满足** | C = CONTINUE（有条件，与 BLOCKED 并列待裁）；SS = EPOCH_INCOMPLETE。两轴均按合同优先级书面说明前序选项为何不成立（SS 侧 ONE_BOUNDED 明确"仅存在一项"不满足）。H6 附页两轴 fresh 来源群均答"未知"、均写"无法保证"、SS 仅限 metadata-only |
| 每个下一行动有责任角色、唯一所需信息、预算/授权、完成或停止条件；不存在开放式无穷 source loop | **满足** | H1–H6 各 14 字段齐全；四处 `stop_if` 显式封死开放式搜索 |
| 独立核对 P7 科学门、owner/P7 证据分层、局部反应 vs 全篇文献结论和保护要求 | **满足** | P8-V 六项判定全 pass（含与 P7 §10.2/§6.3/§18.1/§18.2/§7.3/§7.4/§8/§9 原文逐条对照，无一处降低；`article_level_exclusion_rows=0` 与 17/17 `article_reaction_universe_exhausted=false` 保持） |
| 执行预算与零新增读/HTTP/MCTS/全库清账限制满足，`git diff --check` 通过 | **满足** | 审计件第四、五节；P8-V 独立遍历 5,705 个 P7 文件 0 漂移、三个 G4 SHA 逐字符相符 |
| `P7_DECISION_HANDOFF.md`、事实性的本报告与当前 STATE 一致；P8 结案不冒充 P7/TASK-016 development/TASK-017 已关闭 | **满足** | 三者同轮更新；全文零"P7 完成/Roadmap P2 关闭/TASK-017 就绪"表述；H1–H6 各项 `status_of_O_P1_P6_assets` 明写"不冒充 TASK-017 正式盲测" |

## 八、机器证据入口

- 本轮决策产物：`outputs/task016-p8/v2/`（`approval.json`、D0/D1/D2、`P7_DECISION_HANDOFF.md`、`P8_DECISION_AUDIT.md`、`superseded/*.pre-p8v-correction-v1`）
- 本轮引用的 P7 权威产物（**均未修改**）：`outputs/task016-p7/v1/reaction_eligibility_ledger_v1/`、`G6_owner_16_historical_source_review_v2/{C,SS}/`、`G6_three_decisions_20261012_v1/`、`C/E03/{stages,fresh,design}/`、`SS/E02/fresh/SS-E02-R80-owner-originals-full-qualification-v1/`、`SS/E02/fresh/SS-E02-R82-trapero-structural-evidence-read-v1/`、`governance/{R74-R75-source-loop-stop-review-v1,R76-skill-routes-saturation-confirmation-v1,R79-originals-request-v1,R80-owner-originals-A11-A6-v1,C-E03-liu2021-design-recovery-A0-v1,R73-partial-read-permanent-exposure-v1}/`、`verification-C-E03-R83-R87-metadata-preflight-A11-v1/`、`manual_grabbed_20261012/manual_grabbed_1/intake_manifest.json`、`discovery_evidence/session2_20261012/old_era_patents_agent_report.md`、`discovery_r76_skill_routes_20261012/`、`report_snapshots/progress-{v35-final,v36-final,v37-final,v38-final,C-E03-preflight-v1,SS-R80-recovery-preflight-v1}.json`、`epoch_ledger.jsonl`
- 操作审计：`operations/events.jsonl`（task=TASK-016-P8）

## 九、未升格声明

本轮**未**升格：`human_reviewed`、independent chemical validation、formal blind benchmark、训练独立泛化、实验可行性/产率、供应认证、production/release、`actionable`/`evidence_closed`/`prediction_conditions_verified`、`formal_run_ready`/`release_ready`。**TASK-017/018 未执行。TASK-016-P7 与 Roadmap P2 仍 In Progress。未 Git commit/push/tag/release。** 是否实际恢复 P7、建立新 epoch、执行 H1–H6 中任何一项，**均需独立批准，不由本 P8 结案自动触发。**
