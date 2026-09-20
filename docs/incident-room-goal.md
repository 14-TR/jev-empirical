# Goal: build and test Incident Room

Status: first scoped goal completed. Reviewed simulator/app source published in `8b2734e`; actual hybrid episode stabilized at tick 8, while the rules baseline stabilized at tick 4. All 79 tests and hosted CI passed. Public browser playback passed desktop/phone-width smoke checks with no failed assets or unexpected network requests. Preview: https://14-tr.github.io/jev-empirical/apps/incident-room/ . Browser is explicitly recorded replay; new inference runs via the local CLI. See `apps/incident-room/RESULTS.md` for evidence and remaining hardening limitations.

## Product

A small original fictional space-station incident simulator. Three crew members respond to a bounded crisis. A station map, event timeline and decision inspector make the hybrid architecture visible. This is an operations/monitor console, not a generic chatbot.

## Architecture and scope

- Deterministic code owns state transitions, legal actions, resource accounting and terminal outcomes.
- Jev chooses bounded per-crew actions against the same snapshot, batching independent decisions.
- Local Qwen supplies advisory planning or narrative at a consequential point; its output cannot directly execute actions or alter state.
- Keep actor observations explicit; do not claim realistic human behavior or multi-agent cognition from a synthetic scenario.
- Separate state transition logic, provider adapters and rendering. Reuse the existing bounded provider components where suitable; preserve the evidence-agent behavior/tests.
- Provide explicit offline-rule, live-hybrid and recorded-replay labels. Never represent a rule-based or recorded decision as live inference.
- First UI may be static with recorded actual episodes plus local run/export commands. No public paid-inference endpoint, credentials in browser assets, or external real-world tools.

## Acceptance criteria

1. Working clickable browser console with map, crew state, resources, incident timeline, decision inspection, step/play/reset and visible stopping reason.
2. Bounded deterministic simulation with tests for legal/illegal actions, conservation/bounds, simultaneous resolution, terminal precedence, and deterministic replay.
3. Actual live Jev actions and at least one actual local Qwen invocation in a bounded synthetic episode; preserve failures and clarify if the episode is unresolved rather than forcing a success.
4. Offline conventional-policy comparison under the same transition rules; record outcome, total model calls, latency and invariant violations. One scenario is illustrative, not evidence of superior intelligence.
5. Browser smoke verification including playback to termination and no unexpected network calls.
6. Independent review, secret checks, incremental commits/pushes and a verified public static preview if available without exposing live credentials.

## Initial resource boundary

Use the existing Python stdlib runtime, browser HTML/CSS/JavaScript and already installed Ollama qwen2.5:7b. No new model download, database, cloud inference service or scheduler. Bound first live episode to at most 20 Jev requests, 2 Qwen requests and 300 seconds, with no automatic retries. Request caps are not dollar ceilings. Preserve actual token usage and label price estimates separately from invoices.

Source/runtime artifacts should remain small text files; model weights already occupy local disk. Measure final artifact size and actual run duration rather than treating source size as total runtime footprint. This is a first scoped build, not a persistent autonomous service.

## Evidence and publication

Credentials remain in environment only. Private response logs stay outside Git and synced notes. Publish original fixture data, source code, allowlisted episode state/action records, explicit model provenance and honest limitations. Ground scene state and displayed metrics in executed records, not decorative invented statistics.

Follow-up work can grow agent behavior or world complexity separately after this interaction is observed and tested.
