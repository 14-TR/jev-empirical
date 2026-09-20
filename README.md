# Jev Empirical

Independent, reproducible behavioral evaluation of TypeSafe's Jev.

**Status: empirical studies, a working hybrid evidence agent, and the tested Incident Room app are published.**

## Try Incident Room

**[Open the browser console](https://14-tr.github.io/jev-empirical/apps/incident-room/)** — inspect and play an actual recorded Jev/Qwen episode. No API keys or paid inference in the browser.

The first hybrid episode stabilized at tick 8; the simple rules baseline stabilized at tick 4. The hybrid worked, but did not beat that baseline. [Results and limitations](apps/incident-room/RESULTS.md) · [run new episodes locally](apps/incident-room/README.md) · [read-only evidence-agent instructions](docs/hybrid-harness.md).

- [Live speed comparison](studies/speed-01/summary.md): batching, serial calls, and concurrency four on matched eight-question workloads; [reproduction instructions](studies/speed-01/README.md).

- [First live diagnostic results](results/diagnostic-01/README.md): 101/101 authored diagnostic labels matched; deliberately limited, ceiling-effect evidence.
- [Run the harness](scripts/USAGE.md): offline baseline, explicit live mode, replay, safety limits, and metric conventions.

## Read the study

- [Evidence review](docs/evidence-review.md): documented API and price, vendor results, third-party experiments, and methodological qualifications.
- [Broad evaluation protocol](docs/protocol.md): prospective design, baselines, statistical analysis, robustness, and operational tests. A draft, not a completed preregistration.
- [Limitations](docs/limitations.md): what each evidence tier can and cannot establish.
- [Source ledger](docs/sources.json): retrieved references and supporting excerpts.

This project asks where typed decision models succeed, where they fail, and whether their probabilities, latency, and cost support useful software decisions. It is broad by design; application-specific adoption decisions come later.

## Study boundaries

- Evaluate Choice, Noul, and Score separately before drawing workflow conclusions.
- Cover routing, evidence judgments, candidate selection, ordinal judgments, robustness, calibration, and operational behavior.
- Distinguish original synthetic diagnostics from representative held-out evaluations.
- Separate vendor claims, observed API behavior, offline baseline measurements, and untested hypotheses.
- Preserve failure denominators, uncertainty, provenance, and negative results.
- A well-typed answer is not necessarily correct. Distribution concentration is not permission to execute an action.

## Publication policy

Development lands in meaningful, independently reviewed checkpoints, not one final code dump. Initial milestones: study charter and safety policy; protocol and source audit; tested benchmark harness; bounded experiments; measured findings and limitations.

Public artifacts contain only original/publicly redistributable inputs and explicitly selected results. Credentials, private source downloads, raw API responses, local environment files, and private execution logs stay outside Git. See [SECURITY.md](SECURITY.md).

This is an independent project, not an official TypeSafe benchmark or endorsement. No affiliation is asserted.

Copyright © 2026 TR Ingram. Code is MIT licensed; third-party material retains its original rights. Original benchmark fixtures are separately labeled in their dataset documentation.
