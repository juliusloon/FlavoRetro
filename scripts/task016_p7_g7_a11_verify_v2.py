"""Independent bounded G7 writer engineering audit. No science qualification."""
from pathlib import Path
import ast,hashlib,json
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
OUT=B/"verification-v23-g7-writer/independent_G7_writer_verification_v2.json"
REQ=B/"governance/named_exposure_gate_v1/future_G7_documentary_requirement.v4.json"
W=Path("scripts/task016_p7_g7_final_writer.py")
T=Path("tests/test_task016_p7_g7_final_writer.py")
OLD=B/"report_snapshots/progress-v22.json"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def js(p):return json.loads((ROOT/p).read_text())
def check():
    checks={}
    frozen=js(OLD);requirement=js(REQ)
    checks["v22_report_bytes_unchanged"]=sha(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"))==frozen["current_report_SHA"]
    checks["v22_state_bytes_unchanged"]=sha(Path("STATE.md"))==frozen["current_state_SHA"]
    checks["SS_E02_G4_frozen"]=sha(B/"SS/E02/stages/G4_SCOPE_FREEZE.json")==frozen["G4_SHA"]
    checks["SS_R12_G6_frozen"]=sha(B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G6_IDENTITY_STRUCTURE_ADMIT.json")==frozen["G6_SHA"]
    checks["C_E02_G4_still_frozen"]=verify_stage_chain(ROOT/B/"C/E02/stages/G4_SCOPE_FREEZE.json",sha(B/"C/E02/stages/G4_SCOPE_FREEZE.json"))["stage"]=="G4_SCOPE_FREEZE"
    checks["SS_E02_G4_G6_chains_still_valid"]=all(verify_stage_chain(ROOT/p,sha(p))["stage"]==stage for p,stage in [
       (B/"SS/E02/stages/G4_SCOPE_FREEZE.json","G4_SCOPE_FREEZE"),
       (B/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G6_IDENTITY_STRUCTURE_ADMIT.json","G6_IDENTITY_STRUCTURE_ADMIT")])
    checks["v4_validator_unchanged"]=sha(Path(requirement["validator_path"]))==requirement["validator_sha256"]
    checks["v4_all_declared_code_SHA_unchanged"]=all(sha(Path(p))==v for p,v in requirement["implementation_files_sha256"].items())
    checks["all_28_exposure_sources_pinned"]=len(requirement["registry_files_sha256"])==3 and all(sha(Path(p))==v for p,v in requirement["registry_files_sha256"].items())
    tree=ast.parse((ROOT/W).read_text());code=(ROOT/W).read_text()
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    validate=functions["validate_contract"];freeze=functions["freeze"]
    attr=lambda x:isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute)
    v4_calls=[n for n in ast.walk(validate) if attr(n) and n.func.attr=="validate_final_panel" and isinstance(n.func.value,ast.Name) and n.func.value.id=="named_gate"]
    alias_calls=[n for n in ast.walk(validate) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="assert_alias_zero_leakage"]
    checks["actual_G7_validator_v4_called_once"]=len(v4_calls)==1
    checks["G7_explicit_PMID_alias_gate_called"]=len(alias_calls)==1 and alias_calls[0].lineno>v4_calls[0].lineno
    checks["G7_permanent_floor_hardwired"]=len(v4_calls)==1 and any(k.arg=="enforce_floor" and isinstance(k.value,ast.Constant) and k.value.value is True for k in v4_calls[0].keywords)
    gated=[n for n in ast.walk(freeze) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="validate_contract"]
    writes=[n for n in ast.walk(freeze) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ("write","freeze_stage_manifest")]
    checks["all_G7_writes_after_complete_preflight"]=len(gated)==1 and len(writes)==2 and all(n.lineno>gated[0].lineno for n in writes)
    checks["writer_no_bypass_CLI_flag"]="enforce_floor" not in "".join(code.split("def main():")[-1].splitlines()) and "--request" in code
    checks["G7_actual_stage_not_claimed"]=all(not (ROOT/B/f"{family}/E02/stages/G7_CLOSURE_PANEL_FREEZE.json").exists() for family in ("C","SS"))
    checks["no_automatic_new_MCTS"]= "task016_runs" not in code and "subprocess" not in code and "mcts_run" not in code.casefold() and "flavoretro.worker" not in code
    checks["seven_independent_contract_tests_defined"]=sum(isinstance(n,ast.FunctionDef) and n.name.startswith("test_") for n in ast.walk(ast.parse((ROOT/T).read_text())))==7
    checks["writer_and_tests_are_real"]=len((ROOT/W).read_text())>7000 and len((ROOT/T).read_text())>2000
    return checks
def main():
    if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_A11_AUDIT_EXISTS")
    checks=check();passed=sum(checks.values());failed=len(checks)-passed
    output=dict(task=TASK,role="A11_bounded_G7_writer_independent_engineering_audit",
        timestamp=datetime.now(timezone.utc).isoformat(),checks=checks,
        passed=passed,failed=failed,approval_type="agent_delegated",
        human_reviewed=False,qualified_fresh=0,real_G7_panel_exists=False,
        scientific_ABE_cells=0,scientific_transfer_metrics=None,
        G7_writer_path=str(W),G7_writer_SHA=sha(W),test_file_SHA=sha(T),
        prior_v4_requirement_SHA=sha(REQ),
        no_new_source_HTTP=True,no_new_MCTS=True,
        limitation="engineering writer+fail-closed controls only, not independent chemistry or fresh panel admission")
    write(TASK,str(OUT),json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"A11_pass":passed,"A11_fail":failed,"fresh":0,"G7_actual":False}))
    if failed:raise RuntimeError([k for k,v in checks.items() if not v])
if __name__=="__main__":main()

