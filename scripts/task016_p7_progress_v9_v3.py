"""Archive progress v8 and publish evidence-bounded progress v9 without rewriting history."""
import json
from scripts.operate import write
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
R=ROOT/"docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"; S=ROOT/"STATE.md"
O=BASE/"report_snapshots/progress-v9-inputs"
def main():
    prior=json.loads((BASE/"report_snapshots/progress-v8.json").read_text())
    assert sha_file(R)==prior["report_pointer"]["sha256"] and sha_file(S)==prior["state_pointer"]["sha256"]
    archives={}
    for label,p in [("prior_report_archive",R),("prior_state_archive",S)]:
        q=O/("progress-v8-"+p.name);assert not q.exists();write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p);archives[label]=pointer(q)
    files=[
      "C/E02/stages/batches/C-E02-R5/G5_FRESH_HOLDOUT_ACQUIRE.json",
      "C/E02/stages/batches/C-E02-R5/fresh_source_input_manifest.json",
      "C/E02/stages/batches/C-E02-R5/raw_intake_manifest.json",
      "C/E02/fresh/C-E02-R5/query_audit.json",
      "C/E02/fresh/C-E02-R5/source_exposure_custodian_v1/permanent_exposure_manifest.json",
      "C/E02/fresh/C-E02-R5/A5_fixed_extraction_v1/A5_role_manifest.json",
      "C/E02/fresh/C-E02-R5/A5_fixed_extraction_v1/A5_extraction_validation.json",
      "C/E02/fresh/C-E02-R5-A3/source_original_identity_verification.v4.json",
      "C/E02/fresh/C-E02-R5-A3/author_footnote_parser_correction.v4.json",
      "C/E02/fresh/C-E02-R5-A3/role_A3_manifest.v4.json",
      "C/E02/fresh/C-E02-R3/A6_source_reconciliation_v2/later_R4_identity_dependency_disclosure.append.v1.json",
      "C/E02/post_scope_internal_hypotheses/v1/permanent_exposure_manifest.json",
      "SS/E02_design/second_acceptor_A4_v1/A4_role_manifest.json",
      "SS/E02_design/second_acceptor_A5_v1/A5_role_manifest_v2.json",
      "SS/E02_design/second_acceptor_A4_donor_supplement_v1/A4_role_manifest.json",
      "SS/E02_design/second_acceptor_A4_PMC106_donor_v2/A4_role_manifest.json",
      "SS/E02_design/second_acceptor_A6_final_reconciliation_v1/A6_final_reconciliation_summary.json",
      "SS/E02_design/second_acceptor_A6_final_reconciliation_v1/role_A6_final_reconciliation_manifest.json",
      "SS/E02_design/second_acceptor_graph_identity_v1/four_official_graph_identity_comparisons.json",
      "SS/E02_design/second_acceptor_graph_identity_v1/permanent_exposure_manifest.json",
      "epochs/C-E02/epoch_state.v4.json",
      "verification-v12-incremental/independent_verification.v2.json",
      "verification-v12-incremental/role_A11_independent_manifest.v2.json",
      "report_audit/progress-v8-isolated-A12-v1/bounded_report_validation.json",
      "report_audit/progress-v8-isolated-A12-v1/role_A12_isolated_manifest.json",
      "report_snapshots/progress-v9-budget-prefix.json"]
    inputs={}
    for name in files:
        p=BASE/name;q=O/"evidence"/name;assert p.is_file() and not q.exists(),name
        write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p)
        inputs[str(p.relative_to(ROOT))]=dict(sha256=sha_file(p),physical_archive=pointer(q))
    budget=json.loads((BASE/"report_snapshots/progress-v9-budget-prefix.json").read_text());b=budget["totals"];assert b["HTTP"]==586 and b["bytes"]==1088404409
    text=R.read_text()
    def sub(a,z):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,z)
    sub("report_snapshots/progress-v8.json","report_snapshots/progress-v9.json")
    sub("现已实际冻结R1–R4四个G5分支，R1/R3/R4三个G6的准入数均0；","现已实际冻结R1–R5五个G5分支，R1/R3/R4三个G6的准入数均0；R5新原件独立提取中、尚未G6；")
    sub("最新C epoch_state.v2保留真实创建时间，旧状态不覆写。","最新C epoch_state.v4保留真实创建时间与A3脚注解析更正链，旧状态不覆写。")
    sub("C-E02的R1–R4均已在各自首次化学抽取前实际G5冻结，其中R1/R3/R4后续G6准入结果均0；","C-E02的R1–R5均已在各自首次化学抽取前实际G5冻结，其中R1/R3/R4后续G6准入结果均0；R5提取中不提前计准入；")
    sub("future-fresh已按R1–R4采集原件或记录访问延后","future-fresh已按R1–R5采集原件或记录访问延后")
    sub("78部分身份和7历史未知继续保留。","78部分身份和7历史未知继续保留。另3个post-scope内部未核实命名hypothesis（techtochrysin拼写未知、wogonin、isorhamnetin）均永久exposed，具体图/来源null；R5输入现绑定全19个hypothesis及新增SS图/同义词曝光，不能把名字猜测升级为来源事实。")
    sub("HTTP 200、正确数据库 CID、SI 下载成功均不单独等于反应证据合格。","R5作者稿现由A3 v4核对：官方repository精确DOI→PDF文件链、标题、5作者顺序与Crossref/MED登记一致；PDF第2页5作者姓名后的单位脚注数字原样保留，仅在已标Authors字段内显式投影。Root v2词边界误拒与v3误记4姓名缺失均保留并更正，不能再称原PDF缺这4作者；检查过的PDF标题页未给DOI保持缺失。R3当时身份核对实际使用后来R4柑橘原件及ACS SI，两项晚依赖追加披露，不回填到R3 G5当时。HTTP 200、正确数据库 CID、SI 下载成功均不单独等于反应证据合格。")
    sub("WASABI、Diosmin的端点身份不能补足缺失实际donor，总体完整双抽取分歧数仍未完成，null。","SS第二受体补核现在完成：17 raw共同输入、A4/A5固定角色及供体补充，4个受体/路径产品完整图与2个来源特定供体图一致；4个官方完整图身份匹配，但不是实际反应产品资格。3个focus均defer、新支持0，现支持仍同1受体；路径图与具体assay产品之间的原文联系缺口保持，未添加通用NMR或标准品硬门。两供体中性来源图一致、实际盐/混合物/纯度未知保留；Standard InChI tautomer与FixedH精确图往返分别记录。WASABI、Diosmin的端点身份不能补足缺失实际donor，总体完整双抽取分歧数仍未完成，null。")
    old=next(x for x in text.splitlines() if x.startswith("18. **预算。**"))
    new="18. **预算。** 搜索仍107/600=91真MCTS+16fixture，107terminal/0pending，工程32/60。A0在2026-10-09T11:46:57.970076Z完成追加前缀快照：586 HTTP、1,088,404,409 bytes；C346/85,876,572B，SS236/1,002,493,915B，root4/33,922B；附件91请求，失败或redirect115。article-version按旧xml/article_version口径47请求、加入original_pdf为48请求（C36/SS12）；这是请求类别而非47/48篇可用原件，SS scientific focus 11与请求12的总体分母仍pending。快照为有真实起止时间的追加文件窗口，后续采集继续不得追写成当时已发生；原533及更旧372/497快照均保留各自时间。外部web工具内部HTTP不可观测单列；预算没有提高，未绕过访问控制。来源全局disposition、图/命名/SI闭包仍pending，不宣称饱和。"
    sub(old,new)
    sub("R1–R4四G5及R1/R3/R4三G6已真实创建登记","R1–R5五G5及R1/R3/R4三G6已真实创建登记")
    start=text.index("SS现有2支持仍同1受体；原始SI中另两个flavone")
    end=text.index("\n\n工程仍引用221",start)
    text=text[:start]+"SS现有2支持仍同1受体；第二受体原图双独立转写和来源特定供体补充已完成。4个受体/路径产品canonical、Standard InChI、FixedH图一致，2个来源特定中性UDP-apiose图的7个碳立体中心一致；实际盐、混合物和纯度未知保持。8次官方精确完整InChIKey属性/同义词查询均200，4图身份匹配、4改名实际被曝光闭包拒绝；此前8次字面全名404并不表示结构不存在。官方身份与反应出处两轴分开：3个focus全部defer、新qualified=0，未推进SS G2/G3/G4。PMC106原文特定受体阳性、通用Glc-O2说法与S1路径图均保留，路径图未明确连到具体assay产品；PMC131的2a仍只有579.1296[M-H]-/C26H27O15等部分证据，受体标准不能冒充产物标准。未发明所有反应必需NMR/标准的额外门。更广SS公开一手来源发现继续，先固定raw，再做新双抽取。"+text[end:]
    sub("最新R3/R4和新guard的A11 v12独立增量核验进行中。","A11 v12已完成7通过/7pending/0failed、overall=false：绑定4,655输入SHA、3,961保护文件及R3/R4/SS局部来源与当时533预算，非科学门全部通过。原解析/入口失败保留。v8另由root编写隔离A12文档进程实际8通过/5pending/0failed，因agent thread limit未获得独立子agent A12；独立性不足明确披露，不称盲化学验证。")
    sub("SS双原图核对和来源准入；达到每scope两受体后","SS新一手来源与具体assay产品核准；达到每scope两受体后")
    insertion="\n\nC-R5已按三类预注册路线执行7查询（565返回/565去重）、13 PMID精确MED补核、4永久来源别名排除、9 DOI公开位置解析和原件采集，共44治理HTTP；另A3精确Crossref1HTTP。实际新增1个56页作者稿+SI及2个同仓储HTML落地，8其他来源仍metadata/access-deferred。G5在首次化学提取前实际冻结；A5现已固定9 dispositions、81正文表测量格=70numeric+11ND，0NT/0反应数值零，另18表达量值含6个0.00分别保留；这些仍是A5输出，A4/A6终核待完成。原文直接apigenin/luteolin C6阳性观察与完整donor/reference缺口分开；正文RT2.54/mz447与Fig2 RT2.63/约431峰冲突原样保留，资格与fresh均0。作者稿原件已永久post-scope暴露，后续不再当未观察来源。ACS相同官方API POST在发HTTP前触发已有URL次数门，0新HTTP；失败保留，没有造新URL重试；RSC SI未核实locator尝试失败也保留，不升级原件证据。\n"
    marker="\n## 执行中修订记录\n";assert text.count(marker)==1;text=text.replace(marker,insertion+marker)
    text+="\n- progress-v9：新增C-R5第五G5/9 raw来源/44HTTP，A5先固定而A4/A6待核；A3 v4纠正姓名脚注解析错误，原错误和later-R4身份依赖均保留。SS新双轨4图及2供体核对、4官方图身份匹配完成，但3focus仍defer/新支持0、现1受体；A11v12与隔离非独立A12实测保留边界。586HTTP以真实asof绑定，科学fresh0/null/新bank G9未成、P2未关闭。\n"
    state=S.read_text(); oldp=next(x for x in state.splitlines() if x.startswith("TASK-016-P7（"))
    newp="TASK-016-P7（2026-10-09 CST）：[合同](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md)及[执行中报告](docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md) **In Progress**，agent_delegated。C/SS E01已incomplete、旧原件/guard保留；C-E02原1个C6 scope/CH6-LU6两受体/10负控/C3-H保持G4 SHA，现R1–R5五G5和R1/R3/R4三G6实际冻结登记，合格fresh0。R1十source同域完整0；R2八十四PMID解析/4访问延后；R3/R4前体糖化再酸脱水及114个原始测量格核对保留，source ID复用不加算新出处。R5新增1个56页作者稿+SI/2仓库落地、9dispositions，A5固定、A4/A6待核；正文RT/mz冲突、完整donor/reference缺口保持。A3 v4核5作者与官方DOI文件链一致，姓名脚注解析原错误及更正链保留；publication identity不授化学资格。19命名hypotheses及SS新增图/同义词曝光已绑定R5。SS原11focus=2支持/9defer但同1canonical acceptor；第二受体4完整图、2来源特定供体双转写一致和4官方完整图身份匹配已完成，新增3focus全defer/0支持，实际盐/混合物/assay身份未知保留，未形成SS G2+。两轴G7/G8及新bank G9未成，科学A/B/E0cell、指标null。旧221全量和187+34无资产仍限144文件快照；新增8intake+4alias单测不伪称full233。搜索107terminal/0pending=91真MCTS16fixture，工程32/60。A0截至11:46:57UTC源586HTTP/1,088,404,409B，article请求47/48口径不当可用论文数，总体分母pending。A11v12实际7pass/7pending/0failed、overall=false、3961保护0漂移；v8 root隔离A12为8pass/5pending，独立子agent不可用限制披露。最新报告progress-v9，P2 development effect/formal/release未关闭；未Git同步。"
    assert state.count(oldp)==1;state=state.replace(oldp,newp)
    oldnext=next(x for x in state.splitlines() if x.startswith("下一步：继续已批准TASK-016-P7。"))
    newnext="下一步：继续已批准TASK-016-P7。C-E02五G5/三0准入G6已实际建立，完成R5独立双抽取与A6原始值/图/曝光核对，继续合法同域primary原件及完整来源闭包；所有后续fresh intake绑定全新增永久曝光与PMID别名，不能复用closed E01或改写design。SS第二受体双图和官方身份已核但具体assay产品资格仍defer，继续更广一手来源、按每scope两不同受体/完整重放/边界门建bank后才freeze。两轴各≥6完整可执行fresh/≥2组、100%适用/零泄漏后才真实A/B/E；G≥3且≥50%、双基线净增益/零reference loss及≥3目标/≥2组三seed节点迁移另核。新bank G9及科学资产变化后完整工程/历史回归；失败/未知/冲突/零保留，TASK-017、训练独立性及formal/release门保持。"
    assert state.count(oldnext)==1;state=state.replace(oldnext,newnext)
    write(TASK,str(R.relative_to(ROOT)),text);write(TASK,str(S.relative_to(ROOT)),state)
    snap=dict(task=TASK,approval_type="agent_delegated",revision="progress-v9",created_at=now(),parent_snapshot=pointer(BASE/"report_snapshots/progress-v8.json"),report_pointer=pointer(R),state_pointer=pointer(S),**archives,inputs=inputs,G5_batches=5,G6_batches=3,SS_current_source_support_contexts=2,SS_current_distinct_eligible_acceptors=1,SS_new_focus_deferred=3,R5_A5_fixed=True,R5_A4_A6_pending=True,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,goal_completed=False,human_reviewed=False,source_chemical_saturation=False,independent_A12_subagent_available=False,isolated_A12_v8_bounded_checks_passed=True,budget_pointer=pointer(BASE/"report_snapshots/progress-v9-budget-prefix.json"))
    p=BASE/"report_snapshots/progress-v9.json";immutable_json(p,snap)
    print(json.dumps(dict(snapshot=pointer(p),report=pointer(R),state=pointer(S),archived_evidence_inputs=len(inputs),goal_completed=False)))
if __name__=="__main__":main()
