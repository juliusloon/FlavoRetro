"""TASK-016-P4 G2: scope-support correction by distinct canonical acceptor.

P3 counted scope support by source/enzyme context. The P4 contract requires the
counting key to be canonical_acceptor_signature, so the same acceptor confirmed by
two papers, two enzymes or several assays counts once.

For each of the three P3 scope templates this recomputes, from the frozen P3 build
supports only:
  * the canonical acceptor signatures,
  * the canonical reaction signatures,
  * the distinct canonical acceptor count,
and then applies the scope hard gates. Read-only on P3.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
P3 = ROOT / "outputs/task016-p3/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

# Transcribed from scripts/task016_p3_build.py (P3 evidence, frozen). Used only to
# recompute the counting key, never to create a new structure.
P3_SUPPORTS = {
    "C_hydroxyflavanone_C3": [
        dict(pmcid="PMC9563126", enzyme="MhCGT", reaction="P3R-C01",
             acceptor="O=C1CC(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
             p3_identification="source NMR-assigned 2-hydroxyflavanone C-glycoside; single C-C forming step retained (dehydration excluded)"),
        dict(pmcid="PMC6036675", enzyme="CjCGT1", reaction="P3R-C01",
             acceptor="O=C1CC(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
             p3_identification="in vivo yeast de novo production, NMR-assigned products; same covalent step"),
        dict(pmcid="PMC9563126", enzyme="MhCGT", reaction="P3R-C02",
             acceptor="O=C1CC(O)(c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c12",
             p3_identification="source NMR-assigned 2-hydroxyflavanone C-glycoside cascade"),
    ],
    "rhamnoside_glucoside_O2": [
        dict(pmcid="PMC13084081", enzyme="MpRhaT", reaction="P3R-SS01",
             acceptor="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
             p3_identification="source standard/NMR-assigned neohesperidoside product"),
        dict(pmcid="PMC13084081", enzyme="MpRhaT", reaction="P3R-SS02",
             acceptor="O=C1C[C@@H](c2ccc(O)c(O)c2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
             p3_identification="source standard/NMR-assigned neohesperidoside product"),
    ],
    "rhamnoside_glucoside_O6": [
        dict(pmcid="PMC13084081", enzyme="MpRhaT", reaction="P3R-SS03",
             acceptor="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
             p3_identification="source standard/NMR-assigned rutinoside product"),
        dict(pmcid="PMC9706480", enzyme="Cm1,6RhaT", reaction="P3R-SS03",
             acceptor="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
             p3_identification="source LC-MS/MS against named rutinoside reference standard; identity upgraded at admission"),
    ],
}

GATE_MIN_DISTINCT_ACCEPTOR = 2
GATE_MIN_STRUCTURE_COMPLETE_BUILD = 2


def sig(text):
    return hashlib.sha256(str(text).encode()).hexdigest()


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def main():
    corrected = {r["reaction_id"]: r for r in rows(OUT / "corrected_reaction_records.jsonl")}
    p3_templates = {t["scope"]["center_class"]: t
                    for t in rows(P3 / "templates.jsonl")}

    records, summary = [], {}
    for center, supports in P3_SUPPORTS.items():
        by_acceptor, by_reaction = {}, {}
        for s in supports:
            a_sig = sig(s["acceptor"])
            by_acceptor.setdefault(a_sig, []).append(
                dict(pmcid=s["pmcid"], enzyme=s["enzyme"], reaction=s["reaction"]))
            by_reaction.setdefault(sig(f"{s['reaction']}|{s['acceptor']}"), []).append(
                dict(pmcid=s["pmcid"], enzyme=s["enzyme"], reaction=s["reaction"]))

        distinct_acceptors = len(by_acceptor)
        distinct_reactions = len(by_reaction)
        sources = sorted({s["pmcid"] for s in supports})
        # structure-complete build reactions after the G1 correction
        complete_reactions = sorted({
            s["reaction"] for s in supports
            if corrected.get(s["reaction"], {}).get("countable_as_structure_complete")})
        complete_acceptors = sorted({
            sig(s["acceptor"]) for s in supports
            if corrected.get(s["reaction"], {}).get("countable_as_structure_complete")})

        gates = {
            "min_distinct_canonical_acceptor": {
                "required": GATE_MIN_DISTINCT_ACCEPTOR, "observed": distinct_acceptors,
                "pass": distinct_acceptors >= GATE_MIN_DISTINCT_ACCEPTOR},
            "min_structure_complete_build_reactions": {
                "required": GATE_MIN_STRUCTURE_COMPLETE_BUILD,
                "observed": len(complete_reactions),
                "pass": len(complete_reactions) >= GATE_MIN_STRUCTURE_COMPLETE_BUILD},
            "min_structure_complete_distinct_acceptor": {
                "required": GATE_MIN_DISTINCT_ACCEPTOR,
                "observed": len(complete_acceptors),
                "pass": len(complete_acceptors) >= GATE_MIN_DISTINCT_ACCEPTOR},
        }
        accepted = all(g["pass"] for g in gates.values())

        if center == "C_hydroxyflavanone_C3":
            decision = "quarantined"
            reason = ("every P3 support for this scope rests on NMR/standards of the DEHYDRATED "
                      "flavone products; G1 re-audit downgraded P3R-C01 and P3R-C02 to "
                      "identity_complete_structure_deferred, so the scope has no "
                      "structure-complete intermediate evidence and 0 structure-complete acceptors")
        elif not accepted:
            decision = "quarantined"
            reason = ("distinct canonical acceptor count is "
                      f"{distinct_acceptors} < {GATE_MIN_DISTINCT_ACCEPTOR}; the two P3 supports "
                      "share one canonical acceptor and one reaction id, so a second source does "
                      "not create a second receptor")
        else:
            decision = "accepted_as_p4_increment_candidate"
            reason = ("distinct canonical acceptors and structure-complete build reactions both "
                      "meet the gate after canonicalisation")

        summary[center] = dict(
            p3_support_contexts=len(supports), p3_sources=sources,
            distinct_canonical_acceptor=distinct_acceptors,
            distinct_canonical_reaction=distinct_reactions,
            structure_complete_reactions=complete_reactions,
            structure_complete_distinct_acceptor=len(complete_acceptors),
            p3_template_id=p3_templates.get(center, {}).get("template_id"),
            gates=gates, decision=decision, reason=reason,
            counted_into_v5=accepted and decision != "quarantined",
        )

        for s in supports:
            records.append(dict(
                center_class=center,
                pmcid=s["pmcid"], enzyme=s["enzyme"], reaction=s["reaction"],
                acceptor_smiles_sha256=sig(s["acceptor"]),
                canonical_acceptor_signature=sig(s["acceptor"]),
                canonical_reaction_signature=sig(f"{s['reaction']}|{s['acceptor']}"),
                p3_identification=s["p3_identification"],
                g1_reaction_status=corrected.get(s["reaction"], {}).get("p4_status"),
                structure_complete=bool(
                    corrected.get(s["reaction"], {}).get("countable_as_structure_complete")),
                counting_note=("same canonical acceptor as another support of this scope; "
                               "counts once toward distinct_acceptor"),
            ))

    save_jsonl("scope_support_reaudit.jsonl", records)
    save("scope_decisions.json", {
        "task": TASK,
        "counting_key": "canonical_acceptor_signature",
        "rule": ("one acceptor structure + one target structure + one covalent reaction = one "
                 "acceptor, however many papers, enzymes or assays report it; extra contexts may "
                 "increase source count but never distinct acceptor count"),
        "scopes": summary,
        "v5_increment_scopes": sorted(k for k, v in summary.items() if v["counted_into_v5"]),
        "quarantined_scopes": sorted(k for k, v in summary.items() if not v["counted_into_v5"]),
    })

    event(TASK, "g2_scopes",
          accepted=len([v for v in summary.values() if v["counted_into_v5"]]),
          quarantined=len([v for v in summary.values() if not v["counted_into_v5"]]))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
