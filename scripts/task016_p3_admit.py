#!/usr/bin/env python3
"""TASK-016-P3 G2: single-step admission, old-bank dedup and source-closure
freeze.  Emits the contract deliverables into outputs/task016-p3/v1/:

  reaction_records.jsonl      admitted new covalent reactions (P3R-*)
  identity_checks.jsonl       one check row per candidate record (all pools)
  old_new_reaction_map.jsonl  every candidate row -> old signature or NEW
  source_group_edges.jsonl    closure edges (same covalent reaction / source)
  exposure_ledger.jsonl       development-exposure basis per source
  split_manifest.json         frozen build/holdout assignment (pre-template)
  unselected_records.jsonl    rows not admitted, with reasons

Read-only on all candidate pools and on every P1/P2 payload."""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "outputs/task016-p3/v1"
P2V2 = ROOT / "outputs/task016-p2/v2"
P1V2 = ROOT / "outputs/task016-p1/v2"


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def starts(value, *prefixes):
    v = str(value or "")
    return any(v.startswith(p) for p in prefixes)


# ---------------------------------------------------------------- reactions
# key -> (class, human name, status, holdout_eligible, old_signature)
R = {}


def R_new(key, cls, name, holdout=False):
    R[key] = dict(reaction_key=key, bond_class=cls, name=name,
                  admission="new_reaction", holdout_eligible=holdout,
                  old_signature=None)


def R_old(key, cls, name, sig):
    R[key] = dict(reaction_key=key, bond_class=cls, name=name,
                  admission="old_reaction_new_context", holdout_eligible=False,
                  old_signature=sig)


OLD_C = {
    "phloretin+Glc": None, "phloretin+Gal": None, "phloretin+Xyl": None,
    "monoCGal+Glc": None, "monoCXyl+Glc": None,
}
OLD_SS = {
    "apiose@apigenin7G": None, "apiose@liquiritin": None,
    "apiose@isoliquiritin": None, "apiose@narirutin": None,
    "apiose@calycosin": None, "apiose@daidzin": None,
    "apiose@trilobatin": None, "apiose@743diOHF": None,
    "Glc@K3Glu_O2": None, "Glc@K3Gal_O2": None,
}

# --- C new reactions
R_new("C01", "C_formation", "2-hydroxynaringenin + UDP-Glc -> 3-C-beta-D-glucosyl-2-hydroxynaringenin (dehydration yields vitexin/isovitexin)")
R_new("C02", "C_formation", "2-hydroxyeriodictyol + UDP-Glc -> 3-C-beta-D-glucosyl-2-hydroxyeriodictyol (dehydration yields orientin/isoorientin)")
R_new("C03", "C_formation", "apigenin + UDP-Glc -> apigenin 6-C-beta-D-glucoside (direct flavone C-glycosylation, in vivo)")
R_new("C04", "C_formation", "luteolin + UDP-Glc -> luteolin 6-C-beta-D-glucoside (direct flavone C-glycosylation, in vivo)")
R_new("C05", "C_formation", "kaempferol + UDP-Glc -> kaempferol 8-C-beta-D-glucoside (TcCGT; P2-withdrawn encoding re-admitted on re-extracted complete evidence)")
R_new("C06", "C_formation", "quercetin + UDP-Glc -> quercetin 8-C-beta-D-glucoside (TcCGT; P2-withdrawn encoding re-admitted on re-extracted complete evidence)")
R_new("C07", "C_formation", "apigenin + UDP-Glc -> apigenin 8-C-beta-D-glucoside (vitexin-type)")
R_new("C08", "C_formation", "2-hydroxynaringenin 3-C-glucoside + UDP-Rha -> 3-C-beta-D-glucosyl-5-C-alpha-L-rhamnosyl-2-hydroxynaringenin")
R_new("C09", "C_formation", "phloretin-3'-C-beta-D-glucoside + UDP-Glc -> 3',5'-di-C-beta-D-diglucosyl phloretin (AbCGT second step)")
R_new("C10", "C_formation", "nothofagin + UDP-Gal -> 3'-C-beta-D-glucosyl-5'-C-beta-D-galactosyl phloretin (FcCGT reverse order)")
R_new("C11", "C_formation", "nothofagin + UDP-Xyl -> 3'-C-beta-D-glucosyl-5'-C-beta-D-xylosyl phloretin (FcCGT reverse order)")
R_new("C12", "C_formation", "8-bromo-5,7,4'-trimethoxyflavone + beta-D-glucosyl stannane -> 8-C-beta-D-glucosyl-5,7,4'-trimethoxyflavone (Pd-catalysed Stille, chemical)", holdout=True)
# --- SS new reactions
R_new("SS01", "sugar_sugar_formation", "naringenin 7-O-glucoside + UDP-Rha -> 2''-O-alpha-L-rhamnosyl (neohesperidoside bond)")
R_new("SS02", "sugar_sugar_formation", "hesperetin 7-O-glucoside + UDP-Rha -> 2''-O-alpha-L-rhamnosyl (neohesperidoside bond)")
R_new("SS03", "sugar_sugar_formation", "naringenin 7-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (rutinoside bond)")
R_new("SS04", "sugar_sugar_formation", "hesperetin 7-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (rutinoside bond)")
R_new("SS05", "sugar_sugar_formation", "quercetin 3-O-glucoside + UDP-Rha -> 2''-O-alpha-L-rhamnosyl")
R_new("SS06", "sugar_sugar_formation", "kaempferol 3-O-glucoside + UDP-Rha -> 2''-O-alpha-L-rhamnosyl")
R_new("SS07", "sugar_sugar_formation", "quercetin 3-O-glucoside + UDP-Glc -> 2''-O-beta-D-glucosyl (sophoroside bond)")
R_new("SS08", "sugar_sugar_formation", "luteolin 7-O-glucoside + UDP-apiose -> 2''-O-beta-D-apiosyl")
R_new("SS09", "sugar_sugar_formation", "chrysoeriol 7-O-glucoside + UDP-apiose -> 2''-O-beta-D-apiosyl")
R_new("SS10", "sugar_sugar_formation", "quercetin 7-O-glucoside + UDP-apiose -> 2''-O-beta-D-apiosyl")
R_new("SS11", "sugar_sugar_formation", "naringenin 7-O-glucoside + UDP-apiose -> 2''-O-beta-D-apiosyl")
R_new("SS12", "sugar_sugar_formation", "astragalin (kaempferol 3-O-glucoside) + UDP-apiose -> 2''-O-beta-D-apiosyl")
R_new("SS13", "sugar_sugar_formation", "trilobatin + UDP-Xyl -> 2''-O-beta-D-xylosyl")
R_new("SS14", "sugar_sugar_formation", "naringenin 7-O-glucoside + UDP-Glc -> 2''-O-beta-D-glucosyl")
R_new("SS15", "sugar_sugar_formation", "rutin + UDP-Glc -> 3'''-O-beta-D-glucosyl on the rhamnose unit")
R_new("SS16", "sugar_sugar_formation", "cyanidin 3-O-glucoside + UDP-Glc -> 2''-O-beta-D-glucosyl")
R_new("SS17", "sugar_sugar_formation", "acacetin 7-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (1,6RhaT)")
R_new("SS18", "sugar_sugar_formation", "apigenin 7-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (1,6RhaT)")
R_new("SS19", "sugar_sugar_formation", "diosmetin 7-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (1,6RhaT)")
R_new("SS20", "sugar_sugar_formation", "quercetin 3-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (1,6RhaT)")
R_new("SS21", "sugar_sugar_formation", "kaempferol 3-O-glucoside + UDP-Rha -> 6''-O-alpha-L-rhamnosyl (1,6RhaT)")
R_new("SS22", "sugar_sugar_formation", "astragalin (kaempferol 3-O-glucoside) + UDP-Glc -> 6''-O-beta-D-glucosyl (gentiobioside bond; UGT94BY1)", holdout=True)
R_new("SS23", "sugar_sugar_formation", "mini-MbA (myricetin acylated 3-O-glucoside) + UDP-Glc -> 1,2-beta-D-glucosyl on the sugar moiety (CcUGT3/UGT703E1)", holdout=True)
# --- old-context reactions (candidate rows matching the pre-P3 bank)
R_old("OLD-C-phlGlc", "C_formation", "phloretin + Glc -> 3'-C-beta-D-glucosyl phloretin (nothofagin bond)", "old")
R_old("OLD-C-phlGal", "C_formation", "phloretin + Gal -> 3'-C-beta-D-galactosyl phloretin", "old")
R_old("OLD-C-phlXyl", "C_formation", "phloretin + Xyl -> 3'-C-beta-D-xylosyl phloretin", "old")
R_old("OLD-C-monoCGal+Glc", "C_formation", "phloretin mono-C-galactoside + Glc -> 3'-C-Gal-5'-C-Glc", "old")
R_old("OLD-C-monoCXyl+Glc", "C_formation", "phloretin mono-C-xyloside + Glc -> 3'-C-Xyl-5'-C-Glc", "old")
R_old("OLD-SS-apiose@apigenin7G", "sugar_sugar_formation", "apigenin 7-O-glucoside + apiose -> 2''-O-beta-D-apiosyl", "old")
R_old("OLD-SS-apiose@liquiritin", "sugar_sugar_formation", "liquiritin + apiose -> 2''-O-beta-D-apiosyl", "old")
R_old("OLD-SS-apiose@isoliquiritin", "sugar_sugar_formation", "isoliquiritin + apiose -> 2''-O-beta-D-apiosyl", "old")
R_old("OLD-SS-apiose@narirutin", "sugar_sugar_formation", "narirutin + apiose -> apiosylated", "old")
R_old("OLD-SS-apiose@calycosin", "sugar_sugar_formation", "calycosin 7-O-glucoside + apiose -> apiosylated", "old")
R_old("OLD-SS-apiose@daidzin", "sugar_sugar_formation", "daidzin + apiose -> apiosylated", "old")
R_old("OLD-SS-apiose@trilobatin", "sugar_sugar_formation", "trilobatin + apiose -> 2''-O-beta-D-apiosyl", "old")
R_old("OLD-SS-apiose@743diOHF", "sugar_sugar_formation", "7,4'-dihydroxyflavone 7-O-glucoside + apiose -> apiosylated", "old")
R_old("OLD-SS-Glc@K3Glu_O2", "sugar_sugar_formation", "kaempferol 3-O-glucoside + Glc -> 2''-O-beta-D-glucosyl (UGT79B31)", "old")
R_old("OLD-SS-Glc@K3Gal_O2", "sugar_sugar_formation", "kaempferol 3-O-galactoside + Glc -> 2''-O-beta-D-glucosyl (UGT79B31)", "old")


def acceptor(r):
    return str(r.get("acceptor_name") or "")


def donor(r):
    return str(r.get("donor_name") or "")


def pos(r):
    p = str((r.get("new_bond") or {}).get("acceptor_position") or "")
    return p


def pos_is(p, which):
    if which == "O2":
        return p.startswith("O2") or "2-position" in p or "2''" in p
    if which == "O3":
        return p.startswith("O3") or "3-position" in p or "3''' " in p
    if which == "O6":
        return p.startswith("O6") or "6-position" in p or "6''" in p
    return False


def donor_is_glc(d):
    return starts(d, "UDP-glucose") or starts(d, "UDP-alpha-D-glucose") or starts(d, "UDP-α-D-glucose")


def match_row(r):
    """Map one candidate record to a reaction key; None if no complete match."""
    a, d, p = acceptor(r), donor(r), pos(r)
    cls = r.get("class")
    if cls == "C_formation":
        if starts(a, "2-hydroxynaringenin 3-C-glucoside"):
            return "C08" if starts(d, "UDP-rhamnose") else None
        if starts(a, "2-hydroxynaringenin") and starts(d, "UDP-glucose"):
            return "C01"
        if starts(a, "2-hydroxyeriodictyol") and starts(d, "UDP-glucose"):
            return "C02"
        if a.startswith("apigenin") and starts(d, "UDP-glucose"):
            return "C03" if p.startswith("C6") else ("C07" if p.startswith("C8") else None)
        if a.startswith("luteolin") and starts(d, "UDP-glucose"):
            return "C04"
        if a == "kaempferol" and starts(d, "UDP-glucose"):
            return "C05"
        if a == "quercetin" and starts(d, "UDP-glucose"):
            return "C06"
        if a.startswith("8-Bromo") or a.startswith("8-((2S"):
            return "C12"
        if starts(a, "phloretin-3'-C-beta-D-glucoside") and donor_is_glc(d):
            return "C09"
        if starts(a, "phloretin-3'-C") or a.startswith("nothofagin"):
            if starts(d, "UDP-galactose") or starts(d, "UDP-alpha-D-galactose"):
                return "C10"
            if starts(d, "UDP-xylose") or starts(d, "UDP-alpha-D-xylose"):
                return "C11"
            return None
        if starts(a, "3'-C-beta-galactosyl phloretin") or starts(a, "3'-C-beta-xylosyl phloretin"):
            return "OLD-C-monoCGal+Glc" if "galactosyl" in a else "OLD-C-monoCXyl+Glc"
        if a.startswith("phloretin"):
            if starts(d, "UDP-galactose") or starts(d, "UDP-alpha-D-galactose"):
                return "OLD-C-phlGal"
            if starts(d, "UDP-xylose") or starts(d, "UDP-alpha-D-xylose"):
                return "OLD-C-phlXyl"
            if donor_is_glc(d) or starts(d, "TDP-alpha-D-glucose"):
                return "OLD-C-phlGlc"
        return None
    if cls == "sugar_sugar_formation":
        a = a.replace("-3-O-", " 3-O-").replace("-7-O-", " 7-O-")
        donor_rha = starts(d, "UDP-rhamnose") or "rhamnose" in d[:24].lower()
        donor_glc = donor_is_glc(d)
        donor_api = starts(d, "UDP-apiose")
        donor_xyl = starts(d, "UDP-xylose") or starts(d, "UDP-beta-D-xylose")
        if donor_rha:
            if pos_is(p, "O2"):
                if a.startswith("naringenin"):
                    return "SS01"
                if a.startswith("hesperetin"):
                    return "SS02"
                if a.startswith("quercetin 3-O"):
                    return "SS05"
                if a.startswith("kaempferol 3-O"):
                    return "SS06"
                return None
            if pos_is(p, "O6"):
                if a.startswith("naringenin"):
                    return "SS03"
                if a.startswith("hesperetin"):
                    return "SS04"
                if a.startswith("acacetin"):
                    return "SS17"
                if a.startswith("apigenin"):
                    return "SS18"
                if a.startswith("diosmetin"):
                    return "SS19"
                if a.startswith("quercetin 3-O"):
                    return "SS20"
                if a.startswith("kaempferol 3-O"):
                    return "SS21"
                return None
            return None
        if donor_api:
            if a.startswith("apigenin"):
                return "OLD-SS-apiose@apigenin7G"
            if a.startswith("luteolin"):
                return "SS08"
            if a.startswith("chrysoeriol"):
                return "SS09"
            if a.startswith("quercetin 7-O"):
                return "SS10"
            if a.startswith("naringenin 7-O-glucoside"):
                return "SS11"
            if a.startswith("astragalin"):
                return "SS12"
            if a.startswith("liquiritin"):
                return "OLD-SS-apiose@liquiritin"
            if a.startswith("isoliquiritin"):
                return "OLD-SS-apiose@isoliquiritin"
            if a.startswith("narirutin"):
                return "OLD-SS-apiose@narirutin"
            if a.startswith("calycosin"):
                return "OLD-SS-apiose@calycosin"
            if a.startswith("daidzin"):
                return "OLD-SS-apiose@daidzin"
            if a.startswith("trilobatin"):
                return "OLD-SS-apiose@trilobatin"
            if a.startswith("7,4'-dihydroxyflavone"):
                return "OLD-SS-apiose@743diOHF"
            return None
        if donor_xyl:
            if a.startswith("trilobatin"):
                return "SS13"
            return None
        if donor_glc:
            if a.startswith("astragalin"):
                if pos_is(p, "O6"):
                    return "SS22"
                if pos_is(p, "O2"):
                    return "OLD-SS-Glc@K3Glu_O2"
                return None
            if a.startswith("kaempferol 3-O-galactoside"):
                return "OLD-SS-Glc@K3Gal_O2"
            if a.startswith("kaempferol 3-O-glucoside"):
                return "OLD-SS-Glc@K3Glu_O2"
            if a.startswith("quercetin 3-O-glucoside"):
                return "SS07" if pos_is(p, "O2") else (None if not pos_is(p, "O6") else "SS20")
            if a.startswith("naringenin 7-O-glucoside"):
                return "SS14"
            if a.startswith("cyanidin"):
                return "SS16"
            if a.startswith("quercetin 3-O-rutinoside"):
                return "SS15"
            if a.startswith("mini-MbA"):
                return "SS23"
            return None
    return None


def main():
    # ------------------------------------------------------------- load pools
    pools = {}
    grp = rows(V1 / "candidate_reactions.jsonl")
    pools["group"] = grp
    pools["inherited"] = rows(V1 / "inherited_queue_review.jsonl")
    r3 = json.loads((ROOT / "temp/p3-extract/r3-review.json").read_text())
    for i, r in enumerate(r3):
        r["candidate_uid"] = f"R3-{r['pmcid']}-{i:03d}"
        r.setdefault("group", "R3")
    pools["round3"] = r3
    for tag, fname in (("p2qA", "p2q-batchA.json"), ("p2qB", "p2q-batchB.json")):
        data = json.loads((ROOT / "temp/p3-extract" / fname).read_text())
        for i, r in enumerate(data):
            r["candidate_uid"] = f"{tag.upper()}-{r['pmcid']}-{i:03d}"
            r.setdefault("group", tag)
        pools[tag] = data

    # P2 9706480 standard-based admission upgrade (see identity_checks rows)
    UPGRADE = {"PMC9706480"}
    old_table = {r["signature"]: r for r in json.load(open("/tmp/old_reactions.json"))}

    reaction_rows = []
    old_matched_rows = []
    identity_checks = []
    old_new_map = []
    unselected = []
    uid_counter = 0
    for pool_name, pool in pools.items():
        for r in pool:
            uid = r.get("candidate_uid") or f"{pool_name}-{uid_counter:03d}"
            uid_counter += 1
            key = match_row(r) if r.get("disposition") == "candidate" else None
            extracted_complete = r.get("identity_complete") is True
            upgraded = False
            if pmc := r.get("pmcid"):
                pass
            if r.get("pmcid") in UPGRADE and r.get("disposition") == "candidate":
                # linkage stated explicitly (C6-position quote); anomeric via
                # named rutinoside reference standards + 1,6RhaT nomenclature
                upgraded = key in {"SS17", "SS18", "SS19", "SS20", "SS21", "SS03", "SS04"}
            admissible = key is not None and (extracted_complete or upgraded)
            if r.get("disposition") != "candidate":
                identity_checks.append(dict(
                    candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                    extraction_disposition="no_candidate",
                    admission_decision="no_candidate",
                    decision_reason="scope exclusion documented at extraction",
                    notes=(r.get("notes") or "")[:400]))
                unselected.append(dict(candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                                       disposition="no_candidate"))
                continue
            if key is None:
                decision = "retained_pending_identity"
                reason = ("no complete single-step identity match; missing: "
                          + "; ".join(r.get("missing_elements") or []) or "position/anomer unresolved")
                identity_checks.append(dict(
                    candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                    extraction_identity_complete=extracted_complete,
                    admission_decision=decision, decision_reason=reason[:400],
                    missing_elements=r.get("missing_elements") or []))
                old_new_map.append(dict(candidate_uid=uid, pmcid=r["pmcid"],
                                        mapping="pending_no_complete_identity",
                                        reaction_key=None))
                unselected.append(dict(candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                                       disposition="retained_pending_identity",
                                       missing_elements=r.get("missing_elements") or []))
                continue
            spec = R[key]
            if not admissible:
                identity_checks.append(dict(
                    candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                    extraction_identity_complete=extracted_complete,
                    admission_decision="retained_pending_identity",
                    decision_reason="reaction identified but identity incomplete for admission",
                    missing_elements=r.get("missing_elements") or []))
                old_new_map.append(dict(candidate_uid=uid, pmcid=r["pmcid"],
                                        mapping="pending_incomplete_identity",
                                        reaction_key=key,
                                        reaction_admission=spec["admission"]))
                unselected.append(dict(candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                                       disposition="retained_pending_identity",
                                       reaction_key=key))
                continue
            identity_checks.append(dict(
                candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                extraction_identity_complete=extracted_complete,
                admission_identity_upgrade=upgraded,
                admission_decision="admitted",
                admission_judgment=("anomeric configuration assigned via named rutinoside reference-standard identity and 1,6RhaT enzyme nomenclature; C6 linkage quoted verbatim" if upgraded else "all four identity elements stated in source"),
                reaction_key=key,
                evidence_locators=r.get("evidence_locators") or [],
                evidence_quote_count=len(r.get("evidence_quotes") or [])))
            old_new_map.append(dict(
                candidate_uid=uid, pmcid=r["pmcid"], mapping="matched",
                reaction_key=key, reaction_admission=spec["admission"],
                old_signature=("pre-P3 bank" if spec["admission"] == "old_reaction_new_context" else None)))
            if spec["admission"] == "old_reaction_new_context":
                old_matched_rows.append((key, r["pmcid"]))
            if spec["admission"] == "new_reaction":
                reaction_rows.append(dict(
                    candidate_uid=uid, pmcid=r["pmcid"], pool=pool_name,
                    reaction_key=key, bond_class=spec["bond_class"],
                    reaction_name=spec["name"], holdout_eligible=spec["holdout_eligible"],
                    context=r.get("context"), enzyme_or_catalyst=r.get("enzyme_or_catalyst"),
                    acceptor_name=r.get("acceptor_name"), donor_name=r.get("donor_name"),
                    new_bond=r.get("new_bond"),
                    conditions_summary=r.get("conditions_summary"),
                    yield_reported=r.get("yield_reported"),
                    evidence_locators=r.get("evidence_locators") or [],
                    evidence_quotes=r.get("evidence_quotes") or [],
                    source_group=r["pmcid"]))

    # ------------------------------------------------------- reaction rollup
    by_key = defaultdict(list)
    for rr in reaction_rows:
        by_key[rr["reaction_key"]].append(rr)
    reaction_records = []
    for key, rows_ in sorted(by_key.items()):
        spec = R[key]
        sources = sorted({x["pmcid"] for x in rows_})
        reaction_records.append(dict(
            reaction_id=f"P3R-{key}",
            bond_class=spec["bond_class"], name=spec["name"],
            admission=spec["admission"],
            context_count=len(rows_),
            source_pmcds=sources,
            source_groups=sources,
            holdout_eligible=spec["holdout_eligible"],
            supporting_candidate_uids=sorted(x["candidate_uid"] for x in rows_),
            reference_context=[dict(pmcid=x["pmcid"], conditions=x["conditions_summary"],
                                    yield_reported=x["yield_reported"],
                                    acceptor=x["acceptor_name"], donor=x["donor_name"],
                                    evidence_locators=x["evidence_locators"]) for x in rows_]))

    # ---------------------------------------------------------- closure graph
    payload_used, ext, unres = set(), set(), set()
    import re
    pmc_re = re.compile(r"PMC\d+")
    for f in (P2V2 / "runtime_instances.jsonl", P1V2 / "runtime_instances.jsonl"):
        for r in rows(f):
            for field in ("actual_assay_group", "source_group", "original_reference"):
                payload_used.update(pmc_re.findall(str(r.get(field, ""))))
    ext = {e["pmcid"] for e in rows(P2V2 / "primary_extension_source_review.jsonl")}
    unres = {u["pmcid"] for u in rows(P2V2 / "unresolved_instances.jsonl")}
    exposed = payload_used | ext | unres

    edges = []
    pmc_by_key = defaultdict(set)
    for key, rows_ in by_key.items():
        pmcs = sorted({x["pmcid"] for x in rows_})
        for pm in pmcs:
            pmc_by_key[key].add(pm)
        spec = R[key]
        if spec["admission"] == "old_reaction_new_context":
            for pm in pmcs:
                edges.append(dict(edge_type="reaction_in_pre_P3_bank", source=pm,
                                  other="pre-P3-bank(58 signatures)",
                                  reaction_key=key, reason="candidate row matches a pre-P3 admitted covalent reaction"))
        if len(pmcs) > 1:
            for i in range(len(pmcs)):
                for j in range(i + 1, len(pmcs)):
                    edges.append(dict(edge_type="same_covalent_reaction", source=pmcs[i],
                                      other=pmcs[j], reaction_key=key,
                                      reason="both sources encode the same complete covalent reaction"))
    # old-context rows connect their sources to the pre-P3 bank closure
    for key, pm in sorted(old_matched_rows):
        edges.append(dict(edge_type="reaction_in_pre_P3_bank", source=pm,
                          other="pre-P3-bank(58 signatures)",
                          reaction_key=key,
                          reason="candidate row matches a pre-P3 admitted covalent reaction (old-context confirmation)"))
    # exposure edges: same payload assay identity reuse
    for pm in sorted(exposed):
        edges.append(dict(edge_type="development_exposed_source", source=pm,
                          other="pre-P3-development", reason="source identity used in P1/P2 payload, identity review or unresolved/withdrawn coding"))

    # union-find
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    nodes = set()
    for e in edges:
        nodes.add(e["source"])
        nodes.add(e["other"])
    if "pre-P3-bank(58 signatures)" in nodes or "pre-P3-development" in nodes:
        anchor = "pre-P3-development"
        nodes.add(anchor)
        for e in edges:
            if e["other"].startswith("pre-P3"):
                union(e["source"], anchor)
            else:
                union(e["source"], e["other"])
    for key, pmcs in pmc_by_key.items():
        pmcs = sorted(pmcs)
        for i in range(1, len(pmcs)):
            union(pmcs[0], pmcs[i])
    components = defaultdict(set)
    for n in list(parent) + sorted({x["pmcid"] for x in reaction_rows}):
        components[find(n)].add(n)
    exposed_roots = {find(p) for p in exposed}
    source_split = {}
    for pm in {x["pmcid"] for x in reaction_rows}:
        source_split[pm] = "build" if find(pm) in exposed_roots else "holdout-eligible"

    split_manifest = dict(
        task="TASK-016-P3", frozen_before_templates=True,
        rule=("closure before templates: sources whose identity was used in P1/P2 "
              "development (payload, identity review, unresolved/withdrawn coding) or "
              "sharing a complete covalent reaction with them are build; remaining "
              "admitted reactions are holdout-eligible"),
        source_split=source_split,
        exposed_source_count=len(exposed),
        exposed_sources=sorted(exposed),
        holdout_reactions=sorted(k for k, v in by_key.items()
                                 if R[k]["holdout_eligible"]
                                 and all(source_split[x["pmcid"]] == "holdout-eligible" for x in by_key[k])),
        holdout_targets_by_class={
            "C_formation": sorted(f"P3R-{k}" for k, v in by_key.items()
                                  if R[k]["bond_class"] == "C_formation"
                                  and R[k]["holdout_eligible"]
                                  and all(source_split[x["pmcid"]] == "holdout-eligible" for x in by_key[k])),
            "sugar_sugar_formation": sorted(f"P3R-{k}" for k, v in by_key.items()
                                            if R[k]["bond_class"] == "sugar_sugar_formation"
                                            and R[k]["holdout_eligible"]
                                            and all(source_split[x["pmcid"]] == "holdout-eligible" for x in by_key[k])),
        },
        gate_status=dict(
            admission_target=">=16 total, C>=8, SS>=8",
            admitted_new_C=len([k for k in by_key if R[k]["bond_class"] == "C_formation" and R[k]["admission"] == "new_reaction"]),
            admitted_new_SS=len([k for k in by_key if R[k]["bond_class"] == "sugar_sugar_formation" and R[k]["admission"] == "new_reaction"]),
            holdout_panel_target=">=6 targets and >=2 closure groups per class",
        ),
    )

    exposure_ledger = []
    for pm in sorted({x["pmcid"] for x in reaction_rows} | exposed):
        reasons = []
        if pm in payload_used:
            reasons.append("P1/P2 payload runtime instance")
        if pm in ext:
            reasons.append("P2 primary/extension source identity review")
        if pm in unres:
            reasons.append("P2 unresolved-instance identity coding")
        exposure_ledger.append(dict(pmcid=pm, development_exposed=bool(reasons),
                                    basis=reasons or ["no pre-P3 identity use; P3 extraction only"],
                                    split=source_split.get(pm, "not-admitted")))

    def dump(name, data, jl=False):
        p = V1 / name
        if jl:
            with p.open("w") as f:
                for x in data:
                    f.write(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n")
        else:
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

    dump("reaction_records.jsonl", reaction_records, True)
    dump("identity_checks.jsonl", identity_checks, True)
    dump("old_new_reaction_map.jsonl", old_new_map, True)
    dump("source_group_edges.jsonl", edges, True)
    dump("exposure_ledger.jsonl", exposure_ledger, True)
    dump("split_manifest.json", split_manifest)
    dump("unselected_records.jsonl", unselected, True)

    new_c = [k for k in by_key if R[k]["bond_class"] == "C_formation" and R[k]["admission"] == "new_reaction"]
    new_ss = [k for k in by_key if R[k]["bond_class"] == "sugar_sugar_formation" and R[k]["admission"] == "new_reaction"]
    old_ctx = [k for k in by_key if R[k]["admission"] == "old_reaction_new_context"]
    print(f"admitted NEW reactions: C={len(new_c)} SS={len(new_ss)} total={len(new_c)+len(new_ss)}")
    print(f"old-reaction context rows (not new): keys={sorted(old_ctx)}")
    print(f"identity checks: {len(identity_checks)}; unselected: {len(unselected)}; edges: {len(edges)}")
    print("holdout C:", split_manifest["holdout_targets_by_class"]["C_formation"])
    print("holdout SS:", split_manifest["holdout_targets_by_class"]["sugar_sugar_formation"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
