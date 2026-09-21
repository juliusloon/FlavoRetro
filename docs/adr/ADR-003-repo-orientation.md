# ADR-003：一次性脚本归档、文档分层、GitHub 发布前清单

- 状态：accepted
- 日期：2026-09-21
- 负责人：Kimi（agent_delegated）

## 背景

TASK-001—008 由 agent 于 2026-09-21 一天内自主执行完成（治理授权见 ADR-001），仓库在 TASK-008 中完成面向人类接管与 GitHub 发布的整理。当时存在三个需要长期记录理由的问题：

- `scripts/` 下的 `admit.py`、`history_guard.py` 硬编码 `/home/ljx/retro_synthesis`，只在 TASK-001/002/006 的当时机器上可运行。
- 它们留在活动 `scripts/` 会对新协作者（人或 agent）构成误导，仿佛仍在维护期内的活动工具。
- 但直接删除会破坏溯源链：TASK-002 的准入逻辑、TASK-001/006 的历史完整性核对方法需要可查。
- 项目硬约束"数据保留并标记"同样适用于代码遗产。
- TASK-001—007 全程由 agent 自主执行，交接文档（REPORT-007）当时未生成，且 README 已出现死链。
- 不补齐导航与接管指南，"功能完成"与"人可接手"之间会持续存在落差。

## 决定

1. 一次性机器相关脚本（`admit.py`、`history_guard.py`）从 `scripts/` 归档到 `operations/archive/`，活动脚本只保留 `operate.py`、`smoke.py`、`browser_check.py`。
   - 实际归档文件名为 `operations/archive/admit-task-002.py`、`operations/archive/history_guard-task-001.py`，沿用 `operations/archive/resources-v1.py` 的先例。
2. 文档分三层，导航统一走 docs/README.md：
   - 机器契约层：PROJECT/STATE/ARCHITECTURE，agent 先读；
   - 人接管层：docs/HUMAN_TAKEOVER.md；
   - 论文层：docs/PAPER_ROADMAP.md。
3. GitHub 公开改为清单驱动（PAPER_ROADMAP 末节），许可证与推送由所有者决定，本任务不代办。

## 备选方案

- 原地保留并加注释：活动树噪音仍在，agent 仍可能误执行机器相关脚本。不采用。
- 直接删除：丢失准入与完整性核对的复现方法，违反"保留并标记"。不采用。
- 由本任务代办许可证与 GitHub 推送：超出授权范围（PROJECT.md 明确新代码许可"发布前单独登记"）。不采用。

## 影响与风险

- 读序与入口：新会话/agent 的读序不变（AGENTS.md），但接手人先看 HUMAN_TAKEOVER。
- 论文相关工作一律对照 PAPER_ROADMAP 的缺口清单，防止工程结果被误写为化学结论。
- 归档脚本的误用风险：`admit-task-002.py`、`history_guard-task-001.py` 硬编码旧库路径，离开当时机器即不可运行。
- 与"保留并标记"原则的平衡：它们被保留是为溯源而非复用；归档位置（`operations/archive/`，ARCHITECTURE.md 标 archived）与文件头说明共同承担"标记"职责，使用者不得当作活动工具执行。
- 文档三层职责边界的维持成本：机器契约、人接管、论文三层互不重复事实；边界靠 ARCHITECTURE.md 的责任登记表维持（"新增产物先检查本表，禁止重复事实源"），绕过登记会出现重复事实源。
- 许可证其后已由所有者于 2026-09-21 决定：代码 Apache-2.0、项目原创文档 CC BY 4.0（见 LICENSES/README.md）。
- 仓库尚未连接 GitHub 远程；发布前需完成 PAPER_ROADMAP 末节清单，包括替换 repo-local git 占位身份 `ljx@flavoretro.local`。

## 复审条件

- GitHub 远程建立并推送后——清单驱动的发布流程落地，PAPER_ROADMAP 末节清单的角色需重估。
- git 占位身份替换后——`ljx@flavoretro.local` 被所有者 GitHub 身份替换，历史提交身份的表述需更新。
- 一次性脚本被再次需要时——例如旧库迁移后需重做历史完整性核对，届时应决定恢复、重写还是重新归档。

文档形态：TASK-009 由速记体扩写，决定内容未变。
