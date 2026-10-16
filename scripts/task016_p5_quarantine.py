"""TASK-016-P5 G1b-5: purge the hallucinated rhamnosylation intake.

Independent reconnaissance returned five PMCIDs with confident titles, linkage
positions, NMR evidence and complete SMILES. Three of them were downloaded into
the P5 manifest before their identity was checked against the publisher metadata.

They do not exist as described:

  PMC11062225  agent: "1->3 rhamnosylation of quercetin glycosides, isolated
                          products with full NMR assignment, CC BY-NC"
                actual: "Using virtual reality to manage pain and anxiety during
                         dental treatments in patients with stroke: a case series"
  PMC12308137  agent: "1->6 rhamnosylation of oleanolic acid 3-O-glucoside, CC BY"
                actual: "Resistance training increases myofibrillar protein
                         synthesis in middle-to-older aged adults..."
  PMC9707320   agent: "1->6 rhamnosylation of hyperoside, CC BY-NC"
                actual: "Safety and efficacy of filgotinib, lanraplenib and
                         tirabrutinib in Sjogren's syndrome..."

PMC12769892 and PMC8796060 returned HTTP 404 and so were never downloaded.

The failure was mine as much as the agent's: I treated a subagent's report as
evidence about the outside world when the whole point of the source contract is
that a claim must resolve to a frozen original. Downloading is cheap and proving
absence is not, so a plausible-sounding title reads as confirmation. The project's
own evidence discipline says a file's existence is not content review, and a
subagent's assertion is one step weaker than a file's existence.

This script removes the three fabricated sources from the manifest, records them
as quarantined, and re-asserts the negative result: the 1->3 rhamnosylation
scope that reconnaissance claimed to have found does not exist as described, so
the SS shortfall stands and no 1->3 build scope may enter v6.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

FABRICATED = {
    "PMC11062225": dict(
        claimed_title="1->3 rhamnosylation of quercetin glycosides with isolated "
                      "products and full NMR assignment",
        actual_title="Using virtual reality to manage pain and anxiety during dental "
                     "treatments in patients with stroke: a case series",
        oa_http_status=200, license="CC BY-NC"),
    "PMC12308137": dict(
        claimed_title="1->6 rhamnosylation of oleanolic acid 3-O-beta-D-glucoside "
                      "with full NMR assignment",
        actual_title="Resistance training increases myofibrillar protein synthesis in "
                     "middle-to-older aged adults consuming a typical protein diet",
        oa_http_status=200, license="CC BY"),
    "PMC9707320": dict(
        claimed_title="1->6 rhamnosylation of hyperoside with full NMR assignment",
        actual_title="Safety and efficacy of filgotinib, lanraplenib and tirabrutinib "
                     "in Sjogren's syndrome: a randomized, phase 2, placebo-controlled trial",
        oa_http_status=200, license="CC BY-NC"),
}

NOT_IN_OA = {
    "PMC12769892": "claimed 1->6 rhamnosylation of hesperidin; HTTP 404, never downloaded",
    "PMC8796060": "claimed UDP-glucose/UDP-rhamnose steps on galloyl glycosides; "
                  "HTTP 404, never downloaded",
}


def main():
    manifest_path = OUT / "article_acquisition_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    before = len(manifest["articles"])
    manifest["articles"] = [a for a in manifest["articles"]
                            if a["pmcid"] not in FABRICATED]
    removed = before - len(manifest["articles"])
    manifest.pop("rhamnosylation_followup", None)
    manifest["quarantined_hallucinated_sources"] = dict(
        rule="a source claim must resolve to a frozen original whose publisher metadata "
             "matches the claim. These three were downloaded on a subagent report and "
             "then found to be unrelated papers; they are removed from the intake set and "
             "may not be cited as evidence anywhere in P5.",
        removed_from_manifest=removed,
        fabricated=FABRICATED,
        claimed_but_never_in_oa_subset=NOT_IN_OA,
        consequence="the 1->3 rhamnosylation build scope asserted by reconnaissance does "
                    "not exist as described. SS remains below its 6-target gate and no "
                    "1->3 scope may enter v6.",
        root_cause="a plausible title, position, licence and NMR claim were accepted from a "
                   "subagent report without resolving the PMC ID against publisher metadata. "
                   "HTTP 200 only proves the PMC ID exists, never that it is the paper claimed.",
        detectable_by_a_contract_test=True,
    )
    write(TASK, str((manifest_path.relative_to(ROOT))),
          json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    acct = json.loads((OUT / "source_accounting.json").read_text())
    acct["quarantined_hallucinated"] = dict(
        note="bytes and attempts spent downloading these three are retained in the ledger and "
             "are NOT subtracted. The spend happened and hiding it would make the accounting "
             "unreproducible; what is withdrawn is the evidentiary use, not the cost.",
        pmcids=sorted(FABRICATED),
        attempts_retained=True)
    write(TASK, str((OUT / "source_accounting.json").relative_to(ROOT)),
          json.dumps(acct, ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    event(TASK, "g1_quarantine_hallucinated", removed=removed,
          pmcids=sorted(FABRICATED))
    print(json.dumps(dict(removed_from_manifest=removed,
                          remaining_articles=len(manifest["articles"]),
                          fabricated=sorted(FABRICATED)), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())