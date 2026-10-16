"""Finalize P7 progress-v31 after actual source-A11 and full regressions; no scientific claim upgrade."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

from scripts.operate import ROOT, write
from scripts.task016_p7_c_e02_http import physical_attempts

T="TASK-016-P7"
B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
A11=B/"verification-v31-official-tabular-SI-v1/independent_A11_tabular_and_access_audit.json"
A11B=B/"verification-v31-ACS-tabular-original/independent_A11_raw_OOXML_stage_audit.json"
SC=B/"SS/E02/fresh/SS-E02-R56-Laportea-tabular-science-v1/A6/source_scientific_assessment.json"
OLD=B/"report_snapshots/progress-v30-physical-budget.v2.json"
NOW=B/"report_snapshots/progress-v31-physical-budget.v2.json"
def load(p): return json.loads((ROOT/p).read_text())
def digest_bytes(b):return hashlib.sha256(b).hexdigest()
def main():
    a=load(A11);b=load(A11B);sc=load(SC);budget=load(NOW);prior=load(OLD)
    assert a["passed"]==67 and a["failed"]==0 and b["passed"]==73 and b["failed"]==0
    assert len(physical_attempts())==budget["totals"]["HTTP"]==1206
    assert sum(x["bytes"] for x in physical_attempts())==budget["totals"]["bytes"]==1242653972
    assert a["new_HTTP"]==11 and a["new_bytes"]==119758
    assert budget["totals"]["HTTP"]-prior["totals"]["HTTP"]==11
    assert budget["totals"]["bytes"]-prior["totals"]["bytes"]==119758
    assert a["registered_unique_G5_G6"]==25
    assert sc["chemical_qualification"]=="deferred" and sc["fresh_admitted"]==0
    log=(ROOT/"operations/command-5159.log").read_text()
    assert "Ran 286 tests" in log and "OK" in log
    assert (ROOT/"operations/command-5160.log").read_text()==""
    assert (ROOT/"operations/command-5161.log").read_text().find('"passed": 67')!=-1
    report_bytes=(ROOT/REPORT).read_bytes();state_bytes=(ROOT/STATE).read_bytes()
    report=report_bytes.decode("utf-8");state=state_bytes.decode("utf-8")
    assert report.startswith("# REPORT-016-P7")
    assert "当前权威截面progress-v30" in report[:550]
    assert "## progress-v31：" not in report
    assert state.rstrip().endswith("无Git提交/推送或human_reviewed/formal升级。权威证据见REPORT-016-P7 progress-v30及outputs/task016-p7/v1/report_snapshots/progress-v30.json。")
    # Preserve the complete previous bytes before editing their active documents.
    snap=B/"report_snapshots/progress-v31-inputs/prior_documents"
    assert not (ROOT/snap).exists()
    write(T,str(snap/REPORT.name),report)
    write(T,str(snap/STATE.name),state)
    assert digest_bytes((ROOT/snap/REPORT.name).read_bytes())==digest_bytes(report_bytes)
    assert digest_bytes((ROOT/snap/STATE.name).read_bytes())==digest_bytes(state_bytes)
    now=datetime.now(timezone.utc).isoformat()
    section="""## progress-v31：ACS 原始补充表格取得、SS 来源级处理闭环与独立原件守恒（2026-10-11）

**本轮产生可核验的原始来源及资格处理阶段进展，但并未得到新的合格 fresh holdout 或科学迁移收益。** 2026-10-11T05:51 UTC 的 v30 截面之后，完成 R54–R58 来源获取/访问核查、R56 独立双解析及 A6 资格裁决，并以两套独立原件审核复验；完整测试 286/286 OK。

1. **具体原件缺口关闭。** 对 ACS DOI `10.1021/acs.jafc.4c00488` 的官方 Figshare 广告补充条目（SI DOI `10.1021/acs.jafc.4c00488.s001`），R54 原签名下载地址已到期的 403 与原响应保留；R55 按实际官方 Location 独立注册并取得原版 XLSX `jf4c00488_si_001.xlsx`，68,338 字节、SHA-256 `c72d758299381dd62f2951d35dcfcb2839f1347c5ffbfa618470bdbec51fb23a`，其 MD5 与官方字段 `30aa6648c27369368949a9032b031502` 一致。原件保留为原始本地只读数据，不入 Git。R57 的四个合法公开来源定位请求仅取得元数据，R58 两个原件 PDF 官方声明地址均 403、有效主文仍 0；没有绕过挑战、重试禁止地址或声称正文已获得。
2. **科学审查从“补充表格未知”变成可复核的明确 disposition。** R56 在原表科学读取前已固定 G5；两个不同角色分别用 stdlib 与 lxml 独立解析原始 OOXML，A6 精确核对 14 个命名工作表、4,994 个存储单元格、523 条代谢物注释、43 个字面数值零、269 个显式空白、15 个带缓存的外部公式。缓存公式不重新计算，不打开外部工作簿、不按缺失补零。表中确实出现 Quercetin-3-O-sophoroside、Kaempferol-3-O-sophoroside、Isovitexin 等名称，但**仅为代谢物注释，不能当作直接糖间 O2 酶促反应，更不能将 523 条视作参考反应**。A6 裁决为 `deferred`，未完整核过对应主文酶学反应、来源绑定全分子图、供体、位点/糖立体与参考前体，独立完整图准入 0、新独立研究组增加 0、fresh 增加 0。这也不等于否定整篇论文不存在相关反应。
3. **完整阶段/来源独立核对。** 原有预登记的 A11 `verification-v31-official-tabular-SI-v1/independent_A11_tabular_and_access_audit.json` 实跑 **67/67 pass、0 fail**，逐源验证 R54/R55/R57/R58 所有 HTTP/原始响应 SHA、官方 XLSX 字节/MD5、14 表格 OOXML 原始单元格与 A4/A5 逐项一致、G5 时间早于实际读取、25 个唯一活动 G5/G6 注册链、两轴原 G4、MCTS run ledger 不变。附加独立 stdlib source reader `verification-v31-ACS-tabular-original/independent_A11_raw_OOXML_stage_audit.json` **73/73 pass、0 fail**。两套检查有重叠，不合计为 140 个独立科学证据，也不称为 independent chemical validation。
4. **物理预算守恒。** 相对 v30 的 1,195 请求/1,242,534,214 字节，本轮 R54=3、R55=2、R57=4、R58=2，新增 11 HTTP、119,758 字节；当前实际 **1,206 HTTP/1,242,653,972 字节**。原 HTTP200/302/403 原始字节、失败和时间顺序均保留。新预算快照 `report_snapshots/progress-v31-physical-budget.v2.json`；早期中间截面与旧 v30 不覆盖。不把 HTTP 次数、表格格数或注释行数计作合格论文/反应数。
5. **工程回归与治理。** 本次额外完整运行 `.venv-foundation/bin/python -B -m unittest discover -s tests`，**286/286 OK**（`operations/command-5159.log`）；`git diff --check` 通过（`command-5160.log`）；原件 A11 运行见 `command-5161.log`，另一套独立检查见 `command-5158.log`。所有最终产物写入经 `scripts/operate.py` 登记；旧 REPORT/STATE 完整 bytes 保存在 `report_snapshots/progress-v31-inputs/prior_documents/`。没有本轮新增科学 A/B/E MCTS，也无 Git commit/push。
6. **仍不可关闭的门。** C/SS 合格 fresh **0/0**、真实 G7/G8/新 bank G9 尚无面板、科学 A/B/E **0 cell**、迁移指标 **null**，Roadmap P2 / TASK-016-P7 整体 **In Progress**。R56 来源本 epoch 已暴露，不能未来漂白为新 fresh。SS 其余 ACS 原件及主文科学结构、C-R39 质量异常、Iris 原文编号冲突、来源别名/28 命名曝光和完整参考前体仍待审；来源并未饱和。无 human_reviewed、formal blind、actionable/evidence_closed 或 release 升格。

**下一科学动作：** 依据冻结范围与已审原件名单，先补齐具合法直接原件路径的 SS 主文机制或 C 高优先级来源的完整 A3/G5/A4/A5/A6；按 source→reaction→complete-graph→leakage→scope-preflight 的分母逐级收口。只有每轴 >=6 个合格新目标、>=2 个独立 closure groups 才能冻结真实 G7 并执行 A/B/E；不得为追求数量降低门槛。
"""
    section=section.replace("（2026-10-11）","（"+now+"）",1)
    report=report.replace("当前权威截面progress-v30（2026-10-11T05:51:26.622140+00:00）","当前权威截面progress-v31（"+now+"）",1)
    report=report.replace("C/SS G4均已冻结，合格fresh均0，科学A/B/E0 cell、迁移指标null，Roadmap P2尚未关闭。","C/SS G4均已冻结，合格fresh均0，科学A/B/E0 cell、迁移指标null，Roadmap P2尚未关闭。本次新增一项官方XLSX原件及14工作表资格审查闭环，仍为deferred。",1)
    report=report.rstrip()+"\n\n"+section.rstrip()+"\n"
    write(T,str(REPORT),report)
    update=("\nTASK-016-P7 当前权威状态progress-v31（"+now+"）：In Progress / agent_delegated。继v30后R54–R58新增11 HTTP/119,758字节，累计1,206 HTTP/1,242,653,972字节；R55取得官方ACS DOI 10.1021/acs.jafc.4c00488.s001 XLSX原件68,338字节，MD5/SHA与官方登记一致，R56双独立解析14工作表/4,994单元格、523代谢物注释、43数值零、269显式空白及15公式，科学A6审查deferred（代谢物注释不是直接酶学反应；原主文/供体/位点/立体/前体/历史别名仍缺）。R57四路仅定位metadata、R58两次正式PDF403保留。独立A11 67/67和第二原件守恒73/73通过；25唯一G5/G6链与C/SS G4、214行MCTS账保持，286/286本地全量单测与git diff --check通过。C/SS fresh仍0/0、G7/G8/G9未形成、科学A/B/E0 cell、metrics=null、Roadmap P2未关闭；来源并未饱和。全部原始受限载荷不入Git，本轮未commit/push，不升格human_reviewed、科学认证、actionable或release。权威证据详见REPORT-016-P7 progress-v31、outputs/task016-p7/v1/verification-v31-official-tabular-SI-v1及verification-v31-ACS-tabular-original。\n")
    write(T,str(STATE),state.rstrip()+"\n"+update)
    snapshot={"task":T,"status":"In Progress","at":now,"stage":"progress-v31","human_reviewed":False,"current_report_sha256":digest_bytes((ROOT/REPORT).read_bytes()),"current_state_sha256":digest_bytes((ROOT/STATE).read_bytes()),"original_report_sha256":digest_bytes(report_bytes),"original_state_sha256":digest_bytes(state_bytes),"A11_main":{"path":str(A11),"sha256":digest_bytes((ROOT/A11).read_bytes()),"passed":67},"A11_secondary":{"path":str(A11B),"sha256":digest_bytes((ROOT/A11B).read_bytes()),"passed":73},"full_tests":{"path":"operations/command-5159.log","count":286},"git_diff_check":{"path":"operations/command-5160.log","passed":True},"source_science":{"path":str(SC),"status":"deferred"},"new_HTTP":11,"new_bytes":119758,"total_HTTP":1206,"total_bytes":1242653972,"fresh_C":0,"fresh_SS":0,"scientific_ABE_cells":0,"metrics":None,"Roadmap_P2_Completed":False,"Git_commit_or_push":False}
    write(T,str(B/"report_snapshots/progress-v31.json"),json.dumps(snapshot,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"result":"progress-v31_updated","stage":"original_tabular_SI_recovered_and_independently_audited","A11_main":67,"A11_secondary":73,"full_tests":286,"fresh_C":0,"fresh_SS":0,"Roadmap_P2_Completed":False},ensure_ascii=False))
if __name__=="__main__":main()
