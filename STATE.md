# 当前状态

TASK-001—009 已完成工程验收与治理文档详细化；资源 3,059 条，0 production（候选，无独立审核）。

TASK-010 已完成 Web 工作台完整化：四页架构（路线探索 / 资源与证据 / 文献教学 / 项目状态），顶栏固定，探索页双栏贴边独立滚动；路线解读（评分构成、closure 徽章、末端原料证据、逐步反应卡）、教学解释模式（27 个反应家族条目，/api/teaching）、文献教学层（15 文献卡 + 1 课程，/api/literature-teaching，claim 边界原样呈现）已上线；教学配置文件已入仓 configs/（与旧项目源 SHA-256 一致）；28 项单元测试与浏览器验收在 cano 通过。长期决定见 ADR-004。

TASK-011 已完成有效性判断可视化（WORKBENCH_ROADMAP P1）：糖苷连接拓扑审计接入界面——新增 /api/topology 实时审计端点与 /api/molecule 可选候选键着色高亮；探索页目标分子侧栏与末端原料卡显示糖苷位点家族候选标注（aryl_O / sugar_sugar_O / aryl_C 等原样标签附中文释义），每处标注同屏携带 "labelled graph synthons, not reagents" 边界文案与 claim 原文；标注带文献教学层的工程关键词关联链接（可跳转定位）。只呈现，搜索语义未变；32 项单元测试与浏览器验收在 cano 通过。本任务起恢复人工批准流（所有者 2026-09-25 收回 agent 代行批准权，TASK-011 为人工批准）。

活动数据指针：data/derived/v1（v2 重放保留未切换，TASK-007-P1 补充被所有者搁置）。一次性脚本已归档 operations/archive/（见 ADR-003）。

工作区提示：STATE.md 早前"27 个空白格式化文件未提交"的备注已过期——那些改动已随 f272c36 提交；服务器端 git 工作区无遗留噪音（挂载视图下的 mode 位变化是挂载手段产物，非仓库事实）。operations/events.jsonl 有一条 2026-09-22 的误记行（task 字段为 "--help"），追加式日志不删改，已在 REPORT-010 标注。

已知缺口：教学条目的命名家族键与现行模板数值 classification 未对齐（前端 default 回退，见 REPORT-010）；黄酮苷有效性判断已进界面（只读呈现），接入搜索属 P2，未动工；文献关联为工程关键词匹配，对 O-糖苷家族选择性弱（REPORT-011）。

下一步由人决定：工作台方向读 docs/WORKBENCH_ROADMAP.md（P2—P5 阶段与准入规则；P1 已于 TASK-011 完成）；论文工作读 docs/PAPER_ROADMAP.md；接手维护读 docs/HUMAN_TAKEOVER.md。正式盲测与任何证据晋级需人工批准，不得由 agent 代行；TASK 起草后须经所有者人工确认才可执行（2026-09-25 起）。
