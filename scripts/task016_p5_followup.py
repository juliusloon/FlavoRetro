"""TASK-016-P5 G1b-2: acquire a small, explicitly enumerated follow-up source set.

The P5 discovery round returned 34 full texts but the structural evidence in most
of them is MS-level. Two sources identified by independent reconnaissance were
not reached by the title-scoped discovery queries, so they are acquired here by
explicit PMCID rather than by a new search. This is an intake decision, not a
selection decision: it happens before any A/B/E number exists and before any
product structure is judged.

Budget, reuse ledger and namespace are the same P5 counters as the main run, so
this cannot silently overspend: it asserts against the same ceilings.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import task016_p5_sources as S
from scripts.operate import event

TASK = "TASK-016-P5"
FOLLOWUP = [
    dict(pmcid="PMC7720146",
         title="Dissection of the general two-step di-C-glycosylation pathway for the "
               "biosynthesis of (iso)schaftosides in higher plants",
         reason="SbCGTa/b di-C-glycosylation; the paper states that products were purified "
                "in this study and identified by NMR and that others were compared against "
                "reference standards, which is the evidence level P4 found missing for C",
         intent="C_build_side_and_holdout_side"),
    dict(pmcid="PMC8539612",
         title="Enzymatic Synthesis of Novel Vitexin Glucosides",
         reason="BtGT_16345 converts vitexin into vitexin-4'-O-glucoside and "
                "vitexin-5-O-glucoside; a sugar-on-sugar step on a C-glycoside, i.e. a "
                "genuine sugar-sugar formation outside the flavonoid O-glycoside closure",
         intent="C_or_SS_holdout_side"),
    dict(pmcid="PMC11975207",
         title="One-Pot Hetero-Di-C-Glycosylation of the Natural Polyphenol Phloretin",
         reason="re-fetched under the P5 namespace so the P5 ledger records its own SHA; "
                "the source itself is inside the P4 exposure closure",
         intent="exposed_closure_reuse"),
]


def main():
    manifest_path = S.OUT / "article_acquisition_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    have = {a["pmcid"] for a in manifest["articles"]}
    added = []
    for rec in FOLLOWUP:
        if rec["pmcid"] in have:
            print("already present", rec["pmcid"], flush=True)
            continue
        entry = dict(rec)
        entry.update(families=["p5_explicit_followup"], in_known_exposed_closure=None,
                     selection_is_title_only=False,
                     selection_reason="explicit PMCID intake from independent reconnaissance")
        res = S.available_article(entry)
        manifest["articles"].append(res)
        added.append((rec["pmcid"], res["status"]))
        print("followup", rec["pmcid"], res["status"], flush=True)
    manifest["followup_intake"] = dict(
        note="explicit-PMCID intake decided before any A/B/E number existed; "
             "not a post-hoc selection on model output",
        sources=FOLLOWUP)
    S.save("article_acquisition_manifest.json", manifest)
    S.accounting()
    event(TASK, "g1_followup_intake", added=len(added))
    print(json.dumps(dict(added=added), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())