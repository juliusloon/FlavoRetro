# 工程能力覆盖与证据边界

TASK-012 的统一验收范围是工程基线；科学就绪仍以 release 元数据和正式 preflight 为准。核查与执行证据见 [REPORT-012](reports/REPORT-012-foundation-readiness.md)。

| 能力 | 后台/CLI | 前端入口 | 验证与边界 |
| --- | --- | --- | --- |
| 实时搜索全参数 | SearchRequest；cli/web → service → 新 worker | 路线探索，实验参数内 engine/top_k/depth/branching/nodes，模式/seed/候选库存/seconds/iterations | browser_check 校验提交参数、v3、真实双阶段、非零步骤；native 不等价节点上限原样展示 |
| 路线/评分/证据 | worker 输出树、cost、phase、哈希 | 评分、叶子、步骤卡、版本指纹/manifest 和 JSON 导出 | 暂定成本、surrogate/partial、actionable/evidence_closed 与限制保留；没有逐例可行性结论 |
| 显式历史运行 | GET /api/runs 列表；GET /api/runs/<id> 校验所有 manifest 文件 | 项目状态运行列表、完整 run ID 输入、历史读取按钮 | browser_check 验证读取前后 run 数不变；test_web_foundation 验证日志篡改/缺文件 409；不冒充实时运行 |
| 数据库/QC | database SQLite query；GET /api/records | 9 个 kind、名称/原始字段、QC/收率/来源状态筛选与 JSON 明细 | 全量分页逐 ID 与 JSON 一致；3 冲突/1075 缺失/0 零值/249 token 命中；零规则另用原创 fixture 验证 |
| 来源/版本/重建 | workspace.active_data 与 index manifest；资源/database CLI | 资源明细、项目状态安装/索引/重建说明 | 管理操作显示命令，不开放任意路径写入；定位到文件/token 命中不等于化学审核 |
| 拓扑诊断 | /api/topology；/api/molecule?topology=1 | 目标/叶子 family、键高亮、关键词文献链接 | 原 topology.py 不变；labelled graph synthons, not reagents；未进搜索 |
| 教学/文献 | /api/teaching；/api/literature-teaching | 27 教学条目目录、路线教学、15 文献卡/课程 | 0.0 Unrecognized 明确无法确定家族；关键词关联不构成原文验证 |
| 开发评估 | 固定 12-cell compare；POST/GET /api/evaluations | 项目状态启动、进度、已存对照、cell 表与单次 run 读取 | 每 cell 新 MCTS；共享本服务的 GATE；429 忙碌；0 失败的验收实例仅为工程观测，不是算法优越证据 |
| 正式 preflight | GET /api/preflight；evaluation CLI 默认 | 项目状态只读 JSON 门槛 | 来源/供应/标签/协议/生产投影逐项检查；当前 formal_run_ready/release_ready=false |
| 独立安装/Git | wheel/sdist、包外探测、私有仓库 CI | 项目状态工程门槛、安装/工作区、带核查时间的 Git SHA/CI 快照 | Git 状态来自本机验收快照，非界面实时远端查询；缺快照明确未核查；单平台验收不冒充跨平台 |

桌面 1440×1000、移动 390×844 的四页均已核对，无横向溢出、JS 错误 0；非法输入可见。引擎失败界面用明确标记的 503 fixture 验证，真实 timeout/engine failure 保留合同由单元测试验证，不把 UI fixture 当作真实 MCTS 成功。

开发 job 持久化进度；若记录不属于当前服务进程，以 interrupted_or_untracked 呈现，不改写原记录或自动恢复。服务仍为本机开发服务器，不具备分布式调度或正式部署验收。
