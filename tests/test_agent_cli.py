import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from test_agent_loop import FakeJev, FakeOllama


def load(name):
    try: return importlib.import_module('jev_agent.' + name)
    except ImportError: raise AssertionError('missing agent module: ' + name) from None


class CLITests(unittest.TestCase):
    def test_trace_filesystem_root_is_not_chmodded(self):
        api = load('trace')
        with patch.object(api.os, 'fchmod', side_effect=AssertionError('must not chmod filesystem root')):
            with self.assertRaises(ValueError): api.Trace(Path('/'))

    def test_consent_and_missing_key_stop_before_provider_construction(self):
        cli = load('cli')
        base = ['run', '--workspace', '/nonexistent', '--goal', 'g', '--trace-dir', '/nonexistent']
        for flags, code in [([], 'live_consent_required'), (['--allow-live'], 'workspace_upload_consent_required'),
                            (['--allow-live', '--allow-workspace-upload'], 'missing_key')]:
            with patch.dict(os.environ, {}, clear=True), patch.object(cli, 'Jev') as adapter, contextlib.redirect_stdout(io.StringIO()) as out:
                result = cli.main(base + flags)
            self.assertEqual(result, 2)
            self.assertIn(code, out.getvalue())
            adapter.assert_not_called()

    def test_cli_full_offline_injected_run_and_private_trace(self):
        cli = load('cli')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            workspace = root / 'workspace'
            workspace.mkdir()
            (workspace / 'policy.md').write_text('Original public source. NEVER-LOG-RAW-EVIDENCE')
            trace = root / 'private-trace'
            args = ['run', '--workspace', str(workspace), '--goal', 'Compare policy', '--trace-dir', str(trace), '--allow-live', '--allow-workspace-upload']
            with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'offline-placeholder-only'}), patch.object(cli, 'Jev', FakeJev), patch.object(cli, 'Ollama', FakeOllama), contextlib.redirect_stdout(io.StringIO()) as out:
                result = cli.main(args)
            self.assertEqual(result, 0)
            parsed = json.loads(out.getvalue())
            self.assertEqual(parsed['status'], 'completed')
            self.assertEqual(parsed['provider_requests'], {'fake-jev-offline': 3, 'fake-ollama-offline': 1})
            self.assertEqual(stat.S_IMODE(trace.stat().st_mode), 0o700)
            receipts = list(trace.iterdir())
            self.assertTrue(receipts)
            for receipt in receipts:
                self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
                self.assertNotIn('NEVER-LOG-RAW-EVIDENCE', receipt.read_text())
                self.assertNotIn('offline-placeholder-only', receipt.read_text())
            self.assertIn('completed', (trace / 'events.jsonl').read_text())

    def test_cli_late_trace_failure_does_not_claim_zero_provider_calls(self):
        cli = load('cli')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            workspace = root / 'workspace'
            workspace.mkdir()
            (workspace / 'policy.md').write_text('Original public source')
            args = ['run', '--workspace', str(workspace), '--goal', 'Compare policy', '--trace-dir', str(root / 'trace'), '--allow-live', '--allow-workspace-upload']
            record = cli.Trace.record
            def fail_final(trace, event):
                if event['kind'] == 'result': raise OSError('PRIVATE IO DETAILS')
                return record(trace, event)
            with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'offline-placeholder-only'}), patch.object(cli, 'Jev', FakeJev), patch.object(cli, 'Ollama', FakeOllama), patch.object(cli.Trace, 'record', fail_final), contextlib.redirect_stdout(io.StringIO()) as out:
                status = cli.main(args)
            result = json.loads(out.getvalue())
            self.assertEqual(status, 2)
            self.assertEqual(result.get('provider_requests'), {'fake-jev-offline': 3, 'fake-ollama-offline': 1})
            self.assertNotIn('PRIVATE', str(result))

    def test_trace_rejects_git_symlink_and_reuse(self):
        api = load('trace')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            (root / 'repo').mkdir()
            (root / 'repo' / '.git').mkdir()
            with self.assertRaises(ValueError): api.Trace(root / 'repo' / 'trace')
            (root / 'alias').symlink_to(root / 'repo')
            with self.assertRaises(ValueError): api.Trace(root / 'alias' / 'trace')
            with api.Trace(root / 'private') as trace:
                trace.record({'kind': 'test'})
            with self.assertRaises(ValueError): api.Trace(root / 'private')
            with self.assertRaises(ValueError): api.Trace(root / '..' / 'trace')
