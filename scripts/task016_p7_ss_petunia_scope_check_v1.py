"""A7 final isolated verification, with preregistered synthetic OH canaries."""
from __future__ import annotations
import ast
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "outputs/task016-p7/v1/SS/E02_design/Petunia_scope_proposal_v1"
TASK = "TASK-016-P7"
SELF = "scripts/task016_p7_ss_petunia_scope_check_v1.py"
GUARD = "scripts/task016_p7_ss_petunia_scope_guard_v1.py"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(name, value):
    from scripts.operate import write as opwrite
    path = OUT / name
    if path.exists():
        raise ValueError("immutable supplement exists: " + name)
    opwrite(TASK, str(path.relative_to(ROOT)),
            json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")

def now():
    return datetime.now(timezone.utc).isoformat()

def preregister():
    for name in [SELF, GUARD]:
        ast.parse((ROOT / name).read_text())
    write("final_engineering_check_preregistration.json", dict(
        task=TASK, epoch_id="SS-E02-design", agent_role="A7 Scope Builder",
        timestamp=now(), read_holdout=False, read_model_outcome=False,
        input_sha={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.is_file()},
        code_sha={n:sha(ROOT / n) for n in [SELF, GUARD]},
        controls=[
            dict(id="synthetic_add_one_aromatic_OH_at_core_map102",expected_scope=True,expected_exact=False),
            dict(id="synthetic_remove_one_source_aromatic_OH",expected_scope=True,expected_exact=False),
            dict(id="required_context_mismatch",expected_scope=False),
            dict(id="existing_unmodified_v7_O6_dispatcher_not_yet_wired",expected_scope=False)],
        synthetic_variants_are_not_source_support=True,
        no_source_qualification_or_independent_chemical_claim=True,
        no_scope_or_guard_mutation=True, no_stage_or_runtime_registration=True))

def check():
    from rdkit import Chem
    from rdkit.Chem import rdChemReactions
    from scripts.task016_p7_ss_petunia_scope_guard_v1 import (
        CORE, apply_template, mapped_reference_path, canonical, side)
    from flavoretro.glycoside_library_v7 import apply_template as old_v7_apply
    plan = json.loads((OUT / "final_engineering_check_preregistration.json").read_text())
    for name,digest in {**plan["input_sha"],**plan["code_sha"]}.items():
        if sha(ROOT / name) != digest:
            raise ValueError("precheck frozen input/code SHA drift: " + name)
    t=json.loads((OUT / "scope_bank.json").read_text())[0]
    supports=json.loads((OUT / "build_supports.json").read_text())
    seed=next(r for r in supports if r["parent_sugar"]=="beta-D-Glcp")
    q=Chem.MolFromSmarts(CORE)
    labels={a.GetAtomMapNum():a.GetIdx() for a in q.GetAtoms()}
    def variant(text, op):
        mol=Chem.MolFromSmiles(text)
        match=mol.GetSubstructMatch(q)
        rw=Chem.RWMol(mol)
        if op=="add":
            owner=match[labels[102]]
            assert mol.GetAtomWithIdx(owner).GetTotalNumHs()==1
            oxygen=rw.AddAtom(Chem.Atom(8))
            rw.AddBond(owner,oxygen,Chem.BondType.SINGLE)
        else:
            oxygen=next(a.GetIdx() for a in mol.GetAtoms()
                        if a.GetAtomicNum()==8 and a.GetDegree()==1
                        and a.GetBonds()[0].GetBondType()==Chem.BondType.SINGLE
                        and a.GetNeighbors()[0].GetIsAromatic())
            rw.RemoveAtom(oxygen)
        value=rw.GetMol();Chem.SanitizeMol(value)
        return Chem.MolToSmiles(value,isomericSmiles=True)
    exact_rows=json.loads((OUT / "exact_templates.json").read_text())
    canaries=[]
    for op,cid in [("add","synthetic_add_one_aromatic_OH_at_core_map102"),
                   ("remove","synthetic_remove_one_source_aromatic_OH")]:
        target=variant(seed["target"],op)
        acceptor=variant(seed["acceptor"],op)
        expected=side([Chem.MolFromSmiles(acceptor),Chem.MolFromSmiles(seed["donor"])])
        outcomes=apply_template(t,target)
        mapped=mapped_reference_path(t,target)
        exact_fires=[]
        for exact in exact_rows:
            reaction=rdChemReactions.ReactionFromSmarts(exact["smarts"])
            reaction.GetSubstructParams().useChirality=True
            exact_fires.append(bool(reaction.RunReactants((Chem.MolFromSmiles(target),))))
        passed=(expected in [o["precursors"] for o in outcomes]
                and any(o["precursors"]==expected and o["original_target_maps_preserved"]
                        and o["all_output_maps_unique"] for o in mapped)
                and not any(exact_fires)
                and target not in {r["target"] for r in supports})
        canaries.append(dict(control_id=cid,target=target,
                             expected_precursors=expected,dispatcher_outcomes=outcomes,
                             mapped_outcomes=mapped,exact_templates_fired=exact_fires,
                             source_support=False,fresh_holdout=False,source_assay=False,passed=passed))
    context_outcomes=apply_template(t,seed["target"],context={"mode":"chemical","donor_name":"UDP-glucose"})
    old_outcomes=[dict(instance_id=r["instance_id"],outcomes=old_v7_apply(t,r["target"])) for r in supports]
    canaries.extend([
        dict(control_id="required_context_mismatch",outcomes=context_outcomes,passed=not context_outcomes),
        dict(control_id="existing_unmodified_v7_O6_dispatcher_not_yet_wired",outcomes=old_outcomes,
             passed=all(not r["outcomes"] for r in old_outcomes),
             interpretation="expected lack of production integration; isolated proposal only")])
    write("final_engineering_check_results.json",dict(
        task=TASK,epoch_id="SS-E02-design",agent_role="A7 Scope Builder",timestamp=now(),
        preregistration_sha256=sha(OUT/"final_engineering_check_preregistration.json"),
        counts=dict(processed=4,passed=sum(r["passed"] for r in canaries),
                    rejected=sum(not r["passed"] for r in canaries),pending=0),
        results=canaries, no_scope_or_guard_mutation=True,
        existing_formal_dispatcher_connected=False, read_holdout=False,read_model_outcome=False,
        other5_scientific_sources_read=False, HTTP=0,MCTS=0,
        human_reviewed=False,independent_chemical_validation=False))
    assert all(r["passed"] for r in canaries),"final isolated verification failure"
    print(json.dumps(dict(engineering_canaries_passed=4,of=4,scope_mutated=False,
                          formal_runtime_connected=False)))

if __name__=="__main__":
    {"preregister":preregister,"check":check}[sys.argv[1]]()
