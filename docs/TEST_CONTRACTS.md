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

## TASK-012 工程合同

- test_database：原创 fixture 核 SQL/JSON 守恒、中文/字面查询、分页、零/缺失/未解析、只读/外键、指针/源清单/索引损坏；本地另逐 ID 核查全量 3,059 条。
- test_search：PUCT、动作融合/去重、替代动作、转置、多产物预算、同次扩展去重及原产物索引。修复前的两项失败日志保留。
- test_package / package_check：默认资源/覆盖配置/副本一致，仓库外安装路径、无资产诊断与安装包真实 MCTS。
- test_web_foundation：全部保存运行文件完整性、显式历史不触发搜索、资源筛选参数、无资产 preflight、共享门控与固定 job、外进程未完成记录不伪装运行。
- browser_check：全参数、v3/清单导出、QC/收率/来源筛选、27 教学条目、历史 run 数不变、12-cell 真实开发对照、429、四页移动宽度、非法输入与 UI 引擎失败 fixture。
- artifact_check：wheel/sdist 应用资源与本地/受限载荷排除。

当前全量测试 51 项；CI 无本地资产时预期跳过 6 项（数据守恒/历史回放/候选冲突三项及 live 三项），其余合同在原创 fixture 上执行。CI 的跳过不是 MCTS、化学或浏览器验收；最终实际结果以 REPORT-012 和对应提交 CI 为准。
