# TASK-005：工作台与新运行比较

## 合同元数据

- 任务 ID：TASK-005
- 状态：Completed
- 批准：Cano（agent_delegated，2026-09-21）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 文档形态：TASK-009 由速记体扩写，范围与结论未变
- 执行时段：2026-09-21 09:50—09:58（与 TASK-004 并行；依赖 TASK-004 真实 smoke 验证，完成后一起集成验收）

## 目标

实现独立中文 Web 工作台与评估入口：中文浏览器界面、资源筛选和原字段详情、来源/治理状态、JSON API、结构 SVG、逐次结果导出；开发目标×seed×原生/优化树短预算对照；正式预检拒绝未证资产。借鉴旧 web 的共享服务、结构预览、路线/证据展示与实时标签，重新实现简洁界面，不整体复制旧前端状态机。

## 背景

旧系统为 AiZynthFinder 4.4.1 MCTS 平台，复盘结论“候选闭合≠化学可行”（13 靶标 solved 9/13 但 evidence-closed 0；reward 优先候选 solved 30/39 而 actionable 0/39）。因此工作台必须展示来源/治理状态与限制，不暗示生产就绪；所有比较必须本次新跑，不复用旧运行数字。前端只借鉴旧 web 的交互概念，不复制其状态机。

## 范围

### 允许项

- 新建 `flavoretro/web.py`（标准库 HTTP 服务，本地工作台）；
- 新建 `web/index.html`、`web/style.css`、`web/app.js`；
- 新建 `flavoretro/evaluation.py`（开发对照运行器+正式 preflight）；
- 新建 `scripts/browser_check.py`（Playwright Chromium 验收）；
- 在 `.venv` 内安装 playwright==1.63.0（不动共享环境）；
- 产物写入 `outputs/evaluation/` 与浏览器验收证据目录。

### 禁止项

- 部署到公网；
- 修改共享 Conda 环境；
- 复用历史运行结果充当本次比较；
- 把开发对照解释为化学优越性结论；
- 普通搜索调用 `GET /api/runs/<run_id>`（该端点仅限显式读取已存运行）。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途 |
| --- | --- | --- |
| `flavoretro/` | `web.py` | 标准库 HTTP 本地工作台：共享实时服务、有界资源端点 |
| | `evaluation.py` | 新跑有界开发对照；不回放历史验收 |
| `web/` | `index.html`、`style.css`、`app.js` | 中文单页界面、结构预览、路线/证据展示、实时标签 |
| `scripts/` | `browser_check.py` | Playwright Chromium 工程验收 |
| `outputs/evaluation/` | `development-*` | 开发对照输出，失败 cell 保留 |

## 非目标

- 部署到公网、5 人用户评价；
- 已审核生产模板；
- 独立标签和正式 360 cell 盲测（正式盲测执行器尚未交付）。

## 必须执行的操作

1. 实现 API：`GET /api/health`、`/api/status`、`/api/targets`、`/api/records`（kind/q/offset/limit≤100）、`/api/molecule`（本地 RDKit SVG）；`POST /api/search`（smiles/mode/seed/seconds/iterations/candidate_stock）；`GET /api/runs/<run_id>`（显式读已存运行、校验结果哈希、execution_source=explicit_saved_run；普通搜索从不调用此端点）。429=另一请求执行中。
2. 开发对照矩阵：3 靶标（hesperidin/hesperetin/quercetin）×2 引擎（native/optimized）×2 seed=12 cell，全部新跑、失败 cell 保留；claim 原文“Engineering development observation only; no chemical superiority conclusion”。
3. Playwright 浏览器验收：Chromium desktop 1440×1000 / mobile 390×844、js_errors=[]、live_search=true、invalid_http_status=400、overflow=false、resource_detail=true、two_phases=true；scope 声明：本机浏览器工程验收，非真人可用性评价。

## 验收标准

- [x] `node --check web/app.js`（command-0010，rc=0）。
- [x] `python -m venv --system-site-packages .venv`（command-0011）；`pip install playwright==1.63.0`（含 pyee 13.0.1，command-0013，仅装在 .venv，不改共享环境）。
- [x] `flavoretro.evaluation --development`：12/12 cell 完成、failures 0（command-0014，输出 outputs/evaluation/development-59b2f86e…）；全部 evidence_closed=0。
- [x] 浏览器验收：首次失败（command-0015，rc=1：等待 select option visible 超时 30s，option 实为 attached 但 hidden）→ validation_fix 修等待逻辑、保留失败目录、重跑到新证据目录（command-0018 通过）；再次浏览器验收 command-0022 通过。
- [x] 修复后第二次 evaluation：12/12（command-0023，输出 development-e0b94fc8818a40038f5da0c340339309）。
- [x] 真实 HTTP/浏览器请求、错误输入（400）、桌面/移动无溢出、两阶段显示、资源记录可追踪；所有比较新跑，不主张科学收益。

### 执行期事件（并入合同事实）

- acceptance_correction：结构预览在表单变更后可能仍显示旧 SMILES→提交时刷新为被搜索分子。

## 验证

```bash
node --check web/app.js                          # command-0010，rc=0
python -m flavoretro.evaluation --development    # command-0014/0023，12/12，failures 0
python scripts/browser_check.py                  # command-0018/0022 通过
```

## 停止条件

- 需修改共享环境才能安装浏览器依赖；
- 浏览器验收修复需要删除失败证据；
- 开发对照被要求表述为化学结论。

## 必须提交的报告

生成同编号 REPORT-005，记录命令日志（command-0010—0023 中属本任务者）、失败目录与重跑证据、scope 声明，并更新 `STATE.md`。
