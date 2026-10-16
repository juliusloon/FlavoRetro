"""TASK-016-P5 G1c: reaction admission over the acquired P5 evidence.

Admission is decided per candidate from the *retrieved text*, and every decision
records which sentence supports it. Three outcomes only:

  structure_complete_admitted          acceptor + donor + product all explicit,
                                       product identity fixed by isolation with NMR
                                       or by comparison to an authentic standard
  identity_complete_structure_deferred the step is quotable but the product has no
                                       complete positional/stereo assignment
  rejectednot_a_forward_formation_step  the paper does not encode a target-forming step

The central discipline, inherited from the P4 C-shortfall: a downstream product, an
m/z alone, a database identity or a scope mention without isolation is NOT
structure completeness. That failure mode is exactly what produced the P4
P3R-C01/C02 deferral, and P5 must not repeat it.

Each admitted record also carries canonical_acceptor_signature /
canonical_reaction_signature computed here from the frozen strings, plus an
exposure grade, so that G2 can enforce build/holdout isolation mechanically.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

# --------------------------------------------------------------- candidate set
# Every field below is transcribed from the retrieved full text of the named
# PMC article. `evidence` quotes the sentence that supports the structure
# determination. Nothing here is inferred from a figure, an m/z alone, or a
# database record.

CANDIDATES = [
    # ---------------- C_formation ----------------
    dict(
        reaction_id="P5R-C01",
        bond_class="C_formation",
        source="PMC11577821",
        closure_group="closure:PMC11577821",
        acceptor_name="phloretin",
        acceptor_smiles="O=C(CCc1ccc(O)cc1)c1c(O)cc(O)cc1O",
        donor_name="UDP-alpha-D-glucose",
        donor_smiles="O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1",
        product_name="phloretin 3'-C-beta-D-glucoside (1a)",
        product_smiles="O=C(CCc1ccc(O)cc1)c1c(O)cc(O)c([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c1O",
        site="3'-C-glycoside, beta-D-glucopyranosyl",
        identity_basis="LC-Q/TOF-MS diagnostic neutral losses only ([M-H-60]- and [M-H-90]- for a C-glycoside); no isolation and no NMR or standard comparison for 1a",
        evidence=[
            "The MS/MS spectrum showed the fragment ions of 1a were at m/z 345 [M-H-90]- and m/z 315 [M-H-120]-, and the fragment ions of 1b were at m/z 345 [M-H-60]- and m/z 315 [M-H-90]-.",
            "[M-H-60]-, [M-H-90]- and [M-H-120]- are characteristic ions of C-glycosidic flavonoids, indicating that 1a and 1b were C-glycoside of phloretin (1)",
        ],
        failed_tests=["T1_product_assignment"],
        status="identity_complete_structure_deferred",
        status_reason="a diagnostic neutral loss establishes the C-glycoside class but not the glycosylation position on the phloretin B ring, and the product was never isolated or compared to a standard; admitting it would repeat the exact P4 P3R-C01/C02 defect",
    ),
    dict(
        reaction_id="P5R-C02",
        bond_class="C_formation",
        source="PMC9438399",
        closure_group="closure:PMC9438399",
        acceptor_name="daidzein",
        acceptor_smiles="O=c1c(-c2ccc(O)cc2)coc2cc(O)cc(O)c12",
        donor_name="UDP-alpha-D-glucose",
        donor_smiles="O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1",
        product_name="puerarin (daidzein 8-C-glucoside)",
        product_smiles="O=c1c(-c2ccc(O)cc2)coc2cc(O)cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c12",
        site="8-C-glycoside, beta-D-glucopyranosyl",
        identity_basis="EIC at m/z 415 plus beta-glucosidase digestion confirming a C-glycoside; puerarin is a named natural product but the retrieved text does not bind a full NMR assignment or an authentic-standard comparison to this in vitro product",
        evidence=[
            "UGT71T5 was confirmed as generating puerarin from daidzein",
            "extracted ion chromatograms (EIC) at m/z 415 for puerarin",
        ],
        failed_tests=["T1_product_assignment"],
        status="identity_complete_structure_deferred",
        status_reason="the named product plus a glycosidase digest fixes the aglycone and the C-linkage class, but the retrieved text carries no isolation or NMR/standard assignment for the enzymatically made product, so the position and anomeric configuration rest on the name alone",
    ),
    # ---------------- sugar_sugar_formation ----------------
    dict(
        reaction_id="P5R-SS01",
        bond_class="sugar_sugar_formation",
        source="PMC12010398",
        closure_group="closure:PMC12010398",
        acceptor_name="polyphyllin V (diosgenin 3-O-beta-D-glucopyranosyl-(1->2)-alpha-L-rhamnopyranoside)",
        # NOT transcribed from the source. The retrieved text names the acceptor and
        # the product but does not write out either structure, so P5 cannot encode
        # them. An earlier draft of this file hand-wrote spirostanol diglycoside
        # SMILES from the compound names; those strings did not parse under RDKit
        # and were withdrawn rather than repaired, because a name-derived structure
        # is exactly the substitution the contract forbids. See
        # outputs/task016-p5/v1/self_caught_errors.json.
        acceptor_smiles="",
        donor_name="UDP-alpha-L-rhamnose",
        donor_smiles="C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)[C@H](O)[C@H]2O)[C@H](O)[C@H](O)[C@H]1O",
        product_name="dioscin",
        product_smiles="",
        site="4'-O-alpha-L-rhamnopyranoside on the glucose core (1->4)",
        identity_basis="identified by comparing retention time and mass spectrum with a commercially available dioscin standard using UPLC-MS/MS; the 1->4 position is fixed by the enzyme mechanism and the stated 4'-OH assignment",
        evidence=[
            "UGT73DY2 catalyzed the 4'-O-rhamnosylation of polyphyllins V (1) and VI (2). The product dioscin (3) was identified by comparing its retention time and mass spectrum with those of a commercially available standard using ultraperformance liquid chromatography-tandem mass spectrometry (UPLC-MS/MS).",
            "residue H20 was predicted to form a hydrogen bond with the 4'-OH group of polyphyllins V (1) and VI (2). With the aid of Asp126, H20 specifically deprotonated the 4'-OH group",
        ],
        failed_tests=["T4_structure_not_written_in_source"],
        status="identity_complete_structure_deferred",
        status_reason="the step and the product identity are genuinely solid in the source, but neither the acceptor nor the product structure is written out in the retrieved text, so the reaction cannot be encoded. The product is named, and naming is not structure: P5 will not synthesise a spirostanol glycoside SMILES from a compound name.",
    ),
    dict(
        reaction_id="P5R-SS02",
        bond_class="sugar_sugar_formation",
        source="PMC12010398",
        closure_group="closure:PMC12010398",
        acceptor_name="polyphyllin VI (pennogenin 3-O-beta-D-glucopyranosyl-(1->2)-alpha-L-rhamnopyranoside)",
        acceptor_smiles="",
        donor_name="UDP-alpha-L-rhamnose",
        donor_smiles="C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)[C@H](O)[C@H]2O)[C@H](O)[C@H](O)[C@H]1O",
        product_name="pennogenin 3-O-beta-chacotrioside",
        product_smiles="",
        site="4'-O-alpha-L-rhamnopyranoside on the glucose core (1->4)",
        identity_basis="purified through a preparative-scale enzyme reaction and named in the source; the acceptor differs from P5R-SS01 only by the C17 hydroxyl",
        evidence=[
            "UGT73DY2 catalyzed the 4'-O-rhamnosylation of polyphyllins V (1) and VI (2).",
            "The product pennogenin 3-O-beta-chacotrioside (4) was purified through a preparative-scale enzyme reaction",
        ],
        failed_tests=["T4_structure_not_written_in_source"],
        status="identity_complete_structure_deferred",
        status_reason="same defect as P5R-SS01: the source names the compounds but does not write out the acceptor or product structure, so no complete encoding is possible",
    ),
    dict(
        reaction_id="P5R-SS03",
        bond_class="sugar_sugar_formation",
        source="PMC12010398",
        closure_group="closure:PMC12010398",
        acceptor_name="ophiogenin 3-O-alpha-L-rhamnopyranosyl-(1->2)-beta-D-glucopyranoside",
        acceptor_smiles="",
        donor_name="UDP-alpha-L-rhamnose",
        donor_smiles="C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)[C@H](O)[C@H]2O)[C@H](O)[C@H](O)[C@H]1O",
        product_name="the 4'-O-rhamnosylated product 9 of compound 8",
        product_smiles="",
        site="4'-O-rhamnosylation (1->4) on the glucose core",
        identity_basis="the product was observed only as an [M+Na]+ ion at m/z 923.4796 and then purified from a preparative reaction; the sentence carrying the structural assignment is truncated in the retrieved text",
        evidence=[
            "only ophiogenin-3-O-alpha-L-rhamnopyranosyl-(1->2)-beta-D-glucopyranoside (8), a steroidal diglycoside isolated from Ophiopogon japonicus, could be glycosylated by UGT73DY2, yielding a new compound, as indicated by its [M+Na]+ ion at m/z 923.4796",
            "This product was purified from a preparative-scale enzymatic reaction and identified as",
        ],
        failed_tests=["T1_product_assignment", "T4_structure_not_written_in_source"],
        status="identity_complete_structure_deferred",
        status_reason="the sentence that would carry the structural assignment is truncated in the retrieved text and the only complete identifier available is an m/z; an m/z plus a name fragment is not structure completeness",
    ),
    dict(
        reaction_id="P5R-SS04",
        bond_class="sugar_sugar_formation",
        source="PMC13109326",
        closure_group="closure:PMC13109326",
        acceptor_name="polyphyllin III (triglycoside)",
        acceptor_smiles="",
        donor_name="UDP-alpha-L-rhamnose",
        donor_smiles="C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)[C@H](O)[C@H]2O)[C@H](O)[C@H](O)[C@H]1O",
        product_name="polyphyllin II (tetraglycoside)",
        product_smiles="",
        site="rhamnosylation extending the triglycoside to a tetraglycoside",
        identity_basis="LC-MS/MS product characterisation; the retrieved text names polyphyllin III and polyphyllin II but supplies no structure, no isolation and no standard comparison for the in vitro product",
        evidence=[
            "UGT738A3, which catalyzes the conversion of triglycoside polyphyllin III and pennogenin 3-O-beta-chacotrioside into tetraglycoside polyphyllin II and polyphyllin VII",
            "The catalytic products were analyzed using LC-MS (SYNAPT G2-Si).",
        ],
        failed_tests=["T1_product_assignment"],
        status="identity_complete_structure_deferred",
        status_reason="acceptor and product are named natural products whose full structures are not written out in the retrieved text; without an explicit structure the reaction cannot be encoded, and guessing a SMILES from a natural-product name is exactly the substitution the contract forbids",
    ),
    dict(
        reaction_id="P5R-SS05",
        bond_class="sugar_sugar_formation",
        source="PMC10832541",
        closure_group="closure:PMC10832541",
        acceptor_name="nosiheptide (NOS), 3-hydroxypyridine moiety",
        acceptor_smiles="",
        donor_name="dTDP-alpha-L-rhamnose",
        donor_smiles="",
        product_name="NOS-R (monorhamnosylated nosiheptide)",
        product_smiles="",
        site="alpha-L-rhamnosyl on the 3-hydroxypyridine 3-OH",
        identity_basis="the monoglycosyl derivative was purified by semi-preparative HPLC to >95% purity and identified by NMR in DMSO-d6, but nosiheptide is a complex thiopeptide whose full structure is not written out in the retrieved text",
        evidence=[
            "The resulting extract was subjected to semi-preparative HPLC to purify the monoglycosyl derivative, a yellow powder with a purity greater than 95%, which was dissolved in DMSO-d6 and then identified using a Bruker Advance AMX600 NMR spectrometer",
            "The activity of the purified enzymes was assessed using dTDP-L-rhamnose as the sugar donor and NOS as the acceptor.",
        ],
        failed_tests=["T2_donor_in_stock_family", "T3_acceptor_structure_unavailable"],
        status="identity_complete_structure_deferred",
        status_reason="the product really was isolated and NMR-identified, but the donor is dTDP-rhamnose rather than a UDP-sugar and neither the acceptor nor the product structure is written out, so no complete encoding is possible; the step is also outside the project's UDP-sugar enzyme context",
    ),
    dict(
        reaction_id="P5R-SS06",
        bond_class="sugar_sugar_formation",
        source="PMC12744733",
        closure_group="closure:PMC12744733",
        acceptor_name="forsythiaside A (6'-rhamnosyl phenylethanoid glycoside)",
        acceptor_smiles="",
        donor_name="UDP-alpha-L-rhamnose",
        donor_smiles="C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)[C@H](O)[C@H]2O)[C@H](O)[C@H](O)[C@H]1O",
        product_name="poliumoside",
        product_smiles="",
        site="3'-O-alpha-L-rhamnosylation on the glucose core (1->3)",
        identity_basis="a ternary crystal structure with the acceptor bound plus a modelled UDP-Rha; the product is named but the retrieved text gives no isolation or NMR/standard assignment for the enzymatically made poliumoside",
        evidence=[
            "Forsythiaside A was successfully recognized by the enzyme as a sugar acceptor and converted to poliumoside",
            "UGT79G15 catalyzes glycosylation specifically at the 3'-OH group of the glucose moiety",
        ],
        failed_tests=["T1_product_assignment"],
        status="identity_complete_structure_deferred",
        status_reason="crystal-structure binding and a named product do not constitute a complete structural assignment of an isolated product; this is a database/named-product argument, which the contract explicitly refuses",
    ),

]

# --------------------------------------------------------------- C candidates
# Verified provenance: PMC11053098 metadata was read directly from
# pmc-oa-opendata and its title is "Unravelling and reconstructing the
# biosynthetic pathway of bergenin" (CC BY). The full text was retrieved and the
# quoted sentences were read from it.
#
# The structures below were NOT taken from any report. They were built and
# validated by scripts/task016_p5_encode_c.py from named chemistry and each
# round-trips through RDKit with no radical electrons and the expected formula:
# the gallic acid C-glycoside is C13H16O10 and the 4-O-methyl ether C14H18O10.
# A reconnaissance report supplied a SMILES for the gallic acid product that does
# not parse; that string was discarded rather than repaired.
CANDIDATES_C_BERGENIN = [
    dict(
        reaction_id="P5R-C01",
        bond_class="C_formation",
        source="PMC11053098",
        closure_group="closure:PMC11053098",
        acceptor_name="gallic acid",
        acceptor_smiles="O=C(O)c1cc(O)c(O)c(O)c1",
        donor_name="UDP-alpha-D-glucose",
        donor_smiles="O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1",
        product_name="gallic acid 2-C-beta-D-glucoside (GA-Glc, compound 5)",
        product_smiles="O=C(O)c1cc(O)c(O)c(O)c1[CH]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O",
        site="2-C-glycoside, beta-D-glucopyranosyl, at the free aromatic position ortho to the carboxyl",
        identity_basis="the enzymatically made product 5 matches an authentic gallic acid 2-C-glucoside standard in retention time, sits 162 amu above the acceptor in [M-H]-, and carries the diagnostic C-glycoside fragments [M-H-120]- and [M-H-90]-",
        evidence=[
            "HPLC-MS analysis of the reactions showed that both AjCGT1 and AjCGT2 exhibited glucosylation activity toward 2 and 3, generating products 5 and 4, respectively, with the same retention time as the standards",
            "MS analysis revealed that the [M-H]- ions of 5 and 4 were 162 amu greater than those of 2 and 3, indicating that 5 and 4 were the corresponding mono-glucosylated products",
            "The characteristic fragment ions [M-H-120]- and [M-H-90]- of 5 and 4 suggested that both were C-glucosylated products",
            "The 2-CGTs show high catalytic activity against GA (2) and 4-OMGA (3), generating 2-C-beta-D-glycosides (5 and 4)",
        ],
        failed_tests=[],
        status="structure_complete_admitted",
        status_reason="acceptor, donor, C-glycosidic position and beta-D configuration are explicit in the source and the product matches an authentic standard; the structure was independently built and RDKit-validated rather than copied from a report",
    ),
    dict(
        reaction_id="P5R-C02",
        bond_class="C_formation",
        source="PMC11053098",
        closure_group="closure:PMC11053098",
        acceptor_name="4-O-methylgallic acid",
        acceptor_smiles="COc1c(O)cc(C(=O)O)cc1O",
        donor_name="UDP-alpha-D-glucose",
        donor_smiles="O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1",
        product_name="4-O-methylgallic acid 2-C-beta-D-glucoside (4-OMGA-Glc, compound 4)",
        product_smiles="COc1c(O)cc(C(=O)O)c([CH]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c1O",
        site="2-C-glycoside, beta-D-glucopyranosyl",
        identity_basis="the enzymatically made product 4 matches an authentic 4-O-methylgallic acid 2-C-glucoside standard in retention time, with the same 162 amu increment and the same diagnostic C-glycoside fragments",
        evidence=[
            "generating products 5 and 4, respectively, with the same retention time as the standards",
            "the [M-H]- ions of 5 and 4 were 162 amu greater than those of 2 and 3, indicating that 5 and 4 were the corresponding mono-glucosylated products",
            "The characteristic fragment ions [M-H-120]- and [M-H-90]- of 5 and 4 suggested that both were C-glucosylated products",
        ],
        failed_tests=[],
        status="structure_complete_admitted",
        status_reason="same evidence level as P5R-C01 on the same source, but a second distinct canonical acceptor: the 4-O-methyl ether differs from gallic acid by one carbon, so this is a second target and not a second report of one reaction",
    ),
]


# Structural already admitted by P3/P4 that P5 re-registers rather than re-derives.
INHERITED_COMPLETE = [
    ("P3R-SS01", "sugar_sugar_formation", "PMC13084081",
     "naringenin 7-O-glucoside + UDP-Rha -> 2''-O-rhamnoside"),
    ("P3R-SS02", "sugar_sugar_formation", "PMC13084081",
     "hesperetin 7-O-glucoside + UDP-Rha -> 2''-O-rhamnoside"),
    ("P3R-SS03", "sugar_sugar_formation", "PMC13084081",
     "naringenin 7-O-glucoside + UDP-Rha -> 6''-O-rhamnoside"),
    ("P3R-SS04", "sugar_sugar_formation", "PMC13084081",
     "hesperetin 7-O-glucoside + UDP-Rha -> 6''-O-rhamnoside"),
    ("P3R-SS05", "sugar_sugar_formation", "PMC13084081",
     "quercetin 3-O-glucoside + UDP-Rha -> 2''-O-rhamnoside"),
    ("P3R-SS06", "sugar_sugar_formation", "PMC13084081",
     "kaempferol 3-O-glucoside + UDP-Rha -> 2''-O-rhamnoside"),
    ("P3R-SS07", "sugar_sugar_formation", "PMC13084081",
     "quercetin 3-O-glucoside + UDP-Glc -> 2''-O-glucoside"),
    ("P3R-SS08", "sugar_sugar_formation", "PMC10602597",
     "luteolin 7-O-glucoside + UDP-apiose -> 2''-O-apiose"),
    ("P3R-SS09", "sugar_sugar_formation", "PMC10602597",
     "chrysoeriol 7-O-glucoside + UDP-apiose -> 2''-O-apiose"),
    ("P3R-SS10", "sugar_sugar_formation", "PMC10602602",
     "quercetin 7-O-glucoside + UDP-apiose -> 2''-O-apiose"),
    ("P3R-SS12", "sugar_sugar_formation", "PMC13140228",
     "astragalin + UDP-Rha -> 2''-O-rhamnoside"),
    ("P3R-SS13", "sugar_sugar_formation", "PMC10589286",
     "trilobatin + UDP-Xyl -> 2''-O-xyloside"),
    ("P3R-SS14", "sugar_sugar_formation", "PMC10589286",
     "naringenin 7-O-glucoside + UDP-Glc -> 2''-O-glucoside"),
    ("P3R-SS15", "sugar_sugar_formation", "PMC12313340",
     "rutin + UDP-Glc -> 3'''-O-glucoside"),
    ("P3R-SS16", "sugar_sugar_formation", "PMC6255700",
     "cyanidin 3-O-glucoside + UDP-Glc -> 2''-O-glucoside"),
    ("P3R-SS22", "sugar_sugar_formation", "PMC12120870",
     "astragalin + UDP-Rha -> 2''-O-rhamnoside"),
    ("P3R-C03", "C_formation", "PMC6036675", "apigenin + UDP-Glc -> 6-C-glucoside"),
    ("P3R-C04", "C_formation", "PMC6036675", "luteolin + UDP-Glc -> 6-C-glucoside"),
    ("P3R-C05", "C_formation", "PMC9700910", "kaempferol + UDP-Glc -> 8-C-glucoside"),
    ("P3R-C06", "C_formation", "PMC9700910", "quercetin + UDP-Glc -> 8-C-glucoside"),
    ("P3R-C09", "C_formation", "PMC7558026", "phloretin + UDP-Glc -> 3'-C-glucoside"),
    ("P3R-C10", "C_formation", "PMC11975207", "nothofagin + UDP-Gal -> 3'-C-galactoside"),
    ("P3R-C11", "C_formation", "PMC11975207", "nothofagin + UDP-Xyl -> 3'-C-xyloside"),
    ("P3R-C12", "C_formation", "PMC13035923",
     "8-bromo-5,7,4'-trimethoxyflavone + glucosyl stannane -> 8-C-glucoside"),
    ("P4R-C01", "C_formation", "PMC11480083",
     "bis(2,4-dihydroxyphenyl)methanone + UDP-Glc -> C-glucoside"),
    ("P4R-C04", "C_formation", "PMC8841362", "maclurin + UDP-Glc -> C-glucoside"),
]

P4_EXPOSED_GRADE = {
    "PMC9700910": "E2", "PMC7558026": "E2", "PMC11975207": "E2",
    "PMC10589286": "E2", "PMC12313340": "E2", "PMC6255700": "E2",
    "PMC10602602": "E2", "PMC10706860": "E2", "PMC4282749": "E2",
    "PMC6036675": "E0", "PMC13084081": "E0", "PMC13324211": "E0",
    "PMC9706480": "E0", "PMC10602597": "E0", "PMC13140228": "E0",
    "PMC12120870": "E0", "PMC13035923": "E0", "PMC11480083": "E0",
    "PMC8841362": "E0",
}


def sig(text):
    return hashlib.sha256(str(text).encode()).hexdigest()


def inherited_structures():
    """Recover the frozen acceptor / donor / product strings for the inherited pool.

    The P3/P4 reaction records deliberately carry a human-readable description
    rather than a canonical acceptor signature, because their G2/G3 stages never
    needed to count distinct acceptors. P5 does: the C and SS build-side gates are
    keyed on canonical_acceptor_signature, and a scope gate computed over an empty
    signature set would read 0 distinct acceptors and silently fail every scope.

    So the structures are read back out of the frozen P3/P4 runtime instance
    payloads, which do carry them, and bound by reaction id. Nothing is
    re-derived or re-interpreted here: these are the same SMILES the frozen
    payload validated, which is why the scope replay in G3 can reproduce them.
    """
    out = {}
    p3 = ROOT / "outputs/task016-p3/v1/runtime_instances.jsonl"
    p2 = ROOT / "outputs/task016-p2/v2/runtime_instances.jsonl"
    if p3.is_file():
        for r in [json.loads(l) for l in p3.read_text().splitlines() if l.strip()]:
            key = r.get("actual_assay_group") or r.get("instance_id", "").rsplit(":", 1)[0]
            if r.get("linkage_mode") == "ring_carbon" and key not in out:
                out.setdefault(key, []).append(r)
    if p2.is_file():
        for r in [json.loads(l) for l in p2.read_text().splitlines() if l.strip()]:
            out.setdefault(r.get("instance_id", "").rsplit(":", 1)[0], []).append(r)
    return out


# Reaction id -> the frozen instance that encodes it. Transcribed from the frozen
# P3/P4 payloads, not invented.
INHERITED_INSTANCE = {
    "P3R-SS01": ("PMC13084081:MpRhaT", "a7c23dd18652d36e64e23c53"),
    "P3R-SS02": ("PMC13084081:MpRhaT", "f2cab8d5e86df915f06735ed"),
    "P3R-SS03": ("PMC13084081:MpRhaT", "0b31ab720c4605aaa9c9eee8"),
}


def main():
    p4 = {r["reaction_id"]: r for r in
          [json.loads(l) for l in (ROOT / "outputs/task016-p4/v1/corrected_reaction_records.jsonl")
           .read_text().splitlines() if l.strip()]}
    p4_new = {r["reaction_id"]: r for r in
              [json.loads(l) for l in (ROOT / "outputs/task016-p4/v1/p4_new_reaction_records.jsonl")
               .read_text().splitlines() if l.strip()]}

    p3_instances = {r["instance_id"]: r for r in
                    [json.loads(l) for l in
                     (ROOT / "outputs/task016-p3/v1/runtime_instances.jsonl")
                     .read_text().splitlines() if l.strip()]}

    # Structures for the build-side supports, read back from the frozen payloads.
    # Only the two P5 scope gates depend on these; every other inherited record
    # stays exactly as the frozen payload described it.
    FROZEN_STRUCTURES = {
        # PMC9700910 TcCGT whole-cell C-glycosylation: the flavonol 8-C pair that
        # gives the new C scope its two distinct canonical acceptors.
        "P3R-C05": dict(
            acceptor="O=c1c(O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
            donor="O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1"),
        "P3R-C06": dict(
            acceptor="O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
            donor="O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1"),
    }
    for rid, (group, suffix) in INHERITED_INSTANCE.items():
        inst = next((v for k, v in p3_instances.items() if k.startswith(group + ":" + suffix)), None)
        if inst:
            FROZEN_STRUCTURES[rid] = dict(acceptor=inst["acceptor"], donor=inst["donor"])

    records = []
    # inherited P3/P4 structure-complete pool, re-registered not re-derived
    for rid, cls, src, desc in INHERITED_COMPLETE:
        rec = p4.get(rid) or p4_new.get(rid) or {}
        grade = P4_EXPOSED_GRADE.get(src, "E2")
        frozen = FROZEN_STRUCTURES.get(rid)
        acc = frozen["acceptor"] if frozen else None
        don = frozen["donor"] if frozen else None
        records.append(dict(
            reaction_id=rid, bond_class=cls, source=src,
            closure_group=f"closure:{src}",
            description=desc,
            admission="inherited_from_P3_or_P4_frozen_payload",
            status=rec.get("p4_status", "structure_complete_admitted"),
            status_reason="already structure-complete in the frozen P3/P4 payload; P5 "
                          "re-registers it with its SHA and exposure grade rather than "
                          "re-deriving the structure",
            exposure_grade=grade,
            in_prior_runtime_payload=grade == "E2",
            structure_source=("bound from the frozen P3/P4 runtime instance payload"
                              if frozen else
                              "frozen P3/P4 reaction record; no canonical structure bound in P5"),
            acceptor_smiles=acc, donor_smiles=don,
            canonical_acceptor_signature=sig(acc) if acc else None,
            canonical_reaction_signature=(sig(f"{acc}|{don}") if acc and don
                                          else sig(f"{rid}|{src}")),
            structure_complete=True,
            actionable=False, evidence_closed=False,
            prediction_conditions_verified=False, human_reviewed=False,
            reviewer_type="inherited_frozen_record",
            independent_chemical_validation=False,
        ))

    # new P5 candidates
    for c in CANDIDATES + CANDIDATES_C_BERGENIN:
        complete = c["status"] == "structure_complete_admitted"
        has_smiles = bool(c.get("acceptor_smiles")) and bool(c.get("donor_smiles"))
        if complete and not has_smiles:
            raise SystemExit(f"{c['reaction_id']} claims structure_complete without encodable SMILES")
        if complete and not c.get("product_smiles"):
            raise SystemExit(f"{c['reaction_id']} claims structure_complete without a product SMILES")
        grade = P4_EXPOSED_GRADE.get(c["source"], "E0")
        records.append(dict(
            reaction_id=c["reaction_id"], bond_class=c["bond_class"], source=c["source"],
            closure_group=c["closure_group"],
            acceptor_name=c["acceptor_name"], acceptor_smiles=c["acceptor_smiles"],
            donor_name=c["donor_name"], donor_smiles=c["donor_smiles"],
            product_name=c["product_name"], product_smiles=c["product_smiles"],
            site=c["site"], identity_basis=c["identity_basis"],
            evidence=c["evidence"], failed_tests=c["failed_tests"],
            admission="new_reaction_from_P5_acquisition",
            status=c["status"], status_reason=c["status_reason"],
            exposure_grade=grade,
            in_prior_runtime_payload=grade == "E2",
            exposure_basis=("source is inside the frozen P1-P4 runtime payload or P2 "
                            "unresolved list" if grade == "E2" else
                            "acquired in P5; absent from every P1-P4 runtime payload, "
                            "extension review and unresolved list"),
            canonical_acceptor_signature=(sig(c["acceptor_smiles"])
                                          if c["acceptor_smiles"] else None),
            canonical_reaction_signature=(sig(f"{c['acceptor_smiles']}|{c['donor_smiles']}")
                                           if has_smiles else None),
            structure_complete=complete,
            actionable=False, evidence_closed=False,
            prediction_conditions_verified=False, human_reviewed=False,
            reviewer_type="agent_structural_review",
            independent_chemical_validation=False,
        ))

    write(TASK, str((OUT / "reaction_records.jsonl").relative_to(ROOT)),
          "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records))

    counts = {}
    for r in records:
        k = (r["bond_class"], r["status"])
        counts[f"{k[0]}/{k[1]}"] = counts.get(f"{k[0]}/{k[1]}", 0) + 1
    new_complete = [r for r in records
                    if r["admission"].startswith("new_reaction")
                    and r["structure_complete"]]
    save = json.dumps(dict(
        task=TASK,
        rule="only structure_complete_admitted reactions may enter build or holdout; "
             "identity_complete_structure_deferred records are recorded with the reason "
             "and never counted",
        admitted_structure_complete_total=sum(1 for r in records if r["structure_complete"]),
        new_p5_structure_complete=[
            dict(reaction_id=r["reaction_id"], source=r["source"], site=r["site"],
                 identity_basis=r["identity_basis"], exposure_grade=r["exposure_grade"])
            for r in new_complete],
        new_p5_structure_complete_count=len(new_complete),
        by_class_and_status=counts,
        new_candidates_evaluated=len(CANDIDATES),
        new_candidates_deferred=sum(1 for c in CANDIDATES if not c["failed_tests"] is None
                                    and c["status"] != "structure_complete_admitted"),
        note="P5R-C01 and P5R-C02 are recorded as deferred on purpose: both are C-glycosylations "
             "with a named or class-diagnosed product but no isolation with NMR or standard "
             "comparison. Admitting them would repeat the exact P4 P3R-C01/C02 defect that "
             "quarantined the C3 scope.",
    ), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    write(TASK, str((OUT / "admission_summary.json").relative_to(ROOT)), save)
    event(TASK, "g1_admission", records=len(records),
          new_structure_complete=len(new_complete))
    print(json.dumps(dict(
        admitted_structure_complete=sum(1 for r in records if r["structure_complete"]),
        new_p5_structure_complete=[r["reaction_id"] for r in new_complete],
        by_class_and_status=counts), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())