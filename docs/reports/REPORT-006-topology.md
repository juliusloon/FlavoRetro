# REPORT-006：独立糖苷连接诊断

## 对应任务

- 任务 ID：TASK-006
- 任务文件：`docs/tasks/TASK-006-topology.md`
- 状态：Completed（完成）
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：`aa012ca` / `1f027a8` / `2b305a4`（TASK-008 分层初始提交时入库）
- 文档形态：TASK-009 由速记体扩写，事实未变
- 执行时段：2026-09-21 09:54—10:00

## 改动文件

生成但不进入 Git 的文件：`outputs/validation/topology-v1.json`（首版失败输出，保留未删）与 `outputs/validation/topology-v2.json`（修复后输出），均为本机运行产物。

另有 `outputs/validation/history-integrity.json`（历史目录完整性对比）归本任务名下，但实际执行于 TASK-007 时段，见"实际改动"第 11 条。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `flavoretro/`：包本体 | `flavoretro/topology.py` | 新建。独立结构诊断模块：有限 5/6 元含氧糖环候选检测，O/C/N/糖间连接分类，断开—重接图一致性回放；不修改 MCTS，独立于搜索 policy。 |
| `tests/`：合同测试 | `tests/test_topology.py` | 新建。TopologyContracts 5 项，另加绝对立体回归 test_absolute_stereo_survives_neighbor_reordering。 |

## 实际改动

本节面向未接触过旧项目的读者：糖苷连接诊断回答的是"分子中哪些位点是糖环、糖与苷元以何种原子连接"这一结构问题。TASK-006 把它做成独立自检工具，与搜索收益分线，避免把图算法自洽误读为化学预测能力。

1. 结构诊断独立于搜索 policy：作为单独模块运行（`python -B -m flavoretro.topology`），不接入 MCTS expansion，不修改搜索行为。
2. 检测与分类范围：有限 5/6 元含氧糖环候选检测，O/C/N/糖间连接分类。
3. 自检方式：断开—重接图一致性回放；对本次 156 个分子、192 个位点运行，保留未检出与未解析记录。
4. 首版在 192 个位点中出现 55 次立体图往返回放失败（roundtrip_failures=55）。
5. diagnosis 定位原因：手性标签的语义是相对的，依赖邻居顺序，而断开—重接会改变邻居顺序。
6. 修复方法为校正置换奇偶性；修复后 192/192 图一致（roundtrip_failures=0）。
7. 顺带修正一处 logging 关键字冲突（具体位置未单独记录）。
8. 原失败文件 `topology-v1.json` 保留未删；新增带绝对立体的回归测试，防止修复回退。
9. 修复后计数 JSON 原样保留如下；其中 scope 字段声明本输出是开发结构诊断，不是 precision/recall 或 MCTS 改进证据：

```json
{
  "code_sha256": "44dd9cbe05f5722b5c3ff3c1bd626fc53f5f5b904506b328bce383a3fbbbf3ec",
  "detected": 132,
  "input_sha256": "e09c2906cf900514f357a58abeae3b040cb4547b189b3c25c724e48c624fe141",
  "molecules": 156,
  "roundtrip_failures": 0,
  "scope": "development structural diagnostic; not precision/recall or MCTS improvement",
  "sites": 192
}
```

10. 修复前后 code_sha256 从 b7583f23… 变为 44dd9cbe…，而 input_sha256、detected、sites 均不变：改动在代码侧，输入与检出规模一致。
11. 附带职责说明：`outputs/validation/history-integrity.json`（历史目录完整性 after 对比结果：33,146 条零漂移）因 `history_guard.py` 硬编码在 TASK-006 名下生成，实际执行于 TASK-007 时段（command-0025），特此说明归属差异。
12. 继承与边界：设计继承旧糖苷审计知识（O/C 分类、糖间键、普通醚阴性、重编号不变性），但不以历史 98/98 作为本次指标；无独立 gold labels，不报 precision/recall；图自洽不能解释为反应预测成功。

## 验证

注：`command-XXXX` 指 `operations/command-XXXX.log`，为本机日志，不入 Git，关键输出已内联于本表。

| 命令或检查项 | 结果 |
| --- | --- |
| topology 首跑 → `outputs/validation/topology-v1.json`（command-0016） | rc=0：roundtrip_failures 55；detected 132 / sites 192 / molecules 156 / input_sha256=e09c2906…；code_sha256=b7583f23… |
| `python -m unittest`（command-0017） | rc=0：21 tests OK（新增 TopologyContracts 5 项） |
| topology 二跑 → `outputs/validation/topology-v2.json`（command-0019） | rc=0：roundtrip_failures 0；detected 132 / sites 192 / molecules 156 / input_sha256 均不变；code_sha256=44dd9cbe… |
| `python -m unittest`（command-0020） | rc=0：22 tests OK（新增 test_absolute_stereo_survives_neighbor_reordering） |
| 历史目录完整性对比（command-0025，TASK-007 时段执行） | rc=0：33,146 条 entries、changed=[]、unchanged=true；输出归 TASK-006 名下，见"实际改动"第 11 条 |

## 与任务合同的偏差

无。验收标准（普通醚阴性、O/C 正例、重编号不变性、全量 156 分子本次输出和错误统计）全部满足。

合同非目标（独立准确率、酶识别、真实反应条件、把图重接当作化学预测）均未触碰，未以历史 98/98 作为本次指标。

## 已发现但未修改的问题

首版失败输出 `topology-v1.json`（roundtrip_failures=55）保留未删，为有意保留的失败探索记录。

它与修复后的 `topology-v2.json` 共用同一 input_sha256（e09c2906…），可直接对比修复前后差异。

## 遗留风险

- 仅为开发自检，无独立真值（gold labels），不报 precision/recall；
- 诊断结果未接入 MCTS expansion，对搜索行为无影响；
- 图一致性不能解释为化学预测或反应成功；
- 检测范围限于 5/6 元含氧糖环候选，未覆盖其他环系。

## 仓库与 CI 状态

报告时点仓库已 `git init` 但无任何提交、无远端 origin、无 CI；本报告所述文件随 TASK-008 分层初始提交入库。验证所引用的 `command-XXXX.log` 为本机日志，不入 Git，关键输出已内联。`outputs/validation/` 下的三份 JSON 为本机运行产物，同样不入 Git。

## 建议的下一任务

TASK-007（交接）：结构诊断、运行时与工作台三条线均已闭环，适合整理交接。仅为建议，不自动开始。
