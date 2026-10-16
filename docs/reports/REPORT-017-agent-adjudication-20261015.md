# REPORT-017：32条历史反应最终代理审核（2026-10-15）

**本轮审核已完成：纳入25（C9/糖间16），领域排除4，证据不足3。无需所有者再逐条审核。** 所有者明确“这不需要我审核啊，你直接就能干掉。直接你审核完”，本次批准及最终裁定均为agent_delegated、human_reviewed=false。不是实际人审、实验重验证或独立gold；TASK-017整体正式评价仍Partial。

[已填写结论表](../../outputs/evaluation/task017-agent-adjudication-20261015/agent_review.csv)、[逐卡理由与证据](../../outputs/evaluation/task017-agent-adjudication-20261015/DECISIONS.md)、[阅读页](../../outputs/evaluation/task017-agent-adjudication-20261015/final_review.html)。机器结果final_decisions.json覆盖32卡/34上下文，保留接受/排除/不足的具体理由和所有来源上下文。

## 最终裁定

| 范围 | 最终结论 |
| --- | --- |
| 黄酮C成键 | 纳入9：HIST-03/05/07/08/19/21/23/24/27 |
| 黄酮糖间成键 | 纳入16：HIST-01/02/04/06/09/10/11/13/17/18/20/22/28/29/31/32 |
| 领域排除4 | HIST-14/15为酚酸，HIST-26/30为benzophenone；真实反应保留，不计黄酮集合 |
| 结构证据不足3 | HIST-12/16/25：GuApiGT的4a/7a/9a，没有该产物专属标准品/NMR闭合具体位点与构型 |

没有删除排除或不足记录。HIST-15/30同时保留产物本身鉴定限制；领域排除不表示否认反应发生。每个accepted卡至少一个充分来源支持规范化GT步骤；HIST-06的GuApiGT、AgApiT、PcApiT三上下文分别审核，未用一条来源替其他来源背书。

## 实际核对与纠正

Cano及三位主审分工实际读取一手XML/PDF/SI、必要结构和图谱：C13上下文、非Gu糖间7卡+2额外上下文、Gu12上下文，合计32卡/34上下文。来源等级区分NMR、标准品、命名/共洗脱/MS与LC-MS范围证据，不把来源总体选择性或某产物鉴定移给其他实例。

1. **HIST-02**：拒绝旧eriodictyol型图，接受原文H7Glu/H7Neo与标准品身份支持的hesperetin完整图纠正（受体C22H24O11、产物C28H34O15）。HIST-02/17来源酶最终采用Cm1,2RhaT；禁止称MpRhaT已证同义。旧图/原target/旧评分保留，代理采用图在新overlay中单列。
2. **HIST-12/16**：上一材料包把4a/7a标为标准品支持，现撤销。Fig3b仅画受体4/7，未列4a/7a产品鉴定标记；SI仅反应与阴性对照、LC/MS。Fig8用Gu自身催化产物作烟草产物比较，不能循环作为独立结构鉴定。与9a一起最终不足。五个本轮涉及的Gu NMR产物分别核对自己的HMBC，不统称12条NMR。
3. **HIST-24/27**：2018一手来源实际产品标准品/实验，加上合法Sasaki2015原文HTML的UDP-glucose、C6/β等依据，足以接受相应规范化历史GT步骤。缺Sasaki正文PDF/SI只是归档格式缺口，不再要求所有者先补档后作科学判断，也不重试403。
4. **HIST-01/11**：现有MOESM2.docx实际只有引物TableS1；应有FigS1的MOESM1 EPS未核验。判决采用正文Fig3实际比较、原文命名/MS等，不宣称读过FigS1。上一阶段“14份SI包括全部必要鉴定附件”的表述过强，现明确纠正。
5. **实验与结构边界**：TcCGT的两个C8实例是静息细胞及细胞内供体体系；完整Fig9定位纠正为正文物理14页。FcCGT两条接受同锅第二GT步骤，有方法/时间过程/产物鉴定，不能改成纯中间体投加的孤立两底物实验。Gu作用供体UDP-Api与实际UDP-GlcA/UAXS/NAD+体系分开；UGT94BY1仅25→25a，4h/8h不混用，25b/c不回填。
6. **保留源内冲突**：HIST-22的SI MS碎片Man/Rha标签冲突保留，以结构/命名/NMR支持Rha，不随错误碎片标签改糖。2018 isovitexin标准差差异保留，不作为新收率或评价指标。UDP-Glc disodium与中性母体及其他盐型/全体系缺项均保留。

C主审随后独立交叉复核SS的HIST02/17及Gu的HIST12/16/25具体论点，亲看原图并核对SI31–33。发现Gu三条证据绑定说明仍残留“产品鉴定标记”的模板措辞；最终overlay修正为无标记，保留原claim、原主审文件和原不足判决。交叉复核仅覆盖这5卡的指定论点，不冒充第二套全量独立科学验证。

## 采用范围与后续门

25条接受仅表示代理文献证据支持相应**规范化历史GT反应**，不表示新湿实验复现、独立人工gold、来源fresh或精确实际试剂/全部组分参考已冻结。本次所有exact_formal_reference_ready=false；不把规范化糖核苷酸图与实际盐型/全体系混为一谈。formal reference冻结和正式科研准入未执行。

所有32卡仍historical_development_exposed、independent_panel_eligible=false；独立fresh目标0、gold新建0、正式科学cell0，C/SS迁移效果null。preparation_ready=true，panel_ready/evaluation_complete/research_run_ready=false，legacy formal/release=false。本次取代历史资料交回ljx逐卡审核的安排，未取代正式独立标签/合格新面板及隔离要求。

G0/G1本轮批准、有限代理审核及资料交付完成；G2仅完成历史源证据裁定，正式独立标签/闭包/最低新面板/最终协议未完成；G3实际科研门false；G4矩阵未执行；G5交付本报告。正式AC02–AC09不因此勾选完成。TASK整体Partial，本轮agent_review_complete=true。

## 核验与保护

820项交付与一致性检查通过：32卡/34上下文守恒与无重复，224证据绑定源文件SHA、90PDF页文本SHA、67XML段落SHA；全部原始/候选图快照保留，HIST02为唯一显式变更目标身份；规范化接受门与精确正式参考/独立性/人审/gold分开。图诊断验证34个受体全立体子图及供体/产物新增糖非端基一致性，未把此诊断当αβ/位点的来源证明。

上一材料包208文件逐字节保持，20261013资料92文件保持，785实质保护文件保持（合计沿用877实质保护检查范围）；旧v2交付manifest和上一报告未改。旧42个缺失AppleDouble侧车不恢复/删除，未知时点保留，不能宣称包含这些侧车的919全量无漂移。原始SI/PDF及所有主审判决文件保留SHA，最终纠正采用overlay。离线页面所有本地链接和JS语法核验；没有全浏览器交互测试，来源特定结构/图谱已视觉核对。

旧人工空白表、旧科学/曝光/epoch账、P7停止与R80/Liu2021/R73内容停止保持。没有新HTTP、查询、下载、外源输入、MCTS/训练/调参/模板/运行时/新scope/新epoch/Git同步/发布；并行TASK019的命令和STATE追加保留且不计本任务预算。

累计命令以budget_accounting.json最终快照为准，上限由TASK§17显式200→280，不重置旧消耗；累计源输入174/200文件、155002911/400MiB，查询15/20、HTTP保守38/120，实测52175073字节另留web8MiB（实际wire未知）。所有失败日志保留；root核验器首轮把非XML绑定当XML解析失败，已按格式分派修正后通过。此前48书目未定位候选未扩搜，不声称旧48原件齐全。

最终文件SHA见delivery_manifest.json；SOURCE_GAPS.md将真正科学不足与PDF/EPS归档缺口分开。原始/受限反应明细与源件均留在Git忽略目录。
