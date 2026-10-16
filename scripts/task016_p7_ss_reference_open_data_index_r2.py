from pathlib import Path
import json,importlib.util,xml.etree.ElementTree as E
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
O=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/originals"
sp=importlib.util.spec_from_file_location("origtransport",O/"ss_original_transport_v1.py");t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
plan=json.loads((O/"official_open_data_index_plan.json").read_text());done={r["query_id"] for r in t.rows(O/"official_index_execution.jsonl")}
for q in plan["queries"]:
 if q["query_id"] in done:continue
 rr=t.chain(q["url"],"metadata",q["route"],q["source_id"],{"query_id":q["query_id"],"plan_sha256":sha_file(O/"official_open_data_index_plan.json")},q["object_limit"]);r=rr[-1];entries=[];error=None;truncated=None
 if r.get("status_code")==200 and not r.get("error"):
  try:
   root=E.fromstring((ROOT/r["path"]).read_bytes());ns={"s":"http://s3.amazonaws.com/doc/2006-03-01/"}
   truncated=root.findtext("s:IsTruncated",namespaces=ns)
   for c in root.findall("s:Contents",ns):
    entries.append({k:c.findtext("s:"+k,namespaces=ns) for k in ["Key","Size","ETag","LastModified"]})
  except Exception as e:error=type(e).__name__+": "+str(e)
 t.append("official_index_execution.jsonl",{"query_id":q["query_id"],"source_id":q["source_id"],"physical_attempts":[{k:x.get(k) for k in ["path","sha256","bytes","status_code","attempt_id"]} for x in rr],"advertised_objects":entries,"is_truncated_literal":truncated,"parse_error":error,"chemical_read":False,"terminal":True,"finished_at":now()})
 print(json.dumps({"source":q["source_id"],"objects":len(entries),"status":r.get("status_code"),"parse_error":error}),flush=True)
