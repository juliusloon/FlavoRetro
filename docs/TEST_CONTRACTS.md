# 历史测试知识与本次合同
旧 67 个测试方法目录以只读副本保存在 data/raw/legacy/outputs/retrospective/2026-09-20/。不将旧通过数计为本次测试数。
| 历史知识 | 新实现/验收 | 本次边界 |
|---|---|---|
| 实时 MCTS、API/CLI 同源 | service + test_live + Chromium HTTP | 无缓存回退 |
| 参数有效、种子/route ID | contracts + test_live | 短预算工程检查 |
| MW/virtual 弱终止 | 不启用 MW、virtual；candidate 只能 surrogate | 没有 production |
| 候选与来源不能晋级 | resources/policies + 逐记录字段 | 无逐例原文人工审核 |
| 零与缺失、原始守恒 | test_contracts + 双重全量重放 | 真实导入未出现数值零；零规则用合成例 |
| 三个 stock 名称冲突 | 重新计算连接键 | 参考响应仍为旧快照 |
| O/C、普通醚阴性、顺序不变 | test_topology + 156 分子本次 audit | 无独立 gold labels |
| 立体回放错误 | 55 失败保留，邻序修复，新立体回归 | 图自洽不等于化学预测 |
| 浏览器/错误/溢出 | scripts/browser_check.py | Chromium 桌面/390px；无真人评价 |
| 模板晋级、四臂 360 cell | 默认拒绝候选进入 production | production builder 与正式盲跑 planned |
| AHP/教学、供体 D1–D5、外部供应 | 原材料保留为 reference | 未移植为已验证能力 |
