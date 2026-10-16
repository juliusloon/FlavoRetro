"""Conservative independent budget and real/fixture accounting from raw provenance."""
import json
from pathlib import Path
from scripts.task016_p7_orchestrate import save_json,sha_file,now
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1"
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def recompute():
    ledger=O/"run_ledger.jsonl";rs=rows(ledger);starts={};ends={};decisions=[]
    for row in rs:
        if row["phase"]=="started":
            if row["run_id"] in starts:raise RuntimeError("duplicate budget start")
            starts[row["run_id"]]=row
        else:
            if row["run_id"] in ends:raise RuntimeError("duplicate budget terminal")
            ends[row["run_id"]]=row
    for rid,end in ends.items():
        if rid not in starts or starts[rid]["purpose"]!=end["purpose"]:raise RuntimeError("terminal reservation mismatch")
        path=Path(end["manifest"]);real=end.get("execution_source")=="live_aizynthfinder_mcts"
        if real:
            if not path.is_relative_to(R) or not path.is_file():raise RuntimeError("real MCTS provenance missing")
            result=path.with_name("result.json");raw=json.loads(result.read_text())
            if raw["run_id"]!=rid or raw["execution_source"]!="live_aizynthfinder_mcts" or not raw.get("phases") or any(x["engine_class"]!="flavoretro.search.SearchTree" for x in raw["phases"]):raise RuntimeError("real MCTS physical provenance incomplete")
            decision=dict(run_id=rid,purpose=end["purpose"],effective_class="real_MCTS",raw_manifest_sha256=sha_file(path),raw_result_sha256=sha_file(result),raw_path=str(result.relative_to(R)))
        elif end.get("synthetic_fixture") is True and end["purpose"]=="p7_engineering" and str(path).startswith("/tmp/"):
            decision=dict(run_id=rid,purpose=end["purpose"],effective_class="synthetic_fixture",raw_path=str(path),fixture_type=end.get("error",{}).get("code"),source="governed unittest failure/timeout fixture; never scientific")
        else:
            decision=dict(run_id=rid,purpose=end["purpose"],effective_class="failed_real_attempt_or_unproven",raw_path=str(path),counted_conservatively=True)
        decision["original_start_fixture_flag"]=starts[rid].get("synthetic_fixture")
        decision["original_terminal_fixture_flag"]=end.get("synthetic_fixture")
        decision["classification_correction"]=real and bool(starts[rid].get("synthetic_fixture") or end.get("synthetic_fixture"))
        decisions.append(decision)
    limits={"p7_C_validation":81,"p7_SS_validation":81,"p7_legacy_canary":90,"p7_engineering":60,"p7_revalidation":252}
    counts={purpose:sum(x["purpose"]==purpose for x in starts.values()) for purpose in limits}
    if len(starts)>600 or any(counts[x]>limits[x] for x in counts):raise RuntimeError("approved search budget exceeded")
    return dict(task="TASK-016-P7",as_of=now(),ledger_sha256=sha_file(ledger),reserved_attempts=len(starts),terminal_attempts=len(ends),pending=len(set(starts)-set(ends)),category_counts=counts,category_limits=limits,total_limit=600,real_MCTS=sum(x["effective_class"]=="real_MCTS" for x in decisions),synthetic_fixture=sum(x["effective_class"]=="synthetic_fixture" for x in decisions),failed_or_unproven=sum(x["effective_class"]=="failed_real_attempt_or_unproven" for x in decisions),decisions=decisions,original_ledger_preserved=True,classification_policy="physical raw engine phases and immutable result identity take precedence over suite intent flag; all starts consume budget")
if __name__=="__main__":
    value=recompute();out=O/"budget_accounting_latest.json";save_json(out,value);print({k:v for k,v in value.items() if k not in ["decisions"]})
