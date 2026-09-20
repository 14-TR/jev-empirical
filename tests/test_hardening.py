import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from jev_bench import core, runner, transport
from test_core import fixture
from test_answers import response, input_for


class HardeningTests(unittest.TestCase):
    def test_untrusted_task_and_family_strings_cannot_enter_exports(self):
        for field in ("task", "variant"):
            d = fixture(); d["cases"][0][field] = "SECRET-ALPHANUMERIC-TOKEN"
            with self.assertRaises(core.ValidationError): core.validate_dataset(d)

    def test_response_body_containing_credential_is_discarded(self):
        class Resp:
            status = 200
            def read(self, n): return b'{"echo":"TEST-CREDENTIAL-MARKER"}'
        class Conn:
            def __init__(self, *args, **kwargs): pass
            def request(self, *args, **kwargs): pass
            def getresponse(self): return Resp()
            def close(self): pass
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "TEST-CREDENTIAL-MARKER"}), \
             patch.object(transport.http.client, "HTTPSConnection", Conn):
            result = transport.exchange({}, 1)
        self.assertEqual(result, {"status": "invalid_response"})

    def test_oversized_and_duplicate_json_responses_rejected(self):
        class Resp:
            status = 200
            def read(self, n): return self.body[:n]
        class Conn:
            def __init__(self, *args, **kwargs): pass
            def request(self, *args, **kwargs): pass
            def getresponse(self): return Resp()
            def close(self): pass
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only"}), \
             patch.object(transport.http.client, "HTTPSConnection", Conn):
            for body, status in ((b'x'*(transport.MAX_RESPONSE_BYTES+1), "response_too_large"),
                                 (b'{"answers":{},"answers":{}}', "invalid_response"),
                                 (b'', "invalid_response")):
                Resp.body = body
                self.assertEqual(transport.exchange({}, 1)["status"], status)

    def test_invalid_success_body_never_retained_and_budget_times_out(self):
        d = fixture(); other = copy.deepcopy(d["cases"][0]); other["id"] = "two"; other["pair_id"] = "two"
        d["cases"].append(other)
        def fake(payload, timeout):
            time.sleep(0.015)
            return {"status": "ok", "response": {"secret": "FAIL-BODY"}}
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only"}), \
             patch.object(runner, "bounded_request", fake):
            rec = runner.run(d, "live", Path(folder)/"raw", model="jev-1.13.0", max_requests=2, max_seconds=.01)
            self.assertEqual([r["status"] for r in rec["records"]], ["invalid_response", "budget_exhausted"])
            self.assertNotIn("FAIL-BODY", (Path(folder)/"raw/receipt.json").read_text())

    def test_replay_rejects_unknown_record_fields_and_wrong_resolved_model(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only"}), \
             patch.object(runner, "bounded_request", return_value={"status": "ok", "response": response()}):
            rec = runner.run(fixture(), "live", Path(folder)/"raw", model="jev-1.13.0", max_requests=1)
        extra = copy.deepcopy(rec); extra["records"][0]["secret"] = "SECRET"
        with self.assertRaises(core.ValidationError): runner.report(fixture(), extra)
        mismatch = copy.deepcopy(rec); mismatch["records"][0]["response"]["model"] = "jev-9.99.0"
        with self.assertRaises(core.ValidationError): runner.report(fixture(), mismatch)

    def test_success_contract_and_optional_usage_fields(self):
        raw = response(); raw["usage"] = {}
        self.assertEqual(core.parse_response(input_for("choice"), raw)["predicted"], "billing")
        for field, value in (("confidence", -1), ("confidence", float("inf")), ("choice", "unknown")):
            raw = response(); raw["answers"]["q"][field] = value
            with self.assertRaises(core.ValidationError): core.parse_response(input_for("choice"), raw)
        raw = response("score"); raw["answers"]["q"]["legend"]["0"] = "different"
        with self.assertRaises(core.ValidationError): core.parse_response(input_for("score"), raw)

    def test_authored_dataset_generator_matches_checked_in_file(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location("build_dataset", root/"scripts/build_dataset.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        self.assertEqual(module.build(), json.loads((root/"datasets/synthetic_diagnostics.json").read_text()))

    def test_request_hash_preserves_choice_order(self):
        inp = input_for("choice"); other = copy.deepcopy(inp)
        other["question"]["criteria"] = dict(reversed(list(other["question"]["criteria"].items())))
        self.assertNotEqual(runner.digest(core.request_for(inp, "jev-1.13.0")),
                            runner.digest(core.request_for(other, "jev-1.13.0")))
