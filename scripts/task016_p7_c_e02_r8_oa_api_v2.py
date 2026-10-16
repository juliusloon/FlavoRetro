"""C R8 v2: official PMC OA API metadata; prior empty S3 listings are not absence."""
import json,xml.etree.ElementTree as ET
from scripts.task016_p7_orchestrate import ROOT,now,sha_file
from scripts.task016_p7_c_e02_http import E,immutable_json,acquire,append,rows,require_active
B=E/"fresh/C-E02-R8"
def ptr(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))
def main():
 p=B/"query_plan.v2.json"
 if not p.exists():
  prev=B/"query_plan.json";x=json.loads(prev.read_text())
  execution=B/"official_index_execution.jsonl";rr=rows(execution);assert len(rr)==2 and all(z["terminal"] for z in rr)
  x.update(preregistered_at=now(),parent_query_plan=ptr(prev),prior_terminal_execution=ptr(execution),stage="exact-source official PMC OA API metadata fallback after two empty official S3 indexes",maximum_HTTP_this_plan=2,maximum_cumulative_HTTP_R8_preregistered=4,primary_discovery_routes=["official_PMC_OA_API_metadata"],queries=[dict(query_id=s+"-OFFICIAL-OA-API",source_id=s,url="https://pmc.ncbi.nlm.nih.gov/utils/oa/oa.fcgi?id="+s,route="official PMC OA API exact PMCID; metadata response only",object_limit=2*1024**2) for s in ["PMC7720146","PMC2709393"]])
  x["files_sha256"].update({str(prev.relative_to(ROOT)):sha_file(prev),str(execution.relative_to(ROOT)):sha_file(execution),str(ROOT/"scripts/task016_p7_c_e02_r8_oa_api_v2.py").removeprefix(str(ROOT)+"/"):sha_file(ROOT/"scripts/task016_p7_c_e02_r8_oa_api_v2.py")})
  immutable_json(p,x)
 plan=require_active(p);done={r["query_id"] for r in rows(B/"official_oa_api_execution.jsonl")}
 for q in plan["queries"]:
  if q["query_id"] in done:continue
  r=acquire(p,q["url"],"metadata",q["route"],object_limit=q["object_limit"])
  info=None;parse_error=None
  if r["status_code"]==200 and not r["error"]:
   try:
    z=ET.fromstring((ROOT/r["path"]).read_bytes())
    info=dict(root_tag=z.tag,errors=[dict(attributes=n.attrib,text="".join(n.itertext())) for n in z.findall(".//error")],records=[dict(attributes=n.attrib,links=[x.attrib for x in n.findall("link")]) for n in z.findall(".//record")])
   except Exception as e:parse_error=type(e).__name__+": "+str(e)
  append(B/"official_oa_api_execution.jsonl",dict(query_id=q["query_id"],source_id=q["source_id"],plan_pointer=ptr(p),raw_pointer={k:r.get(k) for k in ["attempt_id","path","sha256","bytes","status_code","error","started_at","finished_at"]},metadata=info,parse_error=parse_error,terminal=True,chemical_read=False,original_scientific_body_read=False))
  print(json.dumps(dict(source=q["source_id"],status=r["status_code"],metadata=info,parse_error=parse_error)),flush=True)
if __name__=="__main__":main()
