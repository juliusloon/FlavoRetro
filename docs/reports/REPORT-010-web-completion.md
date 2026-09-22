# REPORT-010：Web 工作台完整化、布局修复与项目独立收口

## 对应任务

- 任务 ID：TASK-010
- 任务文件：[../tasks/TASK-010-web-completion.md](../tasks/TASK-010-web-completion.md)
- 状态：Completed
- 基线：main @ f272c36（doc: 可读性提升）
- 批准：Kimi（agent_delegated，2026-09-22，AGENTS.md 记载的本次授权 + 用户本会话直接指令）
- 执行时段：2026-09-22 15:58—16:18 UTC（合同登记至验收完成；后续文档落盘另计）
- 结果提交：见末节 Git 提交

## 改动文件

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| docs/tasks（事前合同） | TASK-010-web-completion.md | 新增：本任务合同（before=null → after=c64519a1…） |
| configs（运行配置） | teaching_guidance.json | 新增：27 个反应家族教学条目（after=e652ddcf…），复制自旧项目 `config/product/teaching_guidance.json`，SHA-256 与源一致 |
| configs（运行配置） | literature_teaching_layer.json | 新增：15 张文献卡 + 1 条反应课程 + claim 政策（after=311f10bf…），复制自旧项目 `config/product/literature_teaching_layer.json`，SHA-256 与源一致 |
| flavoretro（共享 API 逻辑） | web.py | 改动（5329ce73… → 28946946…）：新增 `GET /api/teaching` 与 `GET /api/literature-teaching` 两个端点，沿用既有 JSON 端点写法与响应头；其余逐字节未动 |
| tests（测试合同） | test_web.py | 新增（after=8fbbf407…）：3 项端点测试（教学分类边界字段、文献卡 claim_status、未知路径 404 与 no-store 头），ephemeral 端口起真实服务器 |
| web（浏览器工作台） | index.html、app.js、style.css | 重写扩充：四页架构、固定顶栏、双栏独立滚动、路线解读、教学解释开关、文献教学页、状态页 profiles 卡片（前后哈希见 events.jsonl） |
| scripts（活动工具） | browser_check.py | 适配（c8bd43b1… → 9df22b65…）：新增文献教学页断言（paper-card >0）；既有 23 个元素 id 与其余流程逐行未动 |
| outputs/validation（非 Git 证据） | browser-fc15e727/ | 新增：通过当次的 desktop/mobile 截图与 report.json |

staging 目录 `operations/.staging-task010/` 为写入暂存（沿用 TASK-009 先例），其内容不是交付物。

## 实际改动

1. **布局修复**：顶栏改为 `position: sticky` 固定，四页滚动均不丢失；路线探索页 `.workspace` 双栏撑满视口剩余高度，左栏贴视口左边、右栏贴视口右边，两栏各自 `overflow-y: auto` 独立滚动；≤900px 退化为单列文档流（移动端 390px 无横向溢出已由浏览器验收断言）。
2. **路线解读移植**：路线卡片新增 closure 徽章（surrogate→"候选闭合 · 无独立证据"、partial→"部分路线 · 未闭合"）、评分构成（`score = steps + 2×未解决原料 + 5×已知危险 + 未指定立体` 分项与公式，附 score_status 中文释义）、`evidence_closed:false · actionable:false · release_ready:false` 事实行、末端原料证据小卡（结构图、evidence_basis/structure_check/hazard 中文标签）、逐步反应卡（模板号、反应家族中文名、policy 概率与排名、mapped_reaction_smiles）；已知局限（limitations）逐条中文化并附原始记录。
3. **教学解释模式**：表单内开关（默认开，状态存 localStorage `flavoretro.teaching`）；教学文案来自 `/api/teaching`，按步骤 metadata.classification 联查，缺条目回退 default 并注明"通用说明"；教学依据经 sources 注册表渲染为外链（DOI 自动补全）。
4. **文献教学页**（新 tab）：渲染 `/api/literature-teaching` 的 claim 政策横幅、统计 chips、15 张文献卡（标题链接、年份期刊、证据范围、claim_status、路线目标、关键步骤、报告条件、危险标记）与 1 条反应课程（原理/边界/来源定位/条件表）；全部值原样呈现。
5. **状态页**：新增 profiles 卡片区（quick/balanced/strict 各阶段预算、包络、候选池与策略权重，来自 `/api/status.profiles`）。
6. **独立性收口**：grep 复核 `flavoretro/ web/ configs/ tests/ scripts/` 无 `retro_synthesis` 与 `/home/ljx` 运行时引用（command-0040.log）；教学配置文件入仓后，工作台内容不再依赖旧项目文件。
7. **证据边界**：界面无升格措辞；所有候选语义（surrogate/partial、非实验验证）原样呈现，符合 ADR-002 与任务合同禁止项。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| `.venv/bin/python -B -m unittest discover -s tests`（command-0034、0035） | 28 项全部通过（含新增 test_web 3 项），两次运行均 OK |
| 端点逐一 curl（command-0037） | /api/health、/api/status、/api/targets、/api/teaching、/api/literature-teaching、/api/records?kind=paper 全部 200；teaching 含 27 条分类、literature 含 15 卡 + 1 课程 |
| `scripts/browser_check.py`（command-0039，产物 browser-fc15e727） | 通过：实时双阶段搜索、路线卡 >0、库存"共 49 条"、记录详情、文献卡 15 张、治理统计 4 项、移动端 390px 无溢出、非法 SMILES 得 400、JS 零错误 |
| 教学块渲染抽查（真实平衡搜索，非合同命令） | 教学块 17 处渲染、无 JS 错误；截图核对路线解读与文献教学页版式 |
| 独立性 grep（command-0040） | 运行时代码无旧项目引用 |
| configs 两文件 SHA-256 与旧项目源文件 | 三方一致（源 = staging = 仓库） |

## 与任务合同的偏差

- 8766 端口被旧代码的滞留开发服务器（pid 2610817，当日更早会话启动）占用，首次端点验收打到旧进程导致新端点 404（command-0036）。处置：杀死该滞留进程后以新代码重启（合同未列此操作，属恢复验证前提的必要操作；服务器为项目自有开发进程，非用户数据）。
- `browser_check.py` 首次运行（command-0038，rc=1）在资源页"共 49 条"等待处超时；人工单独复现资源页正常，重跑全套通过（command-0039）。疑似一次性时序抖动，未再复现，未改代码。
- staging 目录的使用未在合同"允许项"逐字列明，沿用 TASK-009 先例（合同已允许"全部写入经 operate.py 执行记录"），暂存文件非交付物。

## 已发现但未修改的问题

- **教学条目 classification 映射缺口**：`configs/teaching_guidance.json` 的命名家族键（o_glycoside_cleavage 等）源自旧项目定制模板；新运行时使用 uspto/ringbreaker 模板，metadata.classification 为数值代码，命名家族条目暂不会命中，前端回退 default/"0.0 Unrecognized" 条目（界面已正确标注）。按合同停止条件保留并记录，不改 worker 强行对齐。补齐映射列入 WORKBENCH_ROADMAP P3。
- **events.jsonl 存在一条 2026-09-22 的误记行**（task 字段为 "--help"，旧机器上 TASK-009 之后的操作事故）：追加式日志不删改，在此标注。
- STATE.md 原"27 个空白格式化文件"备注已过期：那些改动已随 f272c36 提交；服务器端 `git status` 无该噪音（挂载视图下的 mode 位变化为挂载手段产物，非仓库事实）。本次已在 STATE.md 更正。

## 遗留风险

- `/api/teaching` 与 `/api/literature-teaching` 为原样透传静态配置，无版本协商；配置文件扩充时需同步前端字段假设（当前前端对缺字段跳过处理，风险低）。
- 文献教学层内容来自机器抽取登记（claim_status 含 pending 字样），界面已原样标注；扩充课程前需人工结构复核（门槛 human_structure_reviewed）。
- 浏览器验收为工程验收，不构成人体可用性结论（report.json scope 已注明）。

## 仓库与 CI 状态

- 无 CI；验证依赖本地 unittest 与 browser_check（结果见上表）。
- 本任务全部写入与命令在 `operations/events.jsonl` 可查（TASK-010 前缀，含前后 SHA-256；命令输出存 operations/command-0034…0040.log，本机证据不入 Git）。
- Git 提交：见本节下方提交记录；`data/`、`outputs/`、`operations/.staging-task010/` 不入 Git。

## 建议的下一任务

- 按 [../WORKBENCH_ROADMAP.md](../WORKBENCH_ROADMAP.md) 推进：P1（糖苷拓扑审计结果接入界面呈现，不改搜索语义）或 P3（教学条目与数值 classification 的映射补齐）均为低风险和候选；P2（黄酮苷有效性判断接入搜索）需先冻结定义与评测协议，建议独立 TASK 并人工批准。
- 工程向：`.venv` 独立环境重建验证（现依赖 retro Conda 环境的 system-site-packages，见 environment/README.md）。
