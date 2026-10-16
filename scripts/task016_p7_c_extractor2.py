"""A5 source-graph extraction independent of P7 extractor A4 output.

Graph table is transcribed from the actual numbered original figures inspected
in this execution, not a name-only structure guess. Complete donor is decoded
from authoritative PubChem InChI, a different serialization from A4 SMILES.
"""
import json
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.task016_p7_orchestrate import sha_file,role_manifest,save_json
from scripts.operate import write
from flavoretro.reviewed_resources import canonical_side,reaction_signature
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1"
# Position-bearing source drawing transcription; all sugar centers explicit.
C_RECORDS=[
("P3R-C05","PMC9700910","C8","O=c1c(O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12","O=c1c(O)c(-c2ccc(O)cc2)oc2c([C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)cc(O)c12","C21H20O11"),
("P3R-C06","PMC9700910","C8","O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12","O=c1c(O)c(-c2ccc(O)c(O)c2)oc2c([C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)cc(O)c12","C21H20O12"),
("P3R-C03","PMC6036675","C6","O=c1cc(-c2ccc(O)cc2)oc2cc(O)cc(O)c12","O=c1cc(-c2ccc(O)cc2)oc2cc(O)c([C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)c12","C21H20O10"),
("P3R-C04","PMC6036675","C6","O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12","O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)c([C@@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)c(O)c12","C21H20O11"),
("P4R-C01","PMC11480083","C3","O=C(c1ccc(O)cc1O)c1ccc(O)cc1O","O=C(c1ccc(O)cc1O)c1ccc(O)c([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c1O","C19H20O10"),
("P4R-C04","PMC8841362","C3","O=C(c1ccc(O)c(O)c1)c1c(O)cc(O)cc1O","O=C(c1ccc(O)c(O)c1)c1c(O)cc(O)c([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c1O","C19H20O11"),
("P5R-C01","PMC11053098","C2","O=C(O)c1cc(O)c(O)c(O)c1","O=C(O)c1cc(O)c(O)c(O)c1[C@@H]1O[C@H](CO)[C@@H](O)[C@H](O)[C@H]1O","C13H16O10"),
("P5R-C02","PMC11053098","C2","COc1c(O)cc(C(=O)O)cc1O","COc1c(O)cc(C(=O)O)c([C@@H]2O[C@H](CO)[C@@H](O)[C@H](O)[C@H]2O)c1O","C14H18O10")]
FIGURES={"PMC9700910":("data/raw/task016-p7/C/ef5a4c5375c27a6fccf2ef13f2207bb86fcfb4ad26e11b751a60d63f53ffb49e.attempt-1.jpg","Fig9 a-d"),"PMC6036675":("data/raw/task016-p6/2026-10-07/5e09eea1ec2021aae9f6e91708a01628eeca02dc0f83d0762f94240f636a86a0.jpg","Fig1a positional table and Fig1b; direct experimental route body p29/35"),"PMC11480083":("data/raw/task016-p7/C/d9e3c82d44274220d0d499d91b69bcdd22c20df3a74c51d530c0c8563071ac23.attempt-1.jpg","Fig2c black1a to blue3a"),"PMC8841362":("data/raw/task016-p6/2026-10-07/355f240d3b350fb6fb7bc7e4d464dd2de1e90f347b68afa91fe38f0b30d2e168.jpg","Fig2A maclurin1 to1a"),"PMC11053098":("data/raw/task016-p6/2026-10-07/932d1dbf8ca75ff20cd8f549b0af0b758ed666564b80e5f5b9f572a7ec00f853.jpg","Fig1A GA2 to GA-Glc5 and4OMGA3 to4OMGA-Glc4; methods explicit 2-C-beta-D")}
def main():
    donor_path=R/"data/raw/task016-p7/root/udp-glucose-attempt-1.json"
    donor_raw=json.loads(donor_path.read_text())["PropertyTable"]["Properties"][0]
    donor=Chem.MolFromInchi(donor_raw["InChI"])
    if donor is None:raise RuntimeError("authoritative donor InChI parse")
    donor_s=Chem.MolToSmiles(donor,isomericSmiles=True)
    values=[]
    for rid,pid,site,acc,target,formula in C_RECORDS:
        a=Chem.MolFromSmiles(acc);p=Chem.MolFromSmiles(target)
        observed=rdMolDescriptors.CalcMolFormula(p)
        if observed!=formula:raise RuntimeError("figure/formula mismatch "+rid)
        if p.GetNumHeavyAtoms()-a.GetNumHeavyAtoms()!=11:raise RuntimeError("transfer atom conservation")
        image,locator=FIGURES[pid]
        values.append(dict(agent_role="A5 Structure Extractor-2",task="TASK-016-P7",epoch_id="C-E01",instance_id="p7-C-E01-build:"+rid,reaction_id=rid,pmcid=pid,acceptor=canonical_side([acc]),product=canonical_side([target]),donor=canonical_side([donor_s]),reference_precursors=[canonical_side([acc]),canonical_side([donor_s])],site=site,stereo="beta-D-glucopyranosyl",reaction_direction="forward formation; encoded reverse candidates",single_step=True,source_formula=formula,formula_check=True,structure_origin="original_source_graph_independent_transcription_plus_authoritative_donor_InChI",evidence_pointers=[dict(path=image,sha256=sha_file(R/image),locator=locator),dict(path=str(donor_path.relative_to(R)),sha256=sha_file(donor_path),locator="PubChem CID "+str(donor_raw["CID"])+" InChI")],read_extractor_A4=False,read_model_outcome=False,human_reviewed=False))
    path=O/"C/E01/design_extractor_A5.jsonl"
    write("TASK-016-P7",str(path.relative_to(R)),"".join(json.dumps(v,ensure_ascii=False,sort_keys=True)+"\n" for v in values))
    save_json(O/"C/E01/role_A5_manifest.json",role_manifest("A5 Structure Extractor-2","C-E01",[R/FIGURES[pid][0] for pid in FIGURES]+[donor_path],[path],dict(processed=len(values),passed=len(values),rejected=0,pending=0),pointers=[p for v in values for p in v["evidence_pointers"]]))
    print(dict(extracted=len(values),formula_checks=sum(v["formula_check"] for v in values),donor_CID=donor_raw["CID"]))
if __name__=="__main__":main()
