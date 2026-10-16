# 盲测集预注册协议 v1（BLIND BENCHMARK PREREGISTRATION V1）

状态：**Proposed**（TASK-015-P5 阶段 C 交付物（原编号 TASK-019）；等待所有者批准。批准前不得按本协议导出、冻结或标注任何材料）。本文件只预注册规则与检索式；**不构建、不包含任何盲测数据**。盲测的实际冻结与执行属 TASK-017，须另行所有者批准。

对应路线：[PAPER_ROADMAP](../PAPER_ROADMAP.md)「阻断性缺口」之 `independent_chemical_labels: not_available` 与 `formal_benchmark: not_executed`；阶段计划 P2（预注册正式评测）。

## 1. 独立性定义（先于任何数据接触锁定）

1. **标签独立**：panel 每条实例的 gold 标签（底物/产物身份、断键位置、糖苷连接变化、反应类别、收率归属）由**所有者亲核或文献双源**产生；Cano/agent 不得产生、修改或预填任何 gold 标签字段。代理只能做结构解析、规范化、去重等**非标签**工程层。
2. **开发隔离**：panel 实例不得与下列开发材料重叠——TASK-014 的 2,301 条本地导出与 60 条开发样本、TASK-015 的 60 卡及其 47 个文献标题、P2 的 635 行 SciFinder RDF（508 严格结构/327 重叠）、v3 的 508 条笔记反应。排除检查按 leakage_group、InChIKey、Murcko 骨架与文献身份（DOI/专利号）四层执行，检查结果入 manifest。
3. **上游训练不独立**：ORD/USPTO 及其衍生集合曾用于模板模型训练，不得作为盲测来源（沿用 TASK-015 结论）；Reaxys/SciFinder 导出内容的训练重叠状态按记录登记 `training_overlap_status=unknown`，除非有可核实的排除证据。
4. **时间隔离**：检索式在下方预登记并随本文件冻结；所有者导出应在本协议批准后、后续开发动工前进行。导出批次的接收、冻结与解析顺序见 §4。

## 2. Panel 来源路线

- **主路线（已验证通道）**：所有者在机构 SciFinder 中按 §3 检索式检索，合法导出原始 RDF/RDfile（带结构、reference、reaction number、procedure、conditions/yield），放入 `data/inbox/scifinder/task017-blind/`。不手工抄 SMILES；不可导出的实例提供定位与失败原因，不用其他反应顶替。
- **备选路线（需所有者先行注册）**：EPO OPS web services 取专利实验实例。该路线在本项目尚未验证（SOURCE_ACCESS_SURVEY 仅确认入口存在）；启用前需一个单独的接入核查步骤与所有者的 API 注册。
- **不采用**：ORD 及其衍生集合（训练重叠）；任何“上游 benchmark”数据集；本地笔记或既有导出的变体。

## 3. 预登记检索式（SciFinder，冻结于本文件）

以下检索式一经批准即冻结；执行时的界面差异与命中情况如实记录，不因命中过少/过多而改写检索式——不足时另立补充协议再登记新检索式。

| 编号 | 方向 | 检索式要点 | 边界 |
| --- | --- | --- | --- |
| Q1 | 黄酮醇 3-O 糖基化 | 反应检索：kaempferol/quercetin 母核 3-OH + 糖供体（溴糖/三氯乙酰亚胺酯/糖基 o-炔基苯甲酸酯） | 要求具体反应物与产物实例；排除只列天然产物存在的记录 |
| Q2 | 黄酮 7-O / 5-O 糖基化 | 反应检索：apigenin/luteolin/naringenin 7-OH 选择性糖基化 | 记录保护/脱保护顺序；区分位点选择性声明与实际证据 |
| Q3 | 黄酮 C-糖苷构建 | 反应检索：vitexin/isovitexin 6-C/8-C 构建（化学与酶促分开计数） | 位点/异构体须有原文证据；酶促实例标注 donor 类别 |
| Q4 | 糖苷水解/脱糖 | 反应检索：黄酮 O-糖苷选择性脱糖（酶法/化学法） | 与不改变糖苷连接的后修饰区分 |
| Q5 | 糖链伸长 | 反应检索：rhamnosyl/glucosyl 二糖苷（rutinose/neohesperidose 型）构建 | 保留重复来源与条件，不合并证据强度 |

规模建议（provisional，最终在 TASK-017 合同确定）：每方向 ≥6 个具体实例、panel 总量 ≥30，糖苷重点 ≥50%；另留 ≥10% 实例作为重复来源对照（同一实例多出处，不并入统计）。

## 4. 到达与冻结机制

1. 到达即冻结：`data/inbox/scifinder/task017-blind/` 内每个文件到达时计算 SHA-256 并写入 `outputs/blind/task017-blind/inbox-manifest.json`（到达顺序、字节、哈希），原始件此后只读。
2. 代理工程层：解析、结构规范化、严格去重、与 §1.2 开发材料的四层重叠排除；产出 `panel-structures.jsonl`（无任何标签字段）。
3. 标签层：所有者按 [ANNOTATION_EVALUATION_V1](ANNOTATION_EVALUATION_V1.md) 的字段口径逐条标注；文献双源引用记 DOI/专利号与定位；代理可代录所有者口述结论但须保留 `agent_transcribed` 溯源，不冒充亲填。
4. 冻结 panel：标签齐后生成 `blind-panel-v1`（manifest 绑定结构层与标签层哈希）；此后任何修改都产生 v2 并保留 v1。评测执行（TASK-017）在 panel 冻结与 preflight 通过后才开始。

## 5. 与 preflight 的关系

本协议获批并按上述机制产出冻结 panel 前：
- `independent_chemical_labels` 保持 `not_available`；
- `evaluation_protocol_review` 需所有者对本文件及 ANNOTATION_EVALUATION_V1 的评测口径作出批准后才能置 `approved`；
- `formal_run_ready` 在四项全通过前保持 false。代理不代行任何字段翻转。

## 6. 局限声明

- SciFinder 导出的训练重叠状态 unknown；盲测结论的适用范围限于“黄酮/黄酮苷糖苷化变换”的限域问题，不外推通用逆合成性能。
- 机构检索行为本身引入选择偏差；报告中须如实描述检索式与筛选痕迹。
- 本文件是预注册，不是评测结果；任何在 panel 冻结前接触实例标签的开发行为都应登记为 development_exposed 并触发补 Freeze。
