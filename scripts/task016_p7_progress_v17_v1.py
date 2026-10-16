"""Archive P7 progress-v17 evidence and update REPORT/STATE without promoting science."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from scripts.operate import ROOT, write

TASK="TASK-016-P7"
B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
SNAP=B/"report_snapshots/progress-v17-inputs/prior_documents"
R5=B/"SS/E02/fresh/SS-E02-R5-original-acquisition-v1"
INDEP=B/"verification-v17-ss-r5/independent_R5_verification.json"
FIX=B/"governance/SS_E02_R5_G5_binding_repair_v1/validation.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())

def main():
    oldr=(ROOT/REPORT).read_text(); olds=(ROOT/STATE).read_text()
    if "当前文档版本progress-v16" not in oldr or "TASK-016-P7 当前状态（progress-v16" not in olds:
        raise RuntimeError("UNEXPECTED_PRIOR_REPORT_STATE")
    v=load(INDEP);t=load(R5/"raw_only_intake_manifest.json")["counts"];f=load(FIX)
    assert v["passed"]==10 and v["failed"]==0 and v["formal_task_completed"] is False
    assert t["HTTP"]==18 and t["bytes"]==15319520 and t["fresh_admitted"]==0
    assert f["new_HTTP"]==0 and f["fresh_admitted"]==0
    logs=sorted((ROOT/"operations").glob("command-*.log"),key=lambda p:int(p.stem.split("-")[1]))
    tests=[p for p in logs if "Ran 243 tests" in p.read_text(errors="replace") and "OK" in p.read_text(errors="replace")]
    if not tests:raise RuntimeError("NO_FULL_SUITE_TEST_PROOF")
    testlog=Path("operations")/tests[-1].name
    now=datetime.now(timezone.utc).isoformat()
    for p,content in [(REPORT,oldr),(STATE,olds)]:
        if (ROOT/SNAP/p).exists():raise RuntimeError("ARCHIVE_EXISTS")
        write(TASK,str(SNAP/p),content)
        if sha(p)!=sha(SNAP/p):raise RuntimeError("PRIOR_DOCUMENT_DRIFT")
    old_header="状态：In Progress。当前文档版本progress-v16；实际写入时间 2026-10-10T18:03:39.170653+00:00。批准与阶段决定为agent_delegated，非human_reviewed。"
    new_header=f"状态：In Progress（未完成）。最新增量progress-v17（{now}）。以下20项原回答是progress-v16的冻结截面，最新增量与预算以本报告末尾v17节为准。agent_delegated，非human_reviewed。"
    if oldr.count(old_header)!=1:raise RuntimeError("REPORT_HEADER_MISMATCH")
    r=oldr.replace(old_header,new_header,1)
    r+=f"""
## progress-v17：SS-R5 源文件获取闭环和 G5 登记修复（{now}）

此为后续增量，不重写 progress-v16 的历史事实。TASK-016-P7 继续 In Progress，Roadmap P2 未关闭。

1. 冻结 G4/G5 的内容 SHA 保持不变。此前 operations/command-4480.log 中 SS_G5_SCOPE_BINDING_MISMATCH 属登记缺字段：最近 SS-R4 metadata G5 的阶段文件正确以 G4 SHA 作为 input_manifest_sha，但全局注册缺 scope_manifest_sha256。scripts/task016_p7_ss_g5_binding_repair_v1.py 先校验 stage、前驱链、scope、manifest SHA，再追加带真实时间的修正登记；未修改历史登记、scope、G4/G5 或预冻结 R5 脚本。真实门控已通过，原失败留存，未追认更早的时序和漏账。

2. 原计划的 SS-R5 只读原件获取在修复后继续执行并 finish。9 locator 与 9 article/SI 请求均为终态（合计 18 HTTP，15,319,520 bytes），其中 8 article-version 请求、1 SI 请求及 9 metadata 请求。三次 301 禁止自动跳转，保留原响应；另外取得 XML、PDF、opaque SI 等字节。原 6 个被选中来源中仅 2 个有格式有效的原件容器（共 4 个有效原件对象），另 1 个 SI 为 opaque；2 次 XML front 信息校验。其余来源以及科学身份、全文/图/产物/供体/立体仍为 pending；格式成功不等于化学源证据准入。

3. scripts/task016_p7_ss_r5_verify_v17.py 从 raw bytes、物理请求、各个独立账本及冻结SHA重新检查，outputs/task016-p7/v1/verification-v17-ss-r5/independent_R5_verification.json 显示 10 pass、0 fail。R5 结案时全局物理预算快照为 946 HTTP / 1,210,575,757 bytes，包含此前固定902前缀后的其他 C/SS 批次；不能将其差额都归于本批。R5 独占18 HTTP/15,319,520 bytes。

4. 新增的 5 项阶段身份/错配 fail-closed 测试通过。全套 unittest 共 243 tests OK，日志 {testlog}。旧版 REPORT/STATE 原字节留存于 {SNAP}；本轮新验证、程序、日志及文档 SHA 见 report_snapshots/progress-v17.json。未执行 Git commit/push/tag/release。

5. 严守原合同：SS-R5仅 raw-only，未开放科学正文/结构抽取准入，已有 9 个 SS 命名假设与 C 19 个名字假设不能直接计 fresh；下一步仍须官方身份/历史曝光核验，合格来源依次经 G5→A3→A4/A5→A6与closure。C和SS均 fresh=0；G7/G8/最终新bank G9未完成；科学A/B/E=0 cells、metrics=null。没有取得迁移正增益或node-transfer证据；formal_run_ready/release_ready及independent chemical validation仍不满足。
"""
    s=olds.replace("TASK-016-P7 当前状态（progress-v16；","TASK-016-P7 既有固定截面（progress-v16；",1)
    s+=f"""
2026-10-11 TASK-016-P7 最新增量 progress-v17（{now}）：原SS-R4 G5登记缺scope SHA导致R5拒绝，已追加实际核验的scope绑定，原G4/G5/scope字节与失败日志不改；R5原预登记9 locator+9原件/SI共18 HTTP / 15,319,520字节结案，6来源中2个有4份格式有效原件对象，未获得科学准入。独立10/10、专项5/5、全量243/243测试通过；全局物理预算截面946 HTTP / 1,210,575,757字节（含此前其他新批次）。fresh C=0/SS=0，正式G7/G8/G9、科学A/B/E仍未执行，迁移指标null，Roadmap P2持续In Progress。REPORT/STATE旧字节快照和证据目录位于outputs/task016-p7/v1/report_snapshots/progress-v17；不升级human_reviewed/production/release，本次未Git同步。
"""
    write(TASK,str(REPORT),r)
    write(TASK,str(STATE),s)
    ev=[INDEP,R5/"raw_only_intake_manifest.json",R5/"role_A2_raw_only_manifest.json",R5/"HTTP_budget_audit.json",
       FIX,testlog,Path("scripts/task016_p7_ss_g5_binding_repair_v1.py"),
       Path("scripts/task016_p7_ss_r5_verify_v17.py"),
       Path("tests/test_task016_p7_g5_binding_repair.py"),
       B/"SS/E02/stages/G4_SCOPE_FREEZE.json",
       B/"SS/E02/stages/batches/SS-E02-R4-metadata/G5_FRESH_HOLDOUT_ACQUIRE.json"]
    manifest={"task":TASK,"version":"progress-v17","time":now,"status":"In Progress",
      "prior_REPORT_sha":sha(SNAP/REPORT),"prior_STATE_sha":sha(SNAP/STATE),
      "current_REPORT_sha":sha(REPORT),"current_STATE_sha":sha(STATE),
      "evidence_SHA":{str(p):sha(p) for p in ev},
      "R5_HTTP":18,"R5_bytes":15319520,"R5_valid_source_count":2,
      "global_HTTP_after_R5":946,"global_bytes_after_R5":1210575757,
      "test_suite_passed":243,"independent_R5_passed":10,
      "fresh_C":0,"fresh_SS":0,"scientific_ABE_cells":0,"metrics":None,
      "completed":False,"no_git_sync":True,"old_failures_preserved":True}
    write(TASK,str(B/"report_snapshots/progress-v17.json"),json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":"archived","REPORT_sha":sha(REPORT),"STATE_sha":sha(STATE),
      "manifest":str(B/"report_snapshots/progress-v17.json"),"task":"In Progress"},ensure_ascii=False))

if __name__=="__main__":main()
