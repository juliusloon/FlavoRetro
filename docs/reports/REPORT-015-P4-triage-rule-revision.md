# REPORT-015-P4：筛选规则修订（人审校准回灌）

对应 [TASK-015-P4](../tasks/TASK-015-P4-triage-rule-revision.md)。所有者 2026-09-29 会话回复「批准」（human_direct 工程执行授权）后执行完毕。任务目标：把 TASK-015-P3 人审暴露的机器假阳性模式回灌为 TASK-014 筛选规则 v2，并在 60 卡开发校准集上验证不误伤 gold。全部产物为开发用筛选行为观察，不构成化学验证、不接入 MCTS。

## 交付

**规则 v2**（`configs/domain_triage-v2.json` + 资产副本，protocol_version `task015-p4-v2`，provisional）：在 v1 全部字段之上新增三类处置（`dispositions`，优先级 blocked_source > incomplete_record > pathway_suspect）与内联撤稿黑名单（`source_blacklist`）。

1. **blocked_source（来源级拦截）**：命中可核实撤稿论文的记录进 `blocked_source_blacklist` 队列。匹配 = 引用文本 DOI 子串 或（刊名或别名 + 年 + 卷 + 页 全命中；年/卷词边界，期号仅在引用携带除年份外的括号数字组时判别；连字符/破折号归一化）。黑名单初始 1 条：Research on Chemical Intermediates (2024), 50(7), 3079-3108（原论文 DOI 10.1007/s11164-024-05300-x，撤稿注记 DOI 10.1007/s11164-024-05454-8，2024-11-22；证据链 = P1 代理核对撤稿事实 + P3 卡 53 所有者亲审排除）。
2. **incomplete_record（不完整降级）**：`status != parsed` 的记录不再占据领域队列（v1 中 54 条 partial 记录因产物侧有骨架而进入 guide_supported/outside_guide_structure）。
3. **pathway_suspect（路径压缩嫌疑）**：parsed 且反应物侧零领域骨架、产物侧 ≥2 个各自携带领域骨架的不同分子 → 疑似多步路径被导出压缩为单步"反应"，降入 `pathway_suspect` 队列保留待审。

**代码**：`flavoretro/triage.py` 最小扩展——`load_rules` 双版本校验、`citation_texts`/`source_blacklist_hits`/`pathway_compression_suspect`/`v2_disposition` 四个纯函数、pilot 行的 `v1_queue`/`v2_disposition` 字段与 summary limitations 行均以 `schema_version >= 2` 门控。v1 路径行为不变（见验证）。

## 重跑与迁移（同一冻结 2,301 输入）

| 队列 | v1 | v2 | 变化 |
| --- | --- | --- | --- |
| guide_supported | 1,289 | 1,287 | −2（→pathway_suspect） |
| outside_guide_structure | 654 | 586 | −68（51 不完整 + 14 路径嫌疑 + 3 黑名单） |
| low_or_unknown | 358 | 356 | −2（2 条非领域 partial 重新归类 incomplete_record） |
| blocked_source_blacklist | — | 3 | 新增 |
| incomplete_record | — | 53 | 新增 |
| pathway_suspect | — | 16 | 新增 |

**黑名单实际拦截 3 条**：卡 53 的记录（98ecd879…，在 60 卡样本内）加上**两条样本外同引用记录**（9f1d3817…、cd8ff6f5…）——后者未经逐条人审，按来源级规则随已核实的撤稿论文一并拦截，是本次回灌的直接增量收益。被拦截记录保留全部原始数据，仅队列处置变化。

## 校准验证

证据：`outputs/validation/task015-p4-calibration.json`。

- **Gold 回归**：53 张 gold 保留卡 v1→v2 队列变化 **0**（零误降级），含 5 张 low_or_unknown 原位不变。
- **7 张排除卡逐卡**：27→pathway_suspect ✓；51/52/54/55→incomplete_record ✓；53→blocked_source_blacklist ✓；**28→无规则处置（保持 guide_supported）**。卡 28 的排除理由"这实验没看出来有什么用"是效用判断，其结构合法（苄基保护糖苷化步骤）且 17 张摘要级 gold 卡同此来源等级，无机器可表达判别信号——按合同"不伪造规则覆盖"如实登记为人审层判断，v2 的 summary limitations 已声明处置规则源于 60 张开发暴露卡的校准、非化学验证过滤器。
- **测试**：新增 `tests/test_triage_v2.py` 15 项（双版本加载/未知版本拒绝/黑名单必填可核身份/7 组黑名单匹配语义/路径压缩 5 组/处置优先级 4 组/规则字段删除拒绝）；全量 **82 项通过**（原 67 + 新 15）。

## 可复现性

- v2 两次独立构建（task015-p4-v2 / task015-p4-v2-replay）**12 文件逐字节一致**（含 manifest）。
- v1 回归重跑（task015-p4-v1-regression）与冻结的 task014-final **11 个载荷文件逐字节一致**；manifest 仅 `triage_code_sha256` 不同（P4 授权的代码变更本身）。首次回归曾暴露 v2 字段泄漏进 v1 载荷（pilot 行新增键、limitations 行），当轮修复为版本门控后重建三个目录——回归检查按设计拦截了该回归。
- 受保护基线 `operations/task015-p4-baseline.json`（31 文件哈希）：gold-v1、ingest-1、final JSON、所有者提交原件、task014-final、P1/P2 输出、v3、搜索/UI 代码全部未漂移。

## 边界（不变）

处置规则是 60 张 development_exposed 卡校准出的筛选行为，不是化学验证；16 条 pathway_suspect 与 53 条 incomplete_record 是队列重排而非排除，人工复核仍可恢复；撤稿黑名单仅收录可核实公开撤稿记录（当前 1 条，含证据字段，可扩展）。0 production、0 blind、MCTS/搜索未触碰；TASK-016 糖苷感知搜索、正式盲测、公开发布仍需新的所有者批准。原始/受限数据不入 Git；构建产物在 Git 忽略的 outputs/。
