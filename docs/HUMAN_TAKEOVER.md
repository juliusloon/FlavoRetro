# 人接管指南

本指南回答一个问题：**agent 不在时，人如何安全地理解、验证并继续这个项目。**

## 三分钟读序

1. [README.md](../README.md) — 项目是什么、怎么启动。
2. [PROJECT.md](../PROJECT.md) — 目标、硬约束、非目标（尤其证据边界）。
3. [STATE.md](../STATE.md) — 当前事实与下一步。
4. [ARCHITECTURE.md](../ARCHITECTURE.md) — 每个文件/目录的职责，禁止重复事实源。
5. 本文件 + [WORKBENCH_ROADMAP.md](WORKBENCH_ROADMAP.md)（工作台方向）+ [PAPER_ROADMAP.md](PAPER_ROADMAP.md)（论文方向）。
6. 需要追溯某次任务的完整边界、执行事实与验证证据时，读 [tasks/](tasks/README.md) 与 [reports/](reports/README.md) 中同编号的 TASK/REPORT（CondRxnBench 详细格式；TASK-001—008 由 TASK-009 从速记体扩写，事实未变）。

## 系统能做什么、不能做什么

**能**：对黄酮/黄酮糖苷目标实时运行 MCTS 逆合成搜索（原生/优化树两引擎）；在浏览器工作台查看路线解读（评分构成、末端原料证据、逐步反应说明）、切换教学解释模式、浏览文献教学层（15 文献卡 + 反应课程）；浏览 3,059 条带来源哈希的候选资源；运行结构诊断（糖苷连接候选）；新跑短预算开发对照。

**不能**（当前证据状态下）：给出"已验证可合成"结论——无独立审核库存、无独立化学标签、无正式盲测；候选库存闭合只是 surrogate；工程测试结果不构成化学有效性；教学文案与文献课程是教学材料，不是操作规程。详见 `metadata/release.json` 与 `flavoretro/evaluation.py` 的 preflight。

## 常用命令（在仓库根目录）

```bash
.venv-foundation/bin/python -B -m unittest discover -s tests -v      # 全部测试（含 live，需本地模型）
.venv-foundation/bin/python -B scripts/smoke.py                      # 实时冒烟
.venv-foundation/bin/python -B -m flavoretro.web --port 8766         # 浏览器工作台
.venv-foundation/bin/python -B -m flavoretro.cli --smiles 'COc1ccc(O)cc1' --mode quick
.venv-foundation/bin/python -B -m flavoretro.evaluation --development  # 12 cell 开发对照（新跑）
.venv-foundation/bin/python -B -m flavoretro.evaluation                # 正式评测 preflight
.venv-foundation/bin/python -B -m flavoretro.topology outputs/validation/topology-new.json  # 结构诊断
```

`data/` 与 `outputs/` 不入 Git；新机器按 [environment/README.md](../environment/README.md) 建环境、再按 `metadata/sources.json` 恢复本地资产。

## 如何执行一次正式任务

沿用项目治理流（AGENTS.md）：

1. 以 [tasks/TEMPLATE.md](tasks/TEMPLATE.md) 写 `docs/tasks/TASK-NNN-*.md`：范围、理由、验收、停止条件；编号、状态与批准记录规则见 [tasks/README.md](tasks/README.md)。取得用户明确批准（或记录用户事先授权；agent 代行批准须记 `agent_delegated` 并注明依据，禁止写 `human_reviewed`）。
2. 所有写入/命令经 `scripts/operate.py` 记录：命令用 `python -B scripts/operate.py TASK-NNN <cmd>`；文件写入用 `python -B scripts/operate.py TASK-NNN --write <相对路径> --from <内容文件>`（自动记录前后 SHA-256）；或在 Python 中 import 其 `write`/`event`。
3. 完成后以 [reports/TEMPLATE.md](reports/TEMPLATE.md) 写同编号 `docs/reports/REPORT-NNN-*.md`（事实、哈希、失败也记录；Partial/Blocked/Failed 也必须写）。
4. 更新 STATE.md（只存当前事实）；长期决定按 [adr/0000-template.md](adr/0000-template.md) 写 ADR；代码变化提交 Git。

## 如何验证完整性

- **历史目录只读**：`/home/ljx/retro_synthesis` 的基线在 `operations/history-before.json`，核对脚本已归档为 `operations/archive/history_guard-task-001.py`（用法见其文件头，需 `before`/`after` 两次快照对比）。
- **派生数据防漂移**：`flavoretro.policies.records()` 每次读取都校验 活动指针与资源 manifest/records/source manifest 及 SQLite index 的 SHA-256，漂移即拒绝。
- **单次运行防篡改**：每次搜索的 `outputs/runs/<id>/manifest.json` 记录结果文件哈希，`/api/runs/<id>` 读取时复核。
- **配置入仓核对**：`configs/teaching_guidance.json`、`configs/literature_teaching_layer.json` 的 SHA-256 与旧项目源文件一致（登记见 REPORT-010 与 events.jsonl）。
- **Git**：`git log` 查看分层提交；仓库永不包含 `data/`、`outputs/` 载荷。

## 决策权边界（何时必须找人）

- 任何化学事实晋级（候选 → production）：需要独立来源审核 + 人工化学审核，agent 批准不算数。
- 许可证选择、GitHub 公开、数据再分发：仅所有者决定。
- 正式盲测、独立标注、湿实验：需要人事先设计并批准方案。
- 额度/重置卡使用：仅所有者决定。

## 已知坑

- 原 `.venv` 是历史借用环境；当前 `.venv-foundation` 已独立。换机器按 environment/README 与新 lock 重建。
- `python` 必须是 3.10（pyproject 限定 `>=3.10,<3.11`）。
- 不要在历史目录 `/home/ljx/retro_synthesis` 运行任何会写缓存的代码。
- 经挂载手段（如 /Volumes/cano）查看仓库时 `git status` 可能出现大量 mode 位 modified，这是挂载产物而非仓库事实；以 cano 服务器上的 `git status` 为准。
- `operations/events.jsonl` 有一条 2026-09-22 的误记行（task 字段为 "--help"），追加式日志不删改（见 REPORT-010）。
- 当前 47,836 条模型模板全部 classification=0.0 Unrecognized，不能凭补映射获得专属家族；界面明确 Unknown。深化教学须先获得可靠标签，见 WORKBENCH_ROADMAP P3。
