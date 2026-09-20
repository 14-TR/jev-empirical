"""Private metadata-only traces, in a NEW directory outside every Git tree."""
import json
import os
from pathlib import Path

from jev_bench.core import require
from .workspace import DIR_FLAGS


class Trace:
    def __init__(self, path):
        path = Path(path).expanduser()
        require('..' not in path.parts, 'trace_traversal')
        path = path.absolute()
        require(len(path.parts) > 1, 'trace_directory_must_be_new')
        source_root = Path(__file__).resolve().parents[2]
        require(path != source_root and source_root not in path.parents, 'trace_inside_repository')
        fd, file_fd = os.open(path.anchor, DIR_FLAGS), None
        self.handle = None
        self.bytes = 0
        try:
            for index, part in enumerate(path.parts[1:]):
                try:
                    os.stat('.git', dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    raise ValueError('trace_inside_repository')
                last = index == len(path.parts) - 2
                try:
                    os.mkdir(part, mode=0o700, dir_fd=fd)
                except FileExistsError:
                    require(not last, 'trace_directory_must_be_new')
                nxt = os.open(part, DIR_FLAGS, dir_fd=fd)
                os.close(fd)
                fd = nxt
            os.fchmod(fd, 0o700)
            file_fd = os.open('events.jsonl', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            self.handle = os.fdopen(file_fd, 'w', encoding='utf-8')
            file_fd = None
            self.path = path
        except OSError:
            raise ValueError('trace_path_denied') from None
        finally:
            if file_fd is not None: os.close(file_fd)
            os.close(fd)

    def __enter__(self): return self

    def __exit__(self, *args):
        if self.handle is not None: self.handle.close()

    def record(self, event):
        raw = json.dumps(event, ensure_ascii=False, allow_nan=False) + '\n'
        key = os.environ.get('TYPESAFE_API_KEY')
        require(not key or key not in raw, 'trace_sensitive_content')
        self.bytes += len(raw.encode('utf-8'))
        require(self.bytes <= 131072, 'trace_budget')
        handle = self.handle
        if handle is None:
            raise ValueError('trace_closed')
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
