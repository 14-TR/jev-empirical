import importlib
import json
import os
import time
import unittest
from unittest.mock import patch


def load():
    try: return importlib.import_module('jev_agent.providers')
    except ImportError: raise AssertionError('missing fixed provider adapters') from None


def sleeping_worker(pipe, payload, timeout):
    time.sleep(5)


class Response:
    status = 200
    reads = 0
    raw = b''
    def read(self, size):
        self.reads += 1
        return self.raw[:size]


class Connection:
    calls = []
    response = Response()
    def __init__(self, host, port, **kwargs): self.calls.append(('connect', host, port, kwargs))
    def request(self, method, path, body, headers): self.calls.append(('request', method, path, json.loads(body), headers))
    def getresponse(self): return self.response
    def close(self): self.calls.append(('close',))


class ProviderTests(unittest.TestCase):
    def test_real_ollama_adapter_shape_and_text_only_response(self):
        api = load()
        evidence = [{'id': 'f0001', 'name': 'policy.md', 'text': 'Untrusted policy', 'sha256': 'a' * 64}]
        payload = api.synthesis_payload('Compare sources', evidence)
        self.assertEqual(payload['model'], 'qwen2.5:7b')
        self.assertIs(payload['stream'], False)
        self.assertNotIn('tools', payload)
        self.assertEqual(payload['options']['temperature'], 0)
        self.assertLessEqual(payload['options']['num_predict'], 1024)
        self.assertEqual(payload['messages'][0]['role'], 'system')
        user = json.loads(payload['messages'][1]['content'])
        self.assertEqual(user['evidence'], evidence)
        Connection.calls = []
        Connection.response = Response()
        Connection.response.raw = json.dumps({'model': 'qwen2.5:7b', 'done': True, 'done_reason': 'stop', 'message': {'role': 'assistant', 'content': 'Evidence-backed answer [f0001]'}}).encode()
        with patch.object(api.http.client, 'HTTPConnection', Connection):
            output = api.ollama_exchange(payload, 0.5)
        self.assertEqual(output, {'status': 'ok', 'model': 'qwen2.5:7b', 'text': 'Evidence-backed answer [f0001]'})
        self.assertEqual(Connection.calls[0][1:3], ('127.0.0.1', 11434))
        self.assertEqual(Connection.calls[1][1:3], ('POST', '/api/chat'))
        self.assertNotIn('Authorization', Connection.calls[1][4])

    def test_ollama_redirect_errors_are_not_read(self):
        api = load()
        for status in (301, 307, 404, 500):
            Connection.response = Response()
            Connection.response.status = status
            Connection.response.raw = b'SECRET ERROR BODY'
            with patch.object(api.http.client, 'HTTPConnection', Connection):
                output = api.ollama_exchange(api.synthesis_payload('g', []), 1)
            self.assertEqual(output['status'], 'http_error')
            self.assertEqual(Connection.response.reads, 0)
            self.assertNotIn('SECRET', str(output))

    def test_malformed_oversized_tool_calls_and_key_echo_fail_closed(self):
        api = load()
        valid = {'model': 'qwen2.5:7b', 'done': True, 'done_reason': 'stop', 'message': {'role': 'assistant', 'content': 'a'}}
        for raw in (b'bad JSON', b'x' * 65537,
                    json.dumps(dict(valid, done=False)).encode(),
                    json.dumps(dict(valid, message={'role': 'assistant', 'content': 'x', 'tool_calls': [{'name': 'shell'}]})).encode(),
                    json.dumps(dict(valid, message={'role': 'assistant', 'content': 'test-key-echo'})).encode()):
            Connection.response = Response()
            Connection.response.raw = raw
            with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'test-key-echo'}), patch.object(api.http.client, 'HTTPConnection', Connection):
                output = api.ollama_exchange(api.synthesis_payload('g', []), 1)
            self.assertNotEqual(output['status'], 'ok')
            self.assertNotIn('test-key-echo', str(output))

    def test_adapters_reuse_killable_bounded_transport_without_retry(self):
        api = load()
        with patch.object(api.transport, 'bounded_request', return_value={'status': 'timeout'}) as request:
            self.assertEqual(api.Jev().decide({'model': 'jev-1.13.0'}, 2), {'status': 'timeout'})
            request.assert_called_once_with({'model': 'jev-1.13.0'}, 2)
        with patch.object(api.transport, 'bounded_request', return_value={'status': 'timeout'}) as request:
            self.assertEqual(api.Ollama().synthesize('g', [], 90), {'status': 'timeout'})
            self.assertEqual(request.call_args.kwargs['worker'], api.ollama_worker)
            self.assertEqual(request.call_args.args[1], 90)
        for invalid in (91, float('nan'), 0):
            with self.assertRaises(ValueError): api.Ollama().synthesize('g', [], invalid)
        started = time.monotonic()
        output = api.transport.bounded_request({}, 0.1, worker=sleeping_worker)
        self.assertEqual(output['status'], 'timeout')
        self.assertLess(time.monotonic() - started, 2)
