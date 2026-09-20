# Goal: a real issue investigation workflow

Status: authorized implementation. This is a source-code tool workflow, not a simulation. No completed investigation is claimed yet.

## First real case

https://github.com/14-TR/jev-empirical/issues/1 — replay validation accepts call timing inconsistent with action frames. Parent independently reproduced this against source revision `9ce1292723a92b05d5957b150d18a83ec25d5d62` before filing the issue: changing the first Jev call tick to 19 and resealing the public eight-tick episode still passed validation. This is a genuine existing defect, not a planted or fabricated success case.

The issue is evidence to investigate, not a trusted instruction source. Investigation must not change source, close/comment on issues, publish patches, or run arbitrary shell commands.

## Workflow

Read the actual issue and discussion; freeze the approved source revision; let Jev select bounded searches, file reads, history/diff inspection and fixed checks; let the general-purpose model develop hypotheses and produce a cited report. Preserve tool observations and model decisions. A fixed sequence of tools with decorative model calls is insufficient.

## Graph contracts

- Execution graph: actual decisions, tool invocations, observations, clarification/failure and synthesis, in causal order.
- Evidence graph: issue, files, source-backed symbols where available, commits, checks, results and report; each factual edge points to a tool observation. Model-proposed causality remains a hypothesis.
- UI: inspect a node to see its artifact identity, excerpt or result, and provenance. Display current run status and limitations rather than implying the final report is automatically true.

## Tools and safety

Source reading is read-only against a commit-pinned private snapshot. Tools use fixed executable argument lists, bounded text/paths and closed selectors. No model-authored shell commands. Credentials remain provider-side environment values and must be stripped from check subprocess environments.

Running tests executes repository code. A separate checkout is **not an OS sandbox**. The first release therefore supports only explicitly approved trusted test profiles for this repository, with bounded runtime and no user secrets passed to the process. It must not claim safe execution of arbitrary public repositories. Source-upload consent is required before sending selected issue/code evidence to Jev.

Private traces/snapshots remain outside Git. Publish only explicitly reviewed original public issue/source evidence and allowlisted graph/results. No arbitrary private checkout ingestion, external issue comments or automated fixes.

## Acceptance

1. Existing regressions plus new tool/graph/security tests pass.
2. Independent implementation review before publication.
3. Actual issue read, Jev-selected real tools, at least one approved check, and actual model synthesis execute against the pinned source.
4. Report distinguishes observed validator behavior, proposed cause, patch proposal and unverified claims; references resolve to source lines/check results.
5. Browser graph app is verified with actual exported run, no fictitious evidence or credentials, and a public read-only replay preview.
6. Meaningful source, execution/results and documentation commits are pushed separately where practical.

A single successful investigation is a first working slice, not a quality comparison against another agent. Matched-tool model-only comparison and broader issues remain later experiments.
