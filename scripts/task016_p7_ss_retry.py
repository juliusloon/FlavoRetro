"""Preserve initial failures and execute at most one registered URL retry."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,request,rows,save,save_rows,now,sha
from scripts.task016_p7_ss_fresh import historical

def execute():
    plans={r["query_id"]:r for r in rows(OUT/"fresh_discovery_query_plan.jsonl")}
    failed=[r for r in rows(OUT/"fresh_query_execution.jsonl") if r["error"]]
    retryplans=[dict(plans[r["query_id"]],retry_id=r["query_id"]+":retry2",previous_response_sha256=r["response_sha256"],retry_registered_at=now(),maximum_attempts_per_url=2) for r in failed]
    if (OUT/"fresh_discovery_retry_plan.jsonl").exists():raise RuntimeError("RETRY_ALREADY_REGISTERED")
    save_rows("fresh_discovery_retry_plan.jsonl",retryplans)
    hits=[];execs=[];seen=historical()
    for q in retryplans:
        res=request(q["url"],"metadata","Registered retry after transient official API failure; original response preserved",phase="fresh",scope_id="SS-E01-bank",route=q["route"])
        candidates=[]
        if res["status_code"]==200 and not res["error"]:
            data=json.loads((ROOT/res["path"]).read_text())
            candidates=data.get("resultList",{}).get("result",[]) if q["endpoint"]=="epmc" else data.get("citationList",{}).get("citation",[]) or data.get("referenceList",{}).get("reference",[])
        execs.append(dict(retry_id=q["retry_id"],query_id=q["query_id"],round=q["round"],route=q["route"],executed_at=now(),http_query_id=res["query_id"],returned=len(candidates),error=res["error"],response_sha256=res["sha256"],raw_response=res["path"]))
        for ix,rec in enumerate(candidates):
            pmcid=rec.get("pmcid");doi=rec.get("doi") or rec.get("DOI");pmid=rec.get("pmid") or (rec.get("id") if rec.get("source")=="MED" else None)
            title=rec.get("title",rec.get("articleTitle",""));title=" ".join(title) if isinstance(title,list) else title
            key=pmcid or doi or str(rec.get("id",rec.get("key","")))+"|"+title
            hits.append(dict(discovery_id=q["retry_id"]+":"+str(ix),query_id=q["query_id"],retry_id=q["retry_id"],round=q["round"],route=q["route"],pmcid=pmcid,pmid=pmid,doi=doi,title=title,id=rec.get("id"),source=rec.get("source"),isOpenAccess=rec.get("isOpenAccess"),discovery_key=key,metadata_only=True,chemical_extracted=False,disposition="rejected_historical_source_exposure" if pmcid in seen else "metadata_only_pending_original_source",historical_source=pmcid in seen,raw_response=res["path"],scope_freeze_sha256=sha(OUT/"scope_freeze.json")))
        save_rows("fresh_discovery_retry_execution.jsonl",execs);save_rows("fresh_discovery_retry_hits.jsonl",hits)
    unique={}
    for r in rows(OUT/"fresh_discovery_hits.jsonl")+hits:unique.setdefault(r["discovery_key"],[]).append(r)
    ds=[dict(discovery_key=k,pmcid=next((h["pmcid"] for h in v if h.get("pmcid")),None),pmid=next((h["pmid"] for h in v if h.get("pmid")),None),doi=next((h["doi"] for h in v if h.get("doi")),None),title=v[0]["title"],routes=sorted({h["route"] for h in v}),rounds=sorted({h["round"] for h in v}),hit_count=len(v),historical_source=any(h["historical_source"] for h in v),disposition="rejected_historical_source_exposure" if any(h["historical_source"] for h in v) else "metadata_only_pending_original_source",chemical_extracted=False,admitted=False,evidence_eligible=False) for k,v in unique.items()]
    save_rows("fresh_source_dispositions_v2.jsonl",ds)
    save("fresh_discovery_retry_summary.json",dict(planned=len(retryplans),executed=len(execs),conserved=len(retryplans)==len(execs),failures=sum(bool(e["error"]) for e in execs),returned=len(hits),unique_sources_after_retry=len(ds),original_failures_preserved=True,saturation_claimed=False))
    print(dict(retries=len(execs),returned=len(hits),unique=len(ds),failures=sum(bool(e["error"]) for e in execs)))
if __name__=="__main__":execute()
