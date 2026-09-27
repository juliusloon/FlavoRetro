# 定向 SciFinder 材料与人工审核 v1

对应 [TASK-015](../tasks/TASK-015-ord-coverage-review-cards.md)。ORD 当前镜像已完整扫描；覆盖实测见 [ORD_COVERAGE_V1.md](ORD_COVERAGE_V1.md)。现有本地导出已含 744 条领域糖苷候选，其中 227 条有芳基 C 连接候选；现在不要求用户重新搜全量黄酮/糖苷。

## 先做什么

用浏览器打开 `/home/ljx/FlavoRetro/outputs/review/task015-v2/index.html`，选择“糖苷重点 30 条”。卡片包含原始两侧结构、收率及来源定位，黄色键仅为拓扑候选。初筛先填写领域相关性、糖苷连接和歧义；没拿到原文时选“保留候选”或“需裁决”，不要填写“具体原文已核对”。确认本步是否形成/断裂糖苷键，必须与“分子存在糖苷连接”分开写。

30 条重点样本中 9 条有 SciFinder 导出实验步骤，其余 21 条没有；所有步骤仍需与原文核对。60 条涉及 47 个文献标题：32 个有保守匹配的 DOI 导航，11 个有原导出专利号，4 个仍需核对文献身份。元数据匹配不是具体化学实例确认。

## 首批定向材料：4 条已有文献

这批目的是补出处/具体实验，建议优先找与卡片底物和产物对应的 scheme/example/化合物号。已有本地反应，无须重复导出整篇所有反应。

| 卡片 ID 前缀 | 文献与入口 | 要补什么 |
| --- | --- | --- |
| 86ecdf66af63 | Glycosyl imidates. 69. Synthesis of flavone C-glycosides vitexin, isovitexin, and isoembigenin；[DOI](https://doi.org/10.1002/jlac.199519950362) | C-糖苷具体实例、位点/异构体、参与物与原始条件/收率定位；当前卡片无导出步骤 |
| 2f1f0ed4b8ad | Biosynthesis of natural and novel C-glycosylflavones utilising recombinant Oryza sativa C-glycosyltransferase (OsCGT) and Desmodium incanum root proteins；[DOI](https://doi.org/10.1016/j.phytochem.2016.02.013) | 酶促实例、供体/受体与位点、产物鉴定证据；与化学合成分开标记，当前卡片无导出步骤 |
| 08db9e0029fb | Synthesis of Kaempferol 3-O-(3'',6''-Di-O-E-p-coumaroyl)-β-D-glucopyranoside, Efficient Glycosylation of Flavonol 3-OH with Glycosyl o-Alkynylbenzoates as Donors；[DOI](https://doi.org/10.1021/jo1014189) | 3-O 糖基化对应具体结构与步骤、供体、保护/脱保护、立体及收率归属；标题差异的元数据匹配不能代替来源核对 |
| 4ab74bb58f03 | Design, synthesis, docking, antitumor screening, and absorption, distribution, metabolism, and excretion prediction of new hesperidin derivative；Asian Journal of Pharmaceutical and Clinical Research (2020), 13(1), 24–31 | 用准确题名/期刊卷期页码定位正文；Crossref 候选的年份与原引用存在问题，DOI 未直接采信；确认此实例是否糖苷构建、后修饰或只是已有糖苷 |

先按 DOI 或准确题名找 References，再定位相关 Reactions 和正文/SI。只需要所列卡片对应的具体实例；材料取不到则记录 unavailable 和原因，不用其他反应或通式顶替。SciFinder 的确切界面/可导出字段由机构版本决定，本 TASK 未登录或验证用户账号能力。

## 如果第一批仍显示真实覆盖缺口

再做小批量（每方向先 5 个具体实例）的反应/结构检索，按实际审核缺口选择：

1. C-糖苷构建：目标 vitexin/isovitexin 与 flavone C-glycoside；区分 6-C/8-C、单/双 C、化学/酶促，要求有明确反应物和产品，而非只提到天然产物存在。
2. O-糖苷位点与立体：flavonol 3-O、flavone 7-O；供体类别、α/β 和保护顺序需有原文，不以泛化结构或数据库身份替代。
3. 糖—糖或苷元释放：在已有糖苷中伸长糖链、选择性水解/脱糖；与不改变糖苷连接的保护、氢化和后修饰对照一起保留。

上述为建议，尚未检索或形成 gold。未来若用于独立 benchmark，还必须排除本地已有论文/专利及家族、笔记/通式变体关联，并在开发前冻结；“新导出”不代表训练或来源独立。

## 你提供材料，我负责什么

优先提供当前 SciFinder 允许合法导出的原始 RDF/RDfile（最好带结构、reference、reaction number、procedure、conditions/yield），不用手工抄 SMILES。无法导出 RDF 时，可提供原始 SDF/反应导出文件及独立的引用/步骤文本；不要把截图当成唯一结构来源。

合法取得的正文/SI PDF 可与原导出一起放到 `data/inbox/scifinder/task015-user/`。保留原文件名，另附一份纯文本检索记录：检索日期、DOI/题名或专利号、查询/筛选方法、命中具体卡片 ID、正文/SI 页码及 scheme/example/化合物号；不提供密码、登录 cookie 或账号令牌。不能获取原文时只提供定位与失败原因即可。

收到材料后由 Cano 负责原始件冻结、SHA-256、字段解析、严格去重、匹配已有卡片并保留重复来源/条件/收率/冲突/零值；新的记录仍作为候选，不自动加入活动 v3 或 production。具体化学结论由实际审核者填写，后续来源/标签接管使用独立版本，不重写 TASK-014 原样本。受限导出和 PDF 不入 Git、不要公开分发。

在卡片中点“保存当前审核草稿”，定期“导出审核 JSON”备份。浏览器存储可能因浏览器/文件地址变化而不同；JSON 是交接载荷。把导出文件放到相同 inbox 并给出路径即可。Cano 会校验样本 ID、源 SHA、来源定位、允许标签和证据完整性；导入/保存只是人工提交草稿，不自动获得 human_reviewed、gold 或科学准入。
