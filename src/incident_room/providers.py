"""Fixed localhost Qwen adapter; Jev reuses the reviewed bounded transport."""
import http.client
import json
import os
from jev_bench import transport
from jev_bench.core import require, strict_json
from jev_agent.providers import Jev
from .episode import usage


def advisory_payload(world):
    return {'model': 'qwen2.5:7b', 'stream': False,
        'options': {'temperature': 0, 'num_predict': 500, 'num_ctx': 8192},
        'messages': [{'role': 'system', 'content':
            'You advise a fictional station crew. You have no tools or execution authority. '
            'Give a short concrete opening plan, assigning priorities to Ada, Ivo and Nia using their current rooms. '
            'Account for simultaneous decisions and scarce starting power. Use only the supplied fictional scenario. '
            'Plain text, at most 200 words. Do not output commands, code, links or real-world instructions.'},
            {'role': 'user', 'content': json.dumps(world, allow_nan=False)}]}


def parse_qwen(raw):
    require(type(raw) is dict and raw.get('model') == 'qwen2.5:7b' and raw.get('done') is True and raw.get('done_reason') == 'stop', 'invalid_response')
    msg = raw.get('message')
    require(type(msg) is dict and msg.get('role') == 'assistant' and not msg.get('tool_calls'), 'invalid_response')
    text = msg.get('content')
    require(type(text) is str and text.strip() and len(text) <= 4000, 'invalid_response')
    key = os.environ.get('TYPESAFE_API_KEY')
    require(not key or key not in json.dumps(raw), 'invalid_response')
    return {'status': 'ok', 'model': raw['model'], 'text': text,
            'usage': usage({'input_tokens': raw.get('prompt_eval_count'), 'output_tokens': raw.get('eval_count')})}


def qwen_worker(pipe, payload, timeout):
    conn = None
    try:
        body = json.dumps(payload, allow_nan=False).encode()
        require(len(body) <= 65536, 'request_too_large')
        conn = http.client.HTTPConnection('127.0.0.1', 11434, timeout=timeout)
        conn.request('POST', '/api/chat', body, {'Content-Type': 'application/json', 'Accept': 'application/json'})
        response = conn.getresponse()
        if response.status != 200: result = {'status': 'http_error'}
        else:
            raw = response.read(65537); require(len(raw) <= 65536, 'response_too_large')
            parsed = strict_json(raw)
            result = parse_qwen(parsed)
            result['raw'] = parsed  # retained only in private call journal
        pipe.send(result)
    except ValueError: pipe.send({'status': 'invalid_response'})
    except Exception: pipe.send({'status': 'network_error'})
    finally:
        if conn: conn.close()
        pipe.close()


class Qwen:
    def advise(self, world, timeout):
        return transport.bounded_request(advisory_payload(world), timeout, worker=qwen_worker)
