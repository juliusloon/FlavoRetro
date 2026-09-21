# TASK-002：资源快照与逐项来源登记

## 合同元数据

- 任务 ID：TASK-002
- 状态：Completed
- 批准：Cano（agent_delegated，2026-09-21，用户授权本次重建自主逐项决策）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 文档形态：TASK-009 由速记体扩写，范围与结论未变

## 目标

把旧库中与当前方向相关的来源与候选资产逐字节复制到新仓库的只读原始层，并为每个文件登记来源定位、哈希与许可边界；只保留来源，不继承任何历史生产状态。完成判定：114 个文件复制且哈希相等、全部置 0444 只读、`metadata/sources.json` 逐项含许可与审核状态、181 条历史 inventory 路径全部重校验并报告漂移（实际漂移为空）。

## 背景

旧库复盘（`data/raw/legacy/docs/reports/260920-pre_refactor_project_retrospective.md`）指出：旧库"数据不少但证据未闭环"——49 条分层库存（18 strict / 2 trusted / 29 virtual）、35.2M 行 ZINC、15 篇 DOI 文献卡、150 条教学模板（全部 candidate）、67 项测试，最终状态仍是 `candidate-not-production`（production 模板与库存晋级均为 0）。标题命中不等于原文确认、solved 多不等于化学有效。因此新仓库的资产策略是：复制来源证据与候选数据，逐文件固化哈希与许可边界，历史结论只作 reference；逐记录的来源与审核检查由 TASK-003 承担。

旧库 `/home/ljx/retro_synthesis` 规模 5.6 GB（旧库磁盘盘点 29,698 个文件），本任务只复制选定子集，整体源码与历史产物有意不复制（见非目标）。

## 范围

### 允许项

- 将选定文件从 `/home/ljx/retro_synthesis` 逐字节复制到 `data/raw/legacy/<原相对路径>`，复制后 SHA-256 相等验证并设 0444 只读。
- 创建来源清单 `metadata/sources.json`（schema_version 1，逐文件记录 source_path/path/sha256/size/role/license_status/review_status/redistribute）。
- 创建历史 inventory 校验产物 `outputs/validation/historical-inventory-check.json`。
- 复制类别：分子与反应候选数据、文献笔记、供应列表、原始 SciFinder 导出（RDF/mhtml/xlsx）、来源清单与数据集说明卡、外部预训练模型与模板文件；历史报告只以 `historical_reference` 角色入档。

### 禁止项

- 使用符号链接指回旧目录（必须真实复制字节）。
- 把历史搜索结果当作新结果；复制整个历史源码；公开或许可再分发任何复制资产。
- 把模型等大文件加入 Git（`data/` 由 `.gitignore` 排除）。
- 修改旧库任何文件；本任务不做逐记录化学审核（属 TASK-003）。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| data/raw/legacy（不可变原始层） | 114 个复制文件 | 新增：逐字节副本，0444 只读，Git 忽略 |
| metadata（来源元数据） | sources.json | 新增：逐文件来源、哈希、角色、许可与审核状态 |
| outputs/validation（校验产物） | historical-inventory-check.json | 新增：181 条历史 inventory 路径重校验结果 |
| scripts（活动工具） | admit.py | 新增：准入复制与登记脚本（本次执行入口） |
| operations（治理日志） | command-0003.log | 新增：admit.py 执行日志（rc=0） |
| docs/tasks、docs/reports | TASK-002、REPORT-002 | 新增：本合同与事后报告 |

## 准入结果摘要（执行事实）

`python scripts/admit.py` 输出 `{"copied_files":114,"bytes":157940327,"historical_inventory_checks":181,"drift":[]}`。每条记录 `copy_verified` 且统一 `license_status=source_inherited_not_cleared_for_redistribution`、`review_status=historical_claims_only_not_revalidated`、`redistribute=false`。

- role 分布：`source_evidence` 96、`candidate_data` 8、`external_model` 5、`historical_reference` 5。
- 来源目录分布：`import_raw` 64、`outputs` 22、`maintenance` 17、`data` 5、`templates` 4、`config` 1、`docs` 1。
- 关键条目：
  - 外部模型 5 个：`uspto_model.onnx`（91.5 MB）、`uspto_filter_model.onnx`（16.8 MB）、`uspto_ringbreaker_model.onnx`（15.0 MB）、`uspto_templates.csv.gz`、`uspto_ringbreaker_templates.csv.gz`。
  - 候选数据 8 个：`literature_registry.json`、`flavonoid_literature_reactions.json`、`production_template_registry.json`、`production_stock_registry.json`、`stock_layers_metadata.csv`、library_v3 分子库（csv + summary）、`stock_identity_review.json`。
  - 历史参考 5 个：复盘报告、`inventory.json`、`test_contract_catalog.md`、`early_template_search_summary.md`、`proposal_first_git_version.md`。
  - `import_raw` 64 个：30 份 A3 文献合成 xlsx、22 份供应证据 xlsx、9 个反应证据 RDF、2 个文献 mhtml、1 个 .DS_Store。
  - `maintenance` 17 个：9 份 dataset_cards、8 份 source_manifests；`outputs` 内含 scifinder_import 15 个。

## 非目标

有意不复制（与当前方向无关或被禁止）：旧源码整体；历史搜索结果（不作新结果）；海报/答辩材料（如 `docs/project/260729-academic_poster.md`）；论文草稿与审稿回复；`deploy/` 与 Dockerfile（从未真实部署）；AHP 专家问卷与可用性评价 SOP；MinerU 文献抽取管线（275 个派生文件）。

## 必须执行的操作

1. 依据选定清单执行 `python scripts/admit.py`：逐文件复制到 `data/raw/legacy/`、SHA-256 比对、设 0444。
2. 生成 `metadata/sources.json`，逐项写明许可边界与 `redistribute=false`。
3. 对历史 `inventory.json` 的 181 条路径重新计算哈希并比对，输出 `historical-inventory-check.json` 与漂移报告。
4. 确认 `data/` 与模型文件未被 Git 跟踪或暂存。
5. 撰写 REPORT-002，更新 STATE.md。

## 验收标准

- [x] 无符号链接回旧目录（全部为真实字节副本）。
- [x] 复制哈希相等（114/114 逐文件 SHA-256 验证通过）。
- [x] 清单逐项含许可边界（全部 `source_inherited_not_cleared_for_redistribution`、`redistribute=false`）。
- [x] 模型不入 Git。
- [x] 历史 inventory 哈希全部校验并报告漂移：181 条全部 `matches=true`，`drift` 为空。

## 验证

```bash
# 实际执行（2026-09-21 09:40—09:42 本地）：
python scripts/admit.py    # operations/command-0003.log，rc=0
# stdout: {"copied_files":114,"bytes":157940327,"historical_inventory_checks":181,"drift":[]}
```

## 停止条件

- 复制字节不同或源漂移：停止并报告，不继续登记。
- 许可不明的资产：保留为 local_only（`redistribute=false`），不作公开授权，记录后继续。

## 必须提交的报告

完成、部分完成或失败时，均生成同编号 `docs/reports/REPORT-002-admission.md` 并更新 `STATE.md`（已执行）。
