"""C-E02 R5 metadata discovery beyond OA-indexed metadata; scope remains frozen."""
import json,urllib.parse
from pathlib import Path
import scripts.task016_p7_c_e02_fresh as f
from scripts.task016_p7_c_e02_http import immutable_json,require_active
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file,verify_stage_chain
B=f.E/"fresh/C-E02-R5"
EXTRA=(
 "outputs/task016-p7/v1/C/E02/fresh/C-E02-R1/A6_source_reconciliation_v1/permanent_postscope_source_exposures.jsonl",
 "outputs/task016-p7/v1/C/E02/fresh/C-E02-R3/A6_source_reconciliation_v2/permanent_postscope_source_exposures.jsonl",
 "outputs/task016-p7/v1/C/E02/fresh/C-E02-R4/A6_source_reconciliation_v1/permanent_postscope_source_exposures.jsonl",
 "outputs/task016-p7/v1/C/E02/post_scope_internal_hypotheses/v1/permanent_name_hypothesis_exposure.jsonl",
 "outputs/task016-p7/v1/C/E02/post_scope_internal_hypotheses/v1/permanent_exposure_manifest.json")
def prepare():
    f.EXPOSURE_FILES=f.EXPOSURE_FILES+EXTRA
    tokens,files=f.exposures()
    for p in (f.SCOPE,f.G4,ROOT/"scripts/task016_p7_c_e02_http.py",ROOT/"scripts/task016_p7_c_e02_fresh.py",Path(__file__),ROOT/"scripts/task016_p7_source_harness.py",ROOT/"scripts/task016_p7_source_alias_closure.py"):
        files[f.rel(p)]=sha_file(p)
    verify_stage_chain(f.G4,sha_file(f.G4))
    terms=[
      ('("C-glycosyltransferase" OR "C-glucosyltransferase") AND (flavone OR flavones)',"primary_keyword"),
      ('("C-glycosylation" OR "C-glucosylation") AND (direct OR regioselective) AND flavonoid',"primary_keyword"),
      ('("GtUF6CGT" OR "MiCGT" OR "UGT708A3" OR "UGT708C1")',"enzyme_reverse"),
      ('"C-glycosyltransferase" AND (Dendrobium OR Gentiana OR Trollius)',"enzyme_reverse"),
      ('("C-glycosyltransferase" OR "C-glucosyltransferase") AND ("6-C" OR C6)',"primary_keyword")]
    qs=[]
    for term,route in terms:
        qs.append(dict(query=term,route=route,url=f.DISCOVERY_BASE+"search?"+urllib.parse.urlencode(dict(query=term,format="json",resultType="lite",pageSize=100)),payload="search"))
    for pmid in ("19411659",):
        for ep in ("citations","references"):
            qs.append(dict(query="MED/"+pmid+"/"+ep,route="citation_chase",url=f.DISCOVERY_BASE+"MED/"+pmid+"/"+ep+"?"+urllib.parse.urlencode(dict(format="json",pageSize=100,page=1)),payload=ep))
    for i,q in enumerate(qs,1):
        q.update(query_id="C-E02-R5-Q%02d"%i,database="EuropePMC",family="C",scope_id="p7-C-E02:flavone_6_C_glucoside_C3_H",reason="Post-G4 raw metadata, no OPEN_ACCESS restriction; lawful original routes planned separately; source aliases and all prior chemical exposures excluded",max_pages=1,max_objects=100)
    plan=dict(task=TASK,family="C",epoch_id="C-E02",batch_id="C-E02-R5",preregistered_at=now(),G4_pointer=f.pointer(f.G4),scope_pointer=f.pointer(f.SCOPE),files_sha256=files,historical_source_tokens=tokens,queries=qs,chemical_extraction_permitted=False,unknown_name_identity_fail_closed=True,metadata_title_selection_regex=r"C[- ]?(glycosyl|glucosyl)|glycosyltransferase|UGT708|\bCGT\b",maximum_primary_original_sources=20,primary_discovery_routes=["primary_keyword","enzyme_reverse","citation_chase"],route_completeness_not_assumed_from_one_metadata_page=True,permanent_name_hypotheses=19,future_holdout_name_synonym_identity_verification_required=True,source_alias_wrapper_required_for_all_admission=True,read_model_outcome=False,human_reviewed=False,approval_type="agent_delegated")
    immutable_json(B/"query_plan.json",plan);require_active(B/"query_plan.json")
    print(json.dumps(dict(plan=f.pointer(B/"query_plan.json"),queries=len(qs),chemistry=0)))
if __name__=="__main__":
    import sys
    if sys.argv[1]=="prepare":prepare()
    elif sys.argv[1]=="discover":f.discover("C-E02-R5")
    else:raise SystemExit("prepare|discover")
