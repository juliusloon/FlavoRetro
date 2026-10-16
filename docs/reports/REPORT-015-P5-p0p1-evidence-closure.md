# REPORT-015-P5：P0/P1 证据最终裁决

任务合同：[TASK-015-P5-p0p1-evidence-closure.md](../tasks/TASK-015-P5-p0p1-evidence-closure.md)。**Completed（2026-10-05）**。所有者明确要求直接采纳代理结论、取消重复人工审核；以 `agent_delegated` 记录此授权，已有真实人审溯源保留。所有对象已定案，后续不需要提交审核 JSON、样本表或身份签字。

## 最终结论（2026-10-05；替代下方历史人工交接要求）

最终产物：`outputs/evidence/task015-p5-final-v1/`，含 60 卡来源/产率裁决、508 条笔记定位裁决、2 组名称裁决、51 条身份裁决、49 条供应裁决、支持子集与 manifest。它是独立、哈希绑定的裁决覆盖层；**搜索运行时尚不消费该层**，不回写 v3、原始记录或历史审核包。

| 对象 | 最终决定 |
| --- | --- |
| 60 卡结构/分类 | 保持已有 **53 development gold + 7 excluded**；采用此前人审与代理审核，不新增虚构人审 |
| 53 条保留卡的来源 | 9 原文实例已核、9 导出实验段支持、30 仅书目/摘要、3 来源冲突、2 不可得；后三类保留结构结论，否决来源已验证声明 |
| 产率正面子集 | 卡 4/30/32/33/41/45 分别为 **96、38.11、72、86.96、73、91.9%**；卡 45 保留 ±5.2 与 HPLC 方法。数据库取整值不覆盖原文；卡 6 原文 **>99%**，不能证实导出的严格 100 |
| 508 笔记 | **242** 原位置 token/两侧组分一致，**1** 再定位规范化且逐组分确认，**7** 解析失败不准入精确反应，**258** 未定位到同一反应、不作正面来源证据；原记录全保留 |
| 名称冲突 | 实际 **2 组/4 ID**；无第三组冻结记录，“3 条”旧文案改正。narirutin/isonaringin 为同结构别名；两条 UDP-arabinose 名称指派均隔离 |
| 49 库存/2 模板 | 45 编码库存候选保留；4 名称与结构冲突的声明隔离；2 模板保留候选、不认证原文合成验证 |
| 供应证据 | 19 历史目录线索、25 内部片段未有精确供应、4 名称错配供应声明否决、1 母体糖替代声明否决；**0 条当前精确库存供应已认证** |
| 盲测准备 | 预注册协议草案已交付；没有独立盲测集、没有正式运行；本批开发资料不能改名作 blind |

来源/产率子集采用 P1 已有原文核对结果，本轮没有重新逐篇读取或下载论文/SI。没有原文的记录采用最终“未验证/冲突/不可得”结论，不再转成人工待办。

### 本轮补充身份核对与旧结论更正

公开 PubChem PUG REST 核对冻结于 `outputs/evidence/task015-p5-final-input/`：26 CID 属性、23 个库存名称查询全部返回，另有 TBSCl 对照。核对发现 **CID/分子图一致不保证名称正确**：

- `TBSCl` 的编码图/CID 6397 是 TMSCl（C3H9ClSi），声明的 TBSCl 为 C6H15ClSi、CID 28928；隔离该名称/供应对应。见 [PubChem TBSCl](https://pubchem.ncbi.nlm.nih.gov/compound/Tert-Butyldimethylsilyl-chloride)。
- `naringenin` 的编码为 C9H8O5、缺少 B 芳环，与名称所指 C15H12O5 不符；隔离该名称/供应对应。见 [PubChem naringenin](https://pubchem.ncbi.nlm.nih.gov/compound/439246)。
- `2,4-dihydroxy-6-methoxyacetophenone` 的图为乙酰基邻位甲氧基、两个间位羟基；与声明的羟基位点不符。`neohesperidose` 图中第二糖的受糖位点为 C4，不能对应其应有的 (1→2) 连接；均隔离名称声明，公开名称查询的对照图与原图分别保存。
- UDP-arabinose 两条记录并非只需二选一：其同一编码图中含两个五元糖环，二磷酸仅一端有 P-O-C，另一糖经 C-C 接核糖侧链；不是常规 UDP 糖的两端 O-磷酸连接。即使 CID 3082070 同图、同式，也不能证明名称。两条均隔离；保留正确连接的 [UDP-L-arabinose CID 644105](https://pubchem.ncbi.nlm.nih.gov/compound/644105) 作对照，不静默替换立体结构。
- [PubChem Narirutin](https://pubchem.ncbi.nlm.nih.gov/compound/Isonaringin) 明确列 Isonaringin 为别名；覆盖层统一为 narirutin，原 FGM ID 均保留。
- C6H12O4 的历史 quercitrin 片段不同于 C6H12O5 鼠李糖，不能声称“母体糖供应覆盖”。原 vendor 汇编没有逐条产品 URL/快照，因此目录线索未晋级当前精确供应认证；旧“薄市场”也不等于供应已验证。

笔记更正：项目锁定 RDKit 2023.9.6 对 entries 491/492 也解析失败，故最终 **242+7** 替代旧预筛 **244+5**；同时以组分多重集合复核，保留重复组分与立体化学，不使用模糊相似度作为证实。

### 最终验收

- 确定性重放通过：9 个最终文件逐字节一致；manifest **63 个输入/输出哈希**核验全部通过。
- **50 个受保护文件零漂移**，含 v3、active/release、gold-v1、原所有者提交、旧卡与 P0/vendor/handoff 文件；未修改 MCTS 或搜索资源。
- 全量既有 **82 项测试通过**（项目 Python 3.10/RDKit 2023.9.6）；逐卡来源/产率边界、六个原文数值及 HPLC 不确定度核对通过。
- 全部裁决标记 `reviewer_type=agent`、`owner_adopted_conclusions=true`、`further_owner_review_required=false`；新造人审数 0。既有 38 张所有者提交及 22 张委托记录保持原样。
- `metadata/release.json` 和 formal 门未翻转：当前供应与独立盲测不足是实际证据结论，取消重复审核不能替代这些证据。TASK-016 范围与批准不变，本轮未启动。

## 2026-09-29 历史材料交付

下方保留当时的构建、浏览器核验与待回填方案，供追溯；其再次人工审核要求已被上述授权与最终裁决取代。

## 阶段 A：60 卡两轴审核包（handoff-v3）

`outputs/review/task015-p5-axes/handoff-v3/`（packet_id `task015-p5-axes-handoff-v3-5e2d24e1da43`，由 6 个输入哈希派生）。60 卡逐卡包含：结构 SVG（复用 task015-v2 载荷）、引用与 reference 状态、**已冻结的结构/分类轴结论**（gold-v1 / excluded 徽章，53+7）、来源等级徽章、P1 代理定位线索（DOI 链接 / 本地文件 / 证据段）、P1 代理收率评估（reported/status/reason，明确标注 agent）、缺口表提示，以及空白所有者字段 `ps_status / ps_locator / evidence_excerpt / ps_sha256 / yield_status / yield_value / notes`。

- 每卡来源路线分布（来自 P1 + 缺口表）：9 `primary_instance_verified`（agent 上下文）、9 `export_procedure_supported`、34 `bibliography_or_abstract_only`、4 conflict、4 unavailable；23 处 DOI 链接、6 处本地文件引用、46 卡有定位提示。
- 校验规则：亲核必填定位+原文关键句；收率核对必须先亲核原文；「不可得」必须写尝试路线；SHA-256 格式校验。
- 验收：两次构建逐字节一致；无头 Chromium（Playwright 1.63/Chromium 1243）17 项检查全过——渲染、60 卡、三类校验拦截、保存→进度、localStorage 重载恢复、envelope 绑定（packet_id+6 源哈希+60 记录顺序）、**错 packet_id 导入拒绝**、合法导入回灌、1440/390 双视口零横向溢出、JS 错误 0（`outputs/validation/task015-p5-browser/check.json`）。说明：本环境无托管 IAB 后端，文件选择器路径以 Playwright `set_input_files` 驱动，代码路径与 handoff-v2（P3 已核验）相同。

## 阶段 B：P0 遗留三包（`outputs/evidence/task015-p5-p0/`）

**B1 内容预筛（249 条 token 命中）**：口径与准入对齐（`flavoretro/resources.py` 的 `raw_reaction_smiles` 逐字子串定义），逐条重验：token 仍在定位文件中（249/249）、实际行 vs 上游报告行、RDKit 规范化两侧集合 vs 记录 components、条件文本在场。结果 **244 条 `consistent_at_reported_line`**（token 在报告行、化学一致）、**5 条 `parse_failure`**（entries 3/9/52/195/221：通式占位符 `[X]/[Y]`、离子型产物 `[O+]…FB(F)F`、非标准环闭合写法——程序无法独立确认，自动并入所有者样本）。冻结笔记文件对 `metadata/sources.json` 零漂移（脚本内置漂移即停检查，未触发）。

**所有者样本表**：`owner_sample30.tsv`，固定种子 **20260929**（先于任何人审核登记）抽 30 条 + 5 条 parse_failure 自动并入，共 34 行；代理结论列与所有者空白列分离，`reviewer=Cano/agent-prescreen`，不填任何 human_reviewed 字段。

**B2 再定位（259 条未命中）**：在全部 5 个文献笔记文件内做规范化反应检索 + difflib 模糊：1 条 `canonical_found_in_located_file`（准入时逐字匹配失败但规范化相同反应实际在定位文件中——准入判定偏严的实例）、133 条 `fuzzy_candidate`（top 相似度 ≥0.6，带行号与候选原文）、125 条 `no_candidate`；另有部分记录本无定位文件（note_missing）如实保留。

**B3 名称冲突决议表**：`name_conflict_decision.md` + 证据 JSON。冻结数据共 **2 组** duplicate_names、涉 4 个 FGM ID：组 1 narirutin（FGM-0003）vs isonaringin（FGM-0014），同 CID 442431、同 InChIKey（同义词合并型）；组 2 UDP-arabinopyranose（FGM-0155）vs UDP-arabinofuranose（FGM-0156），同 CID 3082070、同 InChIKey 但名称断言不同环大小（吡喃/呋喃）——真实化学身份歧义。**对账**：TASK-003 起冻结数据即 2 组；后续文档「3 条名称冲突」未见第三组，登记为表述差异待所有者确认。每组给出 A 合并 / B 独立标注 / C 否决 三选项。

## 阶段 C：盲测集预注册协议（Proposed）

`docs/protocols/BLIND_BENCHMARK_PREREGISTRATION_V1.md`：独立性定义（标签由所有者/文献双源产生，代理不得产生 gold 标签；与 2,301 导出/60 卡/635 RDF/47 文献/508 笔记四层重叠排除；ORD 上游训练来源不采用）、来源路线（SciFinder 所有者导出为主、EPO OPS 备选需先注册）、**Q1–Q5 预登记检索式**（3-O/7-O/5-O 糖基化、C-糖苷构建、脱糖、糖链伸长，规模建议 ≥30 实例、糖苷重点 ≥50%）、到达即哈希冻结→代理仅结构层→所有者标注→panel 冻结的机制、与 preflight 四字段的对应关系。**本协议不构成盲测集，TASK-017 须另批。**

## 阶段 D：身份包与供应商带日期核查（`outputs/evidence/task015-p5-vendor/`）

D1：49 库存 + 2 模板身份包（名称/SMILES/InChIKey/CID/promotion 状态/历史 listing 引用）+ `identity_review.tsv` 所有者工具表；22 条供应商记录登记为 historical 上下文（与库存名交集仅 5，均为糖供体历史导出）。

D2：**49/49 全覆盖**（2026-09-29，公开目录 Web 检索，美国区结果，未登录、未绕权限；价格仅录公开页面所示，非报价）：

| 结论 | 条数 | 说明 |
| --- | --- | --- |
| commercial_listing_found | 18 | 常规试剂/黄酮苷元，Sigma/TCI/Fisher 等在售（含目录号与所见价格） |
| specialty_found / mg_scale / thin | 4 | neohesperidose、rutinose（mg 级标样）、hesperetin chalcone、2,4-二羟基-6-甲氧基苯乙酮（薄市场） |
| covered_by_parent_sugar | 2 | α-L-吡喃鼠李糖、quercitrin 鼠李糖片段（CID 核实为糖片段） |
| not_commodity_internal_fragment | 25 | 内部桥接/保护片段（16 sugar_gap + 8 protected_rhamnose_leaf + 1），无外部商品身份，核查不适用 |

身份核查附带发现（供所有者身份人审参考）：isovanillin 正确 CAS 621-59-0、phenyl acetate 正确 CAS 122-79-2、2,4-dihydroxy-6-methoxyacetophenone 正确 CAS 3602-54-8（90-24-4 是 xanthoxylin，不同化合物）；naringenin 库存缺 CID 证据且市售分外消旋/S(-) 型；hesperetin 供应商页立体形式表述不一（± vs 单一对映体）；2,4,6-三羟基苯乙酮市售多为单水合物。**本阶段不声称 `current_vendor_evidence=approved`。**

## 边界与并行任务

0 production；未触碰 MCTS/搜索/v3/active/release.json/task014-final/gold-v1/所有者提交原件；未翻转 preflight 任何字段；原始/受限数据未入 Git。回传后的动作（两轴 gold 扩展冻结、名称冲突处置、release.json 字段变化）全部留待所有者决定。

并行说明：同日并行会话立项 TASK-016（开放数据模板扩展， Approved）并提交了 TASK-015-P4/gold 冻结（3361c07/993b22f）；其合同明确「TASK-015-P5 等既有工作不纳入本轮」，与本任务无文件冲突。TASK-015-P5 编号沿用我方会话对 016—018 预留的判断，编号说明已写入合同。

## 验收核对

- [x] A：60/60 卡可执行路线或 unavailable 登记；确定性重建逐字节一致；浏览器 17 项检查全过、JS 0
- [x] B：249+259+决议表交付带 manifest；30 条样本以登记种子（20260929）先于审核抽出；代理结论与所有者列分离
- [x] C：协议+检索式以 Proposed 交付，文本明确不构成盲测集
- [x] D：49+2 身份包交付；49 条核查逐条带 retrieved_at；未声称 approved
- [x] 全部写入/命令经 scripts/operate.py 记录；全量 82 项测试通过（unittest discover，OK）；受保护基线零漂移（git status 仅新增本任务文件与并行任务改动）
