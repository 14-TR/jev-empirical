# Evidence review: TypeSafe Jev

**Retrieved: 2026-09-20 UTC. Scope: a bounded first research pass, not a systematic literature review or an inference benchmark.**

## Bottom line

The public evidence supports **evaluating Jev as a typed decision component**, not assuming it is universally calibrated, semantically infallible, or cheaper than every competent alternative. Live documentation supplies a concrete API, versioned model, price, and admitted failure modes.[2][3][8]
Provider workflow results are comparisons with model-consensus reference decisions, not independent human ground truth.[10]
Third-party empirical reports and public prediction artifacts are discoverable, including useful qualifications and contrary results; this is not a situation in which “no independent evidence exists” is defensible from this search.[11][12][23]

This documentation pass did **not** send model inference requests. It read public sources and inspected archived third-party code/results. One archived classification result was counted from the author's saved predictions; that is an artifact consistency check, not a new Jev measurement or authenticated replication. Repository smoke experiments, if supplied elsewhere, must remain separately labeled and linked to actual receipts.

## 1. Search and provenance

Discovery began with the live TypeSafe documentation index and followed API, primitive, confidence, model, limitation, pattern, and cookbook links.[1]
The open-web queries were `TypeSafe Jev benchmark model pricing API independent evaluation` and `"Jev" "TypeSafe" calibration benchmark`. Follow-up acquisition traced original links from third-party coverage to event-validation, Norwegian-document, email-classification, and small classifier-suite sources. The pass prioritized primary reports and inspectable artifacts over launch summaries.

The companion [sources.json](sources.json) is a task-specific numbered citation ledger. It records retrieved URLs, access metadata, brief supporting excerpts, and, where available, source hashes and public repository revisions. Full downloaded pages, source snapshots, and cloned research repositories were kept outside this repository in private research storage. The ledger does not embed full articles, email corpora, credentials, or local filesystem locations. Discovery-only and blocked entries are not equivalent to reviewed full texts.

Evidence categories used here:

- **Documented contract:** what the provider currently says its service accepts/returns; not proof of live account availability.
- **Provider-reported measurement:** vendor-authored experiment, including its chosen harness and reference labels.
- **Third-party report:** an author outside the provider reports a run; independence of financial relationships and raw receipts is not assumed.
- **Artifact-inspected report:** code and/or predictions were available and statically examined; this still does not establish which live configuration generated them.
- **Local artifact check:** deterministic reaggregation of downloaded results, without inference.
- **Proposed study:** our prospective protocol, not an external finding or completed experiment.

## 2. Current API, model, price, and operational contract

| Topic | Live documented position | Audit implication |
|---|---|---|
| Endpoint | `POST https://api.typesafe.ai/v1/systemone`; bearer authentication; body with state, model, and questions.[3] | Test the direct API separately from gateway adapters; no authenticated request was made in this documentation pass. |
| Current version | Model page lists `jev-1.13.0`; `jev-latest` and `jev-preview` point to it at retrieval.[2] | Pin a version and record the response's model. Aliases can change. |
| Price | $42 per billion / $0.042 per million input tokens; output tokens free.[2] | A dated list price, not a verified bill or sustainability guarantee. |
| Capacity | 64k tokens across state and all questions; 32k for state plus the longest question.[2] | Neither a character limit nor evidence that accuracy is constant up to the limit. |
| Published limits | 250,000 tokens/second and 1,200 requests/minute, explicitly described as dynamic.[2] | Recheck before load tests; do not infer an SLA. |
| Input | Text represented as strings, JSON objects, or arrays; not image/audio/video input.[2] | OCR or transcription adds a separate error/cost component. |
| Model list | `GET /v1/models` is described as currently listing aliases; versioned IDs can be accepted without appearing there.[2] | Absence from the list is not sufficient to reject an explicitly documented version. |
| Response | One answer per question, model identifier, input/output usage; HTTP examples can report output tokens despite free output pricing.[3] | “Free output” must not be rewritten as “no output usage field.” |
| Retry behavior | SDK retry policy exposes attempt/backoff/status controls.[29] | Measure logical decisions and individual attempts; silent retries distort latency/failure comparisons. |

The direct model documentation says customer requests/responses are not used for training and points to legal documents and enterprise zero-data-retention arrangements.[2]
That is a provider representation, not a completed contractual, retention, or security audit. Do not send sensitive inputs on the strength of this research note.

## 3. What the primitives establish—and what they do not

**Choice:** selects from the specified answer set and supplies probabilities and confidence.[4]
It supports closed-set decisions, but the quality of that answer space is part of the system. Add no-match when the correct result can be absent; evaluate multi-label tasks as such rather than forcing one exclusive label.

**Noul:** supplies P(yes), with no separate confidence value.[5]
An ambiguous probability is not a medium-strength attribute. The relevant empirical checks are event calibration, discrimination, thresholded decision loss, and selective review.

**Score:** supplies a distribution over ordered levels and their probability-weighted index, on a rubric with two to ten levels.[6]
A fractional output is not evidence of accurate interpolation of an underlying numeric quantity. The provider separately warns about weak numerical calibration and numeric precision.[8]

**Confidence versus calibration:** the confidence guide defines the returned Choice/Score field from distribution shape, but the retrieved text does not give its exact mathematical formula.[7]
The System One concept page expressly says calibration is assessed across predictions, not a guarantee about one answer.[30]
Therefore we must test both event probabilities and whether concentration signals rank or calibrate errors. A high confidence threshold without held-out outcome evidence is not a measured safety policy.

## 4. Provider claims and their evidence boundaries

### Launch claims

The launch article advertises 70–500 ms end-to-end timing and headline advantages of 193.6x faster and 444.6x cheaper from its workflow evaluations, while describing those multipliers as near the high end of real-world gains.[9]
It also states that the published timings generally originate on the US West Coast, acknowledges uncertainty about pricing subsidy, and describes the plotted zero type-error figure as non-empirical.[9]

**Assessment:** these claims motivate measurement but do not supply our workload's latency, cost, calibration, or semantic error rate. Preserve schema conformance, successful transport, semantic correctness, and safe final action as different outcomes. No generated prose does not mean no wrong decisions.

### Public workflow dashboard

At retrieval, the overview displayed the following equal-weight averages over four workflows; the dashboard calls the first column accuracy, but its target is consensus-derived labels.[10]

| Dashboard label | Reported accuracy/agreement | Reported USD/case | Reported seconds/case |
|---|---:|---:|---:|
| Jev | 67.8% | $0.0004 | 0.4 |
| terra | 67.9% | $0.0304 | 10.1 |
| sol | 74.1% | $0.0836 | 23.3 |
| opus 5 | 73.1% | $0.1761 | 37.8 |

These are transcribed provider results, not newly computed comparisons. The reference is an average of GPT-6 Astra and Claude Fable 5.1 at high thinking, with other models using provider-default reasoning settings; the workflows are security incidents, agent-trace observability, invoice processing, and customer service.[10]
The launch post acknowledges vendor-authored workflows and says its LLM wrapper requires compatible structured decisions/probabilities, which can cost more than decisions alone.[9]

**Assessment:** model agreement and ground-truth correctness are different estimands. A shared compute graph controls one source of variability, but assuming the graph correct does not validate its business policy. Equal weighting across tasks also differs from case weighting or a deployment traffic mix. Default reasoning is not necessarily the best low-latency baseline. We did not reconstruct every case, authenticate billing, or independently verify each comparator's live availability.

### Cookbooks: examples rather than general benchmarks

- **Parallel questions:** reports 13 questions over a long document, five repeats per strategy, and 12.2x lower cost / 10.0x faster execution from batching; code pins `jev-1.12`.[15] The comparison's document reuse and sequential round trips matter; concurrent singles are a necessary additional control.
- **Reranking:** reports 40 CLERC queries and 30-passage shortlists, with top-1 moving from 5% to 18% and top-10 from 38% to 62%.[16] This is a small query collection and retrieval configuration, not a substitute for a specialist-reranker comparison or held-out replication.
- **Citation verification:** first matches a quote and then judges support in context.[17] This is a useful decomposition; its demonstration threshold is not a transferable operating point.
- **Candidate extraction:** regex candidates are selected and copied in code.[18] This constrains value provenance, but omitted candidates and wrong-field selections remain possible.
- **Cascade:** the page explicitly uses text-mode extraction rather than constrained-output LLMs and includes an illustrative hard-coded extraction failure.[21] Distinguish that illustrative failure from its separate aggregate experiment, and include stronger output-constrained baselines in a new study.

## 5. Third-party empirical evidence

### WotAI: ambiguous prose and classification

The report describes 150 passages from 35 posts and 16 models; Jev is reported at 66.0% accuracy, ECE 0.121, and median 455 ms, while Sonnet 5 has lower reported ECE (0.062) and higher accuracy (71.3%) but higher latency.[11]
Its additional business-category and commit-label tasks expose label ambiguity; its statement that no price was published is inconsistent with the currently retrieved model page.[11][2]

**Assessment:** encouraging measured latency, not universal calibration leadership. Passage clustering, uncertain gold, ECE specification, and threshold selection matter. The frequency of middling scores is not itself evidence that review catches more errors. Current price documentation supersedes this report for current list pricing; it does not retroactively establish the author's billed cost.

### Lindfors: Norwegian hearing documents

The report describes 24 documents and eleven questions per document, with model-generated reference labels, median Jev latency 0.32 s, and estimated $0.22 per 1,000 documents.[12]
The pinned result file reports Noul ECE 0.116 and Brier 0.086 for the careful wording, versus ECE 0.040 and Brier 0.089 for draft wording.[48]

**Assessment:** ECE and Brier can rank variants differently. These are agreement-with-reference results, not adjudicated Norwegian truth. Static code inspection shows argument-label bootstrapping pools labels within documents and the Choice threshold uses maximum class probability, not the provider confidence field.[49]
Reanalysis should cluster by document; a point estimate from this sample does not establish general multilingual calibration or stable tail latency. The author also identifies mixed routing providers for the LLM comparison.[12]

### Near Here: event validation

The report's 96% Jev result is 48/50 on cases used in prompt selection, not an untouched test; separate additional listings yielded Jev 19/21, Gemini 20/21, and Mistral 19/21.[23]
It reports Jev average latency 0.59 s and list-price-estimated $0.043 per 1,000 decisions, measured on that separate additional set, with high-reasoning/explanation-bearing LLM comparators.[23]

**Assessment:** the author carefully discloses selection, assistant-written expected labels, rejection-heavy samples, and the absence of independent blind administration. Do not combine the development accuracy and additional-set timing into a claim about one representative blind population. This motivates matched low-effort baselines and human label review, not a general accuracy advantage.

### Public email-classification repository

The current pinned README is broader than the early binary result repeated in coverage: it includes a later matched-evidence experiment and explicitly labels the research exploratory.[46]
The matched report gives 5,733 main messages, Jev text accuracy 93.62%, enriched-evidence accuracy 97.98%, and enriched logistic regression 98.87%; the baseline uses grouped folds and matching additional fields.[47]
The README also discloses label-informed specification development, unknown pretraining exposure, and a recent phishing-only set that cannot measure false positives.[46]

**Assessment:** upstream evidence availability is a load-bearing variable. It would be misleading to cite only “zero-shot near a trained classifier” without the unequal supervision and exploratory development context. A newer public repository report should qualify an older summary; neither establishes the performance of a general production spam filter. The original corpora and the full inference path were not rerun here.

### Small public classifier suite and archived result check

The pinned report covers eight tasks and 78 cases spanning Choice, Noul, and Score, with Jev hosted and the other models local; it reports Jev micro accuracy 0.974 and mean latency approximately 302 ms.[50]
A deterministic count of the downloaded Jev predictions found **78 cases, 76 marked correct, and zero recorded terminal errors**, matching the saved aggregate; no inference was performed.[53]
The adapter uses an OpenRouter decisions route and selects Score's most probable level where possible, rather than evaluating the expected Score itself.[51]
The shared harness computes accuracy on successful cases and excludes errored cases from that denominator.[52]

**Assessment:** useful inspectable micro-suite, not broad calibration evidence. Its deployment path is not a verified statement about today's direct API or gateway availability. Saved “correct” flags and model names are not independently authenticated receipts. Score discretization, output requirements, retry handling, and local-versus-network execution must be aligned before wider model claims. There were no terminal failures in the inspected Jev artifact, but the harness's exclusion rule would matter if they occurred.

### Secondary coverage and partial access

Arize summarizes several early experiments and says its own benchmarking remains forthcoming; treat that article as synthesis, not an additional independent run.[13]
The fetched Every article stopped at an account-creation wall before the detailed experiment; its introduction and metadata were visible.[24]
Its reported 777-judgment headline appears in secondary coverage, but this pass does not certify the inaccessible methods, denominator, concurrency, or accuracy behind it.[13]

## 6. Explicit known weaknesses worth testing

The provider's Jev 1.13 limitation page, marked reviewed 2026-09-17, lists literal reading, math/counting, date comparison, indirection, irrelevant context, adversarial content, contradictory instructions/criteria, non-guaranteed structural invariants, and lack of text generation.[8]
These are provider-described risk hypotheses, not measured prevalence estimates for our data.

The protocol therefore includes evidence removal, option permutations, independent paraphrases, distractor growth, injected instructions in source text, and composition failures. A guardrail built from the same model is another component to test, not an independent safety proof. The provider warning about missing invariants also means separately phrased complements and Noul-versus-Choice probabilities are not interchangeable.[8]

## 7. What remains unresolved

| Question | Evidence status | Next discriminating action |
|---|---|---|
| Does confidence predict error after conditioning on domain and class? | Documented concentration signal; scattered domain-specific reports, no universal validation | Held-out risk–coverage, error detection, and confidence-to-correctness calibration |
| Are native event probabilities well calibrated at an actionable operating point? | Mixed external evidence and small/clustered samples | Proper scoring rules, reliability intervals, raw/calibrated comparisons |
| Is Jev better value than a competent small classifier/reranker/low-effort LLM? | Depends on representation, labels, endpoint, and task | Matched-evidence and best-system comparisons with tuning budgets |
| Do batched questions retain quality and deliver end-to-end savings? | Provider cookbook and early outside use reports | Concurrent-single control, repeated pairs, whole-pipeline accounting |
| Does the service satisfy a workload's availability and tail-latency needs? | No SLA or local long-run reliability measurements established here | Authorized bounded load tests across time blocks and failure conditions |
| Is RLCD's architecture/training mechanism independently established? | Provider description; no decisive technical paper/independent mechanism audit retrieved in this pass | Broader literature/patent/implementation search if mechanism claims become necessary |
| Are public corpora absent from pretraining? | Unknown | Fresh controlled cases, contamination audits, and qualified generalization claims |
| Are training/retention/security assurances adequate for private data? | Provider statements only | Contractual/security review before private-input use |

Not retrieving a paper, independent replication, or guarantee in this bounded search is **not proof that none exists**. Publication, access, and model details can change. Search engines and accessible pages are a sampling process, not an exhaustive registry.

## 8. Recommended interpretation

Proceed with the broad protocol, prioritizing data and candidate/evidence audits before choosing an application. Keep the best conventional baseline viable. Require a measurable gain in final utility, validated review behavior, and operational budgets—not merely a typed response or an appealing speed ratio.

No deployment target, production threshold, or claim of superiority is established by this document. The next reliable milestone is a completed data/label audit and a frozen, affordable comparison design. Initial smoke receipts can establish that the harness runs; only later held-out evidence can establish that a particular workflow benefits.

## Sources

[1] https://docs.typesafe.ai/llms.txt — TypeSafe documentation index
[2] https://docs.typesafe.ai/models.md — Models
[3] https://docs.typesafe.ai/api.md — API reference
[4] https://docs.typesafe.ai/primitives/choice.md — Choice
[5] https://docs.typesafe.ai/primitives/noul.md — Noul
[6] https://docs.typesafe.ai/primitives/score.md — Score
[7] https://docs.typesafe.ai/confidence.md — Confidence
[8] https://docs.typesafe.ai/model-jaggedness/jev-1.13.md — Jev 1.13 jaggedness
[9] https://typesafe.ai/blog/introducing-system-one-models-and-jev — Introducing System One Models & Jev - TypeSafe AI Blog
[10] https://evals.typesafe.ai — Workflow evals
[11] https://wotai.co/blog/typesafe-jev-vs-claude-haiku-tested — TypeSafe Jev vs 15 other models, measured | WotAI
[12] https://lindfors.no/blog/a-first-look-at-typesafes-jev — An early-access test of TypeSafe's Jev: calibrated judgments for half a cent | lindfors.no
[13] https://arize.com/blog/typesafe-jev-llm-judge — TypeSafe Jev: Can Decision Models Replace LLM Judges? | Arize AI
[15] https://docs.typesafe.ai/cookbooks/parallel_questions.md — Parallel questions
[16] https://docs.typesafe.ai/cookbooks/rerank_typesafe.md — Re-ranking
[17] https://docs.typesafe.ai/cookbooks/citation_check.md — Double-checking citations
[18] https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md — Pre-parsed value extraction
[21] https://docs.typesafe.ai/cookbooks/sde_cascade.md — SDE cascade
[23] https://nearhere.events/blog/typesafe-jev-mistral-gemini-event-validation — TypeSafe Jev vs Mistral vs Gemini: Event Validation Test | Near Here
[24] https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds — Mini-Vibe Check: TypeSafe's Jev Judged Everything I’ve Written in 0.7 Seconds
[29] https://docs.typesafe.ai/sdk/python/api/retries.md — Retries
[30] https://docs.typesafe.ai/concepts/system-one.md — System One
[46] https://github.com/bitnovus/jev-spam-eval/blob/a3757a1b3412177a686c1b4d95227b50a8f73537/README.md — Zero-shot email classification with TypeSafe’s Jev
[47] https://github.com/bitnovus/jev-spam-eval/blob/a3757a1b3412177a686c1b4d95227b50a8f73537/experiments/jev-context/REGRESSION_REPORT.md — Matched-evidence comparison: Jev versus logistic regression
[48] https://github.com/EmilLindfors/jev-horingssvar-eval/blob/ec97e2d7dc17ed035bf4a96365dfec9c360659a4/results/quick_eval_2026-09-18.txt — reference: 24 docs in A, 24 in B
[49] https://github.com/EmilLindfors/jev-horingssvar-eval/blob/ec97e2d7dc17ed035bf4a96365dfec9c360659a4/analysis/metrics.py — norwegian-metrics
[50] https://github.com/jabr/classifier-benchmark/blob/91741e63c69017daeb2c775cdcd681c588280955/results/benchmark-summary.md — Head-to-head: Von (wfzyx/von-1.0) vs GLiNER2 (fastino/gliner2-large-v1) vs Jev (typesafe/jev-1.13)
[51] https://github.com/jabr/classifier-benchmark/blob/91741e63c69017daeb2c775cdcd681c588280955/bench/backends/jev.py — classifier-adapter
[52] https://github.com/jabr/classifier-benchmark/blob/91741e63c69017daeb2c775cdcd681c588280955/bench/run.py — classifier-harness
[53] https://github.com/jabr/classifier-benchmark/blob/91741e63c69017daeb2c775cdcd681c588280955/results/jev.json — Archived Jev classifier predictions, pinned revision
