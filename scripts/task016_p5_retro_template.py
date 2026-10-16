"""TASK-016-P5 G3 helper: derive the C-glycosylation retro template from its support.

P5 deliberately reuses the frozen P3 derivation rather than writing a new one.
`derive_template_smarts` in scripts/task016_p3_build.py produced every working C
and sugar-sugar scope template in the v4/v5 chain, and it has the two properties
P5 needs: the acceptor must be fully conserved by an MCS with the product, and the
transferred sugar must match the donor in exactly one way.

Re-deriving this locally produced three malformed templates in this task before it
was abandoned: a wrong glycosidic bond, a wrong fragment split, and a hand-mapped
donor RDKit could not parse. The frozen function selects atoms by MCS and by
uniqueness, so it has none of those failure modes.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

UDP_GLC = ("O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)"
           "[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1")


def derive(acceptor_smiles, product_smiles, donor_smiles=UDP_GLC):
    """Return the frozen-P3 retro template for one C-glycosylation build support."""
    import importlib.util
    from rdkit import Chem
    spec = importlib.util.spec_from_file_location(
        "p3build", ROOT / "scripts/task016_p3_build.py")
    p3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p3)

    out = p3.derive_template_smarts(
        dict(acceptor=acceptor_smiles, donor=donor_smiles, target=product_smiles))

    rxn = Chem.rdChemReactions.ReactionFromSmarts(out["smarts"])
    rxn.GetSubstructParams().useChirality = True
    mol = Chem.MolFromSmiles(product_smiles)
    want = sorted({Chem.MolToSmiles(Chem.MolFromSmiles(acceptor_smiles), isomericSmiles=True),
                   Chem.MolToSmiles(Chem.MolFromSmiles(donor_smiles), isomericSmiles=True)})
    got = []
    for prods in rxn.RunReactants([mol]):
        try:
            for x in prods:
                Chem.SanitizeMol(x)
        except (ValueError, RuntimeError):
            continue
        got.append(sorted(Chem.MolToSmiles(x, isomericSmiles=True) for x in prods))
    if want not in got:
        raise ValueError(f"derived template does not reproduce its support: {got} != {want}")
    return out


if __name__ == "__main__":
    import io, json, contextlib, importlib.util
    spec = importlib.util.spec_from_file_location(
        "sup", ROOT / "scripts/task016_p5_flavonol_support.py")
    sup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sup)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sup.main()
    built = json.loads(buf.getvalue())
    for rid, v in built.items():
        out = derive(v["acceptor_smiles"], v["product_smiles"])
        print(rid, "REPLAY_OK", out["mapping"])
