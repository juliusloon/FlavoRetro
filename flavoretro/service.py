"""CLI and HTTP share this isolated live execution boundary."""
import json,os,subprocess,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from .contracts import SearchRequest
from .resources import ROOT,dumps,sha

def search(request:SearchRequest,run_root=None):
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex
    root=Path(run_root) if run_root else ROOT/'outputs/runs'
    folder=root/run_id;folder.mkdir(parents=True,exist_ok=False)
    req=request.model_dump();(folder/'request.json').write_text(dumps(req))
    envelope={'run_id':run_id,'request':req,'output':str(folder/'result.json')}
    start=time.monotonic();error=None
    env={**os.environ,'PYTHONHASHSEED':str(request.seed),'PYTHONPATH':str(ROOT),'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MPLCONFIGDIR':str(ROOT/'outputs/cache/matplotlib')}
    try:
        with (folder/'worker.log').open('w') as log:
            proc=subprocess.run([sys.executable,'-B','-m','flavoretro.worker'],input=json.dumps(envelope),text=True,stdout=log,stderr=subprocess.STDOUT,cwd=ROOT,env=env,timeout=sum(p['seconds'] for p in request.phases())+90)
        if proc.returncode: error={'code':'engine_error','message':'MCTS execution failed; inspect run worker.log','returncode':proc.returncode}
    except subprocess.TimeoutExpired: error={'code':'timeout','message':'Isolated MCTS exceeded wall-clock budget; worker terminated'}
    if error:
        result={'run_id':run_id,'status':'error','error':error,'execution_source':'live_attempt_failed','routes':[],'release_ready':False}
        (folder/'result.json').write_text(dumps(result))
    else: result=json.loads((folder/'result.json').read_text())
    manifest={'run_id':run_id,'status':result['status'],'wall_seconds':time.monotonic()-start,'files':{p.name:sha(p) for p in folder.iterdir() if p.is_file()}}
    (folder/'manifest.json').write_text(dumps(manifest))
    for p in folder.iterdir():p.chmod(0o444)
    return result
