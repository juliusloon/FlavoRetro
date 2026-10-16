"""P7 progress-v28: actual prospective v3 round, bounded scientific finding, no admission."""
import json,re,subprocess
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md");STATE=Path("STATE.md")
ARCH=B/"report_snapshots/progress-v28-inputs/prior_documents";SN=B/"report_snapshots/progress-v28.json"
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1";O=B/"verification-v28-C-R39-full-qualification"
def main():
 assert not (ROOT/SN).exists()
 expected={str(REPORT):"9275ed5288b79f9e19e5c9a49f5eac404cbbd3fd0e343e9378667344321b3c84",str(STATE):"2efd4a228be0ee62aac7a69c028a1c31c05a7cdd948ce3357964e840a05c5499"}
 assert all(sha(p)==h for p,h in expected.items())
 for p in (REPORT,STATE):
  out=ARCH/(p.name+".progress-v27-final");assert not (ROOT/out).exists()
  write(T,str(out),(ROOT/p).read_text());assert sha(out)==expected[str(p)]
 audit=load(O/"independent_A11_actual_qualification_audit.json");add=load(O/"A11_stage_name_correction_addendum.json");rt=load(O/"counterfactuals/red_team_results.json")
 assert audit["passed"]==57 and audit["failed"]==0 and add["passed"]==2 and add["failed"]==0 and rt["passed"]==18 and rt["failed"]==0
 log=Path("operations/command-4960.log");tests=(ROOT/log).read_text()
 assert "Ran 286 tests in 39.822s" in tests and "\nOK" in tests
 budget=load(B/"report_snapshots/progress-v28-physical-budget.json");assert budget["totals"]["HTTP"]==1116 and budget["totals"]["bytes"]==1236688048
 valid=load(R/"full_round_validation.json");assert valid["round_execution_complete"] and valid["fresh_admitted"]==0 and not valid["eligible_as_source_saturation_complete_round"]
 mass=load(R/"A6/reported_mass_identity_sanity_check.json")
 at=now()
 summary=("TASK-016-P7 当前状态progress-v28（"+at+"）：In Progress / agent_delegated。C-E02/SS-E02 G4及scope原SHA保持；C/SS合格fresh均0，科学A/B/E 0 cell、metrics=null，真实G7/G8/新bank G9未形成，Roadmap P2尚未关闭。已有SS同范围O2源级证据3个研究组均历史暴露。"
 "本轮C-R37六项近期元数据检索331条观察/312独立题录，288个字面新题录；三项下一页未处理，不宣称来源饱和。选择PMC13564134（2026异荭草苷酵母合成）后取得原文XML、DOCX SI及A6补采原文PDF。5199条暴露快照及实际C G4/list bank绑定到新qualification合同，G5前置；两个隔离解析进程各处理52正文+1479 SI段，42处差异均为空白。A6复核五处图版，作者报告GyCGT1参与luteolin→isoorientin、末级3.17mg/L；SI m/z449.2320与该假定结构[M+H]+449.10784冲突保留。"
 "G6封存1来源/1反应deferred，完整图/立体/前体及历史别名闭包未完成；本轮文档执行完整不等于科学资格通过，不计饱和合格完整轮。v3已跑通实际deferred路径，18项拦截检查通过，真实qualified分支和28名称候选审核仍未实测。累计1116 HTTP/1,236,688,048字节，本轮+11 HTTP/+4,724,715字节；MCTS账本214行SHA未变。19当前G5/G6链通过，A11 57/57加真实G8阶段名补核2/2，全量286/286测试、git diff --check通过。无Git提交/推送、human_reviewed或formal升级。权威证据见REPORT-016-P7 progress-v28和outputs/task016-p7/v1/report_snapshots/progress-v28.json。")
 state=(ROOT/STATE).read_text();rows=[];inserted=False
 for line in state.splitlines(keepends=True):
  if line.startswith("TASK-016-P7 当前状态progress-v"):
   if not inserted:rows.append(summary+"\n");inserted=True
  else:rows.append(line)
 assert inserted
 newstate="".join(rows).rstrip()+"\n";assert newstate.count("TASK-016-P7 当前状态progress-v")==1
 report=(ROOT/REPORT).read_text()
 report,n=re.subn(r"状态：In Progress（未完成）。当前权威截面progress-v27（[^）]+）；阶段决定agent_delegated，非human_reviewed。","状态：In Progress（未完成）。当前权威截面progress-v28（"+at+"）；阶段决定agent_delegated，非human_reviewed。",report,count=1);assert n==1
 report=report.replace("v22–v27增量见本文末尾","v22–v28增量见本文末尾")
 section="\n\n## progress-v28：实际事前合同、原文科学疑点与资格程序拦截验证\n\n"
 section+="当前结果仍为fresh C=0 / SS=0、完整新反应图0、科学A/B/E 0 cell、指标null，任务未完成。新增的范围相关作者报告保留，但尚未取得完整科学资格；不形成G7，不将元数据数、处理轮次数或工程检查数替代留出闭包数。\n\n"
 section+="1. C-R37近期题录：六项2022–2026 Europe PMC lite查询均执行，331条观察、312独立元数据、相对旧R11 288个字面新题录。三项查询仍有下一页；其余311题录在本轮合同中明确not_selected，既非化学拒绝，也非来源不存在或饱和。选择直接异荭草苷生物合成题名的PMC13564134，DOI 10.1016/j.abiote.2026.100085。\n"
 section+="2. 原件与A3：R38取得127,746字节JATS XML和Crossref；R40官方精确PMC对象索引11项，其中同一mmc1.docx在JATS广告重复两次，仅唯一对象下载一次，975,221字节。DOI、题名、期刊、年、卷、期、文章号与出版商的可用字段全部一致。Crossref正式期号2026-12、在线2026-08同年，未来正式月份原样保留。原文CC BY-NC-ND4.0；原件均留本地并被Git忽略。R41按广告精确取得3,301,428字节原文PDF，供A6图版核对，未改A4/A5两件原始输入或G5。\n"
 section+="3. 实际事前合同：prior_exposure_inventory_v3封存38个来源文件/36个规范文件、5199行，语义不明项保留。所选DOI/PMCID/PMID已知token无命中只支持继续审核，full_alias_or_graph_historical_clearance仍false。新full-qualification harness v3绑定自身实际代码SHA、C-E02冻结G4、真实JSON list bank、A3与两件opaque原件；实际合同验证通过后G5于首次正文读取前冻结，SHA 6436ddb72d9e2529870418eeac257c362c2817f9bb1f7fb2432a26e5df23af79。历史v1/v2未验证结论不回写；本次仅对v3实际运行证据作结论。\n"
 section+="4. 双解析与A6：A4 stdlib ElementTree、A5 lxml为独立OS进程，各处理52段正文、1479段DOCX SI，共1531段。1489段原文字串SHA相同、42段仅inline XML空白不同，非空白差异0；11处关键化学上下文逐项对照。A6另对10页原文PDF提取文字，并实际查看正文Figure1/Figure6、SI Figure5/Figure6/Figure8五处图版。两个解析器只构成独立文本解析及上下文观察，不是双分子图转写，也不构成独立化学验证。\n"
 section+="5. 科学观察：作者报告在酵母STL12引入GyCGT1，STI1产异荭草苷0.54mg/L，经UDP-glucose供给工程STI5为3.17mg/L；正文写luteolin经6-C糖基转移一步生成isoorientin。SI将GyCGT1来源列为Gentiana yunnanensis Franch.、accession PZ535504。这是全细胞多步通路中的末级反应报告，不冒充纯化酶单独测定。作者购入标准品；SI Figure5是BY4742外加标准品的降解稳定性对照，不能误作新生成STI1产物的共进样鉴定。\n"
 section+=("6. 保留鉴定疑点：SI Figure6和caption均将449.2320标为isoorientin [M+H]+。用既有冻结build C-CHRYSIN-LU6图仅作假定身份质量核查，分子式"+mass["formula"]+"、理论[M+H]+ %.8f，与原值差 %.8f Da（%.2f ppm）。"%(mass["theoretical_M_plus_H"],mass["difference_Da"],mass["difference_ppm"])+"不修改原值，不捏造新候选图，不据此推断整篇研究无反应。糖立体、完整三方图/前体和来源/别名/历史图闭包仍未闭合；同名既有build提示风险，但没有冒充已完成的新候选全图比较。\n")
 section+="7. G6与计数：固定1来源/1反应均terminal_for_this_round/deferred，非未处理原件；v3验证round_execution_complete=true、unprocessed=[]、科学资格待定2项（同一来源的source与reaction两个对象，非两篇论文）、fresh_admitted=0。该完成值仅表示固定文档流程执行完毕，complete_execution_is_not_scientific_clearance=true，eligible_as_source_saturation_complete_round=false，不能抵作饱和要求的连续两轮。G6 SHA 75f58fdbf737f89dc58aef3bb8a035ab1b2b9681aae8bc679bf8d97f3a1b1777；A4/A5四个开始/完成事件和A6 PDF读取事件共5条永久暴露导出，当前epoch资格仅conditional，下一epoch不得重用fresh。\n"
 section+="8. 工程验证及限制：真实deferred路径通过；18项检查覆盖错误代码/银行绑定、来源宇宙变更、五类epoch终止、旧暴露、重复读者、缺实际G5收据、漏SI路线、有原件未处理、漏反应、无完整双图冒充qualified、读取对方输出等，均通过，0新增科学读取。A11 57/57通过；原A11两处G8缺失检查误用不存在的G8_PREFLIGHT文件名，追加更正记录用实际G8_STATIC_PREFLIGHT重新核对2/2通过，原审计保留。19个当前G5/G6链完整通过，C/SS G4、scope、运行账本214行SHA不变。全项目unittest286/286通过（operations/command-4960.log，39.822秒），git diff --check通过。真实qualified候选路径及28名称候选审查仍未实测，不能据18项检查宣称化学准入成功。\n"
 section+="9. 采集执行与预算：R41前两次本地调用因不支持original_pdf kind、缺显式raw-only字段而在HTTP前被拒绝，0网络请求；原失败与precontract v1/v2保留，v3补齐原件采集字段，正文科学审核授权仍独立。实际新增R37 6 + R38 2 + R40 2 + R41 1 = 11 HTTP，全部200，共4,724,715 bytes。累计1116 HTTP / 1,236,688,048 bytes（C521、SS552、root43）；legacy article kinds153/expanded160、attachment请求222、历史失败/跳转235。请求kind含本轮PDF article_version，不等同可用论文数；外部web工具内部HTTP仍另列不可观测。0新MCTS，原始与受限数据未加入Git，无commit/push。\n"
 section+="10. 未闭合工作：继续有边界的未处理题录页和合法原件/SI路线；对可合格来源完成真正独立三方图、糖立体、前体、来源/历史别名及28名称审查，再做冻结scope静态完整前体测试。SS三项ACS待定仍需正文或原始表格证据。每轴至少6目标/2独立closure group的硬门和A/B/E三seed矩阵仍有效；现有证据不能触发来源饱和或完成判定。\n\n"
 section+="机器证据：[来源科学判断](../../"+str(R/"A6/source_scientific_assessment.json")+")；[质量疑点](../../"+str(R/"A6/reported_mass_identity_sanity_check.json")+")；[实际轮次验证](../../"+str(R/"full_round_validation.json")+")；[18项拦截检查](../../"+str(O/"counterfactuals/red_team_results.json")+")；[A11审计](../../"+str(O/"independent_A11_actual_qualification_audit.json")+")；[G8阶段名补核](../../"+str(O/"A11_stage_name_correction_addendum.json")+")；[物理预算](../../outputs/task016-p7/v1/report_snapshots/progress-v28-physical-budget.json)。旧v27最终REPORT/STATE逐字节归档于"+str(ARCH)+"；v27 whitespace-finalization历史仍保留。\n"
 assert all(line==line.rstrip() for line in section.splitlines())
 write(T,str(REPORT),report.rstrip()+section);write(T,str(STATE),newstate)
 subprocess.run(["python3","-B","scripts/operate.py",T,"git","diff","--check"],cwd=ROOT,check=True)
 data=dict(task=T,progress="progress-v28",prior_progress="progress-v27-final",at=at,status="In Progress",approval_type="agent_delegated",human_reviewed=False,prior_documents_SHA=expected,report_SHA=sha(REPORT),state_SHA=sha(STATE),source_HTTP_delta=11,source_bytes_delta=4724715,source_HTTP_global=1116,source_bytes_global=1236688048,C_recent_metadata_observations=331,C_recent_unique_metadata=312,C_new_literal_metadata=288,C_queries_with_unprocessed_next_page=3,selected_original_source_count=1,source_scope_related_author_report=1,source_scientific_deferred=1,reaction_scientific_deferred=1,new_full_graphs_qualified=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,source_saturation_established=False,round_execution_complete=True,eligible_as_source_saturation_complete_round=False,permanent_read_event_export_rows=5,prior_exposure_rows=5199,actual_v3_contract_and_deferred_round_validated=True,actual_qualified_candidate_path_exercised=False,redteam_pass=18,redteam_fail=0,A11_pass=57,A11_fail=0,A11_stage_name_correction_pass=2,A11_stage_name_correction_fail=0,registered_current_stage_chains=19,unit_tests_passed=286,unit_tests_total=286,test_log_path=str(log),test_log_SHA=sha(log),git_diff_check=True,git_commit_push=False,MCTS_run_ledger_SHA=sha(B/"run_ledger.jsonl"),MCTS_run_ledger_rows=214,new_MCTS=0,real_G7=False,real_G8=False,R39_G5_SHA=sha(B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"),R39_G6_SHA=sha(B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G6_IDENTITY_STRUCTURE_ADMIT.json"),full_round_validation=fqptr(R/"full_round_validation.json"),A11=fqptr(O/"independent_A11_actual_qualification_audit.json"),A11_stage_name_addendum=fqptr(O/"A11_stage_name_correction_addendum.json"),redteam=fqptr(O/"counterfactuals/red_team_results.json"),budget=fqptr(B/"report_snapshots/progress-v28-physical-budget.json"))
 put(SN,data);print(json.dumps(dict(progress="progress-v28",report_SHA=sha(REPORT),state_SHA=sha(STATE),fresh_C=0,fresh_SS=0,task_complete=False)))
def fqptr(p):return dict(path=str(p),sha256=sha(p))
if __name__=="__main__":main()
