"""Independent SS source identity, through JATS and official Europe PMC metadata."""
import json,urllib.parse,urllib.request,hashlib
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import write,event
from scripts.task016_p7_orchestrate import sha_file,save_json,role_manifest
from scripts.task016_p7_identity_harness import parse_jats,verify_identity
from scripts.task016_p7_design_identity import european
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/SS"
def main():
    source=json.loads((O/"design_source_intake.json").read_text())
    plans=[dict(query_id="ROOT-SS-IDENTITY-"+s["pmcid"],pmcid=s["pmcid"],route="Europe PMC official metadata",phase="design_identity",url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode(dict(query="PMCID:"+s["pmcid"],format="json",resultType="core",pageSize=2)),max_attempts=2) for s in source]
    save_json(O/"root_identity_query_plan.json",plans,immutable=True)
    attempts=[];results=[]
    for s,p in zip(source,plans):
        good=None
        for i in [1,2]:
            rel="data/raw/task016-p7/root/"+s["pmcid"]+"-identity-attempt-"+str(i)+".json"; path=R/rel
            if path.exists():
                data=path.read_bytes();code=200;err=None
            else:
                data=b"";code=None;err=None;start=datetime.now(timezone.utc).isoformat()
                try:
                    with urllib.request.urlopen(urllib.request.Request(p["url"],headers={"User-Agent":"FlavoRetro research provenance/0.1"}),timeout=25) as f:code=f.status;data=f.read(2*1024**2)
                except Exception as e:err=str(e)
                path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
                event("TASK-016-P7","write_binary",path=rel,before=None,after=sha_file(path),bytes=len(data))
                attempts.append(dict(query_id=p["query_id"],attempt=i,url=p["url"],path=rel,sha256=sha_file(path),bytes=len(data),status_code=code,error=err,role="metadata",started_at=start,finished_at=datetime.now(timezone.utc).isoformat()))
            if code==200 and not err:good=path;break
        if good is None:raise RuntimeError("authoritative metadata unavailable "+s["pmcid"])
        jats=parse_jats(R/s["xml"]["path"],dict(path=s["xml"]["path"],sha256=sha_file(R/s["xml"]["path"])))
        em=european(good)
        if jats["metadata"].get("pages") and not jats["metadata"].get("article_number"):em["metadata"]["pages"]=em["metadata"].pop("article_number")
        meta=json.loads((R/s["metadata"]["path"]).read_text())
        claim={k:meta.get(k) for k in ["pmcid","pmid","doi","title"]}
        v=verify_identity(claim,[jats,em]);v["pmcid"]=s["pmcid"];v["scope_role"]="design_build_only";results.append(v)
    a_path=O/"root_identity_http_attempts.jsonl"
    if attempts:
        old=a_path.read_text() if a_path.exists() else ""
        write("TASK-016-P7",str(a_path.relative_to(R)),old+"".join(json.dumps(x,sort_keys=True)+"\n" for x in attempts))
    p=O/"source_identity_verification.jsonl";write("TASK-016-P7",str(p.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in results))
    save_json(O/"role_A3_identity_manifest.json",role_manifest("A3 Source Identity Verifier","SS-E01",[O/"design_source_intake.json"]+[R/x["path"] for x in attempts],[p],dict(processed=len(results),passed=sum(x["source_identity_verified"] for x in results),pending=sum(not x["source_identity_verified"] for x in results),rejected=0),pointers=[p for x in results for p in x["authoritative_evidence_pointers"]]))
    print([dict(pmcid=x["pmcid"],verified=x["source_identity_verified"],conflicts=x["conflict_fields"]) for x in results])
if __name__=="__main__":main()
