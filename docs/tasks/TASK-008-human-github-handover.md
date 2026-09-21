# TASK-008：人接管友好化与 GitHub/论文导向整理

## 合同元数据

- 任务 ID：TASK-008
- 状态：已完成（Completed）
- 批准：Kimi（agent_delegated，2026-09-21）；依据用户 2026-09-21 直接指令。批准事件记录为 `task_approved`，`authority=kimi_agent_delegated`、`basis=user_direct_instruction_2026-09-21`。用户原话要点："constructively rebuild this project and make it highly human-take-over friendly, discarding some of the old python scripts that is no longer useful for our current goal and final paper work and github repository"
- 基线分支：main
- 基线提交：无（仓库首个提交形成于本任务）
- 人工负责人：项目所有者（ljx）
- 执行者：Kimi
- 修改预算：当时未设定
- 执行窗口：2026-09-21 10:45—10:51（与 TASK-007 之间约 44 分钟会话间隔）
- 文档形态：TASK-009 由速记体扩写，范围与结论未变

## 目标

把项目整理到人可低摩擦接管、可面向 GitHub 公开仓库与最终论文继续推进的状态：归档一次性脚本、补齐人接管与论文路线文档、修复死链、形成分层初始 Git 提交。

## 背景

TASK-001—007 由 agent 长时间自主完成，工程产物功能完整但"接手摩擦"高：README 有死链（指向不存在的 `docs/reports/REPORT-007-handoff.md` 与 `docs/README.md`）、缺少面向人的接管指南、缺少面向论文的目标路线、活动脚本中混有一次性迁移脚本。此前仓库没有任何 Git 提交。

## 范围

### 允许项

1. 归档一次性脚本：`scripts/admit.py`（TASK-002 数据准入，硬编码 `/home/ljx/retro_synthesis`）与 `scripts/history_guard.py`（TASK-001/006 历史目录完整性基线，同样机器相关）移至 `operations/archive/`，附归档说明；活动 `scripts/` 只保留可复用工具 `operate.py`（治理日志）、`smoke.py`（实时冒烟）、`browser_check.py`（浏览器验收，需 Playwright）。
2. 补人接管文档：新建 `docs/README.md`（全部文档导航）、`docs/HUMAN_TAKEOVER.md`（人接管指南）、`docs/PAPER_ROADMAP.md`（论文路线与未证事项清单）。
3. 修复失效链接：以 REPORT-008 承接交接汇总，导航由 `docs/README.md` 承担。
4. 更新 `README.md`、`STATE.md`、`ARCHITECTURE.md` 至当前事实。
5. GitHub 准备：结构化初始提交、repo-local git 身份（占位，推送前由所有者替换）、发布前检查清单写入文档。
6. 记录 `docs/adr/ADR-003-repo-orientation.md`；为 `smoke.py`/`browser_check.py` 增加仓库根自举（此前直接运行报 `ModuleNotFoundError`）。

### 禁止项

- 修改 `data/` 与 `outputs/` 内容，或切换派生数据版本指针；
- 继续 TASK-007 补充（v2 来源定位切换）工作；
- 执行正式盲测，或伪造独立审核与标签；
- 替所有者选择开源许可证（后由所有者当日决定）、实际创建 GitHub 远程仓库或推送；
- 改动 `flavoretro/` 包逻辑（本任务只做整理与文档）。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| `scripts/`：活动工具 | `operate.py`、`smoke.py`、`browser_check.py` | 保留；后两者补仓库根自举 |
| `operations/archive/`：一次性脚本留档 | `admit-task-002.py`、`history_guard-task-001.py`、`README.md` | 迁入并附归档说明（含此前归档的 `resources-v1.py`） |
| `docs/`：导航与接管 | `docs/README.md`、`HUMAN_TAKEOVER.md`、`PAPER_ROADMAP.md` | 新增 |
| `docs/adr/`：长期决定 | `ADR-003-repo-orientation.md` | 新增（归档、文档分层、发布清单驱动） |
| 仓库根：治理 | `README.md`、`STATE.md`、`ARCHITECTURE.md` | 修死链并更新至当前事实 |
| Git 历史 | — | 六个分层初始提交（见下） |

## 非目标

- 不继续 TASK-007 补充（来源路径迁移 v2 切换）——用户明确指示忽略该线；v2 派生数据保留原样，指针仍在 v1；
- 不执行正式盲测、不伪造独立审核或标签；
- 不替所有者选择开源许可证；不实际创建 GitHub 远程仓库或推送；
- 不改动 `flavoretro/` 包逻辑。

## 必须执行的操作

1. 归档两个一次性脚本并新建 `operations/archive/README.md`。
2. 新建三份人接管/论文文档与 ADR-003。
3. 修复 README 死链并更新 STATE、ARCHITECTURE。
4. 修复 smoke/browser_check 的仓库根自举并重跑验收。
5. 以分层初始提交建立 Git 历史：`aa012ca`（docs 治理骨架）、`1f027a8`（feat 核心包）、`2b305a4`（chore 操作日志/来源清单/环境锁定/活动脚本）、`cba0452`（REPORT-008）、`d8d84c0`（操作日志收尾）、`b9a1359`（许可分层：代码 Apache-2.0/文档 CC BY 4.0/数据保留来源许可，所有者 2026-09-21 决定，同 CondRxnBench）。
6. 设置 repo-local git 身份为占位 `ljx@flavoretro.local`，推送前由所有者替换。

## 验收标准

- [x] 单元测试 25/25 通过（command-0027，`Ran 25 tests in 4.543s`，OK）。
- [x] 实时冒烟通过：首次 rc=1（command-0028，无 PYTHONPATH 直接运行 `ModuleNotFoundError: No module named 'flavoretro'`），修脚本自举后 command-0030 通过（3 次新 MCTS、run_id 各异、两阶段、全部非 evidence 闭合）。
- [x] 浏览器验收通过：首次 rc=1（command-0031，resources 页等待"共 49 条"文本 30s 超时），重跑 command-0032 通过，记为偶发时序问题（未修改产品代码规避）。
- [x] 活动 `scripts/` 无一次性脚本（仅剩 `operate.py`、`smoke.py`、`browser_check.py`）。
- [x] 文档导航无死链；STATE/ARCHITECTURE 与事实一致。
- [x] Git 历史为清晰的分层初始提交；仓库不含受限数据载荷（`data/`、`outputs/` 仍被忽略）。
- [x] 未修改 `data/` 与 `outputs/` 内容；未切换派生数据版本指针。
- [x] 许可分层按所有者当日决定落实（`b9a1359`），不代办 GitHub 远程与推送。

verification 事件记录：`unit_tests` 25/25 ok；`smoke` ok；`browser_check` pass after one flaky 30s timeout on resources page。

## 验证

```bash
.venv/bin/python -B -m unittest discover -s tests -v   # command-0027，25/25 OK
.venv/bin/python -B scripts/smoke.py                    # command-0030（command-0028 失败后修复）
.venv/bin/python -B scripts/browser_check.py            # command-0032（command-0031 偶发超时后重跑）
git log --oneline                                        # 六个分层初始提交
```

## 停止条件

- 测试失败先诊断再写报告；
- 文档内容与仓库事实冲突时以事实为准修正文档，不用文档掩盖问题。

## 必须提交的报告

`docs/reports/REPORT-008-human-github-handover.md` 已生成并随 `cba0452` 提交；STATE.md 已更新（含 v2 指针搁置与脚本归档事实）。
