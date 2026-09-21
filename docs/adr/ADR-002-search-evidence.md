# ADR-002：先可解释的实时研究产品，再逐证据晋级
接受。外部预训练模板是预测模型资产；领域模板候选不默认进入运行。默认无已确认库存，返回 partial 是真实覆盖缺口，不凑路线。
候选库存探索仅在显式请求后启用，排除 virtual 与名称冲突。其闭合标 surrogate / unreviewed_candidate_stock，actionable 始终 false。
quick/balanced/strict 预算继承作为暂定配置，balanced 仍两阶段，无 ZINC。保留原生树用于同资产短预算比较，不能称正式盲测。
新实现不照搬旧 AHP 权重为专家结果；展示步数、未解决原料、已知危害、未指定立体的分项成本，权重暂定。
