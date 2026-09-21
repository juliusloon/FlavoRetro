# TASK-008：人接管友好化与 GitHub/论文导向整理

Approved。用户于 2026-09-21 在 Kimi 会话中直接授权继续重建工作（原话要点："constructively rebuild this project and make it highly human-take-over friendly, discarding some of the old python scripts that is no longer useful for our current goal and final paper work and github repository"）；批准记录 Kimi agent_delegated，理由：用户明确要求继续并由其本人给出新方向。

## 目的

TASK-001—007 由 agent 长时间自主完成，工程产物功能完整但"接手摩擦"高：README 有死链、缺少面向人的接管指南、缺少面向论文的目标路线、活动脚本中混有一次性迁移脚本。本任务把项目整理到人可低摩擦接管、可面向 GitHub 公开仓库与最终论文继续推进的状态。

## 范围

1. 归档一次性脚本：`scripts/admit.py`（TASK-002 数据准入，硬编码 `/home/ljx/retro_synthesis`）与 `scripts/history_guard.py`（TASK-001/006 历史目录完整性基线，同样机器相关）移至 `operations/archive/`，附归档说明。活动 `scripts/` 只保留可复用工具：`operate.py`（治理日志）、`smoke.py`（实时冒烟）、`browser_check.py`（浏览器验收，需 Playwright）。
2. 补人接管文档：新建 `docs/README.md`（全部文档导航）、`docs/HUMAN_TAKEOVER.md`（人接管指南）、`docs/PAPER_ROADMAP.md`（论文路线与未证事项清单）。
3. 修复失效链接：README 指向的 `docs/reports/REPORT-007-handoff.md` 与 `docs/README.md` 此前不存在；以 REPORT-008 承接交接汇总，导航由 docs/README.md 承担。
4. 更新 `README.md`、`STATE.md`、`ARCHITECTURE.md` 至当前事实。
5. GitHub 准备：结构化初始提交、repo-local git 身份（占位，推送前由所有者替换）、发布前检查清单写入文档。
6. 记录 `docs/adr/ADR-003-repo-orientation.md`。

## 验收

- 单元测试与实时冒烟全部通过；活动树无一次性脚本。
- 文档导航无死链；STATE/ARCHITECTURE 与事实一致。
- git 历史为清晰的分层初始提交；仓库不含受限数据载荷（data/、outputs/ 仍被忽略）。
- 不修改 `data/` 与 `outputs/` 内容；不切换派生数据版本指针。

## 非目标

- 不继续 TASK-007 补充（来源路径迁移 v2 切换）——用户明确指示忽略该线；v2 派生数据保留原样，指针仍在 v1。
- 不执行正式盲测、不伪造独立审核或标签。
- 不替所有者选择开源许可证；不实际创建 GitHub 远程仓库或推送。
- 不改动 `flavoretro/` 包逻辑（本任务只做整理与文档）。

## 停止条件

测试失败先诊断再写报告；文档内容与仓库事实冲突时以事实为准修正文档，不用文档掩盖问题。
