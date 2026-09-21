# REPORT-004：独立实时 MCTS 与共享服务

## 对应任务

- 任务 ID：TASK-004
- 任务文件：`docs/tasks/TASK-004-runtime.md`
- 状态：Completed（完成）
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：`aa012ca` / `1f027a8` / `2b305a4`（TASK-008 分层初始提交时入库）
- 文档形态：TASK-009 由速记体扩写，事实未变
- 执行时段：2026-09-21 09:44—09:57

## 改动文件

生成但不进入 Git 的文件：`outputs/runs/<run_id>/`（逐次运行的不可变 run/error 记录，含 manifest 与 worker.log）与 `outputs/validation/live-smoke.json`（真实 smoke 汇总细节），均为本机运行产物。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `configs/`：版本化运行配置 | `configs/search.json` | 新建。三档 profile（quick 单阶段 45 s/50 迭代；balanced 两阶段 120 s/100 迭代 + 240 s/800 迭代；strict 单阶段 360 s/1800 迭代）、envelope 上限（depth 10 / branching 24 / nodes 25000）、candidate_pool 25、display_k 5、policy_weights（uspto 1.0 / ringbreaker 0.65）、PUCT c_init 1.4 / c_base 19652.0；`status=provisional_not_optimized`。 |
| `flavoretro/`：包本体 | `flavoretro/search.py` | 新建。AiZynthFinder 节点覆盖层：PUCT 选择、policy 融合、有界备选扩展。 |
| `flavoretro/`：包本体 | `flavoretro/contracts.py` | 新建。Pydantic 请求/结果模型，定义对外数据合同。 |
| `flavoretro/`：包本体 | `flavoretro/policies.py` | 新建。保守候选库存与已知危害过滤；仅检查已知特征与元数据，无安全认证。 |
| `flavoretro/`：包本体 | `flavoretro/worker.py` | 新建。一请求一进程的隔离执行体；无缓存、无旧 import。 |
| `flavoretro/`：包本体 | `flavoretro/service.py` | 新建。CLI 与 HTTP 共享的隔离实时执行边界。 |
| `flavoretro/`：包本体 | `flavoretro/cli.py` | 新建。命令行入口，调用同一 `service.search`。 |
| 根目录：包配置 | `pyproject.toml` | 新建。声明 Python `>=3.10,<3.11`。 |
| `scripts/`：可复现脚本 | `scripts/smoke.py` | 新建。真实引擎 smoke（quick、重复 quick、candidate balanced 两阶段）。 |
| `tests/`：合同测试 | `tests/test_contracts.py` | 新建。8 项 DataContracts + 8 项 RuntimeContracts。 |
| `tests/`：合同测试 | `tests/test_live.py` | 新建。3 项 LiveContracts：test_actual_node_bound_and_partial_paths、test_fresh_real_engine、test_seed_scoped_structural_identity。 |
| `docs/adr/`：长期决策 | `docs/adr/ADR-002-search-evidence.md` | 新建。记录"先可解释的实时研究产品，再逐证据晋级"的决策。 |

## 实际改动

本节面向未接触过旧项目的读者：本项目是一个逆合成路线搜索工具，给定目标分子，用蒙特卡洛树搜索（MCTS）向后拆解为可获得的原料；TASK-004 的目标是在不继承旧代码的前提下，先建立可信的执行身份。

1. 从零实现 `flavoretro` 包：原生（native）与优化（optimized）两棵搜索树的适配、共享子进程服务与 CLI；没有导入旧项目 `src`。
2. 搜索引擎为外部开源逆合成库 AiZynthFinder 4.4.1 的 MCTS，通过其已安装接口调用，不修改该库本身；`flavoretro/search.py` 在其上叠加 PUCT 选择、policy 融合与有界备选扩展。
3. 每次提交都启动新进程、新 MCTS、新 run ID；worker 无缓存，CLI 与后续 Web 入口共用同一 `service.search`。
4. 模型资产为 5 个独立复制的外部预训练文件（ONNX/CSV），逐文件 SHA-256 登记于运行 manifest；领域 2 候选模板未启用。
5. 默认 0 条 verified stock：搜索产生 partial（未闭合到已确认库存的路线）是真实证据边界，不凑路线。
6. 候选库存探索仅在显式开启时启用，排除 virtual 与名称冲突；其闭合只能标记 surrogate，始终非 actionable。
7. 安全检查仅覆盖已知危害特征与元数据，未做独立前向模型验证；未知风险不标安全。
8. 原生树没有等价节点上限，保留为同资产短预算对照基线，不能称正式盲测。
9. 结构 route ID 与 seed 分阶段保存；不承诺墙钟预算导致的逐位可重复性。
10. 环境缺少 FastAPI，HTTP 服务改用 Python 标准库实现；未修改共享 `retro` conda 环境。
11. 关键 decision 之一：原生路线选择器 `nmin=0` 会丢弃全部未解候选，第一次 smoke 生成树但 `min_routes=0`、无 partial 输出；改为 `nmin=1` 后返回真实 partial，不伪造路线。首次失败范围保留未删。
12. 关键 decision 之二：AiZynthFinder 会原地修改配置字典，因此每个请求须先保存有效配置再交隔离进程执行。
13. 验收修正（acceptance_correction）：partial 结果曾被"根不变路线"主导；改为选择真实前沿节点、有界候选池、结构去重，并禁止候选集只含根路线。此前实验保留，重跑验收。

## 验证

注：`command-XXXX` 指 `operations/command-XXXX.log`，为本机日志，不入 Git，关键输出已内联于本表。

| 命令或检查项 | 结果 |
| --- | --- |
| CLI 单次运行（command-0006） | rc=0：status ok、execution_source=live_aizynthfinder_mcts、node_count 31、release_ready=false、limitations 5 条；资产与代码哈希写入 manifest |
| `python -c "import fastapi"`（command-0007） | rc=1：ModuleNotFoundError → decision：改用标准库 HTTP |
| 查询 playwright 可用性（command-0008） | 不存在（输出 None） |
| `scripts/smoke.py` 第 1 次（command-0009） | rc=0：quick 单阶段，nodes=[33]，run_id=20260921T014726-c7b43a6d… |
| `scripts/smoke.py` 第 2 次（command-0009） | rc=0：重复 quick，nodes=[31]，run_id=20260921T014728-501caa5c…；两次 quick run ID 不同 |
| `scripts/smoke.py` 第 3 次（command-0009） | rc=0：candidate balanced 两阶段，nodes=[50,59]，run_id=20260921T014730-4698a7e0… |
| 三次 smoke 汇总细节 | 记录于 `outputs/validation/live-smoke.json`（本机产物，不入 Git） |
| `python -m unittest`（command-0012） | rc=0：16 tests OK（8 项 DataContracts + 8 项 RuntimeContracts） |
| `python -m unittest` 全量（command-0021） | rc=0：25 tests OK（含后续任务新增的 Topology 与 Live 合同） |

## 与任务合同的偏差

无。验收标准逐项核验如下：真实 MCTS 重复调用生成不同 run ID（command-0009 三次运行 run ID 互不相同）；有效约束与新运行哈希绑定（command-0006 manifest 含资产与代码哈希）；错误与超时可追踪（不可变 run/error 记录于 `outputs/runs/<id>/`）；无旧目录运行依赖（代码全新实现，未导入旧 `src`）；单元测试与真实 smoke 均通过。

合同非目标（参数最优性、独立化学收益、正式盲测、湿实验）均未触碰；未知风险未标安全。

## 已发现但未修改的问题

第一次 smoke 的失败输出（生成树但 `min_routes=0`、无 partial）有意保留未删，作为失败探索记录；修复后已重新验证。

## 遗留风险

- 搜索参数暂定（`provisional_not_optimized`），未调优；
- 无独立前向模型验证，安全过滤不构成认证；
- 原生基线树无等价节点上限；
- 墙钟预算不保证逐位可重复性；
- 领域 2 候选模板仍未启用。

## 仓库与 CI 状态

报告时点仓库已 `git init` 但无任何提交、无远端 origin、无 CI；本报告所述文件随 TASK-008 分层初始提交入库。验证所引用的 `command-XXXX.log` 为本机日志，不入 Git，关键输出已内联。

## 建议的下一任务

TASK-005（工作台与新运行比较）；历史上已与 TASK-004 并行推进，此处仅为记录，不自动开始。
