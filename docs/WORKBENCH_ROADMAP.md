# 工作台路线图（WORKBENCH_ROADMAP）

本文档回答：**逆合成工作台现在到哪一步、下一步往哪走。** 论文线的证据缺口另见 [PAPER_ROADMAP.md](PAPER_ROADMAP.md)；两线共享同一证据边界（ADR-002）：候选不升格，工程测试不冒充化学验证。

## 项目目标（所有者 2026-09-22 表述）

建立逆合成工作台：在 AiZynthFinder 基础上优化搜索，加入基于黄酮苷针对性的有效性判断，最后加入文献教学模式。工作台独立于旧 `retro_synthesis` 项目存在。

## 现状（TASK-010 完成后）

- **已就绪**：实时 MCTS（优化树，每次新建不读缓存）；四页工作台（路线探索 / 资源与证据 / 文献教学 / 项目状态）；路线解读（评分构成、closure 徽章、末端原料证据、逐步反应卡）；教学解释模式（27 个反应家族条目，default 回退）；文献教学层（15 文献卡 + 1 课程，claim 边界原样呈现）；3,059 条候选资源（0 production）。
- **未就绪**：黄酮苷有效性判断只在结构诊断（topology.py，CLI/outputs）层存在，未进搜索、未进界面；教学条目与现行模板数值 classification 有映射缺口；无图形编辑器与可缩放路线树；证据晋级（候选→production）全部待人工。

## 阶段方向

### P1 · 有效性判断可视化（低风险，建议优先）

把已有的糖苷连接拓扑审计（`flavoretro/topology.py`，`outputs/validation/topology-v1.json`，156 分子）接入界面：分子/路线叶子的糖苷位点家族标注（aryl_O / sugar_sugar_O / C-苷等候选标签），并与文献课程关联。**只呈现，不改搜索语义。** 验收要点：拓扑候选标注"labelled graph synthons, not reagents"的边界文案随标注同屏出现。

### P2 · 黄酮苷有效性判断接入搜索（高风险，需独立 TASK + 人工批准）

目标：让 MCTS 扩展/评分感知黄酮苷反应家族（如芳基 O-糖苷键断裂、O-甲基化/去甲基化），思路可参照旧项目 `reaction_families.json` 中 3 个 active_expansion 家族的审计门控做法。前置条件：先冻结定义（什么算"有效"）、冻结评测协议（目标 × 种子矩阵、对照引擎），再动 `worker.py`/`search.py`。禁止以工程跑分自称化学有效性。

### P3 · 教学层深化（低风险）

- 补齐教学条目与 uspto/ringbreaker 数值 classification 的映射（先统计实际搜索命中的分类分布，再补条目）。
- 文献课程扩充（更多 LRC）：门槛 `human_structure_reviewed`，机器抽取内容须人工核对结构后才能进课程。
- 教学目标的中文名表（TARGET_NAMES_ZH）与预设快照（frozen example）评估移植。

### P4 · 交互组件（中风险，vendor 许可需登记）

D3 可缩放路线树、JSME 结构编辑器、路线对照视图、PubChem 名称联查。复制 vendor 文件时登记许可到 LICENSES/，并复审静态资源 allowlist。

### P5 · 证据晋级流（仅人工发起）

模板/库存的独立来源审核界面、名称冲突处置（现有 3 条）、正式盲测。决策权边界见 [HUMAN_TAKEOVER.md](HUMAN_TAKEOVER.md)：agent 不得代行。

### 工程向（随时可做）

- `.venv` 独立环境重建验证（现依赖 retro Conda 环境的 system-site-packages，换机即断；见 environment/README.md）。
- 服务部署形态（systemd 单元 / nginx 反代），当前为手工启动开发服务器。
- browser_check 时序加固（TASK-010 曾出现一次未复现的等待超时）。

## 阶段准入规则

每个 P 阶段动工前：写 TASK 合同（范围/验收/停止条件）→ 批准（人工或记录授权的 agent_delegated）→ operate.py 全程记录 → REPORT + STATE 更新。P2、P5 必须人工批准，不接受 agent_delegated。
