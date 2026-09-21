"""Read-only immutable Git inputs. No checkout, hooks, submodules or credentials.

The private filtered archive is NOT an OS sandbox. Trusted test profiles may
execute repository code; the operator must authorize that separately.
"""
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import signal
import stat
import subprocess
import tarfile
import time

from jev_agent.trace import Trace
from jev_agent.workspace import open_directory, SECRET_TEXT

MAX_FILE = 131072
MAX_TOTAL = 4194304
MAX_FILES = 256
SUFFIXES = {'.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.md', '.txt', '.toml', '.json', '.yml', '.yaml', '.rst', '.csv'}
DENIED = re.compile(r'credential|secret|password|passwd|token|api[-_ ]?key|receipt|private|node_modules|__pycache__|^venv$|^env$|^dist$|^build$|^coverage$|\.pem$|\.key$', re.I)
SHA = re.compile(r'[a-f0-9]{40}\Z')
URL = re.compile(r'https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/([A-Za-z0-9_][A-Za-z0-9_.-]{0,99})/issues/([1-9][0-9]{0,8})\Z')


def issue_url(url):
    match = URL.fullmatch(url) if type(url) is str else None
    if not match or match[2] in ('.', '..') or match[2].endswith('.git'):
        raise ValueError('invalid_issue_url')
    return match[1], match[2], int(match[3])


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(path):
    if not isinstance(path, str) or len(path) > 240 or '\\' in path:
        return False
    parts = PurePosixPath(path).parts
    return bool(parts) and not path.startswith('/') and all(
        re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_. -]{0,99}', part) and not DENIED.search(part)
        for part in parts) and PurePosixPath(path).suffix.lower() in SUFFIXES


def safe_text(text):
    if any(ord(c) < 32 and c not in '\t\n\r' for c in text) or SECRET_TEXT.search(text):
        return False
    return not any(value and len(value) >= 8 and value in text for key, value in os.environ.items()
                   if re.search(r'TOKEN|KEY|SECRET|PASSWORD|CREDENTIAL', key, re.I))


def child_env(home):
    """Allowlist, not a credential denylist. No inherited PYTHONPATH or proxies."""
    return {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'HOME': str(home), 'TMPDIR': str(home),
            'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONNOUSERSITE': '1', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
            'GIT_OPTIONAL_LOCKS': '0', 'GIT_TERMINAL_PROMPT': '0'}


def command(argv, cwd=None, env=None, timeout=20, cap=65536):
    """Bound output and whole process-group lifetime; never a shell."""
    if timeout <= 0:
        raise ValueError('time_budget')
    proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    assert proc.stdout is not None
    selector = selectors.DefaultSelector(); selector.register(proc.stdout, selectors.EVENT_READ)
    result = bytearray(); deadline = time.monotonic() + timeout
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0: raise ValueError('command_timeout')
            for key, _ in selector.select(min(remaining, .1)):
                chunk = os.read(key.fd, min(65536, cap + 1 - len(result)))
                if not chunk:
                    selector.unregister(key.fileobj); continue
                result.extend(chunk)
                if len(result) > cap: raise ValueError('command_output_budget')
        code = proc.wait(timeout=max(.001, deadline - time.monotonic()))
        return code, bytes(result)
    finally:
        selector.close(); proc.stdout.close()
        try: os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        proc.wait()


def git(repo, args, timeout=20, cap=MAX_TOTAL):
    code, raw = command(['/usr/bin/git', '--no-replace-objects', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false',
                         '-c', 'diff.external=', '-C', str(repo)] + args,
                        env=child_env('/nonexistent'), timeout=timeout, cap=cap)
    if code: raise ValueError('git_read_failed')
    return raw


def private_directory(path):
    # Trace already implements descriptor-relative no-follow creation outside Git.
    with Trace(path): pass
    return Path(path).absolute()


def save_json(path, value):
    data = json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False).encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())


def fetch_issue(url, timeout=20):
    owner, repo, number = issue_url(url)
    # Fixed read-only JSON fields; neither issue prose nor model can add arguments.
    env = dict(os.environ, GH_PROMPT_DISABLED='1', GH_PAGER='cat', NO_COLOR='1')
    code, raw = command(['gh', 'issue', 'view', str(number), '--repo', owner + '/' + repo,
                         '--json', 'url,number,title,body,state,updatedAt'], env=env, timeout=timeout, cap=32768)
    if code: raise ValueError('issue_fetch_failed')
    try: value = json.loads(raw)
    except (ValueError, UnicodeError): raise ValueError('issue_response_invalid') from None
    if (type(value) is not dict or value.get('url') != url or value.get('number') != number
            or not all(type(value.get(k)) is str for k in ('title', 'body', 'state', 'updatedAt'))
            or len(value['body']) > 18000 or not safe_text(value['title'] + '\n' + value['body'])):
        raise ValueError('issue_response_invalid')
    return {k: value[k] for k in ('url', 'number', 'title', 'body', 'state', 'updatedAt')}


class Snapshot:
    def __init__(self, root, repo, commit, files):
        self.root, self.repo, self.commit, self.files = Path(root), Path(repo), commit, files

    def read(self, path):
        if path not in self.files or not safe_path(path): raise ValueError('path_denied')
        fd = open_directory(self.root); file_fd = None
        try:
            parts = PurePosixPath(path).parts
            for part in parts[:-1]:
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = nxt
            file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            info = os.fstat(file_fd)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_FILE:
                raise ValueError('source_changed')
            raw = os.pread(file_fd, MAX_FILE + 1, 0)
            if digest(raw) != self.files[path]['sha256']: raise ValueError('source_changed')
            return raw.decode('utf-8')
        except (OSError, UnicodeError): raise ValueError('source_read_denied') from None
        finally:
            if file_fd is not None: os.close(file_fd)
            os.close(fd)


def freeze(repo, commit, private):
    if type(commit) is not str or not SHA.fullmatch(commit): raise ValueError('full_commit_required')
    repo = Path(repo).absolute()
    fd = open_directory(repo); os.close(fd)
    actual = git(repo, ['rev-parse', '--verify', commit + '^{commit}'], cap=256).decode().strip()
    if actual != commit: raise ValueError('commit_mismatch')
    listing = git(repo, ['ls-tree', '-r', '-l', '-z', commit], cap=262144)
    names = []; blobs = {}
    for row in listing.split(b'\0'):
        if not row: continue
        meta, name = row.split(b'\t', 1); mode, kind, blob, size = meta.split()
        path = name.decode('utf-8', errors='replace')
        if kind != b'blob' or mode not in (b'100644', b'100755') or not safe_path(path): continue
        if int(size) > MAX_FILE: continue
        names.append(path)
        blobs[path] = blob.decode('ascii')
    if not names or len(names) > MAX_FILES: raise ValueError('snapshot_file_budget')
    # git archive does not initialize submodules or execute repository hooks.
    raw = git(repo, ['archive', '--format=tar', commit, '--'] + names, cap=MAX_TOTAL + 1048576)
    private = private_directory(private); root = private / 'source'; root.mkdir(mode=0o700)
    files = {}; total = 0
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive:
            if not member.isfile() or member.name not in names or member.size > MAX_FILE: continue
            handle = archive.extractfile(member)
            if handle is None: raise ValueError('archive_invalid')
            data = handle.read(MAX_FILE + 1)
            blob_hash = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
            if blob_hash != blobs[member.name]: raise ValueError('archive_transformed_source')
            try: text = data.decode('utf-8')
            except UnicodeError: continue
            if not safe_text(text): continue
            total += len(data)
            if total > MAX_TOTAL: raise ValueError('snapshot_byte_budget')
            target = root / member.name; target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as handle: handle.write(data)
            files[member.name] = {'sha256': digest(data), 'bytes': len(data)}
    if not files: raise ValueError('empty_snapshot')
    save_json(private / 'snapshot.json', {'commit': commit, 'source_repo': str(repo), 'files': files,
                                         'filter': 'public-text-only-v1', 'os_sandbox': False})
    return Snapshot(root, repo, commit, files)
