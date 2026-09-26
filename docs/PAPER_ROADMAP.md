# 论文路线（PAPER ROADMAP）

当前系统状态：`metadata/release.json` 标记为 `research_candidate`，六个外部验证维度全部 unresolved / not_executed / not_performed。本路线把"最终论文"拆成可执行阶段；**任何阶段都不得用工程测试冒充化学验证**。

## 阻断性缺口（写论文前必须关闭）

| 缺口 | 现状 | 关闭条件 |
|---|---|---|
| 模板/库存独立来源审核 | `primary_source_review: unresolved` | 有署名的人工化学审核记录，逐条 template/stock 晋级或否决 |
| 当前供应商证据 | `current_vendor_evidence: unresolved` | 可日期的供应/价格核查，与历史 listing 分开 |
| 独立化学标签 | `independent_chemical_labels: not_available` | 预注册评测 panel + 独立标注（人或文献双源） |
| 正式盲测 | `formal_benchmark: not_executed` | 冻结合同后一次性执行（evaluation.preflight 的 `formal_run_ready` 变为 true 才允许启动） |
| 结构诊断真值 | topology 只有开发自检 | 糖苷连接候选的人工标注子集，报告 precision/recall |

`evaluation.py` 的 preflight 是这道门的代码化形式：**先补齐前三行，formal 执行器才允许动工。**

## 阶段计划

- **P0 证据整理（无新实验）**：来源定位已由 TASK-012 获批恢复并切换 v3（249 条 token 命中、259 条文件定位但 token 未命中）；剩余 token/原文内容审核仍需科学任务；产率字段覆盖率统计；3 个名称冲突库存条目的处置决定。产出：数据审核附录素材。
- **P1 人工审核与标注**：template/stock 逐条人工审核（多名审核人 + 分歧记录）；糖苷连接诊断标注 50—100 分子子集。产出：`production_eligible` 首批记录、诊断真值表。
- **P2 预注册正式评测**：定义目标 panel、对照基线、指标（闭合率需 evidence 定义、成本分布、多样性）；冻结合同后跑正式盲测（开发对照的 12 cell 规模远不够）。产出：`outputs/evaluation/formal-*` 与统计报告。
- **P3 论文产物**：图表全部从 `outputs/` 已存运行重绘（禁止手改数值）；附录含 sources 清单、哈希、运行 ID；代码打版本标签并公开仓库。

## 可直接复用的工程素材（论文方法部分）

- 每次搜索独立进程、独立 run ID、结果哈希入 manifest（可追溯性）。
- 原生/优化树同资产、同时间/迭代预算的开发对照运行器（节点上限不等价）（`flavoretro/evaluation.py`）。
- 证据分级输出（partial / surrogate / evidence_closed，默认全 false）。
- 资源准入：逐记录 SHA-256、解析失败保留、零收率≠缺失。
- 结构诊断：立体化学感知的图往返回归测试（`tests/test_topology.py`）。

## GitHub 发布检查清单（所有者执行）

- [x] 选择代码许可证（已确定：代码 Apache-2.0、项目原创文档 CC BY 4.0，同 CondRxnBench，2026-09-21）
- [ ] 确认仓库无受限数据：`data/`、`outputs/` 在 .gitignore；`metadata/` 只含哈希与清单
- [ ] 替换 repo-local git 身份为所有者 GitHub 身份
- [ ] README 补充仓库地址与引用方式（建议届时加 CITATION.cff）
- [ ] 环境可复现声明：pyproject 固定版本 + pip-freeze + 模型资产获取说明
- [ ] 打版本标签（如 v0.1.0-research-candidate）

TASK-012 只同步现有私有仓库并保留已有 repo-local Git 身份，不替代本页的公开发表身份、引用、许可或科学检查清单。Linux/Python 3.10 独立安装已验证，锁清单改用 environment/requirements-linux-py310.lock；其他平台、标签和公开发布仍需单独批准。
