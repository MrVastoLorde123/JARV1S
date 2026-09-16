# M29 — Perception

**Status:** implementation in progress.

M29 establishes a provider-neutral perception layer over JARVIS's existing environment observation and freshness architecture.

## Milestone chain

- **M29.1 — Perception boundary:** distinguish observation from authority and execution.
- **M29.2 — Source contract:** identify filesystem, process, network, service, log, and hardware observation domains.
- **M29.3 — Immutable observation:** bind source, environment, timestamp, availability, payload, and provenance.
- **M29.4 — Snapshot contract:** reject mixed environments and duplicate observation identities.
- **M29.5 — Freshness integration:** retain existing deterministic freshness semantics rather than inventing a second temporal model.
- **M29.6 — Verification gate:** focused perception tests, UI build, and established core regression baseline.

## Boundary

M29 is perception and environment observation. It does not authorize actions, execute tools, mutate the environment, or treat observations as authority or certainty.

## Verification

```text
python -m unittest src.core.tests.test_perception_contract -v
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```
