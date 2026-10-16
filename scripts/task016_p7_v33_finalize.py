"""v33 document repair and evidence snapshot; preserves every earlier byte archive."""
import json,re,sys,hashlib
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,now,lines
T="TASK-016-P7"; B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"); STATE=Path("STATE.md")
def main():
 ap=Path(sys.argv[1]); audit=load(ap)
 passed=int(sys.argv[2]); failed=int(sys.argv[3]); assert passed>0 and failed==0 and audit["agent_role"]=="A11"
 old=load(B/"report_snapshots/progress-v32.json")
 assert sha(REPORT)==old["report_sha256"] and sha(STATE)==old["state_sha256"]
 assert not (ROOT/B/"report_snapshots/progress-v33.json").exists()
 budget=B/"report_snapshots/progress-v33-physical-budget.json"; bs=load(budget)
 assert bs["totals"]["HTTP"]==1210 and bs["totals"]["bytes"]==1243067262
 before={str(p):sha(p) for p in (REPORT,STATE)}
 for p in (REPORT,STATE):
  dest=B/"report_snapshots/progress-v33-inputs/prior_documents"/p.name
  assert not (ROOT/dest).exists()
  write(T,str(dest),(ROOT/p).read_text()); assert sha(dest)==before[str(p)]
 at=now(); r=(ROOT/REPORT).read_text(); s=(ROOT/STATE).read_text()
 start="## 合同要求的 20 项直接回答\n"; end="## 验证、偏差与尚待执行\n"
 historical=r[r.index(start):r.index(end)]
 r=re.sub(r"^状态：In Progress.*$",f"状态：In Progress（未完成）。当前权威截面progress-v33（{at}）；阶段决定agent_delegated，非human_reviewed。",r,count=1,flags=re.M)
 oldintro=r.splitlines()[3]; assert "以下20项" in oldintro
 intro="C/SS G4均已冻结，合格fresh仍0/0，科学A/B/E 0 cell、迁移指标null，Roadmap P2尚未关闭。本轮取得两篇历史来源的PMC主文HTML，核对原文首页并完成双路文本提取；历史排除保留，未增加fresh。以下20项问答是progress-v21历史截面，其数字和‘当前’字样仅指当时；v22–v33增量见文末。当前事实只以首头最新版本、本文对应最新增量及同版本snapshot为准。旧REPORT/STATE完整字节归档，历史截面不覆盖最新预算。"
 r=r.replace(oldintro,intro,1)
 r=r.replace("## 实际改动与证据入口\n","## 实际改动与证据入口（progress-v21历史摘要）\n",1)
 oldtest="最新既有全量测试为SS-R8时点268/268通过，不声称覆盖此后所有新资产。R8 A11改正后18/18、旧失败保留。名字gate v4独立20/20是有界工程探针；prospective policy A12 8pass/0fail/2pending是政策边界审核。当前文件SHA重放与源码hash固定属于工程验证，不冒充独立化学审核。"
 newtest="最新已完成全量测试为v32时点operations/command-5169.log的286/286通过（v31另有command-5159.log的286/286）；v33未重跑全套，新增原件流程以本轮独立审计验证，不外推旧全量测试覆盖。R8的268项及其A11改正18项属于历史证据。名字gate v4的20探针与prospective policy A12 8pass/0fail/2pending均是有界工程/政策验证，不能替代实际28名称candidate审查或独立化学验证。"
 assert r.count(oldtest)==1; r=r.replace(oldtest,newtest,1)
 r=r.replace("## 历史修订与增量（原日期保留，当前结论以上文为准）","## 历史修订与增量（各版保留原时点，当前以最新明确版本及snapshot为准）",1)
 section=f"""
## progress-v33：两篇历史主文取得与当前状态入口修复（{at}）

整体仍 **In Progress / agent_delegated**。本轮关闭两个具体主文访问缺口，未得到新的合格留出；C/SS fresh=0/0、科学A/B/E 0 cell、metrics=null，真实G7/G8/新bank G9仍未形成。

1. **真实原件入口。** R66首次请求官方canonical PMC文章页：PMC2709393（10.1074/jbc.M109.009258）和PMC7720146（10.1073/pnas.2012745117），均HTTP200，共412,990字节。原HTML字节及SHA只读保全；没有重试已满额EPMC全文API或既存BioC错误地址，没有绕过登录/验证码。R67仅核原文head题录；Crossref与原文的DOI、规范化题名、明确期刊别名、年/卷/期/首页面及canonical PMCID自链接均通过。原始日期保留，不将上线日期差异抹平。A3首版因内联C标签和期刊leading-The字面差异待定，原版保留，v2只补可审计的文字归一化与两组明确期刊别名。
2. **G5先于正文读取。** R68先固定两份原HTML、A3 v2、prior-v4及两个解析代码；之后A4/A5在不同进程读取。69/102个选定段落、标题、表格和图注标签文本块分别严格相等，原重复图注保留；未解码或转写图中分子图，未获取补充件，不宣称完整化学反应枚举或独立结构转写。A5首次foundation解释器缺lxml，在任何读取receipt前失败；原代码不改，system解释器成功，失败日志保留。
3. **科学分母与历史排除。** 所核具体实验路径：2009论文OsCGT/小麦CGT作用于活化2-羟基黄烷酮/开链互变异构体，之后脱水得到黄酮6C/8C端点；2020论文CGTa/CGTb在2-羟基中间体上顺序作用，主要分别使用UDPGlc/UDPAra，酸脱水产生二C端点。这些指认路径不能当成冻结的直接flavone C6反应，也不据此声称整篇无其他反应。两源仍命中SHA绑定prior/design保守排除；旧ledger的scientific_content_read=null保持unknown，不能改写成历史正文已读。A6按fresh角色处理2项、排除2项，source-bound完整图准入0、新独立fresh组0。G6已固定，新增12条按来源导出的永久读取事件；不把事件数、端点名称或原件取得数计入fresh。本批不是strict full-qualification v3完整科学轮，不计来源饱和。
4. **阶段账口径明确。** 两轴G4/scope原SHA与完整214行MCTS账SHA不变。当前全登记40行/38个唯一路径；其中29行显式status=active，去重27条G5/G6链通过。另11个旧C R1/R2/R3/R4/R5/R7注册未填写status，单列保留，不称为已active、已superseded或已注销。这里27只代表显式active子集，不代表全部历史阶段。进入最终G7前仍须解释全部相关来源/读取闭包，不能靠该筛选省略历史暴露。
5. **具名缺口与下一批分开。** v32的16项具名分母保留；其中2项主文HTML访问缺口已关闭，剩14项原件/访问事项（C6/SS8）。两已得主文未获完整化学资格。A1对原95题名及既有曝光/HTTP核对，交付5个条件酶学题录、10个待执行metadata查询；未新请求、未读取摘要/正文/图、不是5个C6合格来源。A2对SS四个较新DOI核对20条白名单投影、16个metadata原件和36个历史请求，没有在保存元数据中发现新的公开主文/作者稿/机构库地址，保留4项pending/unknown；不宣称全部合法渠道已耗尽。
6. **独立验证与文档修复。** A11 {passed}/{passed}通过，独立复核原件、A3归一化、双进程/时序、历史排除、显式active链与MCTS账；属于原件/工程/证据边界审核。A12前审31项为22pass/6文档问题/3pending，原件保留。修复REPORT首头版本时间、历史索引、最新测试标识和权威优先级；20问答整块字节保持。STATE原三条自称当前的v30/v31/v32完整归档，现仅保留一条v33。full-qualification v3已实现并验证真实deferred文档路径，qualified真实准入路径及完整科学round仍未证明。修后A12另存后审，不覆盖前审失败。
7. **物理预算与失败保留。** 当前1210 HTTP/1,243,067,262字节，相对v32新增2 HTTP/412,990字节；C604/SS563/root43，legacy article请求165/expanded172、attachment233、失败或跳转248，均不是有效论文/反应数。新预算SHA绑定，旧预算和失败不回写。恢复时旧A11重复启动被不可变输出assert拒绝，0HTTP、未覆写既有67/67结果。SS侦察一次误把已过期SI签名URL写入本地命令stdout，原日志和披露保留，后续仅输出host/path及URL SHA，未新增该URL请求。首版v33文档生成器因字符串引号嵌套语法错误在任何写入前失败，随后追加可执行生成器，不覆盖原日志。
8. **未满足的验收。** 未新增MCTS，未改核心runtime、scope、模型、PUCT或库存；v33未重跑全套，继承v32的286项已完成测试，新增解析以本轮独立审计验证。每轴>=6个完整、同域、无泄漏新目标/>=2组、全28名称/历史别名闭包、完整reference静态适用、真实A/B/E三seed及零reference loss均仍待完成，Roadmap P2未关闭。来源硬预算未触及、来源饱和未建立；无commit/push、人审或formal/release升格。

证据：[R66原件保管](../../outputs/task016-p7/v1/C/E02/fresh/C-E02-R66-canonical-PMC-HTML-custody-v1/raw_custody_summary.json)；[A3 v2](../../outputs/task016-p7/v1/C/E02/fresh/C-E02-R67-two-PMC-original-identity-v1/A3_original_front_identity.v2.json)；[R68 A6](../../outputs/task016-p7/v1/C/E02/fresh/C-E02-R68-two-historical-PMC-science-v1/A6/scientific_reconciliation_completed.json)；[16项访问更新](../../outputs/task016-p7/v1/verification-v33-known-source-intake-update/named_original_access_update.json)；[A11](../../{ap.as_posix()})；[A12前审](../../outputs/task016-p7/v1/verification-v33-current-document-audit/A12_pre_repair_findings.json)；[物理预算](../../outputs/task016-p7/v1/report_snapshots/progress-v33-physical-budget.json)。旧v32 REPORT/STATE完整字节归档于report_snapshots/progress-v33-inputs/prior_documents。
"""
 r+=section; assert r[r.index(start):r.index(end)]==historical
 current=f"TASK-016-P7 当前状态progress-v33（{at}）：In Progress / agent_delegated。C/SS G4/scope原SHA不变，fresh仍0/0，科学A/B/E 0 cell、metrics=null，G7/G8/新bank G9未形成，Roadmap P2未关闭。R66首次canonical PMC HTML两次200，取得PMC2709393/PMC7720146主文412,990字节；R67 A3 v2书目归一化后2项身份通过，原v1待定保留。R68先冻结G5，A4/A5两进程69/102文本块一致，A6保留prior/design保守排除2项（旧正文读取null仍unknown），完整图/fresh增量0；不把2-羟基中间体后脱水端点当冻结直接C6，也不否定整篇。16项具名分母中主文访问关闭2，剩14项C6/SS8；完整化学资格未授予。A1交付5候选/10待执行metadata计划，A2四源无新增已证公开地址。累计1210 HTTP/1,243,067,262字节，本轮+2/+412,990；40登记/38唯一路径，显式active29行/27唯一链通过，11旧C注册status未填另列，不能称已注销。MCTS214行完整SHA不变，A11 {passed}/{passed}。三条当前状态与REPORT优先级已修，20问答历史字节保留；A12前审6文档问题原件保留，修后另审。继承v32全量286/286，本轮未重跑；依赖/归一化/不可变输出拒绝等失败均保留。不计完整科学round/饱和，不降低每轴>=6目标/>=2组及真实A/B/E硬门，无Git提交推送或更高科学升格。权威证据见REPORT-016-P7 progress-v33及outputs/task016-p7/v1/report_snapshots/progress-v33.json。"
 oldlines=[x for x in s.splitlines() if x.startswith("TASK-016-P7 当前")]; assert len(oldlines)==3
 output=[]; replaced=False
 for line in s.splitlines():
  if line.startswith("TASK-016-P7 当前"):
   if not replaced:output.append(current);replaced=True
  else:output.append(line)
 s="\n".join(output)+"\n"
 write(T,str(REPORT),r); write(T,str(STATE),s)
 snap=dict(task=T,progress="progress-v33",prior_progress="progress-v32",at=at,status="In Progress",approval_type="agent_delegated",human_reviewed=False,report_SHA=sha(REPORT),state_SHA=sha(STATE),prior_documents_SHA=before,twenty_historical_answers_SHA=hashlib.sha256(historical.encode()).hexdigest(),budget=dict(path=str(budget),sha256=sha(budget)),source_HTTP_global=1210,source_bytes_global=1243067262,source_HTTP_delta=2,source_bytes_delta=412990,A11=dict(path=str(ap),sha256=sha(ap)),A11_pass=passed,A11_fail=failed,A12_pre_repair=dict(path=str(B/"verification-v33-current-document-audit/A12_pre_repair_findings.json"),sha256=sha(B/"verification-v33-current-document-audit/A12_pre_repair_findings.json")),A12_postrepair_pending_at_snapshot=True,new_main_original_HTML=2,new_original_front_identities_passed=2,historical_source_text_blocks=[69,102],historical_source_fresh_exclusions=2,prior_scientific_read_unknowns_retained=True,known_intake_denominator=16,original_access_gaps_closed=2,remaining_named_original_access_items=14,C_metadata_candidate_plans=5,C_metadata_queries_not_executed=10,SS_metadata_sources_reconciled=4,SS_new_saved_metadata_supported_open_routes=0,new_independent_fresh_groups=0,explicit_active_registered_unique_G5_G6=27,total_registration_rows=40,total_unique_registered_stage_paths=38,old_C_registrations_without_status=11,new_complete_chemical_records=0,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,new_MCTS=0,MCTS_run_ledger_rows=214,MCTS_run_ledger_SHA=sha(B/"run_ledger.jsonl"),real_G7=False,real_G8=False,real_new_bank_G9=False,source_saturation_established=False,eligible_as_source_saturation_complete_round=False,source_hard_budget_reached=False,inherited_unit_tests_passed=286,inherited_full_test_log_path="operations/command-5169.log",inherited_full_test_log_SHA=sha(Path("operations/command-5169.log")),full_suite_rerun_this_turn=False,chemical_independent_validation=False,core_runtime_scope_modified=False,git_commit_push=False)
 put(B/"report_snapshots/progress-v33.json",snap)
 print(json.dumps(dict(report_SHA=snap["report_SHA"],state_SHA=snap["state_SHA"],snapshot_SHA=sha(B/"report_snapshots/progress-v33.json"),A11_pass=passed,source_HTTP=1210)))
if __name__=="__main__":main()
