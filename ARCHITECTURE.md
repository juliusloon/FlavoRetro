# 当前责任与产物登记

本表登记活动事实源与文件职责。TASK 保存事前合同，REPORT 保存执行历史，STATE 保存当前事实，ADR 保存长期理由；新的产物先核本表。

| 入口/目录 | 责任与主要文件 | 状态 |
| --- | --- | --- |
| PROJECT.md / AGENTS.md | 稳定目标、硬约束与批准流程；本任务批准仅限 TASK-012 | active |
| STATE.md | 当前版本、阶段验收与待办，不替代历史报告 | active |
| pyproject.toml | Python 3.10 范围、固定核心依赖、验证工具、三项程序入口、默认资源打包 | active |
| environment/ | README 独立安装/资产恢复；requirements-linux-py310.lock 新解析锁；pip-freeze.txt 历史借用环境快照 | active |
| docs/ | 导航、用户/接管/测试文档、工作台/论文路线、FOUNDATION_CAPABILITIES.md 能力与边界矩阵 | active |
| docs/tasks、reports、adr | TASK-001…012；REPORT-001…012（含 007-P1）；ADR-001…005；编号目录说明与模板 | active |
| metadata/ | sources.json 来源/许可/哈希清单；sources-v1.json 历史留档；note-relocations.json 文件定位；active.json 活动版本/manifest 绑定；foundation.json 工程阶段事实；release.json 科学候选状态 | active |
| data/raw/ | 合法本地只读副本/模型，字节不可变，不入 Git | local immutable |
| data/derived/ | 活动 v3：records.json 事实源、manifest.json 构建/来源/记录哈希、index.sqlite 派生查询库、index.json 索引 schema/哈希；replay-v3 独立字节重放；v1/replay-v1/v2 原样保留 | local immutable |
| flavoretro/workspace.py | 显式工作区、包路径、默认/覆盖配置、活动版本验证；避免安装目录被当成可写工作区 | active |
| flavoretro/resources.py | 损失保全的源解析与新不可变版本构建，零/缺失/冲突/失败保持原值 | active |
| flavoretro/database.py | SQLite 索引构建、只读查询/分页/QC/收率/源状态、索引错配检测；JSON 仍是唯一事实源 | active |
| flavoretro/contracts.py、policies.py | 严格输入/预算；候选库存与明确已知危害过滤，未知不认证安全 | active |
| flavoretro/search.py | PUCT、动作融合/去重、替代动作、转置与预算；多产物保持原 index，不改变糖苷家族定义 | active |
| flavoretro/service.py、worker.py | CLI/API 共享的逐次进程与真正 MCTS；工作区/版本/模型/配置/代码指纹；运行结果、失败与 manifest | active |
| flavoretro/cli.py、web.py | 搜索 CLI 和本机 HTTP；静态前端、资源、拓扑、显式历史全文件核查、同进程搜索/开发对照门控 | active |
| flavoretro/evaluation.py | 固定 12-cell 工程开发对照与真实门槛 preflight；不是正式执行器，不是盲测 | active |
| flavoretro/topology.py | 保持原独立图诊断语义；labelled graph synthons, not reagents；不进 MCTS 扩展/评分 | active |
| web/、configs/ | 前端三个编辑源与三个配置编辑源；前端四页完整能力入口，不开放任意管理写入 | active source |
| flavoretro/assets/ | web/configs 的包交付副本；测试逐文件字节比较，独立安装读取，不依赖 checkout | active packaged snapshots |
| tests/ | 输入/保全、真实运行、优化行为、拓扑、SQLite、安装与 HTTP 合同；需本地资产的项明确标记 | active |
| scripts/ | operate.py 操作日志；browser_check.py 四页/历史/12-cell 浏览器验收；package_check.py 包外安装/真实搜索；artifact_check.py wheel/sdist 载荷边界；smoke.py 历史冒烟入口 | active |
| .github/workflows/engineering.yml | 固定 Linux/Python 3.10 无受限资产 CI，构建/安装/合同；CI 命令也经 operate.py；不上传本地载荷 | active |
| outputs/runs/ | 每次独立 request/result/worker.log/manifest，错误也保留；历史只显式读取 | local evidence |
| outputs/evaluation/ | 独立开发对照 contract/cell/summary；HTTP job 进度原子保存，外进程未完成记录不声称仍运行 | local evidence |
| outputs/validation/ | 每次独立浏览器/包/构建目录、TASK-012 阶段 JSON；task012-sync.json 是带时间的实际远端/CI 核查快照 | local evidence |
| operations/ | events.jsonl 追加式操作事件入 Git；命令日志/基线 JSON/本轮暂存不入 Git；最终只读核查可产生未提交追加尾部 | audit |
| operations/archive/ | 一次性脚本/旧构建器；不作为活动 runtime | archived |

科学门槛由 release 元数据和 preflight 显式保留；工程阶段通过不自动改变 primary source/vendor/independent labels/production/formal benchmark 状态。
