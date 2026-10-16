"""Progress v13: fixed C-R7 A6, Petunia design supports, current evidence boundary."""
import json,re
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
R=ROOT/"docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md";S=ROOT/"STATE.md";O=BASE/"report_snapshots/progress-v13-inputs"
def main():
    assert not O.exists()
    prev=BASE/"report_snapshots/progress-v12.json";v12=json.loads(prev.read_text())
    assert sha_file(R)==v12["report_pointer"]["sha256"] and sha_file(S)==v12["state_pointer"]["sha256"]
    names=[
    "report_snapshots/root-actual-resume-20261010-111333UTC.json",
    "report_snapshots/progress-v12-root-documentary-verification-v2.json",
    "report_snapshots/progress-v13-prior-independent-role-SHA-replay.json",
    "report_snapshots/progress-v13-R8-AST-and-Git-exclusion.json",
    "report_snapshots/progress-v13-root-new-script-AST-and-Git-check.json",
    "report_snapshots/progress-v13-budget-actual-resume.json",
    "verification-v14-newSS-bounded-v2/independent_verification.json",
    "verification-v14-newSS-bounded-v2/role_A11_independent_manifest.json",
    "report_audit/progress-v12-A12-v1/A12_bounded_documentary_validation.v2.json",
    "report_audit/progress-v12-A12-v1/role_A12_manifest.v2.json",
    "C/E02/fresh/C-E02-R7/A4_contract_adapter_v1/role_A4_contract_adapter.json",
    "C/E02/fresh/C-E02-R7/A5_contract_adapter_v1/role_A5_contract_adapter.json",
    "C/E02/fresh/C-E02-R7/root_A6_precomparison_input_SHA_v2.json",
    "C/E02/fresh/C-E02-R7/root_A6_graph_comparison_v1.json",
    "C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/378_literal_comparisons_v1.json",
    "C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/A6_source_reconciliation_summary.json",
    "C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/role_A6_manifest.json",
    "C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/postprocessing_field_and_purity_clarifications.json",
    "C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/permanent_exposure_manifest.json",
    "C/E02/stages/batches/C-E02-R7/G6_IDENTITY_STRUCTURE_ADMIT.json",
    "epochs/C-E02/epoch_state.v7.json",
    "C/E02/fresh/C-E02-R8/raw_only_fallback_closeout_v1.json",
    "C/E02/fresh/C-E02-R8/role_A2_raw_only_fallback_manifest_v1.json",
    "C/E02/fresh/C-E02-R8/official_OA_service_documentation_findings_v1.json",
    "SS/E02_design/reference_discovery_r2/Petunia_dual_extraction_assignment_v2.json",
    "SS/E02_design/reference_discovery_r2/Petunia_A4_v1/role_A4_manifest.json",
    "SS/E02_design/reference_discovery_r2/Petunia_A5_v1/role_A5_fixed_manifest.json",
    "SS/E02_design/reference_discovery_r2/Petunia_root_A6_precomparison_SHA_v2.json",
    "SS/E02_design/reference_discovery_r2/Petunia_A6_v1/A6_source_reconciliation_summary.json",
    "SS/E02_design/reference_discovery_r2/Petunia_A6_v1/role_A6_manifest.json",
    "SS/E02_design/reference_discovery_r2/Petunia_A6_v1/2_source_qualified_design_supports.jsonl",
    "SS/E02_design/reference_discovery_r2/Petunia_A6_v1/permanent_exposure_manifest.json"]
    for n in names: assert (BASE/n).is_file(),n
    b=json.loads((BASE/"report_snapshots/progress-v13-budget-actual-resume.json").read_text());assert b["totals"]["HTTP"]==883 and b["totals"]["bytes"]==1193878292
    archive={};inputs={}
    for label,p in [("prior_report_archive",R),("prior_state_archive",S)]:
        q=O/("progress-v12-"+p.name);write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p);archive[label]=pointer(q)
    for n in names:
        p=BASE/n;q=O/"evidence"/n;write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p)
        inputs[str(p.relative_to(ROOT))]=dict(sha256=sha_file(p),physical_archive=pointer(q))
    text=R.read_text().replace("report_snapshots/progress-v12.json","report_snapshots/progress-v13.json")
    answers={
    1:"**epoch 数和状态。** C累计冻结2个epoch：C-E01已incomplete；C-E02 active，来源CH6/LU6构建的C6 scope/2个不同acceptor/10负控/C3-H G4 SHA不变。R1–R5及R7六个G5；R1/R3/R4/R5/R7五个G6，准入均0。最新epoch_state.v7绑定R7固定双轨/A6、G6和新增永久暴露。R2只做身份/访问补核，R6与R8无新可用原件、无G5/G6。SS仅E01曾冻结并已incomplete，SS-E02仍design。旧api7Glc/UDP-apiose层两来源支持同一受体；新UDPGlc/flavonol3-O层已有番茄Kgal→K2一上下文，加Petunia K3Gal/K3Glc两具体反应，共3上下文、2不同canonical受体、2共价反应签名。A7正在检验inner Glc/Gal C4有限二择一边界，尚无合格新SS bank/G2/G3/G4。不能把不同供体/核心的旧层合并凑数。两轴fresh0、科学A/B/E0cell、metricsnull，G7/G8/新bankG9均未形成。",
    4:"**先冻结后抽取。** C-E02 G4先于R1–R5/R7各自G5和首次化学抽取，R7双轨现已固定并完成A6/G6，0fresh。A4首次实际读出02:28UTC；A5固定role实际06:46:51UTC，均按真实记录，不以quota返回状态猜是否未完成。R6/R8为访问补核，非完整化学轮次。SS历史候选的首次科学审查前缺逐批正式G5，晚绑定事实保留；不能回填为顺序通过。新增Petunia在科学读取前冻结design-only allocation，A4实际首读06:30:31UTC、A5 06:46:25UTC；两轨固定后root才比较具体图和assay。另五来源仅metadata/front/容器检查，科学正文/图仍未读；这不预授future-fresh资格。尚无正式fresh面板，整体阶段顺序不能笼统写全部通过。",
    18:"**预算。** 搜索仍107/600=91真实MCTS+16fixture，107terminal/0pending，工程32/60。物理前缀截至2026-10-10T11:30:45.233474+00:00：883 HTTP、1,193,878,292B；C455/111,640,608B、SS424/1,082,203,762B、root4/33,922B。旧article类别98、含original_pdf扩展105、附件204、失败或redirect182均为请求计数，不是有效论文数。相对v12新增R8七HTTP/280,125B，0科学原件；外部web工具3次调用/5个显式文档页，内部HTTP不可观测，单列。R9 raw-only官方访问补核已分派，后续请求不追填到此883前缀；采集窗口不是全局原子快照。总8000HTTP/8GiB、家族2500HTTP/2GiB/200附件及每URL2+1规则不变，SS附件149。完整科学round/分母仍未闭合，未宣称来源饱和。"
    }
    for i,p in answers.items():
        pat=r"^"+str(i)+r"\. .*?(?=\n\n)"
        text,n=re.subn(pat,str(i)+". "+p,text,count=1,flags=re.M|re.S);assert n==1
    pat=r"^7\. .*?(?=\n\n)"
    match=re.search(pat,text,flags=re.M|re.S);assert match
    extra=" C-R7新增11对完整图/分子式一致、378重叠原值一致：297测量格及81比值/产率标签，不推断独立反应数。3有原件来源不适用冻结范围、6缺原件pending；source-specific glycal donor、作者putative C6及后处理分开。Petunia两条K具体反应经9对全图与36表格核对；36个m/z标签35初始一致，1处A5误抄611.1618，原EPS对应酶产物为611.1616、下方标准为611.1618。原值和A6失败保留，另行裁定。2设计支持不等于合格scope、fresh或独立化学验证；Q具体体外产物链不足，F4作者m/z限定保留。"
    text=text[:match.end()]+extra+text[match.end():]
    start=text.index("## 验证、偏差与尚待执行")
    hist=text.index("## 执行中修订记录")
    history=text[hist:]
    validation="""## 验证、偏差与尚待执行

当前科学门仍未关闭。C-R7完成固定双轨/A6/G6；Petunia完成固定双轨/A6并新增两条design来源支持。任何后续SS范围必须先完成A7、独立A8实际dispatcher/mapped完整前体重放、至少6边界0违反，再冻结G4；另五篇未读原件不得提前化学读取或按标题计支持。达到每轴≥6完整可执行、同域且零泄漏fresh/≥2闭包组后，才运行冻结A/B/E。

C-R7的9来源处分完整保留，3篇实际原件共27对象、6篇只有元数据/访问缺口。11对图表示一致不等于11个实证反应。378核对记录=42 NMR单元格+234 SI荧光均值/SD对+21正文膜均值/误差对+13比值+16优化产率+43化学产率标签+9 Scheme标签；均值与SD不翻倍为独立测量。SI第六列原头<τ>，A4 tau_mean_ns与A5 tau_weighted_ns仅按原列显式对应；标签均保留。10 NMR空白、主图2个数值零、SI另3个零及主/SI重复、<50界、未知重复数/误差均分别保留。

PMC13273386实际供体为2-hydroxy-3-keto-glucal，图源C6H8O5，与冻结完整UDPGlc图不同。phloretin是dihydrochalcone；apigenin形成酮糖苷后自发异构化，NaBH4另行还原，一峰与C8 vitexin共洗脱，另一C6为作者putative。AtRED/NADPH是对先前酮产物混合物的后处理，不把A4继承的原glycal donor/acceptor字段当新的还原反应前体。原文SI Method1.3报告1H NMR纯度检查；定量纯度百分比/独立认证仍未知，两者不互相抹除。PMC11663222为protected glucal/organoboron/I2–NaOMe化学序列；PMC7904931为膜测定及TMSOTf多步合成。三者不适用当前冻结范围；不以未编码无关系列或未重指认全部NMR作为排除依据，不新设通用标准品/NMR硬门。6原件缺口意味着本批不宣称完整化学round或饱和。11图与3来源永久暴露补充只约束未来fresh，不倒用事后曝光否定本批首次资格。

Petunia仅PMC5856881 design白名单，A4/A5固定输入/输出SHA先核验再比较。原文body23、Fig3a/b、FigS1与Fig2a构成两个具体产品链；K3Gal/K3Glc是已有3-O糖苷的单步受体，A5初版误指苷元的precursor及旧donor绘图指针均保留，v2明确改为实际受体/官方供体参考。9对完整图含4产品/4糖苷受体/1UDPGlc，另2 A5苷元骨架图不计本步前体。Table1 26格=13numeric/12ND/1Trace，Table2另10numeric；均值零0，误差宽度零1与UDP浓度零2分别保留，Table1 ±不能自动称已明示SD。24组合=2完整设计支持/12ND/10partial；正活性或作者一般结论不能补足Q具体产品链。F4组织峰仅m/z相应的作者限定保留。完整图的分子式/中性精确质量是计算诊断；原件实际正离子m/z和RT保留，未标明加合离子式或中性质量/式的字段保持null，不造新的通用准入门。实际盐/质子化/水合未知；UDPGlc Standard InChI keto/lactim精确图差异与FixedH分别记录，不自动归一化。旧api7Glc/UDPApi层独立保留。

R8只处理两个既有metadata线索及当前官方服务文档：7HTTP/280,125B全部terminal，S3 prefix 200空不等于文章不存在，退役OA端点404不作为科学缺失证据。官方[OA服务说明](https://pmc.ncbi.nlm.nih.gov/tools/oa-service/)确认服务2026年8月退役；[文本挖掘政策](https://pmc.ncbi.nlm.nih.gov/tools/textmining/)限定自动文章获取路线，未执行原拟公共article HTML抓取。当前云数据布局必须依官方实际index/JSON，不猜版本或SI地址。R9仅授权bounded raw-only官方OAI等补核，尚未纳入本版科学原件或G5。

独立A11新SS v14-v2现为5pass/5pending/0fail、overall=false，304输入；原v14 4pass/1fail/5pending保留。原失败是审计字段解析错误，v2由原角色按实际records四个same=false及原SI纠正；番茄四个真实A4丰度转录差异没有撤销。独立A12 progress-v12 v2现为7pass/5继承科学pending/0fail、995输入/14输出、20必答均已审；原v1 literal parser失败保留，v11真实旧文字矛盾不抹除。root另重放两角色1318 SHA检查/1226唯一路径全部匹配，是root下游复核，不另称独立审计。C-R7 A11原件/A6复核进行中；此前A5角色背景和已知汇总值须披露，不能称完全盲或独立化学验证。

工程继承：全量221实际通过/0skip，资产隔离187pass+34预登记skip，均绑定当时144代码文件；新增intake8与alias4单测单列，不宣称233或新来源脚本全套覆盖。旧17×3保留16/17，另1为P6已有失败；P1七canary保持，TASK-016 charged四canary×3恢复重跑全过，75实际运行已独立审。protected3961独立0漂移事实继承，旧helper历史SHA恢复及真实晚时间链保留。此次7个新增/失败保留脚本AST通过、git diff --check通过、raw/outputs tracked0，属于限定工程核验，不关闭科学transfer门。

本版实际root恢复11:13:33UTC，先确认无live旧process；先前quota具体开始/持续时间未知，未声称无观测间隔完成工作。C A5已在06:46:51固定，quota消息不能作为未完成证据；progress-v12当时asof与原报告/STATE物理归档保留。root的相对路径/schema解析错误、Petunia真实m/z差异检查失败均保留，再以新增脚本和产物纠正。未改冻结scope、模型、PUCT、评分或stock17，未commit/push/tag/release。

"""
    text=text[:start]+validation+history
    text+="\n- progress-v13：C-R7双轨/A6与第五G6固定，11对完整图、378记录一致，3来源outside frozen scope/6缺原件，0fresh；后处理/纯度语义和原失败保留。Petunia双轨/A6新增K3Gal/K3Glc两设计支持，9图/36格核对、1个mz转录差异按原EPS裁定；A7边界proposal执行中、尚未freeze。A11v14-v2 5/0/5、A12v12-v2 7/0/5均overallfalse；R8七HTTP无原件、883前缀按真实时间，R9raw-only后续单列。科学0/null/P2仍开。\n"
    state=S.read_text();old=next(x for x in state.splitlines() if x.startswith("TASK-016-P7（"))
    new="TASK-016-P7（2026-10-10 CST）：[合同](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md)及[执行中报告](docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md) **In Progress**，agent_delegated。C/SS E01 incomplete保留；C-E02 C6/2受体/10负控/C3-H G4 SHA不变，六G5/五G6/fresh0，epoch_state.v7。R7双轨/A6固定：11完整图对与378原值记录一致，3来源不适用冻结UDPGlc/flavoneC6范围、6缺原件pending；后处理、作者putative及原失败保留。R6/R8无新原件/G5，R8官方退役服务/合法数据路线补核7HTTP，R9 bounded raw-only补取执行中，不能称来源饱和。SS-E02 design：旧api7Glc/UDPApi两支持同1受体独立保留；新层番茄Kgal→K2一上下文+Petunia K3Gal/K3Glc两具体设计支持，共3上下文/2canonical受体/2共价签名。Petunia A6 9完整图对、36表格一致，36mz中35初始一致、1处A5误抄原EPS611.1616已裁定、原值与失败保留；Q具体产品链pending/F4作者m/z限定不升级。A7仅design做Glc/Gal innerC4有限二择一proposal，未有SS新bank/G2/G3/G4；另5正文图仍未读、不预授fresh。独立A11v14-v2 5pass/5pending/0fail、A12v12-v2 7pass/5pending/0fail均overallfalse，原失败保留，root1318SHA下游重放全匹配不冒充独立审计。G7/G8/新bankG9未成，C/SS fresh0，科学A/B/E0cell、metricsnull。历史221全量及187+34无资产限144文件，新增8intake+4alias单测与7脚本AST/限定Git核验分开；107terminal=91real16fixture/工程32。883HTTP/1,193,878,292B截至11:30:45UTC，扩展article105/附件204为请求数、R9后续另计。最新progress-v13，quota真实时间不倒填，P2/formal/release未关闭，未commit/push/tag/release。"
    assert state.count(old)==1;state=state.replace(old,new)
    oldnext=next(x for x in state.splitlines() if x.startswith("下一步：继续已批准TASK-016-P7。"))
    nextp="下一步：继续已批准TASK-016-P7。完成C-R7 bounded A11及R9合法raw-only访问补核；不得将访问空结果/退役接口/metadata当科学不存在或饱和。SS仅从已固定Petunia design支持构建有明确Glc/Gal内层C4边界的A7 proposal，独立A8走完整dispatcher/mapped参照、≥6负控0违反后才登记G2/G3/G4；不得并入旧api7Glc/UDPApi层。另5未读科学原件在scope冻结及适当G5、closure绑定之前保持隔离，后续fresh须完整图/源身份/零泄漏/同域可执行。两轴各≥6fresh/≥2组后才做真实A/B/E，保持所有迁移硬门、独立重算及旧能力/保护审计。未满足合同来源停止条件，持续执行，不降低门槛。"
    assert state.count(oldnext)==1;state=state.replace(oldnext,nextp)
    write(TASK,str(R.relative_to(ROOT)),text);write(TASK,str(S.relative_to(ROOT)),state)
    snap=dict(task=TASK,revision="progress-v13",created_at=now(),approval_type="agent_delegated",human_reviewed=False,parent_snapshot=pointer(prev),report_pointer=pointer(R),state_pointer=pointer(S),**archive,inputs=inputs,G5_batches=6,G6_batches=5,C_R7_fixed_A6=True,C_R7_dual_graphs=11,C_R7_literal_records=378,C_R7_outside_scope_sources=3,C_R7_access_pending_sources=6,Petunia_source_qualified_design_supports=2,Petunia_distinct_canonical_acceptors=2,Petunia_dual_complete_graphs=9,Petunia_table_cells=36,Petunia_mz_literal_count=36,Petunia_mz_raw_agree=35,Petunia_mz_source_arbitrated=1,SS_new_layer_support_contexts=3,SS_new_layer_distinct_acceptors=2,SS_scope_proposal_in_progress=True,SS_G2_created=False,SS_other5_scientifically_unread=True,A11_v14_v2=dict(passed=5,failed=0,pending=5),A12_progress_v12_v2=dict(passed=7,failed=0,pending=5),R8_HTTP=7,R8_new_originals=0,R9_raw_only_assigned_not_in_snapshot_budget=True,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,goal_completed=False,source_chemical_saturation=False,budget_pointer=pointer(BASE/"report_snapshots/progress-v13-budget-actual-resume.json"))
    p=BASE/"report_snapshots/progress-v13.json";immutable_json(p,snap)
    print(json.dumps(dict(snapshot=pointer(p),report=pointer(R),state=pointer(S),physical_evidence_archives=len(inputs),goal_completed=False)))
if __name__=="__main__":main()
