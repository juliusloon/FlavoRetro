"""Acquire the 64 actual publicly advertised PMC objects; no chemical reading."""
import json,importlib.util,hashlib,re,io,contextlib
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
O=ROOT/"outputs/task016-p7/v1/SS/E02_design/reference_discovery_r2/originals"
spec=importlib.util.spec_from_file_location("ss_bytes_transport",O/"ss_original_transport_v1.py")
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
def main():
 plan=json.loads((O/"official_advertised_byte_plan.json").read_text());done={x["request_id"] for x in t.rows(O/"official_byte_execution.jsonl")}
 for q in plan["requests"]:
  if q["request_id"] in done:continue
  with contextlib.redirect_stdout(io.StringIO()):
   rr=t.chain(q["url"],q["kind"],"actual publicly advertised PMC OA object",q["source_id"],{"request_id":q["request_id"],"plan_sha256":sha_file(O/"official_advertised_byte_plan.json"),"index_HTTP_pointer":q["index_HTTP_pointer"]},q["object_limit"])
  r=rr[-1];qc={};container=None
  if r.get("path"):
   p=ROOT/r["path"];data=p.read_bytes();etag=q["advertised_ETag"].strip('"')
   qc=dict(size_exact=len(data)==q["advertised_size"],SHA_actual_matches=sha_file(p)==r["sha256"],advertised_MD5_available=bool(re.fullmatch("[0-9a-fA-F]{32}",etag)),MD5_match=hashlib.md5(data).hexdigest()==etag.lower() if re.fullmatch("[0-9a-fA-F]{32}",etag) else None)
   if data.startswith(b"%PDF-"):container="PDF"
   elif data.startswith(b"\xff\xd8\xff"):container="JPEG"
   elif data.startswith(b"\x89PNG\r\n\x1a\n"):container="PNG"
   elif data.startswith(b"PK\x03\x04"):container="ZIP/OOXML"
   elif data.startswith(b"%!PS"):container="EPS/PostScript"
   else:container="other_or_failed_bytes"
  usable=r.get("status_code")==200 and not r.get("error") and qc.get("size_exact") and qc.get("SHA_actual_matches") and (not qc.get("advertised_MD5_available") or qc.get("MD5_match")) and container!="other_or_failed_bytes"
  t.append("official_byte_execution.jsonl",dict(request_id=q["request_id"],source_id=q["source_id"],advertised_key=q["advertised_key"],kind=q["kind"],physical_attempts=[{k:x.get(k) for k in ["path","sha256","bytes","status_code","attempt_id","error"]} for x in rr],container=container,container_QC=qc,usable_bytes_container_only=bool(usable),scientific_identity_unverified=True,chemical_science_read=False,terminal=True,finished_at=now()))
 rows=t.rows(O/"official_byte_execution.jsonl");assert len(rows)==64 and {x["request_id"] for x in rows}=={q["request_id"] for q in plan["requests"]}
 p=O/"official_byte_conservation.json"
 immutable_json(p,dict(task=TASK,created_at=now(),requests=64,terminal=64,pending=0,usable_original_byte_objects=sum(x["usable_bytes_container_only"] for x in rows),failed_or_deferred=sum(not x["usable_bytes_container_only"] for x in rows),main_PDF_usable=sum(x["usable_bytes_container_only"] and x["kind"]=="article_version" for x in rows),attachments_usable=sum(x["usable_bytes_container_only"] and x["kind"]=="attachment" for x in rows),all_original_namespace_HTTP=len(t.rows(O/"http_ledger.jsonl")),all_original_namespace_bytes=sum(x["bytes"] for x in t.rows(O/"http_ledger.jsonl")),source_qualified=0,fresh=0,chemical_read=False,complete_chemical_round=False,source_saturation=False))
 print(json.dumps(dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p),usable=sum(x["usable_bytes_container_only"] for x in rows),terminal=64,HTTP=len(t.rows(O/"http_ledger.jsonl")))))
if __name__=="__main__":main()
