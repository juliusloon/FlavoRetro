"""TASK-016-P5 G2: exposure ledger, build/holdout isolation and panel freeze.

This runs before any P5 template exists and before any A/B/E number exists, so the
split cannot have been tuned against model output.

The isolation rules are the whole point of this stage, and each one exists because
P3 or P4 broke it:

  R1  a reaction consumed as a template build support is forced to build and can
      never also be a holdout target
  R2  a holdout target may not share an E2 (development-exposed) source with any
      build reaction
  R3  a holdout target may not encode the same complete covalent reaction as any
      build reaction
  R4  the same canonical acceptor reported by several papers, enzymes or assays
      counts once toward the >=2 acceptor gate
  R5  deferred / inferred / name-only records never enter N_family

R4 matters because P4's whole C shortfall came from counting sources instead of
acceptors. R1 matters because P4's first G4 panel put P3R-SS01/02/03 into holdout
while v5 was simultaneously built from them, and only a contract test caught it.

Whatever the gates return, this script records them. A failing gate is a finding,
not an error to be papered over.
"""
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
P4 = ROOT / "outputs/task016-p4/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

MIN_TARGETS = 6
MIN_GROUPS = 2
GLOBAL_MIN = 12
GLOBAL_MAX = 18
MAX_PER_CLASS = 9


def rows(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def sig(text):
    return hashlib.sha256(str(text).encode()).hexdigest()


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


# ---------------------------------------------------------------------------
# Build-side scope selection.
#
# The C class needs a genuinely new build scope with >=2 distinct canonical
# acceptors. The only E2 (build-forced) C reactions that are structure-complete
# and not already represented in the v3 baseline payload are the PMC9700910
# kaempferol/quercetin 8-C-glucoside pair. Using them costs the holdout nothing,
# because E2 sources are build-only anyway. That is why they are chosen here:
# the build side is filled from E2 first, precisely so the holdout pool is not
# cannibalised.
#
# The SS class reuses the P4-revalidated rhamnoside_glucoside_O2 scope, whose
# build supports P3R-SS01/SS02 are already forced to build, and adds the new P5
# 1->4 rhamnosylation scope when it qualifies.
# ---------------------------------------------------------------------------

C_BUILD_SUPPORTS = ["P3R-C05", "P3R-C06"]
SS_BUILD_SUPPORTS = ["P3R-SS01", "P3R-SS02"]
SS_BUILD_SUPPORTS_P5 = ["P5R-SS01", "P5R-SS02"]

FORCED_BUILD = {
    **{r: "consumed as a P5 build support for a C or SS scope template; a build "
          "support cannot also be a holdout target (R1)"
        for r in C_BUILD_SUPPORTS + SS_BUILD_SUPPORTS + SS_BUILD_SUPPORTS_P5},
    # already consumed by the frozen v5 payload
    "P3R-C09": "already an exact-instance support in the frozen v3 payload",
    "P3R-C10": "already an exact-instance support in the frozen v3 payload",
    "P3R-C11": "already an exact-instance support in the frozen v3 payload",
}


def main():
    records = {r["reaction_id"]: r for r in rows(OUT / "reaction_records.jsonl")}
    complete = {k: v for k, v in records.items() if v["structure_complete"]}

    # --------------------------------------------------------- exposure ledger
    exposure = []
    for rid, rec in sorted(complete.items()):
        exposure.append(dict(
            reaction_id=rid,
            bond_class=rec["bond_class"],
            source=rec["source"],
            closure_group=rec["closure_group"],
            exposure_grade=rec["exposure_grade"],
            exposure_basis=rec.get("exposure_basis", "inherited from the frozen P4 grading"),
            in_prior_runtime_payload=rec.get("in_prior_runtime_payload", False),
            eligible_for_holdout=rec["exposure_grade"] in ("E0", "E1"),
            development_exposed=rec["exposure_grade"] == "E2",
        ))
    save_jsonl("exposure_ledger.jsonl", exposure)

    build_sources = {records[r]["source"] for r in FORCED_BUILD if r in records}
    build_reactions = set(FORCED_BUILD)
    build_closures = {records[r]["closure_group"] for r in FORCED_BUILD if r in records}
    build_reaction_sigs = {
        records[r].get("canonical_reaction_signature") for r in FORCED_BUILD
        if records.get(r, {}).get("canonical_reaction_signature")
    }

    # ------------------------------------------------------------ closure edges
    edges = []
    by_source = defaultdict(list)
    for rid, rec in complete.items():
        by_source[rec["source"]].append(rid)
    for src, rids in sorted(by_source.items()):
        for other, orids in sorted(by_source.items()):
            if other == src:
                continue
            shared = set(rids) & set(orids)
            if shared:
                edges.append(dict(edge_type="same_covalent_reaction", source=src,
                                  other=other, reactions=sorted(shared),
                                  reason="both sources encode the same complete covalent reaction"))
    for rid in sorted(build_reactions):
        rec = records[rid]
        for src in sorted(by_source):
            if src == rec["source"]:
                continue
            same_rxn = any(records[o].get("canonical_reaction_signature")
                           == rec.get("canonical_reaction_signature")
                           for o in by_source[src]
                           if records[o].get("canonical_reaction_signature"))
            if same_rxn:
                edges.append(dict(edge_type="build_source_contamination", source=src,
                                  other=rec["source"], reactions=[rid],
                                  reason="a non-build source encodes the same complete covalent "
                                         "reaction as a build support"))
    save_jsonl("source_group_edges.jsonl", edges)

    # ------------------------------------------------------------------ panel
    panel, refs, unselected = [], [], []
    for rid, rec in sorted(complete.items()):
        cls = rec["bond_class"]
        if rid in FORCED_BUILD:
            unselected.append(dict(reaction_id=rid, bond_class=cls, selected_part="build",
                                   reason=FORCED_BUILD[rid]))
            continue
        if rec["exposure_grade"] == "E2":
            unselected.append(dict(reaction_id=rid, bond_class=cls, selected_part="build",
                                   reason=f"source {rec['source']} is development-exposed (E2) and "
                                          "is therefore build-only"))
            continue
        if rec["source"] in build_sources:
            unselected.append(dict(reaction_id=rid, bond_class=cls, selected_part="rejected",
                                   reason=f"closure leak: source {rec['source']} also supplies a "
                                          "build support (R2)"))
            continue
        if rec["closure_group"] in build_closures:
            unselected.append(dict(reaction_id=rid, bond_class=cls, selected_part="rejected",
                                   reason=f"closure leak: {rec['closure_group']} supplies a build "
                                          "support (R2)"))
            continue
        rs = rec.get("canonical_reaction_signature")
        if rs and rs in build_reaction_sigs:
            unselected.append(dict(reaction_id=rid, bond_class=cls, selected_part="rejected",
                                   reason="the exact covalent reaction is already a build support (R3)"))
            continue
        contam = [e for e in edges if e["edge_type"] == "build_source_contamination" and rid in e["reactions"]]
        if contam:
            unselected.append(dict(reaction_id=rid, bond_class=cls, selected_part="rejected",
                                   reason="closure leak: the same covalent reaction appears in a "
                                          "non-build source that collides with a build support"))
            continue

        ref = dict(
            reaction_id=rid, bond_class=cls,
            name=rec.get("product_name") or rec.get("description"),
            structure_encoding="complete",
            source_pmcds=[rec["source"]],
            closure_group=rec["closure_group"],
            acceptor_smiles=rec.get("acceptor_smiles"),
            product_smiles=rec.get("product_smiles"),
            donor_name=rec.get("donor_name"),
            site=rec.get("site"),
            identity_basis=rec.get("identity_basis"),
            evidence=rec.get("evidence"),
            evaluator_side_only=True,
            human_reviewed=False, actionable=False, evidence_closed=False,
            prediction_conditions_verified=False,
        )
        refs.append(ref)
        panel.append(dict(reaction_id=rid, bond_class=cls,
                          closure_group=rec["closure_group"], sources=[rec["source"]]))

    save_jsonl("heldout_references.jsonl", refs)
    save_jsonl("panel_manifest.jsonl", panel)
    save_jsonl("unselected_records.jsonl", unselected)

    # deferred / inferred records are recorded but never counted
    deferred = [dict(reaction_id=k, bond_class=v["bond_class"], source=v["source"],
                     status=v["status"], reason=v.get("status_reason"))
                for k, v in sorted(records.items()) if not v["structure_complete"]]
    save_jsonl("deferred_records.jsonl", deferred)

    # ------------------------------------------------------------------ gates
    per_class = defaultdict(lambda: dict(targets=[], groups=set()))
    for p in panel:
        per_class[p["bond_class"]]["targets"].append(p["reaction_id"])
        per_class[p["bond_class"]]["groups"].add(p["closure_group"])

    gates, verdict = {}, {}
    for cls, label in (("C_formation", "C"), ("sugar_sugar_formation", "SS")):
        n = len(per_class[cls]["targets"])
        g = len(per_class[cls]["groups"])
        ok_n, ok_g = n >= MIN_TARGETS, g >= MIN_GROUPS
        gates[cls] = dict(
            targets=n, closure_groups=g,
            require_targets=MIN_TARGETS, require_groups=MIN_GROUPS,
            require_global_window=f"{GLOBAL_MIN}-{GLOBAL_MAX}",
            require_max_per_class=MAX_PER_CLASS,
            deferred_in_denominator=0,
            gate_pass=bool(ok_n and ok_g),
            status="PASS" if ok_n and ok_g else "FAIL",
            shortfall=dict(targets=max(0, MIN_TARGETS - n), closure_groups=max(0, MIN_GROUPS - g)),
        )
        verdict[label] = "eligible_for_A/B_E" if gates[cls]["gate_pass"] else "not_eligible_A_B_E_null"

    total = sum(len(v["targets"]) for v in per_class.values())
    window_ok = GLOBAL_MIN <= total <= GLOBAL_MAX
    per_class_ok = all(len(v["targets"]) <= MAX_PER_CLASS for v in per_class.values())

    manifest = {
        "task": TASK,
        "frozen_before_any_p5_template_or_A_B_E": True,
        "a_b_e_results_existed_at_freeze_time": False,
        "selection_rule": "every structure-complete admitted reaction whose source is leakage-free "
                          "and whose closure group supplies no build support; no post-hoc selection "
                          "against any model output, because no P5 A/B/E number existed yet",
        "isolation_rules": {
            "R1": "a template build support is forced to build and can never be a holdout target",
            "R2": "a holdout target may not share a source or closure group with any build reaction",
            "R3": "a holdout target may not encode the same complete covalent reaction as a build reaction",
            "R4": "the same canonical acceptor across papers, enzymes or assays counts once",
            "R5": "deferred / inferred / name-only records never enter N_family",
        },
        "panel": {k: dict(targets=sorted(v["targets"]), closure_groups=sorted(v["groups"]),
                          targets_count=len(v["targets"]), groups_count=len(v["groups"]))
                  for k, v in per_class.items()},
        "global_targets": total,
        "global_window": f"{GLOBAL_MIN}-{GLOBAL_MAX}",
        "global_window_met": window_ok,
        "per_class_cap_met": per_class_ok,
        "deferred_counted_in_denominator": 0,
        "deferred_excluded_count": len(deferred),
        "gates": gates,
        "verdict": verdict,
        "eligible_classes": sorted(k for k, v in verdict.items() if v == "eligible_for_A/B_E"),
        "ineligible_classes": sorted(k for k, v in verdict.items() if v != "eligible_for_A/B_E"),
        "human_reviewed": False,
    }
    save("panel_manifest.json", manifest)

    # ------------------------------------------------------------ scope record
    scopes = {}
    for label, supports, center in (
        ("C_scope_flavonol_8_C", C_BUILD_SUPPORTS, "flavonol_8_C_glucoside"),
        ("SS_scope_rhamnoside_O2_revalidated", SS_BUILD_SUPPORTS, "rhamnoside_glucoside_O2"),
        ("SS_scope_steroid_1_4_rhamnose_P5", SS_BUILD_SUPPORTS_P5, "steroidal_1_4_rhamnose"),
    ):
        accs = {records[r].get("canonical_acceptor_signature") for r in supports
                if records.get(r, {}).get("canonical_acceptor_signature")}
        accs.discard(None)
        complete_supports = [r for r in supports if r in complete]
        scopes[center] = dict(
            supports=complete_supports,
            support_count=len(complete_supports),
            distinct_canonical_acceptors=len(accs),
            distinct_canonical_acceptor_sha256=sorted(accs),
            require_distinct_acceptors=2,
            gate_pass=bool(len(accs) >= 2 and len(complete_supports) >= 2),
            sources=sorted({records[r]["source"] for r in complete_supports}),
            counting_key="canonical_acceptor_signature",
            counting_rule="one acceptor structure counts once however many papers, enzymes or "
                          "assays report it (R4)",
        )
    save("scopes.json", dict(
        task=TASK,
        scopes=scopes,
        v5_increment_revalidated=["rhamnoside_glucoside_O2"],
        quarantined_inherited=["C_hydroxyflavanone_C3", "rhamnoside_glucoside_O6"],
        note="the C scope is built from E2 sources precisely so that filling the build side does "
             "not cannibalise the leakage-free holdout pool",
    ))

    split = {
        "task": TASK,
        "frozen_at": "G2, before any P5 template construction and before any P5 A/B/E run",
        "build_reactions": sorted(build_reactions),
        "holdout_reactions": sorted(r["reaction_id"] for r in refs),
        "rejected_at_split": sorted(r["reaction_id"] for r in unselected
                                    if r["selected_part"] == "rejected"),
        "deferred_never_counted": sorted(r["reaction_id"] for r in deferred),
        "counts": {
            "structure_complete_total": len(complete),
            "build": len(build_reactions),
            "holdout": len(refs),
            "rejected": sum(1 for r in unselected if r["selected_part"] == "rejected"),
            "deferred": len(deferred),
        },
        "build_source_closure": sorted(build_sources),
        "build_closure_groups": sorted(build_closures),
        "closure_rule": "same DOI/PMC/SI, same original experiment, patent family, identical "
                        "complete covalent reaction, or explicit reuse of an experiment share a "
                        "closure group",
        "exposure_rule": "E2 sources are build-only; E0/E1 may seed holdout",
        "build_support_rule": "any reaction consumed as a template build support is forced to build (R1)",
    }
    save("split_manifest.json", split)

    stop_conditions = []
    for label, cls in (("C", "C_formation"), ("SS", "sugar_sugar_formation")):
        if not gates[cls]["gate_pass"]:
            stop_conditions.append(dict(
                condition=3, axis=label,
                text="C or SS holdout below 6 complete targets after full de-leakage halts the "
                     "corresponding scientific acceptance",
                shortfall=gates[cls]["shortfall"]))
    if not window_ok:
        stop_conditions.append(dict(condition=3, axis="global",
                                    text=f"global holdout must be {GLOBAL_MIN}-{GLOBAL_MAX}",
                                    observed=total))

    event(TASK, "g2_split", holdout=len(refs), build=len(build_reactions),
          C_targets=gates["C_formation"]["targets"],
          SS_targets=gates["sugar_sugar_formation"]["targets"],
          stop_conditions=len(stop_conditions))
    print(json.dumps(dict(
        gates={k: {kk: v[kk] for kk in ("targets", "closure_groups", "status", "shortfall")}
               for k, v in gates.items()},
        global_targets=total, global_window_met=window_ok,
        verdict=verdict, stop_conditions=stop_conditions,
        counts=split["counts"],
        scope_gates={k: v["gate_pass"] for k, v in scopes.items()},
    ), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())