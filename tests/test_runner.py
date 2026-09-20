import copy
import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_core import fixture
from test_answers import response


class RunnerTests(unittest.TestCase):
    def api(self):
        try: return importlib.import_module("jev_bench.runner")
        except ImportError: self.fail("receipt runner missing")

    def test_offline_receipt_is_replayable_and_export_has_no_state(self):
        r = self.api()
        d = fixture()
        d["cases"][0]["input"]["state"]["text"] = "PRIVATE-STATE-MARKER"
        with tempfile.TemporaryDirectory() as folder:
            receipt = r.run(d, "baseline", Path(folder)/"private", max_requests=0, max_seconds=5)
            report = r.report(d, receipt)
            self.assertEqual(report["mode"], "baseline")
            self.assertEqual(report["summary"]["n_cases"], 1)
            self.assertNotIn("PRIVATE-STATE", json.dumps(report))
            path = Path(folder)/"private"/"receipt.json"
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            replayed = r.load_receipt(d, path)
            self.assertEqual(r.report(d, replayed), report)
            self.assertIn("Not Jev results", r.markdown(report))

    def test_live_budget_counts_failures_and_does_not_retry(self):
        r = self.api()
        d = fixture(); second = copy.deepcopy(d["cases"][0]); second["id"] = "route-2"
        second["pair_id"] = "route-2"; d["cases"].append(second)
        calls = []
        def fake(payload, timeout):
            calls.append(payload)
            self.assertNotIn("gold", json.dumps(payload))
            return {"status": "http_error", "http_status": 429}
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only"}), \
             patch.object(r, "bounded_request", fake):
            rec = r.run(d, "live", Path(folder)/"raw", model="jev-1.13.0", max_requests=1, max_seconds=5)
            self.assertEqual(len(calls), 1)
            report = r.report(d, rec)
            self.assertEqual(report["summary"]["n_failed"], 2)
            self.assertEqual(report["summary"]["failure_counts"], {"http_error": 1, "budget_exhausted": 1})
            self.assertEqual(rec["records"][1]["latency_ms"], None)

    def test_receipt_rejects_missing_duplicate_malformed_or_dataset_mismatch(self):
        r = self.api(); d = fixture()
        with tempfile.TemporaryDirectory() as folder:
            rec = r.run(d, "baseline", Path(folder)/"raw", max_requests=0, max_seconds=5)
            bad = []
            x = copy.deepcopy(rec); x["records"] = []; bad.append(x)
            x = copy.deepcopy(rec); x["records"] *= 2; bad.append(x)
            x = copy.deepcopy(rec); x["dataset_sha256"] = "0"*64; bad.append(x)
            x = copy.deepcopy(rec); x["records"][0]["baseline_prediction"]["probabilities"]["billing"] = 0.9; bad.append(x)
            x = copy.deepcopy(rec); x["records"][0]["latency_ms"] = float("nan"); bad.append(x)
            for x in bad:
                with self.subTest(x=x), self.assertRaises(ValueError): r.report(d, x)

    def test_live_validation_and_unknown_fields_cannot_escape_allowlist(self):
        r = self.api(); d = fixture()
        # Protocol test only: fixture injection is not an empirical run.
        raw = response(); raw["secret_extra"] = "SECRET-MARKER"
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only"}), \
             patch.object(r, "bounded_request", return_value={"status": "ok", "response": raw}):
            rec = r.run(d, "live", Path(folder)/"raw", model="jev-1.13.0", max_requests=1, max_seconds=5)
            report = r.report(d, rec)
            self.assertEqual(report["resolved_models"], ["jev-1.13.0"])
            self.assertNotIn("SECRET-MARKER", json.dumps(report))
            self.assertEqual(report["usage"]["input_tokens_reported"], 10)
        for kwargs in ({}, {"model": "jev-1.13.0", "max_requests": -1}, {"model": "jev-1.13.0", "max_seconds": 0}):
            with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
                r.run(d, "live", Path(folder)/"raw", **kwargs)

    def test_raw_directory_inside_repository_or_symlink_rejected(self):
        r = self.api()
        repo = Path(__file__).resolve().parents[1]
        with self.assertRaises(ValueError): r.run(fixture(), "baseline", repo/"raw")
        with tempfile.TemporaryDirectory() as folder:
            link = Path(folder)/"link"; link.symlink_to(repo, target_is_directory=True)
            with self.assertRaises(ValueError): r.run(fixture(), "baseline", link/"raw")
