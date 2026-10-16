#!/usr/bin/env python3
"""TASK-016-P3 G3 panel freeze: emit panel_manifest.json and
heldout_references.jsonl from the frozen split_manifest.

Honesty rules: P3R-SS22 ships a complete SMILES reference; P3R-C12 and
P3R-SS23 references are evidence-bound (names/locators/conditions) with
structure encoding explicitly deferred — no SMILES are fabricated.  The
holdout references are evaluator-side data only; they are never part of the
runtime registry payload."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from scripts.task016_p3_sources import write as _reg_write, TASK as _TASK  # noqa: E402
from scripts.operate import run as _run  # noqa: E402

V1 = ROOT / "outputs/task016-p3/v1"

ASTRAGALIN = "O=c1c(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12"
GENTIOBIOSIDE_TARGET = ("O=c1c(O[C@@H]2O[C@H](CO[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)"
                        "[C@@H](O)[C@H](O)[C@H]2O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12")
UDP_GLC = "O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1"


def main():
    split = json.loads((V1 / "split_manifest.json").read_text())
    reactions = {r["reaction_id"]: r for r in
                 (json.loads(l) for l in (V1 / "reaction_records.jsonl").open() if l.strip())}
    holdout_ids = split["holdout_targets_by_class"]

    references = []
    for cls, ids in holdout_ids.items():
        for rid in ids:
            r = reactions[rid]
            ref = dict(
                reaction_id=rid, bond_class=cls,
                source_pmcds=r["source_pmcds"],
                supporting_candidate_uids=r["supporting_candidate_uids"],
                evidence_locators=[loc for ctx in r["reference_context"] for loc in ctx["evidence_locators"]],
                evaluator_side_only=True)
            if rid == "P3R-SS22":
                ref.update(
                    reference=dict(acceptor=ASTRAGALIN, donor=UDP_GLC, target=GENTIOBIOSIDE_TARGET),
                    structure_encoding="complete",
                    linkage="beta-D-Glc-(1->6)-beta-D-Glc on the kaempferol 3-O-glucoside",
                    note="structures validated by the frozen structural_formation (1->6 site reported unresolved by the frozen classifier, see local P3 derivation in the build record)")
            elif rid == "P3R-C12":
                ref.update(
                    reference=dict(acceptor_name="8-bromo-5,7-dimethoxy-2-(4-methoxyphenyl)-4H-chromen-4-one (91)",
                                   donor_name="C2-OH unprotected beta-D-glucosyl stannane 45n",
                                   product_name="8-((2S,3S,4R,5R,6R)-glucosyl)-5,7-dimethoxy-2-(4-methoxyphenyl)-4H-chromen-4-one (92); BCl3 debenzylation to 93"),
                    structure_encoding="deferred",
                    structure_encoding_reason="regiochemistry relies on figure inspection; no SMILES fabricated",
                    context="chemical (Pd-catalysed Stille glycosylation)")
            else:
                ref.update(
                    reference=dict(acceptor_name="mini-MbA (myricetin acylated 3-O-glucoside, montbretin biosynthesis intermediate)",
                                   donor_name="UDP-glucose",
                                   product_name="MbA-XR2 (1,2-beta-D-glucosylated sugar moiety)"),
                    structure_encoding="deferred",
                    structure_encoding_reason="acylated aglycone structure requires figure/SI verification; no SMILES fabricated",
                    context="enzymatic (CcUGT3/UGT703E1; three assay contexts in reaction record)")
            references.append(ref)

    manifest = dict(
        task="TASK-016-P3",
        frozen_before_templates=True,
        selection_rule=("all admitted new reactions whose closure component contains no "
                        "development-exposed source; no post-hoc selection against any "
                        "model output (A/B/E did not exist at freeze time)"),
        panel=dict(
            C_formation=dict(targets=holdout_ids["C_formation"], groups=len({r["source_pmcds"][0] for r in references if r["bond_class"] == "C_formation"})),
            sugar_sugar_formation=dict(targets=holdout_ids["sugar_sugar_formation"], groups=len({r["source_pmcds"][0] for r in references if r["bond_class"] == "sugar_sugar_formation"})),
        ),
        gate_status=dict(
            required=">=6 targets and >=2 closure groups per class",
            C_formation="FAIL (1 target / 1 group) - transfer metrics not executed, reported null",
            sugar_sugar_formation="FAIL (2 targets / 2 groups; group count met, target count short) - transfer metrics not executed, reported null",
        ),
        references=len(references),
    )
    _reg_write(_TASK, "outputs/task016-p3/v1/panel_manifest.json",
               json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _reg_write(_TASK, "outputs/task016-p3/v1/heldout_references.jsonl",
               "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in references))
    print("panel manifest:", json.dumps(manifest["panel"], ensure_ascii=False))
    print("references:", len(references))
    return 0


if __name__ == "__main__":
    sys.exit(main())
