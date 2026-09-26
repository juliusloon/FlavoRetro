# 当前状态

TASK-001—011 的工程交付与历史报告保留。TASK-012 已由所有者于 2026-09-26 明确批准全部 G1—G5（“同意，开始执行”，human_direct 工程授权）；当前 G1—G4 通过，G5 提交/私有同步与远端 CI 验收中，尚未宣告五项全部完成。

活动资源：metadata/active.json → data/derived/v3。v3/replay-v3 的 records/manifest 逐字节一致，3,059 条记录与 v2 完全相同；v1/replay-v1/v2 原样保留。SQLite 为 v3 的只读派生索引，保留 123 条来源和全部记录；定位状态为 249 条 note_located_token_found、259 条 note_located_token_unmatched。文件定位/token 命中不是内容审核，0 production、3 条名称冲突仍保留。

运行与安装：.venv-foundation 使用独立托管 CPython 3.10.20，system-site-packages=false；依赖锁 environment/requirements-linux-py310.lock 不含本机 file:// 引用。wheel/sdist 包含默认配置和前端，仓库外安装已验证 CLI/Web/拓扑/缺资产诊断和 v3 实时 MCTS。原 .venv 与历史环境快照保留，日常使用新环境。仅验证 Linux x86_64/Python 3.10。

算法：实时 optimized/native MCTS 共享服务，每次新进程、新 run ID；修复同次扩展重复状态与过滤后原多产物 index 错配；PUCT/去重/替代动作/转置/节点预算合同通过。native 不共享 optimized 节点上限，不能声称等价预算或优越性。糖苷拓扑仍只作独立诊断与展示，未进扩展/评分。

前端：四页已有能力入口覆盖完整，包括全部搜索参数、评分/证据/版本/清单导出、9 类资源及 QC/收率/来源筛选、历史运行显式读取、27 个教学条目、15 文献卡及课程、12-cell 开发对照启动/进度/历史/结果与只读 preflight。47,836 条模型模板全为 0.0 Unrecognized，界面明确无法确定家族；文献联查仍为工程关键词匹配。未完成外进程 job 记录不冒充当前运行，不自动恢复。

验收：51 项本地全量测试通过；无资产 CI 模拟 45 项通过、6 项明确跳过。Chromium 在 1440×1000 与 390×844 核四页、参数、历史、导出、12-cell（0 失败）、429/400 与 UI 失败 fixture；JS 错误 0、四页移动无横向溢出。证据见 REPORT-012、outputs/validation/task012-g1…g4.json、task012-portable-v2.json、browser-714dac2a、package-66d62d36。CI 跳过、图回放、工程验收均不构成独立化学证据。

科学准入：research_candidate，primary source/current vendor unresolved、independent labels unavailable、formal benchmark not_executed，formal_run_ready/release_ready=false。教学标签、独立审核、正式盲测、P2 糖苷感知搜索、P4 交互及公开发布仍需新 TASK 与所有者批准，不自动开始。

工作区与 Git：现有私有 origin 为 juliusloon/FlavoRetro；保留既有 repo-local Git 身份，不代替公开发表检查。operations/.staging-task011/ 为原有未跟踪暂存，未清理、不提交。最终核查会追加 operations/events.jsonl，尾部状态如实记录，不声称工作区绝对干净。旧误记行保留。已准入历史 123 个源文件只读哈希核查一致，不把它写成新的全旧目录完整性审计。

下一步：完成 TASK-012 的 G5 同步与对应提交 CI 核查，报告五项最终结论；之后仅等待所有者决定新任务。
