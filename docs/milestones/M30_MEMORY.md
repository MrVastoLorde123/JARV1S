# M30 — Memory

**Status:** implementation in progress.

M30 formalizes durable memory as a typed, provenance-bearing knowledge layer over the existing structured memory and memory-evidence stores.

## Milestone chain

- **M30.1 — Memory contract:** define immutable memory records, lifecycle status, source identity, and evidence references.
- **M30.2 — Evidence lineage:** keep supporting evidence explicit and bounded rather than treating remembered claims as self-proving truth.
- **M30.3 — Retrieval contract:** define read-only memory queries and retrieval results with deterministic bounds.
- **M30.4 — Authority separation:** memory cannot imply permission, authorization, execution, or completion.
- **M30.5 — Verification gate:** focused memory tests, repository-local contract validation, UI build, and the established core regression baseline.

## Boundary

M30 is memory and knowledge persistence. Existing memory/evidence stores remain authoritative for persistence. No new authority, tool execution, or duplicate memory store is introduced.

## Verification

```text
python -m unittest src.memory.tests.test_m30_memory_contract -v
python scripts/verify_m30_memory.py
cd ui
npm run build
cd ..
python -m unittest discover -s src.core.tests -p "test_*.py"
```

M30 closes only after the user-local receipt is green.
