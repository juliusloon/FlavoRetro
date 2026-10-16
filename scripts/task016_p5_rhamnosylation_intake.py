"""TASK-016-P5 G1b-4: intake the verified leakage-free 1->3 / 1->6 rhamnosylation sources.

Independent reconnaissance identified a family of rhamnosylation papers that report
isolated products with full NMR assignment and that sit on linkage positions the
P1-P4 closure never covered: 1->3 (quercetin glycoside 3''-O-rhamnoside) and
1->6 on non-flavonoid glycosides. PMC11062225 is the important one, because 1->3
rhamnosylation is absent from every frozen payload.

Downloadability was verified before intake, per source:

  PMC12308137  HTTP 200  CC BY     1->6 on oleanolic acid 3-O-glucoside
  PMC11062225  HTTP 200  CC BY-NC  1->3 and 1->6 on quercetin/isoquercitrin glycosides
  PMC9707320   HTTP 200  CC BY-NC  1->6 on hyperoside

  PMC12769892  HTTP 404  not in the PMC OA subset -> unusable, original cannot be frozen
  PMC8796060   HTTP 404  not in the PMC OA subset -> unusable, original cannot be frozen

The two 404s are recorded as deliberate exclusions rather than omissions: the
contract forbids reaching around a missing original, and a named product in an
unfreezable paper is not evidence P5 may use.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import task016_p5_sources as S
from scripts.operate import event

INTAKE = [
    dict(pmcid="PMC11062225",
         title="rhamnosylation of quercetin glycosides at 3'' and 6''",
         reason="1->3 rhamnosylation, a linkage position absent from every P1-P4 payload; "
                "isolated products with full NMR assignment",
         intent="SS_holdout_and_new_build_scope",
         verified_oa=dict(http_status=200, license="CC BY-NC", version=1,
                          is_retracted=False,
                          checked="pmc-oa-opendata metadata endpoint")),
    dict(pmcid="PMC12308137",
         title="1->6 rhamnosylation of oleanolic acid 3-O-glucoside",
         reason="isolated product with full NMR; a non-flavonoid glycosyl acceptor outside "
                "the whole P1-P4 closure",
         intent="SS_holdout",
         verified_oa=dict(http_status=200, license="CC BY", version=1,
                          is_retracted=False,
                          checked="pmc-oa-opendata metadata endpoint")),
    dict(pmcid="PMC9707320",
         title="1->6 rhamnosylation of hyperoside",
         reason="isolated product with full NMR; hyperoside is a named natural product",
         intent="SS_holdout",
         verified_oa=dict(http_status=200, license="CC BY-NC", version=1,
                          is_retracted=False,
                          checked="pmc-oa-opendata metadata endpoint")),
]

EXCLUDED_NOT_OA = [
    dict(pmcid="PMC12769892", http_status=404,
         reason="not in the PMC OA subset; the original cannot be frozen, so a named "
                "product there is not usable evidence"),
    dict(pmcid="PMC8796060", http_status=404,
         reason="not in the PMC OA subset; the original cannot be frozen"),
]


def main():
    manifest_path = S.OUT / "article_acquisition_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    have = {a["pmcid"] for a in manifest["articles"]}
    added = []
    for rec in INTAKE:
        if rec["pmcid"] in have:
            print("already present", rec["pmcid"], flush=True)
            continue
        entry = dict(pmcid=rec["pmcid"], title=rec["title"],
                     families=["p5_rhamnosylation_followup"],
                     intent=rec["intent"], in_known_exposed_closure=False,
                     selection_is_title_only=False,
                     selection_reason=rec["reason"], verified_oa=rec["verified_oa"])
        res = S.available_article(entry)
        manifest["articles"].append(res)
        added.append((rec["pmcid"], res["status"]))
        print("intake", rec["pmcid"], res["status"], flush=True)
    manifest["rhamnosylation_followup"] = dict(
        note="intake decided after verifying PMC OA downloadability, and still before any "
             "P5 A/B/E number existed",
        sources=INTAKE, excluded_not_in_oa_subset=EXCLUDED_NOT_OA)
    S.save("article_acquisition_manifest.json", manifest)
    S.accounting()
    event(TASK, "g1_rhamnosylation_intake", added=len(added))
    print(json.dumps(dict(added=added,
                          excluded=[e["pmcid"] for e in EXCLUDED_NOT_OA]),
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())