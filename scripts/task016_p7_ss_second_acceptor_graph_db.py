"""Official identity lookup of already observed dual source graphs; no reaction qualification."""
import json,urllib.parse
from pathlib import Path
import scripts.task016_p7_ss_sources as io
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
B=ROOT/"outputs/task016-p7/v1/SS/E02_design"
I=B/"second_acceptor_A6_bounded_comparison_v1/four_existing_graph_candidates_comparison.json"
O=B/"second_acceptor_graph_identity_v1"
def main():
    comparisons=json.loads(I.read_text());plan=[]
    for x in comparisons:
        assert x["canonical_graph_equal"] and x["full_InChI_equal"] and x["A4_InChIKey"]==x["A5_InChIKey"]
        for k in ["A4_pointer","A5_partial_pointer"]:
            assert sha_file(ROOT/x[k]["path"])==x[k]["sha256"]
        base="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/"+urllib.parse.quote(x["A4_InChIKey"],safe="")
        for kind,suffix in [("structure_database","/property/Title,IUPACName,MolecularFormula,InChI,InChIKey,IsomericSMILES/JSON"),("metadata","/synonyms/JSON")]:
            plan.append(dict(candidate_id=x["candidate_id"],object_role=x["object_role"],source_derived_full_InChIKey=x["A4_InChIKey"],query_kind=kind,url=base+suffix,reference_pointer=pointer(I)))
    pp=O/"exact_source_graph_identity_request_plan.json"
    immutable_json(pp,dict(task=TASK,approval_type="agent_delegated",human_reviewed=False,preregistered_at=now(),agent_role="A2 source database identity scout",source_graph_observation_input=pointer(I),script_pointer=pointer(Path(__file__)),requests=plan,no_guessed_trivial_names=True,A5_partial_not_completed_extraction=True,source_qualification_granted=0,scope_change_permitted=False))
    io.OUT=O;rr=[]
    for q in plan:
        r=io.request(q["url"],q["query_kind"],"Already observed source-derived graph exact full InChIKey; database identity only, no enzyme/chemical qualification",phase="design",route="PubChem_exact_source_graph_InChIKey",epoch_id="SS-E02",max_bytes=8*1024**2)
        row=dict(request=q,response=r,database_hit_not_reaction_evidence=True,source_qualification_granted=0)
        io.append("raw_graph_identity_intake.jsonl",row);rr.append(row)
        print(json.dumps(dict(candidate_id=q["candidate_id"],object_role=q["object_role"],role=q["query_kind"],status_code=r["status_code"],bytes=r["bytes"])),flush=True)
    immutable_json(O/"raw_graph_identity_intake_summary.json",dict(task=TASK,created_at=now(),requests=len(plan),terminal=len(rr),successful_raw_200=sum(x["response"]["status_code"]==200 and not x["response"].get("error") for x in rr),source_qualification_granted=0,new_MCTS=0,no_scope_change=True))
if __name__=="__main__":main()
