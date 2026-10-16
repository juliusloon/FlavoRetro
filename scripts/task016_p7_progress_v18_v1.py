"""Archive TASK-016-P7 progress-v18 (R6 original identity and alias work)."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write

TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
PRIOR=B/"report_snapshots/progress-v18-inputs/prior_documents"
V17=B/"report_snapshots/progress-v17.json"
INDEP=B/"verification-v18-ss-r6/independent_R6_verification.json"
A3=B/"SS/E02/fresh/SS-E02-R6-A3-original-identity-v1"
A61=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v1"
A62=B/"SS/E02/fresh/SS-E02-R6-A6-documentary-exposure-screen-v2"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def main():
    oldreport=(ROOT/REPORT).read_text();oldstate=(ROOT/STATE).read_text()
    v17=load(V17); v=load(INDEP);a3=load(A3/"A3_original_identity_results.json")
    a6=load(A62/"A6_full_alias_union_dispositions.json")
    assert sha(REPORT)==v17["current_REPORT_sha"] and sha(STATE)==v17["current_STATE_sha"]
    assert v["passed"]==14 and v["failed"]==0
    assert a3["counts"]=={"processed":6,"passed":2,"rejected":0,"pending":4}
    assert a6["counts"]["fresh_admitted"]==0 and a6["new_HTTP"]==0
    if "progress-v18" in oldreport or "progress-v18" in oldstate:raise RuntimeError("ARCHIVE_ALREADY_DOCUMENTED")
    logs=sorted((ROOT/"operations").glob("command-*.log"),key=lambda p:int(p.stem.split("-")[1]))
    full=[p for p in logs if "Ran 252 tests" in p.read_text(errors="replace") and "OK" in p.read_text(errors="replace")]
    single=[p for p in logs if "Ran 9 tests" in p.read_text(errors="replace") and "OK" in p.read_text(errors="replace")]
    if not full or not single:raise RuntimeError("NO_TEST_LOG")
    full_log=Path("operations")/full[-1].name
    nine_log=Path("operations")/single[-1].name
    for p,contents in [(REPORT,oldreport),(STATE,oldstate)]:
        q=PRIOR/p
        if (ROOT/q).exists():raise RuntimeError("PRIOR_SNAPSHOT_EXISTS")
        write(TASK,str(q),contents)
        if sha(q)!=sha(p):raise RuntimeError("PRIOR_SNAPSHOT_SHA_MISMATCH")
    now=datetime.now(timezone.utc).isoformat()
    r=oldreport+f"""
## progress-v18：SS-R6 原件书目身份与官方别名联合筛查（{now}）

最新进展按TASK-016-P7已批准的 agent_delegated 合同执行。此前 progress-v17 原报告、STATE原字节均已存入 report_snapshots/progress-v18-inputs/prior_documents，旧日志/冻结原件和阶段SHA均未改写。P7依旧 In Progress、Roadmap P2 未闭环。

1. A3原件出版身份：先冻结R5角色manifest、官方R4原始书目、两份原件XML bytes及G4/G5 SHA，再通过此前已恢复的SS-E02 fresh登记门控。新A3仅访问完整XML的 front 部分（不处理摘要、化学正文、图、结构/SI），单独提取并与 Europe PMC及PubMed两条官方元数据路线核对 DOI/PMCID/PMID/题名/期刊/年/卷/期及页码或文章编号。PMC13387883（10.1111/pbi.70674）及PMC5517534（10.1038/s41598-017-06453-z）各10项全通过；其余4个选中来源没有可同等核验的独立原件，仍 pending。源已确定是文章，并**不**表示来源反应、供体、位点、范围、立体、图或目标fresh已获资格。A3证据目录：{A3}。

2. A6纪录一致的保守来源识别：初版 v1 仅匹配最小DOI与两原件PMID，发现可能遗漏非原件候选的PMID，故保留初版而新增v2；v2从既存冻结R4原始官方书目读取全部DOI/PMID/PMCID并进行并集闭包，六来源分别有 [3,2,2,1,2,3] 个官方标识。对冻结R3历史 exposure projection 全部2240行逐项精确复查，**六篇均无可证实的直接阳性来源标识匹配**；这只是有界匹配结果，**不是证明不存在历史曝光**。SS冻结前9个及C的16+3个，共28个未证实内部名称假设仍须官方同义名/结构级排除；无名称猜图，无化学曝光新结论，六来源全部继续 unknown/pending/fresh=0。v1原件与失败均保留，v2为当前A6 documentary-only审查，非最终G6或transitive reaction closure。v2目录：{A62}。

3. 独立审计（A11范围有限）独立重算两篇原件文件SHA、A3计数/10核对项、R4别名集合和R3阳性历史匹配等，14项通过、0失败；审计文件 {INDEP}。新9项合同测试包括PMID-only曝光、防标题推断、官方标识冲突fail-closed，全部通过；全量 252/252 tests OK（{full_log}）。本次为已取得原始数据的离线审查，**新HTTP=0，新MCTS=0**，全局物理预算截至上一R5快照仍为946HTTP/1,210,575,757B（不是新时刻的联网重算）。

4. 阻断与后续：A3通过的两篇仍须先完成严格来源/活性/供体/acceptor/product/site/关键立体的独立A4/A5核验、A6全文与未验证名称闭包，然后才能判断是否与冻结SS O2同域且可形成无泄漏反应；无法取到原件的其余四篇不伪填通过。C和SS正式fresh仍各0，G7/G8/新bank G9及科学A/B/E未启动，metrics=null。没有许可例外、绕过访问控制、扩大范围、后验改scope、git commit/push、human_reviewed或生产宣称。

progress-v18主证据SHA索引：outputs/task016-p7/v1/report_snapshots/progress-v18.json。
"""
    s=oldstate+f"""
2026-10-11 TASK-016-P7 progress-v18（{now}）：在v17可核档案上继续SS-R6。A3仅使用冻结原XML front与独立EuropePMC/PubMed原始书目复核，2篇原件各10项全通过、剩余4篇原件身份pending，无化学正文读取。A6 v1标识覆盖不足保留旧版，v2合并六篇官方DOI/PMID/PMCID [3,2,2,1,2,3]，对2240条冻结R3曝光投影未找到直接阳性匹配，但28个永久内命名假设未解析，不能判fresh。A11独立14/14通过；新9项测试通过、全量252/252通过，R6新HTTP0、MCTS0。SS/C fresh均0、科学A/B/E0cell、metrics=null、G7/G8/G9未成，P7 In Progress、Roadmap P2未关闭、未升级人审/production/release。v18报告前态SHA与结果索引outputs/task016-p7/v1/report_snapshots/progress-v18.json；不执行Git commit/push。
"""
    write(TASK,str(REPORT),r)
    write(TASK,str(STATE),s)
    inputs=[INDEP, A3/"preflight.json",A3/"A3_original_identity_results.json",A3/"role_A3_manifest.json",
      A61/"A6_source_exposure_dispositions.json",A62/"preflight.json",A62/"A6_full_alias_union_dispositions.json",
      A62/"role_A6_manifest.json",full_log,nine_log,
      Path("scripts/task016_p7_ss_r6_a3_original_identity.py"),
      Path("scripts/task016_p7_ss_r6_a6_alias_screen.py"),
      Path("scripts/task016_p7_ss_r6_a6_alias_screen_v2.py"),
      Path("scripts/task016_p7_ss_r6_verify_v18.py"),
      Path("tests/test_task016_p7_ss_r6_identity.py"),V17]
    manifest={"task":TASK,"version":"progress-v18","timestamp":now,
       "status":"In Progress","approval":"agent_delegated",
       "prior_REPORT_sha":sha(PRIOR/REPORT),"prior_STATE_sha":sha(PRIOR/STATE),
       "current_REPORT_sha":sha(REPORT),"current_STATE_sha":sha(STATE),
       "input_and_evidence_SHA":{str(p):sha(p) for p in inputs},
       "A3_original_identity_verified":2,"A3_original_pending":4,
       "A6_official_alias_counts":[3,2,2,1,2,3],
       "A6_bounded_positive_historical_matches":0,
       "A6_not_a_negative_exposure_certificate":True,
       "unresolved_legacy_names":28,"independent_checks_passed":14,
       "new_tests_passed":9,"full_suite_passed":252,
       "new_HTTP":0,"new_MCTS":0,"SS_fresh":0,"C_fresh":0,
       "scientific_ABE_cells":0,"scientific_metrics":None,
       "no_full_science_G6":True,"completed":False,
       "no_git_sync":True,"old_v17_report_and_state_snapshotted":True}
    write(TASK,str(B/"report_snapshots/progress-v18.json"),json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"archived":"progress-v18","independent":14,
       "full_tests":252,"report_sha":sha(REPORT),"state_sha":sha(STATE),
       "status":"In Progress"},ensure_ascii=False))
if __name__=="__main__":main()
