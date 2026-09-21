# TASK-003：来源保留的资源与结构 QC

## 合同元数据

- 任务 ID：TASK-003
- 状态：Completed
- 批准：Cano（agent_delegated，2026-09-21，用户授权本次重建自主逐项决策）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 文档形态：TASK-009 由速记体扩写，范围与结论未变

## 目标

在原始来源不可变（TASK-002 只读快照）的前提下，对全部准入资源重新解析并做确定性的本地结构检查：不沿用旧统计，分子解析与名称/供应审核分离，产出可离线重放、逐字节一致的派生记录层。完成判定：全量记录守恒、同一构建器两次运行输出逐字节一致、已知冲突复现并保留、全部记录保持 candidate。

## 背景

旧库复盘的核心教训（来源：`data/raw/legacy/docs/reports/260920-pre_refactor_project_retrospective.md`）是概念混淆：`parser-ready ≠ runtime-active ≠ chemistry-reviewed`；旧系统 150 条教学模板全部是 candidate、production 晋级为 0，却曾被统计数字包装得接近"可用"。因此本任务的解析原则是"来源保留"：保留原字段，不修补、不推断、不晋级；解析失败、重复名称、名称/连接冲突全部显式保留并计数。批准理由记录在案：原始来源不可变，分子解析与名称/供应审核必须分开——RDKit 能解析分子不代表名称或供应关系已被确认。

执行时使用的解释器为 `/home/ljx/miniforge3/envs/retro/bin/python`，RDKit 版本 2023.09.6。

## 范围

### 允许项

- 新建 Python 包骨架 `flavoretro/__init__.py` 与资源模块 `flavoretro/resources.py`（模块职责："Lossless admission and deterministic local structure checks"）。
- 对 `data/raw/legacy/` 全量准入资产重新解析：笔记反应、SciFinder RDF、分子库（含失败与重复项）、49 条库存、2 个模板、15 篇文献、22 份供应列表。
- 产出派生记录层 `data/derived/v1/`（records.json、manifest.json），并用同一构建器构建 `data/derived/replay-v1/` 作离线重放比对。
- 以源哈希 + 来源定位生成稳定记录 ID；零值与缺失分开计数。

### 禁止项

- 修改 `data/raw/legacy/` 任何字节；沿用旧库统计数字替代重新解析。
- 把 RDKit sanitize 警告（如 `Can't kekulize`、`SMILES Parse Error`）当作记录丢弃理由；不得以解析通过数宣称化学有效。
- 把任何记录晋级为 production 或独立证据；不做逐例原文人工审核。
- 自动补实验条件、确认原文/供应、推断缺失结构（见非目标）。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| flavoretro（包逻辑） | __init__.py、resources.py | 新增：包骨架与无损准入/确定性结构检查构建器 |
| data/derived（派生记录层） | v1/records.json、v1/manifest.json | 新增：解析记录与计数/哈希清单（Git 忽略） |
| data/derived | replay-v1/ | 新增：同构建器重放产物，用于逐字节比对 |
| operations（治理日志） | command-0004.log、command-0005.log | 新增：两次构建命令日志（均 rc=0） |
| docs/tasks、docs/reports | TASK-003、REPORT-003 | 新增：本合同与事后报告 |

## 非目标

- 不自动补实验条件；不确认原文或供应事实；不推断缺失结构。
- 不以解析通过作为晋级依据；不做任何化学有效性声明。
- 不解决名称/连接冲突（本次只重新比较并复现，参考响应仍为旧快照）。

## 必须执行的操作

1. 实现 `flavoretro/resources.py`：逐来源解析、保留原字段、源哈希+定位生成稳定 ID、零/缺失分开、失败与警告保留。
2. 构建 `data/derived/v1`：`python -B -m flavoretro.resources data/derived/v1`。
3. 用同一构建器离线重放：`python -B -m flavoretro.resources data/derived/replay-v1`；比对两次输出逐字节一致。
4. 对 3 个已知 stock 名称/连接冲突重新比较，确认复现。
5. 逐项给出 decision；未定位来源的记录显式标记。
6. 撰写 REPORT-003，更新 STATE.md。

## 执行结果摘要（写入 manifest.json 的计数）

- molecule 156（其中 duplicate_names 2、failures 4）；note_reaction 508；paper 15；scifinder_reaction 2301；stock 49；supplier 22；template 2。
- name_conflicts 3；production_records 0；yield_missing 1075、yield_zero 0（真实来源无数值零，零值保护由合成测试另行覆盖）。
- 环境指纹：rdkit 2023.09.6；`code_sha256=6d383883…`；`sources_sha256=d7de679a…`。
- 重放一致性：`records.json` sha256=e09c2906…、`manifest.json` sha256=a38aa600…，两次构建各产生 `replay_verified` 事件。

## 验收标准

- [x] 全量记录守恒（计数如上，无静默丢失；解析失败 4 条显式保留）。
- [x] 两次离线重放一致（records.json / manifest.json 逐字节相同）。
- [x] 三个已知 stock 名称/连接冲突本次重新比较并复现（参考响应仍为旧快照）。
- [x] 所有数据保持 candidate（production_records=0），无逐例原文人工审核冒充。
- [x] 逐项 decision；未定位来源显式标记。

## 验证

```bash
# 实际执行（2026-09-21 09:42—09:44 本地），解释器 /home/ljx/miniforge3/envs/retro/bin/python：
python -B -m flavoretro.resources data/derived/v1         # operations/command-0004.log，rc=0
python -B -m flavoretro.resources data/derived/replay-v1  # operations/command-0005.log，rc=0
# 两次输出逐字节一致：records.json sha256=e09c2906…，manifest.json sha256=a38aa600…
```

## 停止条件

- 原始哈希变化或记录丢失：停止并报告。
- 未知证据：局部标记 unresolved 后继续，不阻断整体。

## 必须提交的报告

完成、部分完成或失败时，均生成同编号 `docs/reports/REPORT-003-resources.md` 并更新 `STATE.md`（已执行）。
