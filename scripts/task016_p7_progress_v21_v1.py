"""Consolidate current P7 status while archiving the exact v20 documents."""
import hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
TASK="TASK-016-P7"
B=Path("outputs/task016-p7/v1")
REP=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
ST=Path("STATE.md")
OUT=B/"report_snapshots/progress-v21.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/OUT).exists():raise RuntimeError("v21 already exists")
 assert sha(REP)=="15a5f8702d3ae51cfebb92df46cf9928776429b3d514b9d09ef5a8cfc8a7e764"
 assert sha(ST)=="ea432f232a6d5b5ce1952e58def5c87c8a198b4d6c566b93f398fc2dcdb9aa65"
 oldrep=(ROOT/REP).read_text();oldstate=(ROOT/ST).read_text()
 archive=B/"report_snapshots/progress-v21-inputs/prior_documents"
 for p,t in [(REP,oldrep),(ST,oldstate)]:
  assert not (ROOT/archive/p).exists()
  write(TASK,str(archive/p),t);assert sha(archive/p)==sha(p)
 fixed=[
  B/"report_snapshots/progress-v20.json",
  B/"report_snapshots/progress-v21-physical-budget.json",
  B/"C/E02/fresh/C-E02-R10/role_A2_raw_only_manifest.json",
  B/"C/E02/fresh/C-E02-R11/role_A2_raw_only_manifest.json",
  B/"C/E02/fresh/C-E02-R11/A1_prior_route_full_round_and_stop_condition_audit_v1.json",
  B/"SS/E02/fresh/SS-E02-R9-access-completion-v1/role_A2_raw_only_manifest.json",
  B/"SS/E02/fresh/SS-E02-R9-access-completion-v1/R5_access_gap_clarification.json",
  B/"SS/E02/fresh/SS-E02-R9-access-completion-v1/final_verification.json",
  B/"governance/named_exposure_gate_A8_v1/A8_independent_named_gate_validation.json",
  B/"governance/named_exposure_gate_A8_v3/A8_independent_named_gate_validation.json",
  B/"governance/named_exposure_gate_A8_v4/A8_independent_named_gate_validation.json",
  B/"governance/named_exposure_gate_A8_v4/role_A8_manifest.json",
  B/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json",
  B/"governance/named_exposure_gate_v1/role_A0_manifest.v4.json",
  B/"governance/current_epoch_evaluation_exposure_policy_v1/agent_delegated_prospective_decision.json",
  B/"governance/current_epoch_evaluation_exposure_policy_A12_v1/A12_bounded_prospective_policy_validation.json",
  B/"governance/current_epoch_evaluation_exposure_policy_A12_v1/role_A12_manifest.json",
  B/"epochs/C-E02/epoch_state.v9.json",B/"epochs/SS-E02/epoch_state.v6.json",
  Path("scripts/task016_p7_named_exposure_gate_v4.py")]
 for p in fixed:assert (ROOT/p).is_file(),str(p)
 a8=load(fixed[10]);assert len(a8["checks"])==20 and all(x["status"]=="passed" for x in a8["checks"])
 budget=load(fixed[1]);n=budget["totals"]["HTTP"];nb=budget["totals"]["bytes"];asof=budget["capture_finished_at"]
 rows=[json.loads(x) for x in (ROOT/B/"run_ledger.jsonl").read_text().splitlines() if x]
 terminal=[x for x in rows if x.get("status") in ["ok","error"]]
 assert len(rows)==214 and len(terminal)==107
 assert sum(x["execution_source"]=="live_aizynthfinder_mcts" for x in terminal)==91
 assert sum(x["execution_source"]=="live_attempt_failed" for x in terminal)==16
 answer_text=oldrep.split("## 合同要求的 20 项直接回答\n\n",1)[1].split("## 验证、偏差与尚待执行",1)[0]
 parts=re.split(r"(?m)^(?=\d+\. \*\*)",answer_text)
 answers={}
 for p in parts:
  m=re.match(r"(\d+)\. ",p)
  if m:answers[int(m.group(1))]=p.strip()
 assert set(answers)==set(range(1,21))
 answers[1]="1. **epoch 数和当前阶段。** C-E01/SS-E01保留development_epoch_incomplete。C-E02的C6范围和SS-E02的Petunia糖残基O2范围均G4冻结、原scope与G4 SHA不变。C六G5/五G6；SS五个不同G5/两个G6（全局11注册行对应10个不同阶段，R4 G5修复追加登记不重复计阶段）。C/SS合格fresh均0，G7/G8/新bank G9未成，科学A/B/E0 cell、指标null。SS-R8两篇已真实科学筛查、0准入，不再可作以后fresh。"
 answers[4]+="\n\nSS-R5取得两篇的四份格式有效原件对象及一份opaque SI；SS-R6只核两篇XML front出版身份，不构成反应资格。R8在G4及正式新G5之后以隔离A4/A5正文审查、A6段落重核完成screen-only批次。其原合同无条件禁止准入的限制保持，不能追认为完整qualification。未来新来源由已批准且经A12边界审核的时间分层规则处理：先固定prior exposure baseline，当前epoch的首次evaluation读取单列；通过全部原门槛才可由A6裁定资格，仍永久禁止下一epoch重用。此政策不是实际准入，也未改变scope或硬门。"
 answers[5]+="\n\nSS9+C16+C3共28条永久命名暴露，27个唯一名字，R7官方PubChem各得单CID和候选图；这些只是候选身份，不是化学同义名确认。未来G7现明确必须调用named_exposure_gate_v4.validate_final_panel：固定真实三ledger、28项逐一官方证据比较、A3/A6角色及全部输出SHA、原>=6/2门均不可关闭。A8同组20探针全过，真实候选的28项身份审核仍0、实际G7 writer尚未接入；未匹配候选图不能代替完整无泄漏判断。"
 answers[6]+="\n\nSS-R6两篇原XML front各10书目项通过，4篇原件缺失仍pending。SS-R9按官方API/显式Location补取4缺件，10 HTTP全部终结、0有效正文，未绕过许可或自动重定向。R5原intake.access_gaps空列表与4篇缺件不一致，R9另立clarification修正解释，保留原bytes/SHA。C-R10十次补取仍0正文/SI。C-R11为metadata-only新发现，不以其212旧提示+196新提示的分流升级任何科学资格。"
 answers[7]+="\n\nSS-R8 A4/A5分别解析两篇原XML；A6重核原段落后裁定PMC5517534是母核7-O新糖而非糖残基O2（outside frozen scope），PMC13387883代谢物积累不足以证明直接糖间O2反应（deferred）。2 processed、0 admitted，不做复杂结构猜测；两篇永久暴露。后者不是对整篇论文所有化学内容的否定。"
 answers[10]="10. **A/B/E cells 与 MCTS/fixture。** 两轴科学迁移A/B/E各0 cell，指标null。当前run_ledger 214行=107预留+107终结，终结91 ok实际MCTS、16 error实际live_attempt_failed；107无待终结。旧progress-v16至v20将这16次写成synthetic fixture的当前摘要已更正，旧文档逐字节归档保留。曾带synthetic_fixture或suite标签的历史原字段不改，按实际execution_source及manifest区分；本次未重新运行搜索，旧能力/工程运行不进入迁移分母。"
 answers[18]=f"18. **预算与时间截面。** 截至{asof}物理账归并为{n} HTTP / {nb:,} B，C {budget['families']['C']['HTTP']}/{budget['families']['C']['bytes']:,} B、SS {budget['families']['SS']['HTTP']}/{budget['families']['SS']['bytes']:,} B、root {budget['families']['root']['HTTP']}/{budget['families']['root']['bytes']:,} B。扩展article请求{budget['totals']['article_expanded']}、附件请求{budget['totals']['attachments']}，均不是有效论文数。非原子append-only捕获窗口及逐账prefix SHA已固定，活动C-R12/SS-R10可在此后继续。原SS漏8次已归一化且不重新请求。全局8000HTTP/8GiB等硬预算不变；当前查询/原件获取不算完整科学轮次，C-R11独立自查支持的完整科学round数0，未满足连续两完整零新增round停止条件，不能宣称饱和。搜索107/600，工程32/60，科学0，均未新增。"
 ts=datetime.now(timezone.utc).isoformat()
 intro=f"""# REPORT-016-P7：领域对齐的新底物迁移闭环
状态：In Progress（未完成）。当前权威截面progress-v21（{ts}）；阶段决定agent_delegated，非human_reviewed。

C/SS G4均已冻结，合格fresh均0，科学A/B/E0 cell、迁移指标null，Roadmap P2尚未关闭。以下20项回答反映当前状态；旧REPORT/STATE完整bytes已归档于outputs/task016-p7/v1/report_snapshots/progress-v21-inputs/prior_documents。历史增量另保留，不作为更新后的预算截面。

## 实际改动与证据入口

- SS-R5/R6/R8：两篇原件身份通过后经隔离科学筛查0准入；母核7-O和糖残基O2分开，代谢物积累与直接酶促反应分开。R8原screen-only限制保留。
- C-R11：三种不同metadata发现路线605观察→408严格提示组，212既有提示/暴露、196新metadata提示；身份和科学均pending。Rhea响应真实字段修正、152分页行/151唯一记录的一条重复保留。
- SS-R9：四篇缺件10次请求、0有效正文；原R5空access_gaps已通过追加澄清更正，不改旧版。
- 名字防泄漏v4：A8同20探针20通过。旧v1五失败、v3两失败均留存；全部声明输出SHA和不可关闭面板硬门已补。真实28项candidate审查0，尚无实际G7。
- 未来full-qualification政策：固定prior/design exposure与current-evaluation时间层，保留下一epoch永久曝光。A12 8通过/0失败/2待执行；当前不增加资格。
- 当前C-R12合法原件获取、SS-R10三路线题录发现与未来fullbatch入口实现仍进行中，不能写为已完成。

## 合同要求的 20 项直接回答

"""
 verify="""## 验证、偏差与尚待执行

最新既有全量测试为SS-R8时点268/268通过，不声称覆盖此后所有新资产。R8 A11改正后18/18、旧失败保留。名字gate v4独立20/20是有界工程探针；prospective policy A12 8pass/0fail/2pending是政策边界审核。当前文件SHA重放与源码hash固定属于工程验证，不冒充独立化学审核。

继续从新题录取得公开原件，在正式full-qualification G5固定时间层和prior exposure后做A3、隔离双抽取/A6；28名字未解、来源/图/供体/立体/reference/closure/适用缺口一律pending。每轴>=6 targets/>=2 closure groups且全部门槛通过后才G7/G8/新bank G9及真实A/B/E；当前未满足来源停止条件。无Git commit/push/tag/release。

## 历史修订与增量（原日期保留，当前结论以上文为准）

"""
 hist=oldrep.split("## 执行中修订记录",1)[1]
 write(TASK,str(REP),intro+"\n\n".join(answers[i] for i in range(1,21))+"\n\n"+verify+hist)
 marker="TASK-016-P7 既有固定截面"
 assert oldstate.count(marker)==1
 statecurrent=f"""TASK-016-P7 当前状态progress-v21（{ts}）：In Progress/agent_delegated。C-E02 C6和SS-E02 Petunia糖残基O2范围G4冻结、SHA不变；C六G5/五G6，SS五个不同G5/两个G6。SS-R8两篇隔离科学筛查0准入：茶树是母核7-O而非糖O2，康乃馨直接糖O2反应未获足够证据；旧screen-only限制与永久曝光保留。C-R11三路线metadata发现408组=212既有+196新提示，全部身份/科学pending；SS-R9四缺件10HTTP/0正文，R5旧空gap另行澄清。28永久名字暴露有27官方CID候选但0实际化学身份审查；未来G7固定v4 gate，A8 20/20有界工程通过，真实G7 writer未接线。前瞻fullqualification政策A12 8pass/0fail/2pending，未追认R8、未改变scope/门槛。C/SS fresh0、科学A/B/E0 cell/metricsnull、G7/G8/新bank G9未成，Roadmap P2未关闭。物理预算截至{asof}为{n}HTTP/{nb}B，后续采集另记；run ledger107终结=91真实MCTS成功+16实际启动失败，旧误记fixture已归档更正、0新增搜索。最近全量268通过限于R8时点，名字gate与政策另有有界验证，不冒充当前整体科学闭环。当前C-R12/SS-R10和fullbatch入口实现继续，尚无完整科学round饱和证据。REPORT及前STATE原字节/证据SHA在report_snapshots/progress-v21；人审/独立化学/formal/release未升级、未Git同步。

下一步：完成新来源合法获取、G5先行时间分层与A3/隔离A4-A5/A6/28名字及完整结构闭包资格。各轴至少6新底物/2组、完整同域零泄漏之后才能冻结最终面板并运行真实矩阵。来源/访问停止条件按原合同，不以题录或访问批次替代完整科学轮次。
"""
 write(TASK,str(ST),oldstate.split(marker)[0]+statecurrent)
 snapshot={"task_id":TASK,"version":"progress-v21","timestamp":ts,"approval_type":"agent_delegated","human_reviewed":False,"status":"In Progress","prior_REPORT_SHA":sha(archive/REP),"prior_STATE_SHA":sha(archive/ST),"current_REPORT_SHA":sha(REP),"current_STATE_SHA":sha(ST),"evidence_SHA256":{str(p):sha(p) for p in fixed},"source_budget_asof":asof,"source_budget":budget["totals"],"search_terminal":107,"actual_MCTS_ok":91,"actual_live_attempt_failed":16,"corrected_old_summary_fixture_claim":True,"new_HTTP_by_this_writer":0,"new_MCTS":0,"fresh_C":0,"fresh_SS":0,"scientific_ABE_cells":0,"metrics":None,"names_A8_probes_passed":20,"names_real_candidate_identity_reviews":0,"prospective_policy_A12":{"passed":8,"failed":0,"pending":2},"active_batches":["C-E02-R12","SS-E02-R10"],"task_completed":False}
 write(TASK,str(OUT),json.dumps(snapshot,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"version":"progress-v21","report_sha":sha(REP),"state_sha":sha(ST),"evidence_files":len(fixed),"fresh_C":0,"fresh_SS":0,"task_completed":False},ensure_ascii=False))
if __name__=="__main__":main()
