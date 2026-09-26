# REPORT-012：工程地基补齐与统一验收

## 对应任务与当前结论

- 任务：[TASK-012](../tasks/TASK-012-foundation-readiness.md)
- 状态：In Progress（G1—G4 已通过；G5 远端同步/CI 待收口）
- 本地基线：main @ 5f3240f；核查时远端 main=f272c36，落后两个功能提交。
- 批准：所有者 2026-09-26 回复“同意，开始执行”，human_direct 工程授权，包含 v3 切换与现有私有 origin 普通推送；非 agent_delegated、非逐记录 human_reviewed。
- 执行者：Cano；全部本机写入/命令经 operate.py，CI 命令也使用 operate.py。原始与受限载荷不入 Git。

| 工程门槛 | 当前结果 | 证据 |
| --- | --- | --- |
| 资源版本/数据库 | pass | v3/replay-v3 字节一致、3,059 条守恒、123 来源、只读 SQLite 全量分页/QC |
| 算法运行合同 | pass | 真实 MCTS、PUCT/去重/替代/转置/预算、多产物 index 合同；native 限制仍明确 |
| 独立 Python 交付 | pass | 独立 CPython/venv、191 依赖锁、wheel/sdist、包外静态/配置/真实 MCTS |
| 前端已有能力覆盖 | pass | 全参数/历史/资源/教学/拓扑/开发对照/preflight，四页浏览器验收 |
| GitHub/CI | pending | 工作流与本地无资产模拟通过；尚未把待推送当作同步完成 |

只在五项同时通过后宣告 TASK-012 的工程地基就绪；不据此宣告 production、独立化学验证、正式盲测或公开发布完成。

## 实际修改与文件职责

| 目录 | 文件/产物 | 实际用途与改变 |
| --- | --- | --- |
| flavoretro | workspace.py（新增） | 显式工作区、安装包默认资源、活动指针/来源/记录哈希验证，缺资产不回退 |
| flavoretro | database.py（新增） | SQLite schema、源外键、全部原记录 JSON、outcomes/QC、只读筛选分页、索引错配检测 |
| flavoretro | resources.py、contracts.py、policies.py | 当前工作区构建、包内/覆盖配置、统一活动索引；未启用候选库存时不要求私有资源 |
| flavoretro | service.py、worker.py、cli.py | 父服务/worker 同一工作区和解释器；不依赖可写 checkout；v3/manifest/配置/代码指纹；CLI 全参数 |
| flavoretro | search.py | 修复同次扩展重复状态预算分配和过滤后反应 outcome index 错配；保留原 PUCT/策略/家族科学定义 |
| flavoretro | evaluation.py、web.py | 真实门槛 preflight、固定 12-cell 进度/失败持久化、HTTP 共享门控、显式历史所有文件哈希核查、版本/安装/同步快照 |
| flavoretro/assets | web 三文件、configs 三文件（新增） | 受控包资源副本；测试与编辑源逐字节比对。配置值不编造分类标签 |
| web | index.html、app.js、style.css | 全部已有能力入口；Unknown 分类、原证据边界保留；资源请求防过期结果覆盖；四页架构保留 |
| tests | test_database/package/search/web_foundation（新增）；test_contracts | 数据/安装/优化/HTTP 实质性合同；私有资产项标记跳过，不把跳过当成成功 |
| scripts | package_check.py、artifact_check.py（新增）；browser_check.py | 包外独立运行、发行载荷边界、全部能力与真实开发对照/错误 UI 验收；浏览器用当前独立解释器 |
| metadata | active.json、foundation.json（新增） | 绑定已验收 v3；分别记录 human_direct 工程门槛，不改 release 的科学候选裁决 |
| environment/根级 | requirements-linux-py310.lock、README、pyproject、.gitignore | 独立依赖固定、工具分组与入口/资源打包；历史 pip-freeze/原 .venv 保留 |
| .github | workflows/engineering.yml（新增） | 固定 Linux/Python 3.10、无受限资产合同/构建/包外安装；官方 action SHA 已现场核对；不上传本地运行/数据 |
| docs/根级 | TASK/本 REPORT、能力矩阵、ADR-005、STATE/架构/导航/使用/测试/接管/路线 | 中文职责与实际边界；修正“补数值映射即可确定家族”和旧远端/环境/v1 文案；历史 TASK/REPORT 不静默重写 |
| operations/archive | database-index-task-012-v1.py（新增） | 初次 SQLite 构建器原字节快照，匹配 index.json 的 builder SHA；当前模块后来只优化 inventory 读取，schema/build 没变 |

本地生成、均不入 Git：新 .venv-foundation；data/derived/v3/replay-v3；v3 的 index.sqlite/index.json；独立 runs/evaluation/validation；构建 wheel/sdist；失败与成功的浏览器/无资产模拟目录。既有 data/raw、v1/replay-v1/v2、outputs、原 staging-task011 未删除或覆写。

## 数据与构建证据

- v3 与 v2 的 records 逐字节一致，ID/原值/结构/冲突/失败保持；records SHA-256=448dbbdcd511df0aade80903d33abc34707fdcc2d529d3ecb29dbae94898192e。
- v3/replay-v3 的 records 和 manifest 各自逐字节一致；manifest SHA-256=07a41aa61e3a031d4e48b1e16c8739c5351cdd8a93cc2cd871e9306a6e1a5a0e，构建器 resources.py SHA=b92bfdc7bd52a72c6412d95d7b0eba0189087ef317cb67e6dc6ad66325dd8816。相对 v2 仅构建器版本元数据变化。
- SQLite SHA-256=ff130bbeade254632e2020b09863ce45b60a7886b9128bc61857b62cad5887f7；初次构建器快照 SHA=feb30942780617c88a030f472581c34547d56586c77e67d7bc29f185e68587ee，与 index.json 一致。
- 3,059 条：508 note_reaction、2,301 scifinder_reaction、156 molecule、2 duplicate-name、4 failure-group、49 stock、2 template、15 paper、22 supplier。4 是失败分组记录数，不是失败结构数量。
- 0 production、3 个名称冲突、17 条候选库存准入记录；数值零收率 0、明确缺失 1,075。零规则用原创 fixture 证明，未删零或猜测缺失。
- v3 的 508 文献记录中，249 条找到原 token，259 条只定位文件；均不升格为原文内容/人工化学审核。TASK-007-P1 的历史“计数一致即重放”不作为此次回放证据。
- 本项目保护基线全一致，另只读核了 123 个已准入历史源文件，全部与 source manifest 匹配；未在旧仓库执行代码或写入。不是一次新的全旧目录 33,146 路径盘点。

## 验证结果与原始证据

| 检查 | 实际结果 | 本机证据 |
| --- | --- | --- |
| G1 构建/独立重放/活动指针 | pass，records/manifest 字节一致，v2 原值完全守恒 | outputs/validation/task012-g1.json |
| G2 SQL/JSON 守恒/分页/QC/preflight | pass，全量 9 kind 逐 ID/原记录一致 | outputs/validation/task012-g2.json |
| 两个优化缺陷复现→修复 | 先 2 个明确失败，后合同与真实运行通过；未改糖苷语义 | command-0098 失败、0100 修复后 44 项通过；最终 0143 |
| 新独立环境/依赖 | CPython 3.10.20 托管发行，system-site-packages=false；pip check 通过；191 第三方依赖/工具锁，无本机 file:// | command-0103/0105/0111/0113/0119；task012-g3.json |
| 最终完整测试 | 51 项通过、0 跳过 | operations/command-0143.log |
| 无数据/模型 CI 模拟 | 51 项中 45 通过、6 明确跳过（保全/回放/冲突三项+live三项） | task012-portable-v2.json；command-0148 |
| 最终 wheel/sdist 资源/边界 | 配置/静态资源齐全，原始/模型/索引/运行不在包中 | command-0142/0144；task012-final-dist |
| 最终安装包仓库外探测 | site-packages 中应用，sys.path 无旧 Conda/旧仓库；配置/静态/教学/拓扑 200，缺资产 status 503；真实 v3 MCTS 6 节点/2 条非零步骤路线 | outputs/validation/package-66d62d36/report.json；command-0149 |
| 全能力浏览器 | 全参数/v3/manifest 导出/历史 run 数不变/QC/收率/来源/27 教学/15 文献/12 cell 0 失败/429/非法输入/UI 503 fixture | browser-714dac2a/report.json；command-0131 |
| 四页移动与 JS | 1440×1000 / 390×844；四页无横向溢出、JS 错误 0；截图已实际查看 | browser-714dac2a；task012-g4.json |
| 保留文件/历史源完整性 | 基线无漂移、123 历史源无缺失/哈希差异、topology.py 原字节不变、命令日志名无碰撞 | outputs/validation/task012-integrity.json |
| Git/CI 权限和身份边界 | origin 仍私有、认证账户 juliusloon 与 owner 一致，push/admin=true，Actions enabled；保留原 ljx (repo-local placeholder) 身份，未替换 | command-0134/0135 |

最终本地发行物（未公开上传）：

- wheel：outputs/validation/task012-final-dist/flavoretro-0.1.0-py3-none-any.whl，SHA-256=90b5cc8a9366edfd420d9a26321653eb149a49a7722f85beb46fd85e6c4d3274。
- sdist：outputs/validation/task012-final-dist/flavoretro-0.1.0.tar.gz，SHA-256=274efb3b5c0bf419b9bfcb4252ee251bfaba6ebb4a6aa1ecb1b0cc6d5c768e9a。

实时运行均是新的 run ID/worker/MCTS，历史读取另有明确 execution_source。安装包最终探测 run=20260926T104330-ee85e91597a7412db2b5ed1568c18264；成功浏览器开发对照 development-a89860b321f648f7a41bb40091bf6aea 的 12 cell 全部留档。这些只证明工程流程，不构成独立算法性能/化学证据。

## 偏差、失败及处置

1. 新优化合同先发现同次扩展重复状态和过滤后 outcome index=0 错配，按已批准 search.py 工程缺陷预算修复。原失败日志保留。
2. 全能力浏览器首轮 command-0127 因折叠 details 内 pre 的 inner_text 为空而失败；真实 12-cell 当时已完成、0 失败（development-db405aeaad694ae2b10db85e04011b1b）。仅将检查改为 text_content，再在新目录独立验收通过；不删前一次输出，也不冒充其浏览器验收成功。
3. 无资产模拟首轮 command-0146 错将 venv 的 Python symlink resolve 到基础解释器，导致模块缺失；保持 venv 调用路径后在新目录通过。原 task012-portable.json 与失败目录保留；不是依赖解析失败或借用旧环境。
4. 本地 CI shell 验证辅助选择步骤时一度直接读取没有 name 的 action 步骤，引发 KeyError；改为 get 后验证实际安装 shell 成功，未改运行代码。诊断日志保留。
5. web/configs 保留编辑源，新增包内受控副本，未物理移动原文件；自动测试阻止副本漂移。这是合同允许的打包方案。
6. SQLite 初次构建器完整文件 SHA 与后来优化 records 读取后的活动模块不同；已保留能逐字节匹配原 SHA 的完整构建快照，不改 immutable index manifest，不将差异解释为数据漂移。

## 限制与未开展事项

- 科学状态仍 research_candidate，primary source/vendor unresolved、independent labels unavailable、formal benchmark not_executed、formal_run_ready/release_ready=false；工程 human_direct 不等于化学人工审核。
- 模型 47,836 个模板全部为 0.0 Unrecognized；能浏览 27 条教学材料不等于自动识别 27 个家族。拓扑与关键词文献关联仍为候选/工程关联。
- Linux x86_64/Python 3.10 单平台；浏览器复用匹配的用户缓存 Chromium，不据此保证新机浏览器安装或其他平台性能。
- HTTP 为本机开发服务器，门控只在同一服务进程；未做分布式调度/公开部署/真人可用性试验。中断 job 不自动恢复，不伪装仍运行。
- CI 无真实本地资产，不执行 MCTS/浏览器，跳过 6 项不能替代本地证据；不上传真实输出。
- 私有同步不包含 PyPI、公开仓库、标签或论文发表身份替换，PAPER_ROADMAP 的公开发布检查仍待所有者。

## GitHub 同步与最终收口

当前正在完成普通提交/推送与对应 SHA 的远端 CI 验收；本段只在获得实际结果后更新，不提前称完成。交付前精确检查 staged 清单，data/outputs/环境/旧 staging 不纳入；最终只读核查仍追加 operations/events.jsonl，报告其尾部状态。

本任务之后不自动进入 P2/P4/P5 或正式盲测；由所有者审核下一份 TASK。
