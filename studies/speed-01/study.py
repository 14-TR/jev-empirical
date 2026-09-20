"""Bounded original synthetic Jev strategy/context study; Python stdlib only."""
import json
import random
import statistics
from jev_bench.core import parse_response, ValidationError


def summarize(runs, cases):
    groups = {}
    for run in runs:
        k = (run['context'],run['strategy'])
        row = groups.setdefault(k,dict(context=k[0],strategy=k[1],makespan_s=[],call_latency_s=[],
            question_ready_s=[],correct=0,wrong=0,missing=0,invalid=0,expected_answers=0,
            calls=0,failed_calls=0,input_tokens=0,output_tokens=0,usage_missing_calls=0,
            fully_correct_workloads=0,workloads=0,answer_records=[]))
        row['makespan_s'].append(run['makespan_s'])
        row['workloads'] += 1
        row['expected_answers'] += len(cases['questions'])
        observed = {}
        for call in run['calls']:
            row['calls'] += 1
            row['call_latency_s'].append(call['call_latency_s'])
            result = call['result']
            raw = result.get('response',{})
            if result['status'] != 'ok':
                row['failed_calls'] += 1
            usage = raw.get('usage',{})
            if all(type(usage.get(f)) is int and usage[f] >= 0 for f in ('input_tokens','output_tokens')):
                row['input_tokens'] += usage['input_tokens']
                row['output_tokens'] += usage['output_tokens']
            else:
                row['usage_missing_calls'] += 1
            for qid in call['qids']:
                if qid not in cases['questions']:
                    continue
                answer = raw.get('answers',{}).get(qid)
                if result['status'] != 'ok' or answer is None:
                    observed[qid] = ('missing',None,None)
                    continue
                try:
                    if raw.get('model') != MODEL:
                        raise ValidationError('unpinned_model')
                    parsed = parse_response({'state':cases['states'][run['context']],
                                             'question':cases['questions'][qid]},
                                            {'model':raw['model'],'answers':{'q':answer},'usage':usage})
                    predicted = parsed['predicted']
                    status = 'correct' if predicted == cases['gold'][qid] else 'wrong'
                    observed[qid] = (status,predicted,call['ready_offset_s'])
                except (ValidationError,KeyError,TypeError):
                    observed[qid] = ('invalid',None,None)
        correct_in_run = 0
        for qid in cases['questions']:
            status,predicted,ready = observed.get(qid,('missing',None,None))
            row[status] += 1
            correct_in_run += (status == 'correct')
            if ready is not None:
                row['question_ready_s'].append(ready)
            row['answer_records'].append({'repetition':run['repetition'],'qid':qid,'status':status,
                'predicted':predicted,'gold':cases['gold'][qid],'ready_s':ready})
        row['fully_correct_workloads'] += (correct_in_run == len(cases['questions']))
    for row in groups.values():
        for field in ('makespan_s','call_latency_s','question_ready_s'):
            row[field+'_median'] = statistics.median(row[field]) if row[field] else None
        row['list_price_estimate_usd'] = row['input_tokens'] * 0.042 / 1000000
    conditions = [groups[k] for k in sorted(groups)]
    totals = {f:sum(r[f] for r in conditions) for f in ('correct','wrong','missing','invalid',
        'expected_answers','calls','failed_calls','input_tokens','output_tokens','usage_missing_calls',
        'fully_correct_workloads','workloads','list_price_estimate_usd')}
    return dict(conditions=conditions,**totals)
from pathlib import Path
import time
import datetime
import multiprocessing
import threading
from jev_bench.transport import _worker


def run_workload(spec, cases, budget, timeout, worker=None, journal=None):
    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError('spawn_requires_main_thread')
    start = time.monotonic()
    wall = datetime.datetime.now(datetime.timezone.utc).isoformat()
    qids = list(cases['questions'])
    pending = [qids] if spec['strategy'] == 'batch' else [[qid] for qid in qids]
    limit = 4 if spec['strategy'] == 'concurrency4' else 1
    active, calls, peak = [], [], 0
    ctx = multiprocessing.get_context('spawn')
    while pending or active:
        while pending and len(active) < limit:
            if budget['attempts'] >= budget['max_attempts'] or time.monotonic()+timeout+0.3 > budget['deadline']:
                pending.clear()
                break
            ids = pending.pop(0)
            payload = make_payload(cases,spec['context'],ids)
            reader,writer = ctx.Pipe(duplex=False)
            proc = ctx.Process(target=worker or _worker,args=(writer,payload,timeout),daemon=True)
            budget['attempts'] += 1
            call = {'attempt_slot':budget['attempts'],'qids':ids,'request':payload,
                    'wall_start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
            if journal:
                journal({'event':'launch','spec':spec,**call})
            call_start = time.monotonic()
            try:
                proc.start()
            except Exception:
                reader.close(); writer.close()
                call.update(result={'status':'spawn_error'},call_latency_s=time.monotonic()-call_start,
                            ready_offset_s=time.monotonic()-start)
                calls.append(call)
                if journal:
                    journal({'event':'complete','spec':spec,**call})
                continue
            writer.close()
            active.append((proc,reader,call,call_start))
            peak = max(peak,len(active))
        for item in list(active):
            proc,reader,call,call_start = item
            result = None
            if reader.poll():
                try:
                    result = reader.recv()
                except (EOFError,OSError):
                    result = {'status':'network_error'}
            elif time.monotonic()-call_start >= timeout or time.monotonic() >= budget['deadline']:
                result = {'status':'timeout'}
            elif not proc.is_alive():
                result = {'status':'worker_exit'}
            if result is not None:
                proc.join(timeout=0.01)
                if proc.is_alive():
                    proc.terminate(); proc.join(timeout=0.1)
                if proc.is_alive():
                    proc.kill(); proc.join(timeout=0.1)
                proc.close(); reader.close()
                finished = time.monotonic()
                call.update(result=result,call_latency_s=finished-call_start,
                            ready_offset_s=finished-start,
                            wall_end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                calls.append(call)
                active.remove(item)
                if journal:
                    journal({'event':'complete','spec':spec,**call})
        if active:
            time.sleep(0.001)
    return dict(spec,wall_start_utc=wall,wall_end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                makespan_s=time.monotonic()-start,calls=calls,peak_workers=peak)


def make_plan():
    rng = random.Random(731029)
    schedule = []
    for repetition in range(1,4):
        contexts = ['short','long']
        rng.shuffle(contexts)
        for context in contexts:
            strategies = ['batch','serial','concurrency4']
            rng.shuffle(strategies)
            schedule.extend({'repetition':repetition,'context':context,'strategy':strategy}
                            for strategy in strategies)
    return {'config':{'seed':731029,'max_post_attempts':110,'total_seconds':600,
                      'request_timeout_seconds':15,'retries':0,'model':'jev-1.13.0',
                      'endpoint':'https://api.typesafe.ai/v1/systemone','redirects':False,
                      'planned_posts':102,'planned_answers':144,'repetitions':3,
                      'input_usd_per_million_tokens':0.042,'output_usd_per_million_tokens':0,
                      'pricing_source':'https://docs.typesafe.ai/models.md',
                      'warmup_posts':0,'connection_reuse':False},
            'schedule':schedule,'cases':build_cases()}

MODEL = 'jev-1.13.0'
ROOT = Path(__file__).resolve().parent
import hashlib
import os
import platform


def freeze(directory):
    directory = Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    plan = make_plan()
    sources = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(ROOT.rglob('*.py'))}
    plan_text = json.dumps(plan,indent=2,ensure_ascii=False)+'\n'
    manifest = {'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'plan_sha256':hashlib.sha256(plan_text.encode()).hexdigest(),
                'source_sha256':sources,'python':platform.python_version(),
                'platform':platform.platform(),
                'vendored_from':'/Users/tr/Projects/jev-empirical/src/jev_bench',
                'docs_read':['https://docs.typesafe.ai/llms.txt','https://docs.typesafe.ai/api.md',
                             'https://docs.typesafe.ai/models.md','https://docs.typesafe.ai/primitives/choice.md',
                             'https://docs.typesafe.ai/patterns/fan-out.md',
                             'https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md']}
    with (directory/'plan.json').open('x') as f:
        f.write(plan_text)
    with (directory/'freeze.json').open('x') as f:
        json.dump(manifest,f,indent=2)
    return manifest


def read_frozen(directory):
    directory = Path(directory)
    raw = (directory/'plan.json').read_bytes()
    manifest = json.loads((directory/'freeze.json').read_text())
    if hashlib.sha256(raw).hexdigest() != manifest['plan_sha256']:
        raise ValueError('plan_changed_after_freeze')
    for relative,digest in manifest['source_sha256'].items():
        if hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() != digest:
            raise ValueError('code_changed_after_freeze')
    plan = json.loads(raw)
    if plan != make_plan():
        raise ValueError('unexpected_plan')
    return plan


def execute(directory, private_directory, worker=None):
    start = time.monotonic()
    wall_start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    directory,private_directory = Path(directory).resolve(),Path(private_directory).resolve()
    plan = read_frozen(directory)
    if private_directory == ROOT or ROOT in private_directory.parents or directory == private_directory or directory in private_directory.parents:
        raise ValueError('raw_must_be_outside_public_candidate')
    if worker is None and not os.environ.get('TYPESAFE_API_KEY'):
        raise ValueError('missing_TYPESAFE_API_KEY')
    private_directory.mkdir(mode=0o700,parents=True,exist_ok=False)
    budget = {'attempts':0,'max_attempts':plan['config']['max_post_attempts'],
              'deadline':start+plan['config']['total_seconds']}
    runs=[]
    raw_path=private_directory/'requests-responses.jsonl'
    fd=os.open(str(raw_path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as raw:
        def journal(event):
            raw.write(json.dumps(event,ensure_ascii=False,allow_nan=False)+'\n')
            raw.flush()
        journal({'event':'study_start','wall_start_utc':wall_start,
                 'manifest':json.loads((directory/'freeze.json').read_text()),
                 'execution':'offline-test' if worker else 'live'})
        for spec in plan['schedule']:
            run=run_workload(spec,plan['cases'],budget,plan['config']['request_timeout_seconds'],worker,journal)
            runs.append(run)
            journal({'event':'workload','run':run})
            if worker is None:
                print(json.dumps(dict(spec,makespan_s=run['makespan_s'],calls=len(run['calls']))),flush=True)
        duration=time.monotonic()-start
        journal({'event':'study_end','wall_end_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'duration_s':duration,'attempt_slots':budget['attempts']})
    summary=summarize(runs,plan['cases'])
    confirmed=sum(c['result']['status'] in ('ok','http_error') for r in runs for c in r['calls'])
    summary.update(wall_start_utc=wall_start,wall_end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   duration_s=duration,post_attempt_upper_bound=budget['attempts'],confirmed_posts=confirmed,
                   planned_posts=plan['config']['planned_posts'],planned_answers=plan['config']['planned_answers'],
                   execution='offline-test' if worker else 'live',
                   state_characters={k:len(v['text']) for k,v in plan['cases']['states'].items()},
                   plan_sha256=json.loads((directory/'freeze.json').read_text())['plan_sha256'],
                   makespan_definition='Workload start through final receipt, worker cleanup and journal; includes scheduling, process startup, TLS and network.',
                   question_ready_definition='Per-question valid answer availability from workload start; all eight batch answers share its completion time. Not makespan divided by eight.',
                   call_latency_definition='Parent wall time from before worker spawn to response receipt and worker cleanup; excludes prelaunch journal write.',
                   price_note='List-price estimate from observed input tokens at USD 0.042 per million; output free. Not an invoice. Missing usage unpriced.',
                   uncertainty_note='Three workload repetitions per cell; p95 would be unstable and is deliberately not reported. Repeated answers are correlated, not independent quality trials.')
    (directory/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def build_cases():
    text = '''FICTIONAL EXPEDITION ALDER: current operational bulletin, revision 7.
Only facts about Expedition Alder answer the questions. Other depots are unrelated.
Revision 2 (SUPERSEDED): Mara coordinated; gate Amber; departure Tuesday; backup enabled.
Revision 7 (CURRENT): Lyn is coordinator, not Oren; gate Indigo replaces Amber.
Departure is Thursday, not Tuesday. Backup is NOT enabled. A proposal to enable it Friday is not approved and is not current policy.
Current Alder rovers (all other rover facts are obsolete):
Kestrel: water-sealed yes; quarantined no; charge 70 percent.
Marten: water-sealed yes; quarantined yes; charge 95 percent.
Plover: water-sealed no; quarantined no; charge 90 percent.
Swift: water-sealed yes; quarantined no; charge 40 percent.
Current Alder samples:
Quartz: refrigerated yes; spoiled no; transfer permit valid.
Jasper: refrigerated yes; spoiled no; transfer permit revoked, not valid.
Opal: refrigerated no; spoiled no; transfer permit valid.
Flint: refrigerated yes; spoiled yes; transfer permit valid.
Current Alder operators:
Ivo: on duty yes; certified yes; suspended no.
Nia: on duty yes; certified yes; suspended yes (old clearance is superseded).
Uma: on duty no; certified yes; suspended no.
Teo: on duty yes; certified no; suspended no.
Current Alder transfer slots:
S1: west dock; daylight yes; canceled yes.
S2: east dock; daylight yes; canceled no.
S3: west dock; daylight yes; canceled no.
S4: west dock; daylight no; canceled no.
END OF CURRENT ALDER BULLETIN.'''
    distractors = [f'Unrelated Depot D{i:03d} archive: coordinator Agent{i:03d}; gate Copper; departure Monday. '
                   'Its spare pump was enabled in revision 1 but disabled in revision 2. '
                   'Its cargo is not refrigerated; local rover is quarantined. These records do not concern Expedition Alder.'
                   for i in range(44)]
    long = '\n'.join(distractors[:22]) + '\n' + text + '\n' + '\n'.join(distractors[22:])
    specs = [
        ('coordinator', 'For Expedition Alder, who is the CURRENT coordinator, ignoring superseded assignments and explicitly excluded names?', ['mara','lyn','oren','none'], 'lyn'),
        ('gate', 'For Expedition Alder, which gate is CURRENTLY assigned after the replacement, not the superseded gate?', ['amber','copper','indigo','none'], 'indigo'),
        ('backup', 'For Expedition Alder, is backup CURRENTLY enabled or disabled? An unapproved future proposal does not change the current policy.', ['enabled','disabled','unknown'], 'disabled'),
        ('departure', 'For Expedition Alder, what is the CURRENT departure day, not the superseded day?', ['monday','tuesday','thursday','friday'], 'thursday'),
        ('rover', 'Select the current Alder rover that is water-sealed AND not quarantined AND has at least 60 percent charge. All three conditions are required.', ['kestrel','marten','plover','swift','none'], 'kestrel'),
        ('sample', 'Select the current Alder sample that is refrigerated AND not spoiled AND has a currently valid transfer permit. A revoked permit is not valid.', ['quartz','jasper','opal','flint','none'], 'quartz'),
        ('operator', 'Select the current Alder operator who is on duty AND certified AND not suspended. Superseded clearance does not cancel a current suspension.', ['ivo','nia','uma','teo','none'], 'ivo'),
        ('slot', 'Select the current Alder transfer slot at the west dock AND in daylight AND not canceled. All three conditions are required.', ['s1','s2','s3','s4','none'], 's3'),
    ]
    return {'provenance':'original-authored-synthetic-speed-study',
            'states':{'short':{'text':text},'long':{'text':long}},
            'questions':{qid:{'type':'choice','instructions':instruction,
                              'criteria':{option:('No candidate satisfies the question.' if option == 'none' else option)
                                          for option in options}} for qid,instruction,options,gold in specs},
            'gold':{qid:gold for qid,instruction,options,gold in specs}}


def make_payload(cases, context, qids):
    return {'model':MODEL,'state':cases['states'][context],
            'questions':{qid:cases['questions'][qid] for qid in qids}}
