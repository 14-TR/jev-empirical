"""Offline regressions for the first independent review's blocker ledger."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jev_bench import core, runner, transport
from test_core import fixture
from test_answers import input_for, response


def dataset_for(kinds):
    dataset = fixture()
    template = dataset["cases"][0]
    dataset["cases"] = []
    for i, kind in enumerate(kinds):
        case = copy.deepcopy(template)
        case.update(id="case-%d" % i, pair_id="case-%d" % i,
                    input=input_for(kind), gold={"choice": "billing", "score": "1", "noul": "true"}[kind])
        dataset["cases"].append(case)
    return dataset


class ReviewRegressions(unittest.TestCase):
    def test_unserializable_response_extras_are_invalid_not_checkpoint_errors(self):
        for value in (float("inf"), float("nan"), "\ud800"):
            with self.subTest(value=repr(value)), tempfile.TemporaryDirectory() as folder, \
                 patch.dict(os.environ, {"TYPESAFE_API_KEY": "fixture-only"}):
                raw = response(); raw["unknown"] = {"nested": value}
                with patch.object(runner, "bounded_request", return_value={"status": "ok", "response": raw}):
                    rec = runner.run(fixture(), "live", Path(folder)/"raw", model="jev-1.13.0", max_requests=1)
                self.assertEqual(rec["records"][0]["status"], "invalid_response")
                self.assertIsNone(rec["records"][0]["response"])
                self.assertEqual(runner.load_receipt(fixture(), Path(folder)/"raw/receipt.json"), rec)

    def test_receipt_utc_start_end_are_validated_and_replayed(self):
        from datetime import datetime, timezone
        before = datetime.now(timezone.utc)
        with tempfile.TemporaryDirectory() as folder:
            receipt = runner.run(fixture(), "baseline", Path(folder)/"raw")
            self.assertEqual(receipt["schema_version"], 2)
            self.assertRegex(receipt["started_at_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
            self.assertRegex(receipt["completed_at_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
            start = datetime.fromisoformat(receipt["started_at_utc"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(receipt["completed_at_utc"].replace("Z", "+00:00"))
            self.assertLessEqual(before, start)
            self.assertLessEqual(start, end)
            self.assertLessEqual(end, datetime.now(timezone.utc))
            self.assertEqual(runner.load_receipt(fixture(), Path(folder)/"raw/receipt.json"), receipt)
            for field in ("started_at_utc", "completed_at_utc"):
                for bad in (None, "", "2026-02-30T00:00:00.000000Z", "2026-01-01T00:00:00+01:00"):
                    with self.subTest(field=field, bad=bad):
                        changed = copy.deepcopy(receipt); changed[field] = bad
                        with self.assertRaises(core.ValidationError): runner.validate_receipt(fixture(), changed)
                changed = copy.deepcopy(receipt); del changed[field]
                with self.assertRaises(core.ValidationError): runner.validate_receipt(fixture(), changed)

    def test_101_large_responses_obey_aggregate_budget_and_replay(self):
        dataset = dataset_for(["choice"] * 101)
        raw = response(); raw["unknown"] = "x" * 330000
        body = json.dumps(raw).encode()
        self.assertLess(len(body), transport.MAX_RESPONSE_BYTES)
        rec = self.run_http_fixtures(dataset, [body] * 101)
        # Contract: 8 MiB total compact UTF-8 response JSON, never drop case records.
        size = len(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode())
        expected_successes = (8 * 1024 * 1024) // size
        self.assertEqual([r["status"] for r in rec["records"]],
                         ["ok"] * expected_successes + ["response_too_large"] * (101 - expected_successes))
        self.assertEqual(rec["records"][0]["response"], raw)
        self.assertTrue(all(r["response"] is None for r in rec["records"][expected_successes:]))
        self.assertEqual(runner.report(dataset, rec)["summary"]["n_cases"], 101)

    def test_aggregate_budget_accepts_exact_fit_after_rejecting_larger_result(self):
        small = response(); large = response(); large["unknown"] = "x" * 1000
        body = json.dumps(small).encode()
        size = len(json.dumps(small, ensure_ascii=False, separators=(",", ":")).encode())
        with patch.object(runner, "MAX_RETAINED_RESPONSE_BYTES", 2 * size):
            rec = self.run_http_fixtures(dataset_for(["choice"] * 4),
                                         [body, json.dumps(large).encode(), body, body])
        self.assertEqual([r["status"] for r in rec["records"]],
                         ["ok", "response_too_large", "ok", "response_too_large"])
        self.assertEqual(rec["records"][2]["response"], small)

    def test_over_limit_receipt_read_has_a_finite_allocation_limit(self):
        class LimitedReader:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(inner, n=-1):
                self.assertGreater(n, 0, "replay must not allocate the whole file")
                self.assertLessEqual(n, 32000001)
                return b"x" * n
        with patch.object(Path, "open", return_value=LimitedReader()):
            with self.assertRaisesRegex(core.ValidationError, "receipt_too_large"):
                runner.load_receipt(fixture(), "oversized-receipt.json")

    def test_deadline_minimum_zero_negative_and_submillisecond_replay(self):
        dataset = dataset_for(["choice"] * 3)
        for remaining, attempts in ((0.0005, 0), (0.001, 1), (0.0, 0), (-0.001, 0)):
            with self.subTest(remaining=remaining), tempfile.TemporaryDirectory() as folder, \
                 patch.dict(os.environ, {"TYPESAFE_API_KEY": "fixture-only"}), \
                 patch.object(runner, "bounded_request", return_value={"status": "timeout"}) as call:
                # Deadline = 0.001; subtract exactly to exercise its inclusive boundary.
                clock = [0.0, 0.001 - remaining] + [1.0] * 12
                with patch.object(runner.time, "monotonic", side_effect=clock):
                    rec = runner.run(dataset, "live", Path(folder)/"raw", model="jev-1.13.0",
                                     max_requests=3, max_seconds=0.001)
                self.assertEqual(call.call_count, attempts)
                expected = (["timeout"] if attempts else []) + ["budget_exhausted"] * (3 - attempts)
                self.assertEqual([r["status"] for r in rec["records"]], expected)
                if attempts: self.assertEqual(call.call_args[0][1], 0.001)
                self.assertEqual(runner.load_receipt(dataset, Path(folder)/"raw/receipt.json"), rec)

    def run_http_fixtures(self, dataset, bodies):
        bodies = iter(bodies)
        class Resp:
            status = 200
            def __init__(self): self.body = next(bodies)
            def read(self, n): return self.body[:n]
        class Conn:
            def __init__(self, *args, **kwargs): pass
            def request(self, *args, **kwargs): pass
            def getresponse(self): return Resp()
            def close(self): pass
        with tempfile.TemporaryDirectory() as folder, \
             patch.dict(os.environ, {"TYPESAFE_API_KEY": "fixture-only-not-a-secret"}), \
             patch.object(transport.http.client, "HTTPSConnection", Conn), \
             patch.object(runner, "bounded_request", transport.exchange):
            receipt = runner.run(dataset, "live", Path(folder)/"raw", model="jev-1.13.0",
                                 max_requests=len(dataset["cases"]), max_seconds=120)
            replay = runner.load_receipt(dataset, Path(folder)/"raw/receipt.json")
            self.assertEqual(runner.report(dataset, replay), runner.report(dataset, receipt))
            self.assertEqual(replay, receipt)
        return receipt

    def test_exponent_overflow_in_answer_and_nested_unknown_field_is_counted(self):
        for target in ("answer", "extra"):
            for literal in ("1e309", "-1e309", "NaN", "Infinity", "-Infinity"):
                with self.subTest(target=target, literal=literal):
                    bad = response()
                    if target == "answer": bad["answers"]["q"]["confidence"] = "NUMERIC-MARKER"
                    else: bad["unknown"] = {"nested": ["NUMERIC-MARKER"]}
                    body = json.dumps(bad).replace('"NUMERIC-MARKER"', literal).encode()
                    rec = self.run_http_fixtures(dataset_for(["choice"] * 3),
                                                 [json.dumps(response()).encode(), body,
                                                  json.dumps(response()).encode()])
                    self.assertEqual([r["status"] for r in rec["records"]],
                                     ["ok", "invalid_response", "ok"])
                    self.assertIsNone(rec["records"][1]["response"])

    def test_oversized_integer_on_every_bounded_answer_surface_is_counted(self):
        for kind, field in (("choice", "confidence"), ("choice", "probabilities"),
                            ("score", "confidence"), ("score", "probabilities"),
                            ("score", "score"), ("noul", "noul")):
            with self.subTest(kind=kind, field=field):
                bad = response(kind)
                if field == "probabilities":
                    bad["answers"]["q"][field][next(iter(bad["answers"]["q"][field]))] = 10**400
                else: bad["answers"]["q"][field] = 10**400
                rec = self.run_http_fixtures(dataset_for([kind] * 3),
                                             [json.dumps(response(kind)).encode(), json.dumps(bad).encode(),
                                              json.dumps(response(kind)).encode()])
                self.assertEqual([r["status"] for r in rec["records"]],
                                 ["ok", "invalid_response", "ok"])
                self.assertIsNone(rec["records"][1]["response"])
