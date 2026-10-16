"""TASK-016-P7 progress-v23: bounded engineering G7 writer binding closeout."""
from pathlib import Path
import json,hashlib,re
from datetime import datetime,timezone
from scripts.operate import ROOT,write
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
REPORT=Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE=Path("STATE.md")
REQ=B/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json"
WRITER=Path("scripts/task016_p7_g7_final_writer.py")
TEST=Path("tests/test_task016_p7_g7_final_writer.py")
VERIFY=B/"verification-v23-g7-writer/independent_G7_writer_verification_v3.json"
BIND=B/"governance/G7_writer_integration_v1/production_writer_binding.json"
SNAP=B/"report_snapshots/progress-v23-inputs/prior_documents"
INDEX=B/"report_snapshots/progress-v23.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def save(p,content):write(TASK,str(p),content)
def main():
 if (ROOT/INDEX).exists() or (ROOT/BIND).exists():raise RuntimeError("IMMUTABLE_V23_EXISTS")
 a11=read(VERIFY);prior=read(B/"report_snapshots/progress-v22.json")
 assert a11["passed"]==20 and a11["failed"]==0 and not a11["real_G7_panel_exists"]
 assert a11["G7_writer_SHA"]==sha(WRITER) and a11["test_file_SHA"]==sha(TEST)
 assert prior["version"]=="progress-v22" and prior["qualified_fresh_SS"]==0
 assert sha(REQ)==a11["prior_v4_requirement_SHA"]
 full=[]
 for f in (ROOT/"operations").glob("command-*.log"):
  text=f.read_text()
  if "Ran 276 tests in " in text and text.strip().endswith("OK"):
   full.append((f.stat().st_mtime,f,text))
 assert full,"NO_FULL_SUITE_276_OK"
 _,log,logtext=max(full)
 log=log.relative_to(ROOT)
 assert "Ran 276 tests" in logtext and "OK" in logtext
 now=datetime.now(timezone.utc).isoformat()
 earlier=(ROOT/REPORT).read_text()
 state=(ROOT/STATE).read_text()
 assert sha(REPORT)==prior["current_report_SHA"]
 assert sha(STATE)==prior["current_state_SHA"]
 save(SNAP/"REPORT-016-P7-prior.md",earlier)
 save(SNAP/"STATE-prior.md",state)
 binding=dict(task=TASK,epoch_families=["C-E02","SS-E02"],at=now,
    approval_type="agent_delegated",human_reviewed=False,
    writer_path=str(WRITER),writer_SHA=sha(WRITER),
    tests_path=str(TEST),tests_SHA=sha(TEST),
    v4_prior_requirement_path=str(REQ),v4_prior_requirement_SHA=sha(REQ),
    original_requirement_field_actual_G7_writer_integrated=False,
    later_additive_writer_integration=True,
    v4_validator_actually_called=True,explicit_PMID_source_alias_check=True,
    full_prior_historical_exposure_files_hard_pinned=True,
    current_G5_G6_exposure_coverage_receipt_required=True,
    A6_and_A11_current_source_qualification_bindings_required=True,
    cannot_disable_completion_floor=True,required_targets_per_family=6,
    required_closure_groups_per_family=2,
    reject_before_persistent_write=True,
    G7_actual_panel_formed=False,G7_stage_manifest_present=False,
    actual_28_named_identity_chemical_reviews=0,
    scientific_fresh_C=0,scientific_fresh_SS=0,
    ABE_scientific_cells=0,science_metrics=None,
    independent_review=dict(path=str(VERIFY),sha256=sha(VERIFY),passed=20,failed=0,
       bounded_engineering_only=True,not_scientific_A11=True),
    tests=dict(new_specific_cases=8,full_unittest=276,full_passed=276,
       full_log_path=str(log),full_log_sha256=sha(log)),
    no_new_source_HTTP=True,no_new_MCTS=True,
    task_completed=False,roadmap_P2_closed=False,git_commit_push=False)
 save(BIND,json.dumps(binding,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
 before="状态：In Progress（未完成）。当前权威截面progress-v22（2026-10-11T02:47:43.527468+00:00）；阶段决定agent_delegated，非human_reviewed。"
 assert before in earlier
 updated=earlier.replace(before,"状态：In Progress（未完成）。当前权威截面progress-v23（"+now+"）；阶段决定agent_delegated，非human_reviewed。",1)
 section="""

## progress-v23：G7 最终面板写入入口强制接入 28 名称曝光及完整阶段覆盖（"""+now+"""）

本次交付是可运行的**受控工程准入入口**，不是已冻结的 G7 化学面板。此前 progress-v22 的 REPORT/STATE 原字节与 SHA 在 `outputs/task016-p7/v1/report_snapshots/progress-v23-inputs/prior_documents/` 保留，不改旧治理或 G4/G6 阶段事实。

1. 新增正式入口 `scripts/task016_p7_g7_final_writer.py`，通过 `--request` 消费全部 SHA 绑定的本地冻结输入。G7 写盘前必须直接执行现有 `task016_p7_named_exposure_gate_v4.validate_final_panel(..., enforce_floor=True)`；原 `future_G7_documentary_requirement.v4.json` 的 SHA 与三条永久名字来源 ledger 原样强绑定，不允许注入其他验证器、置空历史名录、用旧 v1/v2/v3 或直接调用简化 panel harness 代替。

2. 入口另外执行显式 PMID/source-alias 的 `assert_zero_leakage`，防止只核对 DOI/PMCID 而漏 PMID；历史 P1–P6 `exposure_ledger.jsonl`、既有 `prior_exposure_rows.jsonl` 为强制原输入。新增 `current_exposure_receipt` 为当前 epoch 必需凭证：须逐一覆盖有效 `epoch_ledger` 上全部 G5/G6 阶段 SHA，绑定实际当前曝光 JSONL，并由固定 A6 与独立 A11 角色清单复核；只提供局部曝光集合或未关闭别名即 fail closed。G4、G6、scope、epoch、来源身份、最终 6–9 targets / >=2 groups 等原硬门不能被关闭或替换。

3. 工程验证：新入口 8 项专项测试全部通过，覆盖缺字段/降门、跨范围/跨 epoch、丢失 28 名字来源/历史 ledger、SHA 格式错误、当前 G5/G6 覆盖遗漏、空 panel、强制实际调用 v4 及无写盘失败。完整 `unittest` **276/276 OK**，日志 `"""+str(log)+"""`；A11 独立有界检查 **20/20 pass、0 fail**，证据 `outputs/task016-p7/v1/verification-v23-g7-writer/independent_G7_writer_verification_v3.json`。早先 7 项版本与 A11 v1（17/18，系审计脚本字符串检查误判）、v2（18/18）均保留而非篡改。

4. 权威新增绑定为 `outputs/task016-p7/v1/governance/G7_writer_integration_v1/production_writer_binding.json`。旧 v4 requirement 的 `actual_G7_writer_integrated=false` 反映当时冻结时点，保留原 bytes；此处新增证据说明**入口现已集成**，但未来完整化学资格、各候选真实 28 名字官方身份对照、当前 epoch 的 A6/A11 全覆盖凭证尚未准备；当前并未实际成功冻结任何 G7，测试中成功路径为受控合成合同注入测试，不是假称真实科学面板。两个家族当前 fresh=0，科学 A/B/E=0 cell、科学指标null，Roadmap P2仍为 In Progress。

5. 不修改 v4 核心验证器、G4/G6、scope/模型/PUCT/库存、来源原件、MCTS 或既有门槛。本轮不新增 HTTP 或 MCTS、不执行 Git commit/push、不升级 human_reviewed/独立化学/formal/release。后续真正最重要的阻断仍是：合法获取新独立原件、正式 G5 先行、双独立完整图与 A6/曝光闭包，达到每轴至少 6 targets、2 groups，随后才允许此次新 G7 writer 实际冻结面板和进入真实 A/B/E。

完整 SHA 索引：`outputs/task016-p7/v1/report_snapshots/progress-v23.json`。
"""
 updated+=section
 save(REPORT,updated)
 k=state.index("\nTASK-016-P7 当前状态progress-v22")
 updated_state=state[:k]+"""
TASK-016-P7 当前状态progress-v23（"""+now+"""）：In Progress / agent_delegated。新增 G7 最终面板正式写入入口 scripts/task016_p7_g7_final_writer.py，写盘前强制 v4 官方命名曝光全28对照、独立 A3/A6 角色证据、永不关闭的每家族>=6targets/2groups、全历史 P1–P6 及 prior_exposure ledger、显式PMID/source-alias闭包；新增 current_exposure_receipt 强制覆盖真实epoch_ledger中全部G5/G6 SHA并绑定当前曝光和A6+A11角色。8专项检查通过，全量单测276/276通过，A11 20/20有界工程审计通过。绑定输出 outputs/task016-p7/v1/governance/G7_writer_integration_v1/production_writer_binding.json；旧冻结 v4 文档当时'G7 writer unintegrated'保留，不回写历史。原v22 REPORT/STATE完整备份按SHA保留。当前未生成真实G7面板，C/SS fresh=0、科学A/B/E=0 cell、metrics=null、Roadmap P2未关闭。后续仍需真实source-qualified新反应与完整曝光闭包；工程入口测试不等同独立化学或科学迁移收益。G4/G6、模型、MCTS、源原件未改；无新HTTP、无新搜索、无Git提交推送、人审/formal/release均未升级。
"""
 save(STATE,updated_state)
 index=dict(task=TASK,status="In Progress",version="progress-v23",at=now,
    previous_progress="progress-v22",
    prior_report_SHA=sha(SNAP/"REPORT-016-P7-prior.md"),
    prior_state_SHA=sha(SNAP/"STATE-prior.md"),
    report_SHA=sha(REPORT),state_SHA=sha(STATE),binding_SHA=sha(BIND),
    G7_writer_SHA=sha(WRITER),A11_G7_SHA=sha(VERIFY),test_SHA=sha(TEST),
    full_test_log_path=str(log),full_test_log_SHA=sha(log),unit_tests=276,
    A11_pass=20,A11_fail=0,actual_G7_panel=False,
    current_fresh_C=0,current_fresh_SS=0,ABE_science_cells=0,scientific_metrics=None,
    no_new_HTTP=True,no_new_MCTS=True,human_reviewed=False,git_synced=False)
 save(INDEX,json.dumps(index,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(dict(version="progress-v23",writer_integrated=True,G7_actual=False,
     tests=276,A11=20,report_SHA=sha(REPORT),state_SHA=sha(STATE))))
if __name__=="__main__":main()

