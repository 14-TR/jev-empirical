# First actual Jev diagnostic run

This is an executed live `jev-1.13.0` API run, not mocked output. The versioned model returned 101 successful responses, with no retries or failed cases. All predicted labels matched the authored answer key. The saved private receipt replayed to an identical public report.

## Observations

- Routing: 24/24 correct.
- Evidence judgments: 18/18 correct.
- Candidate selection: 24/24 correct.
- Noul predicates: 20/20 correct.
- Ordinal modal levels: 15/15 correct.
- Client-observed median latency: 311.843 ms; p95: 382.481 ms; p99: 434.663 ms.
- Reported input tokens: 38,936; output tokens: 3,643. These counters are not invoice reconciliation.

## Interpretation and limits

These 101 rows comprise 18 simple original English scenarios plus correlated perturbations. They are not independent population samples. Perfect diagnostic accuracy is a ceiling effect, not evidence of universal accuracy, calibration, injection resistance, or superiority over competent competitors. Six injection variants target an answer already equal to the gold label; do not count those as discriminating attack tests. These results motivate harder workloads.

Latency includes Python worker startup and HTTPS client overhead, measured serially from one client in one short run. It is not server-only inference time, steady-state throughput, or a production SLA. There was no competing model run.

## Provenance and publication

The report includes dataset and executed-code hashes. Raw API responses and credentials remain outside the repository. The repaired harness had 35 passing local tests when used; its independent re-review was pending at execution, so this run must not be described as post-approval. No inputs/prompts/labels were revised in response to these outcomes. The original receipt schema lacks a wall-clock timestamp; publication timing must not be substituted for exact request timestamps.

- [Sanitized JSON](report.json)
- [Full generated report](report.md)

This is the first live diagnostic checkpoint, not completion of the broader study.
