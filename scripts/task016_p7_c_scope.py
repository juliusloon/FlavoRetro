"""P7 A7 proposal builder. Freeze requires external A3/A4/A5/A6 qualification."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p3_build import derive_template_smarts,scoped_smarts
from scripts.task016_p6_c_scope import formation_indices
from flavoretro.reviewed_resources import canonical_side
from rdkit import Chem
from rdkit.Chem import rdFMCS,rdChemReactions
from rdkit.Chem.Scaffolds import MurckoScaffold
TASK="TASK-016-P7";OUT=ROOT/"outputs/task016-p7/v1/C/E01"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def rows(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def save(n,x):write(TASK,str((OUT/n).relative_to(ROOT)),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def save_rows(n,rr):write(TASK,str((OUT/n).relative_to(ROOT)),"".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rr))
def binding(acceptor,target):
    a=Chem.MolFromSmiles(acceptor);p=Chem.MolFromSmiles(target)
    m=rdFMCS.FindMCS([a,p],timeout=5,ringMatchesRingOnly=True,completeRingsOnly=True,bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if m.canceled or m.numAtoms!=a.GetNumAtoms():raise ValueError("nonconserved acceptor")
    q=Chem.MolFromSmarts(m.smartsString)
    am=a.GetSubstructMatch(q);pm=p.GetSubstructMatch(q)
    links=[b for b in p.GetBonds() if (b.GetBeginAtomIdx() in pm)!=(b.GetEndAtomIdx() in pm)]
    if len(links)!=1:raise ValueError("not one linkage")
    b=links[0];site=b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in pm else b.GetEndAtomIdx()
    ano=b.GetOtherAtomIdx(site)
    return a,p,am[pm.index(site)],site,ano
def guard_spec(s):
    a,p,asi,ps,ano=binding(s["acceptor"],s["target"])
    scaffold=MurckoScaffold.GetScaffoldForMol(a)
    core=set(a.GetSubstructMatch(scaffold))
    # Retain carboxyl for gallic acid and the two source oxygens adjacent to site.
    if s["center_class"]=="gallic_acid_2_C_glucoside":
        core=set(range(a.GetNumAtoms()))
        # Drop methyl beyond phenolic O, keeping source oxygen as flexible frontier.
        core={i for i in core if a.GetAtomWithIdx(i).GetAtomicNum()!=6 or a.GetAtomWithIdx(i).IsInRing() or any(b.GetBondType()==Chem.BondType.DOUBLE for b in a.GetAtomWithIdx(i).GetBonds())}
    for n in a.GetAtomWithIdx(asi).GetNeighbors():
        core.add(n.GetIdx())
        core.update(x.GetIdx() for x in n.GetNeighbors() if x.GetAtomicNum()==8)
    if s["center_class"]=="flavonol_8_C_glucoside":
        # C3 hydroxyl is the only exocyclic O attached to a pyrone-ring carbon.
        for ring in a.GetRingInfo().AtomRings():
            if any(a.GetAtomWithIdx(i).GetAtomicNum()==8 for i in ring):
                for i in ring:core.update(x.GetIdx() for x in a.GetAtomWithIdx(i).GetNeighbors() if x.GetAtomicNum()==8)
    a.GetAtomWithIdx(asi).SetAtomMapNum(777)
    query=Chem.MolFragmentToSmarts(a,atomsToUse=sorted(core),isomericSmarts=True)
    q=Chem.MolFromSmarts(query)
    site_index=next(x.GetIdx() for x in q.GetAtoms() if x.GetAtomMapNum()==777)
    return dict(kind="source_derived_core_site",core_query=query,site_query_atom_index=site_index,site_atom_map=777,query_origin="Murcko scaffold + source site-neighbor oxygens; gallic acid retains carboxyl; flavonol retains pyrone C3-OH",query_source_reaction_id=s["reaction_id"],required_transferred_atoms=11,required_sugar="beta-D-glucopyranose",required_complete_donor=canonical_side([s["donor"]]),acceptor_conservation="full canonical graph after removal of exactly one transferred 11-atom glycan",stereo_enforced_by="scoped SMARTS useChirality plus every glycan carbon stereo assigned")
from flavoretro.glycoside_scope_c_v7 import apply_c_scope as apply_scope
def mutate_controls(s,t):
    a,p,asi,site,ano=binding(s["acceptor"],s["target"])
    alpha=Chem.Mol(p);alpha.GetAtomWithIdx(ano).InvertChirality()
    unspecified=Chem.Mol(p);unspecified.GetAtomWithIdx(ano).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    epimer=Chem.Mol(p)
    c=next(n for n in epimer.GetAtomWithIdx(ano).GetNeighbors() if n.GetAtomicNum()==6 and n.GetIdx()!=site);c.InvertChirality()
    # Move existing source glycan bond to another source aromatic H position.
    site_ring=next(r for r in p.GetRingInfo().AtomRings() if site in r)
    alt=next(i for i in site_ring if i!=site and p.GetAtomWithIdx(i).GetTotalNumHs()==1)
    wrong_site=Chem.RWMol(p);wrong_site.RemoveBond(site,ano)
    if s["center_class"]=="gallic_acid_2_C_glucoside":
        alt=next(i for i in site_ring if i!=site and any(n.GetAtomicNum()==8 and n.GetDegree()==1 for n in p.GetAtomWithIdx(i).GetNeighbors()) and not any(n.GetAtomicNum()==6 and not n.IsInRing() for n in p.GetAtomWithIdx(i).GetNeighbors()))
        oxygen=next(n.GetIdx() for n in p.GetAtomWithIdx(alt).GetNeighbors() if n.GetAtomicNum()==8 and n.GetDegree()==1)
        wrong_site.AddBond(alt,ano,Chem.BondType.SINGLE);wrong_site.RemoveAtom(oxygen)
    else:wrong_site.AddBond(alt,ano,Chem.BondType.SINGLE)
    w=wrong_site.GetMol();Chem.SanitizeMol(w)
    # Break defining scaffold by changing source carbonyl double bond to single.
    wrong_core=Chem.RWMol(p)
    carbonyl=next(b for b in p.GetBonds() if b.GetBondType()==Chem.BondType.DOUBLE and {b.GetBeginAtom().GetAtomicNum(),b.GetEndAtom().GetAtomicNum()}=={6,8})
    if s["center_class"].startswith("flav"):
        ring_o=next(x for x in p.GetAtoms() if x.GetAtomicNum()==8 and x.IsInRing() and x.GetIsAromatic());wrong_core.GetAtomWithIdx(ring_o.GetIdx()).SetAtomicNum(16)
    else:wrong_core.GetBondBetweenAtoms(carbonyl.GetBeginAtomIdx(),carbonyl.GetEndAtomIdx()).SetBondType(Chem.BondType.SINGLE)
    wc=wrong_core.GetMol();Chem.SanitizeMol(wc)
    return [(n,Chem.MolToSmiles(m,True)) for n,m in [("wrong_anomer",alpha),("unspecified_anomer",unspecified),("wrong_glucose_stereo",epimer),("wrong_site",w),("wrong_core",wc)]]+[("no_transferred_sugar",s["acceptor"])]
def main():
    if (OUT/"scope_bank_manifest.json").exists():raise RuntimeError("already frozen")
    rr=rows(OUT/"design_candidates.jsonl");templates=[];exacts=[];replays=[];boundaries=[]
    for center in sorted({x["center_class"] for x in rr}):
        ss=[x for x in rr if x["center_class"]==center]
        if len({canonical_side([x["acceptor"]]) for x in ss})<2:raise ValueError("fewer than 2 acceptors")
        exact=derive_template_smarts(ss[0]);seed=dict(ss[0],formation=formation_indices(exact))
        scoped=scoped_smarts(exact,seed,center)
        t=dict(template_id="p7-C-E01:"+center,template_role="scope_template",category="C_formation",sugar_type="glucose",donor=canonical_side([ss[0]["donor"]]),required_context=dict(mode="enzymatic",donor_name="UDP-glucose"),support_instances=[x["instance_id"] for x in ss],smarts=scoped,scope_template=scoped,exact_instance_template=exact["smarts"],exact_sha256=digest(exact["smarts"]),scope_sha256=digest(scoped),allowed_targets=[],scope=dict(namespace="task016_p7",center_class=center,site=center.split("_")[-3] if False else center,donor="complete UDP-glucose",stereo="beta-D-glucopyranose",allowed_generalization="decorations outside source-derived mandatory core/site query",forbidden_generalization="different core or linkage site, sugar or stereo",interpretation="source-supported structural candidate range; activity and conditions unverified"),guard_spec=guard_spec(ss[0]),scope_transformation=dict(function="scripts.task016_p3_build.scoped_smarts",source_sha256=sha(ROOT/"scripts/task016_p3_build.py"),seed_formation=seed["formation"]),validation_status="pending_independent_source_and_structure")
        templates.append(t)
        for s in ss:
            outcomes=apply_scope(t,s["target"])
            replays.append(dict(scope_id=t["template_id"],reaction_id=s["reaction_id"],passed=canonical_side(s["reference_precursors"]) in [x["precursors"] for x in outcomes],outcomes=outcomes))
            exacts.append(dict(reaction_id=s["reaction_id"],scope_id=t["template_id"],**derive_template_smarts(s)))
        for name,target in mutate_controls(ss[0],t):
            outcomes=apply_scope(t,target)
            boundaries.append(dict(scope_id=t["template_id"],control=name,target=target,expected="refused",violated=bool(outcomes),fixture_only=True,derived_from=ss[0]["reaction_id"]))
    save_rows("scope_proposals.jsonl",templates);save_rows("exact_templates.jsonl",exacts);save("scope_build_replay.json",dict(replay=replays,passed=sum(x["passed"] for x in replays),total=len(replays)));save("scope_boundary_results.json",dict(controls=boundaries,violations=sum(x["violated"] for x in boundaries)))
    outnames=["scope_proposals.jsonl","exact_templates.jsonl","scope_build_replay.json","scope_boundary_results.json"]
    save("role_A7_proposal_manifest.json",dict(task=TASK,epoch_id="C-E01",agent_role="A7_Scope_Builder",created_at=datetime.now(timezone.utc).isoformat(),input_manifest_sha256={str((OUT/"role_A1_design_manifest.json").relative_to(ROOT)):sha(OUT/"role_A1_design_manifest.json")},output_files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in outnames},source_evidence_pointers=[dict(pmcid=s["pmcid"],reaction_id=s["reaction_id"],source_evidence=s["source_evidence"]) for s in rr],processed=len(rr),passed=0,rejected=0,pending=len(rr),counts=dict(processed=len(rr),passed=0,rejected=0,pending=len(rr)),build_replay_passed=sum(x["passed"] for x in replays),errors=[x for x in replays if not x["passed"]]+[x for x in boundaries if x["violated"]],unprocessed=[],holdout_read=False,model_outcomes_read=False,freeze_status="pending_external_qualification",human_reviewed=False))
    print(json.dumps(dict(scopes=len(templates),build_replay=sum(x["passed"] for x in replays),build_total=len(replays),boundaries=len(boundaries),violations=sum(x["violated"] for x in boundaries))))
if __name__=="__main__":main()
