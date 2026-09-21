# REPORT-008：人接管友好化与 GitHub/论文导向整理

## 对应任务

- 任务 ID：TASK-008
- 任务文件：`docs/tasks/TASK-008-human-github-handover.md`
- 状态：Completed（完成）
- 基线：无提交（`git init` 后）
- 结果提交：`aa012ca`、`1f027a8`、`2b305a4`、`cba0452`、`d8d84c0`、`b9a1359`（职责见"仓库与 CI 状态"）
- 批准：Kimi agent_delegated（用户 2026-09-21 直接指令）
- 执行时段：2026-09-21 10:45—10:51
- 文档形态：本报告原为速记体，TASK-009 转为模板结构，事实未变。本报告只陈述事实。

## 改动文件

生成但不进入 Git 的文件：本任务无新增；`data/`、`outputs/`、`operations/command-*.log` 维持既有的不入 Git 约定。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `scripts/`：活动可复用工具 | `admit.py` → `operations/archive/admit-task-002.py` | 迁出归档。一次性 TASK-002 数据准入脚本，硬编码 `/home/ljx/retro_synthesis`，仅本机核对历史用。 |
| `scripts/`：活动可复用工具 | `history_guard.py` → `operations/archive/history_guard-task-001.py` | 迁出归档。一次性 TASK-001/006 历史目录完整性基线脚本，同样机器相关。 |
| `operations/archive/`：一次性脚本归档 | `README.md` | 新建。说明归档脚本的历史使命、机器相关性与本机用法。 |
| `scripts/`：活动可复用工具 | `smoke.py`、`browser_check.py` | 增加仓库根自举（原先按 README 写法直接运行会 `ModuleNotFoundError`），命令照文档原样可跑。活动 `scripts/` 仅剩 `operate.py`、`smoke.py`、`browser_check.py`。 |
| `docs/`：项目文档 | `README.md` | 新建。全部文档导航。 |
| `docs/`：项目文档 | `HUMAN_TAKEOVER.md` | 新建。人接管指南。 |
| `docs/`：项目文档 | `PAPER_ROADMAP.md` | 新建。论文路线、阻断性缺口清单与 GitHub 发布检查清单。 |
| `docs/adr/`：长期决定记录 | `ADR-003-repo-orientation.md` | 新建。记录仓库取向与一次性脚本归档决定。 |
| 仓库根与治理入口 | `README.md`、`STATE.md`、`ARCHITECTURE.md` | 更新至当前事实；修复 README 死链（见"实际改动"第 3 条）。 |
| 仓库根与 `LICENSES/`：许可 | `LICENSE`、`LICENSES/`（含 `CC-BY-4.0.md`、`README.md`） | 许可分层落地：代码 Apache-2.0、项目原创文档 CC BY 4.0、数据保留来源许可（见"实际改动"第 6 条）。 |

## 实际改动

1. 归档一次性脚本（ADR-003）：`scripts/admit.py` → `operations/archive/admit-task-002.py`；`scripts/history_guard.py` → `operations/archive/history_guard-task-001.py`；新增 `operations/archive/README.md` 说明其历史使命与机器相关性。活动 `scripts/` 仅剩 `operate.py`、`smoke.py`、`browser_check.py`。
2. 补文档：新建 `docs/README.md`（导航）、`docs/HUMAN_TAKEOVER.md`（人接管指南）、`docs/PAPER_ROADMAP.md`（论文路线与 GitHub 发布检查清单）、`docs/adr/ADR-003-repo-orientation.md`。
3. 修死链：README 原指向不存在的 `docs/reports/REPORT-007-handoff.md` 与 `docs/README.md`；当时前者由本报告承接交接汇总，后者已建（注：TASK-009 已补立真正的 REPORT-007 与 REPORT-007-P1）。`README.md`、`STATE.md`、`ARCHITECTURE.md` 更新至当前事实。
4. 脚本可接管性：`smoke.py`、`browser_check.py` 增加仓库根自举（原先按 README 写法直接运行会 `ModuleNotFoundError`），命令照文档原样可跑。
5. Git 分层初始提交（此前仓库无任何提交）：6 个提交依次为 `aa012ca`、`1f027a8`、`2b305a4`、`cba0452`、`d8d84c0`、`b9a1359`；repo-local git 身份为占位（`ljx@flavoretro.local`），推送 GitHub 前由所有者替换。
6. 许可分层：代码 Apache-2.0、项目原创文档 CC BY 4.0、数据保留来源许可；所有者 2026-09-21 决定，同 CondRxnBench（`license_decision` 事件：`basis=owner_instruction_2026-09-21_same_as_CondRxnBench`）。
7. 全部操作经 `scripts/operate.py` 记入 `operations/events.jsonl` 与 command 日志。
8. 按合同非目标未做：TASK-007 补充（508 条笔记来源路径迁移的 v2 切换）未继续，v2 派生数据保留、活动指针仍在 v1——按用户指示搁置；未创建 GitHub 远程、未推送（检查清单在 PAPER_ROADMAP 末节）；`flavoretro/` 包逻辑零改动；`data/`、`outputs/` 内容零改动。

## 验证

注：`command-XXXX` 指 `operations/command-XXXX.log`，为本机日志，不入 Git，关键输出已内联于本表。

| 命令或检查项 | 结果 |
| --- | --- |
| `.venv/bin/python -B -m unittest discover -s tests -v`（command-0027） | rc=0：25/25 OK，4.5 s（含 2 次真实 MCTS live 搜索） |
| `.venv/bin/python -B scripts/smoke.py` 修复前首次（command-0028） | rc=1：`ModuleNotFoundError: No module named 'flavoretro'`——无 PYTHONPATH 直接运行即失败 |
| `env PYTHONPATH=/home/ljx/FlavoRetro .venv/bin/python -B scripts/smoke.py` 中间诊断（command-0029） | rc=0，确认问题仅为导入路径 |
| `.venv/bin/python -B scripts/smoke.py` 加仓库根自举后（command-0030） | rc=0：3 次新 MCTS、run_id 各异、两阶段、全部非 evidence 闭合 |
| `.venv/bin/python -B scripts/browser_check.py` 首次（command-0031） | rc=1：resources 页等待"共 49 条"30 s 超时 |
| `.venv/bin/python -B scripts/browser_check.py` 重跑（command-0032） | rc=0：桌面+移动验收、资源详情、无效输入 400、无 JS 错误、无横向溢出；首次超时判定为偶发时序，未修改产品代码规避 |
| `events.jsonl` 的 verification 事件原文 | `unit_tests: 25/25 ok`；`smoke: ok`；`browser_check: pass after one flaky 30s timeout on resources page` |

25 项单元测试分布在 `tests/test_contracts.py`、`tests/test_live.py`、`tests/test_topology.py`（command-0027 所列测试类：DataContracts / RuntimeContracts / LiveContracts / TopologyContracts），其中 live 合同含 2 次真实 MCTS 搜索。

## 与任务合同的偏差

1. 合同验收含"文档导航无死链"，但当时 `REPORT-005` 与 `REPORT-007` 仍未单独成文（导航指向的报告文件缺失），由本报告临时承接交接汇总；TASK-009 补立后才完全满足。
2. 浏览器验收首次运行偶发 30 s 超时一次，重跑通过；未改产品代码规避，记录在案。

## 已发现但未修改的问题

1. 浏览器验收在 resources 页存在偶发 30 s 超时（一次性，重跑通过），根因未定位，产品代码未改动。
2. 无其他记录。

## 遗留风险

1. repo-local git 身份为占位（`ljx@flavoretro.local`），推送前待所有者替换。
2. 许可证已定但 GitHub 远程未建、仓库未推送。
3. 剩余事项需人决策：许可证与仓库公开（可对照 PAPER_ROADMAP 清单逐项确认）、论文阻断性缺口（独立来源审核、供应商证据、独立标签、正式盲测，详见 PAPER_ROADMAP）、git 身份替换。

## 仓库与 CI 状态

本任务建立了 6 个分层初始提交（此前仓库无任何提交）：

| 提交 | 主题 | 内容 |
| --- | --- | --- |
| `aa012ca` | docs | 治理骨架、TASK/REPORT 全档案、ADR、人接管指南与论文路线 |
| `1f027a8` | feat | 核心包（资源准入 / MCTS 覆盖层 / 共享服务 / Web / 测试） |
| `2b305a4` | chore | 操作日志、来源清单、环境锁定与活动脚本 |
| `cba0452` | docs | REPORT-008 |
| `d8d84c0` | chore | 操作日志收尾 |
| `b9a1359` | docs | 许可分层 |

无远端（GitHub 仓库未创建、未推送），无 CI。repo-local git 身份为占位 `ljx@flavoretro.local`。受限数据载荷（`data/`、`outputs/`）仍被 `.gitignore` 排除，未进入任何提交。

## 建议的下一任务

文档详细化（速记体报告扩写与缺失报告补立，即 TASK-009，由用户当日稍后直接指令）。仅为建议，不自动开始。
