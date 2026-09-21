# TASK-007-P1：来源路径追溯修复（TASK-007 补充）

## 合同元数据

- 任务 ID：TASK-007-P1（原文件名 `TASK-007-amendment-source-relocation.md`；TASK-009 重命名以消除双 TASK-007 编号冲突，内容不变）
- 状态：部分完成（Partial）——v2 派生数据构建完成且重放一致，活动数据指针切换被所有者搁置
- 批准：Cano（agent_delegated，2026-09-21）
- 基线分支：main
- 基线提交：无（仓库首个提交形成于 TASK-008）
- 人工负责人：项目所有者（ljx）
- 执行者：Cano（Kimi Code CLI agent 会话）
- 修改预算：当时未设定
- 执行窗口：2026-09-21 10:00—10:01（紧随 TASK-007）
- 文档形态：TASK-009 由速记体扩写，范围与结论未变

## 目标

修复 508 条 `note_reaction` 的来源定位：v1 资源构建按旧文件名格式找不到实际笔记文件而将其标为缺失；本任务在不改动旧原始 source 记录的前提下，建立旧文件名到新路径的映射，补复制实际笔记，并构建独立的 v2 派生数据。

## 背景

TASK-007 最终审计发现：508 条笔记反应的 source 文件名已由旧格式"YY-MM-DD 空格"（如 `26-06-15 黄酮化合物的结构.md`）迁移为"YYMMDD-"格式（如 `docs/literature/260615-黄酮化合物的结构.md`），v1 构建因此把这些来源标为缺失。

理由（原文要点）：用户要求逐项核实来源；不能把能定位的实际文件永久标缺失，也不能只靠名称声称反应原文核验。

## 范围

### 允许项

- 从只读历史目录补复制 9 篇 `docs/literature` 实际笔记到 `data/raw/legacy/docs/literature/`，登记 `role=source_note`、`review_status=project_input_not_primary_reviewed`（与 TASK-002 的 `historical_claims_only_not_revalidated` 不同：这 9 篇是项目输入笔记，而非历史声称）；
- 生成 `metadata/note-relocations.json`（9 条旧文件名 → 新路径映射）；
- 留档 `metadata/sources-v1.json`（TASK-002 的 114 条版）与 `operations/archive/resources-v1.py`（首版资源构建器）；
- 将 `flavoretro/resources.py` 改写为 v2：记录每条来源的文件定位结果、原反应 token 是否在文件中找到；
- 构建 `data/derived/v2` 并与 v1 重放对比。

### 禁止项

- 修改旧原始 source 记录或历史目录内容；
- 在两次重放一致之前切换活动数据指针；
- 把笔记文件的存在表述为反应原文已核验；
- 改变任何记录的计数字段。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| `data/raw/legacy/`：原始快照 | `docs/literature/` 下 9 篇笔记 | 补复制的项目输入笔记（只读） |
| `metadata/`：来源元数据 | `note-relocations.json` | 9 条旧名 → 新路径映射（新增） |
| `metadata/`：留档 | `sources-v1.json` | TASK-002 的 114 条来源清单原样留档 |
| `operations/archive/`：代码留档 | `resources-v1.py` | 首版资源构建器归档 |
| `flavoretro/`：核心包 | `resources.py` | 改写为 v2（来源定位与 token 命中记录） |
| `data/derived/`：派生数据 | `v2/` | 新构建版本，与 v1 并存不覆盖 |

## 非目标

- 不重新验证任何化学反应原文（笔记定位 ≠ 内容核验）；
- 不改变记录计数与化学载荷；
- 不切换 `data/derived` 活动指针（原设计为重放一致后切换，实际被所有者搁置）；
- 不删除 v1 派生数据与 v1 构建器。

## 必须执行的操作

1. 逐条核对 9 个旧文件名对应的实际新路径并补复制笔记文件。
2. 生成 `metadata/note-relocations.json` 映射。
3. 留档 v1 来源清单与 v1 构建器。
4. 改写 `resources.py` 为 v2，构建 `data/derived/v2`（command-0026，rc=0）。
5. 重放对比 v1/v2 的计数与哈希。
6. 重放一致后按合同设计切换活动数据指针（实际被所有者搁置，未执行）。

9 条映射（`metadata/note-relocations.json` 全量）：

- `26-06-15 黄酮化合物的结构.md` → `docs/literature/260615-黄酮化合物的结构.md`
- `26-06-18 黄酮化合物的生物合成.md` → `docs/literature/260618-黄酮化合物的生物合成.md`
- `26-06-21 黄酮化合物研究进展（1）：黄酮类化合物.md` → `docs/literature/260621-黄酮化合物研究进展（1）：黄酮类化合物.md`
- `26-06-21 黄酮类化合物立体化学.md` → `docs/literature/260621-黄酮类化合物立体化学.md`
- `26-06-24 黄酮化合物研究进展（2）：异黄酮类化合物.md` → `docs/literature/260624-黄酮化合物研究进展（2）：异黄酮类化合物.md`
- `26-06-25 黄酮化合物的性质.md` → `docs/literature/260625-黄酮化合物的性质.md`
- `26-06-26 黄酮化合物的合成.md` → `docs/literature/260626-黄酮化合物的合成.md`
- `26-06-26 黄酮化合物的波谱学特征和结构解析.md` → `docs/literature/260626-黄酮化合物的波谱学特征和结构解析.md`
- `26-06-27 黄酮化合物的生物活性.md` → `docs/literature/260627-黄酮化合物的生物活性.md`

## 验收标准

- [x] 9 条旧文件名全部定位到实际文件并补复制，`note-relocations.json` 与之一致。
- [x] v2 记录计数与 v1 完全一致：molecule 156、note_reaction 508、stock 49、scifinder_reaction 2301、paper 15、supplier 22、template 2。
- [x] v2 哈希独立留痕：`records_sha256=448dbbd…`、`sources_sha256=5cf9374…`、`code_sha256=21089846…`（v1 分别为 `e09c2906…`、`d7de679a…`、`6d38388…`）；计数不变、哈希变化来自来源定位元数据与构建器版本，记录载荷未再编辑。
- [x] v1 来源清单（114 条版）与 v1 构建器已留档，可溯源。
- [ ] 切换活动数据指针：原设计为"两次重放一致后切换，旧 v1 保留"；重放一致已达成，但切换被所有者搁置（STATE.md："v2 重放与来源定位映射保留未切换，TASK-007 补充被所有者搁置"）。runtime 固定 v1，不自动采用新版本；USER_GUIDE 说明重放命令拒绝覆盖旧版本。

## 验证

```bash
.venv/bin/python -B -m flavoretro.resources   # command-0026，rc=0，构建 data/derived/v2
# 重放对比 data/derived/v1/manifest.json 与 data/derived/v2/manifest.json 的 counts 与 *_sha256
```

## 停止条件

- 应定位的笔记文件缺失或哈希不符；
- v2 与 v1 计数不一致或重放不一致；
- 出现任何需要改动旧原始 source 的情况；
- 出现以上任一情况即停止并报告，不切换指针。

## 必须提交的报告

对应报告为 `docs/reports/REPORT-007-P1-source-relocation.md`（TASK-009 补立）；STATE.md 记录指针搁置状态。
