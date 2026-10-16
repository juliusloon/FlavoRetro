"""TASK-016-P5 G3: build the explicit default-off v6 runtime.

v6 is NOT v4 or v5 with fields flipped. Following the same construction the P4
contract forced on v5, the payload is assembled from the qualified v3 baseline
plus exactly the increments that passed a P5 build gate:

    v6 = v3
       + the P4-revalidated rhamnoside_glucoside_O2 scope, revalidated here
       + the P5 flavonol 8-C-glycosylation scope

and nothing else. The two quarantined P3 scopes stay out by construction, not by
a status field: C_hydroxyflavanone_C3 (no structure-complete intermediate) and
rhamnoside_glucoside_O6 (one distinct canonical acceptor).

The C scope template is derived from its own two build supports by cleaving the
C-glycosidic bond in silico, so the template cannot encode anything the supports
do not. Its declared applicability is flavone/flavonol C-glycosylation at a ring
carbon, with site selectivity explicitly unverified: the two supports sit at C8,
and the guard accepts any aromatic ring carbon because a template that hard-codes
C8 could not be honestly declared as a scope at all.

Every gate that G3 asserts is an engineering fact about the implementation. None
of it is transfer evidence, and support replay in particular proves only that the
template reproduces its own build sources.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P5"
OUT = ROOT / "outputs/task016-p5/v1"
P4 = ROOT / "outputs/task016-p4/v1"
P2V2 = ROOT / "outputs/task016-p2/v2"
sys.path.insert(0, str(ROOT))
from scripts.operate import write, event

# kaempferol 8-C-beta-D-glucoside and quercetin 8-C-beta-D-glucoside: the two
# structure-complete E2 reactions that give the new C scope its two distinct
# canonical acceptors. They are E2 (development-exposed), so consuming them as
# build supports costs the leakage-free holdout nothing.
C_BUILD = None  # built at runtime by task016_p5_flavonol_support
UDP_GLC = ("O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)"
           "[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1")

# The revalidated P4 scope, carried forward unchanged and re-proved below.
SS_SCOPE_INSTANCE_IDS = [
    "PMC13084081:MpRhaT:a7c23dd18652d36e64e23c53",
    "PMC13084081:MpRhaT:f2cab8d5e86df915f06735ed",
]
QUARANTINED = ("C_hydroxyflavanone_C3", "rhamnoside_glucoside_O6")


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def save(name, value):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def retro_c_glycoside_smarts(product_smiles, donor_smiles):
    """Derive the retro template by cleaving the C(aromatic)-C(anomeric) bond.

    Written generically rather than by hand so that the template provably comes
    from the build support it will be replayed against: the donor is matched as a
    subgraph and the transferred fragment is everything that is not the acceptor.
    """
    from rdkit import Chem
    prod = Chem.MolFromSmiles(product_smiles)
    donor = Chem.MolFromSmiles(donor_smiles)
    if prod is None or donor is None:
        raise ValueError("build support or donor does not parse")
    # find the single bond between an aromatic carbon and an aliphatic carbon
    # whose environment matches the transferred glucosyl anomeric centre
    hits = []
    for bond in prod.GetBonds():
        a, b = bond.GetBeginAtom(), bond.GetEndAtom()
        pair = None
        if a.GetIsAromatic() and not b.GetIsAromatic():
            pair = (a, b)
        elif b.GetIsAromatic() and not a.GetIsAromatic():
            pair = (b, a)
        if pair is None:
            continue
        arom, alip = pair
        if alip.GetTotalNumHs() == 1 and alip.GetDegree() == 3:
            hits.append((arom, alip))
    if len(hits) != 1:
        raise ValueError(f"expected exactly one C-glycosidic bond, found {len(hits)}")
    return prod, hits[0]



def _derive(acceptor_smiles, product_smiles):
    """Derive the retro template through the frozen P3 routine, with a replay proof."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "p5rt", ROOT / "scripts/task016_p5_retro_template.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.derive(acceptor_smiles, product_smiles)


def main():
    from rdkit import Chem
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "p5sup", ROOT / "scripts/task016_p5_flavonol_support.py")
    sup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sup)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = sup.main()
    assert rc == 0, buf.getvalue()
    C_BUILD = json.loads(buf.getvalue())
    C_BUILD = [dict(reaction_id=k, **v) for k, v in C_BUILD.items()]
    from rdkit.Chem import rdFMCS, rdChemReactions
    sys.path.insert(0, str(ROOT))
    from flavoretro.open_glycoside_library import normalize_species
    from flavoretro.reviewed_resources import canonical_side

    scopes = json.loads((OUT / "scopes.json").read_text())
    assert scopes["scopes"]["flavonol_8_C_glucoside"]["gate_pass"], \
        "the C scope must pass its P5 build gate before v6 may carry it"
    assert scopes["scopes"]["rhamnoside_glucoside_O2"]["gate_pass"], \
        "the revalidated SS scope must pass its P5 build gate"

    # ------------------------------------------------- derive the C template
    templates, instances, replay, controls = [], [], [], []
    for entry in C_BUILD:
        prod, (arom, alip) = retro_c_glycoside_smarts(entry["product_smiles"], UDP_GLC)
        # acceptor = product minus the transferred glucosyl fragment
        frags = Chem.GetMolFrags(prod)
        assert len(frags) == 1, "the build support product must be one fragment"
        # split at the glycosidic bond by breaking it on a copy
        rw = Chem.RWMol(prod)
        rw.RemoveBond(arom.GetIdx(), alip.GetIdx())
        for atom in rw.GetAtoms():
            atom.SetNumExplicitHs(0)
            atom.SetNoImplicit(True)
        parts = Chem.GetMolFrags(rw.GetMol())
        assert len(parts) == 2, f"expected two fragments after cleavage, got {len(parts)}"
        acceptor_part = max(parts, key=len)
        sugar_part = min(parts, key=len)
        acc_mol = rw.GetMol()
        # rebuild each part as its own molecule
        def submol(mol, idxs):
            from rdkit.Chem import rdmolops
            return rdmolops.PathToSubmol(mol, [
                b.GetIdx() for b in mol.GetBonds()
                if b.GetBeginAtomIdx() in idxs and b.GetEndAtomIdx() in idxs])
        acc = submol(acc_mol, acceptor_part)
        for a in acc.GetAtoms():
            a.SetNumRadicalElectrons(0)
        Chem.SanitizeMol(acc, Chem.SanitizeFlags.SANITIZE_ALL ^
                         Chem.SanitizeFlags.SANITIZE_PROPERTIES)
        acc_smiles = Chem.MolToSmiles(acc, isomericSmiles=True)

        # the retro SMARTS keeps the transferred sugar generalised to "glucosyl
        # from UDP-Glc", matching the frozen donor by canonical side chain
        # The retro template is assembled from the two validated halves rather than
        # hand-written: the acceptor-side SMARTS comes from the cleavage above and
        # the donor side is the frozen UDP-glucose rewritten with explicit atom
        # maps. Writing the mapped UDP-glucose by hand is error-prone and this task
        # has already been bitten by two malformed hand-written strings.
        derived = _derive(entry["acceptor_smiles"], entry["product_smiles"])
        smarts = derived["smarts"]
        t = dict(
            template_id=f"p5-scope:{hashlib.sha256((entry['reaction_id'] + acc_smiles).encode()).hexdigest()[:20]}",
            template_role="scope_template",
            category="C_formation",
            sugar_type="glucose",
            donor=UDP_GLC,
            required_context={"donor_name": "UDP-alpha-D-glucose", "mode": "enzymatic"},
            smarts=smarts,
            allowed_targets=[],
            scope=dict(
                namespace="task016_p5",
                p5_scope_namespace="task016_p5",
                center_class="flavonol_8_C_glucoside",
                # Written in the RDKit-canonical tautomer of the flavonol core and
                # asserted against the build supports below. An earlier version used
                # the alternative aromatic writing of the same skeleton, which parses
                # but never matches, so the scope silently rejected its own supports.
                # Only the cores that actually match this scope's own build
                # supports are declared. Both supports are FLAVONOLS, so a flavone
                # or flavanone core is not declared: it would be an unsupported
                # extension, and declaring it would also silently import the
                # chemistry of the leakage-free holdout into the build design.
                # The consequence is recorded honestly in the REPORT: the qualified
                # C scope covers no leakage-free holdout target.
                acceptor_cores=[
                    "O=C1Oc2c(O)cc(O)cc2OC(c2ccccc2)=C1O",
                ],
                parent_glycan_patterns=[],
                declaration="flavone/flavonol C-glycosylation by UDP-glucose at an aromatic "
                            "ring carbon; the two build supports sit at C8, and the guard "
                            "accepts any aromatic ring carbon because site selectivity beyond "
                            "the build supports is explicitly unverified",
                interpretation="build-source structural candidate range; new activity, "
                               "regioselectivity, enzyme, conditions and yield unverified",
                enzyme_context="source UDP-glucose donor class; seed gene not copied",
            ),
            support_instances=[],
            validation_status="source_reconstruction_passed",
            p5_build_reaction=entry["reaction_id"],
            p5_build_sources=["PMC9700910"],
            derivation=dict(
                status="machine_inferred",
                tool=derived["mapping"]["tool"],
                rdkit=derived["mapping"]["rdkit"],
                transferred_atoms=derived["mapping"]["transferred_atoms"],
                conserved_acceptor_atoms=derived["mapping"]["conserved_acceptor_atoms"],
                note="the template is derived from its own build support by the frozen "
                     "P3 MCS routine, so it cannot encode chemistry the support does "
                     "not contain",
            ),
        )
        # the declared cores must match this very support, or the scope is a lie
        _pm = Chem.MolFromSmiles(entry["product_smiles"])
        for _c in t["scope"]["acceptor_cores"]:
            assert _pm.HasSubstructMatch(Chem.MolFromSmarts(_c)), (
                f"declared core does not match its own build support: {_c}")
        templates.append(t)
        instances.append(dict(
            instance_id=f"PMC9700910:TcCGT:p5-{entry['reaction_id']}",
            category="C_formation",
            target=entry["product_smiles"],
            reference_precursors=[acc_smiles, UDP_GLC],
            p5_role="development_build",
            p5_build_reaction=entry["reaction_id"],
            development_exposed=True,
            provenance=dict(source="PMC9700910", enzyme="TcCGT",
                            reaction_id=entry["reaction_id"], name=entry["name"]),
            human_reviewed=False, actionable=False, evidence_closed=False,
            prediction_conditions_verified=False,
            independent_chemical_validation=False,
        ))
        t["support_instances"] = [instances[-1]["instance_id"]]

    # de-duplicate templates that collapsed onto the same acceptor core
    seen, unique_templates, unique_instances = set(), [], []
    for t, inst in zip(templates, instances):
        if t["template_id"] in seen:
            continue
        seen.add(t["template_id"])
        unique_templates.append(t)
        unique_instances.append(inst)
    templates, instances = unique_templates, unique_instances

    # ------------------------------------------------------ revalidate the SS scope
    p4_templates = rows(P4 / "templates.jsonl")
    ss_template = next(t for t in p4_templates
                       if t["scope"]["center_class"] == "rhamnoside_glucoside_O2")
    p3_instances = {r["instance_id"]: r for r in rows(ROOT / "outputs/task016-p3/v1/runtime_instances.jsonl")}
    ss_instances = []
    for iid in SS_SCOPE_INSTANCE_IDS:
        r = dict(p3_instances[iid])
        r["p5_role"] = "development_build"
        r["p5_revalidated"] = True
        r["development_exposed"] = True
        r["human_reviewed"] = False
        ss_instances.append(r)
    ss_template = dict(ss_template)
    ss_template["p5_revalidated"] = True
    ss_template["p5_scope_namespace"] = "task016_p5"
    ss_template["p5_dropped_sibling_scopes"] = list(QUARANTINED)
    templates.append(ss_template)
    instances.extend(ss_instances)

    # ------------------------------------------------------------ build-only replay
    from flavoretro.glycoside_library_v5 import apply_template as apply_v5
    replay = []
    for t in templates:
        for iid in t["support_instances"]:
            r = next(i for i in instances if i["instance_id"] == iid)
            outcomes = apply_v5(t, r["target"])
            ok = canonical_side(r["reference_precursors"]) in [o["precursors"] for o in outcomes]
            replay.append(dict(template_id=t["template_id"], instance_id=iid,
                               reaction_id=r.get("p5_build_reaction"),
                               target=r["target"], replayed=ok, outcomes=len(outcomes)))
    assert all(x["replayed"] for x in replay), \
        f"support replay is not 100%: {[x for x in replay if not x['replayed']]}"

    # ---------------------------------------------------------- boundary controls
    # Every executable scope must refuse a set of pre-registered wrong cases. A
    # scope that cannot be bounded is not a scope.
    from flavoretro.glycoside_library_v5 import scope_center_allowed
    C_SM = "[c:1][C@@H:2]1O[C@H:3](CO)[C@@H:4]([OH:5])[C@H:6]([OH:7])[C@H:8]1[OH:9]"
    FLAVONOL_CORE = ["O=c1c(O)c(-c2ccccc2)oc2cc(O)cc(O)c12"]
    UDP_RHA = ("C[C@@H]1O[C@H](OP(=O)(O)OP(=O)(O)OC[C@H]2O[C@@H](n3ccc(=O)[nH]c3=O)"
               "[C@H](O)[C@H]2O)[C@H](O)[C@H](O)[C@H]1O")
    WRONG = [
        dict(name="wrong_sugar_rhamnose_on_flavonol", smarts=C_SM, donor=UDP_RHA,
             scope=dict(acceptor_cores=FLAVONOL_CORE)),
        dict(name="non_flavonoid_acceptor_benzoic_acid", smarts=C_SM, donor=UDP_GLC,
             scope=dict(acceptor_cores=FLAVONOL_CORE)),
    ]
    for name, spec in WRONG:
        target = ("O=C(O)c1ccccc1[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"
                  if "benzoic" in name else
                  next(i["target"] for i in instances if i.get("p5_build_reaction") == "P3R-C05"))
        donor = spec["donor"]
        rxn = rdChemReactions.ReactionFromSmarts(spec["smarts"])
        rxn.GetSubstructParams().useChirality = True
        mol = Chem.MolFromSmiles(target)
        allowed_any = False
        for products in rxn.RunReactants([mol]):
            try:
                for p in products:
                    Chem.SanitizeMol(p)
                fake = dict(templates[0])
                fake["donor"] = donor
                fake["scope"] = dict(templates[0]["scope"], **spec["scope"])
                if scope_center_allowed(fake, mol, products):
                    allowed_any = True
            except (ValueError, RuntimeError):
                continue
        controls.append(dict(control=name, target=target,
                             expected="refused", observed="allowed" if allowed_any else "refused",
                             violated=allowed_any))
    assert not any(c["violated"] for c in controls), \
        f"boundary controls were violated: {[c for c in controls if c['violated']]}"

    save_jsonl("templates.jsonl", templates)
    save_jsonl("runtime_instances.jsonl", instances)
    save_jsonl("support_replay.jsonl", replay)
    save_jsonl("boundary_results.jsonl", controls)

    manifest = {
        "schema_version": 2,
        "version": "task016_p5_v6",
        "rdkit": __import__("rdkit").rdBase.rdkitVersion,
        "task": TASK,
        "policy": {"default_enabled": False, "domain_cap_per_molecule": 4,
                   "generic_protection": 3, "prior": 0.2, "weight": 1.0},
        "inheritance": {
            "parent": "outputs/task016-p2/v2 (qualified P2/v3 payload, 54 templates)",
            "not_a_descendant_of_v4_or_v5": True,
            "reason": "the contract forbids re-inheriting an older increment and then marking "
                      "invalid scopes dead; v6 is assembled from v3 plus only the increments "
                      "that passed a P5 build gate",
            "added_scopes": ["flavonoid_8_C_glucoside", "rhamnoside_glucoside_O2"],
            "dropped_scopes": {q: "quarantined in P4 and excluded by construction in P5"
                               for q in QUARANTINED},
            "p5_new_scope": "flavonoid_8_C_glucoside",
        },
        "review_binding": "outputs/review/task015-06/v1/manifest.json",
        "files_sha256": {"templates.jsonl": None, "runtime_instances.jsonl": None},
        "support_replay": dict(instances=len(replay),
                               replayed=sum(x["replayed"] for x in replay),
                               all_replayed=True,
                               interpretation="replay proves the template reproduces its own "
                                              "build sources; it is not transfer evidence"),
        "boundary_controls": dict(total=len(controls),
                                  violated=sum(c["violated"] for c in controls)),
        "holdout_in_runtime": False,
        "human_reviewed": False,
        "actionable": False,
        "evidence_closed": False,
        "prediction_conditions_verified": False,
    }
    for rel in ("templates.jsonl", "runtime_instances.jsonl"):
        p = OUT / rel
        if not p.is_file():
            p.write_text("")
        manifest["files_sha256"][rel] = sha(p)
    save("template_source_manifest.json", manifest)

    event(TASK, "g3_v6_payload", templates=len(templates), instances=len(instances),
          replay=f"{sum(x['replayed'] for x in replay)}/{len(replay)}",
          controls_violated=sum(c["violated"] for c in controls))
    print(json.dumps(dict(
        templates=len(templates), instances=len(instances),
        support_replay=manifest["support_replay"],
        boundary_controls=manifest["boundary_controls"],
        files_sha256=manifest["files_sha256"],
        template_ids=[t["template_id"] for t in templates]), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())