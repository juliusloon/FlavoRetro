# TASK-009：治理文档详细化与人类可读交接

## 合同元数据

- 任务 ID：TASK-009
- 状态：Approved
- 基线分支：main
- 基线提交：b9a1359（docs: 许可分层确定）
- 人工负责人：项目所有者（ljx）
- 执行者：Kimi（Kimi Code CLI 会话）
- 修改预算：`docs/` 全部治理文档、`scripts/operate.py`、根级 `README.md`/`STATE.md`/`ARCHITECTURE.md`；不动 `flavoretro/` 包逻辑、`tests/`、`configs/`、`web/`、`data/`、`outputs/`
- 批准：Kimi agent_delegated（2026-09-21）；依据：用户在本会话的直接指令（"参照 ~/CondRxnBench 中各文件的 README.md，按照这一详细格式对各文件进行详细化，明确各次 Task 的边界和产出……人类工作员不查看原项目而能完整地同步到目前的所有进展"）

## 目标

把 `docs/tasks/`、`docs/reports/`、`docs/adr/` 全部文件从速记体重写为 CondRxnBench 详细合同/报告格式；补齐缺失的 REPORT-005、REPORT-007 及补充任务的配套报告；新增模板与目录 README。完成判定：每个 TASK 有同编号 REPORT；每份文件具备模板规定的全部小节；`docs/README.md` 导航无死链；全部单元测试通过。

## 背景

- TASK-001—008 由 agent 于 2026-09-21 一天内自主完成，文档为速记体：每份 TASK 仅数行列项，缺合同元数据（基线提交、执行者、修改预算）、缺"必须执行的操作""验证命令"分节；REPORT-005、REPORT-007 未独立成文（旧导航写"REPORT-004 末节 + 运行输出""见 REPORT-008 汇总"），不满足"每个 TASK 必有同编号 REPORT"的规则。
- 存在编号冲突：`docs/tasks/` 下有两个 TASK-007（`TASK-007-handoff.md` 与 `TASK-007-amendment-source-relocation.md`）。
- 大量事实只存在于 `operations/events.jsonl` 与 `operations/command-*.log`；其中 `command-*.log` 与 `operations/*.json` 被 `.gitignore` 排除、不入 Git。报告若不自含关键事实，仓库发布后无法复核。
- 用户要求：人类工作员不查看 `/home/ljx/retro_synthesis` 即可同步所有进展并直接继续开发；与当前方向无关的旧实验脚本、结果、海报等不需保留。

## 范围

### 允许项

- `docs/tasks/`、`docs/reports/`、`docs/adr/` 下文件的重写与新增（TEMPLATE、README、各 TASK/REPORT/ADR）。
- `docs/README.md`、`docs/HUMAN_TAKEOVER.md`、`STATE.md`、`ARCHITECTURE.md`、`README.md` 的一致性更新。
- `scripts/operate.py` 增加 `--write/--from` 子命令，使文档写入可经治理日志记录前后哈希。
- 重命名 `TASK-007-amendment-source-relocation.md` → `TASK-007-P1-source-relocation.md`（`git mv` 保留历史）。
- `operations/.staging-task009/` 暂存区的创建与清理。

### 禁止项

- `flavoretro/` 包逻辑、`tests/`、`configs/`、`web/`、`data/`、`outputs/` 的任何改动。
- 切换 `data/derived` 活动指针（TASK-007-P1 维持所有者搁置状态）。
- 对 `/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench` 的任何写入。
- 把本任务开始前工作区已存在的 27 个文件空白格式化改动混入本次提交。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| docs/tasks（事前合同） | TEMPLATE.md、README.md | 新增：合同模板与目录规则/术语 |
| docs/tasks | TASK-001…008、TASK-007-P1、TASK-009 | 速记体重写为详细合同；007-amendment 重命名为 007-P1 |
| docs/reports（事后事实） | TEMPLATE.md、README.md | 新增：报告模板与目录规则 |
| docs/reports | REPORT-001…008、REPORT-007-P1 | 重写为详细报告；REPORT-005、REPORT-007、REPORT-007-P1 为补立 |
| docs/adr（长期决定） | 0000-template.md、README.md、ADR-001…003 | 新增模板与 README；三份 ADR 扩写背景/备选/复审条件 |
| scripts（活动工具） | operate.py | 增加 `--write/--from` 子命令（已完成，见 events.jsonl） |
| 根级 | STATE.md、ARCHITECTURE.md、README.md | 更新至本任务完成后的事实 |
| docs/ | README.md、HUMAN_TAKEOVER.md | 导航补新文件、读序微调 |
| operations/（治理日志） | .staging-task009/ | 暂存区；落盘登记后删除 |

## 非目标

- 不补充任何化学验证、不晋级任何候选记录、不重跑搜索基准。
- 不改变 TASK-001—008 的事实结论；只提升表述详尽度与结构。
- 不处理工作区已存在的 27 个文件空白格式化改动（留待所有者决定，记入 REPORT-009）。
- 不推送远程、不创建 GitHub 仓库、不替换 repo-local git 身份。

## 必须执行的操作

1. 扩展 `operate.py`（`--write/--from`），变更记入 `operations/events.jsonl`。
2. `git mv` 消除 TASK-007 编号冲突。
3. 按 CondRxnBench 模板新增 6 个格式文件（tasks/reports/adr 的 TEMPLATE 与 README）。
4. 重写 9 份 TASK、9 份 REPORT（含补立 REPORT-005、REPORT-007、REPORT-007-P1）、3 份 ADR；全部经 `operate.py --write` 记录前后哈希。
5. 更新 `docs/README.md` 导航、`STATE.md`、`ARCHITECTURE.md`。
6. 链接与一致性检查；全部单元测试。
7. 写 REPORT-009，更新 STATE，Git 提交。

## 验收标准

- [ ] 每个 TASK-NNN 有同编号 REPORT-NNN（含 TASK-007-P1）。
- [ ] 每份 TASK 含：合同元数据、目标、背景、范围（允许项/禁止项/文件职责表）、非目标、必须执行的操作、验收标准、验证、停止条件。
- [ ] 每份 REPORT 含：对应任务、改动文件表、实际改动、验证表、与任务合同的偏差、已发现但未修改的问题、遗留风险、仓库与 CI 状态、建议的下一任务。
- [ ] 每份 ADR 含：状态、日期、负责人、背景、决定、备选方案、影响与风险、复审条件。
- [ ] `docs/README.md` 及被改文档中所有相对链接可解析到存在的文件。
- [ ] `.venv/bin/python -B -m unittest discover -s tests` 通过。
- [ ] 所有写入在 `operations/events.jsonl` 可查（含前后 SHA-256）。

## 验证

```bash
.venv/bin/python -B -m unittest discover -s tests -v
# 链接检查：提取改动 md 中的相对链接逐一 test -f
# 一致性：grep 确认无 TASK-007-amendment 残留引用；TASK/REPORT 编号一一对应
```

## 停止条件

- 某事实在 events.jsonl、命令日志与仓库文件中均无法核实：标注"未记录"并继续，禁止编造。
- 单元测试失败：先诊断；若与本次文档改动无关，记录并报告，不借机修无关代码。
- 发现必须改动 `flavoretro/` 逻辑才能自洽：停止并报告，由所有者另批任务。

## 必须提交的报告

完成、部分完成或失败时，生成 `docs/reports/REPORT-009-docs-detailing.md` 并更新 `STATE.md`。
