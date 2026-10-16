"""Isolated A7 source-only C-E02 proposal build; no scope freeze or MCTS."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from rdkit import Chem
from scripts.task016_p3_build import derive_template_smarts, scoped_smarts
from scripts.task016_p6_c_scope import formation_indices
from scripts.task016_p7_c_scope import guard_spec, mutate_controls
from scripts.task016_p7_orchestrate import ROOT, now, role_manifest, save_json, sha_file, verify_stage_chain
from scripts.task016_p7_scope_harness import validate_scope_bank
from flavoretro.glycoside_scope_c_v7 import apply_c_scope
from flavoretro.reviewed_resources import canonical_side

B = ROOT / "outputs/task016-p7/v1/C/E02"
O = B / "scope_build"

def source_C3(mol):
    """Locate actual source C3 via pyrone C4 carbonyl and ring topology."""
    choices = set()
    for ring in mol.GetRingInfo().AtomRings():
        if len(ring) != 6 or not any(mol.GetAtomWithIdx(i).GetAtomicNum() == 8 and mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring):
            continue
        for i in ring:
            atom = mol.GetAtomWithIdx(i)
            if atom.GetAtomicNum() != 6 or not any(b.GetBondType() == Chem.BondType.DOUBLE and b.GetOtherAtom(atom).GetAtomicNum() == 8 and b.GetOtherAtomIdx(i) not in ring for b in atom.GetBonds()):
                continue
            choices.update(n.GetIdx() for n in atom.GetNeighbors() if n.GetIdx() in ring and n.GetAtomicNum() == 6 and mol.GetRingInfo().NumAtomRings(n.GetIdx()) == 1)
    if len(choices) != 1:
        raise ValueError("source flavone C3 atom is not uniquely identified")
    idx = choices.pop()
    if mol.GetAtomWithIdx(idx).GetTotalNumHs() != 1:
        raise ValueError("selected source flavone must have explicit C3-H")
    return idx

def strict_guard(support):
    spec = guard_spec(support)
    mol = Chem.MolFromSmiles(support["acceptor"])
    c3 = source_C3(mol)
    query = Chem.MolFromSmarts(spec["core_query"])
    matches = mol.GetSubstructMatches(query)
    if not matches or len({m.index(c3) for m in matches if c3 in m}) != 1:
        raise ValueError("source core/C3 query mapping ambiguous")
    qidx = matches[0].index(c3)
    rw = Chem.RWMol(query)
    replacement = Chem.AtomFromSmarts("[cH1:778]")
    rw.ReplaceAtom(qidx, replacement)
    spec.update(core_query=Chem.MolToSmarts(rw.GetMol()), required_C3_H=True,
                C3_query_atom_index=qidx, C3_atom_map=778,
                source_C3_acceptor_atom_index=c3,
                query_origin="Original source Murcko core/site-neighbor oxygens plus explicit H1 predicate on independently identified source pyrone C3; C3-OH excluded")
    return spec

def c3_oh_negative(target):
    mol = Chem.MolFromSmiles(target)
    c3 = source_C3(mol)
    rw = Chem.RWMol(mol)
    oxygen = rw.AddAtom(Chem.Atom(8))
    rw.AddBond(c3, oxygen, Chem.BondType.SINGLE)
    changed = rw.GetMol()
    Chem.SanitizeMol(changed)
    return Chem.MolToSmiles(changed, isomericSmiles=True)

def main():
    planpath = O / "boundary_plan.v1.json"
    plan = json.loads(planpath.read_text())
    stage = ROOT / plan["input_G2_path"]
    verify_stage_chain(stage, plan["input_G2_sha256"])
    sourcepath = ROOT / plan["build_support_path"]
    if sha_file(sourcepath) != plan["build_support_sha256"]:
        raise ValueError("source support SHA drift")
    sources = json.loads(sourcepath.read_text())
    if len(sources) != 2 or any(x.get("scope_build_support_eligible") is not True or x.get("future_fresh_eligible") is not False for x in sources):
        raise ValueError("only both qualified, permanently exposed build sources may be used")
    supports = [dict(instance_id=x["reaction_id"], reaction_id=x["reaction_id"],
                     acceptor=x["acceptor_smiles"], donor=x["donor_smiles"], target=x["product_smiles"],
                     reference_precursors=x["reference_precursors"], center_class="flavone_6_C_glucoside",
                     category="C_formation", sugar_type="glucose", development_exposed=True,
                     evidence_eligible=True, human_reviewed=False, independent_chemical_validation=False,
                     required_context=dict(mode="enzymatic", donor_name="UDP-glucose"),
                     provenance=dict(pmcid=None, doi="10.1007/s00253-017-8694-6",
                                     source_role="permanent_design_build_only", evidence_pointers=x["evidence_pointers"],
                                     source_admission_sha256=sha_file(sourcepath))) for x in sources]
    if len({canonical_side([s["acceptor"]]) for s in supports}) != 2:
        raise ValueError("fewer than two distinct canonical acceptors")
    for support in supports:
        source_C3(Chem.MolFromSmiles(support["acceptor"]))
    exacts = [dict(instance_id=s["instance_id"], **derive_template_smarts(s)) for s in supports]
    seed = dict(supports[0], formation=formation_indices(exacts[0]))
    scoped = scoped_smarts(exacts[0], seed, "flavone_6_C_glucoside")
    import hashlib
    digest = lambda text: hashlib.sha256(text.encode()).hexdigest()
    template = dict(template_id=plan["scope_candidate_id"], template_role="scope_template",
                    category="C_formation", sugar_type="glucose", donor=supports[0]["donor"],
                    required_context=supports[0]["required_context"], support_instances=[s["instance_id"] for s in supports],
                    smarts=scoped, scope_template=scoped, exact_instance_template=exacts[0]["smarts"],
                    exact_sha256=digest(exacts[0]["smarts"]), scope_sha256=digest(scoped), allowed_targets=[],
                    guard_spec=strict_guard(supports[0]),
                    scope=dict(namespace="task016_p7", center_class="flavone_6_C_glucoside",
                               mandatory_core="source flavone with C3-H and source-neighbor oxygens", site="C6",
                               sugar="beta-D-glucopyranose", donor="complete original-source identity-bound UDP-glucose graph",
                               allowed_generalization="decorations outside mandatory source-derived core/site constraints",
                               forbidden_generalization="C3-OH flavonol, altered core/site, wrong or unspecified sugar stereo"),
                    scope_transformation=dict(function="derive_template_smarts + scoped_smarts + source-topology C3 H1 query",
                                              source_sha256=sha_file(ROOT/"scripts/task016_p3_build.py"),
                                              derivation_code_sha256=sha_file(Path(__file__)), seed_formation=seed["formation"]),
                    validation_status="proposal_replay_checked_pending_A8", human_reviewed=False)
    trials = []
    for support in supports:
        outcomes = apply_c_scope(template, support["target"], support["required_context"])
        expected = canonical_side(support["reference_precursors"])
        trials.append(dict(template_id=template["template_id"], instance_id=support["instance_id"],
                           reference_precursors=expected, outcomes=outcomes,
                           passed=expected in [x["precursors"] for x in outcomes]))
    controls = [("wrong_core_ring_O_to_S" if name == "wrong_core" else name, target)
                for name, target in mutate_controls(supports[0], template)]
    controls += [("C3_OH_on_chrysin_support", c3_oh_negative(supports[0]["target"])),
                 ("C3_OH_on_luteolin_support", c3_oh_negative(supports[1]["target"])),
                 ("chemical_context", supports[0]["target"]), ("UDP_galactose_context", supports[0]["target"])]
    assert len(controls) == len(plan["negative_controls"]) == 10
    negatives = []
    for prereg, (name, target) in zip(plan["negative_controls"], controls):
        if name != prereg["name"]:
            raise ValueError("preregistered control universe changed")
        context = dict(template["required_context"])
        if name == "chemical_context": context["mode"] = "chemical"
        if name == "UDP_galactose_context": context["donor_name"] = "UDP-galactose"
        outcomes = apply_c_scope(template, target, context)
        negatives.append(dict(template_id=template["template_id"], control_id=prereg["control_id"], name=name,
                              target=target, context=context, expected="refused", outcomes=outcomes,
                              violated=bool(outcomes), fixture_only=True,
                              derived_from_source_id=prereg["source_support_id"],
                              source_reaction_evidence_claim=False))
    validation = validate_scope_bank([template], supports, trials, negatives)
    outputs = []
    for name, content in [("scope_proposal.v1.json", [template]), ("build_supports.v1.json", supports),
                          ("exact_templates.v1.json", exacts), ("build_replay.v1.json", trials),
                          ("boundary_results.v1.json", negatives), ("scope_validation.v1.json", validation)]:
        p = O/name
        if p.exists(): raise ValueError("immutable proposal already exists")
        save_json(p, content, immutable=True)
        outputs.append(p)
    role = role_manifest("A7 Scope Builder", "C-E02", [stage, planpath, sourcepath, Path(__file__),
                         ROOT/"scripts/task016_p3_build.py", ROOT/"scripts/task016_p7_c_scope.py",
                         ROOT/"flavoretro/glycoside_scope_c_v7.py"], outputs,
                         dict(processed=12, passed=12, rejected=0, pending=0), read_holdout=False, read_model_outcome=False)
    role.update(scope_frozen=False, logical_isolation="fresh isolated subprocess reads only SHA-bound design artifacts and code; no model results loaded",
                source_supports=2, synthetic_negative_controls=10, new_MCTS_runs=0,
                A6_admission_not_redecided_by_A7=True)
    save_json(O/"role_A7_scope_proposal_manifest.v1.json", role, immutable=True)
    print(json.dumps(dict(scope_candidates=1, source_support_replay=sum(r["passed"] for r in trials),
                          total_supports=2, negative_controls=len(negatives), violations=sum(r["violated"] for r in negatives),
                          source_C3_H_explicit=True, frozen=False, MCTS=0)))

if __name__ == "__main__": main()
