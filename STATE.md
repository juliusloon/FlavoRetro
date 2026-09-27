# 当前状态

TASK-001—011 的工程交付与历史报告保留。TASK-012 已由所有者于 2026-09-26 明确批准全部 G1—G5（“同意，开始执行”，human_direct 工程授权）；G1—G5 全部通过，工程地基就绪；交付提交 4b015cf 已同步私有 origin，同 SHA GitHub CI success。最终文档收口提交的远端/CI 核查快照保存为 outputs/validation/task012-sync.json。

活动资源：metadata/active.json → data/derived/v3。v3/replay-v3 的 records/manifest 逐字节一致，3,059 条记录与 v2 完全相同；v1/replay-v1/v2 原样保留。SQLite 为 v3 的只读派生索引，保留 123 条来源和全部记录；定位状态为 249 条 note_located_token_found、259 条 note_located_token_unmatched。文件定位/token 命中不是内容审核，0 production、3 条名称冲突仍保留。

运行与安装：.venv-foundation 使用独立托管 CPython 3.10.20，system-site-packages=false；依赖锁 environment/requirements-linux-py310.lock 不含本机 file:// 引用。wheel/sdist 包含默认配置和前端，仓库外安装已验证 CLI/Web/拓扑/缺资产诊断和 v3 实时 MCTS。原 .venv 与历史环境快照保留，日常使用新环境。仅验证 Linux x86_64/Python 3.10。

算法：实时 optimized/native MCTS 共享服务，每次新进程、新 run ID；修复同次扩展重复状态与过滤后原多产物 index 错配；PUCT/去重/替代动作/转置/节点预算合同通过。native 不共享 optimized 节点上限，不能声称等价预算或优越性。糖苷拓扑仍只作独立诊断与展示，未进扩展/评分。

前端：四页已有能力入口覆盖完整，包括全部搜索参数、评分/证据/版本/清单导出、9 类资源及 QC/收率/来源筛选、历史运行显式读取、27 个教学条目、15 文献卡及课程、12-cell 开发对照启动/进度/历史/结果与只读 preflight。47,836 条模型模板全为 0.0 Unrecognized，界面明确无法确定家族；文献联查仍为工程关键词匹配。未完成外进程 job 记录不冒充当前运行，不自动恢复。

验收：51 项本地全量测试通过；无资产 CI 模拟 45 项通过、6 项明确跳过。Chromium 在 1440×1000 与 390×844 核四页、参数、历史、导出、12-cell（0 失败）、429/400 与 UI 失败 fixture；JS 错误 0、四页移动无横向溢出。证据见 REPORT-012、outputs/validation/task012-g1…g4.json、task012-portable-v2.json、browser-714dac2a、package-66d62d36。CI 跳过、图回放、工程验收均不构成独立化学证据。

科学准入：research_candidate，primary source/current vendor unresolved、independent labels unavailable、formal benchmark not_executed，formal_run_ready/release_ready=false。教学标签、独立审核、正式盲测、P2 糖苷感知搜索、P4 交互及公开发布仍需新 TASK 与所有者批准，不自动开始。

工作区与 Git：现有私有 origin 为 juliusloon/FlavoRetro；保留既有 repo-local Git 身份，不代替公开发表检查。operations/.staging-task011/ 为原有未跟踪暂存，未清理、不提交；本地 .workbuddy 仍保留、不提交；WEB_UI_DESIGN 随 TASK-013 成果版本化；AppleDouble 文件已按所有者 2026-09-27 授权删除并加入 Git 忽略。最终核查会追加 operations/events.jsonl，尾部状态如实记录，不声称工作区绝对干净。旧误记行保留。已准入历史 123 个源文件只读哈希核查一致，不把它写成新的全旧目录完整性审计。

下一步：TASK-015 已完成 ORD 实测与审核准备；使用 outputs/review/task015-v2/index.html 做 30 条糖苷重点初筛，按 4 条定向清单补来源。实际独立人审/开发 gold 尚未执行；P2/正式盲测/公开发布没有自动授权。

2026-09-26：[TASK-013 Web 界面设计规范落地（移动优先、对比度与可访问性）](docs/tasks/TASK-013-web-ui-design.md) 已起草，状态 Proposed，设计依据 docs/WEB_UI_DESIGN.md（含 WCAG 实测对比度审计、色彩/字体 token、移动优先断点方案）；待所有者人工批准，起草轮未改动 web/ 任何代码。

2026-09-26：TASK-013 已完成（所有者当日“批准，执行”，human_direct）。web/ 三文件呈现层落地设计规范：配色/字体 token 化，4 组对比度修正过 WCAG 2.2 AA；移动优先 min-width 断点（768/992/1280），sticky 侧栏替代 body overflow:hidden；tablist 语义 + 方向键 + skip link + th scope + role=alert + 骨架屏 + 触控目标 ≥44px + reduced-motion；既有文本节点零变更（唯一新增为合同列明的 skip link）。验收：51 项单测、contrast 34 组、浏览器全量（24 项视口溢出全 false、JS 0、12-cell 0 失败、既有断言零回归）全过；证据 outputs/validation/browser-7ff005c5、contrast-ca9a2615 与 command-0182—0189，详见 docs/reports/REPORT-013-web-ui-design.md。未执行 git 提交/推送（合同未授权），改动待所有者决定。T4 深色模式未动工。

2026-09-26：所有者指示把后续发展空间写入路线文档，作为之后 TASK 的思路。已在 docs/PAPER_ROADMAP.md 新增「下一阶段主线：从"工程正确"到"科学可评价"（TASK-014—018）」：现状判断、D1—D7 方向价值排序、主线任务序列表（TASK-014 评测协议与标签规范 → TASK-015 人工 gold set → TASK-016 P2 糖苷感知搜索 → TASK-017 冻结 blind benchmark 并执行 → TASK-018 消融与论文结果）、并行低风险线与论证链；在 docs/WORKBENCH_ROADMAP.md（P2→TASK-016、P3 并行、算法调优排在评测之后）与 docs/README.md 加交叉指引。该节为方向性计划，不是已批准的 TASK 合同：TASK-014—018 均须所有者人工批准后才可动工，本轮未创建任何 TASK 合同、未改动代码。工作区仍保留 TASK-013 的未提交改动。

2026-09-27：TASK-014 已按所有者 human_direct 批准完成，报告见 docs/reports/REPORT-014-domain-triage.md。交付黄酮总分类 v1（9 个母核查询、7 项候选分类，化学 provisional）、508 条笔记 guide、2,301 条离线试点与标注/评测协议。精确反应 1,444 组，重复来源 857 条全部保留；三队列为 1,289 guide 支持、654 guide 外结构候选、358 低/未知，含 56 条不完整/泛化记录。60 条未填写开发审核样本含 30 条糖苷重点；全部输入 development_exposed，无独立盲测集。最终目录 outputs/triage/task014-final，12 个文件与 task014-replay 逐字节一致；独立审计通过，141 个受保护文件不变，本地 62 项回归全部通过。新模块 flavoretro/triage.py 不接入 MCTS，v3/active/release/UI 保持原样；formal_run_ready/release_ready=false，0 production，独立化学标签未产生。未提交/推送，TASK-013 既有改动与范围外文件继续保留。下一步是所有者审批 TASK-015，不自动执行。

2026-09-27：TASK-015 已获本会话“好，开做”的 human_direct 工程授权并 Completed，报告 docs/reports/REPORT-015-ord-coverage-review-cards.md。ORD 官方镜像冻结 revision 93475c46949f9218e1dfb6624096025135db2add，53 个当前 Parquet 全部校验并逐行扫描，1,256,526,213 字节、2,428,291 来源记录；8,509 领域候选、1,246 无法判断；8,508 完整候选严格分组 6,013，另 1 不完整候选保留。78 糖苷候选严格 65 组，来源仅 USPTO/上游训练/验证；产物侧芳基 C 拓扑未命中。本地已有 227 条芳基 C 候选，当前优先缺具体实例/原文而非大批重搜。60 条离线审核卡（30 糖苷重点）含结构/原始事实/机器建议/空白人审，支持浏览器草稿、校验导入导出；47 文献标题中 32 DOI 导航、11 原报专利号、4 待核对，均非化学来源确认。最终 outputs/review/task015-v2，与 task015-replay-v2 的 3 核心文件字节一致；4 条定向材料清单与 inbox 格式见 SCIFINDER_TARGETED_IMPORT_V1.md。67 本地测试、53 源哈希与 25 行原件绑定、197 受保护文件、最终桌面/手机浏览器检查均通过。原始/候选/卡片均不上 Git，未提交/推送/跑新 CI；v3、active/release、搜索/UI、TASK-014 冻结数据不变，0 human_reviewed / gold / production，formal_run_ready/release_ready=false。实际人审与来源/标签接管须单独合同；训练独立性 unknown。

2026-09-27：所有者 human_direct 授权直接清理 AppleDouble 并同步 Git，不新建 TASK。已删除项目内（不含 .git）32 个经文件头确认的 `._*` 文件，`.gitignore` 增加跨子目录 `._*` 规则；本次授权将 TASK-013—015 的代码/配置/协议/报告及操作审计纳入 Git 同步。原始/受限数据、候选/审核卡片、.workbuddy 与 operations/.staging-task011/ 保留本地、不提交；历史目录未改动。同步结果以 Git 远端与 operations/events.jsonl 为准。
