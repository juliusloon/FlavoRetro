"""TASK-016-P5 G1c-2: structure encoding for the newly admitted C-glycosylation candidates.

Structures are built here from first principles and validated with RDKit, not
copied from a report. That distinction is deliberate: two reconnaissance reports
in this task produced PMCIDs that did not exist as described, and the surviving
one produced SMILES that do not parse. A subagent's string is a claim about a
molecule, exactly like its string about a paper.

Each structure below is assembled from named, unambiguous chemistry:

  gallic acid            3,4,5-trihydroxybenzoic acid
  4-O-methylgallic acid  3-hydroxy-4-methoxy-5-hydroxybenzoic acid
  UDP-glucose            the frozen donor already in the P2/v3 payload

The C-glycosylation site is the aromatic carbon that carries the carboxyl group,
i.e. the ipso carbon of the benzoyl unit, which is the only position consistent
with a 2-C-glycoside of a benzoic acid and the position the source assigns.

Validation is not optional. Every molecule must parse, be a single connected
fragment, and round-trip to a stable canonical SMILES before it may be written.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

# UDP-alpha-D-glucose, byte-identical to the donor already frozen in the P2/v3 payload.
UDP_GLC = ("O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)"
           "[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1")

# beta-D-glucopyranosyl, written as the C-attached fragment anomeric-C1 first.
# C1 is the atom that forms the C-C bond in a C-glycoside.
#
# Atom 0 is the anomeric carbon C1 and carries exactly one implicit hydrogen, so
# that adding the C-C bond to the aromatic ring does not exceed its valence. The
# ring oxygen closes between C1 and C5.
BETAD = "[C@@H]1(O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O)"

# 3,4,5-trihydroxybenzoic acid (gallic acid)
GA = "O=C(O)c1cc(O)c(O)c(O)c1"
# 4-O-methylgallic acid: the 4-OH of gallic acid is methylated
GA_OMe = "O=C(O)c1cc(O)c(OC)c(O)c1"


def attach_C(aromatic_ring_smiles, fragment):
    """Attach the anomeric carbon of `fragment` to a free aromatic ring position.

    A C-glycosylation substitutes an aromatic hydrogen: the enzyme deprotonates a
    phenol and the resulting ortho carbon attacks the donor's anomeric carbon. The
    ipso carbon is therefore a ring atom that still carries an implicit hydrogen,
    which for 3,4,5-trihydroxybenzoic acid is C2/C6, adjacent to the carboxyl.

    The site is chosen by that structural rule rather than by index, and the
    carbon that already bears the carboxyl group is excluded because it has no
    free valence.
    """
    mol = Chem.MolFromSmiles(aromatic_ring_smiles)
    if mol is None:
        raise ValueError(f"aromatic scaffold does not parse: {aromatic_ring_smiles}")
    frag = Chem.MolFromSmiles(fragment)
    if frag is None:
        raise ValueError(f"fragment does not parse: {fragment}")

    sites = [a.GetIdx() for a in mol.GetAtoms()
             if a.GetIsAromatic() and a.GetTotalNumHs() == 1]
    if not sites:
        raise ValueError("no free aromatic position available for C-glycosylation")
    # C2 and C6 are symmetry-equivalent in both scaffolds; take the lowest index.
    ipso = sites[0]

    combined = Chem.RWMol(Chem.CombineMols(mol, frag))
    anomeric = combined.GetAtomWithIdx(mol.GetNumAtoms())
    combined.AddBond(anomeric.GetIdx(), ipso, Chem.BondType.SINGLE)
    # The fragment declares the anomeric hydrogen as an explicit count. After the
    # C-C bond is added, that hydrogen is still the correct one, but RDKit will
    # not recompute a serialised [C] radical correctly, so the hydrogen is handed
    # back to implicit bookkeeping and the charge/radical state is normalised.
    anomeric.SetNumExplicitHs(0)
    anomeric.SetNoImplicit(True)
    anomeric.SetNumExplicitHs(1)
    anomeric.SetFormalCharge(0)
    out = combined.GetMol()
    Chem.SanitizeMol(out)
    return out


def validate(name, mol, expect_heavy_atoms=None):
    smi = Chem.MolToSmiles(mol, isomericSmiles=True)
    check = Chem.MolFromSmiles(smi)
    issues = []
    if check is None:
        issues.append("canonical SMILES does not re-parse")
    if len(Chem.GetMolFrags(mol)) != 1:
        issues.append("molecule is not a single connected fragment")
    if expect_heavy_atoms is not None and mol.GetNumAtoms() != expect_heavy_atoms:
        issues.append(f"heavy atom count {mol.GetNumAtoms()} != expected {expect_heavy_atoms}")
    return smi, issues


def main():
    out = {}
    for label, scaffold, acceptor_name in (
        ("GA_C_glucoside", GA, "gallic acid"),
        ("4OMGA_C_glucoside", GA_OMe, "4-O-methylgallic acid"),
    ):
        acceptor = Chem.MolFromSmiles(scaffold)
        a_smi, a_iss = validate(f"{label}-acceptor", acceptor)
        product = attach_C(scaffold, BETAD)
        p_smi, p_iss = validate(f"{label}-product", product)
        donor = Chem.MolFromSmiles(UDP_GLC)
        d_smi, d_iss = validate(f"{label}-donor", donor)
        # the donor must be byte-identical to the frozen P2/v3 UDP-glucose
        frozen = "O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1"
        out[label] = dict(
            acceptor_name=acceptor_name,
            acceptor_smiles=a_smi,
            donor_name="UDP-alpha-D-glucose",
            donor_smiles=d_smi,
            donor_matches_frozen_v3=(d_smi == frozen),
            product_smiles=p_smi,
            product_formula=rdMolDescriptors.CalcMolFormula(product),
            acceptor_formula=rdMolDescriptors.CalcMolFormula(acceptor),
            heavy_atoms=dict(acceptor=acceptor.GetNumAtoms(), product=product.GetNumAtoms()),
            issues=a_iss + p_iss + d_iss,
        )
    bad = [k for k, v in out.items() if v["issues"] or not v["donor_matches_frozen_v3"]]
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if bad:
        print("REJECTED:", bad)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())