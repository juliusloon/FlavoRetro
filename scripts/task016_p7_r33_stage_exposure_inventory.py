"""R33: seal late G5/G6 provenance separately from the legacy JSONL inventory."""
import json,re,hashlib
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import put,sha,load,lines,now
from scripts.task016_p7_closure_harness import source_tokens,closure_tokens
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"governance/R33-prior-stage-exposure-supplement-v1"
def nodes(obj):
 if isinstance(obj,dict):
  yield obj
  for v in obj.values():yield from nodes(v)
 elif isinstance(obj,list):
  for v in obj:yield from nodes(v)
def main():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 ledger=B/"epoch_ledger.jsonl";stage_map={}
 for r in lines(ledger):
  if r.get("epoch_id") in ("C-E02","SS-E02") and r.get("stage") in ("G5_FRESH_HOLDOUT_ACQUIRE","G6_IDENTITY_STRUCTURE_ADMIT") and r.get("status")=="active":
   p=r["stage_manifest_path"];h=r["stage_manifest_sha256"]
   if p in stage_map and stage_map[p]!=h:raise RuntimeError("CONFLICT")
   stage_map[p]=h
 out=[];origins={};issues=[]
 for stage,h in stage_map.items():
  assert sha(Path(stage))==h
  m=load(Path(stage));tokens=set();docs=[]
  for p,expected in m["files"].items():
   path=Path(p)
   if path.suffix not in (".json",".jsonl") or not p.startswith("outputs/") or "prior_exposure_inventory" in p or path.name=="exposure_ledger.jsonl":continue
   actual=sha(path)
   # immutable original-science role inputs checked; drift retained, never claimed clear.
   origins[p]=actual
   if actual!=expected:issues.append(dict(stage=stage,path=p,expected_SHA=expected,actual_SHA=actual,classification="bound_input_changed_keep_pending"))
   if path.suffix==".jsonl":objects=lines(path)
   else:objects=[load(path)]
   for obj in objects:
    for node in nodes(obj):
     n={str(k).casefold():v for k,v in node.items()}
     try:tokens.update(closure_tokens(n))
     except Exception:tokens.update(source_tokens(n))
     for k,v in n.items():
      if k in {"doi","source_doi","resource_doi"} and isinstance(v,str):
       for hit in re.findall(r"10\.\d{4,9}/[^\s<>]+",v,re.I):tokens.add("doi:"+hit.rstrip(".,);").lower())
      if k in {"pmid","source_pmid"} and isinstance(v,(str,int)) and str(v).isdigit():tokens.add("pmid:"+str(v))
      if k in {"pmcid","source_id","source_pmcid","article_id"} and isinstance(v,str):
       for hit in re.findall(r"PMC\d+",v,re.I):tokens.add("article:"+hit.upper())
   docs.append(dict(path=p,sha256=actual,stage_bound_SHA=expected))
  out.append(dict(origin_stage_path=stage,origin_stage_sha256=h,epoch_id=m["epoch_id"],development_exposed=True,exposure_type="prior_stage_conservative_exclusion",scientific_content_read=None,closure_tokens=sorted(tokens),source_documents=docs,semantic_identity_clearance=False,reason="Registered old G5/G6 source and scientific role artifacts, including JSON read receipts outside exposure JSONL. Conservative exclusion; metadata-only semantic exceptions require A6."))
 path=O/"prior_stage_exposure_rows.jsonl"
 write(T,str(path),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in out))
 put(O/"inventory_provenance.json",dict(task=T,at=now(),agent_role="A0",approval_type="agent_delegated",human_reviewed=False,epoch_ledger_path=str(ledger),epoch_ledger_SHA=sha(ledger),registered_stage_SHA=stage_map,stage_count=len(out),documents_SHA=origins,document_count=len(origins),input_drift_issues=issues,output_path=str(path),output_SHA=sha(path),legacy_inventory_path=str(B/"governance/prior_exposure_inventory_v2/prior_exposure_rows.jsonl"),legacy_inventory_SHA=sha(B/"governance/prior_exposure_inventory_v2/prior_exposure_rows.jsonl"),identity_clearance=False,A6_source_alias_review_pending=True,actual_G7_current_exposure_receipt=False))
 print(json.dumps(dict(stages=len(out),documents=len(origins),drift_issues=len(issues),identity_clearance=False)))
if __name__=="__main__":main()
