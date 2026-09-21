# TASK-004：独立实时 MCTS 与共享服务

## 合同元数据

- 任务 ID：TASK-004
- 状态：Completed
- 批准：Cano（agent_delegated，2026-09-21）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 文档形态：TASK-009 由速记体扩写，范围与结论未变
- 执行时段：2026-09-21 09:44—09:57（与 TASK-005、TASK-006 时间交错）

## 目标

从零实现独立搜索运行时：设计采用独立代码，通过已安装 AiZynthFinder 4.4.1 接口实现，不 import 历史 `src`。先建立可信执行身份（真实引擎、可追踪运行、诚实限制），继承旧系统的 PUCT、跨 policy 先验融合、循环处理与候选替补知识，但不继承旧系统的分数与收益主张。完成判定：CLI 真实 MCTS 运行成功、单元测试与真实 smoke 通过、限制如实暴露。

## 背景

旧系统为 AiZynthFinder 4.4.1 MCTS 平台，含自适应 PUCT、跨 policy 先验融合（USPTO 1.0 / RingBreaker 0.65 / domain 1.35）、循环剪枝与 InChIKey transposition、结构 route ID、六级闭合法则（evidence/trusted/discovery/surrogate/heuristic/partial）、硬剪枝（剧毒/重金属/自燃/<-50℃/映射完整性/失败前向回放）以及四因子 AHP 评分（权重从未获专家验证）。复盘关键事实：13 靶标 benchmark solved 9/13 但 evidence-closed 为 0；reward 优先候选 solved 30/39 而 actionable 0/39——“候选闭合≠化学可行”是本次重建的核心教训。因此新运行时先建立可信执行身份：每次运行绑定新哈希、错误可追踪、闭合级别保守，不把旧的收益数字迁移过来。

## 范围

### 允许项

- 新建 `configs/search.json`（单一 profile 集）；
- 新建 `flavoretro/`：`search.py`、`contracts.py`、`policies.py`、`worker.py`、`service.py`、`cli.py`；
- 新建 `pyproject.toml`、`scripts/smoke.py`、`tests/test_contracts.py`、`tests/test_live.py`；
- 新建 `docs/adr/ADR-002`（先可解释的实时研究产品、再逐证据晋级的长期决定）；
- 产物写入 `outputs/runs/<id>/`（不可变 run 目录）。

### 禁止项

- import 或运行历史目录 `/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 的代码；
- 启用 2 个未审核领域模板候选；
- 将 candidate stock 闭合标为 evidence 或 actionable（actionable 恒 false）；
- 结果缓存、BFS 回退、伪造路线（nmin=0 丢弃全部未解候选属禁止行为）；
- 修改共享 retro Conda 环境（`import fastapi` 失败后不改环境，改用标准库 HTTP）；
- 把未知风险标记为安全。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途 |
| --- | --- | --- |
| `configs/` 版本化运行配置 | `search.json` | envelope depth 10/branching 24/nodes 25000；quick 单阶段 45s/50iter，balanced 120s/100iter+240s/800iter，strict 360s/1800iter；candidate_pool 25、display_k 5；policy_weights uspto 1.0/ringbreaker 0.65；puct c_init 1.4/c_base 19652.0；status 标为 provisional_not_optimized |
| `flavoretro/` 包 | `search.py` | AiZynthFinder 节点 overlay：PUCT、policy 融合、有界候选替补 |
| | `contracts.py` | 请求/结果数据契约 |
| | `policies.py` | 保守 candidate stock 与 known-hazard 过滤；不作安全认证 |
| | `worker.py` | 一次新进程一次请求，无结果缓存、无旧 import |
| | `service.py` | CLI 与 HTTP 共用的隔离实时执行边界 |
| | `cli.py` | 命令行入口 |
| `scripts/` | `smoke.py` | 新 MCTS 真实冒烟 |
| `tests/` | `test_contracts.py`、`test_live.py` | 契约与真实引擎测试 |
| `docs/adr/` | `ADR-002` | 证据分级的长期决定：默认无已审库存、候选闭合只标 surrogate、分项成本权重暂定 |
| `outputs/runs/` | `<run_id>/` | manifest 与 worker.log，不可变 |

## 非目标

- 参数最优性、独立化学收益证明、正式盲测、湿实验；
- 未知风险不标安全；
- 不验证旧分数或旧收益主张。

## 必须执行的操作

1. 实现原生基线+优化树双引擎与单一 profile 集；结构 route ID；模型快照。
2. CLI/HTTP 共用隔离子进程服务：每请求新进程、新 run ID、无结果缓存、不回退 BFS。
3. candidate stock 显式开关；闭合只能 surrogate；known-hazard/映射完整性/失败回放过滤。
4. 默认只用外部预训练策略（5 个 ONNX/CSV 模型），2 个领域模板候选不启用；默认 0 已审库存，partial 是真实覆盖缺口。
5. 运行 CLI 单次、smoke 3 次与 unittest，修复并复验，保留首次失败记录。

## 验收标准

- [x] 真实 MCTS 重复调用生成不同 run ID；新运行哈希绑定。
- [x] 有效约束执行：CLI 单次运行（command-0006.log，rc=0）status ok、execution_source live_aizynthfinder_mcts、node_count 31、release_ready=false、limitations 5 条（无独立审核 production 模板/库存；无实验可行性认证；无独立前向模型；未知危害仍是未知；原生基线无等价节点上限）。
- [x] 错误与超时可追踪：command-0007 rc=1（`import fastapi` ModuleNotFoundError）→ decision：标准库 HTTP、不改共享环境；command-0008 确认历史环境无 playwright。
- [x] smoke 3 次新 MCTS 通过（command-0009.log）。
- [x] unittest 16 tests OK（command-0012.log），修复后 25 tests OK（command-0021.log，新增 LiveContracts 3 项：test_actual_node_bound_and_partial_paths、test_fresh_real_engine、test_seed_scoped_structural_identity）。
- [x] 无旧目录运行依赖。

### 执行期事件（并入合同事实）

- decision：原生路线选择器 nmin=0 会丢弃全部未解候选，nmin=1 返回真实 partial 路线而不伪造路线；AiZynthFinder 会原地修改配置字典，须在调用前保存有效配置。
- acceptance_correction：目视检查发现 partial 结果被“根不变路线”主导→改为选真实前沿节点、有界候选池、结构去重、禁止只含根的路线；保留此前实验记录，重跑比较验收。
- 失败保留：第一次 smoke 生成树但 min_routes=0 无 partial 输出，修复后重新验证，首次失败记录不删除。

## 验证

```bash
python -m flavoretro.cli ...        # command-0006，rc=0
python scripts/smoke.py             # command-0009，3 次新 MCTS 通过
python -m unittest discover tests   # command-0012：16 OK；command-0021：25 OK
```

## 停止条件

- 共享环境缺依赖且需修改共享环境（已触发一次：fastapi 缺失，改走标准库而非改环境）；
- 需要 import 历史 src 才能继续；
- partial 结果无法在不伪造路线的前提下呈现。

## 必须提交的报告

生成同编号 REPORT-004，记录命令日志（command-0006—0021 中属本任务者）、失败与修复、限制清单，并更新 `STATE.md`。
