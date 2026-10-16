"""R84 v2 (additive): re-parse PubChem custody with the current property key."""
import json, re
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, now

T = "TASK-016-P7"; OUT = "outputs/task016-p7/v1/C/E03/design/C-E03-R84-pubchem-structure-custody-v1"

def main():
    v1 = json.loads((ROOT / OUT / "structures_by_name.json").read_text())
    structures = {}
    for name, s in v1["structures"].items():
        j = json.loads((ROOT / s["raw_pointer"]).read_text())
        props = j["PropertyTable"]["Properties"][0]
        smi = props.get("IsomericSMILES") or props.get("SMILES") or props.get("ConnectivitySMILES")
        assert smi, name
        structures[name] = dict(s, isomeric_smiles=smi, smiles_field_semantics="PubChem current API: 'SMILES' is the isomeric SMILES; 'ConnectivitySMILES' is non-isomeric")
    if not (ROOT / OUT / "structures_by_name.v2.json").exists():
        put(OUT + "/structures_by_name.v2.json", dict(v1, at=now(), supersedes="structures_by_name.json (property-key rename: IsomericSMILES -> SMILES in current PubChem API)",
            structures=structures))
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    def counts(f):
        return dict((el, int(n or 1)) for el, n in re.findall(r"([A-Z][a-z]?)([0-9]*)", f))
    cg = counts("C6H10O5")
    checks = {}
    for a, p, label in (("apigenin", "vitexin", "apigenin+Glc->vitexin"), ("luteolin", "orientin", "luteolin+Glc->orientin")):
        ma = Chem.MolFromSmiles(structures[a]["isomeric_smiles"]); mp = Chem.MolFromSmiles(structures[p]["isomeric_smiles"])
        assert ma is not None and mp is not None, (label, "rdkit parse failed")
        fa = rdMolDescriptors.CalcMolFormula(ma); fp = rdMolDescriptors.CalcMolFormula(mp)
        ca, cp = counts(fa), counts(fp)
        delta = {k: cp.get(k, 0) - ca.get(k, 0) for k in set(cp) | set(ca)}
        checks[label] = dict(acceptor_formula=fa, product_formula=fp, delta=delta, delta_is_C6H10O5=(delta == cg))
    ok = all(v["delta_is_C6H10O5"] for v in checks.values())
    put(OUT + "/formula_consistency.v2.json", dict(task=T, at=now(), checks=checks, all_deltas_C6H10O5=ok,
        note="product = acceptor + one C6H10O5 glycosyl residue (C-glycosylation, no hydrolysis net change)",
        approval_type="agent_delegated", human_reviewed=False))
    event(T, "R84_v2_parsed", all_ok=ok)
    print(json.dumps({n: dict(cid=structures[n]["cid"], formula=structures[n]["molecular_formula"], smiles=structures[n]["isomeric_smiles"][:60]) for n in structures}))

if __name__ == "__main__":
    main()
