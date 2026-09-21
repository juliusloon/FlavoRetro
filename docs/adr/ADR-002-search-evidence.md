# ADR-002：先可解释的实时研究产品，再逐证据晋级

- 状态：accepted
- 日期：2026-09-21
- 负责人：Cano（agent_delegated）

## 背景

旧项目 `/home/ljx/retro_synthesis` 的 2026-09-20 复盘（快照已复制到 `data/raw/legacy/docs/reports/260920-pre_refactor_project_retrospective.md`）留下了两组必须内联的实证，以及一套只作设计输入、不继承结论的搜索架构知识。

实证：

- 旧 13 靶标 benchmark solved 9/13，而 evidence-closed 0/13——"搜到路线"与"证据闭合"完全脱节。
- 1,053 cell 参数敏感性（13 targets × 3 seeds × 27 configurations，2026-08-12）中，reward 优先候选 solved 30/39，而 actionable 0/39——调参数能提高 solved，不能提高可执行性。
- 旧分层领域库存 49 条（18 strict、2 trusted、29 virtual），按新审核口径 0 条晋级 production；virtual 桥与供体沙箱闭合曾被误当可信。

继承为设计输入的旧架构知识：自适应 PUCT、跨 policy 先验融合（USPTO 1.0 / RingBreaker 0.65 / domain 1.35）、循环剪枝 + InChIKey transposition 登记、结构 route ID、六级闭合法则（evidence/trusted/discovery/surrogate/heuristic/partial）、硬剪枝（剧毒/重金属/自燃/<-50℃/映射完整性/失败前向回放）、四因子 AHP 评分（对步数、未知原料、危害、立体风险的权重约 1/3、1/6、1/6、1/3，为暂定值，从未获专家验证）。

因此新系统的立场是：先交付一个证据边界可解释的实时研究产品，production 级结论随证据逐条晋级，而不是先追求 solved 数字。

## 决定

1. 资产分轴：外部预训练模板（USPTO、RingBreaker）是预测模型资产；领域模板候选不默认进入运行。
2. 默认无已确认库存：返回 partial 是真实覆盖缺口，不凑路线、不为提高 solved 引入弱终止。
3. 候选库存探索仅在显式请求后启用：`flavoretro/contracts.py` 中 `candidate_stock: bool = False`；启用时排除 virtual 与名称冲突记录；其闭合标 `closure=surrogate`、`evidence_basis=unreviewed_candidate_stock`，且 `actionable` 始终为 `false`（`flavoretro/worker.py`）。
4. 预算：`quick`/`balanced`/`strict` 继承旧 profile 作为暂定配置，`configs/search.json` 记 `status=provisional_not_optimized`；`balanced` 仍为两阶段（两段预算依次运行）；无 ZINC（`discovery_stock=False`）。
5. 候选池与展示分离：`candidate_pool=25`、`display_k=5`（对应 `contracts.py` 的 `top_k` 默认 5、上限 25），不按条数凑展示结果。
6. 原生树保留为同资产短预算开发对照（`flavoretro/evaluation.py`，秒级预算、双 engine 比较），不能称正式盲测。
7. 评分不照搬旧 AHP 权重为专家结果：展示 `steps`、`unresolved_materials`、`known_hazards`、`unspecified_leaf_stereo` 分项成本；合成 `score = steps + 2*unresolved + 5*hazard + stereo`，并标 `score_status=provisional_cost_lower_is_better`；权重暂定。
8. 发布状态按事实记录：`metadata/release.json` 六维无一满足——`primary_source_review=unresolved`、`current_vendor_evidence=unresolved`、`independent_chemical_labels=not_available`、`formal_benchmark=not_executed`、`public_deployment=not_requested`、`user_evaluation=not_performed`。

## 备选方案

- 继承旧 49 条分层库存直接当 trusted：新审核口径 0 晋级使 strict/trusted 层名存实亡，且 49 条中混有 29 条 virtual 与已知名称冲突记录；直接继承会把旧混淆带进新系统。不采用。
- 默认开启 ZINC discovery 闭合：discovery 从来不是 actionable 证据，旧库已证明它容易被误读为"原料可得"；默认开启会抬高表观 solved 并稀释证据边界。不采用。
- 照搬旧 AHP 权重作为评分结果：权重从未获专家验证，照搬等于把暂定数字伪装成专家偏好。不采用。

## 影响与风险

- 多数搜索返回 partial：表面能力低于旧库表观数字，这是证据边界诚实的设计结果；汇报与论文叙事不得把 partial/surrogate 写成可执行路线。
- 预算与评分均为暂定：`provisional_not_optimized` 意味着不能宣称已调优；旧 1,053 cell 的结论基于旧基准（depth=5 / branch=3 / nodes=500），不能迁移到当前两阶段配置。
- 分项成本的合成权重（2、5、1）是暂定工程值，不能被引用为专家偏好或化学依据。
- surrogate 闭合依赖候选库存记录的结构与名称质量：虽已排除 virtual 与名称冲突，仍只是 `unreviewed_candidate_stock`，须以 `actionable=false` 向用户显式呈现。

## 复审条件

- 首批 production 审核完成时——出现经人工批准加独立证据晋级的模板或库存，库存与闭合语义需重估。
- 正式盲测（360 cell 合同或其继任定义）启动前——预算、评分权重与对照口径需重新冻结并预注册。
- 候选库存策略被真实使用数据挑战时——例如 surrogate 闭合被用户误读为可执行路线的反馈出现时。

文档形态：TASK-009 由速记体扩写，决定内容未变。
