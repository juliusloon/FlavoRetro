"""Archive TASK-016-P7 progress-v20 with science-screen and supersession evidence."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain

TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REP=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md");PRIOR=B/"report_snapshots/progress-v20-inputs/prior_documents"
V19=B/"report_snapshots/progress-v19.json";V17=B/"report_snapshots/progress-v17.json"
R8=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
VFAIL=B/"verification-v20-ss-r8/independent_R8_verification.json"
VPASS=B/"verification-v20-ss-r8-v2/independent_R8_verification.json"
PRESERVED=B/"verification-v20-ss-r8/error-preservation/original_test_task016_p7_g5_binding_repair.py"
TEST=Path("tests/test_task016_p7_g5_binding_repair.py")
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def main():
 if (ROOT/B/"report_snapshots/progress-v20.json").exists():raise RuntimeError("V20_ALREADY_ARCHIVED")
 prior=load(V19);v17=load(V17);a=load(R8/"A6/source_scope_reconciliation.json")
 passed=load(VPASS);failed=load(VFAIL)
 if sha(REP)!=prior["current_REPORT_sha"] or sha(STATE)!=prior["current_STATE_sha"]:
  raise RuntimeError("REPORT_STATE_PRIOR_DRIFT")
 if passed["passed"]!=18 or passed["failed"]!=0 or failed["failed"]!=1:
  raise RuntimeError("AUDIT_NOT_HONESTLY_CLOSED")
 if a["counts"]["processed"]!=2 or a["counts"]["fresh_admitted"]!=0:
  raise RuntimeError("UNEXPECTED_QUALIFICATION")
 if sha(PRESERVED)!=v17["evidence_SHA"][str(TEST)] or sha(PRESERVED)==sha(TEST):
  raise RuntimeError("V17_TEST_SUPERSESSION_UNPROVEN")
 for stage,path in (("G4_SCOPE_FREEZE",G4),("G5_FRESH_HOLDOUT_ACQUIRE",G5),("G6_IDENTITY_STRUCTURE_ADMIT",G6)):
  if verify_stage_chain(ROOT/path,sha(path))["stage"]!=stage:
   raise RuntimeError("STAGE_CHAIN_INVALID")
 logs=sorted((ROOT/"operations").glob("command-*.log"),key=lambda x:int(x.stem.split("-")[1]))
 def find(label,suffix):
  match=[p for p in logs if label in p.read_text(errors="replace") and suffix in p.read_text(errors="replace")]
  if not match:raise RuntimeError("MISSING_LOG "+label)
  return Path("operations")/match[-1].name
 focused=find("Ran 8 tests","OK");test_pass=find("Ran 268 tests","\nOK")
 test_fail=find("Ran 268 tests","FAILED (failures=1, errors=1)")
 audit_fail=find("INDEPENDENT_R8_FAILED","RuntimeError")
 oldreport=(ROOT/REP).read_text();oldstate=(ROOT/STATE).read_text()
 for path,content in ((REP,oldreport),(STATE,oldstate)):
  dst=PRIOR/path
  if (ROOT/dst).exists():raise RuntimeError("ARCHIVE_EXISTS")
  write(TASK,str(dst),content)
  if sha(dst)!=sha(path):raise RuntimeError("SNAPSHOT_BYTES_CHANGED")
 ts=datetime.now(timezone.utc).isoformat()
 report_add=f"""
## progress-v20：SS-E02 R8 正式预登记原件科学筛查与 G6 零准入（{ts}）

本节是progress-v19后新进展，旧文档和SHA原字节另行存档。此前的R4 metadata-only G5 不被改写或追认为科学授权。本次A0先以冻结G4为直接父阶段，核验scope SHA、R5真实原件SHA、R6 A3出版身份及R6 A6的unknown历史别名条件；在两篇原件科学正文首次读取之前，永久预登记PMC5517534和PMC13387883两篇为开发科学曝光。再生成独立R8 G5阶段清单并进行真实门控，追加非回填的阶段注册行。两篇来源今后不再可以作为fresh holdout重新使用，原G4/scope与既有stage不更改。

A4与A5使用两个隔离进程和不同正文解析逻辑，分别读取同样两份SHA绑定的公开原始XML，只输出文本证据指针、段落hash及审查状态，不读取对方产物、模型结果，也不手写猜测复杂结构。A4对于PMC13387883、PMC5517534各覆盖79、61个正文段落。独立A5核查章节、图注与糖基化位点线索。A6对原文body/p14、p17、p18和p35、p36、p46重读核验后，作出严格区分：

第一，茶树PMC5517534（CsUGT75L12）确实提出黄酮3-O-glucoside可以作为糖受体，产生黄酮3,7-di-O-glycoside，但报告新加糖的位点是黄酮母核7-hydroxy，而不是既有糖残基O2，因此不适用当前SS-E02 Petunia糖间O2冻结scope。第二，康乃馨PMC13387883在转基因背景观察到sophoroside、rutinoside等代谢物升高，并讨论黄酮3-O初始糖基化，但未提供足以证明该酶直接催化糖残基O2再糖基化的完整酶促反应证据；维持当前反应来源资格pending，而非声称论文不存在其他糖间化学。茶树原文段落14的kaempferide/kaempferol命名差异未被擅自同一化。科学资格2 processed、0 admitted：1 source screened-out for O2 scope，1 source deferred；成功closure groups0、fresh0。A6结果SHA绑定并创建G6零准入阶段，完整双图/立体/供体结构资格不曾达成，禁止进入G7/G8/新bankG9。

新R8专门合同测试8/8通过（{focused}）。第一次A11独立审计出现大小写敏感标签程序失误，17/18而非18/18（{audit_fail}），第一次全套268项测试出现1 failure+1 error：旧R4登记修复测试错误地把新增R8的G5当成“最新即R4”的历史记录（{test_fail}）。两种失败及原始程序完整保留在verification-v20-ss-r8和error-preservation。修正版A11仅修正7_O标签判定，另开验证目录，从原始XML独立重核6个段落hash，18/18通过（{VPASS}）。可变R4测试源按批次显式固定旧登记对象，旧代码先存历史SHA字节（其SHA与progress-v17旧引用完全一致）；这一变动为可解释的测试代码版本修订，并非改写冻结科学证据。重跑全量268/268 OK（{test_pass}）。

本批没有新增HTTP或MCTS；物理来源预算沿用progress-v19的最新截面973 HTTP / 1,210,583,689 bytes。C和SS两轴fresh仍0，科学A/B/E均0 cell、metrics=null。没有形式上的人审、正式盲测或独立化学结构验证；Roadmap P2及TASK-016-P7仍In Progress。下一步必须取得和审查真正证明糖残基O2再糖基化的独立未暴露原件，并对C轴推进同样的G5-A3-A4/A5-A6闭包，满足每轴至少6targets/2closure groups才可进入预注册科学实验。本轮未Git提交或推送。证据索引：outputs/task016-p7/v1/report_snapshots/progress-v20.json。
"""
 state_add=f"""
2026-10-11 TASK-016-P7 progress-v20（{ts}）：SS-E02-R8新G5按G4及原件SHA前置冻结，PMC5517534/PMC13387883在科学正文首次读取前永久暴露登记。A4/A5隔离原件文本审查、A6凭XML段落裁定：茶树为黄酮母核7-O新糖、不满足糖残基O2；康乃馨sophoroside等代谢物积累不能证明酶直接催化糖间O2，保留待定。新G6 2来源0准入，2个来源永久曝光不可再复用fresh。专项8/8、A11改正后18/18、全量268/268通过；此前A11 17/18与全量268的1fail1error及测试源v17旧SHA均保留有解释的独立版本快照。新HTTP0/MCTS0，总账最近973HTTP/1,210,583,689B。C/SS fresh0、科学A/B/E0cell/metricsnull、G7/G8/G9未完成；Roadmap P2和P7持续In Progress。结果与原始报告字节索引outputs/task016-p7/v1/report_snapshots/progress-v20.json，未Git同步或升级human_reviewed/release。
"""
 write(TASK,str(REP),oldreport+report_add)
 write(TASK,str(STATE),oldstate+state_add)
 evidence=[V19,V17,G4,G5,G6,R8/"pre_read_exposure.json",
   R8/"A0_science_read_precontract.json",
   R8/"A4/pre_execution.json",R8/"A4/source_body_screen.json",
   R8/"A5/pre_execution.json",R8/"A5/independent_body_scope_screen.json",
   R8/"A6/pre_execution.json",R8/"A6/source_scope_reconciliation.json",
   VFAIL,VPASS,PRESERVED,TEST,
   B/"verification-v20-ss-r8/error-preservation/original_task016_p7_ss_r8_a11_verify.py",
   test_pass,test_fail,focused,audit_fail,
   Path("scripts/task016_p7_ss_r8_a0_preregister.py"),
   Path("scripts/task016_p7_ss_r8_a4_screen.py"),
   Path("scripts/task016_p7_ss_r8_a5_screen.py"),
   Path("scripts/task016_p7_ss_r8_a6_reconcile.py"),
   Path("scripts/task016_p7_ss_r8_a11_verify.py"),
   Path("scripts/task016_p7_ss_r8_a11_verify_v2.py"),
   Path("tests/test_task016_p7_ss_r8_science_screen.py")]
 manifest={"task":TASK,"version":"progress-v20","timestamp":ts,
  "status":"In Progress","approval":"agent_delegated",
  "prior_REPORT_SHA":sha(PRIOR/REP),"prior_STATE_SHA":sha(PRIOR/STATE),
  "current_REPORT_SHA":sha(REP),"current_STATE_SHA":sha(STATE),
  "evidence_SHA256":{str(p):sha(p) for p in evidence},
  "new_G5_SHA":sha(G5),"new_G6_SHA":sha(G6),
  "original_sources_scientifically_screened":2,
  "permanently_exposed_sources":2,
  "source_screen_disposition":{"outside_frozen_scope":1,"source_reaction_deferred":1,"fresh":0},
  "old_v17_test_SHA":v17["evidence_SHA"][str(TEST)],
  "preserved_original_test_SHA":sha(PRESERVED),
  "current_updated_test_SHA":sha(TEST),
  "old_test_current_sha_discrepancy_explained":True,
  "old_A11_failed":1,"new_A11_passed":18,
  "old_full_suite_failure_preserved":True,"new_full_suite_passed":268,
  "new_HTTP":0,"new_MCTS":0,"last_budget":{"HTTP":973,"bytes":1210583689},
  "fresh_C":0,"fresh_SS":0,"scientific_ABE_cells":0,"metrics":None,
  "task_completed":False,"no_git_sync":True}
 write(TASK,str(B/"report_snapshots/progress-v20.json"),
   json.dumps(manifest,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"version":"progress-v20","archived":True,
   "evidence_sha_count":len(evidence),"report_sha":sha(REP),"state_sha":sha(STATE),
   "A11_passed":18,"full_suite_passed":268,"task_status":"In Progress"},ensure_ascii=False))
if __name__=="__main__":main()
