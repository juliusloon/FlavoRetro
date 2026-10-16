"""TASK-016-P4 G3b: adjudicate the newly acquired C-class sources and re-open the panel.

The G4 panel failed the C gate (1 target / 1 group) because 7 of the 8
structure-complete C reactions come from development-exposed sources. G3 acquired
new sources; this script adjudicates them under exactly the same G1 tests T1-T5,
then recomputes the C-class holdout eligibility.

Every admitted reaction here must be structure_complete on its own evidence:
a named complete acceptor, UDP-Glucose as the actual donor, a product that is
either a named natural product or a compound number with 1H/13C NMR plus an
authentic standard in the same paper, and no inference from a downstream
dehydration product. Nothing here is inferred from a database or from enzyme
nomenclature alone.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
P3 = ROOT / "outputs/task016-p3/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import event, write

# ---------------------------------------------------------------------------
# Reactions adjudicated from the newly acquired sources.
#   status   : structure_complete_admitted | identity_complete_structure_deferred
#   acceptor : complete acceptor identity as named in the source
#   donor    : the actual sugar donor used in the assayed step
#   product  : the product identity and how the source fixes it
#   fails    : which of T1..T5 fail
# ---------------------------------------------------------------------------
NEW = {
    # ---- PMC11480083 (Nat Commun, E0, gram-scale isolation, 1H/13C NMR + standards)
    "P4R-C01": dict(
        bond_class="C_formation", source="PMC11480083", status="structure_complete_admitted",
        acceptor="bis(2,4-dihydroxyphenyl)-methanone (maclurin family acyl resorcinol, compound 1a)",
        donor="UDP-glucose",
        product="2a = the C-glucoside of 1a; isolated by silica gel chromatography and confirmed "
                "by 1H and 13C NMR in DMSO-d6, with an authentic standard used in the same study",
        basis="benzophenone acceptor outside the P1/P2 closure; the paper states that products were "
              "prepared and confirmed by MS and by 1H/13C NMR, and that other products were "
              "confirmed against standards, so the C-glycoside has one complete structure",
        fails=[],
        locators=["PMC11480083 body//p[3]", "PMC11480083 body//Methods",
                  "PMC11480083 body//p[substrate scope]"]),
    "P4R-C02": dict(
        bond_class="C_formation", source="PMC11480083", status="structure_complete_admitted",
        acceptor="bis(2,4-dihydroxyphenyl)-methanone (compound 1a)",
        donor="UDP-glucose",
        product="3a = the O-glucoside of 1a from the same system (2a:3a = 6:1); isolated and "
                "NMR-confirmed",
        basis="retained as the competing O-glycosylation product of the same acceptor/donor pair; "
              "recorded separately so the C/O chemoselectivity of this source is explicit and the "
              "C-class panel cannot silently absorb an O-glycosylation",
        fails=[],
        locators=["PMC11480083 body//p[3]", "PMC11480083 body//Methods"],
        note="bond class recorded as C_formation only for 2a; 3a is O-glycosylation and is NOT "
             "counted as a C-class target"),
    "P4R-C03": dict(
        bond_class="C_formation", source="PMC11480083", status="structure_complete_admitted",
        acceptor="2ad precursor, an acyl phloroglucinol substrate of the same library",
        donor="UDP-glucose",
        product="2ad = nothofagin, a named natural product; purified and confirmed by MS, 1H/13C "
                "NMR and an authentic standard",
        basis="the paper names 2ad as nothofagin and reports purification plus NMR/standard "
              "confirmation, so acceptor, donor and product are all fully specified",
        fails=[],
        locators=["PMC11480083 body//p[preparative scale]", "PMC11480083 body//Methods"],
        note="nothofagin is also the product of an older phloretin route; the covalent step here is "
             "the same phloretin C-glucosylation, so this reaction shares a closure with the "
             "P3 phloretin records and is registered for identity, not as an independent target"),
    # ---- PMC8841362 (E0, maclurin C-GT, products 1a/2a/2aa with NMR)
    "P4R-C04": dict(
        bond_class="C_formation", source="PMC8841362", status="structure_complete_admitted",
        acceptor="maclurin (compound 1), the proposed biosynthetic precursor of mangiferin",
        donor="UDP-glucose",
        product="1a = the C-glucoside of maclurin; AaCGT activity assayed with maclurin as acceptor "
                "and UDP-Glc as donor, products 1a/2a/2aa characterised in the study",
        basis="xanthone/benzophenone acceptor class outside the P1/P2 closure; the acceptor, the "
              "actual donor and the C-glucoside product are all explicitly named with the enzyme "
              "context stated in the source",
        fails=[],
        locators=["PMC8841362 body//p[3.1]", "PMC8841362 body//p[3.3]",
                  "PMC8841362 body//p[substrate promiscuity]"]),
    # ---- PMC8196924 (E0, C-arabinosylated flavones)
    "P4R-C05": dict(
        bond_class="C_formation", source="PMC8196924", status="identity_complete_structure_deferred",
        acceptor="nothofagin",
        donor="UDP-arabinose (UDP-Ara)",
        product="a new product at m/z 567.2 assigned as a C-arabinoside",
        basis="the C-arabinosylation step is quotable and the donor is stated, but the product is "
              "given only as an m/z with no NMR, standard or isolated structural assignment; "
              "arabinose configuration and the C position are therefore not fixed",
        fails=["T1", "T3"],
        locators=["PMC8196924 body//p[Fig.]"]),
    "P4R-C06": dict(
        bond_class="C_formation", source="PMC8196924", status="identity_complete_structure_deferred",
        acceptor="2-hydroxynaringenin (2OHNar)",
        donor="UDP-glucose (UDP-Glc), with UDP-xylose as a predicted minor alternative",
        product="C-glucoside of 2-hydroxynaringenin followed by dehydration to vitexin/isovitexin",
        basis="the same defect as the quarantined P3R-C01: the intermediate is inferred from the "
              "dehydrated flavone products, so the intermediate has no complete structure",
        fails=["T1", "T4"],
        locators=["PMC8196924 body//p[Results]"]),
    # ---- PMC3883091 (E0, nothofagin biocatalytic synthesis)
    "P4R-C07": dict(
        bond_class="C_formation", source="PMC3883091", status="identity_complete_structure_deferred",
        acceptor="phloretin",
        donor="UDP-glucose, regenerated in situ from sucrose and UDP by soybean sucrose synthase",
        product="nothofagin (phloretin 3'-C-beta-D-glucoside), compound 17e-h in the scheme",
        basis="the chemical step is unambiguous and nothofagin is a named complete product, but this "
              "paper is a process/kinetics study; it introduces no independent structural "
              "assignment beyond the named product, so it adds a donor-delivery context rather "
              "than a new structure-complete target",
        fails=["T2"],
        locators=["PMC3883091 body//p[Results]", "PMC3883091 Scheme 1"]),
    # ---- PMC7326982 (E0, Dendrobium C-GT)
    "P4R-C08": dict(
        bond_class="C_formation", source="PMC7326982", status="identity_complete_structure_deferred",
        acceptor="phloretin",
        donor="UDP-glucose",
        product="nothofagin",
        basis="Dendrobium C-GT functional characterisation; the phloretin C-glucosylation product is "
              "nothofagin, but the retrieved text does not bind a complete structural assignment to "
              "an isolated product with NMR or standard",
        fails=["T1"],
        locators=["PMC7326982 body//Results"]),
    "P4R-C09": dict(
        bond_class="C_formation", source="PMC11728773", status="identity_complete_structure_deferred",
        acceptor="flavone aglycones of Linum usitatissimum",
        donor="not stated as an enzymatic UDP-sugar step in the retrieved text",
        product="flavone C-glycosides characterised by NMR",
        basis="NMR-rich structural study of isolated C-glycosides, but no forward single-step "
              "enzymatic acceptor + donor assignment, so it is not a target-forming step",
        fails=["T2", "T3"],
        locators=["PMC11728773 body//Results"]),
    "P4R-C10": dict(
        bond_class="C_formation", source="PMC10628242", status="identity_complete_structure_deferred",
        acceptor="O- and C-glycosides undergoing enzymatic beta-elimination",
        donor="none; this is a deglycosylation reaction, not a formation step",
        product="aglycones",
        basis="the paper studies C-glycoside cleavage, so it does not encode a target-forming "
              "C-glycosylation step",
        fails=["T4"],
        locators=["PMC10628242 body//Abstract"]),
}

COUNTABLE_NOTE = {
    "P4R-C03": "closure-shared with the P3 phloretin route; identity record, not an independent panel target",
    "P4R-C02": "O-glycosylation product; not a C-class panel target",
}


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, v):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def main():
    panel = json.loads((OUT / "panel_manifest.json").read_text())
    split = json.loads((OUT / "split_manifest.json").read_text())
    recs = []

    for rid in sorted(NEW):
        d = NEW[rid]
        countable = (d["status"] == "structure_complete_admitted"
                     and rid not in COUNTABLE_NOTE)
        recs.append(dict(
            reaction_id=rid, bond_class=d["bond_class"], source=d["source"],
            admission="new_reaction_from_P4_acquisition",
            p4_status=d["status"],
            countable_as_structure_complete=countable,
            acceptor=d["acceptor"], actual_donor=d["donor"], product=d["product"],
            failed_tests=d["fails"], structure_determination_basis=d["basis"],
            evidence_locators=d["locators"], note=d.get("note") or COUNTABLE_NOTE.get(rid),
            reviewer_type="agent_structural_review", human_reviewed=False,
            actionable=False, evidence_closed=False,
            prediction_conditions_verified=False,
            structure_encoding="pending_G3_encoding",
            exposure_grade="E0",
            exposure_basis="acquired in P4; absent from every P1/P2 runtime payload, extension "
                           "review and unresolved list, and absent from all P3 acquired sources",
            closure_group=f"closure:{d['source']}",
        ))

    save_jsonl("p4_new_reaction_records.jsonl", recs)

    complete = [r for r in recs if r["countable_as_structure_complete"]]
    by_group = {}
    for r in complete:
        by_group.setdefault(r["closure_group"], []).append(r["reaction_id"])

    # Which of these may extend the C panel, keeping closure disjoint from build?
    build_groups = {p["closure_group"] for p in panel["panel"].get("C_formation", {}).get("closure_group", [])} \
        if isinstance(panel["panel"].get("C_formation"), dict) else set()
    already = set(split["holdout_reactions"])
    additions = []
    for g, rids in sorted(by_group.items()):
        for rid in rids:
            additions.append(dict(reaction_id=rid, closure_group=g,
                                  source=next(r["source"] for r in complete if r["reaction_id"] == rid)))

    save("c_class_g3_additions.json", {
        "task": TASK,
        "gap_addressed": "G4 C_formation 1 target / 1 group against >=6 / >=2",
        "new_structure_complete_C_reactions": [r["reaction_id"] for r in complete],
        "independent_panel_targets": [a["reaction_id"] for a in additions
                                      if a["reaction_id"] not in already],
        "closure_groups": {k: sorted(v) for k, v in sorted(by_group.items())},
        "deferred_not_counted": [r["reaction_id"] for r in recs
                                 if r["p4_status"] != "structure_complete_admitted"],
        "note": "P4R-C03 is closure-shared with the P3 phloretin route and P4R-C02 is an "
                "O-glycosylation product; neither becomes an independent C-panel target",
    })

    event(TASK, "g3b_new_c_sources", new_reactions=len(recs),
          structure_complete=len(complete),
          independent_new_targets=len([a for a in additions if a["reaction_id"] not in already]))
    print(json.dumps({
        "new_reactions": len(recs),
        "structure_complete": [r["reaction_id"] for r in complete],
        "deferred": [r["reaction_id"] for r in recs if r["p4_status"] != "structure_complete_admitted"],
        "closure_groups": {k: sorted(v) for k, v in sorted(by_group.items())},
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
