"""TASK-016-P2 bounded public acquisition; immutable bytes and conserved attempts."""
import hashlib,json,threading,time,sys
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
TASK="TASK-016-P2";OUT=ROOT/"outputs/task016-p2/v1";RAW=ROOT/"data/raw/task016-p2/2026-10-06"
from scripts.operate import write,event
LOCK=threading.Lock()
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []
def save(name,v,jl=False):
    text="".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in v) if jl else json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    write(TASK,str((OUT/name).relative_to(ROOT)),text)
def append(name,v):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a') as f:f.write(json.dumps(v,ensure_ascii=False,sort_keys=True)+'\n')
    event(TASK,'append_evidence',path=str(p.relative_to(ROOT)),entry=v)
def stamp():return datetime.now(timezone.utc).isoformat()
def get(url,provider,role,name=None,limit=32*1024**2):
    with LOCK:
        history=rows(OUT/'acquisition_attempts.jsonl')
        inherited=[]
        for p in [ROOT/'outputs/task016-p1/v1/acquisition_attempts.jsonl',ROOT/'outputs/task016/v1/acquisition_attempts.jsonl']:
            inherited.extend(rows(p))
        good=[r for r in history+inherited if r.get('url')==url and r.get('status')=='raw_available' and r.get('path')]
        if good:
            r=good[-1];assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
            if r not in history:append('reused_files.jsonl',dict(**r,reuse_task=TASK,reused_at=stamp()))
            return r
        previous=[r for r in history if r.get('url')==url]
        if len(previous)>=2:return previous[-1]
    for attempt in range(len(previous)+1,3):
        with LOCK:
            history=rows(OUT/'acquisition_attempts.jsonl')
            external=rows(OUT/'external_discovery_receipts.jsonl')
            reservations=rows(OUT/'acquisition_reservations.jsonl')
            assert len(reservations)+sum(r['request_units'] for r in external)<2500,'HTTP attempt ceiling'
            total=sum(r.get('bytes',0) for r in history)
            done={(r['url'],r['attempt']) for r in history}
            reserved=sum(r.get('limit',0) for r in reservations if (r['url'],r['attempt']) not in done)
            assert total+reserved+limit<=2*1024**3,'raw byte ceiling'
            if role in ['fullTextXML','supplement']:
                cap=120 if role=='fullTextXML' else 240
                assert len({r['url'] for r in history if r['content_role']==role}|{url})<=cap,'article/attachment ceiling'
            key=hashlib.sha256(url.encode()).hexdigest()[:24]
            target=RAW/provider/key/(role+'.attempt-'+str(attempt))
            assert not target.exists(),'immutable raw snapshot'
            reservation=dict(url=url,provider=provider,content_role=role,name=name,attempt=attempt,status='in_progress',limit=limit,started_at=stamp())
            append('acquisition_reservations.jsonl',reservation)
        data=b'';status=None;error=None;headers={};wait=1
        try:
            with urlopen(Request(url,headers={'User-Agent':'FlavoRetro-TASK016-P2/0.1'}),timeout=25) as response:
                status=response.status;headers={k:response.headers.get(k) for k in ['Content-Type','ETag','Last-Modified']};data=response.read(limit+1)
                if len(data)>limit:raise ValueError('per-file bound exceeded')
        except HTTPError as exc:
            status=exc.code;error=str(exc);data=exc.read(min(limit,1024**2))
            try:wait=min(45,max(1,int(exc.headers.get('Retry-After','1'))))
            except ValueError:wait=2
        except Exception as exc:error=f'{type(exc).__name__}: {exc}'
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o444)
        result=dict(**{k:v for k,v in reservation.items() if k!='status'},path=str(target.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status_code=status,headers=headers,error=error,status='raw_available' if status==200 and not error else 'unavailable',acquired_at=stamp())
        with LOCK:append('acquisition_attempts.jsonl',result)
        event(TASK,'open_download',**result)
        if result['status']=='raw_available' or status in [400,401,403,404,429]:return result
        if attempt<2:time.sleep(wait)
    return result
