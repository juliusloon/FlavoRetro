import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from flavoretro.resources import sha, dumps
from flavoretro.workspace import active_data, AssetError
from flavoretro.database import build, query, records, metadata

class DatabaseContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, FLAVORETRO_WORKSPACE=str(self.root))
        self.env.start(); self.addCleanup(self.env.stop)
        (self.root / "metadata").mkdir()
        self.folder = self.root / "data/derived/fixture"
        self.folder.mkdir(parents=True)
        (self.root / "source.txt").write_text("original fixture only")
        source = {"path":"source.txt","sha256":sha(self.root / "source.txt")}
        (self.root / "metadata/sources.json").write_text(dumps({"files":[source]}))
        self.rows = []
        for i, (value, missing, raw) in enumerate(((0,False,"0%"),(None,True,None),(None,False,"trace"))):
            self.rows.append({"id":str(i),"kind":"fixture","raw":{"label":"中文 ZERO " + str(i)},
                "source_path":"source.txt","source_sha256":source["sha256"],"source_status":"unreviewed",
                "production_eligible":False,"name_conflict_recomputed":i==0,
                "outcome":{"raw":raw,"value":value,"is_missing":missing,"status":"fixture"}})
        (self.folder / "records.json").write_text(dumps(self.rows))
        manifest={"records_sha256":sha(self.folder / "records.json"),"sources_sha256":sha(self.root / "metadata/sources.json")}
        (self.folder / "manifest.json").write_text(dumps(manifest))
        (self.root / "metadata/active.json").write_text(dumps({"schema_version":1,"version":"fixture","manifest_sha256":sha(self.folder/"manifest.json")}))
        build()

    def test_lossless_records_pagination_unicode_and_literal_query(self):
        self.assertEqual(records(),self.rows)
        self.assertEqual(query(q="中文 zero",offset=1,limit=1)["records"],[self.rows[1]])
        self.assertEqual(query(q="%_" )["total"],0)
        self.assertEqual(query(issue="name_conflict")["records"],[self.rows[0]])

    def test_zero_missing_unparsed_distinct(self):
        for name, index in (("zero",0),("missing",1),("unparsed",2)):
            self.assertEqual(query(outcome=name)["records"],[self.rows[index]])
        self.assertEqual(query(outcome="numeric")["total"],1)

    def test_read_only_foreign_keys_and_conservation(self):
        with sqlite3.connect((self.folder/"index.sqlite").as_uri()+"?mode=ro",uri=True) as c:
            self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(),[])
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("DELETE FROM records")
        with self.assertRaises(ValueError): build()

    def test_database_and_pointer_tamper_detected(self):
        db=self.folder/"index.sqlite"; db.chmod(0o644)
        with db.open("ab") as f: f.write(b"tampered")
        with self.assertRaises(AssetError): metadata()
        pointer=self.root/"metadata/active.json"; p=json.loads(pointer.read_text());p["version"]="../fixture";pointer.write_text(dumps(p))
        with self.assertRaises(AssetError): active_data()

    def test_source_or_records_drift_rejected(self):
        (self.root/"source.txt").write_text("changed source")
        # Canonical source manifest protects identity; build verifies actual source bytes.
        (self.root/"metadata/sources.json").write_text("changed manifest")
        with self.assertRaises(AssetError): query()
