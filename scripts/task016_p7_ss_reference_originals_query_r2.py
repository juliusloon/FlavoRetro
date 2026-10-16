"""Serial original intake, one physical request per preregistered public hop."""
import json,importlib.util,xml.etree.ElementTree as E
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
O=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/originals"
spec=importlib.util.spec_from_file_location("ss_orig_transport",O/"ss_original_transport_v1.py")
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
def main():
 plan=json.loads((O/"preregistered_locator_plan.json").read_text());done={r["query_id"] for r in t.rows(O/"original_query_execution.jsonl")}
 for q in plan["queries"]:
  if q["query_id"] in done:continue
  rr=t.chain(q["url"],q["kind"],q["route"],q["source_id"],{"query_id":q["query_id"],"plan_sha256":sha_file(O/"preregistered_locator_plan.json")},q["object_limit"]);r=rr[-1];container=None;error=None;projection=None
  if r.get("status_code")==200 and not r.get("error"):
   try:
    root=E.fromstring((ROOT/r["path"]).read_bytes());container=root.tag
    if root.tag=="article":
     f=root.find("front");title=f.find(".//article-title") if f is not None else None
     projection=dict(front_title="".join(title.itertext()) if title is not None else None,article_ids={x.get("pub-id-type"):"".join(x.itertext()) for x in f.findall(".//article-meta/article-id")} if f is not None else {},body_element_present=root.find("body") is not None,source_license_literals=["".join(x.itertext()) for x in root.findall(".//permissions/license")],public_media_hrefs=[dict(tag=x.tag,href=v,attributes={k:v for k,v in x.attrib.items() if not k.endswith("href")}) for x in root.iter() for k,v in x.attrib.items() if k.endswith("href") and x.tag in ["graphic","media","supplementary-material"]],chemical_body_read=False)
    elif root.tag=="OA":
     projection=dict(records=[dict(attributes=x.attrib,links=[dict(attributes=l.attrib) for l in x.findall("link")]) for x in root.findall(".//record")],errors=[dict(attributes=x.attrib,literal="".join(x.itertext())) for x in root.findall(".//error")],chemical_body_read=False)
   except Exception as e:error=type(e).__name__+": "+str(e)
  t.append("original_query_execution.jsonl",dict(query_id=q["query_id"],source_id=q["source_id"],kind=q["kind"],physical_attempts=[dict(path=x.get("path"),sha256=x.get("sha256"),bytes=x.get("bytes"),status_code=x.get("status_code"),attempt_id=x.get("attempt_id")) for x in rr],container=container,projection=projection,parse_error=error,terminal=True,chemical_science_read=False,finished_at=now()))
  print(json.dumps(dict(query=q["query_id"],status=r.get("status_code"),container=container,body_element=projection.get("body_element_present") if projection else None,parse_error=error)),flush=True)
 rows=t.rows(O/"original_query_execution.jsonl");assert len(rows)==12 and {x["query_id"] for x in rows}=={q["query_id"] for q in plan["queries"]}
 p=O/"original_query_conservation.json";immutable_json(p,dict(task=TASK,created_at=now(),planned=12,executed=12,terminal=12,pending=0,physical_HTTP=len(t.rows(O/"http_ledger.jsonl")),raw_bytes=sum(x["bytes"] for x in t.rows(O/"http_ledger.jsonl")),full_XML_body_containers=sum(bool((x.get("projection") or {}).get("body_element_present")) for x in rows),source_identity_verified=0,source_qualified=0,fresh=0,complete_chemical_round=False,source_saturation=False))
 print(json.dumps(dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p))))
if __name__=="__main__":main()
