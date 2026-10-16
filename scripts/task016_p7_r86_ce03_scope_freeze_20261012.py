"""R86: C-E03 scope build (G3) + G4 freeze for the flavone 8-C-glucoside scope.

Construction mirrors the frozen C-E02 row: exact template via
derive_template_smarts, scope via scoped_smarts (generic branch), guard via
guard_spec + pyrone C3-H predicate (flavone discriminator), replay via
apply_template, >=6 boundary controls with 0 violations.
"""
import json, hashlib
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p3_build import derive_template_smarts, scoped_smarts
from scripts.task016_p7_c_scope import guard_spec
from scripts.task016_p7_c_e02_scope_build import strict_guard
from scripts.task016_p7_scope_harness import validate_scope_bank, replay_scope_bank, freeze_scope_bank
from scripts.task016_p7_orchestrate import role_manifest, freeze_stage_manifest, verify_stage_chain, sha_file
from rdkit import Chem
from flavoretro.reviewed_resources import canonical_side

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
E = B / "C/E03"
R85 = E / "design/C-E03-R85-build-supports-v1"
R84 = E / "design/C-E03-R84-pubchem-structure-custody-v1"
R83 = E / "design/C-E03-R83-liu2021-design-intake-v1"
R84 = E / "design/C-E03-R84-pubchem-structure-custody-v1"
G1 = B / "stages/global/G1_EXPOSURE_LEDGER.json"

def digest(s): return hashlib.sha256(s.encode()).hexdigest()

def main():
    supports = json.loads((ROOT / R85 / "build_supports.json").read_text())
    normalization_note = None
    for s in supports:
        if isinstance(s["reference_precursors"], str):
            s["reference_precursors"] = s["reference_precursors"].split(".")
            normalization_note = "R85 draft stored reference_precursors as a joined canonical string; normalized to the C-E02 list form at scope-build load (no dot inside either component; canonical values unchanged)"
    site_ver = load(R85 / "site_verification.json")
    det = load(R85 / "A6_design_evidence_determination.json")
    assert site_ver["passed"] and det["reactions_admitted_as_design_build_supports"] == 2
    # exact template from the apigenin seed
    from scripts.task016_p6_c_scope import formation_indices
    exact1 = derive_template_smarts(supports[0])
    formation = {"formation": formation_indices(exact1)}
    seed_formation = formation["formation"]
    assert seed_formation and "product_atom_indices" in seed_formation, sorted(seed_formation.keys())
    scope_smarts = scoped_smarts(exact1, formation, "flavone_8_C_glucoside")
    assert scope_smarts.count(">>") == 1
    guard = strict_guard(supports[0])
    exact_sm = exact1["smarts"]
    assert ">>" in exact_sm
    row = dict(template_id="p7-C-E03:flavone_8_C_glucoside_C8_H",
        support_instances=[s["instance_id"] for s in supports],
        exact_instance_template=exact_sm, exact_sha256=digest(exact_sm),
        scope_template=scope_smarts, smarts=scope_smarts, scope_sha256=digest(scope_smarts),
        template_role="scope_template", allowed_targets=[], category="C_formation",
        sugar_type="glucose", donor=canonical_side([supports[0]["donor"]]),
        required_context=dict(donor_name="UDP-glucose", mode="enzymatic"),
        guard_spec=guard,
        scope=dict(family="C", namespace="task016_p7", center_class="flavone_8_C_glucoside",
            site="A-ring C8 (computational locator verified; C6 control discriminates)",
            sugar="beta-D-glucopyranose", donor="complete original-source identity-bound UDP-glucose graph",
            mandatory_core="source flavone with C3-H and source-neighbor oxygens",
            allowed_generalization="decorations outside mandatory source-derived core/site constraints",
            forbidden_generalization="C3-OH flavonol, altered core/site, wrong or unspecified sugar stereo"),
        scope_transformation=dict(function="derive_template_smarts + scoped_smarts (generic) + pyrone C3-H query",
            seed_reaction_id=supports[0]["instance_id"], seed_formation=seed_formation),
        validation_status="A7 proposal; frozen at G4 with replay/boundary evidence",
        human_reviewed=False)
    bank = [row]
    replay = replay_scope_bank(bank, supports)
    assert all(r["passed"] for r in replay) and len(replay) == 2, [(r["instance_id"], r["passed"]) for r in replay]
    from flavoretro.glycoside_library_v7 import apply_template
    v1plan = json.loads((ROOT / R85 / "boundary_plan.json").read_text())
    planpath = R85 / "boundary_plan.v2.json"
    if not (ROOT / planpath).exists():
        from rdkit import Chem as _C
        st2 = load(R84 / "structures_by_name.v2.json")["structures"]
        def epimer(smiles):
            mol = _C.MolFromSmiles(smiles)
            # anomeric carbon = the glycosyl C bearing the ring O and three heavy neighbours
            for a in mol.GetAtoms():
                if a.GetAtomicNum() == 6 and a.IsInRing() and a.GetChiralTag() != _C.ChiralType.CHI_UNSPECIFIED \
                        and any(n.GetAtomicNum() == 8 for n in a.GetNeighbors()) and sum(1 for n in a.GetNeighbors() if n.GetAtomicNum() == 6) >= 2:
                    m2 = _C.Mol(mol); m2.GetAtomWithIdx(a.GetIdx()).InvertChirality()
                    return _C.MolToSmiles(m2, isomericSmiles=True)
            raise ValueError("anomeric carbon not found")
        v2 = dict(task=T, at=now(), supersedes="boundary_plan.json (v1)",
            supersession_reason="v1 BC6/BC7 mis-specified the retro direction: the scope template firing on the exact support targets (vitexin/orientin) is the replay behaviour required by the contract, not a boundary violation; replaced by anomeric-epimer negatives (mutate_controls epimer pattern); v1 retained as evidence",
            controls=[c for c in v1plan["controls"] if c["control_id"] not in ("BC6-vitexin_product", "BC7-orientin_product")] + [
                dict(control_id="BC6v2-vitexin_anomeric_epimer", role="wrong_anomeric_stereo_must_not_fire",
                     structure=epimer(st2["vitexin"]["isomeric_smiles"]), source="computed epimer of R84 vitexin (no new HTTP)"),
                dict(control_id="BC7v2-orientin_anomeric_epimer", role="wrong_anomeric_stereo_must_not_fire",
                     structure=epimer(st2["orientin"]["isomeric_smiles"]), source="computed epimer of R84 orientin (no new HTTP)")],
            note="8 distinct controls, all must not fire; violation=0 required at G3",
            approval_type="agent_delegated", human_reviewed=False)
        put(str(planpath), v2)
    plan = load(planpath)
    controls = []
    for c in plan["controls"]:
        outs = apply_template(row, c["structure"])
        controls.append(dict(template_id=row["template_id"], control_id=c["control_id"], role=c["role"],
            structure_sha256=digest(c["structure"]), fired_outcomes=len(outs), violated=(len(outs) > 0)))
    bad = [c["control_id"] for c in controls if c["violated"]]
    assert not bad, bad
    identity = [dict(instance_id=s["instance_id"], pmcid=None, source_identity_verified=True,
                     identity_basis="Crossref publisher metadata (R83 A3_identity.json) + owner-supplied PDF SHA binding",
                     doi="10.1021/acs.jafc.1c00602") for s in supports]
    structure = [dict(instance_id=s["instance_id"], reconciled=True,
                      basis="PubChem authoritative structures (R84) + formula delta C6H10O5 + computational C8 site verification (R85)",
                      dual_channel="paper reaction-claim harvest (A4/A5 dual readers) x PubChem structure x formula check") for s in supports]
    check = validate_scope_bank(bank, supports, replay, controls)
    assert check["passed"]
    # G2 manifest (design acquire) branching off global G1
    g2_files = [R85 / "precontract.json", R85 / "boundary_plan.json", R85 / "site_verification.json",
                R85 / "build_supports.json", R85 / "A6_design_evidence_determination.json",
                R83 / "precontract.json", R83 / "A3_identity.json", R83 / "A4/article_text_harvest.json",
                R83 / "A5/article_text_harvest.json", R83 / "scientific_exposure_reads.jsonl",
                R84 / "precontract.json", R84 / "structures_by_name.v2.json", R84 / "formula_consistency.v2.json",
                Path("data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P2-2-liu2021.pdf"),
                Path(__file__).resolve().relative_to(ROOT)]
    g2dir = E / "stages"
    if not (ROOT / g2dir / "G2_DESIGN_ACQUIRE.json").exists():
        freeze_stage_manifest(ROOT / g2dir, "G2_DESIGN_ACQUIRE", g2_files, G1,
            expected_previous_sha=sha_file(G1), family="C", epoch_id="C-E03")
    g3_files = [R85 / "build_supports.json", R85 / "site_verification.json", R85 / "boundary_plan.json",
                R85 / "A6_design_evidence_determination.json",
                Path(__file__).resolve().relative_to(ROOT)]
    if not (ROOT / g2dir / "G3_SCOPE_BUILD.json").exists():
        freeze_stage_manifest(ROOT / g2dir, "G3_SCOPE_BUILD", g3_files, g2dir / "G2_DESIGN_ACQUIRE.json",
            expected_previous_sha=sha_file(g2dir / "G2_DESIGN_ACQUIRE.json"), family="C", epoch_id="C-E03")
    manifest = None
    if not (ROOT / E / "scope_manifest.json").exists():
        manifest = freeze_scope_bank(E, bank, supports, replay, controls, identity, structure,
            family="C", epoch_id="C-E03",
        additional_files=[str(R85 / "site_verification.json"), str(R85 / "A6_design_evidence_determination.json"),
                          str(R84 / "structures_by_name.v2.json"), str(R85 / "boundary_plan.json"), str(R85 / "boundary_plan.v2.json")])
    if not (ROOT / g2dir / "G4_SCOPE_FREEZE.json").exists():
        freeze_stage_manifest(ROOT / g2dir, "G4_SCOPE_FREEZE",
            [E / "scope_manifest.json", E / "scope_bank.json", E / "build_supports.json", E / "build_replay.json",
             E / "boundary_results.json", E / "source_identity.json", E / "dual_structure_reconciliation.json",
             R85 / "site_verification.json", Path(__file__).resolve().relative_to(ROOT)],
            g2dir / "G3_SCOPE_BUILD.json",
            expected_previous_sha=sha_file(g2dir / "G3_SCOPE_BUILD.json"), family="C", epoch_id="C-E03")
    if not (ROOT / E / "role_A0_G3_G4_freeze_manifest.json").exists():
        put(E / "role_A0_G3_G4_freeze_manifest.json", dict(task=T, agent_role="A0", epoch_id="C-E03",
        at=now(), approval_type="agent_delegated", human_reviewed=False,
        counts=dict(processed=1, passed=1, rejected=0, pending=0), errors=[],
        input_manifest_sha={str(p): sha_file(p) for p in (R85 / "build_supports.json", R85 / "site_verification.json")},
        output_file_sha={str(E / "scope_manifest.json"): sha_file(E / "scope_manifest.json"),
                         str(g2dir / "G4_SCOPE_FREEZE.json"): sha_file(g2dir / "G4_SCOPE_FREEZE.json")},
        scope_audit=check, read_model_outcome=False, source_evidence_pointers=[],
        reference_precursors_normalization=normalization_note))
    ledger = B / "epoch_ledger.jsonl"
    row2 = dict(task=T, epoch_id="C-E03", family="C", stage="G4_SCOPE_FREEZE", status="active",
        event_type="C_E03_scope_frozen", at=now(),
        stage_manifest_path=str(g2dir / "G4_SCOPE_FREEZE.json"), stage_manifest_sha256=sha_file(g2dir / "G4_SCOPE_FREEZE.json"),
        scope_manifest_sha256=sha_file(E / "scope_manifest.json"), scopes=1,
        build_supports=2, boundary_controls=len(controls), replay_passed=2, boundary_violations=0,
        build_source="liu2021 JAFC 2021 TcCGT1 (late_prior_design)",
        approval_type="agent_delegated", human_reviewed=False)
    write(T, str(ledger), (ROOT / ledger).read_text() + json.dumps(row2, sort_keys=True) + "\n")
    event(T, "C_E03_G4_frozen", scopes=1, replay=2, controls=len(controls))
    print(json.dumps(dict(scope_audit=check, G4=sha_file(g2dir / "G4_SCOPE_FREEZE.json"))))

if __name__ == "__main__":
    main()
