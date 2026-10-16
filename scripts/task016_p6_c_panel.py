"""G2 source-figure encoding of the original C panel, independently frozen.

No structures are filled from compound names. The encoded graphs below are
transcribed from the original numbered figure and positional table, with the
explicit source beta-D-glucose linkage. Chemical Stille target stays deferred
because its complete protected stannane precursor has not been encoded here.
"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
from scripts.task016_p6_c_scope import GLUCOSYL
from scripts.task016_p5_retro_template import UDP_GLC
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from flavoretro.glycoside_scope import c8_sites,runtime_complete,panel_preflight
from flavoretro.reviewed_resources import canonical_side,reaction_signature

def attach_source_glucose(acceptor,site):
    mol=Chem.MolFromSmiles(acceptor); frag=Chem.MolFromSmiles(GLUCOSYL)
    rw=Chem.RWMol(Chem.CombineMols(mol,frag));ano=mol.GetNumAtoms()
    rw.AddBond(site,ano,Chem.BondType.SINGLE)
    a=rw.GetAtomWithIdx(ano);a.SetNumRadicalElectrons(0);a.SetChiralTag(Chem.ChiralType.CHI_TETRAHEDRAL_CCW)
    p=rw.GetMol();Chem.SanitizeMol(p)
    return Chem.MolToSmiles(p,isomericSmiles=True)

def phenolic_carbon(mol):
    return [a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum()==6 and a.GetIsAromatic() and a.GetTotalNumHs()==1
            and sum(any(n.GetAtomicNum()==8 and n.GetTotalNumHs()==1 for n in b.GetNeighbors()) for b in a.GetNeighbors())==2]

def c6_site(mol):
    c8=next(iter(c8_sites(mol)));ring=next(r for r in mol.GetRingInfo().AtomRings() if c8 in r)
    return next(i for i in ring if mol.GetAtomWithIdx(i).GetTotalNumHs()==1 and i!=c8)

def gallic_c2(mol):
    acid=next(a for a in mol.GetAtoms() if a.GetAtomicNum()==6 and any(b.GetBondType()==Chem.BondType.DOUBLE and b.GetOtherAtom(a).GetAtomicNum()==8 for b in a.GetBonds()))
    owner=next(n for n in acid.GetNeighbors() if n.GetIsAromatic())
    return next(n.GetIdx() for n in owner.GetNeighbors() if n.GetIsAromatic() and n.GetTotalNumHs()==1)

def main():
    if (OUT/"c_panel_manifest.json").exists() and "--repair-phosphate-gate" not in sys.argv:raise RuntimeError("C panel already frozen")
    if "--repair-phosphate-gate" in sys.argv:
        assert not load("c_preflight.json")["probe_executed"]
        assert not load("c_panel_manifest.json")["gate"]["passed"]
    scope_manifest=load("c_scope_manifest.json")
    assert all(sha(OUT/n)==h for n,h in scope_manifest["files_sha256"].items())
    sources={r["pmcid"]:r for r in load("source_identity_checks.json") if r["evidence_eligible"]}
    figs=load("source_structure_figures.json")+load("additional_structure_figures.json")
    figs={r["pmcid"]:r["download"] for r in figs if r["download"]["status"]=="available"}
    # Source graphs: PMC6036675 Fig 1a positional substitution table and Fig 1b;
    # PMC8841362 Fig 2A; PMC11480083 Fig 2c; PMC11053098 Fig 1a.
    specs=[
      ("P3R-C03","PMC6036675","O=c1cc(-c2ccc(O)cc2)oc2cc(O)cc(O)c12","C6",c6_site),
      ("P3R-C04","PMC6036675","O=c1cc(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12","C6",c6_site),
      ("P4R-C01","PMC11480083","O=C(c1ccc(O)cc1O)c1ccc(O)cc1O","C3 between source 2/4-OH",lambda m:phenolic_carbon(m)[0]),
      ("P4R-C04","PMC8841362","O=C(c1ccc(O)c(O)c1)c1c(O)cc(O)cc1O","source C3 of phloroglucinol ring",lambda m:phenolic_carbon(m)[0]),
      ("P5R-C01","PMC11053098","O=C(O)c1cc(O)c(O)c(O)c1","C2",gallic_c2),
      ("P5R-C02","PMC11053098","COc1c(O)cc(C(=O)O)cc1O","C2",gallic_c2),
    ]
    original={r["reaction_id"]:r for r in rows(ROOT/"outputs/task016-p5/v1/reaction_records.jsonl")}
    build=rows(ROOT/"outputs/task016-p2/v2/runtime_instances.jsonl")+rows(ROOT/"outputs/task016-p4/v1/runtime_instances.jsonl")+rows(OUT/"c_build_supports.jsonl")
    build_signatures={r["reference_signature"] for r in build}
    build_closures={"closure:"+r["provenance"]["pmcid"] for r in build}
    candidates=[];crosswalk=[]
    for rid,pid,acc,site,fn in specs:
        assert pid in sources and pid in figs
        acceptor=canonical_side([acc]);product=attach_source_glucose(acceptor,fn(Chem.MolFromSmiles(acceptor)))
        precursors=[acceptor,canonical_side([UDP_GLC])]
        sig=reaction_signature([canonical_side(precursors)],[product])
        binding=dict(pmcid=pid,doi=sources[pid]["doi"],xml=sources[pid]["xml"],figure=figs[pid],
                     metadata_verified=True,structure_graph_transcribed=True,source_site=site)
        record=dict(reaction_id=rid,bond_class="C_formation",product_smiles=product,acceptor_smiles=acceptor,
            reference_precursors=precursors,canonical_reaction_signature=sig,closure_group="closure:"+pid,
            exposure_grade=original[rid]["exposure_grade"],source_binding=binding,structure_complete=True,
            inferred=False,deferred=False,structure_origin="original_source_explicit_graph_and_stereochemistry",
            site=site,stereo="beta-D-glucopyranosyl",source_product_formula=rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(product)),
            actionable=False,evidence_closed=False,prediction_conditions_verified=False,human_reviewed=False,evaluator_side_only=True)
        record["runtime_executable"]=runtime_complete(record)
        record["leakage_free"]=sig not in build_signatures and record["closure_group"] not in build_closures
        candidates.append(record)
        crosswalk.append(dict(reaction_id=rid,old_structure_missing=not original[rid].get("product_smiles"),new_structure_complete=record["runtime_executable"],
            old_signature=original[rid]["canonical_reaction_signature"],new_signature=sig,source_binding=binding))
    eligible=[r for r in candidates if r["runtime_executable"] and r["leakage_free"]]
    save_rows("c_runtime_completeness.jsonl",candidates)
    save_rows("c_reference_reconciliation.jsonl",crosswalk)
    deferred=dict(reaction_id="P3R-C12",reason="complete protected glucosyl stannane reference precursor and protecting-group graph not encoded; cannot substitute UDP-glucose",
                  counting_qualified=True,runtime_executable=False,deferred=True,evaluator_side_only=True)
    save("c_deferred_reference.json",deferred)
    save_rows("c_heldout_references.jsonl",eligible)
    gate=panel_preflight(eligible,build_signatures,build_closures)
    save("c_panel_manifest.json",dict(task=TASK,version="p6-c-panel-v2",original_counting_targets=7,runtime_executable_targets=len(eligible),
         gate=gate,scope_manifest_sha256=sha(OUT/"c_scope_manifest.json"),reference_sha256=sha(OUT/"c_heldout_references.jsonl"),
         build_signatures=sorted(build_signatures),build_closures=sorted(build_closures),
         deferred=[deferred],no_probe_or_ABE_results=True,holdout_in_runtime=False))
    print(json.dumps(dict(gate=gate,targets=[r["reaction_id"] for r in eligible],excluded=[r["reaction_id"] for r in candidates if not r["leakage_free"]]),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
