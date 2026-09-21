import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from test_investigator_source import mod, fixture
from test_investigator_loop import ISSUE, Judge, Qwen


class SafetyTests(unittest.TestCase):
    def test_approved_check_is_isolated_and_environment_is_allowlisted(self):
        c = mod('checks'); s = mod('source')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); repo, _ = fixture(root)
            (repo / 'tests').mkdir()
            (repo / 'tests' / 'test_incident_episode.py').write_text(
                'import os, unittest\nfrom pathlib import Path\nclass Probe(unittest.TestCase):\n'
                ' def test_env(self):\n  assert "TYPESAFE_API_KEY" not in os.environ\n'
                '  assert "GH_TOKEN" not in os.environ\n  assert "AWS_SESSION_TOKEN" not in os.environ\n'
                '  Path("public.txt").write_text("child mutation")\n')
            subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'probe'], check=True)
            commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
            snap = s.freeze(repo, commit, root / 'private')
            with self.assertRaises(ValueError): c.run_check('incident-unittest', snap, False, (), 10)
            with self.assertRaises(ValueError): c.run_check('arbitrary;pwd', snap, True, ('incident-unittest',), 10)
            with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'never-transfer-key', 'GH_TOKEN': 'never-transfer-gh', 'AWS_SESSION_TOKEN': 'never-transfer-aws'}):
                result = c.run_check('incident-unittest', snap, True, ('incident-unittest',), 10)
            self.assertEqual(result['exit_code'], 0)
            self.assertFalse(result['os_sandbox'])
            self.assertEqual(snap.read('public.txt'), 'pressure regression\n')
            self.assertEqual((repo / 'public.txt').read_text(), 'pressure regression\n')
            self.assertNotIn('never-transfer', json.dumps(result))

    def test_metadata_probe_is_deterministic_and_preserves_original(self):
        c = mod('checks'); s = mod('source')
        # Explicit historical source/input closure, not checkout HEAD or a fetched SHA.
        data = Path(__file__).resolve().parent / 'fixtures' / 'investigator_metadata'
        inputs = (
            ('episode.py', 'src/incident_room/episode.py', '1887d605eec56b3db935bd102a09b721b720186a912fa10b4f40a3ae6ce9169e'),
            ('engine.py', 'src/incident_room/engine.py', '557571473f9e5c8452b8ea4ca17908e5ede48c4752ab5a0a62e9f2542658a576'),
            ('core.py', 'src/jev_bench/core.py', '3b64ef1e7cc6d3985754e88392c9b1dfeed837f975b12b7598f5247da0be10a4'),
            ('live-episode.json', 'apps/incident-room/live-episode.json', '7808fc0db2b226d6c57dd5690f851cf6fe8446f353b142c8ce2ad28365fef116'),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); repo, _ = fixture(root)
            before = {}
            for name, path, expected in inputs:
                raw = (data / name).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), expected)
                target = repo / path; target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw); before[path] = raw
            subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'metadata fixture'], check=True)
            commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
            snap = s.freeze(repo, commit, root / 'private')
            first = c.run_check('incident-replay-metadata', snap, True, ('incident-replay-metadata',), 10)
            second = c.run_check('incident-replay-metadata', snap, True, ('incident-replay-metadata',), 10)
            self.assertEqual(first['exit_code'], 0)
            self.assertEqual(second['exit_code'], 0)
            self.assertEqual(first['output'], second['output'])
            output = json.loads(first['output'])
            self.assertTrue(output['original_unchanged'])
            self.assertTrue(output['original_valid'])
            self.assertEqual(output['mutated_tick'], 19)
            self.assertEqual(output['final_frame_tick'], 8)
            self.assertIn('changed_call_tick_accepted', output)
            self.assertTrue(output['changed_call_tick_accepted'])
            self.assertNotEqual(output['original_integrity'], output['mutated_integrity'])
            for path, raw in before.items():
                self.assertEqual((repo / path).read_bytes(), raw)
                self.assertEqual(snap.read(path).encode('utf-8'), raw)

    def test_export_is_explicit_allowlisted_escaped_and_review_bound(self):
        io = mod('publication'); e = mod('engine')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); repo, commit = fixture(root)
            snap = mod('source').freeze(repo, commit, root / 'private')
            run = e.investigate(ISSUE, snap, Judge(['search_text', 'synthesize']), Qwen(), mode='offline-test')
            run['private_extra'] = 'DO NOT EXPORT'
            review = io.review(run)
            with self.assertRaises(ValueError): io.export(run, root / 'public', review, False, [])
            with self.assertRaises(ValueError): io.export(run, root / 'public', '0' * 64, True, ['src/logic.py', 'public.txt'])
            io.export(run, root / 'public', review, True, list(snap.files))
            js = (root / 'public' / 'investigation.js').read_text()
            self.assertNotIn('</script>', js)
            self.assertNotIn('DO NOT EXPORT', js)
            artifact = json.loads((root / 'public' / 'investigation.json').read_text())
            self.assertEqual(artifact['mode'], 'offline-test')
            self.assertTrue(e.validate_run(artifact))

    def test_console_starts_empty_and_never_inserts_source_as_html(self):
        root = Path(__file__).resolve().parents[1] / 'apps' / 'investigator'
        self.assertTrue((root / 'index.html').exists(), 'console not implemented')
        app = (root / 'app.js').read_text()
        self.assertNotIn('innerHTML', app)
        self.assertIn('textContent', app)
        self.assertIn('createElementNS', app)
        self.assertFalse((root / 'investigation.json').exists(), 'no fake successful sample')


if __name__ == '__main__': unittest.main()
