# Progress v10: preserve v9 and apply bounded, current evidence.
import json
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
R=ROOT/'docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md';S=ROOT/'STATE.md';O=BASE/'report_snapshots/progress-v10-inputs'
def main():
    prior=json.loads((BASE/'report_snapshots/progress-v9.json').read_text())
    assert sha_file(R)==prior['report_pointer']['sha256'] and sha_file(S)==prior['state_pointer']['sha256']
    names=[
    'C/E02/stages/batches/C-E02-R5/G6_IDENTITY_STRUCTURE_ADMIT.json',
    'C/E02/fresh/C-E02-R5/A4_fixed_extraction_v1/A4_role_manifest.json',
    'C/E02/fresh/C-E02-R5/A5_fixed_extraction_v1/A5_role_manifest.json',
    'C/E02/fresh/C-E02-R5/A6_source_reconciliation_v3/A6_source_reconciliation_summary.json',
    'C/E02/fresh/C-E02-R5/A6_source_reconciliation_v3/role_A6_manifest.json',
    'C/E02/fresh/C-E02-R5/A6_source_reconciliation_v3/permanent_exposure_manifest.json',
    'epochs/C-E02/epoch_state.v5.json',
    'C/E02/fresh/C-E02-R6/exact_primary_location_query_plan.json',
    'C/E02/fresh/C-E02-R6/exact_location_query_conservation.json',
    'C/E02/fresh/C-E02-R6/raw_original_request_plan.json',
    'C/E02/fresh/C-E02-R6/raw_original_intake_summary.json',
    'SS/E02_design/new_source_discovery_v1/common_raw_only_source_input_v1.json',
    'SS/E02_design/new_source_discovery_v1/role_A2_raw_only_source_discovery_manifest.json',
    'SS/E02_design/new_source_discovery_v1/A2_delivery_SHA_and_conservation_verification.json',
    'SS/E02_design/new_source_A3_identity_v3/three_original_publication_identity_checks.json',
    'SS/E02_design/new_source_A3_identity_v3/A3_identity_summary.json',
    'SS/E02_design/new_source_A3_identity_v3/role_A3_manifest.json',
    'SS/E02_design/new_source_actual_exposure_custodian_v1/permanent_exposure_manifest.json',
    'verification-v12-incremental/independent_verification.v2.json',
    'verification-v13-R5-bounded/independent_verification.v4.json',
    'verification-v13-R5-bounded/role_A11_independent_manifest.json',
    'report_audit/progress-v9-A12-v1/bounded_documentary_validation.v3.json',
    'report_audit/progress-v9-A12-v1/role_A12_manifest.json',
    'report_snapshots/progress-v10-budget-prefix.json']
    for n in names:assert (BASE/n).is_file(),n
    bdoc=json.loads((BASE/names[-1]).read_text());b=bdoc['totals'];f=bdoc['families'];assert b['HTTP']==702 and b['bytes']==1125382301
    archives={};inputs={}
    for label,p in [('prior_report_archive',R),('prior_state_archive',S)]:
        q=O/('progress-v9-'+p.name);assert not q.exists();write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p);archives[label]=pointer(q)
    for n in names:
        p=BASE/n;q=O/'evidence'/n;assert not q.exists();write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p)
        inputs[str(p.relative_to(ROOT))]=dict(sha256=sha_file(p),physical_archive=pointer(q))
    text=R.read_text()
    def sub(a,z):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,z)
    sub('本报告为 2026-10-09（CST）执行中快照','本报告为 2026-10-10（CST）执行中快照')
    sub('report_snapshots/progress-v9.json','report_snapshots/progress-v10.json')
    sub('R1/R3/R4三个G6的准入数均0；R5新原件独立提取中、尚未G6；','R1/R3/R4/R5四个G6的准入数均0；R5双轨与A6已固定；R6仅访问补核、尚无G5/G6；')
    sub('最新C epoch_state.v4保留真实创建时间与A3脚注解析更正链，旧状态不覆写。','最新C epoch_state.v5绑定R5 A6和第四G6，保留真实创建时间与A3脚注解析更正链，旧状态不覆写。')
    sub('其中R1/R3/R4后续G6准入结果均0；R5提取中不提前计准入；','其中R1/R3/R4/R5后续G6准入结果均0；R6仅元数据/访问响应补核，未发生化学提取或宣称完整round；')
    sub('R1–R5五G5及R1/R3/R4三G6已真实创建登记','R1–R5五G5及R1/R3/R4/R5四G6已真实创建登记')
    sub('A11 v12已完成7通过/7pending/0failed、overall=false：绑定4,655输入SHA','A11 v12已完成7通过/7pending/0failed、overall=false：绑定4,849输入SHA')
    old=next(x for x in text.splitlines() if x.startswith('18. **预算。**'))
    sub(old,'18. **预算。** 搜索仍107/600=91真MCTS+16fixture，107terminal/0pending，工程32/60。A0追加前缀快照截至2026-10-09T16:29:22.184740+00:00：702 HTTP、1,125,382,301 bytes；C389/86,040,744B，SS309/1,039,307,635B，root4/33,922B；附件122请求，失败或redirect157。article-version旧口径68、含original_pdf扩展口径75，均为请求类别而非可用论文数；SS累计expanded25请求不能称25篇有效原件。快照有真实采集窗口及prefix SHA，后续请求不追写为当时已发生；原586/533/497等快照保留原时间。总8000HTTP/8GiB和家族2500HTTP/2GiB等硬预算不变，外部工具内部不可观测HTTP单列。全局来源disposition/闭包/最终分母仍pending，不宣称饱和。')
    start=text.index('C-R5已按三类预注册路线执行7查询');end=text.index('\n## 执行中修订记录',start)
    text=text[:start]+'''C-R5按三类预注册路线执行7查询（565返回/565去重）、13 PMID精确MED补核、4永久来源别名排除、9 DOI公开位置解析及原件采集，共44治理HTTP；另A3精确Crossref1HTTP。新增1个56页作者稿+SI及2同仓储HTML落地，8其他来源metadata/access-deferred。G5先于首次化学提取。双轨81正文表测量格=70numeric+11ND、0NT/0反应数值零，另18表达量含6个0.00；测量数不作为反应数。ACS相同官方API POST在发HTTP前触发URL次数门，0新HTTP，RSC SI未核实locator失败均保留，没有造新URL重试或升级证据。

C-R5双轨与A6 v3已固定：81表测量格原始数值/SD/status一致（30活性、45纯化、6动力学），另18表达值数值一致，其中17字面一致、1处A4写1.3而原件与A5为1.30；原图精度保留。两完整受体图一致，1产物宪法图一致，但A4未完成5个绝对立体中心转写，完整产物双轨立体一致数0；这是转写未完成，不能说原图缺失或不可读。实际UDP-glucose指定与整个供体图未完成分开；RT/mass冲突保留。2019 DOI与旧2021 WASABI来源不同，但apigenin-C6产物完整图命中C-E01既有目标，实际改名拒绝1次；另2次未来DOI/PMID别名拒绝。准入0按历史目标闭包与原始完整性判断，不用本批事后曝光反过来否定其首次fresh资格。第四G6及epoch_state.v5真实冻结，旧v1/v2失败和部分比较保留。

C-R6复用R5八个metadata-only来源ID，24精确位置查询全部terminal：8 Crossref及1 Semantic Scholar有效200，另7限流429与8 OpenAIRE传输/解析失败保留。随后15登记公开原件链接实际19HTTP（显式redirect计账），15计划全部terminal/0pending，未获得PDF/XML/HTML原件；0qualification/0fresh，不把访问失败当反应不存在。无G5/G6或完整化学round/饱和结论；下一轮新增元数据发现已分派，不更名复用已暴露目标或重试访问拒绝。

SS新raw-only包73计划/73HTTP/73terminal、36,813,720B；173 metadata hints、12 source-associated条目中，获得3有效full sources的6个XML/PDF版本和31原始附件；另外9条仍缺完整一手正文身份。共同输入81 raw SHA由73响应（含失败）加8可选既有官方donor数据库原响应组成，后8仅物种身份参考，不证明实际assay盐型。Crocus下载200是登录HTML、两NCBI XML只有front/abstract没有body，Fg1/Fg4仅SI等均逐件标记。A3 v3从原件与MED核3/3身份及PDF title/DOI，作者组与editor组分开、Molecules地域限定别名显式保留，缺ISSN未造值；v1误纳editor、v2误要求缺ISSN两失败及部分PDF衍生保留。新A4/A5正在独立核具体assay-product图、供体身份链与内部冲突，未冻结科学资格或新SS scope。三篇实际科学读出处永久design暴露，真实登记时间与未知首次读时间分别保留，其余9 metadata不一概化学曝光。

独立A12 progress-v9文档审计14pass/1fail/7pending、15项请求审计均处理：真实失败为上一版误写A11 v12输入4655，实际4849；4655属于v11。此版修正当前文字，旧REPORT/STATE物理存档，A12失败结果不改。A12自身v2把带fixture意图flag的8个实际live运行误分类，v3从原manifest纠正，原错误保留，正确总账仍91real/16fixture。独立A11 R5 bounded v4为10pass/8pending/0current fail、整体false，核371输入SHA、47输出、7递归stage/376绑定及3961保护文件0漂移；81测量、18表达和目标别名拒绝已核。两审计角色先前科学读出已披露，属于分离的工程/文档审计，不声称盲化学验证。AST/浮点/caption解析失败及逐版本更正保留。

'''+text[end:]
    text+='\n- progress-v10：C-R5第四G6与双轨/A6固定、0fresh；81测量+18表达分开，1.30精度及5立体中心转写未完成保留。C-R6 24位置+19原件HTTP全部terminal/0正文。SS新3完整原文/31附件/81raw包及A3身份完成，新双轨进行中、0资格。纠正v12输入4849并保留A12真实失败，新增A11v13；702HTTP按真实asof绑定。科学矩阵0/null、P2未关闭。\n'
    state=S.read_text();oldp=next(x for x in state.splitlines() if x.startswith('TASK-016-P7（'))
    newp='TASK-016-P7（2026-10-10 CST）：[合同](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md)及[执行中报告](docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md) **In Progress**，agent_delegated。C/SS E01均incomplete，旧guard/数据保留；C-E02来源C6 scope/2受体/10负控/C3-H G4 SHA不变。R1–R5五G5、R1/R3/R4/R5四G6实际冻结，合格fresh0；R5双轨81测量及18表达核对固定，原件1.30精度、5产物立体中心A4未完成与RT/mass冲突保留，旧目标图命中实际拒绝。R6八来源复用，24位置+19原件HTTP全部terminal/0原件，无G5/G6或饱和结论。SS原2支持仍同1受体，第二受体3focus全defer；新raw包73HTTP/3全文6版本/31附件/81raw SHA，A3身份3/3，新A4/A5独立提取中，未授化学资格/未形成SS G2+。三新科学读source永久design暴露，其他metadata不混记。两轴G7/G8及新bank G9未成，科学A/B/E0cell、指标null。旧221全量、187+34无资产仍限144文件历史快照，新增8intake+4alias单测单列。搜索107terminal=91real16fixture，工程32/60。源预算截至16:29:22UTC为702HTTP/1,125,382,301B，article请求旧68/扩展75、附件122，不当可用论文分母。A11v13 10pass/8pending/0fail、3961保护0漂移；A12v9 14pass/1fail/7pending，当前修正v12输入4849，原4655误文与失败物理保留。两审计先前读化学内容已披露，不称盲验证。最新progress-v10，P2/formal/release未关闭，未commit/push/tag/release。'
    assert state.count(oldp)==1;state=state.replace(oldp,newp)
    oldnext=next(x for x in state.splitlines() if x.startswith('下一步：继续已批准TASK-016-P7。'))
    newnext='下一步：继续已批准TASK-016-P7。C-E02五G5/四0准入G6已建立，继续合法同域新primary discovery及完整来源闭包，后续合同绑定全19名字hypotheses、R5图和新SS实际暴露；不改旧scope，design不当fresh。SS新双轨独立核具体assay-product身份与完整图并A6对账，不另造通用NMR/标准品门，也不以donor数据库表示冒充实际盐；每scope两不同合格受体及完整重放/边界后才建bank/freeze。两轴各≥6完整可执行fresh/≥2组、100%适用/零泄漏后才真实A/B/E；正净增益、零loss及三seed节点迁移另核。新科学资产变化后完整工程/历史回归，未知/冲突/失败/零保留。'
    assert state.count(oldnext)==1;state=state.replace(oldnext,newnext)
    write(TASK,str(R.relative_to(ROOT)),text);write(TASK,str(S.relative_to(ROOT)),state)
    snap=dict(task=TASK,approval_type='agent_delegated',revision='progress-v10',created_at=now(),parent_snapshot=pointer(BASE/'report_snapshots/progress-v9.json'),report_pointer=pointer(R),state_pointer=pointer(S),**archives,inputs=inputs,G5_batches=5,G6_batches=4,R5_A4_A5_A6_fixed=True,R6_original_plan_terminal=15,R6_new_originals=0,SS_new_original_sources=3,SS_new_original_versions=6,SS_new_attachments=31,SS_new_raw_SHA=81,SS_new_dual_extraction_pending=True,SS_new_source_qualification=0,SS_current_distinct_eligible_acceptors=1,A12_v9_true_report_failure_preserved=True,A11_v12_input_count_corrected=4849,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,goal_completed=False,human_reviewed=False,source_chemical_saturation=False,budget_pointer=pointer(BASE/'report_snapshots/progress-v10-budget-prefix.json'))
    p=BASE/'report_snapshots/progress-v10.json';immutable_json(p,snap)
    print(json.dumps(dict(snapshot=pointer(p),report=pointer(R),state=pointer(S),physical_evidence_archives=len(inputs),goal_completed=False)))
if __name__=='__main__':main()
