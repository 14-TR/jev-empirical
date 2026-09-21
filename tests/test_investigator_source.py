import importlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


def mod(name):
    try:
        return importlib.import_module('jev_investigator.' + name)
    except ImportError:
        raise AssertionError('investigator module missing: ' + name) from None


def fixture(root):
    repo = root / 'repo'; repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    (repo / 'src').mkdir()
    (repo / 'src' / 'logic.py').write_text('def pressure(value):\n    return value + 1\n')
    (repo / '.env').write_text('PRIVATE=do-not-copy\n')
    (repo / 'receipts').mkdir(); (repo / 'receipts' / 'raw.json').write_text('{"private":true}')
    (repo / 'public.txt').write_text('pressure regression\n')
    (repo / 'link.py').symlink_to('src/logic.py')
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True)
    commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    return repo, commit


class SourceTests(unittest.TestCase):
    def test_archive_attribute_rewriting_cannot_impersonate_commit_bytes(self):
        s = mod('source')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); repo, _ = fixture(root)
            (repo / '.gitattributes').write_text('public.txt export-subst\n')
            (repo / 'public.txt').write_text('$Format:%H$\n')
            subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'attributes'], check=True)
            commit = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
            with self.assertRaises(ValueError): s.freeze(repo, commit, root / 'private')

    def test_command_deadline_and_output_cap(self):
        import sys
        s = mod('source')
        with self.assertRaisesRegex(ValueError, 'command_timeout'):
            s.command([sys.executable, '-I', '-S', '-c', 'import time; time.sleep(5)'], timeout=.05)
        with self.assertRaisesRegex(ValueError, 'command_output_budget'):
            s.command([sys.executable, '-I', '-S', '-c', 'print("x" * 1000)'], timeout=2, cap=50)

    def test_strict_url_snapshot_filters_and_commit_identity(self):
        s = mod('source')
        self.assertEqual(s.issue_url('https://github.com/14-TR/jev-empirical/issues/1'), ('14-TR', 'jev-empirical', 1))
        for url in ('http://github.com/o/r/issues/1', 'https://github.com/o/r/issues/0',
                    'https://github.com/o/r/issues/1?x=1', 'https://github.com/o/r/issues/1/',
                    'https://github.com/o/r/issues/01', 'https://github.com/o/r/issues/1#x',
                    'https://github.com/o/../issues/1', 'https://github.com.evil/o/r/issues/1'):
            with self.assertRaises(ValueError): s.issue_url(url)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); repo, commit = fixture(root)
            before = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'])
            (repo / 'src' / 'logic.py').write_text('dirty source must not be read\n')
            snapshot = s.freeze(repo, commit, root / 'private')
            self.assertEqual(snapshot.commit, commit)
            self.assertEqual(snapshot.read('src/logic.py'), 'def pressure(value):\n    return value + 1\n')
            self.assertFalse((snapshot.root / '.git').exists())
            self.assertEqual(set(snapshot.files), {'src/logic.py', 'public.txt'})
            self.assertEqual((repo / 'src' / 'logic.py').read_text(), 'dirty source must not be read\n')
            for path in ('../public.txt', '/etc/passwd', '.env', 'link.py', 'receipts/raw.json'):
                with self.assertRaises(ValueError): snapshot.read(path)
            (snapshot.root / 'public.txt').write_text('tampered\n')
            with self.assertRaises(ValueError): snapshot.read('public.txt')
            self.assertEqual((root / 'private').stat().st_mode & 0o777, 0o700)


if __name__ == '__main__': unittest.main()
