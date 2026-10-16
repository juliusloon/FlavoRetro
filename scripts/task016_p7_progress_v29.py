"""P7 progress-v29: one new primary study, preserved assay universe and source limits."""
import json,re,subprocess
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md");STATE=Path("STATE.md")
ARCH=B/"report_snapshots/progress-v29-inputs/prior_documents";SN=B/"report_snapshots/progress-v29.json"
SOURCE=B/"governance/R47-Iris-cross-axis-source-read-binding-v1/A6"
A11=B/"verification-v29-Iris-cross-axis-original-v1/independent_A11_original_and_scope_boundary_audit.json"
def ptr(p):return dict(path=str(p),sha256=sha(p))
def main():
 assert not (ROOT/SN).exists()
 old=load(B/"report_snapshots/progress-v28.json")
 expected={str(REPORT):old["report_SHA"],str(STATE):old["state_SHA"]}
 assert all(sha(p)==h for p,h in expected.items())
 for p in (REPORT,STATE):
  out=ARCH/(p.name+".progress-v28-final");assert not (ROOT/out).exists()
  write(T,str(out),(ROOT/p).read_text());assert sha(out)==expected[str(p)]
 audit=load(A11);assert audit["passed"]==76 and audit["failed"]==0 and audit["registered_current_G5_G6"]==23
 budget=load(B/"report_snapshots/progress-v29-physical-budget.json")
 assert budget["totals"]["HTTP"]==1128 and budget["totals"]["bytes"]==1237357748
 source=load(SOURCE/"source_scientific_assessment.json");assert source["source_reaction_eligible"] is None and source["observed_Figure4_denominator"]==16 and len(source["conflicts"])==4
 log=Path(old["test_log_path"]);assert sha(log)==old["test_log_SHA"] and "Ran 286 tests" in (ROOT/log).read_text()
 at=now()
 summary=("TASK-016-P7 当前状态progress-v29（"+at+"）：In Progress / agent_delegated。C-E02/SS-E02 G4与scope原SHA保持，C/SS合格fresh仍0/0；科学A/B/E 0 cell、metrics=null，真实G7/G8/新bank G9未形成，Roadmap P2未关闭。"
 "本轮新原始研究PMC13422134（Iris UGT707B2）取得公开PMC全文HTML和6张实际正文JPEG；EPMC XML500、出版商403及SI验证码HTML原样保留，HTTP200的SI响应不计有效PDF。5204行事前暴露快照与两轴实际G4/list bank绑定，C/SS两份G5均在首次正文读取前冻结；A4/A5隔离进程各处理103文字块，SHA及定位全一致。"
 "A6保留全部16测定条目：作者报告6有O糖基化产物、10 N.D.，不将N.D.转缺失或转作冻结SS负控。试剂/结果/Figure4编号、tectoridin标准编号及离子符号共4类冲突保留；未得到完整C6或糖残基O2肯定反应，化学图/立体/前体和历史闭包仍待定。单篇来源跨轴审核不算2独立研究组，两轴G6均deferred，10条永久读事件导出，不计来源饱和完整轮。"
 "累计1128 HTTP/1,237,357,748字节，本轮+12 HTTP/+669,700字节；MCTS214行SHA不变。23当前G5/G6链、A11 76/76及git diff --check通过。核心harness/runtime无改动，沿用v28全量286/286通过证据，本轮未重复运行全套测试。此前C-R39质量疑点、SS三个历史O2研究组及三项ACS待定均未升格。三项C元数据后续页仍未处理。无Git提交/推送、human_reviewed或formal升级。权威证据见REPORT-016-P7 progress-v29与outputs/task016-p7/v1/report_snapshots/progress-v29.json。")
 state=(ROOT/STATE).read_text();rows=[];seen=False
 for line in state.splitlines(keepends=True):
  if line.startswith("TASK-016-P7 当前状态progress-v"):
   if not seen:rows.append(summary+"\n");seen=True
  else:rows.append(line)
 assert seen
 state="".join(rows).rstrip()+"\n";assert state.count("TASK-016-P7 当前状态progress-v")==1
 report=(ROOT/REPORT).read_text()
 report,n=re.subn(r"状态：In Progress（未完成）。当前权威截面progress-v28（[^）]+）；阶段决定agent_delegated，非human_reviewed。","状态：In Progress（未完成）。当前权威截面progress-v29（"+at+"）；阶段决定agent_delegated，非human_reviewed。",report,count=1);assert n==1
 report=report.replace("v22–v28增量见本文末尾","v22–v29增量见本文末尾")
 text="\n\n## progress-v29：新原始研究的完整测定条目与编号冲突保全\n\n"
 text+="结果：仍无合格C/SS新留出、无完整新反应图准入，科学A/B/E为0 cell，指标null。本轮得到1篇新原始研究的可检查主文证据，未把双轴审核、16个测定条目或6个作者报告有产物的底物计作新closure group。\n\n"
 text+="1. 来源与合法公开路径：从R37尚未科学读取的题录选PMC13422134、DOI10.1002/cbic.70486，Iris tectorum UGT707B2。R44取得Crossref、EPMC原件接口500、公开PMC对象索引为空；R45出版商原始入口403，但公共PMC页面200且实际提供全文HTML。R46原文首页题名、DOI、期刊、年、卷、期、文章号、PMID及出版商九字段与Crossref/EPMC一致；六个原文广告图均取得真实JPEG。元数据isOpenAccess=N、Crossref VoR/TDM条款保留，不将公开可读宣称为OA再分发授权；原件仅本地且Git忽略。\n"
 text+="2. SI实际失败：唯一原文广告SI下载请求HTTP200，但原始字节是标题Checking your browser - reCAPTCHA的HTML，非PDF。raw custody保留HTTP状态和字节；语义disposition为access_pending，不把成功HTTP当有效附件，没有解验证码或绕过限制。本轮12请求含2条有效metadata、1件有效正文HTML、6件有效JPEG及3件待定原件响应（500、403、验证码HTML）；custody计9通过/3待定不是9篇研究。\n"
 text+="3. 事前冻结与隔离：prior_exposure_inventory_v4是39来源文件/37规范文件、5204行（v3 5199加R39永久读取5行），已知来源别名字面无命中不代表图/别名清白。C和SS均用实际G4/list scope bank、A3与7件科学原件输入冻结qualification合同；C G5 SHA13000d94517af9705592500abd201a52d32704a18dbc98d0062349b8a2d50f36，SS G5 SHAd01d156e6d0a93fdeba083acc520691ca00160215adb765e7934a45399e73440。两者都在任何首次正文读取前完成。A4 stdlib HTMLParser、A5 lxml为不同进程，各轴各处理103文字块，全部文字SHA及DOM section定位一致；原件图在两提取器仍是opaque bytes，未冒充独立分子图转写。\n"
 text+="4. 原文科学内容：主文报告纯化UGT707B2用UDP-glucose在体外测定，将tectorigenin转成7-O糖苷tectoridin，并有失活酶对照；其余产物被作者依LC-MS初步指认为O糖苷。Figure4完整分母为16测定条目：1–6报告有产物、7–16标N.D.，图注明确N.D.是no product。保留所有条目，不把N.D.当缺失，不捏造数值转换率或唯一产物数。不同O-glycoside.a/b/c不自动意味着糖残基上的糖链延伸；现有主文未建立冻结C3-H flavone C6 β-D-Glc或flavonol3-O母糖O2 β-D-Glc完整反应。13–16底物未独立转写完整图，故其N.D.也不能升级为冻结SS范围的负控。\n"
 text+="5. 来源内部冲突：试剂段将phloretin、luteolin、kaempferol、emodin编号12/6/10/15；结果及Figure4对应2/4/3/6。tectoridin试剂段16、结果与Figure3是14。试剂13/14为aniline/thiol，结果13–16却称glycosides；Results58的失糖离子负号与Figure3正离子标记不一致。四类冲突逐项封存，方法名、结果名、图编号并列，不按常见名称猜图或静默修号。Figure4在实际DOM中绑定g001.jpg，文件后缀并不对应图号；A6按DOM核对Figure3与Figure4，以及已查看的Figure2/图形摘要，避免按文件名错认图。\n"
 text+="6. G6资格：两个轴均1 source deferred、fresh_admitted=0；反应记录为0表示完整化学反应清单尚未转写，绝非论文无反应。C G6 SHAb7c9cd56678304a23102713372849175b07c9503c1264e7ce44733b40281dd86，SS G6 SHA77772536d95932487a48ef8209fe82424a320f4f79751f0396bf650360b0d2f3。v3再次验证固定文档流程执行完整，但eligible_as_source_saturation_complete_round=false、complete_source_scientific_clearance=false，不能抵作饱和连续两轮。一篇研究两个轴审核仍只1来源组。A4/A5共8个开始/完成事件及2个A6审核完成导出共10行，当前资格conditional，下一epoch永久排除fresh。\n"
 text+="7. 验证及预算：A11独立76/76通过，包含原始12对象SHA/字节、SI真实media、九字段身份、双G5先于所有读取、103块守恒、16槽/6肯定/10 N.D.分母、编号冲突、两个科学图DOM关联、23个当前G5/G6完整链、G4冻结与运行账本214行未变。0新MCTS，无核心harness/runtime改动；沿用v28全量unittest286/286（operations/command-4960.log）为历史回归证据，本轮只运行对应实际合同/阶段/来源审计，未伪称重新跑全套。git diff --check通过。累计1128 HTTP、1,237,357,748 bytes，本轮+12 HTTP/+669,700 bytes；C533/SS552/root43，legacy article请求156/expanded163、attachment请求229、HTTP失败/跳转237，含无效SI HTML，不等同可用论文/附件数。无commit/push，原始与受限数据未入Git。\n"
 text+="8. 待办与停止边界：继续R37三项尚未处理的后续页、其他有边界的合法原件路线，以及可合格来源的独立图/位点/立体/前体、完整来源/历史别名和28名称审核。保留R39精确质量疑点与SS三项ACS待定。每轴至少6目标/2独立closure group及实际A/B/E三seed矩阵仍未满足；没有来源饱和判定，不降低硬门。TASK继续In Progress。\n\n"
 text+="机器证据：[科学判断](../../"+str(SOURCE/"source_scientific_assessment.json")+")；[16项测定清单](../../"+str(SOURCE/"all_16_assay_slot_dispositions.json")+")；[原图DOM绑定](../../"+str(SOURCE/"original_figure_DOM_binding.json")+")；[A11独立审计](../../"+str(A11)+")；[实际预算](../../outputs/task016-p7/v1/report_snapshots/progress-v29-physical-budget.json)。旧v28最终REPORT/STATE完整bytes归档于"+str(ARCH)+"。\n"
 assert all(x==x.rstrip() for x in text.splitlines())
 write(T,str(REPORT),report.rstrip()+text);write(T,str(STATE),state)
 subprocess.run(["python3","-B","scripts/operate.py",T,"git","diff","--check"],cwd=ROOT,check=True)
 g5s={};g6s={}
 for f in ("C","SS"):
  p=B/f"{f}/E02/stages/batches/{f}-E02-R47-Iris-prospective-qualification"
  g5s[f]=ptr(p/"G5_FRESH_HOLDOUT_ACQUIRE.json");g6s[f]=ptr(p/"G6_IDENTITY_STRUCTURE_ADMIT.json")
 data=dict(task=T,progress="progress-v29",prior_progress="progress-v28",at=at,status="In Progress",approval_type="agent_delegated",human_reviewed=False,prior_documents_SHA=expected,report_SHA=sha(REPORT),state_SHA=sha(STATE),source_HTTP_delta=12,source_bytes_delta=669700,source_HTTP_global=1128,source_bytes_global=1237357748,new_primary_studies=1,new_valid_original_HTML=1,new_valid_original_JPEG=6,new_valid_SI_PDF=0,retained_SI_captcha_HTML=1,original_A3_fields_verified=9,prior_exposure_snapshot_rows=5204,source_assay_slots=16,source_reported_positive_slots=6,source_reported_ND_slots=10,source_numbering_or_ion_conflict_classes=4,independent_text_blocks_each=103,independent_graph_transcriptions=0,complete_new_chemical_reaction_records=0,zero_reaction_records_is_not_paper_absence=True,shared_study_groups_across_axes=1,scientific_source_admission_C=0,scientific_source_admission_SS=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,new_MCTS=0,MCTS_run_ledger_rows=214,MCTS_run_ledger_SHA=sha(B/"run_ledger.jsonl"),source_saturation_established=False,source_deferred_C=1,source_deferred_SS=1,round_execution_complete_C=True,round_execution_complete_SS=True,eligible_as_source_saturation_complete_round=False,permanent_read_event_export_rows=10,G5=g5s,G6=g6s,registered_current_G5_G6=23,A11=ptr(A11),A11_pass=76,A11_fail=0,budget=ptr(B/"report_snapshots/progress-v29-physical-budget.json"),core_harness_runtime_modified=False,full_suite_rerun_this_turn=False,inherited_full_test_log_path=str(log),inherited_full_test_log_SHA=sha(log),inherited_unit_tests_passed=286,git_diff_check=True,git_commit_push=False,real_G7=False,real_G8=False,chemical_independent_validation=False)
 put(SN,data);print(json.dumps(dict(progress="progress-v29",report_SHA=sha(REPORT),state_SHA=sha(STATE),fresh_C=0,fresh_SS=0,task_complete=False)))
if __name__=="__main__":main()
