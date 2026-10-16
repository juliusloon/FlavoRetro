# ADR 008：教学重建拆分至 FutureHealth 新仓库

- 状态：accepted
- 日期：2026-10-15
- 负责人：Cano（执行，agent_delegated）；所有者（授权）

## 背景

`outputs/restructure/future-health-20261015` 预迁移包确定 FlavoRetro → Future Health 教学重建的 M0—M5 路线，要求全新隔离目录、只复制批准子集、旧库保持科研事实源只读。FlavoRetro 当前承载活跃科研状态（TASK-017 准备就绪、C/糖间独立迁移未验证、formal/release 门关闭），教学建设（24 步课程、D1 仿真、平台、发布门）与其必须隔离。所有者 2026-10-15 指示：按 outputs/restructure 要求重建，新项目与 FlavoRetro 同级（/home/ljx/ 下），名称自拟。

## 决定

1. 教学重建项目定名 **FutureHealth**，位于 `/home/ljx/FutureHealth`，独立 Git 仓库（main；首提交 ca586b3，验证凭据提交 c05767e），不继承 FlavoRetro Git 历史。
2. FlavoRetro 继续作为科研事实源：既有科学账本、formal/release 门、未提交工作区一律不动；本轮仅协作框架写入（TASK/REPORT/STATE/ADR/events 追加）与迁移脚本。
3. 迁移采用「P0 受控副本 + P1 登记待审」：23 个 CORE_REUSE 文件进 `reference/flavoretro-snapshot/`（逐文件 SHA256 验证，非运行时）；49 项 SELECTIVE_REVIEW 只登记 `migrations/p1_pending_review.csv`，教师/所有者审定前不复制内容。
4. 协作规范不变：后续 FutureHealth 建设任务的 TASK 合同、REPORT、STATE 更新仍在 FlavoRetro 按本规范登记并经 `scripts/operate.py` 记录；代码变更落在 FutureHealth 仓库。
5. 数据边界：`data/private/` 与参考副本的 data/metadata 层不入 Git；原始/受限数据、候选记录、评审卡不迁移（NON_MIGRATION_POLICY 继承有效）。

## 备选方案

- 单库双轨（在 FlavoRetro 内建 teaching/ 子树）：否——预迁移包明确要求全新隔离目录；教学写入会混入科研事实源与保护文件基线。
- 立即全量迁移 P1 资料加快进度：否——P1 要求人工/专业审查后选入，agent 代审不构成教师审定；先登记后复制。
- 以 v3 全量数据作教学开放库：否——3,059 条是内部候选筛选池，教学版只允许审定子集。

## 影响与风险

- 跨库溯源依赖 `FutureHealth/migrations/` 的哈希映射与预迁移包登记；两库文件清单以 SHA 对应。
- 风险：参考副本被误当作可运行系统或教学真值——README/ADR/mapping 三处声明「非运行时、复用需新合同」。
- 风险：两处 Git 身份不同（FlavoRetro 保留既有 repo-local 身份；FutureHealth 本地身份 `Cano (AutoClaw agent) <cano@flavoretro.invalid>` 仅审计用）。
- 风险：教学 TASK 在 FlavoRetro 登记、代码在 FutureHealth，评审时需同时看两库——报告必须双库引用。

## 复审条件

M1（结构复核）启动前；任何 P1 复制前；所有者变更项目名/位置/许可门；预迁移包修订。
