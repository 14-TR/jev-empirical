# Original authored synthetic diagnostics

`synthetic_diagnostics.json` contains **101 synthetic input cases**, not model
responses: 18 authored base scenarios and 83 label-preserving perturbations.
The source scenarios, rubrics, gold labels, and transformations are in
`../scripts/build_dataset.py`. They were authored for this project, not copied
from a public benchmark or a vendor's result table.

- Routing: four base requests, covering billing, technical, sales, and other.
- Evidence: three bases, covering supported, contradicted, and insufficient.
- Candidate selection: four bases, including a no-candidate outcome.
- Noul predicate: four bases, including negation and an irrelevant past deadline.
- Ordinal functional impact: three bases, one per concrete level.

Every base gets a separately authored paraphrase, extra whitespace, an irrelevant
sentence, and a quoted instruction-injection perturbation. The eleven Choice
bases additionally get reversed option insertion order. Score levels are never
reordered: that would change their meaning. Labels are preserved by author intent,
not by independent human adjudication. A task-specific base scenario is the unit
of semantic diversity; 101 rows are **not 101 independent examples**.

Gold annotations are separate from `input`. The transport API only accepts an
input object with `state.text` plus a question; it rejects a complete labeled case.
The fixed question ID is `q`, never the case ID. Metadata, family, pair ID, and gold
are not serialized into the API request. This structurally prevents automatic
label copying; it cannot detect a human intentionally typing an answer into text.

Requests are ordered with all bases first, then one family at a time. Under a
request or time cap, later families may be unattempted; they remain failures in
all-case denominators. Use the full 101-case budget to compare every family.

Regenerate using `python3 scripts/build_dataset.py`. The checked-in file is
reproducible and tested against the generator. The harness uses a deliberately
narrow schema: five task names, six families, string instructions/criteria, and a
single text field. Arbitrary imported datasets are not supported by this release.

## Limits

Small English-only, simple, explicitly labeled examples. No external holdout,
contamination analysis, multiple annotation raters, multilingual coverage,
long-context test, task difficulty matching, or adversarial search. Selection
and author bias are substantial. Results diagnose behavior and plumbing; they
are not a representative capability ranking, calibrated deployment guarantee,
or a claim of statistical significance.
