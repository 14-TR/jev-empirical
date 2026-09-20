import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_incident_episode import runner, Judge, Adviser


def load(name):
    try: return importlib.import_module('incident_room.' + name)
    except ImportError: raise AssertionError('missing Incident Room ' + name) from None


class IOTests(unittest.TestCase):
    def test_adapter_uses_bounded_transport_and_rejects_tool_calls(self):
        p = load('providers')
        payload = p.advisory_payload({'world': {}})
        self.assertNotIn('tools', payload)
        self.assertIs(payload['stream'], False)
        with patch.object(p.transport, 'bounded_request', return_value={'status': 'timeout'}) as call:
            self.assertEqual(p.Qwen().advise({}, 3)['status'], 'timeout')
            self.assertEqual(call.call_count, 1)
        valid = {'model': 'qwen2.5:7b', 'done': True, 'done_reason': 'stop', 'message': {'role': 'assistant', 'content': 'Seal leak.'}, 'prompt_eval_count': 20, 'eval_count': 5}
        self.assertEqual(p.parse_qwen(valid)['usage'], {'input_tokens': 20, 'output_tokens': 5})
        for bad in ({}, dict(valid, done=False), dict(valid, message={'role': 'assistant', 'content': 'x', 'tool_calls': [{}]})):
            with self.assertRaises(ValueError): p.parse_qwen(bad)

    def test_public_export_drops_unknown_fields_and_withholds_advice_by_default(self):
        io = load('io'); r = runner()
        e = r.run(mode='live-hybrid', jev=Judge(), qwen=Adviser())
        e['PRIVATE'] = 'private-secret'; e['calls'][0]['raw'] = 'private-secret'
        e['frames'][1]['decisions']['ada']['raw'] = 'private-secret'
        e['metrics']['raw'] = 'private-secret'; e['limits']['raw'] = 'private-secret'
        e['calls'][0]['usage']['raw'] = 'private-secret'
        e = r.seal(e)
        public = io.public_episode(e)
        self.assertNotIn('private-secret', json.dumps(public))
        self.assertEqual(public['advisory']['status'], 'withheld')
        self.assertTrue(r.validate_replay(public))
        with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'secret-test-key'}):
            e['advisory']['text'] = 'secret-test-key https://example.com /Users/name/file'
            e = r.seal(e)
            text = io.public_episode(e, publish_advisory=True)['advisory']['text']
            self.assertNotIn('secret-test-key', text)
            self.assertNotIn('https://', text)
            self.assertNotIn('/Users', text)

    def test_cli_offline_writes_replay_and_js_without_fetch_and_refuses_live_without_consent(self):
        cli = load('__main__'); r = runner()
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'episode.json'; asset = Path(d) / 'episode.js'
            self.assertEqual(cli.main(['run', '--public', str(out), '--asset', str(asset)]), 0)
            self.assertTrue(r.validate_replay(json.loads(out.read_text())))
            self.assertTrue(asset.read_text().startswith('window.INCIDENT_EPISODE = '))
            self.assertNotEqual(cli.main(['run', '--mode', 'live-hybrid', '--public', str(out)]), 0)

    def test_static_console_has_local_assets_accessible_controls_and_no_network_code(self):
        root = Path(__file__).resolve().parents[1] / 'apps' / 'incident-room'
        self.assertTrue((root / 'index.html').exists(), 'missing console')
        html = (root / 'index.html').read_text(); script = (root / 'app.js').read_text()
        for marker in ('id="step"', 'id="play"', 'id="pause"', 'id="reset"', 'id="load"', 'id="map"', 'id="decisions"', 'id="timeline"'):
            self.assertIn(marker, html)
        self.assertIn('textContent', script)
        for forbidden in ('fetch(', 'XMLHttpRequest', 'innerHTML', 'eval(', 'https://'):
            self.assertNotIn(forbidden, script)
