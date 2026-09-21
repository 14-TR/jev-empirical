"""Explicit, hash-reviewed, allowlisted public material; raw traces stay private."""
import copy
import json
import os
from pathlib import Path
from .engine import canonical, graph, validate_run
from .source import digest, open_directory, safe_path, safe_text

FIELDS = ('schema', 'mode', 'issue', 'commit', 'files', 'events', 'observations', 'reports', 'limits', 'metrics', 'outcome', 'execution', 'evidence')


def review(run):
    validate_run(run)
    return digest(canonical({key: run[key] for key in FIELDS}).encode())


def export(run, target, reviewed_sha256, public_source, public_paths):
    if not public_source: raise ValueError('explicit_public_issue_and_source_consent_required')
    if review(run) != reviewed_sha256: raise ValueError('review_mismatch')
    allowed = set(public_paths)
    if not allowed or not all(safe_path(p) and p in run['files'] for p in allowed): raise ValueError('invalid_public_paths')
    observed = {r['path'] for o in run['observations'] for r in o.get('refs', []) if 'path' in r}
    # Decision selectors contain source paths too. Do not leak their names by accident.
    observed.update(c['observation']['selected']['args']['path'] for c in run['events']
                    if 'selected' in c['observation'] and 'path' in c['observation']['selected']['args'])
    if not observed <= allowed: raise ValueError('source_not_publicly_allowlisted')
    result = {key: copy.deepcopy(run[key]) for key in FIELDS}
    result['files'] = {p: m for p, m in result['files'].items() if p in allowed}
    result['execution'], result['evidence'] = graph(result)
    validate_run(result)
    raw = json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False)
    if not safe_text(raw): raise ValueError('sensitive_export')
    if len(raw.encode()) > 524288: raise ValueError('export_budget')
    target = Path(target).absolute()
    if '..' in target.parts: raise ValueError('export_path_denied')
    target.mkdir(parents=True, exist_ok=True)
    fd = open_directory(target)
    try:
        # O_EXCL intentionally refuses to overwrite an existing reviewed publication.
        for name, content in [('investigation.json', raw), ('investigation.js', 'window.INVESTIGATION = ' + raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026') + ';\n')]:
            out = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=fd)
            with os.fdopen(out, 'w', encoding='utf-8') as handle: handle.write(content)
    finally: os.close(fd)
    return result
