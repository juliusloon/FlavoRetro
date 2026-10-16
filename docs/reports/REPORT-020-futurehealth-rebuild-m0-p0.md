# REPORT-020：FutureHealth 新项目重建（M0 基线冻结 + P0 受控迁移）

- 任务：[TASK-020](../tasks/TASK-020-futurehealth-rebuild.md)
- 执行：Cano（AutoClaw）；批准与阶段裁定 **agent_delegated**，human_reviewed=false
- 日期：2026-10-15
- 结论：**M0+P0 阶段 Completed**；M1—M5 未执行（需新 TASK 批准）；教师审定 0、教学真值 0、公开发布 0

## 1. 交付物

### 新仓库（本轮新建，与 FlavoRetro 同级）

`/home/ljx/FutureHealth`（本地挂载视图 `/Volumes/cano/FutureHealth`），Git main 两个提交：

- `ca586b3`：首提交，42 个跟踪文件（骨架、许可、登记表、migrations 凭据、P0 参考副本）
- `c05767e`：verify-post 审计凭据 `migrations/verification-final.json`（首提交后工作树 0 脏项）

| 内容 | 数量与验证 |
| --- | --- |
| `reference/flavoretro-snapshot/` P0 受控副本 | 23 个 CORE_REUSE 文件，保持原相对路径；LICENSE 双目标（副本 + 新仓库顶层）；逐文件 SHA256 与预迁移包 VERIFIED_PRIORITY_HASHES.csv 一致，并经独立脚本重算复核 **23/23 通过** |
| `migrations/mapping.csv` | 24 行（23 源，LICENSE 双目标），含 sha256/size/license_gate/git_tracked 列 |
| `migrations/p1_pending_review.csv` | 49 行 SELECTIVE_REVIEW，全部 copied=false、review_gate=teacher_or_owner_review_required_before_copy；内容零复制（脚本断言 p1_leaks=[] + 独立核查通过） |
| `migrations/flavoretro-baseline.json` | M0 基线：旧库 HEAD 993b22f5、远端真差异 630 条与 porcelain SHA、预迁移包 14 文件 SHA |
| `data/registries/source_registry.csv` | 123 源，SHA d1e17015…，与包内 SOURCE_INTAKE_123.csv **逐字节一致**（byte_equal_to_package=True） |
| `data/registries/case_admission.csv` | 22 行 = 1 案例头（isoquercitrin，molecule id 151fb43d…，identity_status=explicit_identity_resolution_pending_human_review）+ 21 条产物结构命中反应（FH-R-001…021，字段逐列承自 EXACT_TARGET_PRODUCT_REACTIONS.csv）；**全部 admission_status=pending_teacher_review、human_review_status=not_performed** |
| 骨架 | 蓝图 §5 全部 16 个目录存在；Git 跟踪空目录 .gitkeep 14 处（data/private/ 不入 Git 故无 .gitkeep）；AppleDouble 旁车 0 |
| 治理文档 | README.md（三套状态门/目录/Git 边界/许可/下一步）、LICENSES/README.md、docs/decision/ADR-0001、.gitignore（data/private/ 与参考副本 data/metadata 层强制排除） |

### FlavoRetro 侧（协作记录，全部经 scripts/operate.py 写入）

- `docs/tasks/TASK-020-futurehealth-rebuild.md`（合同，含批准记录）
- `docs/reports/REPORT-020-futurehealth-rebuild-m0-p0.md`（本文）
- `docs/adr/ADR-008-futurehealth-project-split.md`（项目拆分长期决定）
- `scripts/task020_futurehealth_rebuild.py`（迁移/验证工具，服务端运行、仅写 FutureHealth）
- `STATE.md`（状态段更新）、`operations/events.jsonl`（TASK-020 事件 50+ 条，每次经 operate.py 的写入/命令各追加，含本报告自身的修订）

## 2. 验收标准逐项结果

| 项 | 结果 | 证据 |
| --- | --- | --- |
| A1 骨架与蓝图一致 | ✅ | 16/16 目录存在（远端逐目录 test -d） |
| A2 P0 逐字节一致 | ✅ | build 内置校验 + 独立重算 23/23 无 mismatch；mapping 24 行 |
| A3 P1 零复制 | ✅ | 49 行登记、copied=false；p1_leaks=[]；新仓库内无对应内容文件 |
| A4 登记表保真与待审 | ✅ | source_registry 字节一致；case_admission 22 行全 pending；全库通过类标记（human_reviewed=true/teacher_approved/教师已审通过）检索 **0 命中** |
| A5 Git 审计 | ✅ | 42 跟踪文件中禁止路径（data/private/、snapshot/{data,metadata}/）0 个；verification-final.json 9 项检查全过 |
| A6 旧库完整性 | ✅ | HEAD 993b22f5 不变；过滤本轮预算文件后 porcelain SHA = 任务起点基线 bbfb641b…（逐位一致）；retro_synthesis/CondRxnBench 零命令触碰 |
| A7 全程记账 | ✅（口径披露见 §3.6） | operations/events.jsonl TASK-020 事件 50+ 条；全部项目写入与状态变更命令均经 scripts/operate.py 记录 |
| A8 文档落盘 | ✅ | 合同/报告/STATE/ADR-008/ADR-0001 全部落盘 |

## 3. 执行过程与如实记录的问题

1. **挂载卷 Write 工具失效（×2）**：`temp/task020-staging/` 下写入 rename EINVAL，无半成品残留（已现场确认空目录）。改为「/tmp 暂存 → operate.py --write（FlavoRetro 侧）/ ssh stdin 管道（FutureHealth 侧）」，全程 SHA 校验。
2. **挂载写入延迟拦截（×2）**：脚本经 mount 更新后远端 SHA 与本地不一致，同步门（sleep 后重比）拦截，未执行过旧版本脚本；等待同步后放行。
3. **build 第 1 次失败**：预迁移包 4 个 CSV 均带 UTF-8 BOM（efbbbf），`csv.DictReader` 首列名带 BOM 致 KeyError。修复：全部 CSV 读取改 `utf-8-sig`（SOURCE_INTAKE 字节复制不受影响，副本与原件仍逐字节一致）。
4. **build 第 2 次失败**：`p1_all_pending` 误从 HIGH 源行取不存在的 status 列（脚本校验 bug）。修复：改用写入行校验；预检改为「仅允许 TASK-020 已知产物存在时幂等续跑」，未删除任何文件，全部产物由源确定性再生。
5. **LICENSES/ 目录缺失**：脚本只为快照侧创建 LICENSES/ 目录，顶层 LICENSES 安装时目录不存在，链式中止（README 已装、其余未装，无错误状态）。补建目录重装，4 份文档 SHA 逐一比对一致。
6. **记账口径披露**：所有项目写入（docs/scripts/STATE 与 FutureHealth 全部内容）和全部状态变更命令均经 `scripts/operate.py` 记录（events.jsonl TASK-020 事件 50+ 条 + 对应 command-*.log）；少量**只读**探查（本地/远端 SHA 比对、`git diff --numstat` 统计、验证凭据读取）未逐条记账，结果均可在 command 日志与本报告数字中复核。

三次 build 失败均发生在 verification 写出之前或中断于登记表之前，最终 build 一次通过（ok=true），不存在错误数据残留。

## 4. 既有状态标注（非本轮改动）

- FlavoRetro 工作区在任务起点即有大量未提交内容：**远端真差异口径** 628 条（打包时）→ 630 条（本轮 +2 预算文件）；**本地挂载口径** 764 → 766。差值均为本轮 2 个预算内新文件（`docs/tasks/TASK-020…`、`scripts/task020…`）。
- `git diff --numstat` 显示 25 个文件有真实内容差异、136 个文件为纯 mode/stat 噪声（`core.filemode=true` + SMB 挂载），**全部先于本 TASK 存在**（过滤哈希与起点逐位一致为证）；`operations/events.jsonl` 对 HEAD 的 39,558 行追加中基线继承 39,506 行，本轮为 TASK-020 的记账行（50+，含报告修订）。
- 旧库未提交工作区按 M0 原样保全；未执行 git clean/reset/commit/force push；未 Git 同步（与近期 TASK 一致，待所有者决定）。

## 5. 边界声明（未做的事，如实为零）

- M1（目标分子/21 条反应结构复核与论文条件登记）、M2（教师审定案例包）、M3（教学最小可用）、M4（服务拆分）、M5（教学/发布门）：**未执行**，需新 TASK 批准。
- 教师审定 **0** 项；独立化学验证 **0**；教学真值/gold **0**；case_admission 21 条反应记录仍为 agent_checked_candidate、STRUCTURE_MATCH_ONLY_NOT_INDEPENDENT_VALIDATION。
- 预迁移包本身未做任何修改；`data/raw/` 原件、outputs/ 评审卡、tests/、旧 TASK/REPORT、日志零复制。
- FlavoRetro 科学状态（TASK-017 准备就绪、C/SS 迁移 null、formal/release 门）未触碰；无 MCTS、无网络检索、无模型改动。

## 6. 三套状态门（重申）

| 门 | 状态 |
| --- | --- |
| research_evaluation | 旧库承载，本轮零改动 |
| teaching_case_review | 全部 pending_teacher_review（22/22），0 通过 |
| public_teaching_release | 未启动 |

候选、数据库身份、图回放、工程测试、供应证据、独立化学验证六类证据在本仓库均未产生、未混同。
