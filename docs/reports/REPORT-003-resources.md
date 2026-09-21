# REPORT-003：资源全量重新解析与结构检查（data/derived/v1）

## 对应任务

- 任务 ID：TASK-003
- 任务文件：[`docs/tasks/TASK-003-resources.md`](../tasks/TASK-003-resources.md)
- 状态：Completed（完成）
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：aa012ca（docs/ 治理与文档）/ 1f027a8（flavoretro/、tests/、web/、configs/）/ 2b305a4（scripts/、metadata/、environment/、operations/）；TASK-008 分层初始提交时入库
- 执行窗口：2026-09-21 09:42—09:44（本机时间）
- 文档形态：本文件由 TASK-009 将速记体原文扩写为详细格式，事实未变

## 改动文件

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `flavoretro/`：资源、搜索、共享 API 逻辑 | `__init__.py` | 新建；包入口 |
| `flavoretro/`：资源、搜索、共享 API 逻辑 | `resources.py` | 新建；无损准入 + 确定性本地结构检查构建器（该首版后被来源定位修复版替代，归档为 `operations/archive/resources-v1.py`） |
| `docs/tasks/`：事前合同 | `TASK-003-resources.md` | 新建；本任务的批准合同 |
| `docs/reports/`：事后证据 | `REPORT-003-resources.md` | 新建；本报告（速记原文；TASK-009 扩写为当前详细版） |
| 仓库根目录：项目治理入口 | `STATE.md` | 更新至本任务完成时的当前事实 |
| `data/derived/v1/`：派生数据（生成，不入 Git） | `records.json`、`manifest.json` | 新建；正式派生数据集，合计 3,059 条 |
| `data/derived/replay-v1/`：派生数据（生成，不入 Git） | `records.json`、`manifest.json` | 新建；同一构建器第二遍重放输出，仅用于一致性核对 |
| `operations/`：治理日志（不入 Git） | `command-0004.log`、`command-0005.log` | 新建；两次构建的完整输出（含 RDKit 警告） |

## 实际改动

1. 原则：不沿用旧库统计，对 TASK-002 准入的只读副本全量重新解析；以来源哈希 + 定位生成稳定 ID；保留原字段；解析失败与重复名单独保留；全部记录保持 candidate，未独立审核原始论文/供应。
2. 交付 `flavoretro/resources.py`：无损准入与确定性本地结构检查；`manifest.json` 记录 `code_sha256` 与 `sources_sha256`，把输出绑定到构建器源码与来源快照。
3. 构建环境：当时解释器为 `/home/ljx/miniforge3/envs/retro/bin/python`，RDKit 2023.09.6；正式构建 `python -B -m flavoretro.resources data/derived/v1`，重放构建输出至 `data/derived/replay-v1`。
4. 两次运行输出的 `records.json` 与 `manifest.json` 逐字节一致。
5. 计数（构建器输出的原始计数 JSON，原样保留）：

```json
{
  "code_sha256": "6d383883c6d75e80c6934d41cb033b4bc58411750a4b84ae9fb095125a810b43",
  "counts": {
    "molecule": 156,
    "molecule_duplicate_names": 2,
    "molecule_failures": 4,
    "note_reaction": 508,
    "paper": 15,
    "scifinder_reaction": 2301,
    "stock": 49,
    "supplier": 22,
    "template": 2
  },
  "name_conflicts": 3,
  "production_records": 0,
  "rdkit": "2023.09.6",
  "records_sha256": "e09c2906cf900514f357a58abeae3b040cb4547b189b3c25c724e48c624fe141",
  "schema_version": 1,
  "sources_sha256": "d7de679a973ae5017cd1e171d4c5acff8cbbdb75facd3889e36dc41c6191246f",
  "yield_missing": 1075,
  "yield_zero": 0
}
```

6. 记录构成：molecule 156、note_reaction 508、paper 15、scifinder_reaction 2301、stock 49、supplier 22、template 2，七类合计 3,053 条；加上单独保留的 2 个重复名与 4 个解析失败，总计 3,059 条。
7. `name_conflicts=3`：3 个名称/连接冲突本次重新比较复现；涉及来源的参考响应仍为旧快照，未据新证据改写。
8. `production_records=0`：没有任何记录被晋级；`yield_missing=1075` / `yield_zero=0`——真实来源中无数值零，零与缺失分开记录，零值保护另用合成测试覆盖。
9. RDF 分子 sanitize 警告保留于构建日志，不能按解析数量宣称化学有效。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| `python -B -m flavoretro.resources data/derived/v1`（`operations/command-0004.log`） | rc=0；输出上方计数 JSON。该日志为本机日志，被 `.gitignore` 排除不入 Git，关键输出已内联 |
| 同一构建器第二遍 `python -B -m flavoretro.resources data/derived/replay-v1`（`operations/command-0005.log`） | rc=0。该日志为本机日志，被 `.gitignore` 排除不入 Git，关键输出已内联 |
| 重放一致性 | 通过：`operations/events.jsonl` 中 2 条 `replay_verified` 事件确认两次输出的 `records.json`（sha256=e09c2906…）与 `manifest.json`（sha256=a38aa600…）逐字节一致 |
| 记录守恒 | 通过：156+508+15+2301+49+22+2+2+4=3,059，与合计一致 |
| 3 个已知名称/连接冲突 | 通过：本次重新比较复现，`name_conflicts=3` |
| 候选边界 | 通过：`production_records=0`，无晋级记录 |

## 与任务合同的偏差

无。

## 已发现但未修改的问题

- RDKit sanitize 警告（`Can't kekulize`、`SMILES Parse Error` 等）保留于 `operations/command-0004.log`，未逐条人工处置。
- 2 个重复名与 4 个解析失败单独保留、不修复。

## 遗留风险

- 所有记录均为 candidate，无独立审核；解析通过不构成化学有效性证据。
- v1 中 508 条 note_reaction 的来源文件名因旧库改名（`YY-MM-DD ` 空格形式改为 `YYMMDD-` 形式）显示未定位；该问题后由 TASK-007-P1 处理。

## 仓库与 CI 状态

本报告所述操作发生时（2026-09-21 上午），仓库已 `git init` 但尚无任何提交、未配置远端、无 CI。本任务涉及的已跟踪文件（`flavoretro/` 包与 `docs/` 文档）随 TASK-008 的分层初始提交入库（aa012ca / 1f027a8 / 2b305a4）；`data/derived/` 与 `operations/command-0004/0005.log` 仅存在于本机。

## 建议的下一任务

TASK-004：运行时与搜索服务（在已构建资源之上建立搜索运行时）。按流程不自动开始。
