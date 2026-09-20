# Hybrid Jev agent harness — implementation contract

Status: authorized implementation; not yet a verified running agent.

## Goal

Build an actual model-driven agent loop, distinct from the evaluation harness. Jev chooses bounded next actions from the goal and current observations. A general-purpose language model synthesizes an answer using gathered evidence. Deterministic code owns tool execution, capability restrictions, and resource limits.

## First vertical slice

A user selects an explicit workspace of public text documents and asks a question requiring evidence from more than one document. The controller enumerates safe files. Jev selects read actions and candidate file IDs, updates its decisions after observations, and chooses synthesis or clarification. Local Ollama `qwen2.5:7b` generates a source-grounded answer. This model is the initial general-purpose synthesis backend, not a claimed frontier reasoning model.

Jev must genuinely choose actions based on state; a fixed scripted retrieval sequence with a cosmetic model call does not meet acceptance. The answer backend must actually run; a mock or template answer does not establish hybrid execution.

## Capability boundary

- Read-only tools: bounded file listing and text-file reading in the explicit workspace.
- No shell, arbitrary network requests, file writes, installations, remote messages, or autonomous Git operations exposed to the agent.
- Candidate file IDs come from code, not model-authored paths. Reject escaping paths, symlinks, hidden/sensitive files, oversized inputs and nontext content.
- Workspace files are untrusted evidence, never instructions authorizing new capabilities.
- Provider adapters use fixed endpoints. Jev credentials come only from environment; Ollama uses fixed local loopback.
- Explicit live and workspace-upload opt-ins are required. Local files can be transmitted to Jev after consent; local synthesis does not make the whole workflow local-only.
- Filename filters are defense in depth, not comprehensive secret detection. Operators must select a safe workspace. The included original synthetic fixture is the default verification target.

## Controller contract

Inputs: goal, workspace, explicit model configuration, consent flags, finite step/request/time/context limits, and private trace destination outside Git.

Outputs: completed answer, clarification, or typed failure; provider invocation counts; bounded execution trace. No silent fake provider or fallback success.

Jev route and candidate judgments may be batched, but neither can depend on the other response. Only consume a candidate judgment for a branch requiring it. Probability thresholds are uncalibrated engineering heuristics pending evaluation, not proven safety thresholds. Code validates every result and keeps authorization separate from confidence.

Repeated actions, absent progress, exhausted budgets, malformed provider output, or unavailable providers end in an explicit non-success state. Synthesis text cannot trigger tools. Traces are private by default and must not contain credentials or raw transport errors.

## Acceptance evidence

1. Offline tests cover state transitions, malicious evidence, invalid selections, abstention, loops, resource exhaustion, scope escape and provider failures.
2. Existing benchmark regressions continue to pass.
3. Independent security/code review of exact implementation before publication.
4. A real run against versioned Jev and the local language model reads original fixture evidence and produces an answer consistent with current versus superseded policy. Record actual route, tool, and synthesis steps without inventing them.
5. Publish source, fixture and explicitly selected sanitized live evidence in meaningful separate commits. Credentials and private traces remain outside the public repository.

## Deferred scope

This first release is a read-only evidence agent, not a general autonomous coding agent or replacement for Hermes. Write-capable tools, human approvals, durable resumable sessions, external model adapters, calibrated routing, and broader comparative evaluations require additional implementation and acceptance tests.

## Relevant official design guidance

- https://docs.typesafe.ai/cookbooks/function_calling.md
- https://docs.typesafe.ai/patterns/fan-out.md
- https://docs.typesafe.ai/api.md

These references inform the design; they do not establish this harness's correctness or safety.
