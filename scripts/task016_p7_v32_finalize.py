"""P7 v32 durable checkpoint: preserve earlier bytes, attach provenance and noncompletion status."""
import datetime,hashlib,json
from pathlib import Path
from scripts.operate import ROOT,write
T="TASK-016-P7"
B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
I=B/"verification-v32-pending-original-source-inventory/named_pending_original_inventory.json"
A=B/"verification-v32-pending-original-source-inventory/independent_A11_named_source_access_reconciliation.json"
R=B/"C/E02/fresh/C-E02-R61-two-legacy-official-original-recovery-v1/raw_custody_summary.json"
SNAP=B/"report_snapshots/progress-v32.json"
BACK=B/"report_snapshots/progress-v32-inputs/prior_documents"
def sha_bytes(x):return hashlib.sha256(x).hexdigest()
def sha(p):return sha_bytes((ROOT/p).read_bytes())
def load(p):return json.loads((ROOT/p).read_text())
def main():
 assert not (ROOT/SNAP).exists() and not (ROOT/BACK).exists()
 inventory=load(I);audit=load(A);retrieval=load(R)
 assert inventory["denominator"]==16 and inventory["axis_counts"]=={"C":8,"SS":8}
 assert audit["passed"]==64 and audit["failed"]==0 and retrieval["valid_JATS"]==0
 assert audit["current_HTTP"]==1208 and audit["current_bytes"]==1242654272
 report_bytes=(ROOT/REPORT).read_bytes();state_bytes=(ROOT/STATE).read_bytes()
 report=report_bytes.decode();state=state_bytes.decode()
 assert "progress-v31" in report[:500] and "progress-v32" not in report[:500]
 assert "progress-v31" in state[-2100:] and "progress-v32" not in state[-2100:]
 import glob
 tests=[]
 for p in ROOT.glob("operations/command-*.log"):
  tail=p.read_text(errors="replace")[-300:]
  if "Ran 286 tests" in tail and "OK" in tail:tests.append(p)
 tests.sort(key=lambda p:p.stat().st_mtime)
 assert tests
 final_test=tests[-1];last_text=final_test.read_text()
 assert "Ran 286 tests" in last_text and "OK" in last_text
 timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 for p,content in [(BACK/REPORT.name,report),(BACK/STATE.name,state)]:
  write(T,str(p),content)
 assert sha(BACK/REPORT.name)==sha_bytes(report_bytes)
 assert sha(BACK/STATE.name)==sha_bytes(state_bytes)
 section="""## progress-v32：16 项具名待获取来源清单与两项历史缺件的真实接口关闭（{time}）

**当前整体 In Progress，不是“全部文件获取完成”，更不是科学迁移成功。** P7 的显式 source/intake hard gates 未降低。旧 v31 原文和当前 STATE 的修改前 bytes 均完整归档于 `outputs/task016-p7/v1/report_snapshots/progress-v32-inputs/prior_documents/`。

1. **有限具名缺口总账建立。** 独立对已有 R12（6 个 C 轴来源访问缺口）、R9（4 个 SS 历史原文缺口）、R52（绿豆主要原件）、R46（Iris 原文广告 SI）、R32/R55/R56/R58（三篇 ACS 的原始 SI 已获得但主文仍缺）及 R16（另一份 PDF 403）进行了交叉核对，形成**16 项有明确来源身份与历史证据的未闭合原件/来源资格事项：C 8、SS 8**。每项保留 DOI/PMCID、已有原件/SI 与缺少原件的区别、最新合法访问状态、审计证据路径和下一合法操作。此分母是**当前已明确命名的来源缺口**，不代表所有潜在论文、未选择的 95 个元数据题名或源饱和。证据：`outputs/task016-p7/v1/verification-v32-pending-original-source-inventory/named_pending_original_inventory.json` 及同目录 README。
2. **两个 C 历史确切来源的真实原件请求结束。** 对 `PMC2709393`、`PMC7720146`，此前各 1 次官方 Europe PMC `fullTextXML` 记录 HTTP 500。R61 在先冻结原 G4、历史 R12 与操作代码 SHA，并登记恰好两次新查询后，各执行第二次且**仍为 HTTP 500**，没有取得任何 JATS 全文。该精确 URL 的常规两次上限已经用尽，不得再无合同重试。两个来源早已历史暴露，不能再算 future-fresh；不能因公开网页可阅读就自动变为项目已取得原件或 C6 完整化学反应。
3. **澄清历史 HTTP 200 非原件。** R63 另拟试用 NCBI 已公开文档中的 BioC-PMC 官方 OA API，但预登记前发现**同一两个精确 URL 在旧账已被请求**；入口在零新 HTTP 时拒绝，原失败日志保留。独立 A11 随后重读既存 BioC 响应：虽然各标 HTTP 200、GZip 原始 1715 字节，解压后均明确返回 `[Error] : No result can be found.`，**不是有效 BioC/XML 全文**。没有把状态码升格为原件，亦没有再次请求同一 API。
4. **三篇 ACS 论文与其他原件的范围边界。** R32 的 3 份官方 SI PDF 和 R55 的 1 份 XLSX 均已原字节保全，但主文原件未合法取得，R34/R56 科学裁决仍 `deferred`；SS 原历史 R9 四项返回重定向或 202 不代表有效 PDF。Iris 的所谓 PDF 实际是验证码 HTML，绿豆 Wiley 声明 VoR PDF/XML 为 403；均没有绕过。不能把零结果的具体来源查询解释成“全部合法渠道已穷尽”。
5. **独立审计与预算。** 新的 A11 从真实原始响应、曝光、16 项记录与所有 SHA 复算，**64/64 pass、0 failed**；当前来源 HTTP 账为 **1,208 次 / 1,242,654,272 字节**，相对 v31 净新增 2 次 / 300 字节，全部来自 R61 的两次 500。R62 首版仅程序变量 NameError、R63 前置 URL 重复拒绝均原样留存，追加 v2 实际成功结果，不静默覆盖。无新的合格科学原件、没有新实际 A/B/E MCTS。
6. **硬门与下一行动。** C/SS qualified fresh **0/0**、真实 G7/G8/G9 无冻结面板、科学 A/B/E 0 cell、指标 `null`，Roadmap P2 / TASK-016-P7 仍 **In Progress**。剩余原件要么需要新的有证据支撑的合法官方获取路径，要么存在付费/403/验证码/不提供全文等明确障碍；后续应在预登记之后依来源逐案处理，或由合法提供者交付原始文件，再经 A3→G5→隔离 A4/A5→A6 和完整结构、来源别名、28 名字曝光、scope preflight。不能以摘要、题录或低质量推测替代完整三方结构。未达来源饱和条件，不能宣告 TASK-016-P7 完成，也不升格人审、行动建议或 release。

**这一阶段实际完成了可核对的具名缺件边界与误判排除；并未达成“将全部文件获取分析”这一更高目标。** 当前仍有 16 个具名未闭合事项；不对后续获取成功、时间或来源资格做虚假承诺。
""".replace("{time}",timestamp)
 report=report.replace("当前权威截面progress-v31（", "当前权威截面progress-v32（",1)
 report=report.rstrip()+"\n\n"+section
 write(T,str(REPORT),report)
 update=("\nTASK-016-P7 当前权威状态 progress-v32（"+timestamp+"）：In Progress / agent_delegated。基于v31开展全部当前具名缺件的保守盘点，登记16项具名且实际未闭合的原件/来源资格事项（C8/SS8；仅已命名缺口，不代表全部文献）。C历史PMC2709393/PMC7720146官方EuropePMC fullTextXML经先冻结合同进行各第二次合规尝试，均HTTP500；两条URL常规尝试上限已用尽，0合法JATS。另有原BioC两个HTTP200原始响应解压为[Error] No result can be found而非有效全文；新BioC入口0HTTP拒绝重复。三份ACS SI PDF和一份ACS XLSX已保全，但主文仍缺；Iris SI验证码HTML及绿豆Wiley VoR403均保持访问待定，禁止绕过。新增两次HTTP/300字节，累计1208 HTTP/1,242,654,272字节；具名总账与A11 64/64独立审计通过，整库286单测验收见本轮命令日志。C/SS fresh仍0/0、科学A/B/E0 cell、G7/G8/G9未成，metrics=null；Roadmap P2未关闭，来源未饱和；不宣称已取得所有文件、不提升human_reviewed/release。详见REPORT-016-P7 progress-v32与outputs/task016-p7/v1/verification-v32-pending-original-source-inventory。\n")
 write(T,str(STATE),state.rstrip()+"\n"+update)
 record=dict(task=T,at=timestamp,stage="progress-v32",status="In Progress",approval_type="agent_delegated",inventory=dict(path=str(I),sha256=sha(I),named_unresolved=16,C=8,SS=8),independent_A11=dict(path=str(A),sha256=sha(A),passed=64),new_primary_originals=0,legal_new_HTTP=2,legal_new_bytes=300,physical_HTTP=1208,physical_bytes=1242654272,old_BioC_HTTP200_actual_error=2,full_tests=dict(path=str(final_test.relative_to(ROOT)),passed=286),report_sha256=sha(REPORT),state_sha256=sha(STATE),prior_report_sha256=sha_bytes(report_bytes),prior_state_sha256=sha_bytes(state_bytes),fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,source_saturation=False,Roadmap_P2_complete=False,git_commit_or_push=False)
 write(T,str(SNAP),json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(updated=True,stage="progress-v32",named_unresolved=16,A11=64,full_tests=286,physical_HTTP=1208,source_saturation=False)))
if __name__=="__main__":main()
