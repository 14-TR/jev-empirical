import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_investigator_source import mod, fixture
from test_investigator_loop import ISSUE


class CLITests(unittest.TestCase):
    def test_live_denied_before_issue_or_provider_access(self):
        cli = mod('cli')
        with patch('jev_investigator.cli.fetch_issue', side_effect=AssertionError('must not fetch')):
            with contextlib.redirect_stderr(io.StringIO()):
                code = cli.main(['run', '--issue', ISSUE['url'], '--source-repo', '/invalid', '--commit', 'a'*40, '--private', '/invalid'])
        self.assertEqual(code, 2)

    def test_freeze_cli_issue_failure_never_becomes_success(self):
        cli = mod('cli')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); repo, commit = fixture(root)
            args = ['freeze', '--issue', ISSUE['url'], '--source-repo', str(repo), '--commit', commit, '--private', str(root/'bundle')]
            with patch('jev_investigator.cli.fetch_issue', side_effect=ValueError('issue_fetch_failed')):
                with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(cli.main(args), 2)
            self.assertFalse((root/'bundle').exists())
            with patch('jev_investigator.cli.fetch_issue', return_value=ISSUE), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(args), 0)
            self.assertEqual(json.loads((root/'bundle'/'snapshot.json').read_text())['commit'], commit)
            self.assertEqual(json.loads((root/'bundle'/'issue.json').read_text()), ISSUE)
            self.assertFalse((root/'bundle'/'run.json').exists())
            preparation = json.loads((root/'bundle'/'preparation.json').read_text())
            self.assertEqual([e['label'] for e in preparation], ['gh issue view', 'issue fetched', 'git archive', 'source frozen'])

    def test_qwen_adapter_carries_only_evidence_no_tools_and_caps_tokens(self):
        provider = mod('providers')
        with patch('jev_investigator.providers.bounded_request', return_value={'status':'timeout'}) as transport:
            self.assertEqual(provider.Qwen().reason('hypothesis', [], 3), {'status':'timeout'})
        payload = transport.call_args[0][0]
        self.assertEqual(payload['model'], 'qwen2.5:7b')
        self.assertEqual(payload['options']['num_predict'], 1000)
        self.assertNotIn('tools', payload)
        self.assertEqual(transport.call_args[0][1], 3)


if __name__ == '__main__': unittest.main()
