# M26 — Activity & Evidence

**Status:** VERIFIED / COMPLETE.

M26 turns the cockpit's existing activity and verification projections into a typed, safe presentation contract. It makes operational history and evidence references consumable without making the interface a second authority system.

## Milestone chain

- **M26.1 — Activity contract:** normalize bounded runtime lifecycle events into `CockpitActivityEvent`.
- **M26.2 — Evidence contract:** normalize bounded verification/evidence references into `CockpitEvidenceReference`.
- **M26.3 — Cursor continuity:** preserve the runtime-owned monotonic activity cursor.
- **M26.4 — Safe normalization:** reject malformed identity/summary fields and normalize unknown states safely.
- **M26.5 — UI visibility:** preserve the existing activity rail and verification surfaces as runtime-backed presentation.
- **M26.6 — Verification gate:** repository-local contract validation plus UI build and established regression baseline.

## Verification receipt

- `python scripts/verify_m26_activity_evidence.py` → **PASS**
- `cd ui && npm run build` → **PASS**
- `python -m unittest discover -s src.core.tests -p "test_*.py"` → **3276/3276 OK**

## Boundary

M26 is observation and evidence presentation. It introduces no authorization, no new execution path, and no duplicate durable activity store.

M26 is closed on the verified local receipt above. The next milestone may build on its typed activity/evidence contract.
