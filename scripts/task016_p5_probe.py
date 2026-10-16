"""TASK-016-P5 G3b: structure-level transfer probe.

This is not a search and costs no budget. It applies the qualified C scope template
to every leakage-free C holdout target and asks a single question: can this scope
reach this substrate at all?

The distinction matters for how P5 reports itself. "The transfer gate will fail"
and "the transfer gate was measured and failed" are different claims, and only the
second is evidence. A template that cannot fire on a target makes the MCTS matrix
uninformative for that target, because no search budget can create an action the
expansion strategy never generates. Running 63 cells to confirm a structural
impossibility would spend a seventh of the P5 budget to learn nothing.

So the probe runs first, and its result decides whether the A/B/E matrix is worth
executing at all. Every target is probed with both the scope guard and the raw
template, so a miss can be attributed either to the SMARTS or to the declared
applicability, rather than left ambiguous.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

CORE = "O=C1Oc2c(O)cc(O)cc2OC(c2ccccc2)=C1O"


def probe(smarts, target_smiles, donor_smiles, core=CORE):
    """Return (raw_outcomes, core_matches) for one target."""
    from rdkit import Chem
    from rdkit.Chem import rdChemReactions
    mol = Chem.MolFromSmiles(target_smiles)
    if mol is None:
        return 0, False
    query = Chem.MolFromSmarts(core)
    core_ok = bool(query) and mol.HasSubstructMatch(query)
    rxn = rdChemReactions.ReactionFromSmarts(smarts)
    rxn.GetSubstructParams().useChirality = True
    n = 0
    for products in rxn.RunReactants([mol]):
        try:
            for p in products:
                Chem.SanitizeMol(p)
        except (ValueError, RuntimeError):
            continue
        n += 1
    return n, core_ok


def main():
    import importlib.util, io, contextlib
    from rdkit import Chem
    sys.path.insert(0, str(ROOT / "scripts"))

    spec = importlib.util.spec_from_file_location(
        "sup", ROOT / "scripts/task016_p5_flavonol_support.py")
    sup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sup)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sup.main()
    built = json.loads(buf.getvalue())

    spec = importlib.util.spec_from_file_location(
        "rt", ROOT / "scripts/task016_p5_retro_template.py")
    rt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rt)
    derived = rt.derive(built["P3R-C05"]["acceptor_smiles"],
                        built["P3R-C05"]["product_smiles"])

    panel = json.loads((OUT / "panel_manifest.json").read_text())
    refs = [json.loads(l) for l in (OUT / "heldout_references.jsonl").read_text().splitlines()
            if l.strip()]
    records = {r["reaction_id"]: r for r in
               [json.loads(l) for l in (OUT / "reaction_records.jsonl").read_text().splitlines()
                if l.strip()]}

    results, unreachable = [], []
    for cls, label in (("C_formation", "C"), ("sugar_sugar_formation", "SS")):
        ids = panel["panel"].get(cls, {}).get("targets", [])
        for rid in ids:
            rec = records[rid]
            target = rec.get("product_smiles") or ""
            if not target:
                results.append(dict(reaction_id=rid, bond_class=cls,
                                    probed=False,
                                    reason="no encodable product structure is bound to this "
                                           "record, so the substrate cannot be handed to the "
                                           "runtime at all"))
                unreachable.append(rid)
                continue
            if cls != "C_formation":
                continue
            n, core_ok = probe(derived["smarts"], target, rt.UDP_GLC)
            results.append(dict(reaction_id=rid, bond_class=cls, probed=True,
                                target=target, raw_outcomes=n,
                                declared_core_matches=core_ok,
                                reachable=bool(n and core_ok)))
            if not (n and core_ok):
                unreachable.append(rid)

    c_rows = [r for r in results if r["bond_class"] == "C_formation"]
    reachable = [r["reaction_id"] for r in c_rows if r.get("reachable")]
    summary = {
        "task": TASK,
        "kind": "structure_level_transfer_probe",
        "costs_search_budget": False,
        "question": "can the qualified P5 C scope template produce any outcome on each "
                    "leakage-free C holdout target, and does the declared applicability "
                    "core admit that target?",
        "scope_center_class": "flavonol_8_C_glucoside",
        "declared_core": CORE,
        "build_supports": sorted(built),
        "c_rows": c_rows,
        "c_reachable_targets": reachable,
        "c_unreachable_targets": unreachable,
        "verdict": ("the qualified C scope reaches none of the leakage-free C holdout "
                    "targets" if not reachable else
                    f"the qualified C scope reaches {len(reachable)} target(s)"),
        "consequence": (
            "the C transfer gate cannot be met by this build scope: every leakage-free C "
            "holdout target is either outside the declared flavonol applicability or "
            "lacks an encodable structure. Executing the A/B/E matrix would measure a "
            "structural impossibility, so the matrix is not run and the C transfer metrics "
            "stay null."
            if not reachable else
            "the A/B/E matrix is executable for C and is run."),
        "why_this_is_structural": (
            "the only structure-complete C reactions available as build supports all come "
            "from development-exposed sources, which the exposure rule makes build-only. "
            "Every flavonol C-glycosylation source P5 found is therefore build-side, while "
            "every leakage-free C holdout target happens to be a flavone, a benzophenone or "
            "a gallic acid. Build chemistry and holdout chemistry are disjoint by "
            "construction, so a scope declared strictly by its supports cannot reach the "
            "panel. Widening the declared core to cover the holdout would import "
            "holdout-side chemistry into the build design, which the contract forbids."),
        "not_a_transfer_claim": "this probe says nothing about activity, selectivity, "
                               "conditions or yield; it says only whether the template can "
                               "fire at all",
    }
    write(TASK, str((OUT / "transfer_probe.json").relative_to(ROOT)),
          json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    event(TASK, "g3b_transfer_probe", c_targets=len(c_rows),
          reachable=len(reachable), unreachable=len(unreachable))
    print(json.dumps(dict(
        c_rows=[{k: r.get(k) for k in ("reaction_id", "raw_outcomes",
                                       "declared_core_matches", "reachable", "probed")}
                for r in c_rows],
        reachable=reachable, verdict=summary["verdict"],
        consequence=summary["consequence"][:200] + "..."),
        ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())