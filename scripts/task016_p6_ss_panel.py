"""G6 reconcile SS identities and source/reaction closures without threshold relaxation."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
from scripts.task016_p6_c_panel import attach_source_glucose
from rdkit import Chem
from flavoretro.reviewed_resources import canonical_side,reaction_signature
from flavoretro.glycoside_scope import runtime_complete,panel_preflight

def main():
    sources={r["pmcid"]:r for r in load("source_identity_checks.json") if r["evidence_eligible"]}
    baseline=rows(ROOT/"outputs/task016-p2/v2/runtime_instances.jsonl")
    parent=next(r for r in baseline if r["category"]=="sugar_sugar_formation" and r["sugar_type"]=="glucose" and r["annotation_case"]["acceptor_name"]=="kaempferol 3-O-beta-D-glucoside")
    acceptor=canonical_side([parent["acceptor"]]);donor=canonical_side([parent["donor"]]);mol=Chem.MolFromSmiles(acceptor)
    site=next(a.GetIdx() for a in mol.GetAtoms() if a.GetAtomicNum()==8 and a.GetDegree()==1 and a.GetTotalNumHs()==1
         and any(n.GetAtomicNum()==6 and not n.IsInRing() and n.GetDegree()==2 and any(x.IsInRing() for x in n.GetNeighbors()) for n in a.GetNeighbors()))
    product=attach_source_glucose(acceptor,site);sig=reaction_signature([canonical_side([acceptor,donor])],[product])
    source=sources["PMC12120870"]
    r=dict(reaction_id="P6-SS22-corrected",supersedes_label="P3R-SS22",bond_class="sugar_sugar_formation",
        acceptor_smiles=acceptor,product_smiles=product,reference_precursors=[acceptor,donor],canonical_reaction_signature=sig,
        closure_group="closure:PMC12120870",exposure_grade="E0",source_binding=dict(pmcid=source["pmcid"],doi=source["doi"],xml=source["xml"],metadata_verified=True,
            evidence_locator="Results: Flavonoid glycosides ... astragalin (25); authentic-standard match of 25a to kaempferol 3-O-gentiobioside",
            parent_structure_binding=dict(instance_id=parent["instance_id"],source_graph_identity="same source-explicit beta-D-glucopyranoside; source Figure 2a and 25a standard")),
        structure_origin="original_source_explicit_graph_and_stereochemistry",structure_complete=True,deferred=False,inferred=False,
        source_donor="UDP-glucose",linkage="beta-D-glucose (1->6) beta-D-glucose",human_reviewed=False,actionable=False,evidence_closed=False,
        prediction_conditions_verified=False,evaluator_side_only=True)
    build=baseline+rows(ROOT/"outputs/task016-p4/v1/runtime_instances.jsonl")+rows(OUT/"c_build_supports.jsonl")
    build_sig={x["reference_signature"] for x in build};build_closures={"closure:"+x["provenance"]["pmcid"] for x in build}
    qualified=[r] if runtime_complete(r) and sig not in build_sig and r["closure_group"] not in build_closures else []
    apiin=next(x for x in baseline if x["provenance"]["pmcid"]=="PMC10602602")
    edges=[dict(source_a="PMC10602597",source_b="PMC10602602",reason="secondary commentary explicitly reports the primary Yamashita study; not independent primary evidence"),
           dict(source_a="PMC13140228",source_b="PMC10602602",reason="both report the same complete apigenin 7-O-glucoside + UDP-apiose -> apiin reaction",
                canonical_reaction_signature=apiin["reference_signature"],witness_instance_id=apiin["instance_id"])]
    corrected=[dict(reaction_id="P3R-SS08",source="PMC10602597",old="luteolin 7-O-glucoside + UDP-apiose -> O2-apiose",new="secondary commentary about primary PMC10602602, which is baseline build",
              final_status="excluded_primary_and_closure",runtime_denominator=False),
          dict(reaction_id="P3R-SS09",source="PMC10602597",old="chrysoeriol 7-O-glucoside + UDP-apiose -> O2-apiose",new="same secondary commentary and primary build closure",
              final_status="excluded_primary_and_closure",runtime_denominator=False),
          dict(reaction_id="P3R-SS12",source="PMC13140228",old="astragalin + UDP-Rha -> O2-rhamnose",new="astragalin + UDP-apiose -> O2-beta-D-apiose; source 1D/2D NMR and Table S5",
              final_status="corrected_identity_but_build_closure",runtime_denominator=False),
          dict(reaction_id="P3R-SS22",source="PMC12120870",old="astragalin + UDP-Rha -> O2-rhamnose",new="astragalin + UDP-Glc -> beta-(1->6) glucoside; authentic-standard match",
              final_status="runtime_executable_corrected_holdout",runtime_denominator=bool(qualified))]
    save_rows("ss_reference_reconciliation.jsonl",corrected)
    save_rows("ss_source_group_edges.jsonl",edges)
    save_rows("ss_heldout_references.jsonl",qualified)
    save("ss_runtime_completeness.json",dict(records=[r],runtime_executable=runtime_complete(r)))
    gate=panel_preflight(qualified,build_sig,build_closures)
    save("ss_panel_manifest.json",dict(task=TASK,original_counting_targets=4,current_runtime_targets=len(qualified),gate=gate,
         references_sha256=sha(OUT/"ss_heldout_references.jsonl"),reaction_and_source_closure_reconciled=True,
         source_group_edges_sha256=sha(OUT/"ss_source_group_edges.jsonl"),no_model_results_used=True))
    save("ss_preflight.json",dict(passed=gate["passed"],stop_condition=1 if not gate["passed"] else None,reason="SS_runtime_panel_failure" if not gate["passed"] else "qualified",
         targets=len(qualified),groups=gate["closure_groups"],C_can_block_SS=False,scope_build_replay=2))
    intake=[]
    for src in load("source_identity_checks.json"):
        title=src.get("title","").lower()
        if not src["evidence_eligible"]:disposition="identity_unverified_no_evidence_use"
        elif src["pmcid"] in {"PMC10602597","PMC10602602","PMC10706860","PMC13140228","PMC13084081","PMC9437722"}:disposition="build_or_shared_reaction_closure; no independent holdout"
        elif "triglycosides" in title or "polyphyllin" in title or "trillin" in title:disposition="steroidal core/linkage outside frozen SS O2 range; no qualified independent new scope build pair"
        elif "phenylethanoid" in title:disposition="phenylethanoid core/O3 linkage outside frozen flavonoid O2 scope"
        elif src["pmcid"]=="PMC12120870":disposition="one corrected complete beta-(1->6)-glucose target; not O2-rhamnose"
        else:disposition="no additional source-qualified flavonoid O2-rhamnose holdout admitted"
        intake.append(dict(pmcid=src["pmcid"],title=src.get("title"),source_binding=src.get("xml"),evidence_eligible=src["evidence_eligible"],disposition=disposition))
    save_rows("ss_targeted_source_dispositions.jsonl",intake)
    save("ss_closure_resolution.json",dict(path_A=dict(status="not_resolved",reason="no independent two-acceptor O2-rhamnose build closure acquired; 1991/2004 citrus sources reconstruct the same naringin/neohesperidin reactions and cannot detach their existing source/reaction closure"),
        path_B=dict(status="not_resolved",reason="targeted original-source verification yielded no >=6 complete isolated SS panel; corrected existing panel has 1 target",new_qualified_holdouts=0),
        inherited_count_4_not_runtime_valid=True,new_identity_corrections=2,secondary_source_exclusions=2,source_exhaustion_claimed=False))
    print(dict(SS_targets=len(qualified),groups=gate["closure_groups"],passed=gate["passed"],identity_corrections=2))
if __name__=="__main__":main()
