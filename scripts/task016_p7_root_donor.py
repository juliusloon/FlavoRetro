"""One preregistered authoritative donor query; immutable bytes, bounded attempts."""
import hashlib,json,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import write,event
R=Path(__file__).resolve().parents[1];O=R/"outputs/task016-p7/v1/root-acquisition"
def main():
    url="https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/UDP-glucose/property/Title,IUPACName,MolecularFormula,InChI,InChIKey,IsomericSMILES/JSON"
    plan=dict(query_id="ROOT-DESIGN-UDP-01",route="PubChem",phase="design",family="C",query="UDP-glucose",url=url,max_attempts=2,reason="independent complete donor identity/structure",max_objects=1)
    write("TASK-016-P7",str((O/"query_plan.json").relative_to(R)),json.dumps([plan],sort_keys=True,indent=2)+"\n")
    attempts=[]
    for i in [1,2]:
        before=datetime.now(timezone.utc).isoformat();data=b"";status=None;error=None
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"FlavoRetro research provenance/0.1"})
            with urllib.request.urlopen(req,timeout=25) as f:
                status=f.status;data=f.read(1024*1024+1)
            if len(data)>1024*1024:raise RuntimeError("per-file limit")
        except Exception as e:error=str(e)
        rel="data/raw/task016-p7/root/udp-glucose-attempt-"+str(i)+".json"
        p=R/rel;p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():raise RuntimeError("immutable raw file exists")
        p.write_bytes(data);h=hashlib.sha256(data).hexdigest()
        event("TASK-016-P7","write_binary",path=rel,before=None,after=h,bytes=len(data))
        attempts.append(dict(query_id=plan["query_id"],attempt=i,url=url,path=rel,sha256=h,bytes=len(data),status_code=status,error=error,role="structure_database",started_at=before,finished_at=datetime.now(timezone.utc).isoformat(),license="PubChem data policy",redistribution="not_packaged"))
        if status==200 and not error:break
    write("TASK-016-P7",str((O/"http_attempts.jsonl").relative_to(R)),"".join(json.dumps(a,sort_keys=True)+"\n" for a in attempts))
    write("TASK-016-P7",str((O/"query_execution.json").relative_to(R)),json.dumps([dict(query_id=plan["query_id"],status="executed",return_count=1 if attempts[-1]["status_code"]==200 else 0,http_attempts=len(attempts))],sort_keys=True,indent=2)+"\n")
    print(dict(attempts=len(attempts),bytes=sum(a["bytes"] for a in attempts),status=attempts[-1]["status_code"]))
if __name__=="__main__":main()
