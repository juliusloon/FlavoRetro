"""TASK-016-P5 G3 helper: build the two flavonol 8-C-glycoside build supports.

Hand-written flavonol SMILES are error-prone: a fused bicyclic core needs its ring
labels balanced, and this task has already caught two such mistakes. So the two
build supports are assembled here from the frozen acceptor SMILES plus a
beta-D-glucopyranosyl fragment, using RDKit to place the bond and to state the
result. Nothing downstream is allowed to assume a structure string that this
script has not produced and validated.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

# Frozen acceptors, quoted from the P4 payload's C records.
ACCEPTORS = {
    "P3R-C05": dict(name="kaempferol", smiles="O=c1c(O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c2O1"),
    "P3R-C06": dict(name="quercetin", smiles="O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c2O1"),
}
# beta-D-glucopyranosyl with a free anomeric C1 (atom 0 carries one implicit H).
GLUCOSYL = "[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"


def attach_at_c8(smiles, fragment):
    """Bond the fragment's anomeric carbon to C8 of the flavonol.

    C8 is located structurally rather than by a hand-written index: the pyrone
    ring oxygen is the only non-aromatic oxygen with two connections, its aromatic
    neighbour is the C8a fusion carbon, and the free aromatic carbon adjacent to
    that fusion carbon is C8. In kaempferol and quercetin the other free A-ring
    carbon is C6, which is not adjacent to C8a and is therefore not selected.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"acceptor does not parse: {smiles}")
    frag = Chem.MolFromSmiles(fragment)
    if frag is None:
        raise ValueError(f"fragment does not parse: {fragment}")

    ring_o = next((a.GetIdx() for a in mol.GetAtoms()
                   if a.GetSymbol() == "O" and not a.GetIsAromatic() and a.GetDegree() == 2),
                  None)
    if ring_o is None:
        raise ValueError("pyrone ring oxygen not found")
    fusion = [n.GetIdx() for n in mol.GetAtomWithIdx(ring_o).GetNeighbors()
              if n.GetIsAromatic() and n.GetAtomicNum() == 6]
    if not fusion:
        raise ValueError("no aromatic fusion carbon next to the pyrone oxygen")

    site = None
    for f in fusion:
        for nb in mol.GetAtomWithIdx(f).GetNeighbors():
            if (nb.GetIsAromatic() and nb.GetAtomicNum() == 6
                    and nb.GetTotalNumHs() == 1 and nb.GetIdx() != f):
                site = nb.GetIdx()
    if site is None:
        raise ValueError("C8 not found: no free aromatic CH next to the C8a fusion carbon")

    combined = Chem.RWMol(Chem.CombineMols(mol, frag))
    anomeric = combined.GetAtomWithIdx(mol.GetNumAtoms())
    combined.AddBond(anomeric.GetIdx(), site, Chem.BondType.SINGLE)
    anomeric.SetNumRadicalElectrons(0)
    out = combined.GetMol()
    Chem.SanitizeMol(out)
    return out, site



def main():
    result = {}
    for rid, spec in ACCEPTORS.items():
        acc = Chem.MolFromSmiles(spec["smiles"])
        prod, site = attach_at_c8(spec["smiles"], GLUCOSYL)
        acc_smi = Chem.MolToSmiles(acc, isomericSmiles=True)
        prod_smi = Chem.MolToSmiles(prod, isomericSmiles=True)
        # the product must re-parse, be one fragment, and carry no radicals
        assert Chem.MolFromSmiles(prod_smi) is not None, rid
        assert len(Chem.GetMolFrags(prod)) == 1, rid
        assert sum(a.GetNumRadicalElectrons() for a in prod.GetAtoms()) == 0, rid
        # the transferred unit is a glucosyl residue, so the product must be the
        # acceptor plus the whole fragment minus one water
        frag_atoms = Chem.MolFromSmiles(GLUCOSYL).GetNumAtoms()
        frag_bonds = Chem.MolFromSmiles(GLUCOSYL).GetNumBonds()
        assert prod.GetNumAtoms() == acc.GetNumAtoms() + frag_atoms, (
            f"{rid}: product must be acceptor + glucosyl fragment")
        # combining two molecules adds one inter-fragment bond; exactly one new
        # bond may exist, so the product must have precisely the bonds of both parts
        assert prod.GetNumBonds() == acc.GetNumBonds() + frag_bonds + 1, (
            f"{rid}: exactly one new bond must be formed between acceptor and glucosyl")
        result[rid] = dict(
            name=spec["name"],
            acceptor_smiles=acc_smi,
            product_smiles=prod_smi,
            attachment_site_index=site,
            acceptor_formula=rdMolDescriptors.CalcMolFormula(acc),
            product_formula=rdMolDescriptors.CalcMolFormula(prod),
            heavy_atoms=dict(acceptor=acc.GetNumAtoms(), product=prod.GetNumAtoms()),
        )
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())