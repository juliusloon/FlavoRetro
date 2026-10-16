"""C R8: exact previously selected PMC sources, official open-data metadata fallback only."""
import json,xml.etree.ElementTree as ET
from pathlib import Path
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import E,immutable_json,acquire,append,rows,require_active
B=E/"fresh/C-E02-R8"
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def main():
 p=B/"query_plan.json";old=E/"fresh/C-E02-R7/query_plan.json"
 inventory=E/"fresh/C-E02-R7/source_metadata_identity_inventory.v2.json"
 if not p.exists():
  x=json.loads(old.read_text())
  ins=[inventory,E/"fresh/C-E02-R7/root_A3_publication_identity_v2/role_A3_manifest.json",
       ROOT/"outputs/task016-p7/v1/SS/E02_design/new_source_actual_exposure_custodian_v3/permanent_exposure_manifest.json",
       ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/Petunia_dual_extraction_preregistration_v1.json",
       Path(__file__)]
  x.update(batch_id="C-E02-R8",preregistered_at=now(),agent_role="A2 deterministic raw-only fallback harness",stage="previously selected exact-PMC official open-data metadata fallback only",parent_R7_query_plan=ptr(old),primary_discovery_routes=["official_PMC_OA_open_data_exact_source_fallback"],maximum_HTTP_this_plan=2,maximum_primary_source_locator_candidates=2,queries=[dict(query_id=s+"-OFFICIAL-OA-INDEX",source_id=s,route="official PMC open-data exact known PMCID prefix, no chemical extraction",url="https://pmc-oa-opendata.s3.amazonaws.com/?list-type=2&prefix="+s+".",object_limit=2*1024**2) for s in ["PMC7720146","PMC2709393"]],role_prior_knowledge_disclosure="Root received R7 A4/A5 source-context progress summaries but has not read unfinished output graphs; these two exact metadata hints were selected in original R7 before those summaries. This deterministic harness reads only official index metadata.",contains_final_graphs=False,scientific_qualification=0,chemical_extraction_permitted=False,complete_rounds=0,saturation=False,fresh_admitted=0,new_SS_actual_exposure_pointer=ptr(ins[2]),latest_SS_Petunia_design_preregistration_pointer=ptr(ins[3]),Petunia_first_chemical_read_time_not_claimed_here=True,source_intake_not_G5_or_admission=True)
  x["files_sha256"]={**x["files_sha256"],**{str(q.relative_to(ROOT)):sha_file(q) for q in ins}}
  immutable_json(p,x)
 plan=require_active(p);done={r["query_id"] for r in rows(B/"official_index_execution.jsonl")}
 ns={"s":"http://s3.amazonaws.com/doc/2006-03-01/"}
 for q in plan["queries"]:
  if q["query_id"] in done:continue
  r=acquire(p,q["url"],"metadata",q["route"],object_limit=q["object_limit"])
  entries=[];error=None;truncated=None
  if r["status_code"]==200 and r["error"] is None:
   try:
    z=ET.fromstring((ROOT/r["path"]).read_bytes());truncated=z.findtext("s:IsTruncated",namespaces=ns)
    entries=[{k:c.findtext("s:"+k,namespaces=ns) for k in ["Key","Size","ETag","LastModified"]} for c in z.findall("s:Contents",ns)]
   except Exception as exc:error=type(exc).__name__+": "+str(exc)
  append(B/"official_index_execution.jsonl",dict(query_id=q["query_id"],source_id=q["source_id"],query_plan_pointer=ptr(p),raw_pointer={k:r.get(k) for k in ["attempt_id","path","sha256","bytes","status_code","error","started_at","finished_at"]},advertised_objects=entries,is_truncated_literal=truncated,parse_error=error,chemical_read=False,terminal=True,finished_at=now()))
  print(json.dumps(dict(source=q["source_id"],status=r["status_code"],advertised_objects=len(entries),truncated=truncated,parse_error=error)),flush=True)
if __name__=="__main__":main()
