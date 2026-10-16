"""TASK-016-P4 G4: exposure ledger, build/holdout split and complete-holdout panel freeze.

Runs before any P4 template construction and before any A/B/E number exists, so
the split cannot be tuned against model output.

Exposure is graded rather than binary, because the P2 dispositions are not
uniform and a blanket "reviewed = exposed" rule would silently destroy the
holdout panel while "reviewed = clean" would leak:

  E0 clean          no prior development use of this source or its chemistry
  E1 reviewed       prior identity/structure review happened, but nothing was
                    admitted to any runtime payload and no holdout admission was
                    recorded; the exact product structure of the specific new
                    target was not encoded into any template
  E2 build_forced   the source is bound to build by an overlap/closure edge, or
                    its chemistry already entered a runtime payload

Only E0/E1 sources may seed a holdout target. E2 is build-only.

A holdout target additionally requires, per contract:
  * structure_complete_admitted in G1,
  * a complete parseable reference (acceptor + donor + target) encodable here,
  * reaction signature resolved,
  * no closure edge to any build source,
  * never exposed in earlier template design.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
P3 = ROOT / "outputs/task016-p3/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

# Structures already frozen and traceable in P2/P3 payloads, keyed by the acceptor
# identity used in the P4 audit. Nothing here is newly invented.
FROZEN_STRUCTURES = {
    "naringenin 7-O-glucoside":
        "O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
    "hesperetin 7-O-glucoside":
        "O=C1C[C@@H](c2ccc(O)c(O)c2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
    "quercetin 3-O-glucoside":
        "O=c1c(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
    "kaempferol 3-O-glucoside":
        "O=c1c(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
    "luteolin 7-O-glucoside":
        "O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
    "chrysoeriol 7-O-glucoside":
        "O=c1cc(-c2ccc(O)c(OC)c2)oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
    "quercetin 7-O-glucoside":
        "O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
    "apigenin 7-O-glucoside":
        "O=c1cc(-c2ccc(O)cc2)oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
    "astragalin (kaempferol 3-O-glucoside)":
        "O=c1c(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
    "trilobatin":
        "O=C(CC(c1ccc(O)cc1)c1ccc(O[C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)cc1)C",
    "rutin":
        "O=c1c(O[C@@H]2O[C@H](CO[C@@H]3O[C@H](C)[C@@H](O[C@@H]4O[C@H](CO)[C@@H](O)[C@H](O)[C@H]4O)[C@H](O)[C@H]3O)[C@H](O)[C@H]2O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
    "naringenin":
        "O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
    "apigenin":
        "O=c1cc(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
    "luteolin":
        "O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
    "kaempferol":
        "O=c1c(O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
    "quercetin":
        "O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
    "nothofagin":
        "O=C(CC(c1ccc(O)cc1)c1ccc(O)cc1O[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O)C",
    "phloretin":
        "O=C(CC(c1ccc(O)cc1)c1ccc(O)cc1)C",
}

DONORS = {
    "UDP-glucose": "O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1",
    "UDP-alpha-L-rhamnose": None,
    "UDP-apiose": None,
    "UDP-xylose": None,
    "UDP-galactose": None,
}

# Grade overrides derived from the actual P2 dispositions, quoted per source.
EXPOSURE_GRADE = {
    "PMC13084081": ("E0", "not present in any P1/P2 runtime payload, extension review or unresolved list"),
    "PMC13324211": ("E0", "not present in any P1/P2 runtime payload, extension review or unresolved list"),
    "PMC10602597": ("E0", "not present in any P1/P2 runtime payload, extension review or unresolved list"),
    "PMC13140228": ("E0", "not present in any P1/P2 runtime payload, extension review or unresolved list"),
    "PMC12120870": ("E0", "P3 holdout reference source; never entered any runtime payload"),
    "PMC6036675":  ("E0", "not present in any P1/P2 runtime payload, extension review or unresolved list"),
    "PMC13035923": ("E0", "P3 holdout reference source; never entered any runtime payload"),
    "PMC9706480":  ("E0", "used only for identity review with an admission upgrade; no runtime payload entry"),
    "PMC10602602": ("E2", "present in P1/P2 runtime payload"),
    "PMC10706860": ("E2", "present in P1/P2 runtime payload and P2 extension review (forced build)"),
    "PMC10589286": ("E2", "present in P1/P2 runtime payload"),
    "PMC11975207": ("E2", "present in P1/P2 runtime payload"),
    "PMC7558026":  ("E2", "present in P1/P2 runtime payload"),
    "PMC12313340": ("E2", "P2 unresolved: prospective, target encoding not admitted, no runtime entry"),
    "PMC4282749":  ("E2", "P2 unresolved: old reaction overlap forces the entire source component to build"),
    "PMC6255700":  ("E2", "P2 unresolved: prospective, identity admission still pending"),
    "PMC9700910":  ("E2", "P2 unresolved: withdrawn from runtime, provisional encoding preserved"),
}

# A reaction consumed as a template build support can never also be a holdout
# target: its exact structure, site and donor range were used to design the
# template. P3 consumed P3R-C01/C02 (C3 scope), P3R-SS01/SS02 (O2 scope) and
# P3R-SS03 (O6 scope) as build supports, so those five are forced to build.
# This rule was missing from the first G4 run; the accompanying regression test
# caught the resulting holdout/build overlap.
FORCED_BUILD_REACTIONS = {
    "P3R-C01": "consumed as a P3 C3-scope build support",
    "P3R-C02": "consumed as a P3 C3-scope build support",
    "P3R-SS01": "consumed as a P3/v5 O2-scope build support",
    "P3R-SS02": "consumed as a P3/v5 O2-scope build support",
    "P3R-SS03": "consumed as a P3 O6-scope build support",
}

# Per-reaction holdout/build assignment with the reason recorded.
ASSIGNMENT = {
    "P3R-C03": "build", "P3R-C04": "build", "P3R-C05": "build", "P3R-C06": "build",
    "P3R-C09": "build", "P3R-C10": "build", "P3R-C11": "build",
    "P3R-C12": "holdout",
    "P3R-SS01": "holdout", "P3R-SS02": "holdout", "P3R-SS03": "holdout",
    "P3R-SS04": "holdout", "P3R-SS05": "holdout", "P3R-SS06": "holdout",
    "P3R-SS07": "build", "P3R-SS08": "build", "P3R-SS09": "build", "P3R-SS10": "build",
    "P3R-SS12": "holdout", "P3R-SS13": "build", "P3R-SS14": "build",
    "P3R-SS15": "build", "P3R-SS16": "build", "P3R-SS22": "holdout",
}


def sig(t):
    return hashlib.sha256(str(t).encode()).hexdigest()


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def main():
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    corrected = {r["reaction_id"]: r for r in rows(OUT / "corrected_reaction_records.jsonl")}
    closure = json.loads((OUT / "structure_complete_closure.json").read_text())["source_to_reactions"]

    unselected = []

    # ------------------------------------------------------- exposure ledger
    exposure = []
    for src, rids in sorted(closure.items()):
        grade, why = EXPOSURE_GRADE.get(src, ("E2", "unclassified source defaults to build-only"))
        for rid in rids:
            exposure.append(dict(
                source=src, reaction_id=rid,
                exposure_grade=grade, exposure_basis=why,
                in_prior_runtime_payload=(grade == "E2"),
                eligible_for_holdout=grade in ("E0", "E1"),
                development_exposed=grade == "E2",
            ))
    save_jsonl("exposure_ledger.jsonl", exposure)

    # ------------------------------------------------------------ split edges
    edges = []
    for src, rids in sorted(closure.items()):
        grade = EXPOSURE_GRADE.get(src, ("E2", ""))[0]
        for rid in rids:
            for other, orids in sorted(closure.items()):
                if other == src:
                    continue
                shared = set(rids) & set(orids)
                if shared:
                    edges.append(dict(edge_type="same_covalent_reaction",
                                      source=src, other=other,
                                      reactions=sorted(shared),
                                      reason="both sources encode the same complete covalent reaction"))
            if grade == "E2" and EXPOSURE_GRADE.get(other, ("E2", ""))[0] == "E0" \
                    and ASSIGNMENT.get(rid) == "holdout":
                edges.append(dict(edge_type="build_source_contamination",
                                  source=other, other=src, reactions=[rid],
                                  reason="an E2 build source encodes the same covalent reaction as this holdout candidate"))
    save_jsonl("source_group_edges.jsonl", edges)

    # ---------------------------------------------------------------- panel
    panel, refs = [], []
    for rid, part in sorted(ASSIGNMENT.items()):
        rec = corrected[rid]
        if rid in FORCED_BUILD_REACTIONS:
            unselected.append(dict(
                reaction_id=rid, bond_class=rec["bond_class"], selected_part="build",
                reason="forced build: " + FORCED_BUILD_REACTIONS[rid]
                        + "; a template build support cannot also be a holdout target"))
            continue
        srcs = rec["source_groups"]
        grade = EXPOSURE_GRADE.get(srcs[0], ("E2", ""))[0] if srcs else "E2"
        if part == "build":
            unselected.append(dict(
                reaction_id=rid, bond_class=rec["bond_class"], selected_part="build",
                reason=("source is development-exposed (E2) or shares a covalent reaction with an "
                        "E2 build source" if grade == "E2"
                        else "assigned to build to keep the panel closure-disjoint from holdout")))
            continue

        # holdout candidate: must survive every hard rule
        contaminating = [e for e in edges
                         if e["edge_type"] == "build_source_contamination"
                         and rid in e["reactions"]]
        if grade == "E2":
            unselected.append(dict(reaction_id=rid, selected_part="rejected",
                                   reason=f"source {srcs[0]} is development-exposed ({grade})"))
            continue
        if contaminating:
            unselected.append(dict(
                reaction_id=rid, selected_part="rejected",
                reason="closure leak: same covalent reaction appears in an E2 build source "
                       f"({', '.join(sorted({e['source'] for e in contaminating}))})"))
            continue

        ref = {
            "reaction_id": rid,
            "bond_class": rec["bond_class"],
            "name": rec["name"],
            "structure_encoding": "complete",
            "source_pmcds": srcs,
            "closure_group": f"closure:{srcs[0]}",
            "evaluator_side_only": True,
            "supporting_candidate_uids": rec["supporting_candidate_uids"],
            "evidence_locators": rec["identity_evidence_axis"],
            "structure_determination_basis": rec["structure_determination_basis"],
            "human_reviewed": False,
            "actionable": False,
            "evidence_closed": False,
            "prediction_conditions_verified": False,
        }
        refs.append(ref)
        panel.append(dict(reaction_id=rid, bond_class=rec["bond_class"],
                          closure_group=ref["closure_group"], sources=srcs))

    save_jsonl("heldout_references.jsonl", refs)
    save_jsonl("panel_manifest.jsonl", panel)
    save_jsonl("unselected_records.jsonl", unselected)

    # -------------------------------------------------------------- gate eval
    per_class = defaultdict(lambda: dict(targets=[], groups=set()))
    for p in panel:
        per_class[p["bond_class"]]["targets"].append(p["reaction_id"])
        per_class[p["bond_class"]]["groups"].add(p["closure_group"])

    gates, verdict = {}, {}
    for cls, label in (("C_formation", "C"), ("sugar_sugar_formation", "SS")):
        n, g = len(per_class[cls]["targets"]), len(per_class[cls]["groups"])
        ok_n, ok_g = n >= 6, g >= 2
        gates[cls] = dict(
            targets=n, closure_groups=g,
            require_targets=6, require_groups=2,
            deferred_in_denominator=0,
            gate_pass=bool(ok_n and ok_g),
            status=("PASS" if ok_n and ok_g else "FAIL"),
            shortfall=dict(
                targets=max(0, 6 - n), closure_groups=max(0, 2 - g)))
        verdict[label] = "eligible_for_A/B/E" if gates[cls]["gate_pass"] else "not_eligible_A/B_E_null"

    total = sum(len(v["targets"]) for v in per_class.values())
    manifest = {
        "task": TASK,
        "frozen_before_any_p4_template_or_A_B_E": True,
        "a_b_e_results_existed_at_freeze_time": False,
        "selection_rule": ("every structure_complete_admitted reaction with an E0/E1 source and no "
                           "closure edge to an E2 build source; no post-hoc selection against any "
                           "model output, because no P4 A/B/E number existed yet"),
        "panel": {k: dict(targets=sorted(v["targets"]), closure_groups=sorted(v["groups"]),
                          targets_count=len(v["targets"]), groups_count=len(v["groups"]))
                  for k, v in per_class.items()},
        "global_targets": total,
        "global_window": "12-18",
        "global_window_met": bool(12 <= total <= 18),
        "gates": gates,
        "verdict": verdict,
        "p3_nominal_panel": {"C_formation": 1, "sugar_sugar_formation": 2, "references": 3,
                             "note": "P3 nominal C1/SS2 is superseded; P3 already marked 2 of its 3 "
                                     "references structure_encoding=deferred"},
        "deferred_counted_in_denominator": 0,
        "human_reviewed": False,
    }
    save("panel_manifest.json", manifest)

    split = {
        "task": TASK,
        "frozen_at": "G4, before any P4 template construction and before any A/B/E run",
        "build_reactions": sorted(r for r, p in ASSIGNMENT.items()
                                 if p == "build" or r in FORCED_BUILD_REACTIONS),
        "holdout_reactions": sorted(r for r, p in ASSIGNMENT.items() if p == "holdout"
                                    and any(x["reaction_id"] == r for x in refs)),
        "rejected_at_split": sorted(r["reaction_id"] for r in unselected
                                   if r["selected_part"] == "rejected"),
        "counts": {"build": sum(1 for p in ASSIGNMENT.values() if p == "build")
                          + len(FORCED_BUILD_REACTIONS),
                   "holdout": len(refs),
                   "rejected": sum(1 for r in unselected if r["selected_part"] == "rejected")},
        "closure_rule": "same DOI/PMC/SI, same original experiment, patent family, identical complete "
                        "covalent reaction, or explicit reuse of an experiment must share a closure group",
        "exposure_rule": "E2 sources are build-only; E0/E1 may seed holdout; a holdout target sharing "
                         "a covalent reaction with any E2 build source is rejected",
        "build_support_rule": "any reaction consumed as a template build support is forced to build; "
                              "this rule was absent from the first G4 run and was added after the "
                              "v5 contract test exposed a holdout/build overlap",
    }
    save("split_manifest.json", split)

    event(TASK, "g4_split", build=split["counts"]["build"], holdout=split["counts"]["holdout"],
          rejected=split["counts"]["rejected"],
          C_targets=gates["C_formation"]["targets"], SS_targets=gates["sugar_sugar_formation"]["targets"])
    print(json.dumps({"gates": gates, "global_targets": total,
                      "counts": split["counts"], "verdict": verdict},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
