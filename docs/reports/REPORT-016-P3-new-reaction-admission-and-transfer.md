# REPORT-016-P3:新反应准入与 C/糖间迁移证据扩充

**任务**: [TASK-016-P3](../tasks/TASK-016-P3-new-reaction-admission-and-transfer.md)
**日期**: 2026-10-07
**整体状态**: **Partial**(工程 Completed、新反应准入 Completed、C 迁移未执行(null)、糖间迁移未执行(null))
**执行授权**: agent_delegated(G0 登记,合同 SHA `1dfcda3a91d857cef0a867811b67c0f6ebb8906d9e6b6664abf1f323f05b4479`)

---

## 开头回答(合同报告要求)

**1. 新准入多少,其中实际可运行多少?**
新准入 **34 个不同共价反应(C 成键 12、糖间成键 22)**,全部具备完整单步身份(受体/供体/成键位置/异头构型)与逐字证据绑定,远超合同 ≥16(C≥8、SS≥8)硬线。其中 **3 个反应经结构编码成为 v4 可运行模板的能力支持**(C:2-羟基黄烷酮 C3-葡萄糖基化 2 个受体;SS:鼠李糖 1→2 与 1→6 各 2 个受体,7 个 build 实例,52 个准入上下文中其余为多来源同反应上下文,完整前体参照见 reaction_records)。

**2. 相对当前 v3 新增哪些候选能力?**
显式默认关闭的 **v4**(flavoretro/glycoside_library_v4.py + configs/glycoside-library-v4.json + 包副本)链式继承合格 P2/v2 v3 载荷(54 模板逐字节保持),新增 3 个范围模板:
- `C_hydroxyflavanone_C3`:2-羟基黄烷酮 C3-β-D-葡萄糖基化(来源 PMC9563126/PMC6036675/PMC7060329;3 个支持实例,2 个不同完整受体);
- `rhamnoside_glucoside_O2`:黄酮苷葡萄糖 moiety 2″-O-α-L-鼠李糖化(来源 PMC13084081;2 个支持实例);
- `rhamnoside_glucoside_O6`:6″-O-α-L-鼠李糖化(来源 PMC13084081/PMC9706480;2 个支持实例)。
每个范围 ≥4 条预登记边界测试,12/12 全部干净(错误供体/异头失真/1→4 与 1→2 错位/半乳糖母糖/香豆素非黄酮/错糖供体全部拒绝)。v4 守卫自带 aliphatic C3 结构检查与 1→6 环外位点检查(冻结拓扑审计器不分类这两类中心,见模板 derivation 记录);未修改任何冻结代码。

**3. C/SS 各多少独立目标/出处补回?**
**留出面板未形成,补回为 0**。闭包隔离后全部 34 个新反应中仅 3 个为留出资格:C 1 个(P3R-C12,PMC13035923 化学合成,1 组)、SS 2 个(P3R-SS22/PMC12120870 龙胆二糖键、P3R-SS23/PMC6899944 mini-MbA 1,2-葡萄糖化,2 组)。两类均低于"每类 ≥6 目标/≥2 组"硬门(C 还差组数,SS 达组数但差目标数),**候选迁移与真实迁移指标未执行,数值为 null 而非 0**。原因:新来源一旦与已暴露组件共享完整共价反应即被迫入 build(如 PMC9706480 与 PMC13084081 共享 N7Glu/H7Glu+Rha 1→6;PMC13324211 与 PMC13084081 共享 N7Glu+Rha 1→2;PMC13084081 自身经其 K3Glu+Glc 1→2 旧反应连入暴露组件)。

**4. 哪些指标未执行/未通过?**
未执行:A/B/E 新面板比较矩阵(面板不足,合同允许 Partial)、C/SS 候选迁移与真实迁移指标(G≥3、G/N_gap≥50%)、新目标 enzyme/条件认证(保持 actionable=false、evidence_closed=false)。通过:工程(默认关闭/链式加载/字节重放/134 测试/包外验证见下)、新反应准入、E 臂旧能力回归(51 单元 0 错误,SS 4/4、C 5/5、O 7/7 保持,唯一未创建目标与 P2 已单列旧 1b 完全相同,非新退化)。

---

## G0:接手、批准与保护快照

- approval.json:agent_delegated、预算搜索 480(验证 426+工程 54)、来源 4GiB/4,000 HTTP/150 文章/300 附件。
- baseline_manifest.json:P2 的 1,591 保护文件 0 漂移(终验复核),protected_sha256 快照 2,703 文件,git_head 993b22f5 仅定位。
- 运行账本治理:task016_runs.py 新增 P3 分支,绑定 approval SHA `4b8ef3ba…`,purpose 治理(validation/engineering)。

## G1:来源队列、定向发现与自动获取

- 计划查询 19 组(继承队列处置+独立定向发现 c-*/ss-*/citation-chase 8 族)全部执行;补充第三轮 10 组查询(ss-rha-originals/ss-12-glucosyl/c-chemical-aryl/c-direct-flavone/citation-chase-r3),round3_query_ledger 独立登记。
- 本地代理故障期间,10 个 URL 记录 2 次本地连接拒绝后,按合同"恢复另记请求链"以无代理 opener 各做 1 次恢复尝试(round3_recovery_chain.jsonl),计账 189/4,000 HTTP、293,446,233/4 GiB 字节、35 文章版本、41 附件、4,274 证据段。
- 继承队列处置(全部有本任务处置+证据路径):
  - P2 35 条标题候选:全文采集并逐篇证据审查(inherited_queue_review.jsonl,38 条记录:6 候选+32 no_candidate);
  - P2 21 篇已采集但身份从未编码的全文:补充审查(p2q-batchA/B,24 条记录:15 候选+9 no_candidate);
  - P2 9 篇未决+1 篇撤回+12 篇扩展复审:全部重新提取(group B/C/F/H);
  - 交叉绑定 inherited_queue_crosswalk.jsonl 共 59 条,每条含 P2 记录类型、P3 处置与证据指针。
- 第三轮定向发现采得 4 篇全文(其中 PMC5856881 为 P1 已暴露来源,识别为重复采集并按已暴露处理)。
- 关键产出:PMC12120870(UGT94BY1 astragalin→gentiobioside β(1→6),身份完整)、PMC6899944(CcUGT3 mini-MbA 1,2-葡萄糖化,身份完整)、PMC9706480(菊科 1,6RhaT,7 条候选;准入阶段依据命名标准品+酶名 1,6RhaT 将异头构型判定升级为完整,判定与引文见 identity_checks)。

## G2:结构准入、去重与来源闭包

- 候选池 261 条记录(208 候选行+53 no_candidate),identity_checks.jsonl 逐条判定:**82 行准入**(34 新反应的 52 上下文 + 40 行旧反应新上下文确认)、126 行保留待身份、53 行范围排除。
- old_new_reaction_map.jsonl:82 行与旧库/重复反应匹配;旧库 58 共价签名(C5/O38/SS15)对照表来源 P2/v2 运行实例。
- source_group_edges.jsonl 84 条闭包边(同共价反应、同旧库签名、开发暴露),exposure_ledger 35 个暴露来源。
- split_manifest.json 在任何模板构建前冻结:build=全部暴露连接组件;holdout-eligible 仅 3 个独立组件(PMC13035923、PMC12120870、PMC6899944)。
- P2 撤回的 2 条 C8 编码(kaempferol/quercetin C8-β-D-Glc)以重新提取的完整身份在新版本准入(P3R-C05/C06),原撤回事实保留。

## G3:面板与范围能力

- panel_manifest.json+heldout_references.jsonl 冻结(模板构建前):C 1 目标/1 组、SS 2 目标/2 组。SS22 参照全结构编码;C12/SS23 证据绑定参照,结构编码显式 deferred(不伪造 SMILES)。
- 范围能力:3 个新范围模板(见开头),7 个 build-only 实例,支持重放 10/10,边界 12/12。
- runtime 载荷只含 build 实例;heldout_references 仅评估侧,不入运行库。

## G4:显式 v4 与 A/B/E 比较

- v4 实现并接线(worker/service/workspace/contracts 四处显式分支,task016_runs.py 账本治理),默认关闭;v1/v2/v3 加载路径不变(测试验证 v3 绑定不变、P2 模板指纹逐字节一致)。
- **E 臂旧回归**:17 冻结旧目标×3 seed=51 单元真实 MCTS 全部成功,0 错误,最长墙钟 7.72s(≤60s);旧 4SS/5C/7O 参照全 seed 创建保持,唯一未创建目标与 P2 legacy_regression.json 的旧 1b 完全相同(非新退化)。A 前三保护未发现违反(action_trace 全量留档)。
- 新面板 A/B/E 矩阵:未执行(面板不足);未借 P2 结果填补;480 预算仅用 51(全部验证用途,conservative 总账含 2 行治理拒绝尝试前记录=0 次真实尝试)。

## G5:核验与交付

- 载荷字节重放:templates.jsonl/runtime_instances.jsonl/template_source_manifest.json 隔离重跑逐字节一致(verify_summary.payload_byte_replay)。
- 本地测试:**134 项全部通过**(既有 124+新增 10 项 v4 合同测试:默认关闭、链式计数、支持重放、边界 0 违反、v3 不变性、未知版本拒绝)。
- P2 1,591 保护文件终验 0 漂移;来源/搜索预算差额 0;交付 31 个决定性文件 SHA 见 verify_summary.json。
- 本任务全部命令/写入经 scripts/operate.py 登记(operations/events.jsonl)。

## 分轴状态

| 轴 | 状态 | 依据 |
| --- | --- | --- |
| engineering | **Completed** | v4 模块/接线/账本治理/字节重放/134 测试/包副本 |
| new_reaction_admission | **Completed** | 34 新反应(C12/SS22),身份完整、去重、闭包 |
| C_transfer | **未执行(null)** | 留出面板 1 目标/1 组 < 6/2 门 |
| sugar_sugar_transfer | **未执行(null)** | 留出面板 2 目标/2 组,组数达标但目标数 < 6 |

## 科学边界(不变声明)

本交付仅声明来源约束开发覆盖与候选生成能力。新目标的酶活/条件/收率不继承种子认证:actionable=false、evidence_closed=false、prediction_conditions_verified=false、independent_chemical_validation=false、human_reviewed=false。训练重叠 unknown;正式 blind/gold、供应认证、formal_run_ready/release_ready 保持 false;不声称来源穷尽。P2 继续 Partial,其报告不追改。

## 成本与可复算命令

- 来源:HTTP 189/4,000;字节 293,446,233/4 GiB;文章版本 35/150;附件 41/300;metadata 1,253+623/8,000。
- 搜索:账本 102 行(51 started+51 completed),51/480;工程尝试 0 次真实服务调用。
- 可复算:`.venv-foundation/bin/python -B scripts/task016_p3_merge.py`、`task016_p3_g1_close.py`、`task016_p3_round3.py`、`task016_p3_admit.py`、`task016_p3_build.py`(FLAVORETRO_P3_REPLAY_DIR=... 字节重放)、`task016_p3_panel.py`、`task016_p3_regression.py --run`、`task016_p3_verify.py`;命令行参数与输出职责见脚本头部 docstring。合同建议入口形式有效,round3/panel/verify 为新增等价入口。

## 遗留与交接

- 留出面板缺口:需要 ≥5 个 C 与 ≥4 个 SS 完整身份且不与暴露组件共享反应的新来源;P2 的 9 篇未决中 PMC10465961 等已重新提取,2 条撤回 C8 已重新准入。
- 未编码图形:PMC11502824/PMC12790375/PMC13421352 化学图形结构仍待图形级编码(本轮以文本/SI 证据准入,未完成的图形线索保留)。
- temp/p3-extract/ 为工作区,组提取文件 SHA 已固定于 candidate_extraction_summary.json;STATE.md.backup 为前一会话遗留工作文件,保留未清理。

---

**报告生成**: 2026-10-07,agent_delegated 执行
