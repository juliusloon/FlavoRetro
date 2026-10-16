"""TASK-016-P4 G5: build the explicit corrected runtime version v5.

v5 is NOT a descendant of v4. It is rebuilt as:

    v5 = qualified P2/v3 payload  +  only the P4-revalidated increment

The two quarantined P3 scopes are excluded on their own merits, not marked
invalid after the fact:

  C_hydroxyflavanone_C3  quarantined: G1 downgraded P3R-C01/C02, so no
                          structure-complete intermediate evidence exists and the
                          P3 identification string had transferred dehydrated-product
                          NMR onto an unassigned intermediate.
  rhamnoside_glucoside_O6 quarantined: its two P3 supports share one canonical
                          acceptor and one reaction id, so 1 distinct acceptor < the
                          gate of 2.

Only rhamnoside_glucoside_O2 survives: 2 distinct canonical acceptors, 2
structure-complete build reactions. v1..v4 files, fingerprints and behaviour are
untouched; v5 loads only through an explicit request path and fails closed when
the payload or its hash is missing.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P4"
OUT = ROOT / "outputs/task016-p4/v1"
P3 = ROOT / "outputs/task016-p3/v1"
P2V2 = ROOT / "outputs/task016-p2/v2"
sys.path.insert(0, str(ROOT))
from scripts.operate import event, write

SURVIVING_SCOPE = "rhamnoside_glucoside_O2"
QUARANTINED_SCOPES = ("C_hydroxyflavanone_C3", "rhamnoside_glucoside_O6")
# Support instances belonging to the surviving scope only. The C3 and O6
# instances stay in the P3 payload and are deliberately not copied.
O2_INSTANCE_IDS = [
    "PMC13084081:MpRhaT:a7c23dd18652d36e64e23c53",
    "PMC13084081:MpRhaT:f2cab8d5e86df915f06735ed",
]


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rows(p):
    return [json.loads(l) for l in Path(p).open() if l.strip()]


def save(name, v):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def save_jsonl(name, values):
    write(TASK, str((OUT / name).relative_to(ROOT)),
          "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def main():
    from rdkit import Chem
    from rdkit.Chem import rdChemReactions
    sys.path.insert(0, str(ROOT))
    from flavoretro.open_glycoside_library import normalize_species
    from flavoretro.reviewed_resources import canonical_side

    scopes = json.loads((OUT / "scope_decisions.json").read_text())
    assert scopes["counting_key"] == "canonical_acceptor_signature"
    assert SURVIVING_SCOPE in scopes["v5_increment_scopes"], scopes
    for q in QUARANTINED_SCOPES:
        assert scopes["scopes"][q]["decision"] == "quarantined", q

    p3_templates = rows(P3 / "templates.jsonl")
    keep = [t for t in p3_templates if t["scope"]["center_class"] == SURVIVING_SCOPE]
    dropped = [t for t in p3_templates if t["scope"]["center_class"] in QUARANTINED_SCOPES]
    assert len(keep) == 1 and len(dropped) == 2, (len(keep), len(dropped))

    p3_instances = {r["instance_id"]: r for r in rows(P3 / "runtime_instances.jsonl")}
    inst = []
    for iid in O2_INSTANCE_IDS:
        r = dict(p3_instances[iid])
        r["p4_role"] = "development_build"
        r["p4_scope_center"] = SURVIVING_SCOPE
        r["p4_revalidated"] = True
        r["development_exposed"] = True
        r["human_reviewed"] = False
        inst.append(r)
    assert all(i["instance_id"] in O2_INSTANCE_IDS for i in inst)

    t = dict(keep[0])
    t["p4_scope_namespace"] = "task016_p4"
    t["p4_revalidated"] = True
    t["p4_scope_center"] = SURVIVING_SCOPE
    t["p4_dropped_p3_sibling_scopes"] = list(QUARANTINED_SCOPES)

    # ------------------------------------------------ build-only replay proof
    template = t
    rxn = rdChemReactions.ReactionFromSmarts(template["smarts"])
    rxn.GetSubstructParams().useChirality = True
    replay = []
    for r in inst:
        mol = Chem.MolFromSmiles(normalize_species(r["target"])["normalized"])
        produced = set()
        for products in rxn.RunReactants([mol]):
            try:
                for p in products:
                    Chem.SanitizeMol(p)
                v = canonical_side([Chem.MolToSmiles(p, isomericSmiles=True) for p in products])
                if v:
                    produced.add(v)
            except (ValueError, RuntimeError):
                continue
        # reference_precursors is a list; canonical_side returns the joined form
        ok = canonical_side(r["reference_precursors"]) in produced
        replay.append(dict(instance_id=r["instance_id"], target=r["target"],
                           expected=canonical_side(r["reference_precursors"]),
                           replayed=ok,
                           outcomes=len(produced)))
    support_ok = all(x["replayed"] for x in replay)
    assert support_ok, [x for x in replay if not x["replayed"]]

    save_jsonl("templates.jsonl", [t])
    save_jsonl("runtime_instances.jsonl", inst)
    save_jsonl("support_replay.jsonl", replay)

    manifest = {
        "schema_version": 2,
        "version": "task016_p4_v5",
        "rdkit": __import__("rdkit").rdBase.rdkitVersion,
        "task": TASK,
        "policy": {"default_enabled": False, "domain_cap_per_molecule": 4,
                   "generic_protection": 3, "prior": 0.2, "weight": 1.0},
        "inheritance": {
            "parent": "outputs/task016-p2/v2 (qualified P2/v3 payload, 54 templates)",
            "not_a_descendant_of_v4": True,
            "reason": "contract forbids re-inheriting the whole v4 increment and then marking "
                      "two scopes invalid; v5 is rebuilt from v3 plus only the revalidated scope",
            "dropped_p3_scopes": {q: scopes["scopes"][q]["reason"] for q in QUARANTINED_SCOPES},
            "kept_p3_scope": SURVIVING_SCOPE,
        },
        "review_binding": "outputs/review/task015-06/v1/manifest.json",
        "files_sha256": {
            "templates.jsonl": None,
            "runtime_instances.jsonl": None,
        },
        "support_replay": dict(instances=len(replay), replayed=sum(x["replayed"] for x in replay),
                               all_replayed=support_ok),
        "holdout_in_runtime": False,
        "human_reviewed": False,
        "actionable": False,
        "evidence_closed": False,
        "prediction_conditions_verified": False,
    }
    # hashes must be computed after the payload files exist on disk
    for rel in ("templates.jsonl", "runtime_instances.jsonl"):
        p = OUT / rel
        if not p.is_file():
            p.write_text("")
        manifest["files_sha256"][rel] = sha(p)
    save("template_source_manifest.json", manifest)
    event(TASK, "g5_v5_payload", templates=1, instances=len(inst),
          support_replayed=f"{sum(x['replayed'] for x in replay)}/{len(replay)}",
          dropped_scopes=list(QUARANTINED_SCOPES))
    print(json.dumps({"templates": 1, "instances": len(inst),
                      "support_replay": manifest["support_replay"],
                      "files_sha256": manifest["files_sha256"],
                      "dropped": list(QUARANTINED_SCOPES)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
