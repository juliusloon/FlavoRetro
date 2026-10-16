"""G3 immutable applicability probe; no tuning, scope mutation or MCTS."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
from flavoretro.glycoside_scope import apply_c_scope
from flavoretro.reviewed_resources import canonical_side

def probe_frozen(scope_path, panel_path, expected_scope_sha, expected_panel_sha):
    if sha(scope_path)!=expected_scope_sha or sha(panel_path)!=expected_panel_sha:raise ValueError("frozen probe input drift")
    import json
    t=json.loads(Path(scope_path).read_text()); panel=rows(panel_path)
    results=[]
    for r in panel:
        outcomes=apply_c_scope(t,r["product_smiles"])
        matched=canonical_side(r["reference_precursors"]) in [o["precursors"] for o in outcomes]
        results.append(dict(reaction_id=r["reaction_id"],closure_group=r["closure_group"],scope_applicable=bool(outcomes),
            number_of_candidate_matches=len(outcomes),reference_precursor_match=matched,
            reason_if_not_applicable=None if matched else "outside frozen flavonol C8 core/site declaration; no reference outcome"))
    if sha(scope_path)!=expected_scope_sha or sha(panel_path)!=expected_panel_sha:raise RuntimeError("probe mutated frozen input")
    return results

def main():
    m=load("c_panel_manifest.json")
    if not m["gate"]["passed"]:
        save("c_preflight.json",dict(passed=False,probe_executed=False,stop_condition=3,reason="C_runtime_panel_failure",gate=m["gate"]))
        return
    results=probe_frozen(OUT/"c_scope_template.json",OUT/"c_heldout_references.jsonl",sha(OUT/"c_scope_template.json"),m["reference_sha256"])
    good=[r for r in results if r["reference_precursor_match"]]
    groups={r["closure_group"] for r in good};passed=len(good)>=3 and len(groups)>=2
    save_rows("c_scope_applicability.jsonl",results)
    save("c_preflight.json",dict(passed=passed,probe_executed=True,applicable_targets=len(good),applicable_groups=len(groups),
        reason="measurable_C_transfer" if passed else "scope_holdout_domain_mismatch",stop_condition=None if passed else 6,
        exact_build_replay=2,scope_hash=sha(OUT/"c_scope_template.json"),panel_hash=m["reference_sha256"],model_transfer_failure=False,
        C_ABE_required=passed,SS_can_block_C=False))
    print(load("c_preflight.json"))
if __name__=="__main__":main()
