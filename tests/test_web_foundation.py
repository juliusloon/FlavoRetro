import json
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from flavoretro.web import Handler, GATE
from flavoretro.resources import sha,dumps

class FoundationEndpoints(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.env=patch.dict(os.environ,FLAVORETRO_WORKSPACE=self.tmp.name);self.env.start();self.addCleanup(self.env.stop)
        self.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f"http://127.0.0.1:{self.server.server_address[1]}"
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown();self.server.server_close();self.thread.join()

    def request(self,path,data=None):
        request=urllib.request.Request(self.base+path,data=None if data is None else json.dumps(data).encode(),headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(request,timeout=5) as response:return response.status,json.loads(response.read())
        except urllib.error.HTTPError as exc:return exc.code,json.loads(exc.read())

    def test_saved_run_integrity_all_files_and_no_search(self):
        name="20260926T000000-"+"a"*32
        folder=self.root/"outputs/runs"/name;folder.mkdir(parents=True)
        (folder/"result.json").write_text(dumps({"run_id":name,"status":"ok","routes":[]}))
        (folder/"worker.log").write_text("original fixture")
        (folder/"manifest.json").write_text(dumps({"run_id":name,"status":"ok","files":{p.name:sha(p) for p in folder.iterdir()}}))
        with patch("flavoretro.web.search") as search:
            status,body=self.request("/api/runs/"+name)
            self.assertEqual(status,200);self.assertEqual(body["execution_source"],"explicit_saved_run")
            self.assertEqual(body["integrity"],"verified");self.assertIn("worker.log",body["manifest"]["files"]);search.assert_not_called()
        self.assertEqual(self.request("/api/runs")[1]["total"],1)
        (folder/"worker.log").write_text("tampered")
        self.assertEqual(self.request("/api/runs/"+name)[0],409)
        (folder/"worker.log").unlink()
        self.assertEqual(self.request("/api/runs/"+name)[0],409)
        self.assertEqual(self.request("/api/runs/invalid")[0],400)

    def test_asset_free_preflight_and_parameter_filters(self):
        status,body=self.request("/api/preflight")
        self.assertEqual(status,200);self.assertFalse(body["formal_run_ready"]);self.assertFalse(body["release_ready"])
        self.assertFalse(body["engineering"]["assets_verified"])
        with patch("flavoretro.web.query",return_value={"total":0,"records":[],"resource_version":"fixture"}) as query:
            status,_=self.request("/api/records?kind=stock&issue=name_conflict&outcome=zero&source_status=name_conflict&offset=2&limit=3")
            self.assertEqual(status,200)
            self.assertEqual(query.call_args.kwargs,{"kind":"stock","q":"","issue":"name_conflict","outcome":"zero","source_status":"name_conflict","offset":2,"limit":3})

    def test_development_job_uses_shared_gate_and_preserves_progress(self):
        release=threading.Event();self.addCleanup(release.set)
        def compare(folder,progress):
            progress([{"status":"ok","run_id":"fixture"}]);release.wait(5)
            return str(folder),{"completed_cells":12,"expected_cells":12,"failures":0,"cells":[]}
        with patch("flavoretro.web.active_data"),patch("flavoretro.web.index_metadata"),patch("flavoretro.evaluation.compare",side_effect=compare):
            status,job=self.request("/api/evaluations",{"kind":"development"})
            self.assertEqual(status,202)
            self.assertEqual(self.request("/api/search",{"smiles":"CCO"})[0],429)
            self.assertEqual(self.request("/api/evaluations",{"kind":"development"})[0],429)
            release.set()
            for _ in range(50):
                status,state=self.request("/api/evaluations/"+job["evaluation_id"])
                if state["status"]!="running":break
                time.sleep(0.05)
            self.assertEqual(state["status"],"completed")
            self.assertEqual(state["completed_cells"],1) # fixture callback; not a real 12-cell scientific claim
            self.assertEqual(self.request("/api/evaluations")[1]["evaluations"][0]["evaluation_id"],job["evaluation_id"])
        self.assertEqual(self.request("/api/evaluations",{"kind":"formal"})[0],400)
        self.assertEqual(self.request("/api/evaluations",{"kind":"development","seconds":100})[0],400)

    def test_unfinished_job_from_another_process_is_not_claimed_running(self):
        name="development-"+"b"*32
        folder=self.root/"outputs/evaluation"/name;folder.mkdir(parents=True)
        original=dumps({"evaluation_id":name,"status":"running","completed_cells":2,"owner_pid":-1})
        (folder/"job.json").write_text(original)
        status,job=self.request("/api/evaluations/"+name)
        self.assertEqual(status,200);self.assertEqual(job["status"],"interrupted_or_untracked")
        self.assertEqual(job["completed_cells"],2);self.assertEqual((folder/"job.json").read_text(),original)
