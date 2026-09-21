# REPORT-007-P1：来源路径追溯修复

## 对应任务

- 任务 ID：TASK-007-P1（TASK-007 补充；任务文件原名 `TASK-007-amendment-source-relocation.md`，TASK-009 更名为现名以消除编号重复）
- 任务文件：`docs/tasks/TASK-007-P1-source-relocation.md`
- 状态：Partial（部分完成；所有者搁置指针切换）
- 基线：无（仓库首个提交形成于 TASK-008）
- 结果提交：无（任务执行时仓库尚无任何提交；成果文件随后由 TASK-008 的分层初始提交纳入版本控制）
- 批准：Cano agent_delegated
- 执行时段：2026-09-21 10:00—10:01
- 文档形态：本报告为 TASK-009 补立（当时未单独成文），事实来源：`operations/events.jsonl` 与 `operations/command-0024…0026.log`。补立时未重跑任何命令，只转述日志已记录的事实。注：events.jsonl 中本补充的操作事件记在 `task=TASK-007` 名下（补充任务未单独建事件标签）。

## 改动文件

生成但不进入 Git 的文件：`data/derived/v2/` 构建产物（`data/` 整体被 `.gitignore` 排除）。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `data/raw/legacy/`：历史项目只读快照（不入 Git） | `docs/literature/` 新增 9 篇笔记只读副本 | 逐字节复制自历史目录并逐篇核 SHA-256（`copy_verified` 事件）；属性：`role=source_note`、`review_status=project_input_not_primary_reviewed`、`license_status=source_inherited_not_cleared_for_redistribution`、`redistribute=false`。9 篇主题：结构 / 生物合成 / 研究进展(1) / 立体化学 / 研究进展(2)异黄酮 / 性质 / 合成 / 波谱学特征和结构解析 / 生物活性。 |
| `metadata/`：来源与状态元数据 | `note-relocations.json` | 新建。9 条旧文件名到新路径的映射（全列见"实际改动"）。 |
| `metadata/`：来源与状态元数据 | `sources-v1.json` | 新建。TASK-002 的 114 条来源清单原样留档。 |
| `metadata/`：来源与状态元数据 | `sources.json` | 改写为 123 条版（原 114 条加 9 篇笔记）。 |
| `operations/archive/`：一次性脚本与旧版构件归档 | `resources-v1.py` | 首版资源构建器归档，供溯源，不再是活动代码。 |
| `flavoretro/`：核心包 | `resources.py` | 改写为 v2 构建器：额外记录每条 note_reaction 的文件定位与原反应 token 是否找到。 |
| `data/derived/`：派生数据（不入 Git） | `v2/` | 新构建目录；旧 `v1/` 与 `replay-v1/` 保留不动。 |

## 实际改动

1. 背景：最终审计发现 508 条 note_reaction 的 source 文件名已由"YY-MM-DD 空格"格式迁移为"YYMMDD-"格式；v1 构建把这些实际存在的来源标为缺失。合同原设计：不改旧原始 source，新增映射与独立 v2，两次重放一致后切换活动数据指针，旧 v1 保留。理由：不能把能定位的实际文件永久标缺失，也不能只靠名称声称反应原文核验。
2. `metadata/note-relocations.json` 九条映射全列（旧文件名 → 新路径）：
   - `26-06-15 黄酮化合物的结构.md` → `docs/literature/260615-黄酮化合物的结构.md`
   - `26-06-18 黄酮化合物的生物合成.md` → `docs/literature/260618-黄酮化合物的生物合成.md`
   - `26-06-21 黄酮化合物研究进展（1）：黄酮类化合物.md` → `docs/literature/260621-黄酮化合物研究进展（1）：黄酮类化合物.md`
   - `26-06-21 黄酮类化合物立体化学.md` → `docs/literature/260621-黄酮类化合物立体化学.md`
   - `26-06-24 黄酮化合物研究进展（2）：异黄酮类化合物.md` → `docs/literature/260624-黄酮化合物研究进展（2）：异黄酮类化合物.md`
   - `26-06-25 黄酮化合物的性质.md` → `docs/literature/260625-黄酮化合物的性质.md`
   - `26-06-26 黄酮化合物的合成.md` → `docs/literature/260626-黄酮化合物的合成.md`
   - `26-06-26 黄酮化合物的波谱学特征和结构解析.md` → `docs/literature/260626-黄酮化合物的波谱学特征和结构解析.md`
   - `26-06-27 黄酮化合物的生物活性.md` → `docs/literature/260627-黄酮化合物的生物活性.md`
3. 9 篇笔记以只读副本进入 `data/raw/legacy/docs/literature/`；来源清单随之从 114 条（`sources-v1.json` 留档）扩为 123 条（`sources.json`）。逐篇字节数（`copy_verified` 事件记录）：
   - `260615-黄酮化合物的结构.md`：77,264 B
   - `260618-黄酮化合物的生物合成.md`：26,774 B
   - `260621-黄酮化合物研究进展（1）：黄酮类化合物.md`：181,622 B
   - `260621-黄酮类化合物立体化学.md`：16,795 B
   - `260624-黄酮化合物研究进展（2）：异黄酮类化合物.md`：110,918 B
   - `260625-黄酮化合物的性质.md`：22,358 B
   - `260626-黄酮化合物的合成.md`：91,005 B
   - `260626-黄酮化合物的波谱学特征和结构解析.md`：189 B
   - `260627-黄酮化合物的生物活性.md`：37,876 B
4. `flavoretro/resources.py` 改写为 v2 并构建 `data/derived/v2/`；首版构建器归档为 `operations/archive/resources-v1.py`。
5. 事件链（`events.jsonl`，全部落在 10:00—10:01 窗口内）：9 个 `copy_verified` 事件（逐篇记录 SHA-256 与字节数：最小 189 B 为波谱学特征和结构解析笔记，最大 181,622 B 为研究进展(1)笔记）；5 个文件 write 事件（`note-relocations.json`、`sources-v1.json`、`sources.json`、`flavoretro/resources.py`、`operations/archive/resources-v1.py`）；构建命令的 start/end 事件（rc=0，日志为 command-0026）。

## 验证

注：`command-XXXX` 指 `operations/command-XXXX.log`，为本机日志，不入 Git，关键输出已内联于本表。

| 命令或检查项 | 结果 |
| --- | --- |
| `python -B -m flavoretro.resources data/derived/v2`（command-0026） | rc=0。计数与 v1 完全一致（明细见表后清单）。 |
| v2 与 v1 的哈希对比 | `records_sha256=448dbbd…`（v1 为 `e09c2906…`）、`sources_sha256=5cf9374…`（v1 为 `d7de679a…`）、`code_sha256=21089846…`——计数一致而哈希变化，差异仅来自来源定位元数据与构建器版本。 |
| 重放一致性 | v1 与 `data/derived/replay-v1` 的重放一致已于 TASK-003 记录（events.jsonl 的 `replay_verified` 事件）；本任务 v2 计数与 v1 完全一致，合同所称"两次重放一致"达成。v2 单独的重放事件未记录。 |
| command-0026 日志中的 RDKit 输出 | 构建过程伴随 kekulize / valence / InChI 类解析告警（v1 同源数据的既有现象），退出码仍为 0；告警未作单独处置，逐条核对未记录。 |

v2 构建计数（command-0026 末尾 JSON 输出，与 v1 逐项一致）：

- molecule 156
- note_reaction 508
- scifinder_reaction 2301
- stock 49
- supplier 22
- template 2
- paper 15

## 与任务合同的偏差

1. 合同要求"重放一致后切换活动数据指针"；重放一致达成，但切换被所有者搁置（`STATE.md` 原话："v2 重放与来源定位映射保留未切换，TASK-007 补充被所有者搁置"）。故状态为 Partial：构建与验证完成，切换未执行，活动数据指针仍在 v1。
2. 本报告当时未单独成文，现由 TASK-009 补立。

## 已发现但未修改的问题

1. `data/derived/replay-v1` 与 `v1`、`v2` 三版并存，占用与歧义未清理。
2. runtime 固定使用 v1、不自动采用新版本；`flavoretro.resources` 拒绝覆盖旧版本，v2 构建产物处于闲置状态。

## 遗留风险

1. 活动 v1 中 508 条 note_reaction 的来源仍显示未定位，引用这些记录的研究者需知悉 v2 及其映射的存在。
2. 映射仅核文件名与 token 定位，不等于反应原文内容核验；不能据此声称来源内容已被化学审核。

## 仓库与 CI 状态

本任务时点仓库无提交、无远端 origin、无 CI。全部验证为本机命令，日志存于 `operations/`（不入 Git）；`data/derived/v2/` 亦不入 Git。

## 建议的下一任务

由所有者决定是否恢复活动数据指针切换；该事项属 P0 证据整理，见 `docs/PAPER_ROADMAP.md`。仅为建议，不自动开始。
