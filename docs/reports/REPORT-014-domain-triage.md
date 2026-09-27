# REPORT-014：领域反应筛选与科学评测协议（含本地试点）

## 对应任务

- TASK：[TASK-014-domain-triage.md](../tasks/TASK-014-domain-triage.md)。
- 日期：2026-09-27；执行者：Cano；批准：所有者本会话“同意执行 TASK 14，开始”，human_direct 工程与方案执行授权。
- 结论：**Completed（合同范围完成）**。覆盖黄酮相关转化总分类，以糖苷为重点审核子集；规范、离线试点、审核包、重放与回归验收已交付。此结论不代表人工化学审核或正式科研评测完成。
- 基线/当前提交：main / fab9659b10dfd89ca348d48dc855fd9ac1a91092；本任务未创建 Git 提交，未同步远端、未触发 CI。

## 实际改动与文件职责

| 目录 | 文件 | 改动与用途 |
| --- | --- | --- |
| flavoretro | triage.py | 新离线筛选模块：只读验证、分子描述与精确反应复用、guide、结构候选、排序、来源和防泄漏组、审核样本及清单；不进入 MCTS |
| scripts | triage_reactions.py | 新审计入口，必须使用 outputs/triage 下不存在的新目录；经 operate.write 登记所有输出写入 |
| configs 与 assets/configs | domain_triage.json（双处） | 9 个母核查询、7 项总分类、语境词、优先级、抽样名额；两份逐字节一致，工程冻结、化学 provisional |
| tests | test_triage.py | 新增 11 项合同：O/C 分离、非领域/不同连通片段对照、橙酮羰基位置、失败保留、组分/映射/立体身份、无变化控制、泄漏传递、变体分组、抽样唯一性和拒绝覆盖 |
| docs/protocols | README、DOMAIN_TRIAGE_V1、ANNOTATION_EVALUATION_V1、SOURCE_ACCESS_SURVEY | 总分类、guide 身份、独立标注/评测与防泄漏规范、官方来源接入调查、命令和产物导航 |
| docs/tasks、reports | TASK-014、REPORT-014；README | 批准合同、执行事实与索引 |
| STATE、ARCHITECTURE、docs/README、两份 ROADMAP | 当前状态和交叉指引 | 登记本任务完成与后续人工任务，保留既有 TASK-013 及路线改动 |

生成载荷不入 Git：outputs/triage/task014-final 为最终交付，task014-replay 为独立重放，task014-v1 为保留的首轮开发输出；outputs/validation/task014-audit.py 与 task014-audit.json 为独立复核代码和结果；operations/task014-baseline.json 为受保护输入/代码/UI 基线。

## 试点结果

| 观察 | 数量/状态 | 解释 |
| --- | ---: | --- |
| 笔记 guide 原记录 | 508 | 原 ID、raw、历史处理/变体、失败及产率保持原样 |
| 具体笔记例子候选兼粗模式 / 仅粗模式 / 仅上下文 | 122 / 132 / 254 | 这是 guide 用途，不是事实真实性分级；全部未经本轮来源审核 |
| 笔记 token 命中 / 未命中 | 249 / 259 | 重新核当前 MD，同时保留 reported_line 和实际 token 行号 |
| guide 历史变体/处理风险 | 258 | 不继承历史 manual_review 或 confidence |
| guide 组件失败记录 / 上下文收率未归属 | 5 / 64 | 留作审核，不改写成具体实验或自动填收率 |
| SciFinder 试点来源记录 | 2,301 | 全部进入结果；来自 9 组历史检索，不代表无偏化学总体 |
| 精确反应组 / 首记录以外的重复来源 | 1,444 / 857 | 独立重算一致；不同条件、收率、出处不被合并 |
| 完整可解析 / 结构不完整或泛化 | 2,245 / 56 | 56 条保留在完整队列与失败抽样层，不被删除 |
| guide_supported | 1,289 | 粗母核/糖苷家族 signature 支持，不是化学证据 |
| outside_guide_structure | 654 | guide 未覆盖的领域结构候选，保持发现空间 |
| low_or_unknown | 358 | 当前规则未命中或无法判断；不当作真实负例 |
| 领域糖苷候选（含不完整行） | 744 | 结构观察，不是已验证的糖基化反应 |
| 防泄漏连接组 | 612 | 当前全部 development_exposed；文献身份和专利家族未独立审核 |
| 审核包 | 60 | 30 条糖苷重点、20 条其他领域、5 条低/未知、5 条不完整/失败；人工字段全空 |
| 独立标签 / 盲测记录 / production | 0 / 0 / 0 | 未产生科学晋级 |

结构分类为多标签，不能将各类数量相加当作总数。规范化精确身份包括组分多重性、方向、立体、同位素和电荷，map 编号只在身份键中去掉；原始字段保留。不去盐、不补映射、不推断反应中心。

本轮全部 2,809 条记录合计仅进行 1,943 次唯一反应分类、2,716 次分子描述；同一标准化反应/分子复用计算，来源记录分别保留。本轮无神经推理或模型训练。

两策略 top-60 重合 21 条；按机器拓扑候选计，结构基线 top-60 有 60 条糖苷候选，guide 排序有 59 条。guide 改变排序位置不证明排序更好，粗 signature 也不能表示机理/供体/条件相似。precision、recall、accuracy 均为 null，未声称算法或化学优越性。

产率保全：试点 1,734 条 numeric、567 条 missing，真实 value=0 的记录为 0 条；没有从空值生成零。原记录逐字段相等核查覆盖全部输入，既有 zero≠missing 合同测试也通过。

## 本地产物结构

- guide.jsonl / pilot.jsonl：508/2,301 条输入全文快照与附加机器字段，不改活动 v3。
- queues.json：两个策略全部排序与三队列；duplicates.json：完整来源成员关系。
- leakage-groups.json：来源/精确反应/父变体的传递分组，全为开发暴露数据。
- review.jsonl / review.tsv：60 条开发校准样本，机器列与空人工字段分开；审核须复制到新的版本目录，冻结输出保持只读。
- rules.json / summary.json / manifest.json：规则、观察和逐文件哈希；README.md：目录责任与使用边界。
- audit.ipynb：标准库统计核查，实际执行其代码单元通过；不确认化学真值。

关键绑定：records_sha256=448dbbdcd511df0aade80903d33abc34707fdcc2d529d3ecb29dbae94898192e；rules_sha256=df9650edb49e1af328720845bd9e78c918320a3e199431cd84946aee63e3deae；triage_code_sha256=a6f8d9a443cda7c6d00a1f43c1ff6920593646de18ce1b8dac18c437cfbcd50e。manifest 还绑定 topology 代码、来源清单、RDKit 版本及所有输出载荷。

## 验证证据

| 操作 | 实际结果 | 证据 |
| --- | --- | --- |
| 首轮构建 | 成功；后按精确标准化反应复用完善，首轮目录保留 | command-0221.log，task014-v1 |
| 新增专项测试 | 11 项通过 | command-0224.log |
| 最终构建 | 全量 508 + 2,301；60 个审核样本，各层零短缺 | command-0228.log，task014-final |
| 本地全量回归 | 62 项全部通过，0 跳过，包含既有 live MCTS；10.029 秒 | command-0229.log |
| 独立重放 | 12 个文件（含 manifest）逐字节一致 | command-0230.log；task014-replay |
| 独立审计 | 不导入 triage 实现，重新计算规范化反应组、分数算式/计数、全量输入保全、队列/样本/清单/笔记定位和哈希；141 个受保护文件不变 | command-0233.log；outputs/validation/task014-audit.py、task014-audit.json |
| 科学 preflight | formal_run_ready=false、release_ready=false；template/stock production 投影均 0；四项科学条件未闭合 | command-0235.log |
| PubChem 只读核对 | CID 10680 与 6537099 属性读取成功，两项母核查询匹配返回结构；不是反应审核 | command-0231.log |

后续收口核查的 diff、相对链接和输入保护结果写 outputs/validation/task014-closeout.json；操作日志继续追加，不声称工作区绝对干净。无失败构建被覆盖；RDKit 常规孤立氢警告保存在日志。

## 独立标注与正式评测边界

已冻结总分类、字段、配额、策略和防泄漏规则 v1；化学定义待校准。当前样本只用于开发校准，正式独立标注须隐藏机器建议。当前全部输入被开发使用，不能直接充当未见盲测；规范要求论文/专利/变体/精确反应分组，并注明训练数据重叠未知。

评测分成领域筛选、糖苷连接诊断与 MCTS 三层。TASK-015 负责审核者、独立 gold 和校准；TASK-017 才冻结目标/种子/预算/指标/统计合同。当前规范交付不等于 release.evaluation_protocol_review 已获科学批准。

官方来源调查见 [SOURCE_ACCESS_SURVEY](../protocols/SOURCE_ACCESS_SURVEY.md)：ORD 格式/许可、Reaxys 单独数据许可、CAS 年代较早的官方认证文档、EPO 专利入口；Europe PMC 正文读取 403 保留为未验证，PubChem 仅核两个属性请求。机构权限、批量配额和外部黄酮覆盖未验证，未下载外部反应库。

## 与合同的偏差与已发现问题

范围无扩张。为了保留审核可用性，除 JSONL 另导出 TSV；为满足复核附加 audit.ipynb 和本地独立审计脚本，均属于原审核/验证范围。未建设审核 UI。

当前规则只做母核/糖苷拓扑集合和有限语境，不支持原子映射反应中心、供体/条件匹配或独立机制分类。部分母核互相包含，类别是候选多标签。现有 9 组检索偏糖基主题，全域覆盖仍未知。专利家族和文献身份只建立分组线索，未做独立解析。固定配额样本不可作为总体准确率的概率估计。

零 production、一手来源、供应证据、独立标签和正式 benchmark 状态均保留。旧目录未运行代码或执行写入；本次只核查项目已准入的 123 个本地来源，不能写成新的全旧目录完整性审计。

## 仓库与 CI 状态

本任务未提交/推送，HEAD 保持基线；本地 62 项测试通过不等于远端 CI。保留 TASK-013 UI/脚本/文档的既有未提交修改，未清理 .workbuddy、AppleDouble 或 staging 文件。原始与受限载荷继续位于 Git 忽略的 data/outputs 下，生成文件不加入索引。

## 建议的下一任务

TASK-015：按本协议批准首批独立审核/开发 gold。先以 60 条校准包核查来源、具体实例和领域相关性，优先处理 30 条糖苷重点；再选择独立保留的评测来源。若扩大来源，另立有版本/许可/训练重叠检查的 ORD 子集接入任务。当前不自动进入 TASK-015、P2 搜索接入或正式 benchmark。
