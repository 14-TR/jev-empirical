# Incident Room / Sable Relay

A small deterministic incident simulator and static operations console. Open **[index.html](index.html)** directly (`file://`) or serve the repository with `python3 -m http.server 8080` and visit `http://localhost:8080/apps/incident-room/`. Local CSS, JavaScript and a generated `episode.js` supply the default record: **no fetch, API key, backend, CDN or paid call in the browser**. The default is explicitly **recorded live-hybrid replay**, not fresh browser inference. The separate `episode.json` preserves the **rules-only baseline**. See [actual results and limitations](RESULTS.md).

## Run and verify

From the repository root, Python 3.9+ stdlib, no installation required:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m incident_room run --public apps/incident-room/episode.json --asset apps/incident-room/episode.js
PYTHONPATH=src python3 -m incident_room validate apps/incident-room/episode.json
node --check apps/incident-room/app.js
```

Step, play, pause, reset, scrub the tick slider, inspect each crew member's choices, and load an exported JSON file. Playback never calls a provider or changes the underlying record. Loaded JSON is size/shape/invariant checked, frozen recursively and rendered through `textContent`; **the authoritative exact reexecution check is the Python `validate` command**, not the browser's structural check. Validate downloaded records locally before trusting them. The SHA-256 digest detects accidental edits, not forged provenance or malicious re-signing.

## Explicit live run (parent/reviewer only)

No live call was made to build the bundled sample. Before this command, have `TYPESAFE_API_KEY` in the environment and an already installed `qwen2.5:7b` served at `127.0.0.1:11434`. Do not put keys in commands, JSON or browser assets. `--private-dir` must be a **new directory**, outside every Git checkout; symlink components and reuse are rejected by the existing private trace writer.

```sh
PYTHONPATH=src python3 -m incident_room run --mode live-hybrid --allow-live \
  --max-ticks 12 --max-jev 20 --max-qwen 2 --seconds 300 \
  --private-dir /Users/tr/.local/state/incident-room-build/live-01 \
  --public apps/incident-room/live-episode.json
PYTHONPATH=src python3 -m incident_room validate apps/incident-room/live-episode.json
```

This version requests one actual Qwen opening plan, then one Jev HTTP request per tick containing all three independent Choice questions over the same snapshot. Limits are hard ceilings, not a promise to use every call. Jev uses pinned `jev-1.13.0`; Qwen uses `qwen2.5:7b`. Each call runs in the existing killable spawned-process transport with no retries: Jev ≤30 seconds, Qwen ≤60 seconds, remaining wall time also bounds each call. A small reserve covers worker cleanup. Request limits are **not a dollar ceiling**.

Failures remain error/unresolved records with the last valid snapshot. Invalid, absent or malformed model outputs do **not** silently switch to rules. The runner status is separate from world status: a provider failure can stop a still-active world. Calls count attempts including failures; usage is the actual provider count when available, otherwise `null`. Latencies and elapsed time are measured, not estimates. No pricing or invoice claim is made.

Raw successful provider responses and exact supplied payloads go to private `events.jsonl`; the immutable original episode is private `episode.json`, directory 0700/files 0600. Error HTTP bodies are deliberately not read. Disk failure can prevent receipts; such errors never trigger another model call. Normal completed error episodes are exported too. A killed process or machine failure can leave only a partial private journal; there is no crash-resume service.

## Export after review

Default export withholds free-text advisory content. Inspect private evidence locally; only explicitly publish the original fictional advisory after reviewing it. Export projects allowlisted records, removes unknown provider fields, reconstructs state/events with the engine, filters URLs/paths/email/control characters, and rejects current-key echoes. Text filtering is conservative, not a universal secret detector; human review remains required.

```sh
PYTHONPATH=src python3 -m incident_room export \
  /Users/tr/.local/state/incident-room-build/live-01/episode.json \
  --public apps/incident-room/live-episode.json --publish-advisory
PYTHONPATH=src python3 -m incident_room validate apps/incident-room/live-episode.json
```

Load `live-episode.json` with the browser's **Load episode** control. To deliberately make it the default record, add `--asset apps/incident-room/episode.js` to the export command. This changes the displayed default, not its `live-hybrid` provenance; the page still says **recorded replay**. Preserve the rules-only JSON for the conventional-policy comparison. Export does not infer, execute or call models.

## World / rules v1

- Four rooms: bridge connected to reactor, life support, airlock. Ada starts in airlock, Ivo in reactor, Nia in life support. Everyone sees the same complete world telemetry; roles are labels, not privileged capabilities.
- Three 0–100 abstract reserves: oxygen 62, power 45, hull 54. Leak, reactor and scrubber each start with severity 2. Three repair patches are stocked.
- Move along one edge or do one legal local action per tick. Rooms have unlimited occupancy and crossing moves are allowed. At most one crew member can use each workstation in a tick. **Ada, then Ivo, then Nia** wins conflicts deterministically, independent of dictionary order. This fixed priority is a modeling bias, not negotiated coordination.
- Legal menus are computed from the pre-tick snapshot; all selections use that snapshot. Costs reserve starting power; same-tick generation cannot finance another crew action. Conflicted actions consume nothing; events record the reason. Any impossible selection rejects the entire batch before mutation.
- Patch leak: 4 power + 1 patch → leak −1, hull +12. Repair reactor: 6 power → fault −1. Repair scrubber: 4 power → fault −1. Manual crank: power +10. Oxygen boost: 8 power → oxygen +15. Hull brace (after sealing): 4 power → hull +10. Hold costs nothing.
- After all actions: oxygen changes by −3 −3×leak +8 when scrubber is fixed; power changes by −2 +12 when reactor is fixed; hull changes by −2×leak. Reserves clamp to [0,100]; events report **actual** deltas including saturation.
- Terminal precedence: any depleted resource → failed (oxygen before power before hull); otherwise all faults cleared and oxygen≥55, power≥40, hull≥60 for two consecutive ticks → stabilized; otherwise max ticks → unresolved. No further world actions are legal at a terminal state.
- The conventional baseline prioritizes local repairs, then generating power under 60, boosting oxygen under 55, bracing hull under 60, otherwise holding. It uses the same transition engine and is not represented as Jev.
- Qwen's text is advisory data in Jev's input only. It never enters the transition engine, a command interpreter, filesystem tool or browser HTML interpreter. Jev can only select enumerated actions; probabilities/confidence are validated, not a guarantee of good decisions. Low-confidence legal preferences are permitted in this fictional world.

## Boundaries / evidence

`src/incident_room/engine.py` is pure simulation; `episode.py` owns bounded orchestration and exact state/event replay; `providers.py` isolates model I/O; `io.py` projects public records; this folder renders only. The existing evidence-agent controller is unchanged. Tests use explicit injected providers for live-path contracts; these fixtures are **not** real inference or published model evidence.

One fixed, authored scenario is illustrative, not evidence of superiority, realistic multi-agent cognition or general planning performance. There is no stochastic environment, memory beyond telemetry plus opening advice, trained crew policy, database or scheduler. Existing local model weights are separate from these small source/replay artifacts. No new dependencies/models installed. Parent review owns live execution, browser visual verification, publication and any public URL.
