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

### P2 · 黄酮苷有效性判断接入搜索（高风险，需独立 TASK + 人工批准）

目标：让 MCTS 扩展/评分感知黄酮苷反应家族（如芳基 O-糖苷键断裂、O-甲基化/去甲基化），思路可参照旧项目 `reaction_families.json` 中 3 个 active_expansion 家族的审计门控做法。前置条件：先冻结定义（什么算"有效"）、冻结评测协议（目标 × 种子矩阵、对照引擎），再动 `worker.py`/`search.py`。禁止以工程跑分自称化学有效性。

主线编号为 TASK-016：定义与协议由先在的 TASK-014/015 负责冻结，接入后须与普通 MCTS 做冻结协议下的对照；排序与批准要求见 [PAPER_ROADMAP.md](PAPER_ROADMAP.md)「下一阶段主线」。

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

每个 P 阶段动工前：写 TASK 合同（范围/验收/停止条件）→ 批准（人工或记录授权的 agent_delegated）→ operate.py 全程记录 → REPORT + STATE 更新。P2、P5 必须人工批准，不接受 agent_delegated。2026-09-25 起所有者收回 agent 代行批准权：所有 TASK 起草后须经所有者人工确认才可执行（自 TASK-011 起生效）。

## 2026-09-27 当前补充

TASK-014 已完成离线领域筛选试点与 [领域/标注/评测协议](protocols/README.md)，不改变 P2 扩展/评分，也不使 P5 证据晋级完成。已有 60 条未填写开发审核样本（糖苷重点 30 条）；下一步是所有者批准 TASK-015 独立审核/开发 gold。外部来源扩展和搜索接入仍需独立任务。

2026-09-27 更新：TASK-015 以 human_direct 工程授权完成 ORD 当前镜像覆盖和 60 条离线审核卡，实际人工 gold 未执行。当前先用 30 糖苷重点卡、按 protocols/SCIFINDER_TARGETED_IMPORT_V1.md 补 4 条材料；P2 接入和算法评测依赖继续保持，详见 REPORT-015。
