"""Verify the installed wheel outside the checkout, with and without local assets."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("--workspace",required=True)
args=parser.parse_args()
workspace=Path(args.workspace).resolve()
out=workspace/"outputs/validation"/("package-"+uuid.uuid4().hex[:8])
out.mkdir(parents=True)
results={}
with tempfile.TemporaryDirectory() as scratch:
    env={**os.environ,"FLAVORETRO_WORKSPACE":scratch,"PYTHONDONTWRITEBYTECODE":"1"}
    probe="""import json, sys; from flavoretro.workspace import PACKAGE, root; from flavoretro.contracts import SearchRequest; print(json.dumps({'package':str(PACKAGE),'workspace':str(root()),'python':sys.executable,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'sys_path':sys.path,'phases':SearchRequest(smiles='CCO').phases()}))"""
    installed=subprocess.run([sys.executable,"-I","-B","-c",probe],cwd=scratch,env=env,text=True,capture_output=True,check=True)
    info=json.loads(installed.stdout)
    assert str(workspace/"flavoretro") != info["package"], info
    assert not any("miniforge3/envs/retro" in p or "retro_synthesis" in p for p in info["sys_path"])
    results["installed_probe"]=info
    results["cli_help"]=subprocess.run([sys.executable,"-I","-B","-m","flavoretro.cli","--help"],cwd=scratch,env=env,capture_output=True,check=True).returncode==0
    # Reserve an ephemeral port without depending on an already-running checkout service.
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1",0));port=s.getsockname()[1]
    server=subprocess.Popen([sys.executable,"-I","-B","-m","flavoretro.web","--workspace",scratch,"--port",str(port)],cwd=scratch,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health",timeout=1): break
            except OSError: time.sleep(0.1)
        statuses={}
        for path in ("/","/app.js","/style.css","/api/teaching","/api/topology?smiles=CCO","/api/status"):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}"+path,timeout=5) as response:
                    statuses[path]=response.status
            except urllib.error.HTTPError as exc:
                statuses[path]=exc.code
                if path=="/api/status":
                    assert "missing" in json.loads(exc.read())["message"]
        assert all(statuses[p]==200 for p in statuses if p!="/api/status")
        assert statuses["/api/status"]==503
        results["without_assets_http"]=statuses
    finally:
        server.terminate();server.wait(timeout=10)
    env["FLAVORETRO_WORKSPACE"]=str(workspace)
    live="""import json; from flavoretro.service import search; from flavoretro.contracts import SearchRequest; r=search(SearchRequest(smiles='CCOc1ccccc1',mode='quick',seconds=1.0,iterations=4,nodes=7,branching=2)); assert r['status']=='ok' and r['execution_source']=='live_aizynthfinder_mcts' and r['routes'] and all(x['steps']>0 for x in r['routes']); print(json.dumps({'run_id':r['run_id'],'resource_version':r['resource_version'],'nodes':r['phases'][0]['node_count'],'routes':len(r['routes']),'code':r['code']}))"""
    results["installed_live_search"]=json.loads(subprocess.run([sys.executable,"-I","-B","-c",live],cwd=scratch,env=env,text=True,capture_output=True,check=True).stdout)
results["scope"]="installed-wheel engineering checks, not independent chemistry or cross-platform performance"
(out/"report.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n")
print(str(out/"report.json"));print(json.dumps(results,indent=2,ensure_ascii=False))
