# TASK-007：最终独立验收与交接

## 合同元数据

- 任务 ID：TASK-007
- 状态：已完成（Completed）
- 批准：Cano（agent_delegated，2026-09-21）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 执行窗口：2026-09-21 09:58—10:00
- 文档形态：TASK-009 由速记体扩写，范围与结论未变

## 目标

避免把"代码存在"当作"重建完成"。对 TASK-001—006 重建出的系统做最终独立验收，汇总本次新产生的工程证据与仍然存在的研究缺口，形成可交接的交接物：用户运行说明、环境重建说明与锁定、测试合同继承映射、发布状态登记与额度快照。

## 背景

历史项目 `/home/ljx/retro_synthesis` 保持只读，重建工作在本仓库完成。到本任务时，代码与数据已在工程层面可运行，但存在三类交接障碍：

1. 缺少面向使用者的运行说明和面向新机器的环境重建说明；
2. 测试体系继承自历史项目的 67 个测试，缺少逐条继承映射，无法说明哪些历史行为已被覆盖、哪些被有意放弃；
3. 系统的科学证据状态（来源审核、供应商证据、独立标注、盲测等）此前散落在各处，没有一份机器可读的发布状态登记。

本合同起草时仓库尚无任何 Git 提交；分层初始提交最终在 TASK-008 形成。

## 范围

### 允许项

- 运行完整测试套件与工程检查（依赖一致性、节点/来源/权限/输出哈希校验）；
- 验收 CLI、HTTP 接口与浏览器界面，核对当前实验产物；
- 核对历史目录完整性（对 33,146 条路径基线做 after 对比）；
- 编写环境清单与用户运行说明、测试合同继承映射、资源统计、TASK/REPORT/STATE/ADR 导航；
- 登记发布状态与额度快照；Git 提交。

### 禁止项

- 伪造正式盲测、独立标注、供应商核查或人工实验证据；
- 使用额度重置卡（本次不使用；账户快照不能归因本任务总耗费）；
- 修改历史目录 `/home/ljx/retro_synthesis` 的任何内容；
- 将受限数据（`data/`、`outputs/` 载荷）加入 Git；
- 把工程测试通过表述为化学有效性。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| 仓库根：项目入口 | `README.md` | 项目定位、启动方式、证据边界入口 |
| `docs/`：使用者文档 | `docs/USER_GUIDE.md` | 用户运行说明（命令、数据版本、重放行为） |
| `docs/`：测试治理 | `docs/TEST_CONTRACTS.md` | 历史 67 测试 → 本次合同测试的继承映射 |
| `environment/`：环境重建 | `environment/README.md`、`environment/pip-freeze.txt` | 重建步骤；291 行锁定清单 |
| `metadata/`：发布状态 | `metadata/release.json` | 六维证据状态与保留决定（见下） |
| `operations/`：运行留痕 | `operations/usage-snapshot.json` | 账户额度快照（非任务归因） |
| `operations/`：完整性基线 | `operations/history-before.json` | 只读基线，本任务仅对比不修改 |

## 非目标

- 不执行正式盲测、独立化学标注、供应商核查或湿实验；
- 不将系统认证为 production（决定为 `retain_candidate_do_not_certify_production`）；
- 不关闭 `release.json` 中任何 `unresolved` / `not_executed` 项，只登记现状；
- 不归因本任务的额度总耗费（无初始快照，账户级快照不支持任务级归因）。

## 必须执行的操作

1. 依赖一致性检查与完整工程检查。
2. 历史目录完整性 after 对比（基线 33,146 路径）。
3. 编写 README、用户指南、环境重建说明与测试合同继承映射。
4. 导出 291 行 `pip-freeze.txt` 环境锁定。
5. 生成 `metadata/release.json`，登记六个外部验证维度与保留决定。
6. 记录账户额度快照并标注其归因限制。
7. 形成交接汇总（原计划 REPORT-007，实际由 TASK-008 的 REPORT-008 承接，见"必须提交的报告"）。

## 验收标准

- [x] 旧库 33,146 条路径基线比较无变更（command-0025：`{"entries": 33146, "changed": [], "unchanged": true}`）。
- [x] 重建系统运行无历史 `src` 依赖。
- [x] 新产物均有对应任务合同与事实报告承接。
- [x] 受限数据未入 Git（`data/`、`outputs/` 保持忽略）。
- [x] 全部工程检查通过；科学未验证项在 `release.json` 中明确标注。
- [x] `.venv/bin/python -m pip check` 通过（command-0024：`No broken requirements found.`）。

`metadata/release.json` 登记内容：`status=research_candidate`、`primary_source_review=unresolved`、`current_vendor_evidence=unresolved`、`independent_chemical_labels=not_available`、`formal_benchmark=not_executed`、`public_deployment=not_requested`、`user_evaluation=not_performed`、`decision_authority=agent_delegated`、`decision=retain_candidate_do_not_certify_production`。

额度快照要点（`operations/usage-snapshot.json`）：`snapshot_scope=account_not_task`；primary 额度已用 88%（300 分钟窗）、secondary 63%（10080 分钟窗）；`available_reset_credits=2`、`resets_consumed_this_run=0`；无初始快照，不能归因本任务总耗费；本次不使用额度重置卡。

## 验证

```bash
.venv/bin/python -m pip check
python scripts/history_guard.py after   # 该脚本后于 TASK-008 归档至 operations/archive/
```

已知留痕偏差：`history_guard.py` 硬编码输出路径，其产物 `outputs/validation/history-integrity.json` 归入 TASK-006 名下，实为本次 after 对比的结果。

## 停止条件

- 旧库出现漂移、文件被覆盖或基础测试失败：先诊断并报告，不得以报告掩盖问题。

## 必须提交的报告

原计划生成 `docs/reports/REPORT-007-handoff.md`；实际未单独生成，README 一度留下指向它的死链。交接事实最终由 TASK-008 的 `docs/reports/REPORT-008-human-github-handover.md` 承接，死链在 TASK-008 修复。STATE.md 已更新至对应事实。
