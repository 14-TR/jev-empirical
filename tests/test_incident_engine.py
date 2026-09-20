import copy
import importlib
import unittest


def engine():
    try:
        return importlib.import_module('incident_room.engine')
    except ImportError:
        raise AssertionError('Incident Room deterministic engine is missing') from None


class EngineTests(unittest.TestCase):
    def test_one_simultaneous_tick_has_exact_resource_accounting(self):
        e = engine()
        s = e.initial_state()
        original = copy.deepcopy(s)
        result, events = e.step(s, {c: 'hold' for c in e.CREW}, 12)
        self.assertEqual(s, original)
        self.assertEqual(result['tick'], 1)
        self.assertEqual(result['resources'], {'oxygen': 53, 'power': 43, 'hull': 50})
        self.assertEqual(result['status'], 'active')
        self.assertEqual(events[-1]['kind'], 'environment')
        self.assertEqual(e.step(s, {c: 'hold' for c in e.CREW}, 12), (result, events))

    def test_impossible_action_rejects_whole_batch_without_mutation(self):
        e = engine(); s = e.initial_state(); before = copy.deepcopy(s)
        for actions in ({'ada': 'repair_reactor', 'ivo': 'hold', 'nia': 'hold'},
                        {'ada': 'teleport', 'ivo': 'hold', 'nia': 'hold'},
                        {'ada': 'hold'}, {'ada': 'hold', 'ivo': 'hold', 'nia': 'hold', 'x': 'hold'}):
            with self.assertRaises(ValueError): e.step(s, actions)
            self.assertEqual(s, before)

    def test_repairs_resolve_together_and_spend_snapshot_resources(self):
        e = engine(); s = e.initial_state()
        actions = {'ada': 'patch_leak', 'ivo': 'repair_reactor', 'nia': 'repair_scrubber'}
        self.assertEqual(set(e.legal_actions(s, 'ada')), {'hold', 'move_bridge', 'patch_leak'})
        out, events = e.step(s, actions)
        self.assertEqual(out['resources'], {'oxygen': 56, 'power': 29, 'hull': 64})
        self.assertEqual(out['faults'], {'leak': 1, 'reactor': 1, 'scrubber': 1})
        self.assertEqual(out['patches'], 2)
        self.assertEqual(out, e.step(s, dict(reversed(list(actions.items()))))[0])
        s['resources']['power'] = 6
        out, events = e.step(s, actions)
        self.assertEqual([x['result'] for x in events[:3]], ['applied', 'resource_conflict', 'resource_conflict'])
        self.assertEqual(out['faults']['reactor'], 2)
        self.assertEqual(out['resources']['power'], 0)

    def test_single_workstation_collision_has_fixed_crew_priority(self):
        e = engine(); s = e.initial_state(); s['crew']['ivo'] = 'airlock'
        out, events = e.step(s, {'ada': 'patch_leak', 'ivo': 'patch_leak', 'nia': 'hold'})
        self.assertEqual(out['faults']['leak'], 1)
        self.assertEqual(events[1]['result'], 'station_conflict')
        self.assertEqual(out['patches'], 2)

    def test_terminal_precedence_failure_then_success_then_tick_limit(self):
        e = engine()
        s = e.initial_state(); s['resources']['oxygen'] = 1
        out, _ = e.step(s, {c: 'hold' for c in e.CREW}, 1)
        self.assertEqual((out['status'], out['reason']), ('failed', 'oxygen_depleted'))
        with self.assertRaises(ValueError): e.step(out, {c: 'hold' for c in e.CREW}, 1)
        s = e.initial_state(); s['faults'] = dict.fromkeys(s['faults'], 0)
        s['resources'] = {'oxygen': 60, 'power': 60, 'hull': 65}; s['stable_ticks'] = 1
        out, _ = e.step(s, {c: 'hold' for c in e.CREW}, 1)
        self.assertEqual(out['status'], 'stabilized')
        out, _ = e.step(e.initial_state(), {c: 'hold' for c in e.CREW}, 1)
        self.assertEqual((out['status'], out['reason']), ('unresolved', 'tick_limit'))

    def test_state_and_tick_bounds_reject_booleans_and_unbounded_runs(self):
        e = engine()
        for limit in (0, 21, True, float('nan')):
            with self.assertRaises(ValueError): e.step(e.initial_state(), dict.fromkeys(e.CREW, 'hold'), limit)
        for value in (-1, 101, True, float('nan')):
            s = e.initial_state(); s['resources']['oxygen'] = value
            with self.assertRaises(ValueError): e.step(s, dict.fromkeys(e.CREW, 'hold'))
        s = e.initial_state(); s['resources']['power'] = 98
        out, events = e.step(s, {'ada': 'hold', 'ivo': 'generate_power', 'nia': 'hold'})
        self.assertEqual(out['resources']['power'], 98)
        for resource in s['resources']:
            self.assertEqual(s['resources'][resource] + sum(v['delta'][resource] for v in events), out['resources'][resource])
