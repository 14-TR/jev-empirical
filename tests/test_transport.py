import importlib
import os
import time
import unittest
from unittest.mock import patch


class FakeResponse:
    status = 302
    reads = 0
    def read(self, n):
        self.reads += 1
        raise AssertionError("error or redirect body must never be read")


class FakeConnection:
    calls = []
    response = FakeResponse()
    def __init__(self, host, **kwargs):
        self.calls.append((host, kwargs))
    def request(self, method, path, body, headers):
        self.calls.append((method, path, headers["Authorization"]))
    def getresponse(self): return self.response
    def close(self): pass


def sleeping_worker(pipe, payload, timeout):
    time.sleep(5)


class TransportTests(unittest.TestCase):
    def api(self):
        try: return importlib.import_module("jev_bench.transport")
        except ImportError: self.fail("bounded transport missing")

    def test_redirect_and_errors_are_not_read_or_retried(self):
        t = self.api()
        for status in (302, 401, 429, 500, 529):
            FakeConnection.calls = []
            FakeConnection.response.status = status
            with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only-not-real"}), \
                 patch.object(t.http.client, "HTTPSConnection", FakeConnection):
                out = t.exchange({"model": "jev-1.13.0"}, 1)
            self.assertEqual(out, {"status": "http_error", "http_status": status})
            self.assertEqual(len(FakeConnection.calls), 2)
            self.assertEqual(FakeConnection.calls[0][0], "api.typesafe.ai")
            self.assertEqual(FakeConnection.calls[1][:2], ("POST", "/v1/systemone"))
            self.assertEqual(FakeConnection.response.reads, 0)

    def test_missing_key_and_exceptions_never_include_details(self):
        t = self.api()
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(t.exchange({}, 1)["status"], "missing_key")
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test-only"}), \
             patch.object(t.http.client, "HTTPSConnection", side_effect=RuntimeError("SECRET-MARKER")):
            out = t.exchange({}, 1)
        self.assertEqual(out, {"status": "network_error"})
        self.assertNotIn("SECRET", str(out))

    def test_process_deadline_kills_blocking_worker(self):
        t = self.api()
        started = time.monotonic()
        out = t.bounded_request({}, 0.2, worker=sleeping_worker)
        self.assertEqual(out["status"], "timeout")
        self.assertLess(time.monotonic() - started, 2)
        for invalid in (0, -1, float("nan"), 121):
            with self.assertRaises(ValueError): t.bounded_request({}, invalid)
