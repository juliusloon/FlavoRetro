"""Root documentary replay of progress v13; explicitly not independent audit."""
import json,re,subprocess,ast
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_hashes,verify_stage_chain
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
def js(p):return json.loads(p.read_text())
def main():
    p=BASE/"report_snapshots/progress-v13.json";s=js(p);checks=[]
    def ck(name,ok):
        checks.append(dict(name=name,passed=bool(ok)))
        if not ok:raise ValueError(name)
    for k in ("report_pointer","state_pointer","prior_report_archive","prior_state_archive","parent_snapshot"):
        q=s[k];ck(k,sha_file(ROOT/q["path"])==q["sha256"])
    for path,b in s["inputs"].items():
        ck("live "+path,sha_file(ROOT/path)==b["sha256"]);a=b["physical_archive"];ck("archive "+path,sha_file(ROOT/a["path"])==a["sha256"]==b["sha256"])
    report=(ROOT/s["report_pointer"]["path"]).read_text();state=(ROOT/s["state_pointer"]["path"]).read_text()
    section=report.split("## 合同要求的 20 项直接回答\n")[1].split("## 验证、偏差与尚待执行")[0]
    ck("twenty sequential answers",[int(x) for x in re.findall(r"^(\d+)\. ",section,re.M)]==list(range(1,21)))
    ck("report current pointer","report_snapshots/progress-v13.json" in report)
    current=next(x for x in state.splitlines() if x.startswith("TASK-016-P7（"))
    ck("current scientific boundary",all(x in current for x in ("In Progress","fresh0","科学A/B/E0cell","metricsnull","未有SS新bank/G2/G3/G4","P2/formal/release未关闭")))
    ck("snapshot not complete",s["goal_completed"] is False and s["fresh_C"]==s["fresh_SS"]==s["scientific_ABE_cells"]==0 and s["metrics"] is None)
    epoch=js(BASE/"epochs/C-E02/epoch_state.v7.json");ck("stage counts",epoch["G5_batches"]==6 and epoch["G6_batches"]==5 and epoch["G6_admitted"]==0)
    g=BASE/"C/E02/stages/batches/C-E02-R7/G6_IDENTITY_STRUCTURE_ADMIT.json";chain=verify_stage_chain(g,sha_file(g));ck("C-R7 G6 recursive chain",chain["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT")
    c=js(BASE/"C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/A6_source_reconciliation_summary.json")
    ck("C378 and11 andzero admission",c["independently_equal_literal_records"]==378 and c["canonical_full_graph_and_formula_matches"]==11 and c["fresh_admitted"]==0 and not c["full_chemical_round_complete"] and not c["source_saturation"])
    ss=js(BASE/"SS/E02_design/reference_discovery_r2/Petunia_A6_v1/A6_source_reconciliation_summary.json")
    ck("Petunia two supports no scope",ss["source_qualified_design_supports"]==2 and ss["distinct_complete_canonical_acceptors"]==2 and ss["no_scope_frozen"] is True and ss["fresh_admitted"]==0)
    ck("Petunia36 values and1mz",ss["table_cells_equal"]==36 and ss["mz_literal_equal"]==35 and ss["mz_source_arbitrated_differences"]==1)
    for rel in ("C/E02/fresh/C-E02-R7/A6_source_reconciliation_v1/role_A6_manifest.json","SS/E02_design/reference_discovery_r2/Petunia_A6_v1/role_A6_manifest.json"):
        role=js(BASE/rel);verify_hashes(role["input_manifest_sha"]);verify_hashes(role["output_file_sha"]);ck("role replay "+rel,True)
    budget=js(ROOT/s["budget_pointer"]["path"]);ck("883 budget prefix",budget["totals"]["HTTP"]==883 and budget["totals"]["bytes"]==1193878292 and budget["capture_finished_at"]=="2026-10-10T11:30:45.233474+00:00")
    ck("roles not chemistry validation",all(x in report for x in ("不等于合格scope、fresh或独立化学验证","611.1616","611.1618","后处理","定量纯度")))
    git=subprocess.run(["git","diff","--check"],cwd=ROOT,capture_output=True,text=True);ck("git diff --check",git.returncode==0)
    tracked=subprocess.run(["git","ls-files","data/raw/task016-p7","outputs/task016-p7"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.splitlines();ck("raw outputs tracked0",not tracked)
    ast.parse((ROOT/"scripts/task016_p7_progress_v13_v1.py").read_text());ck("writer AST",True)
    out=BASE/"report_snapshots/progress-v13-root-documentary-verification-v2.json";immutable_json(out,dict(task=TASK,at=now(),root_authored=True,independent_A12_audit=False,snapshot=pointer(p),checks=checks,pass_count=len(checks),fail_count=0,scientific_pending=True,overall_completed=False,new_HTTP=0,new_MCTS=0))
    print(json.dumps(dict(path=str(out.relative_to(ROOT)),sha256=sha_file(out),passed=len(checks),failed=0)))
if __name__=="__main__":main()
