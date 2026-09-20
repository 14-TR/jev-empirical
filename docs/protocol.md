# Broad empirical evaluation protocol for TypeSafe Jev

**Status: prospective protocol draft, not a completed preregistration.**
**Evidence snapshot: 2026-09-20 UTC.**

This document defines a broad evaluation program before choosing a product target. It is not a claim that Jev has passed the program. The documentation research pass made no model inference calls. Any initial repository smoke runs belong to a separate, descriptive evidence tier and must be supported by their own receipts. See [evidence-review.md](evidence-review.md) for external findings and [limitations.md](limitations.md) for interpretation boundaries.

All choices stated as “require,” “measure,” or “freeze” below are proposed rules for this study, not claims about completed experiments. A confirmatory run is blocked until its registration record is complete. Publishing this draft alone does not turn exploratory work into preregistered evidence.

## 1. Questions and evidence tiers

The main question is **where typed probabilistic judgments improve a complete system relative to the simplest competent alternative, at acceptable error, review burden, latency, and cost**. There need not be one winner across domains.

Keep four evidence tiers separate:

| Tier | Permitted conclusion | Not permitted |
|---|---|---|
| Contract and offline checks | The adapter and metric implementation pass specified tests | The hosted model is accurate, available, or calibrated |
| Descriptive smoke experiment | These recorded requests produced these answers and timings | Population accuracy, reliable tail latency, deployment safety, or benchmark superiority |
| Exploratory development/pilot | These observations suggest hypotheses and reveal failure modes | Confirmatory significance after selecting prompts, thresholds, or cases on the same observations |
| Frozen confirmatory evaluation | A prespecified contrast on a declared population and held-out sample, with uncertainty | Generalization outside its data, versions, endpoint, budgets, or decision policy |

A smoke suite should include all three primitives, a multi-question call, a known negative/no-match case, a missing-evidence case, and a safe service-failure path. Its purpose is to verify contracts, response capture, billing fields, and metric plumbing. Use synthetic, public, or specifically approved inputs. Exclude smoke examples and their semantic near-duplicates from the later confirmatory test. Never promote a hand-selected demo into that test retrospectively.

## 2. Current contract to pin, not assume

The live model page lists `jev-1.13.0`, with `jev-latest` and `jev-preview` both resolving to that version at retrieval; it describes a $0.042-per-million-input-token price, free output, a 64k aggregate request budget, and a 32k budget for state plus the longest question.[2]
The HTTP interface is `POST https://api.typesafe.ai/v1/systemone`, accepting `state`, `model`, and keyed `questions`, and returning `answers`, `model`, and token `usage`; question identifiers are not used in inference.[3]

Record requested and returned model identifiers separately. Request an explicit version for confirmatory runs; reject or partition unexpected resolutions. Read live limits and prices again at execution time. Do not assume a model-list alias, SDK example, gateway name, and returned immutable identifier are interchangeable. Version the SDK, adapter, question schema, serializer, retry policy, input truncation, and model-access route.

| Primitive | Documented semantics | Required evaluation treatment |
|---|---|---|
| Choice | One selected option plus a distribution over supplied alternatives and a concentration-derived confidence field.[4][7] | Preserve complete distribution, option meanings/order, returned label, and explicit no-match outcome where appropriate. Do not silently substitute argmax when rounded probabilities tie. |
| Noul | A probability of yes, without a separate confidence field; a value near 0.5 is not medium intensity.[5] | Evaluate probability against the binary event; separately evaluate the thresholded policy. Use one event per independently applicable label. |
| Score | Ordered descriptions, two to ten levels, indexed from zero; the score is the probability-weighted index and may be fractional.[6] | Preserve level distribution and legend, not just a rounded class. Ordinal position is not a physical quantity or automatically an interval scale. |

Validate response completeness, finite values, bounds, distribution key coverage, and normalization with a preregistered floating-point tolerance. Log the raw values before any normalization. If normalization is needed for a secondary analysis, disclose its rule and frequency. Test Score expectation consistency and the HTTP-string/SDK-integer key conversion explicitly. A returned typed value may still be semantically wrong.

## 3. Portfolio: evaluate broadly before selecting a target

Run separate task tracks rather than averaging incompatible outputs into a single “Jev score.” Include ordinary cases, rare consequential negatives, ambiguous/insufficient-evidence cases, and realistic distractors. A track can be deferred if adequate labels or lawful data are unavailable; mark it untested, not passed.

### A. Intent routing and bounded action selection

**Unit:** a request plus the relevant policy and account/application state. **Gold:** the permitted handler, any necessary typed arguments, and whether review is required.

Evaluate flat Choice routing, hierarchical routing for larger catalogs, and a Noul presence/relevance gate followed by Choice. Include overlapping intents, multiple simultaneous intents, no supported handler, and correct intent with missing mandatory arguments. Hold action permissions in code; “user wants a transfer” is not authorization to transfer.

Report macro-F1, class-wise precision/recall, no-match performance, and cost-weighted routing loss. For the full system report correct handler **and** correct arguments, unauthorized-action proposals, automatic coverage, fallback load, and final resolved outcomes. An always-review route is a valid safety comparator but not a free success: charge its latency and review cost. The provider's confidence-routing cookbook is a design example, not validation of its example thresholds.[20]

**Competent comparators:** explicit rules for exact policy fields; word/character TF-IDF plus logistic regression with held-out tuning; an embedding classifier; a low-latency structured-output LLM; a stronger structured-output LLM as a quality reference. Do not make a reasoning-heavy chatbot the only baseline.

### B. Evidence and citation verification

**Unit:** an atomic claim, an identified source/version, retrieved evidence, and any quoted span. **Gold:** supported, contradicted, insufficient evidence, or evidence unavailable, with adjudicated supporting spans.

Separate three components: source acquisition and identity; deterministic quote/span matching; semantic entailment. The citation cookbook likewise distinguishes a matching quotation from whether its context supports the claim.[17]
A string match does not establish entailment. Conversely, a retrieval failure or OCR mismatch is not sufficient to label a claim fabricated. Missing evidence is not automatically evidence of falsity. Define treatment of hedging, quantities, negation, temporal scope, tables, and multi-part claims before scoring.

Test oracle evidence and real retrieval separately. Include accurate quotes used misleadingly, correct facts attributed to the wrong source, stale versions, conflicting sources, and claims requiring several passages. Measure unsupported-claim acceptance, contradiction detection, evidence-availability detection, macro-F1, binary-event Brier/log loss, and human-review yield. Score claim-level correctness separately from document-level “all material claims supported.”

**Comparators:** exact/normalized quote checking; lexical matching; a competent NLI/cross-encoder verifier; small and stronger structured-output LLMs using the same supplied evidence. Exact matching alone is not a competent semantic verifier, but is an important component ablation.

### C. Ranking and retrieval

**Unit:** a query and fixed candidate set with adjudicated graded relevance. **Gold:** relevance judgments and acceptable alternatives, not simply another model's ordering.

Compare BM25 and dense retrieval alone; specialist reranking; per-candidate Noul relevance; comparable per-candidate Score rubrics; and, separately, Choice over a fixed shortlist. Choice probabilities compete within a list and should not be treated as cross-list absolute relevance. The provider's re-ranking cookbook is a small shortlist experiment, not a general search leaderboard.[16]

Report first-stage recall@k, nDCG@k, MRR when appropriate, recall@k, and top-result relevance. Freeze gain mapping, k, tie-breaking, and treatment of no-relevant-document queries. If normalized ranking metrics are undefined for an empty relevance set, report that stratum separately rather than assigning a favorable score. Include query-level intervals and latency/cost for retrieval **plus** reranking. Keep the shortlist identical for model-only comparisons; also evaluate separately optimized end-to-end systems.

Test candidate-order effects, duplicates, distractor additions, near-ties, and pairwise cycles. Pairwise ranking must disclose comparison budget and aggregation algorithm. Retrieve more candidates before blaming a ranker that never received a relevant item.

### D. Candidate-based extraction

**Unit:** a source, requested field, and generated candidate spans. **Gold:** source span(s), normalized value, field meaning, and explicit absent/ambiguous states.

Evaluate candidate generation, selection, and normalization independently and end to end. The provider's extraction recipe finds candidates with regexes, selects one, and copies/normalizes it in code.[18]
Report candidate recall, selection accuracy conditional on gold availability, span exact match, normalized-value accuracy, wrong-field selection, absent-value false fills, and total end-to-end accuracy. If equivalent values occur at different offsets, preserve span identity and provenance rather than deduplicating away the distinction.

Compare real candidates with oracle candidates to locate the bottleneck. Deliberately remove the correct candidate; include plausible but incorrect alternatives and no-match. The model cannot select an omitted value. Code should perform number parsing, currency normalization, date validation, and exact arithmetic. Jev's own limitations page warns against relying on numeric precision and date comparison.[8]

**Comparators:** deterministic parsers and context rules; a span/NER model where suitable; a structured-output LLM; an LLM candidate generator followed by Jev selection. Charge upstream generation to the combined system.

### E. Composition, verification cascades, and reusable features

**Unit:** a whole workflow with a versioned decision graph and external outcome. **Gold:** both intermediate judgments where labelable and the resulting action/loss.

Compare a single holistic judgment; decomposed independent judgments plus code; a sequential dependency-aware graph; batched speculative fan-out; and a selective escalation cascade. Score weighted preferences separately from hard constraints: a high convenience score must not compensate for a serious violation. The composite-scoring pattern combines dimension scores in code; its weights are a product policy, not learned proof of validity.[19]

Use component-oracle substitutions: gold candidates, gold intermediate labels, oracle retrieval, or a fixed fallback. These identify whether input preparation, model judgment, composition, or execution dominates errors. Measure pipeline error rate, coverage, residual critical errors, escalation precision/recall, fallback success, full cost, and wall time. Validate new fallback answers too; escalation is not an oracle.

For probability composition, do not multiply marginal probabilities as if independently evaluated questions imply independent events or independent errors. Test final workflow outcomes directly. Report correlated failures and errors on the subset selected for escalation. For learned downstream features, keep feature discovery, model fitting, calibration, and test evaluation in distinct partitions.

The parallel-questions cookbook reports a document-heavy batching advantage against sequential calls; compare batching with both sequential and concurrent single-question requests, rather than using the weakest execution policy as the only control.[15]
The extraction-cascade cookbook explicitly uses text-mode LLM extraction; include competent constrained-output baselines and separate its illustrative example from aggregate experiments when designing our own comparisons.[21]

## 4. Data, labels, and leakage controls

### Candidate public resources, not a frozen dataset selection

Banking77's paper describes a fine-grained intent dataset; it is a possible routing track, not a substitute for open-set or operational routing cases.[26]
FEVER provides claim-verification labels and evidence, making it a possible controlled verification track.[27]
BEIR offers diverse retrieval tasks and an evaluation framework, making it a possible ranking track.[33]
These are discovery leads. Audit dataset versions, licenses, label definitions, splits, and contamination risk before use; this pass did not complete those dataset audits. No downloaded benchmark corpus is authorized for redistribution merely because its paper is public.

### Required partitioning

1. Establish a population and sampling frame before viewing model performance. Document exclusions and natural class prevalence.
2. Group by source document, entity, thread, template, author, or near-duplicate cluster, as appropriate. Keep all paraphrases, transformations, and repeated calls for one source in one partition.
3. Separate development, calibration/threshold validation, and locked test groups. If labels are scarce, use nested group-aware cross-validation for exploration; do not repeatedly consult a nominal test set.
4. Add an independently sampled temporal/domain-shift set when deployment generalization is a goal. A later public document is not known to be absent from pretraining.
5. Freeze raw-data hashes, transformation versions, candidate lists, gold-label version, split assignments, and sampling seeds. Keep restricted full sources private; publish lawful curated examples or identifiers and acquisition instructions.
6. Check exact and semantic duplicates, inverse/reworded questions, direct-answer metadata, class-correlated source channels, leaked intent prefixes, candidate names, and annotation artifacts.
7. Record how many labeled examples influenced prompt writing, criteria, thresholding, or feature discovery. “No weight updates” and “no labeled examples in requests” do not mean development without supervision.

### Label quality

Write a label guide first. Blind annotators to provider identity, outputs, confidence, and each other's judgments. Use at least two independent judgments on all consequential test cases and an adjudication procedure; record disagreements rather than erasing ambiguity. Budget this work before inference. Represent multiple acceptable answers or a distribution over adjudicated labels when the task genuinely supports them, with a prespecified scoring rule.

Model-generated labels are permissible for a separate agreement experiment. They must not be renamed human truth; two passes from the same model are not independent adjudication. Re-labeling after seeing errors requires a logged, provider-blind review applied across all systems. Retain both original and revised analyses when revisions affect a conclusion.

## 5. Calibration is not concentration

The API confidence field is described as a statistic of the Choice/Score probability distribution; the retrieved page does not specify its exact formula.[7]
The broader System One docs explicitly describe calibration as a property across predictions, not an individual correctness guarantee.[30]
Calibration research also treats probability quality as distinct from classification accuracy and studies held-out post-processing such as temperature scaling.[25]

Use three separate concepts:

- **Event probabilities:** Noul P(yes), Choice class probabilities, or Score level probabilities.
- **Concentration/sharpness:** maximum probability, margin, entropy, and the provider's `confidence`. These describe a distribution or provide a ranking signal, not automatically a calibrated P(correct).
- **Decision utility:** the observed loss and coverage of a particular threshold/fallback policy.

Required analyses:

| Output | Primary probability assessment | Secondary diagnostics |
|---|---|---|
| Noul | Brier score `mean((p-y)^2)` and log loss | Reliability diagram, fixed-bin ECE, AUROC, AUPRC, class prevalence, threshold-specific errors |
| Choice | Multiclass log loss and Brier score | Top-label and classwise calibration, confusion matrix, macro-F1, error detection using confidence versus max-probability/margin/entropy |
| Score | Ordinal ranked probability score and level probabilities | MAE of expected index with the scale assumption stated; argmax-level accuracy, adjacent-level errors, severe under/over-rating |
| Workflow | Observed action loss and risk–coverage curve | Critical-error bounds, review load, calibration on accepted/escalated subsets, fallback outcomes |

Freeze Brier normalization (summed or class-averaged), log-loss clipping, and ECE bins in the analysis plan. Proposed defaults: summed multiclass Brier, log clipping at `1e-12`, and ten equal-width ECE bins, plus a declared equal-count sensitivity analysis. Report bin counts and confidence intervals; sparse bins are inconclusive. Do not choose bins after looking for the prettiest diagram. A constant prevalence predictor and a uniform multiclass predictor are essential probability baselines: low calibration error alone need not mean useful discrimination.

Define ordinal ranked probability score as the mean squared difference between predicted and gold cumulative probabilities over the first `K-1` boundaries, normalized by `K-1`. Report the implementation and test it on exact examples. Preserve bimodal level distributions: the same expected Score can conceal very different risk. Reversing a rubric changes its index mapping; arbitrary permutation is not an invariance test.

Fit calibration maps only on validation data and report both native and post-calibrated outputs for every eligible system. Select temperature scaling, logistic calibration, or isotonic calibration before test inspection, considering available sample size. A fitted map from provider confidence to correctness is a **new model component** with its own validation requirement. Do not silently treat raw confidence as the input event probability for Brier or ECE against correctness.

## 6. Routing and selective automation

For a policy threshold `t`, define automatic coverage as accepted cases divided by all eligible cases, and selective risk as erroneous accepted cases divided by accepted cases. Report the denominator and risk when coverage is zero as undefined, not zero error. Include failures, abstentions, and timeouts explicitly in whole-system utility.

Compare policies at **matched coverage** and at **matched validated risk**, not arbitrary equal numeric confidence thresholds across models. Use risk–coverage curves and area under that curve as descriptive summaries; prespecify the deployment operating point. Include random review and simple heuristic review baselines. Evaluate whether uncertainty actually captures errors rather than merely producing more middling numbers.

Freeze a loss matrix, review capacity, fallback latency/cost, deadline, and the permitted false-accept/false-reject rates. Learn thresholds on validation groups, then lock them. Do not claim successful automation from accepted-subset accuracy alone if nearly everything was escalated or the fallback missed its deadline. An abstention changes system behavior; it is not a correct task label unless the gold policy explicitly calls for abstention.

## 7. Robustness matrix

Use paired transformations of the same held-out source and a clean unmodified control. Human-check that purported meaning-preserving transformations actually preserve the answer. Keep all variants together for statistical resampling. Repeat a subset without transformation to estimate ordinary sampling variability.

| Stress | Construction | Measure and interpretation |
|---|---|---|
| Choice order | Seeded option permutations, mapping results back to semantic labels | Decision flips and distribution distance beyond unmodified-repeat variability |
| Question packaging | Question-order changes, identifier renaming, alone/batched/concurrent execution, unused speculative branches | Per-question drift, final action drift, saved input cost, wall time; batching is not statistical independence |
| State serialization | Reorder JSON fields, alter harmless whitespace, preserve exact values | Semantic invariance, token changes, evidence-addressing errors |
| Paraphrase | Independent paraphrases of state, instructions, and criteria, one factor at a time | Accuracy and probability drift; use disjoint paraphrase templates |
| Negation and boundaries | Explicit negatives, exclusions, borderline quantities, double negatives | Directional error analysis; separately asked complements are not assumed to sum to one |
| Missing evidence | Remove decisive span, required field, or gold candidate; mask rather than fabricate | Abstention/no-match behavior and confident unsupported acceptance |
| Irrelevance and length | Append/prepend unrelated content at several lengths; place evidence early/middle/late | Error slope, truncation, token/latency growth, evidence-position effects |
| Candidate set changes | Add near-duplicates, plausible distractors, duplicate spans, no relevant candidates | Ranking stability and no-match behavior; raw Choice probabilities need not stay invariant when the answer space changes |
| Contradiction/staleness | Conflicting sources, explicit updates/retractions, version mismatches | Respect for declared provenance and time; do not silently resolve unavailable facts |
| Prompt injection | Instructions embedded only in untrusted source text; role spoofing, requests to override criteria, forged authority | Attack success, residual false acceptance, benign utility loss; no tools or real external actions |
| Distribution shift | Held-out domains, time, dialects/languages, noisy/OCR text | Per-stratum performance and calibration, not only a pooled mean |
| Composition stress | Correlated component errors, irrelevant branch failures, stale intermediate state | End-to-end loss, unnecessary fallback, unsafe action proposals |

For injection, define the attacker's desired wrong outcome and allowed access before constructing attacks. Use static fixtures with dummy identifiers and no live secrets. Compare vulnerable and defended configurations using identical attacks; defenses may include explicit instruction/data separation, source filtering, or mandatory review. A single “ignore previous instructions” example is not a security evaluation. TypeSafe itself warns that adversarial state can move answers.[8]

Use a factorial design if claiming an interaction, such as length amplifying injection. Otherwise describe only the jointly stressed condition. Maintain a separate exploratory red-team set; discovered attacks become new regression fixtures, not retrospectively pristine test cases.

## 8. Competent and fair comparisons

Two experiments answer different questions and both are useful:

1. **Matched representation:** same evidence, candidates, policy, and output semantics; isolate judgment quality.
2. **Best practical system under budget:** each approach may use its appropriate interface, tuning, batching, and calibration, subject to declared information and development budgets.

Use the same lawful evidence for both. Disclose supervised label budgets and pretrained versus task-fitted components instead of pretending they are equivalent supervision. Fit vectorizers, embeddings-based classifiers, calibration, and thresholds without test leakage. Give low-cost LLMs constrained outputs, sensible low/no-reasoning modes where supported, bounded prompts, and concurrent execution when appropriate. Add a probabilities-required track separately from label-only tasks; generating a full probability vector is not a fair universal cost requirement for a system that only needs one class.

Track retries, parsing repair, cached responses, and invalid outputs for all providers. A “free local baseline” still has hardware, serving, energy, and maintenance costs; report marginal inference separately from training and amortized infrastructure. Report quality/cost/latency Pareto sets with uncertainty, not a universal multiplier derived from different workloads.

## 9. Operational measurements and receipts

The current model page advertises dynamically adjustable limits of 250,000 tokens per second and 1,200 requests per minute.[2]
The SDK exposes configurable retries, backoff, and retryable conditions; record the actual settings rather than hiding SDK behavior inside one latency value.[29]

**Per attempt:** run/case/cluster identifiers; UTC timestamp; request hash; requested/resolved model; endpoint class; SDK/adapter versions; sanitized request or private immutable reference; question/criteria hashes; connection mode; concurrency; attempt index; start/end monotonic times; HTTP status; error class; response completeness; usage; and provider request identifier if safely publishable.

**Per logical decision:** number of attempts, raw answer, final action, fallback path, total wall time, queueing, preprocessing/retrieval/normalization time, total token usage across all attempts, and cost provenance. Preserve raw responses privately when they may contain sensitive input echoes. A public receipt is a redacted audit record, not an authorization header or a full request dump.

Measure cold connection versus warm connection, isolated versus batched calls, representative short/long states, and several concurrency levels below published limits. Interleave provider runs in randomized time blocks across more than one period. Record client region and routing path at a coarse public granularity; avoid private network details. Distinguish service-only timing, where available, from client-observed end-to-end latency.

Report p50/p90/p95/p99 only with sample counts and an appropriate uncertainty statement; do not advertise p99 from a handful of calls. Report success-before-deadline, timeouts, cancellation, 429, 5xx, connection failures, malformed/incomplete responses, and resolved-model drift. Do not omit failed attempts from a “fast” latency result. Treat deadline-censored calls separately from successful latencies and include the full deadline penalty in operational utility.

Compute list-price estimates from provider-reported usage and the dated price sheet. For current direct Jev pricing, the proposed estimate is `input_tokens / 1_000_000 * 0.042`, with no output charge.[2]
Keep **estimated list cost**, **provider-reported charge**, and **verified invoice amount** as separate fields. Include retry/fallback/candidate-generation/retrieval/review costs; indicate unknown costs instead of setting them to zero. Never infer model input tokens from a universal characters-per-token ratio. Compare cost per attempted case, successful case, correct final decision, and automatically resolved case.

## 10. Statistical analysis and uncertainty

### Estimands and denominators

Freeze the population, primary outcome, paired contrast, analysis unit, and treatment of exclusions before test inference. Report case-weighted and task-macro summaries separately. Clustered questions and paraphrases do not increase the number of independent documents. Never silently pool ordinal MAE, ranking quality, classification accuracy, and semantic agreement.

Require an a priori sample-size calculation or simulation using a minimum worthwhile effect, anticipated paired disagreement/variance, cluster structure, desired power, and multiplicity correction. Pilot estimates may set this design, but pilot observations do not enter the locked test. Rare-error safety claims require enough independent relevant exposure; a large easy-negative set cannot certify rare-positive recall.

### Proposed default analysis

- Report paired effect sizes and 95% intervals, using a cluster bootstrap with a frozen seed and 10,000 resamples where suitable. Resample original independent units with all their model outputs and transformations together.
- For independent binary outcomes use Wilson/exact intervals; for paired binary contrasts use an appropriate paired test, not independent-proportion testing. For grouped cases use cluster-aware inference.
- For ranking, bootstrap queries or source-query clusters. For latency, preserve run/time blocks; report distribution shifts as well as central estimates.
- At zero observed errors use a non-degenerate bound, not a naive bootstrap interval of zero width. For independent Bernoulli trials, the exact one-sided 95% upper bound after zero errors is `1 - 0.05^(1/n)`: about 2.95% at 100 trials and 0.299% at 1,000. These are mathematical illustrations, not Jev measurements, and do not apply unchanged to dependent trials.
- Declare a practical non-inferiority margin before evaluation. For a loss difference `Jev - baseline`, require the specified upper confidence bound to lie below that margin; a nonsignificant difference is not evidence of equivalence.
- Keep raw and post-calibrated comparisons distinct. Account for uncertainty in fitting thresholds/calibration, using nested procedures when estimating full training-to-deployment performance.

### Multiple testing and adaptive search

Define a small confirmatory hypothesis family after selecting the target and before test access. Suggested family: task quality/non-inferiority, accepted-case critical risk, and total cost/latency benefit under the frozen policy. Specify which are joint go/no-go constraints rather than opportunities to select any favorable result.

Use Holm familywise adjustment for prespecified superiority tests, or explicitly allocated error budgets for simultaneous guardrail bounds. Do not claim “one significant task” after testing many tasks, models, prompts, thresholds, seeds, and perturbations without accounting for selection. Exploratory broad sweeps may report false-discovery-rate-adjusted findings, clearly labeled for independent follow-up. Publish negative and inconclusive results and the number of tried configurations.

Fix the sample size and stopping plan. No stopping when a favorable p-value appears. If interim efficacy analyses are necessary, preregister a sequential design and its error control. Safety/budget stops are always allowed but leave a potentially censored/incomplete experiment, not a favorable completed benchmark.

## 11. Stop gates and later target selection

| Gate | Must be true to proceed | Stop or downgrade if |
|---|---|---|
| G0 — scope/data | Lawful inputs, privacy plan, no secrets, bounded cost and safe non-acting harness | Unknown license, private data exposure, destructive action, absent budget approval |
| G1 — contract | All primitives round-trip; complete receipts; metric unit tests; exact model resolution | Missing fields, invalid probabilities, silent repairs, untracked retries or model drift |
| G2 — data readiness | Gold/candidate/evidence audit, group splits, known ambiguity, competent baseline | Retrieval/extraction failures dominate, labels are unfit, leakage found |
| G3 — pilot | Coverage across required tracks; error taxonomy; sample-size feasibility | Too little independent data, hidden price/usage, unstable service or unaffordable review |
| G4 — freeze | Immutable protocol/data/configuration hashes and completed registration fields | Open hypotheses, unspecified margins, unavailable comparator, test already used for tuning |
| G5 — confirmatory acceptance | Prespecified quality/risk bounds and resource budgets satisfied jointly | Critical risk bound fails, excess review/latency/cost, inconclusive non-inferiority, multiplicity failure |
| G6 — deployment consideration | Separate shadow evaluation and approval on target traffic | Domain/version drift, insufficient monitoring, fallback unvalidated |

Immediate operational stop conditions must be numeric in the run registration: maximum spend, attempts, wall time, allowed consecutive/rate-limited errors, and maximum input exposure. Stop on credentials appearing in logs or unapproved input. A schema violation triggers preservation and investigation, not automatic deletion of the offending case. A critical injection success blocks unattended use for that workflow until remediation and a new held-out check.

After broad exploration, rank possible targets by label quality, observed bottleneck, incremental utility over the best simple baseline, review capacity, maintainability, and safe fallback. Do not select a target only because its model-only accuracy is high. Keep a conventional implementation as the default if Jev does not clear its added-complexity gate. This draft intentionally does not choose a deployment target or activate one.

## 12. Registration and reporting checklist

Before the first confirmatory test call, complete and timestamp:

- Track, population, sampling frame, dataset licenses/versions, group split and held-out hashes.
- Gold-label guide, adjudication, unknown/ambiguous treatment, inclusion/exclusion rules.
- Exact endpoints, model IDs, adapter/SDK versions, prompts/criteria, candidate generator, calibrator and composition policy.
- Baselines, their tuning/supervision budgets, and fair matched-evidence versus best-system comparison modes.
- Primary estimand(s), practical margins, loss matrix, operating point, sample-size rationale, confidence procedures and multiplicity family.
- Repeats, perturbation seeds, batch sizes, concurrency, time blocks, retry and deadline rules.
- Spend/input limits, stop conditions, exception handling, and who may approve changes.
- Repository revision and protocol/configuration hashes, registration timestamp, access-control plan for test labels, and all prior exploratory exposures.

Every final report must identify its evidence tier, give denominators and uncertainty, link redacted receipts and exact configurations, disclose all exclusions/failures, distinguish external reported findings from local execution, and include a deviation log. Publish the chosen target only after the broad audit justifies it; do not rewrite the original protocol to make exploratory successes appear predicted.

## Sources

[2] https://docs.typesafe.ai/models.md — Models
[3] https://docs.typesafe.ai/api.md — API reference
[4] https://docs.typesafe.ai/primitives/choice.md — Choice
[5] https://docs.typesafe.ai/primitives/noul.md — Noul
[6] https://docs.typesafe.ai/primitives/score.md — Score
[7] https://docs.typesafe.ai/confidence.md — Confidence
[8] https://docs.typesafe.ai/model-jaggedness/jev-1.13.md — Jev 1.13 jaggedness
[15] https://docs.typesafe.ai/cookbooks/parallel_questions.md — Parallel questions
[16] https://docs.typesafe.ai/cookbooks/rerank_typesafe.md — Re-ranking
[17] https://docs.typesafe.ai/cookbooks/citation_check.md — Double-checking citations
[18] https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md — Pre-parsed value extraction
[19] https://docs.typesafe.ai/patterns/composite-scoring.md — Composite scoring
[20] https://docs.typesafe.ai/patterns/confidence-routing.md — Confidence-gated routing
[21] https://docs.typesafe.ai/cookbooks/sde_cascade.md — SDE cascade
[25] https://proceedings.mlr.press/v70/guo17a.html — On Calibration of Modern Neural Networks
[26] https://aclanthology.org/2020.nlp4convai-1.5 — Efficient Intent Detection with Dual Sentence Encoders - ACL Anthology
[27] https://aclanthology.org/N18-1074 — FEVER: a Large-scale Dataset for Fact Extraction and VERification - ACL Anthology
[29] https://docs.typesafe.ai/sdk/python/api/retries.md — Retries
[30] https://docs.typesafe.ai/concepts/system-one.md — System One
[33] https://raw.githubusercontent.com/beir-cellar/beir/main/README.md — <h1 align="center">
