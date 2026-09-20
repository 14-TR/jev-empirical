# Jev Empirical

Independent, reproducible behavioral evaluation of TypeSafe's Jev.

**Status: initial study under construction. No empirical performance conclusions yet.**

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
