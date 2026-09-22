# TASK-010：Web 工作台完整化、布局修复与项目独立收口

## 合同元数据

- 任务 ID：TASK-010
- 状态：Approved
- 基线分支：main
- 基线提交：f272c36（doc: 可读性提升）
- 人工负责人：项目所有者（ljx）
- 执行者：Kimi（Kimi Work 会话，经 ssh cano 在远程执行验证）
- 修改预算：`web/` 三个前端文件、`flavoretro/web.py`、`configs/`（新增两个教学配置）、`tests/`（新增 web 端点测试）、`scripts/browser_check.py`、根级 `STATE.md`、`docs/` 导航与路线图、`docs/adr/` 新增一份；不动 `flavoretro/` 其余模块、`data/`、`outputs/`、`metadata/`、旧项目目录
- 批准：Kimi agent_delegated（2026-09-22）；依据：AGENTS.md 记载的本次用户授予 Cano 自主审批权（批准记录写 agent_delegated），以及用户在本会话的直接指令（"web 端内容没有完整移植过来……页面统一顶栏不固定……路线探索页面架构侧栏未顶到两边，而且左右滑动不是独立的……确保工作完成后这个项目可以独立于之前的 retro_synthesis 项目存在……建立逆合成工作台，在 aizynthfinder 基础上优化，加入基于黄酮苷针对性的有效性判断，最后加入文献教学模式"）

## 目标

把 web 端从骨架补齐为完整的逆合成研究工作台界面：移植旧项目的路线解读与教学解释内容，新增文献教学页；修复顶栏不固定与探索页双栏布局缺陷；收口项目独立性（文档路径、git 状态、教学配置文件入仓）；同步仓库文档，使新来者不查旧项目即可了解成果、问题与下一步方向。完成判定：全部验收标准通过，单元测试与浏览器验收在 cano 远程环境通过。

## 背景

- 旧项目 `retro_synthesis/web/`（index.html 345 行、app.js 约 2400 行、app.css 664 行）为单页富界面：路线解读（评分构成、反应可行性、末端原料证据、逐步反应说明）、教学解释模式（24 个反应家族的中文教学文案，存于旧 `config/product/teaching_guidance.json`）、文献教学层（15 张文献卡与反应课程，存于旧 `config/product/literature_teaching_layer.json`，旧后端有接口但前端从未渲染）、D3 树与 JSME 编辑器。新项目 `web/` 仅 553 行骨架，上述内容均未移植。
- 新后端搜索响应已携带路线解读所需字段：`route.cost` 四项分项与暂定分数、`route.closure`、树节点 `closure`/`evidence_basis`/`structure_check`/`hazard`、反应节点 `metadata.classification`/`template`/`policy_probability`。教学文案可按 `classification` 在前端联查，无需改动搜索逻辑。
- 布局缺陷：顶栏随页面滚动丢失；探索页 `.workspace` 侧栏未撑满视口高度，左右栏共用一个滚动上下文。
- 独立性现状：`flavoretro/` 代码无任何旧项目引用（已全仓 grep 核实）；运行与开发均在 cano 服务器（`/home/ljx/FlavoRetro`）进行，`README.md` 启动路径正确，不改；`metadata/sources.json` 的 `source_root` 仅为出处元数据，运行时不读；STATE.md 关于"27 个空白格式化文件"的备注已过期（实际已随 f272c36 提交，当前工作区噪音为挂载导致的 mode 位变化与一条 events.jsonl 误记）。独立性的剩余缺口是：教学配置文件仍在旧项目、文档对"成果/问题/下一步"的呈现不够集中。
- 旧 `config/product/` 下教学配置文件为项目原创内容，按"只复制不移动"原则可复制入新项目 `configs/` 并登记来源与 SHA-256。

## 范围

### 允许项

- `web/index.html`、`web/app.js`、`web/style.css` 的重写与扩充。
- `flavoretro/web.py` 新增两个 GET 端点：`/api/teaching`（读 `configs/teaching_guidance.json`）、`/api/literature-teaching`（读 `configs/literature_teaching_layer.json`）。
- `configs/` 新增 `teaching_guidance.json`、`literature_teaching_layer.json`（从 `/home/ljx/retro_synthesis/config/product/` 复制，只复制不移动，记录来源路径与 SHA-256）。
- `tests/` 新增 web 端点单元测试（端点返回结构、教学边界字段、错误路径）。
- `scripts/browser_check.py` 选择子与断言适配新页面结构。
- `STATE.md`、`docs/README.md`、`docs/HUMAN_TAKEOVER.md` 的一致性更新；新增 `docs/WORKBENCH_ROADMAP.md`（工作台方向与下一阶段候选）；`docs/adr/` 新增 ADR-004（教学与文献层迁入及 web 信息架构决定）。
- git 工作区噪音处置（mode 位变化与 events.jsonl 误记的核实、说明与提交策略），限本任务 REPORT 记录事实。
- 全部写入与命令经 `scripts/operate.py TASK-010` 在 cano 服务器上执行记录（`/Volumes/cano` 挂载仅用于访问，不作为运行环境）。

### 禁止项

- `flavoretro/` 中 `search.py`、`worker.py`、`policies.py`、`resources.py`、`contracts.py`、`service.py`、`topology.py`、`evaluation.py`、`cli.py` 的任何改动。
- `data/`、`outputs/`、`metadata/` 的任何改动；`data/derived` 活动指针切换维持搁置。
- 对 `/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 的任何写入；不在旧目录运行可能写缓存的代码。
- 移植 D3 树视图与 JSME 结构编辑器（列入 WORKBENCH_ROADMAP 后续方向）。
- 界面措辞升格：不得出现"证据闭合/可执行/已验证可购买"等违背候选语义的表述；`evidence_closed:false`、`actionable:false`、`release_ready:false` 的后端事实必须原样呈现。
- 把候选、数据库身份、拓扑审计候选、工程测试、供应证据混为一谈（教学页与路线解读须保留证据边界文案）。
- 推送远程、创建 GitHub 仓库、替换 git 身份。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| web（浏览器工作台） | index.html、app.js、style.css | 重写扩充：四页架构（路线探索/资源与证据/文献教学/项目状态）、顶栏固定、双栏独立滚动、路线解读、教学解释开关 |
| flavoretro（共享 API 逻辑） | web.py | 新增 /api/teaching 与 /api/literature-teaching 两个 GET 端点 |
| configs（运行配置） | teaching_guidance.json、literature_teaching_layer.json | 新增：复制自旧项目 config/product/，登记来源与 SHA-256 |
| tests（测试合同） | test_web.py（新增） | 两个新端点的结构与边界测试 |
| scripts（活动工具） | browser_check.py | 适配新页面选择子与断言 |
| docs/adr（长期决定） | ADR-004-teaching-layer-and-web-architecture.md | 新增：教学层迁入来源与 web 信息架构决定 |
| docs（文档导航） | WORKBENCH_ROADMAP.md（新增）、README.md、HUMAN_TAKEOVER.md | 工作台方向路线图；导航与接管指南同步 |
| 根级 | STATE.md | 状态更新至本任务完成后事实 |

## 非目标

- 不改变搜索、评分、资源准入的任何语义；不把黄酮苷有效性判断接入搜索逻辑（本次仅在界面呈现已有的 closure/hazard/拓扑审计事实，接入搜索属后续任务）。
- 不做形式盲测、不晋级任何候选记录、不补充化学验证。
- 不处理 TASK-007-P1（所有者搁置）。
- 不移植旧项目的冻结快照、/api/experiments、PubChem 联查、国际化字典（列入路线图评估）。

## 必须执行的操作

1. 复制两个教学配置文件入 `configs/`，经 `operate.py --write` 登记，记录来源 SHA-256。
2. `flavoretro/web.py` 新增两个 GET 端点；新增 `tests/test_web.py`。
3. 重写 `web/` 三文件实现目标界面与布局修复。
4. 适配 `scripts/browser_check.py`。
5. 在 cano 远程依次验证：单元测试全套、启动服务 curl 全部端点、browser_check、一次 quick 实时搜索核对路线解读渲染。
6. 写 ADR-004、`docs/WORKBENCH_ROADMAP.md`，更新 `README.md`、`STATE.md`、`docs/README.md`、`docs/HUMAN_TAKEOVER.md`。
7. 核实并处置 git 工作区噪音；写 REPORT-010，更新 STATE，Git 提交。

## 验收标准

- [ ] 顶栏在三个页面滚动时保持固定。
- [ ] 路线探索页侧栏顶满视口（顶到固定顶栏下缘与视口底边），左右栏各自独立滚动。
- [ ] 路线卡片呈现：评分构成（分项与公式）、closure 徽章、末端原料证据（evidence_basis/structure_check/hazard）、逐步反应卡片（模板与 classification 中文标签、policy 概率）。
- [ ] 教学解释开关控制逐步教学块显隐，状态存入 localStorage；教学文案来自 `/api/teaching`，缺 classification 时回退 default 条目。
- [ ] 文献教学页渲染 `/api/literature-teaching` 全部文献卡与反应课程，并原样标注 claim_status 与证据边界。
- [ ] 界面无升格措辞；`evidence_closed:false` 等事实原样可见。
- [ ] `configs/` 两个新文件与旧来源 SHA-256 一致，events.jsonl 有登记。
- [ ] 仓库内无运行时旧项目依赖（grep 复核）；README 启动指令与 cano 实际路径一致（不改）。
- [ ] `.venv/bin/python -B -m unittest discover -s tests` 在 cano 通过（含新增 test_web）。
- [ ] `scripts/browser_check.py` 在 cano 通过。
- [ ] 所有写入在 `operations/events.jsonl` 可查（含前后 SHA-256）。

## 验证

```bash
# 以下均经 scripts/operate.py TASK-010 包装记录，在 cano 远程 ~/FlavoRetro 执行
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B -m flavoretro.web --host 127.0.0.1 --port 8766 &
for p in /api/health /api/status /api/targets /api/teaching /api/literature-teaching "/api/records?kind=paper" ; do curl -sf "http://127.0.0.1:8766$p" -o /dev/null && echo "OK $p"; done
.venv/bin/python -B scripts/browser_check.py
grep -rn "retro_synthesis\|/home/ljx" --include="*.py" --include="*.js" --include="*.html" --include="*.json" flavoretro/ web/ configs/ tests/ scripts/ | grep -v "operations/" || echo "no runtime legacy reference"
```

## 停止条件

- 旧教学配置的 classification 键与新后端模板 metadata 体系对不上：保留文件与端点，在 REPORT 标注映射缺口，禁止改 worker 强行对齐。
- browser_check.py 需改动超出选择子适配（如流程假设变化）：停止并报告，由所有者另批任务。
- cano 远程环境故障导致无法验证：已完成部分如实记录，任务按 Partial 报告。
- 单元测试失败且与本次改动无关：记录并报告，不借机修无关代码。

## 必须提交的报告

完成、部分完成或失败时，生成 `docs/reports/REPORT-010-web-completion.md` 并更新 `STATE.md`。
