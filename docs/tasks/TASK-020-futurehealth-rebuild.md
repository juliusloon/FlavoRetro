# TASK-020：FutureHealth 新项目重建（M0 基线冻结 + P0 受控迁移）

## 合同元数据

- 任务 ID：TASK-020
- 状态：Approved（agent_delegated）
- 基线分支：main（FlavoRetro）
- 基线提交：993b22f5e8eed5797d27f02c566af1b86a4b7880；工作区未提交条目 764（2026-10-15 现场），按 M0 原样保全，不清理、不重置
- 人工负责人：所有者（本 TASK 审批由 Cano 代行，见批准字段）
- 执行者：Cano（AutoClaw）
- 修改预算：
  - FlavoRetro 内：`docs/tasks/TASK-020-futurehealth-rebuild.md`、`docs/reports/REPORT-020-futurehealth-rebuild-m0-p0.md`、`docs/adr/ADR-008-futurehealth-project-split.md`、`STATE.md`、`scripts/task020_futurehealth_rebuild.py`、`operations/`（events.jsonl 追加与 command 日志）、`temp/task020-staging/`（过程暂存，Git 已忽略）
  - 新建：`/home/ljx/FutureHealth` 整个目录（与 FlavoRetro 同级；本地挂载视图 `/Volumes/cano/FutureHealth`）
- 批准：Cano 代行批准（agent_delegated），2026-10-15；授权依据 = 所有者在协作规范中授予的自主审批权（AGENTS.md「本次用户授予 Cano 自主审批权」）；human_reviewed=false；授权范围仅覆盖本 TASK 的 M0+P0 阶段。

## 目标

1. 按 `outputs/restructure/future-health-20261015/REBUILD_EXECUTION_LIST.md` 的 M0 与 §2，在 `/home/ljx/FutureHealth` 建立新项目：蓝图骨架（§5）+ M0 基线登记 + P0（23 个 CORE_REUSE 文件）受控参考副本，逐文件 SHA256 可验证。
2. P1（49 个 SELECTIVE_REVIEW 项）只登记待审清单（migrations/p1_pending_review.csv），不复制任何内容到新项目。
3. 建立登记表：`data/registries/source_registry.csv`（123 源，与 SOURCE_INTAKE_123.csv 字节一致）与 `data/registries/case_admission.csv`（1 案例头 + 21 条产物结构命中反应），全部 admission_status=pending_teacher_review。
4. 新项目 Git 初始化并完成首个提交；原始/受限数据与 v3 数据副本不入 Git。
5. FlavoRetro 侧 TASK/REPORT/STATE/ADR 按协作规范落盘，全部写入与命令经 `scripts/operate.py` 记录。

## 背景

- 预迁移包 `outputs/restructure/future-health-20261015` 已完成：65,702 文件清点（约 14.81 GB）、处置分类（CORE_REUSE 23 / SELECTIVE_REVIEW 3,201 / REFERENCE_ONLY 9,287 / EXCLUDE 53,191）、72 行优先清单（SHA 全部现场核验，VERIFIED_PRIORITY_HASHES.csv）、123 源登记（SOURCE_INTAKE_123.csv）、异槲皮苷 21 条产物结构命中（EXACT_TARGET_PRODUCT_REACTIONS.csv，均 agent_checked_candidate、独立审核 0）。
- 重建要求（REBUILD_EXECUTION_LIST §0/§5/§6）：旧目录是保留的科研事实源，所有迁移在新目录的受控副本中发生；M0 即刻冻结；P0 能力先保留但「逻辑与适用范围需要新合同」；P1 需人工/专业审查后选入；M2 起需教师审定；未达条件不得以虚拟数据替代。
- 远端 `/home/ljx/FutureHealth` 当前不存在（2026-10-15 现场确认 FREE），磁盘可用约 192 GB。
- 所有者指定：重建项目与 FlavoRetro 同级（`/home/ljx/` 下），名称自拟 → 定名 **FutureHealth**（与蓝图 §5 一致）。
- 环境纪律：本地挂载卷写入对服务端有延迟且会产生 `._*` 旁车；本 TASK 的新内容写入全部经服务端执行或先做 SHA 同步校验。

## 范围

### 允许项

- 新建 `/home/ljx/FutureHealth` 全部内容：骨架目录、README.md、LICENSES/README.md、docs/decision/ADR-0001、.gitignore、data/registries/ 两表、migrations/ 五件（mapping.csv、p1_pending_review.csv、flavoretro-baseline.json、verification-m0p0.json、verification-final.json）、reference/flavoretro-snapshot/ 下 23 个 P0 文件副本、空目录 .gitkeep。
- FlavoRetro 侧合同/报告/STATE/ADR/迁移脚本（如预算所列）。
- 对 FlavoRetro 只读访问（复制源文件、读预迁移包）；对 FutureHealth 的服务端命令执行。

### 禁止项

- 修改/删除 FlavoRetro 任何既有跟踪文件（STATE.md 与 operations/events.jsonl 的协作框架追加属预算内）；不执行 git clean/reset/force push；不清理 764 条未提交条目。
- 复制 P1 内容文件、data/raw/ 原件、outputs/ 评审卡、tests/、旧 TASK/REPORT、日志等到新项目。
- 触碰 `/home/ljx/retro_synthesis` 与 `/home/ljx/CondRxnBench`（历史只读）。
- 生成任何教学真值/gold；写入任何教师审核/人审通过标记；把 agent 记录写成 human_reviewed。
- 新项目内容进入公网或公开发布。
- 在 FlavoRetro 目录内运行可能写缓存的代码（迁移脚本在服务端以绝对路径运行，仅写 FutureHealth）。

### 涉及目录与文件职责

| 目录及职责 | 文件 | 用途与拟改动 |
| --- | --- | --- |
| /home/ljx/FutureHealth（新建） | 全部 | 教学重建仓库，本阶段仅骨架+受控副本+登记，无业务代码 |
| FutureHealth/reference/flavoretro-snapshot/ | 23 个 P0 文件（保持原相对路径） | 冻结参考副本；非新运行时，复用需新合同 |
| FutureHealth/data/registries/ | source_registry.csv、case_admission.csv | 源登记（字节保真）；案例准入（全部待教师审） |
| FutureHealth/migrations/ | mapping.csv、p1_pending_review.csv、flavoretro-baseline.json、verification-m0p0.json、verification-final.json | 哈希映射、待审清单、M0 基线、验证凭据 |
| FutureHealth/data/private/ | （空） | 未来按许可存放原始/审核后数据；Git 禁止 |
| FutureHealth/docs/curriculum|cases|policy、src/futurehealth/ 五子包、frontend/ 两端、tests/ | .gitkeep | 蓝图占位，业务文件本轮不建 |
| FlavoRetro docs/、scripts/ | TASK-020、REPORT-020、ADR-008、task020_futurehealth_rebuild.py、STATE.md | 协作记录与迁移工具（计划新增；STATE 为既有文件追加状态段） |

## 非目标

- M1（目标分子/21 条反应逐条结构复核与论文/条件登记）、M2（教师审定案例包）、M3（教学最小可用）、M4（服务拆分）、M5（教学/发布门）均不在本轮。
- 不编写 FutureHealth 业务代码、课程内容、前端；不迁移旧搜索为服务；不建 iLab 适配。
- 不回答任何 C/糖间独立迁移科学问题；不改变 FlavoRetro 既有科学状态（formal/release 门保持）。
- 不对预迁移包本身做任何修改（它是本轮的输入与 M0 证据）。

## 必须执行的操作

1. 写入本合同并登记批准（agent_delegated）。
2. `scripts/task020_futurehealth_rebuild.py` 写入 FlavoRetro（经 operate.py），ssh 校验同步后于服务端执行 `--phase build`：骨架、P0 复制+SHA 验证、migrations 五件、登记表两份。
3. 暂存 README/LICENSES/ADR-0001/.gitignore，服务端 SHA 校验后经 ssh 管道写入 FutureHealth。
4. FutureHealth `git init` + 首提交（仓库本地身份 Cano，仅含 .gitignore 允许清单内文件）。
5. 服务端执行 `--phase verify-post`：对已提交树做禁止路径与标记审计，写 verification-final.json（含首提交 SHA）并二次提交。
6. FlavoRetro 完整性核查：HEAD 不变；跟踪文件改动仅限预算路径；retro_synthesis/CondRxnBench 未触碰。
7. REPORT-020 + STATE.md 更新 + ADR-008。

## 验收标准

- [ ] A1 骨架与蓝图 §5 一致（全部目录存在）。
- [ ] A2 23 个 P0 文件逐字节存在于 reference/flavoretro-snapshot/，SHA256 与 VERIFIED_PRIORITY_HASHES.csv 的 current_sha256 全部相等；migrations/mapping.csv 逐行对应（LICENSE 双目标共 24 行）。
- [ ] A3 migrations/p1_pending_review.csv 恰 49 行且全部 copied=false；全库检索证明 49 项内容未复制入新项目。
- [ ] A4 source_registry.csv 与 SOURCE_INTAKE_123.csv SHA 一致；case_admission.csv 恰 22 数据行、全部 pending_teacher_review；新项目内检索不到「human_reviewed=true」「教师已审通过」类标记。
- [ ] A5 `git -C /home/ljx/FutureHealth ls-files` 审计：不含 data/private/、不含 reference/flavoretro-snapshot/data|metadata/ 路径；verification-final.json 全部检查通过。
- [ ] A6 FlavoRetro HEAD 仍为 993b22f5…；跟踪文件改动仅 STATE.md 与 operations/events.jsonl，新增未跟踪仅预算路径；retro_synthesis/CondRxnBench 无任何写入。
- [ ] A7 每步写入/命令在 operations/events.jsonl 或 operations/command-*.log 有对应记录。
- [ ] A8 REPORT-020、STATE.md 更新、ADR-008、FutureHealth/docs/decision/ADR-0001 全部落盘。

## 停止条件

- P0 任一文件现场 SHA256 与 VERIFIED_PRIORITY_HASHES.csv 不符：停止该文件迁移、登记 mismatch、报告等待处置，不猜测替换。
- `/home/ljx/FutureHealth` 已存在非空内容，或磁盘/权限不足：停止。
- 蓝图与现实冲突（P0 源文件缺失、路径无法创建等）：停止并报告，不自行替代。
- FlavoRetro 跟踪文件出现预算外改动：立即停止并报告。
- 服务端执行连续 2 次失败无进展：停止并如实报告现状与已落盘部分。

## 必须提交的报告

完成、部分完成或失败时，均生成 `docs/reports/REPORT-020-futurehealth-rebuild-m0-p0.md` 并更新 `STATE.md`。
