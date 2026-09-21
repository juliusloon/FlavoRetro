"""Structural candidates only; this is not an expansion or feasibility policy."""

import json
from rdkit import Chem
from .resources import structure, dumps, ROOT, sha


def audit(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"status": "parse_failure", "sites": []}
    rings = []
    for ring in mol.GetRingInfo().AtomRings():
        atoms = [mol.GetAtomWithIdx(i) for i in ring]
        if len(ring) not in (5, 6) or any(a.GetIsAromatic() for a in atoms):
            continue
        if sorted(a.GetAtomicNum() for a in atoms) != [6] * (len(ring) - 1) + [8]:
            continue
        oxygenated = sum(
            any(
                n.GetAtomicNum() in (7, 8) and n.GetIdx() not in ring
                for n in a.GetNeighbors()
            )
            for a in atoms
            if a.GetAtomicNum() == 6
        )
        if oxygenated >= 2:
            rings.append(set(ring))
    sites = {}
    for ring in rings:
        oxygen = next(
            mol.GetAtomWithIdx(i)
            for i in ring
            if mol.GetAtomWithIdx(i).GetAtomicNum() == 8
        )
        for carbon in oxygen.GetNeighbors():
            if carbon.GetIdx() not in ring or carbon.GetAtomicNum() != 6:
                continue
            for other in carbon.GetNeighbors():
                if other.GetIdx() in ring:
                    continue
                family = None
                if other.GetAtomicNum() == 8:
                    partners = [
                        a for a in other.GetNeighbors() if a.GetIdx() != carbon.GetIdx()
                    ]
                    if not partners:
                        continue  # Free OH is not a glycosidic connection.
                    if any(
                        any(p.GetIdx() in r for r in rings if r != ring)
                        for p in partners
                    ):
                        family = "sugar_sugar_O_candidate"
                    elif any(p.GetIsAromatic() for p in partners):
                        family = "aryl_O_candidate"
                    elif any(p.GetAtomicNum() == 15 for p in partners):
                        family = "phosphate_donor_control"
                    else:
                        family = "other_O_candidate"
                elif other.GetAtomicNum() == 6 and other.GetIsAromatic():
                    family = "aryl_C_candidate"
                elif other.GetAtomicNum() == 7:
                    family = "N_candidate"
                if not family:
                    continue
                bond = mol.GetBondBetweenAtoms(carbon.GetIdx(), other.GetIdx())
                idx = bond.GetIdx()
                # Direct remove/add only tests graph bookkeeping, not reaction prediction.
                rw = Chem.RWMol(mol)
                rw.RemoveBond(carbon.GetIdx(), other.GetIdx())
                rw.AddBond(carbon.GetIdx(), other.GetIdx(), bond.GetBondType())
                restored = rw.GetMol()
                # Atom chiral tags are relative to neighbor order. Re-adding a bond
                # changes that order, so preserve the original absolute stereo.
                for old in mol.GetAtoms():
                    if old.GetChiralTag() == Chem.ChiralType.CHI_UNSPECIFIED:
                        continue
                    new = restored.GetAtomWithIdx(old.GetIdx())
                    before = [n.GetIdx() for n in old.GetNeighbors()]
                    after = [n.GetIdx() for n in new.GetNeighbors()]
                    permutation = [before.index(i) for i in after]
                    inversions = sum(
                        permutation[i] > permutation[j]
                        for i in range(len(permutation))
                        for j in range(i + 1, len(permutation))
                    )
                    if inversions % 2:
                        new.InvertChirality()
                Chem.SanitizeMol(restored)
                sites[idx] = {
                    "family": family,
                    "bond_index": idx,
                    "anomeric_candidate": carbon.GetIdx(),
                    "other_atom": other.GetIdx(),
                    "sugar_ring_size": len(ring),
                    "graph_roundtrip": Chem.MolToSmiles(restored, isomericSmiles=True)
                    == Chem.MolToSmiles(mol, isomericSmiles=True),
                }
    return {
        "status": "checked",
        "sugar_ring_candidates": len(rings),
        "sites": list(sites.values()),
        "claim": "topology candidates; no independent labels or reaction feasibility",
    }


def build(output):
    from pathlib import Path
    from .policies import records

    path = Path(output)
    if path.exists():
        raise ValueError("immutable output exists")
    results = []
    for row in records():
        if row["kind"] == "molecule":
            results.append(
                {
                    "id": row["id"],
                    "name": row["raw"]["query_name"],
                    "source_sha256": row["source_sha256"],
                    **audit(row["raw"]["smiles"]),
                }
            )
    result = {
        "code_sha256": sha(__file__),
        "input_sha256": sha(ROOT / "data/derived/v1/records.json"),
        "molecules": len(results),
        "detected": sum(bool(r["sites"]) for r in results),
        "sites": sum(len(r["sites"]) for r in results),
        "roundtrip_failures": sum(
            not s["graph_roundtrip"] for r in results for s in r["sites"]
        ),
        "scope": "development structural diagnostic; not precision/recall or MCTS improvement",
        "records": results,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(result))
    path.chmod(0o444)
    return {k: v for k, v in result.items() if k != "records"}


if __name__ == "__main__":
    import sys

    print(dumps(build(sys.argv[1])))
