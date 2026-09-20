# Jev speed study 01: context and execution strategy

## Result

Live execution completed 2026-09-20T01:45:27.912619+00:00–2026-09-20T01:45:50.008324+00:00. **102 confirmed POSTs; 144/144 correct answers; 18/18 fully correct workloads.** No HTTP/network failures, invalid answers, missing answers, or missing usage records. Live study elapsed **22.089945 s** (600 s limit). No retries, warmups, redirects, or additional live probes.

Only **jev-1.13.0** was tested. These are client-observed execution-strategy measurements, not comparisons against other models or measurements of GPU inference time.

## Complete eight-question workload makespan

Every cell has three repetitions. Values below are milliseconds, listed in repetition order; medians are descriptive only. All timings include worker startup/cleanup, TLS/network work, and the scheduler. Workload timing also includes per-call journal writes.

| Context | Strategy | All 3 makespans (ms) | Median (ms) | Correct / expected |
|---|---|---|---:|---:|
| short | batch | 322.707, 351.532, 313.906 | 322.707 | 24/24 |
| short | serial | 2576.914, 2810.521, 2651.329 | 2651.329 | 24/24 |
| short | concurrency4 | 625.549, 731.575, 625.493 | 625.549 | 24/24 |
| long | batch | 370.004, 349.628, 325.221 | 349.628 | 24/24 |
| long | serial | 2586.990, 2635.485, 2551.118 | 2586.990 | 24/24 |
| long | concurrency4 | 749.703, 722.043, 779.749 | 749.703 | 24/24 |

Batch was faster for the complete workload in every observed repetition. Ratios of cell medians: short serial/batch **8.216×**, short concurrency4/batch **1.938×**; long serial/batch **7.399×**, long concurrency4/batch **2.144×**. These are descriptive ratios, not statistical guarantees.

## Per-question response availability, not batch latency divided by eight

All questions are ready at workload start. A question’s readiness time is measured from that common origin until its containing response has been received and its worker cleaned up. In a batch, all eight answers share that response-completion timestamp. In serial and concurrency4, queueing is therefore included. Validation against the oracle occurs after collection; these are receipt times of answers subsequently validated.

| Context | Strategy | Median question ready (ms; 24 answers/cell) | Median call wall latency (ms) | Calls/cell |
|---|---|---:|---:|---:|
| short | batch | 322.179 | 320.930 | 3 |
| short | serial | 1495.233 | 330.577 | 24 |
| short | concurrency4 | 479.597 | 302.350 | 24 |
| long | batch | 348.957 | 348.639 | 3 |
| long | serial | 1477.098 | 314.695 | 24 |
| long | concurrency4 | 512.572 | 330.183 | 24 |

Call wall latency runs from just before process spawn through receipt and cleanup, excluding the prelaunch journal write. It is not directly comparable as an eight-answer latency: batched calls contain eight answers, single calls one. Individual values are preserved in `calls.csv`, `answers.csv`, and `summary.json`. **Do not divide batch request latency by eight and call that answer latency.**

## Workload and protocol

- Original, fictional Expedition Alder bulletin; no private user data. Eight fixed independent Choice questions: current coordinator, replaced gate, negated backup policy/unapproved proposal, revised departure day, then conjunctive selection among rovers, samples, operators, and transfer slots.
- Short state: **1,507 characters**. Long state: **12,859 characters** (**8.533×**), containing the identical short bulletin between two equal groups of unrelated archive distractors. This changes context length and target position together; it is a combined distractor/context scaling condition, not a pure length-only causal experiment.
- The same state and exact question text/options are used for all strategies. Labels remain outside API payloads. Serial/concurrency4 resend the state for each question.
- One eight-question batched request; eight serial one-question requests; or eight one-question requests scheduled with at most four active workers. All children are spawned directly by the main thread. New process and HTTPS connection for every request; no pooling.
- Seed **731029** randomizes context order within repetition and strategy order within each context. Actual full order is in `plan.json`; no warmup or seed-shopping.
- Three repetitions per context × strategy: 18 workloads, 102 planned/confirmed POSTs, 144 expected answers. Limit 110 attempt slots; total 600 s; per-request timeout 15 s; retries zero. An attempt slot is reserved before launch. All 102 returned successful responses, so POST count is exact here; on network failure the harness reports confirmed responses separately from the conservative attempt upper bound.
- Fixed endpoint `https://api.typesafe.ai/v1/systemone`; environment `TYPESAFE_API_KEY` only. Vendored reviewed transport does not follow redirects, read proxy settings, retry, or log credentials. It drops error bodies; non-200 status would remain recorded.
- Frozen before live execution at **2026-09-20T01:45:23.781181+00:00**. Fixture/config/seed hash: `15229c3cb11a286d0bc925686ca96951baf7e47a4f262841956ecba7c9825279`. Source hashes and runtime are in `freeze.json`.
- Python **3.9.6**, macOS **26.6.2**, arm64. State lengths are characters, not estimated tokens; actual billed-input token counters are reported below.

## Usage and list-price estimate

Price source: [live TypeSafe model documentation](https://docs.typesafe.ai/models.md), retrieved during this study: USD **$0.042 per million input tokens**, output tokens free. This is a list-price multiplication of reported usage, **not an invoice** or a claim about credits/discounts.

| Context | Strategy | Input tokens | Output tokens | Estimated USD |
|---|---|---:|---:|---:|
| short | batch | 4,452 | 1,176 | $0.000186984 |
| short | serial | 18,165 | 1,239 | $0.000762930 |
| short | concurrency4 | 18,165 | 1,239 | $0.000762930 |
| long | batch | 12,636 | 1,176 | $0.000530712 |
| long | serial | 83,637 | 1,239 | $0.003512754 |
| long | concurrency4 | 83,637 | 1,239 | $0.003512754 |

**Total: 220,692 input tokens; 7,308 output tokens; $0.009269064 estimated.** Usage available for all 102/102 calls; zero unpriced failed/missing-usage calls.

## Interpretation and limits

Long/short median batch makespan was **1.083×** despite 8.533× as many state characters. Three repetitions are too few to estimate tails or establish a small context penalty reliably. No p95 is reported: **p95 on three repetitions is explicitly unstable**. All values and medians are preferred.

The 144 correct answers reuse the same eight answers across contexts/strategies/repetitions; they are correlated measurements, not 144 independent generalization tests. This is a bounded synthetic diagnostic, not a broad accuracy benchmark. Fixed question order, time-varying service load, unknown provider caching, one host/network, fresh connections, and process-isolation overhead limit generalization. There is no unmeasured claim that latency is purely model execution.

## Verification and artifacts

- Six offline tests passed before freeze/live calls (14.696 s): workload/oracle contract; seeded schedule/bounds; response parsing and failure denominators; worker scheduling/timeout/cap/expired budget; freeze tampering/private raw separation; standalone CLI help. RED failures were observed before each implementation slice.
- Post-run readback verified 102 distinct launch/completion IDs, 18 workloads, 144 returned question slots, pinned response model, caps, usage totals, and agreement with the pre-call freeze hash. All 102 call latencies were below 15 seconds.
- `study.py`, `run_study.py`, `test_study.py`, `jev_bench/`: standalone stdlib code, tests, and byte-identical vendored transport/parser.
- `plan.json`: original fixtures, gold labels, configuration, seed, and scheduled order. `freeze.json`: pre-call source/config digest receipt.
- `summary.json`, `summary.md`, `calls.csv`, `answers.csv`, `workloads.csv`: publishable derived results, including all timing values and explicit denominators.
- Private only (outside this candidate): `../private-raw/requests-responses.jsonl`, containing exact requests, parsed successful responses, timestamps, usage, and launch/completion/workload events. Directory mode 0700; file mode 0600.
- No shared-repository files were edited; no Git commits or pushes.
