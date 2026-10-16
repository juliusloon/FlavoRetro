# REPORT-017：历史反应证据与正文/SI补件（2026-10-15）

本轮材料准备已交付；TASK-017整体 **Partial**，execution_status=historical_review_packet_delivered_with_three_deferred_cards。科研门false，科学cell0，C/SS效果null。所有者已明确授权配齐具体反应、正文和必要SI，再由ljx实际核验；本轮批准agent_delegated，human_reviewed=false。

审核入口：[START_HERE](../../outputs/evaluation/task017-evidence-completion-20261015/START_HERE.md)，[离线结构/原文页](../../outputs/evaluation/task017-evidence-completion-20261015/reaction_review.html)，[空白CSV](../../outputs/evaluation/task017-evidence-completion-20261015/human_review.csv)。没有预填实际化学结论或gold。

## 交付与范围

32历史目标/34上下文全部保留：25条主表（C7/糖间18），4条范围核对附录（HIST-14/15/26/30），3条暂缓（HIST-24/27/25）。14篇具名母文献正文PDF均已合法获得并核验，14份必要SI归档（13复用、1新取得），两个ZIP另解出可读PDF。每条主表有受体/GT供体/产物与完整参考、原文段落及明确边界；主表25条覆盖27上下文，不把同一反应的多上下文重复计为新目标。

本轮只处理32历史目标固定来源及一篇引用补证；没有继续扩搜此前48书目。旧30份用户PDF对账、48索引的保留/无效/母文献处置沿用20261013包；当时未定位候选仍保留，不声称48条原件全部补齐。

HIST-02原结构与H7Glu/H7Neo名称/分子式不符：保留旧图，新增PubChem完整图纠正提议（CIDs147394/442439，受体C22H24O11、产物C28H34O15），尚待人工批准；该提议改变目标身份，旧target/评分不覆盖。数据库身份不作为反应证据。HIST-02/17旧MpRhaT与原文Cm1,2RhaT没有已证同义关系，新增来源酶绑定提议而保留原标签。HIST-29只绑定UGT94BY1的25→25a，4h表格与8h底物谱分开，25b/c不回填。

GuApiGT各产品按Fig3b标准品/NMR标记和SI编号逐条对应，不把所有12条统称NMR；9a未有具体标准品/NMR标记，HIST-25暂缓。区分UDP-Api作用供体与UDP-GlcA/UAXS/NAD+全供给体系。C8静息细胞和FcCGT同锅分阶段实例明确列实验边界，实际“单步/完整参考/领域”裁决仍空。4条非黄酮原文对象放范围附录，不能以继承标签冒充领域合格。

## 剩余材料与人工动作

仅就本轮固定来源，仍需Sasaki等2015（DOI10.1016/j.febslet.2014.11.045）的正文PDF及必要SI。出版方Free Access HTML可读；正文直接下载403、实际SI链接经web访问403。本机浏览器控制未接通，没有尝试视觉captcha，没有宣称机构无权限或全球不可得。保留失败响应和访问记录，没有把HTML冒充PDF。

该一手原文§2.5明确UDP-glucose，§3.3有luteolin产物β-C6定位依据，可补GtUF6CGT1历史实例来源；但HIST-24/27待正文PDF和SI归档后再交审。HIST-25缺9a具体位点/立体鉴定资料；该篇正文/SI已经在包内，不要求重复上传，不用其他产物谱图代替。详见[精确补件清单](../../outputs/evaluation/task017-evidence-completion-20261015/MISSING_MATERIALS.md)。

ljx现在可以核验25条主表，在空白CSV/JSON中填写真实正向步骤、原文对应、结构/立体/位点、供体及完整参考、耦合边界、领域及纳入/排除/不足理由。暂缓项不要求提前结论。实际审核也不会消除历史开发曝光；这些条目仍不能直接变成新独立评价面板。

## 验证、预算及边界

421项工程检查通过：14正文的文件头/页数/DOI/SHA，14SI格式/SHA及复用原件一致性，两个ZIP成员精确一致；93原文段落绑定、92正文页绑定、9个新增SI页绑定；全部原图快照保留，32SVG可解析，空白审核字段、三队列计数、本地链接及HTML筛选JS核验通过。RDKit仅作图和编码诊断，不判化学真值。没有可控浏览器的完整交互测试，Fig3b来源图已做针对性视觉核对。

877个现存实质保护文件与旧准备包SHA一致，v2交付manifest未改。旧20261013保护快照另列42个现已缺失AppleDouble侧车；本阶段未删除/恢复，缺失时点不能由本阶段起点快照确认，原列表和第一次失败检查保留在verification-first-attempt.json。不能将该历史辅助文件缺失掩盖成919全量无漂移；科学源件/代码的实质检查无漂移。首轮链接检查把代码块中的SMILES识别成链接，已修正检查器忽略围栏块，真实链接均存在。SS段落键遗漏与源页绑定经子agent指出后补齐，再由主agent逐项核对。

累计输入174/200文件、155,002,911/419,430,400字节；查询15/20；直接HTTP33加5次web调用保守记38/120；直接累计52,175,073字节，web实际wire字节unknown，另预留8MiB，不把预留量冒充实测值。本地命令及全部错误以本轮budget_accounting.json最终快照为准，沿用旧消耗，不退款或重置。范围/预算补充仅见TASK§15，没有扩大方法或科学运行授权。

旧批准、v1/v2载荷和20261013资料包只读；P7停止/旧epochs、R80及Liu2021/R73内容停止保持，中央科学/曝光账不回写。新来源/结构访问角色另记source_access_roles.json；新增引用内容读取也不冒充fresh独立源。算法/模板/MCTS/训练/调参/新scope/新epoch/正式矩阵/发布/Git同步均0。使用nature-downloader技能的合法正文/SI路由及格式核验，技能位于/home/ljx/.agents/skills/nature-downloader/SKILL.md。

## TASK验收映射

G0/G1：本轮有限范围/合法访问/材料准备完成并交付；G2：只交历史核验材料，实际独立标签/闭包/最低panel/最终协议未完成；G3实际research_run_ready=false；G4科学矩阵未执行；G5完成本轮报告与交付校验。AC01/AC10仅本轮授权/证据/报告部分有新增交付，AC02–AC09的正式科学要求未因此完成。preparation_ready=true、panel_ready=false、evaluation_complete=false，legacy formal_run_ready=false、release_ready=false，全部效果指标null，独立gold与fresh目标0。

最终文件SHA清单见delivery_manifest.json；机器摘要summary.json、verification.json、budget_accounting.json及输入清单均保留本地。原始/受限数据不加入Git。
