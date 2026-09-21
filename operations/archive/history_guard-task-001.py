import os,json,sys,stat
from pathlib import Path
from operate import ROOT,digest,event,write
source=Path('/home/ljx/retro_synthesis')
def snapshot():
    result={}
    for base,ds,fs in os.walk(source,followlinks=False):
        for name in sorted(ds+fs):
            p=Path(base)/name; s=p.lstat(); row={'mode':stat.S_IMODE(s.st_mode),'size':s.st_size,'mtime_ns':s.st_mtime_ns}
            if p.is_symlink(): row['symlink']=os.readlink(p)
            elif p.is_file(): row['sha256']=digest(p)
            else: row={'mode':row['mode'],'kind':'directory'}
            result[str(p.relative_to(source))]=row
    return result
now=snapshot(); baseline=ROOT/'operations/history-before.json'
if sys.argv[1]=='before':
    if baseline.exists(): raise RuntimeError('baseline exists')
    write('TASK-001','operations/history-before.json',json.dumps(now,ensure_ascii=False,sort_keys=True))
    event('TASK-001','history_baseline',entries=len(now),sha256=digest(baseline))
    print('Baseline',len(now))
else:
    old=json.loads(baseline.read_text()); changes=[k for k in old.keys()|now.keys() if old.get(k)!=now.get(k)]
    result={'entries':len(now),'changed':changes,'unchanged':not changes}
    write('TASK-006','outputs/validation/history-integrity.json',json.dumps(result,indent=2))
    print(json.dumps(result)); sys.exit(bool(changes))
