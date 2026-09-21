# REPORT-009：治理文档详细化与人类可读交接

## 对应任务

- 任务 ID：TASK-009
- 任务文件：[docs/tasks/TASK-009-docs-detailing.md](../tasks/TASK-009-docs-detailing.md)
- 状态：Completed（完成）
- 基线：main @ b9a1359
- 结果提交：见"仓库与 CI 状态"节（两个新提交）
- 批准：Kimi（agent_delegated，2026-09-21，用户本会话直接指令）
- 执行时段：2026-09-21（events.jsonl 中 TASK-009 事件自 06:28 UTC 起）

## 改动文件

生成但不进入 Git 的文件：`operations/.staging-task009/`（撰写暂存区，落盘登记后删除）；`operations/command-0033.log`（测试日志，`.gitignore` 排除）。

| 所在目录及职责 | 文件 | 实际改动与文件用途 |
| --- | --- | --- |
| `docs/tasks/` 事前合同 | `TEMPLATE.md`、`README.md` | 新增。合同模板与目录规则（编号/状态/agent_delegated 批准规则/术语表），格式取自 CondRxnBench 并适配本仓库 |
| `docs/tasks/` | `TASK-001`…`TASK-008`（8 份） | 速记体扩写为详细合同（合同元数据/背景/范围表/操作/验收/验证/停止条件），事实与结论未变 |
| `docs/tasks/` | `TASK-007-amendment-source-relocation.md` → `TASK-007-P1-source-relocation.md` | `git mv` 更名消除双 TASK-007 编号冲突并扩写；状态如实记 Partial |
| `docs/tasks/` | `TASK-009-docs-detailing.md` | 新增，本任务合同 |
| `docs/reports/` 事后报告 | `TEMPLATE.md`、`README.md` | 新增。报告模板与目录规则（含补立约定与本机日志说明） |
| `docs/reports/` | `REPORT-001`…`REPORT-004`、`REPORT-006`、`REPORT-008`（6 份） | 速记体扩写/转模板结构；REPORT-003 的计数 JSON 原样保留 |
| `docs/reports/` | `REPORT-005-workbench-evaluation.md`、`REPORT-007-handoff.md`、`REPORT-007-P1-source-relocation.md` | 补立（当时未单独成文）；事实来源 events.jsonl 与 command-0010…0026.log；007-P1 记 Partial |
| `docs/adr/` 长期决定 | `0000-template.md`、`README.md` | 新增。ADR 模板与建制规则 |
| `docs/adr/` | `ADR-001`、`ADR-002`、`ADR-003` | 扩写背景（内联旧项目实证）/备选方案/影响与风险/复审条件；决定内容未变 |
| `docs/` | `README.md`、`HUMAN_TAKEOVER.md` | 导航补全（模板、README、补立报告、007-P1、009）；接管指南更新治理流引用与归档脚本正名 |
| 根级 | `STATE.md`、`ARCHITECTURE.md` | 更新至本任务完成后事实；登记表补 data/derived、USER_GUIDE 等行 |
| `scripts/` | `operate.py` | 新增 `--write/--from` 子命令：文件写入经治理日志记录前后 SHA-256 |
| `operations/archive/` | `README.md` | 修正用法示例中的文件名（`history_guard.py` → 实际的 `history_guard-task-001.py`） |

## 实际改动

1. 治理文档从速记体（每份数行）扩写为 CondRxnBench 详细格式：10 份 TASK 与 10 份 REPORT 编号一一对应，ADR 补全模板小节；读者无需访问 `/home/ljx/retro_synthesis` 即可同步全部进展（旧项目事实已内联进各背景节）。
2. 补立三份缺失报告：REPORT-005（工作台与 12 cell 开发对照）、REPORT-007（最终验收）、REPORT-007-P1（来源定位 v2，Partial——指针切换被所有者搁置）。
3. 起草方式：8 个文档子代理并行起草至 `operations/.staging-task009/`，主控对照 events.jsonl、command 日志与 git 历史抽查并修正后，统一经 `operate.py --write` 登记落盘；全部写入的前后 SHA-256 在 `operations/events.jsonl` 可查（TASK-009 名下）。
4. 主控修正记录：报告元数据中的提交归属经 `git log` 核实为 aa012ca（docs 与治理）/ 1f027a8（代码与测试）/ 2b305a4（脚本、metadata、environment、operations）；旧库"29,698 个文件"在本仓库不可复核，已标注来源为旧库磁盘盘点；TASK-004 中 ADR-002 职责误述（"标准库 HTTP 服务决定"）已修正为证据分级决定。
5. TASK-001—008 的文本均在文件内注明"TASK-009 由速记体扩写，范围与结论未变"；原始速记体可从 git 提交 aa012ca 查回。

## 验证

| 命令或检查项 | 结果 |
| --- | --- |
| 全部 md 相对链接解析（自写脚本，逐链接 test 存在） | 通过：唯一缺失项为本报告落盘前的自引用，落盘后 0 缺失 |
| `grep -rn "TASK-007-amendment"` 残留检查 | 仅剩 3 处合法引用（更名说明本身） |
| TASK/REPORT 编号配对检查 | 10 TASK ↔ 10 REPORT，同编号同短标题 |
| `.venv/bin/python -B -m unittest discover -s tests -v`（command-0033，本机日志不入 Git） | rc=0：25 tests OK，4.476s |
| 遗留工作区改动语义核验（AST 逐文件比对 16 个 Python 文件；去空白文本比对 web/×3 与 PROJECT.md） | 除本任务改动的 `operate.py` 外全部 AST/TEXT 一致；`README.md` 另有 2 处文字删改（见下节） |

## 与任务合同的偏差

- 合同"验收标准"中导航无死链一项，在本报告（被导航引用的最后一篇）落盘后才完全满足；无其他偏差。
- 起草采用子代理并行，合同未限定执行方式；全部内容由主控抽查、修正并统一登记。

## 已发现但未修改的问题

1. 21 个文件存在本任务开始前（约 13:53—13:58 本机时间，未经 operate.py 记录）遗留的格式化改动：16 个 Python 文件 AST 与 HEAD 完全一致（引号/换行风格变化），`web/`×3 与 `PROJECT.md` 去空白文本一致，`README.md` 另有 2 处文字删改（删去"独立重建于 2026-09-21；"与"（同 CondRxnBench）"）。以上均未提交，留所有者决定提交或还原。
2. `scripts/operate.py` 的提交一并包含上述遗留格式化（该文件本任务有实质改动，无法在同文件内拆分）。
3. 三处历史粒度缺口已如实标注"未记录"：REPORT-007-P1 的 v2 单独重放事件与 command-0026 的 RDKit 告警逐条核对、REPORT-006 的 logging 关键字冲突位置。

## 遗留风险

- 扩写后的历史合同/报告非原始文本；虽经事实核验，细节仍以 `operations/events.jsonl` 与 git 历史为最终事实源。
- `operations/command-*.log`、`operations/history-before.json` 等本机证据不入 Git；报告已内联关键输出，完整日志仅在本机。
- 本次为文档任务：系统科学状态无任何变化（`metadata/release.json` 六维仍未关闭，`data/`、`outputs/`、`flavoretro/` 逻辑未触碰，TASK-007-P1 指针维持搁置）。

## 仓库与 CI 状态

本任务产生两个新提交：`feat: operate.py 增加 --write/--from 受记录写入子命令` 与 `docs: TASK-009 治理文档详细化与缺失报告补立`；提交身份仍为 repo-local 占位（ljx@flavoretro.local）。无远端、无 CI。上述 21 个文件的遗留格式化改动未包含在提交中。

## 建议的下一任务

由所有者决定，不自动开始：P0 证据整理（含 TASK-007-P1 指针切换与否的处置，见 [PAPER_ROADMAP.md](../PAPER_ROADMAP.md)）；遗留格式化改动的提交或还原；GitHub 远程建立与 git 身份替换。
