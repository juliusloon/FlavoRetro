# TASK-004：独立实时 MCTS 与共享服务
Approved，Cano agent_delegated。本次设计采用独立代码，通过已安装 AiZynthFinder 4.4.1 接口实现，不 import 历史 src。
理由：先建立可信执行身份，继承 PUCT/融合/循环/候选替补知识，不继承旧分数与收益主张。
范围：原生基线+优化树；单一 profile；结构 route ID；模型快照；CLI/API 共用隔离子进程服务；不可变 run/error；明确 candidate stock 开关；known-hazard/映射/回放过滤。
默认只用外部预训练策略，不启用 2 个未审领域模板；空 verified stock 可以产生 partial 结果。候选探索显式开启且不可成为 evidence/actionable。
验收：真实 MCTS 重复调用生成不同 run ID；有效约束；新运行哈希绑定；错误与超时可追踪；无旧目录运行依赖；单元和真实 smoke。
非目标：参数最优性、独立化学收益、正式盲测、湿实验。未知风险不标安全。
