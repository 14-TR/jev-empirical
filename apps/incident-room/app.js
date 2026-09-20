'use strict';
(() => {
  const $ = id => document.getElementById(id), crew = ['ada', 'ivo', 'nia'];
  const roomNames = {bridge: 'Bridge', reactor: 'Reactor', support: 'Life support', airlock: 'Airlock'};
  let episode, index = 0, selected = 'ada', timer = null;
  const pretty = s => String(s).replaceAll('_', ' ');
  const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
  const freeze = x => { if (x && typeof x === 'object') { Object.values(x).forEach(freeze); Object.freeze(x); } return x; };
  function check(e) {
    if (!e || e.schema !== 'incident-room/1' || !['offline-rule', 'live-hybrid'].includes(e.mode) || e.scenario?.id !== 'sable-relay-01') throw Error('Not an Incident Room v1 public episode.');
    if (!Array.isArray(e.frames) || !e.frames.length || e.frames.length > 21 || !Number.isInteger(e.limits?.max_ticks) || e.limits.max_ticks < 1 || e.limits.max_ticks > 20 || e.frames.length > e.limits.max_ticks + 1) throw Error('Invalid frame bounds.');
    if (!['stabilized', 'failed', 'unresolved', 'error'].includes(e.outcome?.status)) throw Error('Invalid endpoint.');
    if (typeof e.advisory?.text !== 'string' || e.advisory.text.length > 4000 || !Array.isArray(e.calls) || e.calls.length > 22 || !e.metrics) throw Error('Invalid metadata.');
    e.frames.forEach((f, i) => {
      const s = f.state;
      if (!s || s.tick !== i || !['active', 'stabilized', 'failed', 'unresolved'].includes(s.status) || !Array.isArray(f.events) || f.events.length > 10) throw Error('Invalid snapshot sequence.');
      ['oxygen', 'power', 'hull'].forEach(k => { if (!Number.isInteger(s.resources?.[k]) || s.resources[k] < 0 || s.resources[k] > 100) throw Error('Resource invariant failed.'); });
      ['leak', 'reactor', 'scrubber'].forEach(k => { if (!Number.isInteger(s.faults?.[k]) || s.faults[k] < 0 || s.faults[k] > 2) throw Error('Invalid fault.'); });
      crew.forEach(c => {
        if (!Object.hasOwn(roomNames, s.crew?.[c])) throw Error('Unknown crew location.');
        if (i && (!f.legal?.[c] || !Object.hasOwn(f.legal[c], f.actions?.[c]) || f.decisions?.[c]?.choice !== f.actions[c])) throw Error('Decision is not in the recorded legal menu.');
        if (i && Object.keys(f.legal[c]).length > 12) throw Error('Oversized decision menu.');
      });
    });
    return freeze(e);
  }
  function pause() { clearInterval(timer); timer = null; $('play').disabled = !episode || index === episode.frames.length - 1; $('pause').disabled = true; $('playback').textContent = episode && index === episode.frames.length - 1 ? 'END OF RECORD' : 'PAUSED'; }
  function load(data) { const checked = check(data); pause(); episode = checked; index = 0; $('error').hidden = true; $('scrubber').max = episode.frames.length - 1; render(); }
  function step() { if (index < episode.frames.length - 1) { index++; render(); } if (index === episode.frames.length - 1) pause(); }
  function render() {
    const f = episode.frames[index], s = f.state, end = index === episode.frames.length - 1;
    $('mode').textContent = 'RECORDED REPLAY · ' + (episode.mode === 'offline-rule' ? 'RULES ONLY' : 'LIVE-HYBRID SOURCE');
    $('brief').textContent = episode.scenario.brief;
    $('tick').textContent = String(index).padStart(2, '0'); $('total').textContent = '/ ' + String(episode.frames.length - 1).padStart(2, '0');
    ['oxygen', 'power', 'hull'].forEach(k => { $(k).value = s.resources[k]; $(k + '-value').textContent = s.resources[k]; });
    $('status').textContent = s.status.toUpperCase(); $('stability').textContent = 'Stable ticks ' + s.stable_ticks + ' / 2'; $('patches').textContent = 'PATCH STOCK ' + s.patches + ' / 3';
    Object.keys(roomNames).forEach(room => {
      const box = $('room-' + room), fault = {reactor: 'reactor', support: 'scrubber', airlock: 'leak'}[room];
      box.classList.toggle('alert', !!(fault && s.faults[fault]));
      box.querySelector('.fault').textContent = fault ? (s.faults[fault] ? pretty(fault) + ' fault ' + s.faults[fault] + '/2' : 'System restored') : 'Shared telemetry';
      const occupants = box.querySelector('.occupants'); occupants.replaceChildren();
      crew.filter(c => s.crew[c] === room).forEach(c => occupants.append(el('span', c.toUpperCase(), 'occupant')));
    });
    $('crew').replaceChildren(...crew.map(c => { const n = el('div', undefined, 'crew-person'); n.append(el('b', c[0].toUpperCase() + c.slice(1)), el('span', roomNames[s.crew[c]]), el('span', index ? pretty(f.actions[c]) : 'Awaiting response')); return n; }));
    $('outcome').textContent = end ? episode.outcome.status.toUpperCase() + ' / ' + pretty(episode.outcome.reason) + (s.status === 'active' ? ' — last world snapshot remains active' : '') : 'Record in progress · ' + (episode.frames.length - 1 - index) + ' ticks remaining';
    $('decision-tick').textContent = index ? 'T+' + String(index - 1).padStart(2, '0') + ' → ' + String(index).padStart(2, '0') : 'INITIAL SNAPSHOT';
    const dest = $('decisions'); dest.replaceChildren();
    if (!index) { dest.append(el('p', 'Awaiting first decision', 'selection'), el('p', 'Step forward to inspect the recorded choices, legal options and deterministic resolution.', 'caption')); }
    else {
      const d = f.decisions[selected], event = f.events.find(x => x.crew === selected);
      dest.append(el('p', pretty(d.choice), 'selection'), el('p', (d.source === 'rules' ? 'Conventional rule policy · no model call' : 'Jev choice · confidence ' + (100 * d.confidence).toFixed(1) + '%') + ' · ' + pretty(event?.result || ''), 'caption'));
      Object.entries(f.legal[selected]).forEach(([a, description]) => {
        const row = el('div', undefined, 'option' + (a === d.choice ? ' selected' : '')); row.append(el('span', (a === d.choice ? '→ ' : '') + pretty(a)));
        if (d.probabilities) { const p = d.probabilities[a]; row.append(el('span', (100 * p).toFixed(1) + '%', 'prob')); const bar = el('span', undefined, 'probbar'); bar.style.width = Math.max(0, Math.min(100, p * 100)) + '%'; row.append(bar); }
        row.append(el('p', description)); dest.append(row);
      });
    }
    $('advice-source').textContent = episode.mode === 'offline-rule' ? 'NO MODEL' : 'QWEN · ADVISORY ONLY';
    $('advice').textContent = episode.advisory.text || (episode.advisory.status === 'withheld' ? 'An opening advisory was recorded privately; text was withheld from this public export.' : 'No advisory requested. This episode uses the explicit rules-only baseline.');
    const m = episode.metrics, accounting = $('accounting'); accounting.replaceChildren();
    [['Jev requests', m.jev_calls], ['Qwen requests', m.qwen_calls], ['Runner elapsed', Number(m.elapsed_seconds).toFixed(3) + ' s'], ['Invariant violations', m.invariant_violations]].forEach(([k,v]) => accounting.append(el('dt', k), el('dd', v)));
    episode.calls.forEach(call => { accounting.append(el('dt', call.provider + ' @ tick ' + call.tick + ' / ' + call.status), el('dd', Number(call.latency_seconds).toFixed(3) + ' s')); accounting.append(el('dt', 'Tokens in / out'), el('dd', (call.usage?.input_tokens ?? 'unknown') + ' / ' + (call.usage?.output_tokens ?? 'unknown'))); });
    const log = $('timeline'); log.replaceChildren();
    const init = el('div', undefined, 'event'); init.append(el('time', 'T+00'), el('span', 'Debris strike. Pressure loss and systems fault detected.'), el('span', '3 crew · shared telemetry')); log.append(init);
    episode.frames.slice(1, index + 1).forEach(frame => frame.events.forEach(event => {
      const row = el('div', undefined, 'event' + (event.kind === 'terminal' ? ' event-terminal' : ''));
      let text = event.kind === 'action' ? event.crew.toUpperCase() + ' / ' + pretty(event.action) : event.kind === 'environment' ? 'Station life-support cycle' : pretty(event.reason);
      const delta = event.delta ? Object.entries(event.delta).filter(([,v]) => v).map(([k,v]) => k + ' ' + (v > 0 ? '+' : '') + v).join(' · ') : '';
      row.append(el('time', 'T+' + String(frame.state.tick).padStart(2, '0')), el('span', text), el('span', (event.result && event.result !== 'applied' ? pretty(event.result) : delta))); log.append(row);
    }));
    if (end && s.status === 'active') { const row = el('div', undefined, 'event event-terminal'); row.append(el('time', 'STOP'), el('span', pretty(episode.outcome.reason)), el('span', 'No fallback / world not advanced')); log.append(row); }
    log.scrollTop = log.scrollHeight;
    $('scrubber').value = index; $('step').disabled = end; $('play').disabled = end || timer !== null; if (end) pause();
  }
  $('step').onclick = () => { pause(); step(); };
  $('reset').onclick = () => { pause(); index = 0; render(); };
  $('pause').onclick = pause;
  $('play').onclick = () => { if (!timer && index < episode.frames.length - 1) { timer = setInterval(step, 950); $('play').disabled = true; $('pause').disabled = false; $('playback').textContent = 'PLAYING RECORD'; } };
  $('scrubber').oninput = event => { pause(); index = Number(event.target.value); render(); };
  document.querySelectorAll('[data-crew]').forEach(button => button.onclick = () => { selected = button.dataset.crew; document.querySelectorAll('[data-crew]').forEach(b => b.setAttribute('aria-pressed', String(b === button))); render(); });
  $('load').onchange = async event => { pause(); try { const file = event.target.files[0]; if (!file) return; if (file.size > 1048576) throw Error('Episode exceeds the 1 MB limit.'); load(JSON.parse(await file.text())); } catch (error) { $('error').textContent = 'Load rejected. ' + error.message; $('error').hidden = false; } finally { event.target.value = ''; } };
  try { load(JSON.parse(JSON.stringify(window.INCIDENT_EPISODE))); } catch (error) { $('error').hidden = false; $('error').textContent = 'No valid default record. Load a public episode JSON. ' + error.message; ['step','play','reset'].forEach(k => $(k).disabled = true); }
})();
