"""TASK-016-P4 G1: deterministic re-admission audit of the 34 P3 new reactions.

Re-judges every P3R-* reaction into exactly one of the four contract levels and
writes the correction into an independent namespace. P3/v1 is read-only.

Admission test (all five must hold for structure_complete_admitted):

  T1 product identity assigned by an authentic standard, a complete NMR
     assignment, or an explicit in-source product statement -- MS / mass shift /
     product-class name alone is not sufficient;
  T2 acceptor identity assigned on the same basis as the product;
  T3 new-bond position and linkage stated in the source, not merely implied by a
     product-class name or by enzyme nomenclature;
  T4 the encoded structure is NOT reverse-inferred from a different downstream
     compound (dehydration, deprotection, oxidation, rearrangement);
  T5 no newly created sp3 stereocentre is left unspecified by the cited evidence.

A failing T1..T5 gives identity_complete_structure_deferred when the single step
and its linkage remain describable, and provisional_inferred when the structure
would additionally require machine inference, a database substitute or a
terminal-product back-inference. rejected is reserved for a non-target step, an
internal contradiction, duplication of an old bank reaction, or evidence vetoed
by stronger evidence.

Structure encoding is deliberately NOT performed here. This stage judges whether
the evidence supports a complete unique structure; the SMILES themselves are
produced and formula-verified in G3/G4.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
P3 = ROOT / "outputs/task016-p3/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

LEVELS = (
    "structure_complete_admitted",
    "identity_complete_structure_deferred",
    "provisional_inferred",
    "rejected",
)

# ---------------------------------------------------------------------------
# Per-reaction adjudication table.
#   level      : one of LEVELS
#   axis       : identity evidence axis actually present in the source
#   basis      : what makes the structure uniquely determined (or why it is not)
#   fails      : which of T1..T5 fail
#   locators   : where in the frozen payload / raw source the basis sits
#   override   : set when this level differs from the P3 recorded status
# ---------------------------------------------------------------------------
A = {
 "P3R-C01": dict(level="identity_complete_structure_deferred",
   axis="authentic standard on the DEHYDRATED products only (vitexin/isovitexin)",
   basis="single step and C3 linkage are quotable; the 2-hydroxyflavanone C-glucoside "
         "intermediate itself is MS-only in PMC9563126 and calculated-m/z-only in PMC6036675, "
         "and PMC7060329 only reports intermediate accumulation next to NMR of the final "
         "products; PMC10465961 compares intermediate 2 with a reference standard but leaves "
         "the C2/C3 configuration unassigned. No unique complete structure.",
   fails=["T4", "T5"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-A-PMC9563126-008",
             "outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-A-PMC6036675-011",
             "outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-H-PMC7060329-002",
             "outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-B-PMC10465961-003"],
   override="downgrade: P3 build used identification='source NMR-assigned 2-hydroxyflavanone "
            "C-glycoside', which transfers dehydrated-product NMR onto the unassigned intermediate"),
 "P3R-C02": dict(level="identity_complete_structure_deferred",
   axis="authentic standard on the DEHYDRATED products only (orientin/isoorientin)",
   basis="same defect as P3R-C01 for the 2-hydroxyflavanone C-glucoside intermediate; "
         "PMC7060329 SI Fig 12c gives only Mw = 465.1 for the intermediate",
   fails=["T4", "T5"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-A-PMC9563126-009",
             "outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-A-PMC6036675-012",
             "outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-H-PMC7060329-003"],
   override="downgrade: same terminal-product evidence transfer as P3R-C01"),
 "P3R-C03": dict(level="structure_complete_admitted",
   axis="commercial authentic standards (Sigma-Aldrich) used for quantification, "
        "explicit in-source product statement",
   basis="apigenin + UDP-glucose -> isovitexin (apigenin 6-C-beta-D-glucopyranoside); both "
         "species are fully specified sp2 flavone structures, C6 position and beta-D anomeric "
         "configuration stated; no intermediate inference",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-A-PMC6036675-013",
             "PMC6036675 body//p[30]"], override=None),
 "P3R-C04": dict(level="structure_complete_admitted",
   axis="commercial authentic standards, explicit in-source product statement",
   basis="luteolin + UDP-glucose -> isoorientin (luteolin 6-C-beta-D-glucopyranoside); same basis as P3R-C03",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-A-PMC6036675-014",
             "PMC6036675 body//p[30]"], override=None),
 "P3R-C05": dict(level="structure_complete_admitted",
   axis="full 1H/13C NMR of the isolated product in the source",
   basis="kaempferol + UDP-glucose -> kaempferol 8-C-beta-D-glucoside; complete 13C list plus "
         "H-6 assignment and absence of H-8 fix the C8 position; no sp3 stereocentre created",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-B-PMC9700910-000",
             "PMC9700910 body//p[21] body//p[22] supp//Fig.S4 supp//Fig.S5"], override=None),
 "P3R-C06": dict(level="structure_complete_admitted",
   axis="full 1H/13C NMR of the isolated product in the source",
   basis="quercetin + UDP-glucose -> quercetin 8-C-beta-D-glucoside; same basis as P3R-C05",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-B-PMC9700910-001",
             "PMC9700910 body//p[23] body//p[24] supp//Fig.S4 supp//Fig.S5"], override=None),
 "P3R-C07": dict(level="identity_complete_structure_deferred",
   axis="LC-MS of product 1a plus a general enzyme/product statement; no authentic standard "
        "or NMR for vitexin in this article",
   basis="apigenin + UDP-glucose -> vitexin is a quotable single step at C8 with beta-D "
         "configuration, but the product assignment rests on MS plus the sentence that the CGT "
         "produces vitexin; weaker than the standard/NMR basis required by T1",
   fails=["T1"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-B-PMC12993211-017",
             "PMC12993211 body//p[4] body//p[26] supp//Fig.S6-caption"], override=None),
 "P3R-C08": dict(level="identity_complete_structure_deferred",
   axis="mass shift (+146) on the intermediate plus reference standards on the dehydrated products",
   basis="the 5-C-rhamnosylation of 2-hydroxynaringenin 3-C-glucoside is quotable, but "
         "intermediate 3 is characterised only by m/z 595 = 2 + 146 and its C2 configuration is "
         "unspecified; violanthin/iso-violanthin standards describe a later dehydration step",
   fails=["T1", "T5"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-B-PMC10465961-002"],
   override=None),
 "P3R-C09": dict(level="structure_complete_admitted",
   axis="1H/13C NMR of the isolated di-C-glucoside in the source",
   basis="phloretin-3'-C-beta-D-glucoside + UDP-glucose -> 3',5'-di-C-beta-D-glucosyl phloretin; "
         "C-3' and C-5' both resolved at 104.5 ppm and C-1 at 105.0 ppm fix the second C-bond; "
         "phloretin is achiral so no stereocentre is left open",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-H-PMC7558026-008",
             "PMC7558026 si//MS_NMR_data(17aa) si//Supplementary_Fig_3 si//Supplementary_Fig_4"],
   override=None),
 "P3R-C10": dict(level="structure_complete_admitted",
   axis="HPLC identity against an NMR-characterised isolated product",
   basis="nothofagin + UDP-galactose -> 3'-C-beta-D-galactosyl-5'-C-beta-D-glucosyl phloretin; "
         "product compared to the isolated NMR-characterised compound, C5' position and both "
         "beta-D anomerics stated; phloretin is achiral",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-H-PMC11975207-018",
             "PMC11975207 body//p[16] body//p[19] si//Figure_S7"], override=None),
 "P3R-C11": dict(level="structure_complete_admitted",
   axis="HPLC identity against an NMR-characterised isolated product",
   basis="nothofagin + UDP-xylose -> 3'-C-beta-D-glucosyl-5'-C-beta-D-xylosyl phloretin; same basis as P3R-C10",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-H-PMC11975207-019",
             "PMC11975207 body//p[16] body//p[20] si//Figure_S12"], override=None),
 "P3R-C12": dict(level="structure_complete_admitted",
   axis="full stereodefined IUPAC names plus 1H NMR and HRMS of 91, 92 and the stannyl donor in the SI",
   basis="8-bromo-5,7,4'-trimethoxyflavone + C2-OH unprotected beta-D-glucosyl stannane -> "
         "flavone 8-C-(3,4,6-tri-O-benzyl-beta-D-glucopyranoside) under Pd/Stille. The regiochemistry "
         "is fixed by the precursor, which is explicitly 8-bromo, so it does not depend on figure "
         "inspection; donor and product carry complete (2S,3S,4R,5R,6R) descriptors and the "
         "tri-O-benzyl protection state is explicit. The paper's own name for the debenzylated "
         "product 93 is internally inconsistent and is NOT used; the audited single step is 91+45n->92.",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-C-PMC13035923-000",
             "PMC13035923 body//p[25] supplementary//f96e0b4dccd0e626ec860cea.txt (S74-S77, compounds 90-93)"],
   override="upgrade: P3 heldout_references recorded structure_encoding=deferred with reason "
            "'regiochemistry relies on figure inspection'; the SI text already carried by P3 gives "
            "the explicit 8-bromo precursor and the stereodefined name of 92, so the stated reason "
            "does not hold. The deferred P3 record itself is left untouched."),

 "P3R-SS01": dict(level="structure_complete_admitted",
   axis="authentic product standard with CAS and formula, plus a mechanism statement naming the 2''-OH",
   basis="naringenin 7-O-glucoside + UDP-rhamnose -> naringenin 7-O-neohesperidoside (naringin, "
         "C27H32O14, CAS 10236-47-2); 1->2 linkage, alpha-L configuration and the parent glucose "
         "all explicit",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-000",
             "PMC13084081 supplement: Supplemental Table 6 body//p[21]"], override=None),
 "P3R-SS02": dict(level="structure_complete_admitted",
   axis="authentic product standard with CAS and formula",
   basis="hesperetin 7-O-glucoside + UDP-rhamnose -> hesperetin 7-O-neohesperidoside "
         "(neohesperidin, C28H34O15, CAS 13241-33-3); same basis as P3R-SS01",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-001",
             "PMC13084081 supplement: Supplemental Table 6 body//p[22]"], override=None),
 "P3R-SS03": dict(level="structure_complete_admitted",
   axis="authentic product standard with CAS and formula",
   basis="naringenin 7-O-glucoside + UDP-rhamnose -> naringenin 7-O-rutinoside (narirutin, "
         "C27H32O14, CAS 14259-46-2); 1->6 linkage and alpha-L explicit. Admission is per "
         "reaction; the distinct-acceptor count is a G2 question and is handled there.",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-004",
             "PMC13084081 supplement: Supplemental Table 6 body//p[24]"], override=None),
 "P3R-SS04": dict(level="structure_complete_admitted",
   axis="authentic product standard with CAS and formula",
   basis="hesperetin 7-O-glucoside + UDP-rhamnose -> hesperetin 7-O-rutinoside (hesperidin, "
         "C28H34O15, CAS 520-26-3); same basis as P3R-SS03",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-005",
             "PMC13084081 supplement: Supplemental Table 6 body//p[24]"], override=None),
 "P3R-SS05": dict(level="structure_complete_admitted",
   axis="authentic product standard with CAS and formula",
   basis="quercetin 3-O-glucoside + UDP-rhamnose -> quercetin 3-O-neohesperidoside "
         "(C27H30O16, CAS 32453-36-4); 2''-rhamnosylation stated",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-009",
             "PMC13084081 supplement: Supplemental Table 6 body//p[21]"], override=None),
 "P3R-SS06": dict(level="structure_complete_admitted",
   axis="authentic product standard with CAS and formula",
   basis="kaempferol 3-O-glucoside + UDP-rhamnose -> kaempferol 3-O-neohesperidoside "
         "(C27H30O15, CAS 142451-65-8); same basis as P3R-SS05",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-010",
             "PMC13084081 supplement: Supplemental Table 6 body//p[21]"], override=None),
 "P3R-SS07": dict(level="structure_complete_admitted",
   axis="authentic standard with CAS plus full 1H NMR with ROE correlation in the second source",
   basis="quercetin 3-O-glucoside + UDP-glucose -> quercetin 3-O-sophoroside (C27H30O17, "
         "CAS 18609-17-1); PMC4282749 gives Glc H-1''/H-1''' and the ROE correlation from the "
         "anomeric proton to H-2''', which establishes beta-(1->2) on the acceptor glucose",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-E-PMC13084081-011",
             "outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-F-PMC4282749-018",
             "PMC4282749 body//p[17]"], override=None),
 "P3R-SS08": dict(level="structure_complete_admitted",
   axis="explicit in-source product statement with fully systematic product name and stated linkage",
   basis="luteolin 7-O-glucoside + UDP-apiose -> luteolin 7-O-beta-D-apiofuranosyl-(1->2)-"
         "beta-D-glucopyranoside; AgApiT invertibility, the beta1-2 linkage and the apiose "
         "pyranoid/ring form are all stated in the source",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-D-PMC10602602-006",
             "PMC10602602 body//p[18] body//p[33]"], override=None),
 "P3R-SS09": dict(level="structure_complete_admitted",
   axis="explicit in-source product statement with fully systematic product name and stated linkage",
   basis="chrysoeriol 7-O-glucoside + UDP-apiose -> chrysoeriol 7-O-beta-D-apiofuranosyl-(1->2)-"
         "beta-D-glucopyranoside; same basis as P3R-SS08",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-D-PMC10602602-007",
             "PMC10602602 body//p[18] body//p[33]"], override=None),
 "P3R-SS10": dict(level="structure_complete_admitted",
   axis="explicit in-source product statement; acceptor and linkage stated, product given as a "
        "fully systematic name",
   basis="quercetin 7-O-glucoside + UDP-apiose -> quercetin 7-O-[beta-D-apiofuranosyl-(1->2)]-"
         "beta-D-glucopyranoside; the 1->2 position and beta-D configuration are stated, so the "
         "unnamed product still has one complete structure",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-D-PMC10602602-005",
             "PMC10602602 body//p[18] body//p[35]"], override=None),
 "P3R-SS12": dict(level="structure_complete_admitted",
   axis="HMBC correlation plus 13C/DEPT assignment of the apiosyl group in the source",
   basis="astragalin + UDP-apiose -> kaempferol 3-O-[beta-D-apiofuranosyl-(1->2)-beta-D-"
         "glucopyranoside]; the H-1'''/C-2'' HMBC correlation fixes the 1->2 attachment point",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-D-PMC13140228-014",
             "PMC13140228 body//p[19] supp//Table S5"], override=None),
 "P3R-SS13": dict(level="structure_complete_admitted",
   axis="1H/13C NMR of the isolated product in the source",
   basis="trilobatin + UDP-xylose -> trilobatin 2''-O-beta-D-xyloside (32b), purified and "
         "identified by NMR; acceptor, position and beta-D configuration all stated",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-D-PMC10589286-031",
             "PMC10589286 supp//Supplementary Note (NMR data of 32b)"], override=None),
 "P3R-SS14": dict(level="structure_complete_admitted",
   axis="1H/13C NMR of the isolated product in the source",
   basis="naringenin 7-O-glucoside + UDP-glucose -> naringenin 7-O-beta-D-glucosyl-(1->2)-"
         "beta-D-glucoside (3c), purified and identified by NMR",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-D-PMC10589286-032",
             "PMC10589286 supp//Supplementary Note (NMR data of 3c)"], override=None),
 "P3R-SS15": dict(level="structure_complete_admitted",
   axis="1H/13C NMR of the isolated triglycoside plus prior-method comparison",
   basis="rutin + UDP-glucose -> quercetin 3-O-beta-D-glucopyranosyl-(1->3)-alpha-L-rhamnopyranosyl-"
         "(1->6)-beta-D-glucopyranoside (Q-g-r-g); the (1->3) branch on the rhamnose unit is "
         "explicit in the systematic product name and confirmed by NMR",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-F-PMC12313340-000",
             "PMC12313340 body//p[11] attachment-text/PMC12313340 (Supplementary Table S4)"],
   override=None),
 "P3R-SS16": dict(level="structure_complete_admitted",
   axis="named authentic standard plus an enzyme name that states the acceptor position",
   basis="cyanidin 3-O-glucoside + UDP-glucose -> cyanidin 3-O-sophoroside via "
         "UDP-glucose:anthocyanidin 3-O-glucoside-2''-O-glucosyltransferase; the 2''-O position "
         "and beta-D configuration are fixed by the enzyme definition and the standard",
   fails=[],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P3CAND-F-PMC6255700-001",
             "PMC6255700 body//p[4] body//p[10]"], override=None),
 "P3R-SS17": dict(level="identity_complete_structure_deferred",
   axis="LC-MS/MS against the linarin standard; no NMR in the article",
   basis="acacetin 7-O-glucoside + UDP-rhamnose -> acacetin 7-O-rutinoside (linarin) at the 6'' "
         "position; the P3 extraction itself recorded identity_complete=false because the alpha-L "
         "anomeric configuration is implied by the product-class name and the UDP-beta-L-rhamnose "
         "donor rather than established",
   fails=["T1", "T3"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#R3-PMC9706480-004",
             "PMC9706480 body//p[20] body//fig[4]"], override=None),
 "P3R-SS18": dict(level="identity_complete_structure_deferred",
   axis="LC-MS/MS against a reference standard; no NMR in the article",
   basis="apigenin 7-O-glucoside + UDP-rhamnose -> apigenin 7-O-rutinoside (isorhoifolin); same "
         "defect as P3R-SS17 (extraction recorded identity_complete=false)",
   fails=["T1", "T3"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#R3-PMC9706480-005",
             "PMC9706480 body//p[20] body//p[51]"], override=None),
 "P3R-SS19": dict(level="identity_complete_structure_deferred",
   axis="LC-MS/MS against a reference standard; no NMR in the article",
   basis="diosmetin 7-O-glucoside + UDP-rhamnose -> diosmetin 7-O-rutinoside (diosmin); same "
         "defect as P3R-SS17",
   fails=["T1", "T3"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#R3-PMC9706480-006",
             "PMC9706480 body//p[20] body//p[51]"], override=None),
 "P3R-SS20": dict(level="identity_complete_structure_deferred",
   axis="UPLC against purchased authentic rutinoside standards; no NMR in the article",
   basis="quercetin 3-O-glucoside + UDP-rhamnose -> quercetin 3-O-rutinoside (rutin); the 6'' "
         "position is stated in the source but the alpha-L anomeric configuration is only implied "
         "by the product-class name and the donor specification",
   fails=["T1", "T3"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#R3-PMC9706480-009",
             "PMC9706480 body//p[23] body//p[41]"], override=None),
 "P3R-SS21": dict(level="identity_complete_structure_deferred",
   axis="UPLC against purchased authentic rutinoside standards; no NMR in the article",
   basis="kaempferol 3-O-glucoside + UDP-rhamnose -> kaempferol 3-O-rutinoside (7a); same defect "
         "as P3R-SS20",
   fails=["T1", "T3"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#R3-PMC9706480-010",
             "PMC9706480 body//p[23] body//p[41]"], override=None),
 "P3R-SS22": dict(level="structure_complete_admitted",
   axis="authentic standard comparison; structure already encoded and frozen by P3",
   basis="astragalin + UDP-glucose -> kaempferol 3-O-gentiobioside via UGT94BY1; 25a identified "
         "against an authentic standard and the beta-(1->6) attachment on the free 6-OH of the "
         "existing 3-O-glucose is stated; P3 already froze a complete parseable reference",
   fails=[],
   locators=["outputs/task016-p4/v1/p3_reaudit.jsonl#P3R-SS22",
             "outputs/task016-p3/v1/heldout_references.jsonl#P3R-SS22",
             "PMC12120870 body//p[11]"], override=None),
 "P3R-SS23": dict(level="identity_complete_structure_deferred",
   axis="retention time plus MS/MS fragmentation against an external authentic standard; no "
        "de-novo NMR",
   basis="mini-MbA + UDP-glucose -> MbA-XR2 (1,2-beta-D-glucosylation on the acylated sugar "
         "moiety); the product is named systematically, but the caffeoyl ester position on the "
         "acceptor sugar is only fixable from a figure/SI check that P3 explicitly declined to "
         "perform and did not perform",
   fails=["T1"],
   locators=["outputs/task016-p3/v1/candidate_reactions.jsonl#P2QB-PMC6899944-003",
             "outputs/task016-p3/v1/heldout_references.jsonl#P3R-SS23"],
   override=None),
}


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def pool_index():
    """Rebuild the P3 candidate-pool index with P3's own uid numbering."""
    idx = {}
    for r in rows(P3 / "candidate_reactions.jsonl"):
        idx[r["candidate_uid"]] = ("group", r)
    for i, r in enumerate(rows(P3 / "inherited_queue_review.jsonl")):
        idx[f"inherited-{i:03d}"] = ("inherited", r)
    r3 = json.loads((ROOT / "temp/p3-extract/r3-review.json").read_text())
    for i, r in enumerate(r3):
        idx[f"R3-{r['pmcid']}-{i:03d}"] = ("round3", r)
    for tag, fn in (("p2qA", "p2q-batchA.json"), ("p2qB", "p2q-batchB.json")):
        for i, r in enumerate(json.loads((ROOT / "temp/p3-extract" / fn).read_text())):
            idx[f"{tag.upper()}-{r['pmcid']}-{i:03d}"] = (tag, r)
    return idx


def main():
    p3_records = {r["reaction_id"]: r for r in rows(P3 / "reaction_records.jsonl")}
    heldout = {r["reaction_id"]: r for r in rows(P3 / "heldout_references.jsonl")}
    idx = pool_index()

    missing = [rid for rid in A if rid not in p3_records]
    unjudged = sorted(set(p3_records) - set(A))
    if missing or unjudged:
        raise SystemExit(f"adjudication table incomplete: unknown={missing} unjudged={unjudged}")

    # ---------------------------------------------------------- per reaction
    reaudit, corrected, crosswalk, checks = [], [], [], []
    for rid in sorted(p3_records):
        rec = p3_records[rid]
        adj = A[rid]
        ctx = rec["reference_context"]
        pmcs = sorted({c["pmcid"] for c in ctx})
        ho = heldout.get(rid)
        p3_encoding = ho["structure_encoding"] if ho else "not_in_holdout_panel"
        p3_claim = "admitted_new_reaction_complete_single_step_identity"
        status = adj["level"]
        countable = status == "structure_complete_admitted"

        reaudit.append(dict(
            reaction_id=rid, bond_class=rec["bond_class"],
            p3_claimed_status=p3_claim,
            p3_holdout_structure_encoding=p3_encoding,
            p4_status=status,
            countable_as_structure_complete=countable,
            failed_tests=adj["fails"],
            identity_evidence_axis=adj["axis"],
            structure_determination_basis=adj["basis"],
            reviewer_type="agent_structural_review",
            human_reviewed=False,
            p3_override=adj["override"],
            decision_sha_source="scripts/task016_p4_audit.py#A",
        ))

        corrected.append(dict(
            reaction_id=rid, bond_class=rec["bond_class"], name=rec["name"],
            admission="new_reaction", p4_status=status,
            countable_as_structure_complete=countable,
            context_count=rec["context_count"], source_pmcds=pmcs,
            source_groups=pmcs,
            supporting_candidate_uids=rec["supporting_candidate_uids"],
            holdout_eligible_p3=rec["holdout_eligible"],
            reference_context=ctx,
            failed_tests=adj["fails"], identity_evidence_axis=adj["axis"],
            structure_determination_basis=adj["basis"],
            p3_override=adj["override"],
            reviewer_type="agent_structural_review", human_reviewed=False,
            actionable=False, evidence_closed=False,
            prediction_conditions_verified=False,
            structure_encoding="pending_G3_encoding" if countable else "not_encoded",
        ))

        crosswalk.append(dict(
            reaction_id=rid, p3_claim=p3_claim,
            p3_holdout_structure_encoding=p3_encoding,
            p4_status=status, supersedes_p3_judgement=bool(adj["override"]),
            note=adj["override"] or "level unchanged; recorded explicitly for auditability",
        ))

        for uid in rec["supporting_candidate_uids"]:
            pool, row = idx[uid]
            checks.append(dict(
                reaction_id=rid, candidate_uid=uid, pool=pool, pmcid=row.get("pmcid"),
                p3_extraction_identity_complete=row.get("identity_complete"),
                p3_extraction_disposition=row.get("disposition"),
                p3_missing_elements=row.get("missing_elements") or [],
                p3_sugar_stereo_evidence=row.get("sugar_stereo_evidence"),
                p4_status=status, p4_failed_tests=adj["fails"],
                p4_reason=adj["basis"][:400],
                evidence_locators=row.get("evidence_locators") or [],
            ))

    # ------------------------------------------------------------- counting
    by_class = defaultdict(Counter)
    for r in reaudit:
        by_class[r["bond_class"]][r["p4_status"]] += 1
    c_cnt = by_class["C_formation"]["structure_complete_admitted"]
    s_cnt = by_class["sugar_sugar_formation"]["structure_complete_admitted"]
    total = c_cnt + s_cnt

    complete = {r["reaction_id"] for r in reaudit if r["countable_as_structure_complete"]}
    # distinct (source, reaction) closure keys for later split work
    closure = defaultdict(set)
    for r in corrected:
        if r["reaction_id"] in complete:
            for pmc in r["source_pmcds"]:
                closure[pmc].add(r["reaction_id"])

    counts = dict(
        p3_claim={"C_formation": 12, "sugar_sugar_formation": 22, "total": 34},
        p4_corrected={
            "C_formation": {k: by_class["C_formation"][k] for k in LEVELS},
            "sugar_sugar_formation": {k: by_class["sugar_sugar_formation"][k] for k in LEVELS},
        },
        p4_structure_complete={"C_formation": c_cnt, "sugar_sugar_formation": s_cnt,
                               "total": total},
        p4_deferred={
            "C_formation": by_class["C_formation"]["identity_complete_structure_deferred"],
            "sugar_sugar_formation":
                by_class["sugar_sugar_formation"]["identity_complete_structure_deferred"],
        },
        p4_provisional_inferred={
            "C_formation": by_class["C_formation"]["provisional_inferred"],
            "sugar_sugar_formation":
                by_class["sugar_sugar_formation"]["provisional_inferred"],
        },
        p4_rejected={"C_formation": by_class["C_formation"]["rejected"],
                     "sugar_sugar_formation": by_class["sugar_sugar_formation"]["rejected"]},
        floor={"C_formation": 8, "sugar_sugar_formation": 8, "total": 16},
        floor_met={"C_formation": c_cnt >= 8, "sugar_sugar_formation": s_cnt >= 8,
                   "total": total >= 16},
        audited_reactions=len(reaudit),
        expected_reactions=34,
        overrides=sorted(r["reaction_id"] for r in reaudit if r["p3_override"]),
    )

    save_jsonl("p3_reaudit.jsonl", reaudit)
    save_jsonl("corrected_reaction_records.jsonl", corrected)
    save_jsonl("identity_checks.jsonl", checks)
    save_jsonl("status_crosswalk.jsonl", crosswalk)
    save("reaudit_counts.json", counts)
    save("structure_complete_closure.json", {
        "task": TASK,
        "note": "build/holdout closure input only; not yet a split decision",
        "source_to_reactions": {k: sorted(v) for k, v in sorted(closure.items())},
        "distinct_sources": len(closure),
    })

    event(TASK, "g1_reaudit", audited=len(reaudit),
          C_complete=c_cnt, SS_complete=s_cnt, total_complete=total,
          overrides=len(counts["overrides"]))
    print(json.dumps(counts, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
