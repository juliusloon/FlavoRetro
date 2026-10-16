"""TASK-016-P7 progress-v26 science milestone immutable closeout:
three independent primary-source SS direct-O2 enzymes (not fresh), and
three C original out-of-scope reactions independently screened.
"""
import json,hashlib
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
OLD=B/"report_snapshots/progress-v25.json"
AUDIT=B/"verification-v26-science-source-groups/independent_A11_three_O2_primary_groups_v2.json"
AUDIT_PREV=B/"verification-v26-science-source-groups/independent_A11_three_O2_primary_groups.json"
C=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1/A6/three_original_science_scope_dispositions.json"
SS=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1/A6/two_original_O2_scientific_group_closure.json"
FG3=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1/A3_original_front_verified.json"
C_G6=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
SS_G6=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G6_IDENTITY_STRUCTURE_ADMIT.json"
ARAB=B/"governance/R28-SS-Arabidopsis-original-access-v1/raw_custody_summary.json"
R27=B/"C/E02/fresh/C-E02-R27-publisher-original-access-v1/lawful_publisher_original_access_disposition.json"
OUT=B/"report_snapshots/progress-v26.json"
SNAP=B/"report_snapshots/progress-v26-inputs/prior_documents"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def j(p):return json.loads((ROOT/p).read_text())
def put(p,s):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_OUTPUT "+str(p))
 write(T,str(p),s)
def main():
 if (ROOT/OUT).exists():raise RuntimeError("V26_EXISTS")
 v=j(OLD);a=j(AUDIT);c=j(C);s=j(SS);r=j(R27)
 assert v["progress"]=="progress-v25"
 assert a["passed"]==38 and a["failed"]==0 and a["source_global_physical_HTTP"]==1086
 assert a["independent_SS_source_level_direct_enzymatic_O2_groups_with_tomato"]==3
 assert c["original_primary_science_reviewed"]==3 and c["original_source_scope_positive_C6"]==0
 assert s["independent_O2_groups_newly_verified_this_round"]==2 and s["independent_O2_groups_including_prior_tomato"]==3
 assert s["current_epoch_fresh_holdout_admitted"]==0 and s["complete_reaction_atomgraphs_admitted"]==0
 assert r["valid_pdf_count"]==0 and r["attempted"]==2
 assert j(ARAB)["usable_original_XML"]==1
 before=(ROOT/REPORT).read_text();state=(ROOT/STATE).read_text()
 assert sha(REPORT)==v["report_SHA"] and sha(STATE)==v["state_SHA"]
 logs=[]
 for f in (ROOT/"operations").glob("command-*.log"):
  text=f.read_text()
  if "Ran 286 tests" in text and text.strip().endswith("OK"):
   logs.append((f.stat().st_mtime,f.relative_to(ROOT)))
 assert logs,"NO_FRESH_COMPLETE_286_TESTS_LOG"
 log=max(logs)[1]
 now=datetime.now(timezone.utc).isoformat()
 if (ROOT/SNAP/"REPORT-016-P7-prior.md").exists():
  assert (ROOT/SNAP/"REPORT-016-P7-prior.md").read_text()==before
 else:put(SNAP/"REPORT-016-P7-prior.md",before)
 if (ROOT/SNAP/"STATE-prior.md").exists():
  assert (ROOT/SNAP/"STATE-prior.md").read_text()==state
 else:put(SNAP/"STATE-prior.md",state)
 oldline="状态：In Progress（未完成）。当前权威截面progress-v25（2026-10-11T03:34:37.303139+00:00）；阶段决定agent_delegated，非human_reviewed。"
 assert oldline in before
 before=before.replace(oldline,"状态：In Progress（未完成）。当前权威截面progress-v26（"+now+"）；阶段决定agent_delegated，非human_reviewed。",1)
 before+="""

## progress-v26：SS 独立直接糖 O2 原始酶学来源拓展为 3 组；C 三份原件完成源级 C6 严格筛查（"""+now+"""）

**这是可验的科学来源阶段进展，不是新 fresh 科学 holdout/迁移完成。** 继 progress-v25 取得番茄 SlUGT79B-B 的单项 SS 直接 O2 证据后，本轮沿已保存的其他原始研究、合法 PMC JATS 全文及来源双独立科学审查获得**两项新增独立原件来源的直接糖残基 2″-O 葡糖基转移证明**。源级独立原始研究组现为 **3**。C 轴的三篇在 progress-v25 已获得原始 JATS 完整文章得到 G5→A4/A5→A6 的来源级资格结论，未把异黄酮 C8、O7 或 2-羟基黄烷酮 C-糖基化误读为冻结 C6 直接黄酮反应。

### 1. SS-E02：新增 2 项原始直接 O2 酶学研究（累计 3 独立原始研究组）

| 独立原始实验组 | 来源与本轮确认证据 | 资格边界 |
|---|---|---|
| 番茄 SlUGT79B-B（承接 v25） | `PMC12611259`, DOI `10.1093/plphys/kiaf556`；重组 79-B，kaempferol 3-O-galactoside + UDP-glucose → 3-O-glucosyl(1→2)galactoside（K2）；预印本 `PMC11974848` **并非第二组** | 源级 direct O2 正证据，既有历史曝光，非 fresh |
| 大豆 GmF3G2″Gt/UGT79B30 (Fg3)（本轮新复核） | `PMC4494776`, DOI `10.1186/s12870-015-0504-7`，原始重组酶段落 `body/p-30` + 讨论 `body/p-42`：kaempferol 3-O-glucoside + UDP-glucose → 3-O-sophoroside；实际受体面还包括 kaempferol/quercetin 3-O-Glc/Gal；独立 A4/A5 同 SHA | 正式直接糖 O2、UDP-glucose 源级支持；原件本来已有档案及独立 SI，**不重复下载、不计新 fresh** |
| 拟南芥 UGT79B6（本轮新复核） | `PMC4282749`, DOI `10.1111/tpj.12580`；本轮新增官方 JATS XML HTTP200、149114 bytes；原文 `body/p-20` 重组酶 kaempferol 3-O-glucoside → 3-O-glucosyl(1→2)glucoside；`body/p-28` UDP-sugar 对照证明 UDP-glucose donor 优选；`body/p-32` 来源 β-D-Glcp 1→2 结构名称与位点。A4/A5 各独立审查，A6 与原文 SHA 完全吻合 | 正式 direct O2、UDP-glucose 源级支持；**历史曝光，非新 fresh** |

R29 前置 G5 在读取上述两份正式原件正文前冻结。大豆全篇原始 XML、完整论文 PDF 和多份独立 SI 已在 `data/raw/task016-p7/SS/reference_discovery_r2/originals/` 旧来源保管，无额外 HTTP 重取；拟南芥官方 JATS 原件用新批次 R28 合法获取，A3 原件封面 2/2 通过。R29 各 2 份 source 原件分别经 A4 与 A5 独立正文抽取，再由 A6 与直接原始 SHA 核对，G6 现已冻结。新来源事实**不是独立 fresh holdout groups**：大豆和拟南芥都在 project-wide historical exposure 图中，番茄也已事前暴露；三个原始研究也尚未满足独立完整分子 SMILES/atom-map/stereo/100% runtime precursors 全部验收。当前 `complete_reaction_atomgraphs_admitted=0`。

### 2. C-E02：原有三份真正科学原件的首次三方原始文献定向排除

在本轮 G5 预登记与项目历史曝光联合固定后，独立 A4 与 A5 分别读取 C 轴全部三个真实原始 JATS，再由 A6 查回原始 SHA 与段落，最终 G6 严格源级准入判定：

1. `PMC9855344`（DOI `10.3390/biom13010170`）：puerarin 及异黄酮 8-C 葡糖基化的 transcriptomic/candidate 研究，不属于冻结的黄酮 C3-H/C6 直接葡糖基化反应，不能因出现 8-C 产品或引用旧 CGT 反应而升级。
2. `PMC12525976`（DOI `10.3390/plants14193112`）：自身两种 UGT84A28/UGT84B3 的原始酶学实验分别为 apigenin/naringenin **7-O** 和 luteolin **3′-O**，不是 C6；该篇确实准确引用了两项独立原始直接 flavone C6 研究 DOI `10.1016/j.febslet.2014.11.045`（GtUF6CGT1）和 `10.1093/pcp/pcz164`（UGT84A57），但二者不能冒充本论文的新反应。
3. `PMC11577821`（DOI `10.1186/s12896-024-00923-9`）：UGT708S6 重组酶可对 phloretin/2-hydroxynaringenin 等形成 C 结合；来源中涉及的“C6”属于 2-hydroxyflavanone 或酶残基/定位讨论；其 flavone/luteolin 底物方向主要是 O-糖基化，**不是冻结的 flavone C6 直接反应**。

C R26 **3/3 原件源级 disposition 完成、0 合格 C6，G6 冻结**。额外对已有准确官方文章入口验证 Gentiana GtUF6CGT1 的公开论文 PDF 和原始出版商 HTML，各进行了唯一一次新的事前登记来源请求，**2/2 HTTP403**，按原始字节、SHA 保留，未更换凭据/绕过访问控制；该论文在此前已有历史 source HTTP 与曝光，不能作为 fresh。

### 3. 独立验证、预算与当前硬门

- 本轮物理 HTTP 净新增 **3 次**（C Gentiana 官方出版商两个原件请求 HTTP403；SS Arabidopsis PMC XML 一个请求 HTTP200），全球精确 physical source HTTP **1086**；大豆已有旧原件仅重用 SHA，不重复计费。源级 A3 原件、G4→G5→G6 按轴闭环；未产生新 A/B/E MCTS。
- R30 独立 A11 v1 先通过 35 项，但其中一项 G7 文件路径检查过宽；**保留 v1**，修正该文件系统检查并追加双轴真实 G7 缺失、旧证据保留项，最终 **A11 v2 38/38 pass**。审计路径 `outputs/task016-p7/v1/verification-v26-science-source-groups/independent_A11_three_O2_primary_groups_v2.json`。
- 新添 6 个专属独立 JATS 段落、身份、原件 SHA、来源组与 fail-closed 测试；**全量 `unittest` 286/286 OK**，日志 `"""+str(log)+"""`。
- **不可越级认定**：SS 已有 3 个不同发表原始研究的 *source-level enzymatic evidence groups*，但 **fresh SS=0、C=0**，真实 G7 panel 未冻结，独立完整反应全图准入 **0**、科学 A/B/E **0 cell**、迁移指标仍 null，Roadmap P2 仍 In Progress。SS source group ≥2 **绝不等价于** TASK 正式 fresh closure group ≥2。无 G4/scope/UGT template/模型/PUCT/通用搜索更改、无 Git commit/push、无 human_reviewed 与 formal blind 升级。

关键工件：
`outputs/task016-p7/v1/C/E02/fresh/C-E02-R26-original-science-screen-v1/A6/three_original_science_scope_dispositions.json`；
`outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1/A6/two_original_O2_scientific_group_closure.json`；
`outputs/task016-p7/v1/report_snapshots/progress-v26.json`。

后续真闭环需要在冻结 scope 前置曝光门下发现尚未被使用/未被别名闭包曝光的原件化学反应，并由双独立完整结构、全合法 reaction closure 与 runtime 完整门通过，至少每轴 ≥6 fresh/≥2 groups，才可启动真 G7 与 A/B/E。
"""
 write(T,str(REPORT),before)
 state += """

TASK-016-P7 当前状态progress-v26（"""+now+"""）：In Progress，agent_delegated。本轮首次把SS同范围直接糖 O2 酶学科学原件证据从1原始研究组扩展至3组：之前番茄SlUGT79B-B（PMC12611259）、现新增原件复核大豆Fg3/GmF3G2″Gt (PMC4494776,原始XML及SI已有旧档案) 与拟南芥UGT79B6 (PMC4282749，本轮官方JATS原件HTTP200)。新增两项均G5前置曝光、A3 original front、独立A4/A5与A6原文段落SHA交叉核查并完成G6；三组均历史暴露，不能算fresh。C原件PMC9855344/PMC12525976/PMC11577821完成独立A4/A5+A6的严格科学范围排除：isoflavone C8、O7/3′O、2-hydroxyflavanone/phloretin C不是冻结C3-H flavone C6，C本轮源范围positive0。两条来自C原件的直接C6原始研究精确DOI均有历史曝光，Gentiana官方 PDF/HTML本轮各1HTTP403；不绕过。物理来源HTTP净新增3、累计1086，无新MCTS；R30 A11修正路径断言后v2 38/38ผ่าน；全量unittest286/286通过，git diff check待核，无Git commit/push。科学source-level SS独立研究证据=3，不等同TASK的fresh closure groups（C/SS fresh均0），完整结构图准入0，真实G7及科学A/B/E0，metrics=null，P2仍未关闭。权威证据位于REPORT-016-P7 progress-v26与outputs/task016-p7/v1/report_snapshots/progress-v26.json。
"""
 write(T,str(STATE),state)
 out=dict(task=T,progress="progress-v26",status="In Progress",at=now,
   prior_progress="progress-v25",
   prior_report_SHA=sha(SNAP/"REPORT-016-P7-prior.md"),prior_state_SHA=sha(SNAP/"STATE-prior.md"),
   report_SHA=sha(REPORT),state_SHA=sha(STATE),
   R26_C_science_SHA=sha(C),R29_SS_2_groups_SHA=sha(SS),R29_front_SHA=sha(FG3),
   R26_G6_SHA=sha(C_G6),R29_G6_SHA=sha(SS_G6),
   R27_publisher_access_SHA=sha(R27),R28_original_custody_SHA=sha(ARAB),
   A11_first_verifier_SHA=sha(AUDIT_PREV),
   A11_corrected_v2_SHA=sha(AUDIT),A11_v2_pass=38,A11_v2_failed=0,
   new_source_originals_C=0,new_source_originals_SS=1,
   original_sources_C_scientifically_reviewed=3,
   original_sources_SS_scientifically_reviewed_newly=2,
   independent_source_level_SS_O2_evidence_groups_total=3,
   source_groups_formally_fresh_C=0,source_groups_formally_fresh_SS=0,
   fully_structure_admitted_reactions=0,real_G7=False,scientific_ABE_cells=0,
   source_HTTP_delta=3,source_HTTP_global=1086,
   unit_tests_total=286,unit_tests_passed=286,new_science_provenance_tests=6,
   full_test_log_path=str(log),full_test_log_SHA=sha(log),
   no_scope_model_MCTS_mutation=True,source_saturation_proven=False,
   reviewed_status="agent_delegated_not_human",git_commit_push=False)
 put(OUT,json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(progress="v26",SS_independent_direct_O2_groups=3,C_originals_chemically_screened=3,
  C_scope_positive=0,fresh=0,A11=38,unittest=286,new_HTTP=3,
  report_SHA=sha(REPORT),state_SHA=sha(STATE))))
if __name__=="__main__":main()

