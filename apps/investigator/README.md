# Issue investigator

A read-only tool-using controller, not a scripted fix. Jev selects a closed action/argument candidate after **each** real observation. The candidates come from the issue's keywords, frozen source inventory, search hits, and observed immutable Git history. Qwen on `127.0.0.1:11434` develops a hypothesis and, only if selected by Jev, a final cited report. Its text never becomes a tool argument or executable command.

Open `index.html` directly and choose **Open reviewed JSON** after export. Nothing is preloaded. The SVG execution and evidence graphs have keyboard/click inspectors. All source/model strings use `textContent`. No external dependencies, network requests or provider credentials exist in the console. Offline test exports explicitly say **PROVIDER DOUBLES**; recorded-live means recorded actual adapter calls, not a real-time browser session.

## Operator commands

Run from `/Users/tr/Projects/jev-empirical`. `PYTHONPATH=src` avoids changing the root packaging configuration. Every private directory below must be a **new** leaf outside every Git tree. No inference occurs during `freeze` or `check`.

```sh
PYTHONPATH=src python3 -m jev_investigator freeze \
  --issue https://github.com/14-TR/jev-empirical/issues/1 \
  --source-repo /Users/tr/Projects/jev-empirical \
  --commit 9ce1292723a92b05d5957b150d18a83ec25d5d62 \
  --private /Users/tr/jev-investigator-freeze-operator

PYTHONPATH=src python3 -m jev_investigator check \
  --bundle /Users/tr/jev-investigator-freeze-operator \
  --allow-checks --profile incident-unittest

PYTHONPATH=src python3 -m jev_investigator check \
  --bundle /Users/tr/jev-investigator-freeze-operator \
  --allow-checks --profile incident-replay-metadata
```

The optional metadata probe is a **predeclared operator profile**, not model-generated code. It loads the frozen public bundled live episode, deep-copies it, relabels its first Jev call to tick 19, recomputes integrity, and records whether validation accepts it. It compares the original with a saved deep copy; it never mutates the public episode or relies on nondeterministic elapsed-time fields from a fresh run. Check exit 0 means the probe ran, **not** that the bug is fixed.

After candidate review, the parent may run actual inference (requires `TYPESAFE_API_KEY` in the parent environment and installed Ollama `qwen2.5:7b`):

```sh
PYTHONPATH=src python3 -m jev_investigator run \
  --issue https://github.com/14-TR/jev-empirical/issues/1 \
  --source-repo /Users/tr/Projects/jev-empirical \
  --commit 9ce1292723a92b05d5957b150d18a83ec25d5d62 \
  --private /Users/tr/jev-investigator-live-operator \
  --allow-live --allow-source-upload --allow-checks \
  --profile incident-unittest --profile incident-replay-metadata \
  --steps 12 --seconds 300
```

`--allow-checks` and named profiles are independent of live/upload consent. Without them no check candidate exists. Checks run fixed Python with `-I -S`, credential-free allowlisted environment, bounded process-group lifetime/output, and a disposable copy of the filtered snapshot. **This is NOT an OS sandbox. Only approve trusted repository code.** Such code can still access the host filesystem and network using its own privileges.

The source working tree/index are never checked out, reset, cleaned or modified. Archive members are compared with immutable Git blob identities (rejecting `export-subst` transformations); hidden paths, symlinks, submodules, credential-like names, private/receipt directories, nontext and oversized files are not copied. There is no `.git`, copied credential store, broad home-directory scan, arbitrary model path, or shell command. Git history/diff read immutable objects from the explicit source repository with hooks, global config, external diffs and textconv disabled. The private source copy detects changed bytes on every read.

Limits: 12 steps / 12 Jev calls / 2 Qwen calls / 300 seconds including CLI preparation; 256 files / 4 MiB filtered source / 128 KiB per file; 40 lines and 6 KiB per read; 12 bounded search hits; 5 history commits; 8 KiB diff; 10 KiB check output; 15,500-byte Jev state and 24,576-byte Qwen evidence; Qwen output 1,000 tokens. Source-name/content filters are defense in depth, **not proof arbitrary source is nonsensitive**. Live upload consent covers issue text and selected source observations sent to TypeSafe; Qwen remains localhost-only.

All raw call receipts and `run.json` remain private. Failures/clarification/budget exhaustion are explicit, return nonzero, and never invoke a scripted fallback or successful sample. Offline tests inject provider doubles only; tool actions still read real temporary Git repositories and run real subprocess checks.

Jev receives up to four newest whole observations, dropping older whole observations if needed to fit its unchanged 15,500-byte state cap. Each state explicitly records `omitted_observations`; the newest observation must fit or the run fails with `context_budget`. The complete private observations, graphs and Qwen final evidence are not pruned by this packing. A final evidence set exceeding Qwen's unchanged cap still fails explicitly.

### Investigator-only probability rounding policy

The shared benchmark parser remains strict (sum tolerance `1e-6`). The TypeSafe API documents probabilities summing to one, but the private live-04 receipt returned 20 cent-valued probabilities summing to `0.99`. This investigator alone permits a **documented accommodation, not a provider guarantee**: after strict parsing fails specifically with `probability_sum`, a Choice may be proportionally normalized only when every probability is finite, in `[0,1]`, on the exact decimal `0.01` grid, the total is in `[0.99,1.01]`, and each corrected probability moves by at most `0.005`. The per-value half-cent limit makes the correction compatible with cent rounding; the one-percentage-point total cap deliberately does **not** grow with option count. Some genuinely rounded responses will therefore still be rejected.

The normalized copy must pass the entire original parser, including exact candidate IDs, selected ID/argmax and valid confidence. The provider-selected action and **original provider confidence are unchanged**; normalized mass is not recalibration or evidence of correctness. Raw receipts are saved before parsing and never rewritten. Each accepted correction emits a `cent-rounding-v1` normalization event linked to the Jev response, recording the original probabilities and both totals. Material errors, non-cent values and invalid selections still fail closed with allowlisted validation codes; arbitrary error text is never copied into the run. No retry or fallback is added.

Qwen's final report receives the issue as context and actual `oN` tool observations only. Both its JSON-schema citation enum and the controller's independent response validation restrict final citations to these observed IDs; the hypothesis cannot cite itself into evidence. Low distribution concentration among approved read-only actions is recorded honestly, not treated as permission or blocked by an uncalibrated confidence threshold. Explicit live/upload/check consent and closed tool candidates remain required.

## Explicit review and export

```sh
PYTHONPATH=src python3 -m jev_investigator review \
  --run /Users/tr/jev-investigator-live-operator/run.json
```

Inspect the printed observations, model hypotheses, private raw receipts and source references. Copy the exact `review_sha256`. Then explicitly list **each public source path** to be released, including every path mentioned in selected tool arguments and observed check inputs. `--allow-public-source` asserts that the issue and these selected inputs are public and approved for release. The exporter refuses omitted paths, changed review bytes, unknown fields, sensitive text and existing output files.

```sh
PYTHONPATH=src python3 -m jev_investigator export \
  --run /Users/tr/jev-investigator-live-operator/run.json \
  --review-sha256 REPLACE_WITH_REVIEWED_HASH \
  --allow-public-source \
  --public-path src/incident_room/episode.py \
  --public-path tests/test_incident_episode.py \
  --public-path apps/incident-room/live-episode.json \
  --out /Users/tr/jev-investigator-public-operator
```

The public paths above are examples, **not an automatic allowance**; include the actual reviewed observed paths or export fails. Output is `investigation.json` and script-safe `investigation.js`, not private traces. Load JSON through the console's local file picker. No publishing, Git commit, issue comment or fix occurs.

## Offline verification

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_investigator*.py' -v
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --check apps/investigator/app.js
```

Graph validity is structural provenance, not proof of model truth: solid edges mean recorded sequence or observed source; dashed `hypothesis` edges are model interpretations. AST symbol nodes are only created from successfully parsed actual Python definitions. A cited claim can still be wrong; report review is mandatory.
