"""Offline tests; literal oracles are independent of the workload builder."""
import importlib
import importlib.util
import json
import unittest
from pathlib import Path

class WorkloadTests(unittest.TestCase):
    def test_original_workload_has_eight_independent_questions(self):
        self.assertIsNotNone(importlib.util.find_spec('study'), 'study implementation is missing')
        s = importlib.import_module('study')
        cases = s.build_cases()
        expected = {'coordinator':'lyn','gate':'indigo','backup':'disabled','departure':'thursday',
                    'rover':'kestrel','sample':'quartz','operator':'ivo','slot':'s3'}
        self.assertEqual(cases['gold'], expected)
        self.assertEqual(set(cases['questions']), set(expected))
        self.assertIn(cases['states']['short']['text'], cases['states']['long']['text'])
        self.assertGreater(len(cases['states']['long']['text']), 5*len(cases['states']['short']['text']))
        self.assertLessEqual(len(cases['states']['long']['text']), 16000)
        for qid, gold in expected.items():
            self.assertIn(gold, cases['questions'][qid]['criteria'])
            for context in ['short','long']:
                payload = s.make_payload(cases, context, [qid])
                self.assertEqual(set(payload), {'state','model','questions'})
                self.assertEqual(payload['model'], 'jev-1.13.0')
                self.assertNotIn('gold', payload)
                self.assertNotIn('oracle', payload)
                self.assertEqual(list(payload['questions']), [qid])

class ScheduleTests(unittest.TestCase):
    def test_seeded_plan_freezes_all_conditions_within_bounds(self):
        import study as s
        self.assertTrue(hasattr(s, 'make_plan'), 'seeded plan missing')
        p = s.make_plan()
        self.assertEqual(p, s.make_plan())
        self.assertEqual(p['config']['seed'], 731029)
        self.assertEqual(p['config']['max_post_attempts'], 110)
        self.assertEqual(p['config']['total_seconds'], 600)
        self.assertEqual(p['config']['request_timeout_seconds'], 15)
        self.assertEqual(p['config']['retries'], 0)
        self.assertEqual(len(p['schedule']),18)
        counts = {}
        for run in p['schedule']:
            k = (run['context'],run['strategy'])
            counts[k] = counts.get(k,0)+1
        self.assertEqual(set(counts.values()),{3})
        self.assertEqual(len(counts),6)
        self.assertEqual(sum(1 if r['strategy']=='batch' else 8 for r in p['schedule']),102)
        self.assertEqual(p['cases'],s.build_cases())

class AggregationTests(unittest.TestCase):
    def test_oracle_failures_denominators_and_completion_latency(self):
        import study as s
        self.assertTrue(hasattr(s,'summarize'), 'aggregation missing')
        cases=s.build_cases()
        qids=list(cases['questions'])
        answers={q:{'type':'choice','choice':cases['gold'][q], 'confidence':1.0,
                    'probabilities':{o:float(o==cases['gold'][q]) for o in cases['questions'][q]['criteria']}}
                 for q in qids}
        result={'status':'ok','response':{'model':'jev-1.13.0','answers':answers,
                                         'usage':{'input_tokens':1000,'output_tokens':100}}}
        runs=[{'context':'short','strategy':'batch','repetition':1,'makespan_s':2.0,
               'calls':[{'qids':qids,'result':result,'call_latency_s':2.0,'ready_offset_s':2.0}]}]
        summary=s.summarize(runs,cases)
        row=summary['conditions'][0]
        self.assertEqual(row['correct'],8)
        self.assertEqual(row['expected_answers'],8)
        self.assertEqual(row['question_ready_s'],[2.0]*8) # never divide batch latency by 8
        self.assertEqual(row['call_latency_s'],[2.0])
        self.assertAlmostEqual(summary['list_price_estimate_usd'],0.000042)
        result['response']['answers'].pop('gate')
        result['response']['answers']['coordinator']['choice']='mara'
        result['response']['answers']['coordinator']['probabilities']={'mara':1,'lyn':0,'oren':0,'none':0}
        runs[0]['calls'].append({'qids':['extra'],'result':{'status':'timeout'},'call_latency_s':15,'ready_offset_s':15})
        row=s.summarize(runs,cases)['conditions'][0]
        self.assertEqual((row['correct'],row['wrong'],row['missing'],row['invalid']), (6,1,1,0))
        self.assertEqual(row['failed_calls'],1)
        self.assertEqual(row['expected_answers'],8)
        self.assertEqual(row['usage_missing_calls'],1)
        result['response']['model']='jev-9.9.9'
        row=s.summarize(runs,cases)['conditions'][0]
        self.assertEqual(row['invalid'],7)

def fake_worker(pipe,payload,timeout):
    import time
    time.sleep(0.08)
    pipe.send({'status':'offline_test'})
    pipe.close()


def slow_worker(pipe,payload,timeout):
    import time
    time.sleep(2)


class RunnerTests(unittest.TestCase):
    def test_scheduler_observes_completion_and_bounds_without_network(self):
        import study as s
        import time
        self.assertTrue(hasattr(s,'run_workload'), 'bounded main-thread scheduler missing')
        cases=s.build_cases()
        spec={'context':'short','strategy':'concurrency4','repetition':1}
        budget={'attempts':0,'max_attempts':110,'deadline':time.monotonic()+10}
        run=s.run_workload(spec,cases,budget,1,worker=fake_worker)
        self.assertEqual(len(run['calls']),8)
        self.assertEqual(budget['attempts'],8)
        self.assertEqual(run['peak_workers'],4)
        self.assertGreater(run['makespan_s'],0.16)
        for call in run['calls']:
            self.assertGreater(call['call_latency_s'],0.08)
            self.assertLessEqual(call['ready_offset_s'],run['makespan_s'])
        budget={'attempts':109,'max_attempts':110,'deadline':time.monotonic()+10}
        run=s.run_workload(spec,cases,budget,1,worker=fake_worker)
        self.assertEqual(len(run['calls']),1)
        self.assertEqual(budget['attempts'],110)
        self.assertEqual(s.summarize([run],cases)['missing'],8)
        spec['strategy']='batch'
        budget={'attempts':0,'max_attempts':110,'deadline':time.monotonic()+10}
        run=s.run_workload(spec,cases,budget,0.15,worker=slow_worker)
        self.assertEqual(run['calls'][0]['result']['status'],'timeout')
        self.assertLess(run['makespan_s'],1)
        budget={'attempts':0,'max_attempts':110,'deadline':time.monotonic()-1}
        run=s.run_workload(spec,cases,budget,1,worker=fake_worker)
        self.assertEqual(len(run['calls']),0)

class FreezeTests(unittest.TestCase):
    def test_freeze_rejects_tampering_and_offline_execution_saves_safe_summary(self):
        import study as s
        import tempfile
        self.assertTrue(hasattr(s,'freeze'), 'freeze missing')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            candidate=root/'candidate'
            s.freeze(candidate)
            self.assertEqual(s.read_frozen(candidate)['config']['planned_posts'],102)
            outcome=s.execute(candidate,root/'private',worker=fake_worker)
            self.assertEqual(outcome['calls'],102)
            self.assertEqual(outcome['expected_answers'],144)
            self.assertEqual(outcome['missing'],144)
            self.assertEqual(outcome['post_attempt_upper_bound'],102)
            self.assertTrue((root/'private'/'requests-responses.jsonl').exists())
            self.assertFalse((candidate/'requests-responses.jsonl').exists())
            self.assertNotIn('"response":',json.dumps(json.loads((candidate/'summary.json').read_text())))
            with self.assertRaises(FileExistsError):
                s.execute(candidate,root/'private',worker=fake_worker)
            p=candidate/'plan.json'
            p.write_text(p.read_text()+' ')
            with self.assertRaises(ValueError):
                s.read_frozen(candidate)

class CliTests(unittest.TestCase):
    def test_cli_help_is_offline_and_discloses_explicit_actions(self):
        import subprocess
        script=Path(__file__).parent/'run_study.py'
        self.assertTrue(script.exists(),'standalone CLI missing')
        result=subprocess.run(['python3',str(script),'--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertIn('freeze',result.stdout)
        self.assertIn('run',result.stdout)

if __name__ == '__main__':
    unittest.main()
