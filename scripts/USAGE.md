# Running the harness (Python 3.9+, stdlib at runtime)

Run from the repository root. No package installation is required:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m jev_bench --help
PYTHONPATH=src python3 -m jev_bench live --help
```

## No-network deterministic baseline

Both directories must be new. Raw directories are private (0700) with 0600
receipts, and must resolve outside this source tree and every Git repository.
Do not put raw outputs in a synced/public directory.

```sh
PYTHONPATH=src python3 -m jev_bench baseline   --dataset datasets/synthetic_diagnostics.json   --raw-dir "$HOME/jev-private/baseline-01"   --export-dir "$HOME/jev-private/baseline-01-export"
```

The baseline emits uniform probabilities and deterministic argmax ties. It does
not use gold labels, semantic rules, an API, or a language model. Baseline latency
is a zero placeholder and must not be compared to live network latency.

## Explicit opt-in paid live run (parent/operator only)

Independently review the code and dataset before making calls. Supply
`TYPESAFE_API_KEY` using your environment's secret-management facility. There is
no key argument, config file, dotenv loader, default model, or endpoint override.
Do not paste keys into terminal command lines, reports, screenshots, or commits.

The current versioned ID observed in the official docs was `jev-1.13.0`; recheck
https://docs.typesafe.ai/models before running. This command is bounded to 101
POST attempts, a 300-second request window, and 15 seconds per request. No retry,
redirect following, or proxy environment support. TLS validation is enabled.

```sh
PYTHONPATH=src python3 -m jev_bench live   --dataset datasets/synthetic_diagnostics.json   --model jev-1.13.0   --max-requests 101 --max-seconds 300 --request-timeout 15   --raw-dir "$HOME/jev-private/jev-1.13.0-01"   --export-dir "$HOME/jev-private/jev-1.13.0-01-export"
```

Each case is a separate serial request with one question. The process deadline
covers DNS, TLS, and response reading; terminating/reaping the worker adds up to
0.2 seconds, plus OS scheduling/startup and local receipt/report I/O. The total
request window stops new calls; it is not a real-time bound on disk I/O or Python
process startup. Maximum accepted settings are 1000 requests, 900 seconds total,
and 120 seconds per call; response bodies are capped at 1 MiB, requests at 64 KiB.
New calls require at least 0.001 seconds remaining; a positive submillisecond
remainder is `budget_exhausted`, with no transport attempt.
These byte limits are not tokenizer-based cost estimates. Budget exhaustion,
transport errors, non-200 statuses, and invalid response shapes remain in the
failure denominator. No HTTP error bodies or exception details are retained.
A successful response echoing the current credential is discarded.
Nonfinite JSON numbers (including exponent overflow in unknown nested fields),
out-of-range answer numbers, and unserializable responses are `invalid_response`.

Private receipts retain at most **8 MiB in aggregate** of successful response
objects, measured as compact UTF-8 JSON. Unknown API extras count toward this
budget and are preserved in accepted private response records, not silently
stripped. A response that would exceed the remaining aggregate budget is counted
as `response_too_large`; its body is discarded, but its case, request hash,
latency, and failure status remain. Later smaller responses can still fit.
Every case remains in the denominator, and size-rejected calls may be billed.
The 1000-case bound plus this response budget leaves room for receipt metadata
under the 32,000,000-byte writer/replay limit. Replay reads at most that limit
plus one byte, not the whole file before checking; parsed objects add bounded
Python allocation overhead beyond the serialized byte budget.

Exit codes: 0 all cases successful; 3 report written with failures; 2 validation
or path/configuration failure; 130 interrupted. An interruption leaves a private
partial checkpoint, which replay rejects rather than silently dropping cases.

## Replay and public export

```sh
PYTHONPATH=src python3 -m jev_bench replay   --dataset datasets/synthetic_diagnostics.json   --receipt "$HOME/jev-private/jev-1.13.0-01/receipt.json"   --export-dir "$HOME/jev-private/jev-1.13.0-01-replay"
```

Replay validates the exact case count/order, dataset digest, request digests,
response types, complete finite probability distributions, selected choices,
Score legends/expectations, model identity, and failure fields. It accepts only
receipt schema v2, including validated `started_at_utc` and `completed_at_utc`
timestamps (`YYYY-MM-DDTHH:MM:SS.ffffffZ`); older v1 receipts are not accepted.
Partial checkpoints have no completion timestamp and cannot replay. Timestamps
are local wall-clock observations, may reflect clock adjustments, and do not
replace monotonic request deadlines. Replay does not contact the service. Receipts
are local records, not signed attestations that cannot be forged.

Only `report.json` and `report.md` are designed for publication. They are built
from an explicit allowlist of version/dataset/code hashes, modes/model IDs,
fixed task/family names, numeric summaries, fixed failure codes, and methodology
notes. No case texts, instructions, per-case records, full probability vectors,
arbitrary API fields, headers, credentials, or error bodies are copied.
Risk/coverage thresholds are exact observed top-class probabilities; sparse
strata may reveal individual outcomes by differencing. Reassess small-cell
publication before any private-data extension. Review even these reports
before publication. Do not publish `receipt.json` or raw output directories.

## Metric conventions and remaining gaps

- Accuracy reports both successful-only and all-case denominators (failures count
  incorrect); no imputed probabilities for failed cases.
- Brier is the multiclass sum, including two-class Noul; log loss uses natural
  logs with a declared `1e-15` floor. Both metrics average successful cases.
- Noul is probability of yes, not intensity or a separate confidence statistic.
- Ordinal accuracy uses the modal level; expected-score MAE uses the weighted
  index. These are different decisions, not a rounded API score.
- Ten equal-width descriptive bins and tie-aware risk/coverage use top-class
  probability, not provider confidence. Provider confidence is summarized
  separately and its unpublished computation is not reverse-engineered.
- Probability sums must be within `1e-6` of one; Score expectation within `1e-5`.
  No renormalization or silent field coercion is performed.
- Pooled metrics mix task cardinalities and class balances; use per-task results.
  Paired families are highly correlated. No fitted calibrator, ECE claim,
  confidence intervals, hypothesis test, bootstrap, or deployed threshold tuning.
- Latency includes client worker startup/HTTPS overhead and failures; linear
  interpolation gives p50/p95/p99. No warm-up removal or throughput measurement.
- Usage totals include only successful calls with supplied counters. Failed calls
  may still be billed. There is no billing reconciliation or cost ceiling beyond
  request/time/size bounds.
- No batching comparison, concurrency, resumption, retry, external benchmark,
  independent human-label audit, or non-Jev comparator besides uniform baseline.
