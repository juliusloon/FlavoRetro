"""SS design encoding and exact->scope proposal; freeze is independently gated."""
import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,save,save_rows,sha,now,manifest
from scripts.task016_p3_build import derive_template_smarts,scoped_smarts
from scripts.task016_p6_c_scope import formation_indices
from flavoretro.glycoside_scope_ss_v7 import apply_template,PARENT_BETA_D_GLC
from flavoretro.reviewed_resources import canonical_side,reaction_signature
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
SCOPE_SPECS=[
 dict(center="flavanone_glucoside_O6_rhamnosyl",core="O=C1[CH2][C@@H](c2ccccc2)Oc2ccccc12",source="PMC13084081",locator="body//p[21] and Figure2E/G; purchased N7Rut/H7Rut standards in body//p[83], SI Table6",pairs=[("prunin","narirutin"),("hesperetin 7-O-glucoside","hesperidin")]),
 dict(center="flavone_glucoside_O6_rhamnosyl",core="O=c1[cH]c(-c2ccccc2)oc2ccccc12",source="PMC9706480",locator="Fig4A/B source products with standard MS/MS; Fig5B substrate 1/2 graphs; body//p[24,25,51]; SI FigS5 reference standards",pairs=[("acacetin 7-O-glucoside","linarin"),("apigenin 7-O-glucoside","isorhoifolin")]),
 dict(center="flavonol_glucoside_O6_rhamnosyl",core="O=c1c(O)c(-c2ccccc2)oc2ccccc12",source="PMC9706480",locator="Fig5A/B substrate6/7; body//p[23,51]; SI FigS5 standards, chemical qualification pending",pairs=[("quercetin 3-O-glucoside","rutin"),("astragalin","nicotiflorin")]),
]
def db_objects():
    values={}
    for sub in ["pubchem_design","pubchem_supports2"]:
        for rec in json.loads((OUT/sub/"pubchem_design_intake.json").read_text()):
            if rec["properties"]["status_code"]!=200:continue
            props=json.loads((ROOT/rec["properties"]["path"]).read_text())["PropertyTable"]["Properties"]
            if len(props)!=1:raise ValueError("ambiguous database identity")
            p=props[0];mol=Chem.MolFromSmiles(p["SMILES"])
            if mol is None or rdMolDescriptors.CalcMolFormula(mol)!=p["MolecularFormula"]:raise ValueError("invalid graph/formula")
            values[rec["name"]]=dict(name=rec["name"],properties=p,smiles=canonical_side([p["SMILES"]]),raw_path=rec["properties"]["path"],raw_sha256=sha(ROOT/rec["properties"]["path"]),synonym_path=rec["synonyms"]["path"])
    return values
def encode():
    db=db_objects();donor=db["UDP-beta-L-rhamnose"];supports=[]
    for spec in SCOPE_SPECS:
        for ix,(aname,pname) in enumerate(spec["pairs"],1):
            a,p=db[aname],db[pname]
            if not Chem.MolFromSmiles(p["smiles"]).HasSubstructMatch(Chem.MolFromSmiles(a["smiles"]),useChirality=True):raise ValueError("full acceptor stereo not conserved")
            iid="p7-SS-build:"+spec["center"]+":"+str(ix)
            supports.append(dict(instance_id=iid,reaction_id=iid,template_role="development_build",acceptor=a["smiles"],donor=donor["smiles"],target=p["smiles"],reference_precursors=[a["smiles"],donor["smiles"]],reference_signature=reaction_signature([canonical_side([a["smiles"],donor["smiles"]])],[p["smiles"]]),
                source_names=dict(acceptor=aname,product=pname,donor="UDP-beta-L-rhamnose"),category="sugar_sugar_formation",sugar_type="rhamnose",scope_group=spec["center"],
                structure_origin="authoritative_structure_database_source_standard_identity_chain",structure_complete=False,evidence_eligible=False,chemical_admission="pending_A3_A5_reconciliation",historical_development_exposure=True,development_exposed=True,human_reviewed=False,prediction_conditions_verified=False,
                closure_group="closure:"+spec["source"],provenance=dict(pmcid=spec["source"],locators=spec["locator"],review_type="agent_delegated",database_identity=[dict(role=role,CID=item["properties"]["CID"],raw_path=item["raw_path"],raw_sha256=item["raw_sha256"],synonym_path=item["synonym_path"]) for role,item in [("acceptor",a),("product",p),("donor",donor)]])))
    save_rows("design_extractor_A4.jsonl",supports)
    save("A4_structure_manifest.json",dict(agent_role="A4_Structure_Extractor_1",method="official_SMILES_graph_formula_source_standard_identity",at=now(),task_id="TASK-016-P7",epoch_id="SS-E01",input_sha256={str(OUT/sub/"pubchem_design_intake.json"):sha(OUT/sub/"pubchem_design_intake.json") for sub in ["pubchem_design","pubchem_supports2"]},output_sha256={"design_extractor_A4.jsonl":sha(OUT/"design_extractor_A4.jsonl")},read_holdout=False,read_model_outcomes=False,total=6,admitted=0,deferred=6,rejected=0,pending="independent identity + A5 InChI graph reconciliation"))
    return supports
def boundary_targets(seed,exact):
    mol=Chem.MolFromSmiles(exact["smarts"].split(">>")[0]);idx=formation_indices(exact)["product_atom_indices"];ano=idx["anomeric"];site=idx["acceptor_site"];added=set(idx["added"])
    def smi(m):
        for a in m.GetAtoms():a.SetAtomMapNum(0)
        Chem.SanitizeMol(m);return Chem.MolToSmiles(m,isomericSmiles=True)
    wrong_ano=Chem.Mol(mol);wrong_ano.GetAtomWithIdx(ano).InvertChirality()
    missing=Chem.Mol(mol);missing.GetAtomWithIdx(ano).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    wrong_donor=Chem.Mol(mol);carbon=next(a for a in wrong_donor.GetAtoms() if a.GetIdx() in added and a.GetIdx()!=ano and a.GetChiralTag()!=Chem.ChiralType.CHI_UNSPECIFIED);carbon.InvertChirality()
    parent_query=Chem.MolFromSmarts(PARENT_BETA_D_GLC.replace("[OH:16]","[O:16]"))
    match=mol.GetSubstructMatch(parent_query,useChirality=True)
    if not match:raise ValueError("parent exact graph missing")
    # A source-parent non-anomeric ring stereocenter, intentionally inverted fixture.
    parent_atom=next(a.GetIdx() for a in parent_query.GetAtoms() if a.GetAtomMapNum()==3)
    wrong_parent=Chem.Mol(mol);wrong_parent.GetAtomWithIdx(match[parent_atom]).InvertChirality()
    # Reposition the donor glycosidic bond from O6 to a free ring hydroxyl.
    other_oxygen=next(a.GetIdx() for a in mol.GetAtoms() if a.GetIdx() not in added and a.GetIdx()!=site and a.GetAtomicNum()==8 and a.GetDegree()==1 and a.GetTotalNumHs()==1 and any(n.IsInRing() and not n.GetIsAromatic() and n.GetAtomicNum()==6 for n in a.GetNeighbors()))
    moved=Chem.RWMol(mol);moved.RemoveBond(site,ano);moved.AddBond(other_oxygen,ano,Chem.BondType.SINGLE);moved.GetAtomWithIdx(other_oxygen).SetNumExplicitHs(0);moved.GetAtomWithIdx(site).SetNumExplicitHs(1)
    controls=[("wrong_transferred_anomer",smi(wrong_ano)),("unspecified_transferred_anomer",smi(missing)),("wrong_transferred_sugar_stereo",smi(wrong_donor)),("wrong_parent_glucose_stereo",smi(wrong_parent)),("wrong_parent_ring_O_site",smi(moved.GetMol())),("no_transferred_sugar",seed["acceptor"])]
    return controls
def build():
    if (OUT/"scope_freeze.json").exists():raise RuntimeError("SS_SCOPE_ALREADY_FROZEN")
    supports=[json.loads(l) for l in (OUT/"design_extractor_A4.jsonl").read_text().splitlines()];templates=[];exact_out=[];replays=[];boundaries=[];plans=[]
    for spec in SCOPE_SPECS:
        members=[r for r in supports if r["scope_group"]==spec["center"]]
        if len({canonical_side([r["acceptor"]]) for r in members})<2:raise ValueError("too few distinct canonical acceptors")
        exact=derive_template_smarts(members[0]);seed=dict(members[0],formation=formation_indices(exact))
        scope_smarts=scoped_smarts(exact,seed,"rhamnoside_glucoside_O6")
        template=dict(template_id="p7-ss-scope:"+spec["center"]+":"+hashlib.sha256(scope_smarts.encode()).hexdigest()[:16],template_role="scope_template",exact_instance_template=exact["smarts"],scope_template=scope_smarts,smarts=scope_smarts,allowed_targets=[],category="sugar_sugar_formation",sugar_type="rhamnose",donor=members[0]["donor"],support_instances=[r["instance_id"] for r in members],required_context=dict(mode="enzymatic",donor_name="UDP-beta-L-rhamnose"),validation_status="pending_source_and_dual_graph_verification",scope=dict(namespace="task016_p7",center_class=spec["center"],acceptor_cores=[spec["core"]],parent_glycan_patterns=[PARENT_BETA_D_GLC],site="O6",donor="complete source UDP-beta-L-rhamnose",stereo="alpha-L-rhamnopyranosyl (1->6) beta-D-glucopyranoside",allowed_generalization="source-supported core only; aglycone decorations outside sugar O6 centre",forbidden_generalization="different core, parent sugar/anomer/stereo, transferred sugar/anomer/stereo or linkage",interpretation="source-supported structural candidate range; novel activity/enzyme/conditions unknown"),derivation=exact["mapping"],scope_transformation=dict(function="scripts.task016_p3_build.scoped_smarts",source_sha256=sha(ROOT/"scripts/task016_p3_build.py"),center="rhamnoside_glucoside_O6",exact_sha256=hashlib.sha256(exact["smarts"].encode()).hexdigest(),scope_sha256=hashlib.sha256(scope_smarts.encode()).hexdigest(),formation_indices=seed["formation"]))
        for member in members:
            exact_out.append(dict(instance_id=member["instance_id"],**derive_template_smarts(member)))
            replays.append(dict(scope_id=template["template_id"],instance_id=member["instance_id"],expected=canonical_side(member["reference_precursors"]),target=member["target"]))
        wrong_core=next(r["target"] for r in supports if ("flavonol" in r["scope_group"] if "flavone_" in spec["center"] else "flavone_" in r["scope_group"]))
        controls=boundary_targets(members[0],exact)+[("different_acceptor_core",wrong_core)]
        if spec["center"].startswith("flavanone"):
            aglycone_boundary=Chem.MolFromSmiles(members[0]["target"])
            c2=next(a for a in aglycone_boundary.GetAtoms() if a.GetChiralTag()!=Chem.ChiralType.CHI_UNSPECIFIED and any(n.GetIsAromatic() for n in a.GetNeighbors()))
            c2.InvertChirality();controls.append(("wrong_flavanone_C2_stereo",Chem.MolToSmiles(aglycone_boundary,isomericSmiles=True)))
        for name,target in controls:
            plans.append(dict(scope_id=template["template_id"],control=name,target=target,fixture_only=True,expected="refused",registered_before_holdout=True))
        templates.append(template)
    plan_path=OUT/"scope_boundary_plan.json"
    if plan_path.exists():raise RuntimeError("IMMUTABLE_BOUNDARY_PLAN_ALREADY_EXISTS")
    save("scope_boundary_plan.json",dict(task_id="TASK-016-P7",epoch_id="SS-E01",registered_at=now(),controls=plans,read_holdout=False,read_model_outcomes=False,guard_sha256=sha(ROOT/"flavoretro/glycoside_scope_ss_v7.py")))
    plan_sha=sha(plan_path);by_id={t["template_id"]:t for t in templates}
    for replay in replays:
        outcomes=apply_template(by_id[replay["scope_id"]],replay["target"]);replay.update(outcomes=outcomes,passed=replay["expected"] in [x["precursors"] for x in outcomes],boundary_plan_sha256=plan_sha,executed_at=now())
    for control in plans:
        outcomes=apply_template(by_id[control["scope_id"]],control["target"]);boundaries.append(dict(control,violated=bool(outcomes),outcomes=outcomes,boundary_plan_sha256=plan_sha,executed_at=now()))
    save_rows("design_exact_templates.jsonl",exact_out);save_rows("scope_templates_proposed.jsonl",templates)
    save("scope_build_replay.json",dict(total=len(replays),passed=sum(r["passed"] for r in replays),records=replays))
    save("scope_boundaries.json",dict(total=len(boundaries),violations=sum(r["violated"] for r in boundaries),records=boundaries))
    save("scope_proposal_manifest.json",dict(task_id="TASK-016-P7",epoch_id="SS-E01",family="SS",at=now(),scopes=len(templates),build_supports=len(supports),scope_frozen=False,independently_verified=False,read_holdout=False,read_model_outcomes=False,files_sha256={p:sha(OUT/p) for p in ["design_extractor_A4.jsonl","design_exact_templates.jsonl","scope_templates_proposed.jsonl","scope_boundary_plan.json","scope_build_replay.json","scope_boundaries.json"]},guard_sha256=sha(ROOT/"flavoretro/glycoside_scope_ss_v7.py")))
    manifest("A7_SS_Scope_Builder",["scripts/task016_p3_build.py","flavoretro/glycoside_scope_ss_v7.py"],["scope_proposal_manifest.json"])
    print(dict(scopes=len(templates),build_replay=f'{sum(r["passed"] for r in replays)}/{len(replays)}',boundary_violations=sum(r["violated"] for r in boundaries),chemical_admission="pending_independent_A3_A5"))
    if not all(r["passed"] for r in replays) or any(r["violated"] for r in boundaries):raise RuntimeError("SS_SCOPE_IMPLEMENTATION_FAILED")
if __name__=="__main__":build()
