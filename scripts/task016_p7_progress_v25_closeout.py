"""TASK-016-P7 progress-v25: six new real official XML original custody
and one source-level same-scope original enzyme result; science fresh remains zero.
"""
import hashlib,json,re
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
PRE=B/"report_snapshots/progress-v24.json"
A11=B/"verification-v25-original-science-R18-R21/independent_A11_provenance_science_check.json"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
A6=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1/A6/source_O2_scope_positive_reconciliation.json"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G6_IDENTITY_STRUCTURE_ADMIT.json"
ORIGINALS=B/"governance/R20-six-original-front-identity-v1/source_RAW_custody_corrected_v2.json"
OLD=B/"report_snapshots/progress-v25-inputs/prior_documents"
INDEX=B/"report_snapshots/progress-v25.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def j(p):return json.loads((ROOT/p).read_text())
def put(p,text):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_PROGRESS_V25_ALREADY_EXISTS "+str(p))
 write(T,str(p),text)
def main():
 if (ROOT/INDEX).exists():raise RuntimeError("ALREADY_COMPLETE")
 v24=j(PRE);a=j(A11);ident=j(A3);result=j(A6);original=j(ORIGINALS)
 assert v24["version"]=="progress-v24" and v24["source_discovery"]["cumulative_global_source_HTTP"]==1072
 assert a["failed"]==0 and a["passed"]==30 and a["new_usable_full_primary_originals"]==6
 assert original["by_family"]=={"C":3,"SS":3}
 assert result["source_science_reaction_supported"] is True and result["source_qualified_for_bounded_biochemical_O2_mechanism"] is True
 assert result["P7_G7_qualified_fresh_holdouts"]==0
 full=[]
 for logfile in (ROOT/"operations").glob("command-*.log"):
  t=logfile.read_text()
  if "Ran 280 tests" in t and t.strip().endswith("OK"):
   full.append((logfile.stat().st_mtime,logfile.relative_to(ROOT)))
 assert full,"MISSING_RUN_OF_280_TESTS"
 log=sorted(full)[-1][1]
 before_report=(ROOT/REPORT).read_text()
 before_state=(ROOT/STATE).read_text()
 assert sha(REPORT)==v24["report_SHA"] and sha(STATE)==v24["state_SHA"]
 at=datetime.now(timezone.utc).isoformat()
 put(OLD/"REPORT-016-P7-prior.md",before_report)
 put(OLD/"STATE-prior.md",before_state)
 header="状态：In Progress（未完成）。当前权威截面progress-v24（2026-10-11T03:17:03.516853+00:00）；阶段决定agent_delegated，非human_reviewed。"
 assert header in before_report
 output=before_report.replace(header,
   "状态：In Progress（未完成）。当前权威截面progress-v25（"+at+"）；阶段决定agent_delegated，非human_reviewed。",1)
 output+="""

## progress-v25：原件获取瓶颈实质突破与首项 SS 直接 O2 酶学原件证据（"""+at+"""）

**结论层级：已完成可验的原件采集和来源级直接酶学科学论证；尚未达到全图反应 fresh holdout 与正式 A/B/E。** 本轮避免继续空转于 metadata；从标准官方 PMC/EuropePMC 全文接口取得 6 份实际可解析的 JATS 论文原件，按原字节及 SHA 保存。新增 HTTP=11（R18 八次 + R19 三次），全球物理来源请求账本合计 **1083**；没有新 MCTS。

### 1. 六份实际原件（3 C、3 SS）

| 家族 | PMCID | DOI | 状态与边界 |
|---|---|---|---|
| C | PMC9855344 | 10.3390/biom13010170 | 官方 JATS 原始全文保存，A3 front 核验通过；未开始完整化学资格抽取 |
| C | PMC12525976 | 10.3390/plants14193112 | 官方 JATS 原始全文保存，A3 front 核验通过；未开始完整化学资格抽取 |
| C | PMC11577821 | 10.1186/s12896-024-00923-9 | 官方 JATS 原始全文保存，A3 front 核验通过；既有曝光/化学准入待独立审核 |
| SS | PMC3795551 | 10.1107/S0909049513020712 | 官方 JATS 原始全文保存，A3 front 核验通过；未宣称直接糖间 O2 |
| SS | PMC12611259 | 10.1093/plphys/kiaf556 | 2025 正式出版原件，已由 G5 之后的双独立 A4/A5 原始实验文字核实 direct SS sugar O2 |
| SS | PMC11974848 | 10.1101/2025.03.27.645607 | 同项番茄研究预印本，完整原件已保存，**与正式论文同一来源 closure，不能算第二独立实验组** |

**重要的原件识别修复：** R18 首次 raw-only 检查只接受 XML 声明或以 article 开头，误拒两份有效 JATS 原件（PMC9855344、PMC12525976），其文件实际以标准 `<!DOCTYPE article>` 起始。旧失败报告 `R18/raw_custody_summary.json` 按审计保留，新增独立 A3 对六份真实 JATS 重新解析 front/PMCID/DOI/title/year 并复核原始 SHA，给出正确的 **6/6** 合格原始全文身份。其余 5 个 R18 原件获取 HTTP 500 仍原样保留，不伪造成 absence 或完整来源饱和。

### 2. SS 首次同范围直接实验（source-level）

来源：Doosan Shin 等人，*Tomato pollen tube growth requires flavonol glycosylation*（2025），`PMC12611259`，DOI `10.1093/plphys/kiaf556`。原件来源 `body/p-16` 中独立 A4/A5 一致读得：

- 重组酶 **SlUGT79B-B (79-B)**，供体 **UDP-glucose**，受体为**预先 3-O-半乳糖基化的 kaempferol (K-gal/K1)**；在已有糖残基的 **2″-O** 位增加葡糖，生成 kaempferol 3-O-glucosyl(1→2)galactoside (K-gal-glu/K2)。
- 同原件的对照酶 SlUGT79B-A 没有显示同样反应，属于直接重组酶实验陈述而非仅靠组织丰度推断。
- 正式文章原始实验段落 `body/p-16` 与相关预印本原始段落 `body/p-12` 的 A4、A5、A6 文字 SHA 两套抽取逐字一致，并均从原始 XML 复核。
- Source-to-frozen SS-E02 Petunia 3-O-βGal/Glc 残基 O2、UDP-glucose、β-glucose transfer 的反应方向/位点**一致，得到一项来源级实验机制正证据**。与原建模设计目标的可迁移性仍需后续独立结构编码与功能实验检验。

已先冻结 `SS-E02-R21` 的 G5（SHA `"""+sha(G5)+"""`）登记公开网页预先曝光和正式出版/预印本同一来源，随后才打开正式原件正文进行 A4/A5 独立审查、A6 复核。G6 源资格及裁决 SHA `"""+sha(G6)+"""`。重要边界：`PMC12611259` 亦已列入既有历史曝光盘点，当前记录是**可复核的研发科学来源证据**，并**不是新 fresh evaluation 样本**；无法将既有曝光永久洗白。全分子 covalent graph、准确糖异头立体、完整参考先驱体、零泄漏闭包尚未通过，G6 全结构合格反应 admission **0**；fresh C/SS **0/0**、G7 真实面板 **无**、正式科学 A/B/E **0 cells**、科学收益 metrics=null。

### 3. 来源失败、审计和回归

实际 11 次来源 HTTP 仅对登记官方 PMCID URL 请求、无登录/付费绕过、无自动跟随跳转、无未登记恢复；其中 **6 原始 JATS 真有效，5 次原件请求 HTTP 500**（R18）。两篇预印本与正刊按**同一原始研究**合并，不能将 2 文件、2 DOI 等同于 2 independent closure groups。SS 补充附件来自论文 JATS 有精确文件标识，但本次没有通过独立附件的合法物理采集审批，故**未获得并未计数任何新 SI 附件**。

受限 A11 从真实官方原始字节重新执行 30 项检查：**30/30 pass、0 fail**，核 PMCID/front/DOI/SHA、旧错误纠正、G4-G5-G6 必须前后相连、A4/A5/A6 原文段落、曝光/预印本同组、MCTS 零新增及 G7 未冻结。新加 4 条独立单元测试覆盖 6 原件 SHA、JATS DOCTYPE、原件直接 O2 及阶段链；**全量 unittest 280/280 OK**，日志 `"""+str(log)+"""`。A11 出具文件 `outputs/task016-p7/v1/verification-v25-original-science-R18-R21/independent_A11_provenance_science_check.json`。

本轮源码及 provenance 见 `scripts/task016_p7_r18_PMC_originals.py`、`scripts/task016_p7_r19_PMC_originals.py`、`scripts/task016_p7_r20_A3_six_originals.py`、`scripts/task016_p7_ss_r21_A0_g5.py` 至 `A6_reconcile.py`，全部通过 `scripts/operate.py` 留痕。冻结 G4 与原模型/库存/PUCT/v7 搜索配置不变。无 Git commit/push、无 human_reviewed、无 formal blind/release 夸大，Roadmap P2 与 P7 均 In Progress。

**下一关键科学动作：** 针对当前仍未深入审查的合法新 C 原件和新来源，完成明确的 A3→G5→A4/A5 全原图独立提取、A6 exposure 闭包，寻找不在历史曝光内的 source-qualified 新 closure group；到每家族 ≥6 fresh、≥2 independent groups 后才能真正触发 G7+A/B/E，不能通过降门槛替代。
"""
 write(T,str(REPORT),output)
 before_state += """

TASK-016-P7 当前状态progress-v25（"""+at+"""）：In Progress / agent_delegated。本轮优先解决原件瓶颈：标准 EuropePMC 全文接口在 R18/R19 合计 11 次真实 HTTP，取得六份可解析官方 JATS 原始全文（C=3、SS=3），全部保存不可变 raw+SHA，并完成 A3 original front 6/6。修正 R18 以 <!DOCTYPE article> 开头的两份 JATS 原件被误判失败的逻辑，旧报告保留。番茄正式原件 PMC12611259（10.1093/plphys/kiaf556）首次给出与 SS-E02 原冻结范围直接一致的 SlUGT79B-B 酶促 K-gal + UDP-glucose → K-gal-glu(K2) 糖残基 O2 连接原始科学证据；预印本 PMC11974848 属同一来源 closure。先 G5 登记历史与网页曝光，再 A4/A5 原件双独立段落复核和 A6 源级肯定、G6 冻结。**来源酶学正证据=1、但历史已接触、完整共价图/别名闭包未完成，fresh仍0，G7实际未冻结，科学A/B/E0 cell**。R18另外5次HTTP500如实保留；本轮全球来源账本HTTP1083，无新MCTS。独立A11 30/30全通过，新4测试与全项目280/280全部通过。路径 outputs/task016-p7/v1/report_snapshots/progress-v25.json；scope/G4与运行参数未改、无git commit/push或人审/formal升级，Roadmap P2仍未关闭。
"""
 write(T,str(STATE),before_state)
 index=dict(task=T,progress="progress-v25",status="In Progress",at=at,
  prior_version="progress-v24",
  previous_report_SHA=sha(OLD/"REPORT-016-P7-prior.md"),
  previous_state_SHA=sha(OLD/"STATE-prior.md"),
  report_SHA=sha(REPORT),state_SHA=sha(STATE),
  A3_6_SHA=sha(A3),six_originals_custody_SHA=sha(ORIGINALS),
  A6_direct_sugar_O2_positive_SHA=sha(A6),G5_SHA=sha(G5),G6_SHA=sha(G6),
  A11_SHA=sha(A11),A11_pass=30,A11_fail=0,
  science_origin=dict(original_article_versions=6,C_originals=3,SS_originals=3,
   actual_source_level_direct_O2_groups=1,
   fully_structure_qualified_fresh=0,preprint_independent=False),
  physical_HTTP_delta=11,global_source_HTTP=1083,new_source_SI_attachments=0,
  complete_unittest=280,complete_unittest_passed=280,added_special_tests=4,
  test_log_path=str(log),test_log_SHA=sha(log),
  fresh_C=0,fresh_SS=0,real_G7=False,ABE_scientific_cells=0,
  no_new_MCTS=True,source_saturation_established=False,
  human_reviewed=False,git_commit_push=False,roadmap_P2_complete=False)
 put(INDEX,json.dumps(index,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(progress="v25",originals=6,source_positive=1,G6=sha(G6),A11=30,unittest=280,
  report_SHA=sha(REPORT),state_SHA=sha(STATE),global_HTTP=1083)))
if __name__=="__main__":main()

