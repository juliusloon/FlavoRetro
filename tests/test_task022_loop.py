"""Integrity tests for the new cumulative experiment ledger (no MCTS)."""
import concurrent.futures
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import task022_loop as loop


class LoopIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "operations").mkdir()
        self.base = self.root / "outputs/task022"
        self.base.mkdir(parents=True)
        self.patches = [patch.object(loop, "ROOT", self.root), patch.object(loop, "BASE", self.base), patch.object(loop.operate, "ROOT", self.root)]
        for item in self.patches:
            item.start()
        (self.root / "contract.md").write_text("approved\n")
        (self.root / "method.py").write_text("frozen = True\n")
        self.approval = {"task": "TASK-022", "approval": "agent_delegated", "human_reviewed": False,
                         "max_search_attempts": 2, "contract": "contract.md", "contract_sha256": loop.sha(self.root / "contract.md")}
        (self.base / "approval.json").write_text(json.dumps(self.approval))
        self.protocol = {"purpose": "engineering", "claim_boundary": "fixture only", "metrics": ["count"],
                         "stopping_rule": "2 attempts", "approval": "agent_delegated",
                         "cells": [{"cell_id": str(i), "request": {"smiles": "CCO", "seed": i}} for i in range(3)]}
        loop.freeze_batch("fixture", self.protocol, ["method.py"])

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.tmp.cleanup()

    def test_attempt_is_charged_before_run_and_failure_does_not_reset_budget(self):
        first = loop.reserve_cell("fixture", "0")
        self.assertEqual(loop.status()["search_attempts"], 1)
        loop.finish_cell(first["attempt_id"], status="failed", error="worker never started")
        loop.reserve_cell("fixture", "1")
        with self.assertRaisesRegex(ValueError, "budget"):
            loop.reserve_cell("fixture", "2")
        self.assertEqual(len(loop.status()["unfinished"]), 1)

    def test_same_cell_cannot_be_retried_or_completed_twice(self):
        first = loop.reserve_cell("fixture", "0")
        with self.assertRaisesRegex(ValueError, "already attempted"):
            loop.reserve_cell("fixture", "0")
        loop.finish_cell(first["attempt_id"], status="interrupted", error="explicit interrupted audit")
        with self.assertRaisesRegex(ValueError, "already terminal"):
            loop.finish_cell(first["attempt_id"], status="failed", error="second end")

    def test_asset_drift_rejects_before_budget_charge(self):
        (self.root / "method.py").write_text("frozen = False\n")
        with self.assertRaisesRegex(ValueError, "asset drift"):
            loop.reserve_cell("fixture", "0")
        self.assertEqual(loop.status()["search_attempts"], 0)

    def test_manifest_drift_is_detected(self):
        path = loop.batch_path("fixture")
        value = json.loads(path.read_text())
        value["protocol"]["cells"][0]["request"]["smiles"] = "CCC"
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "manifest drift"):
            loop.reserve_cell("fixture", "0")

    def test_new_batch_cannot_reset_cumulative_budget(self):
        loop.reserve_cell("fixture", "0")
        loop.reserve_cell("fixture", "1")
        loop.freeze_batch("next", self.protocol, ["method.py"])
        with self.assertRaisesRegex(ValueError, "budget"):
            loop.reserve_cell("next", "0")

    def test_parallel_duplicate_reservation_is_rejected(self):
        def attempt():
            try:
                return loop.reserve_cell("fixture", "0")["attempt_id"]
            except ValueError:
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertEqual(sum(item is not None for item in results), 1)
        self.assertEqual(loop.status()["search_attempts"], 1)

    def test_declared_cells_and_terminal_evidence_required(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            loop.reserve_cell("fixture", "unexpected")
        first = loop.reserve_cell("fixture", "0")
        with self.assertRaisesRegex(ValueError, "manifest"):
            loop.finish_cell(first["attempt_id"], status="completed")
        self.assertEqual(loop.status()["terminal"], 0)


if __name__ == "__main__":
    unittest.main()
