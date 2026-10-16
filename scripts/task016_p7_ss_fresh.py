"""SS post-freeze, three-route fresh acquisition with query/result conservation."""
import json,sys,urllib.parse,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,save,save_rows,request,sha,now
QUERIES=[
 dict(round=1,route="EuropePMC_keyword",query='(rhamnosyltransferase OR rutinoside) AND (flavonoid OR flavone OR flavonol) AND OPEN_ACCESS:Y',endpoint="epmc",reason="Independent post-scope keyword literature discovery"),
 dict(round=1,route="Crossref_bibliographic",query="flavonoid glucoside 1,6 rhamnosyltransferase",endpoint="crossref",reason="Independent bibliographic index and DOI discovery"),
 dict(round=1,route="Citation_graph",query="MED/35947689/citations",endpoint="citation",reason="Forward citation graph of historical Chrysanthemum build paper; metadata only then closure check"),
 dict(round=2,route="EuropePMC_keyword",query='(UGT79 OR UGT91 OR rhamnosyltransferase) AND (flavonoid OR flavone OR flavonol) AND OPEN_ACCESS:Y',endpoint="epmc",reason="Second round broadened enzyme-family discovery"),
 dict(round=2,route="Crossref_bibliographic",query="rutin biosynthesis rhamnosyltransferase substrate promiscuity",endpoint="crossref",reason="Second round distinct product/enzyme route in bibliographic index"),
 dict(round=2,route="Citation_graph",query="MED/35947689/references",endpoint="citation",reason="Backward citation graph to primary original reaction papers; closure checked independently"),
]
def historical():
    seen=set()
    for line in (ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl").read_text().splitlines():
        row=json.loads(line)
        for token in row["closure_tokens"]:
            for pmcid in re.findall(r"PMC\d+",token):seen.add(pmcid)
    return seen
def url_for(q):
    if q["endpoint"]=="epmc":return "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query=q["query"],format="json",pageSize=100,resultType="core"))
    if q["endpoint"]=="crossref":return "https://api.crossref.org/works?"+urllib.parse.urlencode({"query.bibliographic":q["query"],"rows":100})
    return "https://www.ebi.ac.uk/europepmc/webservices/rest/"+q["query"]+"?format=json&pageSize=1000"
def execute():
    freeze=OUT/"scope_freeze.json"
    if not freeze.exists():raise RuntimeError("SS_SCOPE_NOT_FROZEN")
    f=json.loads(freeze.read_text())
    if not f["independently_verified"]:raise RuntimeError("INDEPENDENT_SS_SCOPE_VERIFICATION_PENDING")
    for path,expected in f["files_sha256"].items():
        p=ROOT/path if path.startswith(("outputs/","flavoretro/")) else OUT/path
        if sha(p)!=expected:raise RuntimeError("SS_SCOPE_SHA_DRIFT")
    scope_ids=f["scope_ids"]
    plans=[dict(q,query_id=f"SS-FRESH-R{q['round']}-{q['route']}",family="SS",epoch_id="SS-E01",scope_ids=scope_ids,url=url_for(q),max_pages=1,max_objects=100 if q["endpoint"]!="citation" else 1000,registered_at=now(),chemical_extract_allowed_after=f["frozen_at"],scope_freeze_sha256=sha(freeze)) for q in QUERIES]
    if (OUT/"fresh_discovery_query_plan.jsonl").exists():raise RuntimeError("FRESH_QUERY_PLAN_ALREADY_EXECUTED")
    save_rows("fresh_discovery_query_plan.jsonl",plans)
    seen=historical();hits=[];execs=[]
    for q in plans:
        result=request(q["url"],"metadata",q["reason"],phase="fresh",scope_id="SS-E01-bank",route=q["route"])
        candidates=[]
        if result["status_code"]==200:
            payload=json.loads((ROOT/result["path"]).read_text())
            if q["endpoint"]=="epmc":candidates=payload.get("resultList",{}).get("result",[])
            elif q["endpoint"]=="crossref":candidates=payload.get("message",{}).get("items",[])
            else:candidates=payload.get("citationList",{}).get("citation",[]) or payload.get("referenceList",{}).get("reference",[])
        execs.append(dict(query_id=q["query_id"],round=q["round"],route=q["route"],executed_at=now(),http_query_id=result["query_id"],returned=len(candidates),explicitly_skipped=False,error=result["error"],response_sha256=result["sha256"]))
        for index,rec in enumerate(candidates):
            pmcid=rec.get("pmcid");doi=rec.get("doi") or rec.get("DOI");pmid=rec.get("pmid") or (rec.get("id") if rec.get("source")=="MED" else None)
            title=rec.get("title",rec.get("articleTitle",""));title=" ".join(title) if isinstance(title,list) else title
            key=pmcid or doi or str(rec.get("id",rec.get("key","")))+"|"+title
            hits.append(dict(discovery_id=q["query_id"]+":"+str(index),query_id=q["query_id"],round=q["round"],route=q["route"],pmcid=pmcid,pmid=pmid,doi=doi,title=title,id=rec.get("id"),source=rec.get("source"),isOpenAccess=rec.get("isOpenAccess"),discovery_key=key,metadata_only=True,chemical_extracted=False,disposition="rejected_historical_source_exposure" if pmcid in seen else "metadata_only_pending_original_source",historical_source=pmcid in seen,raw_response=result["path"],scope_freeze_sha256=sha(freeze)))
        save_rows("fresh_query_execution.jsonl",execs);save_rows("fresh_discovery_hits.jsonl",hits)
    unique={}
    for hit in hits:unique.setdefault(hit["discovery_key"],[]).append(hit)
    dispositions=[dict(discovery_key=k,pmcid=v[0]["pmcid"],pmid=next((h["pmid"] for h in v if h.get("pmid")),None),doi=v[0]["doi"],title=v[0]["title"],routes=sorted({h["route"] for h in v}),rounds=sorted({h["round"] for h in v}),hit_count=len(v),historical_source=any(h["historical_source"] for h in v),disposition="rejected_historical_source_exposure" if any(h["historical_source"] for h in v) else "metadata_only_pending_original_source",chemical_extracted=False,admitted=False,evidence_eligible=False) for k,v in unique.items()]
    save_rows("fresh_source_dispositions.jsonl",dispositions)
    save("fresh_discovery_summary.json",dict(task_id="TASK-016-P7",epoch_id="SS-E01",scope_freeze_sha256=sha(freeze),routes=len({e["route"] for e in execs}),rounds=2,planned_queries=len(plans),executed_queries=len(execs),skipped_queries=0,plan_conservation=len(plans)==len(execs),discovered_hits=len(hits),unique_sources=len(dispositions),historical_rejected=sum(x["historical_source"] for x in dispositions),metadata_only=sum(not x["historical_source"] for x in dispositions),admitted=0,deferred=0,chemical_rejected=0,original_source_review_complete=False,saturation_claimed=False,no_model_outcomes_read=True))
    print(dict(planned=len(plans),executed=len(execs),hits=len(hits),unique=len(dispositions),historical=sum(x["historical_source"] for x in dispositions)))
if __name__=="__main__":execute()
