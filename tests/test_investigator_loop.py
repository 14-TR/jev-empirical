import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from test_investigator_source import mod, fixture

ISSUE = {'url': 'https://github.com/owner/repo/issues/1', 'number': 1, 'title': 'pressure regression',
         'body': 'pressure returns wrong value. <script>attack()</script>', 'state': 'OPEN', 'updatedAt': '2026-01-01T00:00:00Z'}


class Judge:
    def __init__(self, actions): self.actions = iter(actions); self.payloads = []
    def decide(self, payload, timeout):
        self.payloads.append(copy.deepcopy(payload))
        tool = next(self.actions)
        options = payload['state']['candidates']
        selected = next(c['id'] for c in options if c['tool'] == tool and (tool != 'read_lines' or c['args']['path'].endswith('.py')))
        return {'status': 'ok', 'response': {'model': 'jev-1.13.0', 'usage': {}, 'answers': {'q': {
            'type': 'choice', 'choice': selected, 'confidence': 1.0,
            'probabilities': {c['id']: float(c['id'] == selected) for c in options}}}}}


class Qwen:
    def __init__(self): self.calls = []
    def reason(self, phase, evidence, timeout):
        self.calls.append((phase, copy.deepcopy(evidence)))
        citation = evidence[-1]['id']
        return {'status': 'ok', 'model': 'qwen2.5:7b', 'text': json.dumps({
            'summary': 'Hypothesis only, not a confirmed fix',
            'claims': [{'text': 'Inspect the observed pressure behavior.', 'citations': [citation]}],
            'limitations': ['No fix performed.']})}


class LoopTests(unittest.TestCase):
    def setup_run(self, root):
        repo, commit = fixture(root)
        return mod('source').freeze(repo, commit, root / 'private')

    def test_dynamic_tools_actual_observations_and_graph_causality(self):
        e = mod('engine')
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve()); judge = Judge(['search_text', 'read_lines', 'git_history', 'git_diff', 'synthesize'])
            qwen = Qwen()
            run = e.investigate(ISSUE, snap, judge, qwen, mode='offline-test')
            self.assertEqual(run['outcome']['status'], 'reported')
            self.assertEqual(run['metrics']['jev_calls'], 5)
            self.assertEqual(run['metrics']['qwen_calls'], 2)
            self.assertFalse(any('files' in n.get('observation', {}) for phase, nodes in qwen.calls for n in nodes), 'Qwen receives observed evidence, not a broad repository inventory')
            self.assertNotEqual(judge.payloads[0]['state'], judge.payloads[1]['state'])
            self.assertEqual(judge.payloads[0]['state']['observations'], [])
            self.assertIn('pressure', json.dumps(run['observations']))
            self.assertEqual([x['tool'] for x in run['observations']], ['search_text', 'read_lines', 'git_history', 'git_diff'])
            self.assertTrue(e.validate_run(run))
            symbols = [n for n in run['evidence']['nodes'] if n['kind'] == 'symbol']
            self.assertTrue(symbols)
            self.assertEqual(symbols[0]['source']['commit'], snap.commit)
            self.assertTrue(all(x['label'] in ('observed', 'hypothesis') for x in run['evidence']['edges']))
            corrupted = copy.deepcopy(run); corrupted['evidence']['edges'][0]['source'] = 'missing'
            with self.assertRaises(ValueError): e.validate_run(corrupted)
            corrupted = copy.deepcopy(run)
            next(n for n in corrupted['evidence']['nodes'] if n['kind'] == 'file')['source']['commit'] = '0' * 40
            with self.assertRaises(ValueError): e.validate_run(corrupted)
            corrupted = copy.deepcopy(run)
            next(n for n in corrupted['events'] if n['kind'] == 'tool')['observation']['decision'] = 'x999'
            corrupted['execution'], corrupted['evidence'] = e.graph(corrupted)
            with self.assertRaises(ValueError): e.validate_run(corrupted)

    def test_final_report_controller_rejects_non_observation_citations(self):
        for citation in ('report0', 'issue', 'commit', 'o0f0'):
            class SelfCiting(Qwen):
                def reason(self, phase, evidence, timeout):
                    out = super().reason(phase, evidence, timeout)
                    if phase == 'final report':
                        report = json.loads(out['text'])
                        report['claims'][0]['citations'] = [citation]
                        out['text'] = json.dumps(report)
                    return out
            with self.subTest(citation=citation), tempfile.TemporaryDirectory() as tmp:
                snap = self.setup_run(Path(tmp).resolve())
                qwen = SelfCiting()
                run = mod('engine').investigate(ISSUE, snap, Judge(['search_text', 'synthesize']), qwen, mode='offline-test')
                self.assertEqual(run['outcome']['reason'], 'qwen_citation_invalid')
                self.assertEqual(len(run['reports']), 1)
                self.assertNotIn('report0', [n['id'] for n in qwen.calls[-1][1]])

    def test_recent_context_packing_preserves_full_evidence_and_exposes_omissions(self):
        from unittest.mock import patch
        def observed(candidate, snapshot, timeout, check=None):
            return {'tool': candidate['tool'], 'text': 'observed data ' * 350, 'refs': []}
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve())
            judge = Judge(['search_text'] * 4 + ['synthesize'])
            qwen = Qwen()
            with patch('jev_investigator.engine.tools.execute', side_effect=observed):
                run = mod('engine').investigate(ISSUE, snap, judge, qwen, mode='offline-test')
        self.assertEqual(run['outcome']['status'], 'reported')
        self.assertEqual(len(run['observations']), 4)
        self.assertTrue(any(p['state']['omitted_observations'] > 0 for p in judge.payloads))
        for index, payload in enumerate(judge.payloads):
            state = payload['state']
            self.assertLessEqual(len(mod('engine').canonical(state).encode()), 15500)
            self.assertEqual(len(state['observations']) + state['omitted_observations'], index)
            if index:
                self.assertEqual(state['observations'][-1], run['observations'][index - 1])
        self.assertEqual(len([n for n in qwen.calls[-1][1] if n['id'].startswith('o')]), 4)

    def test_low_concentration_among_safe_actions_does_not_block_investigation(self):
        class Diffuse(Judge):
            def decide(self, payload, timeout):
                out = super().decide(payload, timeout)
                out['response']['answers']['q']['confidence'] = 0.25
                return out
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve())
            run = mod('engine').investigate(ISSUE, snap, Diffuse(['search_text', 'synthesize']), Qwen(), mode='offline-test')
            self.assertEqual(run['outcome']['status'], 'reported')
            self.assertEqual(run['observations'][0]['tool'], 'search_text')

    def test_cent_rounding_is_explicit_without_changing_raw_or_confidence(self):
        class Rounded(Judge):
            def decide(self, payload, timeout):
                out = super().decide(payload, timeout)
                answer = out['response']['answers']['q']
                others = [k for k in answer['probabilities'] if k != answer['choice']]
                answer['probabilities'][answer['choice']] = 0.49
                answer['probabilities'][others[0]] = 0.48
                answer['probabilities'][others[1]] = 0.02
                answer['confidence'] = 0.27
                return out
        receipts = []
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve())
            run = mod('engine').investigate(ISSUE, snap, Rounded(['search_text']), Qwen(),
                                           mode='offline-test', max_steps=1, record=receipts.append)
        self.assertEqual(run['outcome']['reason'], 'step_budget')
        self.assertEqual(len(run['observations']), 1)
        raw = next(r for r in receipts if r['kind'] == 'jev')['result']['response']
        self.assertAlmostEqual(sum(raw['answers']['q']['probabilities'].values()), 0.99)
        events = [e for e in run['events'] if e['kind'] == 'normalization']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['observation']['method'], 'cent-rounding-v1')
        self.assertEqual(events[0]['observation']['raw_sum'], 0.99)
        response = next(e for e in run['events'] if 'selected' in e['observation'])
        self.assertEqual(response['observation']['confidence'], 0.27)
        self.assertAlmostEqual(sum(response['observation']['probabilities'].values()), 1.0)
        self.assertTrue(mod('engine').validate_run(run))

    def test_validation_reason_is_preserved_without_untrusted_exception_text(self):
        from unittest.mock import patch
        from jev_bench.core import ValidationError
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve())
            for supplied, expected in [('probability_sum', 'probability_sum'),
                                       ('private_secret_value', 'invalid_or_failed_operation')]:
                error = ValidationError('sensitive provider body must not appear')
                setattr(error, 'code', supplied)
                with patch('jev_investigator.engine.parse_decision', side_effect=error):
                    run = mod('engine').investigate(ISSUE, snap, Judge(['search_text']), Qwen(), mode='offline-test')
                self.assertEqual(run['outcome']['reason'], expected)
                self.assertNotIn('sensitive provider body', json.dumps(run))
                self.assertNotIn('private_secret_value', json.dumps(run))

    def test_material_probability_error_keeps_strict_code(self):
        class Bad(Judge):
            def decide(self, payload, timeout):
                out = super().decide(payload, timeout)
                a = out['response']['answers']['q']
                a['probabilities'][a['choice']] = 0.98
                return out
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve())
            run = mod('engine').investigate(ISSUE, snap, Bad(['search_text']), Qwen(), mode='offline-test')
        self.assertEqual(run['outcome']['reason'], 'probability_sum')
        self.assertEqual(run['observations'], [])

    def test_candidate_pool_fits_provider_contract_and_keeps_check_choices(self):
        from jev_bench.core import validate_input
        tools = mod('tools')
        class Inventory:
            files = {'src/module%d.py' % n: {} for n in range(30)}
        options = tools.candidates(dict(ISSUE, title='alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima'), Inventory(), [], set(), True, ('incident-unittest',))
        self.assertLessEqual(len(options), 20)
        self.assertIn('run_check', {o['tool'] for o in options})
        validate_input({'state': {'text': 'bounded state'}, 'question': {'type': 'choice', 'instructions': 'Select tool',
                       'criteria': {c['id']: c['label'] for c in options}}})

    def test_consent_refusal_malformed_and_budgets_fail_closed(self):
        e = mod('engine')
        with tempfile.TemporaryDirectory() as tmp:
            snap = self.setup_run(Path(tmp).resolve())
            for flags in ({}, {'allow_live': True}, {'allow_source_upload': True}):
                with self.assertRaises(ValueError): e.investigate(ISSUE, snap, Judge([]), Qwen(), mode='recorded-live', **flags)
            run = e.investigate(ISSUE, snap, Judge(['clarify']), Qwen(), mode='offline-test')
            self.assertEqual(run['outcome']['status'], 'clarification_needed')
            self.assertEqual(run['observations'], [])
            class Bad:
                def decide(self, *args): return {'status': 'ok', 'response': {}}
            run = e.investigate(ISSUE, snap, Bad(), Qwen(), mode='offline-test')
            self.assertEqual(run['outcome']['status'], 'error')
            self.assertEqual(run['metrics']['jev_calls'], 1)
            run = e.investigate(ISSUE, snap, Judge(['search_text']), Qwen(), mode='offline-test', max_steps=1)
            self.assertEqual(run['outcome']['reason'], 'step_budget')
            self.assertEqual(run['metrics']['jev_calls'], 1)
            for kwargs in ({'max_steps': 13}, {'seconds': 301}, {'seconds': float('nan')}, {'max_steps': True}):
                with self.assertRaises(ValueError): e.investigate(ISSUE, snap, Judge([]), Qwen(), mode='offline-test', **kwargs)
            class Refusal(Qwen):
                def reason(self, *args): return {'status': 'ok', 'model': 'qwen2.5:7b', 'text': 'I cannot help'}
            run = e.investigate(ISSUE, snap, Judge([]), Refusal(), mode='offline-test')
            self.assertEqual(run['outcome']['status'], 'error')
            self.assertEqual(run['metrics']['jev_calls'], 0)


if __name__ == '__main__': unittest.main()
