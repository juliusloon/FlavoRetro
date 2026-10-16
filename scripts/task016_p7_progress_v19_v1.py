"""P7 progress-v19: snapshot v18 REPORT/STATE, append authoritative R7 results."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from scripts.operate import ROOT,write

TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md");PRIOR=B/"report_snapshots/progress-v19-inputs/prior_documents"
V18=B/"report_snapshots/progress-v18.json"
NAME=B/"governance/P7-R7-authoritative-exposed-name-resolution-v1"
GRAPH=B/"governance/P7-R7-exposed-graph-candidate-guard-v1"
VERIFY=B/"verification-v19-exposed-name-resolution/independent_R7_verification.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def main():
 dest=B/"report_snapshots/progress-v19.json"
 if (ROOT/dest).exists():raise RuntimeError("V19_ALREADY_ARCHIVED")
 old=load(V18);v=load(VERIFY);s=load(NAME/"disposition_summary.json")
 g=load(GRAPH/"candidate_graph_guard.json")
 oldr=(ROOT/REPORT).read_text();olds=(ROOT/STATE).read_text()
 if sha(REPORT)!=old["current_REPORT_sha"] or sha(STATE)!=old["current_STATE_sha"]:
  raise RuntimeError("V18_PRIOR_DOCUMENT_DRIFT")
 if v["passed"]!=17 or v["failed"]!=0:raise RuntimeError("AUDIT_NOT_PASSED")
 if (s["counts"]["physical_HTTP"],s["counts"]["raw_bytes"],s["counts"]["single_CID_candidate_only"])!=(27,7932,27):
  raise RuntimeError("R7_COUNTS_MISMATCH")
 if g["counts"]["graph_candidate_inputs"]!=27 or g["counts"]["name_exposure_records"]!=28:raise RuntimeError("GUARD_COUNT_ERROR")
 budget=s["current_global_physical_budget"]
 if budget!={"HTTP":973,"bytes":1210583689}:raise RuntimeError("BUDGET_CHANGED")
 logs=sorted((ROOT/"operations").glob("command-*.log"),key=lambda p:int(p.stem.split("-")[1]))
 full=[p for p in logs if "Ran 260 tests" in p.read_text(errors="replace") and "\nOK" in p.read_text(errors="replace")]
 spec=[p for p in logs if "Ran 8 tests" in p.read_text(errors="replace") and "\nOK" in p.read_text(errors="replace")]
 if not full or not spec:raise RuntimeError("TEST_LOG_MISSING")
 full_log=Path("operations")/full[-1].name;spec_log=Path("operations")/spec[-1].name
 for p,content in ((REPORT,oldr),(STATE,olds)):
  dst=PRIOR/p
  if (ROOT/dst).exists():raise RuntimeError("PRIOR_DOC_EXISTS")
  write(TASK,str(dst),content)
  if sha(dst)!=sha(p):raise RuntimeError("SNAPSHOT_SHA_DIFFERENCE")
 ts=datetime.now(timezone.utc).isoformat()
 text=f"""
## progress-v19: 已暴露名称的官方化合物候选身份与防泄漏图索引（{ts}）

本节是在不改变 progress-v18 事实的情况下追加，并已先保存v18的REPORT/STATE原字节SHA快照。TASK-016-P7、Roadmap P2仍为 In Progress，批准属性agent_delegated、非human_reviewed。

1. 以历史永久曝光 ledger 为起点，9条SS冻结前+16条C冻结前+3条C冻结后内部名称假设合计28条，跨轴 isorhamnetin 重复，形成27个唯一名称。仅对这些已暴露名称查询官方PubChem PUG REST exact-name property API，不对fresh候选化学抽取或设计scope。使用 scripts/task016_p7_r7_exposed_name_identity.py 先冻结查询URL、来源SHA、共享预算和单对象上限，再逐条执行，无自动跳转或重试，27条HTTP全部200、终态27/27，总下载7,932字节，逐件保留 raw/URL/SHA/status/physical-http账本。新累计物理预算截面973HTTP/1,210,583,689B。官方响应均返回一个CID候选，作为name-to-CID candidate，仅代表检索结果，不是独立验证的化学名称、图、天然产物立体或来源反应事实。批次证据在 {NAME}，raw位于 data/raw/task016-p7/governance/P7-R7-authoritative-exposed-name-resolution-v1。

2. 实际原始响应的结构字段为 SMILES/ConnectivitySMILES，旧名称 CanonicalSMILES 不存在不得当作化学结构缺失。用 scripts/task016_p7_r7_exposed_graph_guard.py 对27份SHA冻结原件独立解析并以RDKit规范化27个候选图，保留28条原始曝光ID及各自family。跨轴重复 isorhamnetin 仍保留2条永久曝光记录。候选结构匹配时保守输出 potential_prior_exposure_block；不匹配、输入错误、立体不同都只表示pending而不自动给予fresh。该索引不是已完成的同义名/独立化学图验证，也不代表对应论文有scope-relevant反应。索引见 {GRAPH}/candidate_graph_guard.json。

3. 增量8个防误判测试通过，整套260 tests OK，测试日志 {spec_log}、{full_log}。独立A11验收对输入SHA、27原始HTTP文件/大小/身份字段、结构规范化、账本守恒与预算逐项复算，17/17通过、0错误（{VERIFY}）。本轮新HTTP=27/7,932B、新MCTS=0、来源反应合格=0、fresh C=0/SS=0、科学A/B/E=0 cell，指标为null。SS此前A3仅2篇原件书目身份通过，4篇仍待原件；G5 science-read、G6原件双结构抽取/完整来源closure、G7/G8/新bankG9都未成。禁止以单CID结构候选代替A4/A5或提高科研完成状态，未Git commit/push/tag/release。主要索引见 outputs/task016-p7/v1/report_snapshots/progress-v19.json。
"""
 state_text=f"""
2026-10-11 TASK-016-P7 progress-v19（{ts}）：在v18增量上完成已曝光内部名称的官方PubChem候选标识对照。SS9+C16+C3=28条永久名称曝光、27个唯一名称，预登记后27/27HTTP200、7,932B；27单CID与27个RDKit候选图，但独立化学同义名/来源准入仍0。跨轴同名isorhamnetin保留2曝光记录，图正匹配仅候选阻断，未匹配仍pending。独立17/17通过、新测试8/8、全套260/260通过。物理预算973HTTP/1,210,583,689B。C/SS fresh均0、科学A/B/E0cell、metrics=null，G7/G8/G9未完成，TASK-016-P7与Roadmap P2仍In Progress。v18报告/STATE原字节与v19新证据哈希已存outputs/task016-p7/v1/report_snapshots/progress-v19；未Git同步、human_reviewed/正式生产无升级。
"""
 write(TASK,str(REPORT),oldr+text)
 write(TASK,str(STATE),olds+state_text)
 evidence=[V18,NAME/"query_plan.json",NAME/"request_preregistration.jsonl",NAME/"query_execution.jsonl",
   NAME/"http_ledger.jsonl",NAME/"disposition_summary.json",GRAPH/"candidate_graph_guard.json",
   VERIFY,full_log,spec_log,Path("scripts/task016_p7_r7_exposed_name_identity.py"),
   Path("scripts/task016_p7_r7_exposed_graph_guard.py"),
   Path("scripts/task016_p7_r7_independent_verify_v19.py"),
   Path("tests/test_task016_p7_r7_exposed_guard.py")]
 manifest={"task":TASK,"version":"progress-v19","timestamp":ts,"status":"In Progress",
  "approval":"agent_delegated","prior_REPORT_sha":sha(PRIOR/REPORT),
  "prior_STATE_sha":sha(PRIOR/STATE),"current_REPORT_sha":sha(REPORT),
  "current_STATE_sha":sha(STATE),"evidence_SHA256":{str(p):sha(p) for p in evidence},
  "permanent_name_exposure_records":28,"unique_exposed_names":27,
  "CID_and_graph_candidates":27,"independently_qualified_name_structure":0,
  "R7_HTTP":27,"R7_raw_bytes":7932,"global_budget":budget,
  "independent_checks_passed":17,"new_tests_passed":8,"full_tests_passed":260,
  "C_fresh":0,"SS_fresh":0,"scientific_ABE_cells":0,"scientific_metrics":None,
  "P7_completed":False,"G5_science_G6_G7_G8_G9_unclosed":True,"no_git_commit":True}
 write(TASK,str(dest),json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"status":"archived","version":"progress-v19",
       "REPORT_SHA":sha(REPORT),"STATE_SHA":sha(STATE),
       "verified_inputs":len(evidence),"P7_completed":False},ensure_ascii=False))
if __name__=="__main__":main()
