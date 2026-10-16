"""Append P7 progress-v22 after genuine SS-R12 A3/G5/A4/A5/G6/A11 closeout.
Preserve prior report/STATE exact bytes; no change to raw/scope/library/runtime.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from scripts.operate import ROOT,write
TASK="TASK-016-P7"
BASE=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
SNAP=BASE/"report_snapshots/progress-v22-inputs/prior_documents"
INDEX=BASE/"report_snapshots/progress-v22.json"
G4=BASE/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=BASE/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=BASE/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G6_IDENTITY_STRUCTURE_ADMIT.json"
SRC=BASE/"SS/E02/fresh/SS-E02-R12-original-science-review-v3"
AUD=BASE/"verification-v22-ss-r12/independent_R12_verification.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def save(p,data):write(TASK,str(p),data)
def main():
 if (ROOT/INDEX).exists():raise RuntimeError("IMMUTABLE_PROGRESS_V22_EXISTS")
 old_report=(ROOT/REPORT).read_text()
 old_state=(ROOT/STATE).read_text()
 assert "当前权威截面progress-v21" in old_report
 assert "TASK-016-P7 当前状态progress-v21" in old_state
 audit=read(AUD);source=read(SRC/"A6/source_scope_reconciliation.json")
 assert audit["passed"]==15 and audit["failed"]==0
 assert source["counts"]["outside_current_O2_scope"]==2 and source["counts"]["fresh_admitted"]==0
 assert sha(G4)=="a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f"
 assert sha(G5)=="69e5bbdf2fa5913e079c9adef03bb3e0b743f1f90bc490a0ade5f95d1fc8a506"
 assert sha(G6)=="0aaba58d18a8ae63022c940e364a195669ff3f0a55ad4ed92f0f551b852349c9"
 t=datetime.now(timezone.utc).isoformat()
 p_r=SNAP/"REPORT-016-P7-prior.md"
 p_s=SNAP/"STATE-prior.md"
 save(p_r,old_report);save(p_s,old_state)
 from scripts.task016_p7_orchestrate import verify_stage_chain
 assert verify_stage_chain(ROOT/G6,sha(G6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
 r_intro="状态：In Progress（未完成）。当前权威截面progress-v21（2026-10-11T02:03:38.939137+00:00）；阶段决定agent_delegated，非human_reviewed。"
 assert r_intro in old_report
 new_report=old_report.replace(r_intro,
    "状态：In Progress（未完成）。当前权威截面progress-v22（"+t+"）；阶段决定agent_delegated，非human_reviewed。",1)
 new_report=new_report.replace("以下20项回答反映当前状态；旧REPORT/STATE完整bytes已归档",
   "以下20项原始问答对应progress-v21截面，新增R12进展见本文末尾；旧REPORT/STATE完整bytes已归档",1)
 append="""

## progress-v22：SS-R12 两篇新原件完成原始身份证据与独立科学范围筛查（"""+t+"""）

本增量在已批准的 TASK-016-P7 约束内执行，审批仍为 agent_delegated，非 human_reviewed。既有 G4/scope、原始 R11 bytes、模型与 MCTS 语义均未修改。progress-v21 的原 REPORT/STATE 原字节及 SHA 保留在 `outputs/task016-p7/v1/report_snapshots/progress-v22-inputs/prior_documents/`。

1. **新增可复核的 G5→G6 阶段成果。** SS-R11 原件采集账本中 PMC5444469（DOI 10.1093/jxb/erw420，Lotus japonicus，155,361B）与 PMC6813240（DOI 10.3389/fpls.2019.01330，Freesia hybrida，159,018B）已经合法取得 XML 原件；另一个 PMC2947185 请求为 HTTP 500，不冒充已取得原件。新 A3 仅解析两篇 XML `front`，与既有 R10 官方 metadata 中 DOI/PMID/PMCID/title/year 对照，2/2 文章出版身份通过，但不以此认证反应。A3 首版/二版因既有 metadata title 类型及 raw pointer 类型不一致分别失败，未抹除；第三版（`SS-E02-R12-original-science-review-v3`）通过并保留失败中间态。

2. **先预登记，再读取正文。** R12 在新 G5 阶段登记两篇原件完整 SHA 与范围 G4 父阶段 SHA，事前永久登记来源科学曝光、禁止下一 epoch 再作 fresh，并要求 A4/A5 隔离进程读相同两份原件、A6 仅在双方产物存在后复核。新增 G5 manifest SHA：`69e5bbdf2fa5913e079c9adef03bb3e0b743f1f90bc490a0ade5f95d1fc8a506`。旧 G4 scope SHA 保持 `c173c0e6aaee7dacfcb9195cbd481577703ecdebcd18aaf506b76b84e74e53b6`，未调范围。

3. **独立科学筛查与原文段落复核。** A4/A5 分别审查 Lotus 原文 88 段和 Freesia 原文 51 段；原始文本/段落 SHA 被记录。Lotus 原文 body/p-40 报告重组 UGT72AD1/UGT72Z2 对黄酮醇苷元产生 3-O 单葡糖苷，body/p-58/69 的糖间连接产物出现在转基因代谢物累积叙述，不能证明两种酶直接把 UDPGlc 接到既有 3-O-糖的 O2。Freesia 原文 body/p-4/23/26 讨论从黄酮醇/花青素苷元开始的 3-O 糖基转移，并非糖残基 O2 再糖基化。A6 将两篇明确裁定为**所核反应不适用当前冻结的 SS-E02 O2 范围**，不是断言论文所有化学反应都不可能有价值。两篇均不构成完整双结构图、供体/立体/闭包合格反应，0 fresh/0 新closure，且永久曝光。新 G6 SHA：`0aaba58d18a8ae63022c940e364a195669ff3f0a55ad4ed92f0f551b852349c9`。

4. **独立与回归验证。** A11 从冻结原始 XML 重算出版前置、两个独立 A4/A5 输入、七个原件段落定位/文本 SHA、G4→G5→G6 阶段链及准入计数，15/15 通过；输出 `outputs/task016-p7/v1/verification-v22-ss-r12/independent_R12_verification.json`。当前 `.venv-foundation` 全量 unittest 重新执行 **268/268 OK**，该测试覆盖既有主回归，新增 R12 完整文件 SHA 由 A11 独立审计覆盖；不宣称形成全新科学矩阵。

5. **同时间段 C-R12 与 SS-R11 来源线进展的真实边界。** C-R12 独立 raw-only 访问整理 20 HTTP、15 项工程/来源文档检查通过，4 个新题录提示与 2 个历史访问缺口均待原件与 A3 科学资格（6 pending，0 已合格原文/SI）；它不是完整科学发现轮次。SS-R11 当前本机账本另记录 10 个 HTTP，包括上述两份 XML 和尚未完成的书目索引查询，成功 metadata 不能代替原始反应。R12 未新增 HTTP/MCTS，整体物理预算需另行统一核对，不能把各批局部账本简单相加作为最新全局总账。

6. **不可升格结论与下一步。** 本轮是真正完成的两篇 **source identity + independent original science + G6 scoped disposition**，但不是正向迁移准入：C/SS 仍 **fresh=0**，科学 A/B/E **0 cell**、metrics=null；G7/G8/科学新bank G9 未完成，Roadmap P2 仍 In Progress。应优先寻找真正提供糖残基 O2 直接酶促糖基化与完整受体/供体/产物位点证据的新的独立原件，并核 28 个永久名字暴露，严格按 G5→A3→双抽取→A6→零泄漏推进，不将已筛除两篇再次当 future-fresh。无 Git commit/push，未提高独立化学、human_reviewed、release 或 formal 状态。

完整证据 SHA 索引：`outputs/task016-p7/v1/report_snapshots/progress-v22.json`。
"""
 new_report+=append
 save(REPORT,new_report)
 start=old_state.index("\nTASK-016-P7 当前状态progress-v21")
 updated=old_state[:start]+"""
TASK-016-P7 当前状态progress-v22（"""+t+"""）：In Progress / agent_delegated。与v21相比，SS-R11 已成功获得2份新 XML 原件，SS-R12 的 A3 对两篇出版身份2/2通过，G5先于科学正文读取且永久曝光登记，独立 A4/A5 分别复核 Lotus 88 段/Freesia 51 段，A6 对原文直接反应证据裁定2篇均属于苷元3-O初始糖基化而非冻结的糖残基O2再糖基化，G6登记0准入；A11 15/15独立核验通过。C-R12另有20HTTP/15工程文档检查通过，但6来源仍全部pending、0合格科学原件/SI；SS-R11账本包含10HTTP与2份有效XML，不能把原始获取当资格。新一轮完整单元测试268/268通过。原SS-R12 A3 v1/v2失败记录保留，v3成功；原 v21 报告与STATE原字节按SHA保留。G4/scope SHA、v7模型/搜索不变，未Git提交推送。

P7 总体科学门仍不关闭：C/SS fresh各0；G7/G8/新bank G9未形成合格终验；科学A/B/E仍0 cell、metrics=null；Roadmap P2未完成。下一步聚焦可合法获得、source-qualified、具有完整受体/供体/产物/糖残基O2及立体与无泄漏闭包的新反应；先满足每轴>=6 targets、>=2 groups，才允许冻结面板并执行科学矩阵。R12不新增MCTS/HTTP，全局预算以单独物理账本归并为准。人审、formal、independent chemical validation、release均未升级。证据见 docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md 的 progress-v22 与 outputs/task016-p7/v1/report_snapshots/progress-v22.json。
"""
 save(STATE,updated)
 snapshot=dict(task=TASK,status="In Progress",version="progress-v22",at=t,
    initial_report_SHA=hashlib.sha256(old_report.encode()).hexdigest(),
    initial_state_SHA=hashlib.sha256(old_state.encode()).hexdigest(),
    prior_documents={str(p_r):sha(p_r),str(p_s):sha(p_s)},
    current_report_SHA=sha(REPORT),current_state_SHA=sha(STATE),
    G4_SHA=sha(G4),G5_SHA=sha(G5),G6_SHA=sha(G6),A11_SHA=sha(AUD),
    original_A3_verified=2,new_scientific_source_screened=2,qualified_fresh_C=0,
    qualified_fresh_SS=0,scientific_ABE_cells=0,metrics=None,
    unittest_passed=268,unit_tests_failed=0,
    no_new_MCTS=True,no_git_commit=True,human_reviewed=False,
    errors_preserved=["R12 A3 v1 title string-vs-list","R12 A3 v2 metadata pointer shape"])
 save(INDEX,json.dumps(snapshot,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(progress="v22",A11_pass=15,unittest=268,report_SHA=sha(REPORT),state_SHA=sha(STATE),G6_SHA=sha(G6))))
if __name__=="__main__":main()

