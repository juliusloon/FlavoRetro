#!/usr/bin/env python3
"""Petunia A7 scope proposal, preregistration and isolated dispatcher validation.

Only SHA-pinned Petunia design supports are read. No fresh, model output,
network, MCTS, runtime registry, stage ledger or historical payload is consumed
or mutated. Output is a proposal awaiting independent A8 and root registration.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TASK = "TASK-016-P7"
OUT = ROOT / "outputs/task016-p7/v1/SS/E02_design/Petunia_scope_proposal_v1"
A6 = "outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/Petunia_A6_v1/"
INPUTS = {
    A6 + "2_source_qualified_design_supports.jsonl": "12a563910fa8e3ecb1dcf8081a1de314d235286090f06d86b4a8677bdd3500fe",
    A6 + "A6_source_reconciliation_summary.json": "281f5b8f395dcb722a34c48b3be109e03ba9465089da0a4ec310f933ce9ee350",
    A6 + "role_A6_manifest.json": "a99f413b977d313ad5a6a278c7804d062408cdc2572b4c20bf8eadae05025d98",
}
GUARD_PATH = "scripts/task016_p7_ss_petunia_scope_guard_v1.py"
BUILD_PATH = "scripts/task016_p7_ss_petunia_scope_build_v3.py"
RAW = "data/raw/task016-p7/SS/reference_discovery_r2/originals/SS-REF-ORIG-R2-d94d8131c3734af38dee07d8ca0fba65.article_version"
RAW_SHA = "404f25913b161a16c6b9c16ba6750c78d089a8407f3f6cdb64afc74c623bf26b"
CONTROLS = [
    ("parent_C4_unspecified", "remove_parent_stereo", 4),
    ("parent_C2_epimer", "flip_parent_stereo", 2),
    ("parent_C3_epimer", "flip_parent_stereo", 3),
    ("parent_C5_epimer", "flip_parent_stereo", 5),
    ("parent_alpha_anomer", "flip_parent_stereo", 1),
    ("terminal_alpha_anomer", "flip_terminal_stereo", 1),
    ("terminal_C2_epimer", "flip_terminal_stereo", 2),
    ("terminal_C3_epimer", "flip_terminal_stereo", 3),
    ("terminal_C4_epimer", "flip_terminal_stereo", 4),
    ("terminal_C5_epimer", "flip_terminal_stereo", 5),
    ("wrong_parent_O3_site", "move_link", 3),
    ("wrong_parent_O6_site", "move_link", 6),
    ("wrong_flavanone_core", "reduce_core", None),
    ("wrong_missing_UDP_donor", "donor_drop_UDP", None),
    ("wrong_UDP_Gal_donor", "donor_epimer", 4),
    ("wrong_UDP_anomer_donor", "donor_epimer", 1),
    ("wrong_extra_glycosylation", "decorate_parent_O3", 3),
    ("wrong_methoxy_decoration", "methylate_core_OH", None),
    ("wrong_namespace", "namespace", None),
    ("wrong_center", "center", None),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(name, value):
    from scripts.operate import write
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                      allow_nan=False) + "\n"
    path = OUT / name
    if path.exists():
        if path.read_text() != text:
            raise ValueError("immutable proposal artifact already exists: " + name)
        return
    write(TASK, str(path.relative_to(ROOT)), text)


def pinned():
    for name, digest in {**INPUTS, RAW: RAW_SHA}.items():
        if sha(ROOT / name) != digest:
            raise ValueError("A7 input SHA drift: " + name)
    return [json.loads(line) for line in
            (ROOT / (A6 + "2_source_qualified_design_supports.jsonl")).read_text().splitlines()]


def preregister():
    pinned()
    for name in [GUARD_PATH, BUILD_PATH]:
        ast.parse((ROOT / name).read_text())
    put("pre_execution_contract.v3.json", dict(
        task=TASK, epoch_id="SS-E02-design", agent_role="A7 Scope Builder",
        timestamp=now(), input_manifest_sha={**INPUTS, RAW: RAW_SHA},
        code_sha256={name: sha(ROOT / name) for name in [GUARD_PATH, BUILD_PATH]},
        status="proposal_pre_registered_before_any_boundary_run",
        scientific_basis="same UGT79B31, two complete source-qualified acceptors; inner C4 epimers, one aglycone",
        finite_parent_domain=["beta-D-Glcp", "beta-D-Galp"],
        invariant="all other parent C stereo, flavonol 3-O glycoside, parent O2, terminal beta-D-Glcp, complete UDPGlc",
        peripheral_domain=["core H", "single neutral aromatic OH"],
        peripheral_domain_evidence="prospective bounded candidate extrapolation; not two-aglycone source validation",
        controls=[dict(control_id=cid, operation=op, parameter=arg,
                       expected_allowed=False, source_assay=False,
                       evidence_class="synthetic_engineering_graph_boundary")
                  for cid, op, arg in CONTROLS],
        acceptance=dict(complete_reference_replay="2/2", mapped_reference_replay="2/2",
                        boundary_controls_minimum=6, boundary_violations=0),
        read_holdout=False, read_model_outcome=False, other5_scientific_sources_read=False,
        HTTP=0, MCTS=0, approval_type="agent_delegated", human_reviewed=False,
        stop_conditions=["any support replay failure", "any unexplained boundary violation",
                         "any input SHA drift", "need to read fresh/model output",
                         "cannot enforce finite complete parent or terminal stereochemistry"],
        forbidden=["G4 registration", "runtime registry mutation", "changing old frozen helpers"]))
    print(json.dumps(dict(preregistered=True, controls=len(CONTROLS),
                          path=str(OUT / "pre_execution_contract.v3.json"))))


def sugar_positions(mol, anomer):
    rings = [ring for ring in mol.GetRingInfo().AtomRings()
             if anomer in ring and len(ring) == 6
             and sum(mol.GetAtomWithIdx(i).GetAtomicNum() == 8 for i in ring) == 1]
    if len(rings) != 1:
        raise ValueError("ambiguous complete hexopyranose")
    ring = set(rings[0])
    oxygen = next(i for i in ring if mol.GetAtomWithIdx(i).GetAtomicNum() == 8)
    pos = {1: anomer, "O5": oxygen}
    previous, current = oxygen, anomer
    for number in range(2, 6):
        choices = [n.GetIdx() for n in mol.GetAtomWithIdx(current).GetNeighbors()
                   if n.GetIdx() in ring and n.GetIdx() != previous]
        if len(choices) != 1:
            raise ValueError("ambiguous sugar carbon traversal")
        previous, current = current, choices[0]
        pos[number] = current
    for number in range(1, 6):
        extras = [n.GetIdx() for n in mol.GetAtomWithIdx(pos[number]).GetNeighbors()
                  if n.GetIdx() not in ring]
        if len(extras) != 1:
            raise ValueError("sugar exocyclic branch absent/ambiguous")
        if number == 5:
            pos[6] = extras[0]
            oxygen6 = [n.GetIdx() for n in mol.GetAtomWithIdx(extras[0]).GetNeighbors()
                       if n.GetAtomicNum() == 8]
            if len(oxygen6) != 1:
                raise ValueError("complete CH2OH missing")
            pos["O6"] = oxygen6[0]
        else:
            pos["O" + str(number)] = extras[0]
    return pos


def sugar_graph(mol, pos):
    keep = {v for k, v in pos.items() if k != "O1"}
    keep.add(pos["O1"])
    return keep


def parent_positions(acceptor):
    found = []
    for atom in acceptor.GetAtoms():
        if atom.GetAtomicNum() != 6 or atom.GetIsAromatic() or not atom.IsInRing():
            continue
        for oxygen in atom.GetNeighbors():
            if (oxygen.GetAtomicNum() == 8 and not oxygen.IsInRing()
                    and any(n.GetIsAromatic() for n in oxygen.GetNeighbors())):
                pos = sugar_positions(acceptor, atom.GetIdx())
                pos["core"] = next(n.GetIdx() for n in oxygen.GetNeighbors()
                                   if n.GetIsAromatic())
                found.append(pos)
    if len(found) != 1:
        raise ValueError("source parent 3-O hexose ambiguous")
    return found[0]


def terminal_positions(product, added):
    candidates = [i for i in added if product.GetAtomWithIdx(i).GetAtomicNum() == 6
                  and any(n.GetIdx() not in added for n in product.GetAtomWithIdx(i).GetNeighbors())]
    if len(candidates) != 1:
        raise ValueError("terminal sugar anomer ambiguous")
    return sugar_positions(product, candidates[0])


def fragment_query(mol, kept, wildcard=()):
    from scripts.task016_p1_build import subset
    value = Chem.Mol(mol)
    for i in wildcard:
        old = value.GetAtomWithIdx(i)
        old.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    text = subset(value, kept)
    for i in wildcard:
        amap = mol.GetAtomWithIdx(i).GetAtomMapNum()
        text = re.sub(r"\[[^\]]*:" + str(amap) + r"\]", "[*:" + str(amap) + "]", text)
    if Chem.MolFromSmarts(text) is None:
        raise ValueError("invalid source-derived query")
    return text


def flip(mol, index):
    atom = mol.GetAtomWithIdx(index)
    if atom.GetChiralTag() == Chem.ChiralType.CHI_UNSPECIFIED:
        raise ValueError("cannot flip absent source stereochemistry")
    atom.InvertChirality()


def build():
    from scripts.task016_p3_build import derive_template_smarts, scoped_smarts
    from scripts.task016_p7_ss_petunia_scope_guard_v1 import (
        CENTER, CORE, apply_template, mapped_reference_path, dispatch_guard,
        canonical, side, unmap, raw_outcomes)
    contract_path = OUT / "pre_execution_contract.v3.json"
    contract = json.loads(contract_path.read_text())
    for name, digest in contract["code_sha256"].items():
        if sha(ROOT / name) != digest:
            raise ValueError("preregistered code drift")
    records = pinned()
    assert len(records) == 2
    assert {r["parent_sugar"] for r in records} == {"beta-D-Galp", "beta-D-Glcp"}
    assert all(r["enzyme"] == "UGT79B31" and r["source_qualified_design_support"]
               and r["source_identity_verified"] and r["dual_full_graph_complete"] for r in records)
    assert len({canonical(Chem.MolFromSmiles(r["acceptor"])) for r in records}) == 2
    exact, parent_queries, instances = [], [], []
    for record in records:
        instance = dict(record, instance_id=record["record_id"], target=record["product"],
                        template_role="development_build",
                        provenance=dict(pmcid=record["source_id"], doi=record["doi"]),
                        required_context=dict(mode="enzymatic", donor_name="UDP-glucose"))
        derived = derive_template_smarts(instance)
        exact.append(dict(instance_id=instance["instance_id"], **derived))
        left, right = derived["smarts"].split(">>")
        target = Chem.MolFromSmiles(left)
        acceptor = Chem.MolFromSmiles(right.split(".", 1)[0])
        apos = parent_positions(acceptor)
        maps = {key: acceptor.GetAtomWithIdx(idx).GetAtomMapNum() for key, idx in apos.items()}
        keep = sugar_graph(acceptor, apos) | {apos["core"]}
        parent_queries.append(dict(
            parent=record["parent_sugar"], smarts=fragment_query(acceptor, keep, [apos["core"]]),
            O2_map=maps["O2"], aglycone_owner_map=maps["core"],
            glycosidic_oxygen_map=maps["O1"], carbon_maps=[maps[i] for i in range(1, 6)],
            source_instance=instance["instance_id"], source_atom_maps={str(k): v for k, v in maps.items()}))
        conserved = {a.GetAtomMapNum() for a in acceptor.GetAtoms()}
        added = {a.GetIdx() for a in target.GetAtoms() if a.GetAtomMapNum() not in conserved}
        tpos = terminal_positions(target, added)
        site = tpos["O1"]
        owner = next(n.GetIdx() for n in target.GetAtomWithIdx(site).GetNeighbors()
                     if n.GetIdx() not in added)
        instance["formation"] = dict(product_atom_indices=dict(
            added=sorted(added), acceptor_site=site, anomeric=tpos[1]))
        instance["_mapped_parent"] = maps
        instance["_mapped_terminal"] = {k: target.GetAtomWithIdx(v).GetAtomMapNum() for k, v in tpos.items()}
        instances.append(instance)
        if record["parent_sugar"] == "beta-D-Glcp":
            seed = instance
            seed_exact = derived
            terminal_query = dict(smarts=fragment_query(target, added | {site, owner}, [owner]),
                                  anomer_map=target.GetAtomWithIdx(tpos[1]).GetAtomMapNum(),
                                  site_map=target.GetAtomWithIdx(site).GetAtomMapNum(),
                                  added_maps=sorted(target.GetAtomWithIdx(i).GetAtomMapNum() for i in added))
    local_before_epimer = scoped_smarts(seed_exact, seed, "rhamnoside_Petunia_O2_UDPGlc")
    c4map = seed["_mapped_parent"][4]
    def relax_c4(text):
        count = 0
        def replacement(match):
            nonlocal count
            if int(match[2]) != c4map:
                return match[0]
            assert "@" in match[1]
            count += 1
            return "[" + match[1].replace("@", "") + ":" + match[2] + "]"
        value = re.sub(r"\[([^\]]*):(\d+)\]", replacement, text)
        assert count == 2, ("parent C4 must relax exactly once on each reaction side", count)
        return value
    scoped = relax_c4(local_before_epimer)
    template = dict(
        template_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1",
        template_role="scope_template", smarts=scoped,
        support_instances=sorted(r["instance_id"] for r in instances),
        allowed_targets=[], donor=canonical(Chem.MolFromSmiles(seed["donor"])),
        category="sugar_sugar_formation", sugar_type="glucose",
        required_context=dict(mode="enzymatic", donor_name="UDP-glucose"),
        validation_status="proposal_pending_A8",
        exact_sha256=hashlib.sha256(seed_exact["smarts"].encode()).hexdigest(),
        scope_sha256=hashlib.sha256(scoped.encode()).hexdigest(),
        scope_transformation=dict(
            pipeline=["derive_template_smarts", "scoped_smarts", "relax_only_parent_C4_on_both_sides"],
            exact_derive_function="scripts.task016_p3_build.derive_template_smarts",
            scoped_function="scripts.task016_p3_build.scoped_smarts",
            helper_source_sha256=sha(ROOT / "scripts/task016_p3_build.py"),
            local_before_parent_C4_relaxation=local_before_epimer,
            parent_C4_map=c4map, all_other_sugar_stereo_retained=True),
        scope=dict(
            namespace="task016_p7", family="SS", center_class=CENTER,
            parent_sugar_domain=["beta-D-Glcp", "beta-D-Galp"], parent_queries=parent_queries,
            terminal_query=terminal_query, transferred_atoms=11, acceptor_cores=[CORE],
            decoration_classes=["single neutral aromatic OH"],
            source_supported_acceptor_count=2, source_supported_aglycone_count=1,
            source_supported_enzyme="UGT79B31", same_source_closure_group="PMC5856881",
            peripheral_OH_domain="prospective candidate extrapolation; not source-validated two-aglycone coverage",
            interpretation="bounded candidate graph scope; novel enzyme activity and conditions unverified"))
    assert template["exact_sha256"] != template["scope_sha256"]
    put("exact_templates.json", exact)
    put("scope_bank.json", [template])
    cleaned = [{k: v for k, v in r.items() if not k.startswith("_") and k not in ("A4_record", "A5_record")}
               for r in instances]
    put("build_supports.json", cleaned)
    replay = []
    for record in records:
        expected = side([Chem.MolFromSmiles(s) for s in record["reference_precursors"]])
        ordinary = apply_template(template, record["product"])
        mapped = mapped_reference_path(template, record["product"])
        replay.append(dict(
            template_id=template["template_id"], instance_id=record["record_id"],
            expected_complete_precursors=expected, dispatcher_outcomes=ordinary, mapped_outcomes=mapped,
            passed=expected in [o["precursors"] for o in ordinary],
            mapped_passed=any(o["precursors"] == expected and o["original_target_maps_preserved"]
                              and o["original_target_maps_unique"] and o["all_output_maps_nonzero"]
                              and o["all_output_maps_unique"] for o in mapped)))
    put("build_replay.json", replay)

    source_product = Chem.MolFromSmiles(seed["target"])
    source_acceptor = Chem.MolFromSmiles(seed["acceptor"])
    apos = parent_positions(source_acceptor)
    acceptor_match = source_product.GetSubstructMatch(source_acceptor, useChirality=True)
    ppos = {k: acceptor_match[v] for k, v in apos.items()}
    added = set(range(source_product.GetNumAtoms())) - set(acceptor_match)
    tpos = terminal_positions(source_product, added)
    base_raw = list(raw_outcomes(template, seed["target"]))
    if not base_raw:
        raise ValueError("scope raw template cannot replay seed")
    base_products = base_raw[0][2]
    boundaries = []
    for cid, operation, argument in CONTROLS:
        target = Chem.Mol(source_product)
        used_template = json.loads(json.dumps(template))
        donor_override = None
        if operation in ("remove_parent_stereo", "flip_parent_stereo", "flip_terminal_stereo"):
            idx = ppos[argument] if "parent" in operation else tpos[argument]
            if operation == "remove_parent_stereo":
                target.GetAtomWithIdx(idx).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
            else:
                flip(target, idx)
        elif operation == "move_link":
            value = Chem.RWMol(target)
            value.RemoveBond(ppos["O2"], tpos[1])
            value.AddBond(ppos["O" + str(argument)], tpos[1], Chem.BondType.SINGLE)
            target = value.GetMol()
        elif operation == "reduce_core":
            # Replace flavonol aromatic C2=C3 bond by a saturated flavanonol
            # core through a graph operation, never a source-derived admission.
            value = Chem.RWMol(target)
            Chem.Kekulize(value, clearAromaticFlags=True)
            core = value.GetSubstructMatch(Chem.MolFromSmarts(
                "O=[C:4]1[C:3]([O])[C:2](-[C]2=[C][C]=[C][C]=[C]2)[O][C]2=[C][C]=[C][C]=[C]12"))
            # If Kekule resonance does not match the SMARTS, use the labelled
            # aromatic source match before kekulization to identify C2/C3.
            q = Chem.MolFromSmarts(CORE)
            labels = {a.GetAtomMapNum(): a.GetIdx() for a in q.GetAtoms()}
            cmatch = target.GetSubstructMatch(q)
            i, j = cmatch[labels[2]], cmatch[labels[3]]
            value.GetBondBetweenAtoms(i, j).SetBondType(Chem.BondType.SINGLE)
            target = value.GetMol()
        elif operation.startswith("donor_"):
            donor_override = Chem.Mol(base_products[1])
            if operation == "donor_drop_UDP":
                query = Chem.MolFromSmarts("O[C@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O")
                # A deliberate truncated donor; complete UDP identity must reject.
                donor_override = Chem.MolFromSmiles("O")
            else:
                glyco_ano = next(a.GetIdx() for a in donor_override.GetAtoms()
                                if a.GetAtomicNum() == 6 and a.IsInRing()
                                and any(n.GetAtomicNum() == 8 and not n.IsInRing()
                                        and any(x.GetAtomicNum() == 15 for x in n.GetNeighbors())
                                        for n in a.GetNeighbors()))
                dpos = sugar_positions(donor_override, glyco_ano)
                flip(donor_override, dpos[argument])
        elif operation == "decorate_parent_O3":
            value = Chem.RWMol(target)
            added_carbon = value.AddAtom(Chem.Atom(6))
            value.AddBond(ppos["O3"], added_carbon, Chem.BondType.SINGLE)
            target = value.GetMol()
        elif operation == "methylate_core_OH":
            oxygen = next(a.GetIdx() for a in target.GetAtoms()
                          if a.GetAtomicNum() == 8 and a.GetDegree() == 1
                          and a.GetBonds()[0].GetBondType() == Chem.BondType.SINGLE
                          and a.GetNeighbors()[0].GetIsAromatic())
            value = Chem.RWMol(target)
            carbon = value.AddAtom(Chem.Atom(6))
            value.AddBond(oxygen, carbon, Chem.BondType.SINGLE)
            target = value.GetMol()
        elif operation == "namespace":
            used_template["scope"]["namespace"] = "task016_p2"
        elif operation == "center":
            used_template["scope"]["center_class"] = "glucoside_O6"
        else:
            raise ValueError("unimplemented preregistered control")
        Chem.SanitizeMol(target)
        target_smi = Chem.MolToSmiles(target, isomericSmiles=True)
        if donor_override is None:
            outputs = apply_template(used_template, target_smi)
            allowed = bool(outputs)
            raw_count = len(list(raw_outcomes(used_template, target_smi)))
        else:
            outputs = []
            allowed = dispatch_guard(used_template, target, (base_products[0], donor_override))
            raw_count = len(base_raw)
        boundaries.append(dict(
            template_id=template["template_id"], control_id=cid,
            operation=operation, expected_allowed=False, target=target_smi,
            precursor_override=(side([base_products[0], donor_override]) if donor_override is not None else None),
            raw_template_outcomes=raw_count, dispatcher_outcomes=outputs,
            observed_allowed=allowed, violated=allowed, source_assay=False,
            evidence_class="synthetic_engineering_graph_boundary"))
    put("boundary_results.json", boundaries)
    summary = dict(
        task=TASK, epoch_id="SS-E02-design", agent_role="A7 Scope Builder", timestamp=now(),
        status="scope_proposal_built_pending_A8_and_root_G2_G3_G4",
        distinct_complete_canonical_acceptors=2, source_supported_aglycones=1,
        source_closure_groups=1, source_qualified_design_supports=2, scopes_proposed=1,
        build_reference_replay_passed=sum(r["passed"] for r in replay), build_reference_replay_total=2,
        mapped_reference_replay_passed=sum(r["mapped_passed"] for r in replay), mapped_reference_replay_total=2,
        preregistered_boundaries=len(CONTROLS), tested_boundaries=len(boundaries),
        boundary_violations=sum(r["violated"] for r in boundaries),
        formal_runtime_connected=False, scope_frozen=False, qualified_by_A8=False,
        full_chemical_round=False, prediction_conditions_verified=False,
        actionable=False, evidence_closed=False, human_reviewed=False,
        independent_chemical_validation=False, physical_assay_salt_hydration_protonation="unknown",
        unknown_physical_species_is_not_new_gate=True, old_api7Glc_UDPApi_stratum_not_merged=True,
        peripheral_OH_extrapolation_is_not_two_aglycone_evidence=True,
        other5_scientific_sources_read=False, read_holdout=False, read_model_outcome=False,
        HTTP=0, MCTS=0, scientific_ABE_cells=0, metrics=None)
    put("summary.json", summary)
    outputs = sorted(p for p in OUT.iterdir() if p.is_file())
    inputs = {**INPUTS, RAW: RAW_SHA}
    inputs.update({name: sha(ROOT / name) for name in [
        GUARD_PATH, BUILD_PATH, "scripts/task016_p3_build.py",
        "scripts/task016_p1_build.py", "flavoretro/glycoside_library_v7.py",
        "flavoretro/glycoside_scope_ss_v7.py"]})
    put("role_A7_manifest.json", dict(
        task=TASK, epoch_id="SS-E02-design", agent_role="A7 Scope Builder", timestamp=now(),
        input_manifest_sha=inputs,
        output_file_sha={str(p.relative_to(ROOT)): sha(p) for p in outputs},
        source_evidence_pointers=[dict(path=RAW, sha256=RAW_SHA,
            location="Table1 K3Gal/K3Glc + footnotes a/b/d; Fig2a/3/S1 original evidence bound in A6")],
        counts=dict(processed=2, passed=2 if all(r["passed"] and r["mapped_passed"] for r in replay) else 0,
                    rejected=0, pending=0 if all(r["passed"] and r["mapped_passed"] for r in replay) else 2),
        boundary_counts=dict(planned=len(CONTROLS), processed=len(boundaries),
                             passed=sum(not r["violated"] for r in boundaries),
                             rejected=sum(r["violated"] for r in boundaries), pending=0),
        errors=["v1 parent sugar locator treated aromatic C3 as anomer; v1 code and failed operation retained; v2 excludes aromatic parent carbons", "v2 serialization failed on mixed int/string source atom-label keys; v3 writes those audit keys as strings"], unprocessed=["Independent A8 review", "Root G2/G3/G4 registration",
                                 "Fresh holdout acquisition", "Runtime integration", "MCTS/transfer"],
        approval_type="agent_delegated", human_reviewed=False, independent_chemical_validation=False,
        read_holdout=False, read_model_outcome=False, other5_scientific_sources_read=False,
        read_scientific_family="Petunia design only", source_saturation=False))
    print(json.dumps(summary, ensure_ascii=False))
    if not all(r["passed"] and r["mapped_passed"] for r in replay):
        raise ValueError("complete reference replay failure; proposal not qualified")
    if any(r["violated"] for r in boundaries):
        raise ValueError("engineering boundary failure; proposal not qualified")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("preregister", "build"):
        raise SystemExit("usage: preregister | build")
    if sys.argv[1] == "preregister":
        preregister()
    else:
        from rdkit import Chem
        build()
