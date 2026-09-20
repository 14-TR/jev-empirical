# Limitations, validity threats, and release boundaries

**Applies to the evidence snapshot collected 2026-09-20 UTC and the prospective protocol draft.**

Read alongside [protocol.md](protocol.md) and [evidence-review.md](evidence-review.md). This is a research package, not an endorsement, production certification, or assertion that all proposed experiments have run.

## 1. What has and has not been established

This documentation pass retrieved live public material, inspected selected public code/results at pinned revisions, and checked the count of an archived prediction file. It made no new Jev or comparator inference calls and did not authenticate the generation of third-party artifacts. A cited author result remains that author's result, even when its arithmetic can be checked locally.

Any initial smoke experiments in the repository are **descriptive**. Their calls can establish that an endpoint and harness worked for those inputs at that time. They cannot establish representative accuracy, robust calibration, rare-error risk, p99 latency, or superiority over a baseline. No number should enter a result table without a real receipt or an explicitly attributed external source.

The future protocol is a **draft for preregistration**, not an already completed preregistration. Dataset selection, sample sizes, practical margins, operating thresholds, and spend limits must be frozen before confirmatory test access. Exploratory prompt/criteria editing cannot be retroactively relabeled preregistered.

## 2. Interface guarantees are not truth guarantees

The launch article describes its plotted zero type-error figure as non-empirical and grounded in schema matching.[9]
That claim does not establish zero transport errors, complete service availability, correct labels, valid source interpretation, adequate candidate coverage, or safe final actions. A syntactically valid wrong answer can still cause harm. Validate runtime responses and enforce authorization and deterministic business constraints independently of the model.

The model is documented as text-only; images, audio, and video require an upstream textual representation.[2]
Extraction, OCR, transcription, truncation, source acquisition, and normalization can dominate the resulting error rate. Report those failures separately from model judgment, then include them again in end-to-end outcomes.

## 3. Calibration and confidence are distribution-dependent

The provider confidence statistic is derived from Choice/Score probability concentration; its exact formula was not specified in the retrieved confidence guide.[7]
It must not be interpreted as a calibrated probability that the entire workflow is correct. Native class/event probabilities and a fitted correctness predictor are different objects. The provider also explicitly describes calibration as a group-level property rather than an individual guarantee.[30]

Calibration depends on the evaluated population, label definition, prevalence, question wording, candidate set, and model version. A pooled reliability diagram can hide poor calibration in a consequential minority stratum. ECE is sensitive to bins and sample composition; it is not a standalone proof of useful uncertainty. Report proper scoring rules, discrimination, bin support, and selective risk together. Refit or revalidate after material changes instead of transferring one threshold across domains or primitives.

Score is an expected rubric index, not a measurement in physical units.[6]
An average can conceal a bimodal distribution; arbitrary spacing between verbal levels is a modeling choice. Evaluate severe under/over-estimation and downstream action errors, not only average distance. No exact numeric reconstruction should be inferred from fractional outputs.

## 4. External evidence is informative but heterogeneous

The vendor dashboard uses model-consensus references and equal-weight workflow averages.[10]
It does not directly answer how often actions are correct under independently adjudicated business policy. Model agreement can inherit shared biases; two references do not become truth by averaging. Do not pool those scores with human-labeled accuracy.

Independent reports use different outputs, settings, baselines, timing boundaries, samples, and reference labels. Near Here's primary development cases influenced prompt selection, and its separately reported additional set is small and narrow.[23]
Lindfors's study uses model-generated reference labels, while its metrics code pools multiple argument judgments within each document for bootstrapping.[12][49]
The small classifier adapter converts Score to a discrete most-probable level, unlike the Norwegian script's rounded expected Score.[51][49]
These are different estimands, not directly comparable Score-accuracy measurements.

The public email study explicitly acknowledges labeled feedback during specification development and unknown pretraining exposure.[46]
“Zero-shot inference” does not mean no prior supervision, no label-informed engineering, or equal development budgets. Matched inputs do not imply matched training information. Baselines should be competent without pretending every supervision regime is identical.

## 5. Sampling, labels, and uncertainty

No single public benchmark represents every intended application. Published corpora may contain duplicates, stale facts, annotation artifacts, and source/label confounding. A later document is not necessarily novel to a hosted model. Public questions and published test examples may also contaminate future evaluations; maintain fresh held-out groups.

Cases, questions, repeated calls, paraphrases, and perturbations are not interchangeable sample units. Resampling thousands of judgments from a few documents as independent can give misleadingly narrow intervals. Use source-level clusters and report both numbers. Repetition estimates variability on known cases, not coverage of the population.

Small samples are particularly weak for rare consequential errors, calibration bins, and tail latency. Zero observed errors is not zero underlying risk. Ordinary bootstrap intervals can collapse at a boundary, so use an appropriate non-degenerate bound where assumptions permit. Statistical non-significance does not establish equivalence or non-inferiority.

Human annotations also have uncertainty. Preserve adjudication disagreements and ambiguous/insufficient-evidence labels. Gold labels written after viewing predictions, selecting only favorable error examples, or using the same LLM as both generator and judge all threaten validity. If a label revision is necessary, apply it blindly and consistently to all systems and retain a deviation record.

Broad sweeps create multiplicity and selection risk. Choosing a task, model, prompt, threshold, calibration method, binning, or reported subgroup after looking at results is adaptation. Report that development history. Use fresh tests or appropriate nested procedures rather than polishing a headline from a reused test set.

## 6. Composition and evidence boundaries

The provider documents known weaknesses involving literal wording, numbers/dates, indirection, irrelevant context, adversarial state, contradictory criteria, and unguaranteed structural invariants.[8]
Those warnings justify stress tests but do not establish the frequency of failures in a target domain. Equally, a successful synthetic stress test does not prove real-world immunity.

Candidate extraction has a hard dependency on candidate coverage. Ranking has a hard dependency on retrieval coverage. Verification can assess entailment only from supplied evidence; it cannot establish that the source itself is truthful, current, or authoritative. A missing quote may be an acquisition failure, formatting discrepancy, or OCR error rather than fabrication.

Independent evaluation of questions within a request is not statistical independence of their errors. Correlated failures can survive voting, redundant checks, and cascades. Review the whole decision graph, test the final action, and validate fallback quality. A serious violation should not be offset by high scores on unrelated preferences.

## 7. Operational and economic uncertainty

The live model page's price and limits are a dated provider statement; rate limits are explicitly dynamic.[2]
Actual cost depends on provider tokenization, input length, question count, retries, retrieval, candidate generation, caching, fallback, and human review. List-price estimates are not invoices. Output usage and output billing are distinct fields. Unknown costs must remain unknown rather than silently becoming zero.

Timing depends on client region, provider routing, connection reuse, concurrency, queueing, payload size, retries, and the measurement boundary. A single hosted-provider median versus a local-model runtime is not a hardware-efficiency experiment. Measure useful throughput and deadline completion as well as successful-request latency. Never erase outages and timeouts from an operational result.

Model pinning improves reproducibility but does not prove immutable infrastructure, sampling implementation, or service conditions. Record returned identifiers and time blocks. Neither access to a model catalog nor a successful prior smoke request guarantees later account access, capacity, or availability.

## 8. Privacy, safety, and redistribution

Keep downloaded full sources and restricted datasets in private storage outside the repository. Public artifacts should contain curated analysis, citations, minimal permitted excerpts, hashes, and redacted receipts. Do not publish keys, headers, cookies, private prompts, raw account data, private hostnames, or absolute local paths. Scrub error bodies as well as successful responses.

The provider's no-training and enterprise retention statements are not a substitute for reviewing applicable terms, privacy policy, subprocessors, retention, and account-specific agreements.[2]
Do not send private data or run high-volume stress tests until scope and spend are authorized. Dataset/code licenses are separate, and a public source is not automatically licensed for wholesale redistribution.

Injection tests must use controlled untrusted text, dummy identities, and a non-acting harness. Do not connect test outputs to payments, account changes, external messages, or destructive actions. This study does not certify medical, legal, financial, security, employment, or other high-impact autonomous decision making.

## 9. Research-access and coverage gaps

The search was time-bounded and English-query dominated. It was not exhaustive across academic indexes, social platforms, private communities, incident reports, or non-English sources. Third-party affiliations and receipt authenticity were not comprehensively audited. Search results can omit contrary or newer evidence; repeated coverage of one experiment is not independent corroboration.

The detailed Every article was account-gated in the fetched page.[24]
The attempted BEIR paper page returned a challenge rather than the paper; its public repository was available and used only as a dataset/framework lead.[33]
The calibration and dataset paper landing pages support the limited descriptions in this package, not a claim of full-paper methodological review.[25][26][27]
No decisive independent mechanism audit of RLCD was retrieved. That is a statement about this pass, not proof that none exists.

## 10. Release language and hard stop rules

Acceptable: “This exploratory run observed…”, “The provider reports…”, “The author artifact contains…”, “At the frozen operating point, the held-out interval was…”.

Not acceptable without additional evidence: “cannot hallucinate” as semantic infallibility; “calibrated confidence” as a universal safety guarantee; “production-ready”; “preregistered” for a mutable retrospective plan; “free” for an uncosted local system; “no independent evidence exists”; or a generalized speed/price multiplier detached from its comparator and workload.

Stop publication of a result if receipts are missing, source attribution is ambiguous, private content remains, dataset rights are unresolved, or an analysis denominator disagrees with its actual records. Stop a confirmatory run for leakage, unapproved inputs, breached spend limits, unresolved schema/model drift, or an unsafe harness. Safety/budget stopping does not turn an incomplete run into a passing benchmark.

The deliverable at this stage is a source-grounded research design and evidence audit. Application targeting, new model measurements, formal preregistration, and deployment approval remain separate decisions.

## Sources

[2] https://docs.typesafe.ai/models.md — Models
[6] https://docs.typesafe.ai/primitives/score.md — Score
[7] https://docs.typesafe.ai/confidence.md — Confidence
[8] https://docs.typesafe.ai/model-jaggedness/jev-1.13.md — Jev 1.13 jaggedness
[9] https://typesafe.ai/blog/introducing-system-one-models-and-jev — Introducing System One Models & Jev - TypeSafe AI Blog
[10] https://evals.typesafe.ai — Workflow evals
[12] https://lindfors.no/blog/a-first-look-at-typesafes-jev — An early-access test of TypeSafe's Jev: calibrated judgments for half a cent | lindfors.no
[23] https://nearhere.events/blog/typesafe-jev-mistral-gemini-event-validation — TypeSafe Jev vs Mistral vs Gemini: Event Validation Test | Near Here
[24] https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds — Mini-Vibe Check: TypeSafe's Jev Judged Everything I’ve Written in 0.7 Seconds
[25] https://proceedings.mlr.press/v70/guo17a.html — On Calibration of Modern Neural Networks
[26] https://aclanthology.org/2020.nlp4convai-1.5 — Efficient Intent Detection with Dual Sentence Encoders - ACL Anthology
[27] https://aclanthology.org/N18-1074 — FEVER: a Large-scale Dataset for Fact Extraction and VERification - ACL Anthology
[30] https://docs.typesafe.ai/concepts/system-one.md — System One
[33] https://raw.githubusercontent.com/beir-cellar/beir/main/README.md — <h1 align="center">
[46] https://github.com/bitnovus/jev-spam-eval/blob/a3757a1b3412177a686c1b4d95227b50a8f73537/README.md — Zero-shot email classification with TypeSafe’s Jev
[49] https://github.com/EmilLindfors/jev-horingssvar-eval/blob/ec97e2d7dc17ed035bf4a96365dfec9c360659a4/analysis/metrics.py — norwegian-metrics
[51] https://github.com/jabr/classifier-benchmark/blob/91741e63c69017daeb2c775cdcd681c588280955/bench/backends/jev.py — classifier-adapter
