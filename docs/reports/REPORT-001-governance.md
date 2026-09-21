# REPORT-001：独立根治理入口与历史目录基线

## 对应任务

- 任务 ID：TASK-001
- 任务文件：[`docs/tasks/TASK-001-governance.md`](../tasks/TASK-001-governance.md)
- 状态：Completed（完成）
- 批准：Cano agent_delegated（2026-09-21，依据用户本次明确授权自主逐项决策）；非人工科学审核
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：aa012ca（docs/ 治理与文档）/ 1f027a8（flavoretro/、tests/、web/、configs/）/ 2b305a4（scripts/、metadata/、environment/、operations/）；TASK-008 分层初始提交时入库
- 执行窗口：2026-09-21 09:39—09:40（本机时间，对应 operations/events.jsonl 中 01:39 UTC 时间戳）
- 文档形态：本文件由 TASK-009 将速记体原文扩写为详细格式，事实未变
- 阅读提示：本报告面向未接触过旧项目的研究者；文中"旧库"指 `/home/ljx/retro_synthesis`，"样板库"指 `/home/ljx/CondRxnBench`

## 改动文件

本任务为仓库奠基，下表文件均为新建；迁移/删除不适用。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| 仓库根目录：项目治理入口 | `PROJECT.md` | 新建；登记稳定目标、硬约束与非目标（尤其证据边界：候选不等于已验证） |
| 仓库根目录：项目治理入口 | `AGENTS.md` | 新建；协作规范：阅读顺序、UNDERSTAND→SPECIFY→APPROVE→EXECUTE→VERIFY→REPORT→UPDATE STATE 流程、禁止项 |
| 仓库根目录：项目治理入口 | `ARCHITECTURE.md` | 新建；责任与产物登记表，新增产物先查表以禁止重复事实源 |
| 仓库根目录：项目治理入口 | `STATE.md` | 新建；当前事实（本任务内两次写入：建立时与收尾时各一次） |
| 仓库根目录：版本控制配置 | `.gitignore` | 新建；排除 `data/`、`outputs/`、`__pycache__`、`.venv`、`operations/*.log`、`operations/*.json` 等 |
| `docs/adr/`：长期设计理由 | `ADR-001-independent-rebuild.md` | 新建；独立根决定（不与旧库共根、不整体复制旧仓库） |
| `docs/tasks/`：事前合同 | `TASK-001-governance.md` | 新建；本任务的批准合同 |
| `docs/reports/`：事后证据 | `REPORT-001-governance.md` | 新建；本报告（速记原文；TASK-009 扩写为当前详细版） |
| `scripts/`：可复现编排与工具 | `operate.py` | 新建；追加式治理日志：`write` 记录写入前后 SHA-256，`run` 记录命令行与日志文件 |
| `scripts/`：可复现编排与工具 | `history_guard.py` | 新建；历史目录基线快照与对比脚本（TASK-008 已归档为 `operations/archive/history_guard-task-001.py`，`scripts/` 下不再保留） |
| `operations/`：治理日志（不入 Git） | `events.jsonl` | 新建；追加式事件日志，首批事件由本任务写入（bootstrap、understand、write、command 等） |
| `operations/`：治理日志（不入 Git） | `history-before.json` | 新建；33,146 条历史路径基线 |
| `operations/`：治理日志（不入 Git） | `command-0001.log` | 新建；`git init` 命令完整输出 |
| `operations/`：治理日志（不入 Git） | `command-0002.log` | 新建；`history_guard.py before` 命令完整输出 |

生成但不进入 Git 的文件汇总（均位于 `operations/`，承担治理审计职责，被 `.gitignore` 排除）：`events.jsonl`、`history-before.json`、`command-0001.log`、`command-0002.log`。

## 实际改动

1. 背景：旧库 `/home/ljx/retro_synthesis` 规模 5.6 GB（旧库磁盘盘点 29,698 个文件）、131 个 Python 文件；其复盘报告揭示候选数据、工程测试通过与化学有效性证据被混为一谈。因此新项目在独立根 `/home/ljx/FlavoRetro` 重建，且治理设施先于一切数据与代码落地。
2. 建立 `PROJECT.md`：登记稳定目标、硬约束与非目标，明确候选、工程通过、化学证据三者不得混淆的证据边界。
3. 建立 `AGENTS.md`：规定文档阅读顺序与逐任务批准流程，每个任务先明确范围、理由、验收与停止条件。
4. 建立 `ARCHITECTURE.md`：以登记表维持文档职责唯一，新增产物必须先查表，禁止重复事实源。
5. 建立 `STATE.md`：只保存当前事实；本任务内写入两次（建立时与收尾时）。
6. 以 `ADR-001` 记录独立根决定：原地重构违反用户硬约束、整体复制旧仓库会带入隐式依赖与旧结论，两个备选方案均不采用。
7. 批准方式：TASK-001 由 Cano 于 2026-09-21 批准，记录为 agent_delegated（依据用户本次明确授权自主逐项决策），非人工科学审核；文档职责划分采用 CondRxnBench 样板，但覆盖其等待人工条款。
8. 建立 `scripts/operate.py` 追加式治理日志：此后每次写入记录前后 SHA-256，每次命令记录命令行与输出日志，全部追加进 `operations/events.jsonl`；`operate.py` 自身与 `operations/` 目录经 bootstrap 事件自我登记。
9. 建立 `scripts/history_guard.py` 并对旧库执行基线快照，生成 `operations/history-before.json` 共 33,146 条，按条目类型分别记录：
   - 文件：sha256 / size / mtime；
   - 符号链接：链接目标；
   - 目录：仅 mode / kind，不比较 mtime。
10. 在新目录执行 `git init -b main` 初始化仓库，未配置远端。
11. `.gitignore` 从首个文件起即排除数据载荷（`data/`、`outputs/`）与本机日志（`operations/*.log`、`operations/*.json`），保证其永不入库。
12. `understand` 事件记录已读清单：旧库复盘报告第 1—12 节、`test_contract_catalog.md`、`inventory.json` 全量解析、CondRxnBench 治理文件全套（AGENTS/PROJECT/STATE/ARCHITECTURE 及全部 docs/tasks）。读取的样板只作为设计参考，未修改 CondRxnBench 任何文件。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| `git init -b main`（`operations/command-0001.log`） | rc=0；仓库初始化于 `main` 分支。该日志为本机日志，被 `.gitignore` 排除不入 Git，关键输出已内联 |
| `python scripts/history_guard.py before`（`operations/command-0002.log`） | rc=0；生成 `operations/history-before.json` 基线 33,146 条。该日志为本机日志，被 `.gitignore` 排除不入 Git，关键输出已内联 |
| 治理日志自我登记 | 通过：`operations/events.jsonl` 以 `bootstrap` 事件登记 `scripts/operate.py` 与 `operations/`，随后 13 条 `write`、2 条 `command_start`/`command_end`、`history_baseline`、`understand` 事件齐全 |
| 背景资料已读清单 | 通过：`understand` 事件逐项记录（见"实际改动"第 12 条） |
| 对 `/home/ljx/CondRxnBench` 只读 | 通过：全程无对该目录的写入事件 |
| 对 `/home/ljx/retro_synthesis` 只读 | 通过：`understand` 事件声明只读操作（pwd/rg/cat/sed/Python 检查/du/df），未导入历史代码；`history_guard.py before` 仅读取 |
| 仓库远端配置 | 通过：`git init` 后未添加任何远端，无推送目标 |
| 文档职责唯一性 | 通过：四件套职责分别登记于 `ARCHITECTURE.md`，无重叠条目 |

TASK-001 合同的四条验收（背景资料读取有清单、旧库基线已保存、新库 Git 初始化、文档职责唯一）与上表逐项对应，全部通过。

## 与任务合同的偏差

无。

## 已发现但未修改的问题

无记录。

## 遗留风险

- `operations/history-before.json` 与 `operations/command-*.log` 被 `.gitignore` 排除、不入 Git；异地复核需重新生成基线，而重新生成的条件已不存在——旧库仅以只读形式保留在本机 `/home/ljx/retro_synthesis`，他机无此目录。
- 文档职责唯一性靠 `ARCHITECTURE.md` 登记表人工维持，无自动检查机制。

## 仓库与 CI 状态

本报告所述操作发生时（2026-09-21 上午），仓库已执行 `git init -b main`，但尚无任何提交、未配置远端、无 CI。本任务涉及的全部已跟踪文件随 TASK-008 的分层初始提交入库（aa012ca / 1f027a8 / 2b305a4）。`operations/command-*.log` 与 `operations/*.json` 被 `.gitignore` 排除，仅存在于本机。

## 建议的下一任务

TASK-002：资源快照与逐项来源登记（从只读旧库准入选定来源文件并逐文件登记许可边界）。按流程不自动开始。
