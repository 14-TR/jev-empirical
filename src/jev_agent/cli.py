"""CLI is the consent boundary; no offline/mock/fallback production option."""
import argparse
from dataclasses import fields
import json
import os
from pathlib import Path

from .controller import Bounds, MODEL, run
from .providers import Jev, Ollama, OLLAMA_MODEL
from .trace import Trace
from .workspace import Workspace


def parser():
    p = argparse.ArgumentParser(description='Bounded read-only hybrid Jev/Ollama evidence agent')
    sub = p.add_subparsers(dest='command', required=True)
    cmd = sub.add_parser('run')
    cmd.add_argument('--workspace', required=True, help='Explicit safe text workspace; original fixture recommended')
    cmd.add_argument('--goal', required=True)
    cmd.add_argument('--trace-dir', required=True, help='NEW private directory outside Git and outside workspace')
    cmd.add_argument('--allow-live', action='store_true', help='Consent to actual fixed-provider requests')
    cmd.add_argument('--allow-workspace-upload', action='store_true', help='Consent to send filenames and read source contents to TypeSafe Jev')
    cmd.add_argument('--jev-model', choices=[MODEL], default=MODEL)
    cmd.add_argument('--ollama-model', choices=[OLLAMA_MODEL], default=OLLAMA_MODEL)
    for field in fields(Bounds):
        cmd.add_argument('--' + field.name.replace('_', '-'), type=field.type, default=field.default,
                         help='Uncalibrated heuristic' if 'confidence' in field.name else None)
    for name, default in [('max-files', 32), ('max-file-bytes', 8192), ('max-entries', 256), ('max-depth', 4)]:
        cmd.add_argument('--' + name, type=int, default=default)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    error = ('live_consent_required' if not args.allow_live else
             'workspace_upload_consent_required' if not args.allow_workspace_upload else
             'missing_key' if not os.environ.get('TYPESAFE_API_KEY') else None)
    if error:
        print(json.dumps({'status': 'failed', 'reason': error, 'providers_invoked': [], 'requests': 0}))
        return 2
    result = {'providers_invoked': [], 'provider_requests': {}, 'requests': 0}
    try:
        bounds = Bounds(**{field.name: getattr(args, field.name) for field in fields(Bounds)})
        workspace_path, trace_path = Path(args.workspace).expanduser().absolute(), Path(args.trace_dir).expanduser().absolute()
        if trace_path == workspace_path or workspace_path in trace_path.parents:
            raise ValueError('trace_in_workspace')
        with Workspace(workspace_path, args.max_files, args.max_file_bytes, args.max_entries, args.max_depth) as workspace:
            with Trace(trace_path) as trace:
                trace.record({'kind': 'start', 'confidence_policy': 'uncalibrated_heuristics',
                              'requested_models': [MODEL, OLLAMA_MODEL],
                              'bounds': {field.name: getattr(bounds, field.name) for field in fields(Bounds)}})
                result = run(workspace, args.goal, Jev(), Ollama(), bounds=bounds, emit=trace.record)
                trace.record({'kind': 'result', **{key: result[key] for key in
                             ('status', 'reason', 'requests', 'providers_invoked', 'provider_requests', 'resolved_models')}})
                result['trace_dir'] = str(trace.path)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0 if result['status'] == 'completed' else 2
    except (OSError, ValueError, TypeError):
        # Never serialize exception text, transport bodies or arbitrary paths.
        result.update(status='failed', reason='invalid_configuration_or_local_io', text='')
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 2
