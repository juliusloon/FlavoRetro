"""P7 progress-v27: archive previous current documents, write bounded current facts."""
import json,re
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import now,sha,load,put
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md");STATE=Path("STATE.md")
SN=B/"report_snapshots/progress-v27.json";ARCH=B/"report_snapshots/progress-v27-inputs/prior_documents"
A11=B/"verification-v27-ACS-SI-and-restoration-v2/independent_A11_public_SI_custody_and_restoration.json"
R=B/"SS/E02/fresh/SS-E02-R34-three-ACS-SI-science-v1"
def main():
 if (ROOT/SN).exists():raise RuntimeError("IMMUTABLE_SNAPSHOT")
 assert sha(REPORT)=="7163377efb2e2123718b055ca85597e5e8659e6966343d975f7bb09383315eea"
 assert sha(STATE)=="0366d2adee6b00f951559a578142c45a5234ebfabc348b88f8df4196aad5121e"
 audit=load(A11);assert audit["passed"]==66 and audit["failed"]==0
 log=Path("operations/command-4858.log");assert "Ran 286 tests" in (ROOT/log).read_text() and "\nOK" in (ROOT/log).read_text()
 budget=load(B/"report_snapshots/progress-v27-physical-budget.json")
 prior={str(p):sha(p) for p in (REPORT,STATE)}
 for p in (REPORT,STATE):
  out=ARCH/(p.name+".progress-v26");assert not (ROOT/out).exists()
  write(T,str(out),(ROOT/p).read_text());assert sha(out)==prior[str(p)]
 at=now()
 summary=("TASK-016-P7 当前状态progress-v27（"+at+"）：In Progress / agent_delegated。C-E02/SS-E02 G4与scope原SHA保持；C/SS合格fresh均0，科学A/B/E 0 cell、metrics=null，真实G7/G8/新bank G9未形成，Roadmap P2尚未关闭。已有SS同范围直接O2源级科学证据3个研究组（番茄/大豆/拟南芥）均历史暴露，不计新fresh。"
 "本轮补齐SS-R11一份10,660,352字节不透明SI（仅custody）；新R31/R32经ACS官方Figshare精确resource DOI链取得番茄SlUGT75C1、茶树CsUGT73AC15、Laportea三份SI PDF，共6,210,434字节，官方文件大小/MD5/本地SHA一致，许可CC BY-NC4.0。3/3 A3首页题名匹配，G5前置后A4/A5两隔离文本解析器处理45页、A6图版与7处caption交叉核对；三项均科学deferred，完整共价图/立体/前体及直接SS O2单步证据未闭合，未宣称整篇论文无反应或来源饱和。"
 "晚近暴露补充封存15个旧G5/G6与102个JSON文档；发现根执行者补采R11时误追加两份已被旧G5绑定的账本。R35先封存完整11请求/4执行行，再恢复原10请求/3执行行至原SHA，原始件、全部物理请求及失败历史保留；旧R12与新R34链恢复通过。"
 "来源本轮净增19 HTTP（R11+1，R31+12，R32+6）、累计1105 HTTP/1,231,963,333字节，外部网页工具内部HTTP另列不可观测；MCTS账本214行SHA未变。A11 v1误用不存在status字段产生1假失败，v2 66/66通过；17个当前G5/G6阶段链通过，全量286/286测试与git diff --check通过。两个旧输入漂移已由R35精确恢复，历史快照不回写。full-qualification harness v2仍未验证，来源/别名/28名称审查及实际候选准入尚未闭合。无Git提交/推送、human_reviewed或formal升级。权威证据见REPORT-016-P7 progress-v27与outputs/task016-p7/v1/report_snapshots/progress-v27.json。")
 state=(ROOT/STATE).read_text()
 result=[];inserted=False
 for line in state.splitlines(keepends=True):
  if line.startswith("TASK-016-P7 当前状态progress-v"):
   if not inserted:result.append(summary+"\n");inserted=True
  else:result.append(line)
 assert inserted
 newstate="".join(result);assert newstate.count("TASK-016-P7 当前状态progress-v")==1
 report=(ROOT/REPORT).read_text()
 report=re.sub(r"状态：In Progress（未完成）。当前权威截面progress-v26（[^）]+）；阶段决定agent_delegated，非human_reviewed。","状态：In Progress（未完成）。当前权威截面progress-v27（"+at+"）；阶段决定agent_delegated，非human_reviewed。",report,count=1)
 report=report.replace("以下20项原始问答对应progress-v21截面，新增R12进展见本文末尾；","以下20项原始问答明确保留为progress-v21历史截面，v22–v27增量见本文末尾；当前预算与阶段以最新截面为准。")
 report+="\n\n## progress-v27：三份公开 ACS SI 原件、科学待定与冻结输入恢复\n\n"
 report+="本轮 source-level scientific admission 0、fresh C=0 / SS=0、完整反应图准入0；科学A/B/E仍0 cell，迁移指标null，真实G7未冻结。三份SI可读不等同三项新闭包，之前三个SS O2肯定研究组仍因历史暴露不计fresh。未降低任何完成硬门。\n\n"
 report+="1. SS-R11补采完成：上轮中断的官方广告SI已取得，1 HTTP、10,660,352字节，仅封存opaque bytes。两份已被R12科学读取的XML没有重新算fresh。\n"
 report+="2. R31/R32公开SI：三篇ACS新题录均获Figshare精确resource DOI/题名/原始文件登记。R31 12 HTTP保存metadata、302及三个已过期签名403；错误XML明确Request has expired、签名寿命10秒。R32按事前恢复合同对同一官方下载入口第二次尝试，并在同一进程内先登记实际Location再立即读取，6 HTTP获3 PDF，无登录、签名修改或自动跳转。大小/MD5/SHA全匹配，合计6,210,434字节，许可CC BY-NC4.0，原件留本地。\n"
 report+="3. R34科学资格：G5 SHA "+sha(B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G5_FRESH_HOLDOUT_ACQUIRE.json")+" 在SI内容读取前冻结；A3首页3/3题名对应。A4 Poppler与A5 PyMuPDF隔离抽取45页，不读对方最终产物；这仅证明双文本抽取，不冒充双分子图转写或独立化学验证。A6七处caption在两解析器均匹配，并实际查看五页图版。番茄SI显示K/Q与UDP-Glc的单糖质量产物；茶树SI明确苷元Q的O糖基化及组织rutin，P1–P13位点指向缺失正文Figure5；Laportea SI酶动力学受体为K/M/G/Q苷元。三项统一deferred：现有SI未建立冻结SS糖残基O2完整单步反应，整篇论文不存在此反应并未被证明。茶SI p10 K7位点与K3G缩写、p11 K7G的冲突原样保留。\n"
 report+="4. Exposure：原JSONL快照v2仍5175行，增加R33封存15个旧注册G5/G6与102个相关JSON文档，以覆盖仅写在JSON的晚近原件读取登记。字面DOI/PMID未命中不证明图/别名新鲜度；A6完整历史、28内部名称及来源闭包均仍须实际完成。新九条A3/A4/A5科学读取收据已保留，下一epoch永久曝光。\n"
 report+="5. 本轮自身失误及恢复：根执行者补齐R11时向旧G5已绑定的http_ledger/raw_execution追加记录，R33识别2个SHA漂移。R35事前证明原件10/3行前缀恰好匹配旧SHA；先封存完整11/4行字节，再恢复两条旧路径为原冻结bytes。旧G5/G6 manifest字节未动，全部11次实际HTTP通过独立archive和operations保留。R11新custody v2明确替代原role绑定，不将原件和失败删除。17个当前已注册G5/G6链均通过。R33/R34漂移记录是当时历史，最新恢复事实见R35 receipt。\n"
 report+="6. 验证：A11首版65通过/1失败，原因是核算器错误使用运行账本不存在的status字段。v2对实际04:01UTC预算快照中的整个run-ledger SHA核对，66/66通过，214行未变化，0新MCTS。全项目unittest 286/286通过（"+str(log)+"），git diff --check通过。本轮未给低风险采集脚本堆叠镜像单测；验证聚焦真实原件/冻结链/预算/不升格。\n"
 report+="7. 当前物理预算：1105 HTTP、1,231,963,333 bytes；C510 / SS552 / root43 HTTP。article kinds legacy151/expanded158、attachment请求221，含失败与跳转；不等同可用文章/附件数。相对v26净增19 HTTP，其中R11补采1、R31 12、R32 6。此前新建但误名为progress-v22-physical-budget.json的文件实际捕获于04:01UTC，文件保留且不得当旧v22截面；本轮正确命名progress-v27-physical-budget.json。\n"
 report+="8. 待办：继续合法原件与未处理官方表格SI、独立A4/A5分子图/立体/前体及来源别名闭包；完成真正全资格轮次与3路线/连续2轮的饱和审计后方可适用来源停止条件。完整qualification harness v2尚未验证，实际G7 writer已在v23集成；不得重新报告为未集成。模型、scope、搜索参数、旧v7资产与正式运行门槛保持；本轮没有Git commit/push。当前任务继续In Progress。\n\n"
 report+="本轮机器证据："+str(R/"A6/scientific_SI_dispositions.json")+"；"+str(R35path())+"；"+str(A11)+"；outputs/task016-p7/v1/report_snapshots/progress-v27-physical-budget.json。旧REPORT/STATE逐字节归档于"+str(ARCH)+"。\n"
 write(T,str(REPORT),report);write(T,str(STATE),newstate)
 data=dict(task=T,progress="progress-v27",prior_progress="progress-v26",at=at,status="In Progress",reviewed_status="agent_delegated_not_human",prior_documents_SHA=prior,report_SHA=sha(REPORT),state_SHA=sha(STATE),source_HTTP_delta=19,source_HTTP_global=1105,source_bytes_global=1231963333,new_public_ACS_SIs=3,new_SI_PDF_bytes=6210434,R11_extra_opaque_SI_bytes=10660352,original_SI_front_verified=3,independent_text_pages_each=45,scientific_sources_deferred=3,new_qualified_reaction_graphs=0,source_groups_formally_fresh_C=0,source_groups_formally_fresh_SS=0,independent_source_level_SS_O2_evidence_groups_total=3,scientific_ABE_cells=0,metrics=None,real_G7=False,source_saturation_proven=False,old_frozen_input_drift_restored=2,all_physical_records_preserved=True,registered_stage_chains_verified=17,A11_v1_pass=65,A11_v1_fail=1,A11_v2_pass=66,A11_v2_fail=0,A11_v2_SHA=sha(A11),full_test_log_path=str(log),full_test_log_SHA=sha(log),unit_tests_total=286,unit_tests_passed=286,git_diff_check=True,git_commit_push=False,full_qualification_harness_v2_validated=False,R34_G6_SHA=sha(B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G6_IDENTITY_STRUCTURE_ADMIT.json"),R35_restoration_SHA=sha(R35path()),budget_snapshot_SHA=sha(B/"report_snapshots/progress-v27-physical-budget.json"),legacy_run_ledger_SHA_unchanged=True)
 put(SN,data)
 print(json.dumps(dict(progress="v27",report_SHA=sha(REPORT),state_SHA=sha(STATE),fresh_C=0,fresh_SS=0,task_complete=False)))
def R35path():return B/"governance/R35-frozen-input-exact-restoration-v1/restoration_receipt.json"
if __name__=="__main__":main()
