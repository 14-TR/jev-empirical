"""Incident Room v1: pure, deterministic state transitions; no I/O or models."""
from copy import deepcopy

VERSION = 'incident-room/1'
CREW = ('ada', 'ivo', 'nia')
ROOMS = {'bridge': ('reactor', 'support', 'airlock'), 'reactor': ('bridge',),
         'support': ('bridge',), 'airlock': ('bridge',)}
WORK = {'patch_leak': ('airlock', 4), 'repair_reactor': ('reactor', 6),
        'repair_scrubber': ('support', 4), 'boost_oxygen': ('support', 8),
        'generate_power': ('reactor', 0), 'brace_hull': ('airlock', 4)}
DESCRIPTIONS = {'hold': 'Wait without spending resources.',
    'patch_leak': 'Spend 4 power and 1 patch: leak -1, hull +12.',
    'repair_reactor': 'Spend 6 power: reactor fault -1. At zero: generate 12 power/tick.',
    'repair_scrubber': 'Spend 4 power: scrubber fault -1. At zero: generate 8 oxygen/tick.',
    'boost_oxygen': 'Spend 8 power: oxygen +15.',
    'generate_power': 'Manual crank: power +10, no cost.',
    'brace_hull': 'Spend 4 power: hull +10.'}


def initial_state():
    return {'tick': 0, 'resources': {'oxygen': 62, 'power': 45, 'hull': 54},
            'faults': {'leak': 2, 'reactor': 2, 'scrubber': 2}, 'patches': 3,
            'crew': {'ada': 'airlock', 'ivo': 'reactor', 'nia': 'support'},
            'stable_ticks': 0, 'status': 'active', 'reason': 'incident_open'}


def legal_actions(state, crew):
    if crew not in CREW or state['status'] != 'active':
        return {}
    room = state['crew'][crew]
    actions = {'hold': DESCRIPTIONS['hold']}
    actions.update({'move_' + dest: 'Move to ' + dest + '; no work this tick.' for dest in ROOMS[room]})
    f, r = state['faults'], state['resources']
    for action, (station, cost) in WORK.items():
        if station != room or cost > r['power']:
            continue
        if action == 'patch_leak' and (not f['leak'] or not state['patches']): continue
        if action == 'repair_reactor' and not f['reactor']: continue
        if action == 'repair_scrubber' and not f['scrubber']: continue
        if action == 'brace_hull' and (f['leak'] or r['hull'] == 100): continue
        if action == 'boost_oxygen' and r['oxygen'] == 100: continue
        if action == 'generate_power' and r['power'] == 100: continue
        actions[action] = DESCRIPTIONS[action]
    return actions


def validate_state(s):
    if type(s) is not dict or set(s) != set(initial_state()): raise ValueError('invalid_state')
    for field, keys, maximum in (('resources', ('oxygen', 'power', 'hull'), 100),
                                  ('faults', ('leak', 'reactor', 'scrubber'), 2)):
        if type(s[field]) is not dict or set(s[field]) != set(keys): raise ValueError('invalid_state')
        if any(type(v) is not int or not 0 <= v <= maximum for v in s[field].values()): raise ValueError('invalid_state')
    if type(s['crew']) is not dict or set(s['crew']) != set(CREW) or any(v not in ROOMS for v in s['crew'].values()): raise ValueError('invalid_state')
    for k, hi in (('patches', 3), ('tick', 20), ('stable_ticks', 2)):
        if type(s[k]) is not int or not 0 <= s[k] <= hi: raise ValueError('invalid_state')
    if s['status'] not in ('active', 'failed', 'stabilized', 'unresolved'): raise ValueError('invalid_state')
    if s['reason'] not in ('incident_open', 'oxygen_depleted', 'power_depleted', 'hull_depleted', 'station_stable', 'tick_limit'): raise ValueError('invalid_state')


def step(state, actions, max_ticks=12):
    validate_state(state)
    if type(max_ticks) is not int or not 1 <= max_ticks <= 20 or state['tick'] >= max_ticks:
        raise ValueError('invalid_tick_limit')
    if type(actions) is not dict or set(actions) != set(CREW):
        raise ValueError('invalid_action_batch')
    if any(type(actions[c]) is not str or actions[c] not in legal_actions(state, c) for c in CREW):
        raise ValueError('illegal_action')
    s, events, occupied = deepcopy(state), [], set()
    available = state['resources']['power']
    for c in CREW:
        action, result = actions[c], 'applied'
        before = deepcopy(s['resources'])
        if action.startswith('move_'):
            s['crew'][c] = action[5:]
        elif action in WORK:
            room, cost = WORK[action]
            if room in occupied: result = 'station_conflict'
            elif cost > available: result = 'resource_conflict'
            else:
                occupied.add(room); available -= cost; s['resources']['power'] -= cost
                if action == 'patch_leak':
                    s['faults']['leak'] -= 1; s['patches'] -= 1; s['resources']['hull'] += 12
                elif action == 'repair_reactor': s['faults']['reactor'] -= 1
                elif action == 'repair_scrubber': s['faults']['scrubber'] -= 1
                elif action == 'boost_oxygen': s['resources']['oxygen'] += 15
                elif action == 'generate_power': s['resources']['power'] += 10
                elif action == 'brace_hull': s['resources']['hull'] += 10
                s['resources'] = {k: min(100, v) for k, v in s['resources'].items()}
        events.append({'kind': 'action', 'crew': c, 'action': action, 'result': result,
                       'delta': {k: s['resources'][k] - v for k, v in before.items()}})
    s['tick'] += 1
    before = deepcopy(s['resources'])
    delta = {'oxygen': -3 - 3 * s['faults']['leak'] + (8 if not s['faults']['scrubber'] else 0),
             'power': -2 + (12 if not s['faults']['reactor'] else 0), 'hull': -2 * s['faults']['leak']}
    for key, value in delta.items():
        s['resources'][key] = max(0, min(100, s['resources'][key] + value))
    events.append({'kind': 'environment', 'delta': {k: s['resources'][k] - v for k, v in before.items()}})
    stable = not any(s['faults'].values()) and all(s['resources'][k] >= v for k, v in {'oxygen': 55, 'power': 40, 'hull': 60}.items())
    s['stable_ticks'] = s['stable_ticks'] + 1 if stable else 0
    depleted = next((k for k in ('oxygen', 'power', 'hull') if s['resources'][k] == 0), None)
    if depleted: s['status'], s['reason'] = 'failed', depleted + '_depleted'
    elif s['stable_ticks'] >= 2: s['status'], s['reason'] = 'stabilized', 'station_stable'
    elif s['tick'] >= max_ticks: s['status'], s['reason'] = 'unresolved', 'tick_limit'
    if s['status'] != 'active': events.append({'kind': 'terminal', 'status': s['status'], 'reason': s['reason']})
    validate_state(s)
    return s, events
