# 工作台路线图（WORKBENCH_ROADMAP）

本文档回答：**逆合成工作台现在到哪一步、下一步往哪走。** 论文线的证据缺口另见 [PAPER_ROADMAP.md](PAPER_ROADMAP.md)；两线共享同一证据边界（ADR-002）：候选不升格，工程测试不冒充化学验证。下一阶段主线（TASK-014—018）、方向价值排序 D1—D7 与批准要求见 [PAPER_ROADMAP.md](PAPER_ROADMAP.md) 的「下一阶段主线」一节，本页的阶段编号（P1—P5）与那里的 P0—P3 不通用。

## 项目目标（所有者 2026-09-22 表述）

建立逆合成工作台：在 AiZynthFinder 基础上优化搜索，加入基于黄酮苷针对性的有效性判断，最后加入文献教学模式。工作台独立于旧 `retro_synthesis` 项目存在。

## 现状（TASK-012 工程验收）

- **已就绪**：实时 MCTS（优化树，每次新建不读缓存）；四页工作台（路线探索 / 资源与证据 / 文献教学 / 项目状态）；路线解读（评分构成、closure 徽章、末端原料证据、逐步反应卡）；教学解释模式（27 个反应家族条目，default 回退）；文献教学层（15 文献卡 + 1 课程，claim 边界原样呈现）；糖苷连接拓扑审计进界面（/api/topology 实时审计、/api/molecule 候选键高亮、目标分子与末端原料家族候选标注、边界文案同屏、文献工程关联，TASK-011）；3,059 条候选资源（0 production）。
- **未就绪**：黄酮苷有效性判断未进搜索（仅界面只读呈现，接入搜索属 P2）；当前模型模板全部 classification=0.0 Unrecognized，尚无可靠家族标签；无图形编辑器与可缩放路线树；证据晋级（候选→production）全部待人工。

## 阶段方向

### P1 · 有效性判断可视化（已完成，TASK-011）

~~把已有的糖苷连接拓扑审计接入界面~~：已于 2026-09-25 由 TASK-011 完成（只读呈现，未改搜索语义），验收要点"labelled graph synthons, not reagents 边界文案随标注同屏出现"已满足；事实见 [reports/REPORT-011-topology-web.md](reports/REPORT-011-topology-web.md)。

### P2 · 黄酮苷领域搜索扩展（工程已建立；P7已终止，development effect未验收）

2026-09-29 所有者明确第一版优先补充基础模型缺失的黄酮苷候选生成能力：通过公开 API/官方批量下载自动获取数据，核查实例与模型缺口，构建来源可追溯、适用范围受限的模板，再作为独立策略受控接入 MCTS。化学合成与酶催化均可纳入，不依赖人工检索。当前 topology 仍是只读诊断，不能直接当作反应模板或可行性判据。

主线合同 [TASK-016 v0.2](tasks/TASK-016-open-glycoside-expansion.md) 于2026-10-06完成G1—G5工程，见[REPORT-016](reports/REPORT-016-open-glycoside-expansion.md)。开放接口获得4个产物实例、3个实验上下文、2论文，构建4个来源精确物种O成键模板，默认关闭；A/B同task015-06-v1审核与17库存，过滤后参照0/4→4/4，12/12真实MCTS配对补回。支持步骤、C/糖间成键分母均0；中性物种/新底物泛化未覆盖，固定分支预算另减少8个非参照动作。下一版先界定这些缺口与取舍，不把来源重现当作独立化学有效性；正式评测仍保持TASK-017门槛。

2026-10-06：[TASK-016-P1](tasks/TASK-016-P1-open-glycoside-library-expansion.md) Completed，见[REPORT-016-P1](reports/REPORT-016-P1-open-glycoside-library-expansion.md)。公开来源准入新增54精确成键反应（O33/C5/糖间16）、47模板（51总、5多受体范围）；冻结12开发目标C补回7（58.3%），三seed实际动作/参照零损失/通用前三保护通过。12身份待确认上下文保留，预算明确agent_delegated修订180→240、最终216次。已有来源约束的有限新目标迁移能力；全部增益同一出处、4糖间留出未补回、C留出0，不称化学/全空间泛化。P2扩库合同完成，可进入TASK-017设计与独立标签/来源/库存/evidence准入核查，正式评测尚未执行。

2026-10-06 当前补充：[TASK-016-P2](tasks/TASK-016-P2-c-sugar-transfer-validation.md)经human_direct批准执行，本轮[REPORT](reports/REPORT-016-P2-c-sugar-transfer-validation.md)整体Partial。默认关闭v3共54模板，新增1C/2糖间范围；旧4SS/5C/7O参照三seed真实创建，但新增准入0、两类新面板不足，新A/B/D未执行。6目标/2出处、至少3且50%补回及三seed要求不降低。独立账61保守（51验证+10工程、含6模拟fixture）/55实际，240上限保持。下一步补身份/闭包与新精确面板；TASK-017仅设计/准入，本轮无正式/供应/发布/Git同步。任务后缀P2与本节工作台P2阶段分开，阶段决定agent_delegated不伪装human_reviewed。

2026-10-13 终止裁定：[TASK-016-P7](tasks/TASK-016-P7-domain-aligned-transfer-closure.md) **Partial，执行终止，科学验收未完成**；C-E02/SS-E02/C-E03已按原§3.3/§18.1正式development_epoch_incomplete，C-E01/SS-E01维持关闭。[终止审计](reports/REPORT-016-P7-closeout-20261013.md)。fresh C0/SS0、科学A/B/E0 cell、metrics=null；P2 development effect未验收，原科学门不变。已有O/P1/P6工程成果与曝光保留，不恢复R80、不以G7修复作为退出前置；本轮不建新epoch。后续研究须另行批准并先证明干净评价来源的可达性与隔离方案；TASK-017正式盲测未执行。

2026-10-13 重新设计交付：[TASK-016-P9](tasks/TASK-016-P9-development-evaluation-redesign.md) **Completed（规划交付）**，[报告](reports/REPORT-016-P9-development-evaluation-redesign.md)。34输入、96去重上下文，C13/SS19不同编码目标；12候选折与56资产排除计划已交付，可证实同范围支持充足折C0/SS0，停止本库存留组迁移执行。若另批，可开展最多288-cell当前系统历史目标描述性评价；本轮科学0 cell。原双轴增益/P2门未通过，P7保持Partial/stopped，旧epochs关闭。

2026-10-05 衔接任务：[TASK-015-06：审核结果如何进入搜索](tasks/TASK-015-06-review-into-search.md) 已Completed。P3/P4/P5已有裁决用于实际资源准入、严格实例关联、逐步/末端/资源/导出及运行指纹；默认审核视图task015-06-v1，保留未知候选，错配隔离并保留原件，模型排序/评分原样。17库存键保持，4错配原已禁用、2本地模板仍不启用，供应认证0。后续TASK-016的G4–G5绑定交付审核版本；本轮未启动。

### P3 · 教学层深化（低风险）

- 当前 uspto/ringbreaker 合计 47,836 条全部为 0.0 Unrecognized；先建立可靠且有来源的家族标签，再考虑映射，不将 27 条教学材料冒充 27 类已识别结果。
- 文献课程扩充（更多 LRC）：门槛 `human_structure_reviewed`，机器抽取内容须人工核对结构后才能进课程。
- 教学目标的中文名表（TARGET_NAMES_ZH）与预设快照（frozen example）评估移植。

本线可在 TASK-014/015 期间作为并行低风险工程线推进（模板 → 结构变换 → reaction family，每条映射带来源、置信等级与复核状态）；安排见 [PAPER_ROADMAP.md](PAPER_ROADMAP.md)「下一阶段主线」D3。

### P4 · 交互组件（中风险，vendor 许可需登记）

D3 可缩放路线树、JSME 结构编辑器、路线对照视图、PubChem 名称联查。复制 vendor 文件时登记许可到 LICENSES/，并复审静态资源 allowlist。

### P5 · 证据晋级流（仅人工发起）

模板/库存的独立来源审核界面、名称冲突处置（现有 3 条）、正式盲测。决策权边界见 [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md)：agent 不得代行。

### 搜索算法调优（排序：在可信评测集之后）

PUCT、动作融合、去重、替代动作、转置与节点预算合同已经存在（TASK-012 修复了同次扩展重复状态与多产物 outcome index 两个真实缺陷）；但 native 与 optimized 没有严格等价的节点预算，早期搜索参数仍是 provisional。系统调优（预算归一基准、参数消融、PUCT 权重、template-policy 融合、转置策略比较）按 [PAPER_ROADMAP.md](PAPER_ROADMAP.md) D4 排在可信评测集建立之后，不在 TASK-014—018 主线内。

### 工程向（随时可做）

- 独立环境与工程基线由 TASK-012 收口：新 .venv-foundation、wheel/sdist、统一 v3/SQLite、全参数/历史/开发评估 UI、无资产 CI；当前同步验收进度以 STATE/REPORT-012 为准。
- 服务部署形态（systemd 单元 / nginx 反代），当前为手工启动开发服务器。
- browser_check 时序加固（TASK-010 曾出现一次未复现的等待超时）。

## 阶段准入规则

每个 P 阶段动工前：写 TASK 合同（范围/验收/停止条件）→ 批准（人工或记录授权的 agent_delegated）→ operate.py 全程记录 → REPORT + STATE 更新。历史2026-09-25规则要求P2/P5人工批准；本次所有者明确授予TASK-016-P1高自主权限，按agent_delegated记录阶段/预算修订并已完成。不伪装human_reviewed，不将本次批准写成其他TASK自动授权。

## 2026-09-27 当前补充

TASK-014 已完成离线领域筛选试点与 [领域/标注/评测协议](protocols/README.md)，不改变 P2 扩展/评分，也不使 P5 证据晋级完成。已有 60 条未填写开发审核样本（糖苷重点 30 条）；下一步是所有者批准 TASK-015 独立审核/开发 gold。外部来源扩展和搜索接入仍需独立任务。

2026-09-27 更新：TASK-015 以 human_direct 工程授权完成 ORD 当前镜像覆盖和 60 条离线审核卡，实际人工 gold 未执行。当前先用 30 糖苷重点卡、按 protocols/SCIFINDER_TARGETED_IMPORT_V1.md 补 4 条材料；P2 接入和算法评测依赖继续保持，详见 REPORT-015。
