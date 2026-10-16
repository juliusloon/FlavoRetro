#!/usr/bin/env python3
"""TASK-016-P3 G3: build the v4 build-only increment.

Constructs runtime instances for the admitted build reactions that support
the new scope capabilities, derives scoped templates, replays every declared
support instance, and writes the P3 payload files.  The C3 scope covers an
aliphatic C-glycosidic centre that the frozen topology auditor does not
classify (its families are aryl_O/aryl_C/sugar_sugar_O); template derivation
therefore uses the same MCS mapping logic locally with the audit gate
replaced by the explicit v4 structural guard, documented in the template
record."""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from rdkit import Chem, rdBase
from rdkit.Chem import rdFMCS
from flavoretro.reviewed_resources import canonical_side
from flavoretro.open_glycoside_library import structural_formation
from scripts.task016_p1_build import subset
from scripts.task016_p3_sources import write as _reg_write, TASK as _TASK

OUT = ROOT / "outputs/task016-p3/v1"

from rdkit import Chem as _Chem
DONOR_GLC = _Chem.CanonSmiles("O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1")
DONOR_RHA = _Chem.CanonSmiles("O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@@H](C)[C@H](O)[C@@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1")

FLAVONOID_CORES = [
    # flavanone (naringenin/hesperetin skeleton; aromatic substitution flexible)
    "O=C1CC(c2ccccc2)Oc2ccccc12",
    # flavone (apigenin/luteolin/diosmetin/chrysoeriol/acacetin skeleton)
    "O=c1cc(-c2ccccc2)oc2ccccc12",
    # flavonol (kaempferol/quercetin/myricetin skeleton)
    "O=c1c(O)c(-c2ccccc2)oc2ccccc12",
]
RHA_PATTERN = "[C@@H]1O[C@@H](C)[C@H](O)[C@@H](O)[C@H]1O"
GLC_PATTERN = "[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"

C_SUPPORTS = [
    dict(pmcid="PMC9563126", enzyme="MhCGT", context="enzymatic",
         acceptor="O=C1CC(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
         target="O=C1C([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)C(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
         donor_name="UDP-glucose", donor=DONOR_GLC, reaction="P3R-C01",
         identification="source NMR-assigned 2-hydroxyflavanone C-glycoside; single C-C forming step retained (dehydration excluded)",
         conditions="recombinant enzyme, UDP-Glc"),
    dict(pmcid="PMC6036675", enzyme="CjCGT1", context="enzymatic",
         acceptor="O=C1CC(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
         target="O=C1C([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)C(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
         donor_name="UDP-glucose", donor=DONOR_GLC, reaction="P3R-C01",
         identification="in vivo yeast de novo production, NMR-assigned products; same covalent step",
         conditions="yeast in vivo, endogenous UDP-Glc"),
    dict(pmcid="PMC9563126", enzyme="MhCGT", context="enzymatic",
         acceptor="O=C1CC(O)(c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c12",
         target="O=C1C([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)C(O)(c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c12",
         donor_name="UDP-glucose", donor=DONOR_GLC, reaction="P3R-C02",
         identification="source NMR-assigned 2-hydroxyflavanone C-glycoside cascade",
         conditions="recombinant enzyme, UDP-Glc"),
]

SS2_SUPPORTS = [
    dict(pmcid="PMC13084081", enzyme="MpRhaT", context="enzymatic",
         acceptor="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
         target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@H]3O)cc(O)c12",
         donor_name="UDP-alpha-L-rhamnose", donor=DONOR_RHA, reaction="P3R-SS01",
         identification="source standard/NMR-assigned neohesperidoside product",
         conditions="purified enzyme, UDP-Rha"),
    dict(pmcid="PMC13084081", enzyme="MpRhaT", context="enzymatic",
         acceptor="O=C1C[C@@H](c2ccc(O)c(O)c2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
         target="O=C1C[C@@H](c2ccc(O)c(O)c2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@H]3O)cc(O)c12",
         donor_name="UDP-alpha-L-rhamnose", donor=DONOR_RHA, reaction="P3R-SS02",
         identification="source standard/NMR-assigned neohesperidoside product",
         conditions="purified enzyme, UDP-Rha"),
]

SS6_SUPPORTS = [
    dict(pmcid="PMC13084081", enzyme="MpRhaT", context="enzymatic",
         acceptor="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
         target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
         donor_name="UDP-alpha-L-rhamnose", donor=DONOR_RHA, reaction="P3R-SS03",
         identification="source standard/NMR-assigned rutinoside product",
         conditions="purified enzyme, UDP-Rha"),
    dict(pmcid="PMC9706480", enzyme="Cm1,6RhaT", context="enzymatic",
         acceptor="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
         target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
         donor_name="UDP-beta-L-rhamnose (commercial)", donor=DONOR_RHA, reaction="P3R-SS03",
         identification="source LC-MS/MS against named rutinoside reference standard; identity upgraded at admission",
         conditions="purified enzyme, UDP-Rha"),
]


def iid(pmcid, enzyme, target):
    return f"{pmcid}:{enzyme}:{hashlib.sha256(target.encode()).hexdigest()[:24]}"


def build_instances():
    instances = []
    for group, supports, category, sugar in (
            ("C3-hydroxyflavanone-glucosylation", C_SUPPORTS, "C_formation", "glucose"),
            ("SS-rhamnoside-O2", SS2_SUPPORTS, "sugar_sugar_formation", "rhamnose"),
            ("SS-rhamnoside-O6", SS6_SUPPORTS, "sugar_sugar_formation", "rhamnose")):
        for s in supports:
            for key in ("acceptor", "target", "donor"):
                if Chem.MolFromSmiles(s[key]) is None:
                    raise ValueError(f"unparseable {key} for {s['pmcid']}")
            instances.append(dict(
                instance_id=iid(s["pmcid"], s["enzyme"], s["target"]),
                template_role="development_build",
                P3_role="development_build", development_exposed=True,
                reaction_id=s["reaction"], scope_group=group,
                acceptor=s["acceptor"], donor=s["donor"], target=s["target"],
                actual_assay_group=f"{s['pmcid']}:{s['enzyme']}",
                required_context=dict(mode=s["context"], donor_name=s["donor_name"]),
                reference_precursors=[s["acceptor"], s["donor"]],
                identification=s["identification"], conditions=s["conditions"],
                provenance=dict(pmcid=s["pmcid"], review_type="agent_delegated",
                                locators="bound in reaction_records.jsonl supporting_candidate_uids"),
                human_reviewed=False, prediction_conditions_verified=False,
                source_yield=dict(status="not numerically extracted here; source values retained in reaction_records"),
                category=category, sugar_type=sugar))
    return instances


def derive_template_smarts(instance):
    """Mirror flavoretro.glycoside_expansion.extract_template mapping without
    the topology.audit gate (documented in the template record)."""
    acceptor = Chem.MolFromSmiles(instance["acceptor"])
    donor = Chem.MolFromSmiles(instance["donor"])
    product = Chem.MolFromSmiles(instance["target"])
    for atom in product.GetAtoms():
        atom.SetAtomMapNum(atom.GetIdx() + 1)
    mcs = rdFMCS.FindMCS([acceptor, product], timeout=5, ringMatchesRingOnly=True,
                         completeRingsOnly=True, bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms != acceptor.GetNumAtoms():
        raise ValueError("acceptor not fully conserved")
    query = Chem.MolFromSmarts(mcs.smartsString)
    am, pm = acceptor.GetSubstructMatch(query), product.GetSubstructMatch(query)
    for aidx, pidx in zip(am, pm):
        acceptor.GetAtomWithIdx(aidx).SetAtomMapNum(pidx + 1)
    transferred = [i for i in range(product.GetNumAtoms()) if i not in pm]
    sugar = Chem.RWMol()
    positions = {i: sugar.AddAtom(Chem.AtomFromSmarts(f"[#{product.GetAtomWithIdx(i).GetAtomicNum()}:{i+1}]")) for i in transferred}
    for bond in product.GetBonds():
        a, b = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        if a in positions and b in positions:
            sugar.AddBond(positions[a], positions[b], bond.GetBondType())
    matches = donor.GetSubstructMatches(sugar.GetMol(), useChirality=False)
    if len(matches) != 1:
        raise ValueError("sugar-to-donor mapping absent or ambiguous")
    for fidx, didx in enumerate(matches[0]):
        donor.GetAtomWithIdx(didx).SetAtomMapNum(sugar.GetMol().GetAtomWithIdx(fidx).GetAtomMapNum())
    links = [b for b in product.GetBonds() if (b.GetBeginAtomIdx() in pm) != (b.GetEndAtomIdx() in pm)]
    if len(links) != 1:
        raise ValueError("not a single attachment")
    left = Chem.MolToSmiles(product, isomericSmiles=True)
    right = Chem.MolToSmiles(acceptor, isomericSmiles=True) + "." + Chem.MolToSmiles(donor, isomericSmiles=True)
    right = re.sub(r"\[([^\]]*?):(\d+)\]",
                   lambda m: "[" + m[1] + ("+0" if "+" not in m[1] and "-" not in m[1] else "") + ":" + m[2] + "]",
                   right)
    return dict(smarts=left + ">>" + right,
                mapping=dict(tool="RDKit MCS + unique transferred-sugar graph match (local P3 derivation)",
                             rdkit=rdBase.rdkitVersion, status="machine_inferred",
                             transferred_atoms=len(transferred), conserved_acceptor_atoms=len(pm)),
                center=dict(acceptor_site=product.GetAtomWithIdx(links[0].GetOtherAtomIdx(
                    links[0].GetBeginAtomIdx() if links[0].GetBeginAtomIdx() not in pm else links[0].GetEndAtomIdx())).GetIdx()))


def scoped_smarts(t, seed, center):
    left, right = t["smarts"].split(">>")
    product = Chem.MolFromSmiles(left)
    acceptor_smiles, donor = right.split(".", 1)
    acceptor = Chem.MolFromSmiles(acceptor_smiles)
    idx = seed["formation"]["product_atom_indices"]
    kept = set(idx["added"]) | {idx["acceptor_site"]}
    site = product.GetAtomWithIdx(idx["acceptor_site"])
    owner = next(a for a in site.GetNeighbors() if a.GetIdx() != idx["anomeric"])
    kept.add(owner.GetIdx())
    if center.startswith("rhamnoside"):
        # full glucosyl ring + every exocyclic substituent so that no kept
        # chiral atom loses a neighbour (a dropped neighbour would distort the
        # pattern's H count or chirality); the frontier is the aromatic owner
        # beyond the glycosidic O, which stays a flexible SMARTS atom.
        def glycosyl_ring():
            for atom in [owner] + [n for n in owner.GetNeighbors() if n.IsInRing()]:
                for ring in product.GetRingInfo().AtomRings():
                    if atom.GetIdx() in ring and len(ring) == 6 \
                            and sum(product.GetAtomWithIdx(i).GetAtomicNum() == 8 for i in ring) == 1:
                        return ring
            raise ValueError("glycosyl ring not found")
        sugar_ring = glycosyl_ring()
        kept |= set(sugar_ring)
        frontier = set()
        for i in sugar_ring:
            for n in product.GetAtomWithIdx(i).GetNeighbors():
                if n.GetIdx() in idx["added"] or n.GetIdx() in sugar_ring:
                    continue
                frontier.add(n.GetIdx())
        # bridge oxygen -> aglycone owner (O1'' -> aromatic c)
        for i in list(frontier):
            a = product.GetAtomWithIdx(i)
            if a.GetAtomicNum() == 8 and not a.IsInRing():
                for n in a.GetNeighbors():
                    if n.GetIdx() not in idx["added"] and n.GetIdx() not in sugar_ring:
                        frontier.add(n.GetIdx())
        kept |= frontier
    kept.add(idx["anomeric"])
    maps = {product.GetAtomWithIdx(i).GetAtomMapNum() for i in kept if i not in idx["added"]}
    return subset(product, kept) + ">>" + subset(acceptor, {a.GetIdx() for a in acceptor.GetAtoms() if a.GetAtomMapNum() in maps}) + "." + donor


def local_C3_formation(instance):
    """Formation record for the aliphatic C3 centre that the frozen
    structural_formation does not classify.  Mirrors its MCS linkage logic and
    adds explicit centre-context checks."""
    acceptor = Chem.MolFromSmiles(instance["acceptor"])
    product = Chem.MolFromSmiles(instance["target"])
    mcs = rdFMCS.FindMCS([acceptor, product], timeout=5, ringMatchesRingOnly=True,
                         completeRingsOnly=True, bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms != acceptor.GetNumAtoms():
        raise ValueError("acceptor not fully conserved")
    query = Chem.MolFromSmarts(mcs.smartsString)
    conserved = product.GetSubstructMatch(query, useChirality=True)
    if not conserved or not product.HasSubstructMatch(acceptor, useChirality=True):
        raise ValueError("acceptor not fully conserved including stereochemistry")
    inside = set(conserved)
    added = sorted(set(range(product.GetNumAtoms())) - inside)
    links = [b for b in product.GetBonds() if (b.GetBeginAtomIdx() in inside) != (b.GetEndAtomIdx() in inside)]
    if len(links) != 1 or not added:
        raise ValueError("not a single conserved linkage")
    b = links[0]
    anomeric = b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in added else b.GetEndAtomIdx()
    site = b.GetOtherAtomIdx(anomeric)
    siteatom = product.GetAtomWithIdx(site)
    if siteatom.GetAtomicNum() != 6 or siteatom.GetIsAromatic():
        raise ValueError("site is not an aliphatic carbon")
    neighbours = [n for n in siteatom.GetNeighbors() if n.GetIdx() != anomeric]
    # explicit centre context: C3 bonded to C4(=O) and C2(OH)(aryl)O within a flavanone-2-ol
    has_carbonyl = any(n.GetAtomicNum() == 6 and any(b2.GetBondType() == Chem.BondType.DOUBLE and b2.GetOtherAtom(n).GetAtomicNum() == 8 for b2 in n.GetBonds()) for n in neighbours)
    has_flavanone_OH = any(n.GetAtomicNum() == 6 and any(x.GetAtomicNum() == 8 and x.GetTotalNumHs() + x.GetNumImplicitHs() >= 1 and x.GetFormalCharge() == 0 and x.GetDegree() == 1 for x in n.GetNeighbors()) and any(x.GetIsAromatic() for x in n.GetNeighbors()) and any(x.GetAtomicNum() == 8 and x.IsInRing() for x in n.GetNeighbors()) for n in neighbours)
    if not (has_carbonyl and has_flavanone_OH and len(neighbours) == 2):
        raise ValueError("centre is not a 2-hydroxyflavanone C3")
    return dict(family="C_formation", product_atom_indices=dict(acceptor_site=site, anomeric=anomeric, added=added),
                bond_type=str(b.GetBondType()), acceptor_atoms=acceptor.GetNumAtoms(), added_atoms=len(added),
                direction="forward formation", equivalent_match_count=1,
                validation="local P3 derivation: aliphatic C3 of a 2-hydroxyflavanone; frozen structural_formation does not classify this centre")


def local_SS_formation(instance):
    """Formation record for rhamnosidic sites.  The frozen
    structural_formation classifies only ring-carbon sites (1->2/3/4); a 1->6
    site's acceptor neighbour is the exocyclic C6 of the glucose, which the
    frozen code leaves 'unresolved_O_formation'.  This local derivation keeps
    the same linkage logic and explicitly admits the exocyclic CH2 case."""
    acceptor = Chem.MolFromSmiles(instance["acceptor"])
    donor = Chem.MolFromSmiles(instance["donor"])
    product = Chem.MolFromSmiles(instance["target"])
    mcs = rdFMCS.FindMCS([acceptor, product], timeout=5, ringMatchesRingOnly=True,
                         completeRingsOnly=True, bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms != acceptor.GetNumAtoms():
        raise ValueError("acceptor not fully conserved")
    query = Chem.MolFromSmarts(mcs.smartsString)
    conserved = product.GetSubstructMatch(query, useChirality=True)
    if not conserved or not product.HasSubstructMatch(acceptor, useChirality=True):
        raise ValueError("acceptor not fully conserved including stereochemistry")
    inside = set(conserved)
    added = sorted(set(range(product.GetNumAtoms())) - inside)
    links = [b for b in product.GetBonds() if (b.GetBeginAtomIdx() in inside) != (b.GetEndAtomIdx() in inside)]
    if len(links) != 1 or not added:
        raise ValueError("not a single conserved linkage")
    b = links[0]
    anomeric = b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in added else b.GetEndAtomIdx()
    site = b.GetOtherAtomIdx(anomeric)
    siteatom = product.GetAtomWithIdx(site)
    if siteatom.GetAtomicNum() != 8:
        raise ValueError("SS site is not oxygen")
    others = [x for x in siteatom.GetNeighbors() if x.GetIdx() != anomeric]
    if len(others) != 1:
        raise ValueError("SS site not a bridging oxygen")
    other = others[0]
    ring_carbon = other.IsInRing() and other.GetAtomicNum() == 6
    exocyclic = (not other.IsInRing() and other.GetAtomicNum() == 6
                 and other.GetDegree() == 2
                 and any(n.IsInRing() and n.GetAtomicNum() == 6 for n in other.GetNeighbors()))
    if not (ring_carbon or exocyclic):
        raise ValueError("SS site is neither a ring carbon nor an exocyclic sugar CH2")
    frag_map = {}
    glycan = Chem.PathToSubmol(product, [bb.GetIdx() for bb in product.GetBonds()
                                         if bb.GetBeginAtomIdx() in added and bb.GetEndAtomIdx() in added],
                               atomMap=frag_map)
    glycan.GetAtomWithIdx(frag_map[anomeric]).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    if not donor.HasSubstructMatch(glycan, useChirality=True):
        raise ValueError("transferred glycan stereo absent from donor")
    mode = "ring_carbon" if ring_carbon else "exocyclic_C6 (1->6)"
    return dict(family="sugar_sugar_formation",
                product_atom_indices=dict(acceptor_site=site, anomeric=anomeric, added=added),
                bond_type=str(b.GetBondType()), acceptor_atoms=acceptor.GetNumAtoms(),
                added_atoms=len(added), direction="forward formation", equivalent_match_count=1,
                validation=f"local P3 derivation: sugar-sugar O site ({mode}); ring-carbon case agrees with the frozen structural_formation classification",
                linkage_mode=mode)


def main():
    from rdkit.Chem import rdChemReactions
    instances = build_instances()
    from flavoretro.reviewed_resources import reaction_signature as _rsig
    from flavoretro.open_glycoside_library import normalize_species as _nspec
    for inst in instances:
        inst["reference_signature"] = _rsig(
            [canonical_side(inst["reference_precursors"])],
            [_nspec(inst["target"])["normalized"]])
    for inst in instances:
        if inst["scope_group"] == "C3-hydroxyflavanone-glucosylation":
            inst["formation"] = local_C3_formation(inst)
        else:
            inst["formation"] = local_SS_formation(inst)
        if inst["formation"]["family"] != inst["category"]:
            raise ValueError(f"formation family mismatch: {inst['instance_id']} {inst['formation']['family']}")
    groups = {}
    for inst in instances:
        groups.setdefault(inst["scope_group"], []).append(inst)

    CENTER = {"C3-hydroxyflavanone-glucosylation": "C_hydroxyflavanone_C3",
              "SS-rhamnoside-O2": "rhamnoside_glucoside_O2",
              "SS-rhamnoside-O6": "rhamnoside_glucoside_O6"}
    templates = []
    for group, members in groups.items():
        seed = members[0]
        exact = derive_template_smarts(seed)
        seed["formation"] = exact.get("formation") or seed["formation"]
        smarts = scoped_smarts(dict(smarts=exact["smarts"]), seed, CENTER[group])
        t = dict(
            template_id="p3-scope:" + hashlib.sha256((smarts + CENTER[group]).encode()).hexdigest()[:20],
            template_role="scope_template", smarts=smarts, allowed_targets=[],
            required_context=dict(mode="enzymatic", donor_name=seed["required_context"]["donor_name"]),
            donor=seed["donor"], category=seed["category"], sugar_type=seed["sugar_type"],
            scope=dict(
                namespace="task016_p3", center_class=CENTER[group],
                parent_glycan_patterns=[GLC_PATTERN] if group.startswith("SS") else [],
                acceptor_cores=FLAVONOID_CORES,
                interpretation="build-source structural candidate range; new activity, enzyme, site selectivity, conditions and yield unverified",
                enzyme_context="source UDP candidate class; seed gene not copied",
                declaration=("source parent sugar and connection preserved; transferred-sugar stereo explicit in SMARTS; "
                             "flavonoid aglycone class guarded by core patterns; aliphatic C3 centre guarded structurally in the v4 module "
                             "because the frozen topology auditor does not classify it")),
            derivation=exact["mapping"], support_instances=[m["instance_id"] for m in members],
            validation_status="pending")
        templates.append((t, members))

    checks = []
    for t, members in templates:
        rxn = rdChemReactions.ReactionFromSmarts(t["smarts"])
        if rxn is None:
            checks.append(dict(template_id=t["template_id"], kind="smarts_parse", passed=False))
            continue
        checks.append(dict(template_id=t["template_id"], kind="smarts_parse", passed=True))
        for m in members:
            outcomes = []
            for index, mols in enumerate(rxn.RunReactants([Chem.MolFromSmiles(m["target"])])):
                try:
                    for x in mols:
                        Chem.SanitizeMol(x)
                    precursors = canonical_side([Chem.MolToSmiles(x, isomericSmiles=True) for x in mols])
                    if precursors:
                        outcomes.append(precursors)
                except (ValueError, RuntimeError):
                    continue
            expected = canonical_side(m["reference_precursors"])
            checks.append(dict(kind="support_replay", template_id=t["template_id"],
                               instance_id=m["instance_id"],
                               passed=expected in outcomes,
                               expected=expected, outcomes=outcomes))
    failed = [c for c in checks if not c["passed"]]
    for c in checks:
        print(c["kind"], c.get("template_id", "")[:24], c.get("instance_id", ""), "PASS" if c["passed"] else "FAIL")
        if not c["passed"] and c["kind"] == "support_replay":
            print("   expected:", c["expected"])
            print("   outcomes:", c["outcomes"])

    # ------------------------------------------------ pre-registered boundaries
    # each boundary target/acceptor pair must NOT replay to the reference
    # precursors through the scoped template (violations must be 0)
    GLC_ALPHA = "[C@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O"
    BOUNDARIES = {
        "C_hydroxyflavanone_C3": [
            dict(name="wrong_anomeric_glucose",
                 target="O=C1C([C@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)C(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
                 expect="no replay: transferred glucose anomeric stereo distorted"),
            dict(name="no_2_hydroxyl_context",
                 target="O=C1C([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)CC(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
                 expect="no replay: centre lacks the 2-hydroxyflavanone context"),
            dict(name="direct_flavone_carbon",
                 target="O=c1c([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
                 expect="no replay: aromatic C-glycosylated flavone is not the aliphatic C3 centre"),
            dict(name="wrong_transferred_sugar",
                 target="O=C1C([C@@H]2O[C@@H](CO)[C@H](O)[C@H](O)[C@H]2O)C(O)(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
                 expect="no replay: transferred-sugar stereo in SMARTS does not match"),
        ],
        "rhamnoside_glucoside_O2": [
            dict(name="wrong_linkage_1to4",
                 target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@H](O[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
                 expect="no replay: 1->4 rhamnoside is outside the declared 1->2 centre"),
            dict(name="galactoside_parent",
                 target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@H]3O)cc(O)c12",
                 expect="no replay: parent glycan pattern is the declared beta-D-glucosyl only"),
            dict(name="non_flavonoid_aglycone",
                 target="O=C1OC2=CC(O)=CC(O)=C2C=C1O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@H]3O",
                 expect="no replay: coumarin aglycone fails the flavonoid core guard"),
            dict(name="transferred_glucose_not_rhamnose",
                 target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O[C@@H]4O[C@H](CO)[C@@H](O)[C@H](O)[C@H]4O)[C@H]3O)cc(O)c12",
                 expect="no replay: transferred sugar is glucose, SMARTS requires L-rhamnose"),
        ],
        "rhamnoside_glucoside_O6": [
            dict(name="wrong_linkage_1to2",
                 target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO)[C@@H](O)[C@H](O[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@H]3O)cc(O)c12",
                 expect="no replay: 1->2 rhamnoside is the O2 template's centre, not O6"),
            dict(name="galactoside_parent",
                 target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@H]3O[C@H](CO[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
                 expect="no replay: parent glycan pattern is the declared beta-D-glucosyl only"),
            dict(name="non_flavonoid_aglycone",
                 target="O=C1OC2=CC(O)=CC=C2C=C1O[C@@H]3O[C@H](CO[C@@H]4O[C@@H](C)[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O",
                 expect="no replay: coumarin aglycone fails the flavonoid core guard"),
            dict(name="xylose_transferred",
                 target="O=C1C[C@@H](c2ccc(O)cc2)Oc2cc(O[C@@H]3O[C@H](CO[C@H]4O[C@@H](CO)[C@H](O)[C@@H](O)[C@H]4O)[C@@H](O)[C@H](O)[C@H]3O)cc(O)c12",
                 expect="no replay: transferred sugar is xylose, SMARTS requires L-rhamnose"),
        ],
    }
    boundary_checks = []
    from flavoretro import glycoside_library_v4 as _v4
    for t, members in templates:
        center = t["scope"]["center_class"]
        for b in BOUNDARIES[center]:
            outcomes = _v4.apply_template(t, b["target"])
            hit = bool(outcomes)
            boundary_checks.append(dict(template_id=t["template_id"], center=center,
                                        name=b["name"], matched=hit,
                                        violation=hit, expect=b["expect"]))
    violations = [b for b in boundary_checks if b["violation"]]
    for b in boundary_checks:
        print("boundary", b["center"], b["name"], "OK" if not b["violation"] else "VIOLATION")

    print(f"templates {len(templates)}; checks {len(checks)-len(failed)}/{len(checks)} passed; "
          f"boundaries {len(boundary_checks)-len(violations)}/{len(boundary_checks)} clean")
    if failed or violations:
        return 1

    # ------------------------------------------------------------- payload out
    for t, members in templates:
        t["validation_status"] = "source_reconstruction_passed"
    def _inst_out(inst):
        out = {k: v for k, v in inst.items() if k != "formation"}
        out["formation"] = {k: v for k, v in inst["formation"].items() if k != "product_atom_indices"}
        return out
    payload_templates = [t for t, _ in templates]
    def _jl(records):
        return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)
    _reg_write(_TASK, "outputs/task016-p3/v1/templates.jsonl", _jl(payload_templates))
    _reg_write(_TASK, "outputs/task016-p3/v1/runtime_instances.jsonl", _jl(_inst_out(i) for i in instances))

    import flavoretro.resources as res
    files_sha = {name: res.sha(OUT / name) for name in ("templates.jsonl", "runtime_instances.jsonl")}
    manifest = dict(
        schema_version=2, version="task016-p3-qualified-v4",
        claim=("P3 build-only increment: 3 scoped templates (C hydroxyflavanone C3-glucosylation; "
               "rhamnoside 1->2 and 1->6 on flavonoid glucosides) with 7 build runtime instances; "
               "chained onto the qualified P2/v2 v3 payload"),
        files_sha256=files_sha,
        policy=dict(default_enabled=False, domain_cap_per_molecule=4, generic_protection=3,
                    prior=0.2, weight=1.0),
        raw_dependencies_sha256={},
        rdkit=rdBase.rdkitVersion,
        review_binding=json.load(open(ROOT / "outputs/task016-p2/v2/template_source_manifest.json"))["review_binding"],
        chain=dict(manifest="outputs/task016-p2/v2/template_source_manifest.json",
                   manifest_sha256=json.load(open(ROOT / "configs/glycoside-library-v3.json"))["manifest_sha256"]),
        boundaries=boundary_checks,
        support_replay=checks,
    )
    _reg_write(_TASK, "outputs/task016-p3/v1/template_source_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    import os as _os
    _replay = _os.environ.get("FLAVORETRO_P3_REPLAY_DIR")
    if _replay:
        import pathlib as _p
        _rd = _p.Path(_replay); _rd.mkdir(parents=True, exist_ok=True)
        (_rd / "templates.jsonl").write_text(_jl(payload_templates))
        (_rd / "runtime_instances.jsonl").write_text(_jl(_inst_out(i) for i in instances))
        (_rd / "template_source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        print("replay payload written to", _rd)
        return 0
    print("payload written:",
          OUT / "templates.jsonl", len(payload_templates),
          OUT / "runtime_instances.jsonl", len(instances),
          OUT / "template_source_manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
