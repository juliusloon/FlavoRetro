#!/usr/bin/env python3
"""TASK-016-P3 G1: build per-article review inputs for the 35 inherited
pending_source_only_title_candidate articles acquired in P3.  Concatenates
body segments (with locators) and parsed SI attachment text into
temp/p3-extract/inh-<PMCID>.txt.  Read-only on outputs; writes working files."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEG = ROOT / "outputs/task016-p3/v1/article_evidence_segments.jsonl"
MAN = ROOT / "outputs/task016-p3/v1/article_acquisition_manifest.json"
ATT = ROOT / "outputs/task016-p3/v1/attachment-text"
OUT = ROOT / "temp/p3-extract"


def main():
    p2 = [
        json.loads(l)
        for l in (ROOT / "outputs/task016-p2/v2/metadata_dispositions.jsonl").open()
        if l.strip()
    ]
    p2_pend = {
        r["pmcid"]: r
        for r in p2
        if r.get("disposition") == "pending_source_only_title_candidate_not_acquired"
    }
    man = json.loads(MAN.read_text())
    inh = {a["pmcid"]: a for a in man if a["pmcid"] in p2_pend}
    missing = sorted(set(p2_pend) - set(inh))
    if missing:
        print("ERROR: inherited PMCIDs absent from P3 manifest:", missing)
        return 2

    segs = {}
    for line in SEG.open():
        if not line.strip():
            continue
        s = json.loads(line)
        segs.setdefault(s["pmcid"], []).append(s)

    def locator_key(loc):
        # body//p[N] sorts before supplementary//... keep document order
        return loc

    built = []
    for pmcid in sorted(inh):
        title = (inh[pmcid].get("title") or "").strip()
        parts = [f"# {pmcid}\n# title: {title}\n"]
        art_segs = sorted(segs.get(pmcid, []), key=lambda s: locator_key(s["locator"]))
        parts.append(f"\n## BODY ({len(art_segs)} segments)\n")
        for s in art_segs:
            parts.append(f"[{s['locator']}] {s['text']}\n")
        att_dir = ATT / pmcid
        if att_dir.exists():
            for f in sorted(att_dir.glob("*.txt")):
                txt = f.read_text(errors="replace")
                parts.append(
                    f"\n## SUPPLEMENTARY TEXT sha256:{f.stem} ({len(txt)} chars)\n"
                )
                parts.append(txt + "\n")
        else:
            parts.append("\n## SUPPLEMENTARY TEXT: none parsed for this article\n")
        out_path = OUT / f"inh-{pmcid}.txt"
        out_path.write_text("".join(parts))
        built.append((pmcid, out_path.stat().st_size, len(art_segs), att_dir.exists()))

    for pmcid, size, nseg, has_att in built:
        print(f"{pmcid}\t{size:>8}B\tbody_segs={nseg}\tSI={'y' if has_att else 'n'}")
    print(f"built {len(built)} review inputs in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
