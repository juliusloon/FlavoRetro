# REPORT-007：最终独立验收与交接

## 对应任务

- 任务 ID：TASK-007
- 任务文件：`docs/tasks/TASK-007-handoff.md`
- 状态：Completed（完成）
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：无（任务执行时仓库尚无任何提交；成果文件随后由 TASK-008 的分层初始提交纳入版本控制）
- 批准：Cano agent_delegated
- 执行时段：2026-09-21 09:58—10:00
- 文档形态：本报告为 TASK-009 补立（当时未单独成文），事实来源：`operations/events.jsonl` 与 `operations/command-0024…0026.log`。补立时未重跑任何命令，只转述日志已记录的事实。

## 改动文件

任务合同要求的范围包括：完整测试、节点/来源/权限/输出 hash、CLI/HTTP/浏览器、当前实验、历史全目录完整性，以及环境清单、用户运行说明、测试合同继承映射、资源统计、TASK/REPORT/STATE/ADR 导航、Git 提交与额度快照。本任务落盘文件如下。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| 仓库根：项目门面 | `README.md` | 新建。项目定位、启动说明与文档入口（其死链问题在 TASK-008 才发现并修复）。 |
| `docs/`：项目文档 | `USER_GUIDE.md` | 新建。工作台使用说明，面向最终使用者。 |
| `docs/`：项目文档 | `TEST_CONTRACTS.md` | 新建。历史 67 项测试到本次合同的继承映射表，逐行列出历史知识、新实现/验收与本次边界三栏。 |
| `environment/`：运行环境重建与审计 | `README.md` | 新建。说明 `.venv` 由 retro conda python 创建、启用 system-site-packages，不是独立克隆的 Conda 环境；给出新机器重建步骤与"不要在历史目录运行构建、编译或测试"的约束。 |
| `environment/`：运行环境重建与审计 | `pip-freeze.txt` | 新建。291 行依赖锁定清单，入 Git。 |
| `metadata/`：来源与状态元数据 | `release.json` | 新建。发布状态声明（全文要点见"实际改动"），入 Git。 |
| `operations/`：本机操作证据（不入 Git） | `usage-snapshot.json` | 新建。账户额度快照，属被 `.gitignore` 排除的本地证据。 |

生成但不进入 Git 的文件：`operations/usage-snapshot.json`（见上表末行）与 `outputs/validation/history-integrity.json`（归属偏差见"与任务合同的偏差"）。

## 实际改动

1. 汇总交接文档：新建 `README.md`、`docs/USER_GUIDE.md`、`docs/TEST_CONTRACTS.md`，把合同要求的"用户运行说明、测试合同继承映射"落成文，避免把代码存在当作重建完成。
2. 环境锁定：新建 `environment/README.md` 与 291 行的 `environment/pip-freeze.txt`，明确 `.venv` 的来源与局限（非独立环境、未在全新机器重装验证）。
3. `metadata/release.json` 全文要点：`status=research_candidate`；`primary_source_review=unresolved`；`current_vendor_evidence=unresolved`；`independent_chemical_labels=not_available`；`formal_benchmark=not_executed`；`public_deployment=not_requested`；`user_evaluation=not_performed`；`decision_authority=agent_delegated`；`decision=retain_candidate_do_not_certify_production`。即：保留候选地位，不认证为可生产。文件全文如下：

```json
{
  "schema_version": 1,
  "status": "research_candidate",
  "primary_source_review": "unresolved",
  "current_vendor_evidence": "unresolved",
  "independent_chemical_labels": "not_available",
  "formal_benchmark": "not_executed",
  "public_deployment": "not_requested",
  "user_evaluation": "not_performed",
  "decision_authority": "agent_delegated",
  "decision": "retain_candidate_do_not_certify_production"
}
```

4. 额度快照（`operations/usage-snapshot.json`）要点：`snapshot_scope=account_not_task`；primary 88%（300 分钟窗）、secondary 63%（10080 分钟窗）；`available_reset_credits=2`、`resets_consumed_this_run=0`。无初始快照，不能归因任务耗费；本次未使用额度重置卡。文件全文如下：

```json
{
  "snapshot_scope": "account_not_task",
  "primary_used_percent": 88,
  "primary_minutes": 300,
  "primary_resets_at": 1789972638,
  "secondary_used_percent": 63,
  "secondary_minutes": 10080,
  "secondary_resets_at": 1790411951,
  "available_reset_credits": 2,
  "resets_consumed_this_run": 0,
  "limitation": "No initial account snapshot; cannot infer exact task consumption"
}
```

5. 合同明确不伪造正式盲测、独立标注、供应商核查或人工实验，本任务未执行这些事项。
6. 上述全部写入均经 `scripts/operate.py` 记录，`events.jsonl` 中每个文件都有对应 write 事件（含写入前后 SHA-256）。

## 验证

注：`command-XXXX` 指 `operations/command-XXXX.log`，为本机日志，不入 Git，关键输出已内联于本表。

| 命令或检查项 | 结果 |
| --- | --- |
| `.venv/bin/python -m pip check`（command-0024） | rc=0，输出 `No broken requirements found.` |
| `python scripts/history_guard.py after`（command-0025） | rc=0，输出 `{"entries":33146,"changed":[],"unchanged":true}`——历史目录 33,146 条路径全程零漂移 |

## 与任务合同的偏差

1. `outputs/validation/history-integrity.json` 因 `scripts/history_guard.py` 硬编码任务名而归入 TASK-006 名下：`events.jsonl` 中该文件的写入事件标记为 TASK-006，实际由本任务的 `after` 运行触发。
2. 本报告当时未生成；TASK-008 才发现 README 死链指向不存在的 `docs/reports/REPORT-007-handoff.md`，当时由 REPORT-008 临时承接交接汇总，现由 TASK-009 补立本文。

## 已发现但未修改的问题

无记录。

## 遗留风险

1. 科学验证六维度全部未关闭（`release.json`：`primary_source_review`、`current_vendor_evidence`、`independent_chemical_labels`、`formal_benchmark`、`public_deployment`、`user_evaluation` 分别为 unresolved / unresolved / not_available / not_executed / not_requested / not_performed）；工程验收不构成化学结论。
2. 额度快照为账户级且无初始值，不能归因本任务总耗费。

## 仓库与 CI 状态

本任务时点仓库无提交、无远端 origin、无 CI。全部验证为本机命令，日志存于 `operations/`（不入 Git）。

## 建议的下一任务

TASK-007-P1（来源路径追溯修复，当时随即执行）；其后 TASK-008（人接管友好化与 GitHub/论文导向整理）。仅为建议，不自动开始。
