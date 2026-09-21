# Investigator metadata-check fixture

This is a **test-only historical source/input closure**, not a restored Incident
Room application or a new investigation result. The four files are byte-for-byte
copies of original public, MIT-licensed project material at
`9ce1292723a92b05d5957b150d18a83ec25d5d62`, the revision named in
`docs/investigator-goal.md`. No private investigator run or raw provider receipt is
included.

| Fixture file | Historical path | SHA-256 |
| --- | --- | --- |
| `episode.py` | `src/incident_room/episode.py` | `1887d605eec56b3db935bd102a09b721b720186a912fa10b4f40a3ae6ce9169e` |
| `engine.py` | `src/incident_room/engine.py` | `557571473f9e5c8452b8ea4ca17908e5ede48c4752ab5a0a62e9f2542658a576` |
| `core.py` | `src/jev_bench/core.py` | `3b64ef1e7cc6d3985754e88392c9b1dfeed837f975b12b7598f5247da0be10a4` |
| `live-episode.json` | `apps/incident-room/live-episode.json` | `7808fc0db2b226d6c57dd5690f851cf6fe8446f353b142c8ce2ad28365fef116` |

The closure is four files / 52,149 bytes. It contains the replay validator, its
pure reducer and strict-parser dependencies, and the already-public eight-tick
replay. It contains no application entrypoint, UI, provider adapter or HTTP
transport. Keep the historical bytes intact rather than replacing the validator
with an always-successful stub. The fixture retains the known issue: a resealed
Jev call tick of 19 is accepted despite a final frame tick of 8.

`test_metadata_probe_is_deterministic_and_preserves_original` verifies each hash,
copies only these named files into a disposable local Git fixture, freezes that
temporary commit through the real source loader, and runs the unchanged approved
check twice. The temporary source and frozen snapshot must remain byte-identical.
The check's source requirements and consent guard remain in force.

The test never resolves this checkout's `HEAD`, fetches historical objects, or
invokes `episode.run`. It works with a depth-one checkout (or a source archive);
the historical commit is provenance, **not a runtime dependency**. The historical
`src/incident_room/` and `apps/incident-room/` paths exist only inside the disposable
test repository. They are not restored in the product source/application roots.

This fixture establishes deterministic check execution against explicitly trusted
public test inputs. It does not complete issue 1, demonstrate current live model
behavior, approve arbitrary repository execution, or satisfy the outstanding
investigation/public-preview acceptance gates.
