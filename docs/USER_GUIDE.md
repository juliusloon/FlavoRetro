# 使用说明

## 路线探索
选择示例或输入 SMILES，预览结构后开始搜索。quick 单阶段 45 秒/50 迭代；balanced 主阶段 120 秒/100 迭代与第二阶段 240 秒/800 迭代；strict 360 秒/1800 迭代。这是搜索时间预算，模型装载另计，单次迭代可能跨过边界，隔离进程另有整体超时。
每次提交都启动新进程、新 MCTS、新 run ID。CLI 与 Web 使用同一个 service.search。内部候选池每阶段最多 25，显示默认 5；实际路线少则显示少，不凑数。
默认无已审库存，可得到 partial；显式候选库存探索会排除 virtual 与已发现名称冲突，闭合仍只是 surrogate。预测步骤没有逐步原文证据时明确未知，不自动匹配 DOI 声称先例。
成本越低排序越前，由步数、未解决原料、已知危害、未指定叶子立体构成；系数暂定，不是专家偏好结论。未知风险不表示安全。结构图不是实验操作指导。
若返回 429，表示同一服务中已有搜索或开发对照正在执行。错误结果保留在 outputs/runs/<id>/；worker.log 与 manifest 可诊断。导出 JSON 使用 execution_source + manifest + result 封装，包含配置、资产/代码哈希、阶段、候选和限制；历史读取明确标注 explicit_saved_run。

## 资源与证据
可按类型、名字、SMILES 或来源筛选。详情 raw 保留来源字段；source_path + SHA-256 + locator 定位只读原始副本。source_status、结构解析、human_review_status 和 production_eligible 分开。
SciFinder RDF 本次重新解析；笔记条目与分子库是已搜集资源的快照，未补未知产率。molecule_failures 与 duplicate_names 单独保留。供应商 listing 只代表历史导出内容，不确认当前供货。

## API
- GET /api/health、/api/status、/api/targets。
- GET /api/records?kind=stock&q=...&offset=0&limit=25（上限 100）。
- GET /api/molecule?smiles=... 输出本地 RDKit SVG。
- POST /api/search：JSON {"smiles":"CCOc1ccccc1","mode":"quick","seed":0,"seconds":2.0,"iterations":5,"candidate_stock":false}。
- GET /api/runs/<run_id>：显式读取本项目已保存运行，校验 manifest 中全部文件 hash；返回 execution_source=explicit_saved_run。普通搜索从不调用此端点。

## 重放资源与诊断
`python -B -m flavoretro.resources data/derived/new-version` 拒绝覆盖旧版本，读取 metadata/sources.json 及新目录 raw；当前 runtime 使用 metadata/active.json 绑定的 v3，且 SQLite 索引校验同一版本；版本切换需明确批准，不自动采用任意新版本。
`python -B -m flavoretro.topology outputs/new-topology.json` 运行独立结构检查，不修改 MCTS。
`python -B -m flavoretro.evaluation --development` 新跑 12 开发 cell。无参数输出 formal preflight；正式盲测执行器尚未交付。

## TASK-012 新入口

实验参数补齐 optimized/native、top_k、depth、branching、nodes；native 节点上限不等价。资源页可查询全部 9 类记录、冲突/解析失败、零值/缺失/未解析收率，以及来源文件/token 定位状态。教学页可独立浏览 27 个条目；0.0 Unrecognized 不自动归为具体家族。

项目状态页可按 run ID 显式读取历史、查看全部 manifest/指纹，读取不会运行新 MCTS。开发对照固定 12 cell，显示进度、错误和 cell/run 明细，可打开已存结果；不属于正式盲测。当前正式 preflight 为 false。

新增 API：GET /api/runs（分页），GET /api/preflight，GET/POST /api/evaluations（POST 只接受 {"kind":"development"}），GET /api/evaluations/<id>。资源查询另支持 issue、outcome、source_status。

默认使用独立 .venv-foundation；源码和安装包均可 --workspace 指定工作区。安装与资产恢复见 [环境说明](../environment/README.md)，能力对应关系见 [能力清单](FOUNDATION_CAPABILITIES.md)。
