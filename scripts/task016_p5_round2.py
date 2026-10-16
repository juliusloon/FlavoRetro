"""TASK-016-P5 G1b-3: second targeted discovery round for the C shortfall.

Round 1 found 34 full texts, but after evidence grading the C class holds exactly
five leakage-free structure-complete reactions against a >=6 target gate. This
round is therefore C-only and asks a different question from round 1: not "which
papers study C-glycosylation" but "which papers isolate and fully assign a
C-glycoside product of a stated forward step".

Round 1 was dominated by enzyme-mechanism and molecular-dynamics papers whose
products exist only as diagnostic MS/MS fragments. Round 2 therefore queries:

  * other C-linked sugars, not just glucose (arabinose, xylose, rhamnose, galactose),
    because a C-arabinosylation scope is a genuinely different build scope and its
    products are more often isolated;
  * C-glycosides outside the flavonoid skeleton class already in the closure;
  * biosynthesis of named C-glycosides where isolation and NMR are the point of
    the paper, which is how round 1's own false positives are avoided;
  * chemi-enzymatic and total-synthesis routes that do isolate the C-glycoside.

Selection stays title-level and still happens before any A/B/E number exists. The
exposure closure is unchanged, so an exposed-closure hit can only ever support a
build scope, never a holdout target.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import task016_p5_sources as S
from scripts.operate import event

ROUND2_FAMILIES = [
    dict(family="c2-other-c-sugar",
         purpose="C-glycosylation with a sugar other than glucose; a C-arabinosylation or "
                 "C-xylosylation scope is a genuinely distinct build scope and its products "
                 "are more often isolated than C-glucosides",
         queries=[
             "(C-arabinosylation OR \"C-arabinoside\" OR \"C-arabinopyranoside\") AND "
             "(glycosyltransferase OR biosynthesis OR enzymatic) AND OPEN_ACCESS:Y",
             "(C-xylosylation OR \"C-xyloside\" OR \"C-mannosylation\" OR \"C-galactosylation\" "
             "OR \"C-rhamnosylation\") AND (flavonoid OR natural product OR glycoside) AND "
             "OPEN_ACCESS:Y",
         ]),
    dict(family="c2-named-biosynthesis",
         purpose="biosynthesis of a named C-glycoside where isolation and NMR are the "
                 "deliverable, which is the evidence round 1 lacked",
         queries=[
             "TITLE:(\"C-glycoside\") AND (TITLE:(biosynthesis) OR TITLE:(total synthesis) OR "
             "TITLE:(chemoenzymatic) OR TITLE:(chemo-enzymatic)) AND OPEN_ACCESS:Y",
             "(mangiferin OR homomangiferin OR neomangiferin OR \"C-glycosyl xanthone\") AND "
             "(TOTAL:(\"C-glycoside\") OR ABSTRACT:(\"C-glycoside\")) AND "
             "(isolated OR \"structure elucidation\") AND OPEN_ACCESS:Y",
         ]),
    dict(family="c2-non-flavonoid",
         purpose="C-glycosides on acceptors outside the flavonoid closure already held",
         queries=[
             "(chromone OR xanthone OR anthraquinone OR naphthalene OR stilbene OR "
             "\"phenolic glycoside\") AND (\"C-glycoside\" OR \"C-glycosylation\") AND "
             "(NMR OR \"structure elucidation\" OR isolated) AND OPEN_ACCESS:Y",
             "(\"C-glycosylated\" AND (coumarin OR lignan OR alkaloid OR terpenoid)) AND "
             "OPEN_ACCESS:Y",
         ]),
    dict(family="c2-isolation-led",
         purpose="papers whose stated purpose is isolating and assigning C-glycosides, "
                 "which is where complete product structure is most likely to exist",
         queries=[
             "ABSTRACT:(\"C-glycosides\") AND ABSTRACT:(isolated) AND "
             "ABSTRACT:(\"NMR\") AND OPEN_ACCESS:Y",
             "TITLE:(\"C-glycosylated\") AND OPEN_ACCESS:Y",
         ]),
]


def main():
    doc = json.loads((OUT / "query_plan.json").read_text())
    existing = {q["url"] for q in doc["queries"]}
    added = []
    for fam in ROUND2_FAMILIES:
        for q in fam["queries"]:
            url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
                   + S.urlencode({"query": q, "format": "json", "pageSize": 100,
                                  "resultType": "lite"}))
            if url in existing:
                continue
            existing.add(url)
            added.append(dict(family=fam["family"], purpose=fam["purpose"],
                              intent="C_holdout_and_build_side",
                              interface="europepmc-lite", query=q, url=url,
                              role="discovery-json", pagination_cap=1, page_size=100,
                              dedup_key="pmcid",
                              stop_reason="single page of 100 or hitCount<100; "
                                          "interface failure after 2 attempts"))
    doc["queries_round2"] = added
    doc["round2_rationale"] = (
        "Round 1 graded to five leakage-free structure-complete C reactions against a "
        ">=6 gate. Round 2 re-queries for isolated and assigned C-glycoside products "
        "rather than for papers that merely study C-glycosylation, and widens the "
        "transferred sugar beyond glucose. Selection remains title-level and precedes "
        "any A/B/E number.")
    S.save("query_plan.json", doc)
    doc = json.loads((OUT / "query_plan.json").read_text())
    selected = S.discovery()
    print("round2 selected:", len(selected), flush=True)
    articles = []
    with S.ThreadPoolExecutor(max_workers=4) as pool:
        for res in pool.map(S.available_article, selected):
            articles.append(res)
            print("article", res["pmcid"], res["status"], flush=True)
    m = json.loads((OUT / "article_acquisition_manifest.json").read_text())
    have = {a["pmcid"] for a in m["articles"]}
    m["articles"].extend(a for a in articles if a["pmcid"] not in have)
    m["round2"] = dict(executed_at=S.stamp(), queries=len(added),
                       rationale=doc["round2_rationale"])
    S.save("article_acquisition_manifest.json", m)
    S.accounting()
    event(TASK, "g1_round2", queries=len(added), articles=len(articles))
    return 0


if __name__ == "__main__":
    sys.exit(main())