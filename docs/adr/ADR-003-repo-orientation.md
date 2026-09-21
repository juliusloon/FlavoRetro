# ADR-003：一次性脚本归档、文档分层、GitHub 发布前清单

接受。理由与替代方案如下。

## 决定

1. 一次性机器相关脚本（`admit.py`、`history_guard.py`）从 `scripts/` 归档到 `operations/archive/`，活动脚本只保留 `operate.py`、`smoke.py`、`browser_check.py`。
2. 文档分三层：机器契约（PROJECT/STATE/ARCHITECTURE，agent 先读）、人接管层（docs/HUMAN_TAKEOVER.md）、论文层（docs/PAPER_ROADMAP.md），导航统一走 docs/README.md。
3. GitHub 公开改为清单驱动（PAPER_ROADMAP 末节），许可证与推送由所有者决定，本任务不代办。

## 理由

- `admit.py` 与 `history_guard.py` 硬编码 `/home/ljx/retro_synthesis`，只在 TASK-001/002/006 的当时机器上可运行；留在活动 `scripts/` 会对新协作者（人或 agent）构成误导，仿佛在维护期内工具。
- 直接删除会破坏溯源链：TASK-002 的准入逻辑、TASK-001/006 的历史完整性核对方法需要可查。项目硬约束"数据保留并标记"同样适用于代码遗产，沿用 `operations/archive/resources-v1.py` 的先例。
- TASK-001—007 全程由 agent 自主执行，交接文档（REPORT-007）未生成且 README 已出现死链；不把导航与接管指南补齐，"功能完成"与"人可接手"之间会持续存在落差。

## 替代方案（不采用）

- 原地保留并加注释：活动树噪音仍在，agent 仍可能误执行机器相关脚本。
- 直接删除：丢失准入与完整性核对的复现方法，违反"保留并标记"。
- 由本任务代办许可证与 GitHub 推送：超出授权范围（PROJECT.md 明确新代码许可"发布前单独登记"）。

## 影响

- 新会话/agent 的读序不变（AGENTS.md），但接手人先看 HUMAN_TAKEOVER；论文相关工作一律对照 PAPER_ROADMAP 的缺口清单，防止工程结果被误写为化学结论。
