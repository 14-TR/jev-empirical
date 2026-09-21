"""Predeclared operator-trusted checks. Isolated copy, NOT an OS sandbox."""
from pathlib import Path
import sys
import tempfile
from .source import child_env, command, digest, safe_text

PROFILES = ('incident-unittest', 'incident-replay-metadata')
BOOTSTRAP = "import sys; sys.path.insert(0, 'src'); "
SCRIPTS = {
    'incident-unittest': BOOTSTRAP + "import unittest; suite=unittest.defaultTestLoader.discover('tests', pattern='test_incident_episode.py'); result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(0 if result.wasSuccessful() and result.testsRun else 1)",
    'incident-replay-metadata': BOOTSTRAP + "import copy,json; from pathlib import Path; from incident_room import episode as r; original=json.loads(Path('apps/incident-room/live-episode.json').read_text()); before=copy.deepcopy(original); candidate=copy.deepcopy(original); next(c for c in candidate['calls'] if c['provider']=='jev')['tick']=19; candidate=r.seal(candidate); accepted=False\ntry: accepted=bool(r.validate_replay(candidate))\nexcept (ValueError,KeyError,TypeError): pass\nprint(json.dumps({'original_valid':r.validate_replay(original),'changed_call_tick_accepted':accepted,'mutated_tick':19,'final_frame_tick':original['frames'][-1]['state']['tick'],'original_integrity':original['integrity'],'mutated_integrity':candidate['integrity'],'original_unchanged':original==before}))"
}


def run_check(profile, snapshot, allow_checks, approved, timeout):
    if not allow_checks or profile not in approved or profile not in PROFILES:
        raise ValueError('check_consent_required')
    required = 'tests/test_incident_episode.py' if profile == 'incident-unittest' else 'src/incident_room/episode.py'
    if required not in snapshot.files: raise ValueError('check_source_missing')
    inputs = [required]
    if profile == 'incident-replay-metadata':
        inputs += ['apps/incident-room/live-episode.json']
        if any(path not in snapshot.files for path in inputs): raise ValueError('check_source_missing')
    with tempfile.TemporaryDirectory(prefix='check-', dir=snapshot.root.parent) as tmp:
        root = Path(tmp); work = root / 'checkout'; work.mkdir(mode=0o700)
        home = root / 'home'; home.mkdir(mode=0o700)
        for path in snapshot.files:
            text = snapshot.read(path); target = work / path
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.write_text(text, encoding='utf-8'); target.chmod(0o600)
        code, raw = command([str(Path(sys.executable).resolve()), '-I', '-S', '-c', SCRIPTS[profile]],
                            cwd=work, env=child_env(home), timeout=min(timeout, 25), cap=10000)
        text = raw.decode('utf-8', errors='replace')
        if not safe_text(text): raise ValueError('sensitive_check_output')
        return {'tool': 'run_check', 'profile': profile, 'exit_code': code, 'output': text,
                'profile_sha256': digest(SCRIPTS[profile].encode()),
                'output_sha256': digest(raw), 'os_sandbox': False, 'environment': 'explicit allowlist; no inherited credentials',
                'refs': [{'commit': snapshot.commit, 'path': path, 'sha256': snapshot.files[path]['sha256']} for path in inputs]}
