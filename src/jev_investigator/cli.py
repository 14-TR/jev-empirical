"""Private preparation/run, explicit review, separate explicit public export."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from .source import fetch_issue, freeze, save_json, Snapshot, open_directory
from .engine import investigate
from .publication import review, export
from .checks import PROFILES, run_check


def read_json(path):
    path = Path(path).absolute(); fd = open_directory(path.parent)
    try:
        f = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(f, 'rb') as handle: raw = handle.read(524289)
        if len(raw) > 524288: raise ValueError('input_budget')
        from jev_bench.core import strict_json
        return strict_json(raw)
    finally: os.close(fd)


def load_snapshot(bundle):
    bundle = Path(bundle).absolute(); meta = read_json(bundle / 'snapshot.json')
    snap = Snapshot(bundle / 'source', meta['source_repo'], meta['commit'], meta['files'])
    for path in snap.files: snap.read(path)
    return snap


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only bounded issue investigation; no fixes, comments, commits or live fallback.')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('freeze', 'run'):
        p = sub.add_parser(name)
        p.add_argument('--issue', required=True); p.add_argument('--source-repo', required=True)
        p.add_argument('--commit', required=True); p.add_argument('--private', required=True)
        if name == 'run':
            p.add_argument('--allow-live', action='store_true'); p.add_argument('--allow-source-upload', action='store_true')
            p.add_argument('--allow-checks', action='store_true'); p.add_argument('--profile', choices=PROFILES, action='append', default=[])
            p.add_argument('--steps', type=int, default=12); p.add_argument('--seconds', type=float, default=300)
    p = sub.add_parser('check'); p.add_argument('--bundle', required=True)
    p.add_argument('--allow-checks', action='store_true'); p.add_argument('--profile', choices=PROFILES, required=True)
    p = sub.add_parser('review'); p.add_argument('--run', required=True)
    p = sub.add_parser('export'); p.add_argument('--run', required=True); p.add_argument('--out', required=True)
    p.add_argument('--review-sha256', required=True); p.add_argument('--allow-public-source', action='store_true')
    p.add_argument('--public-path', action='append', default=[])
    args = parser.parse_args(argv)
    try:
        if args.command in ('freeze', 'run'):
            start = time.monotonic()
            if args.command == 'run':
                if not (args.allow_live and args.allow_source_upload): raise ValueError('live_upload_consent_required')
                if args.profile and not args.allow_checks: raise ValueError('check_consent_required')
                import math
                if not 1 <= args.steps <= 12 or not math.isfinite(args.seconds) or not 1 <= args.seconds <= 300:
                    raise ValueError('invalid_budget')
            issue = fetch_issue(args.issue)
            snap = freeze(args.source_repo, args.commit, args.private)
            save_json(snap.root.parent / 'issue.json', issue)
            preparation = [
                {'kind': 'tool', 'label': 'gh issue view', 'observation': {'url': args.issue, 'fields': 'url,number,title,body,state,updatedAt'}},
                {'kind': 'result', 'label': 'issue fetched', 'observation': {'url': issue['url'], 'updatedAt': issue['updatedAt']}},
                {'kind': 'tool', 'label': 'git archive', 'observation': {'commit': snap.commit, 'filter': 'public-text-only-v1'}},
                {'kind': 'result', 'label': 'source frozen', 'observation': {'commit': snap.commit, 'file_count': len(snap.files)}}]
            save_json(snap.root.parent / 'preparation.json', preparation)
            if args.command == 'freeze':
                print(json.dumps({'status': 'frozen', 'commit': snap.commit, 'file_count': len(snap.files), 'private': str(snap.root.parent), 'inference_calls': 0})); return 0
            from .providers import Jev, Qwen
            calls = [0]
            def record(value):
                calls[0] += 1
                save_json(snap.root.parent / ('receipt-%03d.json' % calls[0]), value)
            remaining = args.seconds - (time.monotonic() - start)
            if remaining <= 0: raise ValueError('time_budget')
            run = investigate(issue, snap, Jev(), Qwen(), mode='recorded-live', allow_live=args.allow_live,
                              allow_source_upload=args.allow_source_upload, allow_checks=args.allow_checks,
                              profiles=tuple(args.profile), max_steps=args.steps, seconds=remaining, record=record,
                              preparation=preparation,
                              check=lambda profile, timeout: run_check(profile, snap, args.allow_checks, tuple(args.profile), timeout))
            save_json(snap.root.parent / 'run.json', run)
            print(json.dumps({'outcome': run['outcome'], 'metrics': run['metrics'], 'run': str(snap.root.parent / 'run.json'), 'public_export': False}))
            return 0 if run['outcome']['status'] == 'reported' else 2
        if args.command == 'check':
            snap = load_snapshot(args.bundle)
            result = run_check(args.profile, snap, args.allow_checks, (args.profile,), 25)
            save_json(snap.root.parent / (args.profile + '.json'), result)
            print(json.dumps(result)); return 0 if result['exit_code'] == 0 else 2
        run = read_json(args.run)
        if args.command == 'review':
            print(json.dumps({'review_sha256': review(run), 'outcome': run['outcome'], 'metrics': run['metrics'],
                              'files': list(run['files']), 'observations': run['observations'], 'reports': run['reports']}, indent=2))
        else:
            export(run, args.out, args.review_sha256, args.allow_public_source, args.public_path)
            print(json.dumps({'exported': str(Path(args.out).absolute()), 'mode': run['mode']}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Fixed error codes only; never provider bodies, credentials or arbitrary paths.
        code = str(exc)
        if not code.isidentifier() or len(code) > 80: code = 'operation_failed'
        print('investigator: ' + code, file=sys.stderr); return 2
