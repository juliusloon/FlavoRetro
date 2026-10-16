"""Bounded immutable public source snapshots and shared acquisition accounting."""
import fcntl,hashlib,json,threading,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
TASK="TASK-016-P1"; OUT=ROOT/"outputs/task016-p1/v1"; RAW=ROOT/"data/raw/task016-p1/2026-10-06"
from scripts.operate import event,write
_LOCK=threading.Lock()
def rows(path):return [json.loads(s) for s in Path(path).read_text().splitlines()] if Path(path).exists() else []
def save(name,value,jl=False):
    payload="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in value) if jl else json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    write(TASK,str((OUT/name).relative_to(ROOT)),payload)
def get(url,provider,role,name=None,limit=32*1024**2):
    key=hashlib.sha256(url.encode()).hexdigest()[:20]
    ledger=OUT/"acquisition_attempts.jsonl"; ledger.parent.mkdir(parents=True,exist_ok=True)
    history=[r for r in rows(ledger) if r['url']==url]
    good=[r for r in history if r['status']=='raw_available']
    if good:
        r=good[-1];assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'];return r
    if len(history)>=2:return history[-1]
    for attempt in range(len(history)+1,3):
        with _LOCK:
            existing=rows(ledger)
            assert len(existing)<4000,"acquisition attempt ceiling"
            total=sum(p.stat().st_size for p in RAW.rglob('*') if p.is_file()) if RAW.exists() else 0
            assert total+limit<=5*1024**3,"raw byte budget"
        target=RAW/provider/(name or key)/f"{role}.attempt-{attempt}"
        assert not target.exists(),"immutable raw snapshot"
        status=None;error=None;data=b"";retry_after=1
        try:
            with urlopen(Request(url,headers={'User-Agent':'FlavoRetro-TASK016-P1/0.1'}),timeout=25) as response:
                status=response.status;data=response.read(limit+1)
                if len(data)>limit:raise ValueError('per-file bound exceeded')
        except HTTPError as exc:
            status=exc.code;error=str(exc);data=exc.read(min(limit,1024**2))
            try:retry_after=min(45,max(1,int(exc.headers.get('Retry-After','1'))))
            except ValueError:retry_after=2
        except Exception as exc:error=f'{type(exc).__name__}: {exc}'
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o444)
        r=dict(url=url,provider=provider,content_role=role,name=name,attempt=attempt,path=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status_code=status,error=error,status='raw_available' if status==200 and not error else 'unavailable',acquired_at=datetime.now(timezone.utc).isoformat())
        with _LOCK:
            with ledger.open('a') as f:
                fcntl.flock(f,fcntl.LOCK_EX);f.write(json.dumps(r,sort_keys=True)+'\n');f.flush();fcntl.flock(f,fcntl.LOCK_UN)
            event(TASK,'open_download',**r)
        if r['status']=='raw_available' or status in [400,401,403,404,429]:return r
        if attempt<2:time.sleep(retry_after)
    return r
