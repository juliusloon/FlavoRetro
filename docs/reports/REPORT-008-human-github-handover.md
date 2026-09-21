# REPORT-008：人接管友好化与 GitHub/论文导向整理

对应 [TASK-008](tasks/TASK-008-human-github-handover.md)；批准：Kimi agent_delegated（用户 2026-09-21 直接指令）。本报告只陈述事实。

## 做了什么

1. **归档一次性脚本**（ADR-003）：`scripts/admit.py` → `operations/archive/admit-task-002.py`；`scripts/history_guard.py` → `operations/archive/history_guard-task-001.py`；新增 `operations/archive/README.md` 说明其历史使命与机器相关性。活动 `scripts/` 仅剩 `operate.py`、`smoke.py`、`browser_check.py`。
2. **补文档**：新建 `docs/README.md`（导航）、`docs/HUMAN_TAKEOVER.md`（人接管指南）、`docs/PAPER_ROADMAP.md`（论文路线与 GitHub 发布检查清单）、`docs/adr/ADR-003-repo-orientation.md`。
3. **修死链**：README 原指向不存在的 `docs/reports/REPORT-007-handoff.md` 与 `docs/README.md`；前者由本报告承接交接汇总，后者已建。`README.md`、`STATE.md`、`ARCHITECTURE.md` 更新至当前事实。
4. **脚本可接管性**：`smoke.py`、`browser_check.py` 增加仓库根自举（原先按 README 写法直接运行会 `ModuleNotFoundError`），命令照文档原样可跑。
5. **Git 分层初始提交**（此前仓库无任何提交）：
   - `aa012ca` docs: 治理骨架、TASK/REPORT 全档案、ADR、人接管指南与论文路线
   - `1f027a8` feat: 核心包（资源准入/MCTS 覆盖层/共享服务/Web/测试）
   - `2b305a4` chore: 操作日志、来源清单、环境锁定与活动脚本
   - repo-local git 身份为占位（`ljx@flavoretro.local`），推送 GitHub 前由所有者替换。
6. 全部操作经 `scripts/operate.py` 记入 `operations/events.jsonl` 与 command 日志。

## 验证结果（本任务新跑）

- `unittest discover -s tests -v`：25 项全部通过（含 2 次真实 MCTS live 搜索），4.5 s。
- `scripts/smoke.py`：3 次新 MCTS、run_id 各异、两阶段、全部非 evidence 闭合，通过。
- `scripts/browser_check.py`：桌面+移动验收、资源详情、无效输入 400、无 JS 错误、无横向溢出，通过；首次运行曾因资源页等待 30 s 超时失败一次，重跑通过，判定为偶发时序问题（未修改产品代码规避）。

## 未做（按任务非目标）

- TASK-007 补充（508 条笔记来源路径迁移）未继续，v2 派生数据保留、活动指针仍在 v1——按用户指示搁置。
- 未选择许可证、未创建 GitHub 远程、未推送；检查清单在 PAPER_ROADMAP 末节。
- `flavoretro/` 包逻辑零改动；`data/`、`outputs/` 内容零改动。

## 剩余事项（需人决策）

1. 许可证选择与仓库公开（所有者可对照 PAPER_ROADMAP 清单逐项确认）。
2. 论文阻断性缺口：独立来源审核、供应商证据、独立标签、正式盲测（详见 PAPER_ROADMAP）。
3. git 身份占位替换。
