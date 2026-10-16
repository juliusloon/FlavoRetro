"""TASK-016-P7 progress-v24: scientific-source bibliographic stage closeout.

No chemistry qualification, scope rewrites, G6/G7 additions or model/MCTS changes.
"""
import json,hashlib
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
A11=B/"verification-v24-ss-r13-r16/independent_source_admission_audit_v1.json"
A3=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1/A3_two_route_bibliographic_preflight_v2.json"
R16=B/"SS/E02/fresh/SS-E02-R16-verified-publisher-PDF-access-v1/bounded_raw_access_dispositions.json"
R16NOTE=B/"SS/E02/fresh/SS-E02-R16-verified-publisher-PDF-access-v1/public_access_attempt_attestation_v2.json"
PRE=B/"report_snapshots/progress-v23.json"
DIR=B/"report_snapshots/progress-v24-inputs/prior_documents"
OUTPUT=B/"report_snapshots/progress-v24.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def put(p,txt):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS "+str(p))
 write(TASK,str(p),txt)
def main():
 if (ROOT/OUTPUT).exists():raise RuntimeError("V24_ALREADY_EXISTS")
 before=read(PRE);audit=read(A11);a3=read(A3);raw=read(R16)
 assert before["version"]=="progress-v23" and before["ABE_science_cells"]==0
 assert audit["passed"]==34 and audit["failed"]==0
 assert audit["physical_cumulative"]["HTTP"]==1072
 assert a3["count"]["bibliography_verified"]==4 and a3["count"]["fresh_admitted"]==0
 assert raw["successful_public_PDF"]==0 and raw["http_requests"]==2
 report=(ROOT/REPORT).read_text();state=(ROOT/STATE).read_text()
 assert sha(REPORT)==before["report_SHA"] and sha(STATE)==before["state_SHA"]
 # An actual current full-test log, not previous-run test count, binds this closeout.
 logs=[]
 for f in (ROOT/"operations").glob("command-*.log"):
  content=f.read_text()
  if "Ran 276 tests" in content and content.strip().endswith("OK"):
   logs.append((f.stat().st_mtime,f))
 assert logs
 log=max(logs)[1].relative_to(ROOT)
 t=datetime.now(timezone.utc).isoformat()
 put(DIR/"REPORT-016-P7-prior.md",report)
 put(DIR/"STATE-prior.md",state)
 current="状态：In Progress（未完成）。当前权威截面progress-v23（2026-10-11T02:59:04.054666+00:00）；阶段决定agent_delegated，非human_reviewed。"
 assert current in report
 report=report.replace(current,"状态：In Progress（未完成）。当前权威截面progress-v24（"+t+"）；阶段决定agent_delegated，非human_reviewed。",1)
 report+="""

## progress-v24：SS-E02 冻结范围后的新原始研究书目身份证据 + 原件准入障碍审查（"""+t+"""）

本轮系 TASK-016-P7 下的真实**来源发现与身份审核**阶段结果；它不是新化学反应准入，也不是已达到科学迁移硬门。G4 冻结的 Petunia flavonol-3O-Glcp/Galp 糖残基 O2 再葡糖基化范围、G5/G6 既有阶段、模型及 MCTS 均未改。相较 progress-v23，本轮消耗 22 个真实可对账 HTTP 请求，完全无新 MCTS；保留每次请求前的注册 SHA、原始响应不可变字节、错误与失败的历史。用户未授权 Git commit/push。

1. **SS-R13/R14 新的一手论文发现。** 两轮在 G4 与已登记有效 G5 门下先预注册合计 16 条 EuropePMC title-only 检索，均 HTTP 200；R13 得到 8 个互异题录，R14 得到 44 个互异题录（两轮之间有重叠，不能相加报总量）。从 R14 中鉴别出至少四项 R10 320 个题录簇未出现的**原始研究书目线索**：
   - SlUGT75C1 番茄黄酮醇糖苷论文（2025，DOI 10.1021/acs.jafc.5c06227）。
   - CsUGT73AC15 茶树黄酮醇三糖苷论文（2024，DOI 10.1021/acs.jafc.4c03824）。
   - 苹果组织四种糖基转移酶论文（2024，DOI 10.1111/tpj.16898）。
   - Laportea bulbifera 黄酮醇糖苷代谢论文（2024，DOI 10.1021/acs.jafc.4c00488）。
   题录与 DOI 命中不是“化学未暴露”的官方确认；四篇的真实历史别名/结构曝光全闭包依旧 unknown，不按 fresh 计数。

2. **SS-R15 新来源双权威书目身份核验。** 事前登记 4 条具体 DOI 的 Crossref 原件元数据请求，4/4 HTTP 200，并与 EuropePMC title/DOI/year 进行逐项规范化比对。四项通过 DOI、title、year、primary journal article、journal、publisher、EuropePMC subscription 状态检查，成功从**单路题录线索**提升为**双权威书目身份一致的四篇原始研究候选**；但是**不是 A3 官方科学原件封面/文章 front 身份通过**，不是 evidence-eligible。初版年份 parser 将 Crossref date-parts 列表误转成字符串，使四篇显示年份冲突，故不可作为有效验收；错误产物原样保留，`A3_two_route_bibliographic_preflight_v2.json` 在原始 Crossref SHA 上修正并四篇通过。

3. **SS-R16 合法原件访问实证。** 对上述茶树及苹果论文中 Crossref 实际广告的两个出版商 HTTPS PDF URL 逐件预登记、公共匿名请求、严格不跟随重定向和不作 access bypass；两次实测均 HTTP 403。无一获得有效 PDF 原件；原始响应及 SHA 按失败永久保留。原件科学内容尚未读取，不可以靠 Crossref 论文链接推定可访问、靠摘要推定反应、靠题目推导供体/受体/成键位点或立体结构。R16 v1 有一处不清晰的双重否定记录字段，另附 `public_access_attempt_attestation_v2.json`，不篡改 v1，明确实际匿名请求只包含 User-Agent 和 Accept-Encoding，无凭据、cookie、登录或绕过。

4. **A11 独立来源账本/版权约束复核：34/34 pass，0 fail。** 独立复算 R13/R14/R15/R16 共 8+8+4+2 = 22 次 physical HTTP，逐项核原始 SHA、预合同 SHA、G4/G5 阶段链、两官方 title/DOI/year、失败 PDF magic/status、旧报告/STATE 固定字节、未新建 G7 和未运行科学 A/B/E。最新 source physical global 计数 1072 HTTP（原 v23 的 source budget 仍不冒称任务总 MCTS）；其余精确累计字节详见审计输出。全量 unit tests **276/276 OK**，日志 `"""+str(log)+"""`。A11 只验证来源发现/访问结果，**不是独立化学结构验收**。

5. **科学任务状态未升格。** 本轮新增 title/identity evidence，但本轮取得的科学原件 **0**、可合格化学反应 **0**、fresh C=0/SS=0、closure groups 新增 0、科学 A/B/E **0 cell**、metrics=null、G7 未形成实际面板、Roadmap P2 仍 In Progress。不能由 403 推论学科来源饱和；也未完成三路线/连续两轮完整科学资格饱和判据。下一步若发现合法且实际可取的 primary original/SI，仍须完成 A3 原件、前置曝光登记、A4/A5 双独立完整结构/位点与 A6 别名反应闭包后才可能计 fresh；无原件则保持 access-blocked/pending，不绕过付费或登录。

证据根：`outputs/task016-p7/v1/SS/E02/fresh/SS-E02-R13-title-metadata-discovery-v1/` 至 `SS-E02-R16-verified-publisher-PDF-access-v1/`；A11：`outputs/task016-p7/v1/verification-v24-ss-r13-r16/independent_source_admission_audit_v1.json`；新截面 `outputs/task016-p7/v1/report_snapshots/progress-v24.json`。
"""
 write(TASK,str(REPORT),report)
 ix=state.index("\nTASK-016-P7 当前状态progress-v23")
 state=state[:ix]+"""
TASK-016-P7 当前状态progress-v24（"""+t+"""）：In Progress / agent_delegated。SS-E02 增量双轮 title-only 预注册研究（8+8 HTTP）获得R13 8/R14 44个各轮唯一题录，判明四篇未列R10题录簇的原始研究（2024/2025，茶树CsUGT73AC15、番茄SlUGT75C1、苹果GT组、Laportea GT）；R15 四条确切Crossref DOI元数据请求，4/4两权威DOI/title/year期刊出版物身份一致。R15 v1曾将日期列表错误当字符串导致4个假冲突，v2修正但保留v1原记录。R16 按Crossref实际出版商PDF路径尝试两条原件，2/2公共匿名请求HTTP403，0可读PDF；不登录/绕过，双重否定旧字段另外说明。22个新可观测HTTP、全球source ledger 1072；独立A11原件/provenance/预算/冻结链检查34/34通过，完整单元测试276/276通过。四项仅书目身份已核，不是A3原件科学身份、化学反应或新fresh；历史别名图未闭合。C/SS fresh均0，科学A/B/E0、metrics null、真实G7未冻结，Roadmap P2未完成。G4/scope/模型/v7/MCTS无改动，无Git commit/push及formal/human_reviewed升级；访问限制未绕过。证据见REPORT-016-P7 progress-v24与outputs/task016-p7/v1/report_snapshots/progress-v24.json。
"""
 write(TASK,str(STATE),state)
 result=dict(task=TASK,version="progress-v24",status="In Progress",time=t,
   prior_version="progress-v23",
   prior_report_SHA=sha(DIR/"REPORT-016-P7-prior.md"),
   prior_state_SHA=sha(DIR/"STATE-prior.md"),
   report_SHA=sha(REPORT),state_SHA=sha(STATE),
   A11_SHA=sha(A11),corrected_A3_bib_SHA=sha(A3),R16_access_SHA=sha(R16),
   public_access_attestation_SHA=sha(R16NOTE),
   source_discovery=dict(R13_unique_titles=8,R14_unique_titles=44,
     two_authoritative_bibliographies_verified=4,official_originals_acquired=0,
     newly_qualified_scientific_reactions=0,new_HTTP=22,
     cumulative_global_source_HTTP=1072),
   A11_bounded_source_checks=dict(passed=34,failed=0),
   unit_test_count=276,unit_test_passed=276,
   full_suite_log_path=str(log),full_suite_log_SHA=sha(log),
   fresh=dict(C=0,SS=0),scientific_ABE_cells=0,metrics=None,
   source_saturation_established=False,real_G7_panel=False,
   human_reviewed=False,git_pushed=False,scope_changed=False,no_new_MCTS=True)
 put(OUTPUT,json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(v="progress-v24",R15_bibliography=4,raw_PDF=0,A11_pass=34,tests=276,HTTP_delta=22,report_SHA=sha(REPORT),state_SHA=sha(STATE))))
if __name__=="__main__":main()

