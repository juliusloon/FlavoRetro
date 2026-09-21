# TASK-006：独立糖苷连接诊断

## 合同元数据

- 任务 ID：TASK-006
- 状态：Completed
- 批准：Cano（agent_delegated，2026-09-21）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 文档形态：TASK-009 由速记体扩写，范围与结论未变
- 执行时段：2026-09-21 09:54—10:00

## 目标

实现独立于搜索 policy 的结构诊断：新实现有限 5/6 元含氧糖环候选检测，O/C/N/糖间连接分类，断开-重接图一致性校验；对本次 156 分子记录运行，保留未检出与未解析项。完成判定：普通醚阴性、O/C 正例、重编号不变性测试通过，全量输出与错误统计落盘。

## 背景

旧项目复盘第 8/11 节要求结构审计与 MCTS 搜索收益分线，故诊断器独立成线。保留旧糖苷审计知识：O/C 糖苷键分类、糖—糖键区分、普通醚/苷元阴性、SMILES 重编号不变性、98 黄酮苷开发集中旧单一芳基-O 模式命中 66/98 而审计器 98/98、rutinose(1→6)/neohesperidose(1→2) 可由 InChIKey 区分；旧审计无独立 gold labels。历史 98/98 不作为本次指标。`flavoretro/topology.py` 的自我定位（模块 docstring 原文）：“Structural candidates only; this is not an expansion or feasibility policy.”

## 范围

### 允许项

- 新建 `flavoretro/topology.py`、`tests/test_topology.py`；
- 对本次 156 分子记录运行诊断，输出 `outputs/validation/topology-v*.json`；
- 保留未检出与未解析记录；失败版本输出文件保留不删。
- 兼历史目录完整性核对：文件名虽为 topology，原合同同时覆盖历史冻结核对；核对产物 `outputs/validation/history-integrity.json` 因 history_guard 脚本硬编码归入 TASK-006 名下，实际在 TASK-007 时段生成。

### 禁止项

- 把诊断结果解释为反应预测成功、独立准确率或 MCTS 改进；
- 把图重接当作化学预测；酶识别；真实反应条件推断；
- 以历史 98/98 作为本次指标；
- 修改 MCTS 搜索代码。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途 |
| --- | --- | --- |
| `flavoretro/` | `topology.py` | 仅结构候选；不是扩展或可行性 policy |
| `tests/` | `test_topology.py` | 普通醚阴性、O/C 正例、重编号不变性、绝对立体回归 |
| `outputs/validation/` | `topology-v1.json`、`topology-v2.json`、`history-integrity.json` | 诊断输出与历史冻结核对；v1 失败保留 |

## 非目标

- 独立准确率评估、酶识别、真实反应条件；
- 把图重接当作化学预测。

## 必须执行的操作

1. 实现 5/6 元含氧糖环候选检测与 O/C/N/糖间连接分类；
2. 实现断开-重接图一致性（roundtrip）校验；
3. 对 156 分子本次记录全量运行，输出统计与未检出/未解析清单；
4. 单元测试覆盖阴性/正例/重编号不变性，修复后补绝对立体回归。

## 验收标准

- [x] 首次运行 → `outputs/validation/topology-v1.json`（command-0016：detected 132、molecules 156、sites 192、roundtrip_failures 55）。
- [x] unittest 21 tests OK（command-0017，新增 TopologyContracts 5 项）。
- [x] 修复后 → `topology-v2.json`（command-0019：roundtrip_failures 0，detected/sites 不变）。
- [x] unittest 22 tests OK（command-0020，新增 test_absolute_stereo_survives_neighbor_reordering）。
- [x] 普通醚阴性、O/C 正例、重编号不变性、全量 156 分子本次输出和错误统计齐全。

### 执行期事件（并入合同事实）

- diagnosis：55/192 图往返回放失败；原因：手性标签依赖被键重接改变的邻居顺序；修复：校正置换奇偶性；失败的 v1 输出文件保留不删；新增 v2 与绝对立体回归；顺带修正 logging 关键字冲突。
- scope 声明（写入输出 JSON 原文）：“development structural diagnostic; not precision/recall or MCTS improvement”——不能解释为反应预测成功。

## 验证

```bash
python -B -m flavoretro.topology outputs/validation/topology-v1.json   # command-0016
python -m unittest discover tests                                      # command-0017：21 OK
python -B -m flavoretro.topology outputs/validation/topology-v2.json   # command-0019：roundtrip_failures 0
python -m unittest discover tests                                      # command-0020：22 OK
```

## 停止条件

- 修复 roundtrip 需要删除 v1 失败证据；
- 结果被要求表述为准确率或反应预测；
- 需要改动 MCTS 搜索代码才能继续。

## 必须提交的报告

生成同编号 REPORT-006，记录两版输出统计、diagnosis 事件、history-integrity 归属说明，并更新 `STATE.md`。
