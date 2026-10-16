"""SS exposed source-native product names: official raw database identity lookup only."""
import json,urllib.parse
from pathlib import Path
import scripts.task016_p7_ss_sources as io
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer,save_rows
B=ROOT/"outputs/task016-p7/v1/SS/E02_design/SS_second_acceptor_source_gaps_v1"
O=ROOT/"outputs/task016-p7/v1/SS/E02_design/second_acceptor_database_v1"
I=B/"common_raw_only_second_acceptor_input.v1.json"
def main():
    inp=json.loads(I.read_text())
    for p,h in inp["raw_input_files_sha256"].items():
        if sha_file(ROOT/p)!=h:raise ValueError("original raw SHA drift")
    plan=[]
    for h in inp["source_native_focus_hints"]:
        if h["source_id"]!="PMC10602602":continue
        literal=h["product_literal"]
        variants=[("literal_UTF8",literal),("typographic_ASCII_only",literal.replace("β","beta").replace("→","->"))]
        for label,name in variants:
            base="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"+urllib.parse.quote(name,safe="")
            for kind,suffix in (("structure_database","/property/Title,IUPACName,MolecularFormula,InChI,InChIKey,IsomericSMILES/JSON"),("metadata","/synonyms/JSON")):
                plan.append(dict(source_id=h["source_id"],candidate_id=h["candidate_id"],literal_source_product_name=literal,
                  lookup_name=name,variant=label,typography_projection_is_not_graph_guess=True,url=base+suffix,role=kind,phase="design",epoch_id="SS-E02",preregistered_at=now(),source_hint_pointer=pointer(I)))
    pp=O/"source_name_request_plan.json";immutable_json(pp,dict(task=TASK,agent_role="A2 SS Source Scout",at=now(),input_pointer=pointer(I),script_pointer=pointer(Path(__file__)),requests=plan,source_qualified=0))
    io.OUT=O;outputs=[]
    for r in plan:
        out=io.request(r["url"],r["role"],"SS-E02 already-exposed PMC106 literal product name official raw identity; no structure admission",phase="design",route="PubChem_source_literal_identity",epoch_id="SS-E02",max_bytes=8*1024**2)
        row=dict(request=r,response=out,contains_extractor_final_graph=False,evidence_eligible=False)
        outputs.append(row);io.append("raw_identity_intake.jsonl",row)
        print(json.dumps(dict(candidate_id=r["candidate_id"],variant=r["variant"],role=r["role"],status_code=out["status_code"],bytes=out["bytes"])),flush=True)
    immutable_json(O/"raw_identity_intake_summary.json",dict(task=TASK,at=now(),requests=len(plan),terminal=len(outputs),raw_200=sum(r["response"]["status_code"]==200 and not r["response"].get("error") for r in outputs),chemical_qualification_granted=0,new_MCTS=0))
    common=dict(inp);files=dict(inp["raw_input_files_sha256"])
    for r in outputs:files[r["response"]["path"]]=r["response"]["sha256"]
    common.update(created_at=now(),upstream_second_acceptor_input_pointer=pointer(I),raw_input_files_sha256=files,
      source_named_official_database_raw_identity_candidates=outputs,contains_A4_final_structures=False,contains_A5_final_structures=False,
      contains_new_SMILES=False,contains_raw_database_graph_fields=True,raw_graph_fields_are_not_extractor_graphs=True,
      source_qualified=0,new_HTTP=len(outputs),scientific_scope_or_qualification_changed=False)
    cp=O/"common_raw_only_second_acceptor_input.v2.json";immutable_json(cp,common)
    print(json.dumps(dict(common_input=pointer(cp),actual_HTTP=len(outputs),qualified=0)))
if __name__=="__main__":main()
