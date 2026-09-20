"""Bounded descriptor-relative reads. Paths never cross the model boundary as actions.

A listing freezes identities, not contents: a changed file fails closed on read.
The workspace must be an explicit, non-symlink directory. Credential filtering is
conservative best effort, not a guarantee that arbitrary prose is non-sensitive.
"""
import hashlib
import os
from pathlib import Path
import re
import stat

from jev_bench.core import require

SAFE_NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9 _.,()-]{0,119}\Z')
SENSITIVE = re.compile(r'credential|secret|password|passwd|token|api[-_ ]?key|id_rsa|id_ed25519|keychain|\.pem$|\.key$', re.I)
SECRET_TEXT = re.compile(r'''-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:api[_-]?key|access[_-]?token|password|secret)["']?\s*[=:]\s*\S+|\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16})''', re.I)
TEXT_SUFFIXES = {'.md', '.txt', '.rst', '.csv', '.json', '.yaml', '.yml'}
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK


def identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def safe_name(name):
    return SAFE_NAME.fullmatch(name) is not None and not SENSITIVE.search(name)


def open_directory(path):
    """Open every component with no-follow; reject lexical traversal first."""
    path = Path(path).expanduser()
    require('..' not in path.parts, 'workspace_traversal')
    path = path.absolute()
    fd = os.open(path.anchor, DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            nxt = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd
    except Exception:
        os.close(fd)
        raise ValueError('workspace_path_denied') from None


class Workspace:
    def __init__(self, root, max_files=32, max_file_bytes=8192, max_entries=256, max_depth=4):
        for value, upper in ((max_files, 64), (max_file_bytes, 16384), (max_entries, 1024), (max_depth, 8)):
            require(type(value) is int and 0 < value <= upper, 'workspace_limit')
        self.root = Path(root).expanduser().absolute()
        self.max_files, self.max_file_bytes = max_files, max_file_bytes
        self.max_entries, self.max_depth = max_entries, max_depth
        self.fd = open_directory(root)
        self.candidates = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def list_files(self):
        require(self.fd is not None, 'workspace_closed')
        found, visited = [], [0]
        def walk(fd, parts):
            # scandir is consumed incrementally, never materialize an unbounded directory.
            with os.scandir(fd) as entries:
                for entry in entries:
                    visited[0] += 1
                    require(visited[0] <= self.max_entries, 'workspace_entry_budget')
                    if not safe_name(entry.name):
                        continue
                    info = entry.stat(follow_symlinks=False)
                    rel = parts + (entry.name,)
                    if stat.S_ISDIR(info.st_mode):
                        require(len(rel) <= self.max_depth, 'workspace_depth_budget')
                        child = os.open(entry.name, DIR_FLAGS, dir_fd=fd)
                        try:
                            walk(child, rel)
                        finally:
                            os.close(child)
                    elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and Path(entry.name).suffix.lower() in TEXT_SUFFIXES:
                        if info.st_size <= self.max_file_bytes:
                            found.append((rel, identity(info)))
                            require(len(found) <= self.max_files, 'workspace_file_budget')
        try:
            walk(self.fd, ())
        except OSError:
            raise ValueError('workspace_listing_failed') from None
        self.candidates = {'f%04d' % i: row for i, row in enumerate(sorted(found), 1)}
        return [{'id': key, 'name': '/'.join(parts), 'bytes': ident[2]}
                for key, (parts, ident) in self.candidates.items()]

    def read_file(self, selector):
        require(type(selector) is str and selector in self.candidates, 'unknown_selector')
        require(self.fd is not None, 'workspace_closed')
        assert self.fd is not None  # Narrow for static checkers; require enforces under -O.
        parts, expected = self.candidates[selector]
        fd, file_fd = os.dup(self.fd), None
        try:
            for part in parts[:-1]:
                nxt = os.open(part, DIR_FLAGS, dir_fd=fd)
                os.close(fd)
                fd = nxt
            file_fd = os.open(parts[-1], FILE_FLAGS, dir_fd=fd)
            info = os.fstat(file_fd)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and identity(info) == expected, 'workspace_changed')
            require(info.st_size <= self.max_file_bytes, 'file_too_large')
            raw = os.pread(file_fd, self.max_file_bytes + 1, 0)
            require(len(raw) == info.st_size and len(raw) <= self.max_file_bytes and identity(os.fstat(file_fd)) == expected, 'workspace_changed')
            text = raw.decode('utf-8')
            require(not any(ord(c) < 32 and c not in '\n\r\t' for c in text), 'binary_file')
            require(not SECRET_TEXT.search(text), 'sensitive_content')
            key = os.environ.get('TYPESAFE_API_KEY')
            require(not key or key not in text, 'sensitive_content')
            return {'id': selector, 'name': '/'.join(parts), 'text': text, 'sha256': hashlib.sha256(raw).hexdigest()}
        except (OSError, UnicodeError):
            raise ValueError('workspace_read_denied') from None
        finally:
            if file_fd is not None:
                os.close(file_fd)
            os.close(fd)
