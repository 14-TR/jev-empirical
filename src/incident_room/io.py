"""Strict public projection. Raw model payloads and private paths never export."""
import copy
import json
import os
import re
from pathlib import Path
from . import episode as R
from . import engine as E


def public_episode(source, publish_advisory=False):
    R.validate_replay(source)
    e = {k: copy.deepcopy(source[k]) for k in ('schema', 'scenario', 'mode')}
    for field, keys in (('limits', ('max_ticks', 'max_jev', 'max_qwen', 'seconds')),
                        ('metrics', ('jev_calls', 'qwen_calls', 'elapsed_seconds', 'invariant_violations')),
                        ('outcome', ('status', 'reason'))):
        e[field] = {k: copy.deepcopy(source[field][k]) for k in keys}
    e['calls'] = [{k: copy.deepcopy(call[k]) for k in ('provider', 'tick', 'status', 'latency_seconds', 'model', 'usage')} for call in source['calls']]
    e['frames'] = []; state = E.initial_state()
    e['frames'].append({'state': state, 'actions': None, 'legal': {}, 'decisions': {}, 'events': []})
    for frame in source['frames'][1:]:
        options = R.legal(state); actions = {c: frame['actions'][c] for c in E.CREW}
        state, events = E.step(state, actions, source['limits']['max_ticks'])
        decisions = {}
        for c in E.CREW:
            d = frame['decisions'][c]; keys = ('source', 'choice') if source['mode'] == 'offline-rule' else ('source', 'choice', 'confidence', 'probabilities')
            decisions[c] = {k: copy.deepcopy(d[k]) for k in keys}
        e['frames'].append({'state': state, 'actions': actions, 'legal': options, 'decisions': decisions, 'events': events})
    advisory = source['advisory']
    e['advisory'] = {'status': 'not_requested' if advisory['status'] == 'not_requested' else 'withheld', 'text': ''}
    if publish_advisory and advisory['status'] == 'available':
        text = advisory['text']; key = os.environ.get('TYPESAFE_API_KEY')
        if key: text = text.replace(key, '[redacted]')
        text = re.sub(r'https?://\S+|/[A-Za-z][^\s]*|[\w.+-]+@[\w.-]+', '[redacted]', text)
        text = ''.join(c for c in text if c in '\n\t' or (32 <= ord(c) < 127))[:2400]
        e['advisory'] = {'status': 'available', 'text': text}
    # All provider-derived strings except opt-in advisory are constrained below.
    for call in e['calls']:
        if call['provider'] not in ('jev', 'qwen') or call['status'] not in ('ok', 'timeout', 'network_error', 'http_error', 'invalid_response', 'missing_key', 'request_too_large', 'response_too_large', 'provider_exception', 'pending'): raise ValueError('invalid_call')
        if call['model'] is not None and not re.fullmatch(r'jev-(?:[0-9]+\.[0-9]+\.[0-9]+|latest|preview)|qwen2\.5:7b', call['model']): raise ValueError('invalid_model')
        call['usage'] = R.usage(call['usage'])
    e = R.seal(e); R.validate_replay(e)
    key = os.environ.get('TYPESAFE_API_KEY')
    if key and key in R.canonical(e): raise ValueError('sensitive_content')
    return e


def write_public(e, path, asset=None):
    R.validate_replay(e)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(e, indent=2, allow_nan=False) + '\n')
    if asset:
        Path(asset).parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(e, ensure_ascii=True, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        Path(asset).write_text('window.INCIDENT_EPISODE = ' + text + ';\n')
