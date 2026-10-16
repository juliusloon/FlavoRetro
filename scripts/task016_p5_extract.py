"""TASK-016-P5 G1b: evidence extraction over the acquired P5 full texts.

For every acquired PMC full text this pulls the segments that can carry a
structure-complete forward C-glycosylation or sugar-sugar step, and records what
kind of evidence each segment actually contains. It deliberately stops at
*evidence extraction*: it never asserts structure_complete_admitted, never invents
a SMILES and never chooses holdout targets. Admission is G1c, and the split is G2.

The point of recording an evidence_kind per segment is that P4's C shortfall was
caused by segments that looked like evidence but were not:
  product_identity_only   - the product is named but the step is not a forward
                            acceptor + donor formation step (e.g. a cleavage study)
  mz_only                 - the product is given only as an m/z
  downstream_product      - the intermediate is inferred from a later product
  scope_named_no_isolation - the substrate scope names products without isolation
                            or assignment for this specific step
Only `isolated_assigned` and `standard_assigned` can reach admission.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

# Sources inside the P1-P4 development exposure closure. They can support a build
# scope but can never seed a holdout target.
EXPOSED_CLOSURE = {
    "PMC10589286", "PMC11975207", "PMC7558026", "PMC10602602", "PMC10706860",
    "PMC12313340", "PMC4282749", "PMC6255700", "PMC9700910", "PMC7060329",
    "PMC10465961", "PMC12993211", "PMC6036675", "PMC9563126", "PMC13084081",
    "PMC13324211", "PMC9706480", "PMC10602597", "PMC12120870", "PMC13140228",
    "PMC13035923", "PMC11480083", "PMC8841362", "PMC8196924", "PMC3883091",
    "PMC7326982", "PMC11728773", "PMC10628242", "PMC6749346", "PMC9437722",
    "PMC9786081",
}

# Compound names whose neutral parent structure is already frozen in the P2/P4
# payloads. Re-encoding them creates no new acceptor.
FROZEN_ACCEPTOR_NAMES = {
    "naringenin", "hesperetin", "quercetin", "kaempferol", "luteolin", "apigenin",
    "chrysoeriol", "trilobatin", "rutin", "astragalin", "nothofagin", "phloretin",
    "myricetin",
}

C_TERMS = re.compile(
    r"C-glycosyltransferase|C-glucosyltransferase|C-glycosylation|C-glucosylation|"
    r"C-glycoside|C-glucoside|C-glycosyl|C-arabinosyl|C-mannosyl|C-xylo|"
    r"C-glycosylated", re.I)
SS_TERMS = re.compile(
    r"rhamnosyltransferase|rhamnosylation|xylosyltransferase|xylosylation|"
    r"galactosyltransferase|apiose|arabinosyltransferase|glucuronosyltransferase|"
    r"rutinoside|neohesperidoside|rhamnoside|pentosyltransferase|"
    r"O-glycosylation", re.I)

NMR = re.compile(r"\bNMR\b|nuclear magnetic resonance|1H NMR|13C NMR|HSQC|HMBC|"
                 r"NOESY|cosy|cryoscopy", re.I)
STANDARD = re.compile(r"authentic standard|reference standard|standard (?:of|was|comparison)|"
                      r"compared (?:against|with) (?:the )?(?:authentic )?standard|"
                      r"co-injection|spiked", re.I)
ISOLATION = re.compile(r"isolated|purified|compound \d+\s*\(|yielding|recrystallis|"
                       r"recrystalliz|silica gel|column chromatograph", re.I)
SCOPE = re.compile(r"substrate scope|scope of|acceptor scope|compounds \d+[a-z]?\s*[–-]|"
                   r"Table \d|Table S\d", re.I)
DEGRADATION = re.compile(r"\bcleavage\b|\bdeglycosylat|hydrolysis of|β-elimination|"
                         r"deglycosylation", re.I)
MS_ONLY = re.compile(r"m/z \d|ESI-MS|/m/z", re.I)
DOWNSTREAM = re.compile(r"dehydration|dehydrated|\bvitexin\b|\bisoorientin\b|"
                        r"\bapigenin\b.{0,40}\bdehydrat", re.I)

# Sentences worth keeping as evidence locators, with an evidence_kind so that the
# admission stage can reject the non-structural ones mechanically.
KEEP = re.compile(
    r"C-glycosyl|rhamnosyltransferase|xylosyltransferase|apiose|"
    r"UDP-glucose|UDP-Glc|UDP-rhamnose|UDP-xylose|UDP-galactose|UDP-arabinose|"
    r"substrate scope|was isolated|purified by|authentic standard|"
    r"C-glycoside|C-glucoside|rhamnoside|xyloside|galactoside", re.I)


def text_of(art):
    x = art.get("xml")
    if not x or not (ROOT / x["path"]).is_file():
        return None
    try:
        root = ET.parse(ROOT / x["path"]).getroot()
    except ET.ParseError:
        return None
    # body paragraphs with their structural position preserved
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag in ("p", "title", "caption"):
            s = "".join(el.itertext())
            s = re.sub(r"\s+", " ", s).strip()
            if s:
                out.append((tag, s))
    return out


def segments(art):
    body = text_of(art)
    if body is None:
        return []
    pmc = art["pmcid"]
    segs = []
    full = " ".join(s for _, s in body)
    has_c = bool(C_TERMS.search(full))
    has_ss = bool(SS_TERMS.search(full))
    if not (has_c or has_ss):
        return []
    for tag, s in body:
        if len(s) < 60 or not KEEP.search(s):
            continue
        kinds = []
        if DEGRADATION.search(s) and not C_TERMS.search(s.replace("cleavage", "")):
            kinds.append("product_identity_only")
        if MS_ONLY.search(s) and not NMR.search(s) and not STANDARD.search(s):
            kinds.append("mz_only")
        if DOWNSTREAM.search(s) and not ISOLATION.search(s):
            kinds.append("downstream_product")
        if SCOPE.search(s) and not (NMR.search(s) or ISOLATION.search(s)):
            kinds.append("scope_named_no_isolation")
        if not kinds:
            if STANDARD.search(s):
                kinds.append("standard_assigned")
            elif NMR.search(s) and ISOLATION.search(s):
                kinds.append("isolated_assigned")
            elif NMR.search(s):
                kinds.append("nmr_without_isolation_statement")
            elif ISOLATION.search(s):
                kinds.append("isolated_without_assignment")
            else:
                kinds.append("narrative_only")
        segs.append(dict(
            pmcid=pmc,
            bond_class="C_formation" if C_TERMS.search(s) else "sugar_sugar_formation",
            tag=tag,
            evidence_kind=kinds[0] if len(kinds) == 1 else kinds,
            structural_kinds=sorted(set(kinds)),
            text=s[:1400],
            chars=len(s),
            in_exposure_closure=pmc in EXPOSED_CLOSURE,
        ))
    return segs


def main():
    manifest = json.loads((OUT / "article_acquisition_manifest.json").read_text())
    all_segs, summary = [], []
    for art in manifest["articles"]:
        if art["status"] != "fulltext_available":
            summary.append(dict(pmcid=art["pmcid"], status=art["status"], segments=0))
            continue
        segs = segments(art)
        all_segs.extend(segs)
        kinds = {}
        for s in segs:
            for k in (s["structural_kinds"] if isinstance(s["structural_kinds"], list)
                      else [s["structural_kinds"]]):
                kinds[k] = kinds.get(k, 0) + 1
        summary.append(dict(
            pmcid=art["pmcid"],
            title=art.get("title"),
            license=art.get("license"),
            article_version=art.get("article_version"),
            in_exposure_closure=art["pmcid"] in EXPOSED_CLOSURE,
            segments=len(segs),
            kinds=kinds,
            structural_segments=sum(1 for s in segs
                                    if s["structural_kinds"] in ("isolated_assigned",
                                                                "standard_assigned")),
        ))
    write(TASK, str((OUT / "evidence_segments.jsonl").relative_to(ROOT)),
          "".join(json.dumps(s, ensure_ascii=False, sort_keys=True) + "\n" for s in all_segs))
    write(TASK, str((OUT / "evidence_summary.json").relative_to(ROOT)),
          json.dumps(dict(
              task=TASK,
              rule="evidence_kind is a mechanical classification of what a segment actually "
                   "contains; only isolated_assigned and standard_assigned can reach "
                   "structure_complete_admitted, and no SMILES or admission is decided here",
              admissible_kinds=["isolated_assigned", "standard_assigned"],
              inadmissible_kinds=["product_identity_only", "mz_only", "downstream_product",
                                  "scope_named_no_isolation", "nmr_without_isolation_statement",
                                  "isolated_without_assignment", "narrative_only"],
              articles=summary,
              total_segments=len(all_segs),
          ), ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    event(TASK, "g1_evidence_segments", articles=len(summary), segments=len(all_segs))
    print(json.dumps([{k: s[k] for k in ("pmcid", "in_exposure_closure", "segments",
                                         "structural_segments")}
                      for s in summary if s.get("segments")], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())