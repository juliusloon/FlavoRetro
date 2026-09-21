# REPORT-002：历史资源准入复制与逐项来源登记

## 对应任务

- 任务 ID：TASK-002
- 任务文件：[`docs/tasks/TASK-002-admission.md`](../tasks/TASK-002-admission.md)
- 状态：Completed（完成）
- 批准：Cano agent_delegated（2026-09-21，于本次运行批准）；非人工科学审核
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：aa012ca（docs/ 治理与文档）/ 1f027a8（flavoretro/、tests/、web/、configs/）/ 2b305a4（scripts/、metadata/、environment/、operations/）；TASK-008 分层初始提交时入库
- 执行窗口：2026-09-21 09:40—09:42（本机时间）
- 文档形态：本文件由 TASK-009 将速记体原文扩写为详细格式，事实未变
- 阅读提示：本报告面向未接触过旧项目的研究者；文中"旧库"指 `/home/ljx/retro_synthesis`（只读保留在本机）

## 改动文件

准入的 114 个数据文件按来源目录分组列行，不逐条列；逐文件清单见 `metadata/sources.json`（TASK-007-P1 后增至 123 条；TASK-002 时点的 114 条版本留档为 `metadata/sources-v1.json`）。数据文件全部落位 `data/raw/legacy/<原相对路径>`，权限 0444，被 `.gitignore` 排除不入 Git。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `data/raw/legacy/import_raw/`：不可变本地副本（64 文件，不入 Git） | 30 份 A3 文献合成 xlsx、22 份供应证据 xlsx、9 个 SciFinder RDF、2 个 mhtml、1 个 `.DS_Store` | 新建只读副本；来源证据（source_evidence） |
| `data/raw/legacy/outputs/`：不可变本地副本（22 文件，不入 Git） | `scifinder_import/` 15 文件、`library_v3/` 2 文件、`retrospective/` 4 文件、`validation/` 1 文件 | 新建只读副本；含解析结果、分子库、复盘快照 |
| `data/raw/legacy/maintenance/`：不可变本地副本（17 文件，不入 Git） | 9 份 `dataset_cards` + 8 份 `source_manifests` | 新建只读副本；旧库维护期元数据 |
| `data/raw/legacy/data/`：不可变本地副本（5 文件，不入 Git） | 3 个 ONNX 模型 + 2 个模板 csv.gz | 新建只读副本；外部模型（external_model） |
| `data/raw/legacy/` 其余：不可变本地副本（6 文件，不入 Git） | `templates/` 4、`config/` 1、`docs/` 1 | 新建只读副本；候选模板/登记与复盘报告 |
| `metadata/`：来源与资源清单 | `sources.json` | 新建；114 条逐文件登记（字段见"实际改动"第 5 条） |
| `scripts/`：可复现编排与工具 | `admit.py` | 新建；一次性准入脚本，硬编码旧库路径（TASK-008 已归档为 `operations/archive/admit-task-002.py`，`scripts/` 下不再保留） |
| `outputs/validation/`：验收输出（不入 Git） | `historical-inventory-check.json` | 新建；181 条历史 inventory 哈希核对结果 |
| `docs/tasks/`：事前合同 | `TASK-002-admission.md` | 新建；本任务的批准合同 |
| `docs/reports/`：事后证据 | `REPORT-002-admission.md` | 新建；本报告（速记原文；TASK-009 扩写为当前详细版） |
| 仓库根目录：项目治理入口 | `STATE.md` | 更新至本任务完成时的当前事实 |
| `operations/`：治理日志（不入 Git） | `command-0003.log` | 新建；`admit.py` 完整输出 |

生成但不进入 Git 的文件汇总：`data/raw/legacy/` 下 114 个数据副本（不可变本地副本职责）、`outputs/validation/historical-inventory-check.json`（验收核对输出）、`operations/command-0003.log`（命令输出）——分别被 `data/`、`outputs/`、`operations/*` 的 `.gitignore` 规则排除。

## 实际改动

1. 背景：旧库复盘指出数据不少但证据未闭环；因此本任务只保留来源并逐文件登记边界，不继承旧库的历史生产状态。
2. 以 `python scripts/admit.py` 从只读旧库逐字节复制并落位 `data/raw/legacy/`，保持原相对路径：
   - 规模：114 个文件、共 157,940,327 字节；
   - 权限：副本全部设为只读 0444；
   - 脚本特性：`admit.py` 硬编码旧库路径，属一次性脚本（不复用、不入活动工具集）；
   - 旧库保护：全程仅读取源目录，未向旧库写入。
3. 准入角色分布：`source_evidence` 96、`candidate_data` 8、`external_model` 5、`historical_reference` 5；来源目录分布：`import_raw` 64、`outputs` 22、`maintenance` 17、`data` 5、`templates` 4、`config` 1、`docs` 1。角色语义：来源证据为原始文献/供应/数据库导出；候选数据为待审核的结构化登记；外部模型为第三方训练产物；历史参考仅供理解旧项目脉络。
4. `metadata/sources.json` 顶层结构：`schema_version=1`、`source_root=/home/ljx/retro_synthesis`、`files` 数组 114 条；每条记录中 `source_path` 为旧库原相对路径，`path` 为本仓库内落位路径。
5. 每条记录同时携带边界字段：`sha256`、`size`、`role`、`license_status=source_inherited_not_cleared_for_redistribution`、`review_status=historical_claims_only_not_revalidated`、`redistribute=false`。
6. 关键条目（外部模型 5）：
   - `uspto_model.onnx`（91.5 MB）
   - `uspto_filter_model.onnx`（16.8 MB）
   - `uspto_ringbreaker_model.onnx`（15.0 MB）
   - `uspto_templates.csv.gz`、`uspto_ringbreaker_templates.csv.gz`
7. 关键条目（候选数据 8）：`literature_registry.json`、`flavonoid_literature_reactions.json`、`production_template_registry.json`、`production_stock_registry.json`、`stock_layers_metadata.csv`、library_v3 分子库 2 文件、`stock_identity_review.json`。
8. 关键条目（历史参考 5）：复盘报告、`inventory.json`、`test_contract_catalog.md`、`early_template_search_summary.md`、`proposal_first_git_version.md`。
9. 其余分组：`import_raw` 64 项（30 份 A3 文献合成 xlsx、22 份供应证据 xlsx、9 个 RDF、2 个 mhtml、1 个 `.DS_Store`）、`maintenance` 17 项（9 dataset_cards + 8 source_manifests）、`scifinder_import` 15 项。
10. 有意不复制：旧源码整体、历史搜索结果、海报/答辩材料、论文草稿与审稿回复、`deploy/` 与 Dockerfile、AHP 问卷与可用性 SOP、MinerU 管线——与当前方向无关或为禁止项。未迁移历史运行结果；复盘快照只作为 reference。
11. 许可未清除公开再分发限制：全部 114 条记录 `redistribute=false`，仅本机保留。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| `python scripts/admit.py`（`operations/command-0003.log`） | rc=0；输出 `{"copied_files": 114, "bytes": 157940327, "historical_inventory_checks": 181, "drift": []}`。该日志为本机日志，被 `.gitignore` 排除不入 Git，关键输出已内联 |
| 复制哈希逐条相等 | 通过：114 条 `copy_verified` 事件追加至 `operations/events.jsonl` |
| 历史 inventory 哈希核对 | 通过：`outputs/validation/historical-inventory-check.json` 181 条全部 `matches=true`，`drift` 为空 |
| 副本只读权限 | 通过：114 个副本全部设为 0444 |
| 符号链接回旧目录 | 通过：无符号链接指向 `/home/ljx/retro_synthesis` |
| 逐文件许可边界登记 | 通过：114 条记录均含 `license_status`/`review_status`/`redistribute` 字段 |
| 模型与数据载荷不入 Git | 通过：全部落位 `data/` 下，被 `.gitignore` 排除 |

TASK-002 合同的五条验收（无符号链接回旧目录、复制哈希相等、清单逐项含许可边界、模型不入 Git、历史 inventory 哈希全部校验并报告漂移）与上表逐项对应，全部通过。

## 与任务合同的偏差

无。

## 已发现但未修改的问题

- `import_raw/.DS_Store` 随目录一并复制；无害，为保留来源原始性未剔除。

## 遗留风险

- 许可未清除：114 条记录全部 `license_status=source_inherited_not_cleared_for_redistribution`，数据不可公开再分发。
- 供应/文献快照仅为历史声称（`review_status=historical_claims_only_not_revalidated`），未经独立复核，不得当作已验证事实引用。

## 仓库与 CI 状态

本报告所述操作发生时（2026-09-21 上午），仓库已 `git init` 但尚无任何提交、未配置远端、无 CI。本任务涉及的已跟踪文件（`metadata/sources.json`、`docs/` 文档等）随 TASK-008 的分层初始提交入库（aa012ca / 1f027a8 / 2b305a4）；`data/`、`outputs/`、`operations/command-0003.log` 仅存在于本机。

## 建议的下一任务

TASK-003：来源保留的资源与结构检查（对准入副本全量重新解析并生成派生资源）。按流程不自动开始。
