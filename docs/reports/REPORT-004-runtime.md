# REPORT-004
已从零实现包、原生/优化树适配、共享子进程服务与 CLI。没有导入旧 src。
16 项合同测试本次通过；3 次新 live smoke 通过，分别为 quick、重复 quick、candidate balanced 两阶段；细节 outputs/validation/live-smoke.json。
保留失败探索记录：第一次 smoke 生成树但 min_routes=0 无 partial 输出；修复后重新验证。不把首次失败范围删除。
模型为 5 个独立复制的外部 ONNX/CSV；领域 2 候选模板未启用。默认 0 verified stock。搜索产生 partial 是证据边界；候选库存闭合只能 surrogate，始终非 actionable。
参数暂定；安全仅检查已知特征与元数据，未独立前向模型验证。原生树无等价节点上限。计算结构 route ID 与 seed 分阶段保存；不承诺墙钟预算导致的逐位可重复性。
环境 FastAPI 缺失，改用标准库 HTTP；未修改共享 retro 环境。
