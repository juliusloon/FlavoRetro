# TASK-021 仓库全面盘点与精简重构

状态：Approved — agent_delegated（所有者 2026-10-15 指令「全面完整分析整个仓库……整理精简……统一重构」授予本轮自主审批权；不伪装 human_reviewed）
日期：2026-10-15
执行：Cano

## 背景与理由

TASK-001—020 期间，仓库按「先跑通、再留存」累积了大量任务期产物：scripts/ 524 个顶层条目中绝大多数是各 TASK 的一次性脚本；outputs/ 15,000 文件 / 1.4 GB 混合冻结证据与临时草稿；operations/ 6,386 个条目中 6,300+ 是历史命令日志；temp/ 混有用户授权数据与散落测试脚本；docs 导航表落后于实际任务账。多个历史版本、temporary 测试文件与活动文件混在一起，可读性差。所有者要求：全面分析、整合精简、历史版本与临时文件不与活动文件混杂，并统一重构 state / progress / architecture 治理文档。

## 范围

IN：
- 全仓盘点（scripts、outputs、operations、temp、build、flavoretro 包、tests、configs、docs、根目录散件），形成分类台账。
- 一次性任务脚本的档案化归位（scripts/archive/），历史草稿与临时测试文件与活动文件分离。
- 冻结证据不动字节：outputs/ 中带 manifest / SHA 钉的载荷保持原路径，只补索引与标记。
- operations 历史命令日志归位归档，事件账 events.jsonl 原样保留。
- 治理文档统一重构：STATE.md（只存当前状态）、新增 PROGRESS.md（全任务时间线与当前位置）、ARCHITECTURE.md（重排为分层责任登记）、docs/README.md 导航补齐、outputs/、scripts/ 说明文件。
- 全程以 scripts/operate.py 记录写入与命令。

OUT（不动）：
- data/（原始/派生冻结数据，字节不可变）；metadata/active.json 绑定的活动数据层。
- flavoretro/ 运行代码与 configs/（含历史版本链模块，被配置与重放钉住，只登记不合并）。
- tests/ 现有合同测试文件的删除或断言修改。
- .venv*、.workbuddy、.zwork、.git、LICENSES/、.github/。
- 历史目录 /home/ljx/retro_synthesis、/home/ljx/CondRxnBench、/home/ljx/FutureHealth 零触碰。
- Git 提交/推送：本轮只整理工作树与暂存区，不同步远端（同步须所有者另行授权）。

## 阶段

- G1 盘点：四个并行子代理分别盘点 scripts / outputs+temp / operations+docs+根目录 / 代码+配置+钉定关系，产出分类台账到 outputs/restructure/repo-consolidation-20261015/。
- G2 处置分级：每项标注 KEEP（原位）/ ARCHIVE（移动到明确档案路径）/ DELETE（仅限可再生缓存，逐项列出）。冻结、被钉文件一律 KEEP。
- G3 执行：按台账移动归档；git 跟踪文件用 git mv；不删任何冻结产物。
- G4 治理文档重构：STATE/PROGRESS/ARCHITECTURE/docs 导航/目录说明。
- G5 验证：compileall 通过、代表性测试通过、git 状态核对、移动前后文件数守恒核对。
- G6 报告 REPORT-021 与 STATE 更新。

## 验收

1. 台账覆盖全部顶层目录与 scripts 顶层条目；每条有处置标记与依据。
2. 移动只发生在一层明确的 archive/ 归档结构内；活动入口（pyproject 入口、CI workflow、常驻脚本、flavoretro 包）引用路径零变更或已同步更新。
3. 被钉文件（manifest/runtime_file_hashes 引用的路径）0 移动。
4. STATE.md 重构后不含任务历史流水（历史由 PROGRESS.md/TASK/REPORT 承载），并如实登记科学门槛现状（formal_run_ready/release_ready=false、C/SS 效果 null 等）。
5. compileall 与至少一项无资产合同测试通过；所有变更经 operate.py 记录。

## 停止条件

- 盘点发现某目录被钉但已被移动/损坏：停止该分支，报告实况。
- 发现删除类操作必须越过「可再生缓存」范围：停，改归档。
- 挂载卷写入异常（EINVAL 等）：记录实况，改用可用通道，不静默重试。

## 2026-10-16 续作批准与验收解释

批准 agent_delegated、human_reviewed=false，依据所有者 continue this work 与本轮自主审批权；事前续作记录见 [continuation-approval.md](../../outputs/restructure/repo-consolidation-20261015/continuation-approval.md)。原合同全文与G1/G2台账原件保留。

- G2 已确定：有路径/哈希或既有受控入口职责的脚本原位 KEEP；不用物理搬动造成旧保护失效。522/523 顶层脚本名字有引用台账，task020工具按报告溯源保留；不把引用名字总量524误作顶层数。
- G4 补齐当前状态/时间线/分层架构/导航与目录索引。归档草稿原字节保全，仅对阅读副本25处链接作位置修正。
- G5 原始全量 compileall 通过标准 **未达成**：两个被冻结历史P7脚本已有SyntaxError。批准保留既有字节，以活动包/测试/常驻入口语法通过、完整扫描失败明确登记、无资产合同通过、保护与归档核验为本轮治理验收；不授权修旧科学脚本或重开P7。
- 日志缺3份历史write事件、1份历史并发哈希歧义、40项脚本/包保护旁车缺失均保留披露。它们不被写作全量无例外通过。临时脚本/网页原盘点没有移动前SHA，验收限于路径与大小守恒。
- 范围不扩展至Git暂存/提交/推送、MCTS/科研矩阵、科学来源/标签/供应/发布、FutureHealth后续阶段或外部历史目录。

执行结果和逐项验收见 [REPORT-021](../reports/REPORT-021-repository-consolidation.md)；本附录不改写任何旧任务结果。
