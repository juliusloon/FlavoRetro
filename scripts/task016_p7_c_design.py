"""P7 A1 design-corpus proposal. No source/structure eligibility is self-granted."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write
from scripts.task016_p7_identity_harness import parse_jats
TASK="TASK-016-P7";OUT=ROOT/"outputs/task016-p7/v1/C/E01"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def save(n,v):write(TASK,str((OUT/n).relative_to(ROOT)),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def save_rows(n,v):write(TASK,str((OUT/n).relative_to(ROOT)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in v))
def main():
    if (OUT/"scope_bank_manifest.json").exists():raise RuntimeError("epoch already frozen")
    inputs=["outputs/task016-p6/v1/c_build_supports.jsonl","outputs/task016-p6/v1/c_heldout_references.jsonl","outputs/task016-p6/v1/source_identity_checks.json","outputs/task016-p7/v1/approval.json"]
    builds=rows(ROOT/inputs[0]);held=rows(ROOT/inputs[1]);identities=json.loads((ROOT/inputs[2]).read_text())
    groups=[("flavonol_8_C_glucoside",builds),("flavone_6_C_glucoside",[r for r in held if r["reaction_id"] in ("P3R-C03","P3R-C04")]),("benzophenone_3_C_glucoside",[r for r in held if r["reaction_id"] in ("P4R-C01","P4R-C04")]),("gallic_acid_2_C_glucoside",[r for r in held if r["reaction_id"] in ("P5R-C01","P5R-C02")])]
    figures=json.loads((ROOT/"outputs/task016-p7/v1/C/design_figure_intake.json").read_text())
    inputs.append("outputs/task016-p7/v1/C/design_figure_intake.json")
    candidates=[]
    for center,rr in groups:
        if len(rr)!=2:raise ValueError(center+" support count")
        for r in rr:
            pmcid=r.get("source_binding",{}).get("pmcid") or r["provenance"]["pmcid"]
            inherited=next(x for x in identities if x["pmcid"]==pmcid)
            evidence=dict(r.get("source_binding") or r["provenance"])
            extra=[x["object"] for x in figures if x["pmcid"]==pmcid]
            evidence["P7_source_attachments"]=extra
            if pmcid=="PMC11480083":
                evidence["supersedes_P6_wrong_figure_pointer"]="P6 Fig4 is not the compound graph; correct graph is Fig2c (1a -> blue C-glucoside 3a)"
                evidence["figure"]=extra[0]
            if pmcid=="PMC9700910":
                evidence["corrected_evidence_locations"]=["main Fig9a/b kaempferol NMR and graph","main Fig9c/d quercetin NMR and graph","SI FigS4 HPLC, SI FigS5 LC/MS; not NMR"]
            identity_input={k:inherited.get(k) for k in ("pmcid","doi","title","journal","publication_metadata","publication_metadata_check","license","xml","meta","europepmc","media_urls")}
            identity_input["raw_JATS_publication_fields"]=parse_jats(ROOT/inherited["xml"]["path"],dict(path=inherited["xml"]["path"],sha256=inherited["xml"]["sha256"]))
            candidates.append(dict(task=TASK,epoch_id="C-E01",agent_role="A1_C_Source_Scout",scope_id="p7-c:"+center,center_class=center,reaction_id=r["reaction_id"],instance_id="p7-C-E01-build:"+r["reaction_id"],acceptor=r.get("acceptor_smiles") or r.get("acceptor"),target=r.get("product_smiles") or r.get("target"),donor=r["reference_precursors"][1],reference_precursors=r["reference_precursors"],closure_group=r["closure_group"],pmcid=pmcid,source_identity_input=identity_input,source_evidence=evidence,historical_structure_source=inputs[0] if r in builds else inputs[1],historical_structure_source_sha256=sha(ROOT/(inputs[0] if r in builds else inputs[1])),historical_development_exposed=True,role="design_build_only",source_identity_status="pending_independent_A3",dual_structure_status="pending_A4_A5_reconciliation",eligibility_not_self_granted=True,human_reviewed=False,actionable=False,evidence_closed=False,prediction_conditions_verified=False))
    save_rows("design_candidates.jsonl",candidates)
    sources={c["pmcid"]:c["source_identity_input"] for c in candidates}
    save_rows("design_source_identity_inputs.jsonl",list(sources.values()))
    save("design_inventory.json",dict(task=TASK,epoch_id="C-E01",candidate_count=len(candidates),strata=4,distinct_sources=len(sources),fresh_holdout_extracted=0,model_outcomes_read=False,scopes=[dict(scope_id="p7-c:"+center,center_class=center,build_reactions=[x["reaction_id"] for x in rr],distinct_acceptors=len({x.get("acceptor_smiles") or x.get("acceptor") for x in rr})) for center,rr in groups],pending=["A3 source identity","A4 and A5 independent graph extraction/reconciliation","A6 source closure registration"],errors=[]))
    outputs=["design_candidates.jsonl","design_source_identity_inputs.jsonl","design_inventory.json"]
    save("role_A1_design_manifest.json",dict(task=TASK,epoch_id="C-E01",agent_role="A1_C_Source_Scout",created_at=datetime.now(timezone.utc).isoformat(),input_manifest_sha256={p:sha(ROOT/p) for p in inputs},output_files_sha256={str((OUT/n).relative_to(ROOT)):sha(OUT/n) for n in outputs},source_evidence_pointers=[dict(pmcid=c["pmcid"],reaction_id=c["reaction_id"],source_evidence=c["source_evidence"]) for c in candidates],processed=8,passed=0,rejected=0,pending=8,counts=dict(processed=8,passed=0,rejected=0,pending=8),errors=[],unprocessed=[],holdout_read=False,model_outcomes_read=False,authority="proposal_only_pending_independent_verification"))
    print(json.dumps(dict(design_candidates=8,strata=4,sources=len(sources),manifest=str((OUT/"role_A1_design_manifest.json").relative_to(ROOT)))))
if __name__=="__main__":main()
