import importlib
import os
from pathlib import Path
import tempfile
import unittest


def load(name):
    try:
        return importlib.import_module('jev_agent.' + name)
    except ImportError:
        raise AssertionError('missing agent module: ' + name) from None


class WorkspaceTests(unittest.TestCase):
    def test_credential_json_and_hardlinks_are_denied(self):
        api = load('workspace')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / 'settings.json').write_text('{"api_key": "private-value"}')
            (root / 'public.md').write_text('public')
            os.link(root / 'public.md', root / 'copy.md')
            with api.Workspace(root) as ws:
                rows = ws.list_files()
                self.assertEqual([r['name'] for r in rows], ['settings.json'])
                with self.assertRaises(ValueError): ws.read_file(rows[0]['id'])

    def test_original_fixture_has_conflict_and_supersession_evidence(self):
        root = Path(__file__).resolve().parents[1] / 'examples' / 'agent-workspace'
        self.assertTrue(root.is_dir(), 'missing original live-demo workspace')
        api = load('workspace')
        with api.Workspace(root) as ws:
            rows = ws.list_files()
            self.assertEqual(len(rows), 4)
            docs = {row['name']: ws.read_file(row['id'])['text'] for row in rows}
        self.assertIn('14 days', docs['policy-v3.md'])
        self.assertIn('30 days', docs['support-handbook.md'])
        self.assertIn('supersedes', docs['change-register.md'])
        self.assertIn('2026-09-01', docs['change-register.md'])

    def test_denied_names_symlinks_binary_and_swaps_never_read(self):
        api = load('workspace')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / 'good.md').write_text('Useful public evidence')
            for name in ('.env', 'credentials.json', 'secret.txt', 'id_rsa', 'token.md'):
                (root / name).write_text('sensitive')
            (root / 'binary.txt').write_bytes(b'abc\x00def')
            (root / 'link.md').symlink_to(root / 'good.md')
            (root / '.hidden').mkdir()
            (root / '.hidden' / 'nested.md').write_text('hidden')
            with api.Workspace(root) as ws:
                rows = ws.list_files()
                self.assertEqual({r['name'] for r in rows}, {'binary.txt', 'good.md'})
                by_name = {r['name']: r['id'] for r in rows}
                with self.assertRaises(ValueError): ws.read_file(by_name['binary.txt'])
                (root / 'good.md').unlink()
                (root / 'good.md').symlink_to(root / '.env')
                with self.assertRaises(ValueError): ws.read_file(by_name['good.md'])
            with self.assertRaises(ValueError): api.Workspace(root / '..')
            with self.assertRaises(ValueError): api.Workspace(root / 'link.md')

    def test_nested_descriptor_reads_and_bounds(self):
        api = load('workspace')
        import inspect
        self.assertIn('max_file_bytes', inspect.signature(api.Workspace).parameters)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / 'docs').mkdir()
            (root / 'docs' / 'ok.md').write_text('hello')
            with api.Workspace(root, max_file_bytes=4) as ws:
                self.assertEqual(ws.list_files(), [])
            with api.Workspace(root) as ws:
                rows = ws.list_files()
                self.assertEqual(rows[0]['name'], 'docs/ok.md')
                self.assertEqual(ws.read_file(rows[0]['id'])['text'], 'hello')
                (root / 'docs' / 'ok.md').write_text('password=do-not-upload')
                with self.assertRaises(ValueError): ws.read_file(rows[0]['id'])
            for i in range(3): (root / ('f%d.md' % i)).write_text('a')
            with api.Workspace(root, max_files=2) as ws:
                with self.assertRaises(ValueError): ws.list_files()

    def test_enumerated_read_only_workspace(self):
        api = load('workspace')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / 'policy.md').write_text('Current policy.\n', encoding='utf-8')
            with api.Workspace(root) as ws:
                rows = ws.list_files()
                self.assertEqual(rows, [{'id': 'f0001', 'name': 'policy.md', 'bytes': 16}])
                evidence = ws.read_file('f0001')
                self.assertEqual(evidence['text'], 'Current policy.\n')
                self.assertEqual(evidence['id'], 'f0001')
                self.assertEqual(len(evidence['sha256']), 64)
                with self.assertRaises(ValueError):
                    ws.read_file('../policy.md')
            self.assertEqual((root / 'policy.md').read_text(), 'Current policy.\n')
