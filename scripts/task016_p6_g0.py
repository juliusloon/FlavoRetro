"""Offline P5-ERR-06 replay, owner authorization binding and immutable baseline."""
import contextlib
import io
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.task016_p6_common import *
from scripts import task016_p5_flavonol_support as old_support
from scripts import task016_p5_retro_template as old_derive
from rdkit import Chem, rdBase
from rdkit.Chem import rdChemReactions, rdMolDescriptors
from flavoretro.reviewed_resources import canonical_side

def raw_outcomes(smarts, target):
    mol = Chem.MolFromSmiles(target)
    rxn = rdChemReactions.ReactionFromSmarts(smarts)
    rxn.GetSubstructParams().useChirality = True
    out = []
    for products in rxn.RunReactants((mol,)):
        try:
            for p in products:
                Chem.SanitizeMol(p)
            out.append(canonical_side([Chem.MolToSmiles(p, isomericSmiles=True) for p in products]))
        except (ValueError, RuntimeError):
            continue
    return out

def main():
    if (OUT / "approval.json").exists():
        raise RuntimeError("G0 is immutable; do not reset the execution baseline")
    approved_sha = sha(ROOT / CONTRACT)
    inherited = json.loads((ROOT / "outputs/task016-p5/v1/execution_baseline.json").read_text())["protected_sha256"]
    drift = [p for p,h in inherited.items() if not (ROOT/p).is_file() or sha(ROOT/p) != h]
    if drift:
        save("g0_protection_failure.json", dict(drift=drift))
        raise RuntimeError("inherited protection drift")
    mutable = {"STATE.md", "ARCHITECTURE.md", "docs/README.md", "docs/tasks/README.md", "docs/reports/README.md", CONTRACT,
               "flavoretro/cli.py", "flavoretro/contracts.py", "flavoretro/worker.py", "flavoretro/service.py", "flavoretro/workspace.py", "flavoretro/task016_runs.py"}
    protected = {p:h for p,h in inherited.items() if p not in mutable}
    for folder in ("outputs/task016-p5/v1", "data/raw/task016-p5", "configs", "flavoretro/assets/configs"):
        for p in (ROOT/folder).rglob("*"):
            rel = str(p.relative_to(ROOT))
            if p.is_file() and not p.name.startswith("._") and rel not in mutable:
                protected[rel] = sha(p)
    for p in (ROOT/"scripts").glob("task016_p5_*.py"):
        protected[str(p.relative_to(ROOT))] = sha(p)
    for p in (ROOT/"flavoretro").glob("glycoside*.py"):
        protected[str(p.relative_to(ROOT))] = sha(p)
    protected["docs/reports/REPORT-016-P5-c-ss-transfer-capability-closure.md"] = sha(ROOT/"docs/reports/REPORT-016-P5-c-ss-transfer-capability-closure.md")
    originals = {}
    for rel in sorted(mutable):
        if (ROOT/rel).is_file():
            target = "operations/task016-p6-original/" + rel
            write(TASK, target, (ROOT/rel).read_text())
            originals[rel] = dict(sha256=sha(ROOT/rel), snapshot=target)
    git_status = subprocess.run(["git","status","--short"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    head = subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    budgets = dict(total_search_attempts=480, C_first_matrix=81, SS_first_matrix=81, legacy=51,
                   revalidation=213, engineering=54, wall_seconds=60, source_HTTP_attempts=3000,
                   source_bytes=4*1024**3, article_versions=200, attachments=360, per_file_bytes=256*1024**2,
                   per_url_attempts=2, concurrency=4, metadata_records=5000)
    save("approval.json", dict(task=TASK, contract=CONTRACT, approved_contract_sha256=approved_sha,
         approval_quote="`docs/tasks/TASK-016-P6-c-scope-runtime-transfer-closure.md` 批准执行.",
         authorization_origin="owner explicit instruction", approval_type="agent_delegated",
         stage_decisions="agent_delegated", human_reviewed=False, approved_date="2026-10-07",
         budgets=budgets, no_git_sync=True, created_at=datetime.now(timezone.utc).isoformat()))
    save("protected_hashes.json", protected)
    save("execution_baseline.json", dict(contract_sha256=approved_sha, git_head=head, git_status=git_status,
         protected_count=len(protected), inherited_count=len(inherited), inherited_drift=drift,
         mutable_originals=originals, python=sys.version, platform=platform.platform(), rdkit=rdBase.rdkitVersion,
         budgets=budgets, review_manifest_sha256=sha(ROOT/"outputs/review/task015-06/v1/manifest.json")))
    write(TASK, "outputs/task016-p6/v1/run_ledger.jsonl", "")
    # Replay exactly the old helper objects, including their erroneous aglycone graph.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        old_support.main()
    supports = json.loads(buf.getvalue())
    exact = old_derive.derive(supports["P3R-C05"]["acceptor_smiles"], supports["P3R-C05"]["product_smiles"])
    replay = []
    frozen = {r["reaction_id"]:r for r in rows(ROOT/"outputs/task016-p5/v1/reaction_records.jsonl")}
    support_drift = []
    for rid,s in supports.items():
        outputs = raw_outcomes(exact["smarts"], s["product_smiles"])
        replay.append(dict(reaction_id=rid, raw_outcomes=len(outputs),
                           reference_replayed=canonical_side([s["acceptor_smiles"],old_derive.UDP_GLC]) in outputs))
        expected = Chem.MolFromSmiles(frozen[rid]["acceptor_smiles"])
        actual = Chem.MolFromSmiles(s["acceptor_smiles"])
        if canonical_side([s["acceptor_smiles"]]) != canonical_side([frozen[rid]["acceptor_smiles"]]):
            support_drift.append(dict(reaction_id=rid, old_helper_acceptor=s["acceptor_smiles"], frozen_acceptor=frozen[rid]["acceptor_smiles"],
                old_formula=rdMolDescriptors.CalcMolFormula(actual), frozen_formula=rdMolDescriptors.CalcMolFormula(expected),
                decision="old helper objects only retained for error replay; reconstruct G1 from frozen qualified source acceptor and source C8 bond/stereo"))
    save("p5_err06_old_probe_replay.json", dict(exact_template=exact["smarts"], exact_sha256=content_sha(exact["smarts"]),
         left_atoms=rdChemReactions.ReactionFromSmarts(exact["smarts"]).GetReactantTemplate(0).GetNumAtoms(), replay=replay, old_helper_identity_drift=support_drift))
    assert [r["raw_outcomes"] for r in replay] == [2,0], replay
    p3 = (ROOT/"scripts/task016_p3_build.py").read_text().splitlines()
    trace = [dict(line=i,text=s) for i,s in enumerate(p3,1) if 315<=i<=353]
    save("p3_scope_pipeline_trace.json", dict(source_sha256=sha(ROOT/"scripts/task016_p3_build.py"),
         pipeline=["qualified instance", "formation indices in same mapped molecule order", "derive_template_smarts", "scoped_smarts(exact, seed, center)", "scope metadata and structural guard", "support replay", "boundary controls"], calling_context=trace))
    save("p5_err06_reconciliation.json", dict(old_claim="qualified C scope cannot transfer to any heldout target", old_template_kind="exact_instance_template",
         missing_pipeline_step="scoped_smarts", build_support_1_result=replay[0], build_support_2_result=replay[1], old_verdict_valid=False,
         superseded_by="P5-ERR-06", new_scope_qualified=False, historical_payload_rewritten=False, additional_identity_drift=support_drift))
    text = (ROOT/CONTRACT).read_text().replace("- 状态：**Proposed（拟议）**。", "- 状态：**In Progress（已批准执行）**。原起草记录：")
    text += "\n- 2026-10-07 执行登记：所有者明确批准本合同执行，原合同 SHA " + approved_sha + "；批准与阶段决策记录 agent_delegated，来源保留所有者原始指令，非 human_reviewed。独立搜索上限 480；来源预算沿用 P5 数值但独立计账（3000 请求、4GiB、200 文章版本、360 附件）。批准登记见 outputs/task016-p6/v1/approval.json。\n"
    write(TASK, CONTRACT, text)
    event(TASK,"g0_completed",protected=len(protected), old_replay=[2,0], additional_helper_identity_drift=len(support_drift))
    print(json.dumps(dict(protected=len(protected), inherited_drift=drift, replay=replay, additional_helper_identity_drift=support_drift),ensure_ascii=False,indent=2))
if __name__ == "__main__":
    main()
