import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from flavoretro.workspace import PACKAGE,config,configure,root,active_data,AssetError

class PackageContracts(unittest.TestCase):
    def test_packaged_defaults_work_without_workspace_files(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ,FLAVORETRO_WORKSPACE=directory):
            self.assertEqual(root(),Path(directory))
            self.assertIn("profiles",config("search.json"))
            self.assertIn("classifications",config("teaching_guidance.json"))
            with self.assertRaises(AssetError): active_data()

    def test_workspace_configuration_override_and_argument_resolution(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ):
            configure(directory)
            configs=Path(directory)/"configs";configs.mkdir();(configs/"search.json").write_text('{"override":true}')
            self.assertEqual(config("search.json"),{"override":True})

    def test_packaged_snapshots_match_checkout_when_present(self):
        checkout=PACKAGE.parent
        for kind in ("configs","web"):
            for p in (PACKAGE/"assets"/kind).iterdir():
                source=checkout/kind/p.name
                if source.is_file():self.assertEqual(p.read_bytes(),source.read_bytes(),str(source))
