# scripts/ 索引与纪律

TASK-021盘点时本目录保留 523 个顶层 Python 脚本；其后新增入口另列下表。原引用台账列 524 个名字，其中两个不是当前顶层脚本；实际 522/523 被记录引用。唯一未记录引用的 task020_futurehealth_rebuild.py 因受控迁移工具职责与 REPORT-020 溯源保留。历史脚本按逐项台账 KEEP，不物理搬动/合并，不据编号或版本后缀自动选择执行。

常驻工具见下表；历史任务脚本只按各 TASK/REPORT 查阅。完整逐脚本用途、SHA、语法状态和保留原因见 [脚本分类表](../outputs/restructure/repo-consolidation-20261015/script-catalog.tsv)。TASK-021 起新增且未被钉定的一次性脚本直接放入 scripts/archive/。

两个历史 P7 脚本已有语法错误：task016_p7_progress_v9.py（65行）、task016_p7_ss_new_source_reconcile_v1.py（121行）。与历史保护 SHA 一致，原字节保留；完整 scripts/ compileall **未通过**，不得将档案脚本视为全部可执行。详见 [整理报告](../docs/reports/REPORT-021-repository-consolidation.md)。

## 常驻通用（多任务复用）

| 脚本 | 用途 |
| --- | --- |
| operate.py | 追加式操作账；所有写入/命令经此记录（CI 引用） |
| browser_check.py | 四页/历史/12-cell 浏览器验收 |
| package_check.py | 包外安装与真实搜索验证 |
| artifact_check.py | wheel/sdist 载荷边界检查（CI 引用） |
| smoke.py | 历史冒烟入口 |
| triage_reactions.py | TASK-014 离线筛选审计入口（不接 MCTS） |
| contrast_check.py | TASK-013 对比度与 token 守卫 |

## TASK-015 链（ORD 覆盖与审核卡）

fetch_ord / scan_ord / survey_ord_mirror / summarize_ord_coverage / setup_ord_schema（冻结镜像与扫描）；analyze_ord_review / assemble_agent_reviews / audit_ord_coverage / build_review_cards / check_review_cards（卡片与审核）；review_references / refine_review_references（来源导航）；build_task015_p3_handoff / check_task015_p3_handoff / task015_p3_gold_freeze / task015_p3_ingest（P3 交接与冻结）；ingest_scifinder_task015_p2 / check_scifinder_task015_p2（P2 RDF 接收）；task015_06_*（审核进搜索 4 件）；task015_p5_*（P5 收尾 6 件）。

## TASK-016 链（开放苷扩库与迁移方法）

task016_* 主任务 10 件；p1 15 件（task016_p1_sources.py 为脚本）；p2 20 件；p3 11 件；p4 9 件；p5 14 件；p6 12 件；**p7 394 件**（ss_* 124、c_* 85、G6_/rNN_ 探针与 *_harness/orchestrate/verify，2026-10-11—13 密集诊断期产物，历史保留）；p9 1 件。职责与验收见各 REPORT-016-P*。

## TASK-017 之后

| 脚本 | 用途 |
| --- | --- |
| task017_formal.py | TASK-017 freeze/check/run/verify 入口（被 tests/test_task017_formal.py 引用） |
| task020_futurehealth_rebuild.py | FutureHealth M0+P0 受控迁移工具（服务端运行，只写 /home/ljx/FutureHealth） |

逐脚本一句话用途与字节数：`outputs/restructure/repo-consolidation-20261015/staging/inventory.json`。

## TASK-022 全流程续作

| 脚本 | 用途 |
| --- | --- |
| task022_loop.py | 不可变批次冻结、先预留预算、逐cell完成/失败账与恢复检查点 |
| task022_build_literature.py | 冻结新版本的来源精确反应检索库；不覆盖已存在版本 |

本轮专用检索、审计和实验runner位于 `outputs/task022/` 独立子目录，按各冻结协议执行，不用新批次名绕过旧预算。

TASK-022当前已结项；最终验证与逐项完成审计位于outputs/task022/optimized_coverage_repair_20261021/strict_stock_v2，入口COMPLETED.md。所有旧批次保留，不因恢复指令重复运行已reserved cell；新任务先获批准。


## 前端项目入口（TASK047）

- frontend.py：纯标准库build/check/watch/routes/create-page，源与运行/包资产一致性检查；写入需活动--task。
- check_frontend.py：使用已有Playwright的只读浏览器回归，禁止非GET和新搜索，覆盖业务子页及组件参考。

编辑入口为web/src、web/styles及frontend/routes清单；详见[前端开发说明](../web/README.md)。不要直接编辑生成的app.js/style.css/index.html。
