# ORD 覆盖实测与候选接入 v1

核查日期：2026-09-27；对应 [TASK-015](../tasks/TASK-015-ord-coverage-review-cards.md)。此文记录实际下载与机器筛选；TASK-014 的 SOURCE_ACCESS_SURVEY.md 保留当时“仅调查入口”的历史事实。

## 覆盖范围

官方 Hugging Face 镜像 open-reaction-database/ord-data，revision `93475c46949f9218e1dfb6624096025135db2add`。完整无分页目录中的 53 个 Parquet 均已下载，合计 1,256,526,213 字节；逐文件大小与 LFS SHA-256 相符，53/53 完整逐行扫描。包含当前镜像的 HTE/ELN 来源和上游训练/验证/测试分割；不包括 retired_datasets.csv 中退休文件、未镜像版本或非 Parquet 工程 fixture。因此这不是 ORD 历史全库的覆盖率。

数据许可 CC-BY-SA-4.0，许可原文和镜像 README 保存在 data/raw/ord/task015/。原始文件不入 Git，也未进入活动 v3。生成 protobuf 模块来自官方 ord-schema，冻结到 `8ed28a6d7f158dcb84119c843b3ba7d3c4a3d21d` 并校验内容哈希；代码 Apache-2.0。未安装完整 ord-schema、未修改 .venv-foundation 依赖；隔离模块与包版本见 environment/task015-ord-schema.json。

## 实测结果

| 指标 | 数值 | 含义 |
| --- | ---: | --- |
| 来源记录 | 2,428,291 | 含来源/上游处理副本，不是独立实验数 |
| 领域结构候选 | 8,509 | 命中冻结的 9 母核规则 |
| 领域候选严格精确组 | 6,013 | 8,508 个完整候选按两侧结构去重；另 1 条不完整候选保留且不强赋 identity |
| 未命中当前查询 | 2,418,536 | 当前结构表示未命中；不表示化学上范围外或规则召回完整 |
| 无法判断 | 1,246 | 结构/反应侧不完整或解析问题；原始行及失败定位保留 |
| 糖苷候选来源记录 | 78 | 同一连接组分内既有母核又有 O/C/糖—糖拓扑候选 |
| 糖苷严格精确组 | 65 | 不等于 65 个已证实的糖苷生成实验 |
| 与本地试点严格精确重合组 | 3 | 对应 ORD 4 个来源行；不同参与物约定可导致匹配遗漏 |
| 糖苷与本地严格重合组 | 1 | 其余 64 组只是当前表示下的新候选，非独立化学证据 |
| 与 guide 严格重合组 | 1 | 不提升 guide 的来源审核状态 |
| 原文确认 / 人工审核 / production | 0 / 0 / 0 | 本 TASK 只完成工程准备 |

53 个数据集中 7 个有领域候选，3 个有糖苷候选。USPTO 汇总有 6,871 条领域与 69 条糖苷候选；其余糖苷来自上游训练集 8 条、验证集 1 条，不是新的独立实验来源。其他命中来源见本地 datasets.json；来源名称与上游 train/test/validation 标签全部保留，但在本项目均 development_exposed，不能据上游标签宣称盲测独立。

| 糖苷连接候选（记录数，可重叠） | ORD 任一侧 | ORD 产物侧 | 本地试点任一侧 | 本地试点产物侧 |
| --- | ---: | ---: | ---: | ---: |
| 芳基 O | 75 | 53 | 518 | 356 |
| 芳基 C | 1 | 0 | 227 | 227 |
| 其他 O | 17 | 7 | 331 | 157 |
| 糖—糖 O | 14 | 6 | 46 | 17 |

ORD 在本规则下没有产物侧芳基 C-糖苷候选，仅 1 条底物侧存在；这是当前表示/规则的命中结果，不能推断整个 ORD 没有此类化学。本地已存在 227 条芳基 C 候选和 744 条全部领域糖苷候选。因此项目目前更明确的缺口是具体实例、出处与人工标签，不是先扩大 C 候选条数。

领域候选中 6,871 条带专利字符串、6,872 条带导出过程描述、3,983 条带可定位的百分比收率；1 条明确零收率原样保留。这些是数据库字段可用性，不是原文审核。provenance.doi 可能指数据集，而非具体专利/反应；专利家族和具体例号尚未解析。

## 读取、标准化与边界

每行保存 reaction_id 与序列化 protobuf，先使用明确给出的 REACTION_SMILES/REACTION_CXSMILES；缺失时才从 ORD 的 REACTANT 和 outcomes products 中取显式 SMILES。中间 agents、溶剂/后处理不作为反应两侧，CX 扩展仅在结构扫描时省略；原始字节/值保留。数据集中的 2,338,291 条使用反应标识符、90,000 条使用组分回退；不自动修补角色、猜测映射或从步骤文字分配收率。明确组分与反应标识符的一致性尚未全面审核。

严格反应身份去除 atom-map 编号，按两侧片段排序；保留立体、同位素、盐、价态、电荷及重复参与物，不做互变异构或消盐。候选有解析问题时保留信息且 identity 为 null。各母核/类别/连接可多标签，不能相加当作互斥样本数。

规则为 TASK-014 v1，工程冻结、化学 provisional。糖环/连接存在或产物侧出现，均不等于本步形成该键；不推断反应中心、机制、可行性、收率正确性、化学 precision/recall 或训练独立性。USPTO 与项目使用模型的训练重叠仍 unknown；低精确重合不证明来源或训练独立。

## 本地文件与复核

- data/raw/ord/task015/：镜像清单、许可、USPTO 原始文件、下载哈希；current-mirror/ 每个其他数据集各自保存 source.json、原始 Parquet、download.json。
- outputs/coverage/task015-full/ 与 task015-mirror/：逐行扫描的 candidates.jsonl、unknown.jsonl、逐批统计、summary、manifest；全部原始非候选也保存在完整 Parquet 中。
- outputs/coverage/task015-summary/：53 源汇总、严格重合、78 条糖苷候选 JSONL/TSV、输入输出哈希。TSV 在表格软件中应按文本导入。
- outputs/review/task015-v2/：最终 60 卡离线 index.html、summary、manifest 与 4 条定向材料清单；之前 task015、task015-final、task015-ready 保留为开发版本，不覆盖。
- outputs/validation/task015-audit.json、task015-cards-v2/：原始哈希/定位、受保护文件和浏览器验证。浏览器 fixture 标注是隔离的工程测试，不是人工化学审核。

在项目根目录，通过 operate.py 执行 setup_ord_schema.py 重建冻结 protobuf 模块；fetch_ord.py 获取已冻结 source.json 指定文件；scan_ord.py --source <manifest> --output <全新目录> --workers 4 完整扫描。批量当前镜像入口 survey_ord_mirror.py，已有扫描输出拒绝覆盖；重放需要新路径。汇总入口 summarize_ord_coverage.py，审核卡入口 build_review_cards.py --references outputs/review/task015/references-v3.json --output <全新目录>。公网文献元数据会变化，卡片重建用本地冻结 references-v3.json；不在重放时重新查询。

官方入口：[ORD 镜像冻结版本](https://huggingface.co/datasets/open-reaction-database/ord-data/tree/93475c46949f9218e1dfb6624096025135db2add)、[ORD 数据仓库](https://github.com/open-reaction-database/ord-data)、[冻结 schema 源码](https://github.com/open-reaction-database/ord-schema/tree/8ed28a6d7f158dcb84119c843b3ba7d3c4a3d21d)。

完整镜像重放时给 survey_ord_mirror.py 提供新的 --output-prefix 和 --download-index；summarize_ord_coverage.py 使用对应 --mirror-index、--uspto-output 和新的 --output。默认既有路径在任何下载/索引写入前拒绝，防止覆盖原始运行证据。原始 Parquet 可哈希核对后复用，不必重复下载。progress.json 为过程快照，完成状态见 summary/manifest。最终卡片 task015-v2 修复浏览器持久存储受限时仍保留本页草稿并能导出备份；v1 与早期重放保留。
