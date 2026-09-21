# TASK-001：独立根与治理骨架

## 合同元数据

- 任务 ID：TASK-001
- 状态：Completed
- 批准：Cano（agent_delegated，2026-09-21，用户授权本次重建自主逐项决策）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 文档形态：TASK-009 由速记体扩写，范围与结论未变

## 目标

在触碰任何数据之前，为新仓库 `/home/ljx/FlavoRetro` 建立完整的治理骨架：唯一职责的 PROJECT/STATE/ARCHITECTURE 根文档、TASK/REPORT/ADR 三层文档体系、逐次写入与命令日志（`scripts/operate.py` + `operations/`）、旧库历史只读基线，以及独立 Git 仓库初始化。完成判定：上述文档与工具全部就位且职责互不重叠，旧库全量路径基线已保存，新仓库可在 `main` 分支接受后续提交。

## 背景

本仓库是旧项目 `/home/ljx/retro_synthesis` 的独立重建，不是原地改造。旧库事实（来源：旧库复盘 `docs/reports/260920-pre_refactor_project_retrospective.md` 与 `maintenance/STATUS.md`，两者后经 TASK-002 复制到本仓库 `data/raw/legacy/`）：

- 旧库规模 5.6 GB（旧库磁盘盘点 29,698 个文件）、131 个 Python 文件（复盘快照第 317 行）；最终状态为 `rebuild-foundation` / `candidate-not-production`——production 模板晋级 0 条、库存晋级 0 条。
- 旧系统曾积累 49 条分层库存（18 strict / 2 trusted / 29 virtual）、35.2M 行 ZINC 快照、15 篇 DOI 文献卡、150 条教学模板（全部为 candidate）、67 项测试。
- 复盘核心结论：旧库把候选、工程通过、化学证据混为一谈——`parser-ready ≠ runtime-active ≠ chemistry-reviewed`；solved 数量多 ≠ 化学有效；标题命中 ≠ 原文确认；测试全绿 ≠ 研究完成。

因此新仓库必须先建立"候选、数据库身份、图回放、工程测试、供应证据、独立化学验证不得混为一谈"的治理结构，再准入任何数据。UNDERSTAND 阶段实际读取：旧库复盘报告第 1—12 节、`test_contract_catalog.md`、`inventory.json` 全量，以及 CondRxnBench 的 AGENTS/PROJECT/STATE/ARCHITECTURE 与全部 `docs/tasks`（仅作文档格式样板，未修改 CondRxnBench 任何文件）。批准采用 CondRxnBench 的文档职责划分，但覆盖其"等待人工批准"条款，理由是用户本次明确授权 agent 自主逐项决策。

## 范围

### 允许项

- 在新仓库根创建治理文档与审计工具：`PROJECT.md`、`AGENTS.md`、`ARCHITECTURE.md`、`STATE.md`、`.gitignore`。
- 创建 `docs/adr/ADR-001-independent-rebuild.md`（独立重建的长期决定）、本合同 `docs/tasks/TASK-001-governance.md`、事后报告 `docs/reports/REPORT-001-governance.md`。
- 创建 `scripts/operate.py`（逐次写入/命令登记）与 `scripts/history_guard.py`（历史基线快照；该脚本后于 TASK-008 归档至 `operations/archive/`）。
- 创建 `operations/` 日志体系：`command-*.log`、`history-before.json`，并由 operate.py 自登记 bootstrap 事件（reason: `User authorized new-root creation; bootstrap journal self-registration`）。
- 在新仓库执行 `git init -b main`，建立本地仓库（当时无远端）。

### 禁止项

- 对 `/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 的任何写入；旧库保持完整只读。
- 复制、移动或解析任何旧库数据文件（数据准入属 TASK-002）。
- 自动确认任何化学事实；不得把工程检查通过当作化学审核。
- 把旧库基线文件 `operations/history-before.json` 纳入 Git（由 `.gitignore` 排除）。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| 根目录（项目治理入口） | PROJECT.md | 新增：目标、三条工作线、硬约束、许可约定 |
| 根目录 | AGENTS.md | 新增：读序、UNDERSTAND→…→UPDATE STATE 流程、禁止事项 |
| 根目录 | ARCHITECTURE.md | 新增：目录职责与产物登记，保证每项职责唯一归属 |
| 根目录 | STATE.md | 新增：只保存当前状态（历史留在 TASK/REPORT） |
| 根目录 | .gitignore | 新增：排除数据、输出与治理日志快照 |
| docs/adr（长期决定） | ADR-001-independent-rebuild.md | 新增：记录"独立重建而非原地改造"的决定与理由 |
| docs/tasks（事前合同） | TASK-001-governance.md | 新增：本合同（速记体，TASK-009 扩写为详版） |
| docs/reports（事后事实） | REPORT-001-governance.md | 新增：本任务执行事实报告 |
| scripts（活动工具） | operate.py | 新增：写入与命令的治理日志登记，bootstrap 自登记 |
| scripts | history_guard.py | 新增：旧库路径基线快照/比对（TASK-008 归档） |
| operations（治理日志） | command-0001.log、command-0002.log | 新增：`git init` 与基线快照的命令日志 |
| operations | history-before.json | 新增：旧库 33,146 条路径基线（Git 忽略） |

## 非目标

- 不复制、不解析旧库任何数据内容（属 TASK-002）。
- 不重写或修复旧库代码，不评价旧系统的化学结论。
- 不建立 Python 包、测试或搜索功能。
- 不配置远端仓库或 CI。

## 必须执行的操作

1. 按读序完成 UNDERSTAND：旧库复盘 1—12 节、`test_contract_catalog.md`、`inventory.json` 全量；CondRxnBench 治理文档与全部 TASK 作格式样板。
2. 编写并落盘治理文档 PROJECT/AGENTS/ARCHITECTURE/STATE、`.gitignore`、ADR-001、TASK-001。
3. 实现 `scripts/operate.py` 与 `scripts/history_guard.py`；operate.py 自登记 bootstrap 事件。
4. 执行 `git init -b main` 初始化新仓库（记入 command-0001.log）。
5. 执行 `python scripts/history_guard.py before` 保存旧库基线：33,146 条路径记录（文件记 sha256/size/mtime，符号链接记目标，目录不比较 mtime），输出 `operations/history-before.json`（记入 command-0002.log）。
6. 撰写 REPORT-001，更新 STATE.md。

## 验收标准

- [x] 背景资料读取有清单（旧库复盘、test_contract_catalog、inventory.json、CondRxnBench 样板均记录在案）。
- [x] 旧库基线已保存：`operations/history-before.json` 含 33,146 条路径记录。
- [x] 新库 Git 已初始化（`main` 分支，本地，无远端）。
- [x] 文档职责唯一：PROJECT/STATE/ARCHITECTURE/TASK/REPORT/ADR/operate 日志分工不重叠。

## 验证

```bash
# 实际执行（2026-09-21 09:39—09:40 本地），日志在 operations/：
git init -b main                          # operations/command-0001.log，rc=0
python scripts/history_guard.py before    # operations/command-0002.log，rc=0
```

## 停止条件

- 治理工作产生对旧库的历史写入需要：停止并报告。
- 输入漂移（基线快照期间旧库内容变化）：停止并报告。
- 局部不确定性（如个别路径无法读取）：保留记录后继续，不阻断整体。

## 必须提交的报告

完成、部分完成或失败时，均生成同编号 `docs/reports/REPORT-001-governance.md` 并更新 `STATE.md`（已执行）。
