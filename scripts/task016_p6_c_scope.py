"""G1: derive exact -> P3 scoped_smarts -> replay -> boundaries -> immutable freeze.

Only the two frozen P5-qualified C8 build reactions are used. P5's extra-oxygen
helper is excluded. Product graph is assembled from the qualified acceptor,
explicit source C8 linkage and beta-D-glucose stereochemistry, never from a name.
"""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
from scripts.task016_p3_build import derive_template_smarts, scoped_smarts
from scripts.task016_p5_retro_template import UDP_GLC
from rdkit import Chem
from rdkit.Chem import rdChemReactions, rdMolDescriptors
from flavoretro.glycoside_scope import c8_sites, apply_c_scope, FLAVONOL
from flavoretro.reviewed_resources import canonical_side, reaction_signature
GLUCOSYL="[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O"

def source_product(acceptor, site=None):
    mol=Chem.MolFromSmiles(acceptor)
    sites=c8_sites(mol)
    if len(sites)!=1:
        raise ValueError("source C8 site not unique")
    site=next(iter(sites)) if site is None else site
    fragment=Chem.MolFromSmiles(GLUCOSYL)
    rw=Chem.RWMol(Chem.CombineMols(mol,fragment))
    ano=mol.GetNumAtoms()
    rw.AddBond(site,ano,Chem.BondType.SINGLE)
    rw.GetAtomWithIdx(ano).SetNumRadicalElectrons(0)
    rw.GetAtomWithIdx(ano).SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW)
    product=rw.GetMol(); Chem.SanitizeMol(product)
    return Chem.MolToSmiles(product,isomericSmiles=True)

def formation_indices(exact):
    left,right=exact["smarts"].split(">>")
    product=Chem.MolFromSmiles(left)
    acc=Chem.MolFromSmiles(right.split(".",1)[0])
    maps={a.GetAtomMapNum() for a in acc.GetAtoms()}
    added={a.GetIdx() for a in product.GetAtoms() if a.GetAtomMapNum() not in maps}
    links=[b for b in product.GetBonds() if (b.GetBeginAtomIdx() in added)!=(b.GetEndAtomIdx() in added)]
    if len(links)!=1: raise ValueError("not one attachment")
    b=links[0]; ano=b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in added else b.GetEndAtomIdx()
    return dict(product_atom_indices=dict(added=sorted(added),anomeric=ano,acceptor_site=b.GetOtherAtomIdx(ano)))

def construct_scope(instance):
    exact = derive_template_smarts(instance)
    seed = dict(instance, formation=formation_indices(exact))
    scope = scoped_smarts(exact, seed, "flavonol_8_C_glucoside")
    return exact, scope, seed

def main():
    if (OUT/"c_scope_manifest.json").exists():
        raise RuntimeError("C scope already frozen")
    frozen={r["reaction_id"]:r for r in rows(ROOT/"outputs/task016-p5/v1/reaction_records.jsonl")}
    correction={r["reaction_id"]:r for r in rows(ROOT/"outputs/task016-p4/v1/corrected_reaction_records.jsonl")}
    supports=[]
    for rid in ("P3R-C05","P3R-C06"):
        r=frozen[rid]; q=correction[rid]
        if not r["structure_complete"] or not q["countable_as_structure_complete"]:
            raise ValueError("unqualified build source")
        acceptor=canonical_side([r["acceptor_smiles"]])
        target=source_product(acceptor)
        supports.append(dict(instance_id="p6-build:"+rid,reaction_id=rid,template_role="development_build",
            acceptor=acceptor,donor=canonical_side([UDP_GLC]),target=target,reference_precursors=[acceptor,canonical_side([UDP_GLC])],
            reference_signature=reaction_signature([canonical_side([acceptor,UDP_GLC])],[target]),
            provenance=dict(pmcid=r["source"],review_type="agent_delegated",source_evidence=q["reference_context"],
                frozen_record_sha256=sha(ROOT/"outputs/task016-p4/v1/corrected_reaction_records.jsonl"),
                encoding="qualified frozen acceptor + source-explicit C8 and beta-D-glucopyranose graph"),
            structure_complete=True, inferred=False, development_exposed=True, human_reviewed=False,
            closure_group=r["closure_group"], category="C_formation",sugar_type="glucose"))
    assert len({s["acceptor"] for s in supports})>=2
    exact,scoped,seed=construct_scope(supports[0])
    template=dict(template_id="p6-c-scope:"+content_sha(scoped)[:20],template_role="scope_template",
        exact_instance_template=exact["smarts"], scope_template=scoped, smarts=scoped,
        exact_sha256=content_sha(exact["smarts"]),scope_sha256=content_sha(scoped),allowed_targets=[],
        category="C_formation",sugar_type="glucose",donor=canonical_side([UDP_GLC]),
        support_instances=[s["instance_id"] for s in supports],
        required_context=dict(mode="enzymatic",donor_name="UDP-glucose"),
        scope=dict(namespace="task016_p6",center_class="flavonol_8_C_glucoside",acceptor_cores=[FLAVONOL],
            parent_glycan_patterns=[],site="C8",donor="complete UDP-glucose",stereo="beta-D-glucopyranose",
            allowed_generalization="aglycone decorations outside C8 centre; flavonol core mandatory",
            forbidden_generalization="different core, attachment site, transferred sugar or stereochemistry",
            interpretation="source-supported structural candidate range; activity and conditions unverified"),
        scope_transformation=dict(function="scripts.task016_p3_build.scoped_smarts",source_sha256=sha(ROOT/"scripts/task016_p3_build.py"),
            seed_formation=seed["formation"],center="flavonol_8_C_glucoside",atom_index_binding="formation indices recomputed on mapped exact LHS order"),
        derivation=exact["mapping"],validation_status="pending")
    replay=[dict(reaction_id=s["reaction_id"],instance_id=s["instance_id"],
        passed=canonical_side(s["reference_precursors"]) in [o["precursors"] for o in apply_c_scope(template,s["target"])],
        outcomes=apply_c_scope(template,s["target"])) for s in supports]
    # Fixtures derived only from the build object; pre-registered before any holdout read.
    mol=Chem.MolFromSmiles(supports[0]["target"])
    # Find glycosyl anomeric atom by its bond to source C8.
    site=next(iter(c8_sites(mol))); ano=next(n.GetIdx() for n in mol.GetAtomWithIdx(site).GetNeighbors() if not n.GetIsAromatic())
    alpha=Chem.Mol(mol); alpha.GetAtomWithIdx(ano).InvertChirality()
    unspecified=Chem.Mol(mol); unspecified.GetAtomWithIdx(ano).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    wrong_sugar=Chem.Mol(mol); nxt=next(n for n in wrong_sugar.GetAtomWithIdx(ano).GetNeighbors() if n.GetAtomicNum()==6 and n.GetIdx()!=site); nxt.InvertChirality()
    accmol=Chem.MolFromSmiles(supports[0]["acceptor"])
    ring=next(r for r in accmol.GetRingInfo().AtomRings() if next(iter(c8_sites(accmol))) in r)
    c6=next(i for i in ring if accmol.GetAtomWithIdx(i).GetTotalNumHs()==1 and i not in c8_sites(accmol))
    controls=[("wrong_anomer",Chem.MolToSmiles(alpha,True)),("unspecified_anomer",Chem.MolToSmiles(unspecified,True)),
        ("wrong_glucose_stereo",Chem.MolToSmiles(wrong_sugar,True)),("wrong_C6_site",source_product(supports[0]["acceptor"],c6)),
        ("no_transferred_sugar",supports[0]["acceptor"])]
    # Remove the C3 hydroxyl on the build graph: synthetic flavone boundary, never a reference.
    rw=Chem.RWMol(mol)
    core=rw.GetSubstructMatch(Chem.MolFromSmarts(FLAVONOL)); rw.RemoveAtom(core[3])
    boundary_mol=rw.GetMol(); Chem.SanitizeMol(boundary_mol)
    controls.append(("non_flavonol_core",Chem.MolToSmiles(boundary_mol,True)))
    boundaries=[dict(control=n,target=s,expected="refused",violated=bool(apply_c_scope(template,s)),fixture_only=True) for n,s in controls]
    save_rows("c_build_supports.jsonl",supports)
    save_rows("c_exact_templates.jsonl",[dict(reaction_id=s["reaction_id"],**derive_template_smarts(s)) for s in supports])
    save("c_scope_build_replay.json",dict(replay=replay,passed=sum(r["passed"] for r in replay),total=len(replay)))
    save("c_scope_boundary_results.json",dict(controls=boundaries,violations=sum(b["violated"] for b in boundaries)))
    if not all(r["passed"] for r in replay) or any(b["violated"] for b in boundaries):
        save("c_scope_implementation_failure.json",dict(template=template,replay=replay,boundaries=boundaries))
        raise RuntimeError("scope implementation gate failure")
    template["validation_status"]="source_reconstruction_passed"
    save("c_scope_template.json",template)
    save("c_scope_manifest.json",dict(task=TASK,version="p6-c-scope-v1",pipeline=["derive_template_smarts","scoped_smarts","scope metadata","build replay","boundary controls"],
         exact_template_sha256=template["exact_sha256"],scope_template_sha256=template["scope_sha256"],
         files_sha256={n:sha(OUT/n) for n in ["c_build_supports.jsonl","c_exact_templates.jsonl","c_scope_template.json","c_scope_build_replay.json","c_scope_boundary_results.json"]},
         build_replay=2,boundary_violations=0,holdout_read=False,human_reviewed=False))
    print(json.dumps(dict(replay=replay,boundaries=boundaries,exact_sha=template["exact_sha256"],scope_sha=template["scope_sha256"]),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
