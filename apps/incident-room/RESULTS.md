# Incident Room: first actual hybrid episode

## Executed result

The live hybrid stabilized the station at **tick 8**. It made **8 Jev requests** (three simultaneous crew questions each) and **1 local Qwen request**, with no failed calls and zero observed invariant violations. Total runner elapsed time was **11.967407 seconds**. The opening Qwen advisory took **9.210152 seconds**; median Jev request latency was **339.172 ms**. Latency includes local client/process and network overhead.

Actual returned model identities were checked: `jev-1.13.0` and `qwen2.5:7b`. Jev reported **8,763 input tokens and 933 output tokens**; Qwen reported **620 input and 129 output tokens**. These are usage counters, not reconciled charges.

## Conventional-policy comparison

The bundled deterministic rule policy stabilized the same initial world at **tick 4**, with **zero model calls**. Thus the hybrid took more simulation ticks in this example; there is no evidence here that adding models improved the outcome or efficiency. The experiment establishes that real model-selected actions can drive the simulator safely within the implemented constraints—not that the models are better than a simple policy.

One fixed scenario and one hybrid episode do not establish reliability, realistic human behavior, general planning ability, or stable latency. All crew see complete shared telemetry. The fixed crew priority for conflicts is a simulation convention.

## Verified

- 79 tests passed, including the existing harness regressions.
- Independent review exercised 2,400 transition-order/conservation probes and provider/export checks.
- Both rules and hybrid records passed exact deterministic reexecution.
- Each actual Jev journal response was reconciled against its published action frame; call counts, model IDs, usage and latencies were checked against the private journal.
- Desktop and phone-sized browser viewports rendered without page/console errors or horizontal overflow. Step, reset and playback to stabilization passed. No external requests were observed on the local static page.
- Public default is **recorded hybrid replay**, not fresh inference. Model calls occur only via the explicit local CLI. Advisory free text remains withheld in the public export.

## Known limitations

Replay validation proves state/action consistency, not provider authenticity. The first validator does not fully bind call metadata to every action frame; this episode was independently reconciled as described above. The first runner also does not automatically enforce the returned Jev version against the pinned request, so the actual response identities were checked separately. These are hardening follow-ups, not claims of completed protections.

## Artifacts

- [Browser console](index.html)
- [Actual hybrid episode](live-episode.json)
- [Rules-only baseline](episode.json)
- [Run and validation instructions](README.md)

Raw provider journals and credentials remain outside Git. Published JSON contains original fictional world state and allowlisted numerical/decision metadata only.
