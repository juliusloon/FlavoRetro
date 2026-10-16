"""Asset-free regression keeps explicit skips; no real MCTS execution."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write
root=Path.cwd()
with tempfile.TemporaryDirectory() as empty:
    env={**os.environ,'FLAVORETRO_WORKSPACE':empty,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(root)}
    env.pop('FLAVORETRO_TASK016_LEDGER',None);env.pop('FLAVORETRO_TASK016_TRACE',None)
    result=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(root/'tests'),'-v'],env=env,cwd=root,text=True,capture_output=True)
    write('TASK-016','outputs/task016/v1/asset-free-regression-v2.log',result.stdout+result.stderr)
    print((result.stdout+result.stderr)[-650:]);assert result.returncode==0
    write('TASK-016','outputs/task016/v1/asset-free-regression-v2.json',json.dumps(dict(returncode=result.returncode,scope='empty external workspace; repository cwd retained for explicit triage config fixtures; 6 local-asset skips; no actual MCTS'),indent=2)+'\n')
