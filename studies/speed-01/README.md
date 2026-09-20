# Bounded Jev context/strategy study

Start with [summary.md](summary.md). This folder is the standalone, publishable candidate; exact live request/response logs are deliberately outside it.

## Reproduce without changing the original evidence

Python 3.9+ and the standard library only; no installs. From this folder:

```sh
python3 -m unittest -v test_study
python3 run_study.py freeze --plan-dir ../reproduction-plan
# TYPESAFE_API_KEY must already exist in the environment; never put it in a file or argument.
python3 run_study.py run --plan-dir ../reproduction-plan --private-dir ../reproduction-private
```

`freeze` is offline and refuses to overwrite its plan/manifest. `run` is LIVE and spends API usage: 102 planned POSTs, hard reservation ceiling 110, 600-second run budget, 15-second request deadlines, no retries. Use fresh output paths for each separately authorized study. There is no default API execution on import, help, or tests. Tests use explicitly named offline workers, not the API.

The supplied original `plan.json` and `freeze.json` were frozen before live calls. `read_frozen` validates the complete plan and every recorded source digest before execution. Do not edit these files or code and present the old measurements as evidence for the edited candidate. Re-freeze into a new directory to measure an intentional new candidate.

Fresh child processes and HTTPS connections are used equally across strategies. Children are launched only in the main thread; concurrency4 means at most four active child workers, not spawning inside a thread pool. Measured client wall latency includes child startup and cleanup. The fixed HTTPS endpoint and no-redirect/no-retry behavior are in the vendored transport; only `TYPESAFE_API_KEY` supplies a credential.

## Evidence

- `plan.json`: original synthetic states, eight independent questions, separate oracle labels, configuration, randomized order and seed.
- `freeze.json`: pre-call timestamp, plan SHA-256, source SHA-256 values, runtime and documentation links.
- `study.py`: original workload, scheduler, strict parser adapter, timing/correctness/usage aggregation, freeze and run lifecycle.
- `run_study.py`: explicit offline `freeze` and live `run` CLI.
- `test_study.py`: six offline tests, including bounded scheduler and full offline lifecycle.
- `jev_bench/{__init__,core,transport}.py`: byte-identical snapshot from the reviewed local Jev harness; hashes recorded in `freeze.json`. No import or write to the shared source tree is needed to reproduce this study.
- `summary.json`: all workload/call/readiness samples, per-question correctness, totals and missing/failure denominators.
- `calls.csv`, `answers.csv`, `workloads.csv`: public derived measurement tables, not raw provider responses.
- `summary.md`: results, costs, definitions, limitations.
- `verification.json`: post-run counts, digests and credential-scan outcome; no credential values.

Raw live evidence is `../private-raw/requests-responses.jsonl`. It contains launch/completion events and per-workload records with the exact original requests and parsed successful JSON responses; it does not contain authorization headers. Raw bytes, error bodies, arbitrary response headers, and redirect locations are intentionally not logged by the reviewed transport. Successful response parsing is strict, and credential echoes are rejected. The raw directory is mode 0700 and the journal 0600. Do not publish that directory automatically.

Question latency means time from the shared workload start until the response containing that question is available, not batched request time divided by eight. Call latency has a different denominator. All three makespan observations and the median are reported; p95 with n=3 is unstable and omitted. Cost is observed usage multiplied by documented list price, not an invoice.

This is one original synthetic diagnostic with three repeats per condition, not a model leaderboard, GPU-only inference benchmark, or 144 independent accuracy cases. Nothing was committed or pushed.
