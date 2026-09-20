"""python3 -m incident_room: offline by default; live requires explicit consent."""
import argparse
import json
import os
from pathlib import Path
from jev_bench.core import strict_json
from jev_agent.trace import Trace
from .episode import run, validate_replay
from .io import public_episode, write_public


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('run'); p.add_argument('--mode', choices=['offline-rule', 'live-hybrid'], default='offline-rule')
    p.add_argument('--allow-live', action='store_true'); p.add_argument('--private-dir')
    p.add_argument('--max-ticks', type=int, default=12); p.add_argument('--max-jev', type=int, default=20)
    p.add_argument('--max-qwen', type=int, default=2); p.add_argument('--seconds', type=float, default=300)
    for p in (p, sub.add_parser('export')):
        p.add_argument('--public', required=True); p.add_argument('--asset'); p.add_argument('--publish-advisory', action='store_true')
    sub.choices['export'].add_argument('receipt')
    sub.add_parser('validate').add_argument('episode')
    args = parser.parse_args(argv)
    try:
        if args.command == 'validate':
            validate_replay(strict_json(Path(args.episode).read_bytes())); print('Exact deterministic reexecution: PASS'); return 0
        if args.command == 'export':
            e = strict_json(Path(args.receipt).read_bytes())
        elif args.mode == 'live-hybrid':
            if not args.allow_live or not args.private_dir or not os.environ.get('TYPESAFE_API_KEY'):
                print('Live refused: --allow-live, new --private-dir, and TYPESAFE_API_KEY are required.'); return 2
            from .providers import Jev, Qwen
            with Trace(args.private_dir) as trace:
                e = run(mode=args.mode, max_ticks=args.max_ticks, max_jev=args.max_jev,
                        max_qwen=args.max_qwen, seconds=args.seconds, jev=Jev(), qwen=Qwen(), record=trace.record)
                # Immutable new receipt, private directory 0700 and file 0600.
                fd = os.open(str(trace.path / 'episode.json'), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(fd, 'w') as handle: json.dump(e, handle, indent=2, allow_nan=False)
        else:
            e = run(max_ticks=args.max_ticks, max_jev=args.max_jev, max_qwen=args.max_qwen, seconds=args.seconds)
        public = public_episode(e, args.publish_advisory)
        write_public(public, args.public, args.asset)
        print(json.dumps({'outcome': e['outcome'], 'metrics': e['metrics'], 'public': args.public}, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError):
        print('Incident Room rejected invalid input or I/O. No retry or rule fallback.'); return 2


if __name__ == '__main__':
    raise SystemExit(main())
