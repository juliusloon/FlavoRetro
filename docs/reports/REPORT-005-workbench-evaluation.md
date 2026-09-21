# REPORT-005：工作台与新运行比较

## 对应任务

- 任务 ID：TASK-005
- 任务文件：`docs/tasks/TASK-005-workbench-evaluation.md`
- 状态：Completed（完成）
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：`aa012ca` / `1f027a8` / `2b305a4`（TASK-008 分层初始提交时入库）
- 文档形态：本报告为 TASK-009 补立（当时未单独成文），事实来源：`operations/events.jsonl` 与 `operations/command-0010…0023.log`
- 执行时段：2026-09-21 09:50—09:58

## 改动文件

生成但不进入 Git 的文件：`.venv/`（虚拟环境本体）、`outputs/evaluation/development-*.json`（开发对照输出），均为本机运行产物。

浏览器验收失败证据目录（首次 browser_check 失败的截图与状态）同样保留未删，用于复查失败现场。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `flavoretro/`：包本体 | `flavoretro/web.py` | 新建。标准库 HTTP 本地工作台，与 CLI 共享同一 `service.search`。端点：GET `/api/health`、`/api/status`、`/api/targets`、`/api/records`（limit≤100）、`/api/molecule`（本地 RDKit SVG）、POST `/api/search`、GET `/api/runs/<id>`（显式读取已保存运行、校验结果哈希、execution_source=explicit_saved_run；普通搜索从不调用）；429 表示另一请求正在执行。 |
| `web/`：前端静态资源 | `web/index.html` | 新建。中文三页界面骨架：路线探索 / 资源与证据 / 项目状态。 |
| `web/`：前端静态资源 | `web/style.css` | 新建。三页样式，含桌面与移动宽度适配。 |
| `web/`：前端静态资源 | `web/app.js` | 新建。前端交互逻辑：提交搜索、轮询状态、渲染路线与资源详情。 |
| `flavoretro/`：包本体 | `flavoretro/evaluation.py` | 新建。开发对照运行器（`--development`）与正式评测 preflight（无参数运行，拒绝未证资产）；正式盲测执行器未交付。 |
| `scripts/`：可复现脚本 | `scripts/browser_check.py` | 新建。Playwright Chromium 浏览器验收脚本，依赖 `.venv` 中的 playwright 1.63.0。 |

## 实际改动

本节面向未接触过旧项目的读者：TASK-005 在 TASK-004 的隔离搜索服务之上，补一层本机浏览器工作台和一套"开发对照"运行器。工作台只在本机回环地址服务，不部署公网；对照运行只回答"两套引擎在新跑、短预算下的工程行为"，不主张任何化学优劣结论。

1. 本地工作台完全用 Python 标准库 HTTP 实现（TASK-004 已确认 FastAPI 缺失），不引入新 Web 框架。
2. 工作台与 CLI 共享同一 `service.search`，因此 Web 提交同样是一请求一进程、新 MCTS、新 run ID。
3. 中文界面三页之"路线探索"：示例/输入 SMILES、结构预览、阶段显示、逐次结果导出。
4. 中文界面三页之"资源与证据"与"项目状态"：按类型/名字/SMILES/来源筛选、原字段详情、来源与治理状态展示。
5. 逐次结果导出为 JSON，包含配置、资产/代码哈希、阶段、候选和限制。
6. `GET /api/runs/<id>` 仅用于显式读取已保存运行：校验结果哈希，返回 execution_source=explicit_saved_run；普通搜索从不调用该端点。
7. 并发约束为单请求：另一个请求执行中时返回 HTTP 429。
8. 开发对照：3 个靶标（hesperidin / hesperetin / quercetin）× 2 个引擎（native / optimized）× 2 个 seed = 12 个 cell，全部本次新跑。
9. 12 个 cell 全部 evidence_closed=0，即没有任何路线闭合到已证实库存。
10. 对照输出的 claim 原文为 "Engineering development observation only; no chemical superiority conclusion"；失败 cell 保留。
11. 验收修正（acceptance_correction）：结构预览在表单变更后可能仍显示旧 SMILES，改为提交搜索时刷新为被搜索分子。
12. 浏览器验收字段（command-0018 与 command-0022 输出内联）：Chromium；desktop 1440×1000 / mobile 390×844；js_errors=[]；live_search=true；invalid_http_status=400；overflow=false；resource_detail=true；two_phases=true；scope="local browser engineering acceptance, not human usability"，即本机浏览器工程验收，非真人可用性评价。
13. 首次浏览器验收失败：等待 select option visible 超时 30 s，而 option 实际为 attached 但 hidden；validation_fix 修正等待逻辑，失败证据目录保留，重跑通过。
14. `.venv` 以 `--system-site-packages` 建立在共享 `retro` conda 环境之上，仅用于浏览器验收，不是独立环境，也未修改共享环境。
15. 正式评测入口仅交付 preflight：拒绝未证资产；正式 360 cell 盲测执行器未交付。

## 验证

注：`command-XXXX` 指 `operations/command-XXXX.log`，为本机日志，不入 Git，关键输出已内联于本表。两次开发对照与两次浏览器验收分别发生在验收修正之前与之后，形成前后对照。

| 命令或检查项 | 结果 |
| --- | --- |
| `node --check web/app.js`（command-0010） | rc=0：语法检查通过 |
| `python -m venv --system-site-packages .venv`（command-0011） | rc=0；.venv 依赖 retro conda 的 system-site-packages，非独立环境 |
| `.venv` 内 `pip install playwright`（command-0013） | rc=0：playwright 1.63.0 + pyee 13.0.1，仅装入 .venv，未改动共享 retro 环境 |
| `python -m flavoretro.evaluation --development`（command-0014） | rc=0：12/12 cell、failures 0；输出 `outputs/evaluation/development-59b2f86e…` |
| 上项 cell 内联示例（command-0014） | hesperidin：native seed 0 → status ok、routes 5、evidence_closed 0；optimized seed 0 → status ok、routes 2、evidence_closed 0 |
| `scripts/browser_check.py` 首次（command-0015） | rc=1：等待 select option visible 超时 30 s（option 实为 attached 但 hidden）；失败证据目录保留 |
| 修正等待逻辑后 browser_check 重跑（command-0018） | rc=0：验收字段全部通过（见"实际改动"第 12 条） |
| 再次浏览器验收（command-0022） | rc=0：字段与 command-0018 相同 |
| 修复后第二次 `--development`（command-0023） | rc=0：12/12；输出 `development-e0b94fc8818a40038f5da0c340339309` |
| 正式评测 preflight（无参数运行） | 拒绝未证资产；正式执行器未交付，未产生正式结果 |

## 与任务合同的偏差

任务合同要求对应 REPORT，当时未单独成文（原导航注记为"REPORT-004 末节 + 运行输出"），本报告为 TASK-009 补立；其余无偏差。

合同验收项（真实 HTTP/浏览器请求、错误输入、桌面/移动溢出、两阶段显示、资源记录可追踪；所有比较新跑，失败 cell 保留，不主张科学收益）逐项对应验证表：command-0022 覆盖真实浏览器请求、错误输入 400、桌面/移动无溢出、两阶段显示与资源详情；command-0014 与 command-0023 覆盖全部新跑的比较 cell。合同非目标（公网部署、5 人用户评价、已审核生产模板、独立标签、正式 360 cell 盲测）均未触碰。

## 已发现但未修改的问题

无记录。

## 遗留风险

- 无真人可用性评价（浏览器验收仅为工程验收）；
- 正式 360 cell 盲测未执行，执行器未交付；
- 开发对照仅 12 个 cell 的工程观察，不构成化学优劣结论证据；
- 浏览器偶发等待超时在 TASK-008 复现一次（重跑通过）；
- `.venv` 不是独立环境，其可用性依赖共享 `retro` conda 环境的 system-site-packages。

## 仓库与 CI 状态

报告时点仓库已 `git init` 但无任何提交、无远端 origin、无 CI；本报告所述文件随 TASK-008 分层初始提交入库。

验证所引用的 `command-XXXX.log` 为本机日志，不入 Git，关键输出已内联。`.venv/` 与浏览器验收证据目录属本机产物，同样不入 Git。

## 建议的下一任务

TASK-006（独立糖苷连接诊断）：工作台已能展示路线与证据，下一步把糖苷连接的结构审计独立成线，与搜索收益分开评价。仅为建议，不自动开始。
