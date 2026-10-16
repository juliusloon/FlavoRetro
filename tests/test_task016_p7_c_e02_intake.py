"""Meaningful fail-closed/physical-accounting checks for the new raw intake."""
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch
from scripts import task016_p7_c_e02_http as h
from scripts import task016_p7_c_e02_fresh as f

class Response(io.BytesIO):
    def __init__(self, body, code=200, url="https://example.test/raw"):
        super().__init__(body)
        self.code=code
        self.headers={"Content-Type":"application/json","Set-Cookie":"must-not-be-recorded"}
        self.url=url
    def geturl(self):
        return self.url

class RawIntakeSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.base=self.root/"outputs/task016-p7/v1"
        self.c=self.base/"C"
        self.e=self.c/"E02"
        self.raw=self.root/"data/raw/task016-p7/C/E02"
        self.contract=self.e/"fresh/C-E02-R1/query_plan.json"
        self.contract.parent.mkdir(parents=True)
        self.contract.write_text("{}")
        self.events=[]
        self.patches=[]
        def writer(task,path,text):
            p=self.root/path
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(text)
        for name,value in (("ROOT",self.root),("BASE",self.base),("C",self.c),("E",self.e),("RAW",self.raw),
                           ("write",writer),("event",lambda task,action,**kw:self.events.append((action,kw)))):
            self.patches.append(patch.object(h,name,value))
        self.patches.append(patch.object(h,"require_active",return_value={
            "batch_id":"C-E02-R1","G4_pointer":{"path":"g4.json","sha256":"a"*64}}))
        self.patches.append(patch.object(h,"physical_attempts",return_value=[]))
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def response(self,body,**kw):
        return patch.object(h.urllib.request,"build_opener",return_value=type("Opener",(),{"open":lambda _,request,timeout:Response(body,**kw)})())
    def test_raw_response_and_header_whitelist(self):
        with self.response(b'{"ok":true}'):
            r=h.acquire(self.contract,"https://example.test/raw","metadata","test",object_limit=100)
        self.assertEqual(r["bytes"],11)
        self.assertEqual((self.root/r["path"]).read_bytes(),b'{"ok":true}')
        self.assertEqual(r["headers"],{"content-type":"application/json"})
        self.assertEqual([e[0] for e in self.events],["write_binary","source_http"])
        self.assertFalse(r["evidence_eligible"])
        self.assertEqual(len(h.rows(self.c/"acquisition_plan.jsonl")),1)
        self.assertEqual(len(h.rows(self.c/"http_ledger.jsonl")),1)
    def test_cap_keeps_failed_prefix_in_budget(self):
        with self.response(b"123456789"):
            r=h.acquire(self.contract,"https://example.test/raw","metadata","test",object_limit=3)
        self.assertEqual(r["status"],"failed")
        self.assertEqual(r["bytes"],4)
        self.assertEqual((self.root/r["path"]).read_bytes(),b"1234")
        self.assertEqual(json.loads((self.c/"raw_manifest.json").read_text())["bytes"],4)
    def test_redirect_not_silently_fetched(self):
        opener=type("Opener",(),{"open":lambda _,request,timeout: (_ for _ in ()).throw(
            urllib.error.HTTPError(request.full_url,302,"Moved",{"Location":"https://example.test/next"},io.BytesIO(b"redirect")))})()
        with patch.object(h.urllib.request,"build_opener",return_value=opener):
            r=h.acquire(self.contract,"https://example.test/raw","metadata","test",object_limit=100)
        self.assertEqual(r["status_code"],302)
        self.assertEqual(r["status"],"failed")
        self.assertEqual(r["bytes"],8)
        self.assertEqual(r["headers"]["location"],"https://example.test/next")
        self.assertEqual(len(h.rows(self.c/"http_ledger.jsonl")),1)
    def test_two_attempts_any_family_block_third_before_request(self):
        prior=[dict(url="https://example.test/raw",bytes=0,path="data/raw/task016-p7/SS/x",kind="metadata")]*2
        with patch.object(h,"physical_attempts",return_value=prior),patch.object(h.urllib.request,"build_opener") as network:
            with self.assertRaisesRegex(h.ContractError,"attempt cap"):
                h.acquire(self.contract,"https://example.test/raw","metadata","test",object_limit=100)
            network.assert_not_called()
        self.assertFalse((self.c/"acquisition_plan.jsonl").exists())
    def test_reserved_maximum_bytes_fail_closed(self):
        rr=[dict(bytes=2*1024**3-5,path="data/raw/task016-p7/C/x",kind="metadata")]
        with self.assertRaisesRegex(h.ContractError,"hard budget"):
            h.budget(rr,"metadata",10)
    def test_credentials_and_unknown_kind_make_zero_requests(self):
        with patch.object(h.urllib.request,"build_opener") as network:
            for url,kind in (("https://name:secret@example.test/raw","metadata"),("https://example.test/raw","unknown")):
                with self.assertRaises(h.ContractError):
                    h.acquire(self.contract,url,kind,"test")
            network.assert_not_called()
    def test_g4_drift_or_terminal_epoch_blocks_before_network(self):
        with patch.object(h,"require_active",side_effect=h.ContractError("G4 drift or terminal epoch")),patch.object(h.urllib.request,"build_opener") as network:
            with self.assertRaises(h.ContractError):
                h.acquire(self.contract,"https://example.test/raw","metadata","test")
            network.assert_not_called()
    def test_identifier_only_historical_match_is_rejected_without_graph(self):
        hint=f.source_hint(dict(source="MED",id="123",doi="10.1234/exposed",pmcid="PMC9999",title="Synthetic metadata"))
        self.assertEqual(f.hint_tokens(hint),{"pmid:123","article:PMC9999","doi:10.1234/exposed"})

if __name__=="__main__":
    unittest.main()
